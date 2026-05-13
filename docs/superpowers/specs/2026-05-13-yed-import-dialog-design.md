# yE-E Dialog UX — Design Spec

**Date:** 2026-05-13
**Branch:** Stratigraph_00001
**Predecessor tag:** `s3dgraphy-bump-5.8.1-alpha` (commit `7f5f82a8`, pushed)
**Target tag:** `yed-import-dialog-5.8.2-alpha` (shifted 3× from original 5.7.9 — PG-UIFix → PG-Bv2 → s3dgraphy-bump)

---

## 1. Goal

Fifth of the 6-milestone yEd-aware-graphml-import rollout. yE-D ships hardcoded defaults: classifier auto-classification, period auto-detection, folder auto_dimension, rapporti `SKIP`. yE-E gives the user a **Qt wizard** to review and override those defaults BEFORE the SQL transaction commits.

When yE-E ships, importing a yEd-raw graphml via the QGIS menu opens a 5-page wizard. The user walks through classifier / periods / folders / rapporti policy / preview, then clicks Commit (or Cancel). The wizard produces a `YedOverrides` dataclass that `import_yed_raw()` consumes to skin its defaults.

## 2. Decisions captured during brainstorming (2026-05-13)

| Q | Decision | Notes |
|---|---|---|
| A modality | **γ — Wizard multi-step + preview at end** | QWizard with 5 pages (4 sections + preview). Pages = QWizardPage subclasses. |
| B classifier override | **γ — Per-row combobox + bulk select+set-all** | Checkbox column + "Apply to selected" toolbar action. |
| B period editing | **β — Full edit** (label, periodo, fase, datazione_iniziale, datazione_finale) | All 5 fields editable per row. |
| B folder editing | **α — Full edit** (dimension combobox + value free-text) | One row per folder; dimension combobox lists 7 valid values from `_ALLOWED_FOLDER_DIMENSIONS` + "skip". |
| C persistence | **β — Sidecar JSON** `<graphml>.yed_overrides.json` | Load if exists, populate wizard. Save on Commit. |
| C discoverability | **β — Auto button** top-right corner of every page | Accept all defaults for this page + advance to next. Final-page Auto = accept all, advance to Preview. |
| C i18n | **β — IT + EN via `self.tr()`** | All visible strings in `self.tr()`. Ship IT .ts file; EN regen later. |
| D execution | **Io-driven completo** | No subagent. Full control over UX details + Qt edge cases. |

## 3. Inherited from predecessors

- yE-A: `yed_detector.py` — unchanged.
- yE-B: `yed_classifier.py` + `ClassifiedNode` — wizard's classifier page consumes it.
- yE-C: `yed_table_parser.py` + `PeriodCandidate` + `yed_group_walker.py` + `FolderCandidate` — wizard's periods + folders pages consume them.
- yE-D: `import_yed_raw(handle, graphml_path, sito, drafts, *, policy, dry_run) → IngestResult`. yE-E **extends signature** with `overrides: YedOverrides | None = None`. Hardcoded-defaults path (overrides=None) stays unchanged.
- s3dgraphy-bump (yE-D 5.8.1-alpha): `REUSED_SPECIAL_FIND` ClassificationKind value available to the classifier combobox.

## 4. Architecture

### Files created (4)

| Path | Responsibility | LOC est |
|---|---|---|
| `gui/ui/Yed_import_dialog.ui` | Qt Designer XML — QWizard + 5 QWizardPage widgets (classifier, periods, folders, rapporti, preview) | ~700 |
| `gui/yed_import_dialog.py` | Controller: page logic, model-view glue, sidecar JSON load/save, Auto button handlers, apply_overrides_to_drafts() helper | ~600 |
| `tests/sync/test_yed_import_dialog.py` | L0 state-machine tests (apply_overrides_to_drafts contract + sidecar JSON round-trip + Auto-button defaults) | ~300 |
| `i18n/pyarchinit_yed_dialog_it.ts` | IT translation source (compiled to .qm at install) | ~150 |

### Files modified (4)

| Path | Change | LOC delta |
|---|---|---|
| `modules/s3dgraphy/sync/yed_import_pipeline.py` | NEW `YedOverrides` dataclass + new `apply_overrides_to_drafts()` helper + extend `import_yed_raw()` signature with `overrides=None` parameter | ~120 |
| `modules/s3dgraphy/sync/graph_ingestor.py:166-216` | Wire branch hook: import dialog, open if running interactively, pass overrides to import_yed_raw; CLI/headless callers (no overrides) unaffected | ~25 |
| `metadata.txt` | 5.8.1-alpha → 5.8.2-alpha | 1 |
| `dev_logs/CHANGELOG.md` | Prepend bilingual `[5.8.2-alpha]` section | ~80 |

### Files NOT touched

- `yed_classifier.py`, `yed_table_parser.py`, `yed_group_walker.py`, `yed_rapporti_policy.py` — inherited as-is.
- Pyarchinit-projected branch of `populate_list()` — AC-2 sacred.
- `scripts/import_yed_graphml.py` CLI — already has `--auto-defaults` flag from yE-D Group D; the CLI passes `overrides=None`, which is the yE-D default (no UI).
- DB schema — no migrations.

### Total LOC

- Production: ~745 (~600 dialog controller + ~120 pipeline + ~25 hook)
- UI XML: ~700
- i18n: ~150
- Test: ~300
- Docs: ~110
- **Grand total: ~2005 LOC** — biggest milestone in the rollout

## 5. `YedOverrides` dataclass

```python
@dataclass
class YedOverrides:
    """User overrides applied AFTER yE-A/B/C parsers + BEFORE yE-D pipeline.

    All fields default to None / empty containers — yE-E wizard populates
    only the fields the user actually touched. apply_overrides_to_drafts()
    merges them onto the auto-* fields of drafts.

    Sidecar JSON shape mirrors this dataclass (camelCase → snake_case).
    """
    classifier: dict[str, ClassificationKind] = field(default_factory=dict)
    """yed_id -> ClassificationKind. Empty dict = keep auto_kind for every leaf."""

    periods: dict[str, dict] = field(default_factory=dict)
    """yed_row_id -> {'periodo': str, 'fase': str, 'datazione_iniziale': int | None,
    'datazione_finale': int | None, 'datazione_estesa': str | None}. Empty = keep auto_*."""

    folders: dict[str, dict] = field(default_factory=dict)
    """folder yed_id -> {'dimension': str | None, 'value': str}. dimension=None or
    'skip' means: don't apply this folder. Empty = keep auto_dimension + auto_value."""

    policy: FolderEdgePolicy | None = None
    """None = use the default passed to import_yed_raw (SKIP)."""


def apply_overrides_to_drafts(drafts: dict, overrides: YedOverrides) -> dict:
    """Return a NEW drafts dict with overrides applied:
    - Each ClassifiedNode in drafts['classified']: user_kind = overrides.classifier.get(yed_id, auto_kind).
    - Each PeriodCandidate in drafts['periods']: user_periodo / user_fase / user_datazione_* set from overrides.periods.
    - Each FolderCandidate in drafts['folders']: user_dimension / user_value set from overrides.folders.
    Pure function. Original `drafts` not mutated."""
```

## 6. `YedImportDialog` (QWizard)

### Class hierarchy

```python
class YedImportDialog(QWizard):
    """5-page wizard for yE-E user overrides."""
    def __init__(self, drafts: dict, graphml_path: Path, parent=None):
        ...
        self.addPage(ClassifierPage(drafts))
        self.addPage(PeriodsPage(drafts))
        self.addPage(FoldersPage(drafts))
        self.addPage(RapportiPolicyPage())
        self.addPage(PreviewPage(handle, graphml_path, sito))

    def get_overrides(self) -> YedOverrides:
        """Collect overrides from each page after Finish."""

    def get_policy(self) -> FolderEdgePolicy:
        """Read from RapportiPolicyPage."""


class ClassifierPage(QWizardPage):
    """Table widget: 1 row per leaf. Columns: checkbox | label |
    auto_kind (display) | user_kind (combobox). Toolbar above:
    [Select All] [Deselect All] [Apply Kind to Selected → dropdown].
    Auto button top-right: 'Accetta auto-kind per tutte le righe'."""


class PeriodsPage(QWizardPage):
    """Table widget: 1 row per PeriodCandidate. Columns: label |
    periodo (edit) | fase (edit) | datazione_iniziale (edit) |
    datazione_finale (edit) | datazione_estesa (edit). Auto button."""


class FoldersPage(QWizardPage):
    """Table widget: 1 row per FolderCandidate. Columns: full_label |
    auto_dimension (display) | user_dimension (combobox: attivita /
    area / struttura / settore / ambient / saggio / quad_par / skip) |
    user_value (edit). Auto button."""


class RapportiPolicyPage(QWizardPage):
    """Single radio-button group: SKIP / FAN_OUT / REPRESENTATIVE /
    SYNTHETIC. Default SKIP. Help labels next to each option."""


class PreviewPage(QWizardPage):
    """Read-only text pane: runs import_yed_raw(..., dry_run=True,
    overrides=collected_overrides) and shows the resulting
    IngestResult counts (us_inserted / inv_inserted / period_inserted /
    us_updated_dim / rapporti_updated / paradata_written). Finish
    button commits; Cancel rolls back (nothing was committed during
    preview since dry_run=True)."""
```

### Sidecar JSON persistence

On `__init__`:
- Compute `<graphml_path>.yed_overrides.json`.
- If file exists: load → instantiate `YedOverrides` → pre-populate each page's widgets.
- On Cancel: do nothing.
- On Finish: serialize `YedOverrides` (after apply_overrides) → write to sidecar.

JSON shape:
```json
{
  "version": 1,
  "graphml_path": "/path/to/file.graphml",
  "saved_at": "2026-05-13T14:30:00Z",
  "classifier": {"n0::n0::n0": "us_real", "n0::n0::n2": "us_real"},
  "periods": {"n0::p0": {"periodo": "Roman", "fase": "Late", ...}},
  "folders": {"n0::f0": {"dimension": "attivita", "value": "VA01"}},
  "policy": "fan_out"
}
```

### Auto button

Top-right corner of each page (custom button via `QWizard.setButton(QWizard.CustomButton1, ...)`). Click handler:
- ClassifierPage: set every row's user_kind = auto_kind (no override).
- PeriodsPage: clear all user_* fields (keep auto_*).
- FoldersPage: keep auto_dimension + auto_value for every folder.
- RapportiPolicyPage: select SKIP (the yE-D default).
- After Auto: advance to next page automatically.

Final-page Auto = collect all + advance to preview. Preview-page has no Auto.

## 7. i18n

All visible strings wrapped in `self.tr(...)`. Example:

```python
self.setTitle(self.tr("Classifier override"))
self.setSubTitle(self.tr("Review the auto-classification "
                         "and override per-row if needed."))
btn_auto.setText(self.tr("Accetta auto"))
```

Translation file: `i18n/pyarchinit_yed_dialog_it.ts` shipped with IT translations (most strings will be `<source>...</source><translation type="unfinished"/>` for EN baseline). Compile at install time via `pyside6-lrelease` (path documented in memory: `/Library/Frameworks/Python.framework/Versions/3.13/bin/pyside6-lrelease`).

Add to `pyarchinit.pro` or equivalent translation manifest.

## 8. Branch hook integration

In `graph_ingestor.py:populate_list()` yEd-raw branch:

```python
if detect_flavor(graphml_path) == "yed-raw":
    drafts = {...}  # yE-A/B/C parsers as before
    # yE-E: open dialog if running interactively (i.e., when QApplication
    # exists). Headless callers (CLI, tests) get None → yE-D defaults.
    overrides = None
    policy = FolderEdgePolicy.SKIP
    try:
        from qgis.PyQt.QtWidgets import QApplication
        if QApplication.instance() is not None:
            from pyarchinit.gui.yed_import_dialog import YedImportDialog
            dlg = YedImportDialog(drafts, graphml_path, handle, sito)
            if dlg.exec() != dlg.Accepted:
                return IngestResult(applied=0, errors=("Cancelled by user",))
            overrides = dlg.get_overrides()
            policy = dlg.get_policy()
    except ImportError:
        # No Qt available — fall through to defaults.
        pass
    return import_yed_raw(handle, graphml_path, sito, drafts,
                          policy=policy, overrides=overrides, dry_run=dry_run)
```

Defensive: `QApplication.instance()` check + ImportError fallback ensures the CLI, the test suite, and any headless caller never block on a dialog they can't render.

## 9. Test plan

### L0 — state machine (pure logic, no Qt)

1. `test_apply_overrides_empty_is_identity` — `apply_overrides_to_drafts(drafts, YedOverrides())` returns drafts with user_* = auto_*.
2. `test_apply_overrides_classifier_per_row` — overrides.classifier{yed_id: ClassificationKind.US_REAL} sets user_kind = US_REAL for that leaf, others unchanged.
3. `test_apply_overrides_periods_full` — overrides.periods{yed_row_id: {periodo, fase, datazione_iniziale, datazione_finale, datazione_estesa}} populates all 5 user_* fields.
4. `test_apply_overrides_folders_dimension_change` — override dimension from 'attivita' to 'struttura' + value 'X' → user_dimension/user_value updated.
5. `test_apply_overrides_folders_skip` — dimension='skip' → folder excluded from `_apply_yed_folder_dimensions` downstream.
6. `test_apply_overrides_policy` — overrides.policy=FAN_OUT → `import_yed_raw` uses FAN_OUT regardless of caller-passed policy.
7. `test_sidecar_json_round_trip` — YedOverrides → JSON → YedOverrides equal.
8. `test_sidecar_json_load_missing_returns_empty` — graceful when file doesn't exist.
9. `test_sidecar_json_load_corrupt_returns_empty_plus_warning` — log warning, return empty.

### L1 — apply on em_demo_02_mini fixture

10. `test_apply_overrides_e2e_classifier_changes_us_count` — start with default, override a USV_VIRTUAL → US_REAL → us_table count increments by 1, paradata decrements by 1.
11. `test_apply_overrides_e2e_folder_skip` — override a folder to 'skip' → its members don't get attivita set.

### Manual QGIS smoke

12. Run import via menu on EM_demo_02.graphml → wizard opens → walk through 5 pages → click Auto on classifier → advance → edit periodo on row 0 → click Auto on folders → choose FAN_OUT on policy → review preview → click Finish → verify DB has the expected rows.

Total: 11 automated tests + 1 manual gate.

## 10. CLI implications

`scripts/import_yed_graphml.py` already has `--auto-defaults` (yE-D Group D). yE-E:
- When CLI runs without `--auto-defaults`, the dialog is NOT opened (CLI has no QApplication). `import_yed_raw(overrides=None)` → yE-D defaults. Same as today.
- `--auto-defaults` becomes redundant (current behaviour is the auto-defaults behaviour). Keep the flag for forward-compat; no-op.
- New optional flag `--overrides PATH`: load YedOverrides from a JSON file at PATH and pass to `import_yed_raw(overrides=...)`. Use case: CI / scripted re-runs with consistent overrides.

LOC delta on CLI: ~30.

## 11. Versioning

- Bump `metadata.txt`: 5.8.1-alpha → 5.8.2-alpha (minor).
- yE-Closure: 5.8.3-alpha (unchanged from previous shift).
- Predecessor: `s3dgraphy-bump-5.8.1-alpha` (commit `7f5f82a8`).

## 12. AC

- **AC-1**: yE-D pipeline unchanged when `overrides=None` is passed; existing tests stay green without modification.
- **AC-2**: pyarchinit-projected branch of `populate_list()` byte-identical; AC-2 critical regression suite green.
- **AC-3**: When QApplication is present, yEd-raw import opens the wizard; when not, falls through to defaults silently.
- **AC-4**: Sidecar JSON saved on Commit and loaded on re-open of the same graphml.
- **AC-5**: Auto button on each page accepts defaults + advances.
- **AC-6**: 11 new automated tests pass. Suite ≥ 349.

## 13. Rollback

- Safety tag `pre-yed-e` posted in Group 0.
- Each commit isolatable (`git revert <sha>`).
- If wizard crashes QGIS: `git revert <branch-hook-commit>` brings back yE-D auto-defaults behavior; dialog files stay in tree but inert.

## 14. Out of scope

- Per-leaf datazione editing in folders (dates belong to periods, not folders).
- ParadataStore API extensions for VIRTUAL_FIND / DOCUMENT / COMBINER / PROPERTY (still Path B, yE-D).
- Drag-and-drop reordering of leaves/periods/folders.
- Search/filter on the classifier page (deferred — for now scroll the table).
- Undo/redo within the wizard (Cancel = discard everything; Finish = commit).
