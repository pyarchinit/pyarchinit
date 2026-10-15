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


# --------------------------------------------------------------------------
# I documenti dei nodi DOC
# --------------------------------------------------------------------------

def test_i_nodi_doc_nominano_un_pdf_dentro_dosco(conn):
    """Portavano i file del computer di chi fece il demo
    (`DosCo\\Scavo archeologico_20220218_.xlsx`, `DosCo\\test1_1.graphml`),
    che non esistono da nessuna parte."""
    nodi = conn.execute(
        "SELECT us, doc_usv FROM us_table WHERE sito = ?"
        "   AND unita_tipo = 'DOC'", (SITO,)).fetchall()
    assert nodi, "nessun nodo DOC"
    for us, percorso in nodi:
        assert percorso, us
        nudo = str(percorso).replace("\\", "/")
        assert nudo.startswith("DosCo/"), (us, percorso)
        assert nudo.lower().endswith(".pdf"), (us, percorso)


def test_i_documenti_si_disegnano_in_dosco(tmp_path):
    pytest.importorskip("PIL")
    scritti, saltati = EM.genera_documenti(DB, tmp_path)
    assert scritti >= 2, (scritti, saltati)
    pdf = sorted(p.name for p in tmp_path.iterdir())
    assert all(n.endswith(".pdf") for n in pdf), pdf
    # un PDF vero comincia con %PDF
    for nome in pdf:
        assert (tmp_path / nome).read_bytes()[:4] == b"%PDF", nome
    assert EM.genera_documenti(DB, tmp_path) == (0, len(pdf))


def test_linstallatore_disegna_anche_i_documenti():
    sorgente = (RADICE / "modules" / "utility"
                / "pyarchinit_folder_installation.py").read_text(
                    encoding="utf-8")
    assert "genera_documenti" in sorgente
    assert "doc_bin_export_path" in sorgente


# --------------------------------------------------------------------------
# I saggi, i campi della scheda US e le geometrie
# --------------------------------------------------------------------------

def test_le_unita_sono_divise_in_quattro_saggi(conn):
    """Senza saggio l'esportazione «uno per saggio» non ha niente da
    dividere: era vuoto su tutte le 510 righe."""
    saggi = dict(conn.execute(
        "SELECT saggio, count(*) FROM us_table WHERE sito = ? GROUP BY 1",
        (SITO,)))
    assert set(saggi) == {"I", "II", "III", "IV"}, saggi
    assert sum(saggi.values()) == conn.execute(
        "SELECT count(*) FROM us_table WHERE sito = ?", (SITO,)).fetchone()[0]


def test_ogni_unita_ha_un_saggio_anche_i_nodi_virtuali(conn):
    """Un nodo virtuale in un file e l'unità che descrive in un altro non
    si legge: il saggio si propaga lungo i rapporti."""
    senza = [r[0] for r in conn.execute(
        "SELECT us FROM us_table WHERE sito = ?"
        "   AND trim(coalesce(saggio, '')) = ''", (SITO,))]
    assert senza == [], senza


def test_i_saggi_ci_sono_su_tutti_e_dieci_i_siti(conn):
    """I dieci demo tradotti hanno gli stessi numeri di US: la prova
    dell'esportazione per saggio deve funzionare in tutte le lingue."""
    scoperti = conn.execute(
        "SELECT count(*) FROM us_table"
        " WHERE trim(coalesce(saggio, '')) = ''").fetchone()[0]
    assert scoperti == 0, scoperti


def test_la_scheda_us_non_ha_colonne_vuote_tranne_quelle_di_servizio(conn):
    """Erano vuote in tutte le righe 88 colonne su 131."""
    righe = conn.execute(
        "SELECT * FROM us_table WHERE sito = ?", (SITO,)).fetchall()
    colonne = [r[1] for r in conn.execute("PRAGMA table_info(us_table)")]
    # Il lucchetto (`editing_by`, `editing_since`), il registro delle
    # modifiche (`audit_trail`) e `other_locations`, che dice in quali
    # ALTRE aree compare la stessa unità: riempirla inventerebbe aree.
    ammesse = {"editing_by", "editing_since", "audit_trail",
               "last_modified_by", "last_modified_timestamp",
               "other_locations"}
    vuote = [c for i, c in enumerate(colonne)
             if c not in ammesse
             and not any(r[i] is not None
                         and str(r[i]).strip() not in ("", "[]", "[[]]")
                         for r in righe)]
    assert vuote == [], vuote


def test_i_campi_della_muratura_stanno_solo_sulle_usm(conn):
    """Su uno strato di terra la tecnica muraria non vuol dire niente."""
    for colonna in ("tecnica_muraria_usm", "spess_giunti", "materiali_lat"):
        fuori = conn.execute(
            'SELECT count(*) FROM us_table WHERE sito = ?'
            '   AND unita_tipo NOT IN ("USM")'
            '   AND trim(coalesce("%s", "")) <> ""' % colonna,
            (SITO,)).fetchone()[0]
        assert fuori == 0, (colonna, fuori)


def test_le_quote_stanno_dove_sta_lo_scavo(conn):
    """Lo scavo è a 488 m s.l.m.: la prima passata scrisse 52."""
    minimo, massimo = conn.execute(
        "SELECT min(quota_q), max(quota_q) FROM pyarchinit_quote"
        " WHERE sito_q = ?", (SITO,)).fetchone()
    for tabella, colonna in (("us_table", "quota_abs"),
                             ("us_table", "quota_max_abs")):
        for (valore,) in conn.execute(
                'SELECT "%s" FROM "%s" WHERE sito = ?'
                '   AND "%s" IS NOT NULL' % (colonna, tabella, colonna),
                (SITO,)):
            assert minimo - 2 <= float(valore) <= massimo + 2, \
                (tabella, colonna, valore)


#: Le due unità del demo senza disegno: il taglio 7 e il suo riempimento 8.
#: L'11 ottobre avevano ricevuto due quadratini segnaposto fuori dal sito;
#: il 13 ottobre Enzo li ha fatti togliere («non c'entrano nulla quei
#: quadratini»): meglio nessun disegno che un disegno finto.
SENZA_DISEGNO = ["7", "8"]


def test_ogni_us_ha_il_suo_poligono_e_la_sua_quota(conn):
    """«Non mi sembra che tutti abbiano le geometrie» (Enzo): erano due
    US senza poligono e tredici senza quota. Restano, per scelta, le due
    di ``SENZA_DISEGNO``."""
    senza_poligono = [str(r[0]) for r in conn.execute(
        "SELECT u.us FROM us_table u WHERE u.sito = ?"
        "   AND u.unita_tipo IN ('US', 'USM')"
        "   AND NOT EXISTS (SELECT 1 FROM pyunitastratigrafiche g"
        "                   WHERE g.scavo_s = u.sito"
        "                     AND cast(g.us_s AS TEXT) = cast(u.us AS TEXT))"
        "   AND NOT EXISTS (SELECT 1 FROM pyunitastratigrafiche_usm g"
        "                   WHERE g.scavo_s = u.sito"
        "                     AND cast(g.us_s AS TEXT) = cast(u.us AS TEXT))"
        "   ORDER BY cast(u.us AS INTEGER)",
        (SITO,)).fetchall()]
    assert senza_poligono == SENZA_DISEGNO, senza_poligono
    senza_quota = conn.execute(
        "SELECT count(*) FROM us_table u WHERE u.sito = ?"
        "   AND u.unita_tipo IN ('US', 'USM')"
        "   AND NOT EXISTS (SELECT 1 FROM pyarchinit_quote g"
        "                   WHERE g.sito_q = u.sito"
        "                     AND cast(g.us_q AS TEXT) = cast(u.us AS TEXT))",
        (SITO,)).fetchone()[0]
    assert senza_quota == 0, senza_quota


def test_nessuna_scheda_resta_col_lucchetto(conn):
    """`editing_by` valorizzato = «in modifica da un altro utente»: la
    prima passata di riempimento l'aveva messo su quaranta record."""
    colpevoli = []
    for (tabella,) in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
            "   AND name LIKE '%_table'"):
        colonne = [r[1] for r in conn.execute(
            'PRAGMA table_info("%s")' % tabella)]
        for colonna in ("editing_by", "editing_since", "last_modified_by",
                        "last_modified_timestamp"):
            if colonna not in colonne:
                continue
            n = conn.execute(
                'SELECT count(*) FROM "%s" WHERE'
                ' trim(coalesce(cast("%s" AS TEXT), "")) <> ""'
                % (tabella, colonna)).fetchone()[0]
            if n:
                colpevoli.append((tabella, colonna, n))
    assert colpevoli == [], colpevoli


def test_le_sigle_virtuali_sono_quelle_nuove(conn):
    """USVA/USVB/USVC sono il vocabolario vecchio: dalla 5.1.0-alpha sono
    USVs (strutturale) e USVn (non strutturale)."""
    vecchie = conn.execute(
        "SELECT count(*) FROM us_table"
        " WHERE unita_tipo IN ('USVA', 'USVB', 'USVC')").fetchone()[0]
    assert vecchie == 0, vecchie
    nuove = dict(conn.execute(
        "SELECT unita_tipo, count(*) FROM us_table"
        " WHERE unita_tipo LIKE 'USV%' GROUP BY 1"))
    assert set(nuove) <= {"USVs", "USVn"}, nuove
    assert sum(nuove.values()) > 0
    sporchi = conn.execute(
        "SELECT count(*) FROM us_table"
        " WHERE rapporti2 LIKE '%USVA%' OR rapporti2 LIKE '%USVB%'"
        "    OR rapporti2 LIKE '%USVC%'").fetchone()[0]
    assert sporchi == 0, sporchi


# --------------------------------------------------------------------------
# La scheda TMA
# --------------------------------------------------------------------------

def test_la_scheda_tma_non_e_piu_vuota(conn):
    """«La scheda TMA me la dà vuota» (Enzo, 12 ottobre 2026): la tabella
    che la scheda legge — `tma_materiali_archeologici` — aveva **zero**
    righe, e la finestra si apriva senza niente dentro."""
    assert conn.execute(
        "SELECT count(*) FROM tma_materiali_archeologici"
        " WHERE sito = ?", (SITO,)).fetchone()[0] >= 10
    assert conn.execute(
        "SELECT count(*) FROM tma_materiali_ripetibili").fetchone()[0] >= 30


def test_ogni_cassetta_tma_ha_i_suoi_materiali(conn):
    scoperte = conn.execute(
        "SELECT count(*) FROM tma_materiali_archeologici t"
        " WHERE t.sito = ? AND NOT EXISTS ("
        "   SELECT 1 FROM tma_materiali_ripetibili r WHERE r.id_tma = t.id)",
        (SITO,)).fetchone()[0]
    assert scoperte == 0, scoperte


@pytest.mark.parametrize("colonna,sigla,tabella", [
    ("ldcn", "10.1", "tma_materiali_archeologici"),
    ("ldct", "10.2", "tma_materiali_archeologici"),
    ("localita", "10.3", "tma_materiali_archeologici"),
    ("dtzg", "10.4", "tma_materiali_archeologici"),
    ("aint", "10.6", "tma_materiali_archeologici"),
    ("ftap", "10.9", "tma_materiali_archeologici"),
    ("settore", "10.15", "tma_materiali_archeologici"),
])
def test_i_campi_della_tma_mostrano_voci_del_vocabolario(conn, colonna, sigla,
                                                         tabella):
    voci = {str(v).strip() for (v,) in conn.execute(
        "SELECT sigla_estesa FROM pyarchinit_thesaurus_sigle"
        " WHERE nome_tabella = ? AND tipologia_sigla = ?", (tabella, sigla))
        if v and str(v).strip()}
    assert voci, sigla
    for (valore,) in conn.execute(
            'SELECT "%s" FROM tma_materiali_archeologici WHERE sito = ?'
            % colonna, (SITO,)):
        if valore and str(valore).strip():
            assert str(valore).strip() in voci, (colonna, valore)


def test_la_tma_non_porta_i_campi_della_concorrenza(conn):
    """Anche la scheda TMA fa `check_version_conflict`: `updated_by` con
    un nome dentro fa aprire «questo record è stato modificato da…»."""
    for colonna in ("created_by", "updated_by", "created_at", "updated_at"):
        pieni = conn.execute(
            'SELECT count(*) FROM tma_materiali_archeologici'
            ' WHERE trim(coalesce(cast("%s" AS TEXT), "")) <> ""' % colonna
        ).fetchone()[0]
        assert pieni == 0, (colonna, pieni)


def test_la_voce_di_menu_esporta_un_grafo_solo_senza_chiedere():
    """Il 12 ottobre 2026 la voce di menu passava sempre «automatico» e su
    uno scavo a saggi divideva **sempre** il file; poi ha chiesto come
    dividerlo. Dal 13 ottobre (Emanuel: la divisione per saggi era un
    fraintendimento) non chiede niente: un grafo solo per tutto il sito,
    detto esplicitamente — `None` vorrebbe ancora dire «automatico»."""
    sorgente = (RADICE / "pyarchinitPlugin.py").read_text(encoding="utf-8")
    assert "saggi_del_sito" not in sorgente
    assert "per_saggio=None" not in sorgente and "per_saggio=per_saggio" not in sorgente
    assert sorgente.count("per_saggio=False") == 2        # «Esporta sito in em.json…» e «Vedi la matrice…»


def test_la_scheda_tma_nomina_i_widget_che_esistono():
    """`tableWidget_disegno` (singolare) non esiste: nel `.ui` si chiama
    `tableWidget_disegni`. La scheda alzava `AttributeError` appena
    c'era un record da mostrare — e finché la tabella era vuota quel
    punto non si raggiungeva mai (Enzo, 12 ottobre 2026)."""
    import re

    sorgente = (RADICE / "tabs" / "Tma.py").read_text(encoding="utf-8")
    ui = (RADICE / "gui" / "ui" / "Tma.ui").read_text(encoding="utf-8")
    nel_ui = set(re.findall(r'name="([^"]+)"', ui))
    # i widget creati a mano nel codice non stanno nel .ui
    a_mano = set(re.findall(r"self\.(\w+)\s*=\s*QTableWidget\(", sorgente))
    usati = set(re.findall(r"self\.(tableWidget_\w+)", sorgente))
    usati |= set(re.findall(r'"self\.(tableWidget_\w+)"', sorgente))
    fuori = sorted(usati - nel_ui - a_mano)
    assert fuori == [], fuori


def test_nessuna_scheda_chiama_fill_record_che_non_esiste():
    """Otto schede chiamavano `self.fill_record()` dentro il ramo del
    conflitto, e quel metodo non esiste in nessuna: il ramo si
    raggiungeva solo quando `last_modified_by` portava il nome di un
    altro utente — cioè proprio nella situazione che i campi della
    concorrenza riempiti creavano."""
    import ast

    colpevoli = []
    for sorgente in sorted((RADICE / "tabs").glob("*.py")):
        testo = sorgente.read_text(encoding="utf-8")
        if "self.fill_record()" not in testo:
            continue
        albero = ast.parse(testo)
        definito = any(isinstance(n, ast.FunctionDef) and n.name == "fill_record"
                       for n in ast.walk(albero))
        if not definito:
            colpevoli.append(sorgente.name)
    assert colpevoli == [], colpevoli
