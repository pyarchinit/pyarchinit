# tests/sync/test_workspace_root.py
"""Consolidation 5.7.4-alpha: L0 unit tests for _resolve_workspace_root().

Verifies the 3-tier fallback chain:
  1. PYARCHINIT_WORKSPACE_DIR env var (highest priority)
  2. QSettings 'pyarchinit/paradata_workspace' (UI override) — NOT
     unit-tested here (would require Qt); manual verification in QGIS.
  3. Default: ~/pyarchinit/pyarchinit_DB_folder

All tests use monkeypatch.delenv/setenv for the env var layer and
do not depend on PG or Qt.
"""
from __future__ import annotations

from pathlib import Path


def test_default_when_env_and_qsettings_unset(monkeypatch):
    """With env var unset + QSettings unavailable (non-Qt env),
    _resolve_workspace_root() returns ~/pyarchinit/pyarchinit_DB_folder."""
    monkeypatch.delenv("PYARCHINIT_WORKSPACE_DIR", raising=False)
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    # In a pytest env, qgis.PyQt is not importable → QSettings layer
    # skipped via try/except ImportError. The default branch fires.
    assert root == Path.home() / "pyarchinit" / "pyarchinit_DB_folder"


def test_env_var_override_takes_precedence(monkeypatch, tmp_path):
    """Setting PYARCHINIT_WORKSPACE_DIR routes the root to that path."""
    custom = tmp_path / "custom_workspace"
    monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", str(custom))
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == custom


def test_empty_env_var_falls_through_to_default(monkeypatch):
    """An empty env var is treated as unset and the function falls
    through to the QSettings/default layers."""
    monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", "")
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    # Empty env var skipped → QSettings unavailable in pytest → default
    assert root == Path.home() / "pyarchinit" / "pyarchinit_DB_folder"


def test_env_var_with_tilde_expanded(monkeypatch):
    """Tilde-prefixed env var values are expanded via Path.expanduser()."""
    monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", "~/test_workspace_consol")
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == Path.home() / "test_workspace_consol"
    # Sanity: the tilde was actually expanded (not literal)
    assert "~" not in str(root)
