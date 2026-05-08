"""Site-scoped CRUD for groups.graphml (atomic-safe writes).

AI06 Phase 2 / node grouping. Manages user-authored ad-hoc groups
that don't derive from any us_table column. SQL-derived groups
(struttura/area/attivita/settore/ambient/saggio/quad_par) are
materialized at export time by group_projector — they're NOT
persisted here.

File location: {db_path.parent}/groups_{sito_slug}.graphml
where sito_slug is `re.sub(r'\\W', '_', sito).lower()` (consistent
with AI05 paradata_store).

Atomic writes via .tmp + os.replace() — crash-safe.
Custom lxml serializer (s3dgraphy GraphMLExporter doesn't render
isolated ActivityNodeGroup instances without a stratigraphic
anchor — same constraint as AI05 paradata).
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from .graph_ingestor import GraphSyncError


class GroupStoreError(GraphSyncError):
    """Base for GroupStore errors."""


class GroupReadError(GroupStoreError):
    """File parse / schema error during read()."""


class GroupWriteError(GroupStoreError):
    """File write / atomic-rename failure during write()."""


class GroupValidationError(GroupStoreError):
    """Caller passed bogus data to add_group/add_us_to_group/etc."""


class GroupNotFoundError(GroupStoreError):
    """Required file or group_uuid missing where caller expected it."""


# Meta-keys produced by s3dgraphy's GraphMLImporter that must NOT be
# round-tripped (same lesson as AI05 paradata).
_GROUP_HYDRATE_SKIP_KEYS: frozenset = frozenset({
    "original_id", "graph_id", "group_attrs",
})


def _sito_slug(sito: str) -> str:
    """Filename-safe lowercase slug for a sito identifier (matches AI05)."""
    return re.sub(r"\W", "_", sito).strip("_").lower()


class GroupStore:
    """Site-scoped CRUD for groups.graphml."""

    def __init__(self, db_path: Path, sito: str) -> None:
        if not sito:
            raise GroupValidationError(
                "sito is required for GroupStore")
        self._db_path = Path(db_path)
        self._sito = sito
        self._slug = _sito_slug(sito)

    @property
    def file_path(self) -> Path:
        return self._db_path.parent / f"groups_{self._slug}.graphml"

    def exists(self) -> bool:
        return self.file_path.exists()

    @property
    def sito(self) -> str:
        return self._sito

    # ---- Low-level ------------------------------------------------------
    def read(self):
        """Return a Graph populated only with ad-hoc group nodes from
        the file. Returns empty Graph when file absent."""
        from s3dgraphy import Graph
        if not self.exists():
            graph = Graph(graph_id=self._sito)
            # Defensive filter: drop the default GeoPositionNode
            graph.nodes = [
                n for n in graph.nodes
                if (getattr(n, "attributes", None) or {}).get("group_kind")
            ]
            return graph
        try:
            from s3dgraphy.importer.import_graphml import GraphMLImporter
            graph = GraphMLImporter(filepath=str(self.file_path)).parse()
        except Exception as e:
            raise GroupReadError(
                f"Cannot parse {self.file_path}: {e}") from e
        # Hydrate AI04 data keys + group_attrs JSON blob
        try:
            from .graph_ingestor import _hydrate_pyarchinit_data_keys
            _hydrate_pyarchinit_data_keys(graph, self.file_path)
        except Exception:
            pass
        try:
            self._hydrate_group_attrs(graph)
        except Exception:
            pass
        # Filter to nodes that carry a group_kind attribute
        graph.nodes = [
            n for n in graph.nodes
            if (getattr(n, "attributes", None) or {}).get("group_kind")
        ]
        return graph

    def _hydrate_group_attrs(self, graph) -> None:
        """Re-parse the file and merge `pyarchinit.group_attrs` JSON
        blob back onto each node's `.attributes` dict."""
        from lxml import etree as ET
        import json as _json
        NS = "http://graphml.graphdrawing.org/xmlns"
        try:
            tree = ET.parse(str(self.file_path))
        except Exception:
            return
        root = tree.getroot()
        attrs_kid = None
        for k in root.findall(f"{{{NS}}}key"):
            if k.get("attr.name") == "pyarchinit.group_attrs":
                attrs_kid = k.get("id")
                break
        if not attrs_kid:
            return
        emid_to_node = {getattr(n, "node_id", None): n for n in graph.nodes}
        for node_el in root.iter(f"{{{NS}}}node"):
            blob_text = None
            emid = node_el.get("id")
            for d_el in node_el.findall(f"{{{NS}}}data"):
                if d_el.get("key") == attrs_kid and d_el.text:
                    blob_text = d_el.text
                    break
            if blob_text is None:
                continue
            try:
                blob = _json.loads(blob_text)
            except (ValueError, TypeError):
                continue
            n = emid_to_node.get(emid)
            if n is None:
                continue
            attrs = getattr(n, "attributes", None)
            if attrs is None:
                try:
                    n.attributes = {}
                    attrs = n.attributes
                except Exception:
                    continue
            for skip_key in _GROUP_HYDRATE_SKIP_KEYS:
                attrs.pop(skip_key, None)
            for k, v in blob.items():
                if k in _GROUP_HYDRATE_SKIP_KEYS:
                    continue
                if attrs.get(k) in (None, ""):
                    attrs[k] = v
