"""Un database di prova che somiglia a uno scavo vero, costruito da codice.

Perché esiste: tutto quello che è uscito il 9 e il 10 ottobre 2026 era stato
verificato su `resources/dbfiles/pyarchinit_db.sqlite`, che ha **un'area sola
su ogni riga**, nessun numero di US ripetuto e nessuna cronologia rovesciata.
Quindi l'identità di riga a quattro colonne, la lettura dei reciproci su più
aree, gli anni a.C. battuti senza il segno meno e il percorso «questo sito non
ha record» non avevano nessuna copertura su dati realistici.

Perché un generatore e non un `.sqlite` committato: un binario è opaco e
marcisce quando lo schema cambia; un generatore dice **a che cosa serve ogni
riga**, si rivede in una diff e si ricostruisce in un `tmp_path`. Non apre mai
il database vivo dell'utente e non copia quello di esempio.

Le colonne sono solo quelle che le verifiche leggono (`us_table`,
`periodizzazione_table`, `site_table`), con i nomi dello schema in
`modules/db/structures/`. Il vincolo `UNIQUE(sito, area, us, unita_tipo)` di
`US_table.py` c'è: è lui a dire che la US 1 dell'area 1 e quella dell'area 2
sono due schede.

Ogni riga di `us_table` porta un `node_uuid` suo. Senza, il projector fonde due
righe con lo stesso numero di US in un nodo solo (51 nodi per 52 righe) e il
comportamento a più aree non si raggiunge più.

Uso::

    from realistic_site_db import build_realistic_site_db, SITO, SITO_VUOTO
    url = build_realistic_site_db(tmp_path)      # "sqlite:///.../db.sqlite"
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

#: Lo scavo a due aree, con tutti i casi.
SITO = "Scavo a due aree"
#: Un sito che esiste in `site_table` e ha una periodizzazione, ma **nessuna**
#: riga in `us_table` (caso 7).
SITO_VUOTO = "Sito senza schede"

_SCHEMA = """
CREATE TABLE site_table (
    id_sito INTEGER PRIMARY KEY,
    sito TEXT, nazione TEXT, regione TEXT, comune TEXT, provincia TEXT,
    descrizione TEXT, entity_uuid TEXT
);
CREATE TABLE periodizzazione_table (
    id_perfas INTEGER PRIMARY KEY,
    sito TEXT, periodo INTEGER, fase TEXT,
    cron_iniziale INTEGER, cron_finale INTEGER,
    descrizione TEXT, datazione_estesa TEXT, cont_per INTEGER, entity_uuid TEXT
);
CREATE TABLE us_table (
    id_us INTEGER PRIMARY KEY,
    sito TEXT, area TEXT, us TEXT, unita_tipo TEXT,
    d_stratigrafica TEXT, d_interpretativa TEXT,
    periodo_iniziale TEXT, fase_iniziale TEXT,
    periodo_finale TEXT, fase_finale TEXT,
    datazione TEXT, rapporti TEXT, node_uuid TEXT,
    attivita TEXT, struttura TEXT, settore TEXT, ambient TEXT,
    saggio TEXT, quad_par TEXT, documentazione TEXT,
    -- la legge `continuity_generator.load_site_records`: senza, il
    -- generatore di continuità non parte affatto
    other_locations TEXT,
    UNIQUE (sito, area, us, unita_tipo)
);
"""

# ---------------------------------------------------------------------------
# Periodizzazione del sito principale
# ---------------------------------------------------------------------------
# (periodo, fase, cron_iniziale, cron_finale, datazione_estesa, a che serve)
_FASI = [
    # Caso 5: a.C. scritto CORRETTAMENTE, con il segno. Non va segnalato.
    (1, "1", -1650, -1450, "Età del Bronzo medio",
     "coppia negativa giusta: non è un errore"),
    # Caso 5: lo stesso periodo con gli anni battuti SENZA il segno meno.
    # inizio > fine, tutt'e due positivi -> proposta di negazione, manuale.
    (2, "1", 1650, 1450, "Età del Bronzo medio (senza segno)",
     "a.C. senza il meno: ramo della negazione"),
    # Caso 5: rovesciata con un anno GIÀ negativo: negare porterebbe nell'era
    # sbagliata, quindi la lettura buona è lo scambio.
    (3, "1", -100, -300, "II-I secolo a.C.",
     "rovesciata con un anno negativo: ramo dello scambio"),
    # Caso 6: due fasi con intervallo IDENTICO. Qualunque restringimento
    # farebbe finire una fase prima di cominciare: nessuna proposta.
    (4, "1", 1000, 1100, "Prima fase dell'XI secolo",
     "sovrapposizione identica: nessuna proposta"),
    (4, "2", 1000, 1100, "Seconda fase dell'XI secolo",
     "sovrapposizione identica: nessuna proposta"),
    # Caso 6: sovrapposizione PARZIALE (1250-1300). La proposta alza l'inizio
    # della più recente a 1301.
    (5, "1", 1200, 1300, "XIII secolo",
     "sovrapposizione parziale: la più antica"),
    (5, "2", 1250, 1400, "Fine XIII - XIV secolo",
     "sovrapposizione parziale: la più recente, cron_iniziale -> 1301"),
    # Caso 8: due fasi in ordine cronologico, usate al contrario dal paradosso.
    (6, "1", 1500, 1549, "Prima metà del XVI secolo", "paradosso: fase antica"),
    (7, "1", 1600, 1700, "XVII secolo", "paradosso: fase recente"),
    # Caso 4c: una fase con datazione_estesa VUOTA. Una scheda piena che punta
    # qui non va mai svuotata in nome di una fonte che non dice niente.
    (8, "1", 1800, 1900, "", "fonte vuota: la scheda piena non si tocca"),
]

# ---------------------------------------------------------------------------
# Le schede US
# ---------------------------------------------------------------------------
# Il numero e l'area sono dati scritti come testo, come in pyArchInit. I
# rapporti stanno nella forma a quattro elementi [tipo, us, area, sito] salvo
# dove il commento dice che è corta.
def _lungo(tipo, us, area):
    return "['%s', '%s', '%s', '%s']" % (tipo, us, area, SITO)


def _schede():
    """(area, us, periodo, fase, datazione, rapporti, a che serve)."""
    return [
        # --- Casi 1 e 2: la US 1 e la US 9 ci sono in tutte e due le aree ----
        # AREA 1. La US 1 dichiara «Copre 9 area 1»; la US 9 dell'area 1 NON
        # risponde con «Coperto da 1»: questo è il reciproco mancante.
        ("1", "1", 5, "1", "XIII secolo",
         "[%s]" % _lungo("Copre", "9", "1"),
         "caso 2: dichiara «Copre 9»; il reciproco manca sulla US 9 area 1"),
        ("1", "9", 4, "1", "Prima fase dell'XI secolo",
         "[%s]" % _lungo("Copre", "5", "1"),
         "caso 2: qui manca «Coperto da 1»; copre solo la US 5"),
        # AREA 2. Stessi numeri, datazione diversa, rapporti diversi. La US 9
        # dell'area 2 HA «Coperto da 1 area 2»: un controllo che ignora l'area
        # lo scambierebbe per il reciproco dell'area 1 e tacerebbe.
        ("2", "1", 5, "2", "Fine XIII - XIV secolo",
         "[%s]" % _lungo("Copre", "9", "2"),
         "caso 1: stessa US 1, altra area, altra fase e altra datazione"),
        ("2", "9", 4, "2", "Seconda fase dell'XI secolo",
         "[%s]" % _lungo("Coperto da", "1", "2"),
         "caso 1/2: porta il reciproco, ma dell'area 2 (non zittisce l'area 1)"),

        # --- Caso 3: reciproco scritto in forma CORTA ----------------------
        # La US 9 area 1 «Copre 5»; la US 5 risponde con ['Coperto da', '9'],
        # senza area né sito, come 1870 voci su 1870 nel database di esempio.
        ("1", "5", 4, "1", "Prima fase dell'XI secolo",
         "[['Coperto da', '9']]",
         "caso 3: reciproco in forma corta a due elementi"),

        # --- Caso 4: tre datazioni ---------------------------------------
        # a) la scheda dice una cosa, la fase un'altra
        ("1", "20", 4, "1", "XII secolo",
         "[]",
         "caso 4a: datazione in disaccordo con la fase (XI secolo atteso)"),
        # b) scheda vuota, fase piena -> è un disallineamento da riempire
        ("1", "21", 4, "1", "",
         "[]",
         "caso 4b: datazione vuota, la fase ne ha una"),
        # c) fase con datazione_estesa vuota, scheda piena: NON si segnala
        ("1", "22", 8, "1", "Età moderna",
         "[]",
         "caso 4c: fonte vuota, scheda piena: non si deve svuotare"),

        # --- Caso 8: un paradosso temporale -------------------------------
        # La US 30 COPRE la US 31, quindi è più recente. Ma la US 30 sta nella
        # fase 6 (1500-1549) e la 31 nella fase 7 (1600-1700): la più recente
        # finisce prima che la più antica cominci. Inversione.
        ("1", "30", 6, "1", "Prima metà del XVI secolo",
         "[%s]" % _lungo("Copre", "31", "1"),
         "caso 8: copre la 31 ma la sua fase è anteriore"),
        ("1", "31", 7, "1", "XVII secolo",
         "[%s]" % _lungo("Coperto da", "30", "1"),
         "caso 8: coperta dalla 30 ma la sua fase è posteriore"),

        # --- Caso 9: rapporti di uguaglianza ------------------------------
        # «Uguale a» e «Si lega a» non sono una sovrapposizione: le due unità
        # sono la stessa cosa vista in due punti dello scavo. Nella matrice
        # di Harris stanno sulla STESSA riga, accostate, e si collegano con
        # due linee orizzontali — il segno di uguale — senza punta di
        # freccia. Due coppie, una per etichetta, e ciascuna con il suo
        # reciproco scritto: stesso periodo e stessa fase, perché sono la
        # stessa cosa.
        ("1", "40", 4, "1", "Prima fase dell'XI secolo",
         "[%s]" % _lungo("Uguale a", "41", "1"),
         "caso 9: «Uguale a» — stessa riga della 41, nessuna freccia"),
        ("1", "41", 4, "1", "Prima fase dell'XI secolo",
         "[%s]" % _lungo("Uguale a", "40", "1"),
         "caso 9: il reciproco dell'uguaglianza"),
        ("1", "42", 5, "1", "XIII secolo",
         "[%s]" % _lungo("Si lega a", "43", "1"),
         "caso 9: «Si lega a» — simmetrica come «Uguale a»"),
        ("1", "43", 5, "1", "XIII secolo",
         "[%s]" % _lungo("Si lega a", "42", "1"),
         "caso 9: il reciproco del legame"),

        # --- Caso 10: unità che SOPRAVVIVONO fra periodi ------------------
        # Il generatore di continuità fa una scheda CON per ogni unità che
        # ha il periodo iniziale **diverso** dal finale: un muro costruito
        # nel periodo 4 e ancora in piedi nel periodo 6 non è un'unità per
        # periodo, è la stessa cosa che dura. Senza nessuna riga così il
        # generatore non ha niente da generare — e fino al 2026-10-11 né
        # questo database né quello di esempio ne avevano **una**.
        #
        # Si scrivono con la fase: una continuità va da (periodo, fase) a
        # (periodo, fase), e il codice le legge tutte e quattro.
        ("1", "50", 4, "1", "Prima fase dell'XI secolo",
         "[]",
         "caso 10: muro costruito nel periodo 4 e in uso fino al 6",
         6, "1"),
        ("1", "51", 5, "1", "XIII secolo",
         "[]",
         "caso 10: struttura di lunga durata, dal periodo 5 al 7",
         7, "1"),
        ("2", "50", 4, "2", "Seconda fase dell'XI secolo",
         "[]",
         "caso 10: la stessa US 50 nell'area 2, con una durata diversa",
         5, "2"),

        # --- Caso 11: rapporti che ESCONO dall'area ----------------------
        # L'esempio di Enzo, 11 ottobre 2026: «se US 1 in area 1 copre US 9
        # in area 2, il reciproco dovrà scrivere US 9 area 2 "coperto da US
        # 1 area 1"». Fino a qui il database non aveva **nessun** rapporto
        # fra due aree: tutti i casi 1-10 stanno dentro la loro.
        #
        # 60 -> 61: la forma corta ['Copre', '61'] non dice l'area, e la US
        # 61 esiste SOLO nell'area 2. Il bottone «Aggiorna Area/Sito»
        # dev'esserci arrivato: scrivere l'area della scheda (1) nomina una
        # riga che non c'è. E il reciproco va scritto sulla scheda
        # dell'area 2, non su una omonima.
        ("1", "60", 5, "1", "XIII secolo",
         "[['Copre', '61']]",
         "caso 11: forma corta che esce dall'area (la 61 sta solo in area 2)"),
        ("2", "61", 4, "2", "Seconda fase dell'XI secolo",
         "[]",
         "caso 11: qui manca «Coperto da 60 area 1»"),
        # 62 -> 63: l'area è dichiarata, è un'altra, ed è GIUSTA. La US 63
        # esiste in tutte due le aree: è lei che ingannava la vecchia
        # ricerca (`WHERE us = ? AND sito = ?` più la prima riga), che
        # riscriveva area 2 -> area 1 e portava la scheda a parlare
        # dell'unità sbagliata.
        ("1", "62", 5, "1", "XIII secolo",
         "[%s]" % _lungo("Copre", "63", "2"),
         "caso 11: area dichiarata e giusta: non si deve riscrivere"),
        ("2", "63", 4, "2", "Seconda fase dell'XI secolo",
         "[%s]" % _lungo("Coperto da", "62", "1"),
         "caso 11: il reciproco, nell'area 2"),
        ("1", "63", 4, "1", "Prima fase dell'XI secolo",
         "[]",
         "caso 11: la US 63 c'è anche in area 1, e non c'entra niente"),
    ]


def _uuid(n):
    """Un `node_uuid` per riga, distinto. Forma uuid7, valore deterministico."""
    return "019f8043-0000-7000-8000-%012d" % n


def siti():
    """I due siti del generatore, in ordine: quello pieno e quello vuoto."""
    return (SITO, SITO_VUOTO)


def popola(conn) -> None:
    """Inserisce i casi in una connessione **già provvista di schema**.

    Separata da :func:`build_realistic_site_db` perché gli stessi casi
    servono due volte: nello schema minimo dei test unitari, e nello schema
    **completo** del database di prova che si installa accanto a quello di
    esempio (`scripts/build_test_db.py`). Una sola fonte: se qui si aggiunge
    un caso, lo vedono entrambi.

    Scrive solo le colonne che i casi usano; tutte esistono sia nello schema
    minimo qui sotto sia in `us_table` vera.
    """
    for i, sito in enumerate(siti(), start=1):
        conn.execute(
            "INSERT INTO site_table (sito, nazione, regione, comune, provincia,"
            " descrizione, entity_uuid) VALUES (?,?,?,?,?,?,?)",
            (sito, "Italia", "Toscana", "Volterra", "PI", "sito di prova",
             "019f8043-0000-7000-9000-%012d" % i))

    # Caso 7: SITO_VUOTO ha la sua periodizzazione e nessuna scheda US.
    fasi = [(SITO,) + f[:5] for f in _FASI]
    fasi.append((SITO_VUOTO, 1, "1", 100, 200, "II secolo"))
    for n, (sito, periodo, fase, ini, fin, estesa) in enumerate(fasi, start=1):
        conn.execute(
            "INSERT INTO periodizzazione_table (sito, periodo, fase,"
            " cron_iniziale, cron_finale, descrizione, datazione_estesa,"
            " cont_per, entity_uuid) VALUES (?,?,?,?,?,?,?,?,?)",
            (sito, periodo, fase, ini, fin, "", estesa, n,
             "019f8043-0000-7000-a000-%012d" % n))

    for n, riga in enumerate(_schede(), start=1):
        # Le righe del caso 10 portano due valori in più: il periodo e la
        # fase **finali**, diversi da quelli iniziali. Tutte le altre
        # finiscono dove cominciano, com'è normale per una unità che non
        # sopravvive.
        area, us, per, fase, dat, rapporti, _perche = riga[:7]
        per_fin = riga[7] if len(riga) > 7 else per
        fase_fin = riga[8] if len(riga) > 8 else fase
        conn.execute(
            "INSERT INTO us_table (sito, area, us, unita_tipo, d_stratigrafica,"
            " d_interpretativa, periodo_iniziale, fase_iniziale,"
            " periodo_finale, fase_finale, datazione, rapporti, node_uuid,"
            " attivita, struttura, settore, ambient, saggio, quad_par,"
            " documentazione) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (SITO, area, us, "US", "Strato", "Livello", str(per), fase,
             str(per_fin), fase_fin, dat, rapporti, _uuid(n),
             "", "", "", "", "", "", ""))
    conn.commit()


def build_realistic_site_db(folder) -> str:
    """Costruisce il database in `folder` e restituisce l'URL SQLAlchemy.

    `folder` è un `tmp_path`: il file è `folder/db.sqlite`. Mai il database
    vivo dell'utente.
    """
    percorso = Path(folder) / "db.sqlite"
    conn = sqlite3.connect(percorso)
    conn.executescript(_SCHEMA)
    popola(conn)
    conn.close()
    return "sqlite:///%s" % percorso
