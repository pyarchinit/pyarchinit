"""La finestra «Sezioni dai modelli 3D»: quali linee del layer delle sezioni
tagliare e con quale spostamento Z (spec 2026-10-18-sezioni-dai-proxy-3d, S7)."""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (QDialog, QDialogButtonBox, QDoubleSpinBox, QHBoxLayout, QHeaderView,
                                 QLabel, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout)

from .em_drawings_dialog import position_text, quote_text
from .sync.em_drawings_import import DrawingUnit
from .sync.em_sections import SectionLine


def _numero(x: float) -> str:
    return ("%.2f" % x).replace(".", ",")


class SectionsDialog(QDialog):
    def __init__(self, lines: Sequence[SectionLine], units: Sequence[DrawingUnit], georef,
                 names: Dict[int, str], shift_z: Optional[float] = None,
                 lengths: Optional[Dict[int, float]] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sezioni dai modelli 3D")
        self.resize(760, 460)
        self._lines: List[SectionLine] = list(lines)
        self._units: List[DrawingUnit] = list(units)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(position_text(georef)))
        riga = QHBoxLayout()
        riga.addWidget(QLabel("Spostamento Z:"))
        self.sp_z = QDoubleSpinBox()
        self.sp_z.setRange(-100000.0, 100000.0)
        self.sp_z.setDecimals(2)
        self.sp_z.setSuffix(" m")
        self.sp_z.setValue(georef.shift_z if shift_z is None else float(shift_z))
        self.lb_quote = QLabel()
        riga.addWidget(self.sp_z)
        riga.addWidget(self.lb_quote, 1)
        lay.addLayout(riga)
        self.sp_z.valueChanged.connect(self._aggiorna_quote)
        usabili = sum(1 for u in self._units if u.usable)
        senza = sum(1 for u in self._units if u.status == "missing")
        self.lb_unita = QLabel("%d unità con un modello 3D%s" % (
            usabili, (" (%d senza file)" % senza) if senza else ""))
        lay.addWidget(self.lb_unita)
        intestazioni = ["Taglia", "Sezione", "Descrizione", "Area", "Tratti", "Lunghezza (m)", "Documento"]
        self.table = QTableWidget(len(self._lines), len(intestazioni))
        self.table.setHorizontalHeaderLabels(intestazioni)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        for r, linea in enumerate(self._lines):
            scelta = QTableWidgetItem()
            if linea.segments >= 1 and linea.length > 0:
                scelta.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
                scelta.setCheckState(Qt.CheckState.Checked)
            else:
                scelta.setFlags(Qt.ItemFlag.NoItemFlags)
            self.table.setItem(r, 0, scelta)
            for c, testo in ((1, linea.id_sezione), (2, linea.descr), (3, linea.area),
                             (4, str(linea.segments)),
                             (5, _numero((lengths or {}).get(linea.gid, linea.length))),
                             (6, names.get(linea.gid, ""))):
                cella = QTableWidgetItem(testo)
                cella.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(r, c, cella)
        lay.addWidget(self.table, 1)
        tasti = QHBoxLayout()
        for testo, stato in (("Tutte", Qt.CheckState.Checked), ("Nessuna", Qt.CheckState.Unchecked)):
            b = QPushButton(testo)
            b.clicked.connect(lambda _x=False, s=stato: self._tutte(s))
            tasti.addWidget(b)
        tasti.addStretch(1)
        lay.addLayout(tasti)
        nota = QLabel("Ogni linea diventa una sezione nel layer dei disegni verticali "
                      "(pyunitastratigrafiche_usm): X = metri lungo la linea dal primo punto, "
                      "Y = quota. Una sezione già fatta si rifà.")
        nota.setWordWrap(True)
        lay.addWidget(nota)
        bottoni = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bottoni.button(QDialogButtonBox.StandardButton.Ok).setText("Taglia")
        bottoni.button(QDialogButtonBox.StandardButton.Cancel).setText("Annulla")
        bottoni.accepted.connect(self.accept)
        bottoni.rejected.connect(self.reject)
        lay.addWidget(bottoni)
        self._aggiorna_quote()

    def _aggiorna_quote(self, *_):
        self.lb_quote.setText(quote_text(self._units, self.sp_z.value()))

    def _tutte(self, stato):
        for r in range(self.table.rowCount()):
            cella = self.table.item(r, 0)
            if cella.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                cella.setCheckState(stato)

    def chosen(self) -> Tuple[List[int], float]:
        gids = [linea.gid for r, linea in enumerate(self._lines)
                if self.table.item(r, 0).flags() & Qt.ItemFlag.ItemIsUserCheckable
                and self.table.item(r, 0).checkState() == Qt.CheckState.Checked]
        return gids, float(self.sp_z.value())
