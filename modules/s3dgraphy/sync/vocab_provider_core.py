"""Pure-Python VocabProvider core — no Qt dependency.

Parses the three s3dgraphy JSON pillars from a bundled directory + an
optional overrides directory. The contract is the JSON shape (Reference
Doc v0.1 §4.5 Option B). No wrapping of typed s3dgraphy APIs.

Override priority: an override file in `overrides_dir` is merged
**per top-level key** (not whole-file) into the bundled JSON, so a
partial datacenter override does not erase locally available types.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .vocab_types import EdgeType, Family, ParadataType, UnitType, VisualRule

# Filenames the loader will accept. Includes the 0.1.30 trailing-space typo.
_NODE_DATAMODEL_NAMES = (
    "s3Dgraphy_node_datamodel.json",
    "s3Dgraphy_node_datamodel .json",  # 0.1.30 typo, kept as fallback
)
_CONNECTIONS_NAMES = ("s3Dgraphy_connections_datamodel.json",)
_VISUAL_RULES_NAMES = ("em_visual_rules.json",)

_FAMILY_KEYS = {
    "stratigraphic_nodes": Family.STRATIGRAPHIC,
    "paradata_nodes": Family.PARADATA,
    "group_nodes": Family.GROUP,
    "reference_nodes": Family.REFERENCE,
    "visualization_nodes": Family.VISUALIZATION,
    "rights_nodes": Family.RIGHTS,
    "temporal_nodes": Family.TEMPORAL,
    "fallback_nodes": Family.FALLBACK,
}


def _first_existing(directory: Path, names: Iterable[str]) -> Path | None:
    for name in names:
        p = directory / name
        if p.exists():
            return p
    return None


def _merge_dicts(base: dict, override: dict) -> dict:
    """Per top-level key merge. override beats base; missing keys preserved."""
    out = dict(base)
    for k, v in override.items():
        out[k] = v
    return out


class VocabProviderCore:
    """Parses the s3dgraphy JSON pillars; query API for client tools."""

    def __init__(self, bundled_dir: Path, overrides_dir: Path):
        self._bundled_dir = Path(bundled_dir)
        self._overrides_dir = Path(overrides_dir)
        self._node_data: dict = {}
        self._connections_data: dict = {}
        self._visual_data: dict = {}
        self.reload()

    def reload(self) -> None:
        self._node_data = self._load_with_override(_NODE_DATAMODEL_NAMES)
        self._connections_data = self._load_with_override(_CONNECTIONS_NAMES)
        self._visual_data = self._load_with_override(_VISUAL_RULES_NAMES)

    def _load_with_override(self, names: Iterable[str]) -> dict:
        bundled = _first_existing(self._bundled_dir, names)
        override = _first_existing(self._overrides_dir, names)
        base = json.loads(bundled.read_text(encoding="utf-8")) if bundled else {}
        if override:
            base = _merge_dicts(base, json.loads(override.read_text(encoding="utf-8")))
        return base

    def get_unit_types(self, family: Family | None = None) -> list[UnitType]:
        out: list[UnitType] = []
        for fam_key, fam_value in _FAMILY_KEYS.items():
            if family is not None and family is not fam_value:
                continue
            family_block = self._node_data.get(fam_key, {})
            for parent_name, parent_def in family_block.items():
                subtypes = parent_def.get("subtypes", {})
                for abbrev, sub in subtypes.items():
                    out.append(UnitType(
                        abbreviation=sub.get("abbreviation", abbrev),
                        label=sub.get("label", abbrev),
                        family=fam_value,
                        cidoc_class=sub.get("mapping", {}).get("cidoc", ""),
                        symbol=sub.get("symbol", ""),
                        description=sub.get("description", ""),
                        properties=sub.get("properties", {}),
                        s3dgraphy_class=sub.get("class", ""),
                    ))
        return out
