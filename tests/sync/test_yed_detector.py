"""yE-A Foundation: L0 unit tests for detect_flavor().

Verifies the 5 acceptance criteria:
  1. pyarchinit-projected graphml (existing AC-2 baseline fixture)
     is detected as "pyarchinit-projected" via its pyarchinit.us /
     pyarchinit.area / pyarchinit.sito etc. key declarations.
  2. yEd-raw graphml (NEW em_demo_02_mini fixture, zero pyarchinit.*
     keys) is detected as "yed-raw".
  3. Malformed XML returns "yed-raw" (safe default, lets the
     downstream pipeline surface the problem to the user).
  4. Empty file returns "yed-raw" (safe default).
  5. Missing file returns "yed-raw" (safe default — no exception
     leaks out of the detector).

The detection marker is presence of ANY pyarchinit.* key, NOT
specifically pyarchinit.node_uuid (that key is conditionally
emitted; the namespace prefix is the robust marker).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from s3dgraphy.sync.yed_detector import detect_flavor

FIXTURES = Path(__file__).parent / "fixtures"


def test_detect_pyarchinit_projected_via_us_key():
    """The AC-2 baseline graphml has 'pyarchinit.us', 'pyarchinit.area',
    'pyarchinit.sito' etc. key declarations -> detect_flavor must
    return 'pyarchinit-projected'."""
    baseline = FIXTURES / "mini_volterra_baseline_ai03.graphml"
    assert baseline.exists(), f"Expected fixture at {baseline}"
    assert detect_flavor(baseline) == "pyarchinit-projected"


def test_detect_yed_raw_em_demo_02_mini():
    """The yE-A mini fixture has zero pyarchinit.* keys -> 'yed-raw'."""
    fixture = FIXTURES / "em_demo_02_mini.graphml"
    assert fixture.exists(), f"Expected fixture at {fixture}"
    assert detect_flavor(fixture) == "yed-raw"


def test_detect_malformed_falls_back_to_yed_raw(tmp_path):
    """Truncated XML mid-tag -> safe default 'yed-raw' (no exception)."""
    bad = tmp_path / "broken.graphml"
    bad.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n'
        '  <key id="d0" attr.nam'  # truncated mid-attribute
    )
    assert detect_flavor(bad) == "yed-raw"


def test_detect_empty_file_returns_yed_raw(tmp_path):
    """Empty file -> safe default 'yed-raw'."""
    empty = tmp_path / "empty.graphml"
    empty.write_text("")
    assert detect_flavor(empty) == "yed-raw"


def test_detect_missing_file_returns_yed_raw(tmp_path):
    """Non-existent path -> safe default 'yed-raw' (no FileNotFoundError leak)."""
    missing = tmp_path / "does_not_exist.graphml"
    assert not missing.exists()
    assert detect_flavor(missing) == "yed-raw"
