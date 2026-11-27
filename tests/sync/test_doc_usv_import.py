"""5.19.3-alpha: a document born in EMStudio keeps its file in doc_usv at
import (as it comes back from a room), plus the deprecated-EPSG hint and the
LaTeX left in a narrative."""
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
for _p in (_ROOT, _ROOT / "ext_libs"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
pytest.importorskip("s3dgraphy")


def test_a_document_from_emstudio_gets_its_file_in_doc_usv(tmp_path):
    from s3dgraphy.graph import Graph
    from s3dgraphy.nodes.document_node import DocumentNode
    from modules.s3dgraphy.sync.graph_ingestor import GraphIngestor
    db = tmp_path / "d.sqlite"
    shutil.copy(_ROOT / "resources" / "dbfiles" / "pyarchinit.sqlite", db)
    g = Graph(graph_id="S")
    d = DocumentNode("doc-1", "D.05", url="D.05 notes.pdf")
    d.description = "Working notes"
    g.add_node(d)
    GraphIngestor().populate_list(g, f"sqlite:///{db}", sito="S", dry_run=False)
    row = sqlite3.connect(db).execute(
        "SELECT doc_usv, documentazione FROM us_table WHERE sito='S' AND unita_tipo='DOC'").fetchone()
    assert row == ("D.05 notes.pdf", "D.05 notes.pdf")


def test_a_deprecated_epsg_code_gets_the_current_one():
    from modules.s3dgraphy.sync.em_drawings_import import current_code_of
    assert current_code_of(31700) == 3844
    assert current_code_of("not a code") is None


def test_latex_left_in_the_narrative_becomes_html():
    from modules.s3dgraphy.em_narrative import latex_to_html
    assert latex_to_html("<h4>\\textit{Forum Novum</h4>") == "<h4><i>Forum Novum</i></h4>"
    assert latex_to_html("a \\emph{b} c \\textbf{d}") == "a <i>b</i> c <b>d</b>"
    assert latex_to_html("plain") == "plain"
