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


def test_a_plain_template_needs_all_three_pieces():
    assert what_to_add({"map": True, "title": False, "matrix": False,
                        "overview": False}) == ["title", "matrix", "overview"]


def test_the_time_manager_template_needs_nothing():
    assert what_to_add({"map": True, "title": True, "matrix": True,
                        "overview": True}) == []


def test_only_what_is_missing_is_added():
    assert what_to_add({"map": True, "title": True, "matrix": False,
                        "overview": True}) == ["matrix"]


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


# ----- le copie preparate devono sopravvivere a una rigenerazione ----------

def test_only_the_missing_ones_are_prepared(tmp_path):
    """I template escono da profile.zip, che si riestrae quando la
    cartella manca: le copie preparate sparirebbero. Si rifanno da sole,
    ma solo quelle che mancano — rifarle tutte a ogni avvio sarebbe
    lavoro inutile (Enzo, 2026-10-09)."""
    from modules.utility.atlas_template import to_prepare

    con_mappa = '<Layout><LayoutItem type="65639"/></Layout>'
    completo = ('<Layout><LayoutItem type="65639"/>'
                '<LayoutItem type="65639"/>'
                '<LayoutItem id="123"/><LayoutItem id="matrix"/></Layout>')
    (tmp_path / "A.qpt").write_text(con_mappa, encoding="utf-8")
    (tmp_path / "B.qpt").write_text(con_mappa, encoding="utf-8")
    (tmp_path / "B + Time Manager.qpt").write_text(completo,
                                                   encoding="utf-8")
    da_fare = [p.name for p in to_prepare(tmp_path)]
    assert da_fare == ["A.qpt"]


def test_a_prepared_copy_is_never_prepared_again(tmp_path):
    from modules.utility.atlas_template import to_prepare

    (tmp_path / "A + Time Manager.qpt").write_text("<Layout/>",
                                                   encoding="utf-8")
    assert to_prepare(tmp_path) == []


def test_a_folder_that_is_not_there_is_not_an_error(tmp_path):
    from modules.utility.atlas_template import to_prepare

    assert to_prepare(tmp_path / "non_esiste") == []


def test_the_startup_prepares_the_templates_after_extracting_them():
    """La preparazione deve stare DOPO l'estrazione di profile.zip, se no
    lavorerebbe su una cartella che non c'è ancora."""
    sorgente = (_ROOT / "modules" / "utility"
                / "pyarchinit_folder_installation.py").read_text(
                    encoding="utf-8")
    assert "ensure_prepared" in sorgente
    assert sorgente.index("profile.zip") < sorgente.index("ensure_prepared")


def test_a_template_that_needs_nothing_is_not_opened_at_every_start(tmp_path):
    """Leggere il testo costa poco, caricare un layout no: un modello già
    completo o senza mappa non deve nemmeno entrare nell'elenco."""
    from modules.utility.atlas_template import to_prepare

    completo = ('<Layout><LayoutItem type="65639"/>'
                '<LayoutItem type="65639"/>'
                '<LayoutItem id="123"/><LayoutItem id="matrix"/></Layout>')
    (tmp_path / "completo.qpt").write_text(completo, encoding="utf-8")
    (tmp_path / "senza_mappa.qpt").write_text("<Layout/>", encoding="utf-8")
    assert to_prepare(tmp_path) == []


def test_preparing_without_a_running_qgis_does_nothing_instead_of_crashing(
        tmp_path, monkeypatch):
    """Costruire un QgsPrintLayout senza QgsApplication non dà
    un'eccezione: dà un **segmentation fault**, e si porta via tutto il
    processo. La preparazione gira all'avvio, anche da `install_dir()`,
    che i test chiamano senza QGIS: lì deve semplicemente non fare
    niente."""
    from modules.utility import atlas_template

    con_mappa = '<Layout><LayoutItem type="65639"/></Layout>'
    (tmp_path / "A.qpt").write_text(con_mappa, encoding="utf-8")

    monkeypatch.setattr(atlas_template, "qgis_is_running", lambda: False)
    assert atlas_template.ensure_prepared(tmp_path) == 0
    assert atlas_template.prepare_file(tmp_path / "A.qpt") is None
    assert not list(tmp_path.glob("*Time Manager*"))


def test_the_startup_path_is_guarded():
    sorgente = (_ROOT / "modules" / "utility"
                / "atlas_template.py").read_text(encoding="utf-8")
    inizio = sorgente.index("def ensure_prepared")
    assert "qgis_is_running()" in sorgente[inizio:inizio + 400]


# ---------------------------------------------------------------------------
# L'inserto panoramico (2026-10-10)
# ---------------------------------------------------------------------------
# Enzo, 2026-10-10: «le fasce si popolano, l'export funziona, ma osm no».
# Non era OSM: dei 23 modelli preparati solo 8 hanno due mappe, e
# ``overview_indexes`` chiama inserto «ogni mappa tranne la grande». Sui
# 15 con una mappa sola l'inserto non esiste, quindi non c'era niente da
# popolare — e il generatore non diceva nulla. L'inserto si aggiunge come
# si aggiungono il titolo e la matrice.

def test_a_template_with_one_map_has_no_inset():
    uno = '<Layout><LayoutItem type="65639"/></Layout>'
    assert capabilities(uno)["overview"] is False


def test_two_maps_are_an_inset():
    due = ('<Layout><LayoutItem type="65639"/>'
           '<LayoutItem type="65639"/></Layout>')
    assert capabilities(due)["overview"] is True


def test_the_inset_is_among_the_things_to_add():
    assert what_to_add({"map": True, "title": True, "matrix": True,
                        "overview": False}) == ["overview"]


def test_a_template_without_a_map_gets_no_inset_either():
    assert what_to_add({"map": False, "title": False, "matrix": False,
                        "overview": False}) == []


def test_the_inset_sits_inside_the_main_map_not_on_the_new_page():
    """Il titolo e la matrice vanno su una pagina nuova per non coprire il
    cartiglio. L'inserto no: un localizzatore su un'altra pagina non
    localizza niente. Sta dentro il rettangolo della mappa grande, in
    basso a destra, dove sta per convenzione — e lì non può coprire né la
    legenda né il cartiglio, perché non esce dalla mappa."""
    from modules.utility.atlas_template import inset_rect

    # mappa grande: 100×80 mm a (10, 20)
    r = inset_rect((10.0, 20.0, 100.0, 80.0))
    assert r is not None
    x, y, w, h = r
    assert w < 100.0 / 2 and h < 80.0 / 2, "un inserto non è mezza tavola"
    assert x >= 10.0 and y >= 20.0
    assert x + w <= 10.0 + 100.0, "sborda a destra dalla mappa"
    assert y + h <= 20.0 + 80.0, "sborda in basso dalla mappa"
    # in basso a destra, non al centro
    assert x > 10.0 + 100.0 / 2
    assert y > 20.0 + 80.0 / 2


def test_a_map_too_small_gets_no_inset():
    from modules.utility.atlas_template import inset_rect

    assert inset_rect((0.0, 0.0, 12.0, 9.0)) is None


def test_a_stale_prepared_copy_is_prepared_again(tmp_path):
    """Una copia preparata da una versione precedente non ha l'inserto.
    Le copie ``+ Time Manager`` sono nostre, non dell'utente: si
    rifanno. L'originale resta intoccabile, sempre."""
    from modules.utility.atlas_template import to_prepare

    completo = ('<Layout><LayoutItem type="65639"/>'
                '<LayoutItem type="65639"/>'
                '<LayoutItem id="123"/><LayoutItem id="matrix"/></Layout>')
    vecchia = ('<Layout><LayoutItem type="65639"/>'
               '<LayoutItem id="123"/><LayoutItem id="matrix"/></Layout>')
    (tmp_path / "A.qpt").write_text(vecchia, encoding="utf-8")
    (tmp_path / "A + Time Manager.qpt").write_text(vecchia, encoding="utf-8")
    (tmp_path / "B.qpt").write_text(vecchia, encoding="utf-8")
    (tmp_path / "B + Time Manager.qpt").write_text(completo, encoding="utf-8")

    da_fare = [p.name for p in to_prepare(tmp_path)]
    assert da_fare == ["A.qpt"], \
        "la copia stantia di A va rifatta, quella completa di B no"
