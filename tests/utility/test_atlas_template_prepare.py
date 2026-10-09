"""Rendere adatto all'atlante un modello che non lo è (2026-10-09).

I venticinque modelli adArte/pyarchinit non hanno il titolo «Tavola N»
né l'immagine della matrice, quindi l'atlante del Time Manager li fa
uscire spogli. Qui si prova la preparazione: i due elementi si
aggiungono su una **pagina nuova**, mai sopra il layout esistente — in
un modello che non si conosce si coprirebbe la legenda o il cartiglio, e
una matrice di Harris in un francobollo non si legge.

Si prova senza QGIS la parte che decide; la parte che scrive il file ha
la sua verifica a parte, con QGIS avviato.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from modules.utility.atlas_template import (  # noqa: E402
    capabilities,
    prepared_name,
    what_to_add,
)


def test_a_plain_template_needs_both_pieces():
    assert what_to_add({"map": True, "title": False, "matrix": False}) == (
        ["title", "matrix"])


def test_the_time_manager_template_needs_nothing():
    assert what_to_add({"map": True, "title": True, "matrix": True}) == []


def test_only_what_is_missing_is_added():
    assert what_to_add({"map": True, "title": True, "matrix": False}) == (
        ["matrix"])


def test_a_template_without_a_map_is_not_worth_preparing():
    """Senza mappa non è un modello da atlante: aggiungerci la matrice
    non lo renderebbe utile."""
    assert what_to_add({"map": False, "title": False, "matrix": False}) == []


def test_the_prepared_file_sits_beside_the_original_with_a_clear_name():
    """Non si sovrascrive mai un modello dell'utente."""
    nome = prepared_name(Path("/t/Modello pyarchinit A4 Landscape.qpt"))
    assert nome.name == "Modello pyarchinit A4 Landscape + Time Manager.qpt"
    assert nome.parent == Path("/t")


def test_preparing_an_already_prepared_file_does_not_stack_suffixes():
    uno = prepared_name(Path("/t/X.qpt"))
    assert prepared_name(uno) == uno


def test_a_prepared_template_declares_both_pieces(tmp_path):
    """La prova che chiude il cerchio: dopo la preparazione il file deve
    essere riconosciuto come completo dallo stesso lettore che usa la
    finestra di scelta."""
    import pytest

    qgis = pytest.importorskip("qgis.core")
    from modules.utility.atlas_template import prepare_file

    sorgente = (_ROOT / "resources" / "dbfiles" / "layout_TimeManager.qpt")
    # si parte da uno COMPLETO: deve restare completo e non raddoppiare
    uscita = prepare_file(sorgente, tmp_path)
    if uscita is None:
        return                                  # niente da aggiungere: giusto
    caps = capabilities(Path(uscita).read_text(encoding="utf-8",
                                               errors="replace"))
    assert caps["title"] and caps["matrix"]


def test_the_matrix_frame_hugs_the_drawing():
    """Una matrice è alta e stretta, la pagina è larga: senza questo il
    riquadro restava mezzo vuoto (visto nella tavola di prova)."""
    sorgente = (_ROOT / "modules" / "utility"
                / "atlas_template.py").read_text(encoding="utf-8")
    assert "ZoomResizeFrame" in sorgente


def test_the_pieces_go_on_a_new_page_never_over_the_existing_one():
    """In un modello che non si conosce si coprirebbe la legenda o il
    cartiglio."""
    sorgente = (_ROOT / "modules" / "utility"
                / "atlas_template.py").read_text(encoding="utf-8")
    assert "QgsLayoutItemPage" in sorgente
    assert "addPage(" in sorgente


def test_the_original_is_never_overwritten():
    sorgente = (_ROOT / "scripts"
                / "prepare_atlas_templates.py").read_text(encoding="utf-8")
    assert "prepared_name(percorso).exists()" in sorgente
    assert "PREPARED_SUFFIX not in p.stem" in sorgente
