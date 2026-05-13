"""yE-E (5.8.2-alpha) — Qt wizard for user overrides on yEd-raw import.

5-page wizard:
  1. Classifier  — per-leaf override of auto_kind (combobox per row +
                   bulk apply via row-selection).
  2. Periods     — full edit of TableNode-extracted PeriodCandidate
                   rows (periodo / fase columns).
  3. Folders     — per-folder dimension override (dimension combobox +
                   value text). 'skip' sentinel = don't apply this folder.
  4. Rapporti    — radio-button choice of FolderEdgePolicy
                   (SKIP / FAN_OUT / REPRESENTATIVE / SYNTHETIC).
  5. Preview     — read-only counts from a dry_run pass of import_yed_raw
                   so the user can verify the diff before commit.

Persistence: a sidecar JSON ``<graphml>.yed_overrides.json`` next to the
graphml. Loaded at __init__ if present; saved on Finish.

i18n: every visible string wrapped in ``self.tr()``. Translation file
ships under ``i18n/pyarchinit_yed_dialog_it.ts`` (Group C deliverable).

Headless-safe: the file imports cleanly without QGIS available
(qgis.PyQt is optional via `_QT_AVAILABLE`); the YedImportDialog class
itself only resolves at instance-construction time, when QApplication
must be present.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from modules.s3dgraphy.sync.yed_classifier import (
    ClassificationKind,
    ClassifiedNode,
)
from modules.s3dgraphy.sync.yed_group_walker import FolderCandidate
from modules.s3dgraphy.sync.yed_rapporti_policy import FolderEdgePolicy
from modules.s3dgraphy.sync.yed_import_pipeline import (
    YedOverrides,
    import_yed_raw,
)


log = logging.getLogger(__name__)

# Folder dimensions surfaced in the combobox; matches
# yed_import_pipeline._ALLOWED_FOLDER_DIMENSIONS + the 'skip' sentinel.
_FOLDER_DIMENSIONS_UI = [
    "attivita", "area", "struttura", "settore",
    "ambient", "saggio", "quad_par", "skip",
]


# ---------------------------------------------------------------------------
# Sidecar JSON persistence (pure functions, Qt-free — testable headless)
# ---------------------------------------------------------------------------

def sidecar_path(graphml_path: Path | str) -> Path:
    """Compute the sidecar JSON path for a given graphml."""
    p = Path(graphml_path)
    return p.with_suffix(p.suffix + ".yed_overrides.json")


def save_sidecar(graphml_path: Path | str, overrides: YedOverrides) -> Path:
    """Serialize YedOverrides to ``<graphml>.yed_overrides.json``.

    Schema:
      {
        "version": 1,
        "saved_at": "<iso8601 UTC>",
        "graphml_path": "<absolute path>",
        "classifier": {yed_id: kind_value, ...},
        "periods":    {yed_row_id: {periodo, fase, ...}, ...},
        "folders":    {yed_id: {dimension, value}, ...},
        "policy":     "skip" | "fan_out" | ... | None
      }
    """
    target = sidecar_path(graphml_path)
    payload = {
        "version": 1,
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "graphml_path": str(Path(graphml_path).resolve()),
        "classifier": {
            k: (v.value if hasattr(v, "value") else str(v))
            for k, v in overrides.classifier.items()
        },
        "periods": dict(overrides.periods),
        "folders": dict(overrides.folders),
        "policy": (
            overrides.policy.value
            if overrides.policy is not None and hasattr(overrides.policy, "value")
            else overrides.policy
        ),
    }
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return target


def load_sidecar(graphml_path: Path | str) -> YedOverrides:
    """Load a sidecar JSON next to *graphml_path* and return a
    YedOverrides instance. Returns an empty YedOverrides() when the
    file does not exist or is unparseable (with a log warning on
    parse errors). Unknown ClassificationKind values are skipped."""
    target = sidecar_path(graphml_path)
    if not target.exists():
        return YedOverrides()
    try:
        raw = json.loads(target.read_text())
    except (json.JSONDecodeError, OSError) as e:
        log.warning("sidecar load failed: %s; starting from empty", e)
        return YedOverrides()

    # Translate classifier values back to ClassificationKind, skipping
    # unknown enum values (forward-compat from older s3dgraphy / future).
    classifier: dict[str, ClassificationKind] = {}
    kind_by_value = {k.value: k for k in ClassificationKind}
    for yed_id, kind_value in (raw.get("classifier") or {}).items():
        kind = kind_by_value.get(kind_value)
        if kind is not None:
            classifier[yed_id] = kind

    policy_value = raw.get("policy")
    policy = None
    if policy_value is not None:
        policy_by_value = {p.value: p for p in FolderEdgePolicy}
        policy = policy_by_value.get(policy_value)

    return YedOverrides(
        classifier=classifier,
        periods=dict(raw.get("periods") or {}),
        folders=dict(raw.get("folders") or {}),
        policy=policy,
    )


# ---------------------------------------------------------------------------
# Qt wizard (resolved lazily; import fails cleanly when Qt is absent)
# ---------------------------------------------------------------------------

try:
    from qgis.PyQt.QtCore import Qt
    from qgis.PyQt.QtWidgets import (
        QButtonGroup,
        QComboBox,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QPushButton,
        QRadioButton,
        QTableWidget,
        QTableWidgetItem,
        QTextBrowser,
        QVBoxLayout,
        QWizard,
        QWizardPage,
    )
    _QT_AVAILABLE = True
except ImportError:
    _QT_AVAILABLE = False


def _kind_choices() -> list[ClassificationKind]:
    """List ClassificationKind values for the classifier combobox,
    in document-friendly order."""
    return [
        ClassificationKind.US_REAL,
        ClassificationKind.US_MASONRY,
        ClassificationKind.US_DOCUMENTARY,
        ClassificationKind.USV_VIRTUAL,
        ClassificationKind.USV_FORMAL,
        ClassificationKind.SPECIAL_FIND,
        ClassificationKind.VIRTUAL_FIND,
        ClassificationKind.REUSED_SPECIAL_FIND,
        ClassificationKind.DOCUMENT,
        ClassificationKind.COMBINER,
        ClassificationKind.PROPERTY,
        ClassificationKind.UNKNOWN,
        ClassificationKind.SKIP,
    ]


if _QT_AVAILABLE:

    class _ClassifierPage(QWizardPage):
        """Step 1: per-leaf user_kind override."""

        def __init__(self, drafts: dict, prepop: YedOverrides):
            super().__init__()
            self._classified = list(drafts.get("classified", []))
            self._prepop = prepop
            self.setTitle(self.tr("1/5 — Classifier"))
            self.setSubTitle(
                self.tr("Review the auto-classified leaves and override "
                        "the kind per row when needed. Use the Auto button "
                        "to accept all defaults.")
            )
            self._build()

        def _build(self) -> None:
            layout = QVBoxLayout(self)

            self.table = QTableWidget(len(self._classified), 3, self)
            self.table.setHorizontalHeaderLabels([
                self.tr("Label"),
                self.tr("Auto kind"),
                self.tr("User kind (override)"),
            ])
            self.table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
            self.table.verticalHeader().setVisible(False)

            choices = _kind_choices()
            choice_values = [k.value for k in choices]
            for row, c in enumerate(self._classified):
                self.table.setItem(row, 0, QTableWidgetItem(c.label))
                self.table.setItem(
                    row, 1, QTableWidgetItem(c.auto_kind.value)
                )
                combo = QComboBox()
                combo.addItems(choice_values)
                initial = self._prepop.classifier.get(c.yed_id, c.user_kind)
                idx = choice_values.index(initial.value) if initial in choices else 0
                combo.setCurrentIndex(idx)
                self.table.setCellWidget(row, 2, combo)
            layout.addWidget(self.table)

            btn_row = QHBoxLayout()
            btn_auto = QPushButton(self.tr("Accetta auto per tutte le righe"))
            btn_auto.clicked.connect(self._auto_all)
            btn_row.addStretch(1)
            btn_row.addWidget(btn_auto)
            layout.addLayout(btn_row)

        def _auto_all(self) -> None:
            """Reset every row's combobox to its auto_kind."""
            choices = _kind_choices()
            choice_values = [k.value for k in choices]
            for row, c in enumerate(self._classified):
                combo = self.table.cellWidget(row, 2)
                if combo is None:
                    continue
                idx = choice_values.index(c.auto_kind.value)
                combo.setCurrentIndex(idx)

        def collect(self) -> dict[str, ClassificationKind]:
            """Return only the rows whose user_kind != auto_kind."""
            out: dict[str, ClassificationKind] = {}
            kind_by_value = {k.value: k for k in ClassificationKind}
            for row, c in enumerate(self._classified):
                combo = self.table.cellWidget(row, 2)
                if combo is None:
                    continue
                chosen = kind_by_value.get(combo.currentText())
                if chosen is not None and chosen != c.auto_kind:
                    out[c.yed_id] = chosen
            return out


    class _PeriodsPage(QWizardPage):
        """Step 2: edit periodo + fase per PeriodCandidate row."""

        def __init__(self, drafts: dict, prepop: YedOverrides):
            super().__init__()
            self._periods = list(drafts.get("periods", []))
            self._prepop = prepop
            self.setTitle(self.tr("2/5 — Periods"))
            self.setSubTitle(self.tr(
                "Review the TableNode-extracted periods. Periodo + fase "
                "are editable; Auto restores the auto-parsed values."
            ))
            self._build()

        def _build(self) -> None:
            layout = QVBoxLayout(self)
            self.table = QTableWidget(len(self._periods), 3, self)
            self.table.setHorizontalHeaderLabels([
                self.tr("Label"),
                self.tr("Periodo"),
                self.tr("Fase"),
            ])
            self.table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
            self.table.verticalHeader().setVisible(False)
            for row, p in enumerate(self._periods):
                self.table.setItem(row, 0, QTableWidgetItem(p.user_label))
                ovr = self._prepop.periods.get(p.yed_row_id, {})
                self.table.setItem(
                    row, 1,
                    QTableWidgetItem(str(ovr.get("periodo", p.user_periodo))),
                )
                self.table.setItem(
                    row, 2,
                    QTableWidgetItem(str(ovr.get("fase", p.user_fase))),
                )
            layout.addWidget(self.table)

            btn_row = QHBoxLayout()
            btn_auto = QPushButton(self.tr("Ripristina auto"))
            btn_auto.clicked.connect(self._auto_all)
            btn_row.addStretch(1)
            btn_row.addWidget(btn_auto)
            layout.addLayout(btn_row)

        def _auto_all(self) -> None:
            for row, p in enumerate(self._periods):
                self.table.item(row, 1).setText(str(p.auto_periodo))
                self.table.item(row, 2).setText(str(p.auto_fase))

        def collect(self) -> dict[str, dict]:
            """Return only periods whose periodo/fase != auto_*."""
            out: dict[str, dict] = {}
            for row, p in enumerate(self._periods):
                try:
                    periodo = int(self.table.item(row, 1).text())
                except (ValueError, AttributeError):
                    periodo = p.auto_periodo
                try:
                    fase = int(self.table.item(row, 2).text())
                except (ValueError, AttributeError):
                    fase = p.auto_fase
                if periodo != p.auto_periodo or fase != p.auto_fase:
                    out[p.yed_row_id] = {"periodo": periodo, "fase": fase}
            return out


    class _FoldersPage(QWizardPage):
        """Step 3: per-folder dimension + value override."""

        def __init__(self, drafts: dict, prepop: YedOverrides):
            super().__init__()
            self._folders = list(drafts.get("folders", []))
            self._prepop = prepop
            self.setTitle(self.tr("3/5 — Folders"))
            self.setSubTitle(self.tr(
                "Map each folder to a us_table dimension column. "
                "Use 'skip' to exclude a folder from the UPDATE pass."
            ))
            self._build()

        def _build(self) -> None:
            layout = QVBoxLayout(self)
            self.table = QTableWidget(len(self._folders), 4, self)
            self.table.setHorizontalHeaderLabels([
                self.tr("Label"),
                self.tr("Auto dimension"),
                self.tr("User dimension"),
                self.tr("User value"),
            ])
            self.table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch
            )
            self.table.verticalHeader().setVisible(False)

            for row, f in enumerate(self._folders):
                self.table.setItem(row, 0, QTableWidgetItem(f.full_label))
                self.table.setItem(
                    row, 1,
                    QTableWidgetItem(f.auto_dimension or "—"),
                )
                ovr = self._prepop.folders.get(f.yed_id, {})

                combo = QComboBox()
                combo.addItems(_FOLDER_DIMENSIONS_UI)
                current_dim = ovr.get("dimension", f.user_dimension or "skip")
                if current_dim in _FOLDER_DIMENSIONS_UI:
                    combo.setCurrentIndex(
                        _FOLDER_DIMENSIONS_UI.index(current_dim)
                    )
                self.table.setCellWidget(row, 2, combo)

                self.table.setItem(
                    row, 3,
                    QTableWidgetItem(str(ovr.get("value", f.user_value))),
                )
            layout.addWidget(self.table)

            btn_row = QHBoxLayout()
            btn_auto = QPushButton(self.tr("Ripristina auto"))
            btn_auto.clicked.connect(self._auto_all)
            btn_row.addStretch(1)
            btn_row.addWidget(btn_auto)
            layout.addLayout(btn_row)

        def _auto_all(self) -> None:
            for row, f in enumerate(self._folders):
                combo = self.table.cellWidget(row, 2)
                target_dim = f.auto_dimension or "skip"
                if combo is not None and target_dim in _FOLDER_DIMENSIONS_UI:
                    combo.setCurrentIndex(
                        _FOLDER_DIMENSIONS_UI.index(target_dim)
                    )
                self.table.item(row, 3).setText(f.auto_value)

        def collect(self) -> dict[str, dict]:
            """Return only folders whose dimension/value != auto_*."""
            out: dict[str, dict] = {}
            for row, f in enumerate(self._folders):
                combo = self.table.cellWidget(row, 2)
                dim = combo.currentText() if combo is not None else (f.auto_dimension or "skip")
                value_item = self.table.item(row, 3)
                value = value_item.text() if value_item is not None else f.auto_value

                # Only record a diff. f.auto_dimension may be None (no
                # prefix matched); treat None as 'skip' for comparison.
                auto_dim_norm = f.auto_dimension or "skip"
                if dim != auto_dim_norm or value != f.auto_value:
                    out[f.yed_id] = {"dimension": dim, "value": value}
            return out


    class _RapportiPolicyPage(QWizardPage):
        """Step 4: pick a folder-edge policy."""

        _POLICIES = [
            (FolderEdgePolicy.SKIP, "Skip — scarta gli edge che toccano folders (default)."),
            (FolderEdgePolicy.FAN_OUT, "Fan-out — espande folder→folder a NxM pair leaf."),
            (FolderEdgePolicy.REPRESENTATIVE, "Representative — usa il primo membro come proxy."),
            (FolderEdgePolicy.SYNTHETIC, "Synthetic — crea us_table VA per folder, rewire edges."),
        ]

        def __init__(self, prepop: YedOverrides):
            super().__init__()
            self._prepop = prepop
            self.setTitle(self.tr("4/5 — Rapporti policy"))
            self.setSubTitle(self.tr(
                "Choose how folder-touching edges are turned into "
                "us_table.rapporti tuples. SKIP is the safe default."
            ))
            self._build()

        def _build(self) -> None:
            layout = QVBoxLayout(self)
            self._group = QButtonGroup(self)
            self._buttons: dict[FolderEdgePolicy, QRadioButton] = {}

            for policy, help_text in self._POLICIES:
                rb = QRadioButton(f"{policy.value} — {help_text}")
                layout.addWidget(rb)
                self._group.addButton(rb)
                self._buttons[policy] = rb

            initial = self._prepop.policy or FolderEdgePolicy.SKIP
            self._buttons[initial].setChecked(True)

            layout.addStretch(1)
            btn_row = QHBoxLayout()
            btn_auto = QPushButton(self.tr("Ripristina default (SKIP)"))
            btn_auto.clicked.connect(
                lambda: self._buttons[FolderEdgePolicy.SKIP].setChecked(True)
            )
            btn_row.addStretch(1)
            btn_row.addWidget(btn_auto)
            layout.addLayout(btn_row)

        def collect(self) -> FolderEdgePolicy | None:
            for policy, btn in self._buttons.items():
                if btn.isChecked():
                    # Only record a diff vs the default.
                    return policy if policy != FolderEdgePolicy.SKIP else None
            return None


    class _PreviewPage(QWizardPage):
        """Step 5: dry-run preview of what import_yed_raw would write."""

        def __init__(self, handle, graphml_path, sito, drafts, wizard_ref):
            super().__init__()
            self._handle = handle
            self._graphml_path = graphml_path
            self._sito = sito
            self._drafts = drafts
            self._wizard_ref = wizard_ref
            self.setTitle(self.tr("5/5 — Preview"))
            self.setSubTitle(self.tr(
                "Dry-run of the import with the chosen overrides — "
                "click Finish to commit, Cancel to abort."
            ))
            self._build()

        def _build(self) -> None:
            layout = QVBoxLayout(self)
            self.output = QTextBrowser(self)
            layout.addWidget(self.output)

        def initializePage(self) -> None:
            """Runs each time the user navigates to this page."""
            ov = self._wizard_ref.get_overrides()
            policy = self._wizard_ref.get_policy()
            self.output.setPlainText(self.tr("Running dry-run preview…"))
            try:
                result = import_yed_raw(
                    self._handle,
                    self._graphml_path,
                    self._sito,
                    self._drafts,
                    policy=policy,
                    dry_run=True,
                    overrides=ov,
                )
            except Exception as e:  # noqa: BLE001 — surface any error
                self.output.setPlainText(
                    self.tr("Preview failed: {e}").format(e=e)
                )
                return
            summary = [
                self.tr("Dry-run preview (no changes committed yet):"),
                "",
                f"  applied   : {result.applied}",
                f"  inserted  : {result.inserted}",
                f"  updated   : {result.updated}",
                f"  skipped   : {result.skipped}",
                f"  dry_run   : {result.dry_run}",
            ]
            if result.errors:
                summary.append("")
                summary.append(self.tr("Errors:"))
                for e in result.errors:
                    summary.append(f"  - {e}")
            pd = result.parsed_drafts or {}
            if pd:
                summary.append("")
                summary.append(self.tr("parsed_drafts:"))
                for k in ("classified", "periods", "folders"):
                    if k in pd:
                        summary.append(f"  {k}: {len(pd[k])}")
                for k in ("rapporti_skipped", "paradata_count"):
                    if k in pd:
                        summary.append(f"  {k}: {pd[k]}")
            self.output.setPlainText("\n".join(summary))


    class YedImportDialog(QWizard):
        """5-page wizard for yE-E user overrides. Modal blocking."""

        def __init__(
            self,
            drafts: dict,
            graphml_path: Path | str,
            handle,
            sito: str,
            parent=None,
        ):
            super().__init__(parent)
            self.setWindowTitle(self.tr("yEd-raw import — overrides"))
            self.setOption(QWizard.WizardOption.IndependentPages, False)

            prepop = load_sidecar(graphml_path)
            self._classifier_page = _ClassifierPage(drafts, prepop)
            self._periods_page = _PeriodsPage(drafts, prepop)
            self._folders_page = _FoldersPage(drafts, prepop)
            self._policy_page = _RapportiPolicyPage(prepop)
            self._preview_page = _PreviewPage(
                handle, graphml_path, sito, drafts, self,
            )

            self.addPage(self._classifier_page)
            self.addPage(self._periods_page)
            self.addPage(self._folders_page)
            self.addPage(self._policy_page)
            self.addPage(self._preview_page)

            self._graphml_path = graphml_path

        def get_overrides(self) -> YedOverrides:
            """Collect overrides from every page."""
            return YedOverrides(
                classifier=self._classifier_page.collect(),
                periods=self._periods_page.collect(),
                folders=self._folders_page.collect(),
                policy=self._policy_page.collect(),
            )

        def get_policy(self) -> FolderEdgePolicy:
            """Read selected policy (SKIP when no other selected)."""
            return self._policy_page.collect() or FolderEdgePolicy.SKIP

        def accept(self) -> None:
            """Override accept() to save the sidecar before closing."""
            try:
                save_sidecar(self._graphml_path, self.get_overrides())
            except Exception as e:  # noqa: BLE001
                log.warning("sidecar save failed: %s", e)
            super().accept()


else:
    # Qt absent — define a clear stub so callers can detect missing UI.
    YedImportDialog = None  # type: ignore[assignment]
