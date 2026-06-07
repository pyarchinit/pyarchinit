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

# Human-readable group titles per issue kind.
_KIND_TITLE = {
    RC.SELF_LOOP: "Self-loop (US in relazione con sé stessa)",
    RC.MISSING_RECIPROCITY: "Reciprocità mancante (verrà creata)",
    RC.CONTRADICTION_REDUNDANT: "Contraddizione ridondante",
    RC.CONTRADICTION_AMBIGUOUS: "Contraddizione diretta (scelta manuale)",
    RC.CYCLE: "Ciclo stratigrafico (scelta manuale)",
    RC.ILLEGAL_CONNECTION: "Tipo relazione non valido (solo segnalazione)",
}

_USER_ROLE = int(Qt.UserRole)


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
            handle = self._handle()
            graph = GraphProjector().populate_graph(handle, sito=sito)
            self._report = RC.check_rapporti(graph, sito=sito)
        except Exception as exc:
            QMessageBox.critical(self, "pyArchInit",
                                 f"Verifica fallita: {exc}")
            return
        self._render()

    def _render(self):
        self.tree.clear()
        groups = {}
        for iss in self._report.issues:
            groups.setdefault(iss.kind, []).append(iss)
        n_auto = 0
        for kind, issues in groups.items():
            title = _KIND_TITLE.get(kind, kind)
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
