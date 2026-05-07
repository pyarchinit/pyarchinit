"""Fixture-based pipeline tests for graphml_writer.

Each of the four tests pins one acceptance criterion from the AI03
spec §7.2 / dev-log limitations L1–L4. They run pure pytest (no
QGIS) against the committed mini_volterra.sqlite.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

# Two-step path setup:
#  1. Import pandas FIRST from the system. This pins it in
#     sys.modules so the broken vendored ext_libs/pandas is never
#     resolved on subsequent imports.
#  2. Insert ext_libs at the FRONT of sys.path. The active site-
#     packages s3dgraphy is 0.1.15 (no `exporter.graphml`); we need
#     ext_libs/s3dgraphy 0.1.40 to win, so a plain `append` would
#     leave the older copy in front.
import pandas  # noqa: F401 — pin system pandas before any s3dgraphy import
from lxml import etree as _etree  # noqa: F401 — same trick for lxml
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
# Evict any pre-loaded older s3dgraphy from sys.modules so the next
# `import s3dgraphy.*` rebinds against ext_libs/.
for _mod in [m for m in list(sys.modules) if m == "s3dgraphy"
             or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

FIXTURE_DB = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
              / "mini_volterra.sqlite")


@pytest.fixture
def mini_volterra(tmp_path):
    """Copy the committed fixture to tmp_path so tests don't mutate it."""
    import shutil
    dst = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, dst)
    return dst


def test_pipeline_produces_populated_graphml(mini_volterra, tmp_path):
    """L1 — the new pipeline must produce a non-empty .graphml.

    Closes the empty-on-grouping-flag bug from Phase 1.
    """
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    out = tmp_path / "out.graphml"
    result = export_graphml(
        db_path=mini_volterra,
        mapping="pyarchinit_us_mapping",
        output_path=out,
    )
    assert out.exists()
    # Legacy bug produced 0-byte files; threshold of 1 KB is well above
    # the empty-document baseline of any GraphML header alone.
    assert out.stat().st_size > 1000
    assert result.node_count > 0
    assert result.edge_count > 0


def test_pipeline_emits_epoch_swimlanes(mini_volterra, tmp_path):
    """L2 — closes 'no period swimlanes' limitation.

    GraphMLExporter wraps strat nodes inside a TableNode swimlane;
    each EpochNode becomes a row inside the table. Look for a
    TableNode marker in the produced XML and assert epoch_count
    matches the fixture's two periods.
    """
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    out = tmp_path / "out.graphml"
    result = export_graphml(
        db_path=mini_volterra, mapping="pyarchinit_us_mapping",
        output_path=out)
    xml = out.read_text(encoding="utf-8")
    assert ("TableNode" in xml or 'yfiles.foldertype="row"' in xml), (
        "no swimlane marker found in output")
    assert result.epoch_count >= 2, (
        f"expected >=2 epochs, got {result.epoch_count}")
