"""I due database che il plugin distribuisce, tenuti in riga.

* `resources/dbfiles/pyarchinit.sqlite` — il **vuoto**, quello da cui il
  plugin crea i nuovi. È il più importante: ogni sua lacuna si ripete in
  ogni database che un utente crea da qui in avanti.
* `resources/dbfiles/pyarchinit_db.sqlite` — quello **con i dati di
  esempio**, distribuito con gli esempi nelle dieci lingue.

Che cosa si è trovato l'11 ottobre 2026, e che questi test non lasciano
tornare:

1. **al vuoto mancavano le Unità Topografiche** e le loro viste — ci sono
   nel distribuito, quindi la scheda UT non funzionava su nessun database
   creato di nuovo;
2. **al vuoto mancava `pyarchinit_doc_view`**, la vista che
   `tabs/US_USM.py` nomina per la documentazione (il vuoto ha al suo posto
   `pyarchinit_doc_view_b`, che nessuno chiama);
3. **il distribuito portava tre tabelle di spazzatura** lasciate dagli
   editor SQLite, e stavano arrivando agli utenti;
4. **le statistiche del distribuito erano stantie** di un fattore dieci:
   `geometry_columns_statistics` diceva 482 righe per
   `pyunitastratigrafiche` (sono 4820) e 19 per
   `pyunitastratigrafiche_usm` (sono 190). `row_count` è quello che QGIS e
   OGR leggono invece di contare.

Chi li fa fallire rilanci::

    /Applications/QGIS.app/Contents/MacOS/bin/python3 scripts/fix_db_templates.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

RADICE = Path(__file__).resolve().parents[2]
VUOTO = RADICE / "resources" / "dbfiles" / "pyarchinit.sqlite"
DISTRIBUITO = RADICE / "resources" / "dbfiles" / "pyarchinit_db.sqlite"

#: Avanzi degli editor SQLite: un backup col timestamp nel nome e due
#: tabelle temporanee. Non vanno in nessuno dei due file.
SPAZZATURA = (
    "inventario_materiali_table_backup_1760259102",
    "inventario_materiali_table_dg_tmp_dg_tmp",
    "sqlitestudio_temp_table2",
)

#: Le tabelle delle Unità Topografiche, con la loro vista.
UT = ("pyarchinit_ut_point", "pyarchinit_ut_line", "pyarchinit_ut_polygon")


def _oggetti(percorso: Path) -> set:
    conn = sqlite3.connect(percorso)
    try:
        return {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table','view')")}
    finally:
        conn.close()


@pytest.fixture(params=["vuoto", "distribuito"])
def database(request):
    percorso = VUOTO if request.param == "vuoto" else DISTRIBUITO
    if not percorso.is_file():
        pytest.skip("manca %s" % percorso.name)
    return percorso


def test_nessuno_dei_due_distribuisce_la_spazzatura(database):
    presenti = _oggetti(database) & set(SPAZZATURA)
    assert not presenti, sorted(presenti)


@pytest.mark.parametrize("tabella", UT)
def test_le_unita_topografiche_ci_sono_in_entrambi(database, tabella):
    """Un database senza queste non apre la scheda UT."""
    oggetti = _oggetti(database)
    assert tabella in oggetti
    assert "%s_view" % tabella in oggetti


def test_la_vista_della_documentazione_ci_e_in_entrambi(database):
    """`tabs/US_USM.py` la nomina come `view_name`: senza, la
    documentazione della scheda US non trova il suo layer."""
    assert "pyarchinit_doc_view" in _oggetti(database)


def test_le_statistiche_dicono_il_vero(database):
    """`row_count` e l'estensione che QGIS e OGR leggono invece di contare.

    `UpdateLayerStatistics` da sola risponde «1» e non aggiorna niente
    quando la riga è marcata valida: va invalidata prima. Era questo a
    lasciare il distribuito con 482 righe dichiarate su 4820 vere.
    """
    conn = sqlite3.connect(database)
    try:
        sbagliate = []
        for tabella, detto in conn.execute(
                "SELECT f_table_name, row_count"
                " FROM geometry_columns_statistics"):
            try:
                vero = conn.execute(
                    'SELECT count(*) FROM "%s"' % tabella).fetchone()[0]
            except sqlite3.Error:
                continue                  # una vista o una tabella sparita
            if (detto or 0) != vero:
                sbagliate.append((tabella, detto, vero))
        assert not sbagliate, sbagliate
    finally:
        conn.close()


def test_nel_vuoto_lo_srid_resta_meno_uno():
    """Lo SRID del template **non** si tocca: lo assegna pyArchInit quando
    crea il database nuovo (Enzo, 11 ottobre 2026). Metterne uno qui
    vorrebbe dire imporre un sistema di riferimento a ogni scavo, compresi
    quelli fuori d'Italia.
    """
    if not VUOTO.is_file():
        pytest.skip("manca il template vuoto")
    conn = sqlite3.connect(VUOTO)
    try:
        sridi = {r[0] for r in conn.execute(
            "SELECT DISTINCT srid FROM geometry_columns")}
    finally:
        conn.close()
    assert sridi == {-1}, sorted(sridi)


def test_il_vuoto_e_vuoto():
    """Il database da cui si creano i nuovi non porta dati di nessuno."""
    if not VUOTO.is_file():
        pytest.skip("manca il template vuoto")
    conn = sqlite3.connect(VUOTO)
    try:
        for tabella in ("us_table", "site_table", "periodizzazione_table",
                        "pyunitastratigrafiche", "media_table"):
            n = conn.execute(
                'SELECT count(*) FROM "%s"' % tabella).fetchone()[0]
            assert n == 0, (tabella, n)
    finally:
        conn.close()


def test_il_vuoto_non_e_piu_povero_del_distribuito():
    """Tutte le tabelle e le viste del distribuito, tranne la spazzatura.

    È la lacuna che ha dato origine a tutto: due file che si credevano uno
    la versione piena dell'altro e invece erano **divergenti**.
    """
    if not (VUOTO.is_file() and DISTRIBUITO.is_file()):
        pytest.skip("manca uno dei due")
    mancanti = _oggetti(DISTRIBUITO) - _oggetti(VUOTO) - set(SPAZZATURA)
    assert not mancanti, sorted(mancanti)


# ---------------------------------------------------------------------------
# La cronologia del database di esempio (11 ottobre 2026)
# ---------------------------------------------------------------------------
# C'erano due fasi «rec» per sito, in tutte e dieci le lingue, che
# duplicavano gli anni di due fasi vere: 2/2.1 (1451-1499) = 2/3, e 2/3.1
# (1500-1549) = 2/2. Erano loro a far dire alla verifica che due periodi si
# sovrappongono, e la seconda portava anche l'etichetta sbagliata — 1500-1549
# è la prima metà del XVI secolo, non del XV.
#
# E sui nove siti tradotti la `datazione` delle US era rimasta in italiano
# mentre le fasi erano tradotte: quaranta disallineamenti per sito.

def test_nessuna_fase_duplica_gli_anni_di_un_altra():
    """Due fasi dello stesso periodo con gli stessi anni dicono la stessa
    cosa due volte, e la verifica cronologica le segnala come
    sovrapposizione."""
    if not DISTRIBUITO.is_file():
        pytest.skip("manca il database distribuito")
    conn = sqlite3.connect(DISTRIBUITO)
    try:
        doppie = conn.execute(
            "SELECT sito, periodo, cron_iniziale, cron_finale, count(*)"
            " FROM periodizzazione_table"
            " GROUP BY sito, periodo, cron_iniziale, cron_finale"
            " HAVING count(*) > 1").fetchall()
    finally:
        conn.close()
    assert not doppie, doppie


def test_nessuna_us_porta_una_datazione_rec():
    """Il testo «rec» era l'etichetta delle fasi doppie: via loro, via lui."""
    if not DISTRIBUITO.is_file():
        pytest.skip("manca il database distribuito")
    conn = sqlite3.connect(DISTRIBUITO)
    try:
        n = conn.execute(
            "SELECT count(*) FROM us_table WHERE"
            " lower(COALESCE(datazione,'')) LIKE '%rec%'"
            " OR lower(COALESCE(datazione,'')) LIKE '%rezent%'").fetchone()[0]
    finally:
        conn.close()
    assert n == 0


def test_la_datazione_di_ogni_us_dice_quello_che_dice_la_sua_fase():
    """La fase è la fonte; la scheda la ripete. Se non combaciano, la
    verifica cronologica segnala un disallineamento a ogni US datata."""
    if not DISTRIBUITO.is_file():
        pytest.skip("manca il database distribuito")
    conn = sqlite3.connect(DISTRIBUITO)
    try:
        discordi = conn.execute(
            "SELECT u.sito, u.us, u.datazione, p.datazione_estesa"
            " FROM us_table u JOIN periodizzazione_table p"
            "   ON p.sito = u.sito"
            "  AND CAST(p.periodo AS TEXT) = CAST(u.periodo_iniziale AS TEXT)"
            "  AND CAST(p.fase AS TEXT) = CAST(u.fase_iniziale AS TEXT)"
            " WHERE COALESCE(p.datazione_estesa,'') <> ''"
            "   AND COALESCE(u.datazione,'') <> COALESCE(p.datazione_estesa,'')"
        ).fetchall()
    finally:
        conn.close()
    assert not discordi, discordi[:5]
