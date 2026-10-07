"""Stub for the AI04 ConflictResolver. Always GRAPH_WINS."""
import pytest


def test_resolver_always_returns_graph_wins():
    from s3dgraphy.sync.conflict_resolver import ConflictResolver
    from s3dgraphy.sync.ingest_result import ConflictResolution
    resolver = ConflictResolver()
    # Even if every input differs:
    out = resolver.resolve(
        db_row={"d_stratigrafica": "old"},
        graph_value="new",
        field="d_stratigrafica",
    )
    assert out is ConflictResolution.GRAPH_WINS


def test_resolver_is_callable_with_any_field():
    from s3dgraphy.sync.conflict_resolver import ConflictResolver
    from s3dgraphy.sync.ingest_result import ConflictResolution
    resolver = ConflictResolver()
    assert resolver.resolve(db_row={}, graph_value=None,
                            field="anything") is ConflictResolution.GRAPH_WINS
