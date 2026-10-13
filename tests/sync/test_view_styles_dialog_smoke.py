"""La finestra «Stili delle viste» in offscreen, sul database di prova
copiato: elenca le viste, carica l'anteprima senza toccare il progetto,
applica i preset, salva, rende predefinito, esporta e importa QML, applica
ai layer del progetto (Task 5). Serve il Python di QGIS."""
from __future__ import annotations

import os
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("qgis.gui")

from qgis.core import QgsApplication, QgsProject, QgsVectorLayer  # noqa: E402
from qgis.PyQt.QtWidgets import QTreeWidget  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from gui import view_styles_dialog as vsd  # noqa: E402
from modules.utility import view_styles_store as store  # noqa: E402
from modules.utility.view_styles import GROUPS, choose_style  # noqa: E402


@pytest.fixture(scope="module")
def qgs():
    app = QgsApplication.instance()
    if app is None:
        QgsApplication.setPrefixPath(
            os.environ.get("QGIS_PREFIX_PATH", "/Applications/QGIS.app/Contents/MacOS"), True)
        app = QgsApplication([], False)
        app.initQgis()
    return app


@pytest.fixture
def db(tmp_path):
    dest = tmp_path / "prova.sqlite"
    shutil.copy(_ROOT / "resources" / "dbfiles" / "pyarchinit_db.sqlite", dest)
    sito = sqlite3.connect(str(dest)).execute(
        "select sito from us_table group by sito order by count(*) desc limit 1").fetchone()[0]
    return "sqlite:///%s" % dest, sito, dest


def test_la_finestra_elenca_le_viste_e_carica_l_anteprima_senza_toccare_il_progetto(qgs, db):
    conn, sito, _ = db
    prima = len(QgsProject.instance().mapLayers())
    dlg = vsd.ViewStylesDialog(None, conn, sito, lang="it")
    albero = dlg.findChild(QTreeWidget, "viste")
    assert albero.topLevelItemCount() == len(GROUPS)
    assert dlg.select_view("pyarchinit_us_view")
    assert dlg.current_layer() is not None and dlg.current_layer().featureCount() > 0
    assert len(QgsProject.instance().mapLayers()) == prima                   # niente nel progetto
    assert dlg.current_layer().labelsEnabled()                               # la ricetta di partenza
    assert dlg.current_recipe().preset == "us_circle"
    assert dlg.select_view("pyarchinit_quote_view")
    assert dlg.current_recipe().preset == "quota" and dlg.current_layer().labelsEnabled()
    assert dlg.select_view("pyarchinit_doc_view_b")                          # non c'è nel DB di prova
    assert dlg.current_layer() is None and "non presente" in dlg.stato.text().lower()
    assert dlg.select_view("pyarchinit_strutture_view")                      # senza QML, senza etichette
    assert not dlg.current_recipe().enabled
    dlg.close()


def test_preset_salva_predefinito_esporta_importa_e_applica_al_progetto(qgs, db, tmp_path):
    conn, sito, percorso = db
    dlg = vsd.ViewStylesDialog(None, conn, sito, lang="it")
    assert dlg.select_view("pyarchinit_us_view")
    assert dlg.apply_symbology_preset("outline")
    assert dlg.current_layer().renderer().type() == "singleSymbol"
    assert dlg.apply_symbology_preset("cat:d_stratigrafica")
    assert dlg.current_layer().renderer().type() == "categorizedSymbol"
    dlg.apply_label_preset("none")
    assert not dlg.current_layer().labelsEnabled()
    dlg.apply_label_preset("us_circle")
    assert dlg.current_layer().labelsEnabled() and dlg.current_recipe().one_per_unit
    dlg.set_text_format(size_mm=3.5, bold=True, color="#AA0000", circle=True)
    formato = dlg.current_layer().labeling().settings().format()
    assert abs(formato.size() - 3.5) < 0.01 and formato.font().bold() and formato.color().red() == 170
    assert formato.background().enabled()
    sid = dlg.save("prova", None)
    engine = create_engine(conn)
    elenco = store.list_styles(engine, "pyarchinit_us_view")
    assert [s.name for s in elenco] == ["prova"] and elenco[0].id == sid and elenco[0].for_all_sites
    assert dlg.set_default("site")                                           # si sposta sul sito
    elenco = store.list_styles(engine, "pyarchinit_us_view")
    scelto = choose_style(elenco, sito)
    assert scelto is not None and scelto.name == "prova" and scelto.site == sito
    assert dlg.stili.count() >= 1 and "predefinito" in dlg.stili.item(0).text()
    qml = tmp_path / "prova.qml"
    assert dlg.export_qml(str(qml)) and "<labeling" in qml.read_text(encoding="utf-8")
    nuovo = dlg.import_qml(str(qml))
    assert nuovo and {s.name for s in store.list_styles(engine, "pyarchinit_us_view")} == {"prova", "prova"} \
        or len(store.list_styles(engine, "pyarchinit_us_view")) == 2
    assert dlg.import_qml(str(tmp_path / "manca.qml")) is None
    # un layer del progetto che viene dalla stessa vista riceve lo stile
    layer = QgsVectorLayer("%s|layername=pyarchinit_us_view" % percorso, "US view", "ogr")
    assert layer.isValid()
    QgsProject.instance().addMapLayer(layer, False)
    try:
        dlg.apply_symbology_preset("outline")
        assert dlg.apply_to_project() == 1
        assert layer.renderer().type() == "singleSymbol" and layer.labelsEnabled()
    finally:
        QgsProject.instance().removeMapLayer(layer.id())
    dlg.close()


def test_un_motore_assente_lascia_solo_esportare(qgs, db, tmp_path):
    conn, sito, _ = db
    dlg = vsd.ViewStylesDialog(None, conn, sito, lang="en", engine=None)
    dlg._engine = None
    assert dlg.select_view("pyarchinit_quote_view")
    assert dlg.save("x", None) is None and dlg.set_default("all") is False
    assert dlg.export_qml(str(tmp_path / "q.qml"))
    dlg.close()
