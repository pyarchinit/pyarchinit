"""Unit tests for IngestResult + ConflictRecord + ConflictResolution.
Pure dataclass invariants. No DB, no QGIS."""
import pytest


def test_conflict_resolution_enum_has_three_members():
    from s3dgraphy.sync.ingest_result import ConflictResolution
    assert ConflictResolution.GRAPH_WINS.value == "graph_wins"
    assert ConflictResolution.DB_WINS.value == "db_wins"
    assert ConflictResolution.SKIPPED.value == "skipped"


def test_conflict_record_is_frozen():
    from s3dgraphy.sync.ingest_result import ConflictRecord
    cr = ConflictRecord(
        node_uuid="abc-123",
        field="d_stratigrafica",
        db_value="Materiale",
        graph_value="Strato",
        resolution="graph_wins",
    )
    with pytest.raises(Exception):  # frozen → FrozenInstanceError
        cr.field = "other"
    assert cr.node_uuid == "abc-123"
    assert cr.resolution == "graph_wins"


def test_ingest_result_default_values():
    from s3dgraphy.sync.ingest_result import IngestResult
    r = IngestResult(applied=0, inserted=0, updated=0, skipped=0,
                     epochs_created=0)
    assert r.conflicts == ()
    assert r.errors == ()
    assert r.dry_run is False


def test_ingest_result_is_frozen():
    from s3dgraphy.sync.ingest_result import IngestResult
    r = IngestResult(applied=5, inserted=3, updated=2, skipped=0,
                     epochs_created=0)
    with pytest.raises(Exception):
        r.applied = 99


def test_ingest_result_with_conflicts():
    from s3dgraphy.sync.ingest_result import (
        IngestResult, ConflictRecord)
    cr = ConflictRecord(node_uuid="u1", field="f", db_value=1,
                        graph_value=2, resolution="graph_wins")
    r = IngestResult(applied=1, inserted=0, updated=1, skipped=0,
                     epochs_created=0, conflicts=(cr,))
    assert len(r.conflicts) == 1
    assert r.conflicts[0].node_uuid == "u1"
