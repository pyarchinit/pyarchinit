"""Il pannello della matrice dentro QGIS (2026-10-08).

Come per il pannello della stanza: nessun widget istanziato: si leggono
le promesse nel sorgente e si prova la parte pura.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

PANEL = _ROOT / "modules" / "s3dgraphy" / "em_matrix_panel.py"
PLUGIN = _ROOT / "pyarchinitPlugin.py"
BRIDGE = _ROOT / "modules" / "s3dgraphy" / "s3dgraphy_dot_bridge.py"


def test_one_panel_per_session_and_it_closes_with_the_plugin():
    """La lezione della 5.13.29: un dock che sopravvive al plugin lascia
    voci doppie al ricaricamento."""
    src = PANEL.read_text(encoding="utf-8")
    assert "PANEL_OBJECT_NAME" in src and "findChild" in src
    assert "em_matrix_panel.close_panel" in PLUGIN.read_text(encoding="utf-8")


def test_the_menu_entry_exists_and_is_removed_on_unload():
    plugin = PLUGIN.read_text(encoding="utf-8")
    assert "actionEmMatrixView" in plugin
    assert '"actionEmMatrixView"' in plugin          # anche nella tupla di unload


def test_the_panel_never_raises_for_a_file_it_cannot_read(tmp_path):
    from modules.s3dgraphy.em_matrix_panel import describe_failure

    rotto = tmp_path / "rotto.em.json"
    rotto.write_text("{non è json", encoding="utf-8")
    messaggio = describe_failure(rotto)
    assert messaggio and "em.json" in messaggio

    assente = tmp_path / "manca.em.json"
    assert describe_failure(assente)


def test_a_good_file_has_nothing_to_complain_about(tmp_path):
    import json

    from modules.s3dgraphy.em_matrix_panel import describe_failure

    buono = tmp_path / "buono.em.json"
    buono.write_text(json.dumps({"graphs": {"S": {"nodes": [], "edges": []}}}),
                     encoding="utf-8")
    assert describe_failure(buono) is None


def test_the_panel_speaks_the_counts_it_shows(tmp_path):
    import json

    from modules.s3dgraphy.em_matrix_panel import summary_line

    percorso = tmp_path / "x.em.json"
    percorso.write_text(json.dumps({"graphs": {"S": {
        "nodes": [
            {"id": "u1", "name": "1.US1", "node_type": "US",
             "data": {"us": "1"}},
            {"id": "e1", "name": "XV secolo", "node_type": "EpochNode",
             "data": {"start_time": 1451, "end_time": 1499}}],
        "edges": [{"source": "u1", "target": "e1",
                   "type": "has_first_epoch"}]}}}), encoding="utf-8")
    riga = summary_line(percorso)
    assert "1" in riga and "unità" in riga and "epoc" in riga


def test_the_export_window_can_show_the_matrix():
    src = BRIDGE.read_text(encoding="utf-8")
    assert "Vedi la matrice" in src
    assert "em_matrix_panel" in src


def test_the_panel_does_not_need_a_web_engine():
    import ast

    moduli = set()
    for nodo in ast.walk(ast.parse(PANEL.read_text(encoding="utf-8"))):
        if isinstance(nodo, ast.Import):
            moduli |= {a.name for a in nodo.names}
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            moduli.add(nodo.module)
    assert not [m for m in moduli if "WebEngine" in m or "WebKit" in m], moduli


def test_a_second_site_replaces_the_first_in_the_details_pane():
    """Il pannello si riusa: la scheda deve seguire il sito aperto adesso,
    non quello di prima. La chiusura che mostra i dati è agganciata una
    volta sola, alla creazione del dock, quindi la tabella delle unità non
    può viverle dentro."""
    from modules.s3dgraphy import em_matrix_panel as panel
    from modules.utility.em_matrix_model import Unit

    panel.remember_units([Unit("a", "1.US1", "US", None,
                               data={"d_stratigrafica": "strato di crollo"})])
    assert "1.US1" in panel.details_for("a")
    assert "strato di crollo" in panel.details_for("a")

    panel.remember_units([Unit("b", "2.US9", "US", None)])
    assert "2.US9" in panel.details_for("b")
    assert panel.details_for("a") == panel.details_for("sconosciuto")


def test_the_details_pane_says_something_when_nothing_is_chosen():
    from modules.s3dgraphy import em_matrix_panel as panel

    panel.remember_units([])
    testo = panel.details_for("qualunque")
    assert testo and "unità" in testo.lower()


def test_the_matrix_gets_most_of_the_room_not_the_record():
    """Visto nello screenshot: senza misure esplicite il divisore dava
    due terzi alla scheda e schiacciava la matrice in una colonnina. La
    matrice è il motivo per cui il pannello esiste."""
    src = PANEL.read_text(encoding="utf-8")
    assert "setSizes(" in src
    assert "setMaximumWidth" in src
