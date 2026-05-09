"""Edge style + paradata classification, sourced from s3dgraphy's
shipped JSON catalogs:

  ext_libs/s3dgraphy/JSON_config/em_visual_rules.json
      → edge_style.{edge_type}.{color, line_style, width}
  ext_libs/s3dgraphy/JSON_config/s3Dgraphy_connections_datamodel.json
      → edge_types.{edge_type}.{label, allowed_connections, mapping}

Override-wins: pyarchinit-specific overrides in
`_PYARCHINIT_EDGE_OVERRIDES` win over the canonical s3dgraphy
catalogs. Future EM edge types added to the catalogs are picked up
automatically without changes here.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# ----------------------------------------------------------------------
# Pyarchinit-specific overrides (D8: override-wins). Empty for now —
# the AI03/AI04 line-style logic (dashed for paradata, solid for
# stratigraphic) is now derived from `is_paradata_edge`. If a future
# pyarchinit deviation emerges (e.g. specific color for "rapporti"
# rendering), add an entry here:
#
#   "is_after": {"color": "#000000", "line_style": "solid", "width": 2}
# ----------------------------------------------------------------------
_PYARCHINIT_EDGE_OVERRIDES: dict[str, dict] = {}


# ----------------------------------------------------------------------
# Hardcoded paradata edge set — used as fallback when the datamodel
# JSON is missing or malformed. These match what AI04's
# `_build_rapporti_from_edges` excludes from the rapporti list and
# what the post-processor renders as dashed.
# ----------------------------------------------------------------------
_HARDCODED_PARADATA_EDGES: frozenset[str] = frozenset({
    "has_property",
    "has_paradata_nodegroup",
    "has_first_epoch",
    "extracted_from",
    "combines",
    "survive_in_epoch",
    "has_data_provenance",
    "is_in_activity",
    "has_author",
    "has_license",
    "has_embargo",
})


# ----------------------------------------------------------------------
# Public catalogue of edge types known to the pyarchinit ↔ s3dgraphy
# bridge. Downstream projectors / ingestors / validators can introspect
# this set to decide whether an incoming edge_type is a first-class
# structural / paradata edge or an unknown extension.
#
# Sourced statically from the union of:
#   - structural / EM edges declared in em_visual_rules.json (0.1.41)
#   - the hardcoded paradata fallback set above
#
# AI07 (2026-05-09) adds "is_in_location" — the canonical edge type
# for spatial / locational membership shipped by s3dgraphy 0.1.41
# alongside LocationNodeGroup. Keep this set sorted alphabetically
# for stable diffs.
# ----------------------------------------------------------------------
# Structural / EM edges + paradata-flow edges. The paradata block is
# computed from `_HARDCODED_PARADATA_EDGES` (defined above) via set
# union to prevent drift — if a paradata edge is added there, it
# automatically enters this set.
_STRUCTURAL_EDGE_TYPES: frozenset[str] = frozenset({
    # Structural / EM edges (from em_visual_rules.json)
    "changed_from",
    "contrasts_with",
    "generic_connection",
    "has_geoposition",
    "has_linked_resource",
    "has_representation_model",
    "has_same_time",
    "has_semantic_shape",
    "has_timebranch",
    "is_before",
    "is_in_activity",         # functional / activity grouping
    "is_in_location",         # AI07: spatial / locational membership
    "is_in_paradata_nodegroup",
    "is_in_timebranch",
})

# Public set: structural ∪ paradata. Downstream projectors / ingestors
# / validators introspect this set to decide whether to accept an edge.
KNOWN_EDGE_TYPES: frozenset[str] = (
    _STRUCTURAL_EDGE_TYPES | _HARDCODED_PARADATA_EDGES
)


_EXT_LIBS_S3DG = (
    Path(__file__).resolve().parents[3] / "ext_libs" / "s3dgraphy"
)
_VISUAL_RULES_PATH = _EXT_LIBS_S3DG / "JSON_config" / "em_visual_rules.json"
_CONNECTIONS_PATH = (
    _EXT_LIBS_S3DG / "JSON_config" / "s3Dgraphy_connections_datamodel.json"
)


# Lazy singletons. False sentinel means "load failed once, don't retry".
_edge_registry_visual: dict | bool | None = None
_edge_registry_connections: dict | bool | None = None


def _load_visual_rules() -> dict | None:
    """Load em_visual_rules.json once. Returns None on failure."""
    global _edge_registry_visual
    if _edge_registry_visual is False:
        return None
    if _edge_registry_visual is None:
        try:
            with open(_VISUAL_RULES_PATH, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            _edge_registry_visual = data.get("edge_style", {})
        except Exception:
            _edge_registry_visual = False
            return None
    return (_edge_registry_visual
            if isinstance(_edge_registry_visual, dict) else None)


def _load_connections_datamodel() -> dict | None:
    """Load s3Dgraphy_connections_datamodel.json once."""
    global _edge_registry_connections
    if _edge_registry_connections is False:
        return None
    if _edge_registry_connections is None:
        try:
            with open(_CONNECTIONS_PATH, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            _edge_registry_connections = data.get("edge_types", {})
        except Exception:
            _edge_registry_connections = False
            return None
    return (_edge_registry_connections
            if isinstance(_edge_registry_connections, dict) else None)


def resolve_edge_style(edge_type: str) -> dict | None:
    """Return the style dict for *edge_type*, or None if not known.

    Lookup order:
        1. _PYARCHINIT_EDGE_OVERRIDES (override-wins)
        2. em_visual_rules.json edge_style.{edge_type}.style
        3. None (caller uses default)

    Returned dict shape: {"color": "#RRGGBB", "line_style": "solid"|"dashed"|"dotted",
                          "width": int}
    """
    if edge_type in _PYARCHINIT_EDGE_OVERRIDES:
        return dict(_PYARCHINIT_EDGE_OVERRIDES[edge_type])
    visual = _load_visual_rules()
    if visual is None:
        return None
    entry = visual.get(edge_type)
    if not entry:
        return None
    style = entry.get("style") if isinstance(entry, dict) else None
    if not isinstance(style, dict):
        return None
    return dict(style)


# ----------------------------------------------------------------------
# Structural override set — edges that are definitively NOT paradata
# regardless of what the connections datamodel says about their
# `allowed_connections`. AI07 is_in_location is the canonical case:
# the datamodel allows paradata-class sources (PropertyNode etc.) to
# carry a location, but the edge type itself is a structural /
# locational membership, not a paradata-flow edge.
# ----------------------------------------------------------------------
_STRUCTURAL_NON_PARADATA_EDGES: frozenset[str] = frozenset({
    "is_in_location",   # AI07: spatial / locational membership
})


def is_paradata_edge(edge_type: str) -> bool:
    """True iff *edge_type* is a paradata-flow edge (rendered dashed in
    the AI03 post-processor; excluded from rapporti round-trip in AI04).

    Uses the connections datamodel when available — paradata edges have
    `allowed_connections.source` or `.target` containing PropertyNode /
    DocumentNode / ExtractorNode / CombinerNode. Falls back to the
    hardcoded `_HARDCODED_PARADATA_EDGES` set when the datamodel is
    unavailable.

    Structural edges listed in `_STRUCTURAL_NON_PARADATA_EDGES` are
    always reported as non-paradata, even if their connections-datamodel
    `allowed_connections` includes paradata-class endpoints (e.g.
    `is_in_location` allows PropertyNode sources for "this property
    measurement was taken at this place").
    """
    if edge_type in _STRUCTURAL_NON_PARADATA_EDGES:
        return False
    if edge_type in _HARDCODED_PARADATA_EDGES:
        return True
    connections = _load_connections_datamodel()
    if connections is None:
        return False
    entry = connections.get(edge_type)
    if not isinstance(entry, dict):
        return False
    allowed = entry.get("allowed_connections", {})
    if not isinstance(allowed, dict):
        return False
    paradata_classes = {
        "PropertyNode", "DocumentNode", "ExtractorNode",
        "CombinerNode", "AuthorNode", "LicenseNode", "EmbargoNode",
        "ParadataNodeGroup",
    }
    src = set(allowed.get("source", []) or [])
    tgt = set(allowed.get("target", []) or [])
    return bool(src & paradata_classes or tgt & paradata_classes)
