"""One bridge (A1): the shared modules come from the library.

The ten modules measured identical on 2026-10-07 are deleted from the
vendored package; a transitional alias keeps the old import path alive
until A5 rewires the callers.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for entry in (str(_ROOT), str(_ROOT / "ext_libs")):
    if entry not in sys.path:
        sys.path.append(entry)

pytest.importorskip("s3dgraphy.sync")

FREE_WINS = ("yed_group_walker", "yed_detector", "vocab_types",
             "vocab_provider_core", "uuid7", "ingest_result",
             "group_store", "conflict_resolver",
             "_legacy_paradata_svgs", "_db_handle")


def test_the_identical_modules_are_gone_from_the_vendored_package():
    for name in FREE_WINS:
        assert not (_ROOT / "modules" / "s3dgraphy" / "sync" / (name + ".py")).exists(), name


def test_the_old_import_path_resolves_to_the_library():
    # File identity, not object identity: several sync tests purge
    # s3dgraphy* from sys.modules on purpose (conftest included), which
    # splits the module OBJECTS while both still come from the library's
    # file — the claim that matters here.
    import importlib
    for name in FREE_WINS:
        ours = importlib.import_module("modules.s3dgraphy.sync." + name)
        libs = importlib.import_module("s3dgraphy.sync." + name)
        assert Path(ours.__file__).resolve() == Path(libs.__file__).resolve(), name
        assert "ext_libs" in str(Path(ours.__file__).resolve()), name
