"""Il database di prova che si installa accanto a quello di esempio.

`scripts/build_test_db.py` lo costruisce in
`resources/dbfiles/pyarchinit_db_test.sqlite` partendo dal database **vuoto**
(`pyarchinit.sqlite`, quello da cui il plugin crea i nuovi), e
`pyarchinit_Folder_installation.install_dir()` lo copia nella
`pyarchinit_DB_folder` dell'utente al primo avvio.

Perché questi test. Un `.sqlite` committato è un binario, e un binario
marcisce in silenzio quando lo schema cambia: è l'obiezione che il
generatore dei test si fa da sé nella sua docstring. Qui quella obiezione ha
una risposta — se il file resta indietro rispetto al database distribuito,
o se perde lo SRID, o l'indice spaziale, o uno dei casi, la suite lo dice.

Chi li fa fallire rifaccia il file::

    /Applications/QGIS.app/Contents/MacOS/bin/python3 scripts/build_test_db.py
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

RADICE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RADICE / "tests" / "fixtures"))
import realistic_site_db as RSD  # noqa: E402

PROVA = RADICE / "resources" / "dbfiles" / "pyarchinit_db_test.sqlite"
DISTRIBUITO = RADICE / "resources" / "dbfiles" / "pyarchinit_db.sqlite"

#: Tabelle che il database distribuito porta e che qui **non** si vogliono:
#: avanzi degli editor SQLite (un backup e due tabelle temporanee).
SPAZZATURA = {
    "inventario_materiali_table_backup_1760259102",
    "inventario_materiali_table_dg_tmp_dg_tmp",
    "sqlitestudio_temp_table2",
}


def _oggetti(percorso: Path) -> set:
    conn = sqlite3.connect(percorso)
    try:
        return {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table','view')")}
    finally:
        conn.close()


@pytest.fixture(scope="module")
def conn():
    if not PROVA.is_file():
        pytest.skip("manca %s: lancia scripts/build_test_db.py" % PROVA.name)
    c = sqlite3.connect(PROVA)
    try:
        yield c
    finally:
        c.close()


def test_il_file_si_chiama_sqlite_e_non_db():
    """pyArchInit legge i database con estensione `.sqlite`."""
    assert PROVA.suffix == ".sqlite"


def test_lo_schema_non_manca_niente_di_quello_distribuito():
    """Tutte le tabelle e le viste del distribuito, tranne la spazzatura.

    È la condizione che l'utente ha posto: «deve rispecchiare perfettamente
    lo schema, cioè avere tutte le tabelle, altrimenti pyarchinit non lo
    legge».
    """
    if not DISTRIBUITO.is_file():
        pytest.skip("manca il database distribuito")
    mancanti = _oggetti(DISTRIBUITO) - _oggetti(PROVA) - SPAZZATURA
    assert not mancanti, sorted(mancanti)


def test_la_spazzatura_degli_editor_non_viene_distribuita():
    assert not (_oggetti(PROVA) & SPAZZATURA)


def test_le_unita_topografiche_ci_sono(conn):
    """Il template vuoto non ha le UT: il costruttore le porta dal
    distribuito, se no la scheda UT non si apre su questo database."""
    oggetti = _oggetti(PROVA)
    for tabella in ("pyarchinit_ut_point", "pyarchinit_ut_line",
                    "pyarchinit_ut_polygon"):
        assert tabella in oggetti, tabella
        assert "%s_view" % tabella in oggetti, tabella


def test_la_vista_della_documentazione_c_e(conn):
    """`tabs/US_USM.py` la nomina come `view_name`. Il template vuoto non ce
    l'ha — cioè nessun database creato di nuovo ce l'ha — e qui sì."""
    assert "pyarchinit_doc_view" in _oggetti(PROVA)


def test_tutte_le_geometrie_hanno_un_solo_srid_e_l_indice(conn):
    """SRID 3004 su **ogni** colonna geometrica, e indice spaziale attivo.

    Non solo su quelle che si riempiono: un database con gli SRID misti è
    un progetto che non si inquadra, un layer a 3004 e uno a -1 nello
    stesso scavo. Nel template lo -1 è giusto — lo assegna pyArchInit
    quando crea il database nuovo — ma qui il database è già creato.

    E un `spatial_index_enabled = 0` con l'indice vuoto è il guasto delle
    «geometrie invisibili»: la tabella ha le righe e il layer non disegna
    niente.
    """
    righe = conn.execute(
        "SELECT f_table_name, srid, spatial_index_enabled"
        " FROM geometry_columns").fetchall()
    assert righe, "nessuna geometria registrata"
    sbagliate = [(t, s, i) for (t, s, i) in righe if s != 3004 or i != 1]
    assert not sbagliate, sbagliate


def test_l_indice_spaziale_e_popolato(conn):
    """Tante righe nell'indice quante geometrie: se no non si vede niente."""
    for tabella in ("pyunitastratigrafiche", "pyarchinit_quote"):
        geom = conn.execute(
            "SELECT count(*) FROM %s WHERE the_geom IS NOT NULL"
            % tabella).fetchone()[0]
        idx = conn.execute(
            "SELECT count(*) FROM idx_%s_the_geom" % tabella).fetchone()[0]
        assert geom > 0, tabella
        assert idx == geom, (tabella, idx, geom)


def test_le_statistiche_dicono_il_vero(conn):
    """`row_count` è quello che QGIS e OGR leggono invece di contare.

    Nel database distribuito quelle di `pyunitastratigrafiche` dicono 482
    righe quando sono 4820: OGR riporta 482 feature. Qui devono combaciare.
    """
    for tabella in ("pyunitastratigrafiche", "pyarchinit_quote"):
        vere = conn.execute("SELECT count(*) FROM %s" % tabella).fetchone()[0]
        dette = conn.execute(
            "SELECT row_count FROM geometry_columns_statistics"
            " WHERE f_table_name = ?", (tabella,)).fetchone()
        assert dette is not None, tabella
        assert dette[0] == vere, (tabella, dette[0], vere)


def test_ci_sono_i_due_siti_e_tutti_i_casi(conn):
    """Gli stessi casi dei test, perché vengono dalla stessa funzione."""
    siti = {r[0] for r in conn.execute("SELECT sito FROM site_table")}
    assert siti == set(RSD.siti())

    attese = len(RSD._schede())
    us = conn.execute(
        "SELECT count(*) FROM us_table WHERE sito = ?", (RSD.SITO,)
    ).fetchone()[0]
    assert us == attese

    # Caso 7: il sito vuoto ha la sua periodizzazione e nessuna scheda.
    assert conn.execute(
        "SELECT count(*) FROM us_table WHERE sito = ?", (RSD.SITO_VUOTO,)
    ).fetchone()[0] == 0
    assert conn.execute(
        "SELECT count(*) FROM periodizzazione_table WHERE sito = ?",
        (RSD.SITO_VUOTO,)).fetchone()[0] > 0


def test_la_stessa_us_sta_in_due_aree(conn):
    """Il caso che sul database di esempio non esiste."""
    doppie = conn.execute(
        "SELECT us FROM us_table WHERE sito = ? GROUP BY us"
        " HAVING count(DISTINCT area) > 1", (RSD.SITO,)).fetchall()
    assert doppie, "il senso del database di prova è questo"


def test_ci_sono_i_rapporti_di_uguaglianza(conn):
    """Caso 9: «Uguale a» e «Si lega a», per il segno di uguale nella
    matrice."""
    rapporti = " ".join(
        r[0] or "" for r in conn.execute(
            "SELECT rapporti FROM us_table WHERE sito = ?", (RSD.SITO,)))
    assert "Uguale a" in rapporti
    assert "Si lega a" in rapporti


def test_ogni_unita_ha_la_sua_geometria_e_la_sua_quota(conn):
    """La pianta sotto la matrice ha qualcosa da disegnare."""
    us = conn.execute("SELECT count(*) FROM us_table WHERE sito = ?",
                      (RSD.SITO,)).fetchone()[0]
    for tabella, colonna in (("pyunitastratigrafiche", "scavo_s"),
                             ("pyarchinit_quote", "sito_q")):
        n = conn.execute("SELECT count(*) FROM %s WHERE %s = ?"
                         % (tabella, colonna), (RSD.SITO,)).fetchone()[0]
        assert n == us, (tabella, n, us)


def test_l_installazione_lo_copia():
    """Senza questa riga in `db_files` il file non arriva all'utente."""
    sorgente = (RADICE / "modules" / "utility"
                / "pyarchinit_folder_installation.py").read_text()
    assert "pyarchinit_db_test.sqlite" in sorgente
