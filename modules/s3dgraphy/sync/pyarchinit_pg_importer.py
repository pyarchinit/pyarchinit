"""DbHandle-aware reader replacing upstream PyArchInitImporter on PG.

PG-Bv2 milestone (5.7.9-alpha): completes the PostgreSQL graphml
export gap left by PG-B (phase3-pgcompat-b-export-5.7.1-alpha,
2026-05-10). PG-B flipped 5 SQL helpers in graph_projector.py but
missed the orchestrator populate_graph() which still called the
upstream PyArchInitImporter (sqlite3-only). This module is the
α-narrow replacement: only used when handle.is_postgres; SQLite
keeps the upstream importer to preserve AC-2 byte-identical
baseline.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import text

from ._db_handle import DbHandle

if TYPE_CHECKING:
    from s3dgraphy import Graph


def _load_mapping(mapping_name: str) -> dict:
    """Load mapping JSON from ext_libs/s3dgraphy/mappings/pyarchinit/."""
    here = Path(__file__).resolve()
    repo_root = here.parents[3]  # plugins/pyarchinit/
    mapping_path = (
        repo_root
        / "ext_libs"
        / "s3dgraphy"
        / "mappings"
        / "pyarchinit"
        / f"{mapping_name}.json"
    )
    if not mapping_path.exists():
        raise FileNotFoundError(
            f"mapping JSON not found: {mapping_path}"
        )
    with mapping_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def import_from_pg(
    handle: DbHandle,
    sito: str,
    mapping_name: str = "pyarchinit_us_mapping",
) -> "Graph":
    """Build a stratigraphic Graph from a PG us_table via SQLAlchemy.

    Replaces the upstream PyArchInitImporter call in
    graph_projector.populate_graph() when backend is PG. Mirrors
    the upstream contract (StratigraphicNode + PropertyNode +
    has_property edges) for the subset pyarchinit actually uses.

    Args:
        handle: DbHandle for the PG database
        sito: site identifier (us_table.sito value)
        mapping_name: mapping JSON name in
            ext_libs/s3dgraphy/mappings/pyarchinit/<name>.json

    Returns:
        s3dgraphy.Graph (unregistered, caller sets graph_id +
        registers).
    """
    from s3dgraphy import Graph
    from s3dgraphy.nodes.property_node import PropertyNode
    from s3dgraphy.utils.utils import get_stratigraphic_node_class

    mapping = _load_mapping(mapping_name)
    table = mapping["table_settings"]["table_name"]
    col_mappings = mapping["column_mappings"]

    id_col = next(
        (col for col, spec in col_mappings.items() if spec.get("is_id")),
        None,
    )
    if id_col is None:
        raise ValueError(
            f"mapping {mapping_name!r} has no column with is_id=true"
        )
    desc_col = next(
        (col for col, spec in col_mappings.items()
         if spec.get("is_description")),
        None,
    )
    property_cols = [
        (col, spec) for col, spec in col_mappings.items()
        if spec.get("node_type") == "PropertyNode"
    ]

    graph = Graph(graph_id="temp_graph")  # caller renames

    with handle.engine.connect() as conn:
        rows = conn.execute(
            text(f"SELECT * FROM {table} WHERE sito = :sito"),
            {"sito": sito},
        ).mappings().all()

    for row in rows:
        if row.get(id_col) in (None, ""):
            continue
        node_name = str(row[id_col])
        unita_tipo = row.get("unita_tipo") or "US"
        try:
            node_cls = get_stratigraphic_node_class(unita_tipo)
        except Exception:
            from s3dgraphy.nodes.stratigraphic_node import (
                StratigraphicNode,
            )
            node_cls = StratigraphicNode
        description = str(row[desc_col]) if (
            desc_col and row.get(desc_col) is not None
        ) else ""
        strat_node = node_cls(
            node_id=node_name,
            name=node_name,
            description=description,
        )
        try:
            graph.add_node(strat_node, overwrite=True)
        except Exception:
            pass

        for col, spec in property_cols:
            value = row.get(col)
            if value is None and not spec.get("create_empty", False):
                continue
            prop_name = spec.get("property_name") or col
            prop_id = f"{node_name}_{prop_name}"
            prop_node = PropertyNode(
                node_id=prop_id,
                name=prop_name,
                description=spec.get("description", ""),
                value=str(value) if value is not None else "",
                property_type=prop_name,
                data={},
            )
            try:
                graph.add_node(prop_node, overwrite=True)
                graph.add_edge(
                    edge_id=f"{node_name}_has_{prop_name}",
                    edge_source=node_name,
                    edge_target=prop_id,
                    edge_type="has_property",
                )
            except Exception:
                pass

    return graph
