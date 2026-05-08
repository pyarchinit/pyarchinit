"""AC-2 regression guard: AI03 export pipeline must keep producing
GraphML byte-identical (modulo line endings and trailing whitespace)
to the pre-AI04 baseline captured at Group 0 of the AI04 plan.

If this test ever goes red, AI04 has regressed AI03 — block on it.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

import pandas  # noqa: F401
from lxml import etree as _etree  # noqa: F401
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_EXT_LIBS = str(PLUGIN_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)
for _mod in [m for m in list(sys.modules)
             if m == "s3dgraphy" or m.startswith("s3dgraphy.")]:
    del sys.modules[_mod]

FIXTURE_DB = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
              / "mini_volterra.sqlite")
BASELINE = (PLUGIN_ROOT / "tests" / "sync" / "fixtures"
            / "mini_volterra_baseline_ai03.graphml")


def _normalise(text: str) -> str:
    """Strip volatile bits: line endings, trailing whitespace,
    UUID-like ids that the writer regenerates per run."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = re.sub(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        "<UUID>",
        text,
    )
    return text.strip()


def test_export_graphml_matches_baseline(tmp_path):
    import shutil
    from modules.s3dgraphy.sync.graphml_writer import export_graphml
    db = tmp_path / "mini_volterra.sqlite"
    shutil.copy2(FIXTURE_DB, db)
    out = tmp_path / "out.graphml"
    export_graphml(db_path=db, mapping="pyarchinit_us_mapping",
                   output_path=out)
    actual = _normalise(out.read_text(encoding="utf-8"))
    baseline = _normalise(BASELINE.read_text(encoding="utf-8"))
    assert actual == baseline, (
        f"AI03 GraphML output drifted from baseline "
        f"(actual={len(actual)} chars, baseline={len(baseline)} chars). "
        f"AI04 has regressed AI03 — investigate."
    )
