"""La mappa della narrativa con i disegni ricavati dal 3D: le piante, anche
delle unità murarie, dal layer delle piante; mai i prospetti ricavati, che
stanno in coordinate del disegno (spec 2026-10-18, D11)."""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

pytest.importorskip("s3dgraphy")


def test_la_mappa_usa_le_piante_e_non_i_prospetti_anche_per_le_usm(tmp_path):
    from modules.s3dgraphy import em_drawings as drw
    from modules.s3dgraphy import em_narrative_map as nm
    from modules.s3dgraphy.sync import em_drawings_import as edi
    from tests.sync.test_em_drawings_import import SITO, make_project
    p = make_project(tmp_path)
    con = sqlite3.connect(p["db"])
    con.execute("UPDATE us_table SET unita_tipo = 'USM' WHERE sito = ? AND us = '001'", (SITO,))
    con.commit()
    con.close()
    unita = edi.plan_units(p["grafo"], str(p["em"]), db=p["eng"], sito=SITO)
    geo = drw.georef_of(p["grafo"])
    scelta = edi.default_choice(unita, geo)
    edi.run_drawings(p["eng"], p["grafo"], SITO, str(p["em"]), units=unita, choice=scelta,
                     georef=geo, decision=edi.crs_decision(p["eng"], geo, scelta), lang="it")
    # le unità come le vede la narrativa (data con sito, area, numero, tipo)
    from s3dgraphy.graph import Graph
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    g = Graph(graph_id=SITO)
    for uid, us, tipo in (("u1", "001", "USM"), ("u2", "002", "US")):
        n = StratigraphicUnit(uid, "1.%s%s" % (tipo, us))
        n.data = {"sito": SITO, "area": "1", "us": us, "unita_tipo": tipo}
        g.add_node(n)
    meta = nm.units_meta(g)
    tipi = {k: v["unita_tipo"] for k, v in meta.items()}
    assert tipi == {"u1": "USM", "u2": "US"}
    disegni = nm.drawings_from_db("sqlite:///%s" % p["db"], SITO, meta, "it")
    per_unita = {}
    for d in disegni:
        per_unita.setdefault(d.unit_id, []).append(d)
    assert set(per_unita) == set(tipi)
    for uid in tipi:
        xs = [x for d in per_unita[uid] for anello in d.rings for x, _y in anello]
        assert min(xs) > 327000.0, tipi[uid]       # sulla mappa: niente prospetti vicino a 0
