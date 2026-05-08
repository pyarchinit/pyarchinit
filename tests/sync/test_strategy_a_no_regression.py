"""L3 regression guards for Strategy A promotion (D7).

After AI05 Group C, the standalone _enrich_pyarchinit_graph function
must NOT exist in production code. Its body lives inside
GraphProjector._enrich_into. The AI03 export_graphml() path uses
GraphProjector().populate_graph(..., include_paradata=False) to
preserve byte-equivalent output.
"""
from __future__ import annotations
import re
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]


def test_enrich_function_removed():
    """D7: the standalone _enrich_pyarchinit_graph function must NOT
    exist anywhere in production code (modules/, scripts/, tabs/,
    gui/)."""
    forbidden = "_enrich_pyarchinit_graph"
    hits = []
    for sub in ("modules", "scripts", "tabs", "gui"):
        sub_path = PLUGIN_ROOT / sub
        if not sub_path.exists():
            continue
        for py in sub_path.rglob("*.py"):
            try:
                text = py.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            # Look for top-level def + import + call patterns
            if re.search(
                    rf"^def {forbidden}\b|"
                    rf"from \S+ import {forbidden}|"
                    rf"\b{forbidden}\s*\(",
                    text, re.MULTILINE):
                hits.append(str(py.relative_to(PLUGIN_ROOT)))
    assert not hits, (
        f"Strategy A incomplete — _enrich_pyarchinit_graph still "
        f"referenced in: {hits}")


def test_export_graphml_uses_graph_projector():
    """D7: export_graphml must call GraphProjector().populate_graph
    instead of the deleted standalone function."""
    src = (PLUGIN_ROOT / "modules" / "s3dgraphy" / "sync"
           / "graphml_writer.py").read_text(encoding="utf-8")
    assert "GraphProjector" in src, (
        "graphml_writer must use GraphProjector after Strategy A")


def test_graph_projector_has_enrich_into_method():
    """The body lives in GraphProjector._enrich_into now."""
    src = (PLUGIN_ROOT / "modules" / "s3dgraphy" / "sync"
           / "graph_projector.py").read_text(encoding="utf-8")
    assert "def _enrich_into" in src
