"""Self-healing of SpatiaLite spatial views in pyArchInit SQLite DBs.

QGIS (SpatiaLite provider) and OGR draw a registered spatial view by
filtering its key column against the R*Tree of the table the geometry comes
from: ``<key> IN (SELECT pkid FROM idx_<base>_<geom> WHERE <bbox>)``.
pyArchInit opens views with OGR (key = ``views_geometry_columns.view_rowid``)
and with the SpatiaLite provider (explicit key ``"ROWID"``). The key must be
the ROWID of the geometry table. Defects found in shipped and user DBs:

* ``bad_key``: no key column (the implicit view rowid is NULL), or a key
  taken from the attribute table (e.g. ``us_table.rowid`` in
  pyarchinit_quote_view): nothing, or the wrong features, are drawn;
* ``stale``: registration naming a geometry column the view lacks;
* ``missing``: registration of a view that does not exist;
* ``broken``: the view itself fails (it references a dropped table);
* ``unregistered``: a pyarchinit_*_view with geometry never registered
  (the UT views), invisible to OGR;
* base tables without a spatial index: OGR then filters with SpatiaLite SQL
  functions, missing in some GDAL builds, and draws nothing.

Every change is first tried on a TEMP view (nothing written to the file) and
applied only when the new view's key is proven right, so a view that cannot
be fixed is left alone and does not trigger a backup at every session.
Standard-library sqlite3 only; SpatiaLite is needed just for CreateSpatialIndex.
"""
from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass

try:
    from .spatial_view_definitions import CANONICAL_VIEWS
except ImportError:  # pragma: no cover - module shipped alongside
    CANONICAL_VIEWS = {}

KEY = 'rowid'
_IDENT = r'(?:"[^"]+"|`[^`]+`|\[[^\]]+\]|[A-Za-z_]\w*)'
_STOP = {'on', 'join', 'left', 'right', 'inner', 'outer', 'cross', 'natural', 'full',
         'where', 'group', 'order', 'limit', 'using', 'union', 'having'}
_ROWID_NAMES = {'rowid', '_rowid_', 'oid'}
_CHILDREN = ('views_geometry_columns_auth', 'views_geometry_columns_statistics',
             'views_geometry_columns_field_infos')
_HEAD_RE = re.compile(r'(?is)^\s*CREATE\s+VIEW\s+(?:IF\s+NOT\s+EXISTS\s+)?(' + _IDENT + r')\s+AS\s+SELECT\b')
_ALIAS_RE = re.compile(r'(?is)^(?P<expr>.*?\S)\s+(?:AS\s+)?(?P<alias>' + _IDENT + r')\s*$')
_QUALIFIED_RE = re.compile(r'(?is)^\s*(' + _IDENT + r')\s*\.\s*(' + _IDENT + r')\s*$')
_PROBE = '_pyarchinit_view_probe'


@dataclass(frozen=True)
class ViewStatus:
    view: str
    geometry: str
    key: str
    base: str
    base_geometry: str
    state: str          # ok | bad_key | stale | missing | broken | unsafe | unregistered
    base_indexed: bool | None   # None: base is not a registered geometry column of an existing table
    fix_sql: str | None = None
    detail: str = ''


# --- SQL helpers (pure) ----------------------------------------------------------------

def _unquote(name):
    name = name.strip()
    if len(name) >= 2 and name[0] in '"`[':
        return name[1:-1]
    return name


def _scan_top(text):
    """(index, char, depth) of every character outside quotes."""
    depth, quote = 0, None
    for i, ch in enumerate(text):
        if quote:
            if ch == quote:
                quote = None
            continue
        if ch in ('"', "'", '`'):
            quote = ch
            continue
        if ch == '[':
            quote = ']'
            continue
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        yield i, ch, depth


def _top_keyword(text, keyword):
    low, kw = text.lower(), keyword.lower()
    for i, _ch, depth in _scan_top(text):
        if depth == 0 and low.startswith(kw, i):
            before = low[i - 1] if i else ' '
            after = low[i + len(kw)] if i + len(kw) < len(low) else ' '
            if not (before.isalnum() or before == '_') and not (after.isalnum() or after == '_'):
                return i
    return None


def _split_items(select_list):
    spans, start = [], 0
    for i, ch, depth in _scan_top(select_list):
        if ch == ',' and depth == 0:
            spans.append((start, i))
            start = i + 1
    spans.append((start, len(select_list)))
    return spans


def _item(text):
    """(expression, output column name) of one select item."""
    t = text.strip()
    m = _ALIAS_RE.match(t)
    if m:
        return m.group('expr').strip(), _unquote(m.group('alias'))
    return t, _unquote(t.split('.')[-1])


def _from_tables(rest):
    out = []
    for m in re.finditer(r'(?is)\b(?:FROM|JOIN)\s+(' + _IDENT + r')(?:\s+(?:AS\s+)?(' + _IDENT + r'))?', rest):
        table, alias = m.group(1), m.group(2)
        if alias and _unquote(alias).lower() in _STOP:
            alias = None
        out.append((table, alias))
    return out


def _is_rowid_of(expr, qualifier):
    m = _QUALIFIED_RE.match(expr)
    return bool(m) and _unquote(m.group(1)).lower() == _unquote(qualifier).lower() \
        and _unquote(m.group(2)).lower() in _ROWID_NAMES


def _analyse(sql, base_table):
    """(end of 'CREATE VIEW x AS SELECT', select list, rest, base qualifier)
    or None when the view cannot be changed safely."""
    m = _HEAD_RE.match(sql or '')
    if not m:
        return None
    body = sql[m.end():]
    if re.match(r'(?is)\s*DISTINCT\b', body):
        return None
    from_pos = _top_keyword(body, 'from')
    if from_pos is None:
        return None
    rest = body[from_pos:]
    if any(_top_keyword(rest, kw) is not None for kw in ('group', 'union', 'intersect', 'except')):
        return None
    for table, alias in _from_tables(rest):
        if _unquote(table).lower() == base_table.lower():
            return m.end(), body[:from_pos], rest, alias or table
    return None


def rewrite_view_with_base_rowid(sql, base_table, key=KEY):
    """SQL of the view with ``<base>.ROWID AS <key>``: the key item is
    replaced when it comes from another table, inserted first when absent.
    Returns ``sql`` unchanged when already right, None when unsafe
    (DISTINCT / GROUP BY / UNION, base table not in FROM, unparsable)."""
    a = _analyse(sql, base_table)
    if a is None:
        return None
    head_end, select_list, rest, qualifier = a
    target = None
    for s, e in _split_items(select_list):
        expr, name = _item(select_list[s:e])
        if name.lower() == key.lower():
            if _is_rowid_of(expr, qualifier):
                return sql
            target = (s, e)
            break
    new_item = '%s.ROWID AS %s' % (qualifier, key)
    if target:
        s, e = target
        seg = select_list[s:e]
        lead, trail = seg[:len(seg) - len(seg.lstrip())], seg[len(seg.rstrip()):]
        select_list = select_list[:s] + lead + new_item + trail + select_list[e:]
    else:
        lead = select_list[:len(select_list) - len(select_list.lstrip())]
        select_list = lead + new_item + ', ' + select_list.lstrip()
    return sql[:head_end] + select_list + rest


# --- key checks on a live (or TEMP) view ---------------------------------------------

def _key_valid(con, schema, name, vg, keys, base, bgeom, sql):
    cols = {r[1].lower() for r in con.execute('PRAGMA %s.table_info("%s")' % (schema, name))}
    if vg.lower() not in cols:
        return False
    ref = '%s."%s"' % (schema, name)
    rows = con.execute('SELECT count(*) FROM %s WHERE "%s" IS NOT NULL' % (ref, vg)).fetchone()[0]
    for key in keys:
        if key.lower() not in cols:
            return False
        if rows == 0:  # nothing to compare: the definition must select the base ROWID
            a = _analyse(sql, base)
            if a is None:
                return False
            select_list, qualifier = a[1], a[3]
            items = [_item(select_list[s:e]) for s, e in _split_items(select_list)]
            if not any(n.lower() == key.lower() and _is_rowid_of(x, qualifier) for x, n in items):
                return False
            continue
        # every row must carry the ROWID of the base row whose geometry it
        # shows. A key repeated on several rows is still right: one geometry
        # joined to many attribute rows (inventario_materiali_view) shares it
        bad = con.execute(
            'SELECT count(*) FROM %s v LEFT JOIN "%s" b ON b.ROWID = v."%s" WHERE v."%s" IS NOT NULL '
            'AND (v."%s" IS NULL OR b.ROWID IS NULL OR b."%s" IS NOT v."%s")'
            % (ref, base, key, vg, key, bgeom, vg)).fetchone()[0]
        if bad:
            return False
    return True


def _probe(con, sql, vg, base, bgeom):
    """The view SQL if, created as a TEMP view, its key is the base ROWID."""
    if not sql:
        return None
    candidate = rewrite_view_with_base_rowid(sql, base) or sql
    m = _HEAD_RE.match(candidate)
    if not m:
        return None
    temp_sql = 'CREATE TEMP VIEW "%s" AS SELECT' % _PROBE + candidate[m.end():]
    try:
        con.execute('DROP VIEW IF EXISTS temp."%s"' % _PROBE)
        con.execute(temp_sql)
        # candidate, not temp_sql: an empty view is checked on its CREATE VIEW text
        ok = _key_valid(con, 'temp', _PROBE, vg, {KEY}, base, bgeom, candidate)
    except sqlite3.Error:
        ok = False
    finally:
        try:
            con.execute('DROP VIEW IF EXISTS temp."%s"' % _PROBE)
        except sqlite3.Error:
            pass
    return candidate if ok else None


def _geometry_source(sql, gcols):
    """(base table, base geometry column, view geometry column) of an
    unregistered view selecting a registered geometry column."""
    m = _HEAD_RE.match(sql or '')
    if not m:
        return None
    body = sql[m.end():]
    from_pos = _top_keyword(body, 'from')
    if from_pos is None:
        return None
    select_list, rest = body[:from_pos], body[from_pos:]
    items = [_item(select_list[s:e]) for s, e in _split_items(select_list)]
    for table, alias in _from_tables(rest):
        t = _unquote(table).lower()
        q = _unquote(alias or table).lower()
        for (gt, gg) in gcols:
            if gt != t:
                continue
            for expr, name in items:
                qm = _QUALIFIED_RE.match(expr)
                if qm and _unquote(qm.group(1)).lower() == q and _unquote(qm.group(2)).lower() == gg:
                    return t, gg, name
    return None


# --- audit / repair --------------------------------------------------------------------

def _indexed(gcols, tables, table, geom):
    """True/False: base geometry column with/without spatial index; None when
    the base is not a registered geometry column of an existing table (there
    is nothing CreateSpatialIndex could do: retrying it would mean a backup
    at every session)."""
    enabled = gcols.get((table.lower(), geom.lower()))
    if enabled is None or table.lower() not in tables:
        return None
    return enabled == 1


def audit_spatial_views(con, canonical=None):
    """Status of every registered spatial view (plus unregistered
    pyarchinit_*_view with geometry). Writes nothing to the database."""
    canonical = CANONICAL_VIEWS if canonical is None else canonical
    canon = {k.lower(): v for k, v in canonical.items()}
    try:
        regs = con.execute('SELECT view_name, view_geometry, view_rowid, f_table_name, f_geometry_column '
                           'FROM views_geometry_columns ORDER BY view_name, view_geometry').fetchall()
        gcols = {(t.lower(), g.lower()): e for t, g, e in con.execute(
            'SELECT f_table_name, f_geometry_column, spatial_index_enabled FROM geometry_columns')}
    except sqlite3.Error:
        return []
    views = {n.lower(): (n, s) for n, s in con.execute("SELECT name, sql FROM sqlite_master WHERE type = 'view'")}
    tables = {n.lower() for (n,) in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    out, registered = [], set()
    for v, vg, vr, ft, fg in regs:
        registered.add(v.lower())
        indexed = _indexed(gcols, tables, ft, fg)
        entry = views.get(v.lower())
        if entry is None:
            fix = _probe(con, canon.get(v.lower()), vg, ft, fg)
            out.append(ViewStatus(v, vg, vr, ft, fg, 'missing', indexed, fix))
            continue
        name, sql = entry
        try:
            cols = {r[1].lower() for r in con.execute('PRAGMA main.table_info("%s")' % name)}
            con.execute('SELECT 1 FROM main."%s" LIMIT 1' % name).fetchall()
        except sqlite3.Error as e:
            fix = _probe(con, canon.get(v.lower()), vg, ft, fg)
            out.append(ViewStatus(v, vg, vr, ft, fg, 'broken', indexed, fix, str(e)))
            continue
        if vg.lower() not in cols:
            out.append(ViewStatus(v, vg, vr, ft, fg, 'stale', indexed))
            continue
        try:
            ok = _key_valid(con, 'main', name, vg, {vr, KEY}, ft, fg, sql)
        except sqlite3.Error as e:
            out.append(ViewStatus(v, vg, vr, ft, fg, 'broken', indexed, None, str(e)))
            continue
        if ok:
            out.append(ViewStatus(v, vg, vr, ft, fg, 'ok', indexed))
            continue
        fix = _probe(con, sql, vg, ft, fg)
        out.append(ViewStatus(v, vg, vr, ft, fg, 'bad_key' if fix else 'unsafe', indexed, fix))
    for low, (name, sql) in sorted(views.items()):
        if low in registered or not (low.startswith('pyarchinit_') and low.endswith('_view')):
            continue
        src = _geometry_source(sql, gcols)
        if src is None:
            continue
        ft, fg, vg = src
        fix = _probe(con, sql, vg, ft, fg)
        if fix:
            out.append(ViewStatus(name, vg, KEY, ft, fg, 'unregistered', _indexed(gcols, tables, ft, fg), fix))
    return out


def needs_repair(status):
    if status.state in ('bad_key', 'stale', 'unregistered'):
        return True
    if status.state == 'missing':
        return True                      # recreate, or drop the orphan registration
    if status.state == 'broken':
        # recreate it from its canonical definition or, when its base table
        # does not exist at all, drop the registration nothing can ever draw
        return bool(status.fix_sql) or status.base_indexed is None
    return False


def _drops_registration(status):
    return status.state == 'stale' or (status.state in ('missing', 'broken') and not status.fix_sql)


def _unindexed_bases(statuses, removed):
    """Base geometry columns without spatial index of the views that are, or
    will be after the repair, usable."""
    return sorted({(s.base, s.base_geometry) for s in statuses
                   if s.base_indexed is False and (s.view, s.geometry) not in removed
                   and (s.state not in ('missing', 'broken') or s.fix_sql)})


def has_work(statuses):
    removed = {(s.view, s.geometry) for s in statuses if needs_repair(s) and _drops_registration(s)}
    return any(needs_repair(s) for s in statuses) or bool(_unindexed_bases(statuses, removed))


def _drop_registration(con, view, geometry):
    for child in _CHILDREN:
        try:
            con.execute('DELETE FROM "%s" WHERE view_name = ? AND view_geometry = ?' % child, (view, geometry))
        except sqlite3.Error:
            pass
    con.execute('DELETE FROM views_geometry_columns WHERE view_name = ? AND view_geometry = ?', (view, geometry))


def repair_spatial_views(con, statuses=None, canonical=None):
    """Apply the proven fixes; ``con`` must be in autocommit mode
    (``isolation_level = None``) with SpatiaLite loaded (CreateSpatialIndex).
    Each change runs in its own SAVEPOINT. Returns what was done."""
    if statuses is None:
        statuses = audit_spatial_views(con, canonical)
    done, recreated, removed = [], set(), set()
    for s in statuses:
        if not needs_repair(s):
            continue
        con.execute('SAVEPOINT spatial_view_repair')
        try:
            if _drops_registration(s):
                _drop_registration(con, s.view, s.geometry)
                removed.add((s.view, s.geometry))
                msg = 'registrazione rimossa %s.%s (%s)' % (s.view, s.geometry, {
                    'missing': 'vista inesistente', 'stale': 'colonna geometria assente',
                    'broken': 'tabella base %s inesistente' % s.base}[s.state])
            else:
                if s.view.lower() not in recreated:
                    con.execute('DROP VIEW IF EXISTS main."%s"' % s.view)
                    con.execute(s.fix_sql)
                    recreated.add(s.view.lower())
                if s.state == 'unregistered':
                    con.execute('INSERT INTO views_geometry_columns (view_name, view_geometry, view_rowid, '
                                'f_table_name, f_geometry_column, read_only) VALUES (?, ?, ?, ?, ?, 1)',
                                (s.view.lower(), s.geometry.lower(), KEY, s.base.lower(), s.base_geometry.lower()))
                    msg = 'vista %s registrata come spaziale' % s.view
                else:
                    con.execute('UPDATE views_geometry_columns SET view_rowid = ? '
                                'WHERE view_name = ? AND view_geometry = ?', (KEY, s.view, s.geometry))
                    msg = {'bad_key': 'vista %s: chiave = ROWID di %s',
                           'missing': 'vista %s ricreata (%s)',
                           'broken': 'vista %s ricreata (%s)'}[s.state] % (s.view, s.base)
            con.execute('RELEASE spatial_view_repair')
            done.append(msg)
        except sqlite3.Error:
            con.execute('ROLLBACK TO spatial_view_repair')
            con.execute('RELEASE spatial_view_repair')
    for base, geom in _unindexed_bases(statuses, removed):
        con.execute('SAVEPOINT spatial_view_repair')
        try:
            con.execute('DROP TABLE IF EXISTS "idx_%s_%s"' % (base, geom))
            if con.execute('SELECT CreateSpatialIndex(?, ?)', (base, geom)).fetchone()[0] != 1:
                raise sqlite3.OperationalError('CreateSpatialIndex failed')
            con.execute('SELECT UpdateLayerStatistics(?, ?)', (base, geom))
            con.execute('RELEASE spatial_view_repair')
            done.append('indice spaziale creato su %s.%s' % (base, geom))
        except sqlite3.Error:
            con.execute('ROLLBACK TO spatial_view_repair')
            con.execute('RELEASE spatial_view_repair')
    return done
