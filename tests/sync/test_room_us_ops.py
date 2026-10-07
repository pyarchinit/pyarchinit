"""L'adapter della stanza: righe di us_table → operazioni (C, piano 2026-10-07).

Puro: niente Qt, niente rete, niente DB. Il payload va DENTRO ``node`` (il
CRDT perde in silenzio un node_type al top level); gli id sono derivati con
stable_id, mai uuid4; i paradata non diventano unità della stanza.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest  # noqa: F401

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]


def test_unit_ids_are_stable_and_origin_bound():
    from modules.s3dgraphy.room.us_ops import unit_id
    a = unit_id("Scavo", "1", "12a")
    assert a == unit_id("Scavo", "1", "12a")          # deterministico
    assert a != unit_id("Scavo", "2", "12a")          # l'area identifica
    assert a != unit_id("Scavo", "1", "12")           # il testo conta ("12a" ≠ "12")


def test_a_plain_us_becomes_an_add_node_with_payload_inside_node():
    from modules.s3dgraphy.room.us_ops import ops_for_units
    made = ops_for_units([{"sito": "S", "area": "1", "us": "3",
                           "unita_tipo": "US",
                           "d_stratigrafica": "strato", "scavato": "Si"}])
    assert len(made.ops) == 1
    op = made.ops[0]
    assert op["op"] == "add_node" and "node" in op
    assert op["node"]["node_type"] == "US"
    assert op["node"]["name"] == "3"
    assert op["node"]["data"]["site"] == "S"
    assert op["node"]["data"]["origin"] == "pyarchinit"
    assert "node_type" not in op, "il tipo al top level viene PERSO dal CRDT"


def test_masonry_and_coating_travel_as_us_with_a_kind():
    # dev40: USM è una US con stratigraphic_kind='masonry'; i codici
    # localizzati (WSU...) idem. Il codice d'origine resta in source_code.
    from modules.s3dgraphy.room.us_ops import ops_for_units
    made = ops_for_units([
        {"sito": "S", "area": "1", "us": "4", "unita_tipo": "USM"},
        {"sito": "S", "area": "1", "us": "5", "unita_tipo": "WSU"},
        {"sito": "S", "area": "1", "us": "6", "unita_tipo": "USR"},
    ])
    kinds = {o["node"]["name"]: (o["node"]["node_type"],
                                 o["node"]["data"].get("stratigraphic_kind"),
                                 o["node"]["data"].get("source_code"))
             for o in made.ops}
    assert kinds["4"] == ("US", "masonry", "USM")
    assert kinds["5"] == ("US", "masonry", "WSU")
    assert kinds["6"] == ("US", "coating", "USR")


def test_virtual_units_keep_their_class_and_legacy_codes_remap():
    from modules.s3dgraphy.room.us_ops import ops_for_units
    made = ops_for_units([
        {"sito": "S", "area": "1", "us": "7", "unita_tipo": "USVs"},
        {"sito": "S", "area": "1", "us": "8", "unita_tipo": "USVA"},
    ])
    types = {o["node"]["name"]: o["node"]["node_type"] for o in made.ops}
    assert types == {"7": "USVs", "8": "USVs"}
    assert made.counts.get("units_remapped_USVA_to_USVs") == 1


def test_rows_that_cannot_be_nodes_are_reported_not_invented():
    from modules.s3dgraphy.room.us_ops import ops_for_units
    made = ops_for_units([
        {"sito": "", "area": "1", "us": "1"},              # senza sito
        {"sito": "S", "area": "1", "us": "9",
         "unita_tipo": "DOC"},                              # paradata: non US
    ])
    assert made.ops == []
    assert len(made.skipped) == 2
