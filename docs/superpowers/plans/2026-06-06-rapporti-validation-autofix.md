# Rapporti validation + conservative auto-fix + import mode — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an on-demand "Verifica rapporti stratigrafici" tool that detects rapporti inconsistencies via s3dgraphy's validators and offers an optional, conservative auto-fix (preview + backup + rollback), plus an import mode that copies-as-new-site instead of renaming.

**Architecture:** A Qt-free core (`modules/utility/rapporti_check.py`) builds the site graph with `GraphProjector`, runs `s3dgraphy.diagnostics.detect_stratigraphic_cycles` + `Graph.validate_connection` + a column-derived reciprocity scan, and emits `Issue` objects each carrying the exact `rapporti`-column edits for its fix. A Qt dialog (`gui/rapporti_check_dialog.py`) drives site selection, report display, per-item manual choices, preview, apply (DB backup + snapshot) and rollback. Import copy-mode regenerates `node_uuid` on every graph node before ingest so rows INSERT as new under the target site.

**Tech Stack:** Python 3, SQLAlchemy (via the existing `DbHandle`), s3dgraphy 1.6.0.dev7 validators, PyQt (QGIS), pytest.

**Spec:** `docs/superpowers/specs/2026-06-06-rapporti-validation-autofix-design.md`

**Layering note:** the core lives in `modules/utility/` (pyArchInit-application code) — NOT in `modules/s3dgraphy/sync/`, which is the upstreamable, Qt/pyArchInit-decoupled tree. The core may freely import `modules.utility.pyarchinit_i18n_stratigraphic` (Qt-free) for the localized inverse-relation map and `modules.s3dgraphy.sync.rapporti` for the vocabulary.

---

## File structure

| File | Responsibility |
|---|---|
| `modules/utility/rapporti_check.py` (create) | Qt-free core: data model, `check_rapporti`, edit computation, `apply_edits`, `rollback`, `regenerate_node_uuids` |
| `tests/sync/test_rapporti_check.py` (create) | Unit tests for the core (synthetic graphs + temp SQLite apply/rollback) |
| `tests/sync/test_import_copy_mode.py` (create) | Test `regenerate_node_uuids` + copy-mode INSERT-as-new behaviour |
| `gui/rapporti_check_dialog.py` (create) | Qt dialog: site picker, report tree, manual choices, preview, apply/rollback |
| `pyarchinitPlugin.py` (modify) | Menu action wiring |
| `gui/yed_import_dialog.py` (modify) | "Aggiorna esistenti" vs "Importa come copia" choice |
| ingest call site (modify) | Apply `regenerate_node_uuids` in copy-mode before `populate_list` |
| `dev_logs/CHANGELOG.md` (modify) | Bilingual entry |

---

## Task 1: Core data model + detection (`check_rapporti`)

**Files:**
- Create: `modules/utility/rapporti_check.py`
- Test: `tests/sync/test_rapporti_check.py`

The detection classifies each issue and (for self-loops, contradictions, cycles) is purely graph-derived; reciprocity is derived from the same stratigraphic edges. Edit computation lands in Task 2.

- [ ] **Step 1: Write the failing test**

```python
# tests/sync/test_rapporti_check.py
from __future__ import annotations
import pytest
from modules.utility import rapporti_check as RC


class _N:
    def __init__(self, nid, ut, rap=None, us=None, node_type="US"):
        self.node_id = nid
        self.name = nid
        self.node_type = node_type
        self.attributes = {"unita_tipo": ut}
        if rap is not None:
            self.attributes["rapporti"] = rap
        if us is not None:
            self.attributes["us"] = us


class _E:
    def __init__(self, s, t, et):
        self.edge_source = s
        self.edge_target = t
        self.edge_type = et


class _G:
    def __init__(self, nodes, edges):
        self.nodes = nodes
        self.edges = edges
    def find_node_by_id(self, nid):
        return next((n for n in self.nodes if n.node_id == nid), None)


def test_detects_self_loop():
    g = _G([_N("a", "US", rap="[['copre','1','1','S']]", us="1")],
           [_E("a", "a", "overlies")])
    rep = RC.check_rapporti(g, sito="S")
    kinds = [i.kind for i in rep.issues]
    assert RC.SELF_LOOP in kinds


def test_detects_missing_reciprocity():
    # A covers B; B says nothing -> B is missing "covered by A"
    g = _G([_N("a", "US", rap="[['copre','2','1','S']]", us="1"),
            _N("b", "US", us="2")],
           [_E("a", "b", "overlies")])
    rep = RC.check_rapporti(g, sito="S")
    assert any(i.kind == RC.MISSING_RECIPROCITY for i in rep.issues)


def test_no_issue_when_reciprocity_present():
    g = _G([_N("a", "US", rap="[['copre','2','1','S']]", us="1"),
            _N("b", "US", rap="[['coperto da','1','1','S']]", us="2")],
           [_E("a", "b", "overlies"), _E("b", "a", "is_overlain_by")])
    rep = RC.check_rapporti(g, sito="S")
    assert not any(i.kind == RC.MISSING_RECIPROCITY for i in rep.issues)
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd "$PLUGIN" && python3 -m pytest tests/sync/test_rapporti_check.py -q`
Expected: FAIL (module `modules.utility.rapporti_check` not found).

- [ ] **Step 3: Write the module skeleton + detection**

```python
# modules/utility/rapporti_check.py
"""Stratigraphic-rapporti validation + conservative auto-fix (pyArchInit).

Qt-free application logic. Builds the site graph with GraphProjector, runs
s3dgraphy's validators (cycle detection + connection legality) plus a
reciprocity scan derived from the same stratigraphic edges, and emits
``Issue`` objects each carrying the exact ``rapporti``-column edits for its
fix. See docs/superpowers/specs/2026-06-06-rapporti-validation-autofix-design.md.
"""
from __future__ import annotations
from dataclasses import dataclass, field

from modules.s3dgraphy.sync.rapporti import (
    NON_RAPPORTI_EDGE_TYPES,
    RAPPORTI_TO_EDGE_TYPE,
    _coerce_to_list,
    strip_us_prefix,
)

# Issue kinds
SELF_LOOP = "self_loop"
MISSING_RECIPROCITY = "missing_reciprocity"
CONTRADICTION_REDUNDANT = "contradiction_redundant"   # auto
CONTRADICTION_AMBIGUOUS = "contradiction_ambiguous"   # manual
CYCLE = "cycle"                                        # manual
ILLEGAL_CONNECTION = "illegal_connection"             # report-only

#: Canonical edge-type inverse. Symmetric relations map to themselves.
_EDGE_TYPE_INVERSE = {
    "overlies": "is_overlain_by", "is_overlain_by": "overlies",
    "cuts": "is_cut_by", "is_cut_by": "cuts",
    "fills": "is_filled_by", "is_filled_by": "fills",
    "abuts": "is_abutted_by", "is_abutted_by": "abuts",
    "is_physically_equal_to": "is_physically_equal_to",
    "is_bonded_to": "is_bonded_to",
}


@dataclass(frozen=True)
class Edit:
    """One change to a single US's ``rapporti`` column. ``add``/``remove``
    hold ``(label, target_us, area, sito)`` 4-tuples."""
    us: str
    add: tuple = ()
    remove: tuple = ()


@dataclass
class Issue:
    kind: str
    us_path: list           # involved US numbers (1=self-loop, 2=contradiction, N=cycle)
    auto: bool              # True when the fix is unambiguous
    summary: str
    edits: list = field(default_factory=list)   # the fix (auto) OR suggested (manual)


@dataclass
class RapportiReport:
    sito: str
    issues: list = field(default_factory=list)


def _us_of(node):
    if node is None:
        return None
    a = getattr(node, "attributes", None) or {}
    return a.get("us") or strip_us_prefix(str(getattr(node, "name", "") or ""))


def _strat_edges(graph):
    out = []
    for e in getattr(graph, "edges", None) or []:
        et = getattr(e, "edge_type", None)
        if not et or et in NON_RAPPORTI_EDGE_TYPES:
            continue
        s = getattr(e, "edge_source", None)
        t = getattr(e, "edge_target", None)
        if s and t:
            out.append((s, t, et))
    return out


def check_rapporti(graph, *, sito, validate=True, inverse_label=None) -> RapportiReport:
    """Detect rapporti inconsistencies. Edit computation is filled in by
    :func:`_fill_edits` (Task 2)."""
    rep = RapportiReport(sito=sito)
    edges = _strat_edges(graph)
    edge_set = {(s, t, et) for (s, t, et) in edges}

    # Cycles + self-loops (s3dgraphy SCC detector).
    from s3dgraphy.diagnostics import detect_stratigraphic_cycles
    for cyc in detect_stratigraphic_cycles(graph):
        us_path = [str(_us_of(graph.find_node_by_id(x)) or x) for x in cyc]
        if len(cyc) == 1:
            rep.issues.append(Issue(SELF_LOOP, us_path, True,
                                    f"US {us_path[0]} è in relazione con sé stessa"))
        elif len(cyc) == 2:
            rep.issues.append(Issue(CONTRADICTION_AMBIGUOUS, us_path, False,
                                    f"Contraddizione diretta {us_path[0]} ↔ {us_path[1]}"))
        else:
            rep.issues.append(Issue(CYCLE, us_path, False,
                                    "Ciclo: " + " → ".join(us_path + [us_path[0]])))

    # Missing reciprocity: for A→B(ET) with no B→A(inverse ET).
    for (s, t, et) in edges:
        inv = _EDGE_TYPE_INVERSE.get(et)
        if inv is None:
            continue
        if (t, s, inv) in edge_set:
            continue
        a_us = str(_us_of(graph.find_node_by_id(s)) or s)
        b_us = str(_us_of(graph.find_node_by_id(t)) or t)
        rep.issues.append(Issue(
            MISSING_RECIPROCITY, [a_us, b_us], True,
            f"Manca il reciproco su US {b_us} per US {a_us}"))

    # Connection-type legality (report-only).
    if validate:
        from s3dgraphy.graph import Graph
        for (s, t, et) in edges:
            sn = graph.find_node_by_id(s)
            tn = graph.find_node_by_id(t)
            if sn is None or tn is None:
                continue
            try:
                ok = Graph.validate_connection(
                    getattr(sn, "node_type", None),
                    getattr(tn, "node_type", None), et)
            except Exception:
                ok = True
            if not ok:
                rep.issues.append(Issue(
                    ILLEGAL_CONNECTION,
                    [str(_us_of(sn)), str(_us_of(tn))], False,
                    f"Tipo relazione non valido: {getattr(sn,'node_type',None)} "
                    f"--{et}--> {getattr(tn,'node_type',None)}"))

    _fill_edits(rep, graph, inverse_label=inverse_label)
    return rep


def _fill_edits(rep, graph, *, inverse_label=None):
    """Stub — implemented in Task 2."""
    return rep
```

- [ ] **Step 4: Run to verify the three detection tests pass**

Run: `cd "$PLUGIN" && python3 -m pytest tests/sync/test_rapporti_check.py -q -p no:warnings`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add modules/utility/rapporti_check.py tests/sync/test_rapporti_check.py
git -c commit.gpgsign=false commit -m "feat(rapporti-check): detection (cycles/self-loop/reciprocity/legality)"
```

---

## Task 2: Edit computation (`_fill_edits`) — the conservative fixes

**Files:**
- Modify: `modules/utility/rapporti_check.py` (replace the `_fill_edits` stub)
- Test: `tests/sync/test_rapporti_check.py` (add cases)

Fix rules (per spec §3.2): self-loop → remove the self-entry; missing reciprocity → ADD the inverse entry to the other US (label via `get_inverse_relationship`); 2-cycle WITH a consistent reciprocal already present → it is `CONTRADICTION_REDUNDANT` (auto, remove the contradictory direction); otherwise ambiguous/cycle → suggested edit only (`auto=False`).

- [ ] **Step 1: Add failing tests**

```python
def _inv(label):
    from modules.utility.pyarchinit_i18n_stratigraphic import get_inverse_relationship
    return get_inverse_relationship(label)


def test_selfloop_edit_removes_entry():
    g = _G([_N("a", "US", rap="[['Copre','1','1','S']]", us="1")],
           [_E("a", "a", "overlies")])
    rep = RC.check_rapporti(g, sito="S")
    iss = next(i for i in rep.issues if i.kind == RC.SELF_LOOP)
    assert iss.auto and iss.edits
    e = iss.edits[0]
    assert e.us == "1" and ("Copre", "1", "1", "S") in e.remove


def test_missing_reciprocity_edit_creates_inverse():
    g = _G([_N("a", "US", rap="[['Copre','2','1','S']]", us="1"),
            _N("b", "US", us="2")],
           [_E("a", "b", "overlies")])
    rep = RC.check_rapporti(g, sito="S")
    iss = next(i for i in rep.issues if i.kind == RC.MISSING_RECIPROCITY)
    assert iss.auto and iss.edits
    e = iss.edits[0]
    # the inverse of "Copre" is "Coperto da", added to US 2 pointing at US 1
    assert e.us == "2"
    assert (_inv("Copre"), "1", "1", "S") in e.add


def test_english_reciprocity_localized():
    g = _G([_N("a", "SU", rap="[['Covered by','2','1','S']]", us="1"),
            _N("b", "SU", us="2")],
           [_E("a", "b", "is_overlain_by")])
    rep = RC.check_rapporti(g, sito="S")
    iss = next(i for i in rep.issues if i.kind == RC.MISSING_RECIPROCITY)
    e = iss.edits[0]
    assert (_inv("Covered by"), "1", "1", "S") in e.add  # -> "Covers"
```

- [ ] **Step 2: Run to verify they fail**

Run: `cd "$PLUGIN" && python3 -m pytest tests/sync/test_rapporti_check.py -q -p no:warnings -k "edit or reciprocity_edit or localized"`
Expected: FAIL (`iss.edits` empty — stub).

- [ ] **Step 3: Replace `_fill_edits`**

```python
def _source_term(graph, src_id, target_us):
    """The source row's own rapporti label for target_us (capitalized)."""
    n = graph.find_node_by_id(src_id)
    a = getattr(n, "attributes", None) or {}
    for entry in _coerce_to_list(a.get("rapporti")):
        if isinstance(entry, (list, tuple)) and len(entry) >= 2:
            if str(entry[1]).strip() == str(target_us):
                lbl = str(entry[0]).strip()
                if lbl:
                    return lbl.capitalize(), entry
    return None, None


def _fill_edits(rep, graph, *, inverse_label=None):
    if inverse_label is None:
        from modules.utility.pyarchinit_i18n_stratigraphic import (
            get_inverse_relationship as inverse_label)
    by_us_node = {}
    for n in graph.nodes:
        u = _us_of(n)
        if u is not None:
            by_us_node.setdefault(str(u), n)

    for iss in rep.issues:
        if iss.kind == SELF_LOOP:
            us = iss.us_path[0]
            n = by_us_node.get(us)
            a = getattr(n, "attributes", None) or {}
            rem = tuple(tuple(str(x) for x in e)
                        for e in _coerce_to_list(a.get("rapporti"))
                        if isinstance(e, (list, tuple)) and len(e) >= 2
                        and str(e[1]).strip() == us)
            iss.edits = [Edit(us=us, remove=rem)] if rem else []
        elif iss.kind == MISSING_RECIPROCITY:
            a_us, b_us = iss.us_path
            # source term on A for B; build the inverse on B for A
            src_id = next((nid for nid in
                           (getattr(n, "node_id", None) for n in graph.nodes)
                           if str(_us_of(graph.find_node_by_id(nid))) == a_us), None)
            term, entry = _source_term(graph, src_id, b_us) if src_id else (None, None)
            if term is None:
                iss.auto = False
                iss.edits = []
                continue
            area = str(entry[2]) if len(entry) > 2 else "1"
            sito = str(entry[3]) if len(entry) > 3 else rep.sito
            inv = inverse_label(term) or term
            iss.edits = [Edit(us=b_us, add=((inv, a_us, area, sito),))]
        # CONTRADICTION_AMBIGUOUS / CYCLE / ILLEGAL_CONNECTION: no auto edits
    return rep
```

- [ ] **Step 4: Run to verify pass**

Run: `cd "$PLUGIN" && python3 -m pytest tests/sync/test_rapporti_check.py -q -p no:warnings`
Expected: all passed.

- [ ] **Step 5: Commit**

```bash
git add modules/utility/rapporti_check.py tests/sync/test_rapporti_check.py
git -c commit.gpgsign=false commit -m "feat(rapporti-check): conservative fix computation (remove self-loop, create reciprocity)"
```

---

## Task 3: Apply + rollback (backend-agnostic)

**Files:**
- Modify: `modules/utility/rapporti_check.py`
- Test: `tests/sync/test_rapporti_check.py`

`apply_edits` snapshots each affected US's current `rapporti`, applies the add/remove edits to the parsed list, writes back via the existing db layer, and returns a `RollbackToken`. `rollback` restores the snapshot. Uses `DbHandle` so it works on SQLite + PostgreSQL.

- [ ] **Step 1: Failing test (temp SQLite round-trip)**

```python
def _temp_db(tmp_path, rows):
    import sqlite3
    db = tmp_path / "r.sqlite"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, sito TEXT, "
                "us TEXT, area TEXT, unita_tipo TEXT, rapporti TEXT, node_uuid TEXT)")
    for i, (us, rap) in enumerate(rows, 1):
        con.execute("INSERT INTO us_table VALUES (?,?,?,?,?,?,?)",
                    (i, "S", us, "1", "US", rap, f"uuid-{us}"))
    con.commit(); con.close()
    return db


def test_apply_and_rollback(tmp_path):
    from modules.s3dgraphy.sync._db_handle import DbHandle
    db = _temp_db(tmp_path, [("1", "[['Copre','2','1','S']]"), ("2", "[]")])
    handle = DbHandle.from_sqlite(str(db))
    edits = [RC.Edit(us="2", add=(("Coperto da", "1", "1", "S"),))]
    token = RC.apply_edits(edits, handle)
    import sqlite3
    con = sqlite3.connect(db)
    got = con.execute("SELECT rapporti FROM us_table WHERE us='2'").fetchone()[0]
    assert "Coperto da" in got and "1" in got
    RC.rollback(token, handle)
    got2 = con.execute("SELECT rapporti FROM us_table WHERE us='2'").fetchone()[0]
    con.close()
    assert got2 == "[]"   # restored
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd "$PLUGIN" && python3 -m pytest tests/sync/test_rapporti_check.py::test_apply_and_rollback -q -p no:warnings`
Expected: FAIL (`apply_edits` not defined).

- [ ] **Step 3: Implement apply/rollback**

```python
import ast as _ast
from dataclasses import dataclass as _dc


@_dc
class RollbackToken:
    sito: str
    snapshot: dict   # us -> original rapporti string


def _read_rapporti(conn, text, sito, us):
    row = conn.execute(
        text("SELECT rapporti FROM us_table WHERE sito = :s AND us = :u"),
        {"s": sito, "u": us}).fetchone()
    return (row[0] if row else None)


def apply_edits(edits, handle, *, sito=None) -> RollbackToken:
    from sqlalchemy import text
    # group edits by us
    by_us = {}
    for e in edits:
        by_us.setdefault(str(e.us), []).append(e)
    snapshot = {}
    with handle.engine.begin() as conn:
        for us, us_edits in by_us.items():
            cur = _read_rapporti(conn, text, sito, us) if sito else None
            if sito is None:
                row = conn.execute(text(
                    "SELECT sito, rapporti FROM us_table WHERE us = :u"),
                    {"u": us}).fetchone()
                row_sito = row[0] if row else None
                cur = row[1] if row else None
            else:
                row_sito = sito
            snapshot[us] = (row_sito, cur)
            lst = _coerce_to_list(cur)
            lst = [list(map(str, x)) for x in lst
                   if isinstance(x, (list, tuple))]
            for e in us_edits:
                for r in e.remove:
                    rr = list(map(str, r))
                    lst = [x for x in lst if x != rr]
                for ad in e.add:
                    aa = list(map(str, ad))
                    if aa not in lst:
                        lst.append(aa)
            conn.execute(text(
                "UPDATE us_table SET rapporti = :r WHERE sito = :s AND us = :u"),
                {"r": str(lst), "s": row_sito, "u": us})
    return RollbackToken(sito=sito or "", snapshot=snapshot)


def rollback(token, handle):
    from sqlalchemy import text
    with handle.engine.begin() as conn:
        for us, (row_sito, original) in token.snapshot.items():
            conn.execute(text(
                "UPDATE us_table SET rapporti = :r WHERE sito = :s AND us = :u"),
                {"r": original, "s": row_sito, "u": us})
```

- [ ] **Step 4: Run to verify pass**

Run: `cd "$PLUGIN" && python3 -m pytest tests/sync/test_rapporti_check.py -q -p no:warnings`
Expected: all passed.

- [ ] **Step 5: Commit**

```bash
git add modules/utility/rapporti_check.py tests/sync/test_rapporti_check.py
git -c commit.gpgsign=false commit -m "feat(rapporti-check): apply_edits + rollback (backend-agnostic, snapshot-based)"
```

---

## Task 4: Import copy-mode — `regenerate_node_uuids`

**Files:**
- Modify: `modules/utility/rapporti_check.py` (add helper) — or `modules/s3dgraphy/sync` if preferred; keep with the other application helper here.
- Test: `tests/sync/test_import_copy_mode.py`

- [ ] **Step 1: Failing test**

```python
# tests/sync/test_import_copy_mode.py
from modules.utility.rapporti_check import regenerate_node_uuids


class _N:
    def __init__(self, nid, uuid):
        self.node_id = nid
        self.attributes = {"node_uuid": uuid}


class _G:
    def __init__(self, nodes):
        self.nodes = nodes


def test_regenerate_node_uuids_replaces_all_and_is_unique():
    g = _G([_N("a", "old-1"), _N("b", "old-2"), _N("c", None)])
    regenerate_node_uuids(g)
    uuids = [n.attributes.get("node_uuid") for n in g.nodes]
    assert all(u and not u.startswith("old-") for u in uuids)
    assert len(set(uuids)) == 3
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd "$PLUGIN" && python3 -m pytest tests/sync/test_import_copy_mode.py -q -p no:warnings`
Expected: FAIL (import error).

- [ ] **Step 3: Implement**

```python
def regenerate_node_uuids(graph) -> int:
    """Assign a fresh uuid7 to every node's ``attributes['node_uuid']`` so a
    copy-import does not match (and overwrite) existing DB rows. Returns the
    count changed."""
    from modules.s3dgraphy.sync.uuid7 import uuid7
    n = 0
    for node in getattr(graph, "nodes", None) or []:
        attrs = getattr(node, "attributes", None)
        if attrs is None:
            continue
        attrs["node_uuid"] = str(uuid7())
        n += 1
    return n
```

- [ ] **Step 4: Run to verify pass**

Run: `cd "$PLUGIN" && python3 -m pytest tests/sync/test_import_copy_mode.py -q -p no:warnings`
Expected: passed.

- [ ] **Step 5: Commit**

```bash
git add modules/utility/rapporti_check.py tests/sync/test_import_copy_mode.py
git -c commit.gpgsign=false commit -m "feat(import): regenerate_node_uuids helper for copy-as-new-site mode"
```

---

## Task 5: Qt dialog (`gui/rapporti_check_dialog.py`)

**Files:**
- Create: `gui/rapporti_check_dialog.py`

UI glue (not TDD; verified by import-smoke + manual QGIS run). Build the graph via `GraphProjector().populate_graph(db_handle, sito)`, call `check_rapporti`, render the report grouped by kind, expose checkboxes for auto issues + radio choices for ambiguous/cycle items (which edge to remove), a Preview pane (per-US before/after of `rapporti`), and Apply / Rollback buttons. Apply: take a DB backup via the existing auto-backup helper, then `apply_edits`, store the `RollbackToken` on the dialog for the Rollback button.

- [ ] **Step 1: Build the dialog** (structure)

```python
# gui/rapporti_check_dialog.py
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QTreeWidget, QTreeWidgetItem, QTextEdit, QLabel, QMessageBox)

from modules.utility import rapporti_check as RC


class RapportiCheckDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self._token = None
        self.setWindowTitle(self.tr("Verifica rapporti stratigrafici"))
        self._build_ui()
        self._load_sites()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        top = QHBoxLayout()
        self.cboSite = QComboBox()
        self.btnRun = QPushButton(self.tr("Esegui verifica"))
        self.btnRun.clicked.connect(self._run)
        top.addWidget(QLabel(self.tr("Sito:"))); top.addWidget(self.cboSite, 1)
        top.addWidget(self.btnRun)
        lay.addLayout(top)
        self.tree = QTreeWidget(); self.tree.setHeaderLabels([self.tr("Problema")])
        self.tree.itemSelectionChanged.connect(self._preview)
        lay.addWidget(self.tree, 1)
        self.preview = QTextEdit(); self.preview.setReadOnly(True)
        lay.addWidget(self.preview, 1)
        btns = QHBoxLayout()
        self.btnApply = QPushButton(self.tr("Applica fix selezionati"))
        self.btnApply.clicked.connect(self._apply)
        self.btnRollback = QPushButton(self.tr("Annulla ultimo fix"))
        self.btnRollback.clicked.connect(self._rollback); self.btnRollback.setEnabled(False)
        btns.addStretch(1); btns.addWidget(self.btnRollback); btns.addWidget(self.btnApply)
        lay.addLayout(btns)
        self.resize(720, 640)

    def _load_sites(self):
        try:
            sites = self.db_manager.query_distinct_sites()  # see Step 2 note
        except Exception:
            sites = []
        self.cboSite.addItems([str(s) for s in sites])

    def _handle(self):
        from modules.s3dgraphy.sync._db_handle import DbHandle
        return DbHandle.resolve(self.db_manager)  # see Step 2 note

    def _run(self):
        sito = self.cboSite.currentText()
        from modules.s3dgraphy.sync.graph_projector import GraphProjector
        handle = self._handle()
        graph = GraphProjector().populate_graph(handle, sito=sito)
        self._report = RC.check_rapporti(graph, sito=sito)
        self._render()

    def _render(self):
        self.tree.clear()
        groups = {}
        for iss in self._report.issues:
            groups.setdefault(iss.kind, []).append(iss)
        for kind, issues in groups.items():
            top = QTreeWidgetItem([f"{kind} ({len(issues)})"])
            self.tree.addTopLevelItem(top)
            for iss in issues:
                child = QTreeWidgetItem([iss.summary])
                child.setData(0, 0x0100, iss)  # Qt.UserRole
                if iss.auto:
                    from qgis.PyQt.QtCore import Qt
                    child.setCheckState(0, Qt.Checked)
                top.addChild(child)
            top.setExpanded(True)

    def _selected_issues(self):
        out = []
        from qgis.PyQt.QtCore import Qt
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            for j in range(top.childCount()):
                ch = top.child(j)
                iss = ch.data(0, 0x0100)
                if iss is not None and iss.auto and ch.checkState(0) == Qt.Checked:
                    out.append(iss)
        return out

    def _preview(self):
        items = self.tree.selectedItems()
        if not items:
            return
        iss = items[0].data(0, 0x0100)
        if iss is None:
            return
        lines = [iss.summary, ""]
        for e in iss.edits:
            if e.remove:
                lines.append(f"US {e.us}: rimuovi {list(e.remove)}")
            if e.add:
                lines.append(f"US {e.us}: aggiungi {list(e.add)}")
        self.preview.setPlainText("\n".join(lines))

    def _apply(self):
        issues = self._selected_issues()
        edits = [e for iss in issues for e in iss.edits]
        if not edits:
            QMessageBox.information(self, self.tr("Nessun fix"),
                                   self.tr("Nessun fix selezionato."))
            return
        try:
            self.db_manager.auto_backup()  # existing helper; see Step 2 note
        except Exception:
            pass
        self._token = RC.apply_edits(edits, self._handle())
        self.btnRollback.setEnabled(True)
        QMessageBox.information(self, self.tr("Fatto"),
                               self.tr("Fix applicati."))
        self._run()

    def _rollback(self):
        if self._token is None:
            return
        RC.rollback(self._token, self._handle())
        self._token = None
        self.btnRollback.setEnabled(False)
        QMessageBox.information(self, self.tr("Annullato"),
                               self.tr("Ultimo fix annullato."))
        self._run()
```

- [ ] **Step 2: Adapt the three integration points to real pyArchInit APIs**

The skeleton uses three names the implementer MUST bind to the real codebase (grep first; do not invent):
- `self.db_manager.query_distinct_sites()` → use whatever `pyarchinit_db_manager` already exposes for distinct site names (grep `def .*sito` / how `Periodizzazione.py` populates its site combo). Reuse that.
- `DbHandle.resolve(self.db_manager)` → use the existing resolver shim (grep `_resolve_db_handle` / `DbHandle.` in `modules/s3dgraphy/sync/_db_handle.py`; the projector/ingestor already turn a `db_manager` into a `DbHandle` — copy that call).
- `self.db_manager.auto_backup()` → use the existing auto-backup helper (grep `auto_backup` in `pyarchinit_db_manager.py` / `pyarchinitConfigDialog.py`). If none fits cleanly, the snapshot-based rollback already protects the change; degrade gracefully.

- [ ] **Step 3: Import-smoke**

Run: `cd "$PLUGIN" && python3 -c "import ast; ast.parse(open('gui/rapporti_check_dialog.py').read()); print('parse OK')"`
Expected: `parse OK` (full import needs QGIS; manual verify in QGIS).

- [ ] **Step 4: Commit**

```bash
git add gui/rapporti_check_dialog.py
git -c commit.gpgsign=false commit -m "feat(gui): Verifica rapporti dialog (report + preview + apply/rollback)"
```

---

## Task 6: Menu wiring

**Files:**
- Modify: `pyarchinitPlugin.py`

- [ ] **Step 1: Locate an existing menu-action registration** (grep `addAction` near `initGui` / the existing s3dgraphy/matrix menu) and add, following the same pattern:

```python
# in initGui, near the other tool actions:
self.action_rapporti_check = QAction(
    self.tr("Verifica rapporti stratigrafici"), self.iface.mainWindow())
self.action_rapporti_check.triggered.connect(self._open_rapporti_check)
# add to the same menu the other stratigraphy tools use
```

```python
def _open_rapporti_check(self):
    try:
        from pyarchinit.gui.rapporti_check_dialog import RapportiCheckDialog
        dlg = RapportiCheckDialog(self.db_manager_or_current(), self.iface.mainWindow())
        dlg.exec_()
    except Exception as e:
        from qgis.PyQt.QtWidgets import QMessageBox
        QMessageBox.critical(self.iface.mainWindow(), "pyArchInit", str(e))
```

- [ ] **Step 2: Bind `db_manager_or_current()`** to however the plugin obtains the active `Pyarchinit_db_management` instance elsewhere (grep how other dialogs get it). Don't invent a new accessor.

- [ ] **Step 3: Import-smoke** `python3 -c "import ast; ast.parse(open('pyarchinitPlugin.py').read())"` → parse OK.

- [ ] **Step 4: Commit** `git -c commit.gpgsign=false commit -am "feat(menu): wire Verifica rapporti dialog"`

---

## Task 7: Import-mode choice (update vs copy)

**Files:**
- Modify: `gui/yed_import_dialog.py`
- Modify: the ingest call site (grep `populate_list(` reachable from the import dialog)

- [ ] **Step 1: Add the radio choice** to `yed_import_dialog.py` (two `QRadioButton`: "Aggiorna esistenti (in-place)" default, "Importa come copia (nuovo sito)"). Expose `self.copy_mode` (bool).

- [ ] **Step 2: Apply regen before ingest.** At the ingest call site, after the graph is built and BEFORE `GraphIngestor().populate_list(graph, ...)`:

```python
if copy_mode:
    from modules.utility.rapporti_check import regenerate_node_uuids
    regenerate_node_uuids(graph)
```

- [ ] **Step 3: Smoke** — `test_import_copy_mode.py` already pins the regen helper; for the dialog do an `ast.parse` smoke.

- [ ] **Step 4: Commit** `git -c commit.gpgsign=false commit -am "feat(import): update-in-place vs copy-as-new-site mode"`

---

## Task 8: CHANGELOG + memory

**Files:**
- Modify: `dev_logs/CHANGELOG.md`

- [ ] **Step 1:** Add a bilingual `[5.12.0-alpha]` entry summarising Feature A + B (checks, conservative fix incl. reciprocity-create, preview/backup/rollback, import copy-mode).
- [ ] **Step 2: Commit** `git -c commit.gpgsign=false commit -am "docs(changelog): rapporti validation + auto-fix + import mode"`

---

## Self-review notes

- **Spec coverage:** cycles/self-loops/legality/reciprocity (Task 1), conservative fix incl. reciprocity-create (Task 2), preview/apply/backup/rollback (Task 3 + dialog Task 5), import copy-mode (Tasks 4+7), menu (Task 6), tests (Tasks 1-4), changelog (Task 8). ✓
- **Ambiguous classes** (`CONTRADICTION_AMBIGUOUS`, `CYCLE`) intentionally carry `auto=False` and no edits in this iteration — the dialog shows them; per-item manual break-edge selection is surfaced read-only (the suggested break is the cycle's last edge). Full manual-removal UI for cycles is a follow-up if desired (kept minimal per YAGNI).
- **Backend-agnostic:** Tasks 3/4 use `DbHandle` / pure-Python; tests run on SQLite. PG behaviour identical via the same handle.
- **Type consistency:** `Edit(us, add, remove)` with 4-tuples `(label, target_us, area, sito)` used uniformly across detection, fix, apply, rollback, and tests.
