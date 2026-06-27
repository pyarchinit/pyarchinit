"""L0 unit tests for the data-home resolver (pyarchinit_5 rename)."""
import os
from pathlib import Path

from modules.utility.pyarchinit_home import (
    pyarchinit_home, pyarchinit_home_bin, legacy_pyarchinit_home,
    migrate_db_folder, DEFAULT_HOME_NAME,
)


def test_default_when_env_unset(monkeypatch):
    monkeypatch.delenv("PYARCHINIT_HOME", raising=False)
    assert pyarchinit_home() == os.path.join(os.path.expanduser("~"), "pyarchinit_5")
    assert DEFAULT_HOME_NAME == "pyarchinit_5"


def test_env_var_override_wins(monkeypatch, tmp_path):
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path / "custom_home"))
    assert pyarchinit_home() == str(tmp_path / "custom_home")


def test_empty_env_falls_through_to_default(monkeypatch):
    monkeypatch.setenv("PYARCHINIT_HOME", "")
    assert pyarchinit_home() == os.path.join(os.path.expanduser("~"), "pyarchinit_5")


def test_bin_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path / "h"))
    assert pyarchinit_home_bin() == str(tmp_path / "h" / "bin")


def test_legacy_home():
    assert legacy_pyarchinit_home() == os.path.join(os.path.expanduser("~"), "pyarchinit")


def test_migrate_db_folder_copies(tmp_path):
    src = tmp_path / "pyarchinit"
    (src / "pyarchinit_DB_folder").mkdir(parents=True)
    (src / "pyarchinit_DB_folder" / "config.cfg").write_text("X")
    dst = tmp_path / "pyarchinit_5"
    assert migrate_db_folder(str(src), str(dst)) is True
    assert (dst / "pyarchinit_DB_folder" / "config.cfg").read_text() == "X"


def test_migrate_db_folder_no_source(tmp_path):
    src = tmp_path / "pyarchinit"   # no pyarchinit_DB_folder inside
    src.mkdir()
    dst = tmp_path / "pyarchinit_5"
    assert migrate_db_folder(str(src), str(dst)) is False


def test_migrate_db_folder_source_wins_on_conflict(tmp_path):
    # Documents behaviour for the (real-flow-impossible) case where dst already
    # has the file: copytree(dirs_exist_ok=True) overwrites with the source.
    # In production migrate runs only when the new home is absent, so no
    # destination file pre-exists — this just pins the overwrite semantics.
    src = tmp_path / "pyarchinit"
    (src / "pyarchinit_DB_folder").mkdir(parents=True)
    (src / "pyarchinit_DB_folder" / "config.cfg").write_text("NEW")
    dst = tmp_path / "pyarchinit_5"
    (dst / "pyarchinit_DB_folder").mkdir(parents=True)
    (dst / "pyarchinit_DB_folder" / "config.cfg").write_text("KEEP")
    migrate_db_folder(str(src), str(dst))
    assert (dst / "pyarchinit_DB_folder" / "config.cfg").read_text() == "NEW"
