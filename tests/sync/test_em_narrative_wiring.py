"""La scheda «Narrativa» del pannello della matrice (2026-10-12).

Come per il pannello: si leggono le promesse nel sorgente e si prova il
widget in offscreen con un iface finto, senza database e senza modello.
"""
from __future__ import annotations

import ast
import json
import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_ROOT = Path(__file__).resolve().parents[2]
for p in (str(_ROOT / "ext_libs"), str(_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

TAB = _ROOT / "modules" / "s3dgraphy" / "em_narrative_tab.py"
PANEL = _ROOT / "modules" / "s3dgraphy" / "em_matrix_panel.py"


@pytest.fixture(scope="module")
def qgs():
    from qgis.core import QgsApplication
    app = QgsApplication.instance()
    if app is None:
        QgsApplication.setPrefixPath(
            os.environ.get("QGIS_PREFIX_PATH", "/Applications/QGIS.app/Contents/MacOS"), True)
        app = QgsApplication([], False)
        app.initQgis()
    return app


class _Bar:
    def __init__(self):
        self.messaggi = []

    def pushInfo(self, t, m):
        self.messaggi.append(("info", t, m))

    def pushWarning(self, t, m):
        self.messaggi.append(("warn", t, m))


class _Iface:
    def __init__(self):
        self._bar = _Bar()

    def messageBar(self):
        return self._bar

    def mainWindow(self):
        return None


def _grafo():
    from s3dgraphy.graph import Graph
    from s3dgraphy.nodes.author_node import AuthorNode
    from s3dgraphy.nodes.epoch_node import EpochNode
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    g = Graph(graph_id="Villa")
    g.add_node(EpochNode("epoch_1_1", "Età romana", -100, 300))
    g.add_node(EpochNode("epoch_2_1", "Medioevo", 500, 1400))
    for uid, nome, epoca in (("u1", "1.US1", "epoch_2_1"), ("u2", "1.US2", "epoch_1_1")):
        n = StratigraphicUnit(uid, nome)
        n.data = {"us": uid[1:]}
        g.add_node(n)
        g.add_edge(uid + "_fe", uid, epoca, "has_first_epoch")
    g.add_edge("u1_overlies_u2", "u1", "u2", "overlies")
    g.add_node(AuthorNode("author::mario_rossi", name="Mario Rossi"))
    return g


def _file_con_narrativa(tmp_path):
    from s3dgraphy.container import container_of
    from modules.s3dgraphy import em_narrative as en
    g = _grafo()
    n = en.scaffold(g, "it")
    en.generate_chapter(g, n, n.chapter_by_anchor("epoch_1_1"),
                        chat=lambda m: "Bozza romana.", model="m")
    percorso = tmp_path / "villa.em.json"
    en.save_project(container_of(g), percorso)
    return percorso


def test_le_stringhe_hanno_italiano_e_inglese():
    from modules.s3dgraphy.em_narrative_tab import _L
    for chiave, voce in _L.items():
        assert set(voce) >= {"it", "en"}, chiave


def test_il_pannello_ha_la_scheda_e_la_ricarica_a_ogni_apertura():
    src = PANEL.read_text(encoding="utf-8")
    assert "QTabWidget" in src and '"schede"' in src
    assert "em_narrative_tab" in src and "show_file(" in src and "build_tab(" in src
    assert 'tab == "narrativa"' in src
    assert "tab=None" in src


def test_ogni_metodo_privato_chiamato_su_self_esiste_nel_thread():
    albero = ast.parse(TAB.read_text(encoding="utf-8"))
    for cls in [n for n in albero.body if isinstance(n, ast.ClassDef)]:
        definiti = {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}
        attributi = {n.attr for n in ast.walk(cls)
                     if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
                     and n.value.id == "self" and n.attr.startswith("_")
                     and not n.attr.startswith("__")}
        assegnati = {a.attr for n in ast.walk(cls) if isinstance(n, ast.Assign)
                     for t in n.targets for a in ast.walk(t)
                     if isinstance(a, ast.Attribute)}
        assert attributi - definiti - assegnati == set(), cls.name


def test_la_scheda_elenca_i_capitoli_con_gli_stati_e_spegne_l_ai_se_manca(qgs, tmp_path, monkeypatch):
    from qgis.PyQt.QtWidgets import QLabel, QListWidget, QPushButton, QTextBrowser, QWidget
    from modules.s3dgraphy import em_narrative_tab as tab
    monkeypatch.setattr(tab.en, "llm_config", lambda load=None: None)
    radice = QWidget()
    w = tab.build_tab(radice, _Iface())
    assert w.objectName() == "narrativa"
    tab.show_file(w, _file_con_narrativa(tmp_path))
    elenco = w.findChild(QListWidget, "capitoli")
    assert elenco.count() == 3
    voci = [elenco.item(i).text() for i in range(elenco.count())]
    assert any("bozza AI" in v for v in voci) and any("da scrivere" in v for v in voci)
    elenco.setCurrentRow(1)
    assert "Bozza romana" in w.findChild(QTextBrowser, "testo").toPlainText()
    assert not w.findChild(QPushButton, "genera").isEnabled()
    assert not w.findChild(QPushButton, "rigenera").isEnabled()
    assert w.findChild(QPushButton, "convalida").isEnabled()
    assert w.findChild(QPushButton, "esporta").isEnabled()
    assert w.findChild(QPushButton, "prepara").isEnabled()
    assert "Relazione AI" in w.findChild(QLabel, "stato").text()


def test_la_scheda_con_l_ai_impostata_accende_genera_e_rigenera(qgs, tmp_path, monkeypatch):
    from qgis.PyQt.QtWidgets import QLabel, QListWidget, QPushButton, QWidget
    from modules.s3dgraphy import em_narrative_tab as tab

    class _Cfg:
        model, provider = "gpt-finto", None
    monkeypatch.setattr(tab.en, "llm_config", lambda load=None: (_Cfg(), "us_report"))
    radice = QWidget()
    w = tab.build_tab(radice, _Iface())
    tab.show_file(w, _file_con_narrativa(tmp_path))
    assert w.findChild(QPushButton, "genera").isEnabled()
    assert "gpt-finto" in w.findChild(QLabel, "stato").text()
    elenco = w.findChild(QListWidget, "capitoli")
    elenco.setCurrentRow(0)                                     # Presentazione: non si genera
    assert not w.findChild(QPushButton, "rigenera").isEnabled()
    elenco.setCurrentRow(1)
    assert w.findChild(QPushButton, "rigenera").isEnabled()


def test_la_scheda_su_un_file_senza_narrativa_lo_dice(qgs, tmp_path, monkeypatch):
    from qgis.PyQt.QtWidgets import QLabel, QListWidget, QPushButton, QWidget
    from modules.s3dgraphy import em_narrative_tab as tab
    monkeypatch.setattr(tab.en, "llm_config", lambda load=None: None)
    percorso = tmp_path / "vuoto.em.json"
    percorso.write_text(json.dumps({"graphs": {"S": {"nodes": [
        {"id": "e1", "name": "XV", "node_type": "EpochNode", "data": {"start_time": 1400, "end_time": 1499}},
        {"id": "u1", "name": "US1", "node_type": "US", "data": {"us": "1"}}],
        "edges": [{"source": "u1", "target": "e1", "type": "has_first_epoch"}]}}}), encoding="utf-8")
    radice = QWidget()
    w = tab.build_tab(radice, _Iface())
    tab.show_file(w, percorso)
    assert w.findChild(QListWidget, "capitoli").count() == 0
    assert "Nessuna narrativa" in w.findChild(QLabel, "vuoto").text()
    assert not w.findChild(QPushButton, "convalida").isEnabled()
    assert w.findChild(QPushButton, "prepara").isEnabled()


def test_prepara_i_capitoli_senza_ai_scrive_lo_scheletro_nel_file(qgs, tmp_path, monkeypatch):
    from qgis.PyQt.QtWidgets import QListWidget, QPushButton, QWidget
    from modules.s3dgraphy import em_narrative_tab as tab
    from modules.s3dgraphy import em_narrative as en
    from s3dgraphy.container import container_of
    monkeypatch.setattr(tab.en, "llm_config", lambda load=None: None)
    percorso = tmp_path / "villa.em.json"
    en.save_project(container_of(_grafo()), percorso)
    iface = _Iface()
    radice = QWidget()
    w = tab.build_tab(radice, iface)
    tab.show_file(w, percorso)
    w.findChild(QPushButton, "prepara").click()
    assert w.findChild(QListWidget, "capitoli").count() == 3
    assert en.narrative_of(en.load_project(percorso)[0].active()) is not None
    assert iface.messageBar().messaggi and iface.messageBar().messaggi[-1][0] == "info"


def test_un_file_illeggibile_spegne_tutto_e_lo_dice(qgs, tmp_path, monkeypatch):
    from qgis.PyQt.QtWidgets import QLabel, QPushButton, QWidget
    from modules.s3dgraphy import em_narrative_tab as tab
    monkeypatch.setattr(tab.en, "llm_config", lambda load=None: None)
    rotto = tmp_path / "rotto.em.json"
    rotto.write_text("{", encoding="utf-8")
    radice = QWidget()
    w = tab.build_tab(radice, _Iface())
    tab.show_file(w, rotto)
    assert "rotto.em.json" in w.findChild(QLabel, "stato").text()
    for nome in ("genera", "rigenera", "convalida", "prepara", "esporta", "emstudio"):
        assert not w.findChild(QPushButton, nome).isEnabled(), nome


# ---------------------------------------------------------------------------
# Task 6: il plugin — file persistente, domanda sui saggi condivisa, bottoni
# ---------------------------------------------------------------------------

PLUGIN = _ROOT / "pyarchinitPlugin.py"


def _corpo(nome: str) -> str:
    sorgente = PLUGIN.read_text(encoding="utf-8")
    albero = ast.parse(sorgente)
    for n in ast.walk(albero):
        if isinstance(n, ast.FunctionDef) and n.name == nome:
            return ast.get_source_segment(sorgente, n)
    raise AssertionError(nome)


def test_vedi_la_matrice_scrive_nella_cartella_em_e_non_in_una_temporanea():
    vista = _corpo("_run_em_matrix_view")
    assert "tempfile" not in vista and "_matrice_temp" not in vista
    assert "pyarchinit_EM_folder" in vista and "_ask_split(" in vista
    assert "_ask_split(" in _corpo("_run_em_export")
    assert "_matrice_temp" not in PLUGIN.read_text(encoding="utf-8")
    assert "saggi_del_sito" in _corpo("_ask_split")


def test_dopo_l_esportazione_si_puo_aprire_la_narrativa():
    esporta = _corpo("_run_em_export")
    assert "llm_config(" in esporta and 'tab="narrativa"' in esporta
    assert "open_in_emstudio" in esporta and "Narrativa con l'AI" in esporta


# ---------------------------------------------------------------------------
# Il pannello intero, in offscreen: la scheda Narrativa c'è e segue il file
# ---------------------------------------------------------------------------

def test_open_in_panel_costruisce_la_scheda_narrativa_e_la_porta_davanti(qgs, tmp_path, monkeypatch):
    from qgis.PyQt.QtWidgets import QListWidget, QMainWindow, QTabWidget, QWidget
    from modules.s3dgraphy import em_matrix_panel as panel
    from modules.s3dgraphy import em_narrative_tab as tab
    monkeypatch.setattr(tab.en, "llm_config", lambda load=None: None)

    class _IfaceConDock(_Iface):
        def __init__(self):
            super().__init__()
            self._win = QMainWindow()

        def mainWindow(self):
            return self._win

        def addDockWidget(self, area, dock):
            self._win.addDockWidget(area, dock)

        def removeDockWidget(self, dock):
            self._win.removeDockWidget(dock)

    iface = _IfaceConDock()
    percorso = _file_con_narrativa(tmp_path)
    assert panel.open_in_panel(iface, percorso, "Matrice — Villa", tab="narrativa")
    dock = iface.mainWindow().findChild(QWidget, panel.PANEL_OBJECT_NAME)
    schede = dock.findChild(QTabWidget, "schede")
    assert schede is not None and schede.count() == 2 and schede.currentIndex() == 1
    assert dock.findChild(QListWidget, "capitoli").count() == 3

    # Riaperto su un altro file: la scheda segue, e senza `tab` resta su «Unità».
    from s3dgraphy.container import container_of
    from modules.s3dgraphy import em_narrative as en
    altro = tmp_path / "altro.em.json"
    en.save_project(container_of(_grafo()), altro)
    assert panel.open_in_panel(iface, altro, "Matrice — Altro")
    assert dock.findChild(QListWidget, "capitoli").count() == 0
    assert schede.currentIndex() == 0
    panel.close_panel(iface)


# ---------------------------------------------------------------------------
# Revisione finale (2026-10-12): thread e pannello
# ---------------------------------------------------------------------------

class _ThreadFinto:
    def __init__(self, vivo=True):
        self.vivo = vivo
        self.chiamate = []

    def isRunning(self):
        return self.vivo

    def cancel(self):
        self.chiamate.append("cancel")

    def wait(self, ms=None):
        self.chiamate.append(("wait", ms))
        self.vivo = False
        return True

    def terminate(self):
        self.chiamate.append("terminate")


def test_show_file_non_cambia_file_mentre_genera(qgs, tmp_path, monkeypatch):
    from qgis.PyQt.QtWidgets import QWidget
    from modules.s3dgraphy import em_narrative_tab as tab
    monkeypatch.setattr(tab.en, "llm_config", lambda load=None: None)
    radice = QWidget()
    iface = _Iface()
    w = tab.build_tab(radice, iface)
    primo = _file_con_narrativa(tmp_path)
    tab.show_file(w, primo)
    w._stato.thread = _ThreadFinto()
    altro = tmp_path / "altro.em.json"
    altro.write_text("{}", encoding="utf-8")
    tab.show_file(w, altro)
    assert w._stato.path == str(primo)
    assert iface.messageBar().messaggi and iface.messageBar().messaggi[-1][0] == "warn"
    w._stato.thread = None


def test_stop_generation_ferma_e_aspetta_il_thread(qgs, tmp_path, monkeypatch):
    from qgis.PyQt.QtWidgets import QWidget
    from modules.s3dgraphy import em_narrative_tab as tab
    monkeypatch.setattr(tab.en, "llm_config", lambda load=None: None)
    radice = QWidget()
    w = tab.build_tab(radice, _Iface())
    finto = _ThreadFinto()
    w._stato.thread = finto
    tab.stop_generation(w)
    assert finto.chiamate[0] == "cancel" and finto.chiamate[1][0] == "wait"
    assert "terminate" not in finto.chiamate and w._stato.thread is None
    tab.stop_generation(w)                                            # senza thread: niente


def test_il_pannello_chiuso_ferma_la_generazione_e_il_thread_si_cancella_da_solo():
    assert "stop_generation(" in PANEL.read_text(encoding="utf-8")
    src = TAB.read_text(encoding="utf-8")
    assert "finished.connect(t.deleteLater)" in src


def test_il_thread_genera_e_salva_nel_file(qgs, tmp_path, monkeypatch):
    from modules.s3dgraphy import em_narrative_tab as tab
    from modules.s3dgraphy import em_narrative as en
    from modules.utility import llm_providers as lp

    def finto_stream(cfg, messages, max_tokens=None, temperature=None, meta=None):
        if meta is not None:
            meta["truncated"] = False
        yield "Dal thread."
    monkeypatch.setattr(lp.LLMProviderManager, "stream_chat", staticmethod(finto_stream))

    class _Cfg:
        model = "finto"
    percorso = _file_con_narrativa(tmp_path)
    t = tab.NarrativeThread(percorso, _Cfg(), "it")
    esiti = []
    t.finished_ok.connect(lambda ok, m: esiti.append((ok, m)))
    t.run()                                                           # sincrono, senza start()
    assert esiti == [(True, "1 capitoli generati, 0 falliti")]
    cont, _ = en.load_project(percorso)
    viste = {v.anchor: v for v in en.overview(cont, "it")}
    assert viste["epoch_2_1"].text == "Dal thread." and viste["epoch_2_1"].status == "ai_draft"
    assert viste["epoch_1_1"].text == "Bozza romana."                 # il capitolo già scritto non si tocca


def test_il_bersaglio_dell_export_rispetta_l_estensione_scritta():
    from modules.s3dgraphy.em_narrative_tab import export_target
    assert export_target("/x/v.html", "Documento Word (*.docx)") == ("/x/v.html", "html")
    assert export_target("/x/v.docx", "Pagina HTML (*.html)") == ("/x/v.docx", "docx")
    assert export_target("/x/v", "Documento Word (*.docx)") == ("/x/v.docx", "docx")
    assert export_target("/x/v", "Pagina HTML (*.html)") == ("/x/v.html", "html")


def test_esporta_in_em_json_non_usa_exec_underscore_e_mostra_gli_avvisi():
    esporta = _corpo("_run_em_export")
    assert "exec_()" not in esporta and "setDetailedText" in esporta
