# -*- coding: utf-8 -*-
"""
StratiGraph integration module for PyArchInit.

Provides UUID management, bundle export, validation, and sync
capabilities for the StratiGraph Horizon Europe project.
"""

# Phase 1 — UUID & bundle
from .uuid_manager import generate_uuid, validate_uuid, ensure_uuid, build_uri
from .bundle_creator import BundleCreator
from .bundle_validator import BundleValidator, validate_bundle

# Phase 2 — Offline-first sync
from .sync_state_machine import SyncState, SyncStateMachine
from .sync_queue import SyncQueue, QueueEntry
from .connectivity_monitor import ConnectivityMonitor
from .sync_orchestrator import SyncOrchestrator
