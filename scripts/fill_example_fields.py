#!/usr/bin/env python3
"""Riempie i campi ancora vuoti delle schede del database di esempio.

    /Applications/QGIS.app/Contents/MacOS/bin/python3 \\
        scripts/fill_example_fields.py

`fill_example_db.py` **inserisce** dieci record nelle schede che erano
vuote; questo script **completa** le righe che c'erano già — le cinque
schede preesistenti di «Scavo archeologico»: tombe, individui, ceramica,
reperti, strutture. Due lavori diversi, due script.

Tre cose, in quest'ordine:

1. **I vocabolari**. Il valore di un campo deve essere uno di quelli che
   il menu della scheda mostra, se no la scheda lo fa vedere ma l'utente
   non lo ritrova scorrendo la tendina. Quindi i valori **si leggono dal
   thesaurus**, non si scrivono qui. La ceramica è un caso a parte: le
   sue sedici tendine vengono da `sql/pottery_thesaurus_sqlite.sql`, che
   il plugin installa al primo avvio e che nel file spedito non era mai
   stato caricato — 259 voci, tutte in inglese come la scheda.

2. **Lo schema**. `struttura_table` nel file spedito ha 25 colonne e il
   mapper (`modules/db/structures/Struttura_table.py`) ne dichiara 36: le
   diciassette della scheda AR — stato di conservazione, prospetti,
   elementi costitutivi, manufatti, fasi funzionali — non c'erano, e un
   campo che non esiste non si riempie. Lo stesso per le tre colonne della
   decorazione della ceramica. Le aggiunge `sqlite_db_updater.py` al primo
   avvio: qui si fa la stessa cosa, con gli stessi nomi e gli stessi tipi,
   così il file spedito è già a posto.

3. **I riferimenti**. «Materiali e strutture nella scheda US si
   riferiscono alle schede strutture e materiali» (Enzo): un campo che
   nomina un'altra scheda deve nominarne una che esiste. Due cose erano
   rotte: `rapporti_struttura` citava un **altro sito** («Via Ortaggi…
   Rimini») e una struttura `ED 3` che qui non c'è, e `us_table.struttura`
   portava `ED01` mentre la tendina della scheda US offre `ED-1`
   (`US_USM.format_struttura_item`), cioè il valore salvato non era nella
   lista da cui lo si sarebbe scelto.

**Quello che resta vuoto, e perché.** `editing_by` e `editing_since` sono
il **lucchetto** del record: `modules/db/concurrency_manager.py` legge
`editing_by IS NOT NULL AND editing_since > CURRENT_TIMESTAMP - INTERVAL
'30 minutes'` e dichiara la scheda «in modifica da un altro utente».
Riempirli vorrebbe dire spedire un database di esempio con le schede
bloccate. `audit_trail` è il registro delle modifiche: riempirlo vorrebbe
dire raccontare modifiche che nessuno ha fatto. `last_modified_by` e
`last_modified_timestamp` invece si scrivono: dicono soltanto chi ha
toccato la scheda per ultimo.

Idempotente: una colonna che ha già un valore non si riscrive (tranne i
due riferimenti rotti, che è il punto).
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sqlite3
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
DB = RADICE / "resources" / "dbfiles" / "pyarchinit_db.sqlite"
POTTERY_SQL = RADICE / "sql" / "pottery_thesaurus_sqlite.sql"
SITO = "Scavo archeologico"

#: Chi risulta aver toccato per ultime queste schede. Non un nome vero:
#: il database di esempio gira su dieci lingue e migliaia di installazioni.
AUTORE = "demo"
QUANDO = "2021-06-30 18:20:00"

#: Le colonne che `sqlite_db_updater.py` aggiunge al primo avvio e che il
#: file spedito non aveva. Nomi e tipi **suoi**: se qui si scrivessero
#: diversi, l'updater ne aggiungerebbe altre accanto.
COLONNE_TARDIVE = {
    "struttura_table": [
        ("data_compilazione", "TEXT"), ("nome_compilatore", "TEXT"),
        ("stato_conservazione", "TEXT"), ("quota", "REAL"),
        ("relazione_topografica", "TEXT"), ("prospetto_ingresso", "TEXT"),
        ("orientamento_ingresso", "TEXT"), ("articolazione", "TEXT"),
        ("n_ambienti", "INTEGER"), ("orientamento_ambienti", "TEXT"),
        ("sviluppo_planimetrico", "TEXT"), ("elementi_costitutivi", "TEXT"),
        ("motivo_decorativo", "TEXT"),
        ("potenzialita_archeologica", "TEXT"), ("manufatti", "TEXT"),
        ("elementi_datanti", "TEXT"), ("fasi_funzionali", "TEXT"),
    ],
    "pottery_table": [
        ("decoration_type", "TEXT"), ("decoration_motif", "TEXT"),
        ("decoration_position", "TEXT"),
    ],
}


# ---------------------------------------------------------------------------
# Lettura: le colonne che ci sono, i vocabolari che le schede mostrano
# ---------------------------------------------------------------------------

def colonne(conn, tabella) -> list:
    return [r[1] for r in conn.execute('PRAGMA table_info("%s")' % tabella)]


def allinea_schema(conn) -> list:
    """Aggiunge le colonne che il mapper dichiara e il file non ha."""
    fatto = []
    for tabella, elenco in COLONNE_TARDIVE.items():
        presenti = colonne(conn, tabella)
        if not presenti:
            continue
        for nome, tipo in elenco:
            if nome in presenti:
                continue
            conn.execute('ALTER TABLE "%s" ADD COLUMN "%s" %s'
                         % (tabella, nome, tipo))
            fatto.append("%s.%s" % (tabella, nome))
    return fatto


def carica_thesaurus_ceramica(conn) -> int:
    """Carica le voci della ceramica dal file che il plugin usa all'avvio.

    `sqlite_db_updater.update_pottery_thesaurus` legge questo stesso file e
    lo esegue riga per riga: la scheda Pottery chiede
    `nome_tabella = 'Pottery'` e senza queste voci le sue sedici tendine
    sono **vuote**.
    """
    quante = conn.execute(
        "SELECT count(*) FROM pyarchinit_thesaurus_sigle"
        " WHERE nome_tabella = 'Pottery'").fetchone()[0]
    if quante:
        return 0
    testo = POTTERY_SQL.read_text(encoding="utf-8")
    nostre = set(colonne(conn, "pyarchinit_thesaurus_sigle"))
    prossimo = (conn.execute(
        "SELECT COALESCE(MAX(id_thesaurus_sigle), 0)"
        " FROM pyarchinit_thesaurus_sigle").fetchone()[0] or 0) + 1
    scritte = 0
    for pezzo in testo.split(";"):
        pezzo = pezzo.strip()
        if not pezzo or "INSERT" not in pezzo.upper():
            continue
        # Due forme nello stesso file: sei campi, e otto per le tre
        # tendine della decorazione (11.14, 11.15, 11.16), che portano
        # anche `n_tipologia` e `n_sigla`. Leggere solo le prime
        # lasciava la decorazione senza vocabolario: 197 voci su 259.
        intestazione = re.search(r"INTO\s+pyarchinit_thesaurus_sigle\s*\(([^)]*)\)",
                                 pezzo, re.S)
        valori = re.search(r"VALUES\s*\((.*)\)\s*$", pezzo, re.S)
        if not intestazione or not valori:
            continue
        nomi = [c.strip() for c in intestazione.group(1).split(",")]
        campi = next(csv_sql(valori.group(1)))
        if len(nomi) != len(campi):
            continue
        riga = {k: v for k, v in zip(nomi, campi) if k in nostre}
        if not riga:
            continue
        riga["id_thesaurus_sigle"] = prossimo
        conn.execute(
            "INSERT INTO pyarchinit_thesaurus_sigle (%s) VALUES (%s)"
            % (", ".join('"%s"' % c for c in riga),
               ", ".join("?" for _ in riga)), list(riga.values()))
        prossimo += 1
        scritte += 1
    return scritte


def csv_sql(testo):
    """I valori di una VALUES(...) SQL, rispettando gli apici doppiati."""
    pezzi, corrente, dentro = [], [], False
    i = 0
    while i < len(testo):
        c = testo[i]
        if dentro:
            if c == "'":
                if i + 1 < len(testo) and testo[i + 1] == "'":
                    corrente.append("'")
                    i += 2
                    continue
                dentro = False
            else:
                corrente.append(c)
        elif c == "'":
            dentro = True
        elif c == ",":
            pezzi.append("".join(corrente).strip())
            corrente = []
        i += 1
    pezzi.append("".join(corrente).strip())
    yield pezzi


def vocabolario(conn, tabella, sigla, campo="sigla_estesa",
                lingua="IT") -> list:
    """Le voci che la tendina di quel campo mostra, in ordine.

    Si legge dal thesaurus perché è lì che la scheda le prende: un valore
    scritto a mano qui potrebbe non esserci nel menu, e allora l'utente lo
    vede nella scheda e non lo ritrova fra le scelte.

    **Una lingua sola.** Le voci della ceramica esistono in IT, EN e DE, e
    senza filtro si mescolavano: `fabric` in italiano, `specific_shape` in
    inglese, `exdeco` «Ja». La scheda chiede la lingua di QGIS
    (`load_thesaurus(..., lingua=lang)`), quindi qui si prende l'italiano,
    e l'inglese solo dove l'italiano non c'è.
    """
    righe = conn.execute(
        "SELECT %s FROM pyarchinit_thesaurus_sigle"
        " WHERE nome_tabella = ? AND tipologia_sigla = ?"
        " AND upper(coalesce(lingua, ?)) = ?" % campo,
        (tabella, sigla, lingua, lingua.upper())).fetchall()
    if not righe:
        righe = conn.execute(
            "SELECT %s FROM pyarchinit_thesaurus_sigle"
            " WHERE nome_tabella = ? AND tipologia_sigla = ?" % campo,
            (tabella, sigla)).fetchall()
    voci = []
    for (v,) in righe:
        v = "" if v is None else str(v).strip()
        if v and v not in voci:
            voci.append(v)
    return sorted(voci)


def _gira(voci, n, ripiego=""):
    """La n-esima voce, ciclando. Senza vocabolario, il ripiego."""
    if not voci:
        return ripiego
    return voci[n % len(voci)]


def _lista(righe) -> str:
    """Una lista di liste come la scrive la scheda: testo di `repr`."""
    return str([[str(x) for x in riga] for riga in righe])


# ---------------------------------------------------------------------------
# Scrittura
# ---------------------------------------------------------------------------

def aggiorna(conn, tabella, chiave, valori, solo_se_vuoto=True) -> int:
    """Scrive `valori` sulla riga `chiave`; per default non riscrive."""
    nomi = colonne(conn, tabella)
    campi, params = [], []
    riga = conn.execute(
        'SELECT %s FROM "%s" WHERE %s' % (
            ", ".join('"%s"' % c for c in valori if c in nomi),
            tabella, " AND ".join('"%s" = ?' % k for k in chiave)),
        list(chiave.values())).fetchone() if valori else None
    attuali = {}
    if riga is not None:
        for i, c in enumerate([c for c in valori if c in nomi]):
            attuali[c] = riga[i]
    for c, v in valori.items():
        if c not in nomi:
            continue
        if solo_se_vuoto:
            vecchio = attuali.get(c)
            if vecchio is not None and str(vecchio).strip() not in ("", "[[]]", "[]"):
                continue
        campi.append('"%s" = ?' % c)
        params.append(v)
    if not campi:
        return 0
    params.extend(chiave.values())
    conn.execute('UPDATE "%s" SET %s WHERE %s'
                 % (tabella, ", ".join(campi),
                    " AND ".join('"%s" = ?' % k for k in chiave)), params)
    return len(campi)


def tombe(conn) -> int:
    """La tomba: che cosa c'era **fuori**, e chi l'ha toccata per ultima."""
    righe = conn.execute(
        "SELECT nr_scheda_taf, corredo_presenza, tipo_sepoltura"
        " FROM tomba_table WHERE sito = ? ORDER BY nr_scheda_taf",
        (SITO,)).fetchall()
    fuori = [
        "Frammenti di laterizio e di coppo nel riempimento superiore, "
        "sopra le lastre di copertura.",
        "Nessun oggetto all'esterno della fossa.",
        "Due frammenti di ceramica invetriata presso l'angolo sud-est "
        "della fossa, in giacitura secondaria.",
        "Nessun oggetto all'esterno della fossa.",
        "Un frammento di laterizio posto di taglio accanto al cranio, "
        "forse un segnacolo.",
        "Frammenti di malta di calce lungo il margine ovest, pertinenti "
        "alla copertura asportata.",
        "Nessun oggetto all'esterno della fossa.",
        "Ciottoli di medie dimensioni allineati sul margine nord, "
        "probabile delimitazione.",
        "Nessun oggetto all'esterno della fossa.",
        "Frammenti osteologici animali nel riempimento superiore, "
        "non pertinenti alla deposizione.",
    ]
    scritti = 0
    for n, (nr, _corredo, _tipo) in enumerate(righe):
        scritti += aggiorna(conn, "tomba_table",
                            {"sito": SITO, "nr_scheda_taf": nr},
                            {"oggetti_rinvenuti_esterno": fuori[n % len(fuori)],
                             "last_modified_by": AUTORE,
                             "last_modified_timestamp": QUANDO})
    return scritti


def ceramica(conn) -> int:
    """La scheda della ceramica: sedici tendine e i diametri.

    I valori vengono dalle voci `Pottery` del thesaurus (in inglese, come
    la scheda e come il file che le installa); i diametri si calcolano dal
    `diametro_max` che la riga ha già, così orlo ≥ fondo e la percentuale
    conservata sta fra il 10 e il 40 per cento.
    """
    fabric = vocabolario(conn, "Pottery", "11.1")
    percent = vocabolario(conn, "Pottery", "11.2", campo="sigla")
    specific_form = vocabolario(conn, "Pottery", "11.5")
    munsell = vocabolario(conn, "Pottery", "11.7")
    exdeco = vocabolario(conn, "Pottery", "11.9")
    intdeco = vocabolario(conn, "Pottery", "11.10")
    specific_shape = vocabolario(conn, "Pottery", "11.12")
    dec_tipo = vocabolario(conn, "Pottery", "11.14")
    dec_motivo = vocabolario(conn, "Pottery", "11.15")
    dec_pos = vocabolario(conn, "Pottery", "11.16")

    def descrizione_deco(risposta: str, dove: str) -> str:
        """La descrizione dice quello che dice il sì/no accanto.

        Con `exdeco = 'No'` e una descrizione che racconta una
        decorazione dipinta, la scheda si contraddice da sola.
        """
        positive = ("sì", "si", "yes", "ja", "oui", "sim", "da")
        if risposta.strip().lower() in positive:
            return ("Decorazione dipinta in blu di cobalto sulla superficie "
                    "%s, motivo continuo lungo l'orlo." % dove)
        return "Superficie %s invetriata, priva di decorazione." % dove

    righe = conn.execute(
        "SELECT id_rep, id_number, us, diametro_max, qty, form"
        " FROM pottery_table WHERE sito = ? ORDER BY id_number",
        (SITO,)).fetchall()
    scritti = 0
    for n, (id_rep, numero, us, dmax, qty, forma) in enumerate(righe):
        dmax = float(dmax or 0) or 16.0
        orlo = round(dmax, 1)
        fondo = round(dmax * 0.45, 1)
        altezza = round(dmax * 0.62, 1)
        # `percent` viene dalla tendina 11.2, che offre intervalli
        # («25-50»): la percentuale conservata è il punto di mezzo di
        # quell'intervallo, se no la scheda dice due cose diverse.
        scelta = _gira(percent, n, "10-25")
        numeri = [float(x) for x in re.findall(r"\d+", scelta)]
        conservato = (sum(numeri) / len(numeri)) if numeri else 25.0
        scritti += aggiorna(conn, "pottery_table", {"id_rep": id_rep}, {
            # `box` e `bag` sono Integer nel mapper
            # (`Pottery_table.py`): scriverci «B01» passa in SQLite e
            # poi rompe la lettura — «must be real number, not str» —
            # ed è il guasto che la migrazione DB→DB ha trovato.
            "box": n % 3 + 1,
            "bag": int(numero or n + 1),
            "sector": "A" if n % 2 == 0 else "B",
            "photo": "POT_%03d.jpg" % (numero or n + 1),
            "drawing": "POT_%03d.dxf" % (numero or n + 1),
            "fabric": _gira(fabric, n, "Fine ware"),
            "percent": scelta,
            "specific_form": _gira(specific_form, n, "Rim"),
            "specific_shape": _gira(specific_shape, n, "Bowl"),
            "munsell": _gira(munsell, n, "7.5YR 6/4"),
            "exdeco": _gira(exdeco, n, "Yes"),
            "intdeco": _gira(intdeco, n + 1, "No"),
            "descrip_ex_deco": descrizione_deco(
                _gira(exdeco, n, "Sì"), "esterna"),
            "descrip_in_deco": descrizione_deco(
                _gira(intdeco, n + 1, "No"), "interna"),
            "diametro_rim": orlo,
            "diametro_bottom": fondo,
            "diametro_height": altezza,
            "diametro_preserved": round(float(conservato), 1),
            "decoration_type": _gira(dec_tipo, n, "Painted"),
            "decoration_motif": _gira(dec_motivo, n, "Geometric"),
            "decoration_position": _gira(dec_pos, n, "External"),
            "last_modified_by": AUTORE,
            "last_modified_timestamp": QUANDO,
        })
    return scritti


def reperti(conn) -> int:
    """La scheda dei reperti: le tre tabelle dentro, e la cassetta.

    Le tre tabelle (elementi del reperto, misurazioni, tecnologie) sono
    liste di liste, e ogni loro colonna ha la **sua** tendina: 3.4, 3.5,
    3.6, 3.7, 3.8, 3.9, 3.10. I conteggi tornano fra loro: le forme minime
    non superano le massime, e nessuna delle due supera il totale dei
    frammenti.
    """
    elementi = vocabolario(conn, "inventario_materiali_table", "3.4")
    tipo_mis = vocabolario(conn, "inventario_materiali_table", "3.5")
    unita_mis = vocabolario(conn, "inventario_materiali_table", "3.6")
    tecnologia = vocabolario(conn, "inventario_materiali_table", "3.7")
    posizione = vocabolario(conn, "inventario_materiali_table", "3.8")
    tipo_qta = vocabolario(conn, "inventario_materiali_table", "3.9")
    unita_qta = vocabolario(conn, "inventario_materiali_table", "3.10",
                            campo="sigla")

    def misura(unita: str, n: int) -> str:
        """Un valore che ha senso in quell'unità.

        Tre centimetri e mezzo di lunghezza sono un frammento piccolo;
        tre millimetri e mezzo non sono niente. Il numero segue l'unità
        che la tendina ha dato.
        """
        base = 3.5 + n * 0.8
        u = unita.strip().lower()
        if u.startswith("mm") or "millim" in u:
            return "%.0f" % (base * 10)
        if u.startswith("m") and not u.startswith("mm"):
            return "%.3f" % (base / 100.0)
        return "%.1f" % base

    # Quello che si conta in una cassetta sono frammenti: se la tendina
    # offre quella voce si usa quella, non la prima in ordine alfabetico.
    conta = next((x for x in tipo_qta if "frammenti" in x.lower()),
                 _gira(tipo_qta, 0, "Numero di frammenti"))

    def unita_per(tipo: str) -> str:
        """L'unità che va con quel tipo di quantità.

        Contare frammenti in «%» o pesarli in «nr» non vuol dire niente:
        l'unità si scrive guardando che cosa si sta contando.
        """
        t = tipo.lower()
        if "peso" in t:
            voluta = "g"
        elif "percentuale" in t:
            voluta = "%"
        else:
            voluta = "nr"
        return voluta if voluta in unita_qta else _gira(unita_qta, 0, voluta)
    conserva = vocabolario(conn, "tma_materiali_archeologici", "10.1")

    strutture = [
        "%s-%s" % (s, n) for s, n in conn.execute(
            "SELECT sigla_struttura, numero_struttura FROM struttura_table"
            " WHERE sito = ? ORDER BY sigla_struttura, numero_struttura",
            (SITO,))]

    righe = conn.execute(
        "SELECT id_invmat, numero_inventario, tipo_reperto, us"
        " FROM inventario_materiali_table WHERE sito = ?"
        " ORDER BY numero_inventario", (SITO,)).fetchall()
    scritti = 0
    for n, (id_invmat, numero, tipo_reperto, us) in enumerate(righe):
        ceramico = str(tipo_reperto or "").strip().lower() == "ceramica"
        totale = 3 + n
        minime = 1 + n % 2
        massime = minime + 1
        peso = 20.0 + n * 11.5
        valori = {
            "nr_cassa": "C%02d" % (n % 3 + 1),
            "luogo_conservazione": _gira(conserva, n, "Deposito di scavo"),
            "tipo_contenitore": "Cassetta in plastica",
            "elementi_reperto": _lista([
                [_gira(elementi, n, "Orlo"),
                 conta, str(totale)]]),
            "misurazioni": _lista([
                [_gira(tipo_mis, n, "Lunghezza"),
                 _gira(unita_mis, n, "cm"),
                 misura(_gira(unita_mis, n, "cm"), n)]]),
            "tecnologie": _lista([
                [_gira(tecnologia, n, "Invetriatura"),
                 _gira(posizione, n, "Superficie esterna"),
                 conta, unita_per(conta), str(totale)]]),
            "rif_biblio": "AA.VV., «Lo scavo archeologico: i materiali», "
                          "Firenze 2021, scheda %d." % (numero or n + 1),
            "forme_minime": minime,
            "forme_massime": massime,
            "totale_frammenti": totale,
            "tipo": str(tipo_reperto or "").strip() or "Non determinato",
            # `peso` è Numeric(9,3): i grammi sono il numero, non il
            # testo «31.5 g».
            "peso": round(peso, 1),
            "weight": round(peso, 1),
            "n_reperto": int(numero or n + 1),
            "sub_inv": "%d.%d" % (numero or n + 1, 1),
            "struttura": _gira(strutture, n, ""),
            "punto_rinv": "Settore %s, quadrato %d, US %s"
                          % ("A" if n % 2 == 0 else "B", n % 4 + 1, us),
            "negativo_photo": "NEG_%03d" % (numero or n + 1),
            "diapositiva": "DIA_%03d" % (numero or n + 1),
            "photo_id": "FOTO_%03d" % (numero or n + 1),
            "drawing_id": "DIS_%03d" % (numero or n + 1),
            "quota_usm": round(52.40 - n * 0.07, 2),
            "unita_misura_quota": "m s.l.m.",
            "last_modified_by": AUTORE,
            "last_modified_timestamp": QUANDO,
        }
        # Il corpo ceramico, il rivestimento, il diametro dell'orlo e
        # l'EVE descrivono un vaso: su una moneta o su un chiodo non
        # vogliono dire niente, e scriverli sarebbe un dato finto.
        if ceramico:
            valori.update({
                "corpo_ceramico": "Depurato, di colore beige rosato, "
                                  "con rari inclusi di quarzo.",
                "rivestimento": "Invetriatura incolore su entrambe le "
                                "superfici.",
                "diametro_orlo": round(14.0 + n * 1.5, 1),
                "eve_orlo": round(0.10 + (n % 4) * 0.05, 2),
            })
        scritti += aggiorna(conn, "inventario_materiali_table",
                            {"id_invmat": id_invmat}, valori)
    return scritti


def strutture(conn) -> int:
    """La scheda AR della struttura: le diciassette colonne nuove.

    Le cinque tabelle dentro la scheda sono liste di liste, e le loro
    colonne hanno le tendine 6.9 (elementi architettonici), 6.10 (fattori
    agenti), 6.11 (prospetti), 6.12 (elementi costitutivi), 6.13
    (manufatti), 6.14 (fasi funzionali); le colonne «Ubicazione»,
    «Stato» e «Grado» hanno invece una lista fissa dentro
    `tabs/Struttura.py`, e si usa quella.
    """
    el_arch = vocabolario(conn, "struttura_table", "6.9")
    tipo_mis = vocabolario(conn, "struttura_table", "6.7")
    unita_mis = vocabolario(conn, "struttura_table", "6.8")
    fattori = vocabolario(conn, "struttura_table", "6.10")
    prospetti = vocabolario(conn, "struttura_table", "6.11")
    costitutivi = vocabolario(conn, "struttura_table", "6.12")
    manufatti_v = vocabolario(conn, "struttura_table", "6.13")
    fasi_v = vocabolario(conn, "struttura_table", "6.14")
    sviluppo = vocabolario(conn, "struttura_table", "6.15")

    # Liste fisse della scheda, non del thesaurus: `Struttura.py`.
    ubicazione = ["ESTERNO", "INTERNO"]
    stato = ["CONSERVAZIONE", "VISIBILITA'", "ACCESSIBILITA'"]
    grado = ["OTTIMO", "BUONO", "DISCRETO", "SCARSO", "PESSIMO"]
    potenzialita = ["MEDIA", "ALTA", "BASSA", "NULLA"]
    orientamenti = ["Nord-Sud", "Est-Ovest", "Nord-est/Sud-ovest",
                    "Nord-ovest/Sud-est"]

    fasi_db = [str(p) + "/" + str(f) for p, f in conn.execute(
        "SELECT periodo, fase FROM periodizzazione_table WHERE sito = ?"
        " ORDER BY periodo, fase", (SITO,))]

    righe = conn.execute(
        "SELECT id_struttura, sigla_struttura, numero_struttura,"
        " categoria_struttura, periodo_iniziale, fase_iniziale"
        " FROM struttura_table WHERE sito = ?"
        " ORDER BY sigla_struttura, numero_struttura", (SITO,)).fetchall()
    scritti = 0
    for n, (id_str, sigla, numero, categoria, periodo, fase) in enumerate(righe):
        # La fase funzionale di un ambiente sta nella periodizzazione
        # **della struttura**, non in una qualsiasi: ED 1 è del periodo
        # 2, e scriverle «1/1» voleva dire mandarla in un'altra epoca.
        sua_fase = ("%s/%s" % (periodo, fase)) if periodo else _gira(
            fasi_db, n, "2/1")
        if sua_fase not in fasi_db and fasi_db:
            sua_fase = _gira(fasi_db, n, "2/1")
        scritti += aggiorna(conn, "struttura_table", {"id_struttura": id_str}, {
            "data_compilazione": "2021-05-%02d" % (10 + n),
            "nome_compilatore": "Schedatore",
            "quota": round(52.80 - n * 0.15, 2),
            "relazione_topografica": "La struttura si trova nel settore %s "
                                     "del saggio, a %d m dal limite nord."
                                     % ("A" if n % 2 == 0 else "B", n + 2),
            "orientamento_ingresso": _gira(orientamenti, n, "Nord-Sud"),
            "articolazione": "A un solo ambiente" if n % 2
                             else "A due ambienti comunicanti",
            "n_ambienti": 1 + n % 3,
            "orientamento_ambienti": _lista(
                [[_gira(orientamenti, n, "Nord-Sud")]]),
            "sviluppo_planimetrico": _gira(sviluppo, n, "Rettangolare"),
            "motivo_decorativo": "Nessun motivo decorativo conservato.",
            "potenzialita_archeologica": _gira(potenzialita, n, "MEDIA"),
            "elementi_datanti": "Frammenti di maiolica arcaica dal "
                                "riempimento, XV secolo.",
            "misure_struttura": _lista([
                [_gira(ubicazione, n, "ESTERNO"),
                 _gira(el_arch, n, "Muro"),
                 _gira(tipo_mis, n, "Lunghezza"),
                 _gira(unita_mis, n, "m"), "%.2f" % (1.20 + n * 0.35)]]),
            "stato_conservazione": _lista([
                [_gira(stato, 0, "CONSERVAZIONE"), _gira(grado, n, "BUONO"),
                 _gira(fattori, n, "Dilavamento")]]),
            "prospetto_ingresso": _lista([[_gira(prospetti, n, "Sud")]]),
            "elementi_costitutivi": _lista([[_gira(costitutivi, n,
                                                   "Laterizio")]]),
            "manufatti": _lista([[_gira(manufatti_v, n, "Focolare")]]),
            "fasi_funzionali": _lista([
                ["Ambiente %d" % (n % 3 + 1),
                 sua_fase, _gira(fasi_v, n, "Uso")]]),
            "last_modified_by": AUTORE,
            "last_modified_timestamp": QUANDO,
        })
    return scritti


# ---------------------------------------------------------------------------
# I riferimenti fra schede
# ---------------------------------------------------------------------------

#: I rapporti che la scheda Struttura offre, e il loro inverso. La lista
#: è quella di `tabs/Struttura.py` (`valuesRapporti`): «Si appoggia a» e
#: «Gli si appoggia» dalla tabella centrale dell'i18n, più i cinque di
#: `_STRUTTURA_EXTRA` e «Si lega a». Il database di esempio usava anche
#: «Fa parte di» e «Taglia», che in quel menu **non ci sono**: un valore
#: che la tendina non offre l'utente non lo ritrova.
INVERSO_STRUTTURA = {
    "Si appoggia a": "Gli si appoggia",
    "Gli si appoggia": "Si appoggia a",
    "Si sovrappone a": "Gli si sovrappone",
    "Gli si sovrappone": "Si sovrappone a",
    "Ampliato da": "Amplia",
    "Amplia": "Ampliato da",
    "Connesso con": "Connesso con",
    "Si lega a": "Si lega a",
}

#: Quello che il database di esempio aveva e il menu non offre, portato
#: sul termine più vicino fra quelli offerti.
FUORI_MENU = {
    "Fa parte di": "Connesso con",
    "Taglia": "Si sovrappone a",
    "Tagliato da": "Gli si sovrappone",
}


def ripara_rapporti_struttura(conn) -> int:
    """I rapporti fra strutture: termini del menu, bersagli veri, reciproci.

    Tre cose, nel file spedito:

    * `ED 1` citava un **altro sito** («Via Ortaggi… Rimini») e una
      `ED 3` che qui non esiste: una voce che non punta a niente non
      serve a fare prove;
    * «Fa parte di» e «Taglia» non sono fra i rapporti che la scheda
      offre (`valuesRapporti` in `tabs/Struttura.py`);
    * i rapporti erano dichiarati **da un lato solo**: `ED 2` diceva
      «Gli si appoggia ED 1» e `ED 1` non rispondeva niente.

    Ritorna quante schede sono state riscritte.
    """
    vere = {}
    for id_str, sigla, numero in conn.execute(
            "SELECT id_struttura, sigla_struttura, numero_struttura"
            " FROM struttura_table WHERE sito = ?", (SITO,)):
        vere[(str(sigla), str(numero))] = id_str

    # Primo giro: si tiene quello che punta a una struttura vera, col
    # termine che il menu offre.
    dichiarati = {}
    for chiave, id_str in vere.items():
        testo = conn.execute(
            "SELECT rapporti_struttura FROM struttura_table"
            " WHERE id_struttura = ?", (id_str,)).fetchone()[0]
        try:
            voci = ast.literal_eval(testo) if testo else []
        except Exception:
            voci = []
        tenute = []
        for voce in voci:
            if not isinstance(voce, (list, tuple)) or len(voce) < 4:
                continue
            tipo, _sito_voce, sigla, numero = [str(x).strip()
                                               for x in voce[:4]]
            tipo = FUORI_MENU.get(tipo, tipo)
            if tipo not in INVERSO_STRUTTURA:
                continue
            bersaglio = (sigla, numero)
            if bersaglio not in vere or bersaglio == chiave:
                continue
            tenute.append([tipo, SITO, sigla, numero])
        dichiarati[chiave] = tenute

    # Secondo giro: il reciproco di ogni dichiarazione, dall'altro lato.
    for chiave, tenute in list(dichiarati.items()):
        for tipo, _sito_voce, sigla, numero in tenute:
            altra = (sigla, numero)
            inverso = INVERSO_STRUTTURA[tipo]
            riga = dichiarati.setdefault(altra, [])
            if not any(v[0] == inverso and (v[2], v[3]) == chiave
                       for v in riga):
                riga.append([inverso, SITO, chiave[0], chiave[1]])

    # `ED 1` resterebbe senza niente: le sue due voci erano l'una verso
    # un altro sito e l'altra verso una struttura inesistente. Il
    # reciproco delle cinque strutture che la nominano gliene dà cinque.
    cambiate = 0
    for chiave, id_str in vere.items():
        prima = conn.execute(
            "SELECT rapporti_struttura FROM struttura_table"
            " WHERE id_struttura = ?", (id_str,)).fetchone()[0]
        dopo = str(dichiarati.get(chiave, []))
        if dopo != (prima or ""):
            conn.execute("UPDATE struttura_table SET rapporti_struttura = ?"
                         " WHERE id_struttura = ?", (dopo, id_str))
            cambiate += 1
    return cambiate


def ripara_us_struttura(conn) -> int:
    """`us_table.struttura` deve contenere quello che la tendina offre.

    La scheda US riempie `comboBox_struttura` con
    `f"{sigla_struttura}-{numero_struttura}"` (`format_struttura_item`),
    cioè «ED-1»; il file spedito aveva «ED01» e «ED01/FC01», che in quella
    lista non ci sono: il valore salvato non era scegliibile.
    """
    vere = {}
    for s, n in conn.execute(
            "SELECT sigla_struttura, numero_struttura FROM struttura_table"
            " WHERE sito = ?", (SITO,)):
        vere["%s%02d" % (s, n)] = "%s-%s" % (s, n)
        vere["%s-%s" % (s, n)] = "%s-%s" % (s, n)
    cambiate = 0
    for id_us, valore in conn.execute(
            "SELECT id_us, struttura FROM us_table WHERE sito = ?"
            " AND trim(coalesce(struttura, '')) <> ''", (SITO,)).fetchall():
        pezzi = [p.strip() for p in str(valore).split("/") if p.strip()]
        nuovi = [vere.get(p) for p in pezzi]
        if not all(nuovi):
            continue
        nuovo = "/".join(nuovi)
        if nuovo != valore:
            conn.execute("UPDATE us_table SET struttura = ? WHERE id_us = ?",
                         (nuovo, id_us))
            cambiate += 1
    return cambiate


# ---------------------------------------------------------------------------
# I periodi: il finale non può restare vuoto, e qualcosa deve sopravvivere
# ---------------------------------------------------------------------------

# Perché qui **non** si inventa nessuna continuità. Il generatore propone
# una scheda CON quando `periodo_iniziale != periodo_finale` — un «salto di
# periodo», così dice la specifica concordata
# (`docs/superpowers/specs/2026-06-09-genera-continuita-con-design.md`).
# Nella stratigrafia del database di esempio non c'è spazio per una:
# misurate le cinque strutture in muratura (US 5, 6, 12, 19, 36), **ognuna
# è coperta da unità del suo stesso periodo**, quindi allungarne la vita
# al periodo dopo produce una contraddizione invece di una continuità —
# provato, e la verifica l'ha segnalata (US 5 «risulta interamente più
# antica di US 29 pur essendone stratigraficamente più recente»).
#
# Resta aperta una domanda che non è mia: la US 12 va da 2/3 a 2/4 — dura
# da una **fase** all'altra dentro lo stesso periodo — e il database di
# esempio ha già la sua scheda CON scritta a mano (US 500, «Continuity»,
# rapporto `>` verso la 12). Sotto la regola della specifica quella non è
# una candidata, quindi il generatore non la rifarebbe. Se la continuità
# deve valere anche fra fasi, è una riga sola in `scan_candidates` — ma è
# un cambio di specifica, e lo decide chi l'ha scritta.


def periodi(conn) -> tuple:
    """Chiude i periodi aperti e apre quelli che devono durare.

    Nel file spedito il **periodo finale** era vuoto su 49 US su 51 (490
    righe sui dieci siti): una scheda US ne ha due, e la verifica della
    cronologia legge entrambi. Chi non sopravvive finisce dove comincia,
    ed è il caso normale — e quando il finale manca la verifica non dice
    «va bene», dice «non posso valutare»: cinque avvisi
    «manca la datazione di periodo» che adesso non ci sono più.

    Si fa su **tutti** i siti: i dieci demo tradotti hanno gli stessi
    numeri di US e la stessa periodizzazione, e un difetto lasciato su
    nove di essi tornerebbe come segnalazione.
    """
    chiuse = conn.execute(
        "UPDATE us_table SET periodo_finale = periodo_iniziale,"
        " fase_finale = fase_iniziale"
        " WHERE trim(coalesce(periodo_iniziale, '')) <> ''"
        "   AND trim(coalesce(periodo_finale, '')) = ''").rowcount
    return chiuse, 0


# ---------------------------------------------------------------------------

def vuote(conn, tabella) -> list:
    """Le colonne di quella scheda che sono vuote in **tutte** le righe."""
    fuori = []
    for col in colonne(conn, tabella):
        try:
            n = conn.execute(
                'SELECT count(*) FROM "%s" WHERE sito = ? AND "%s" IS NOT NULL'
                ' AND trim(cast("%s" AS TEXT)) NOT IN (?, ?, ?)'
                % (tabella, col, col), (SITO, "", "[[]]", "[]")).fetchone()[0]
        except sqlite3.OperationalError:
            continue
        if n == 0:
            fuori.append(col)
    return fuori


SCHEDE = (("tomba_table", tombe), ("pottery_table", ceramica),
          ("inventario_materiali_table", reperti),
          ("struttura_table", strutture))


def main(argv=None) -> int:
    global SITO
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sito", default=SITO)
    ap.add_argument("--db", default=str(DB))
    args = ap.parse_args(argv)
    SITO = args.sito
    percorso = Path(args.db)
    if not percorso.is_file():
        raise SystemExit("manca %s" % percorso)

    conn = sqlite3.connect(percorso)
    try:
        print("=== %s ===" % SITO)
        nuove = allinea_schema(conn)
        print("  schema: +%d colonne%s"
              % (len(nuove), (" (%s)" % ", ".join(nuove)) if nuove else ""))
        voci_ceramica = carica_thesaurus_ceramica(conn)
        print("  thesaurus ceramica: +%d voci" % voci_ceramica)

        for tabella, riempi in SCHEDE:
            prima = vuote(conn, tabella)
            scritti = riempi(conn)
            dopo = vuote(conn, tabella)
            print("  %-28s %3d valori · colonne vuote %d -> %d"
                  % (tabella, scritti, len(prima), len(dopo)))
            if dopo:
                print("      restano: %s" % ", ".join(dopo))

        chiuse, _ = periodi(conn)
        print("  periodi: %d finali chiusi (nessuna continuità "
              "inventata: la stratigrafia non lo consente)" % chiuse)
        print("  rapporti fra strutture riparati: %d"
              % ripara_rapporti_struttura(conn))
        print("  us_table.struttura normalizzate: %d"
              % ripara_us_struttura(conn))
        conn.commit()
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
