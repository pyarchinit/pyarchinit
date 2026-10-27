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
    assert "Report" in w.findChild(QLabel, "stato").text()


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
    elenco.setCurrentRow(0)                                     # Presentazione: si genera anche lei (13-10-2026)
    assert w.findChild(QPushButton, "rigenera").isEnabled()
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
# Task 6: il plugin — file persistente, un grafo solo per il sito, bottoni
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
    assert "pyarchinit_EM_folder" in vista
    assert "_matrice_temp" not in PLUGIN.read_text(encoding="utf-8")


def test_l_em_json_e_un_grafo_solo_per_tutto_il_sito_senza_domande():
    """Emanuel (13 ottobre 2026): l'em.json è un grafo per tutto il sito;
    la divisione per saggi era un fraintendimento. La domanda «Come divido
    il file?» non c'è più: le due voci di menu chiedono solo il sito."""
    assert "_ask_split" not in PLUGIN.read_text(encoding="utf-8")
    for nome in ("_run_em_matrix_view", "_run_em_export"):
        corpo = _corpo(nome)
        assert "per_saggio=False" in corpo, nome
        assert "QInputDialog.getItem" in corpo, nome          # il sito si sceglie ancora


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
    assert esiti == [(True, "2 capitoli generati, 0 falliti")]       # la Presentazione e l'epoca vuota
    cont, _ = en.load_project(percorso)
    viste = {v.anchor: v for v in en.overview(cont, "it")}
    assert viste["epoch_2_1"].text == "Dal thread." and viste["epoch_2_1"].status == "ai_draft"
    assert viste[en.PRESENTATION_KEY].text == "Dal thread." and viste[en.PRESENTATION_KEY].status == "ai_draft"
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


# ---------------------------------------------------------------------------
# Punto 1 (2026-10-12): la mappa dalla scheda Narrativa
# ---------------------------------------------------------------------------

def test_i_nomi_nel_testo_sono_link_e_il_clic_evidenzia_l_unita(qgs, tmp_path, monkeypatch):
    from qgis.PyQt.QtCore import QUrl
    from qgis.PyQt.QtWidgets import QListWidget, QPushButton, QTextBrowser, QWidget
    from modules.s3dgraphy import em_narrative_tab as tab
    from modules.s3dgraphy import em_matrix_panel as panel
    monkeypatch.setattr(tab.en, "llm_config", lambda load=None: None)
    chiamate = []
    monkeypatch.setattr(panel, "highlight", lambda iface, ids, lang="it": chiamate.append(list(ids)) or (len(ids), "ok"))
    monkeypatch.setattr(panel, "can_highlight", lambda ids: True)
    radice = QWidget()
    iface = _Iface()
    w = tab.build_tab(radice, iface)
    from s3dgraphy.container import container_of
    from modules.s3dgraphy import em_narrative as en
    g = _grafo()
    n = en.scaffold(g, "it")
    en.generate_chapter(g, n, n.chapter_by_anchor("epoch_1_1"), chat=lambda m: "Sotto [[u2]] niente.", model="m")
    percorso = tmp_path / "villa.em.json"
    en.save_project(container_of(g), percorso)
    tab.show_file(w, percorso)
    elenco = w.findChild(QListWidget, "capitoli")
    testo = w.findChild(QTextBrowser, "testo")
    assert not testo.openLinks()
    elenco.setCurrentRow(1)
    assert 'unit:u2' in testo.toHtml() and "1.US2" in testo.toPlainText()
    w._apri_unita(QUrl("unit:u2"))
    assert chiamate == [["u2"]]
    assert iface.messageBar().messaggi[-1][0] == "info"
    mappa = w.findChild(QPushButton, "mappa")
    assert mappa.isEnabled()
    mappa.click()
    assert chiamate[-1] == ["u2"]                                     # le unità del capitolo scelto
    elenco.setCurrentRow(0)                                           # Presentazione: niente unità
    assert not mappa.isEnabled()


def test_il_bottone_mappa_e_spento_senza_capitolo():
    src = TAB.read_text(encoding="utf-8")
    assert "setOpenLinks(False)" in src and "anchorClicked" in src and '"mappa"' in src


# ---------------------------------------------------------------------------
# Immagini e PDF (2026-10-12)
# ---------------------------------------------------------------------------

def test_il_bersaglio_dell_export_conosce_il_pdf():
    from modules.s3dgraphy.em_narrative_tab import export_target
    assert export_target("/x/v.pdf", "Pagina HTML (*.html)") == ("/x/v.pdf", "pdf")
    assert export_target("/x/v", "PDF stampabile (*.pdf)") == ("/x/v.pdf", "pdf")


def test_la_scheda_tiene_la_connessione_e_esporta_il_pdf_con_le_figure(qgs, tmp_path, monkeypatch):
    from qgis.PyQt.QtWidgets import QListWidget, QPushButton, QWidget
    from modules.s3dgraphy import em_narrative_tab as tab
    from modules.s3dgraphy import em_narrative as en
    monkeypatch.setattr(tab.en, "llm_config", lambda load=None: None)
    percorso = _file_con_narrativa(tmp_path)
    radice = QWidget()
    iface = _Iface()
    w = tab.build_tab(radice, iface)
    tab.show_file(w, percorso, conn_str="sqlite:///finto.sqlite")
    assert w._stato.conn == "sqlite:///finto.sqlite"
    chiamate = {}

    def finte_figure(g, n, conn, thumb, resize, **kw):
        chiamate["fig"] = conn
        return {"us:u2": b"\x89PNG"}

    def finto_pdf(g, n, path, figures=None, lang="it"):
        chiamate["pdf"] = (str(path), dict(figures or {}))
        return str(path)
    monkeypatch.setattr(en, "figures_for", finte_figure)
    monkeypatch.setattr(en, "export_pdf", finto_pdf)
    proposte = []
    monkeypatch.setattr(tab.QFileDialog, "getSaveFileName",
                        staticmethod(lambda w_, titolo, proposto, filtro: proposte.append(proposto)
                                     or (str(tmp_path / "out"), "PDF stampabile (*.pdf)")))
    monkeypatch.setattr(tab, "_bases", lambda: (str(tmp_path), str(tmp_path)))
    w.findChild(QListWidget, "capitoli").setCurrentRow(1)
    w.findChild(QPushButton, "esporta").click()
    assert chiamate["fig"] == "sqlite:///finto.sqlite"
    assert chiamate["pdf"] == (str(tmp_path / "out.pdf"), {"us:u2": b"\x89PNG"})
    assert iface.messageBar().messaggi[-1][0] == "info"
    assert proposte and not proposte[0].lower().endswith((".html", ".docx", ".pdf"))   # decide il filtro


def test_il_pannello_passa_la_connessione_alla_scheda():
    src = PANEL.read_text(encoding="utf-8")
    assert "show_file(scheda_narrativa, em_json_path, conn_str)" in src
    assert "def resize_base" in src


def test_mostra_sulla_mappa_e_spento_mentre_si_genera(qgs, tmp_path, monkeypatch):
    from qgis.PyQt.QtWidgets import QListWidget, QPushButton, QWidget
    from modules.s3dgraphy import em_narrative_tab as tab
    from modules.s3dgraphy import em_matrix_panel as panel
    monkeypatch.setattr(tab.en, "llm_config", lambda load=None: None)
    monkeypatch.setattr(panel, "can_highlight", lambda ids: True)
    radice = QWidget()
    w = tab.build_tab(radice, _Iface())
    tab.show_file(w, _file_con_narrativa(tmp_path))
    elenco = w.findChild(QListWidget, "capitoli")
    elenco.setCurrentRow(1)
    assert w.findChild(QPushButton, "mappa").isEnabled()
    w._stato.thread = _ThreadFinto()
    elenco.setCurrentRow(2)
    elenco.setCurrentRow(1)
    assert not w.findChild(QPushButton, "mappa").isEnabled()
    w._stato.thread = None


# ------------------------------------------------ la narrativa del file (17-10-2026)

def _file_del_file(tmp_path):
    """Un em.json con la narrativa sua, come TempluMare: capitoli canonici,
    in inglese, nessun template."""
    from s3dgraphy.container import container_of
    from s3dgraphy.nodes.narrative_node import NarrativeNode
    from modules.s3dgraphy import em_narrative as en
    g = _grafo()
    n = NarrativeNode(node_id="narrative_villa", name="The Villa", lang="en")
    n.add_chapter("Survey — Introduction", canonical=True).add_prose("Known since 1750.")
    n.add_chapter("The Roman house", anchor="epoch_1_1", canonical=True).add_prose("Rebuilt.")
    g.add_node(n)
    percorso = tmp_path / "villa.em.json"
    en.save_project(container_of(g), percorso)
    return percorso


def _scheda(tab, percorso, monkeypatch, iface=None):
    from qgis.PyQt.QtWidgets import QWidget
    monkeypatch.setattr(tab.en, "llm_config", lambda load=None: None)
    radice = QWidget()
    w = tab.build_tab(radice, iface or _Iface())
    w._radice_viva = radice                                     # noqa: SLF001
    tab.show_file(w, percorso)
    return w


def test_la_lingua_parte_da_quella_della_narrativa_del_file(qgs, tmp_path, monkeypatch):
    from qgis.PyQt.QtWidgets import QComboBox
    from modules.s3dgraphy import em_narrative_tab as tab
    monkeypatch.setattr(tab, "_lang", lambda: "it")
    w = _scheda(tab, _file_del_file(tmp_path), monkeypatch)
    lingua = w.findChild(QComboBox, "lingua")
    assert lingua is not None and lingua.currentData() == "en"
    assert lingua.count() == 10


def test_senza_narrativa_la_lingua_e_quella_di_qgis(qgs, tmp_path, monkeypatch):
    from qgis.PyQt.QtWidgets import QComboBox
    from modules.s3dgraphy import em_narrative as en
    from modules.s3dgraphy import em_narrative_tab as tab
    from s3dgraphy.container import container_of
    monkeypatch.setattr(tab, "_lang", lambda: "fr")
    percorso = tmp_path / "villa.em.json"
    en.save_project(container_of(_grafo()), percorso)
    w = _scheda(tab, percorso, monkeypatch)
    assert w.findChild(QComboBox, "lingua").currentData() == "fr"


def _prepara_con(tab, monkeypatch, tmp_path, risposta, lingua="it"):
    from qgis.PyQt.QtWidgets import QComboBox, QListWidget, QPushButton
    chieste = []
    monkeypatch.setattr(tab, "_chiedi_capitoli",
                        lambda parent, n: chieste.append(n) or risposta)
    iface = _Iface()
    percorso = _file_del_file(tmp_path)
    w = _scheda(tab, percorso, monkeypatch, iface)
    combo = w.findChild(QComboBox, "lingua")
    combo.setCurrentIndex(combo.findData(lingua))
    w.findChild(QPushButton, "prepara").click()
    elenco = w.findChild(QListWidget, "capitoli")
    return chieste, [elenco.item(i).text() for i in range(elenco.count())], iface, percorso


def test_prepara_sulla_narrativa_del_file_chiede_e_solo_i_suoi_non_aggiunge_niente(qgs, tmp_path, monkeypatch):
    from modules.s3dgraphy import em_narrative_tab as tab
    chieste, voci, iface, _p = _prepara_con(tab, monkeypatch, tmp_path, "file")
    assert chieste == [2] and len(voci) == 2
    assert iface.messageBar().messaggi[-1][0] == "info"


def test_prepara_aggiungendo_quelli_di_pyarchinit_li_scrive_nella_lingua_scelta(qgs, tmp_path, monkeypatch):
    from modules.s3dgraphy import em_narrative as en
    from modules.s3dgraphy import em_narrative_tab as tab
    chieste, voci, _iface, percorso = _prepara_con(tab, monkeypatch, tmp_path, "pyarchinit", "it")
    assert chieste == [2] and len(voci) > 2
    assert any(v.startswith("Presentazione") for v in voci)
    assert voci[0].startswith("Survey — Introduction")
    n = en.narrative_of(en.load_project(percorso)[0].active())
    assert n.data.get("template_id") == "site_story"


def test_prepara_annullato_non_tocca_il_file(qgs, tmp_path, monkeypatch):
    from modules.s3dgraphy import em_narrative_tab as tab
    chieste, voci, iface, percorso = _prepara_con(tab, monkeypatch, tmp_path, None)
    assert chieste == [2] and len(voci) == 2 and iface.messageBar().messaggi == []


def test_genera_passa_al_thread_la_lingua_scelta(qgs, tmp_path, monkeypatch):
    from qgis.PyQt.QtWidgets import QComboBox, QPushButton, QWidget
    from modules.s3dgraphy import em_narrative_tab as tab

    class _Segnale:
        def connect(self, *_a):
            pass

    creati = []

    class _Finto:
        def __init__(self, path, cfg, lang, anchors=None, parent=None, write_lang=None):
            creati.append({"lang": lang, "write_lang": write_lang})
            self.progress = self.finished_ok = self.finished = _Segnale()

        def start(self):
            pass

        def deleteLater(self):
            pass

    class _Cfg:
        model, provider = "finto", None
    monkeypatch.setattr(tab, "NarrativeThread", _Finto)
    monkeypatch.setattr(tab.en, "llm_config", lambda load=None: (_Cfg(), "us_report"))
    radice = QWidget()
    w = tab.build_tab(radice, _Iface())
    tab.show_file(w, _file_con_narrativa(tmp_path))
    combo = w.findChild(QComboBox, "lingua")
    combo.setCurrentIndex(combo.findData("de"))
    w.findChild(QPushButton, "genera").click()
    assert creati and creati[-1]["write_lang"] == "de"


# ------------------------------------------------ i media scelti (5.13.130)

def test_scegli_i_media_avvia_il_thread_con_database_cartelle_e_lingua(qgs, tmp_path, monkeypatch):
    from qgis.PyQt.QtWidgets import QComboBox, QPushButton, QWidget
    from modules.s3dgraphy import em_narrative_tab as tab

    class _Segnale:
        def connect(self, *_a):
            pass

    creati = []

    class _Finto:
        def __init__(self, path, cfg, conn, bases, write_lang=None, parent=None):
            creati.append({"conn": conn, "bases": bases, "cfg": cfg, "write_lang": write_lang})
            self.progress = self.finished_ok = self.finished = _Segnale()

        def start(self):
            pass

        def deleteLater(self):
            pass

    monkeypatch.setattr(tab, "MediaThread", _Finto)
    monkeypatch.setattr(tab, "_bases", lambda: ("/t/", "/r/"))
    monkeypatch.setattr(tab.en, "llm_config", lambda load=None: None)
    radice = QWidget()
    w = tab.build_tab(radice, _Iface())
    tab.show_file(w, _file_con_narrativa(tmp_path), conn_str="sqlite:///db.sqlite")
    bottone = w.findChild(QPushButton, "media")
    assert bottone is not None and bottone.isEnabled()          # anche senza AI: scelta automatica
    combo = w.findChild(QComboBox, "lingua")
    combo.setCurrentIndex(combo.findData("en"))
    bottone.click()
    assert creati == [{"conn": "sqlite:///db.sqlite", "bases": ("/t/", "/r/"), "cfg": None,
                       "write_lang": "en"}]


def test_il_thread_dei_media_sceglie_con_l_ai_e_salva(qgs, tmp_path, monkeypatch):
    import json as _json
    from modules.s3dgraphy import em_narrative as en
    from modules.s3dgraphy import em_narrative_media as nm
    from modules.s3dgraphy import em_narrative_tab as tab
    from modules.utility import llm_providers as lp
    temperature_viste = []

    def finto_stream(cfg, messages, max_tokens=None, temperature=None, meta=None):
        temperature_viste.append(temperature)
        yield _json.dumps({"choices": [{"key": "k1", "after": 1, "caption": "Il muro."}]})
    monkeypatch.setattr(lp.LLMProviderManager, "stream_chat", staticmethod(finto_stream))
    monkeypatch.setattr(nm, "chapter_media_candidates",
                        lambda graph, chapter, *a, **k: [nm.MediaCandidate("k1", "u2", "1.US2", "m.glb", "3d")]
                        if getattr(chapter, "anchor", None) == "epoch_1_1" else [])

    class _Cfg:
        model = "finto"
    percorso = _file_con_narrativa(tmp_path)
    t = tab.MediaThread(percorso, _Cfg(), "sqlite:///db.sqlite", ("", ""), write_lang="it")
    esiti = []
    t.finished_ok.connect(lambda ok, m: esiti.append((ok, m)))
    t.run()
    assert esiti and esiti[0][0] is True and "1" in esiti[0][1]
    assert temperature_viste == [0]
    n = en.narrative_of(en.load_project(percorso)[0].active())
    scelte = nm.stored_choices(n, n.chapter_by_anchor("epoch_1_1"))
    assert scelte and scelte[0]["key"] == "k1" and scelte[0]["by"] == "ai"
