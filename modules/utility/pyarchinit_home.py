"""Single source of truth for the pyArchInit data-home directory.

The data home holds config.cfg, SQLite DBs, exports, backups, paradata and
the bin/ AI tooling. The branch defaults to ~/pyarchinit_5 so the legacy
master keeps ~/pyarchinit intact. Resolution: PYARCHINIT_HOME env var wins
(empty == unset), else the default. Dependency-free (os/shutil only) so it
imports at the very start of __init__.py and from standalone scripts.
"""
import os
import shutil

DEFAULT_HOME_NAME = "pyarchinit_5"
LEGACY_HOME_NAME = "pyarchinit"


def pyarchinit_home() -> str:
    """Resolved data-home base dir. Env var PYARCHINIT_HOME wins; else default."""
    env = os.environ.get("PYARCHINIT_HOME")
    if env:
        return env
    return os.path.join(os.path.expanduser("~"), DEFAULT_HOME_NAME)


def pyarchinit_home_bin() -> str:
    """`<home>/bin` — venvs, models, indexes, API keys."""
    return os.path.join(pyarchinit_home(), "bin")


def legacy_pyarchinit_home() -> str:
    """`~/pyarchinit` — the legacy master home (migration source only)."""
    return os.path.join(os.path.expanduser("~"), LEGACY_HOME_NAME)


def migrate_db_folder(src_home: str, dst_home: str) -> bool:
    """Copy `<src_home>/pyarchinit_DB_folder` into `<dst_home>/`.

    Returns True if the source DB folder existed and was copied. Uses
    dirs_exist_ok=True so a partially-created dst is tolerated. bin/ is NOT
    copied (heavy AI assets are reinstalled separately).
    """
    src_db = os.path.join(src_home, "pyarchinit_DB_folder")
    if not os.path.isdir(src_db):
        return False
    dst_db = os.path.join(dst_home, "pyarchinit_DB_folder")
    shutil.copytree(src_db, dst_db, dirs_exist_ok=True)
    return True


def should_offer_migration(home: str = None, legacy: str = None) -> bool:
    """Whether to offer copying the legacy install into the new data home.

    True when the new home has NO `pyarchinit_DB_folder/config.cfg` yet (i.e.
    not set up) but the legacy `~/pyarchinit` install has one. Keyed on
    config-file presence, NOT on base-dir existence, because the home base can
    be created early by unrelated code paths (paradata workspace mkdir, bin/
    creation) — a base-existence check would suppress the offer forever once
    any stray folder appeared. Once the new home has its own config.cfg
    (migrated or freshly installed) this returns False, so the user is never
    nagged again.
    """
    home = home or pyarchinit_home()
    legacy = legacy or legacy_pyarchinit_home()
    new_config = os.path.join(home, "pyarchinit_DB_folder", "config.cfg")
    legacy_config = os.path.join(legacy, "pyarchinit_DB_folder", "config.cfg")
    return (not os.path.isfile(new_config)) and os.path.isfile(legacy_config)
