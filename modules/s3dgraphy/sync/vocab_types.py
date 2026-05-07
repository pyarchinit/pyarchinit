"""Typed dataclasses for the vocabulary entries parsed by VocabProvider.

These are read-only views over the JSON catalogues shipped inside the
s3dgraphy package (see Reference Doc v0.1 §4.1):

    s3Dgraphy_node_datamodel.json
    s3Dgraphy_connections_datamodel.json
    em_visual_rules.json

The classes intentionally mirror the JSON shape rather than wrapping a
typed s3dgraphy Python API — per Reference Doc v0.1 §4.5 Option B
(per-tool parsing). The JSON top-level file names and top-level keys are
public API per §7.1.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Family(str, Enum):
    STRATIGRAPHIC = "stratigraphic"
    PARADATA = "paradata"
    GROUP = "group"
    REFERENCE = "reference"
    VISUALIZATION = "visualization"
    RIGHTS = "rights"
    TEMPORAL = "temporal"
    FALLBACK = "fallback"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class UnitType:
    abbreviation: str
    label: str
    family: Family
    cidoc_class: str
    symbol: str
    description: str
    properties: dict
    s3dgraphy_class: str


@dataclass(frozen=True)
class EdgeType:
    name: str
    label: str
    description: str
    allowed_pairs: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class VisualRule:
    node_type: str
    icon: str
    fill: str
    stroke: str
    palette: str


@dataclass(frozen=True)
class ParadataType:
    abbreviation: str
    label: str
    description: str
    cidoc_class: str
    s3dgraphy_class: str


@dataclass(frozen=True)
class VocabularyVersion:
    nodes: str = ""
    connections: str = ""
    visual_rules: str = ""
