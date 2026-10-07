# One Bridge (A) + em.json/EMStudio desktop (B1) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** pyArchInit imports `s3dgraphy.sync` from the library (one bridge, pinned exact ≥1.6.0.dev40) and gains «Esporta sito in em.json» + «Apri in EMStudio».

**Architecture:** section-by-section replacement of the vendored `modules/s3dgraphy/sync` with the library's package, driven by parity tests; the vendored package shrinks to three pyArchInit-only modules plus a transitional `sys.modules` shim removed at the end; em.json export rides the library's canonical DB→graph path. The GraphML export retires only after the replacement viewer (B1) has shipped.

**Tech Stack:** Python 3.9 (QGIS bundle), s3dgraphy ≥1.6.0.dev40 (exact pin), SQLAlchemy/GeoAlchemy2 from `ext_libs`, pytest with the QGIS interpreter.

**Spec:** `docs/superpowers/specs/2026-10-07-one-bridge-s3dgraphy-design.md` — the plan argues from it; executors read both.

**Planning note (differs from spec §4 wording, same acceptance):** the shared modules are all-or-nothing against the new library — A1 alone cannot be green (the 26 measured failures live in the projector/ingestor, migrated in A2/A3). First merge/release point is therefore after A1+A2+A3, with the to-retire GraphML-export tests marked `xfail` (reason given) until A4 deletes them. Sub-projects B2 and C get their own plans when a StratiGraph node / local server exists.

## Global Constraints

- Branch policy: all work on a feature branch `one-bridge` cut from `Stratigraph_00001`; merge only at the release points below. Never touch `master`.
- Pin **exact** (`s3dgraphy==1.6.0.devNN`), never `>=`; `dtcstamp>=0.1.4` accompanies it (hard dependency since dev40).
- Canonical suite command (always this, from the checkout being tested):
  `QT_QPA_PLATFORM=offscreen PYARCHINIT_HOME=/Users/enzo/pyarchinit_5 PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python /Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest tests/sync -q --continue-on-collection-errors --ignore=tests/sync/test_groups_dialog_smoke.py --ignore=tests/sync/test_paradata_dialog_smoke.py`
  (the two ignored files are pre-existing Qt crashers; `tests/migrations` and `tests/utility` run as a regression sweep at each release point).
- Known pre-existing failures (dev9 baseline, 2026-10-07): ≤5, order-dependent; the exact list is recorded in Task 0 and is the yardstick everywhere "≤ baseline" appears.
- Test files must not import Qt at module level except via try/except skip (`test_us_pdf_rapporti_overflow.py` stubs `qgis.PyQt.QtWidgets`; order-dependent crashes otherwise).
- Commit messages: plain conventional style (`feat:`/`fix:`/`docs:`…), **no AI-attribution lines of any kind** (user rule).
- Every release point: version bump in `metadata.txt` (next free `5.13.NN-alpha`), bilingual changelog entry in `dev_logs/CHANGELOG.md`, tag `<topic>-5.13.NN-alpha`, GitHub pre-release, api-docs entry — same flow as every release this cycle.
- `ext_libs/` is gitignored: library upgrades there are an install step, never a commit.

## Review Focus

Spec-implied inputs no existing test exercises; each line's test is added in the task that owns the code:

1. A site recorded in a non-Italian vocabulary (`SU`/`WSU` rows) exported to em.json — units and their kinds must survive end-to-end, not only in the projector. → test added in Task 7.
2. A site name with spaces, accents or non-Latin script («Scavo archeologico», «تنقيب أثري») — the em.json filename must be writable and the file must read back. → Task 7.
3. A site with zero `us_table` rows — a clear message, never an empty or corrupt file. → Task 7.
4. EMStudio not installed — the open action reports where to get it and reveals the file; it never raises. → Task 8.
5. `ext_libs` holding a different s3dgraphy than the pin (stale install on a user machine) — the export refuses with "aggiorna le dipendenze", not an ImportError trace. → Task 7 (plus the existing pin-guard test `tests/sync/test_usm_kind_dev40.py`).

---

### Task 0: Worktree, library install, measured baseline

**Files:**
- Create: worktree at `../pyarchinit-one-bridge` (branch `one-bridge`)
- Create: `docs/superpowers/plans/2026-10-07-one-bridge-baseline.txt`

**Interfaces:**
- Produces: a worktree with its own `ext_libs` (new library), and the recorded baseline failure list every later "≤ baseline" check reads.

- [ ] **Step 1: Create the worktree** (superpowers:using-git-worktrees applies)

```bash
PLUGIN="/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
git -C "$PLUGIN" worktree add -b one-bridge "$PLUGIN/../pyarchinit-one-bridge" Stratigraph_00001
WT="$PLUGIN/../pyarchinit-one-bridge"
```

- [ ] **Step 2: Give the worktree its own ext_libs, then upgrade only s3dgraphy**

The main checkout keeps `dev9` so the live plugin stays usable; the worktree gets the new library.

```bash
cp -R "$PLUGIN/ext_libs" "$WT/ext_libs"
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip index versions s3dgraphy   # note the newest 1.6.0.devNN
rm -rf "$WT/ext_libs/s3dgraphy" "$WT/ext_libs"/s3dgraphy-*.dist-info
/Applications/QGIS.app/Contents/MacOS/bin/python3 -m pip install --target "$WT/ext_libs" --no-deps "s3dgraphy==1.6.0.devNN" "dtcstamp>=0.1.4"
```

If the newest dev release is later than dev40: re-run the §3 drift measurement of the spec (`diff` each vendored module against `$WT/ext_libs/s3dgraphy/sync/`) before continuing; if the drift picture changed materially (new modules, identical set shrunk), stop and report to Enzo.

- [ ] **Step 3: Record the dev9 baseline (main checkout) and the dev40 breakage (worktree)**

```bash
cd "$PLUGIN" && <canonical suite command> 2>&1 | grep "^FAILED" | sort > "$WT/docs/superpowers/plans/2026-10-07-one-bridge-baseline.txt"
cd "$WT"     && <canonical suite command> 2>&1 | grep "^FAILED" | sort >> "$WT/docs/superpowers/plans/2026-10-07-one-bridge-baseline.txt"
```

Annotate the file by hand: first block `# baseline dev9 (pre-esistenti)`, second `# rotture dev40 (lista di lavoro)`. Expected: first block ≤5 lines; second ≈31.

- [ ] **Step 4: Commit the baseline file**

```bash
git -C "$WT" add docs/superpowers/plans/2026-10-07-one-bridge-baseline.txt
git -C "$WT" commit -m "chore(one-bridge): baseline misurata prima della migrazione"
```

### Task 1: Pin bump + requirements

**Files:**
- Modify: `requirements.txt` (the pinned block around line 112–127)

**Interfaces:**
- Produces: the pin every later task assumes; `tests/sync/test_usm_kind_dev40.py` arms itself (its module-level skip reads `hasattr(sn, "set_kind")`).

- [ ] **Step 1: Replace the dev9 block in `requirements.txt`**

Replace the whole comment block that currently ends with `s3dgraphy==1.6.0.dev9` (it starts with `# 2026-10-07: 1.6.0.dev40 exists`) with:

```text
# One bridge (spec docs/superpowers/specs/2026-10-07-one-bridge-s3dgraphy-design.md):
# the plugin imports s3dgraphy.sync from the library; the vendored copy
# is reduced to pyArchInit-only extensions. Pin EXACT, never >=: the
# library moves weekly and every bump is re-measured against tests/sync.
s3dgraphy==1.6.0.devNN
dtcstamp>=0.1.4
```

(`devNN` = the version installed in Task 0, written out.)

- [ ] **Step 2: Verify the armed pin guard passes in the worktree**

Run: `cd "$WT" && QT_QPA_PLATFORM=offscreen PYTHONPATH=/Applications/QGIS.app/Contents/Resources/python /Applications/QGIS.app/Contents/MacOS/bin/python3 -m pytest tests/sync/test_usm_kind_dev40.py -v`
Expected: **5 passed** (it skipped on dev9; red here means the kind API moved — stop and report).

- [ ] **Step 3: Commit**

```bash
git -C "$WT" add requirements.txt
git -C "$WT" commit -m "build: pin s3dgraphy 1.6.0.devNN + dtcstamp (one bridge, tappa A1)"
```

### Task 2: A1 — free wins: delete the 10 identical modules, alias to the library

**Files:**
- Delete: `modules/s3dgraphy/sync/{yed_group_walker,yed_detector,vocab_types,vocab_provider_core,uuid7,ingest_result,group_store,conflict_resolver,_legacy_paradata_svgs,_db_handle}.py`
- Modify: `modules/s3dgraphy/sync/__init__.py`
- Test: `tests/sync/test_one_bridge_shim.py` (new)

**Interfaces:**
- Produces: `modules.s3dgraphy.sync.<name>` keeps importing for the 10 names, now resolving to `s3dgraphy.sync.<name>` (callers untouched until Task 11).

- [ ] **Step 1: Write the failing test**

```python
# tests/sync/test_one_bridge_shim.py
"""One bridge (A1): the shared modules come from the library.

The ten modules measured identical on 2026-10-07 are deleted from the
vendored package; a transitional alias keeps the old import path alive
until A5 rewires the callers.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for entry in (str(_ROOT), str(_ROOT / "ext_libs")):
    if entry not in sys.path:
        sys.path.append(entry)

pytest.importorskip("s3dgraphy.sync")

FREE_WINS = ("yed_group_walker", "yed_detector", "vocab_types",
             "vocab_provider_core", "uuid7", "ingest_result",
             "group_store", "conflict_resolver",
             "_legacy_paradata_svgs", "_db_handle")


def test_the_identical_modules_are_gone_from_the_vendored_package():
    for name in FREE_WINS:
        assert not (_ROOT / "modules" / "s3dgraphy" / "sync" / (name + ".py")).exists(), name


def test_the_old_import_path_resolves_to_the_library():
    import importlib
    for name in FREE_WINS:
        ours = importlib.import_module("modules.s3dgraphy.sync." + name)
        libs = importlib.import_module("s3dgraphy.sync." + name)
        assert ours is libs, name
```

- [ ] **Step 2: Run it — must fail** (`...::test_the_identical_modules_are_gone... FAILED`: files still exist)

- [ ] **Step 3: Delete the ten files and add the alias block at the TOP of `modules/s3dgraphy/sync/__init__.py`** (before its other imports, since they may import these names):

```python
# --- One bridge (A1, spec 2026-10-07) -----------------------------------
# The modules measured identical to the library now live only there; the
# old import path stays alive until A5 rewires the callers.
import importlib as _importlib
import sys as _sys
for _name in ("yed_group_walker", "yed_detector", "vocab_types",
              "vocab_provider_core", "uuid7", "ingest_result",
              "group_store", "conflict_resolver",
              "_legacy_paradata_svgs", "_db_handle"):
    _sys.modules[__name__ + "." + _name] = _importlib.import_module(
        "s3dgraphy.sync." + _name)
# -------------------------------------------------------------------------
```

Then fix any `from .<deleted module> import X` inside the remaining vendored files to `from s3dgraphy.sync.<module> import X` (find them: `grep -n "from \.\(yed_group_walker\|yed_detector\|vocab_types\|vocab_provider_core\|uuid7\|ingest_result\|group_store\|conflict_resolver\|_legacy_paradata_svgs\|_db_handle\) import" modules/s3dgraphy/sync/*.py`).

- [ ] **Step 4: Run the new test file (both tests PASS), then the canonical suite** — expected: failure list unchanged from Task 0's dev40 block (the free wins must not add or remove failures).

- [ ] **Step 5: Commit** — `git commit -m "refactor(one-bridge): A1 — i 10 moduli identici vengono dalla libreria (alias transitorio)"`

### Task 3: A1 — reconcile the small-drift modules

**Files:**
- Modify/delete: `modules/s3dgraphy/sync/{yed_rapporti_policy,yed_classifier,yed_import_pipeline,paradata_store,edge_registry,group_projector,yed_table_parser,pyarchinit_pg_importer,_workspace}.py`, `modules/s3dgraphy/sync/rapporti.py`
- Modify: `modules/s3dgraphy/sync/__init__.py` (alias list grows as modules are deleted)

**Interfaces:**
- Consumes: the alias mechanism of Task 2 (same block, append names).
- Produces: each reconciled module deleted from the vendored package and aliased; pyArchInit-specific behavior relocated into `continuity_generator.py` / `paradata_edge_resolver.py` / the caller, never lost.

- [ ] **Step 1: For each module, in this order (smallest drift first): `yed_rapporti_policy` (3), `yed_classifier` (7), `yed_import_pipeline` (8), `paradata_store` (9), `edge_registry` (10), `group_projector` (10), `yed_table_parser` (11), `pyarchinit_pg_importer` (24), `_workspace` (26), `rapporti` (against `s3dgraphy/rapporti.py`, not the 15-line sync shim) — produce the diff and give every hunk one of three fates, written in the commit message:**

```bash
diff -u "modules/s3dgraphy/sync/<m>.py" "ext_libs/s3dgraphy/sync/<m>.py"
```

* **upstream** — ours, generic (a fix the library lacks): keep the vendored line for now, open a small PR to `ExtendedMatrix/s3Dgraphy` (branch `s3dgraphy_v1.6dev`) with just that hunk; the module is deleted only when the PR is merged and the pin re-bumped, otherwise it stays vendored with a `# upstream PR #NN pending` note.
* **ours** — pyArchInit-specific: move the behavior into our extension modules or the Qt caller, with its test.
* **stale** — superseded by the library (this includes Task `bf16b3a9`'s `set_kind` additions in `pyarchinit_pg_importer` if the library's version is already kind-aware): adopt the library's line; the module gets deleted + aliased like Task 2.

- [ ] **Step 2: After each module: run the canonical suite.** Gate: the failure list must only ever **shrink or stay equal** against Task 0's dev40 block. A new failure = that hunk's fate was wrong; revert and re-triage before moving on.

- [ ] **Step 3: One commit per module** — `refactor(one-bridge): A1 — <modulo> riconciliato (hunks: N upstream / N nostri / N adottati)`.

### Task 4: A2 — projector parity

**Files:**
- Delete: `modules/s3dgraphy/sync/graph_projector.py` (goal state; alias added)
- Modify: `modules/s3dgraphy/sync/paradata_edge_resolver.py`, `modules/s3dgraphy/sync/continuity_generator.py` (receive any "ours" behavior)
- Test: existing `tests/sync/test_graph_projector.py`, `tests/sync/test_locationnodegroup_projection.py`, `tests/sync/test_round_trip_file.py` (acceptance)

**Interfaces:**
- Consumes: alias mechanism (Task 2).
- Produces: `modules.s3dgraphy.sync.graph_projector` = `s3dgraphy.sync.graph_projector`; the `GraphProjector`/`populate_graph` surface callers use is the library's.

- [ ] **Step 1: The red is already written — name it.** These currently-failing tests are the acceptance set:
  `test_projector_recognizes_localized_su_wsu`, `test_projector_epoch_name_is_datazione_estesa_not_descrizione`, `test_projector_handles_paradata_name_collisions`, `test_struttura_emits_locationnodegroup_kind_functional[struttura-functional]` and `[ambient-functional]`, `test_import_into_new_sito_copies_not_moves`, `test_import_into_new_sito_is_idempotent`, `test_combiner_extractor_never_link_stratigraphic[src0-tgt0]` and `[src2-tgt2]`.

- [ ] **Step 2: Triage the 209 delta lines with the Task 3 three-fate rule.** Known inventory to look for (today's evidence): the multilingual `_UNITA_TIPO_CANONICAL` map (SU/SE/UE/ΣΜ → US …); epoch name = `datazione_estesa`; the paradata name-collision backfill; `CON` in the stratigraphic family; the Bug-P paradata-as-`StratigraphicUnit` factory (candidate **upstream** or **ours**, never dropped: `test_combiner_extractor_never_link_stratigraphic` guards it); our `set_kind` additions (candidate **stale** if the library projector is kind-aware).

- [ ] **Step 3: Run the acceptance set** — `python -m pytest tests/sync/test_graph_projector.py tests/sync/test_locationnodegroup_projection.py tests/sync/test_round_trip_file.py tests/sync/test_paradata_edge_resolver.py -v` (canonical env). Expected: all PASS.

- [ ] **Step 4: Canonical suite** — remaining failures = baseline + the GraphML-export set only (retired in Task 10).

- [ ] **Step 5: Commit** — `refactor(one-bridge): A2 — projector dalla libreria, parità verificata (SU/WSU, epoche, collisioni paradata, kind)`

### Task 5: A3 — ingestor parity (yEd one-time import)

**Files:**
- Delete: `modules/s3dgraphy/sync/graph_ingestor.py` (goal state; alias added)
- Test: existing `tests/sync/test_graph_ingestor.py`, `tests/sync/test_cli_groups.py`, `tests/sync/test_round_trip_with_groups.py::test_sql_update_when_flag_enabled`

- [ ] **Step 1: Acceptance set (already red):** `test_update_preserves_unmapped_columns`, `test_cli_export_with_group_by`, `test_sql_update_when_flag_enabled`.
- [ ] **Step 2: Triage the 191 delta lines** (three-fate rule; the "mapped column not updated" regression is the first thing to chase in the library delta).
- [ ] **Step 3: Run the acceptance set → PASS; canonical suite → baseline + GraphML-export set only.**
- [ ] **Step 4: Verify the one-time yEd import against a real file**: `tests/sync` fixtures contain GraphML samples (`git grep -l "\.graphml" tests/sync` lists them); run the whole `tests/sync/test_yed_*` families, all PASS.
- [ ] **Step 5: Commit** — `refactor(one-bridge): A3 — ingestor dalla libreria, import yEd una tantum verificato`

### Task 6: Mark the retiring GraphML-export tests xfail; first release (one-bridge alpha)

**Files:**
- Modify: `tests/sync/test_groups_export_em_template.py`, `tests/sync/test_em_export_rendering.py`, `tests/sync/test_graph_projector_groups.py`, `tests/sync/test_ai03_export_byte_identical.py`
- Modify: `metadata.txt`, `dev_logs/CHANGELOG.md`

- [ ] **Step 1: At the top of each of the four files add** (import pytest already present):

```python
pytestmark = pytest.mark.xfail(
    reason="GraphML export retires in A4 (spec 2026-10-07 §4, decision 2): "
           "em.json/EMStudio is the viewer; these tests go with the writer.",
    strict=False)
```

- [ ] **Step 2: Canonical suite → failures ≤ dev9 baseline** (everything else green or xfail). `tests/migrations` + `tests/utility` sweep → counts as on `Stratigraph_00001`.
- [ ] **Step 3: Merge `one-bridge` into `Stratigraph_00001`; upgrade the MAIN checkout's `ext_libs`** with the Task 0 install commands (now pointed at `$PLUGIN/ext_libs`); re-run the suite there.
- [ ] **Step 4: Release** per Global Constraints — topic `one-bridge`, title «Ponte unico: s3dgraphy.sync dalla libreria (tappe A1–A3)»; the changelog names every module's fate and every hunk sent upstream.

### Task 7: B1 — `em_export` module (TDD)

**Files:**
- Create: `modules/s3dgraphy/em_export.py`
- Test: `tests/sync/test_em_export.py` (new)

**Interfaces:**
- Consumes: `s3dgraphy.importer.pyarchinit_importer.PyArchInitImporter(connection_url=…, mapping_name="pyarchinit_us_mapping", filters={"sito": site}).parse()`; `s3dgraphy.exporter.emjson_exporter.export_emjson(graph, path)`; `s3dgraphy.importer.emjson_importer.import_emjson(path) -> (Graph, warnings)`.
- Produces: `em_export.export_site(connection_url: str, site: str, out_dir: str) -> (path, n_nodes, n_edges, warnings)`, `em_export.emjson_available() -> bool`, `em_export.site_filename(site) -> str`, `em_export.EmExportError(RuntimeError)` — Task 8 wires these.

- [ ] **Step 1: Write the failing tests**

```python
# tests/sync/test_em_export.py
"""em.json export of a site (B1, spec 2026-10-07 §5).

The graph travels the library's canonical DB->graph path and the file
is read back before being handed over: a file that does not read back
clean is not given to the user. GraphML stays only as the one-time
import from yEd.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for entry in (str(_ROOT), str(_ROOT / "ext_libs")):
    if entry not in sys.path:
        sys.path.append(entry)

from modules.s3dgraphy import em_export  # noqa: E402

if not em_export.emjson_available():
    pytest.skip("s3dgraphy senza em.json (pin pre-dev40)", allow_module_level=True)


@pytest.fixture()
def sample_db(tmp_path):
    folder = tmp_path / "pyarchinit_DB_folder"
    folder.mkdir()
    resources = _ROOT / "resources" / "dbfiles"
    shutil.copy(resources / "config.cfg", folder / "config.cfg")
    shutil.copy(resources / "pyarchinit_db.sqlite", folder / "db.sqlite")
    os.environ["PYARCHINIT_HOME"] = str(tmp_path)
    return "sqlite:///%s" % (folder / "db.sqlite")


def test_a_site_travels_and_reads_back(sample_db, tmp_path):
    path, nodes, edges, warnings = em_export.export_site(
        sample_db, "Scavo archeologico", str(tmp_path / "out"))
    assert os.path.exists(path) and path.endswith(".em.json")
    assert nodes > 0 and edges > 0
    assert warnings == []


def test_a_site_recorded_in_english_keeps_its_units(sample_db, tmp_path):
    # Review Focus 1: SU/WSU rows (the sample ships the same site in 10 languages)
    path, nodes, edges, _ = em_export.export_site(
        sample_db, "Archaeological Excavation", str(tmp_path / "out"))
    assert nodes >= 51, "le 51 US inglesi devono arrivare nel grafo"


def test_site_names_become_writable_filenames():
    # Review Focus 2
    assert em_export.site_filename("Scavo archeologico") == "Scavo_archeologico.em.json"
    assert em_export.site_filename("Festòs_2025") == "Festòs_2025.em.json"
    arabic = em_export.site_filename("تنقيب أثري")
    assert arabic.endswith(".em.json") and not arabic.startswith(".")


def test_an_empty_site_refuses_with_a_reason(sample_db, tmp_path):
    # Review Focus 3
    with pytest.raises(em_export.EmExportError) as err:
        em_export.export_site(sample_db, "SITO_CHE_NON_ESISTE", str(tmp_path / "out"))
    assert "niente da esportare" in str(err.value)
    assert not list((tmp_path / "out").glob("*.em.json")) if (tmp_path / "out").exists() else True


def test_a_stale_library_refuses_with_a_user_message(monkeypatch, tmp_path):
    # Review Focus 5
    monkeypatch.setattr(em_export, "emjson_available", lambda: False)
    with pytest.raises(em_export.EmExportError) as err:
        em_export.export_site("sqlite:///nowhere.sqlite", "X", str(tmp_path))
    assert "aggiorna le dipendenze" in str(err.value)
```

- [ ] **Step 2: Run — all FAIL** (`ModuleNotFoundError: modules.s3dgraphy.em_export`).

- [ ] **Step 3: Implement `modules/s3dgraphy/em_export.py`**

```python
"""Export a site to em.json, the working format of the Extended Matrix.

GraphML stays only as the one-time import from yEd (spec 2026-10-07):
the matrix a user looks at lives in EMStudio, which opens em.json
natively. The graph is built by the library's own DB->graph path
(PyArchInitImporter + pyarchinit_us_mapping), named after the site,
and read back before being handed over: a file that does not read
back clean is not given to the user.

Pure Python: no Qt. The menu wiring lives in pyarchinitPlugin.
"""
from __future__ import annotations

import os
import re


class EmExportError(RuntimeError):
    """A reason the export could not be done, worded for the user."""


def emjson_available():
    """True when the installed s3dgraphy knows em.json (>= 1.6.0.dev40)."""
    try:
        from s3dgraphy.exporter import emjson_exporter  # noqa: F401
        return True
    except Exception:
        return False


def site_filename(site):
    """A filename the site name can travel in: word characters of any
    script, dash and dot survive; runs of anything else become one '_'."""
    name = re.sub(r"[^\w\-.]+", "_", str(site), flags=re.UNICODE).strip("_.")
    return (name or "sito") + ".em.json"


def export_site(connection_url, site, out_dir):
    """Build the site's graph, write <out_dir>/<site>.em.json, read it
    back. Returns (path, n_nodes, n_edges, warnings)."""
    if not emjson_available():
        raise EmExportError(
            "La libreria s3dgraphy installata non conosce em.json: "
            "aggiorna le dipendenze del plugin.")
    from s3dgraphy.importer.pyarchinit_importer import PyArchInitImporter
    from s3dgraphy.exporter.emjson_exporter import export_emjson
    from s3dgraphy.importer.emjson_importer import import_emjson

    graph = PyArchInitImporter(
        connection_url=connection_url,
        mapping_name="pyarchinit_us_mapping",
        filters={"sito": site},
    ).parse()
    if not getattr(graph, "nodes", None):
        raise EmExportError(
            "Il sito %r non ha righe in us_table: niente da esportare." % site)
    graph.graph_id = str(site)

    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, site_filename(site))
    export_emjson(graph, path)

    check, warnings = import_emjson(path)
    if (len(check.nodes), len(check.edges)) != (len(graph.nodes), len(graph.edges)):
        raise EmExportError(
            "Il file scritto non rilegge uguale (%d/%d nodi, %d/%d archi)."
            % (len(check.nodes), len(graph.nodes),
               len(check.edges), len(graph.edges)))
    return path, len(graph.nodes), len(graph.edges), list(warnings)
```

- [ ] **Step 4: Run — all PASS.**
- [ ] **Step 5: Commit** — `feat(one-bridge): B1 — export di un sito in em.json con rilettura di verifica`

### Task 8: B1 — EMStudio opener + menu wiring

**Files:**
- Modify: `modules/s3dgraphy/em_export.py` (adds `open_in_emstudio`)
- Modify: `pyarchinitPlugin.py` (menu action next to `actionVocabAlign`, same `addPluginToMenu` pattern)
- Test: `tests/sync/test_em_export.py` (extend)

**Interfaces:**
- Consumes: `em_export.export_site` (Task 7); `Connection().conn_str()` (`modules/db/pyarchinit_conn_strings.py`); `Pyarchinit_db_management.query_bool({}, 'SITE')`.
- Produces: `em_export.open_in_emstudio(path, runner=subprocess.run) -> bool`; menu «Extended Matrix → Esporta sito in em.json…».

- [ ] **Step 1: Write the failing tests** (append to `tests/sync/test_em_export.py`)

```python
def test_the_opener_reports_failure_instead_of_raising(tmp_path):
    # Review Focus 4: EMStudio not installed
    target = tmp_path / "x.em.json"
    target.write_text("{}", encoding="utf-8")

    class _Run:                                     # finto subprocess.run
        def __init__(self, code): self.code = code
        def __call__(self, *a, **k):
            class R: returncode = self.code
            return R()

    from modules.s3dgraphy import em_export
    assert em_export.open_in_emstudio(str(target), runner=_Run(0)) is True
    assert em_export.open_in_emstudio(str(target), runner=_Run(1)) is False

    def esplode(*a, **k): raise OSError("no app")
    assert em_export.open_in_emstudio(str(target), runner=esplode) is False
```

- [ ] **Step 2: Run — FAIL** (`open_in_emstudio` not defined).

- [ ] **Step 3: Implement in `em_export.py`**

```python
def open_in_emstudio(path, runner=None):
    """Hand the file to EMStudio; True when something opened, False —
    never an exception — when nothing is installed (the caller then
    points at the EMStudio releases page)."""
    import platform
    import subprocess
    run = runner or subprocess.run
    system = platform.system()
    try:
        if system == "Darwin":
            return run(["open", "-a", "EMStudio", path],
                       capture_output=True).returncode == 0
        if system == "Windows":
            os.startfile(path)      # l'associazione .em.json decide
            return True
        return run(["xdg-open", path], capture_output=True).returncode == 0
    except Exception:
        return False
```

- [ ] **Step 4: Wire the menu in `pyarchinitPlugin.py`** — inside the same guarded block that registers `actionVocabAlign` (grep `actionVocabAlign` for the spot), add:

```python
self.actionEmExport = QAction(
    "Extended Matrix → Esporta sito in em.json…",
    self.iface.mainWindow())
self.actionEmExport.triggered.connect(self._run_em_export)
self.iface.addPluginToMenu(
    "&pyArchInit - Archaeological GIS Tools", self.actionEmExport)
```

and the handler (same class):

```python
def _run_em_export(self):
    """B1 (spec 2026-10-07 §5): one site -> em.json -> EMStudio."""
    from qgis.PyQt.QtWidgets import QInputDialog, QMessageBox
    from modules.db.pyarchinit_conn_strings import Connection
    from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
    from modules.s3dgraphy import em_export

    try:
        conn_str = Connection().conn_str()
        db = Pyarchinit_db_management(conn_str)
        db.connection()
        sites = sorted({str(r.sito) for r in db.query_bool({}, 'SITE')})
    except Exception as e:
        QMessageBox.warning(self.iface.mainWindow(), "em.json",
                            "Connessione al database fallita:\n%s" % e)
        return
    if not sites:
        QMessageBox.information(self.iface.mainWindow(), "em.json",
                                "Nessun sito nel database.")
        return
    site, ok = QInputDialog.getItem(self.iface.mainWindow(),
                                    "Esporta in em.json", "Sito:", sites, 0, False)
    if not ok:
        return
    out_dir = os.path.join(os.environ.get("PYARCHINIT_HOME", os.path.expanduser("~")),
                           "pyarchinit_EM_folder")
    try:
        path, nodes, edges, warnings = em_export.export_site(conn_str, site, out_dir)
    except em_export.EmExportError as e:
        QMessageBox.warning(self.iface.mainWindow(), "em.json", str(e))
        return
    msg = ("Esportato %s\n%d nodi, %d archi, %d avvisi.\n\nAprire in EMStudio?"
           % (path, nodes, edges, len(warnings)))
    if QMessageBox.question(self.iface.mainWindow(), "em.json", msg,
                            QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
        if not em_export.open_in_emstudio(path):
            QMessageBox.information(
                self.iface.mainWindow(), "EMStudio",
                "EMStudio non risulta installato. Il file è in:\n%s\n\n"
                "Scaricalo da: https://github.com/ExtendedMatrix/EMStudio/releases" % path)
```

Note for the executor: check the actual HOME import used by neighbouring code in `pyarchinitPlugin.py` (`grep -n "PYARCHINIT_HOME\|pyarchinit_home" pyarchinitPlugin.py`) and follow that pattern; the `os.environ` fallback above is the lowest common denominator.

- [ ] **Step 5: Run the whole `tests/sync/test_em_export.py` → PASS; `python3 -m py_compile pyarchinitPlugin.py` → clean.**
- [ ] **Step 6: Add a wiring guard to the test file:**

```python
def test_the_menu_offers_the_export_and_handles_a_missing_emstudio():
    src = (_ROOT / "pyarchinitPlugin.py").read_text(encoding="utf-8")
    assert "Esporta sito in em.json" in src
    assert "open_in_emstudio" in src and "EMStudio/releases" in src
```

- [ ] **Step 7: Commit** — `feat(one-bridge): B1 — menu «Esporta sito in em.json» + apertura in EMStudio`

### Task 9: B1 release

- [ ] **Step 1: Canonical suite + `tests/migrations` + `tests/utility` sweep → ≤ baseline.**
- [ ] **Step 2: Hand-verify once**: export Al-Khutm (or the sample site) from the menu in QGIS, open in EMStudio desktop (Enzo does the visual check — per the spec, *if EMStudio reads it, the file is sound*).
- [ ] **Step 3: Tutorial**: add a short section to `docs/tutorials/{it,en,pt,ro}/01_configurazione.md`'s Extended-Matrix/export area describing the menu action (follow the exact style of the «Migrare tutto il database» section added 2026-09-24).
- [ ] **Step 4: Release** per Global Constraints — topic `em-export`, title «Extended Matrix: esporta il sito in em.json e aprilo in EMStudio».

### Task 10: A4 — retire the GraphML export (only after Task 9 shipped)

**Files:**
- Delete: `modules/s3dgraphy/sync/graphml_writer.py`; the four xfail-marked test files of Task 6
- Modify: whatever wires the GraphML export into the UI — discover with `grep -rn "graphml_writer\|GraphMLWriter" tabs/ modules/ gui/ pyarchinitPlugin.py --include="*.py"` and remove those menu actions/buttons (the one-time yEd **import** path and the DOT matrix stay: anything reached from the import dialogs or `s3dgraphy_dot_bridge` is NOT touched)
- Modify: `dev_logs/CHANGELOG.md` (the retirement rationale, IT+EN)

- [ ] **Step 1: Discovery grep (above); list every caller with its UI entry point in the commit message.**
- [ ] **Step 2: Remove the UI entries and the writer; delete the four test files.**
- [ ] **Step 3: Source guard in `tests/sync/test_one_bridge_shim.py`:**

```python
def test_the_graphml_writer_is_gone():
    assert not (_ROOT / "modules" / "s3dgraphy" / "sync" / "graphml_writer.py").exists()
    for probe in ("tabs", "modules", "gui"):
        for path in (_ROOT / probe).rglob("*.py"):
            assert "graphml_writer" not in path.read_text(encoding="utf-8", errors="ignore"), path
```

- [ ] **Step 4: Canonical suite → ≤ baseline, zero xfail remaining. Release** — topic `graphml-retire`, changelog explains: the viewer is EMStudio (B1), yEd import and DOT stay.

### Task 11: A5 — rewire callers, drop the shim, final sweep

**Files:**
- Modify: every plugin file importing `modules.s3dgraphy.sync.<migrated module>` (list: `grep -rln "modules.s3dgraphy.sync" tabs/ modules/ gui/ pyarchinitPlugin.py scripts/ --include="*.py"`)
- Modify: `modules/s3dgraphy/sync/__init__.py` (alias block removed; docstring states the package now holds only `vocab_provider`, `continuity_generator`, `paradata_edge_resolver`)
- Test: `tests/sync/test_one_bridge_shim.py` (extend)

- [ ] **Step 1: Write the failing guard:**

```python
MIGRATED = FREE_WINS + ("yed_rapporti_policy", "yed_classifier",
                        "yed_import_pipeline", "paradata_store",
                        "edge_registry", "group_projector",
                        "yed_table_parser", "pyarchinit_pg_importer",
                        "_workspace", "rapporti",
                        "graph_projector", "graph_ingestor")


def test_no_plugin_file_imports_the_vendored_path_for_migrated_modules():
    offenders = []
    for probe in ("tabs", "modules", "gui"):
        for path in (_ROOT / probe).rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for name in MIGRATED:
                if "modules.s3dgraphy.sync.%s" % name in text or \
                   "from modules.s3dgraphy.sync import %s" % name in text:
                    offenders.append("%s -> %s" % (path.relative_to(_ROOT), name))
    assert not offenders, offenders


def test_the_transitional_alias_is_gone():
    init = (_ROOT / "modules" / "s3dgraphy" / "sync" / "__init__.py").read_text(encoding="utf-8")
    assert "_sys.modules" not in init
```

- [ ] **Step 2: Rewire the callers** (`modules.s3dgraphy.sync.X` → `s3dgraphy.sync.X`; `rapporti` → `s3dgraphy.rapporti`), remove the alias block, run the guard → PASS.
- [ ] **Step 3: Canonical suite + full sweep (`tests/`) → ≤ baseline. Delete Task 0's worktree. Release** — topic `one-bridge-closing`, and update the spec's Status line to "Shipped (A+B1)".

### Task 12: Memory and follow-ups

- [ ] **Step 1:** Update the project memory (`project_s3dgraphy_dev40_direction.md`): A+B1 shipped, tags, what moved upstream (PR numbers), the B2/C prerequisites unchanged.
- [ ] **Step 2:** Comment on ExtendedMatrix/s3Dgraphy#25: the plugin is on the one bridge, pin version, em.json export live, list of upstreamed hunks; ask for the node/server details that unblock B2/C.
