"""Verifica rapporti stratigrafici — Qt panel + dialog.

UI over ``modules.utility.rapporti_check``: pick a site, run the
s3dgraphy-backed validators (cycles / self-loops / connection legality /
reciprocity), preview the conservative fixes, apply them (snapshot-protected)
and roll back. See docs/superpowers/specs/2026-06-06-rapporti-validation-autofix-design.md.

``RapportiCheckPanel`` is a reusable ``QWidget`` (embedded as a tab in the
s3dgraphy import dialog); ``RapportiCheckDialog`` is a thin standalone wrapper.
"""
from __future__ import annotations

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QLabel, QMessageBox, QSplitter,
)

from modules.utility import rapporti_check as RC

_USER_ROLE = int(Qt.UserRole)


def _qgis_lang():
    """Current QGIS UI language (2-letter), defaulting to Italian."""
    try:
        from qgis.core import QgsSettings
        return (QgsSettings().value("locale/userLocale", "it", type=str)
                or "it")[:2]
    except Exception:
        return "it"


class RapportiCheckPanel(QWidget):
    """Site picker → report → preview → apply / rollback.

    ``db_provider`` (optional): a zero-arg callable returning a backend
    ``DbHandle``. When omitted the panel resolves the active pyArchInit
    project connection itself (standalone use). The import dialog passes
    its own ``db_manager`` so the verifica runs against the same DB it
    just imported into.
    """

    def __init__(self, iface=None, parent=None, db_provider=None):
        super().__init__(parent)
        self.iface = iface
        self._db_provider = db_provider
        self._lang = _qgis_lang()
        self._report = None
        self._token = None
        self._build_ui()
        self._load_sites()

    # -- db plumbing (backend-agnostic) ------------------------------------
    def _handle(self):
        if self._db_provider is not None:
            from modules.s3dgraphy.sync._db_handle import _resolve_db_handle
            return _resolve_db_handle(self._db_provider())
        from modules.db.pyarchinit_conn_strings import Connection
        from modules.db.pyarchinit_db_manager import get_db_manager
        from modules.s3dgraphy.sync._db_handle import _resolve_db_handle
        conn_str = Connection().conn_str()
        db_manager = get_db_manager(conn_str, use_singleton=True)
        return _resolve_db_handle(db_manager)

    # -- UI -----------------------------------------------------------------
    def _build_ui(self):
        lay = QVBoxLayout(self)
        top = QHBoxLayout()
        top.addWidget(QLabel("Sito:"))
        self.cboSite = QComboBox()
        top.addWidget(self.cboSite, 1)
        self.btnRun = QPushButton("Esegui verifica")
        self.btnRun.clicked.connect(self._run)
        top.addWidget(self.btnRun)
        self.btnContinuity = QPushButton("Genera continuità")
        self.btnContinuity.setToolTip(
            "Crea/aggiorna le schede CON per le US/USM che attraversano "
            "più periodi (periodo iniziale ≠ finale).")
        self.btnContinuity.clicked.connect(self._run_genera_continuita)
        top.addWidget(self.btnContinuity)
        lay.addLayout(top)

        split = QSplitter(Qt.Vertical)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Problema"])
        self.tree.itemSelectionChanged.connect(self._preview)
        split.addWidget(self.tree)
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        split.addWidget(self.preview)
        split.setSizes([420, 200])
        lay.addWidget(split, 1)

        self.lblSummary = QLabel("")
        lay.addWidget(self.lblSummary)

        btns = QHBoxLayout()
        btns.addStretch(1)
        self.btnRollback = QPushButton("Annulla ultimo fix")
        self.btnRollback.clicked.connect(self._rollback)
        self.btnRollback.setEnabled(False)
        btns.addWidget(self.btnRollback)
        self.btnApply = QPushButton("Applica fix selezionati")
        self.btnApply.clicked.connect(self._apply)
        btns.addWidget(self.btnApply)
        lay.addLayout(btns)

    def _load_sites(self):
        try:
            from sqlalchemy import text
            handle = self._handle()
            with handle.engine.connect() as conn:
                rows = conn.execute(text(
                    "SELECT DISTINCT sito FROM us_table "
                    "WHERE sito IS NOT NULL AND sito <> '' ORDER BY sito")
                ).fetchall()
            self.cboSite.clear()
            self.cboSite.addItems([str(r[0]) for r in rows])
        except Exception as exc:  # pragma: no cover - UI guard
            QMessageBox.warning(self, "pyArchInit",
                                f"Impossibile leggere i siti: {exc}")

    def select_sito(self, sito):
        """Pre-select *sito* in the picker (used by the import dialog to
        focus the verifica on the site just imported)."""
        if not sito:
            return
        idx = self.cboSite.findText(str(sito))
        if idx >= 0:
            self.cboSite.setCurrentIndex(idx)
        else:
            self.cboSite.addItem(str(sito))
            self.cboSite.setCurrentText(str(sito))

    # -- actions ------------------------------------------------------------
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

    def _render(self):
        self.tree.clear()
        groups = {}
        for iss in self._report.issues:
            groups.setdefault(iss.kind, []).append(iss)
        n_auto = 0
        for kind, issues in groups.items():
            title = RC.kind_title(kind, self._lang)
            top = QTreeWidgetItem([f"{title}  ({len(issues)})"])
            self.tree.addTopLevelItem(top)
            for iss in issues:
                child = QTreeWidgetItem([iss.summary])
                child.setData(0, _USER_ROLE, iss)
                if iss.auto and iss.edits:
                    child.setCheckState(0, Qt.Checked)
                    n_auto += 1
                top.addChild(child)
            top.setExpanded(True)
        total = len(self._report.issues)
        self.lblSummary.setText(
            f"{total} problemi · {n_auto} correggibili automaticamente "
            f"(selezionati). Anteprima un elemento per i dettagli.")
        self._token = None
        self.btnRollback.setEnabled(False)

    def _selected_auto_issues(self):
        out = []
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            for j in range(top.childCount()):
                ch = top.child(j)
                iss = ch.data(0, _USER_ROLE)
                if (iss is not None and iss.auto and iss.edits
                        and ch.checkState(0) == Qt.Checked):
                    out.append(iss)
        return out

    def _preview(self):
        items = self.tree.selectedItems()
        if not items:
            return
        iss = items[0].data(0, _USER_ROLE)
        if iss is None:
            return
        lines = [iss.summary, ""]
        if not iss.edits:
            lines.append("(nessuna correzione automatica — scelta manuale "
                         "nella scheda US)")
        for e in iss.edits:
            for r in e.remove:
                lines.append(f"US {e.us}: rimuovi  {list(r)}")
            for a in e.add:
                lines.append(f"US {e.us}: aggiungi {list(a)}")
            for (col, val) in getattr(e, "set_fields", ()):
                lines.append(f"US {e.us}: imposta {col} = {val}")
        self.preview.setPlainText("\n".join(lines))

    def _apply(self):
        issues = self._selected_auto_issues()
        edits = [e for iss in issues for e in iss.edits]
        if not edits:
            QMessageBox.information(self, "pyArchInit",
                                   "Nessun fix automatico selezionato.")
            return
        sito = self.cboSite.currentText().strip()
        if QMessageBox.question(
                self, "Conferma",
                f"Applicare {len(edits)} correzioni al sito '{sito}'?\n"
                f"(potrai annullare con 'Annulla ultimo fix')",
                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
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
        try:
            self._token = RC.apply_edits(edits, self._handle(), sito=sito)
        except Exception as exc:
            QMessageBox.critical(self, "pyArchInit", f"Apply fallito: {exc}")
            return
        self.btnRollback.setEnabled(True)
        QMessageBox.information(self, "pyArchInit",
                               f"{len(edits)} correzioni applicate.")
        self._run()  # re-scan to show the cleaned-up state
        self.btnRollback.setEnabled(True)

    def _run_genera_continuita(self):
        sito = self.cboSite.currentText().strip()
        if not sito:
            return
        from qgis.PyQt.QtWidgets import QCheckBox, QDialogButtonBox
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

    def _rollback(self):
        if self._token is None:
            return
        try:
            RC.rollback(self._token, self._handle())
        except Exception as exc:
            QMessageBox.critical(self, "pyArchInit", f"Rollback fallito: {exc}")
            return
        self._token = None
        self.btnRollback.setEnabled(False)
        QMessageBox.information(self, "pyArchInit", "Ultimo fix annullato.")
        self._run()


class RapportiCheckDialog(QDialog):
    """Standalone wrapper around :class:`RapportiCheckPanel`."""

    def __init__(self, iface=None, parent=None, db_provider=None):
        super().__init__(parent)
        self.iface = iface
        self.setWindowTitle("Verifica rapporti stratigrafici")
        lay = QVBoxLayout(self)
        self.panel = RapportiCheckPanel(iface=iface, db_provider=db_provider)
        lay.addWidget(self.panel)
        self.resize(760, 680)
