"""Public API for the s3dgraphy ↔ host-application SQL sync layer.

This package was moved from pyArchInit (issue #10) and provides a
backend-agnostic (SQLite + PostgreSQL via SQLAlchemy) bridge between
s3dgraphy Graph objects and the host application's relational tables.

Originally lived inside pyArchInit at
``modules/s3dgraphy/sync/``. Moved into the s3dgraphy package proper
in 1.6.0 after a Qt/QGIS decoupling pass — see
zalmoxes-laran/s3Dgraphy#10 for the design discussion.

pyArchInit-local note
---------------------
This is the pyArchInit *vendored* copy of ``s3dgraphy.sync`` (kept at
``modules/s3dgraphy/sync/`` so the ~80 ``modules.s3dgraphy.sync.*``
call sites stay unchanged — Phase 1 migration to 1.6.0.dev7). It mirrors
the upstream public surface and adds one pyArchInit-only symbol,
``get_vocab_provider`` (the Qt-aware wrapper in ``vocab_provider.py``,
which is not part of upstream). The canonical-edge files
(``rapporti.py``, ``graph_ingestor.py``, ``graph_projector.py``,
``graphml_writer.py``) are byte-copies of the dev7 wheel; ``_workspace``,
``edge_registry`` and ``pyarchinit_pg_importer`` carry deliberate
pyArchInit path/config adaptations and must NOT be overwritten from
upstream.

Public surface
==============

Vocabulary (Phase 1):
    VocabProviderCore, vocab dataclasses (EdgeType, Family,
    ParadataType, UnitType, VisualRule, VocabularyVersion)

DB handle (PG-Compat Foundation):
    DbHandle + exception hierarchy

Ingestion (GraphIngestor, the s3dgraphy ↔ SQL writer):
    GraphIngestor, IngestResult, ConflictRecord, ConflictResolution
    ConflictResolver
    YedOverrideResult, register_yed_override_hook,
    clear_yed_override_hook (Qt/GUI hook — host registers, library
    never imports Qt itself)

Projection (Graph ← SQL):
    GraphProjector, GroupProjector

Vocabulary (Qt — pyArchInit-local):
    get_vocab_provider (lazy Qt-aware singleton; not in upstream)

Errors:
    GraphSyncError, GraphIngestError, CycleDetectedError,
    SchemaMismatchError, UnknownUnitaTipoError, SiteMismatchError,
    MissingEpochError

Workspace configuration
-----------------------
``_workspace._resolve_workspace_root()`` (pyArchInit copy) resolves the
paradata workspace via a 3-tier fallback: the ``PYARCHINIT_WORKSPACE_DIR``
env var, then the QSettings key ``pyarchinit/paradata_workspace`` (UI
override), then the default ``~/pyarchinit/pyarchinit_DB_folder``. The
upstream package drops the QSettings tier to stay Qt-free; the vendored
copy keeps it because the plugin may import ``qgis.*``. The plugin also
mirrors the QSettings value into the env var at boot and on config-dialog
save — see ``modules/s3dgraphy/sync/README.md`` for the canonical wiring.

Dependency note
---------------
This subpackage requires SQLAlchemy 2.x. Install via the [sync]
extras::

    pip install s3dgraphy[sync]              # SQLite-only ingestion
    pip install s3dgraphy[sync,postgres]     # + Postgres backend

A friendly ``ImportError`` is raised on first use if SQLAlchemy is
missing.
"""
from __future__ import annotations

# Lazy SQLAlchemy probe with a friendly error — happens on package
# import; users who don't touch s3dgraphy.sync pay nothing.
try:
    import sqlalchemy as _sa  # noqa: F401
except ImportError as _e:  # pragma: no cover
    raise ImportError(
        "s3dgraphy.sync requires SQLAlchemy. Install via:\n"
        "    pip install s3dgraphy[sync]\n"
        "(add [postgres] extra for the PostgreSQL backend)"
    ) from _e

from ._db_handle import (
    DbHandle,
    DbHandleError,
    PgConnectionError,
    UnsupportedBackendError,
)
from .conflict_resolver import ConflictResolver
from .graph_ingestor import (
    CycleDetectedError,
    GraphIngestError,
    GraphIngestor,
    GraphSyncError,
    MissingEpochError,
    SchemaMismatchError,
    SiteMismatchError,
    UnknownUnitaTipoError,
    YedOverrideResult,
    clear_yed_override_hook,
    register_yed_override_hook,
)
from .graph_projector import GraphProjector
from .ingest_result import ConflictRecord, ConflictResolution, IngestResult
from .vocab_provider_core import VocabProviderCore
from .vocab_types import (
    EdgeType,
    Family,
    ParadataType,
    UnitType,
    VisualRule,
    VocabularyVersion,
)

__all__ = [
    # Vocabulary
    "VocabProviderCore",
    "EdgeType",
    "Family",
    "ParadataType",
    "UnitType",
    "VisualRule",
    "VocabularyVersion",
    # DB handle
    "DbHandle",
    "DbHandleError",
    "PgConnectionError",
    "UnsupportedBackendError",
    # Ingestion
    "GraphIngestor",
    "IngestResult",
    "ConflictRecord",
    "ConflictResolution",
    "ConflictResolver",
    # yEd override hook
    "YedOverrideResult",
    "register_yed_override_hook",
    "clear_yed_override_hook",
    # Projection
    "GraphProjector",
    # Vocabulary (Qt — pyArchInit-local)
    "get_vocab_provider",
    # Errors
    "GraphSyncError",
    "GraphIngestError",
    "CycleDetectedError",
    "SchemaMismatchError",
    "UnknownUnitaTipoError",
    "SiteMismatchError",
    "MissingEpochError",
]


# ---------------------------------------------------------------------------
# pyArchInit-local: Qt-aware vocabulary provider.
#
# The Qt wrapper (VocabProvider) lives in vocab_provider.py and is NOT part
# of upstream s3dgraphy.sync. It is imported lazily on first call so that
# pure-Python callers (tests, scripts, headless CLI) never pull Qt in at
# package-import time. ~7 pyArchInit call sites do
# ``from modules.s3dgraphy.sync import get_vocab_provider``.
# ---------------------------------------------------------------------------
def get_vocab_provider():
    """Return a process-wide Qt-aware VocabProvider singleton."""
    from .vocab_provider import get_default_provider
    return get_default_provider()
