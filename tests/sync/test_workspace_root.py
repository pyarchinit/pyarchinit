# tests/sync/test_workspace_root.py
"""L0 unit tests for _resolve_workspace_root().

Verifies the 3-tier fallback chain (Consolidation 5.7.4-alpha, simplified
in s3dgraphy #10 decoupling; data-home rename 2026-06-27):
  1. PYARCHINIT_WORKSPACE_DIR env var (highest priority)
  2. PYARCHINIT_HOME env var (data-home override)
  3. Default: ~/pyarchinit_5/pyarchinit_DB_folder

The previous QSettings tier was removed so this module stays free of
`qgis.*` / `PyQt*` imports (s3dgraphy policy). The host application
(pyArchInit's QGIS plugin) is now responsible for mirroring the
QSettings 'pyarchinit/paradata_workspace' value into the env var at
plugin init + on every config-dialog save.
"""
from __future__ import annotations

from pathlib import Path


def test_default_when_env_unset(monkeypatch):
    """With both env vars unset, the root defaults to
    ~/pyarchinit_5/pyarchinit_DB_folder."""
    monkeypatch.delenv("PYARCHINIT_WORKSPACE_DIR", raising=False)
    monkeypatch.delenv("PYARCHINIT_HOME", raising=False)
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == Path.home() / "pyarchinit_5" / "pyarchinit_DB_folder"


def test_env_var_override_takes_precedence(monkeypatch, tmp_path):
    """Setting PYARCHINIT_WORKSPACE_DIR routes the root to that path."""
    custom = tmp_path / "custom_workspace"
    monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", str(custom))
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == custom


def test_empty_env_var_falls_through_to_default(monkeypatch):
    """Empty workspace + home env vars fall through to the default."""
    monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", "")
    monkeypatch.delenv("PYARCHINIT_HOME", raising=False)
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == Path.home() / "pyarchinit_5" / "pyarchinit_DB_folder"


def test_env_var_with_tilde_expanded(monkeypatch):
    """Tilde-prefixed env var values are expanded via Path.expanduser()."""
    monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", "~/test_workspace_consol")
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == Path.home() / "test_workspace_consol"
    # Sanity: the tilde was actually expanded (not literal)
    assert "~" not in str(root)


def test_pyarchinit_home_env_drives_default(monkeypatch, tmp_path):
    """When PYARCHINIT_WORKSPACE_DIR is unset, PYARCHINIT_HOME drives the base."""
    monkeypatch.delenv("PYARCHINIT_WORKSPACE_DIR", raising=False)
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path / "h"))
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == tmp_path / "h" / "pyarchinit_DB_folder"
