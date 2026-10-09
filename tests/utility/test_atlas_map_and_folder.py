"""Tre guasti del 2026-10-09, segnalati da Enzo provando le stampe.

1. «Esce ancora vuoto»: il generatore calcolava `layoutItemMap` e non lo
   usava mai. La mappa del layout conservava l'inquadratura con cui il
   template era stato salvato — su un altro progetto, altrove — e quindi
   disegnava il niente. `PRINTMAP` fa `zoomToExtent(canvas.extent())`
   (PRINTMAP.py:254); il Time Manager no.
2. «Ho cancellato la cartella template ma non l'ha ricreata»: lo zip si
   riestrae solo quando manca `bin/profile`, non quando manca
   `profile/template`.
3. «La finestra del Time Manager blocca la finestra del layout»: dopo
   aver aperto il Layout Designer si mostravano due QMessageBox modali
   all'applicazione, che gli impedivano di ricevere i clic.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

TM = _ROOT / "tabs" / "Gis_Time_controller.py"
INST = _ROOT / "modules" / "utility" / "pyarchinit_folder_installation.py"


def _corpo(sorgente: str, nome: str) -> str:
    inizio = sorgente.index("def %s" % nome)
    return sorgente[inizio:sorgente.index("\n    def ", inizio + 10)]


# ----------------------------------------------- 1. la mappa va inquadrata

def test_the_map_of_the_sheet_is_actually_framed():
    src = TM.read_text(encoding="utf-8")
    assert "self._inquadra_tavola(mappe)" in _corpo(src, "generate_images")
    corpo = _corpo(src, "_inquadra_tavola")
    assert "zoomToExtent" in corpo, "la mappa non viene mai inquadrata"


def test_the_map_follows_the_project_layers():
    """Un template salvato altrove può portarsi dietro un elenco di layer
    che qui non esistono: la tavola uscirebbe bianca lo stesso."""
    corpo = _corpo(TM.read_text(encoding="utf-8"), "_inquadra_tavola")
    assert "setKeepLayerSet(False)" in corpo


def test_only_the_big_map_is_framed_on_the_dig():
    """Il modello del Time Manager ha DUE mappe, e la piccola è
    l'inserto panoramico: inquadrato sullo scavo non direbbe più dove si
    è nel mondo (Enzo, 2026-10-09)."""
    corpo = _corpo(TM.read_text(encoding="utf-8"), "_inquadra_tavola")
    assert "main_map_index(misure)" in corpo
    assert "principale.zoomToExtent" in corpo


def test_the_drawing_is_framed_on_the_data_not_on_the_canvas():
    """Il canvas può essere molto più largo dello scavo: il disegno
    restava un francobollo in mezzo al foglio."""
    src = TM.read_text(encoding="utf-8")
    assert "def _estensione_dei_dati" in src
    corpo = _corpo(src, "_estensione_dei_dati")
    assert "self.selected_layers" in corpo
    assert "combineExtentWith" in corpo


def test_the_printed_scale_is_a_real_one():
    """1:18,6 non è una scala da disegno."""
    corpo = _corpo(TM.read_text(encoding="utf-8"), "_inquadra_tavola")
    assert "nice_scale(" in corpo and "setScale(" in corpo


def test_the_scale_bars_get_a_map_to_read():
    """Nel modello non sono collegate a nessuna mappa, ed è per questo
    che la numerica stampava «1:1»."""
    corpo = _corpo(TM.read_text(encoding="utf-8"), "_inquadra_tavola")
    assert "QgsLayoutItemScaleBar" in corpo
    assert "setLinkedMap(principale)" in corpo


# ------------------------------------- 2. la cartella template si ricrea

def test_a_missing_template_folder_is_restored(tmp_path):
    from modules.utility.pyarchinit_folder_installation import (
        restore_missing_from_zip)

    sorgente = tmp_path / "profile.zip"
    with zipfile.ZipFile(sorgente, "w") as z:
        z.writestr("profile/template/uno.qpt", "<Layout/>")
        z.writestr("profile/template/due.qpt", "<Layout/>")
        z.writestr("profile/altro/x.txt", "non toccare")
    dove = tmp_path / "bin"
    (dove / "profile" / "template").mkdir(parents=True)
    (dove / "profile" / "template" / "uno.qpt").write_text("MIO",
                                                           encoding="utf-8")

    ripristinati = restore_missing_from_zip(sorgente, dove, "profile/template/")
    assert ripristinati == 1
    # quello che c'era non si tocca MAI: può essere stato modificato
    assert (dove / "profile" / "template" / "uno.qpt").read_text(
        encoding="utf-8") == "MIO"
    assert (dove / "profile" / "template" / "due.qpt").exists()
    # e fuori dal prefisso non si entra
    assert not (dove / "profile" / "altro").exists()


def test_restoring_twice_does_nothing_the_second_time(tmp_path):
    from modules.utility.pyarchinit_folder_installation import (
        restore_missing_from_zip)

    sorgente = tmp_path / "profile.zip"
    with zipfile.ZipFile(sorgente, "w") as z:
        z.writestr("profile/template/uno.qpt", "<Layout/>")
    dove = tmp_path / "bin"
    assert restore_missing_from_zip(sorgente, dove, "profile/template/") == 1
    assert restore_missing_from_zip(sorgente, dove, "profile/template/") == 0


def test_a_zip_that_is_not_there_is_not_an_error(tmp_path):
    from modules.utility.pyarchinit_folder_installation import (
        restore_missing_from_zip)

    assert restore_missing_from_zip(tmp_path / "manca.zip", tmp_path, "x/") == 0


def test_the_installer_restores_the_template_folder_on_its_own():
    src = INST.read_text(encoding="utf-8")
    assert "restore_missing_from_zip" in src
    assert "profile/template/" in src


def test_the_template_folder_is_created_if_it_is_missing():
    """Prima la copia di layout_TimeManager.qpt era dentro
    `if os.path.exists(template_dir)`: cancellata la cartella, non si
    copiava più niente e non lo diceva nessuno."""
    src = INST.read_text(encoding="utf-8")
    assert "makedirs(template_dir" in src or "os.makedirs(template_dir" in src


# ------------------------------- 3. le finestre non bloccano il designer

def test_the_designer_is_not_blocked_by_our_message_boxes():
    """Il Layout Designer è un'altra finestra di primo livello: una
    QMessageBox modale all'applicazione gli impedisce i clic."""
    src = TM.read_text(encoding="utf-8")
    # i due aiutanti sono modali alla sola finestra del Time Manager
    for nome in ("_chiedi", "_informa"):
        assert "WindowModal" in _corpo(src, nome), nome
    # e dove si parla col designer non si usano più le statiche, che
    # sono modali all'APPLICAZIONE e gli tolgono i clic
    for nome in ("generate_images", "open_layout_designer"):
        vive = [r for r in _corpo(src, nome).split("\n")
                if not r.strip().startswith("#")]
        for riga in vive:
            assert "QMessageBox.question(" not in riga, (nome, riga.strip())
            assert "QMessageBox.information(" not in riga, (nome, riga.strip())
