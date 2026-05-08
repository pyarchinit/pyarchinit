"""Exception-hierarchy tests for graph_ingestor module.

Group C onwards adds tests for the GraphIngestor class itself.
"""
import pytest


def test_graph_sync_error_is_base_class():
    from modules.s3dgraphy.sync.graph_ingestor import (
        GraphSyncError, GraphIngestError)
    assert issubclass(GraphIngestError, GraphSyncError)


def test_specific_errors_inherit_graph_ingest_error():
    from modules.s3dgraphy.sync.graph_ingestor import (
        GraphIngestError,
        SchemaMismatchError,
        UnknownUnitaTipoError,
        SiteMismatchError,
        MissingEpochError,
    )
    for cls in (SchemaMismatchError, UnknownUnitaTipoError,
                SiteMismatchError, MissingEpochError):
        assert issubclass(cls, GraphIngestError), (
            f"{cls.__name__} must inherit GraphIngestError")


def test_mapped_columns_constant_present():
    from modules.s3dgraphy.sync.graph_ingestor import MAPPED_COLUMNS
    # The 12 columns spec §3.2 + risk row 5 enumerate.
    expected = {
        "us", "d_stratigrafica", "d_interpretativa", "attivita",
        "struttura", "sito", "area", "unita_tipo",
        "periodo_iniziale", "fase_iniziale", "rapporti", "node_uuid",
    }
    assert set(MAPPED_COLUMNS) == expected
    assert isinstance(MAPPED_COLUMNS, tuple)  # immutable


def test_missing_epoch_error_carries_epoch_list():
    from modules.s3dgraphy.sync.graph_ingestor import MissingEpochError
    err = MissingEpochError(missing=[(2, "3.1"), (3, "1")])
    assert err.missing == [(2, "3.1"), (3, "1")]
    assert "(2, '3.1')" in str(err) or "[(2," in str(err)
