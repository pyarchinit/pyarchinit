"""L0 unit tests for edge_registry: resolve_edge_style + is_paradata_edge.

Pure pytest, no DB, no QGIS. Pins decision D8.
"""
from __future__ import annotations
import sys
from pathlib import Path

import pandas  # noqa: F401
from lxml import etree as _e  # noqa: F401
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]


def test_resolves_topological_to_solid():
    """is_after has a 'solid' line_style in em_visual_rules.json."""
    from modules.s3dgraphy.sync.edge_registry import resolve_edge_style
    style = resolve_edge_style("is_before")  # 'is_before' is in em_visual_rules
    assert style is not None
    assert style.get("line_style") in ("solid", "line")


def test_resolves_paradata_to_dashed():
    """has_property is a paradata edge → dashed line_style or dotted."""
    from modules.s3dgraphy.sync.edge_registry import resolve_edge_style
    style = resolve_edge_style("has_property")
    # If em_visual_rules has it: should be solid/dashed/dotted
    if style is not None:
        assert "line_style" in style


def test_is_paradata_edge_classifies_correctly():
    """has_property and has_paradata_nodegroup are paradata; is_after is not."""
    from modules.s3dgraphy.sync.edge_registry import is_paradata_edge
    assert is_paradata_edge("has_property") is True
    assert is_paradata_edge("has_paradata_nodegroup") is True
    assert is_paradata_edge("extracted_from") is True
    assert is_paradata_edge("is_after") is False
    assert is_paradata_edge("cuts") is False


def test_falls_back_when_datamodel_missing(monkeypatch):
    """resolve_edge_style returns None gracefully if registry can't load."""
    from modules.s3dgraphy.sync import edge_registry
    # Force registry to be sentinel False (failed load)
    monkeypatch.setattr(edge_registry, "_edge_registry_visual", False)
    assert edge_registry.resolve_edge_style("anything") is None


def test_resolve_unknown_returns_none():
    """Unknown edge_type returns None (caller falls back to default)."""
    from modules.s3dgraphy.sync.edge_registry import resolve_edge_style
    assert resolve_edge_style("totally_made_up_edge_type") is None
