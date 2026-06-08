"""Datamodel-driven paradata edge-type resolution.

A pyArchInit→GraphML export stores virtual/paradata links as the EM shorthand
``>> / <<`` (= ``generic_connection``). The projector then refines each
generic edge into the specific EM edge type implied by the node classes at its
ends, per the s3dgraphy connection data model. These tests pin that mapping
(and the rule that Combiner/Extractor never connect to a plain US/USM).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from modules.s3dgraphy.sync.paradata_edge_resolver import (  # noqa: E402
    resolve_edge_type, refine_generic_connections, _class_names,
)


def _names(*class_names):
    """Build an MRO-like class-name set (always includes the Node base)."""
    return frozenset(set(class_names) | {"Node"})


# node class-name sets as the projector would see them (MRO-derived)
DOC = _names("DocumentNode", "ParadataNode")
EXTR = _names("ExtractorNode", "ParadataNode")
COMB = _names("CombinerNode", "ParadataNode")
PROP = _names("PropertyNode", "ParadataNode")
US = _names("StratigraphicUnit", "StratigraphicNode")          # real US
USV = _names("StructuralVirtualStratigraphicUnit", "StratigraphicNode")
SF = _names("SpecialFindUnit", "StratigraphicNode")
VSF = _names("VirtualSpecialFindUnit", "StratigraphicNode")


@pytest.mark.parametrize("src,tgt,expected", [
    (EXTR, DOC, ("extracted_from", False)),    # Extractor -> Document
    (COMB, EXTR, ("combines", False)),         # Combiner  -> Extractor
    (US,  PROP, ("has_property", False)),       # Strat -> Property
    (DOC, PROP, ("has_property", False)),       # Document -> Property
    (US,  DOC, ("has_documentation", False)),   # Strat -> Document
    (USV, DOC, ("has_documentation", False)),   # USV  -> Document
    (SF,  US,  ("is_part_of", False)),          # SpecialFind -> US
])
def test_forward_paradata_edges(src, tgt, expected):
    assert resolve_edge_type(src, tgt) == expected


@pytest.mark.parametrize("src,tgt,expected_type", [
    (PROP, US, "has_property"),         # property >> USV  => swap to USV has_property prop
    (DOC, USV, "has_documentation"),    # DOC >> USV       => swap to USV has_documentation DOC
    (EXTR, PROP, "has_data_provenance"),# Extractor >> property => swap to property has_data_provenance extractor
])
def test_reverse_direction_swaps(src, tgt, expected_type):
    res = resolve_edge_type(src, tgt)
    assert res is not None and res[0] == expected_type and res[1] is True


@pytest.mark.parametrize("src,tgt", [
    (EXTR, US), (COMB, US), (EXTR, USV), (COMB, USV),
])
def test_combiner_extractor_never_link_stratigraphic(src, tgt):
    # No datamodel rule allows Extractor/Combiner <-> a stratigraphic unit:
    # such edges must stay generic_connection (resolver returns None).
    assert resolve_edge_type(src, tgt) is None


class _Edge:
    def __init__(self, eid, s, t, et):
        self.edge_id, self.edge_source, self.edge_target, self.edge_type = eid, s, t, et


class _Graph:
    def __init__(self, nodes, edges):
        self.nodes, self.edges = nodes, edges


def _real_node(node_id, modname, clsname):
    """Instantiate a real s3dgraphy node so _class_names() reflects true MRO."""
    import importlib
    mod = importlib.import_module(modname)
    cls = getattr(mod, clsname)
    try:
        n = cls(node_id=node_id, name=node_id)
    except TypeError:
        n = cls(node_id, node_id)
    return n


def test_refine_generic_connections_on_real_nodes():
    extr = _real_node("E.1", "s3dgraphy.nodes.extractor_node", "ExtractorNode")
    doc = _real_node("D.1", "s3dgraphy.nodes.document_node", "DocumentNode")
    comb = _real_node("C.1", "s3dgraphy.nodes.combiner_node", "CombinerNode")
    g = _Graph(
        nodes=[extr, doc, comb],
        edges=[
            _Edge("e1", "E.1", "D.1", "generic_connection"),  # -> extracted_from
            _Edge("e2", "C.1", "E.1", "generic_connection"),  # -> combines
            _Edge("e3", "E.1", "C.1", "has_property"),         # untouched (not generic)
        ],
    )
    n = refine_generic_connections(g)
    assert n == 2
    by = {e.edge_id: e for e in g.edges}
    assert by["e1"].edge_type == "extracted_from"
    assert by["e2"].edge_type == "combines"
    assert by["e3"].edge_type == "has_property"  # unchanged


def test_class_names_includes_bases():
    extr = _real_node("E.1", "s3dgraphy.nodes.extractor_node", "ExtractorNode")
    names = _class_names(extr)
    assert "ExtractorNode" in names and "Node" in names
