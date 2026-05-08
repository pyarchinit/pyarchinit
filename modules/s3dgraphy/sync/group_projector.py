"""Pure-functional helpers for AI06 node grouping.

build_groups_from_sql: scan us_table for the requested grouping
    dimensions, emit one GroupSpec per (dim, value) pair.
merge_adhoc_groups: append GroupSpec instances from a GroupStore.
dimensions_with_data: return the subset of 7 grouping columns
    that have at least one non-empty value in us_table for sito.

UUID generation: deterministic UUID5 from (sito, group_kind, name)
so re-export with the same SQL state produces identical UUIDs
(idempotent, AC-7). Ad-hoc groups use UUID7 generated at creation
by GroupStore (AC-7 second clause).
"""
from __future__ import annotations

import logging
import sqlite3
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


_log = logging.getLogger("pyarchinit.s3dgraphy.sync.groups")


# The 7 SQL-derived grouping dimensions per spec §1.
_SQL_DIMENSIONS: tuple = (
    "area", "struttura", "attivita", "settore",
    "ambient", "saggio", "quad_par",
)

# Deterministic UUID5 namespace for SQL-derived groups (AC-7).
# A constant, project-internal namespace so the same (sito, kind, name)
# triple maps to the same UUID across exports/runs/machines.
_PYARCHINIT_GROUP_NAMESPACE = uuid.UUID(
    "6e8c0a2e-2026-50a6-9a06-ff77e2e3c5a1"
)


@dataclass(frozen=True)
class GroupSpec:
    """Pre-render specification of a group.

    Resolved to ActivityNodeGroup by GraphProjector._merge_groups.
    """
    group_uuid: str
    name: str
    group_kind: str
    member_us_uuids: List[str] = field(default_factory=list)
    description: str = ""


def dimensions_with_data(db_path: Path, sito: str) -> List[str]:
    """Return subset of {area, struttura, attivita, settore,
    ambient, saggio, quad_par} that has at least one non-empty
    value in us_table for *sito*. Used by the dialog UI to
    pre-check the right boxes (D2)."""
    out = []
    conn = sqlite3.connect(str(db_path))
    try:
        for col in _SQL_DIMENSIONS:
            row = conn.execute(
                f"SELECT 1 FROM us_table "
                f"WHERE sito=? AND {col} IS NOT NULL AND TRIM({col})<>'' "
                f"LIMIT 1",
                (sito,),
            ).fetchone()
            if row is not None:
                out.append(col)
    finally:
        conn.close()
    return out
