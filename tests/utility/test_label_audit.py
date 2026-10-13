"""Chi mette le etichette in ettari? Non pyArchInit (cercato ovunque, 13
ottobre 2026): l'audit guarda i layer del progetto e le annotazioni e lo
dice in chiaro al caricamento della vista US. Parte pura."""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.label_audit import hectare_label_sources, looks_like_area  # noqa: E402


def test_riconosce_le_espressioni_in_ettari():
    assert looks_like_area("format_number($area / 10000, 2) || ' ha'")
    assert looks_like_area('round(area($geometry)/10000, 2)')
    assert looks_like_area("to_string($area) || ' m²'")
    assert not looks_like_area('"us"')
    assert not looks_like_area("'US ' || \"us_s\"")


def test_elenca_layer_e_annotazioni_che_scrivono_aree():
    layers = [("US view", True, "format_number($area/10000, 2) || ' ha'"),
              ("US view_2", True, '"us"'),
              ("vecchio", False, "$area"),                       # etichette spente: non conta
              ("quote", True, None)]
    esito = hectare_label_sources(layers, annotation_texts=["0,00 ha", "nota", "1,20 ha"])
    assert esito == {"layers": [("US view", "format_number($area/10000, 2) || ' ha'")], "annotations": 2}


def test_senza_niente_da_dire_torna_vuoto():
    assert hectare_label_sources([("a", True, '"us"')], annotation_texts=[]) == {"layers": [], "annotations": 0}
