"""Smoke test against the real bundled 0.1.40 JSON_config/.

Skipped if the vendored s3dgraphy is not present (e.g. tests run from a
fresh clone before pip install --target).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from modules.s3dgraphy.sync.vocab_provider_core import VocabProviderCore
from modules.s3dgraphy.sync.vocab_types import Family

BUNDLED = (Path(__file__).resolve().parents[2]
           / "ext_libs" / "s3dgraphy" / "JSON_config")


@pytest.mark.skipif(not BUNDLED.is_dir(),
                    reason="ext_libs/s3dgraphy/JSON_config/ not present")
def test_real_bundled_loads_us_and_usvs(tmp_path):
    core = VocabProviderCore(bundled_dir=BUNDLED, overrides_dir=tmp_path)
    abbrevs = {ut.abbreviation for ut in core.get_unit_types(family=Family.STRATIGRAPHIC)}
    # Must contain the canonical EM 1.5 stratigraphic types
    assert "US" in abbrevs
    assert "USVs" in abbrevs
    assert "USVn" in abbrevs


@pytest.mark.skipif(not BUNDLED.is_dir(),
                    reason="ext_libs/s3dgraphy/JSON_config/ not present")
def test_real_bundled_versions_present(tmp_path):
    core = VocabProviderCore(bundled_dir=BUNDLED, overrides_dir=tmp_path)
    v = core.versions
    assert v.nodes  # non-empty
