"""Le correzioni cronologiche atterrano nella tabella giusta, e si annullano.

Su SQLite di prova: la scrittura si guarda, non si deduce.
"""
from __future__ import annotations

import sqlite3
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

from modules.utility import rapporti_check as RC


def _db(tmp_path):
    """us_table e periodizzazione_table, due siti, con i tipi dello schema:
    `periodo` intero e `fase` testo, che è dove PostgreSQL inciampa."""
    from s3dgraphy.sync._db_handle import DbHandle
    p = tmp_path / "chrono.sqlite"
    c = sqlite3.connect(p)
    c.execute("CREATE TABLE us_table (sito TEXT, us TEXT, rapporti TEXT,"
              " periodo_iniziale TEXT, fase_iniziale TEXT,"
              " periodo_finale TEXT, fase_finale TEXT, datazione TEXT,"
              " area TEXT, unita_tipo TEXT)")
    c.execute("CREATE TABLE periodizzazione_table (sito TEXT,"
              " periodo INTEGER, fase TEXT, cron_iniziale INTEGER,"
              " cron_finale INTEGER, datazione_estesa TEXT, descrizione TEXT)")
    c.execute("INSERT INTO us_table VALUES ('S','12','[]','2','2.2','2','2.2',"
              "'Prima metà del XV secolo','1','US')")
    c.execute("INSERT INTO us_table VALUES ('ALTRO','99','[]','2','2.2','2',"
              "'2.2','non toccare','1','US')")
    c.execute("INSERT INTO periodizzazione_table VALUES "
              "('S',2,'2.2',1500,1549,'Prima metà del XVI secolo','')")
    c.execute("INSERT INTO periodizzazione_table VALUES "
              "('S',3,'1',1500,1549,'Prima metà del XV secolo rec','')")
    c.execute("INSERT INTO periodizzazione_table VALUES "
              "('ALTRO',2,'2.2',1500,1549,'non toccare','')")
    c.commit(); c.close()
    return DbHandle.from_path(p)


def _db_nulls(tmp_path):
    """Le righe che il NULL rende scomode: una fase senza nome e una US senza
    sito, che nel database di Enzo esistono perché il migratore DB→DB scrive
    NULL dove le schede scrivono ''."""
    from s3dgraphy.sync._db_handle import DbHandle
    p = tmp_path / "nulls.sqlite"
    c = sqlite3.connect(p)
    c.execute("CREATE TABLE us_table (sito TEXT, us TEXT, rapporti TEXT,"
              " periodo_iniziale TEXT, fase_iniziale TEXT,"
              " periodo_finale TEXT, fase_finale TEXT, datazione TEXT)")
    c.execute("CREATE TABLE periodizzazione_table (sito TEXT,"
              " periodo INTEGER, fase TEXT, cron_iniziale INTEGER,"
              " cron_finale INTEGER, datazione_estesa TEXT, descrizione TEXT)")
    c.execute("INSERT INTO us_table VALUES (NULL,'77','[]','2','2.2','2','2.2',"
              "'vecchia')")
    c.execute("INSERT INTO us_table VALUES ('ALTRO','77','[]','2','2.2','2',"
              "'2.2','non toccare')")
    c.execute("INSERT INTO periodizzazione_table VALUES "
              "('S',9,NULL,1600,1500,'fase senza nome','')")
    c.commit(); c.close()
    return DbHandle.from_path(p)


def _periodo(h, sito, periodo, fase):
    from sqlalchemy import text
    with h.engine.connect() as c:
        return c.execute(text(
            "SELECT cron_iniziale, cron_finale FROM periodizzazione_table "
            "WHERE sito = :s AND CAST(periodo AS TEXT) = :p AND fase = :f"),
            {"s": sito, "p": periodo, "f": fase}).fetchone()


def test_a_period_edit_writes_in_the_periodization(tmp_path):
    from sqlalchemy import text
    h = _db(tmp_path)
    e = RC.Edit(us="2/2.2", set_fields=(("cron_finale", 1480),),
                target=("periodizzazione_table",
                        {"periodo": "2", "fase": "2.2"}))
    RC.apply_edits([e], h, sito="S")
    assert _periodo(h, "S", "2", "2.2") == (1500, 1480)
    with h.engine.connect() as c:
        # us_table non è stata sfiorata: nessuna riga 'us' = '2/2.2'
        assert c.execute(text("SELECT datazione FROM us_table WHERE us='12'")
                         ).fetchone() == ("Prima metà del XV secolo",)


def test_a_period_edit_leaves_the_other_sites_alone(tmp_path):
    h = _db(tmp_path)
    e = RC.Edit(us="2/2.2", set_fields=(("cron_finale", 1480),),
                target=("periodizzazione_table",
                        {"periodo": "2", "fase": "2.2"}))
    RC.apply_edits([e], h, sito="S")
    assert _periodo(h, "ALTRO", "2", "2.2") == (1500, 1549)


def test_a_period_edit_without_a_sito_refuses_to_write(tmp_path):
    """(periodo, fase) senza sito è la stessa fase in dieci siti."""
    h = _db(tmp_path)
    e = RC.Edit(us="2/2.2", set_fields=(("cron_finale", 1480),),
                target=("periodizzazione_table",
                        {"periodo": "2", "fase": "2.2"}))
    with pytest.raises(ValueError, match="sito"):
        RC.apply_edits([e], h)
    assert _periodo(h, "S", "2", "2.2") == (1500, 1549)
    assert _periodo(h, "ALTRO", "2", "2.2") == (1500, 1549)


def test_an_edit_without_a_target_still_writes_in_us_table(tmp_path):
    """Nessuna chiamata esistente cambia: `target` vuoto vale us_table."""
    from sqlalchemy import text
    h = _db(tmp_path)
    e = RC.Edit(us="12", set_fields=(("datazione", "XV secolo"),))
    RC.apply_edits([e], h, sito="S")
    with h.engine.connect() as c:
        assert c.execute(text("SELECT datazione FROM us_table WHERE us='12'")
                         ).fetchone() == ("XV secolo",)


def test_a_column_outside_the_whitelist_is_not_written(tmp_path):
    from sqlalchemy import text
    h = _db(tmp_path)
    e = RC.Edit(us="2/2.2", set_fields=(("descrizione", "cancellata"),),
                target=("periodizzazione_table",
                        {"periodo": "2", "fase": "2.2"}))
    RC.apply_edits([e], h, sito="S")
    with h.engine.connect() as c:
        assert c.execute(text(
            "SELECT descrizione FROM periodizzazione_table "
            "WHERE sito='S' AND fase='2.2'")).fetchone() == ("",)


def test_a_us_table_column_outside_the_whitelist_is_not_written(tmp_path):
    """`area` è una colonna vera di us_table che la whitelist non contiene:
    la correzione non la tocca, e non per via di un errore SQL."""
    from sqlalchemy import text
    h = _db(tmp_path)
    RC.apply_edits([RC.Edit(us="12", set_fields=(("area", "9"),))], h, sito="S")
    with h.engine.connect() as c:
        assert c.execute(text("SELECT area FROM us_table WHERE us='12'")
                         ).fetchone() == ("1",)


def test_rollback_restores_both_tables(tmp_path):
    from sqlalchemy import text
    h = _db(tmp_path)
    edits = [
        RC.Edit(us="12", set_fields=(("datazione", "XV secolo"),)),
        RC.Edit(us="2/2.2", set_fields=(("cron_finale", 1480),),
                target=("periodizzazione_table",
                        {"periodo": "2", "fase": "2.2"})),
    ]
    tok = RC.apply_edits(edits, h, sito="S")
    RC.rollback(tok, h)
    assert _periodo(h, "S", "2", "2.2") == (1500, 1549)
    with h.engine.connect() as c:
        assert c.execute(text("SELECT datazione FROM us_table WHERE us='12'")
                         ).fetchone() == ("Prima metà del XV secolo",)


def test_two_edits_on_the_same_row_roll_back_to_the_first_value(tmp_path):
    """Una fase che si sovrappone a due altre produce due Edit sulla stessa
    riga: si applicano insieme, e l'annulla torna a prima della prima."""
    h = _db(tmp_path)
    target = ("periodizzazione_table", {"periodo": "2", "fase": "2.2"})
    edits = [RC.Edit(us="2/2.2", set_fields=(("cron_iniziale", 1510),),
                     target=target),
             RC.Edit(us="2/2.2", set_fields=(("cron_finale", 1540),),
                     target=target)]
    tok = RC.apply_edits(edits, h, sito="S")
    assert _periodo(h, "S", "2", "2.2") == (1510, 1540)
    RC.rollback(tok, h)
    assert _periodo(h, "S", "2", "2.2") == (1500, 1549)


def test_an_edit_whose_row_is_gone_writes_nothing_and_does_not_raise(tmp_path):
    """Qualcuno ha cancellato la fase nel frattempo: zero righe aggiornate, e
    la riverifica che segue ripresenta il problema."""
    h = _db(tmp_path)
    e = RC.Edit(us="9/9", set_fields=(("cron_finale", 1480),),
                target=("periodizzazione_table",
                        {"periodo": "9", "fase": "9"}))
    tok = RC.apply_edits([e], h, sito="S")
    RC.rollback(tok, h)
    assert _periodo(h, "S", "2", "2.2") == (1500, 1549)


def test_a_phase_whose_fase_is_null_is_found_and_written(tmp_path):
    """Chi legge la chiave normalizza il NULL a '': se chi scrive non facesse
    lo stesso, zero righe aggiornate, la finestra direbbe «corretto» e la
    riverifica ripresenterebbe lo stesso avviso per sempre."""
    from sqlalchemy import text
    h = _db_nulls(tmp_path)
    RC.apply_edits([RC.Edit(us="9/", set_fields=(("cron_iniziale", 1500),
                                                 ("cron_finale", 1600)),
                            target=("periodizzazione_table",
                                    {"periodo": "9", "fase": ""}))],
                   h, sito="S")
    with h.engine.connect() as c:
        assert c.execute(text(
            "SELECT cron_iniziale, cron_finale FROM periodizzazione_table "
            "WHERE sito='S' AND periodo=9")).fetchone() == (1500, 1600)


def test_a_us_row_whose_sito_is_null_is_refused_not_written_everywhere(tmp_path):
    """Senza il sito la clausola perdeva il predicato e la correzione finiva
    su tutti i siti: adesso rifiuta, e nessuna delle due righe si muove."""
    from sqlalchemy import text
    h = _db_nulls(tmp_path)
    with pytest.raises(ValueError, match="sito"):
        RC.apply_edits([RC.Edit(us="77",
                                set_fields=(("datazione", "SCRITTA"),))], h)
    with h.engine.connect() as c:
        righe = dict(c.execute(text(
            "SELECT sito, datazione FROM us_table WHERE us='77'")).fetchall())
    assert righe == {None: "vecchia", "ALTRO": "non toccare"}


def test_two_edits_on_the_same_column_roll_back_to_before_the_first(tmp_path):
    """Due `Edit` sulla stessa colonna della stessa riga: si applicano insieme,
    vince l'ultima, e l'annulla torna al valore di prima della prima — non a
    quello intermedio."""
    h = _db(tmp_path)
    target = ("periodizzazione_table", {"periodo": "2", "fase": "2.2"})
    edits = [RC.Edit(us="2/2.2", set_fields=(("cron_iniziale", 1510),),
                     target=target),
             RC.Edit(us="2/2.2", set_fields=(("cron_iniziale", 1520),),
                     target=target)]
    tok = RC.apply_edits(edits, h, sito="S")
    assert _periodo(h, "S", "2", "2.2") == (1520, 1549)
    RC.rollback(tok, h)
    assert _periodo(h, "S", "2", "2.2") == (1500, 1549)


def test_load_chronology_rows_reads_one_site_only(tmp_path):
    """Senza il filtro, le 2 sovrapposizioni di un sito diventano le 20 del
    database, e la correzione automatica riscriverebbe dieci siti in un colpo.

    La fixture porta di proposito una fase e una US del sito «ALTRO»: una per
    provare il filtro sulla periodizzazione, una per provare quello sulle US —
    senza la seconda, togliere il `WHERE sito` dalla query delle US non farebbe
    fallire niente.
    """
    from modules.utility import chronology_check as CC
    h = _db(tmp_path)
    periods, units = CC.load_chronology_rows(h, "S")
    assert len(periods) == 2
    assert {p["datazione_estesa"] for p in periods} == {
        "Prima metà del XVI secolo", "Prima metà del XV secolo rec"}
    assert [u["us"] for u in units] == ["12"]


def test_load_chronology_rows_hands_the_values_over_untouched(tmp_path):
    """Il lettore non converte niente: `periodo` torna come lo dà il motore
    (un intero) e la chiave la fa `_key`, che normalizza a testo. Convertire
    qui spaiererebbe le due sponde — sul database vero `fase` può tornare come
    REAL, perché SQLite memorizza 2.1 così.
    """
    from modules.utility import chronology_check as CC
    h = _db(tmp_path)
    periods, _ = CC.load_chronology_rows(h, "S")
    assert all(isinstance(p["periodo"], int) for p in periods), \
        [type(p["periodo"]) for p in periods]
    assert {CC._key(p) for p in periods} == {("2", "2.2"), ("3", "1")}


def test_the_sample_shaped_rows_go_straight_into_check_chronology(tmp_path):
    """Le due funzioni combaciano senza adattatori in mezzo."""
    from modules.utility import chronology_check as CC
    h = _db(tmp_path)
    periods, units = CC.load_chronology_rows(h, "S")
    kinds = sorted(i.kind for i in CC.check_chronology(
        periods, units, sito="S"))
    assert kinds == ["datazione_mismatch", "epoch_overlap"]


# ---------------------------------------------------------------------------
# L'identità di una riga di us_table è di QUATTRO colonne
# (`UniqueConstraint('sito', 'area', 'us', 'unita_tipo')`,
# modules/db/structures/US_table.py), e la chiave della correzione era una
# sola: su uno scavo a più aree — o su una US 1 e una USM 1, che il vincolo
# permette — una correzione ne riscriveva tutte, e l'annulla le appiattiva
# sul valore della prima.
# ---------------------------------------------------------------------------

def _db_due_aree(tmp_path):
    """Lo stesso numero di US in due aree, e una terza riga USM.

    Solo l'area 1 ha un periodo: il disallineamento è **uno**, e le altre due
    righe sono quelle che nessuno ha chiesto di toccare.
    """
    from s3dgraphy.sync._db_handle import DbHandle
    p = tmp_path / "aree.sqlite"
    c = sqlite3.connect(p)
    c.execute("CREATE TABLE us_table (sito TEXT, area TEXT, us TEXT,"
              " unita_tipo TEXT, rapporti TEXT, periodo_iniziale TEXT,"
              " fase_iniziale TEXT, periodo_finale TEXT, fase_finale TEXT,"
              " datazione TEXT)")
    c.execute("CREATE TABLE periodizzazione_table (sito TEXT,"
              " periodo INTEGER, fase TEXT, cron_iniziale INTEGER,"
              " cron_finale INTEGER, datazione_estesa TEXT, descrizione TEXT)")
    c.execute("INSERT INTO us_table VALUES ('S','1','1','US','[]','2','1',"
              "'2','1','SBAGLIATA')")
    c.execute("INSERT INTO us_table VALUES ('S','2','1','US','[]','','',"
              "'','','XV secolo')")
    c.execute("INSERT INTO us_table VALUES ('S','1','1','USM','[]','','',"
              "'','','muro, da non toccare')")
    c.execute("INSERT INTO periodizzazione_table VALUES "
              "('S',2,'1',1500,1549,'XVI secolo','')")
    c.commit(); c.close()
    return DbHandle.from_path(p)


def _righe(h):
    from sqlalchemy import text
    with h.engine.connect() as c:
        return c.execute(text(
            "SELECT area, us, unita_tipo, datazione FROM us_table "
            "WHERE sito='S' ORDER BY area, unita_tipo")).fetchall()


def test_load_chronology_rows_carries_area_and_unit_type(tmp_path):
    """Senza queste due colonne la correzione non può nominare la sua riga."""
    from modules.utility import chronology_check as CC
    h = _db_due_aree(tmp_path)
    _, units = CC.load_chronology_rows(h, "S")
    assert {(u["us"], u["area"], u["unita_tipo"]) for u in units} == {
        ("1", "1", "US"), ("1", "2", "US"), ("1", "1", "USM")}


def test_the_mismatch_edit_names_all_four_identity_columns(tmp_path):
    from modules.utility import chronology_check as CC
    h = _db_due_aree(tmp_path)
    periods, units = CC.load_chronology_rows(h, "S")
    issues = CC.check_chronology(periods, units, sito="S")
    assert [i.kind for i in issues] == ["datazione_mismatch"]
    edit, = issues[0].edits
    assert edit.target == ("us_table",
                           {"us": "1", "area": "1", "unita_tipo": "US"})


def test_one_fix_rewrites_one_row_and_not_the_whole_us_number(tmp_path):
    """Un disallineamento, una riga: «XV secolo» dell'area 2 non si perde, e
    il muro dell'area 1 nemmeno."""
    from modules.utility import chronology_check as CC
    h = _db_due_aree(tmp_path)
    periods, units = CC.load_chronology_rows(h, "S")
    edits = [e for i in CC.check_chronology(periods, units, sito="S")
             for e in i.edits]
    assert len(edits) == 1
    RC.apply_edits(edits, h, sito="S")
    assert _righe(h) == [("1", "1", "US", "XVI secolo"),
                         ("1", "1", "USM", "muro, da non toccare"),
                         ("2", "1", "US", "XV secolo")]


def test_the_undo_does_not_flatten_the_other_rows(tmp_path):
    """L'annulla scriveva «SBAGLIATA» anche dove non c'era mai stata."""
    from modules.utility import chronology_check as CC
    h = _db_due_aree(tmp_path)
    prima = _righe(h)
    periods, units = CC.load_chronology_rows(h, "S")
    edits = [e for i in CC.check_chronology(periods, units, sito="S")
             for e in i.edits]
    token = RC.apply_edits(edits, h, sito="S")
    assert _righe(h) != prima
    RC.rollback(token, h)
    assert _righe(h) == prima


def test_a_key_that_matches_more_than_one_row_refuses_to_write(tmp_path):
    """La guardia vale per qualunque produttore di correzioni, non solo per
    questa: una chiave ambigua è un errore, non una scrittura in silenzio."""
    h = _db_due_aree(tmp_path)
    prima = _righe(h)
    with pytest.raises(ValueError, match="individua 3 righe"):
        RC.apply_edits([RC.Edit(us="1",
                                set_fields=(("datazione", "X"),))], h, sito="S")
    assert _righe(h) == prima


def test_the_refusal_is_whole_and_leaves_nothing_half_written(tmp_path):
    """La correzione ambigua arriva in mezzo a una buona: la transazione
    rifiuta tutto, non la metà che aveva già scritto."""
    h = _db_due_aree(tmp_path)
    prima = _righe(h)
    buona = RC.Edit(us="1", set_fields=(("datazione", "XVI secolo"),),
                    target=("us_table", {"us": "1", "area": "1",
                                         "unita_tipo": "US"}))
    ambigua = RC.Edit(us="1", set_fields=(("datazione", "X"),))
    with pytest.raises(ValueError):
        RC.apply_edits([buona, ambigua], h, sito="S")
    assert _righe(h) == prima


def test_a_mismatch_edit_on_a_null_area_finds_its_row(tmp_path):
    """Il migratore DB→DB scrive NULL dove le schede scrivono '': la chiave
    normalizza a '' e `_where` confronta con COALESCE, quindi la riga si
    trova — se no, zero righe aggiornate e la finestra direbbe «corretto»."""
    from sqlalchemy import text

    from modules.utility import chronology_check as CC
    h = _db_due_aree(tmp_path)
    with h.engine.begin() as c:
        c.execute(text("UPDATE us_table SET area = NULL, unita_tipo = NULL "
                       "WHERE area = '1' AND unita_tipo = 'US'"))
    periods, units = CC.load_chronology_rows(h, "S")
    edits = [e for i in CC.check_chronology(periods, units, sito="S")
             for e in i.edits]
    assert edits[0].target == ("us_table",
                              {"us": "1", "area": "", "unita_tipo": ""})
    RC.apply_edits(edits, h, sito="S")
    with h.engine.connect() as c:
        assert c.execute(text(
            "SELECT datazione FROM us_table WHERE sito='S' AND area IS NULL")
        ).fetchone() == ("XVI secolo",)


# ---------------------------------------------------------------------------
# La chiave con uno spazio in coda: chi legge la strippa, chi scrive no
# ---------------------------------------------------------------------------

def test_a_mismatch_edit_finds_its_row_even_with_a_padded_area(tmp_path):
    """`area` è un `String(20)` battuto a mano: ci finisce uno spazio.

    Chi legge la chiave la strippa (`_text`), chi scriveva confrontava la
    colonna così com'è: zero righe aggiornate, snapshot vuoto, la finestra che
    diceva «1 correzioni applicate» e la riverifica che ripresentava lo stesso
    avviso per sempre — «dice corretti e non applica». È la stessa classe di
    guasto che il COALESCE ha chiuso per il NULL.
    """
    from sqlalchemy import text

    from modules.utility import chronology_check as CC
    h = _db_due_aree(tmp_path)
    with h.engine.begin() as c:
        c.execute(text("UPDATE us_table SET area = '1 ' "
                       "WHERE area = '1' AND unita_tipo = 'US'"))
    periods, units = CC.load_chronology_rows(h, "S")
    edits = [e for i in CC.check_chronology(periods, units, sito="S")
             for e in i.edits]
    assert len(edits) == 1
    assert edits[0].target == ("us_table", {"us": "1", "area": "1",
                                            "unita_tipo": "US"})
    token = RC.apply_edits(edits, h, sito="S")
    with h.engine.connect() as c:
        assert c.execute(text("SELECT datazione FROM us_table "
                              "WHERE sito='S' AND area='1 '")).fetchone() \
            == ("XVI secolo",)
    # Lo snapshot non è vuoto: l'annulla ha qualcosa da rimettere. Senza
    # questa prova, una scrittura a zero righe passerebbe per un annulla
    # riuscito.
    assert any(orig for (_sito, orig) in token.snapshot.values()), token
    RC.rollback(token, h)
    with h.engine.connect() as c:
        assert c.execute(text("SELECT datazione FROM us_table "
                              "WHERE sito='S' AND area='1 '")).fetchone() \
            == ("SBAGLIATA",)


def test_a_padded_us_is_found_too(tmp_path):
    """Il rischio c'era già sulla sola `us`, prima che la chiave crescesse:
    la correzione dei rapporti passa da qui con `target=()`."""
    from sqlalchemy import text
    h = _db(tmp_path)
    with h.engine.begin() as c:
        c.execute(text("UPDATE us_table SET us = '12 ' WHERE us = '12'"))
    RC.apply_edits([RC.Edit(us="12", set_fields=(("datazione", "XV secolo"),))],
                   h, sito="S")
    with h.engine.connect() as c:
        assert c.execute(text("SELECT datazione FROM us_table "
                              "WHERE sito='S' AND us='12 '")).fetchone() \
            == ("XV secolo",)


def test_a_padded_phase_is_found_too(tmp_path):
    """E sulla periodizzazione, dove `fase` è testo battuto a mano."""
    from sqlalchemy import text
    h = _db(tmp_path)
    with h.engine.begin() as c:
        c.execute(text("UPDATE periodizzazione_table SET fase = '2.2 ' "
                       "WHERE sito='S' AND fase = '2.2'"))
    RC.apply_edits([RC.Edit(us="2/2.2", set_fields=(("cron_finale", 1480),),
                            target=("periodizzazione_table",
                                    {"periodo": "2", "fase": "2.2"}))],
                   h, sito="S")
    with h.engine.connect() as c:
        assert c.execute(text(
            "SELECT cron_iniziale, cron_finale FROM periodizzazione_table "
            "WHERE sito='S' AND fase='2.2 '")).fetchone() == (1500, 1480)
