"""L'importazione di un em.json si apre anche con il database vuoto
(Enzo, 16 ottobre 2026: «ho creato un sito "test" prima per poter
importare, dovrei riuscire anche con db vuoto»): la finestra stava solo
dietro il bottone di esportazione della scheda US, che senza sito si
rifiutava. Ora c'è la voce di menu, la scheda US apre la finestra
sull'importazione anche senza sito, i periodi si creano per default, il
nome del sito si propone dal file e il riepilogo dice cosa diventa
scheda e cosa no."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(PLUGIN_ROOT), str(PLUGIN_ROOT / "ext_libs")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

PLUGIN = (PLUGIN_ROOT / "pyarchinitPlugin.py").read_text(encoding="utf-8")
BRIDGE = (PLUGIN_ROOT / "modules" / "s3dgraphy" / "s3dgraphy_dot_bridge.py").read_text(encoding="utf-8")
SCHEDA_US = (PLUGIN_ROOT / "tabs" / "US_USM.py").read_text(encoding="utf-8")


def test_la_voce_di_menu_apre_l_importazione():
    assert re.search(r'self\.actionEmImport = QAction\(\s*"Extended Matrix → Importa em\.json…"', PLUGIN)
    assert "self.actionEmImport.triggered.connect(self._run_em_import)" in PLUGIN
    assert re.search(r'addPluginToMenu\(\s*"&pyArchInit - Archaeological GIS Tools",\s*self\.actionEmImport\)', PLUGIN)
    assert '"actionEmImport"' in PLUGIN                      # tolta allo scarico
    corpo = PLUGIN[PLUGIN.index("    def _run_em_import(self):"):]
    corpo = corpo[:corpo.index("\n    def ", 10)]
    assert "S3DGraphyExportDialog(" in corpo and ".show_import_tab()" in corpo


def test_la_scheda_us_senza_sito_apre_l_importazione():
    corpo = SCHEDA_US[SCHEDA_US.index("    def on_pushButton_export_extended_matrix_integrated(self):"):]
    corpo = corpo[:corpo.index("\n    def ", 10)]
    assert "Please select a site before exporting" not in corpo
    assert ".show_import_tab()" in corpo


def test_i_periodi_si_creano_per_default_e_l_export_vuole_un_sito():
    assert re.search(r"self\.cb_create_epochs\.setChecked\(True\)", BRIDGE)
    corpo = BRIDGE[BRIDGE.index("        def on_export(self):"):]
    corpo = corpo[:corpo.index("\n        def ", 10)]
    assert corpo.index("if not self.site") < corpo.index("getExistingDirectory")


def test_il_nome_del_sito_si_propone_dal_file(tmp_path):
    from modules.s3dgraphy.s3dgraphy_dot_bridge import suggested_site_name
    f = tmp_path / "TempluMare_v3.2.em.json"
    f.write_text(json.dumps({"active_graph_id": "g", "graphs": {"g": {"name": {"default": "Temple"}, "nodes": [], "edges": []}}}), encoding="utf-8")
    assert suggested_site_name(str(f)) == "Temple"
    f.write_text(json.dumps({"graphs": {"g": {"name": "", "nodes": [], "edges": []}}}), encoding="utf-8")
    assert suggested_site_name(str(f)) == "TempluMare_v3.2"
    assert suggested_site_name(str(tmp_path / "manca.em.json")) == "manca"


def test_il_riepilogo_dice_cosa_diventa_scheda():
    pytest.importorskip("s3dgraphy")
    from collections import Counter
    from modules.s3dgraphy.sync.em_native_import import summary_text
    testo = summary_text(Counter({"property": 360, "US": 11}), Counter({"resource": 485, "EpochNode": 3}))
    assert "371 schede" in testo and "property 360" in testo and "US 11" in testo
    assert "488 nodi non sono schede" in testo and "resource 485" in testo


def test_la_finestra_importa_anche_i_media():
    assert re.search(r'self\.cb_import_media = QCheckBox\(\s*"Importa anche i media citati', BRIDGE)
    assert "self.cb_import_media.setChecked(True)" in BRIDGE
    corpo = BRIDGE[BRIDGE.index("        def _on_import_apply(self):"):]
    corpo = corpo[:corpo.index("\n        def ", 10)]
    assert "self.cb_import_media.isChecked()" in corpo and "self._import_media(graph, target_sito)" in corpo
    assert corpo.index("populate_list(") < corpo.index("self._import_media(")
    media = BRIDGE[BRIDGE.index("        def _import_media(self, graph, target_sito):"):]
    media = media[:media.index("\n        def ", 10)]
    assert "import_emjson_media(" in media and "default_media_dest(" in media
