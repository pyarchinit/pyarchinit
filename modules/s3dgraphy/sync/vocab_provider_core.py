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

from .vocab_types import EdgeType, Family, ParadataType, UnitType, VisualRule, VocabularyVersion

# Filenames the loader will accept. Includes the 0.1.30 trailing-space typo.
_NODE_DATAMODEL_NAMES = (
    "s3Dgraphy_node_datamodel.json",
    "s3Dgraphy_node_datamodel .json",  # 0.1.30 shipped this filename by mistake (typo); kept for backward compat. Remove only after dropping 0.1.30 support.
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


def _vtuple(s: str) -> tuple[int, ...]:
    """Parse a 'M.N.P' version string into a comparable tuple."""
    out: list[int] = []
    for part in (s or "0").split("."):
        try:
            out.append(int(part))
        except ValueError:
            out.append(0)
    return tuple(out)


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

    def __init__(self,
                 bundled_dir: Path,
                 overrides_dir: Path,
                 min_versions: dict | None = None):
        self._bundled_dir = Path(bundled_dir)
        self._overrides_dir = Path(overrides_dir)
        self._min_versions = dict(min_versions or {})
        self._node_data: dict = {}
        self._connections_data: dict = {}
        self._visual_data: dict = {}
        self.reload()
        self._enforce_minimum_versions()

    def _enforce_minimum_versions(self) -> None:
        v = self.versions
        for key, required in self._min_versions.items():
            actual = getattr(v, key, "")
            if _vtuple(actual) < _vtuple(required):
                raise ValueError(
                    f"s3dgraphy vocabulary {key} version {actual!r} is below "
                    f"required minimum {required!r}")

    @property
    def versions(self) -> VocabularyVersion:
        # Each pillar uses a slightly different version key on disk; we
        # accept BOTH the simplified fixture key and the real 0.1.40 key
        # so neither test fixtures nor real vendor rolls regress.
        connections = (
            self._connections_data.get("s3Dgraphy_connections_version")
            or self._connections_data.get("s3Dgraphy_connections_model_version", "")
        )
        visual_rules = (
            self._visual_data.get("em_visual_rules_version")
            or self._visual_data.get("version", "")
        )
        return VocabularyVersion(
            nodes=self._node_data.get("s3Dgraphy_data_model_version", ""),
            connections=connections,
            visual_rules=visual_rules,
        )

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

    def get_edge_types(self) -> list[EdgeType]:
        block = self._connections_data.get("edge_types", {})
        out: list[EdgeType] = []
        for name, defn in block.items():
            pairs = tuple(
                (p.get("source", ""), p.get("target", ""))
                for p in defn.get("allowed_pairs", [])
            )
            out.append(EdgeType(
                name=name,
                label=defn.get("label", name),
                description=defn.get("description", ""),
                allowed_pairs=pairs,
            ))
        return out

    def get_legal_targets_for(self, source_type: str, edge_name: str) -> list[str]:
        for e in self.get_edge_types():
            if e.name != edge_name:
                continue
            return [tgt for src, tgt in e.allowed_pairs if src == source_type]
        return []

    def get_paradata_types(self) -> list[ParadataType]:
        block = self._node_data.get("paradata_nodes", {})
        out: list[ParadataType] = []
        for class_name, defn in block.items():
            out.append(ParadataType(
                abbreviation=defn.get("abbreviation", class_name),
                label=defn.get("label", class_name),
                description=defn.get("description", ""),
                cidoc_class=defn.get("mapping", {}).get("cidoc", ""),
                s3dgraphy_class=defn.get("class", class_name),
            ))
        return out

    def get_visual_rule(self, node_type: str) -> VisualRule | None:
        # Two shapes are supported on disk:
        #   (a) flat fixture form used by tests: `{"rules": {"<type>": {"icon", "fill", "stroke", "palette"}}}`
        #   (b) real s3dgraphy 0.1.40 form: `{"node_styles": {"<type>": {"file_2d", "style": {"fill_color", "border_color", ...}, ...}}}`
        block = (
            self._visual_data.get("rules")
            or self._visual_data.get("node_styles")
            or {}
        )
        rule = block.get(node_type)
        if rule is None:
            return None
        # Flat shape (fixture): keys live at the rule's top level.
        if "fill" in rule or "stroke" in rule or "palette" in rule:
            return VisualRule(
                node_type=node_type,
                icon=rule.get("icon", ""),
                fill=rule.get("fill", ""),
                stroke=rule.get("stroke", ""),
                palette=rule.get("palette", ""),
            )
        # Nested shape (s3dgraphy 0.1.40): style block holds fill_color, border_color, shape.
        style = rule.get("style", {}) or {}
        return VisualRule(
            node_type=node_type,
            icon=rule.get("file_2d") or rule.get("2d_file_rast")
                 or rule.get("2d_file_vect", ""),
            fill=style.get("fill_color", ""),
            stroke=style.get("border_color", ""),
            palette=style.get("shape", ""),
        )

    def get_cidoc_mapping(self, type_abbreviation: str) -> str | None:
        for ut in self.get_unit_types():
            if ut.abbreviation == type_abbreviation:
                return ut.cidoc_class or None
        for pt in self.get_paradata_types():
            if pt.s3dgraphy_class == type_abbreviation or pt.abbreviation == type_abbreviation:
                return pt.cidoc_class or None
        return None
