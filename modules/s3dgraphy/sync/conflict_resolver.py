"""Pluggable conflict resolution policy for GraphIngestor.

AI04 ships a stub that always returns ConflictResolution.GRAPH_WINS
(last-writer-wins, matching parent spec §6.4 default). The
interface is in place so AI06+ can subclass without changing
GraphIngestor's signature.
"""
from __future__ import annotations

from typing import Any

from .ingest_result import ConflictResolution


class ConflictResolver:
    """AI04 stub. Always resolves to GRAPH_WINS.

    Subclass and override `resolve()` in AI06+ for interactive,
    timestamp-based or callback-driven strategies.
    """
    def resolve(
        self,
        db_row: dict,
        graph_value: Any,
        field: str,
    ) -> ConflictResolution:
        return ConflictResolution.GRAPH_WINS
