"""La finestra «Export Extended Matrix» dice la verità (2026-10-08).

Chiesto da Enzo guardando la finestra: il formato DOT va bene, ma il
«JSON Format (s3dgraphy native)» non è quello che EMStudio apre, l'import
parla ancora di GraphML, e delle tre «Processing Options» non si sa quali
facciano qualcosa.

I test non costruiscono la finestra (vuole QGIS): leggono il sorgente per
le promesse dell'interfaccia e chiamano le funzioni pure per il resto.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_EXT_LIBS = str(_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)

BRIDGE = _ROOT / "modules" / "s3dgraphy" / "s3dgraphy_dot_bridge.py"


def _source():
    return BRIDGE.read_text(encoding="utf-8")


def test_the_dialog_offers_emjson_not_the_internal_dump():
    """«JSON Format (s3dgraphy native)» era un dump interno: EMStudio non
    lo apre. Il formato di lavoro dell'Extended Matrix è em.json (A4)."""
    source = _source()
    assert "JSON Format (s3dgraphy native)" not in source
    assert "em.json" in source


def test_no_switch_in_the_dialog_is_a_decoration():
    """Ogni casella costruita in setupUI deve essere letta da qualche
    parte: «Generate yEd auto-layout hints» e «Apply period-based
    coloring» parlavano al writer GraphML, ritirato in A4, e
    «Validate stratigraphic sequence» non veniva mai letta."""
    source = _source()
    costruite = set(re.findall(r"self\.(cb_\w+)\s*=\s*QCheckBox", source))
    lette = set(re.findall(r"self\.(cb_\w+)\.isChecked\(\)", source))
    assert costruite - lette == set(), sorted(costruite - lette)


def test_the_retired_graphml_export_left_no_dead_branches():
    """A4 ha ritirato l'export GraphML: i rami che ne stampavano l'esito
    e il blocco swimlane che ci si agganciava non possono più scattare."""
    source = _source()
    assert "graphml_status" not in source
    assert "'graphml' in formats" not in source


def test_the_export_asks_em_export_for_the_file(tmp_path, monkeypatch):
    """Il file em.json della finestra è quello del menu Extended Matrix:
    stesso proiettore, quindi stesso filtro del sito e stessa simbologia."""
    from modules.s3dgraphy import s3dgraphy_dot_bridge as bridge_mod

    chiamate = []

    def finto_export_site(conn, sito, out_dir):
        chiamate.append((conn, sito, str(out_dir)))
        path = Path(out_dir) / "Sito.em.json"
        path.write_text("{}", encoding="utf-8")
        return str(path), 7, 5, ["un avviso"]

    monkeypatch.setattr(bridge_mod, "export_site", finto_export_site)
    bridge = bridge_mod.S3DGraphyDotBridge()
    monkeypatch.setattr(bridge, "_connection_url", lambda: "sqlite:///x.db")
    monkeypatch.setattr(bridge.s3d_integration, "import_from_pyarchinit",
                        lambda *a, **k: True)
    monkeypatch.setattr(bridge.s3d_integration,
                        "validate_stratigraphic_sequence", lambda: [])

    out = bridge.export_integrated_matrix(
        "Sito", None, str(tmp_path), ["emjson"])
    assert chiamate == [("sqlite:///x.db", "Sito", str(tmp_path))]
    assert out["emjson"].endswith(".em.json")
    assert out["emjson_counts"] == (7, 5, ["un avviso"])


def test_an_export_failure_becomes_a_sentence(tmp_path, monkeypatch):
    """Un guasto dell'export non deve uccidere gli altri formati né
    arrivare all'utente come traccia di stack."""
    from modules.s3dgraphy import em_export
    from modules.s3dgraphy import s3dgraphy_dot_bridge as bridge_mod

    def esplode(conn, sito, out_dir):
        raise em_export.EmExportError("il sito non ha unità")

    monkeypatch.setattr(bridge_mod, "export_site", esplode)
    bridge = bridge_mod.S3DGraphyDotBridge()
    monkeypatch.setattr(bridge, "_connection_url", lambda: "sqlite:///x.db")
    monkeypatch.setattr(bridge.s3d_integration, "import_from_pyarchinit",
                        lambda *a, **k: True)
    monkeypatch.setattr(bridge.s3d_integration,
                        "validate_stratigraphic_sequence", lambda: [])

    out = bridge.export_integrated_matrix(
        "Sito", None, str(tmp_path), ["emjson"])
    assert "emjson" not in out
    assert out["emjson_error"] == "il sito non ha unità"


def test_validation_can_actually_be_turned_off(tmp_path, monkeypatch):
    from modules.s3dgraphy import s3dgraphy_dot_bridge as bridge_mod

    chiamate = []
    bridge = bridge_mod.S3DGraphyDotBridge()
    monkeypatch.setattr(bridge.s3d_integration, "import_from_pyarchinit",
                        lambda *a, **k: True)
    monkeypatch.setattr(bridge.s3d_integration,
                        "validate_stratigraphic_sequence",
                        lambda: chiamate.append(1) or [])
    bridge.export_integrated_matrix("Sito", None, str(tmp_path), [],
                                    validate=False)
    assert chiamate == []
    bridge.export_integrated_matrix("Sito", None, str(tmp_path), [],
                                    validate=True)
    assert chiamate == [1]


def test_an_unknown_file_says_what_it_wanted(tmp_path):
    from modules.s3dgraphy.s3dgraphy_dot_bridge import read_graph_for_import

    bad = tmp_path / "appunti.txt"
    bad.write_text("ciao", encoding="utf-8")
    with pytest.raises(ValueError, match="em.json"):
        read_graph_for_import(bad)


def test_what_the_dialog_exports_the_dialog_can_read_back(tmp_path,
                                                        monkeypatch):
    """em.json di andata e ritorno: quello che esce dalla finestra deve
    poterci rientrare, unità virtuali comprese."""
    import os
    import shutil

    from modules.s3dgraphy.em_export import export_site
    from modules.s3dgraphy.s3dgraphy_dot_bridge import read_graph_for_import

    folder = tmp_path / "pyarchinit_DB_folder"
    folder.mkdir()
    resources = _ROOT / "resources" / "dbfiles"
    shutil.copy(resources / "config.cfg", folder / "config.cfg")
    shutil.copy(resources / "pyarchinit_db.sqlite", folder / "db.sqlite")
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path))

    path, _, _, _ = export_site("sqlite:///%s" % (folder / "db.sqlite"),
                                "Scavo archeologico", str(tmp_path / "out"))
    graph, _warnings = read_graph_for_import(path)
    tipi = {getattr(n, "node_type", None) for n in graph.nodes}
    assert "USVs" in tipi, sorted(t for t in tipi if t)


def test_the_room_commands_are_the_menu_ones():
    """Niente logica gemella nella finestra: gli stessi slot del menu."""
    source = _source()
    assert "_run_room_delivery" in source
    assert "_open_rooms_door" in source


def test_the_dialog_opens_what_it_just_exported(tmp_path, monkeypatch):
    from modules.s3dgraphy import s3dgraphy_dot_bridge as bridge_mod

    aperti = []
    monkeypatch.setattr(bridge_mod, "open_in_emstudio",
                        lambda p: aperti.append(str(p)) or True)
    target = tmp_path / "x.em.json"
    target.write_text("{}", encoding="utf-8")
    assert bridge_mod.open_exported_emjson({"emjson": str(target)}) is True
    assert aperti == [str(target)]
    assert bridge_mod.open_exported_emjson({}) is False


def test_the_window_stays_open_after_the_export():
    """Visto nel video di Enzo: la finestra si chiudeva da sola appena
    finito l'export, quindi «Apri in EMStudio» — che si accende proprio
    in quel momento — non era mai premibile. L'export non è l'ultima cosa
    che si fa in questa finestra: dopo si apre il file, si consegna alla
    stanza, si rifà con altri formati."""
    import ast

    tree = ast.parse(_source())
    for nodo in ast.walk(tree):
        if isinstance(nodo, ast.FunctionDef) and nodo.name == "on_export":
            chiuse = [c for c in ast.walk(nodo)
                      if isinstance(c, ast.Call)
                      and isinstance(c.func, ast.Attribute)
                      and c.func.attr in ("accept", "close")]
            assert not chiuse, "on_export chiude la finestra"
            return
    raise AssertionError("on_export non trovata")
