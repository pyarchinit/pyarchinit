"""Il progetto EM per EMStudio: l'em.json dentro EM/ con i file che cita,
agli stessi percorsi relativi (Enzo, 17 ottobre 2026: «controlla che
EMStudio voglia una struttura definita per i media»). EMStudio cerca i file
a partire dalla cartella dell'em.json, nell'albero standard della libreria
(s3dgraphy.project_tree): EM/DosCo i documenti, EM/proxies un glb per
unità, RB il rilievo, SB la scena, RM i modelli."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tests.sync.test_em_media_import import GLB, SITO, _importa, progetto  # noqa: F401


def test_i_percorsi_dei_file_citati_dall_em_json():
    from modules.s3dgraphy import em_project
    doc = {"graphs": {"g": {"nodes": [
        {"id": "a", "node_type": "resource", "data": {"url": "proxies/SU002.glb"}},
        {"id": "b", "node_type": "document", "data": {"url": "DosCo/D.05 Relazione.pdf"}},
        {"id": "c", "node_type": "resource_file", "data": {"url": "../RB/colonna.glb"}},
        {"id": "d", "node_type": "resource", "data": {"url": "http://example.org/scheda"}},
        {"id": "e", "node_type": "resource", "data": {"url": "blend://../SB/Tempio.blend#Mesh/X"}},
        {"id": "f", "node_type": "resource", "data": {"url": "/assoluto/fuori.pdf"}},
        {"id": "g", "node_type": "resource", "data": {"url": "proxies/SU002.glb"}},
        {"id": "h", "node_type": "resource", "data": {"url": "https://bucket.example.org/SU009.glb",
                                                      "addresses": [{"locator": "proxies/SU009.glb"}]}},
        {"id": "i", "node_type": "extractor", "data": {"url": "D.07.05.jpg"}},
        {"id": "j", "node_type": "resource", "data": {"url": "onedrive://Dottorato/3DModels/TM015.obj"}}],
        "edges": []}}}
    # il .blend di un datablock è un file del progetto; il web e i percorsi assoluti no
    assert em_project.project_locators(doc) == [
        "proxies/SU002.glb", "DosCo/D.05 Relazione.pdf", "../RB/colonna.glb", "../SB/Tempio.blend",
        "proxies/SU009.glb", "D.07.05.jpg"]


def test_un_file_citato_col_solo_nome_va_in_dosco():
    """EMStudio inietta l'url dei documenti e degli estrattori dalla
    cartella DosCo (TempluMare: «D.07.05.jpg»); il risolutore della
    libreria cerca un nome nudo in EM/ e poi in EM/DosCo."""
    from modules.s3dgraphy import em_project
    assert em_project.project_path("D.07.05.jpg") == "DosCo/D.07.05.jpg"
    assert em_project.project_path("proxies/SU002.glb") == "proxies/SU002.glb"
    assert em_project.project_path("../RB/LOD0/colonna.obj") == "../RB/LOD0/colonna.obj"
    assert em_project.project_path("./DosCo\\D.05.pdf") == "DosCo/D.05.pdf"


def _esporta(progetto, tmp_path, **kw):  # noqa: F811
    from modules.s3dgraphy import em_project
    conn = "sqlite:///" + str(progetto["db"])
    return em_project.export_project(conn, SITO, str(tmp_path / "progetto"),
                                     work_dir=str(tmp_path / "lavoro"), **kw)


def _ricorda(progetto, cambia=None):  # noqa: F811
    from modules.s3dgraphy.sync.em_sources import remember_source
    em = progetto["em"]
    if cambia is not None:
        doc = json.loads(em.read_text(encoding="utf-8"))
        cambia({n["id"]: n for n in doc["graphs"]["g"]["nodes"]})
        em = progetto["tmp"] / "ricordato.em.json"
        em.write_text(json.dumps(doc), encoding="utf-8")
    remember_source(progetto["db"], SITO, str(em))


def test_il_progetto_ha_l_albero_standard_e_i_file_ai_loro_percorsi(progetto, tmp_path):  # noqa: F811
    _importa(progetto)
    _ricorda(progetto)
    esito = _esporta(progetto, tmp_path)
    dest = tmp_path / "progetto"
    em = Path(esito.path)
    assert em.parent == dest / "EM" and em.is_file()
    for cartella in ("EM/DosCo", "EM/proxies", "RB", "SB", "RM"):
        assert (dest / cartella).is_dir(), cartella
    assert (dest / "EM" / "proxies" / "SU002.glb").read_bytes() == GLB.read_bytes()
    assert (dest / "EM" / "DosCo" / "D.05 Relazione.pdf").is_file()
    assert (dest / "EM" / "DosCo" / "D.07.05.jpg").is_file()           # il nome nudo dell'estrattore
    assert (dest / "RB" / "colonna.glb").is_file()                     # ../RB/ accanto a EM/
    assert not (dest / "EM" / "D.05 Relazione.pdf").exists()           # niente doppione del documento
    # quello che il database non ha: il proxy che mancava già, il .mtl e il .blend non sono
    # media; gli elenchi dicono dove stanno i file nel progetto
    assert sorted(esito.missing) == ["EM/proxies/SU003.glb", "RB/colonna.mtl", "SB/Tempio.blend"]
    assert esito.bytes > 0 and len(esito.copied) == 4
    # il risolutore della libreria, quello di EMStudio, li trova dal progetto
    assert (esito.found, esito.resources) == (3, 6)
    urls = {str((n.get("data") or {}).get("url") or "")
            for g in json.loads(em.read_text(encoding="utf-8"))["graphs"].values() for n in g["nodes"]}
    assert "proxies/SU002.glb" in urls
    testo = esito.summary()
    assert "RB/" in testo and "SB/" in testo                           # i mancanti per cartella


def test_riesportare_non_ricopia_e_non_sovrascrive_quello_cambiato(progetto, tmp_path):  # noqa: F811
    _importa(progetto)
    _ricorda(progetto)
    primo = _esporta(progetto, tmp_path)
    dest = tmp_path / "progetto"
    (dest / "EM" / "proxies" / "SU002.glb").write_bytes(b"glTF cambiato in EMStudio")
    Path(primo.path).write_text(Path(primo.path).read_text(encoding="utf-8") + "\n", encoding="utf-8")
    di_nuovo = _esporta(progetto, tmp_path)
    assert di_nuovo.copied == []
    assert di_nuovo.kept == ["EM/proxies/SU002.glb"]
    assert (dest / "EM" / "proxies" / "SU002.glb").read_bytes() == b"glTF cambiato in EMStudio"
    assert sorted(di_nuovo.unchanged) == ["EM/DosCo/D.05 Relazione.pdf", "EM/DosCo/D.07.05.jpg",
                                          "RB/colonna.glb"]
    # l'em.json di prima, diverso, resta accanto come copia di sicurezza
    assert di_nuovo.backup and Path(di_nuovo.backup).read_text(encoding="utf-8").endswith("\n")
    assert Path(di_nuovo.path).is_file()


def test_lo_sha256_dell_em_json_si_controlla_sulla_copia(progetto, tmp_path):  # noqa: F811
    giusto = "sha256:" + hashlib.sha256(GLB.read_bytes()).hexdigest()

    def cambia(nodi):
        nodi["rp1"]["data"]["checksum"] = "sha256:" + "0" * 64            # non è quello del file
        nodi["rf1"]["data"]["checksum"] = giusto
    _importa(progetto)
    _ricorda(progetto, cambia)
    esito = _esporta(progetto, tmp_path)
    assert esito.mismatched == ["EM/proxies/SU002.glb"]


def test_col_disco_del_progetto_staccato_si_prende_la_copia_dello_stesso_tipo(progetto, tmp_path):  # noqa: F811
    """L'originale non si raggiunge più (il disco esterno staccato): il
    modello e il PDF si prendono dalla cartella delle ridotte, dove sono
    copiati tali e quali; la foto no, lì è ridotta in PNG e non è più il
    file citato."""
    _importa(progetto)
    _ricorda(progetto)
    progetto["radice"].rename(progetto["tmp"] / "staccato")
    esito = _esporta(progetto, tmp_path, resize_base=progetto["resize"])
    dest = tmp_path / "progetto"
    assert (dest / "EM" / "proxies" / "SU002.glb").read_bytes() == GLB.read_bytes()
    assert (dest / "EM" / "DosCo" / "D.05 Relazione.pdf").read_bytes() == b"%PDF-1.4 finto"
    assert "EM/DosCo/D.07.05.jpg" in esito.missing
    assert not (dest / "EM" / "DosCo" / "D.07.05.jpg").exists()


def test_la_cartella_del_progetto(tmp_path):
    """La cartella scelta è il progetto se è vuota o è già un progetto EM;
    altrimenti (la Scrivania) il progetto è una cartella nuova col nome del
    sito: l'albero non si sparge fra i file di un'altra cartella."""
    from modules.s3dgraphy import em_project
    vuota = tmp_path / "vuota"
    vuota.mkdir()
    (vuota / ".DS_Store").write_bytes(b"\0")                         # macOS la crea da sé
    assert em_project.project_root_for(str(vuota), "Temple") == str(vuota)
    progetto = tmp_path / "TempluMare"
    (progetto / "EM").mkdir(parents=True)
    (progetto / "README.md").write_text("x", encoding="utf-8")
    assert em_project.project_root_for(str(progetto), "Temple") == str(progetto)
    assert em_project.project_root_for(str(progetto / "EM"), "Temple") == str(progetto)
    scrivania = tmp_path / "Scrivania"
    scrivania.mkdir()
    (scrivania / "nota.txt").write_text("x", encoding="utf-8")
    assert em_project.project_root_for(str(scrivania), "Tempio media") == str(scrivania / "Tempio_media")


def test_la_voce_di_menu_esporta_il_progetto():
    import re
    plugin = (Path(__file__).resolve().parents[2] / "pyarchinitPlugin.py").read_text(encoding="utf-8")
    assert re.search(r'self\.actionEmProject = QAction\(\s*"Extended Matrix → Esporta progetto EM per EMStudio…"',
                     plugin)
    assert "self.actionEmProject.triggered.connect(self._run_em_project)" in plugin
    assert re.search(r'addPluginToMenu\(\s*"&pyArchInit - Archaeological GIS Tools",\s*self\.actionEmProject\)',
                     plugin)
    assert '"actionEmProject"' in plugin                                # tolta allo scarico
    corpo = plugin[plugin.index("    def _run_em_project(self):"):]
    corpo = corpo[:corpo.index("\n    def ", 10)]
    assert "em_project.project_root_for(" in corpo and "em_project.export_project(" in corpo
    assert "resize_base=" in corpo and "open_in_emstudio(" in corpo and "progress=" in corpo
