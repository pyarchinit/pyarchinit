"""Il pannello delle viste della narrativa (17 ottobre 2026): i link delle
menzioni e dei capitoli anche senza mappa, le schede quando le viste sono
due, una selezione sola (PYA_SEL) per la mappa e la scena 3D."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_ROOT), str(_ROOT / "ext_libs")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from modules.s3dgraphy import em_narrative_views as nv  # noqa: E402

_PAGINA = ('<html lang="it"><head><meta charset="utf-8"><style>body{}</style></head><body>\n'
           '<h1>Tempio</h1>\n<h2>Virtual Activity 1</h2><p>La fondazione <em class="em-mention">SU002</em> '
           'e <em class="em-mention">SU003</em>.</p>'
           '<h2>II A.D.</h2><p>Poi <em class="em-mention">SU002</em>.</p>'
           '<section class="em-sources"><h2>Fonti</h2><ul></ul></section></body></html>')
_CAPITOLI = [{"title": "Virtual Activity 1", "epoch": None, "units": ["u1", "u2"]},
             {"title": "II A.D.", "epoch": "ep1", "units": ["u1"]}]
_META = {"u1": {"name": "SU002", "epochs": ["ep1"]}, "u2": {"name": "SU003", "epochs": ["ep1"]}}


def _vista(key, label):
    return nv.View(key=key, label=label, panel='<div id="pannello-%s"></div>' % key,
                   css=".v-%s {}" % key, script="<script>/* %s */</script>" % key)


def test_senza_viste_la_pagina_resta_com_e():
    assert nv.inject_views(_PAGINA, [], _CAPITOLI, _META, lang="it") == _PAGINA


def test_con_la_sola_scena_3d_i_nomi_diventano_link():
    fuori = nv.inject_views(_PAGINA, [_vista("3d", "3D")], _CAPITOLI, _META, lang="it")
    assert '<a class="em-mention pya-u" href="#pya-map" data-u="u1" data-e="ep1">SU002</a>' in fuori
    # un capitolo ancorato a un'attività: niente epoca, ma le sue unità
    assert '<h2 id="pya-cap-0" class="pya-cap" data-e="" data-units="u1 u2">Virtual Activity 1</h2>' in fuori
    assert '<nav class="pya-tabs">' not in fuori                     # una vista sola: niente schede
    assert '<div class="pya-view" data-pya-view="3d"><div id="pannello-3d"></div></div>' in fuori
    assert fuori.count("var PYA_SEL = ") == 1 and "/* 3d */" in fuori and ".v-3d {}" in fuori
    assert '<aside class="pya-map" id="pya-map">' in fuori and "<h2>Fonti</h2>" in fuori


def test_con_due_viste_le_schede_e_la_prima_aperta():
    fuori = nv.inject_views(_PAGINA, [_vista("map", "Mappa"), _vista("3d", "3D")], _CAPITOLI, _META,
                            lang="it")
    assert ('<nav class="pya-tabs"><a href="#pya-map" data-pya-tab="map" class="on">Mappa</a>'
            '<a href="#pya-map" data-pya-tab="3d">3D</a></nav>') in fuori
    assert '<div class="pya-view" data-pya-view="map">' in fuori
    assert '<div class="pya-view" data-pya-view="3d" hidden>' in fuori
    assert fuori.index("var PYA_SEL = ") < fuori.index("/* map */") < fuori.index("/* 3d */")


def test_la_selezione_comune_passa_epoca_unita_e_gruppo():
    js = nv._JS
    assert "PYA_SEL.select = function (e, u, g)" in js and "PYA_SEL.add = function (fn)" in js
    assert "data-units" in js and "'pya:tab'" in js and "closest('a.pya-u')" in js


@pytest.mark.skipif(shutil.which("node") is None, reason="node non c'è")
def test_lo_script_comune_si_legge(tmp_path):
    f = tmp_path / "sel.js"
    f.write_text("var PYA_SEL = {units: {}, firstEpoch: {}};" + nv._JS, encoding="utf-8")
    subprocess.run(["node", "--check", str(f)], check=True)
