"""Tests for VocabProviderCore (pure Python, no Qt)."""
from __future__ import annotations

from pathlib import Path

import pytest

from modules.s3dgraphy.sync.vocab_provider_core import VocabProviderCore
from modules.s3dgraphy.sync.vocab_types import Family


def test_loads_unit_types_from_node_datamodel(vocab_dir: Path, overrides_dir: Path):
    core = VocabProviderCore(bundled_dir=vocab_dir, overrides_dir=overrides_dir)
    types = core.get_unit_types()
    abbrevs = {ut.abbreviation for ut in types}
    assert {"US", "USVs"}.issubset(abbrevs)


def test_filters_unit_types_by_family(vocab_dir: Path, overrides_dir: Path):
    core = VocabProviderCore(bundled_dir=vocab_dir, overrides_dir=overrides_dir)
    strat = core.get_unit_types(family=Family.STRATIGRAPHIC)
    assert all(ut.family is Family.STRATIGRAPHIC for ut in strat)


def test_handles_legacy_filename_with_trailing_space(tmp_path: Path,
                                                      node_datamodel_path: Path,
                                                      overrides_dir: Path):
    """0.1.30 had a typo: 's3Dgraphy_node_datamodel .json' (trailing space).
    VocabProviderCore must accept both filenames."""
    legacy_dir = tmp_path / "JSON_config"
    legacy_dir.mkdir()
    (legacy_dir / "s3Dgraphy_node_datamodel .json").write_bytes(
        node_datamodel_path.read_bytes())
    core = VocabProviderCore(bundled_dir=legacy_dir, overrides_dir=overrides_dir)
    types = core.get_unit_types()
    assert any(ut.abbreviation == "US" for ut in types)
