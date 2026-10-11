"""I dati di prova nelle schede del database di esempio.

`scripts/fill_example_db.py` mette dieci record in ogni scheda che era
vuota, con tutti i campi compilati, su «Scavo archeologico». Dati inventati
ma **coerenti**: i riferimenti puntano a righe che esistono davvero, e i
numeri si tengono fra loro.

Perché questi test: un `.sqlite` committato è un binario, e qui dentro ci
sono circa 4.300 valori. Se una scheda si svuota, se un riferimento resta
orfano, o se l'antropologia comincia a dire che il cranio è maschile e il
bacino femminile, la suite lo dice invece di farlo scoprire a un utente che
stava provando il plugin.

Chi li fa fallire rilanci::

    /Applications/QGIS.app/Contents/MacOS/bin/python3 scripts/fill_example_db.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

RADICE = Path(__file__).resolve().parents[2]
DB = RADICE / "resources" / "dbfiles" / "pyarchinit_db.sqlite"
SITO = "Scavo archeologico"
QUANTI = 10

#: Le schede riempite, con la colonna che porta il sito (`ut_table` lo
#: chiama `progetto`, `fauna` e le antropologiche non filtrano per sito in
#: questo conteggio).
SCHEDE = (
    ("personale_table", "sito"),
    ("presenze_table", "sito"),
    ("attrezzature_table", "sito"),
    ("budget_table", "sito"),
    ("campioni_table", "sito"),
    ("documentazione_table", "sito"),
    ("computo_metrico_table", "sito"),
    ("inventario_lapidei_table", "sito"),
    ("archeozoology_table", "sito"),
    ("fauna", "sito"),
    ("fauna_table", "sito"),
    ("tafonomia_table", "sito"),
    ("deteta_table", "sito"),
    ("detsesso_table", "sito"),
    ("ut_table", "progetto"),
)

#: Colonne che restano vuote **di proposito**, e perché.
#:
#: * `audit_trail` è il registro delle modifiche che il plugin scrive quando
#:   si salva una scheda: riempirlo di storia inventata vorrebbe dire
#:   raccontare modifiche che nessuno ha fatto;
#: * `editing_by` ed `editing_since` sono il **lucchetto** del record:
#:   `modules/db/concurrency_manager.py` guarda `editing_by IS NOT NULL AND
#:   editing_since > CURRENT_TIMESTAMP - INTERVAL '30 minutes'` e dichiara
#:   la scheda «in modifica da un altro utente». La prima passata di
#:   riempimento li aveva scritti su quaranta record di quattro schede —
#:   cioè un database di esempio con le schede bloccate — e l'11 ottobre
#:   2026 sono stati tolti;
#: * `fauna_table.id_us` è un riferimento interno che il form compila da sé
#:   quando la scheda si apre dalla US.
VUOTE_DI_PROPOSITO = {("*", "audit_trail"), ("*", "editing_by"),
                      ("*", "editing_since"), ("*", "last_modified_by"),
                      ("*", "last_modified_timestamp"),
                      ("*", "created_by"), ("*", "updated_by"),
                      ("*", "created_at"), ("*", "updated_at"),
                      ("fauna_table", "id_us")}


@pytest.fixture(scope="module")
def conn():
    if not DB.is_file():
        pytest.skip("manca il database di esempio")
    c = sqlite3.connect(DB)
    try:
        yield c
    finally:
        c.close()


@pytest.mark.parametrize("tabella,colonna_sito", SCHEDE)
def test_ogni_scheda_ha_almeno_dieci_record(conn, tabella, colonna_sito):
    n = conn.execute('SELECT count(*) FROM "%s" WHERE "%s" = ?'
                     % (tabella, colonna_sito), (SITO,)).fetchone()[0]
    assert n >= QUANTI, (tabella, n)


@pytest.mark.parametrize("tabella,colonna_sito", SCHEDE)
def test_in_ogni_scheda_tutti_i_campi_sono_compilati(conn, tabella,
                                                     colonna_sito):
    """Nessuna colonna resta vuota su tutte le righe, tranne quelle che
    devono restarlo."""
    colonne = [r[1] for r in conn.execute('PRAGMA table_info("%s")' % tabella)]
    tot = conn.execute('SELECT count(*) FROM "%s" WHERE "%s" = ?'
                       % (tabella, colonna_sito), (SITO,)).fetchone()[0]
    vuote = []
    for col in colonne:
        if ("*", col) in VUOTE_DI_PROPOSITO or (tabella, col) in VUOTE_DI_PROPOSITO:
            continue
        n = conn.execute(
            'SELECT count(*) FROM "%s" WHERE "%s" = ?'
            '   AND ("%s" IS NULL OR TRIM(CAST("%s" AS TEXT)) = \'\')'
            % (tabella, colonna_sito, col, col), (SITO,)).fetchone()[0]
        if n == tot:
            vuote.append(col)
    assert not vuote, (tabella, vuote)


# ---------------------------------------------------------------------------
# La coerenza: un riferimento che non punta a niente non serve a fare prove
# ---------------------------------------------------------------------------

def test_le_presenze_citano_persone_che_esistono(conn):
    orfane = conn.execute(
        "SELECT count(*) FROM presenze_table p WHERE NOT EXISTS ("
        " SELECT 1 FROM personale_table x"
        "  WHERE x.id_personale = p.id_personale)").fetchone()[0]
    assert orfane == 0


def test_le_attrezzature_sono_assegnate_a_persone_che_esistono(conn):
    orfane = conn.execute(
        "SELECT count(*) FROM attrezzature_table a"
        " WHERE a.assegnato_a IS NOT NULL AND NOT EXISTS ("
        " SELECT 1 FROM personale_table x"
        "  WHERE x.id_personale = a.assegnato_a)").fetchone()[0]
    assert orfane == 0


def test_i_campioni_citano_us_che_esistono(conn):
    orfani = conn.execute(
        "SELECT count(*) FROM campioni_table c WHERE c.sito = ?"
        "  AND NOT EXISTS (SELECT 1 FROM us_table u WHERE u.sito = c.sito"
        "   AND CAST(u.us AS TEXT) = CAST(c.us AS TEXT))",
        (SITO,)).fetchone()[0]
    assert orfani == 0


@pytest.mark.parametrize("tabella,colonna", [
    ("tafonomia_table", "nr_individuo"),
    ("deteta_table", "nr_individuo"),
    ("detsesso_table", "num_individuo"),
])
def test_l_antropologia_cita_individui_che_esistono(conn, tabella, colonna):
    orfani = conn.execute(
        'SELECT count(*) FROM "%s" t WHERE t.sito = ? AND NOT EXISTS ('
        " SELECT 1 FROM individui_table i WHERE i.sito = t.sito"
        '  AND i.nr_individuo = t."%s")' % (tabella, colonna),
        (SITO,)).fetchone()[0]
    assert orfani == 0


def test_il_cranio_e_il_bacino_dicono_lo_stesso_sesso(conn):
    """La coerenza interna dell'antropologia.

    Una scheda in cui gli indicatori cranici dicono maschile e quelli
    pelvici femminile non serve a provare niente: chi guarda il risultato
    non sa quale credere. Qui tutti gli indicatori di uno stesso individuo
    puntano nella stessa direzione, e il punteggio cranico totale ha il
    segno che gli tocca.
    """
    righe = conn.execute(
        "SELECT num_individuo, sex_cr_tot, ind_cr_sex, ind_bac_sex, sup_p_sex"
        " FROM detsesso_table WHERE sito = ?", (SITO,)).fetchall()
    assert righe, "la scheda deve avere dei record"
    for individuo, totale, cranio, bacino, pelvico in righe:
        assert cranio == bacino, (individuo, cranio, bacino)
        atteso = "M" if cranio == "Maschile" else "F"
        assert pelvico == atteso, (individuo, pelvico, cranio)
        if cranio == "Maschile":
            assert totale > 0, (individuo, totale)
        else:
            assert totale < 0, (individuo, totale)


def test_l_eta_stimata_sta_dentro_gli_intervalli_degli_indicatori(conn):
    """Gli intervalli `min`/`max` dei metodi si sovrappongono.

    Se la sinfisi pubica dice 20-30 e la superficie auricolare 50-60, la
    scheda si contraddice. Qui ogni indicatore contiene l'età stimata,
    quindi l'intersezione non è vuota.
    """
    righe = conn.execute(
        "SELECT nr_individuo, sinf_min, sinf_max, sup_aur_min, sup_aur_max,"
        " ms_sup_min, ms_sup_max, endo_min, endo_max"
        " FROM deteta_table WHERE sito = ?", (SITO,)).fetchall()
    assert righe
    for riga in righe:
        individuo = riga[0]
        estremi = [(riga[i], riga[i + 1]) for i in range(1, 9, 2)]
        for minimo, massimo in estremi:
            assert minimo is not None and massimo is not None, individuo
            assert minimo < massimo, (individuo, minimo, massimo)
        basso = max(m for m, _M in estremi)
        alto = min(M for _m, M in estremi)
        assert basso <= alto, (individuo, "intervalli disgiunti", estremi)


def test_il_computo_metrico_torna(conn):
    """Area per spessore fa volume: i numeri non sono messi a caso."""
    righe = conn.execute(
        "SELECT nome_calcolo, area_mq, volume_mc, quota_min, quota_max"
        " FROM computo_metrico_table WHERE sito = ?", (SITO,)).fetchall()
    assert righe
    for nome, area, volume, qmin, qmax in righe:
        assert qmax > qmin, (nome, qmin, qmax)
        atteso = area * (qmax - qmin)
        assert abs(volume - atteso) < 0.05, (nome, volume, atteso)


def test_le_ore_e_il_costo_della_giornata_si_tengono(conn):
    """Il costo è le ore per la tariffa della persona, con lo straordinario
    maggiorato del 30%."""
    righe = conn.execute(
        "SELECT p.id_presenza, p.ore_ordinarie, p.ore_straordinario,"
        " p.costo_giornata, x.tariffa_oraria"
        " FROM presenze_table p JOIN personale_table x"
        "   ON x.id_personale = p.id_personale"
        " WHERE p.sito = ?", (SITO,)).fetchall()
    assert righe
    for _id, ordinarie, straordinario, costo, tariffa in righe:
        atteso = ordinarie * tariffa + straordinario * tariffa * 1.3
        assert abs(costo - atteso) < 0.02, (costo, atteso)


def test_le_geometrie_delle_schede_nuove_ci_sono(conn):
    """Le schede che usano un disegno ne hanno uno, con l'indice attivo."""
    for tabella in ("pyarchinit_ut_polygon", "pyarchinit_ut_point",
                    "pyarchinit_reperti", "pyarchinit_individui",
                    "pyarchinit_campionature"):
        n = conn.execute('SELECT count(*) FROM "%s"' % tabella).fetchone()[0]
        assert n >= QUANTI, (tabella, n)
        idx = conn.execute(
            "SELECT count(*) FROM idx_%s_the_geom" % tabella).fetchone()[0]
        assert idx == n, (tabella, idx, n)
