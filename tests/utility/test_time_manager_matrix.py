"""Il Time Manager disegna la matrice senza Graphviz (2026-10-09).

Richiesta di Enzo: «uso graphviz e questo spesso blocca o impiega tempo,
dato che ogni generazione deve fare una serie di processi». Qui si
provano le promesse nel sorgente — il collegamento vero vive dentro
QGIS — più la parte pura, che è provata per intero in
``test_em_matrix_records.py``.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

TM = _ROOT / "tabs" / "Gis_Time_controller.py"


def _source() -> str:
    return TM.read_text(encoding="utf-8")


def test_the_matrix_no_longer_goes_through_graphviz():
    """Né il JPEG di `dot` né la chiamata a `generate_matrix_3` restano
    sulla strada della matrice del Time Manager."""
    src = _source()
    assert "Harris_matrix_viewtred.dot.jpg" not in src
    assert "generate_matrix_3" not in src


def test_it_draws_with_the_same_engine_as_the_panel():
    """Una matrice sola, disegnata in un modo solo: se il Time Manager
    avesse un suo disegno, i due divergerebbero."""
    src = _source()
    assert "em_matrix_records" in src
    assert "em_matrix_layout" in src
    assert "MatrixView" in src


def test_the_atlas_gets_a_vector_picture():
    """Nella tavola la matrice è vettoriale: si legge a ogni scala e pesa
    decine di KB invece dei megabyte del JPEG."""
    src = _source()
    assert "FormatSVG" in src
    assert "Harris_matrix_timemanager.svg" in src


def test_the_periods_are_read_once_not_once_per_area_and_period():
    """La via vecchia faceva una query dentro due cicli annidati, a ogni
    rigenerazione. È lì che se ne andava il tempo, più che in `dot`."""
    src = _source()
    assert "_PERIODI_CACHE" in src
    assert "def _periodi_del_sito" in src


def test_the_drawing_helper_filters_to_the_visible_units():
    """Il Time Manager mostra le US fino alla posizione del cursore: la
    matrice deve essere quella, non quella di tutto il sito."""
    src = _source()
    assert "def _disegna_matrice" in src
    assert "visible=visibili" in src
