"""Tests for vocab_types dataclasses."""
from __future__ import annotations

from s3dgraphy.sync.vocab_types import (
    EdgeType,
    Family,
    UnitType,
    VisualRule,
)


def test_unit_type_holds_abbreviation_and_label():
    ut = UnitType(
        abbreviation="US",
        label="US (or SU)",
        family=Family.STRATIGRAPHIC,
        cidoc_class="A2 Stratigraphic Volume Unit",
        symbol="white rectangle",
        description="Stratigraphic Unit",
        properties={"name": "P1_is_identified_by"},
        s3dgraphy_class="StratigraphicUnit",
    )
    assert ut.abbreviation == "US"
    assert ut.family is Family.STRATIGRAPHIC


def test_edge_type_lists_allowed_pairs():
    e = EdgeType(
        name="is_after",
        label="is after",
        description="Stratigraphic posteriority",
        allowed_pairs=(("US", "US"), ("US", "USVs")),
    )
    assert ("US", "USVs") in e.allowed_pairs


def test_visual_rule_holds_palette_membership():
    v = VisualRule(
        node_type="US",
        icon="us.svg",
        fill="#FFFFFF",
        stroke="#000000",
        palette="stratigraphic",
    )
    assert v.palette == "stratigraphic"
