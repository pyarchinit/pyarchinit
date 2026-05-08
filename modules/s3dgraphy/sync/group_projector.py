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


def build_groups_from_sql(
    db_path: Path,
    sito: str,
    dimensions: List[str],
) -> List[GroupSpec]:
    """For each requested dimension, scan us_table for distinct
    non-empty values within sito, and emit one GroupSpec per
    (dimension, value) pair.

    UUID generation: deterministic UUID5 from
    (sito, group_kind, name) so re-export produces identical
    UUIDs (AC-7 idempotent invariant).

    Unknown dimension names (typos) are silently skipped (logged).
    """
    out: List[GroupSpec] = []
    if not dimensions:
        return out

    valid_dims = [d for d in dimensions if d in _SQL_DIMENSIONS]
    if len(valid_dims) != len(dimensions):
        bogus = set(dimensions) - set(valid_dims)
        _log.warning(f"Unknown grouping dimensions skipped: {bogus}")

    conn = sqlite3.connect(str(db_path))
    try:
        for dim in valid_dims:
            # Distinct values + member UUIDs in one pass
            rows = conn.execute(
                f"SELECT {dim}, node_uuid FROM us_table "
                f"WHERE sito=? AND {dim} IS NOT NULL "
                f"AND TRIM({dim})<>'' AND node_uuid IS NOT NULL",
                (sito,),
            ).fetchall()
            # Group by value
            buckets: dict = {}
            for value, node_uuid in rows:
                buckets.setdefault(str(value), []).append(node_uuid)
            for name, member_uuids in buckets.items():
                # Deterministic UUID5 from (sito, dim, name)
                key = f"{sito}|{dim}|{name}"
                group_uuid = str(uuid.uuid5(
                    _PYARCHINIT_GROUP_NAMESPACE, key))
                out.append(GroupSpec(
                    group_uuid=group_uuid,
                    name=name,
                    group_kind=dim,
                    member_us_uuids=list(member_uuids),
                ))
    finally:
        conn.close()
    return out


def merge_adhoc_groups(
    sql_specs: List[GroupSpec],
    store,
) -> List[GroupSpec]:
    """Append GroupSpec instances from groups_{sito}.graphml.

    Collision policy: if an ad-hoc group has the same name as an
    SQL-derived group (regardless of group_kind), the ad-hoc is
    SKIPPED and a warning is logged. SQL "wins". This matches
    spec §10 D6 risk mitigation.
    """
    out = list(sql_specs)
    if not store.exists():
        return out

    sql_names = {s.name for s in sql_specs}
    try:
        groups = store.list_groups()
    except Exception as e:
        _log.warning(f"Cannot read GroupStore, skipping ad-hoc: {e}")
        return out

    for g in groups:
        name = g.get("name", "")
        if name in sql_names:
            _log.warning(
                f"Ad-hoc group name collision with SQL: '{name}' "
                f"(SQL wins, ad-hoc skipped)")
            continue
        out.append(GroupSpec(
            group_uuid=g.get("group_uuid", ""),
            name=name,
            group_kind=g.get("group_kind", "adhoc"),
            member_us_uuids=list(g.get("member_us_uuids", [])),
            description=g.get("description", ""),
        ))
    return out
