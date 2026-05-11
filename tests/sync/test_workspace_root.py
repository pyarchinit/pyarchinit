# tests/sync/test_workspace_root.py
"""Consolidation 5.7.4-alpha: L0 unit tests for _resolve_workspace_root().

Verifies the 3-tier fallback chain:
  1. PYARCHINIT_WORKSPACE_DIR env var (highest priority)
  2. QSettings 'pyarchinit/paradata_workspace' (UI override)
  3. Default: ~/pyarchinit/pyarchinit_DB_folder

Env-var and default branches: covered by direct env manipulation with
monkeypatch.delenv/setenv (no Qt required).

QSettings branch: covered by injecting a fake `qgis.PyQt.QtCore` module
into sys.modules via monkeypatch.setitem (still no Qt runtime required).
These tests verify both the success path AND the defensive fall-through
when QSettings instantiation raises at runtime (e.g., Qt installed but
no QCoreApplication).

NOTE on running pytest from inside QGIS: in that exotic environment the
real `qgis` module is importable, which would activate the QSettings
tier. The tests that assume the default branch fires (without an
explicit QSettings mock) would then read whatever value happens to be
stored in the user's QSettings. The test suite is intended to run in
non-Qt envs; if you must run inside QGIS, expect those tests to depend
on the runtime QSettings state.
"""
from __future__ import annotations

import sys
import types

from pathlib import Path


def test_default_when_env_and_qsettings_unset(monkeypatch):
    """With env var unset + QSettings unavailable (non-Qt env),
    _resolve_workspace_root() returns ~/pyarchinit/pyarchinit_DB_folder."""
    monkeypatch.delenv("PYARCHINIT_WORKSPACE_DIR", raising=False)
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    # In a pytest env, qgis.PyQt is not importable -> QSettings layer
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
    # Empty env var skipped -> QSettings unavailable in pytest -> default
    assert root == Path.home() / "pyarchinit" / "pyarchinit_DB_folder"


def test_env_var_with_tilde_expanded(monkeypatch):
    """Tilde-prefixed env var values are expanded via Path.expanduser()."""
    monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", "~/test_workspace_consol")
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == Path.home() / "test_workspace_consol"
    # Sanity: the tilde was actually expanded (not literal)
    assert "~" not in str(root)


def _install_fake_qgis_qsettings(monkeypatch, qsettings_class):
    """Inject a fake `qgis.PyQt.QtCore.QSettings` into sys.modules.

    Use monkeypatch.setitem so the entries are removed after the test,
    restoring the original (non-importable in non-Qt envs) state.
    """
    fake_qtcore = types.ModuleType("qgis.PyQt.QtCore")
    fake_qtcore.QSettings = qsettings_class
    fake_pyqt = types.ModuleType("qgis.PyQt")
    fake_pyqt.QtCore = fake_qtcore
    fake_qgis = types.ModuleType("qgis")
    fake_qgis.PyQt = fake_pyqt
    monkeypatch.setitem(sys.modules, "qgis", fake_qgis)
    monkeypatch.setitem(sys.modules, "qgis.PyQt", fake_pyqt)
    monkeypatch.setitem(sys.modules, "qgis.PyQt.QtCore", fake_qtcore)


def test_qsettings_tier_returns_override_when_env_var_unset(
    monkeypatch, tmp_path,
):
    """QSettings tier fires when env var is unset and QSettings returns
    a non-empty value for 'pyarchinit/paradata_workspace'."""
    monkeypatch.delenv("PYARCHINIT_WORKSPACE_DIR", raising=False)
    custom = tmp_path / "qsettings_workspace"

    class _FakeQSettings:
        def value(self, key, default=""):
            if key == "pyarchinit/paradata_workspace":
                return str(custom)
            return default

    _install_fake_qgis_qsettings(monkeypatch, _FakeQSettings)
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == custom


def test_qsettings_tier_runtime_error_falls_through(monkeypatch):
    """If `qgis.PyQt.QtCore` imports cleanly but `QSettings()` raises at
    runtime (e.g., Qt installed but no QCoreApplication), the defensive
    inner try/except swallows the error and falls through to the
    default branch."""
    monkeypatch.delenv("PYARCHINIT_WORKSPACE_DIR", raising=False)

    class _ExplodingQSettings:
        def __init__(self):
            raise RuntimeError("No QCoreApplication exists")

    _install_fake_qgis_qsettings(monkeypatch, _ExplodingQSettings)
    from modules.s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == Path.home() / "pyarchinit" / "pyarchinit_DB_folder"
