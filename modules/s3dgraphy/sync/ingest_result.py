"""Result and conflict record dataclasses for GraphIngestor.populate_list().

AI04 ships a fixed atomic-only ingestion model with last-writer-wins
conflict resolution. The ConflictResolution enum has three members so
AI06+ can extend without breaking the API.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ConflictResolution(str, Enum):
    """Outcome of a single field-level conflict during ingest.

    AI04 always uses GRAPH_WINS (the bridge prototype implements
    'last writer wins' policy from parent spec §6.4). DB_WINS and
    SKIPPED are reserved for AI06+ pluggable resolvers.
    """
    GRAPH_WINS = "graph_wins"
    DB_WINS = "db_wins"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class ConflictRecord:
    """A single field-level conflict detected during ingestion.

    A row is inserted into IngestResult.conflicts when the graph
    node has a value different from the DB row for one of the
    MAPPED_COLUMNS and the resolver decides how to merge.
    """
    node_uuid: str
    field: str
    db_value: Any
    graph_value: Any
    resolution: str   # ConflictResolution.value


@dataclass(frozen=True)
class IngestResult:
    """Aggregated outcome of GraphIngestor.populate_list().

    Counters and the conflict / error lists let callers (CLI, UI,
    test) summarise the ingestion without re-walking the graph.
    """
    applied: int            # rows inserted+updated successfully
    inserted: int           # rows newly created
    updated: int            # rows updated in place
    skipped: int            # rows unchanged (idempotent path)
    epochs_created: int     # auto-created periodizzazione rows
    conflicts: tuple[ConflictRecord, ...] = ()
    errors: tuple[str, ...] = ()
    dry_run: bool = False
    # yE-C (5.7.7-alpha): structured output from the yEd-raw parse
    # phase. Populated by populate_list() when graphml_path is
    # yEd-raw; None for pyarchinit-projected graphmls.
    # Shape when populated:
    #   {"classified": list[ClassifiedNode],
    #    "periods": list[PeriodCandidate],
    #    "folders": list[FolderCandidate]}
    # Forward-compat with yE-D pipeline.
    parsed_drafts: dict | None = None
