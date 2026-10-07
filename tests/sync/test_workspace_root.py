# tests/sync/test_workspace_root.py
"""L0 unit tests for _resolve_workspace_root().

One bridge (A1): the resolver is the library's and reads ONE env var
(s3dgraphy #10 dropped the QSettings and PYARCHINIT_HOME tiers to stay
free of qgis.* / PyQt* imports):
  1. PYARCHINIT_WORKSPACE_DIR env var (highest priority)
  2. Default: ~/pyarchinit/pyarchinit_DB_folder

"The workspace follows the data home" is now the HOST's duty: the
plugin's __init__ mirrors PYARCHINIT_HOME into PYARCHINIT_WORKSPACE_DIR
(setdefault, so an external value wins) — pinned here at source level,
since importing the plugin __init__ needs QGIS.
"""
from __future__ import annotations

from pathlib import Path


def test_default_when_env_unset(monkeypatch):
    """With both env vars unset, the root defaults to
    ~/pyarchinit_5/pyarchinit_DB_folder."""
    monkeypatch.delenv("PYARCHINIT_WORKSPACE_DIR", raising=False)
    monkeypatch.delenv("PYARCHINIT_HOME", raising=False)
    from s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == Path.home() / "pyarchinit" / "pyarchinit_DB_folder"


def test_env_var_override_takes_precedence(monkeypatch, tmp_path):
    """Setting PYARCHINIT_WORKSPACE_DIR routes the root to that path."""
    custom = tmp_path / "custom_workspace"
    monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", str(custom))
    from s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == custom


def test_empty_env_var_falls_through_to_default(monkeypatch):
    """Empty workspace + home env vars fall through to the default."""
    monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", "")
    monkeypatch.delenv("PYARCHINIT_HOME", raising=False)
    from s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == Path.home() / "pyarchinit" / "pyarchinit_DB_folder"


def test_env_var_with_tilde_expanded(monkeypatch):
    """Tilde-prefixed env var values are expanded via Path.expanduser()."""
    monkeypatch.setenv("PYARCHINIT_WORKSPACE_DIR", "~/test_workspace_consol")
    from s3dgraphy.sync._workspace import _resolve_workspace_root
    root = _resolve_workspace_root()
    assert root == Path.home() / "test_workspace_consol"
    # Sanity: the tilde was actually expanded (not literal)
    assert "~" not in str(root)


def test_the_plugin_mirrors_the_data_home_into_the_env_var():
    """The host-side half of the contract: pyArchInit's __init__ mirrors
    PYARCHINIT_HOME into PYARCHINIT_WORKSPACE_DIR with setdefault (an
    externally-set value wins)."""
    import re
    root = Path(__file__).resolve().parents[2]
    src = (root / "__init__.py").read_text(encoding="utf-8")
    m = re.search(r"os\.environ\.setdefault\('PYARCHINIT_WORKSPACE_DIR',\s*"
                  r"os\.path\.join\(PYARCHINIT_HOME, 'pyarchinit_DB_folder'\)\)", src)
    assert m, "lo specchio host PYARCHINIT_HOME -> PYARCHINIT_WORKSPACE_DIR manca in __init__.py"
