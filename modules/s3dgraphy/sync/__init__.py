"""Public API for the pyarchinit ↔ s3dgraphy sync layer.

Phase 1 ships only the Vocabulary subsystem; SyncEngine, GraphProjector,
ParadataStore, ConflictResolver land in Phase 2-3 (see
docs/superpowers/specs/2026-05-04-s3dgraphy-bidirectional-sync-design.md).
"""
from __future__ import annotations

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
    "VocabProviderCore",
    "EdgeType",
    "Family",
    "ParadataType",
    "UnitType",
    "VisualRule",
    "VocabularyVersion",
]

# The Qt-aware wrapper (VocabProvider) is imported lazily on first call to
# get_vocab_provider() so that pure-Python callers (tests, scripts) avoid
# pulling Qt in at import time.


def get_vocab_provider():
    """Return a process-wide Qt-aware VocabProvider singleton."""
    from .vocab_provider import VocabProvider, get_default_provider
    return get_default_provider()
