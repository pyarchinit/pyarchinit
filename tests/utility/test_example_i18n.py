"""Il database di esempio nelle altre nove lingue: il motore che copia e traduce.

«Riempi il db di esempio anche nelle altre lingue» (Enzo, 12 ottobre 2026).
Misurato: 27 tabelle piene solo per «Scavo archeologico», 2040 valori di
testo distinti — ma quasi tutti modelli («Ambiente 2») e vocabolario
(«Buona»), non prosa libera. Il motore è puro: frasi e modelli si passano
come argomenti, così le prove non dipendono dal dizionario vero, e quello
che non sa tradurre lo **conta** invece di tacerlo.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.example_i18n import (  # noqa: E402
    SITO_IT, copia_tabella, lingua_del_sito, riempi_us, traduci,
)

FRASI = {"Buona": {"en": "Good", "de": "Gut"},
         "Strato di terra": {"en": "Earth layer"}}
MODELLI = [(r"^Ambiente (\d+)$", {"en": "Room {0}", "de": "Raum {0}"}),
           (r"^Scheda US (\d+), fotopiano e sezione\.$",
            {"en": "SU sheet {0}, photo plan and section."})]


# ---------------------------------------------------------------- lingua

def test_every_demo_site_has_a_language():
    assert lingua_del_sito(SITO_IT) == "it"
    assert lingua_del_sito("Archaeological Excavation") == "en"
    assert lingua_del_sito("Αρχαιολογική Ανασκαφή") == "el"
    assert lingua_del_sito("تنقيب أثري") == "ar"
    assert lingua_del_sito("scavo_arc_ciao") is None


# ---------------------------------------------------------------- traduci

def test_a_phrase_is_translated_and_counted_as_found():
    assert traduci("Buona", "en", FRASI, MODELLI) == ("Good", True)


def test_a_template_keeps_its_number():
    assert traduci("Ambiente 2", "en", FRASI, MODELLI) == ("Room 2", True)
    assert traduci("Scheda US 17, fotopiano e sezione.", "en", FRASI, MODELLI) == \
        ("SU sheet 17, photo plan and section.", True)


def test_what_is_not_text_passes_through_as_found():
    for v in ("12.5", "3", "", None, "2021-04-05", "Q1", "SA-001"):
        assert traduci(v, "en", FRASI, MODELLI) == (v, True), v


def test_an_unknown_phrase_is_left_alone_and_reported():
    assert traduci("Terra battuta", "en", FRASI, MODELLI) == ("Terra battuta", False)


def test_a_phrase_known_in_another_language_only_is_reported():
    assert traduci("Strato di terra", "de", FRASI, MODELLI) == ("Strato di terra", False)


# ---------------------------------------------------------------- copia

@pytest.fixture
def db():
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE personale_table (id_personale INTEGER PRIMARY KEY, "
              "sito TEXT, nome TEXT, ruolo TEXT, ore REAL, data TEXT, entity_uuid TEXT)")
    c.executemany("INSERT INTO personale_table VALUES (?,?,?,?,?,?,?)", [
        (1, SITO_IT, "Marta", "Buona", 42.0, "2026-05-04", "u1"),
        (2, SITO_IT, "Luca", "Ambiente 3", 31.5, "2026-05-05", "u2"),
        (3, "Archäologische Ausgrabung", "Hans", "Gut", 1.0, "2026-05-06", "u3"),
    ])
    return c


def test_the_rows_of_the_italian_site_are_copied_translated(db):
    esito = copia_tabella(db, "personale_table", SITO_IT, "Archaeological Excavation",
                          "en", FRASI, MODELLI)
    assert esito.righe == 2 and esito.mancate == set()
    righe = db.execute("SELECT nome, ruolo, ore, data, entity_uuid, id_personale "
                       "FROM personale_table WHERE sito='Archaeological Excavation' "
                       "ORDER BY id_personale").fetchall()
    assert [r[:4] for r in righe] == [("Marta", "Good", 42.0, "2026-05-04"),
                                      ("Luca", "Room 3", 31.5, "2026-05-05")]
    uuids = {r[4] for r in righe}
    assert len(uuids) == 2 and not uuids & {"u1", "u2", "u3"}
    assert all(r[5] > 3 for r in righe)              # chiavi nuove, non riusate


def test_copying_twice_writes_nothing_the_second_time(db):
    copia_tabella(db, "personale_table", SITO_IT, "Archaeological Excavation", "en", FRASI, MODELLI)
    esito = copia_tabella(db, "personale_table", SITO_IT, "Archaeological Excavation", "en", FRASI, MODELLI)
    assert esito.righe == 0
    assert db.execute("SELECT count(*) FROM personale_table").fetchone()[0] == 5


def test_untranslated_values_are_copied_as_they_are_and_reported(db):
    esito = copia_tabella(db, "personale_table", SITO_IT, "Fouille Archéologique",
                          "fr", FRASI, MODELLI)
    assert esito.righe == 2
    assert esito.mancate == {"Buona", "Ambiente 3"}
    assert db.execute("SELECT ruolo FROM personale_table WHERE sito='Fouille Archéologique' "
                      "ORDER BY id_personale").fetchall() == [("Buona",), ("Ambiente 3",)]


# ---------------------------------------------------------------- scheda US

@pytest.fixture
def db_us():
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, sito TEXT, area TEXT, "
              "us TEXT, unita_tipo TEXT, descrizione TEXT, colore TEXT, ambient TEXT, "
              "quota_max_abs REAL, datazione TEXT)")
    c.executemany("INSERT INTO us_table VALUES (?,?,?,?,?,?,?,?,?,?)", [
        (1, SITO_IT, "1", "1", "US", "Strato di terra", "Bruno", "Ambiente 1", 488.4, "XV secolo"),
        (2, SITO_IT, "1", "12", "USM", "Strato di terra", "Rosso", "Ambiente 2", 488.1, "XV secolo"),
        (3, "Archaeological Excavation", "1", "1", "US", "", "Brown", None, None, "15th century"),
        (4, "Archaeological Excavation", "1", "12", "USM", "Wall", "", "", 480.0, "15th century"),
    ])
    return c


def test_only_the_empty_columns_of_the_other_site_are_filled(db_us):
    esito = riempi_us(db_us, SITO_IT, "Archaeological Excavation", "en", FRASI, MODELLI)
    # Solo «Rosso» si prova a tradurre: la US 1 inglese il colore ce l'ha
    # già («Brown»), e quello che il sito tradotto ha scritto resta suo.
    assert esito.mancate == {"Rosso"}
    r1 = db_us.execute("SELECT descrizione, colore, ambient, quota_max_abs, datazione "
                       "FROM us_table WHERE id_us=3").fetchone()
    assert r1 == ("Earth layer", "Brown", "Room 1", 488.4, "15th century")
    r2 = db_us.execute("SELECT descrizione, colore, ambient, quota_max_abs "
                       "FROM us_table WHERE id_us=4").fetchone()
    assert r2 == ("Wall", "Rosso", "Room 2", 480.0)   # «Wall» resta; il colore arriva, non tradotto


def test_filling_twice_changes_nothing(db_us):
    riempi_us(db_us, SITO_IT, "Archaeological Excavation", "en", FRASI, MODELLI)
    prima = db_us.execute("SELECT * FROM us_table ORDER BY id_us").fetchall()
    esito = riempi_us(db_us, SITO_IT, "Archaeological Excavation", "en", FRASI, MODELLI)
    assert esito.righe == 0
    assert db_us.execute("SELECT * FROM us_table ORDER BY id_us").fetchall() == prima


# ---------------------------------------------------------------- riferimenti

@pytest.fixture
def db_rif():
    """Le presenze puntano alle persone per id: copiando con chiavi nuove,
    il riferimento va rimappato o punta alla persona sbagliata."""
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE personale_table (id_personale INTEGER PRIMARY KEY, sito TEXT, nome TEXT)")
    c.execute("CREATE TABLE presenze_table (id_presenza INTEGER PRIMARY KEY, sito TEXT, "
              "id_personale INTEGER, data TEXT)")
    c.executemany("INSERT INTO personale_table VALUES (?,?,?)",
                  [(1, SITO_IT, "Marta"), (2, SITO_IT, "Luca"),
                   (3, "Archäologische Ausgrabung", "Hans")])
    c.executemany("INSERT INTO presenze_table VALUES (?,?,?,?)",
                  [(1, SITO_IT, 2, "2026-05-04"), (2, SITO_IT, 1, "2026-05-05")])
    return c


def test_the_copy_reports_old_to_new_keys(db_rif):
    esito = copia_tabella(db_rif, "personale_table", SITO_IT, "Archaeological Excavation",
                          "en", FRASI, MODELLI)
    assert esito.mappa_pk == {1: 4, 2: 5}


def test_a_reference_column_is_remapped_with_the_new_keys(db_rif):
    persone = copia_tabella(db_rif, "personale_table", SITO_IT, "Archaeological Excavation",
                            "en", FRASI, MODELLI)
    esito = copia_tabella(db_rif, "presenze_table", SITO_IT, "Archaeological Excavation",
                          "en", FRASI, MODELLI, rimappa={"id_personale": persone.mappa_pk})
    assert esito.righe == 2
    righe = db_rif.execute("SELECT id_personale, data FROM presenze_table "
                           "WHERE sito='Archaeological Excavation' ORDER BY id_presenza").fetchall()
    assert righe == [(5, "2026-05-04"), (4, "2026-05-05")]


# ---------------------------------------------------------------- codici

def test_codes_measures_and_roman_numerals_are_not_text():
    """Misurato sul primo giro: `IT-SA-0001`, `DIS_TMA_001`, `34 cm`,
    `1,5 - 2,5 cm`, `I`/`IV`, `A`…`E` finivano fra le frasi da tradurre."""
    from scripts.example_i18n import e_testo
    for v in ("IT-SA-0001", "DIS_TMA_001", "FOTO_TMA_010", "RA 001", "CP-01",
              "34 cm", "1,5 - 2,5 cm", "4,2 x 1,1 m", "I", "II", "IV", "A", "E",
              "Q3", "UE 1", "TM 6", "2021-04-05", "11-09-2012", "4/5/6"):
        assert not e_testo(v), v
    for v in ("Buona", "Ambiente 1", "Scheda US 1, fotopiano e sezione.",
              "Età del Ferro", "Scavo archeologico"):
        assert e_testo(v), v


def test_an_invariant_phrase_passes_as_found():
    """Nomi di persona e di luogo stanno in `INVARIANTI` e non si contano."""
    assert traduci("Volterra", "en", FRASI, MODELLI, invarianti={"Volterra"}) == ("Volterra", True)
    assert traduci("Volterra", "en", FRASI, MODELLI, invarianti=set()) == ("Volterra", False)


def test_fiscal_codes_invoices_file_names_scales_and_bearings_are_not_text():
    """Secondo giro: `BENMARX60A000A`, `FT/2026/0141`, `dem_us01_post.tif`,
    `1:20`, `1 : 1`, `E-W`, `NE-SW`, `—` finivano fra le frasi."""
    from scripts.example_i18n import e_testo
    for v in ("BENMARX60A000A", "FT/2026/0141", "dem_us01_post.tif", "1:20", "1 : 1",
              "E-W", "NE-SW", "—", "+11.4%", "pyunitastratigrafiche.shp"):
        assert not e_testo(v), v
    for v in ("Inumazione", "Personale", "sezione", "Modello 3D del saggio"):
        assert e_testo(v), v


def test_blobs_units_and_short_acronyms_are_not_text():
    """Terzo giro: le geometrie (BLOB) finivano nel dizionario, e con loro
    `m`, `USM`, `STR`, `GCP` e i progetti `.qgs`."""
    from scripts.example_i18n import e_testo
    for v in (b"\x00\x01\xbc\x0b", memoryview(b"\x00\x01"), "m", "cm", "USM", "STR",
              "GCP", "DosCo/sezioni/sez_A.qgs"):
        assert not e_testo(v), v
    for v in ("Mattina", "Scavo", "Base Camp"):
        assert e_testo(v), v


def test_a_translated_unit_type_still_finds_its_italian_row():
    """Misurato sulla copia: la scheda US in inglese, tedesco e spagnolo
    restava vuota. `riempi_us` cercava la riga italiana per codice **e
    tipo**, e il tipo è tradotto — `US`→`SU`, `USM`→`WSU`, `MSE`, `UEM`:
    la chiave non combaciava mai. Si confronta per famiglia."""
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, sito TEXT, area TEXT, "
              "us TEXT, unita_tipo TEXT, ambient TEXT, datazione TEXT)")
    c.executemany("INSERT INTO us_table VALUES (?,?,?,?,?,?,?)", [
        (1, SITO_IT, "1", "12", "USM", "Ambiente 2", "XV secolo"),
        (2, SITO_IT, "1", "3", "US", "Ambiente 1", "XV secolo"),
        (3, "Archaeological Excavation", "1", "12", "WSU", "", "15th century"),
        (4, "Archaeological Excavation", "1", "3", "SU", None, "15th century"),
        (5, "Archäologische Ausgrabung", "1", "12", "MSE", "", "15. Jahrhundert"),
    ])
    riempi_us(c, SITO_IT, "Archaeological Excavation", "en", FRASI, MODELLI)
    riempi_us(c, SITO_IT, "Archäologische Ausgrabung", "de", FRASI, MODELLI)
    assert c.execute("SELECT ambient FROM us_table WHERE id_us=3").fetchone() == ("Room 2",)
    assert c.execute("SELECT ambient FROM us_table WHERE id_us=4").fetchone() == ("Room 1",)
    assert c.execute("SELECT ambient FROM us_table WHERE id_us=5").fetchone() == ("Raum 2",)


# ---------------------------------------------------------------- per colonna

def test_a_name_column_is_intact_only_in_the_staff_table():
    """`nome` è un nome di persona nel personale, ma il nome di un attrezzo
    nelle attrezzature: «Stazione totale» restava in italiano."""
    from scripts.example_i18n import colonna_intatta
    assert colonna_intatta("personale_table", "nome")
    assert colonna_intatta("personale_table", "cognome")
    assert not colonna_intatta("attrezzature_table", "nome")
    assert colonna_intatta("attrezzature_table", "email")


def test_a_phrase_can_mean_something_else_in_one_column(db):
    """«Personale» è «personal» fra gli oggetti di una tomba e «staff» come
    voce di bilancio: il dizionario può dirlo per colonna."""
    db.execute("CREATE TABLE budget_table (id_budget INTEGER PRIMARY KEY, sito TEXT, categoria TEXT)")
    db.execute("INSERT INTO budget_table VALUES (1, ?, 'Personale')", (SITO_IT,))
    frasi = {"Personale": {"en": "Personal"}}
    per_colonna = {("budget_table", "categoria"): {"Personale": {"en": "Staff"}}}
    esito = copia_tabella(db, "budget_table", SITO_IT, "Archaeological Excavation", "en",
                          frasi, MODELLI, frasi_colonna=per_colonna)
    assert esito.righe == 1 and esito.mancate == set()
    assert db.execute("SELECT categoria FROM budget_table WHERE sito='Archaeological Excavation'"
                      ).fetchone() == ("Staff",)
