"""Le correzioni dei rapporti e della cronologia, su PostgreSQL.

Perché su PostgreSQL e non solo su SQLite: SQLite confronta una colonna
`INTEGER` con una stringa convertendo da sé, PostgreSQL no — alza
`operator does not exist: integer = text` e la correzione non arriva mai
alla riga. `periodizzazione_table.periodo` è `INTEGER` e `fase` è `TEXT`
(lo schema è in `conftest_pg._apply_pyarchinit_schema`, come nel database
vero), quindi la chiave di una correzione cronologica è **mista** e il
`CAST(... AS TEXT)` di `rapporti_check._key_clause` è l'unica ragione per
cui funziona. Su SQLite quella riga di codice si può togliere e tutti i
test restano verdi: è il caso che solo PostgreSQL sa far fallire.

Gli altri due casi che qui si pinzano — l'identità di quattro colonne e il
`TRIM` — sono guasti che l'utente ha visto il 2026-10-10 («dice corretti e
non applica»), e stanno qui perché è su PostgreSQL che il suo scavo gira.
"""
from __future__ import annotations

import pytest
from sqlalchemy import text

from s3dgraphy.sync._db_handle import DbHandle

from modules.utility.rapporti_check import Edit, apply_edits, rollback
from tests.sync.conftest_pg import PG_CONN_STR, pg_engine, clean_pg  # noqa: F401


SITO = "Scavo di prova PG"


@pytest.fixture
def handle(clean_pg):  # noqa: F811
    return DbHandle.from_engine(clean_pg, PG_CONN_STR)


def _us(conn, *, area, us, unita_tipo="US", sito=SITO, **extra):
    cols = {"sito": sito, "area": area, "us": us, "unita_tipo": unita_tipo}
    cols.update(extra)
    conn.execute(
        text("INSERT INTO us_table (%s) VALUES (%s)"
             % (", ".join(cols), ", ".join(":" + c for c in cols))),
        cols,
    )


def _periodo(conn, *, periodo, fase, sito=SITO, **extra):
    cols = {"sito": sito, "periodo": periodo, "fase": fase}
    cols.update(extra)
    conn.execute(
        text("INSERT INTO periodizzazione_table (%s) VALUES (%s)"
             % (", ".join(cols), ", ".join(":" + c for c in cols))),
        cols,
    )


def _leggi(engine, sql, **params):
    with engine.connect() as conn:
        return conn.execute(text(sql), params).fetchall()


def test_la_chiave_di_quattro_colonne_tocca_una_riga_sola_su_pg(handle):
    """La US 5 esiste nell'area 1 e nell'area 2: si scrive una sola.

    L'identità di una scheda è `UniqueConstraint('sito', 'area', 'us',
    'unita_tipo')`. Con la sola `us` la clausola individua entrambe le
    righe e `apply_edits` si rifiuta — quindi questo test diventa rosso sia
    se la chiave si restringe (scrive la riga sbagliata) sia se si allarga
    (rifiuta e non scrive niente).
    """
    with handle.engine.begin() as conn:
        _us(conn, area="1", us="5", periodo_iniziale="1")
        _us(conn, area="2", us="5", periodo_iniziale="1")

    apply_edits(
        [Edit(us="5", set_fields=(("periodo_iniziale", "3"),),
              target=("us_table", {"us": "5", "area": "1",
                                   "unita_tipo": "US"}))],
        handle, sito=SITO,
    )

    righe = _leggi(handle.engine,
                   "SELECT area, periodo_iniziale FROM us_table "
                   "WHERE sito = :s ORDER BY area", s=SITO)
    assert righe == [("1", "3"), ("2", "1")]


def test_la_chiave_con_lo_spazio_in_coda_trova_la_riga_su_pg(handle):
    """`area = '1 '` nel database e `'1'` nella chiave: la riga si trova.

    `area` è testo battuto a mano in una scheda. Senza il `TRIM` la
    clausola non individua nessuna riga, la `UPDATE` ne scrive zero e la
    finestra dice comunque «1 correzioni applicate»: il guasto che l'utente
    ha segnalato come «dice corretti e non applica».
    """
    with handle.engine.begin() as conn:
        _us(conn, area="1 ", us="7", periodo_iniziale="1")

    apply_edits(
        [Edit(us="7", set_fields=(("periodo_iniziale", "4"),),
              target=("us_table", {"us": "7", "area": "1",
                                   "unita_tipo": "US"}))],
        handle, sito=SITO,
    )

    assert _leggi(handle.engine,
                  "SELECT periodo_iniziale FROM us_table WHERE sito = :s",
                  s=SITO) == [("4",)]


def test_la_chiave_intera_della_periodizzazione_si_confronta_come_testo(handle):
    """`periodizzazione_table.periodo` è INTEGER, la chiave arriva stringa.

    È il test che solo PostgreSQL sa far fallire: senza
    `CAST(periodo AS TEXT)` qui si alza `operator does not exist: integer
    = text` e la correzione non arriva mai alla riga. Su SQLite passerebbe
    comunque.

    Il valore nuovo è il 1500 negato: una cronologia `1500 → 1450` è un
    periodo a.C. battuto senza il meno (il caso del database Ventena).
    """
    with handle.engine.begin() as conn:
        _periodo(conn, periodo=2, fase="2.2",
                 cron_iniziale=1500, cron_finale=1450)

    apply_edits(
        [Edit(us="", set_fields=(("cron_iniziale", -1500),
                                 ("cron_finale", -1450)),
              target=("periodizzazione_table", {"periodo": "2",
                                                "fase": "2.2"}))],
        handle, sito=SITO,
    )

    assert _leggi(handle.engine,
                  "SELECT cron_iniziale, cron_finale FROM "
                  "periodizzazione_table WHERE sito = :s",
                  s=SITO) == [(-1500, -1450)]


def test_due_righe_con_la_stessa_chiave_si_rifiutano_su_pg(handle):
    """Chiave ambigua: si alza, e non si scrive niente.

    Due righe identiche nelle quattro colonne non dovrebbero esistere, ma
    un database vero le ha (il vincolo è arrivato dopo i dati). La
    `UPDATE` le riscriverebbe tutte e l'annulla le appiattirebbe su un
    valore che una delle due non ha mai avuto.
    """
    with handle.engine.begin() as conn:
        _us(conn, area="1", us="9", periodo_iniziale="1")
        _us(conn, area="1", us="9", periodo_iniziale="2")

    with pytest.raises(ValueError, match="individua 2 righe"):
        apply_edits(
            [Edit(us="9", set_fields=(("periodo_iniziale", "8"),),
                  target=("us_table", {"us": "9", "area": "1",
                                       "unita_tipo": "US"}))],
            handle, sito=SITO,
        )

    assert sorted(_leggi(handle.engine,
                         "SELECT periodo_iniziale FROM us_table "
                         "WHERE sito = :s", s=SITO)) == [("1",), ("2",)]


def test_l_annulla_riporta_i_valori_di_prima_su_pg(handle):
    """Un annulla che attraversa le due tabelle in un colpo."""
    with handle.engine.begin() as conn:
        _us(conn, area="1", us="5", periodo_iniziale="1",
            datazione="XV secolo")
        _periodo(conn, periodo=2, fase="2.2",
                 cron_iniziale=1500, cron_finale=1450)

    token = apply_edits(
        [Edit(us="5", set_fields=(("datazione", "XVI secolo"),),
              target=("us_table", {"us": "5", "area": "1",
                                   "unita_tipo": "US"})),
         Edit(us="", set_fields=(("cron_iniziale", -1500),),
              target=("periodizzazione_table", {"periodo": "2",
                                                "fase": "2.2"}))],
        handle, sito=SITO,
    )
    assert _leggi(handle.engine,
                  "SELECT datazione FROM us_table WHERE sito = :s",
                  s=SITO) == [("XVI secolo",)]

    rollback(token, handle)

    assert _leggi(handle.engine,
                  "SELECT datazione FROM us_table WHERE sito = :s",
                  s=SITO) == [("XV secolo",)]
    assert _leggi(handle.engine,
                  "SELECT cron_iniziale FROM periodizzazione_table "
                  "WHERE sito = :s", s=SITO) == [(1500,)]


def test_una_riga_senza_sito_non_si_scrive_su_pg(handle):
    """Sito NULL: si rifiuta, perché la chiave da sola nomina dieci scavi."""
    with handle.engine.begin() as conn:
        _us(conn, area="1", us="5", sito=None, periodo_iniziale="1")

    with pytest.raises(ValueError, match="ha bisogno del sito"):
        apply_edits(
            [Edit(us="5", set_fields=(("periodo_iniziale", "3"),),
                  target=("us_table", {"us": "5", "area": "1",
                                       "unita_tipo": "US"}))],
            handle,
        )

    assert _leggi(handle.engine,
                  "SELECT periodo_iniziale FROM us_table") == [("1",)]
