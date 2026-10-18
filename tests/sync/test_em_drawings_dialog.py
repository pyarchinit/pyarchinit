"""La finestra «Geometrie dai modelli 3D» (spec 2026-10-18, D12)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
for p in (str(PLUGIN_ROOT / "ext_libs"), str(PLUGIN_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)


def _unita():
    from modules.s3dgraphy.sync.em_drawings_import import DrawingUnit
    return [DrawingUnit("u1", "SU001", "US", ["proxies/SU001.glb"], ["/x/SU001.glb"], "ok",
                        triangles=12, ymin=-4.0, ymax=-2.0),
            DrawingUnit("u2", "SU002", "US", ["proxies/SU002.glb"], ["/x/SU002.glb"], "ok",
                        hand_plan=True, triangles=12, ymin=-3.0, ymax=1.5),
            DrawingUnit("u3", "USV103", "USVs", ["proxies/USV103.glb"], [], "missing")]


def _geo(usable=True):
    from modules.s3dgraphy.em_drawings import Georef
    return Georef("declared" if usable else "undeclared", 31700 if usable else None,
                  327300.0, 448370.0, 500.0, 0.0, metric=usable)


def test_la_finestra_mostra_unita_e_scelta():
    from modules.s3dgraphy.em_drawings_dialog import DrawingsDialog
    from modules.s3dgraphy.sync.em_drawings_import import default_choice
    unita, geo = _unita(), _geo()
    dlg = DrawingsDialog(unita, default_choice(unita, geo), geo)
    assert dlg.table.rowCount() == 3
    assert dlg.table.item(1, 4).text() == "ok; ha già una pianta a mano"
    assert dlg.table.item(2, 4).text() == "file non trovato"
    scelta = dlg.choice()
    assert scelta.plan == {"u1"} and scelta.prospect == {"u1", "u2"}
    assert scelta.sides == ("N", "E", "S", "W") and scelta.shift_z == pytest.approx(500.0)
    assert dlg.lb_quote.text() == "quote da 496,00 a 501,50 m"
    dlg.sp_z.setValue(0.0)
    assert dlg.lb_quote.text() == "quote da -4,00 a 1,50 m"
    dlg.cb_lati["W"].setChecked(False)
    assert dlg.choice().sides == ("N", "E", "S")


def test_senza_posizione_la_pianta_non_si_sceglie():
    from modules.s3dgraphy.em_drawings_dialog import DrawingsDialog, position_text
    from modules.s3dgraphy.sync.em_drawings_import import default_choice
    unita, geo = _unita(), _geo(False)
    dlg = DrawingsDialog(unita, default_choice(unita, geo), geo)
    assert dlg.choice().plan == set()
    assert "non dice dove sta la scena" in position_text(geo)
    assert position_text(_geo()) == ("Posizione (dall'em.json): EPSG:31700 · X +327300 · "
                                     "Y +448370 · rotazione 0°")


BRIDGE = (PLUGIN_ROOT / "modules" / "s3dgraphy" / "s3dgraphy_dot_bridge.py").read_text(encoding="utf-8")


def test_la_scheda_import_ha_la_casella_spenta(monkeypatch):
    # Senza database il pannello «Verifica rapporti» apre un avviso modale:
    # senza schermo aspetterebbe per sempre.
    from qgis.PyQt.QtWidgets import QMessageBox
    for nome in ("warning", "critical", "information"):
        monkeypatch.setattr(QMessageBox, nome, staticmethod(lambda *a, **k: None))
    from modules.s3dgraphy.s3dgraphy_dot_bridge import S3DGraphyExportDialog
    dlg = S3DGraphyExportDialog(db_manager=None)
    assert dlg.cb_geom_3d.text() == "Ricava piante e prospetti dai modelli 3D"
    assert not dlg.cb_geom_3d.isChecked() and not dlg.btn_geom_3d.isEnabled()
    dlg.cb_geom_3d.setChecked(True)
    assert dlg.btn_geom_3d.isEnabled()


def test_applica_controlla_il_sistema_prima_di_scrivere_e_disegna_dopo_i_media():
    corpo = BRIDGE[BRIDGE.index("        def _on_import_apply(self):"):]
    corpo = corpo[:corpo.index("\n        def ", 10)]
    assert corpo.index('decisione.kind == "refuse"') < corpo.index("GraphIngestor().populate_list(")
    assert corpo.index('decisione.kind == "convert"') < corpo.index("GraphIngestor().populate_list(")
    assert corpo.index("self._import_media(") < corpo.index("self._import_drawings(")


def test_l_anteprima_dice_la_riga_del_3d_e_si_ferma_col_sistema_sbagliato():
    corpo = BRIDGE[BRIDGE.index("        def _on_import_preview(self):"):]
    corpo = corpo[:corpo.index("\n        def ", 10)]
    assert "preview_line(unita, scelta, geo)" in corpo
    assert corpo.index('decisione.kind == "refuse"') < corpo.rindex("self.btn_apply.setEnabled(True)")
