"""Quali template sanno fare l'atlante del Time Manager (2026-10-09).

Enzo: «il generatore a volte parte a volte no, i layout sono vuoti».
Causa: il selettore elenca **tutti** i `.qpt` che trova sul disco, e il
generatore pretende due elementi che solo il modello del Time Manager
possiede — il titolo HTML (`id="123"`) e l'immagine della matrice
(`id="matrix"`). Scegliendone un altro, il generatore stampava
«Couldn't find HTML item» sulla console e **tornava indietro in
silenzio**: nessun messaggio, nessuna tavola, la barra di avanzamento
lasciata aperta.

Qui si prova il riconoscimento, sui template veri che il plugin
distribuisce.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.atlas_template import (  # noqa: E402
    MATRIX_ID,
    TITLE_ID,
    capabilities,
    describe_missing,
    is_usable,
)

NOSTRO = _ROOT / "resources" / "dbfiles" / "layout_TimeManager.qpt"
GENERICO = Path("/Users/enzo/pyarchinit_5/bin/profile/template/"
                "Modello pyarchinit A4 Landscape.qpt")


def test_the_time_manager_template_can_do_everything():
    caps = capabilities(NOSTRO.read_text(encoding="utf-8", errors="replace"))
    assert caps == {"map": True, "title": True, "matrix": True}
    assert is_usable(caps) is True
    assert describe_missing(caps) == ""


def test_a_plain_template_has_a_map_but_no_time_manager_items():
    """È il caso che rompeva tutto: mappa sì, titolo e matrice no."""
    if not GENERICO.exists():
        pytest.skip("i modelli generici non sono su questo computer")
    caps = capabilities(GENERICO.read_text(encoding="utf-8", errors="replace"))
    assert caps["map"] is True
    assert caps["title"] is False and caps["matrix"] is False


def test_a_template_with_a_map_is_usable_even_without_the_extras():
    """Senza titolo e senza matrice le tavole si fanno lo stesso: quello
    che manca si salta, non si abortisce tutto."""
    caps = {"map": True, "title": False, "matrix": False}
    assert is_usable(caps) is True
    testo = describe_missing(caps)
    assert "titolo" in testo.lower() and "matrice" in testo.lower()


def test_a_template_without_a_map_cannot_make_a_sheet():
    caps = {"map": False, "title": True, "matrix": True}
    assert is_usable(caps) is False
    assert "mappa" in describe_missing(caps).lower()


def test_nothing_at_all_is_not_a_template():
    caps = capabilities("")
    assert caps == {"map": False, "title": False, "matrix": False}
    assert is_usable(caps) is False


def test_broken_xml_does_not_raise():
    """Un .qpt troncato o di un'altra versione non deve far saltare la
    finestra di scelta."""
    caps = capabilities("<Layout><LayoutItem type=\"656")
    assert caps["map"] is False


def test_the_ids_are_the_ones_the_generator_looks_for():
    """Se un giorno il modello cambia id, questo test lo dice prima che il
    generatore torni indietro in silenzio."""
    testo = NOSTRO.read_text(encoding="utf-8", errors="replace")
    assert 'id="%s"' % TITLE_ID in testo
    assert 'id="%s"' % MATRIX_ID in testo
    sorgente = (_ROOT / "tabs" / "Gis_Time_controller.py").read_text(
        encoding="utf-8")
    assert "'%s'" % TITLE_ID in sorgente
    assert "'%s'" % MATRIX_ID in sorgente
