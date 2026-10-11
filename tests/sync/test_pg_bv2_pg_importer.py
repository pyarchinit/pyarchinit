"""PG-Bv2 (5.7.9-alpha): tests for the SQLAlchemy-native PG importer
that replaces the upstream PyArchInitImporter (SQLite-only) in
graph_projector.populate_graph() when backend is PG.

2 L0 tests run everywhere (no PG runtime needed). 2 L2 PG tests
skip cleanly when psycopg2 missing or PG offline.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import pg_with_volterra fixture explicitly — conftest_pg.py is not
# auto-discovered (file is named conftest_pg not conftest).
# pg_with_volterra yields a SQLAlchemy Engine seeded with mini_volterra data.
from tests.sync.conftest_pg import pg_engine, pg_with_volterra  # noqa: F401


# ---------------------------------------------------------------------
# L0 — no PG runtime needed
# ---------------------------------------------------------------------

def test_pg_importer_mapping_json_resolves():
    """``_load_mapping`` must find pyarchinit_us_mapping.json and
    return a dict with the expected schema (table_settings,
    column_mappings keys)."""
    from s3dgraphy.sync.pyarchinit_pg_importer import (
        _load_mapping,
    )
    mapping = _load_mapping("pyarchinit_us_mapping")
    assert isinstance(mapping, dict)
    assert "table_settings" in mapping
    assert mapping["table_settings"].get("table_name") == "us_table"
    assert "column_mappings" in mapping
    # At least one is_id column and at least one PropertyNode column.
    cols = mapping["column_mappings"]
    assert any(spec.get("is_id") for spec in cols.values()), (
        "no is_id column in mapping — importer cannot identify nodes"
    )
    assert any(
        spec.get("node_type") == "PropertyNode"
        for spec in cols.values()
    ), "no PropertyNode columns in mapping — nothing to build"


def test_pg_importer_builds_strat_node_from_mock_row():
    """``import_from_pg`` must build a StratigraphicNode named
    after the is_id column value and PropertyNodes for each
    PropertyNode-typed column. Uses mocked DbHandle to avoid PG
    runtime."""
    from s3dgraphy.sync.pyarchinit_pg_importer import (
        import_from_pg,
    )

    # Mock handle.engine.connect().execute().mappings().all()
    #
    # La riga porta **tutte** le colonne che la mappatura trasforma in una
    # PropertyNode, prese dalla mappatura stessa: l'asserzione in fondo le
    # pretende tutte, e una riga scritta a mano con sette colonne non puo'
    # soddisfarla — il test non era soddisfacibile prima di questo (ed era
    # muto, perche' il modulo non si importava).
    from s3dgraphy.sync.pyarchinit_pg_importer import _load_mapping as _lm
    fake_row = {
        "us": "1",
        "sito": "S",
        "d_stratigrafica": "test layer",
        "d_interpretativa": "test interp",
        "attivita": "AC1",
        "struttura": "STR1",
        "unita_tipo": "US",
        "node_uuid": "abc-123",
    }
    for _col, _spec in _lm("pyarchinit_us_mapping")["column_mappings"].items():
        if _spec.get("node_type") == "PropertyNode":
            fake_row.setdefault(_col, "valore di prova")
    fake_cm = MagicMock()
    fake_cm.execute.return_value.mappings.return_value.all.return_value = (
        [fake_row]
    )
    fake_engine = MagicMock()
    fake_engine.connect.return_value.__enter__.return_value = fake_cm
    fake_engine.connect.return_value.__exit__.return_value = None
    handle = MagicMock()
    handle.is_postgres = True
    handle.engine = fake_engine

    graph = import_from_pg(handle, sito="S",
                           mapping_name="pyarchinit_us_mapping")

    node_names = [getattr(n, "name", None) for n in graph.nodes]
    assert "1" in node_names, (
        f"StratigraphicNode named '1' missing — got {node_names}"
    )

    # Each PropertyNode-typed column from the mapping should produce a
    # node whose name is the property_name (e.g. 'Interpretation').
    from s3dgraphy.sync.pyarchinit_pg_importer import (
        _load_mapping,
    )
    mapping = _load_mapping("pyarchinit_us_mapping")
    prop_names_expected = {
        spec["property_name"]
        for spec in mapping["column_mappings"].values()
        if spec.get("node_type") == "PropertyNode"
    }
    found_prop_names = {
        getattr(n, "name", None)
        for n in graph.nodes
        if type(n).__name__ == "PropertyNode"
    }
    assert prop_names_expected.issubset(found_prop_names), (
        f"missing PropertyNodes: expected ⊇ {prop_names_expected}, "
        f"got {found_prop_names}"
    )


# ---------------------------------------------------------------------
# I due test `test_pg_export_graphml_*` che stavano qui sono stati tolti
# l'11 ottobre 2026. Provavano `export_graphml` importandolo da
# `modules.s3dgraphy.sync.graphml_writer`, che non esiste piu' da «One
# bridge» (2026-10-07): il writer vive solo nella libreria, e nel plugin
# `export_graphml` non ha piu' nessun chiamante — la matrice viaggia come
# em.json. Filtravano inoltre per `site_filter="Volterra"` mentre il sito
# di `mini_volterra.sqlite` e' `TestSite`, quindi le loro asserzioni
# sarebbero passate a vuoto.
#
# Il filtro del sito su PostgreSQL — la ragione per cui erano parcheggiati
# — e' coperto da `test_site_filter_pg.py`, contro il percorso che il
# plugin usa davvero (`em_export.export_site`).
