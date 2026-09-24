"""Copy a whole pyArchInit database into another one, in one go.

The import tab of the configuration dialog moved one table at a time,
and the code that moved it named every column by hand — about 1.800
lines, written twice (once for a single table, once for the "ALL"
entry). That is why sheets were missing: budget, personale, presenze,
attrezzature, computo metrico, inventario lapidei, archeozoologia,
detsesso, deteta and the geometries were simply never written down
(2026-09-24).

Here the columns come from the mapper, so every mapped table is copied
the same way and a sheet added tomorrow travels with the others. A
geometry is a column like any other: the mappers declare it with
GeoAlchemy2, it is read as EWKB with its SRID and written back as such.

Two things the destination can refuse:

- a SpatiaLite database created from the shipped template registers its
  geometry columns with ``srid = -1`` and rejects anything else
  ("violates Geometry constraint"). When the destination table is still
  empty, the column is registered again with the SRID of the data
  (DiscardGeometryColumn + RecoverGeometryColumn).
- PostgreSQL asks for rights: pyArchInit's own schema declares the
  geometry columns without a fixed SRID, so the data goes in as it is,
  but a user who cannot write a table gets an error for that table and
  the migration carries on with the others.

Pure Python: no Qt, no dialogs. The caller decides what to show.
"""
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import class_mapper, sessionmaker

# Order matters: a site before what stands on it, the media links last
# (they point at the records copied before them).
ALPHANUMERIC_TABLES = (
    'SITE',
    'PERIODIZZAZIONE',
    'US',
    'UT',
    'STRUTTURA',
    'TOMBA',
    'SCHEDAIND',
    'DETSESSO',
    'DETETA',
    'ARCHEOZOOLOGY',
    'FAUNA',
    'CAMPIONI',
    'DOCUMENTAZIONE',
    'INVENTARIO_MATERIALI',
    'INVENTARIO_LAPIDEI',
    'POTTERY',
    'TMA',
    'TMA_MATERIALI',
    'PDF_ADMINISTRATOR',
    'PYARCHINIT_THESAURUS_SIGLE',
    # cantiere
    'PERSONALE',
    'PRESENZE',
    'ATTREZZATURE',
    'BUDGET',
    'COMPUTO_METRICO',
)

GEOMETRY_TABLES = (
    'PYSITO_POINT',
    'PYSITO_POLYGON',
    'PYUS',
    'PYUSM',
    'PYUS_NEGATIVE',
    'PYQUOTE',
    'PYQUOTEUSM',
    'PYSTRUTTURE',
    'PYREPERTI',
    'PYINDIVIDUI',
    'PYCAMPIONI',
    'PYTOMBA',
    'PYSEZIONI',
    'PYDOCUMENTAZIONE',
    'PYLINEERIFERIMENTO',
    'PYRIPARTIZIONI_SPAZIALI',
)

MEDIA_TABLES = ('MEDIA', 'MEDIA_THUMB', 'MEDIATOENTITY')

ALL_TABLES = ALPHANUMERIC_TABLES + GEOMETRY_TABLES + MEDIA_TABLES

# Tables nobody migrates: they belong to the installation, not to the
# excavation (and hold passwords), or they are views and staging tables.
NOT_MIGRATED = ('PYARCHINIT_USERS', 'PYARCHINIT_ROLES', 'PYARCHINIT_PERMISSIONS',
                'PYARCHINIT_AUDIT_LOG', 'PYARCHINIT_ACCESS_LOG', 'MEDIAVIEW',
                'US_TOIMP', 'INVENTARIO_MATERIALI_TOIMP')

# Sheets the table-by-table import never learned to write: picking them
# did nothing at all. They now travel through this engine, alone or with
# the others.
HANDLED_BY_MIGRATOR = ('ARCHEOZOOLOGY', 'DETSESSO', 'DETETA', 'TMA_MATERIALI', 'FAUNA',
                       'INVENTARIO_LAPIDEI', 'PDF_ADMINISTRATOR', 'PERSONALE', 'PRESENZE',
                       'ATTREZZATURE', 'BUDGET', 'COMPUTO_METRICO')

# SpatiaLite writes the kind of geometry as a number; RecoverGeometryColumn
# wants its name back.
_SPATIALITE_TYPES = {1: 'POINT', 2: 'LINESTRING', 3: 'POLYGON', 4: 'MULTIPOINT',
                     5: 'MULTILINESTRING', 6: 'MULTIPOLYGON', 7: 'GEOMETRYCOLLECTION'}

COMMIT_EVERY = 500


class TableOutcome(object):
    """What happened to one table."""

    def __init__(self, name):
        self.name = name
        self.read = 0           # rows found in the source
        self.written = 0        # rows that reached the destination
        self.skipped = 0        # rows the destination refused (duplicates included)
        self.existing = 0       # rows the destination already held
        self.error = ''         # why the whole table could not be copied
        self.srid_aligned = 0   # SRID the destination was registered again with

    @property
    def ok(self):
        return not self.error and self.skipped == 0

    def __repr__(self):
        return '<%s: %d/%d%s>' % (self.name, self.written, self.read,
                                  ', ' + self.error if self.error else '')


def _mapper_of(manager, name):
    """The SQLAlchemy mapper behind a pyArchInit table name."""
    from modules.db import pyarchinit_db_mapper as m
    return class_mapper(getattr(m, name))


def _is_sqlite(manager):
    return manager.engine.dialect.name == 'sqlite'


def geometry_column(mapper):
    """The name of the geometry column of a mapped table, if it has one."""
    for column in mapper.columns:
        if type(column.type).__name__ == 'Geometry':
            return column.name
    return None


def _sqlite_registration(engine, table):
    """(kind, srid) SpatiaLite registered for a geometry column."""
    with engine.connect() as conn:
        row = conn.execute(text("SELECT geometry_type, srid FROM geometry_columns "
                                "WHERE lower(f_table_name) = lower(:t)"),
                           {'t': table}).fetchone()
    return (int(row[0]), int(row[1])) if row else None


def _empty_to_null(mapper):
    """SQLite keeps an empty string in a number column, PostgreSQL
    refuses it ("invalid input syntax for type bigint"). Give the
    destination a NULL instead — an empty box is an empty box."""
    textual = set()
    for column in mapper.columns:
        kind = type(column.type).__name__.lower()
        if 'char' in kind or 'text' in kind or 'string' in kind or 'geometry' in kind:
            textual.add(column.name)

    def coerce(name, value):
        if value == '' and name not in textual:
            return None
        return value

    return coerce


def _advance_sequence(manager, table, column):
    """After writing rows with their own identifiers, PostgreSQL still
    hands out the next one from where its counter stopped: move it past
    what was just written, or the first record saved from the sheet
    collides with a copied one."""
    if manager.engine.dialect.name != 'postgresql':
        return
    with manager.engine.begin() as conn:
        conn.execute(text(
            "SELECT setval(pg_get_serial_sequence('\"%s\"', '%s'), "
            "COALESCE((SELECT MAX(\"%s\") FROM \"%s\"), 1))" % (table, column, column, table)))


def _row_count(manager, table):
    with manager.engine.connect() as conn:
        return conn.execute(text('SELECT count(*) FROM "%s"' % table)).scalar()


def align_geometry_srid(manager, table, srid):
    """Register the geometry column of a SpatiaLite table again with the
    SRID of the data. Returns the SRID applied, or 0 when nothing was
    done (already right, not SpatiaLite, or the table is not empty:
    geometries already there would be left with the wrong SRID)."""
    if not _is_sqlite(manager) or not srid:
        return 0
    registration = _sqlite_registration(manager.engine, table)
    if not registration:
        return 0
    kind, current = registration
    if current == srid:
        return 0
    if _row_count(manager, table):
        return 0
    name = _SPATIALITE_TYPES.get(kind % 1000, 'GEOMETRY')
    with manager.engine.begin() as conn:
        conn.execute(text("SELECT DiscardGeometryColumn(:t, 'the_geom')"), {'t': table})
        conn.execute(text("SELECT RecoverGeometryColumn(:t, 'the_geom', :s, :k, 'XY')"),
                     {'t': table, 's': srid, 'k': name})
        conn.execute(text("SELECT CreateSpatialIndex(:t, 'the_geom')"), {'t': table})
    return srid


def copy_table(read_manager, write_manager, name, on_row=None, search_dict=None):
    """Copy every row of one table from one database to the other.

    The columns come from the mapper, the primary key is renumbered from
    the highest one already in the destination, and each row is written
    inside its own savepoint: one row the destination refuses (a
    duplicate, a value it does not like) is counted and the others still
    travel.
    """
    outcome = TableOutcome(name)
    try:
        mapper = _mapper_of(read_manager, name)
    except Exception as exc:                       # a name nobody mapped
        outcome.error = 'tabella non mappata (%s)' % exc
        return outcome

    columns = [c.name for c in mapper.columns]
    primary_key = [c.name for c in mapper.primary_key][0]
    table_name = mapper.local_table.name

    try:
        rows = read_manager.query_bool(search_dict or {}, name)
    except Exception as exc:
        outcome.error = 'lettura: %s' % _short(exc)
        return outcome
    outcome.read = len(rows)
    try:
        outcome.existing = _row_count(write_manager, table_name)
    except Exception:
        pass                                       # the count is only for the report
    if not rows:
        return outcome

    geometry = geometry_column(mapper)
    if geometry:
        srid = next((getattr(r, geometry).srid for r in rows
                     if getattr(r, geometry) is not None), 0)
        try:
            outcome.srid_aligned = align_geometry_srid(write_manager, table_name, srid)
        except Exception as exc:
            outcome.error = 'SRID: %s' % _short(exc)
            return outcome

    # An empty destination keeps the identifiers of the source: the links
    # between records (a thumbnail to its media, a media to the US it
    # belongs to) are made of those numbers, and renumbering would break
    # them. A destination that already holds rows cannot: there the
    # numbers continue from the highest one, and the links of what is
    # copied may not find their target.
    keep_ids = not outcome.existing
    next_id = 0
    if not keep_ids:
        try:
            next_id = (write_manager.max_num_id(name, primary_key) or 0) + 1
        except Exception as exc:
            outcome.error = 'scrittura: %s' % _short(exc)
            return outcome

    coerce = _empty_to_null(mapper)
    session = sessionmaker(bind=write_manager.engine)()
    try:
        for done, row in enumerate(rows, start=1):
            record = mapper.class_manager.new_instance()
            for column in columns:
                setattr(record, column, coerce(column, getattr(row, column, None)))
            if not keep_ids:
                setattr(record, primary_key, next_id)
            try:
                with session.begin_nested():
                    session.add(record)
                outcome.written += 1
                if not keep_ids:
                    next_id += 1
            except Exception as exc:
                outcome.skipped += 1
                if not outcome.error:
                    outcome.error = _short(exc)
            if done % COMMIT_EVERY == 0:
                session.commit()
            if on_row is not None:
                on_row(done, outcome.read)
        session.commit()
    except Exception as exc:
        session.rollback()
        outcome.error = _short(exc)
    finally:
        session.close()

    if outcome.written and keep_ids:
        try:
            _advance_sequence(write_manager, table_name, primary_key)
        except Exception:
            pass                                   # a counter, not the data
    return outcome


def migrate(read_manager, write_manager, tables=None, on_table=None, on_row=None,
            search_dict=None):
    """Copy the tables (all of them by default) and return one outcome
    each. A table that fails does not stop the ones after it."""
    names = list(tables) if tables else list(ALL_TABLES)
    outcomes = []
    for index, name in enumerate(names):
        if on_table is not None:
            on_table(index, len(names), name)
        outcomes.append(copy_table(read_manager, write_manager, name, on_row=on_row,
                                   search_dict=search_dict))
    return outcomes


def already_filled(write_manager, tables=None):
    """Which destination tables already hold rows, and how many.

    Tables protected by a unique constraint refuse a record they already
    have, but the others (us_table, the geometries, the thesaurus) would
    take a second copy of everything: whoever runs the migration twice
    must be told before, not after.
    """
    filled = []
    for name in (tables or ALL_TABLES):
        try:
            mapper = _mapper_of(write_manager, name)
            rows = _row_count(write_manager, mapper.local_table.name)
        except Exception:
            continue                               # missing table: copy_table will say so
        if rows:
            filled.append((name, rows))
    return filled


def summary(outcomes):
    """A few lines a dialog can show: what travelled, what did not."""
    copied = [o for o in outcomes if o.written]
    empty = [o for o in outcomes if not o.read and not o.error]
    trouble = [o for o in outcomes if o.error or o.skipped]
    lines = ['Tabelle copiate: %d di %d — righe: %d'
             % (len(copied), len(outcomes), sum(o.written for o in copied))]
    for o in copied:
        note = ' (SRID %d)' % o.srid_aligned if o.srid_aligned else ''
        lines.append('  %s: %d righe%s' % (o.name, o.written, note))
    if trouble:
        lines.append('')
        lines.append('Da controllare:')
        for o in trouble:
            detail = o.error or ''
            if o.skipped:
                detail = '%d righe non scritte%s' % (o.skipped, ' — ' + detail if detail else '')
            lines.append('  %s: %s' % (o.name, detail))
    if empty:
        lines.append('')
        lines.append('Vuote nell\'origine: %s' % ', '.join(o.name for o in empty))
    return '\n'.join(lines)


def _short(exc):
    """The first line of a database error, without the SQL behind it."""
    text_ = str(getattr(exc, 'orig', exc)).strip()
    return text_.splitlines()[0][:200] if text_ else exc.__class__.__name__
