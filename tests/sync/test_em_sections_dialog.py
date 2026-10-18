"""La finestra «Sezioni dai modelli 3D» e la sua voce di menu (spec 2026-10-18
sezioni, S7)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
for p in (str(PLUGIN_ROOT / "ext_libs"), str(PLUGIN_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

PLUGIN = (PLUGIN_ROOT / "pyarchinitPlugin.py").read_text(encoding="utf-8")


def _linee():
    from modules.s3dgraphy.sync.em_sections import SectionLine
    return [SectionLine(1, "A1", "attraverso la cella", "1", [(0.0, 0.0), (8.0, 0.0)]),
            SectionLine(2, "", "", "", [(0.0, 0.0), (3.0, 4.0), (3.0, 10.0)])]


def _unita():
    from modules.s3dgraphy.sync.em_drawings_import import DrawingUnit
    return [DrawingUnit("u1", "SU001", "US", ["p/SU001.glb"], ["/x/SU001.glb"], "ok", ymin=-4.0, ymax=-2.0),
            DrawingUnit("u2", "SU002", "US", ["p/SU002.glb"], ["/x/SU002.glb"], "ok", ymin=-3.0, ymax=1.5),
            DrawingUnit("u3", "USV103", "USVs", ["p/USV103.glb"], [], "missing")]


def test_la_finestra_delle_sezioni():
    from qgis.PyQt.QtCore import Qt
    from modules.s3dgraphy.em_drawings import Georef
    from modules.s3dgraphy.em_sections_dialog import SectionsDialog
    geo = Georef("declared", 31700, 327300.0, 448370.0, 500.0, 0.0, metric=True)
    dlg = SectionsDialog(_linee(), _unita(), geo, {1: "3D-SEZ-A1", 2: "3D-SEZ-G2"})
    assert dlg.table.rowCount() == 2
    assert [dlg.table.item(0, c).text() for c in range(1, 7)] == \
        ["A1", "attraverso la cella", "1", "1", "8,00", "3D-SEZ-A1"]
    assert dlg.table.item(1, 4).text() == "2" and dlg.table.item(1, 5).text() == "11,00"
    assert dlg.lb_unita.text() == "2 unità con un modello 3D (1 senza file)"
    assert dlg.lb_quote.text() == "quote da 496,00 a 501,50 m"
    assert dlg.chosen() == ([1, 2], pytest.approx(500.0))
    dlg.table.item(1, 0).setCheckState(Qt.CheckState.Unchecked)
    dlg.sp_z.setValue(0.0)
    assert dlg.chosen() == ([1], pytest.approx(0.0))


def test_la_voce_di_menu_delle_sezioni():
    assert re.search(r'self\.actionEmSections = QAction\(\s*"Extended Matrix → Sezioni dai modelli 3D…"', PLUGIN)
    assert "self.actionEmSections.triggered.connect(self._run_em_sections)" in PLUGIN
    assert '"actionEmSections"' in PLUGIN                     # tolta allo scarico
    corpo = PLUGIN[PLUGIN.index("    def _run_em_sections(self):"):]
    corpo = corpo[:corpo.index("\n    def ", 10)]
    assert "SectionsDialog(" in corpo and "run_sections(" in corpo and "SectionsError" in corpo


def test_senza_proxy_la_voce_di_menu_lo_dice_prima_della_finestra():
    corpo = PLUGIN[PLUGIN.index("    def _run_em_sections(self):"):]
    corpo = corpo[:corpo.index("\n    def ", 10)]
    controllo = corpo.find("es.NO_PROXY")
    assert controllo != -1 and controllo < corpo.index("SectionsDialog(")
