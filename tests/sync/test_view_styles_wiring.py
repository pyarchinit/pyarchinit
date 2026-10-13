"""Da dove si apre «Stili delle viste» (Task 6): la voce di menu del
plugin (anche nel menu del layer), il bottone «Stile…» della scheda US,
e la funzione unica `open_view_styles` che tutti e due chiamano."""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

PLUGIN = _ROOT / "pyarchinitPlugin.py"
SCHEDA = _ROOT / "tabs" / "US_USM.py"


def _corpo(percorso: Path, nome: str) -> str:
    sorgente = percorso.read_text(encoding="utf-8")
    albero = ast.parse(sorgente)
    for n in ast.walk(albero):
        if isinstance(n, ast.FunctionDef) and n.name == nome:
            return ast.get_source_segment(sorgente, n)
    raise AssertionError(nome)


def test_il_menu_del_plugin_ha_la_voce_e_la_toglie_allo_scarico():
    sorgente = PLUGIN.read_text(encoding="utf-8")
    assert re.search(r'self\.actionViewStyles = QAction\(\s*"Stili delle viste…"', sorgente)
    assert "self.actionViewStyles.triggered.connect(self._run_view_styles)" in sorgente
    assert re.search(r"addPluginToMenu\(\s*\"&pyArchInit - Archaeological GIS Tools\",\s*self\.actionViewStyles\)", sorgente)
    assert "addCustomActionForLayerType(self.actionViewStyles" in sorgente      # anche nel menu del layer
    assert '"actionViewStyles"' in sorgente                                      # nell'elenco di chi si toglie
    assert "removeCustomActionForLayerType(self.actionViewStyles)" in sorgente
    corpo = _corpo(PLUGIN, "_run_view_styles")
    assert "open_view_styles(" in corpo and "activeLayer()" in corpo


def test_la_scheda_us_ha_il_bottone_stile_accanto_a_quello_dei_layer():
    sorgente = SCHEDA.read_text(encoding="utf-8")
    assert "self.pushButton_stile = QPushButton(" in sorgente
    assert "indexOf(self.pushButton_showLayer)" in sorgente
    corpo = _corpo(SCHEDA, "_apri_stili_delle_viste")
    assert "open_view_styles(" in corpo and "pyarchinit_us_view" in corpo
