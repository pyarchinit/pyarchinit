# yE-E Dialog UX — Execution Plan

**Spec**: `docs/superpowers/specs/2026-05-13-yed-import-dialog-design.md`
**Baseline**: `s3dgraphy-bump-5.8.1-alpha` (commit `7f5f82a8`, pushed)
**Target tag**: `yed-import-dialog-5.8.2-alpha`
**Estimated**: ~5h end-to-end (4 commit groups, io-driven)
**Execution model**: io-driven completo (user choice 2026-05-13)

---

## Pre-flight (Group 0)

1. `git status` clean on `Stratigraph_00001`.
2. Baseline `pytest tests/sync/ tests/migrations/ -q` → must show **338 passed / 42 skipped** (post s3dgraphy-bump).
3. Rollback safety tag: `git tag pre-yed-e`.
4. Verify QGIS PyQt shim: `python -c "from qgis.PyQt.QtWidgets import QWizard"` works (best-effort — Qt may be absent in dev venv, in which case manual QGIS smoke is the only validation).
5. Identify pyarchinit's i18n manifest (find `.pro` file or similar): `find . -name "*.pro" -o -name "pyarchinit.pro" 2>/dev/null`.

---

## Group A — `YedOverrides` dataclass + pipeline plumbing

**Files modified**:
- `modules/s3dgraphy/sync/yed_import_pipeline.py`

**Files created**:
- (none)

**Commit message**: `feat(yE-E): YedOverrides dataclass + apply_overrides_to_drafts helper`

### Steps

1. Append `YedOverrides` dataclass after the existing `_DryRunRollback` sentinel definition (spec § 5).
2. Implement `apply_overrides_to_drafts(drafts, overrides) -> dict` per spec § 5. Pure function. Three branches: classifier (set `user_kind`), periods (set `user_periodo / user_fase / user_datazione_*`), folders (set `user_dimension / user_value`).
3. Extend `import_yed_raw()` signature: add `overrides: YedOverrides | None = None` parameter. At the start of the function: if `overrides is not None`, call `drafts = apply_overrides_to_drafts(drafts, overrides)` BEFORE the existing `policy = overrides.policy or policy` line.
4. Update existing imports + `__all__` if present.

### Tests added

Extend `tests/sync/test_yed_import_pipeline.py` with 6 L0:
- `test_apply_overrides_empty_is_identity`
- `test_apply_overrides_classifier_per_row`
- `test_apply_overrides_periods_full`
- `test_apply_overrides_folders_dimension_change`
- `test_apply_overrides_folders_skip`
- `test_apply_overrides_policy`

### Acceptance

- Suite: 338 → 344 passed (+6).
- AC-1: existing yE-D tests pass unchanged (overrides=None codepath).

---

## Group B — `gui/yed_import_dialog.py` + UI XML

**Files created**:
- `gui/yed_import_dialog.py` (~600 LOC)
- `gui/ui/Yed_import_dialog.ui` (~700 LOC, Qt Designer XML)

**Files modified**:
- (none yet)

**Commit message**: `feat(yE-E): YedImportDialog QWizard with 5 pages + sidecar JSON`

### Steps

1. Write `gui/yed_import_dialog.py`:
   - `YedImportDialog(QWizard)` class with `__init__(drafts, graphml_path, handle, sito, parent=None)`.
   - 5 page classes (`ClassifierPage`, `PeriodsPage`, `FoldersPage`, `RapportiPolicyPage`, `PreviewPage`) as `QWizardPage` subclasses. Per spec § 6.
   - `_load_sidecar(graphml_path) -> YedOverrides` — reads `<graphml>.yed_overrides.json` if present, else returns empty `YedOverrides()`. Catches JSONDecodeError + logs warning.
   - `_save_sidecar(graphml_path, overrides) -> None` — writes JSON with version=1 + saved_at ISO timestamp.
   - `_auto_button_handler(page)` — per spec § 6 "Auto button" semantics.
   - `get_overrides() -> YedOverrides` — collect from all pages.
   - `get_policy() -> FolderEdgePolicy` — read from RapportiPolicyPage.
   - All strings wrapped in `self.tr(...)`.
   - PreviewPage.initializePage(): runs `import_yed_raw(..., dry_run=True, overrides=self.wizard().get_overrides())` and displays counts.

2. Write `gui/ui/Yed_import_dialog.ui`:
   - QWizard root.
   - 5 WizardPage children, each with the widgets per spec § 6.
   - Classifier page: QTableWidget with 4 columns + QToolBar for bulk apply.
   - Periods page: QTableWidget with 6 columns (editable).
   - Folders page: QTableWidget with 4 columns; col 3 = QComboBox delegate.
   - Rapporti page: QButtonGroup with 4 QRadioButtons + per-option QLabel help text.
   - Preview page: QTextBrowser for the read-only output.
   - Auto button: top-right of each page via QWizard.setButton(CustomButton1, ...).

3. Use `qgis.PyQt` import shim:
   ```python
   from qgis.PyQt.QtWidgets import (
       QWizard, QWizardPage, QTableWidget, QTableWidgetItem,
       QComboBox, QRadioButton, QButtonGroup, QPushButton,
       QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser, QCheckBox,
   )
   from qgis.PyQt.QtCore import Qt, QSettings
   from qgis.PyQt import uic
   ```

### Tests added

Extend `tests/sync/test_yed_import_pipeline.py` with 3 sidecar tests:
- `test_sidecar_json_round_trip`
- `test_sidecar_json_load_missing_returns_empty`
- `test_sidecar_json_load_corrupt_returns_empty_plus_warning`

Plus prepare `tests/gui/test_yed_import_dialog.py` skeleton (skipif Qt absent):
- (Qt smoke not auto-tested — manual gate covers it.)

### Acceptance

- `python -c "import ast; ast.parse(open('gui/yed_import_dialog.py').read())"` → no syntax errors.
- `python -c "import xml.etree.ElementTree as ET; ET.parse('gui/ui/Yed_import_dialog.ui')"` → XML well-formed.
- Suite: 344 → 347 passed (+3 sidecar tests).

---

## Group C — Branch hook wire + L1 integration + i18n

**Files modified**:
- `modules/s3dgraphy/sync/graph_ingestor.py:166-216` — extend yEd-raw branch to invoke dialog when QApplication present, fall through otherwise.

**Files created**:
- `i18n/pyarchinit_yed_dialog_it.ts` — Italian translations.

**Commit message**: `feat(yE-E): wire dialog in branch hook + L1 e2e + i18n IT`

### Steps

1. Update branch hook per spec § 8. Add try/except ImportError around the `from qgis.PyQt.QtWidgets import QApplication` to keep CLI/headless callers safe. Defensive: catch Exception during dialog `exec()` and fall back to defaults with a log warning (don't crash QGIS on a UI glitch).

2. Generate IT translation file:
   - Run `pyside6-lupdate gui/yed_import_dialog.py gui/ui/Yed_import_dialog.ui -ts i18n/pyarchinit_yed_dialog_it.ts`.
   - Manually fill all `<translation type="unfinished">...</translation>` entries with Italian strings.

3. L1 integration tests:
   - `test_apply_overrides_e2e_classifier_changes_us_count`: load em_demo_02_mini drafts, apply overrides that promote 1 USV_VIRTUAL to US_REAL, run `import_yed_raw(overrides=ov)` end-to-end, assert us_table has +1 row + paradata has -1.
   - `test_apply_overrides_e2e_folder_skip`: override 1 folder dimension to 'skip', run, assert its members do NOT have attivita set.

4. Verify dialog file imports cleanly from inside graph_ingestor by running `python -c "import sys; sys.path.insert(0, '.'); from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor"` — must succeed without QGIS.

### Tests added

- 2 L1 in `tests/sync/test_yed_import_pipeline.py` (or new file `test_yed_overrides_e2e.py`).

### Acceptance

- Suite: 347 → 349 passed (+2 L1).
- AC-1, AC-2, AC-3 from spec met.
- Branch hook tested via `test_cli_dry_run_subprocess_on_mini_fixture` (existing CLI test): subprocess has no QApplication → dialog NOT opened → defaults used → behavior unchanged.

---

## Group D — CLI `--overrides`, docs, version bump, tag, push

**Files modified**:
- `scripts/import_yed_graphml.py` — add `--overrides PATH` argument that loads YedOverrides from JSON.
- `metadata.txt` — 5.8.1-alpha → 5.8.2-alpha.
- `dev_logs/CHANGELOG.md` — bilingual `[5.8.2-alpha]` entry.
- Memory files.

**Commit messages** (2 commits):
- `feat(yE-E): cli --overrides flag + 1 cli test`
- `release(yE-E): docs + version 5.8.2-alpha`

### Steps

1. CLI `--overrides PATH` (~30 LOC): argparse adds optional flag. If present, `json.loads(Path(args.overrides).read_text())` → instantiate `YedOverrides` → pass to `import_yed_raw(overrides=...)`.
2. 1 CLI test: `test_cli_overrides_flag_round_trip` — write a sidecar JSON, run subprocess with `--overrides`, assert the DB reflects the overrides (e.g. classifier-routed leaves end up in the expected table).
3. Version bump in `metadata.txt`.
4. CHANGELOG bilingual entry.
5. Memory updates: `project_yed_import_progress.md` → yE-E row PENDING → SHIPPED; `MEMORY.md` index line refreshed.
6. Tag annotated: `git tag -a yed-import-dialog-5.8.2-alpha -m "..."`.
7. **USER GATE**: manual QGIS smoke test per spec § 9 step 12.
8. On `approvato`: `git push origin Stratigraph_00001 yed-import-dialog-5.8.2-alpha`.

### Acceptance

- Suite: 349 → 350 passed (+1 CLI).
- All 6 ACs from spec met.
- Branch + tag pushed.

---

## Test count progression

| Stage | Tests passed | Notes |
|---|---|---|
| Baseline | 338 | post s3dgraphy-bump |
| After A | 344 | +6 L0 apply_overrides |
| After B | 347 | +3 L0 sidecar JSON |
| After C | 349 | +2 L1 e2e |
| After D | 350 | +1 CLI |

---

## Versioning timeline (no downstream shift)

```
5.8.0-alpha   yE-D Pipeline       (shipped, pushed)
5.8.1-alpha   s3dgraphy-bump      (shipped, pushed)
5.8.2-alpha   yE-E Dialog         (THIS milestone)
5.8.3-alpha   yE-Closure          (next: docs + tutorials + closure)
```

---

## Open plan-time decisions resolved upfront

| Decision | Value | Reason |
|---|---|---|
| **YedOverrides JSON shape** | flat dict with versioning | Forward-compat. version=1 in the file. |
| **Auto button handler** | clears overrides for the page + advances | Matches the user's "Auto = accept defaults" mental model. |
| **PreviewPage dry_run** | yes, full pipeline | Gives the user real counts before commit. Cancelled wizard ≡ rollback (transaction never starts). |
| **Sidecar location** | next to graphml, suffix `.yed_overrides.json` | Self-contained per graphml; user moves the graphml, overrides follow. |
| **CLI `--auto-defaults`** | kept as no-op, forward-compat | Already shipped in yE-D Group D. Headless callers get defaults naturally. |
| **i18n compile** | `.qm` generation deferred to install/release scripts | `pyside6-lrelease` is at `/Library/Frameworks/Python.framework/Versions/3.13/bin/pyside6-lrelease` per memory. |

---

## Rollback

- `pre-yed-e` tag at Group 0.
- Each Group's commit revertable independently.
- If the branch-hook change causes QGIS crashes on import, `git revert <Group-C-hook-commit>` brings back yE-D behavior; the dialog files stay in tree but inert.
- Sidecar JSON files left on user's disk are harmless — they're just data; the next yE-D-only import ignores them.
