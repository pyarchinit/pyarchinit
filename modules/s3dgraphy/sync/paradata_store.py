"""Site-scoped CRUD for paradata.graphml (atomic-safe writes).

AI05 Phase 2 closure. Manages the 3 node types without an SQL
counterpart in pyarchinit:
    - AuthorNode    (authorship metadata)
    - LicenseNode   (rights / SPDX licence)
    - EmbargoNode   (embargo dates)

File location: {db_path.parent}/paradata_{sito_slug}.graphml
where sito_slug is `re.sub(r'\\W+', '_', sito).lower()`.

Atomic writes via .tmp + os.replace() — crash-safe.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from .graph_ingestor import GraphSyncError


# ---------------------------------------------------------------------------
# Exception hierarchy (spec §5.1, extends GraphSyncError so existing
# try/except GraphSyncError handlers in CLI/UI/tests continue to catch).
# ---------------------------------------------------------------------------
class ParadataStoreError(GraphSyncError):
    """Base for ParadataStore errors."""


class ParadataReadError(ParadataStoreError):
    """File parse / schema error during read()."""


class ParadataWriteError(ParadataStoreError):
    """File write / atomic-rename failure during write()."""


class ParadataValidationError(ParadataStoreError):
    """Caller passed bogus data to add_author/license/embargo/etc."""


class ParadataNotFoundError(ParadataStoreError):
    """Required file missing where caller expected it."""


# ---------------------------------------------------------------------------
# ParadataStore
# ---------------------------------------------------------------------------
_PARADATA_NODE_TYPES: frozenset[str] = frozenset({
    "AuthorNode", "LicenseNode", "EmbargoNode",
})


def _sito_slug(sito: str) -> str:
    """Filename-safe lowercase slug for a sito identifier."""
    return re.sub(r"\W", "_", sito).strip("_").lower()


class ParadataStore:
    """Site-scoped CRUD for paradata.graphml.

    Args:
        db_path: filesystem path to the pyarchinit SQLite DB; the
            paradata file lives in the same directory.
        sito: site identifier (a value from `us_table.sito`).

    Raises on instantiation: nothing (lazy file checks; read/write
    perform actual I/O).
    """

    def __init__(self, db_path: Path, sito: str) -> None:
        if not sito:
            raise ParadataValidationError(
                "sito is required for ParadataStore")
        self._db_path = Path(db_path)
        self._sito = sito
        self._slug = _sito_slug(sito)

    @property
    def file_path(self) -> Path:
        """Resolved paradata file path for this (db, sito) pair."""
        return self._db_path.parent / f"paradata_{self._slug}.graphml"

    def exists(self) -> bool:
        """Whether the paradata file is present on disk."""
        return self.file_path.exists()

    @property
    def sito(self) -> str:
        return self._sito

    # ---- Low-level (D5) ------------------------------------------------
    def read(self):
        """Return a Graph populated with only the paradata-family
        nodes from the file. Returns empty Graph when file absent."""
        from s3dgraphy import Graph
        if not self.exists():
            graph = Graph(graph_id=self._sito)
            # Defensive filter even on empty: Graph() bootstraps a
            # default GeoPositionNode which is not paradata.
            graph.nodes = [
                n for n in graph.nodes
                if type(n).__name__ in _PARADATA_NODE_TYPES
            ]
            return graph
        try:
            from s3dgraphy.importer.import_graphml import GraphMLImporter
            graph = GraphMLImporter(filepath=str(self.file_path)).parse()
        except Exception as e:
            raise ParadataReadError(
                f"Cannot parse {self.file_path}: {e}") from e
        # AI04 helper to recover stripped attrs
        try:
            from .graph_ingestor import _hydrate_pyarchinit_data_keys
            _hydrate_pyarchinit_data_keys(graph, self.file_path)
        except Exception:
            pass
        # Defensive filter: drop non-paradata node types
        graph.nodes = [
            n for n in graph.nodes
            if type(n).__name__ in _PARADATA_NODE_TYPES
        ]
        return graph

    def write(self, graph) -> None:
        """Atomic write: serialise to .tmp, embed AI04 data keys,
        os.replace() to final path. Original file untouched on
        failure."""
        tmp = self.file_path.with_suffix(".graphml.tmp")
        try:
            from s3dgraphy.exporter.graphml.graphml_exporter import (
                GraphMLExporter,
            )
            exporter = GraphMLExporter(graph)
            exporter.export(str(tmp), persist_auxiliary=False)
            # Embed pyarchinit data keys so round-trip preserves
            # the AI04-introduced attributes.
            from .graphml_writer import _embed_pyarchinit_data_keys
            _embed_pyarchinit_data_keys(graph, tmp)
            # Atomic rename — POSIX + Windows ≥ Vista.
            os.replace(str(tmp), str(self.file_path))
        except Exception as e:
            # Cleanup tmp if it exists; original is untouched.
            try:
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                pass
            raise ParadataWriteError(
                f"Cannot write {self.file_path}: {e}") from e

    def add_node(self, node) -> None:
        """Append *node* to the paradata graph + write."""
        type_name = type(node).__name__
        if type_name not in _PARADATA_NODE_TYPES:
            raise ParadataValidationError(
                f"Refusing to store {type_name} in paradata.graphml — "
                f"only {sorted(_PARADATA_NODE_TYPES)} are accepted.")
        graph = self.read()
        graph.add_node(node)
        self.write(graph)

    def remove_node(self, node_uuid: str) -> None:
        """Idempotent removal: no error if node_uuid not found."""
        graph = self.read()
        before = len(graph.nodes)
        graph.nodes = [
            n for n in graph.nodes
            if getattr(n, "node_id", None) != node_uuid
        ]
        if len(graph.nodes) != before:
            self.write(graph)

    # alias for D5/B-style API consistency
    remove = remove_node

    def find(self, node_type: str, **kwargs) -> list:
        """Return matching nodes from the file. Empty list if none."""
        graph = self.read()
        out = []
        for n in graph.nodes:
            if type(n).__name__ != node_type:
                continue
            if all(getattr(n, k, None) == v
                   or (getattr(n, "data", {}) or {}).get(k) == v
                   for k, v in kwargs.items()):
                out.append(n)
        return out

    # ---- High-level (D5) — populated in Task B.3 ----------------------
    # add_author / list_authors / add_license / list_licenses /
    # add_embargo / list_embargos
