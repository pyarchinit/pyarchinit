"""Pure-Python wrapper over s3dgraphy.PyArchInitImporter +
s3dgraphy.exporter.graphml.GraphMLExporter.

Public API:
    export_graphml(db_path, mapping, output_path,
                   *, site_filter=None, persist_auxiliary=False) -> ExportResult

This is the AI03 cut-over surface (per spec §3.2). Replaces the
legacy DOT→GraphML pipeline that lived in s3dgraphy_dot_bridge.py
+ graphml_spatial_enhancer.py + dottoxml.exportGraphml.

No Qt imports — runnable from bare pytest.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class ExportResult:
    """Metrics + warnings returned by a successful export_graphml() call."""
    output_path: str
    node_count: int
    edge_count: int
    epoch_count: int
    tred_removed_edges: int
    warnings: list = field(default_factory=list)


VALID_STAGES = frozenset({"import", "filter", "export", "write"})


class EmptyGraphError(ValueError):
    """Graph has no nodes after import + (optional) site filter."""


class GraphMLExportError(RuntimeError):
    """Wraps any failure during the GraphML export pipeline.

    Attributes:
        stage: one of VALID_STAGES — categorises where the failure
            occurred so the bridge UI can present a useful message.
        original: the underlying exception, preserved for logging.
    """

    def __init__(self, stage: str, original: Exception):
        if stage not in VALID_STAGES:
            raise ValueError(
                f"unknown stage {stage!r}; valid: {sorted(VALID_STAGES)}")
        self.stage = stage
        self.original = original
        super().__init__(
            f"GraphML {stage} failed: {type(original).__name__}: {original}")
