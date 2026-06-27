"""L0 unit tests for the data-home resolver (pyarchinit_5 rename)."""
import os
from pathlib import Path

from modules.utility.pyarchinit_home import (
    pyarchinit_home, pyarchinit_home_bin, legacy_pyarchinit_home,
    migrate_db_folder, should_offer_migration, DEFAULT_HOME_NAME,
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


# --- should_offer_migration -------------------------------------------------

def test_offer_migration_when_new_unset_legacy_present(tmp_path):
    home = tmp_path / "pyarchinit_5"
    legacy = tmp_path / "pyarchinit"
    (legacy / "pyarchinit_DB_folder").mkdir(parents=True)
    (legacy / "pyarchinit_DB_folder" / "config.cfg").write_text("x")
    assert should_offer_migration(str(home), str(legacy)) is True


def test_offer_migration_even_when_base_precreated(tmp_path):
    # The bug this fixes: the base dir was created early by other code paths
    # (paradata workspace mkdir, bin/ creation) but no config.cfg exists yet —
    # migration must still be offered.
    home = tmp_path / "pyarchinit_5"
    (home / "bin").mkdir(parents=True)   # base pre-created, NO config.cfg
    legacy = tmp_path / "pyarchinit"
    (legacy / "pyarchinit_DB_folder").mkdir(parents=True)
    (legacy / "pyarchinit_DB_folder" / "config.cfg").write_text("x")
    assert should_offer_migration(str(home), str(legacy)) is True


def test_no_offer_when_new_config_present(tmp_path):
    home = tmp_path / "pyarchinit_5"
    (home / "pyarchinit_DB_folder").mkdir(parents=True)
    (home / "pyarchinit_DB_folder" / "config.cfg").write_text("already set up")
    legacy = tmp_path / "pyarchinit"
    (legacy / "pyarchinit_DB_folder").mkdir(parents=True)
    (legacy / "pyarchinit_DB_folder" / "config.cfg").write_text("x")
    assert should_offer_migration(str(home), str(legacy)) is False


def test_no_offer_when_legacy_absent(tmp_path):
    home = tmp_path / "pyarchinit_5"
    legacy = tmp_path / "pyarchinit"   # no DB folder / config
    assert should_offer_migration(str(home), str(legacy)) is False


# --- install_dir full-tree + idempotency (the fix relies on this) -----------

def test_install_dir_creates_full_tree_and_is_idempotent(tmp_path, monkeypatch):
    from modules.utility.pyarchinit_folder_installation import (
        pyarchinit_Folder_installation)
    home = tmp_path / "pyarchinit_5"
    monkeypatch.setattr(pyarchinit_Folder_installation, "HOME", str(home))
    fi = pyarchinit_Folder_installation()

    fi.install_dir()

    expected = [
        "pyarchinit_DB_folder", "bin", "DosCo", "pyarchinit_EXCEL_folder",
        "pyarchinit_PDF_folder", "pyarchinit_Matrix_folder",
        "pyarchinit_Thumbnails_folder", "pyarchinit_MAPS_folder",
        "pyarchinit_Report_folder", "pyarchinit_Quantificazioni_folder",
        "pyarchinit_Test_folder", "pyarchinit_db_backup",
        "pyarchinit_image_export", "pyarchinit_R_export",
    ]
    for sub in expected:
        assert (home / sub).is_dir(), f"install_dir did not create {sub}"
    assert (home / "pyarchinit_DB_folder" / "pyarchinit_db.sqlite").is_file()

    # Idempotent + non-clobbering: a second call must not raise and must
    # preserve a user-edited file (copy_file skips existing).
    user_cfg = home / "pyarchinit_DB_folder" / "config.cfg"
    user_cfg.write_text("USER EDIT")
    fi.install_dir()
    assert user_cfg.read_text() == "USER EDIT"
