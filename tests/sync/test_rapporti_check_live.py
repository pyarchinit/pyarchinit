"""«Verifica rapporti» risponde davvero (2026-10-08).

Enzo ha chiesto se la scheda funziona: nel suo screenshot la tabella è
vuota. Lo è perché la verifica non era ancora stata lanciata — il
controllo, sul database di esempio, trova le reciprocità mancanti.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_EXT_LIBS = str(_ROOT / "ext_libs")
if _EXT_LIBS in sys.path:
    sys.path.remove(_EXT_LIBS)
sys.path.insert(0, _EXT_LIBS)


@pytest.fixture()
def sample_db(tmp_path, monkeypatch):
    folder = tmp_path / "pyarchinit_DB_folder"
    folder.mkdir()
    resources = _ROOT / "resources" / "dbfiles"
    shutil.copy(resources / "config.cfg", folder / "config.cfg")
    shutil.copy(resources / "pyarchinit_db.sqlite", folder / "db.sqlite")
    monkeypatch.setenv("PYARCHINIT_HOME", str(tmp_path))
    return "sqlite:///%s" % (folder / "db.sqlite")


def test_the_checker_answers_on_the_sample_site(sample_db):
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.utility import rapporti_check as RC

    graph = GraphProjector().populate_graph(sample_db, "Scavo archeologico")
    report = RC.check_rapporti(graph, sito="Scavo archeologico")
    assert report.issues, "la verifica non trova nulla su un sito che ne ha"
    assert any(i.kind == RC.MISSING_RECIPROCITY for i in report.issues)


def test_the_checker_speaks_about_the_site_it_was_given(sample_db):
    """Ogni sito ha le sue: il controllo non deve rispondere con i
    problemi del sito accanto (i dieci siti del demo sono traduzioni
    dello stesso scavo e si somigliano)."""
    from modules.s3dgraphy.sync.graph_projector import GraphProjector
    from modules.utility import rapporti_check as RC

    for sito, unita in (("Scavo archeologico", "1.1.US1"),
                        ("Archaeological Excavation", "1.1.SU1")):
        graph = GraphProjector().populate_graph(sample_db, sito)
        assert any(n.name == unita for n in graph.nodes), sito
        report = RC.check_rapporti(graph, sito=sito)
        assert report.sito == sito
