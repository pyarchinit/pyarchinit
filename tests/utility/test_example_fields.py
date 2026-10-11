"""I campi delle cinque schede preesistenti del database di esempio.

«Rivedi il db di esempio: non tutti i campi sono riempiti di tutte le
schede… mi raccomando tutti i campi, nessuno escluso» (Enzo, 11 ottobre
2026). Le quindici schede che erano **vuote** le riempie
`scripts/fill_example_db.py` (dieci record ciascuna); le cinque che
c'erano già — tombe, individui, ceramica, reperti, strutture — le completa
`scripts/fill_example_fields.py`, e questo file misura il risultato.

Quattro garanzie, e il perché di ognuna:

1. **Nessuna colonna vuota in tutte le righe.** Un campo che in dieci
   record non ha mai un valore non si può provare.
2. **Il tipo della colonna.** `peso` è `Numeric(9,3)` e `box` è
   `Integer`: scrivere «31.5 g» e «B01» passa in SQLite e poi rompe la
   **lettura** con «must be real number, not str» — è il guasto che la
   migrazione DB→DB ha trovato, e che la memoria del progetto chiama
   «ORM schema drift hides under SQLite, breaks under PG».
3. **I valori stanno nei vocabolari.** Un campo che mostra «Invetriatura»
   mentre la sua tendina non la offre è un valore che l'utente non
   ritrova: i valori dei campi a tendina devono venire dal thesaurus.
4. **I riferimenti puntano a qualcosa.** «Materiali e strutture nella
   scheda US si riferiscono alle schede strutture e materiali»: una
   struttura nominata deve esistere, col nome che la tendina della scheda
   offre (`ED-1`, non `ED01`).
"""
from __future__ import annotations

import ast
import re
import sqlite3
import sys
from pathlib import Path

import pytest

RADICE = Path(__file__).resolve().parents[2]
if str(RADICE) not in sys.path:
    sys.path.insert(0, str(RADICE))

DB = RADICE / "resources" / "dbfiles" / "pyarchinit_db.sqlite"
SITO = "Scavo archeologico"

#: Le cinque schede che c'erano già, e che lo script completa.
SCHEDE = ("tomba_table", "individui_table", "pottery_table",
          "inventario_materiali_table", "struttura_table")

#: Le colonne che restano vuote **di proposito**.
#:
#: `editing_by` e `editing_since` sono il lucchetto del record:
#: `modules/db/concurrency_manager.py` guarda `editing_by IS NOT NULL AND
#: editing_since > CURRENT_TIMESTAMP - INTERVAL '30 minutes'` e dichiara la
#: scheda «in modifica da un altro utente» — un database di esempio con le
#: schede bloccate non si può usare. `audit_trail` è il registro delle
#: modifiche: riempirlo vorrebbe dire raccontare modifiche che nessuno ha
#: fatto.
MACCHINA = {"editing_by", "editing_since", "audit_trail"}


@pytest.fixture(scope="module")
def conn():
    if not DB.is_file():
        pytest.skip("manca %s" % DB)
    c = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
    c.row_factory = sqlite3.Row
    yield c
    c.close()


def _colonne(conn, tabella):
    return [r[1] for r in conn.execute('PRAGMA table_info("%s")' % tabella)]


def _righe(conn, tabella):
    return conn.execute('SELECT * FROM "%s" WHERE sito = ?' % tabella,
                        (SITO,)).fetchall()


def _voci(conn, tabella, sigla, campo="sigla_estesa", lingua="IT"):
    return {str(v).strip() for (v,) in conn.execute(
        "SELECT %s FROM pyarchinit_thesaurus_sigle WHERE nome_tabella = ?"
        " AND tipologia_sigla = ? AND upper(coalesce(lingua,'')) = ?" % campo,
        (tabella, sigla, lingua)) if v and str(v).strip()}


def _lista(valore):
    try:
        letto = ast.literal_eval(valore) if valore else []
    except Exception:
        return []
    return [v for v in letto if isinstance(v, (list, tuple))]


# --------------------------------------------------------------------------
# 1. Nessuna colonna vuota in tutte le righe
# --------------------------------------------------------------------------

@pytest.mark.parametrize("tabella", SCHEDE)
def test_ogni_colonna_ha_un_valore_in_almeno_una_riga(conn, tabella):
    righe = _righe(conn, tabella)
    assert len(righe) >= 10, "%s ha %d record" % (tabella, len(righe))
    vuote = []
    for col in _colonne(conn, tabella):
        if col in MACCHINA:
            continue
        if not any(r[col] is not None
                   and str(r[col]).strip() not in ("", "[[]]", "[]")
                   for r in righe):
            vuote.append(col)
    assert vuote == [], vuote


@pytest.mark.parametrize("tabella", SCHEDE)
def test_il_lucchetto_del_record_resta_vuoto(conn, tabella):
    """Un database di esempio con le schede «in modifica» non si usa."""
    for r in _righe(conn, tabella):
        for col in ("editing_by", "editing_since"):
            if col in r.keys():
                assert not (r[col] or "").strip(), (tabella, col, r[col])


# --------------------------------------------------------------------------
# 2. Il tipo della colonna
# --------------------------------------------------------------------------

_MAPPER = {
    "tomba_table": "Tomba_table.py",
    "pottery_table": "Pottery_table.py",
    "struttura_table": "Struttura_table.py",
    "inventario_materiali_table": "Inventario_materiali_table.py",
}


@pytest.mark.parametrize("tabella", sorted(_MAPPER))
def test_le_colonne_numeriche_contengono_numeri(conn, tabella):
    """SQLite accetta una stringa in una colonna numerica; il mapper no.

    `peso` è `Numeric(9,3)`, `box` e `bag` sono `Integer`: con «31.5 g» e
    «B01» dentro, la migrazione DB→DB si fermava su
    `must be real number, not str`.
    """
    sorgente = (RADICE / "modules" / "db" / "structures"
                / _MAPPER[tabella]).read_text(encoding="utf-8")
    tipi = dict(re.findall(r"Column\('([^']+)',\s*([A-Za-z]+)", sorgente))
    numeriche = [c for c, t in tipi.items()
                 if t in ("Integer", "Numeric", "Float")
                 and c in _colonne(conn, tabella)]
    assert numeriche, tabella
    guasti = []
    for r in _righe(conn, tabella):
        for col in numeriche:
            v = r[col]
            if v is None or str(v).strip() == "":
                continue
            try:
                float(v)
            except (TypeError, ValueError):
                guasti.append((col, v))
    assert guasti == [], guasti


# --------------------------------------------------------------------------
# 3. I valori stanno nei vocabolari
# --------------------------------------------------------------------------

def test_la_ceramica_ha_i_suoi_sedici_vocabolari(conn):
    """Le tendine della scheda Pottery vengono da
    `sql/pottery_thesaurus_sqlite.sql`, che il plugin installa al primo
    avvio e che nel file spedito non era mai stato caricato."""
    sigle = {s for (s,) in conn.execute(
        "SELECT DISTINCT tipologia_sigla FROM pyarchinit_thesaurus_sigle"
        " WHERE nome_tabella = 'Pottery'")}
    attese = {"11.%d" % n for n in range(1, 17)}
    assert attese <= sigle, sorted(attese - sigle)


@pytest.mark.parametrize("colonna,sigla", [
    ("fabric", "11.1"), ("specific_form", "11.5"), ("munsell", "11.7"),
    ("exdeco", "11.9"), ("intdeco", "11.10"), ("specific_shape", "11.12"),
    ("decoration_type", "11.14"), ("decoration_motif", "11.15"),
    ("decoration_position", "11.16"),
])
def test_i_campi_della_ceramica_mostrano_voci_del_vocabolario(conn, colonna,
                                                              sigla):
    voci = _voci(conn, "Pottery", sigla)
    assert voci, sigla
    for r in _righe(conn, "pottery_table"):
        valore = (r[colonna] or "").strip()
        if valore:
            assert valore in voci, (colonna, valore, sorted(voci)[:6])


def test_la_percentuale_conservata_sta_nellintervallo_dichiarato(conn):
    """`percent` offre intervalli («25-50»): la percentuale conservata non
    può starne fuori, se no la scheda dice due cose diverse."""
    for r in _righe(conn, "pottery_table"):
        scelta, conservato = (r["percent"] or "").strip(), r["diametro_preserved"]
        if not scelta or conservato is None:
            continue
        numeri = [float(x) for x in re.findall(r"\d+", scelta)]
        if len(numeri) >= 2:
            assert min(numeri) <= float(conservato) <= max(numeri), \
                (scelta, conservato)


def test_la_descrizione_della_decorazione_non_contraddice_il_si_o_no(conn):
    positive = ("sì", "si", "yes", "ja")
    for r in _righe(conn, "pottery_table"):
        for risposta, descrizione in (("exdeco", "descrip_ex_deco"),
                                      ("intdeco", "descrip_in_deco")):
            detto = (r[risposta] or "").strip().lower()
            testo = (r[descrizione] or "").strip().lower()
            if not detto or not testo:
                continue
            decorata = "priva di decorazione" not in testo
            assert decorata == (detto in positive), (risposta, detto, testo[:40])


@pytest.mark.parametrize("colonna,posizione,sigla", [
    ("elementi_reperto", 0, "3.4"),
    ("misurazioni", 0, "3.5"),
    ("misurazioni", 1, "3.6"),
    ("tecnologie", 0, "3.7"),
    ("tecnologie", 1, "3.8"),
])
def test_le_tabelle_dentro_la_scheda_reperti_usano_le_loro_tendine(
        conn, colonna, posizione, sigla):
    voci = _voci(conn, "inventario_materiali_table", sigla)
    assert voci, sigla
    for r in _righe(conn, "inventario_materiali_table"):
        for voce in _lista(r[colonna]):
            if len(voce) > posizione and str(voce[posizione]).strip():
                assert str(voce[posizione]).strip() in voci, \
                    (colonna, posizione, voce)


@pytest.mark.parametrize("colonna,posizione,sigla", [
    ("misure_struttura", 1, "6.9"),
    ("misure_struttura", 2, "6.7"),
    ("misure_struttura", 3, "6.8"),
    ("stato_conservazione", 2, "6.10"),
    ("prospetto_ingresso", 0, "6.11"),
    ("elementi_costitutivi", 0, "6.12"),
    ("manufatti", 0, "6.13"),
    ("fasi_funzionali", 2, "6.14"),
])
def test_le_tabelle_dentro_la_scheda_struttura_usano_le_loro_tendine(
        conn, colonna, posizione, sigla):
    voci = _voci(conn, "struttura_table", sigla)
    assert voci, sigla
    for r in _righe(conn, "struttura_table"):
        for voce in _lista(r[colonna]):
            if len(voce) > posizione and str(voce[posizione]).strip():
                assert str(voce[posizione]).strip() in voci, \
                    (colonna, posizione, voce)


def test_la_quantita_e_la_sua_unita_vanno_daccordo(conn):
    """Contare frammenti in «%» o pesarli in «nr» non vuol dire niente."""
    for r in _righe(conn, "inventario_materiali_table"):
        for voce in _lista(r["tecnologie"]):
            if len(voce) < 4:
                continue
            tipo, unita = str(voce[2]).lower(), str(voce[3]).strip()
            if "frammenti" in tipo or "esemplari" in tipo:
                assert unita == "nr", voce
            elif "peso" in tipo:
                assert unita in ("g", "kg"), voce


def test_le_forme_minime_non_superano_le_massime_ne_il_totale(conn):
    for r in _righe(conn, "inventario_materiali_table"):
        minime, massime = r["forme_minime"], r["forme_massime"]
        totale = r["totale_frammenti"]
        if minime is None or massime is None or totale is None:
            continue
        assert int(minime) <= int(massime) <= int(totale), \
            (minime, massime, totale)


def test_lorlo_non_e_piu_piccolo_del_fondo(conn):
    for r in _righe(conn, "pottery_table"):
        orlo, fondo = r["diametro_rim"], r["diametro_bottom"]
        if orlo is None or fondo is None:
            continue
        assert float(orlo) >= float(fondo), (orlo, fondo)


# --------------------------------------------------------------------------
# 4. I riferimenti puntano a qualcosa
# --------------------------------------------------------------------------

def _strutture(conn):
    return {"%s-%s" % (s, n) for s, n in conn.execute(
        "SELECT sigla_struttura, numero_struttura FROM struttura_table"
        " WHERE sito = ?", (SITO,))}


def test_la_struttura_di_un_reperto_esiste(conn):
    vere = _strutture(conn)
    for r in _righe(conn, "inventario_materiali_table"):
        valore = (r["struttura"] or "").strip()
        if valore:
            assert valore in vere, (valore, sorted(vere))


def test_la_struttura_di_unus_e_quella_che_la_tendina_offre(conn):
    """La scheda US riempie il menu con `f"{sigla}-{numero}"`
    (`US_USM.format_struttura_item`): il file spedito aveva «ED01», che in
    quella lista non c'è."""
    vere = _strutture(conn)
    for (valore,) in conn.execute(
            "SELECT struttura FROM us_table WHERE sito = ?"
            " AND trim(coalesce(struttura,'')) <> ''", (SITO,)):
        for pezzo in str(valore).split("/"):
            assert pezzo.strip() in vere, (valore, sorted(vere))


def test_i_rapporti_fra_strutture_sono_veri_e_reciproci(conn):
    """Nel file spedito `ED 1` citava un altro sito («Via Ortaggi… Rimini»)
    e una `ED 3` che non esiste, con due rapporti che la scheda non offre
    («Fa parte di», «Taglia») e nessun reciproco."""
    from scripts.fill_example_fields import INVERSO_STRUTTURA

    vere = {}
    for id_str, sigla, numero, testo in conn.execute(
            "SELECT id_struttura, sigla_struttura, numero_struttura,"
            " rapporti_struttura FROM struttura_table WHERE sito = ?",
            (SITO,)):
        vere[(str(sigla), str(numero))] = _lista(testo)

    for chiave, voci in vere.items():
        for voce in voci:
            assert len(voce) >= 4, (chiave, voce)
            tipo, sito_voce, sigla, numero = [str(x).strip() for x in voce[:4]]
            assert sito_voce == SITO, (chiave, voce)
            assert tipo in INVERSO_STRUTTURA, (chiave, tipo)
            altra = (sigla, numero)
            assert altra in vere, (chiave, voce)
            inverso = INVERSO_STRUTTURA[tipo]
            assert any(v[0] == inverso and (str(v[2]), str(v[3])) == chiave
                       for v in vere[altra]), \
                "manca il reciproco di %s %s su %s" % (chiave, tipo, altra)


def test_nessuna_us_resta_col_periodo_finale_vuoto(conn):
    """Quando il finale manca la verifica non dice «va bene», dice «non
    posso valutare»: cinque avvisi «manca la datazione di periodo» sul
    database di esempio, che adesso non ci sono più."""
    aperte = conn.execute(
        "SELECT count(*) FROM us_table"
        " WHERE trim(coalesce(periodo_iniziale,'')) <> ''"
        "   AND trim(coalesce(periodo_finale,'')) = ''").fetchone()[0]
    assert aperte == 0, aperte


def test_tutti_i_vocabolari_che_le_schede_chiedono_esistono(conn):
    """Censimento: ogni coppia (nome_tabella, tipologia_sigla) che una
    scheda interroga deve avere voci nel thesaurus, se no il menu esce
    vuoto. Erano 21 a mancare su 62."""
    chiesti = set()
    pat = re.compile(
        r"'nome_tabella':\s*(?:\"'\"\s*\+\s*)?['\"]'?([A-Za-z_ ]+)'?['\"]"
        r"(?:\s*\+\s*\"'\")?\s*,\s*(?:'sigla':[^,]+,\s*)?"
        r"'tipologia_sigla':\s*(?:\"'\"\s*\+\s*)?['\"]'?([0-9.]+)'?['\"]")
    pat2 = re.compile(r"voci_vocabolario\(\s*[^,]+,\s*'([^']+)',\s*'([^']+)'")
    for sorgente in sorted((RADICE / "tabs").glob("*.py")):
        testo = sorgente.read_text(encoding="utf-8", errors="replace")
        for m in pat.finditer(testo):
            chiesti.add((m.group(1).strip(), m.group(2).strip()))
        for m in pat2.finditer(testo):
            chiesti.add((m.group(1).strip(), m.group(2).strip()))
    assert len(chiesti) > 40, len(chiesti)
    presenti = {(str(t).strip(), str(s).strip()) for t, s in conn.execute(
        "SELECT DISTINCT nome_tabella, tipologia_sigla"
        " FROM pyarchinit_thesaurus_sigle")}
    assert sorted(chiesti - presenti) == []
