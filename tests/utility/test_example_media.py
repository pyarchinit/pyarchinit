"""I media del database di esempio, e le immagini che li rappresentano.

«Nel db di esempio aggiungi i media in tutte le schede che le gestiscono,
3-4 media per record con immagini fake, e li fai esportare in due cartelle
separate quando scarichi il db di esempio (thumb e image resize)» (Enzo,
11 ottobre 2026).

Le schede che gestiscono i media sono **sei**, e la lista non la decide
questo file: la dice `tabs/Image_search.ENTITY_TYPE_MAP` — US, CERAMICA,
Pottery, REPERTO, TOMBA, STRUTTURA, UT. Un test lo verifica, così se
domani ne nasce una settima questo file se ne accorge.

Le immagini **non si spediscono**: 606 segnaposto dentro un plugin sono
qualche megabyte a ogni aggiornamento. Le disegna
`modules/utility/example_media.py` al primo avvio, coi nomi che il
database dichiara — `media_thumb_table.filepath` per la miniatura e
`path_resize` per l'immagine grande — e salta quelle che trova già fatte,
così non tocca mai un file dell'utente.
"""
from __future__ import annotations

import ast
import os
import re
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

RADICE = Path(__file__).resolve().parents[2]
if str(RADICE) not in sys.path:
    sys.path.insert(0, str(RADICE))

from modules.utility import example_media as EM  # noqa: E402

DB = RADICE / "resources" / "dbfiles" / "pyarchinit_db.sqlite"
SITO = "Scavo archeologico"
#: I tipi che le schede scrivono in `media_to_entity_table.entity_type`.
TIPI = ("US", "CERAMICA", "REPERTO", "TOMBA", "STRUTTURA", "UT")


@pytest.fixture(scope="module")
def conn():
    if not DB.is_file():
        pytest.skip("manca %s" % DB)
    c = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
    yield c
    c.close()


# --------------------------------------------------------------------------
# I media nel database
# --------------------------------------------------------------------------

def test_le_sei_schede_che_gestiscono_i_media_hanno_i_loro_media(conn):
    conto = dict(conn.execute(
        "SELECT entity_type, count(*) FROM media_to_entity_table"
        " GROUP BY entity_type"))
    for tipo in TIPI:
        assert conto.get(tipo, 0) >= 3, (tipo, conto)


def test_la_lista_delle_schede_e_quella_del_cercatore_di_immagini():
    """Se nasce una settima scheda coi media, questo test cade."""
    sorgente = (RADICE / "tabs" / "Image_search.py").read_text(
        encoding="utf-8")
    blocco = re.search(r"ENTITY_TYPE_MAP\s*=\s*\{(.*?)\}", sorgente, re.S)
    assert blocco, "ENTITY_TYPE_MAP non si legge più"
    dichiarati = {v for v in re.findall(r":\s*'([A-Z]+)'", blocco.group(1))}
    assert dichiarati == set(TIPI), sorted(dichiarati ^ set(TIPI))


def test_ogni_record_ha_tre_media(conn):
    """Tre per record, su tutte le schede, nessuna esclusa."""
    for tipo, tabella, chiave in (
            ("US", "us_table", "id_us"),
            ("CERAMICA", "pottery_table", "id_rep"),
            ("REPERTO", "inventario_materiali_table", "id_invmat"),
            ("TOMBA", "tomba_table", "id_tomba"),
            ("STRUTTURA", "struttura_table", "id_struttura")):
        scoperti = conn.execute(
            'SELECT count(*) FROM "%s" r WHERE r.sito = ? AND ('
            ' SELECT count(*) FROM media_to_entity_table e'
            '  WHERE e.entity_type = ? AND e.id_entity = r."%s") < 3'
            % (tabella, chiave), (SITO, tipo)).fetchone()[0]
        assert scoperti == 0, (tipo, scoperti)


def test_ogni_media_ha_la_sua_riga_nelle_tre_tabelle(conn):
    """Tre tabelle, e servono tutte: senza `media_thumb_table` la scheda
    non ha un'anteprima da mostrare, senza `media_to_entity_table` il
    media non è di nessun record."""
    orfani = conn.execute(
        "SELECT count(*) FROM media_table m WHERE m.tags LIKE '%demo%'"
        " AND (NOT EXISTS (SELECT 1 FROM media_thumb_table t"
        "                  WHERE t.id_media = m.id_media)"
        "   OR NOT EXISTS (SELECT 1 FROM media_to_entity_table e"
        "                  WHERE e.id_media = m.id_media))").fetchone()[0]
    assert orfani == 0, orfani


def test_il_media_punta_a_un_record_che_esiste(conn):
    """Un media attaccato a un id che non c'è non lo vede nessuno."""
    tabelle = {"US": ("us_table", "id_us"),
               "CERAMICA": ("pottery_table", "id_rep"),
               "REPERTO": ("inventario_materiali_table", "id_invmat"),
               "TOMBA": ("tomba_table", "id_tomba"),
               "STRUTTURA": ("struttura_table", "id_struttura"),
               "UT": ("ut_table", "id_ut")}
    for tipo, (tabella, chiave) in tabelle.items():
        rotti = conn.execute(
            "SELECT count(*) FROM media_to_entity_table e"
            " WHERE e.entity_type = ? AND NOT EXISTS ("
            '  SELECT 1 FROM "%s" r WHERE r."%s" = e.id_entity)'
            % (tabella, chiave), (tipo,)).fetchone()[0]
        assert rotti == 0, (tipo, rotti)


def test_i_nomi_dei_file_sono_quelli_che_la_scheda_scriverebbe(conn):
    """La scheda compone `<id_media>_<filename>_thumb.png` e
    `<id_media>_<filename>.png` (`US_USM.py`, dove nasce un media): se il
    database ne dichiara altri, le anteprime non si trovano."""
    for id_media, nome, thumb, grande in conn.execute(
            "SELECT m.id_media, m.filename, t.filepath, t.path_resize"
            " FROM media_table m JOIN media_thumb_table t"
            "   ON t.id_media = m.id_media WHERE m.tags LIKE '%demo%'"):
        assert thumb == "%d_%s_thumb.png" % (id_media, nome), thumb
        assert grande == "%d_%s.png" % (id_media, nome), grande


def test_nessun_nome_di_file_si_ripete(conn):
    """Due media che scrivono lo stesso file si sovrascriverebbero."""
    doppi = conn.execute(
        "SELECT count(*) FROM (SELECT filepath FROM media_thumb_table"
        " GROUP BY filepath HAVING count(*) > 1)").fetchone()[0]
    assert doppi == 0, doppi


def test_la_descrizione_dice_di_che_scheda_e(conn):
    """È la descrizione che finisce **disegnata** nell'immagine."""
    for (descrizione,) in conn.execute(
            "SELECT descrizione FROM media_table WHERE tags LIKE '%demo%'"
            " LIMIT 40"):
        assert SITO in descrizione, descrizione
        assert "·" in descrizione, descrizione


# --------------------------------------------------------------------------
# Le immagini
# --------------------------------------------------------------------------

def test_disegna_una_immagine_della_misura_chiesta():
    pytest.importorskip("PIL")
    immagine = EM.disegna("US 1 · Scavo · insieme", "US")
    assert immagine.size == EM.DIM_RESIZE
    piccola = EM.disegna("US 1 · Scavo · insieme", "US",
                         EM.DIM_THUMB)
    assert piccola.size == EM.DIM_THUMB


def test_ogni_scheda_ha_il_suo_colore():
    """Si deve vedere a occhio da che scheda viene una foto."""
    pytest.importorskip("PIL")
    colori = set()
    for tipo in TIPI:
        immagine = EM.disegna("x", tipo, (40, 40))
        colori.add(immagine.getpixel((20, 36)))
    assert len(colori) == len(TIPI), colori


def test_genera_scrive_nelle_due_cartelle_e_non_ripassa(tmp_path):
    """Due cartelle separate — miniature e ridimensionate — e la seconda
    chiamata non riscrive niente: un'immagine che l'utente ha messo lì
    non si tocca."""
    pytest.importorskip("PIL")
    db = tmp_path / "db.sqlite"
    shutil.copy(DB, db)
    # Si lavora su **dieci** media: disegnarne 606 in un test costa sei
    # secondi e non prova niente di più.
    c = sqlite3.connect(db)
    c.execute("DELETE FROM media_thumb_table WHERE id_media_thumb NOT IN"
              " (SELECT id_media_thumb FROM media_thumb_table LIMIT 10)")
    c.commit()
    c.close()

    thumb, resize = tmp_path / "thumb", tmp_path / "resize"
    scritte, saltate = EM.genera(db, thumb, resize)
    assert scritte == 20 and saltate == 0, (scritte, saltate)
    assert len(list(thumb.iterdir())) == 10
    assert len(list(resize.iterdir())) == 10

    scritte2, saltate2 = EM.genera(db, thumb, resize)
    assert (scritte2, saltate2) == (0, 20)


def test_le_miniature_sono_piccole_e_le_altre_no(tmp_path):
    pytest.importorskip("PIL")
    from PIL import Image

    db = tmp_path / "db.sqlite"
    shutil.copy(DB, db)
    c = sqlite3.connect(db)
    c.execute("DELETE FROM media_thumb_table WHERE id_media_thumb NOT IN"
              " (SELECT id_media_thumb FROM media_thumb_table LIMIT 2)")
    c.commit()
    c.close()
    thumb, resize = tmp_path / "t", tmp_path / "r"
    EM.genera(db, thumb, resize)
    for percorso in thumb.iterdir():
        assert Image.open(percorso).size == EM.DIM_THUMB
    for percorso in resize.iterdir():
        assert Image.open(percorso).size == EM.DIM_RESIZE


def test_senza_database_non_succede_niente(tmp_path):
    assert EM.genera(tmp_path / "non-esiste.sqlite", tmp_path / "a",
                     tmp_path / "b") == (0, 0)


# --------------------------------------------------------------------------
# L'installazione: due cartelle, e i percorsi in config.cfg
# --------------------------------------------------------------------------

def test_linstallatore_crea_la_cartella_delle_ridimensionate():
    sorgente = (RADICE / "modules" / "utility"
                / "pyarchinit_folder_installation.py").read_text(
                    encoding="utf-8")
    assert "pyarchinit_Resize_folder" in sorgente
    assert "home_RESIZE_path" in sorgente
    assert "installa_media_di_esempio" in sorgente


def test_i_percorsi_finiscono_col_separatore(tmp_path):
    """La scheda fa `thumb_path_str + nome_file`: senza separatore finale
    l'immagine va a finire **accanto** alla cartella."""
    from modules.utility.pyarchinit_folder_installation import (
        pyarchinit_Folder_installation)

    db_path = tmp_path / "pyarchinit_DB_folder"
    db_path.mkdir()
    (db_path / "config.cfg").write_text(
        str({"DATABASE": "pyarchinit_db.sqlite", "THUMB_PATH": "",
             "THUMB_RESIZE": ""}), encoding="utf-8")
    installatore = pyarchinit_Folder_installation.__new__(
        pyarchinit_Folder_installation)
    installatore._scrivi_percorsi_media(
        str(db_path), str(tmp_path / "thumb"), str(tmp_path / "resize"))

    dati = ast.literal_eval((db_path / "config.cfg").read_text(
        encoding="utf-8"))
    assert dati["THUMB_PATH"].endswith(os.sep), dati["THUMB_PATH"]
    assert dati["THUMB_RESIZE"].endswith(os.sep), dati["THUMB_RESIZE"]


def test_un_percorso_gia_scelto_non_si_tocca(tmp_path):
    """Chi ha messo un `webdav://` non se lo vede sovrascrivere."""
    from modules.utility.pyarchinit_folder_installation import (
        pyarchinit_Folder_installation)

    db_path = tmp_path / "pyarchinit_DB_folder"
    db_path.mkdir()
    mio = "webdav://192.0.2.10:5006/pyarchinit_media/thumb/"
    (db_path / "config.cfg").write_text(
        str({"THUMB_PATH": mio, "THUMB_RESIZE": ""}), encoding="utf-8")
    installatore = pyarchinit_Folder_installation.__new__(
        pyarchinit_Folder_installation)
    installatore._scrivi_percorsi_media(
        str(db_path), str(tmp_path / "thumb"), str(tmp_path / "resize"))

    dati = ast.literal_eval((db_path / "config.cfg").read_text(
        encoding="utf-8"))
    assert dati["THUMB_PATH"] == mio
    assert dati["THUMB_RESIZE"].endswith(os.sep)


def test_il_trigger_dei_media_cancella_i_legami(tmp_path):
    """`media_entity_delete` scatta **dopo una DELETE** su
    `media_thumb_table` e porta via le righe di
    `media_to_entity_table` con quell'`id_media`. È il trigger del
    disastro di khutm2: chi rifà il popolamento deve cancellare prima i
    legami e poi le miniature, non il contrario."""
    db = tmp_path / "db.sqlite"
    shutil.copy(DB, db)
    c = sqlite3.connect(db)
    try:
        id_media = c.execute(
            "SELECT id_media FROM media_thumb_table LIMIT 1").fetchone()[0]
        prima = c.execute(
            "SELECT count(*) FROM media_to_entity_table WHERE id_media = ?",
            (id_media,)).fetchone()[0]
        assert prima > 0
        c.execute("DELETE FROM media_thumb_table WHERE id_media = ?",
                  (id_media,))
        dopo = c.execute(
            "SELECT count(*) FROM media_to_entity_table WHERE id_media = ?",
            (id_media,)).fetchone()[0]
        assert dopo == 0, "il trigger media_entity_delete non c'è più"
    finally:
        c.close()
