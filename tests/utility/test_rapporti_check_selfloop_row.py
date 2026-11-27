"""A row whose rapporti name the row itself is a self-loop (auto: removed),
not a missing reciprocal whose fix would write a second one (27 Nov 2026)."""
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for _p in (_ROOT, _ROOT / "ext_libs"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
pytest.importorskip("s3dgraphy")

from modules.utility import rapporti_check as RC  # noqa: E402


def _grafo():
    from s3dgraphy.graph import Graph
    from s3dgraphy.nodes.stratigraphic_node import StratigraphicUnit
    g = Graph(graph_id="S")
    for uid, us, area, rap in (
            ("a", "1", "1", [["Copre", "1", "1", "S"], ["Copre", "2", "1", "S"], ["Copre", "1", "2", "S"]]),
            ("b", "2", "1", [["Coperto da", "1", "1", "S"]]),
            ("c", "1", "2", [["Coperto da", "1", "1", "S"]])):
        n = StratigraphicUnit(uid, "%s.US%s" % (area, us))
        n.data = {"sito": "S", "area": area, "us": us, "unita_tipo": "US"}
        n.attributes = {"rapporti": rap, "sito": "S", "area": area, "us": us, "unita_tipo": "US"}
        g.add_node(n)
    g.add_edge("ab", "a", "b", "overlies")
    g.add_edge("ac", "a", "c", "overlies")
    return g


def test_a_row_related_to_itself_is_a_self_loop_removed_alone():
    rep = RC.check_rapporti(_grafo(), sito="S", lang="en", validate=False)
    kinds = [(i.kind, i.auto) for i in rep.issues]
    assert (RC.SELF_LOOP, True) in kinds
    assert not any(i.kind == RC.MISSING_RECIPROCITY and i.us_path == ["1", "1"] for i in rep.issues)
    loop = next(i for i in rep.issues if i.kind == RC.SELF_LOOP)
    removed = [e for ed in loop.edits for e in ed.remove]
    assert removed == [("Copre", "1", "1", "S")]          # not the US 1 of area 2
