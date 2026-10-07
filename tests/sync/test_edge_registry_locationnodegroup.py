"""AI07 Group A: edge_registry recognises is_in_location."""
from __future__ import annotations

from s3dgraphy.sync.edge_registry import (
    KNOWN_EDGE_TYPES,
    resolve_edge_style,
    is_paradata_edge,
)


def test_is_in_location_is_known():
    assert "is_in_location" in KNOWN_EDGE_TYPES


def test_is_in_location_resolves_to_visual_style():
    style = resolve_edge_style("is_in_location")
    assert style is not None
    assert "color" in style or "lineStyle" in style or "stroke" in style


def test_is_in_location_not_paradata():
    # is_in_location is structural, not paradata flow
    assert is_paradata_edge("is_in_location") is False
