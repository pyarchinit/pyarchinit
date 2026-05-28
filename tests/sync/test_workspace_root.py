# tests/sync/test_workspace_root.py
"""L0 unit tests for _resolve_workspace_root().

Verifies the 2-tier fallback chain (Consolidation 5.7.4-alpha, simplified
in s3dgraphy #10 decoupling):
  1. PYARCHINIT_WORKSPACE_DIR env var (highest priority)
  2. Default: ~/pyarchinit/pyarchinit_DB_folder

The previous QSettings tier was removed so this module stays free of
`qgis.*` / `PyQt*` imports (s3dgraphy policy). The host application
(pyArchInit's QGIS plugin) is now responsible for mirroring the
QSettings 'pyarchinit/paradata_workspace' value into the env var at
plugin init + on every config-dialog save.
"""
from __future__ import annotations

from pathlib import Path


def test_default_when_env_unset(monkeypatch):
    """With env var unset, _resolve_workspace_root() returns
    ~/pyarchinit/pyarchinit_DB_folder."""
    monkeypatch.delenv("PYARCHINIT_WORKSPACE_DIR", raising=False)
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
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
    through to the default."""
    monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", "")
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == Path.home() / "pyarchinit" / "pyarchinit_DB_folder"


def test_env_var_with_tilde_expanded(monkeypatch):
    """Tilde-prefixed env var values are expanded via Path.expanduser()."""
    monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", "~/test_workspace_consol")
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == Path.home() / "test_workspace_consol"
    # Sanity: the tilde was actually expanded (not literal)
    assert "~" not in str(root)
