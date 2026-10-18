"""La finestra «Geometrie dai modelli 3D» dell'import em.json: quali unità
hanno pianta e prospetto, quali lati del sito, lo spostamento Z
(spec 2026-10-18-geometrie-dai-proxy-3d-design, D12)."""
from __future__ import annotations

from typing import List, Sequence

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox, QDoubleSpinBox, QHBoxLayout,
                                 QHeaderView, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                                 QVBoxLayout)

from .sync.em_drawings_import import Choice, DrawingUnit, status_text

_LATI = (("N", "Nord"), ("E", "Est"), ("S", "Sud"), ("W", "Ovest"))


def _numero(x: float) -> str:
    return ("%.2f" % x).replace(".", ",")


def position_text(georef) -> str:
    if not georef.usable:
        return ("L'em.json non dice dove sta la scena: niente piante, solo prospetti "
                "con le quote locali.")
    return "Posizione (dall'em.json): EPSG:%d · X %+.0f · Y %+.0f · rotazione %.0f°" % (
        georef.epsg, georef.shift_x, georef.shift_y, georef.rotation)


def quote_text(units: Sequence[DrawingUnit], shift_z: float) -> str:
    basse = [u.ymin for u in units if u.usable and u.ymin is not None]
    alte = [u.ymax for u in units if u.usable and u.ymax is not None]
    if not basse:
        return ""
    return "quote da %s a %s m" % (_numero(min(basse) + shift_z), _numero(max(alte) + shift_z))


class DrawingsDialog(QDialog):
    def __init__(self, units: Sequence[DrawingUnit], choice: Choice, georef, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Geometrie dai modelli 3D")
        self.resize(720, 520)
        self._units: List[DrawingUnit] = list(units)
        self._georef = georef
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(position_text(georef)))
        riga = QHBoxLayout()
        riga.addWidget(QLabel("Spostamento Z:"))
        self.sp_z = QDoubleSpinBox()
        self.sp_z.setRange(-100000.0, 100000.0)
        self.sp_z.setDecimals(2)
        self.sp_z.setSuffix(" m")
        self.sp_z.setValue(georef.shift_z if choice.shift_z is None else float(choice.shift_z))
        self.lb_quote = QLabel()
        riga.addWidget(self.sp_z)
        riga.addWidget(self.lb_quote, 1)
        lay.addLayout(riga)
        self.sp_z.valueChanged.connect(self._aggiorna_quote)
        lati = QHBoxLayout()
        lati.addWidget(QLabel("Prospetti del sito:"))
        self.cb_lati = {}
        for codice, nome in _LATI:
            cb = QCheckBox(nome)
            cb.setChecked(codice in choice.sides)
            self.cb_lati[codice] = cb
            lati.addWidget(cb)
        lati.addStretch(1)
        lay.addLayout(lati)
        self.table = QTableWidget(len(self._units), 5)
        self.table.setHorizontalHeaderLabels(["Unità", "Tipo", "Pianta", "Prospetto", "Stato"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        for r, u in enumerate(self._units):
            for c, testo in ((0, u.name), (1, u.unit_type), (4, status_text(u))):
                it = QTableWidgetItem(testo)
                it.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(r, c, it)
            for c, scelte, possibile in ((2, choice.plan, u.usable and georef.usable),
                                         (3, choice.prospect, u.usable)):
                it = QTableWidgetItem()
                if possibile:
                    it.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
                    it.setCheckState(Qt.CheckState.Checked if u.key in scelte else Qt.CheckState.Unchecked)
                else:
                    it.setFlags(Qt.ItemFlag.NoItemFlags)
                self.table.setItem(r, c, it)
        lay.addWidget(self.table, 1)
        tasti = QHBoxLayout()
        for testo, stato in (("Tutte", Qt.CheckState.Checked), ("Nessuna", Qt.CheckState.Unchecked)):
            b = QPushButton(testo)
            b.clicked.connect(lambda _x=False, s=stato: self._tutte(s))
            tasti.addWidget(b)
        tasti.addStretch(1)
        lay.addLayout(tasti)
        nota = QLabel("Le geometrie ricavate da un import precedente di questo sito vengono "
                      "sostituite; quelle disegnate a mano restano.")
        nota.setWordWrap(True)
        lay.addWidget(nota)
        bottoni = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bottoni.button(QDialogButtonBox.StandardButton.Ok).setText("Conferma")
        bottoni.button(QDialogButtonBox.StandardButton.Cancel).setText("Annulla")
        bottoni.accepted.connect(self.accept)
        bottoni.rejected.connect(self.reject)
        lay.addWidget(bottoni)
        self._aggiorna_quote()

    def _aggiorna_quote(self, *_):
        self.lb_quote.setText(quote_text(self._units, self.sp_z.value()))

    def _tutte(self, stato):
        for r in range(self.table.rowCount()):
            for c in (2, 3):
                it = self.table.item(r, c)
                if it.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                    it.setCheckState(stato)

    def _spuntate(self, colonna: int) -> set:
        return {u.key for r, u in enumerate(self._units)
                if self.table.item(r, colonna).flags() & Qt.ItemFlag.ItemIsUserCheckable
                and self.table.item(r, colonna).checkState() == Qt.CheckState.Checked}

    def choice(self) -> Choice:
        return Choice(plan=self._spuntate(2) if self._georef.usable else set(),
                      prospect=self._spuntate(3),
                      sides=tuple(c for c, _n in _LATI if self.cb_lati[c].isChecked()),
                      shift_z=float(self.sp_z.value()))
