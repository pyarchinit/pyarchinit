"""room_sync and the ingestor's em.json fixes, measured without a node.

What the end-to-end run on the dev-stack found (26 Nov 2026), held here:
a graph read from an em.json keeps row fields in ``node.data`` (the
ingestor read only ``attributes``: an Extractor «400» came back as
«1.Extractor400»); the node description IS d_stratigrafica; the GIS
footprint chain is not a row; a rapporti field written with area and site
is the same relation; the contribution ignores map artefacts and the
``lang`` the node adds.
"""
from __future__ import annotations

from types import SimpleNamespace

from modules.s3dgraphy.sync import graph_ingestor as GI
from modules.stratigraph import room_sync as RS


class DocumentNode(SimpleNamespace):
    """type(n).__name__ is what the footprint rule looks at."""


def _node(node_id, name="", description="", data=None, cls=SimpleNamespace, **extra):
    return cls(node_id=node_id, name=name, description=description, data=data or {},
               attributes={}, **extra)


def _edge(src, kind, tgt):
    return SimpleNamespace(edge_source=src, edge_type=kind, edge_target=tgt)


def test_row_fields_come_from_data_and_description_is_d_stratigrafica():
    ext = _node("e1", "1.Extractor400", data={"us": "400", "node_uuid": "e1", "area": "1"})
    us5 = _node("u5", "1.US5", "Rivista in EMStudio",
                data={"us": "5", "node_uuid": "u5", "d_stratigrafica": "Struttura in muratura"})
    born_elsewhere = _node("x", "Nuova", "Da EMStudio", data={"lang": "it"})
    graph = SimpleNamespace(nodes=[ext, us5, born_elsewhere], edges=[])
    GI.hydrate_row_fields_from_data(graph)
    assert ext.attributes["us"] == "400"                   # not «1.Extractor400»
    assert us5.attributes["d_stratigrafica"] == "Rivista in EMStudio"
    assert born_elsewhere.attributes == {}                 # EMStudio's own rules apply


def test_the_gis_footprint_chain_is_not_a_row():
    prop = _node("p", "footprint", property_type="footprint")
    ext = _node("x", "D.footprint.layer", data={"extractor_type": "gis_analysis"})
    plan = _node("d", "pyArchInit plan · layer", cls=DocumentNode)
    a_document = _node("d2", "D.01", cls=DocumentNode, data={"us": "4001", "node_uuid": "d2"})
    graph = SimpleNamespace(nodes=[prop, ext, plan, a_document],
                            edges=[_edge("x", "extracted_from", "d"), _edge("x", "has_property", "p"),
                                   _edge("x", "extracted_from", "d2")])
    assert GI.footprint_chain_ids(graph) == {"p", "x", "d"}  # a row-born document never


def test_rapporti_that_differ_only_in_format_are_not_conflicts():
    conflict = lambda uuid, a, b: SimpleNamespace(node_uuid=uuid, field="rapporti", db_value=a, graph_value=b)
    result = SimpleNamespace(conflicts=[
        conflict("a", "[['Copre', '2']]", "[['Copre', '2', '1', 'X']]"),
        conflict("b", "[['<', '500'], ['Copre', '3']]", "[['Copre', '3', '1', 'X']]"),
    ])
    out = RS.classify(result, {"a": ("1", "US"), "b": ("12", "USM")})
    assert out["format_only"] == 1
    assert out["real"] == [{"field": "rapporti", "us": "12", "unita_tipo": "USM",
                            "only_local": [("<", "500")], "only_room": []}]


def test_the_contribution_ignores_map_artefacts_and_the_lang_the_node_adds():
    from s3dgraphy.contract import Delta
    delta = Delta(nodes=[{"id": "new-us"}, {"id": "plan"}],
                  edges=[{"id": "e1", "source": "new-us", "target": "u5", "edge_type": "overlies"},
                         {"id": "e2", "source": "plan", "target": "res", "edge_type": "has_linked_resource"}])
    delta.update_field("u1", "data.lang", remove=True)             # the node's «und»
    delta.update_field("u5", "data.rapporti", "[['Copre', '2']]")   # relations travel as edges
    delta.update_field("u5", "description", "Rivista")             # a real difference
    delta.remove_node("plan-old")
    out = RS._without_noise(delta, {"plan", "res", "plan-old"})
    assert [n["id"] for n in out.nodes] == ["new-us"]
    assert [e["id"] for e in out.edges] == ["e1"]
    assert out.ops == [{"op": "update_field", "node_id": "u5", "field": "description", "value": "Rivista"}]
