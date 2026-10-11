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


def test_nell_esempio_ogni_geometria_sta_nello_stesso_sistema():
    """Le UT erano registrate a `srid = -1` mentre le altre diciannove
    tabelle spaziali stanno a 3004.

    Un progetto con i sistemi misti non si inquadra, e un layer a -1 QGIS lo
    apre senza proiezione. Qui il database è quello di **esempio**, cioè già
    creato: lo -1 è giusto solo nel template, dove lo SRID lo assegna
    pyArchInit alla creazione.
    """
    if not DISTRIBUITO.is_file():
        pytest.skip("manca il database distribuito")
    conn = sqlite3.connect(DISTRIBUITO)
    try:
        sridi = {r[0] for r in conn.execute(
            "SELECT DISTINCT srid FROM geometry_columns")}
        storte = conn.execute(
            "SELECT f_table_name, srid, spatial_index_enabled"
            " FROM geometry_columns WHERE srid <> 3004"
            "    OR spatial_index_enabled <> 1").fetchall()
    finally:
        conn.close()
    assert sridi == {3004}, sorted(sridi)
    assert not storte, storte


# ---------------------------------------------------------------------------
# Il thesaurus: i vocabolari che riempiono i menu a tendina
# ---------------------------------------------------------------------------
# Le schede interrogano `pyarchinit_thesaurus_sigle` con
# `{'nome_tabella': "'" + 'tomba_table' + "'"}`, cioè col nome della
# TABELLA. Il database di esempio archiviava le voci sotto il nome che la
# finestra del Thesaurus **mostra** — «Tomba», «Struttura», «Sito»,
# «Inventario Materiali» — che è il nome del Mapper: 232 voci che nessuna
# scheda poteva trovare, e i menu uscivano vuoti.
#
# La fonte non è un'opinione: `tabs/Thesaurus.py` porta la mappa
# `TABLE_DISPLAY_MAPPING_I18N` — `'Sito': 'site_table'`, `'US': 'us_table'`
# — e `SYNCHRONIZED_FIELDS`, che usa i nomi di tabella.

#: I nomi da mostrare, che non vanno MAI salvati in `nome_tabella`.
NOMI_DA_MOSTRARE = ("Sito", "US", "Tomba", "Struttura",
                    "Inventario Materiali", "Campioni", "Fauna")


def test_il_thesaurus_usa_i_nomi_delle_tabelle_non_quelli_del_mapper():
    if not DISTRIBUITO.is_file():
        pytest.skip("manca il database distribuito")
    conn = sqlite3.connect(DISTRIBUITO)
    try:
        nomi = {r[0] for r in conn.execute(
            "SELECT DISTINCT nome_tabella FROM pyarchinit_thesaurus_sigle")}
    finally:
        conn.close()
    sbagliati = nomi & set(NOMI_DA_MOSTRARE)
    assert not sbagliati, sorted(sbagliati)


def test_le_schede_trovano_i_loro_vocabolari():
    """Le coppie (tabella, sigla) che il codice chiede devono esistere.

    Si leggono dalle schede invece di elencarle qui: una scheda che domani
    chiede un vocabolario nuovo fa fallire questo test, che è il momento in
    cui ci si accorge che il menu uscirebbe vuoto.

    Non tutte: ventuno coppie restano scoperte e sono elencate in
    `ANCORA_VUOTI`, perché il codice non dice che cosa siano — il menu che
    riempiono non ha un nome parlante — e inventarci dentro dei termini
    sarebbe peggio che lasciarle vuote.
    """
    import re
    tabelle = re.compile(r"'nome_tabella'\s*:\s*\"'\"\s*\+\s*'([^']+)'")
    sigle = re.compile(r"'tipologia_sigla'\s*:\s*\"'\"\s*\+\s*'?([^'\"+)]+)'?")
    chieste = set()
    for f in sorted((RADICE / "tabs").glob("*.py")):
        testo = f.read_text(encoding="utf-8", errors="ignore")
        for m in tabelle.finditer(testo):
            coda = testo[m.end():m.end() + 300]
            for s in sigle.finditer(coda):
                valore = s.group(1).strip()
                if valore and len(valore) < 12:
                    chieste.add((m.group(1), valore))
    assert chieste, "l'estrazione non ha trovato nessuna richiesta"

    if not DISTRIBUITO.is_file():
        pytest.skip("manca il database distribuito")
    conn = sqlite3.connect(DISTRIBUITO)
    try:
        presenti = {(t, s) for t, s in conn.execute(
            "SELECT nome_tabella, tipologia_sigla"
            " FROM pyarchinit_thesaurus_sigle WHERE lingua = 'IT'")}
    finally:
        conn.close()
    mancanti = sorted(chieste - presenti - ANCORA_VUOTI)
    assert not mancanti, mancanti


#: Le coppie che restano senza vocabolario, e che il test qui sopra lascia
#: passare: il codice non dice che cosa siano. Si riempiono quando si sa.
ANCORA_VUOTI = {
    ("TMA materiali archeologici", s) for s in
    ("10.1", "10.15", "10.2", "10.3", "10.4", "10.5", "10.6", "10.7", "10.9")
} | {
    ("inventario_materiali_table", s) for s in
    ("3.10", "3.4", "3.7", "3.8", "3.9")
} | {
    ("struttura_table", s) for s in
    ("6.10", "6.11", "6.12", "6.13", "6.14", "6.9")
} | {("tma_materiali_ripetibili", "10.12")}


def test_le_aree_dicono_la_stessa_cosa_in_tutte_le_schede():
    """`SYNCHRONIZED_FIELDS` tiene insieme i campi «area» di più schede: se
    le voci divergono, la stessa area si chiama in due modi a seconda
    della scheda da cui la si guarda."""
    if not DISTRIBUITO.is_file():
        pytest.skip("manca il database distribuito")
    coppie = (("inventario_materiali_table", "3.11"),
              ("tomba_table", "7.8"), ("individui_table", "8.6"))
    conn = sqlite3.connect(DISTRIBUITO)
    try:
        viste = []
        for tabella, sigla in coppie:
            voci = {r[0] for r in conn.execute(
                "SELECT sigla_estesa FROM pyarchinit_thesaurus_sigle"
                " WHERE nome_tabella = ? AND tipologia_sigla = ?"
                "   AND lingua = 'IT'", (tabella, sigla))}
            if voci:
                viste.append((tabella, voci))
    finally:
        conn.close()
    assert len(viste) >= 2, viste
    prima = viste[0][1]
    for tabella, voci in viste[1:]:
        assert voci == prima, (tabella, sorted(voci), sorted(prima))
