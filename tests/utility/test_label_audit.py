"""Chi mette le etichette in ettari? Non pyArchInit (cercato ovunque, 13
ottobre 2026): l'audit guarda i layer del progetto e le annotazioni e lo
dice in chiaro al caricamento della vista US. Parte pura."""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.label_audit import describe, hectare_label_sources, looks_like_area  # noqa: E402


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
    assert esito == {"layers": [("US view", "format_number($area/10000, 2) || ' ha'")], "preview": [], "annotations": 2}


def test_senza_niente_da_dire_torna_vuoto():
    assert hectare_label_sources([("a", True, '"us"')], annotation_texts=[]) == {"layers": [], "preview": [], "annotations": 0}


def test_la_descrizione_nomina_ogni_layer_con_la_sua_espressione():
    esito = {"layers": [("US view", "$area || ' ha'"), ("vecchio", "area($geometry)")], "annotations": 0}
    frasi = describe(esito, "it")
    assert len(frasi) == 2 and "«US view»" in frasi[0] and "$area || ' ha'" in frasi[0] and "«vecchio»" in frasi[1]


def test_i_layer_della_map_preview_fuori_dal_pannello_si_riconoscono():
    """I due «pyarchinit_us_view» che l'audit ha trovato da Enzo (13 ottobre
    2026) sono i layer della Map preview, registrati nel progetto fuori dal
    pannello: non si possono spegnere a mano, li toglie il plugin."""
    esito = hectare_label_sources([("pyarchinit_us_view", True, "$area", False), ("US view", True, "$area", True)])
    assert esito["layers"] == [("pyarchinit_us_view", "$area"), ("US view", "$area")]
    assert esito["preview"] == ["pyarchinit_us_view"]
    frasi = describe(esito, "it")
    assert any("Map preview" in f and "toglie" in f for f in frasi)
