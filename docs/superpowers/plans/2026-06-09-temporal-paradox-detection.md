# Feature B — Temporal paradox detection — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the Verifica rapporti with temporal-paradox detection — period assignments that contradict the stratigraphy — with majority-heuristic auto-fix (moving periods), reciprocal-aware suggestions, dry-run preview, auto-backup and rollback.

**Architecture:** New Qt-free `modules/utility/temporal_check.py` (chronology readers + pure detection/solve), integrated into `rapporti_check.check_rapporti` via two optional params (`chrono`, `unit_periods`). `Edit` gains `set_fields` so the existing apply/rollback writes period columns too. UI unchanged in structure.

**Tech Stack:** Python 3, SQLAlchemy (DbHandle), PyQt (QGIS), pytest.

**Spec:** `docs/superpowers/specs/2026-06-09-temporal-paradox-detection-design.md`

---

## Riferimenti chiave (verificati nel codice)

- `modules/utility/rapporti_check.py`: `Edit(frozen: us, add=(), remove=())`; `Issue(kind, us_path, auto, summary, edits=[])`; `RapportiReport(sito, issues)`; `check_rapporti(graph, *, sito, lang="it", validate=True, inverse_label=None)`; `apply_edits(edits, handle, *, sito) -> RollbackToken`; `rollback(token, handle)`; `_real_us(node)` (None for `_synth_*`/placeholders); `_strat_edges(graph)` → `[(s,t,et)]` excluding `NON_RAPPORTI_EDGE_TYPES`; `_utok(us, lang)`; `_t(lang, key)`; `_L` localization dict (it/en/de/es/fr/pt); `kind_title(kind, lang)`; `_coerce_to_list`.
- Graph nodes carry `attributes['us']`, `periodo_iniziale`, `fase_iniziale` — **NOT** `periodo_finale`/`fase_finale` (projector `graph_projector.py:736-739` only attaches the iniziale pair). → period spans must be read from `us_table` (`load_unit_periods`).
- `periodizzazione_table`: `periodo` (Integer), `fase` (Text), `cron_iniziale` (Integer), `cron_finale` (Integer); higher cron = more recent.
- `us_table`: `periodo_iniziale/fase_iniziale/periodo_finale/fase_finale` (String), `rapporti` (Text).
- `DbHandle`: `.engine`. Backup: `scripts/migrations/_common.py` → `auto_backup_sqlite(Path, tag)`, `auto_backup_postgres(engine, tag, dest_dir)`, `BackupSkipped`.
- Test fakes pattern (reuse): `_N(nid, ut, rap=None, us=None, node_type="US")`, `_E(s,t,et)`, `_G(nodes, edges)` with `find_node_by_id` (see `tests/sync/test_rapporti_check.py:6-30`).
- **Circular-import guard:** `temporal_check` imports helpers from `rapporti_check` at top level; `rapporti_check` imports `temporal_check` **lazily inside `check_rapporti`** (function-level) — never at module top.
- Column names written via `set_fields` are a fixed whitelist (period columns) → safe to interpolate into SQL.

## File Structure

| File | Tipo | Responsabilità |
|---|---|---|
| `modules/utility/temporal_check.py` | **Create** | `_classify_relation` + constants; `build_chronology`/`load_unit_periods` (DB); `unit_span` + `detect_temporal` + `solve_fixes` + helpers (pure) |
| `modules/utility/rapporti_check.py` | **Modify** | `Edit.set_fields`; generalize `apply_edits`/`rollback`; add temporal kinds + `_L` templates; call `temporal_check` in `check_rapporti(... chrono, unit_periods)` |
| `gui/rapporti_check_dialog.py` | **Modify** | build `chrono`+`unit_periods`, pass to `check_rapporti`; auto-backup pre-apply if `set_fields`; `_preview` shows `set_fields` |
| `tests/sync/test_temporal_check.py` | **Create** | unit + integration |
| `tests/sync/test_rapporti_check.py` | **Modify** | apply/rollback with `set_fields` |
| `dev_logs/CHANGELOG.md` | **Modify** | bilingual entry (agent) |
| `docs/tutorials/<lang>/36_extended_matrix_s3dgraphy.md` | **Modify** | temporal-paradox section (agent) |

---

## Task 1: Relation classification (pure)

**Files:**
- Create: `modules/utility/temporal_check.py`
- Test: `tests/sync/test_temporal_check.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/sync/test_temporal_check.py
from modules.utility import temporal_check as TC

def test_classify_relation():
    for et in ("overlies", "cuts", "fills", "abuts", "is_after"):
        assert TC._classify_relation(et) == "later"
    for et in ("is_overlain_by", "is_cut_by", "is_filled_by",
               "is_abutted_by", "is_before"):
        assert TC._classify_relation(et) == "earlier"
    for et in ("is_physically_equal_to", "is_bonded_to"):
        assert TC._classify_relation(et) == "contemp"
    assert TC._classify_relation("generic_connection") is None
    assert TC._classify_relation(None) is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/sync/test_temporal_check.py -q`
Expected: FAIL — `ModuleNotFoundError: modules.utility.temporal_check`.

- [ ] **Step 3: Write minimal implementation**

```python
# modules/utility/temporal_check.py
"""Temporal/stratigraphic paradox detection for Verifica rapporti (pyArchInit).

Qt-free. Detects when stratigraphic relations contradict period/phase ordering,
using periodizzazione_table chronology (cron_iniziale/finale). Stratigraphy is
the observed reference; auto-fixes move PERIODS (not relations). See
docs/superpowers/specs/2026-06-09-temporal-paradox-detection-design.md.

Import note: this module imports helpers from rapporti_check at top level;
rapporti_check imports THIS module lazily (inside check_rapporti) to avoid a
circular import.
"""
from __future__ import annotations

from modules.utility.rapporti_check import (
    Edit, Issue, _real_us, _strat_edges, _utok, _t,
)

# Issue kinds
TEMPORAL_INVERSION = "temporal_inversion"
TEMPORAL_CONTEMPORANEITY = "temporal_contemporaneity"
TEMPORAL_UNEVALUABLE = "temporal_unevaluable"

#: source is MORE RECENT than target
_LATER = frozenset({"overlies", "cuts", "fills", "abuts", "is_after"})
#: source is MORE ANCIENT than target
_EARLIER = frozenset({"is_overlain_by", "is_cut_by", "is_filled_by",
                      "is_abutted_by", "is_before"})
#: contemporaneous (same period required)
_CONTEMP = frozenset({"is_physically_equal_to", "is_bonded_to"})


def _classify_relation(et):
    """Map an edge type to 'later' | 'earlier' | 'contemp' | None."""
    if et in _LATER:
        return "later"
    if et in _EARLIER:
        return "earlier"
    if et in _CONTEMP:
        return "contemp"
    return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/sync/test_temporal_check.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add modules/utility/temporal_check.py tests/sync/test_temporal_check.py
git -c commit.gpgsign=false commit -m "feat(temporal): relation classification (later/earlier/contemp)"
```

---

## Task 2: Chronology readers + `unit_span`

**Files:**
- Modify: `modules/utility/temporal_check.py`
- Test: `tests/sync/test_temporal_check.py`

- [ ] **Step 1: Write the failing test** (append)

```python
import sqlite3
from pathlib import Path
from modules.s3dgraphy.sync._db_handle import DbHandle

def _db(tmp_path):
    p = tmp_path / "t.sqlite"
    c = sqlite3.connect(p)
    c.executescript(
        "CREATE TABLE periodizzazione_table (sito TEXT, periodo INTEGER,"
        " fase TEXT, cron_iniziale INTEGER, cron_finale INTEGER);"
        "CREATE TABLE us_table (sito TEXT, us TEXT, periodo_iniziale TEXT,"
        " fase_iniziale TEXT, periodo_finale TEXT, fase_finale TEXT);")
    c.execute("INSERT INTO periodizzazione_table VALUES ('S',1,'1',-100,0)")
    c.execute("INSERT INTO periodizzazione_table VALUES ('S',2,'1',0,100)")
    c.execute("INSERT INTO periodizzazione_table VALUES ('S',3,'1',100,200)")
    c.execute("INSERT INTO us_table VALUES ('S','US5','1','1','1','1')")
    c.execute("INSERT INTO us_table VALUES ('S','US7','3','1','3','1')")
    c.execute("INSERT INTO us_table VALUES ('S','US9',NULL,NULL,NULL,NULL)")
    c.commit(); c.close()
    return DbHandle.from_path(p)

def test_build_chronology(tmp_path):
    chrono = TC.build_chronology(_db(tmp_path), "S")
    assert chrono[("1", "1")] == (-100, 0)
    assert chrono[("3", "1")] == (100, 200)

def test_load_unit_periods(tmp_path):
    up = TC.load_unit_periods(_db(tmp_path), "S")
    assert up["US5"] == ("1", "1", "1", "1")
    assert up["US9"] == ("", "", "", "")

def test_unit_span(tmp_path):
    chrono = TC.build_chronology(_db(tmp_path), "S")
    assert TC.unit_span(("1", "1", "1", "1"), chrono) == (-100, 0)
    assert TC.unit_span(("1", "1", "3", "1"), chrono) == (-100, 200)  # span both
    assert TC.unit_span(("", "", "", ""), chrono) is None
    assert TC.unit_span(("9", "1", "9", "1"), chrono) is None  # no such period

def test_unit_span_fase_fallback(tmp_path):
    chrono = TC.build_chronology(_db(tmp_path), "S")
    # blank fase -> aggregate over the periodo
    assert TC.unit_span(("2", "", "2", ""), chrono) == (0, 100)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/sync/test_temporal_check.py -q`
Expected: FAIL — `AttributeError: module ... has no attribute 'build_chronology'`.

- [ ] **Step 3: Write minimal implementation** (append)

```python
def build_chronology(handle, sito):
    """(periodo, fase) -> (cron_iniziale, cron_finale) for *sito*."""
    from sqlalchemy import text
    out = {}
    with handle.engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT periodo, fase, cron_iniziale, cron_finale "
            "FROM periodizzazione_table WHERE sito = :s"), {"s": sito}).fetchall()
    for periodo, fase, ci, cf in rows:
        key = ("" if periodo is None else str(periodo),
               "" if fase is None else str(fase))
        out[key] = (None if ci is None else int(ci),
                    None if cf is None else int(cf))
    return out


def load_unit_periods(handle, sito):
    """us -> (periodo_iniziale, fase_iniziale, periodo_finale, fase_finale)."""
    from sqlalchemy import text
    out = {}
    with handle.engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT us, periodo_iniziale, fase_iniziale, periodo_finale, "
            "fase_finale FROM us_table WHERE sito = :s"), {"s": sito}).fetchall()
    for us, pi, fi, pf, ff in rows:
        if us is None:
            continue
        out[str(us)] = ("" if pi is None else str(pi),
                        "" if fi is None else str(fi),
                        "" if pf is None else str(pf),
                        "" if ff is None else str(ff))
    return out


def _cron_of(periodo, fase, chrono, which):
    """cron_iniziale (which='ini') or cron_finale (which='fin') of (periodo,
    fase). Falls back to aggregating over all fasi of the periodo when the
    exact (periodo, fase) row is absent (blank fase tolerance)."""
    rec = chrono.get((str(periodo), str(fase)))
    if rec is not None:
        return rec[0] if which == "ini" else rec[1]
    vals = [v[0 if which == "ini" else 1]
            for (p, _f), v in chrono.items()
            if p == str(periodo) and v[0 if which == "ini" else 1] is not None]
    if not vals:
        return None
    return min(vals) if which == "ini" else max(vals)


def unit_span(periods, chrono):
    """periods = (pi, fi, pf, ff) -> (cron_ini, cron_fin) or None if undatable."""
    if periods is None:
        return None
    pi, fi, pf, ff = periods
    if not pi or not pf:
        return None
    ci = _cron_of(pi, fi, chrono, "ini")
    cf = _cron_of(pf, ff, chrono, "fin")
    if ci is None or cf is None:
        return None
    return (ci, cf)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/sync/test_temporal_check.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add modules/utility/temporal_check.py tests/sync/test_temporal_check.py
git -c commit.gpgsign=false commit -m "feat(temporal): chronology + unit-period readers + unit_span"
```

---

## Task 3: `detect_temporal` + localized summaries

**Files:**
- Modify: `modules/utility/temporal_check.py`, `modules/utility/rapporti_check.py` (_L templates)
- Test: `tests/sync/test_temporal_check.py`

- [ ] **Step 1: Write the failing test** (append)

```python
class _N:
    def __init__(self, nid, us=None, node_type="US"):
        self.node_id = nid; self.name = nid; self.node_type = node_type
        self.attributes = {"unita_tipo": "US"}
        if us is not None:
            self.attributes["us"] = us
class _E:
    def __init__(self, s, t, et):
        self.edge_source = s; self.edge_target = t; self.edge_type = et
class _G:
    def __init__(self, nodes, edges): self.nodes = nodes; self.edges = edges
    def find_node_by_id(self, nid):
        return next((n for n in self.nodes if n.node_id == nid), None)

_CHRONO = {("1", "1"): (-100, 0), ("2", "1"): (0, 100), ("3", "1"): (100, 200)}

def test_detect_inversion():
    # US5 (period 1, old) OVERLIES US7 (period 3, new) -> inversion
    g = _G([_N("a", us="US5"), _N("b", us="US7")], [_E("a", "b", "overlies")])
    up = {"US5": ("1", "1", "1", "1"), "US7": ("3", "1", "3", "1")}
    iss = TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it")
    assert [i.kind for i in iss] == [TC.TEMPORAL_INVERSION]
    assert iss[0].us_path == ["US5", "US7"]   # [later, earlier]

def test_no_inversion_same_or_overlapping_period():
    g = _G([_N("a", us="US5"), _N("b", us="US7")], [_E("a", "b", "overlies")])
    up = {"US5": ("3", "1", "3", "1"), "US7": ("1", "1", "1", "1")}  # correct order
    assert TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it") == []
    up2 = {"US5": ("2", "1", "2", "1"), "US7": ("2", "1", "2", "1")}  # same period
    assert TC.detect_temporal(g, _CHRONO, up2, sito="S", lang="it") == []

def test_detect_contemporaneity_disjoint():
    g = _G([_N("a", us="US5"), _N("b", us="US7")],
           [_E("a", "b", "is_physically_equal_to")])
    up = {"US5": ("1", "1", "1", "1"), "US7": ("3", "1", "3", "1")}
    iss = TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it")
    assert [i.kind for i in iss] == [TC.TEMPORAL_CONTEMPORANEITY]

def test_unevaluable_when_one_dated_one_not():
    g = _G([_N("a", us="US5"), _N("b", us="US9")], [_E("a", "b", "overlies")])
    up = {"US5": ("1", "1", "1", "1"), "US9": ("", "", "", "")}
    iss = TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it")
    assert [i.kind for i in iss] == [TC.TEMPORAL_UNEVALUABLE]

def test_placeholder_excluded():
    g = _G([_N("a", us="US5"), _N("b")], [_E("a", "b", "overlies")])  # b us=None
    up = {"US5": ("1", "1", "1", "1")}
    assert TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it") == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/sync/test_temporal_check.py -q`
Expected: FAIL — `AttributeError: ... 'detect_temporal'`.

- [ ] **Step 3a: Add localization templates** to `modules/utility/rapporti_check.py` — inside EACH language block of `_L` (it, en, de, es, fr, pt), add these keys. Italian shown; translate the others naturally (titles + the three summaries). For languages whose block you cannot translate confidently, the existing `_t` fallback to English covers them, so add at least `it` and `en` fully and the rest may copy English.

Italian (`_L["it"]`):
```python
        "t_temporal_inversion": "Paradosso temporale (inversione di periodo)",
        "t_temporal_contemporaneity": "Paradosso temporale (contemporaneità non sovrapposta)",
        "t_temporal_unevaluable": "Coerenza temporale non valutabile (periodo mancante)",
        "s_temporal_inv": "{a} (periodo {pa}) risulta interamente più antica di "
                          "{b} (periodo {pb}) pur essendone stratigraficamente più "
                          "recente — sposta {a} a un periodo ≥ {pb}, oppure {b} ≤ "
                          "{pa}, oppure verifica il rapporto",
        "s_temporal_contemp": "{a} (periodo {pa}) e {b} (periodo {pb}) sono "
                              "dichiarate contemporanee ma i periodi non si "
                              "sovrappongono — assegnale allo stesso periodo",
        "s_temporal_uneval": "{a} è in relazione d'ordine con {b} ma manca la "
                             "datazione di periodo per valutarne la coerenza — "
                             "assegna il periodo mancante",
```

English (`_L["en"]`):
```python
        "t_temporal_inversion": "Temporal paradox (period inversion)",
        "t_temporal_contemporaneity": "Temporal paradox (non-overlapping contemporaneity)",
        "t_temporal_unevaluable": "Temporal consistency not evaluable (missing period)",
        "s_temporal_inv": "{a} (period {pa}) is entirely older than {b} (period "
                          "{pb}) yet stratigraphically more recent — move {a} to a "
                          "period ≥ {pb}, or {b} ≤ {pa}, or check the relationship",
        "s_temporal_contemp": "{a} (period {pa}) and {b} (period {pb}) are declared "
                              "contemporary but their periods do not overlap — "
                              "assign them to the same period",
        "s_temporal_uneval": "{a} has an order relationship with {b} but a period "
                             "date is missing to evaluate consistency — assign the "
                             "missing period",
```

Add the same six keys to `_L["de"]`, `_L["es"]`, `_L["fr"]`, `_L["pt"]` (translated; English values are acceptable as fallback if a confident translation isn't available).

- [ ] **Step 3b: Implement `detect_temporal`** (append to `temporal_check.py`)

```python
def _node_us_map(graph):
    m = {}
    for n in getattr(graph, "nodes", None) or []:
        u = _real_us(n)
        if u is not None:
            m[n.node_id] = str(u)
    return m


def _periodo(us, unit_periods):
    p = unit_periods.get(us)
    return p[0] if p and p[0] else "?"


def detect_temporal(graph, chrono, unit_periods, *, sito, lang="it"):
    """Return temporal-paradox Issues (no edits yet — see solve_fixes)."""
    issues = []
    if not chrono:
        return issues
    id_to_us = _node_us_map(graph)
    seen = set()

    def span(us):
        return unit_span(unit_periods.get(us), chrono)

    for (s, t, et) in _strat_edges(graph):
        rel = _classify_relation(et)
        if rel is None:
            continue
        us_s, us_t = id_to_us.get(s), id_to_us.get(t)
        if not us_s or not us_t or us_s == us_t:
            continue
        if rel == "contemp":
            key = ("c", frozenset((us_s, us_t)))
            if key in seen:
                continue
            seen.add(key)
            sp_s, sp_t = span(us_s), span(us_t)
            if sp_s is None or sp_t is None:
                # dated + undated → gap-fillable; both undated → skip
                if sp_s is None and sp_t is None:
                    continue
                issues.append(Issue(
                    TEMPORAL_CONTEMPORANEITY, [us_s, us_t], False,
                    _t(lang, "s_temporal_contemp").format(
                        a=_utok(us_s, lang), pa=_periodo(us_s, unit_periods),
                        b=_utok(us_t, lang), pb=_periodo(us_t, unit_periods))))
                continue
            if sp_s[1] < sp_t[0] or sp_t[1] < sp_s[0]:
                issues.append(Issue(
                    TEMPORAL_CONTEMPORANEITY, [us_s, us_t], False,
                    _t(lang, "s_temporal_contemp").format(
                        a=_utok(us_s, lang), pa=_periodo(us_s, unit_periods),
                        b=_utok(us_t, lang), pb=_periodo(us_t, unit_periods))))
            continue
        # order relation → normalize to (later, earlier)
        later, earlier = (us_s, us_t) if rel == "later" else (us_t, us_s)
        key = ("i", later, earlier)
        if key in seen:
            continue
        seen.add(key)
        sp_l, sp_e = span(later), span(earlier)
        if sp_l is None or sp_e is None:
            # only actionable if one side is dated (hint to date the other)
            if sp_l is None and sp_e is None:
                continue
            issues.append(Issue(
                TEMPORAL_UNEVALUABLE, [later, earlier], False,
                _t(lang, "s_temporal_uneval").format(
                    a=_utok(later, lang), b=_utok(earlier, lang))))
            continue
        if sp_l[1] < sp_e[0]:   # later entirely before earlier → inversion
            issues.append(Issue(
                TEMPORAL_INVERSION, [later, earlier], False,
                _t(lang, "s_temporal_inv").format(
                    a=_utok(later, lang), pa=_periodo(later, unit_periods),
                    b=_utok(earlier, lang), pb=_periodo(earlier, unit_periods))))
    return issues
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/sync/test_temporal_check.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add modules/utility/temporal_check.py modules/utility/rapporti_check.py tests/sync/test_temporal_check.py
git -c commit.gpgsign=false commit -m "feat(temporal): detect_temporal (inversion/contemporaneity/unevaluable) + i18n"
```

---

## Task 4: `solve_fixes` (majority heuristic + target period)

**Files:**
- Modify: `modules/utility/temporal_check.py`
- Test: `tests/sync/test_temporal_check.py`

- [ ] **Step 1: Write the failing test** (append)

```python
def _mk(rels):
    """rels = list of (src_us, edge_type, tgt_us). Returns graph with one
    node per us."""
    us_set = {u for (s, _e, t) in rels for u in (s, t)}
    nodes = [_N(u, us=u) for u in us_set]
    edges = [_E(s, t, e) for (s, e, t) in rels]
    return _G(nodes, edges)

def test_solve_tie_leaves_suggestion():
    g = _mk([("US5", "overlies", "US7")])
    up = {"US5": ("1", "1", "1", "1"), "US7": ("3", "1", "3", "1")}
    iss = TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it")
    TC.solve_fixes(iss, g, _CHRONO, up, sito="S")
    assert iss[0].auto is False and iss[0].edits == []  # 1 vs 1 conflict = tie

def test_solve_moves_majority_outlier():
    # US5 covers US7 and US8; US5 wrongly in period 1 (older) -> US5 is outlier
    g = _mk([("US5", "overlies", "US7"), ("US5", "overlies", "US8")])
    up = {"US5": ("1", "1", "1", "1"),
          "US7": ("3", "1", "3", "1"), "US8": ("3", "1", "3", "1")}
    iss = TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it")
    TC.solve_fixes(iss, g, _CHRONO, up, sito="S")
    inv = [i for i in iss if i.kind == TC.TEMPORAL_INVERSION]
    assert inv and all(i.auto for i in inv)
    moved = inv[0].edits[0]
    assert moved.us == "US5"
    assert dict(moved.set_fields)["periodo_iniziale"] == "3"  # minimal move to ≥3

def test_solve_skips_multiperiod_unit():
    g = _mk([("CON_US5", "overlies", "US7"), ("CON_US5", "overlies", "US8")])
    up = {"CON_US5": ("1", "1", "2", "1"),    # spans periods -> not auto-movable
          "US7": ("3", "1", "3", "1"), "US8": ("3", "1", "3", "1")}
    iss = TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it")
    TC.solve_fixes(iss, g, _CHRONO, up, sito="S")
    inv = [i for i in iss if i.kind == TC.TEMPORAL_INVERSION]
    assert inv and all(i.edits == [] for i in inv)  # suggestion only

def test_solve_gap_fill_contemporaneity():
    g = _mk([("US5", "is_bonded_to", "US9")])
    up = {"US5": ("2", "1", "2", "1"), "US9": ("", "", "", "")}
    iss = TC.detect_temporal(g, _CHRONO, up, sito="S", lang="it")
    TC.solve_fixes(iss, g, _CHRONO, up, sito="S")
    c = [i for i in iss if i.kind == TC.TEMPORAL_CONTEMPORANEITY][0]
    assert c.auto is True
    assert c.edits[0].us == "US9"
    assert dict(c.edits[0].set_fields)["periodo_iniziale"] == "2"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/sync/test_temporal_check.py -q`
Expected: FAIL — `AttributeError: ... 'solve_fixes'`.

- [ ] **Step 3: Write minimal implementation** (append)

```python
def _build_adjacency(graph, id_to_us):
    """us -> list of (neighbor_us, role) where role describes us vs neighbor:
    'later' (us is later than nb), 'earlier', or 'contemp'."""
    adj = {}
    for (s, t, et) in _strat_edges(graph):
        rel = _classify_relation(et)
        if rel is None:
            continue
        us_s, us_t = id_to_us.get(s), id_to_us.get(t)
        if not us_s or not us_t or us_s == us_t:
            continue
        if rel == "contemp":
            adj.setdefault(us_s, []).append((us_t, "contemp"))
            adj.setdefault(us_t, []).append((us_s, "contemp"))
        else:
            later, earlier = (us_s, us_t) if rel == "later" else (us_t, us_s)
            adj.setdefault(later, []).append((earlier, "later"))
            adj.setdefault(earlier, []).append((later, "earlier"))
    return adj


def _violated(role, su, sn):
    """role is the subject's role vs neighbor; su/sn are their spans (or None)."""
    if su is None or sn is None:
        return False
    if role == "later":
        return su[1] < sn[0]
    if role == "earlier":
        return sn[1] < su[0]
    if role == "contemp":
        return su[1] < sn[0] or sn[1] < su[0]
    return False


def _is_mono(us, unit_periods):
    p = unit_periods.get(us)
    return p is not None and bool(p[0]) and p[0] == p[2]


def _best_target_period(m, adj, work, chrono):
    """Pick the (periodo, fase) satisfying ALL of m's constraints against
    neighbors' CURRENT spans, with the smallest chronological shift. None if
    no candidate satisfies."""
    cur = unit_span(work.get(m), chrono)
    cur_ini = cur[0] if cur else None
    best, best_dist = None, None
    for (periodo, fase), (ci, cf) in chrono.items():
        if ci is None or cf is None:
            continue
        cand = (ci, cf)
        ok = True
        for (nb, role) in adj.get(m, ()):
            if _violated(role, cand, unit_span(work.get(nb), chrono)):
                ok = False
                break
        if not ok:
            continue
        dist = abs(ci - cur_ini) if cur_ini is not None else abs(ci)
        if best is None or dist < best_dist:
            best, best_dist = (periodo, fase), dist
    return best


def _set_fields_for(periodo, fase):
    return (("periodo_iniziale", periodo), ("fase_iniziale", fase),
            ("periodo_finale", periodo), ("fase_finale", fase))


def solve_fixes(issues, graph, chrono, unit_periods, *, sito):
    """Populate iss.edits (auto) where resolvable; leave suggestions otherwise.
    Greedy single pass: each accepted move updates an in-memory period map so
    later decisions see its effect. Mutates the Issue objects in place."""
    work = dict(unit_periods)
    id_to_us = _node_us_map(graph)
    adj = _build_adjacency(graph, id_to_us)

    def span_work(us):
        return unit_span(work.get(us), chrono)

    def conflict_score(us):
        return sum(1 for (nb, role) in adj.get(us, ())
                   if _violated(role, span_work(us), span_work(nb)))

    targetable = [i for i in issues
                  if i.kind in (TEMPORAL_INVERSION, TEMPORAL_CONTEMPORANEITY)]
    targetable.sort(key=lambda i: -sum(conflict_score(u) for u in i.us_path))

    for iss in targetable:
        a, b = iss.us_path[0], iss.us_path[1]
        sp_a, sp_b = span_work(a), span_work(b)
        # gap-fill: contemporaneity with exactly one undated side
        if iss.kind == TEMPORAL_CONTEMPORANEITY and (sp_a is None) != (sp_b is None):
            dated, undated = (a, b) if sp_a is not None else (b, a)
            dp = work.get(dated)
            work[undated] = (dp[0], dp[1], dp[0], dp[1])
            iss.auto = True
            iss.edits = [Edit(us=undated,
                              set_fields=_set_fields_for(dp[0], dp[1]))]
            continue
        if sp_a is None or sp_b is None:
            continue
        ca, cb = conflict_score(a), conflict_score(b)
        if ca == cb:
            continue                      # tie → suggestion
        m = a if ca > cb else b
        if not _is_mono(m, unit_periods):
            continue                      # multi-period → suggestion
        target = _best_target_period(m, adj, work, chrono)
        if target is None:
            continue                      # no valid period → suggestion
        periodo, fase = target
        work[m] = (periodo, fase, periodo, fase)
        iss.auto = True
        iss.edits = [Edit(us=m, set_fields=_set_fields_for(periodo, fase))]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/sync/test_temporal_check.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add modules/utility/temporal_check.py tests/sync/test_temporal_check.py
git -c commit.gpgsign=false commit -m "feat(temporal): solve_fixes (majority heuristic, target period, gap-fill)"
```

---

## Task 5: `Edit.set_fields` + generalized apply/rollback

**Files:**
- Modify: `modules/utility/rapporti_check.py`
- Test: `tests/sync/test_rapporti_check.py`

- [ ] **Step 1: Write the failing test** (append to `tests/sync/test_rapporti_check.py`)

```python
import sqlite3
from pathlib import Path
from modules.s3dgraphy.sync._db_handle import DbHandle

def _apply_db(tmp_path):
    p = tmp_path / "apply.sqlite"
    c = sqlite3.connect(p)
    c.execute("CREATE TABLE us_table (sito TEXT, us TEXT, rapporti TEXT,"
              " periodo_iniziale TEXT, fase_iniziale TEXT,"
              " periodo_finale TEXT, fase_finale TEXT)")
    c.execute("INSERT INTO us_table VALUES ('S','US5','[]','1','1','1','1')")
    c.commit(); c.close()
    return DbHandle.from_path(p)

def test_apply_set_fields_writes_period_and_rolls_back(tmp_path):
    h = _apply_db(tmp_path)
    e = RC.Edit(us="US5", set_fields=(("periodo_iniziale", "3"),
                                      ("fase_iniziale", "1"),
                                      ("periodo_finale", "3"),
                                      ("fase_finale", "1")))
    tok = RC.apply_edits([e], h, sito="S")
    from sqlalchemy import text
    with h.engine.connect() as c:
        row = c.execute(text("SELECT periodo_iniziale, periodo_finale "
                             "FROM us_table WHERE us='US5'")).fetchone()
    assert row == ("3", "3")
    RC.rollback(tok, h)
    with h.engine.connect() as c:
        row = c.execute(text("SELECT periodo_iniziale, periodo_finale "
                             "FROM us_table WHERE us='US5'")).fetchone()
    assert row == ("1", "1")

def test_apply_mixed_rapporti_and_fields(tmp_path):
    h = _apply_db(tmp_path)
    e = RC.Edit(us="US5", add=(("Copre", "7", "1", "S"),),
                set_fields=(("periodo_iniziale", "2"),))
    RC.apply_edits([e], h, sito="S")
    from sqlalchemy import text
    with h.engine.connect() as c:
        rap, pi = c.execute(text("SELECT rapporti, periodo_iniziale "
                                 "FROM us_table WHERE us='US5'")).fetchone()
    assert "Copre" in rap and pi == "2"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/sync/test_rapporti_check.py -q -k set_fields`
Expected: FAIL — `TypeError: __init__() got an unexpected keyword argument 'set_fields'`.

- [ ] **Step 3a: Extend `Edit`** in `rapporti_check.py`:

```python
@dataclass(frozen=True)
class Edit:
    """One change to a single US's row. ``add``/``remove`` hold
    ``(label, target_us, area, sito)`` rapporti 4-tuples; ``set_fields`` holds
    ``(column, value)`` pairs for non-rapporti columns (e.g. period fields)."""
    us: str
    add: tuple = ()
    remove: tuple = ()
    set_fields: tuple = ()
```

- [ ] **Step 3b: Replace `apply_edits` and `rollback`** in `rapporti_check.py` with the generalized versions (snapshot a per-US column→value dict; write rapporti and/or set_fields in one UPDATE):

```python
def apply_edits(edits, handle, *, sito=None) -> RollbackToken:
    from sqlalchemy import text
    by_us = {}
    for e in edits:
        by_us.setdefault(str(e.us), []).append(e)
    snapshot = {}
    with handle.engine.begin() as conn:
        for us, us_edits in by_us.items():
            touch_rapporti = any(e.add or e.remove for e in us_edits)
            field_cols = []
            for e in us_edits:
                for (col, _v) in e.set_fields:
                    if col not in field_cols:
                        field_cols.append(col)
            read_cols = (["rapporti"] if touch_rapporti else []) + field_cols
            if sito is None:
                r0 = conn.execute(text(
                    "SELECT sito FROM us_table WHERE us = :u"), {"u": us}).fetchone()
                row_sito = r0[0] if r0 else None
            else:
                row_sito = sito
            orig = {}
            if read_cols:
                sel = ", ".join(read_cols)
                r = conn.execute(text(
                    f"SELECT {sel} FROM us_table WHERE sito = :s AND us = :u"),
                    {"s": row_sito, "u": us}).fetchone()
                if r is not None:
                    for i, c in enumerate(read_cols):
                        orig[c] = r[i]
            snapshot[us] = (row_sito, orig)
            new_vals = {}
            if touch_rapporti:
                lst = [list(map(str, x)) for x in _coerce_to_list(orig.get("rapporti"))
                       if isinstance(x, (list, tuple))]
                for e in us_edits:
                    for rem in e.remove:
                        rr = list(map(str, rem))
                        lst = [x for x in lst if x != rr]
                    for ad in e.add:
                        aa = list(map(str, ad))
                        if aa not in lst:
                            lst.append(aa)
                new_vals["rapporti"] = str(lst)
            for e in us_edits:
                for (col, val) in e.set_fields:
                    new_vals[col] = val
            if not new_vals:
                continue
            set_clause = ", ".join(f"{c} = :v_{c}" for c in new_vals)
            params = {f"v_{c}": v for c, v in new_vals.items()}
            params["s"] = row_sito
            params["u"] = us
            conn.execute(text(
                f"UPDATE us_table SET {set_clause} WHERE sito = :s AND us = :u"),
                params)
    return RollbackToken(sito=sito or "", snapshot=snapshot)


def rollback(token, handle):
    from sqlalchemy import text
    with handle.engine.begin() as conn:
        for us, (row_sito, orig) in token.snapshot.items():
            if not orig:
                continue
            set_clause = ", ".join(f"{c} = :v_{c}" for c in orig)
            params = {f"v_{c}": v for c, v in orig.items()}
            params["s"] = row_sito
            params["u"] = us
            conn.execute(text(
                f"UPDATE us_table SET {set_clause} WHERE sito = :s AND us = :u"),
                params)
```

Note: column names in `set_fields` are a fixed whitelist (period columns) produced by `temporal_check`, never user input — safe to interpolate.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/sync/test_rapporti_check.py -q`
Expected: PASS — including the pre-existing rapporti apply/rollback tests (behavior preserved).

- [ ] **Step 5: Commit**

```bash
git add modules/utility/rapporti_check.py tests/sync/test_rapporti_check.py
git -c commit.gpgsign=false commit -m "feat(rapporti): Edit.set_fields + generalized apply/rollback (rapporti + period columns)"
```

---

## Task 6: Wire `temporal_check` into `check_rapporti`

**Files:**
- Modify: `modules/utility/rapporti_check.py`
- Test: `tests/sync/test_temporal_check.py`

- [ ] **Step 1: Write the failing test** (append to `tests/sync/test_temporal_check.py`)

```python
from modules.utility import rapporti_check as RC

def test_check_rapporti_appends_temporal_when_chrono_given():
    g = _mk([("US5", "overlies", "US7")])
    up = {"US5": ("1", "1", "1", "1"), "US7": ("3", "1", "3", "1")}
    rep = RC.check_rapporti(g, sito="S", chrono=_CHRONO, unit_periods=up)
    assert any(i.kind == TC.TEMPORAL_INVERSION for i in rep.issues)

def test_check_rapporti_skips_temporal_without_chrono():
    g = _mk([("US5", "overlies", "US7")])
    rep = RC.check_rapporti(g, sito="S")   # no chrono -> backward compatible
    assert not any(i.kind == TC.TEMPORAL_INVERSION for i in rep.issues)

def test_kind_title_localized():
    assert RC.kind_title(TC.TEMPORAL_INVERSION, "it")
    assert RC.kind_title(TC.TEMPORAL_INVERSION, "en")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/sync/test_temporal_check.py -q -k check_rapporti`
Expected: FAIL — `check_rapporti() got an unexpected keyword argument 'chrono'`.

- [ ] **Step 3: Modify `check_rapporti`** signature + body in `rapporti_check.py`. Change the signature to:

```python
def check_rapporti(graph, *, sito, lang="it", validate=True,
                   inverse_label=None, chrono=None, unit_periods=None) -> RapportiReport:
```

Then, immediately before the final `_fill_edits(rep, graph, inverse_label=inverse_label)` / `return rep`, insert:

```python
    # Temporal paradoxes (only when chronology + period spans are supplied).
    if chrono and unit_periods is not None:
        from modules.utility import temporal_check as _TC   # lazy: avoid import cycle
        rep.issues += _TC.detect_temporal(
            graph, chrono, unit_periods, sito=sito, lang=lang)
        _TC.solve_fixes(
            [i for i in rep.issues if i.kind in (
                _TC.TEMPORAL_INVERSION, _TC.TEMPORAL_CONTEMPORANEITY)],
            graph, chrono, unit_periods, sito=sito)
```

(`_fill_edits` only handles the existing kinds; temporal issues carry their own edits from `solve_fixes`, so order doesn't matter — but place this block AFTER `_fill_edits` to avoid `_fill_edits` iterating temporal issues. Put it right before `return rep`.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/sync/test_temporal_check.py tests/sync/test_rapporti_check.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add modules/utility/rapporti_check.py tests/sync/test_temporal_check.py
git -c commit.gpgsign=false commit -m "feat(rapporti): wire temporal paradox detection into check_rapporti (opt-in chrono)"
```

---

## Task 7: UI wiring (panel)

**Files:**
- Modify: `gui/rapporti_check_dialog.py`

> Domain logic is fully tested (Tasks 1–6). The UI is a thin orchestrator. Verify with `py_compile` (QGIS not importable headless).

- [ ] **Step 1: Build + pass chronology in `_run`.** In `RapportiCheckPanel._run`, replace the body that calls `check_rapporti` so it also builds the two dicts:

```python
    def _run(self):
        sito = self.cboSite.currentText().strip()
        if not sito:
            return
        try:
            from modules.s3dgraphy.sync.graph_projector import GraphProjector
            from modules.utility import temporal_check as TC
            handle = self._handle()
            graph = GraphProjector().populate_graph(handle, sito=sito)
            chrono = TC.build_chronology(handle, sito)
            unit_periods = TC.load_unit_periods(handle, sito)
            self._report = RC.check_rapporti(
                graph, sito=sito, lang=self._lang,
                chrono=chrono, unit_periods=unit_periods)
        except Exception as exc:
            QMessageBox.critical(self, "pyArchInit", f"Verifica fallita: {exc}")
            return
        self._render()
```

- [ ] **Step 2: Show `set_fields` in the preview.** In `_preview`, after the loop over `iss.edits` that prints remove/add, add handling for set_fields:

```python
        for e in iss.edits:
            for r in e.remove:
                lines.append(f"US {e.us}: rimuovi  {list(r)}")
            for a in e.add:
                lines.append(f"US {e.us}: aggiungi {list(a)}")
            for (col, val) in getattr(e, "set_fields", ()):
                lines.append(f"US {e.us}: imposta {col} = {val}")
```

- [ ] **Step 3: Auto-backup before applying period writes.** In `_apply`, after the confirmation `question` returns Yes and before `RC.apply_edits(...)`, insert:

```python
        if any(getattr(e, "set_fields", ()) for e in edits):
            try:
                from pathlib import Path
                from scripts.migrations._common import (
                    auto_backup_sqlite, auto_backup_postgres, BackupSkipped)
                h = self._handle()
                if h.is_postgres:
                    auto_backup_postgres(h.engine, "temporal_fix", Path.cwd())
                elif h.sqlite_path:
                    auto_backup_sqlite(Path(h.sqlite_path), "temporal_fix")
            except BackupSkipped:
                if QMessageBox.question(
                        self, "Backup non disponibile",
                        "pg_dump non trovato: procedo senza backup?",
                        QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
                    return
            except Exception:
                pass   # backup is best-effort; rollback still protects
```

- [ ] **Step 4: Verify the file compiles**

Run: `python3 -m py_compile gui/rapporti_check_dialog.py`
Expected: no output (success).

- [ ] **Step 5: Commit**

```bash
git add gui/rapporti_check_dialog.py
git -c commit.gpgsign=false commit -m "feat(gui): temporal paradoxes in Verifica rapporti (chrono build + period-fix backup/preview)"
```

---

## Task 8: Regression — full sync suite + AC-2 baseline

**Files:** none (verification only)

- [ ] **Step 1: Full suite**

Run: `python3 -m pytest tests/sync -q`
Expected: all non-PG tests PASS; pre-existing PG/Spatialite failures unchanged (environment). No NEW failures. In particular all `test_rapporti_check.py` and `test_temporal_check.py` pass.

- [ ] **Step 2: AC-2 baseline untouched**

Run: `git status --porcelain tests/sync/fixtures/mini_volterra_baseline_ai03.graphml`
Expected: empty (the temporal check never runs at export).

---

## Task 9: CHANGELOG + tutorials

- [ ] **Step 1:** Add a bilingual (IT+EN) `dev_logs/CHANGELOG.md` entry (next version after 5.12.12-alpha), describing temporal paradox detection (inversion/contemporaneity/unevaluable), majority-heuristic auto-fix moving periods, gap-fill, suggestions, `Edit.set_fields` + unified apply/rollback, opt-in `chrono`/`unit_periods` in `check_rapporti`, auto-backup. Follow the file's existing format. (Use `stratigraph-changelog` agent if available, else write directly.)

- [ ] **Step 2:** Add a "Paradossi temporali" subsection to `docs/tutorials/<lang>/36_extended_matrix_s3dgraphy.md` (9 languages: it/en/de/es/fr/ar/ca/ro/pt), matching the existing structure. (Use `tutorial-updater` agent if available, else a general-purpose agent.)

- [ ] **Step 3: Commit**

```bash
git add dev_logs/CHANGELOG.md docs/tutorials
git -c commit.gpgsign=false commit -m "docs(temporal): changelog + tutorials for temporal paradox detection"
```

---

## Self-Review

- **Spec coverage:** detection rules §5 → Tasks 1+3; chronology by interval (`cron_finale(A) < cron_iniziale(B)`) → Tasks 2+3; auto-fix policy (majority outlier, target period minimal shift, mono-period restriction, gap-fill, tie/no-target → suggestion) §6 → Task 4; integration into Verifica rapporti §4.2 → Task 6; `Edit.set_fields` + unified apply/rollback §4.3 → Task 5; UI + auto-backup §4.4 → Task 7; localization → Task 3; error handling §7 (undatable → unevaluable/skip, multi-period → suggestion, BackupSkipped dialog, rollback) → Tasks 3/4/5/7; testing §8 → all tasks; regression/AC-2 → Task 8. All covered.
- **Placeholder scan:** none.
- **Type consistency:** `Edit(us, add, remove, set_fields)`; `Issue(kind, us_path, auto, summary, edits)`; `detect_temporal(graph, chrono, unit_periods, *, sito, lang)` and `solve_fixes(issues, graph, chrono, unit_periods, *, sito)` consistent across Tasks 3/4/6; `_set_fields_for` returns the same `(col,val)` tuple shape consumed by `apply_edits`; `check_rapporti(..., chrono=None, unit_periods=None)` consistent in Tasks 6/7.
- **Backward compatibility:** `chrono`/`unit_periods` default `None` → existing `check_rapporti(g, sito=...)` callers/tests unaffected; generalized `apply_edits`/`rollback` preserve rapporti-only behavior (existing tests must stay green — checked in Task 5 Step 4).
