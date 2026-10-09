"""Il generatore dell'atlante non deve più tornare indietro in silenzio.

Enzo, 2026-10-09: «il generatore a volte parte a volte no, i layout sono
vuoti». Cinque strade che finivano senza una parola, provate qui sulle
promesse del sorgente — il generatore vero gira dentro QGIS con un
progetto, dei layer e un modello di stampa.
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


def _corpo(nome: str) -> str:
    src = _source()
    inizio = src.index("def %s" % nome)
    return src[inizio:src.index("\n    def ", inizio + 10)]


def test_a_template_without_the_time_manager_items_no_longer_aborts():
    """Era la causa: il selettore elenca tutti i .qpt del disco, ma solo
    il modello del Time Manager ha il titolo e l'immagine della matrice.
    Scegliendone un altro il generatore stampava una riga sulla console e
    tornava indietro, lasciando la barra aperta e i layout vuoti."""
    src = _source()
    assert "Couldn't find HTML item" not in src
    assert "Couldn't find Image item" not in src
    corpo = _corpo("generate_images")
    assert "_avvisato_senza_titolo" in corpo
    assert "_avvisato_senza_matrice" in corpo


def test_a_template_without_a_map_says_so_instead_of_crashing():
    """`[...][0]` su una lista vuota è un IndexError in mezzo al ciclo."""
    src = _source()
    assert "if isinstance(i, QgsLayoutItemMap)][0]" not in src
    corpo = _corpo("generate_images")
    assert "if not mappe:" in corpo


def test_the_template_is_checked_before_the_work_starts():
    corpo = _corpo("generate_images")
    assert "is_usable(caps)" in corpo
    assert "describe_missing(caps)" in corpo


def test_a_site_without_order_layer_is_a_message_not_a_type_error():
    """`max_num_id` può tornare None, e None + 1 fermava tutto."""
    corpo = _corpo("generate_images")
    assert "if max_num_order_layer is None:" in corpo


def test_the_progress_bar_is_closed_on_every_way_out():
    """`setAutoClose(False)`: uscendo a metà restava sullo schermo per
    sempre, e sembrava che il generatore fosse partito."""
    corpo = _corpo("generate_images")
    dopo = corpo[corpo.index("progress.show()"):]
    righe = dopo.split("\n")
    for n, riga in enumerate(righe):
        if riga.strip() != "return":
            continue
        # la chiusura deve stare nelle poche righe che precedono l'uscita
        prima = "\n".join(righe[max(0, n - 8):n])
        assert "progress.close()" in prima, riga
    assert dopo.count("progress.close()") >= 2


def test_a_failed_export_is_not_thrown_away():
    """Una cartella non scrivibile dava tavole mancanti senza una parola."""
    corpo = _corpo("generate_images")
    assert "QgsLayoutExporter.Success" in corpo
    assert "non_scritte" in corpo


def test_the_chooser_shows_which_templates_can_do_what():
    corpo = _corpo("choose_template")
    assert "capabilities(" in corpo
    assert "✓" in corpo and "✗" in corpo


def test_the_warning_about_the_matrix_is_given_once_not_once_per_sheet():
    """Un QMessageBox per livello avrebbe sepolto l'utente di finestre e
    sembrato un blocco."""
    corpo = _corpo("generate_images")
    assert "L'immagine della matrice non è stata generata correttamente" \
        not in corpo


def test_the_dial_debounce_keeps_out_of_the_way_during_generation():
    """Il generatore muove lui lo spinbox: il timer rifarebbe filtro e
    matrice in mezzo al ciclo."""
    src = _source()
    assert "_atlante_in_corso" in _corpo("_on_debounce_timeout")
    # e la bandiera si abbassa su tutte le uscite
    corpo = _corpo("generate_images")
    assert corpo.count("self._atlante_in_corso = False") >= 2


def test_the_title_placeholder_of_the_generic_templates_is_filled():
    """I modelli generici portano «{{title}}» nelle etichette. PRINTMAP lo
    sostituisce già (PRINTMAP.py:252), il Time Manager no: sulla tavola si
    leggeva «{{title}}» stampato così com'è (visto nelle prove)."""
    corpo = _corpo("generate_images")
    assert "{{title}}" in corpo
    assert "65641" in corpo          # il tipo dell'etichetta, come in PRINTMAP
    assert "Tavola %s" in corpo


def test_the_two_places_that_fill_a_title_agree_on_the_placeholder():
    """Se un giorno il segnaposto cambia, deve cambiare in tutti e due."""
    printmap = (_ROOT / "tabs" / "PRINTMAP.py").read_text(encoding="utf-8")
    assert "{{title}}" in printmap
