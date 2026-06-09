# Feature A — "Genera continuità": automatismo schede CON — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Un'azione esplicita "Genera continuità" che, sul sito corrente, crea/aggiorna idempotentemente una scheda `CON_<us_madre>` per ogni US/USM con `periodo_iniziale ≠ periodo_finale`, con rapporto reciproco di continuità, anteprima dry-run, auto-backup e report.

**Architecture:** Logica di dominio pura e Qt-free in un nuovo modulo `continuity_generator.py` (scan/build/diff puri; reader + `apply_plan` come unica superficie I/O via `DbHandle`, PG+SQLite). Vocabolario di continuità multilingue aggiunto come *dati* a `RAPPORTI_SHORTHAND` (nessuna modifica alla logica di `parse_rapporti`). UI sottile: un pulsante nel pannello *Verifica rapporti* (già nel dialog s3dgraphy) che orchestra read→scan→diff→preview→backup→apply→report.

**Tech Stack:** Python 3, SQLAlchemy (DbHandle), PyQt (QGIS), pytest. s3dgraphy 1.6.0.dev9 vendored.

**Spec:** `docs/superpowers/specs/2026-06-09-genera-continuita-con-design.md`

---

## Riferimenti chiave (verificati nel codice)

- `DbHandle` (`modules/s3dgraphy/sync/_db_handle.py`): `.engine`, `.is_postgres`, `.sqlite_path`; `_columns_of(engine, table) -> set[str]`.
- rapporti column: stringa Python-literal di liste `[[label, target_us, area, sito], ...]`. Letta con `_coerce_to_list`, scritta con `str(lst)`.
- `parse_rapporti(value)` → 5-tuple `(edge_type, target_us, area, sito, swap)`. Cerca PRIMA `RAPPORTI_TO_EDGE_TYPE` (lowercased, swap=False), POI `RAPPORTI_SHORTHAND[raw.strip()]` (con swap). Etichette ignote → silenziosamente saltate.
- `RAPPORTI_SHORTHAND`: `{">": ("is_after", False), "<": ("is_after", True), ...}`. **Aggiungendo qui le etichette di continuità (forward → swap=False, reverse → swap=True) entrambi i lati producono lo stesso edge `CON is_after US`** — niente reverse/2-ciclo.
- `_EDGE_TYPE_INVERSE` in `modules/utility/rapporti_check.py` NON contiene `is_after` → la Verifica rapporti **non** richiede reciprocità per la continuità (nessun falso "reciprocità mancante").
- `us_table` (`modules/db/structures/US_table.py`): PK `id_us` (Integer); `area String(20)` (singola); `other_locations Text` (aree secondarie / multi-folder); `entity_uuid Text`. **`node_uuid` NON è nello schema base** — aggiunto dalla migrazione backfill; settarlo solo se la colonna esiste (`_columns_of`). UniqueConstraint `(sito, area, us, unita_tipo)`.
- `uuid7()` in `modules/s3dgraphy/sync/uuid7.py`.
- Backup: `auto_backup_sqlite(db_path: Path, tag) -> Path` e `auto_backup_postgres(engine, tag, dest_dir) -> Path` (+ `BackupSkipped`) in `scripts/migrations/_common.py`.
- UI: `RapportiCheckPanel` in `gui/rapporti_check_dialog.py` (site picker `cboSite`, `_handle()`), embeddato nel tab import s3dgraphy.

## File Structure

| File | Tipo | Responsabilità |
|---|---|---|
| `modules/s3dgraphy/sync/continuity_generator.py` | **Create** | dataclass `Candidate`/`Plan`/`Report`; `scan_candidates`, `build_con_record`, `desired_rapporti`, `diff_continuity` (puri); `load_site_records`, `load_existing_con`, `apply_plan`, `generate_continuity` (I/O) |
| `modules/s3dgraphy/sync/rapporti.py` | **Modify** | blocco "pyArchInit continuity vocabulary" (10 lingue) + `continuity_label()` helper + registrazione in `RAPPORTI_SHORTHAND` |
| `gui/rapporti_check_dialog.py` | **Modify** | pulsante "Genera continuità" + `_run_genera_continuita()` + dialog anteprima/report |
| `tests/sync/test_continuity_generator.py` | **Create** | unit (puri) + integrazione SQLite + idempotenza |
| `tests/sync/test_continuity_vocab.py` | **Create** | parse forward/reverse 10 lingue + no-falsa-reciprocità |
| `dev_logs/CHANGELOG.md` | **Modify** | entry bilingue (agente) |
| `docs/tutorials/<lang>/…` | **Modify** | nuova azione UI (agente) |

---

## Task 1: Vocabolario di continuità (rapporti.py)

**Files:**
- Modify: `modules/s3dgraphy/sync/rapporti.py` (dopo il blocco `RAPPORTI_SHORTHAND`, ~riga 229)
- Test: `tests/sync/test_continuity_vocab.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/sync/test_continuity_vocab.py
import pytest
from modules.s3dgraphy.sync.rapporti import (
    parse_rapporti, continuity_label, CONTINUITY_LABELS,
)

_LANGS = ["it", "en", "de", "es", "fr", "pt", "ca", "ro", "ar", "el"]

def test_continuity_labels_cover_ten_languages():
    assert set(CONTINUITY_LABELS) == set(_LANGS)
    for lang in _LANGS:
        fwd = continuity_label(lang, "forward")
        rev = continuity_label(lang, "reverse")
        assert fwd and rev and fwd != rev

@pytest.mark.parametrize("lang", _LANGS)
def test_forward_label_parses_to_is_after_no_swap(lang):
    fwd = continuity_label(lang, "forward")
    parsed = parse_rapporti([[fwd, "US5", "1", "Sito"]])
    assert parsed == [("is_after", "US5", "1", "Sito", False)]

@pytest.mark.parametrize("lang", _LANGS)
def test_reverse_label_parses_to_is_after_with_swap(lang):
    rev = continuity_label(lang, "reverse")
    parsed = parse_rapporti([[rev, "CON_US5", "1", "Sito"]])
    assert parsed == [("is_after", "CON_US5", "1", "Sito", True)]

def test_reverse_label_unknown_lang_falls_back_to_italian():
    assert continuity_label("zz", "forward") == CONTINUITY_LABELS["it"][0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/sync/test_continuity_vocab.py -q`
Expected: FAIL — `ImportError: cannot import name 'continuity_label'`.

- [ ] **Step 3: Write minimal implementation**

In `modules/s3dgraphy/sync/rapporti.py`, immediately after the `RAPPORTI_SHORTHAND` dict (the block ending ~line 229), add:

```python
# ---------------------------------------------------------------------------
# pyArchInit continuity vocabulary (candidate for upstream)
# ---------------------------------------------------------------------------
#: Verbose, human-readable directional labels for CON (continuità) units,
#: one (forward, reverse) pair per pyArchInit UI language. The "Genera
#: continuità" action writes these into us_table.rapporti instead of the
#: bare ``>`` / ``<`` shorthand so the Scheda US shows a meaningful term.
#:
#: Direction semantics mirror the shorthand:
#:   * forward  → ("is_after", swap=False): the CON terminates the US life
#:                (``CON is_after US``);
#:   * reverse  → ("is_after", swap=True):  the madre's reciprocal entry
#:                yields the SAME ``CON is_after US`` edge (no reverse edge,
#:                no 2-cycle, no false "missing reciprocity" — is_after is
#:                not in rapporti_check._EDGE_TYPE_INVERSE).
CONTINUITY_LABELS: dict[str, tuple[str, str]] = {
    "it": ("Continuità successiva a", "Continuità precedente a"),
    "en": ("Subsequent continuity of", "Prior continuity of"),
    "de": ("Nachfolgende Kontinuität von", "Vorherige Kontinuität von"),
    "es": ("Continuidad posterior a", "Continuidad anterior a"),
    "fr": ("Continuité postérieure à", "Continuité antérieure à"),
    "pt": ("Continuidade posterior a", "Continuidade anterior a"),
    "ca": ("Continuïtat posterior a", "Continuïtat anterior a"),
    "ro": ("Continuitate ulterioară a", "Continuitate anterioară a"),
    "ar": ("استمرارية لاحقة لـ", "استمرارية سابقة لـ"),
    "el": ("Μεταγενέστερη συνέχεια του", "Προγενέστερη συνέχεια του"),
}


def continuity_label(lang: str, direction: str) -> str:
    """Return the continuity label for *lang* ('forward'|'reverse').
    Falls back to Italian for unknown languages."""
    pair = CONTINUITY_LABELS.get((lang or "it")[:2], CONTINUITY_LABELS["it"])
    return pair[0] if direction == "forward" else pair[1]


# Register every continuity label as shorthand DATA (no parse_rapporti
# logic change): forward → no swap, reverse → swap. Both exact-case and
# lowercased keys are added because parse_rapporti looks up
# RAPPORTI_SHORTHAND with the raw (original-case) label after the verbose
# RAPPORTI_TO_EDGE_TYPE miss.
for _fwd, _rev in CONTINUITY_LABELS.values():
    RAPPORTI_SHORTHAND.setdefault(_fwd, ("is_after", False))
    RAPPORTI_SHORTHAND.setdefault(_fwd.lower(), ("is_after", False))
    RAPPORTI_SHORTHAND.setdefault(_rev, ("is_after", True))
    RAPPORTI_SHORTHAND.setdefault(_rev.lower(), ("is_after", True))
del _fwd, _rev
```

Then add `"CONTINUITY_LABELS"` and `"continuity_label"` to the module's `__all__` list (near the existing `"RAPPORTI_SHORTHAND"` entry, ~line 697).

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/sync/test_continuity_vocab.py -q`
Expected: PASS (13 tests).

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/rapporti.py tests/sync/test_continuity_vocab.py
git -c commit.gpgsign=false commit -m "feat(continuity): multilingual CON continuity vocabulary (10 langs)"
```

---

## Task 2: `scan_candidates` (pure)

**Files:**
- Create: `modules/s3dgraphy/sync/continuity_generator.py`
- Test: `tests/sync/test_continuity_generator.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/sync/test_continuity_generator.py
from modules.s3dgraphy.sync.continuity_generator import (
    Candidate, scan_candidates,
)

def _rec(**kw):
    base = dict(sito="S", us="US5", unita_tipo="US", area="1",
                struttura="M1", periodo_iniziale="1", fase_iniziale="1",
                periodo_finale="3", fase_finale="2", other_locations=None)
    base.update(kw)
    return base

def test_scan_includes_period_jump():
    cands = scan_candidates([_rec()])
    assert len(cands) == 1
    c = cands[0]
    assert isinstance(c, Candidate)
    assert c.us == "US5" and c.periodo_iniziale == "1" and c.periodo_finale == "3"

def test_scan_excludes_same_period():
    assert scan_candidates([_rec(periodo_finale="1")]) == []

def test_scan_excludes_null_periods():
    assert scan_candidates([_rec(periodo_iniziale=None)]) == []
    assert scan_candidates([_rec(periodo_finale="")]) == []

def test_scan_excludes_non_us_usm_types():
    assert scan_candidates([_rec(unita_tipo="USV")]) == []
    assert scan_candidates([_rec(unita_tipo="CON", us="CON_US5")]) == []

def test_scan_inherits_all_areas_via_other_locations():
    c = scan_candidates([_rec(other_locations='["2","3"]')])[0]
    assert c.other_locations == '["2","3"]'
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/sync/test_continuity_generator.py -q`
Expected: FAIL — `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal implementation**

```python
# modules/s3dgraphy/sync/continuity_generator.py
"""Feature A — "Genera continuità": idempotent CON-record generation.

Qt-free domain logic. Scans US/USM rows whose life spans more than one
period (``periodo_iniziale != periodo_finale``) and creates/updates one
``CON_<us_madre>`` record per candidate, with the reciprocal continuity
rapporto on both the CON and its madre.

Pure functions: scan_candidates / build_con_record / desired_rapporti /
diff_continuity. I/O surface: load_site_records / load_existing_con /
apply_plan / generate_continuity (the orchestrator).

Spec: docs/superpowers/specs/2026-06-09-genera-continuita-con-design.md
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .rapporti import continuity_label

#: Source unit types that can bear a continuity (per spec: US / USM only).
CONTINUITY_SOURCE_TYPES = frozenset({"US", "USM"})

#: Columns read for scanning + CON construction.
_READ_COLUMNS = (
    "sito", "us", "unita_tipo", "area", "struttura",
    "periodo_iniziale", "fase_iniziale", "periodo_finale", "fase_finale",
    "other_locations",
)


@dataclass(frozen=True)
class Candidate:
    sito: str
    us: str
    unita_tipo: str
    area: str | None
    struttura: str | None
    periodo_iniziale: str
    fase_iniziale: str | None
    periodo_finale: str
    fase_finale: str | None
    other_locations: str | None


def _nz(v):
    """Normalise a DB cell to a stripped string or None."""
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def scan_candidates(records) -> list[Candidate]:
    """Return one Candidate per US/USM with both periods set and distinct."""
    out: list[Candidate] = []
    for r in records:
        if str(r.get("unita_tipo") or "").strip() not in CONTINUITY_SOURCE_TYPES:
            continue
        pi = _nz(r.get("periodo_iniziale"))
        pf = _nz(r.get("periodo_finale"))
        if pi is None or pf is None or pi == pf:
            continue
        out.append(Candidate(
            sito=str(r.get("sito") or ""),
            us=str(r.get("us") or ""),
            unita_tipo=str(r.get("unita_tipo") or ""),
            area=_nz(r.get("area")),
            struttura=_nz(r.get("struttura")),
            periodo_iniziale=pi,
            fase_iniziale=_nz(r.get("fase_iniziale")),
            periodo_finale=pf,
            fase_finale=_nz(r.get("fase_finale")),
            other_locations=r.get("other_locations"),
        ))
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/sync/test_continuity_generator.py -q`
Expected: PASS (5 tests).

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/continuity_generator.py tests/sync/test_continuity_generator.py
git -c commit.gpgsign=false commit -m "feat(continuity): scan_candidates for period-jumping US/USM"
```

---

## Task 3: `build_con_record` + `desired_rapporti` (pure)

**Files:**
- Modify: `modules/s3dgraphy/sync/continuity_generator.py`
- Test: `tests/sync/test_continuity_generator.py`

- [ ] **Step 1: Write the failing test** (append)

```python
from modules.s3dgraphy.sync.continuity_generator import (
    build_con_record, desired_rapporti, con_us_code,
)
from modules.s3dgraphy.sync.rapporti import continuity_label, parse_rapporti

def test_con_us_code():
    assert con_us_code("US5") == "CON_US5"
    assert con_us_code("USM6") == "CON_USM6"

def test_build_con_record_fields():
    c = scan_candidates([_rec(other_locations='["2"]')])[0]
    rec = build_con_record(c, schedatore="enzo", lang="it")
    assert rec["us"] == "CON_US5"
    assert rec["unita_tipo"] == "CON"
    assert rec["sito"] == "S"
    assert rec["area"] == "1"
    assert rec["struttura"] == "M1"
    assert rec["other_locations"] == '["2"]'
    assert rec["periodo_iniziale"] == "1" and rec["periodo_finale"] == "3"
    assert rec["fase_iniziale"] == "1" and rec["fase_finale"] == "2"
    assert rec["d_stratigrafica"] == "Continuità"
    assert "US5" in rec["descrizione"] and "1" in rec["descrizione"]
    assert rec["schedatore"] == "enzo"
    # CON-side rapporti: forward continuity to the madre
    fwd = continuity_label("it", "forward")
    assert rec["rapporti"] == [[fwd, "US5", "1", "S"]]

def test_desired_rapporti_pair_directions():
    c = scan_candidates([_rec()])[0]
    con_entry, madre_entry = desired_rapporti(c, lang="it")
    # CON row -> forward -> CON is_after US (no swap)
    p_con = parse_rapporti([con_entry])
    assert p_con == [("is_after", "US5", "1", "S", False)]
    # madre row -> reverse -> swap -> still CON is_after US
    p_madre = parse_rapporti([madre_entry])
    assert p_madre == [("is_after", "CON_US5", "1", "S", True)]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/sync/test_continuity_generator.py -q`
Expected: FAIL — `ImportError: cannot import name 'build_con_record'`.

- [ ] **Step 3: Write minimal implementation** (append to `continuity_generator.py`)

```python
def con_us_code(us_madre: str) -> str:
    """Deterministic CON identity for a madre US (idempotency key)."""
    return f"CON_{us_madre}"


def desired_rapporti(cand: Candidate, *, lang: str = "it"):
    """Return (con_side_entry, madre_side_entry) rapporti rows.

    Both are 4-lists ``[label, target_us, area, sito]`` in pyArchInit's
    column convention. The CON side carries the forward label, the madre
    side the reverse label (swap → same CON is_after US edge)."""
    area = cand.area or "1"
    sito = cand.sito
    con_us = con_us_code(cand.us)
    fwd = continuity_label(lang, "forward")
    rev = continuity_label(lang, "reverse")
    con_entry = [fwd, cand.us, area, sito]
    madre_entry = [rev, con_us, area, sito]
    return con_entry, madre_entry


def build_con_record(cand: Candidate, *, schedatore: str = "",
                     lang: str = "it") -> dict:
    """Build the CON scheda dict for a candidate (no DB I/O, no uuids)."""
    con_entry, _ = desired_rapporti(cand, lang=lang)
    descr = (f"Continuità di {cand.us} dal periodo "
             f"{cand.periodo_iniziale} al periodo {cand.periodo_finale}")
    return {
        "sito": cand.sito,
        "us": con_us_code(cand.us),
        "unita_tipo": "CON",
        "area": cand.area,
        "struttura": cand.struttura,
        "periodo_iniziale": cand.periodo_iniziale,
        "fase_iniziale": cand.fase_iniziale,
        "periodo_finale": cand.periodo_finale,
        "fase_finale": cand.fase_finale,
        "other_locations": cand.other_locations,
        "d_stratigrafica": "Continuità",
        "descrizione": descr,
        "rapporti": [con_entry],
        "schedatore": schedatore,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/sync/test_continuity_generator.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/continuity_generator.py tests/sync/test_continuity_generator.py
git -c commit.gpgsign=false commit -m "feat(continuity): build_con_record + reciprocal desired_rapporti"
```

---

## Task 4: `diff_continuity` (pure, idempotent)

**Files:**
- Modify: `modules/s3dgraphy/sync/continuity_generator.py`
- Test: `tests/sync/test_continuity_generator.py`

- [ ] **Step 1: Write the failing test** (append)

```python
from modules.s3dgraphy.sync.continuity_generator import diff_continuity, Plan

def _desired_for(*recs):
    return [build_con_record(c, schedatore="x", lang="it")
            for c in scan_candidates(list(recs))]

def test_diff_creates_when_absent():
    desired = _desired_for(_rec())
    plan = diff_continuity({}, desired)
    assert isinstance(plan, Plan)
    assert [d["us"] for d in plan.to_create] == ["CON_US5"]
    assert plan.to_update == [] and plan.unchanged == [] and plan.orphan == []

def test_diff_unchanged_when_identical():
    desired = _desired_for(_rec())
    # existing CON identical to desired (same comparable fields)
    existing = {"CON_US5": dict(desired[0])}
    plan = diff_continuity(existing, desired)
    assert plan.unchanged == ["CON_US5"]
    assert plan.to_create == [] and plan.to_update == []

def test_diff_updates_when_span_changed():
    desired = _desired_for(_rec(periodo_finale="4"))   # span now 1..4
    existing = {"CON_US5": dict(_desired_for(_rec(periodo_finale="3"))[0])}
    plan = diff_continuity(existing, desired)
    assert [d["us"] for d in plan.to_update] == ["CON_US5"]

def test_diff_marks_orphan():
    # existing CON whose madre no longer jumps periods (no desired entry)
    existing = {"CON_US9": {"us": "CON_US9", "sito": "S"}}
    plan = diff_continuity(existing, [])
    assert plan.orphan == ["CON_US9"]

def test_diff_is_idempotent_second_pass():
    desired = _desired_for(_rec())
    # simulate state after first apply: existing == desired
    existing = {d["us"]: dict(d) for d in desired}
    plan = diff_continuity(existing, desired)
    assert plan.to_create == [] and plan.to_update == []
    assert plan.unchanged == ["CON_US5"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/sync/test_continuity_generator.py -q`
Expected: FAIL — `ImportError: cannot import name 'diff_continuity'`.

- [ ] **Step 3: Write minimal implementation** (append)

```python
@dataclass
class Plan:
    to_create: list = field(default_factory=list)   # CON record dicts
    to_update: list = field(default_factory=list)   # CON record dicts
    unchanged: list = field(default_factory=list)   # us codes
    orphan: list = field(default_factory=list)      # us codes


#: CON fields compared to decide create/update/unchanged.
_COMPARE_FIELDS = (
    "area", "struttura", "periodo_iniziale", "fase_iniziale",
    "periodo_finale", "fase_finale", "other_locations",
    "d_stratigrafica", "descrizione",
)


def _norm_rapporti(value):
    """Order-insensitive normalised form of a rapporti value for compare."""
    from .rapporti import _coerce_to_list
    rows = []
    for e in _coerce_to_list(value):
        if isinstance(e, (list, tuple)) and len(e) >= 2:
            rows.append((str(e[0]).strip(), str(e[1]).strip()))
    return sorted(rows)


def _record_matches(existing: dict, desired: dict) -> bool:
    for f in _COMPARE_FIELDS:
        if _nz(existing.get(f)) != _nz(desired.get(f)):
            return False
    return _norm_rapporti(existing.get("rapporti")) == \
        _norm_rapporti(desired.get("rapporti"))


def diff_continuity(existing_con: dict, desired: list) -> Plan:
    """Compare desired CON records against existing ones (keyed by us)."""
    plan = Plan()
    desired_keys = set()
    for d in desired:
        key = d["us"]
        desired_keys.add(key)
        cur = existing_con.get(key)
        if cur is None:
            plan.to_create.append(d)
        elif _record_matches(cur, d):
            plan.unchanged.append(key)
        else:
            plan.to_update.append(d)
    for key in existing_con:
        if key not in desired_keys:
            plan.orphan.append(key)
    return plan
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/sync/test_continuity_generator.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/continuity_generator.py tests/sync/test_continuity_generator.py
git -c commit.gpgsign=false commit -m "feat(continuity): idempotent diff_continuity (create/update/unchanged/orphan)"
```

---

## Task 5: I/O — readers + `apply_plan` (DbHandle, SQLite integration)

**Files:**
- Modify: `modules/s3dgraphy/sync/continuity_generator.py`
- Test: `tests/sync/test_continuity_generator.py`

- [ ] **Step 1: Write the failing test** (append)

```python
import sqlite3
import pytest
from pathlib import Path
from modules.s3dgraphy.sync._db_handle import DbHandle
from modules.s3dgraphy.sync.continuity_generator import (
    load_site_records, load_existing_con, apply_plan,
)
from modules.s3dgraphy.sync.rapporti import continuity_label, _coerce_to_list

def _make_db(tmp_path: Path) -> DbHandle:
    p = tmp_path / "con_test.sqlite"
    con = sqlite3.connect(p)
    con.executescript(
        "CREATE TABLE us_table ("
        " id_us INTEGER PRIMARY KEY, sito TEXT, area TEXT, us TEXT,"
        " d_stratigrafica TEXT, descrizione TEXT, periodo_iniziale TEXT,"
        " fase_iniziale TEXT, periodo_finale TEXT, fase_finale TEXT,"
        " rapporti TEXT, schedatore TEXT, struttura TEXT, unita_tipo TEXT,"
        " other_locations TEXT, entity_uuid TEXT, node_uuid TEXT);")
    con.execute(
        "INSERT INTO us_table (id_us,sito,area,us,unita_tipo,"
        "periodo_iniziale,periodo_finale,struttura,rapporti) VALUES"
        " (1,'S','1','US5','US','1','3','M1','[]')")
    con.commit(); con.close()
    return DbHandle.from_path(p)

def test_apply_plan_creates_con_and_reciprocal(tmp_path):
    h = _make_db(tmp_path)
    recs = load_site_records(h, "S")
    from modules.s3dgraphy.sync.continuity_generator import (
        scan_candidates, build_con_record, diff_continuity)
    desired = [build_con_record(c, schedatore="enzo", lang="it")
               for c in scan_candidates(recs)]
    plan = diff_continuity(load_existing_con(h, "S"), desired)
    report = apply_plan(h, plan, remove_orphans=False)
    assert report.created == 1
    # CON row exists with unita_tipo CON
    con_rows = load_existing_con(h, "S")
    assert "CON_US5" in con_rows
    # reciprocal written on madre US5
    with h.engine.connect() as c:
        from sqlalchemy import text
        rap = c.execute(text("SELECT rapporti FROM us_table WHERE us='US5'"
                             " AND sito='S'")).fetchone()[0]
    rev = continuity_label("it", "reverse")
    assert any(e[0] == rev and e[1] == "CON_US5"
               for e in _coerce_to_list(rap))

def test_apply_plan_idempotent_second_run(tmp_path):
    h = _make_db(tmp_path)
    from modules.s3dgraphy.sync.continuity_generator import generate_continuity
    r1 = generate_continuity(h, "S", schedatore="enzo", lang="it")
    assert r1.created == 1
    r2 = generate_continuity(h, "S", schedatore="enzo", lang="it")
    assert r2.created == 0 and r2.updated == 0

def test_apply_plan_removes_orphan_only_when_opted_in(tmp_path):
    h = _make_db(tmp_path)
    from sqlalchemy import text
    with h.engine.begin() as c:
        c.execute(text("INSERT INTO us_table (id_us,sito,area,us,unita_tipo,"
                       "periodo_iniziale,periodo_finale) VALUES"
                       " (2,'S','1','CON_US9','CON','1','3')"))
    from modules.s3dgraphy.sync.continuity_generator import generate_continuity
    r = generate_continuity(h, "S", schedatore="x", lang="it",
                            remove_orphans=False)
    assert "CON_US9" in load_existing_con(h, "S")     # kept
    r2 = generate_continuity(h, "S", schedatore="x", lang="it",
                             remove_orphans=True)
    assert "CON_US9" not in load_existing_con(h, "S")  # removed
    assert r2.orphans_removed == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/sync/test_continuity_generator.py -q`
Expected: FAIL — `ImportError: cannot import name 'load_site_records'`.

- [ ] **Step 3: Write minimal implementation** (append)

```python
@dataclass
class Report:
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    orphans_removed: int = 0
    warnings: list = field(default_factory=list)


def load_site_records(handle, sito) -> list[dict]:
    """Read US/USM rows for *sito* (only the columns scan/build need)."""
    from sqlalchemy import text
    cols = ", ".join(_READ_COLUMNS)
    with handle.engine.connect() as conn:
        rows = conn.execute(
            text(f"SELECT {cols} FROM us_table WHERE sito = :s"),
            {"s": sito}).mappings().fetchall()
    return [dict(r) for r in rows]


def load_existing_con(handle, sito) -> dict:
    """Read existing CON_* rows for *sito*, keyed by us. Includes the
    comparable fields + rapporti so diff_continuity can classify them."""
    from sqlalchemy import text
    cols = ("us, area, struttura, periodo_iniziale, fase_iniziale, "
            "periodo_finale, fase_finale, other_locations, "
            "d_stratigrafica, descrizione, rapporti")
    with handle.engine.connect() as conn:
        rows = conn.execute(
            text(f"SELECT {cols} FROM us_table "
                 "WHERE sito = :s AND unita_tipo = 'CON'"),
            {"s": sito}).mappings().fetchall()
    return {r["us"]: dict(r) for r in rows}


def _next_id(conn):
    from sqlalchemy import text
    row = conn.execute(text("SELECT MAX(id_us) FROM us_table")).fetchone()
    return (row[0] or 0) + 1


def _insert_con(conn, rec, next_id, has_node_uuid):
    """Insert one CON row. Sets id_us explicitly (cross-backend safe),
    entity_uuid always, node_uuid only when the column exists."""
    from sqlalchemy import text
    from .uuid7 import uuid7
    fields = {
        "id_us": next_id,
        "sito": rec["sito"], "area": rec["area"], "us": rec["us"],
        "unita_tipo": "CON", "struttura": rec["struttura"],
        "periodo_iniziale": rec["periodo_iniziale"],
        "fase_iniziale": rec["fase_iniziale"],
        "periodo_finale": rec["periodo_finale"],
        "fase_finale": rec["fase_finale"],
        "other_locations": rec["other_locations"],
        "d_stratigrafica": rec["d_stratigrafica"],
        "descrizione": rec["descrizione"],
        "rapporti": str([list(map(str, e)) for e in rec["rapporti"]]),
        "schedatore": rec["schedatore"],
        "entity_uuid": str(uuid7()),
    }
    if has_node_uuid:
        fields["node_uuid"] = str(uuid7())
    cols = ", ".join(fields)
    binds = ", ".join(f":{k}" for k in fields)
    conn.execute(text(f"INSERT INTO us_table ({cols}) VALUES ({binds})"),
                 fields)


def _update_con(conn, rec):
    from sqlalchemy import text
    sets = ("area=:area, struttura=:struttura, "
            "periodo_iniziale=:pi, fase_iniziale=:fi, "
            "periodo_finale=:pf, fase_finale=:ff, "
            "other_locations=:ol, d_stratigrafica=:ds, "
            "descrizione=:descr, rapporti=:rap")
    conn.execute(text(f"UPDATE us_table SET {sets} "
                      "WHERE sito=:sito AND us=:us AND unita_tipo='CON'"),
                 {"area": rec["area"], "struttura": rec["struttura"],
                  "pi": rec["periodo_iniziale"], "fi": rec["fase_iniziale"],
                  "pf": rec["periodo_finale"], "ff": rec["fase_finale"],
                  "ol": rec["other_locations"], "ds": rec["d_stratigrafica"],
                  "descr": rec["descrizione"],
                  "rap": str([list(map(str, e)) for e in rec["rapporti"]]),
                  "sito": rec["sito"], "us": rec["us"]})


def _add_reciprocal_to_madre(conn, sito, us_madre, madre_entry):
    """Append the reverse continuity rapporto to the madre row if absent."""
    from sqlalchemy import text
    from .rapporti import _coerce_to_list
    row = conn.execute(
        text("SELECT rapporti FROM us_table WHERE sito=:s AND us=:u"),
        {"s": sito, "u": us_madre}).fetchone()
    if row is None:
        return
    lst = [list(map(str, e)) for e in _coerce_to_list(row[0])
           if isinstance(e, (list, tuple))]
    target = list(map(str, madre_entry))
    # de-dup on (label, target_us)
    if any(x[:2] == target[:2] for x in lst):
        return
    lst.append(target)
    conn.execute(
        text("UPDATE us_table SET rapporti=:r WHERE sito=:s AND us=:u"),
        {"r": str(lst), "s": sito, "u": us_madre})


def apply_plan(handle, plan, *, remove_orphans=False, lang="it") -> Report:
    """Apply a Plan in a single transaction; return a Report."""
    from sqlalchemy import text
    from ._db_handle import _columns_of
    rep = Report(unchanged=len(plan.unchanged))
    has_node_uuid = "node_uuid" in _columns_of(handle.engine, "us_table")
    with handle.engine.begin() as conn:
        nid = _next_id(conn)
        for rec in plan.to_create:
            if not rec.get("area"):
                rep.warnings.append(f"{rec['us']}: madre senza area")
            _insert_con(conn, rec, nid, has_node_uuid)
            nid += 1
            us_madre = rec["us"].split("CON_", 1)[-1]
            _, madre_entry = _madre_entry_for(rec, us_madre, lang)
            _add_reciprocal_to_madre(conn, rec["sito"], us_madre, madre_entry)
            rep.created += 1
        for rec in plan.to_update:
            _update_con(conn, rec)
            us_madre = rec["us"].split("CON_", 1)[-1]
            _, madre_entry = _madre_entry_for(rec, us_madre, lang)
            _add_reciprocal_to_madre(conn, rec["sito"], us_madre, madre_entry)
            rep.updated += 1
        if remove_orphans:
            for us in plan.orphan:
                conn.execute(text("DELETE FROM us_table WHERE us=:u "
                                  "AND unita_tipo='CON'"), {"u": us})
                rep.orphans_removed += 1
    return rep


def _madre_entry_for(rec, us_madre, lang):
    """Rebuild the (con_entry, madre_entry) pair from a CON record dict."""
    area = rec.get("area") or "1"
    sito = rec["sito"]
    fwd = continuity_label(lang, "forward")
    rev = continuity_label(lang, "reverse")
    return ([fwd, us_madre, area, sito], [rev, rec["us"], area, sito])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/sync/test_continuity_generator.py -q`
Expected: FAIL on `generate_continuity` import (defined in Task 6). Run only the apply test for now:
Run: `python -m pytest tests/sync/test_continuity_generator.py::test_apply_plan_creates_con_and_reciprocal -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add modules/s3dgraphy/sync/continuity_generator.py tests/sync/test_continuity_generator.py
git -c commit.gpgsign=false commit -m "feat(continuity): apply_plan + readers (DbHandle, node_uuid-aware insert)"
```

---

## Task 6: `generate_continuity` orchestrator + auto-backup

**Files:**
- Modify: `modules/s3dgraphy/sync/continuity_generator.py`
- Test: `tests/sync/test_continuity_generator.py` (the idempotent + orphan tests from Task 5)

- [ ] **Step 1: Confirm the failing tests**

Run: `python -m pytest tests/sync/test_continuity_generator.py -q -k "idempotent or orphan"`
Expected: FAIL — `ImportError: cannot import name 'generate_continuity'`.

- [ ] **Step 2: Write minimal implementation** (append)

```python
def build_plan(handle, sito, *, schedatore="", lang="it") -> Plan:
    """Read site → scan → build desired → diff existing. Pure of writes
    (used by the UI to show a dry-run preview before applying)."""
    records = load_site_records(handle, sito)
    desired = [build_con_record(c, schedatore=schedatore, lang=lang)
               for c in scan_candidates(records)]
    return diff_continuity(load_existing_con(handle, sito), desired)


def auto_backup(handle, tag="genera_continuita"):
    """Best-effort pre-write backup. SQLite → file copy; PG → pg_dump.
    Returns the backup path, or None when skipped (caller may warn)."""
    from pathlib import Path
    try:
        from scripts.migrations._common import (
            auto_backup_sqlite, auto_backup_postgres, BackupSkipped)
    except Exception:
        return None
    try:
        if handle.is_postgres:
            return auto_backup_postgres(handle.engine, tag, Path.cwd())
        if handle.sqlite_path:
            return auto_backup_sqlite(Path(handle.sqlite_path), tag)
    except BackupSkipped:
        return None
    return None


def generate_continuity(handle, sito, *, schedatore="", lang="it",
                        remove_orphans=False, do_backup=False) -> Report:
    """End-to-end: build plan, optionally back up, apply, return Report."""
    plan = build_plan(handle, sito, schedatore=schedatore, lang=lang)
    if do_backup and (plan.to_create or plan.to_update or
                      (remove_orphans and plan.orphan)):
        auto_backup(handle)
    return apply_plan(handle, plan, remove_orphans=remove_orphans, lang=lang)
```

- [ ] **Step 3: Run tests to verify they pass**

Run: `python -m pytest tests/sync/test_continuity_generator.py -q`
Expected: PASS (all tasks 2–6 tests).

- [ ] **Step 4: Commit**

```bash
git add modules/s3dgraphy/sync/continuity_generator.py tests/sync/test_continuity_generator.py
git -c commit.gpgsign=false commit -m "feat(continuity): generate_continuity orchestrator + auto-backup"
```

---

## Task 7: UI — "Genera continuità" button + preview/report

**Files:**
- Modify: `gui/rapporti_check_dialog.py`
- Test: `tests/sync/test_continuity_generator.py` (headless smoke via build_plan, no Qt)

> The domain logic is fully tested in Tasks 2–6. The UI is a thin orchestrator; we add a guarded button + handler and a small preview dialog. A Qt-free smoke test already covers `build_plan`; no QGIS test harness is introduced.

- [ ] **Step 1: Add the button** in `RapportiCheckPanel._build_ui`, in the top row after `self.btnRun`:

```python
        self.btnContinuity = QPushButton("Genera continuità")
        self.btnContinuity.setToolTip(
            "Crea/aggiorna le schede CON per le US/USM che attraversano "
            "più periodi (periodo iniziale ≠ finale).")
        self.btnContinuity.clicked.connect(self._run_genera_continuita)
        top.addWidget(self.btnContinuity)
```

- [ ] **Step 2: Add the handler + preview** as a new method on `RapportiCheckPanel`:

```python
    def _run_genera_continuita(self):
        sito = self.cboSite.currentText().strip()
        if not sito:
            return
        from qgis.PyQt.QtWidgets import QDialog, QCheckBox, QDialogButtonBox
        from modules.s3dgraphy.sync import continuity_generator as CG
        try:
            handle = self._handle()
            schedatore = self._current_user()
            plan = CG.build_plan(handle, sito, schedatore=schedatore,
                                 lang=self._lang)
        except Exception as exc:
            QMessageBox.critical(self, "pyArchInit",
                                 f"Genera continuità fallita: {exc}")
            return
        if not (plan.to_create or plan.to_update or plan.orphan):
            QMessageBox.information(
                self, "pyArchInit",
                f"Nessuna continuità da generare per '{sito}'.\n"
                f"({len(plan.unchanged)} già allineate)")
            return
        # Preview dialog
        dlg = QDialog(self)
        dlg.setWindowTitle("Anteprima continuità")
        lay = QVBoxLayout(dlg)
        summary = QTextEdit(); summary.setReadOnly(True)
        lines = [f"Sito: {sito}",
                 f"Da creare: {len(plan.to_create)}",
                 f"Da aggiornare: {len(plan.to_update)}",
                 f"Invariate: {len(plan.unchanged)}",
                 f"Orfane: {len(plan.orphan)}", ""]
        for d in plan.to_create:
            lines.append(f"  + {d['us']}  (periodi {d['periodo_iniziale']}→"
                         f"{d['periodo_finale']})")
        for d in plan.to_update:
            lines.append(f"  ~ {d['us']}  (periodi {d['periodo_iniziale']}→"
                         f"{d['periodo_finale']})")
        for us in plan.orphan:
            lines.append(f"  ? {us}  (orfana)")
        summary.setPlainText("\n".join(lines))
        lay.addWidget(summary)
        chkOrphans = QCheckBox("Rimuovi anche le CON orfane")
        chkOrphans.setEnabled(bool(plan.orphan))
        lay.addWidget(chkOrphans)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.button(QDialogButtonBox.Ok).setText("Genera")
        bb.accepted.connect(dlg.accept); bb.rejected.connect(dlg.reject)
        lay.addWidget(bb)
        dlg.resize(520, 460)
        if dlg.exec_() != QDialog.Accepted:
            return
        try:
            rep = CG.generate_continuity(
                handle, sito, schedatore=schedatore, lang=self._lang,
                remove_orphans=chkOrphans.isChecked(), do_backup=True)
        except Exception as exc:
            QMessageBox.critical(self, "pyArchInit",
                                 f"Generazione fallita: {exc}")
            return
        msg = (f"Continuità generata per '{sito}'.\n"
               f"Create: {rep.created} · Aggiornate: {rep.updated} · "
               f"Invariate: {rep.unchanged} · "
               f"Orfane rimosse: {rep.orphans_removed}")
        if rep.warnings:
            msg += "\n\nAvvisi:\n" + "\n".join(f"• {w}" for w in rep.warnings)
        QMessageBox.information(self, "pyArchInit", msg)

    def _current_user(self):
        try:
            from qgis.core import QgsSettings
            return (QgsSettings().value("pyarchinit/operatore", "", type=str)
                    or "")
        except Exception:
            return ""
```

- [ ] **Step 3: Headless smoke test** (append to `tests/sync/test_continuity_generator.py`)

```python
def test_build_plan_smoke(tmp_path):
    h = _make_db(tmp_path)
    from modules.s3dgraphy.sync.continuity_generator import build_plan
    plan = build_plan(h, "S", schedatore="enzo", lang="it")
    assert [d["us"] for d in plan.to_create] == ["CON_US5"]
```

- [ ] **Step 4: Run test**

Run: `python -m pytest tests/sync/test_continuity_generator.py::test_build_plan_smoke -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add gui/rapporti_check_dialog.py tests/sync/test_continuity_generator.py
git -c commit.gpgsign=false commit -m "feat(gui): Genera continuità button + dry-run preview in rapporti panel"
```

---

## Task 8: Regression — full sync suite + AC-2 baseline

**Files:** none (verification only)

- [ ] **Step 1: Run the full sync suite**

Run: `python -m pytest tests/sync -q`
Expected: PASS for all non-PG tests; pre-existing PG/Spatialite skips unchanged (per memory: 18 PG failures are environment, not regressions). No NEW failures.

- [ ] **Step 2: Confirm AC-2 baseline untouched**

Run: `git status --porcelain tests/sync/fixtures/mini_volterra_baseline_ai03.graphml`
Expected: empty output (the generator never runs at export; baseline byte-identical).

- [ ] **Step 3: Commit** (only if any fixture/import churn needs recording — otherwise skip)

---

## Task 9: CHANGELOG + tutorials (autonomous agents)

- [ ] **Step 1:** Invoke the `tutorial-updater` agent — document the new "Genera continuità" button in the s3dgraphy import dialog, all 9 languages.

- [ ] **Step 2:** Invoke the `stratigraph-changelog` agent — add a bilingual (IT+EN) entry for Feature A (CON continuity automatism).

- [ ] **Step 3: Commit** whatever the agents produced.

```bash
git add dev_logs/CHANGELOG.md docs/tutorials
git -c commit.gpgsign=false commit -m "docs(continuity): changelog + tutorials for Genera continuità"
```

---

## Self-Review

- **Spec coverage:** trigger (Task 7), detection pi≠pf US/USM (Task 2), identity CON_<madre> (Task 3), reciprocal labels (Tasks 1+3+5), inherit all areas = area+other_locations (Tasks 2–3), current-site scope (Task 7 reads `cboSite`), orphan signal + opt-in removal (Tasks 4–7), dedicated 10-lang vocab (Task 1), idempotency (Tasks 4+6), auto-backup (Task 6), error handling — madre senza area warning / null periods skipped / dup reciprocal guard / transaction rollback (Tasks 2+5+6). All covered.
- **Placeholder scan:** none.
- **Type consistency:** `Candidate`/`Plan`/`Report` dataclasses, `con_us_code`, `continuity_label(lang, direction)`, `build_plan`/`generate_continuity` signatures consistent across tasks. `_madre_entry_for` returns the same (con_entry, madre_entry) shape as `desired_rapporti`.
- **Divergence note:** Task 1 adds DATA to `RAPPORTI_SHORTHAND` in dev9-aligned `rapporti.py` — clearly marked "candidate for upstream"; no change to `parse_rapporti` logic. Flag for Emanuel.
- **Out of scope (noted):** export already renders CON rows (verified CON1/CON2); no projector change. Round-trip re-serialise of `is_after` → "Copre" (existing limitation) does not affect generation.
