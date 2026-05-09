"""Shared pytest fixtures for tests/sync/.

The bootstrap below mirrors what `test_ai03_export_byte_identical.py`
does manually: it forces all sync tests to use the vendored
`ext_libs/s3dgraphy` (currently 0.1.41) instead of any system
pip-installed s3dgraphy that may be present in `site-packages`.

This is required because AI07 introduces `LocationNodeGroup` and
`is_in_location` symbols that only exist in 0.1.41+. Without this
bootstrap, sync tests would import an older s3dgraphy from
site-packages and fail with `ImportError: cannot import name
'LocationNodeGroup'`.

NOTE: `pandas` and `lxml.etree` are pre-imported BEFORE we prepend
`ext_libs/` to `sys.path`. This pins the system pip-installed versions
(which work) and prevents Python from later picking up the vendored
copies under `ext_libs/` (which ship without compiled native extensions
and would `ImportError` on this dev machine). Same trick used in
`test_ai03_export_byte_identical.py`.
"""
from __future__ import annotations

# Pin system pandas + lxml BEFORE the ext_libs prepend below — see module docstring.
import pandas  # noqa: F401
from lxml import etree as _etree  # noqa: F401

import json
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def node_datamodel_path() -> Path:
    return FIXTURES / "node_datamodel_sample.json"


@pytest.fixture
def connections_datamodel_path() -> Path:
    return FIXTURES / "connections_datamodel_sample.json"


@pytest.fixture
def visual_rules_path() -> Path:
    return FIXTURES / "em_visual_rules_sample.json"


@pytest.fixture
def vocab_dir(tmp_path: Path,
              node_datamodel_path: Path,
              connections_datamodel_path: Path,
              visual_rules_path: Path) -> Path:
    """Create an isolated JSON_config/ directory holding sample fixtures."""
    out = tmp_path / "JSON_config"
    out.mkdir()
    (out / "s3Dgraphy_node_datamodel.json").write_bytes(node_datamodel_path.read_bytes())
    (out / "s3Dgraphy_connections_datamodel.json").write_bytes(connections_datamodel_path.read_bytes())
    (out / "em_visual_rules.json").write_bytes(visual_rules_path.read_bytes())
    return out


@pytest.fixture
def overrides_dir(tmp_path: Path) -> Path:
    out = tmp_path / "vocab_overrides"
    out.mkdir()
    return out
