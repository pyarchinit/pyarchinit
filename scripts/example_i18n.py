# -*- coding: utf-8 -*-
"""Il database di esempio nelle altre nove lingue: copia e traduzione.

«Riempi il db di esempio anche nelle altre lingue» (Enzo, 12 ottobre 2026).
Misurato prima di scrivere: 27 tabelle piene solo per «Scavo archeologico»,
i media solo lì, e nella scheda US decine di colonne vuote nei nove siti
tradotti — 2040 valori di testo distinti in tutto, ma quasi tutti
**modelli** («Ambiente 2», «Scheda US 17, fotopiano e sezione.») e
**vocabolario** («Buona», «Compatta»), non prosa libera.

Il motore è puro e non inventa: una frase si traduce se sta nel
dizionario (`FRASI`) o combacia con un modello (`MODELLI`); quello che non
sa tradurre lo copia com'è e lo **conta** (`Esito.mancate`), così il
dizionario si completa misurando, non sperando. Numeri, date e codici
(`Q1`, `SA-001`, `RA 001`) passano intatti.

I dizionari stanno in `scripts/example_i18n_testi.py`, tabella per tabella.
"""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

SITO_IT = "Scavo archeologico"

#: Il sito di esempio in ogni lingua, e la sua lingua.
LINGUA_DEL_SITO = {
    "Scavo archeologico": "it",
    "Archaeological Excavation": "en",
    "Archäologische Ausgrabung": "de",
    "Fouille Archéologique": "fr",
    "Excavación Arqueológica": "es",
    "Excavació Arqueològica": "ca",
    "Escavação Arqueológica": "pt",
    "Săpătură Arheologică": "ro",
    "Αρχαιολογική Ανασκαφή": "el",
    "تنقيب أثري": "ar",
}

#: Le colonne che non si copiano mai da un sito all'altro.
_MAI = frozenset({"entity_uuid", "node_uuid"})

#: Le colonne che portano nomi propri, codici o indirizzi: si copiano
#: com'è, e non contano come «da tradurre». Un nome di colonna vale per
#: tutte le tabelle; una coppia (tabella, colonna) per quella sola —
#: `nome` è un nome di persona nel personale, ma il nome di un attrezzo
#: nelle attrezzature.
COLONNE_INTATTE = frozenset({
    ("personale_table", "nome"), ("personale_table", "cognome"),
    "nome_cognome", "schedatore", "direttore_us",
    "responsabile_us", "responsabile", "autore", "compilatore", "operatore",
    "email", "telefono", "username", "cod_ente_schedatore", "ente",
    "sigla", "sigla_struttura", "numero_struttura", "codice", "cod",
    "nr_scheda", "nr_campione", "n_inventario", "numero_inventario",
    "filename", "filepath", "path_resize", "doc_usv", "tags",
})


def colonna_intatta(tabella, colonna) -> bool:
    return colonna in COLONNE_INTATTE or (tabella, colonna) in COLONNE_INTATTE

#: Le colonne della scheda US che non si riempiono dall'italiano: chiavi,
#: cronologia (la datazione è già tradotta in ogni sito e deve combaciare
#: con la sua fase), rapporti, e i campi della concorrenza.
_US_INTOCCABILI = frozenset({
    "id_us", "sito", "area", "us", "unita_tipo", "entity_uuid", "node_uuid",
    "datazione", "periodo_iniziale", "fase_iniziale", "periodo_finale",
    "fase_finale", "rapporti", "rapporti2", "cont_per", "order_layer",
    "editing_by", "editing_since", "last_modified_by",
    "last_modified_timestamp", "audit_trail", "created_by", "updated_by",
})

_RE_DATA = re.compile(r"^\d{4}-\d{2}-\d{2}([ T].*)?$|^\d{2}[-/]\d{2}[-/]\d{4}$")
#: Un codice: gruppi di lettere maiuscole e cifre, con trattini, trattini
#: bassi, spazi o barre — `Q1`, `RA 001`, `CP-01`, `IT-SA-0001`,
#: `DIS_TMA_001`, `4/5/6`. Niente parole: una parola ha anche minuscole.
_RE_CODICE = re.compile(r"^[A-Z]{0,8}([-_ /][A-Z]{1,8})*[-_ /]?\d[\dA-Z\-_./ ]*$")
#: Un nome di file, una scala, un orientamento, o niente lettere affatto.
_RE_FILE = re.compile(r"^[\w\-./]+\.(tif|tiff|jpg|jpeg|png|pdf|xlsx|xls|graphml|dxf|svg|json|csv|txt|shp|qgs|qgz|gpkg)$", re.I)
_RE_SCALA = re.compile(r"^\d+\s*:\s*\d+$")
_RE_ORIENTAMENTO = re.compile(r"^[NSEWO]{1,2}-[NSEWO]{1,2}$")
_RE_LETTERE = re.compile(r"[A-Za-zÀ-ÿĀ-žΑ-ωά-ώء-ي]")
#: Una misura: numeri (anche con la virgola) e un'unità — `34 cm`,
#: `1,5 - 2,5 cm`, `4,2 x 1,1 m`.
_RE_MISURA = re.compile(r"^[\d.,]+(\s*[-x×]\s*[\d.,]+)*\s*(cm|m|mm|km|g|kg|l|ml|%)$")
#: Un numero romano o una lettera sola: una sigla, non una parola.
_RE_SIGLA = re.compile(r"^(M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))$|^[A-Z]{1,5}$|^[a-z]{1,2}$")


def lingua_del_sito(sito) -> Optional[str]:
    return LINGUA_DEL_SITO.get(str(sito or "").strip())


def e_testo(valore) -> bool:
    """Un valore da tradurre: una stringa non vuota che non sia un numero,
    una data o un codice."""
    if valore is None or isinstance(valore, (bytes, bytearray, memoryview)):
        return False                    # una geometria non si traduce
    s = str(valore).strip()
    if not s:
        return False
    try:
        float(s.replace(",", "."))
        return False
    except ValueError:
        pass
    if _RE_DATA.match(s) or _RE_CODICE.match(s) or _RE_MISURA.match(s) \
            or (_RE_SIGLA.match(s) and s) or _RE_FILE.match(s) \
            or _RE_SCALA.match(s) or _RE_ORIENTAMENTO.match(s) \
            or not _RE_LETTERE.search(s):
        return False
    return True


def _modelli_compilati(modelli):
    out = []
    for voce in modelli or ():
        rx, per_lingua = voce
        out.append((re.compile(rx) if isinstance(rx, str) else rx, per_lingua))
    return out


def traduci(valore, lingua, frasi=None, modelli=None,
            invarianti=None) -> Tuple[object, bool]:
    """Il valore nella lingua, e se la traduzione c'era.

    Quello che non è testo passa intatto e conta come trovato; l'italiano
    resta italiano; un invariante (nomi di persona e di luogo) resta
    com'è e conta come trovato; una frase o un modello noti si traducono;
    il resto torna com'è, e **non** trovato."""
    if not e_testo(valore) or lingua in (None, "", "it"):
        return valore, True
    if frasi is None or modelli is None or invarianti is None:
        from scripts.example_i18n_testi import (
            FRASI as _F, INVARIANTI as _I, MODELLI as _M)
        frasi = _F if frasi is None else frasi
        modelli = _M if modelli is None else modelli
        invarianti = _I if invarianti is None else invarianti
    s = str(valore).strip()
    if s in invarianti:
        return valore, True
    voce = frasi.get(s)
    if voce and voce.get(lingua):
        return voce[lingua], True
    for rx, per_lingua in _modelli_compilati(modelli):
        m = rx.fullmatch(s)
        if m and per_lingua.get(lingua):
            return per_lingua[lingua].format(*m.groups()), True
    return valore, False


@dataclass
class Esito:
    righe: int = 0
    mancate: set = field(default_factory=set)
    #: Chiave vecchia → chiave nuova delle righe copiate: serve a chi
    #: punta a questa tabella per id (le presenze alle persone).
    mappa_pk: dict = field(default_factory=dict)


def _nuovo_uuid() -> str:
    try:
        from s3dgraphy.sync.uuid7 import uuid7
        return str(uuid7())
    except Exception:                               # noqa: BLE001
        return str(uuid.uuid4())


def _colonne(conn, tabella):
    return [(r[1], (r[2] or "").upper(), bool(r[5]))
            for r in conn.execute('PRAGMA table_info("%s")' % tabella)]


def _colonna_sito(colonne, preferita="sito"):
    nomi = [c[0] for c in colonne]
    for candidata in (preferita, "sito", "sito_q", "scavo_s"):
        if candidata in nomi:
            return candidata
    raise ValueError("nessuna colonna del sito")


def copia_tabella(conn, tabella, sito_it, sito_dest, lingua,
                  frasi=None, modelli=None, colsito="sito",
                  rimappa=None, frasi_colonna=None) -> Esito:
    """Copia le righe di `sito_it` per `sito_dest`, traducendo il testo.

    Chiavi nuove, uuid nuovi, numeri e date com'erano. Se il sito di
    destinazione ha già righe in questa tabella non scrive niente: si può
    rilanciare senza paura. `rimappa` = {colonna: {vecchio: nuovo}} per le
    colonne che puntano a un'altra tabella copiata prima (le presenze alle
    persone); un valore che non è nella mappa resta com'è."""
    colonne = _colonne(conn, tabella)
    col_sito = _colonna_sito(colonne, colsito)
    nomi = [c[0] for c in colonne]
    pk = [c[0] for c in colonne if c[2]]
    pk = pk[0] if len(pk) == 1 else None
    esito = Esito()
    gia = conn.execute('SELECT count(*) FROM "%s" WHERE "%s" = ?'
                       % (tabella, col_sito), (sito_dest,)).fetchone()[0]
    if gia:
        return esito
    righe = conn.execute('SELECT * FROM "%s" WHERE "%s" = ?'
                         % (tabella, col_sito), (sito_it,)).fetchall()
    prossimo = None
    if pk:
        massimo = conn.execute('SELECT max("%s") FROM "%s"' % (pk, tabella)).fetchone()[0]
        try:
            prossimo = int(massimo or 0) + 1
        except (TypeError, ValueError):
            prossimo = None
    rimappa = rimappa or {}
    if frasi_colonna is None:
        try:
            from scripts.example_i18n_testi import FRASI_COLONNA as frasi_colonna
        except ImportError:
            frasi_colonna = {}
    for riga in righe:
        nuova = {}
        for (nome, _tipo, _e_pk), valore in zip(colonne, riga):
            if nome == col_sito:
                nuova[nome] = sito_dest
            elif nome == pk and prossimo is not None:
                nuova[nome] = prossimo
                esito.mappa_pk[valore] = prossimo
                prossimo += 1
            elif nome in rimappa:
                nuova[nome] = rimappa[nome].get(valore, valore)
            elif nome in _MAI:
                nuova[nome] = _nuovo_uuid() if valore else valore
            elif colonna_intatta(tabella, nome):
                nuova[nome] = valore
            else:
                # Prima la voce **per colonna**, se il dizionario ne ha una:
                # la stessa parola vuol dire due cose in due tabelle.
                speciale = (frasi_colonna.get((tabella, nome)) or {}).get(
                    str(valore).strip() if isinstance(valore, str) else None)
                if speciale and speciale.get(lingua):
                    nuova[nome] = speciale[lingua]
                    continue
                tradotto, trovato = traduci(valore, lingua, frasi, modelli)
                if not trovato:
                    esito.mancate.add(str(valore).strip())
                nuova[nome] = tradotto
        campi = [n for n in nomi if not (n == pk and prossimo is None)]
        conn.execute('INSERT INTO "%s" (%s) VALUES (%s)'
                     % (tabella, ", ".join('"%s"' % n for n in campi),
                        ", ".join("?" for _ in campi)),
                     [nuova[n] for n in campi])
        esito.righe += 1
    return esito


def _vuoto(v) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())


def famiglia_tipo(unita_tipo) -> str:
    """`US` per ogni sigla dell'unità stratigrafica (SU, SE, UE, ΣΜ…),
    `USM` per ogni sigla della muratura (WSU, MSE, UEM, USZ, ΤΣΜ), il
    tipo com'è per tutto il resto. La sigla è tradotta per sito, e la
    riga italiana si ritrova solo per famiglia."""
    sigla = str(unita_tipo or "").strip()
    try:
        from modules.utility.pyarchinit_i18n_stratigraphic import (
            ALL_US_ABBREVS, ALL_USM_ABBREVS)
    except Exception:                               # noqa: BLE001
        ALL_US_ABBREVS, ALL_USM_ABBREVS = {"US"}, {"USM"}
    if sigla in ALL_USM_ABBREVS:
        return "USM"
    if sigla in ALL_US_ABBREVS:
        return "US"
    return sigla


def riempi_us(conn, sito_it, sito_dest, lingua, frasi=None, modelli=None) -> Esito:
    """Riempie le colonne **vuote** delle US di `sito_dest` con i valori
    della US italiana con lo stesso codice e tipo, tradotti.

    Non tocca chiavi, cronologia, rapporti e i campi della concorrenza;
    quello che il sito tradotto ha già scritto resta suo. `righe` conta i
    valori scritti."""
    colonne = [c[0] for c in _colonne(conn, "us_table")]
    da_riempire = [c for c in colonne if c not in _US_INTOCCABILI]
    esito = Esito()
    italiane = {}
    for riga in conn.execute('SELECT * FROM us_table WHERE sito = ?', (sito_it,)):
        d = dict(zip(colonne, riga))
        italiane[(str(d.get("us")).strip(), famiglia_tipo(d.get("unita_tipo")))] = d
    for riga in conn.execute('SELECT * FROM us_table WHERE sito = ?', (sito_dest,)).fetchall():
        d = dict(zip(colonne, riga))
        chiave = (str(d.get("us")).strip(), famiglia_tipo(d.get("unita_tipo")))
        it = italiane.get(chiave)
        if it is None:
            continue
        aggiornamenti = {}
        for c in da_riempire:
            if _vuoto(d.get(c)) and not _vuoto(it.get(c)):
                if colonna_intatta("us_table", c):
                    aggiornamenti[c] = it[c]
                    continue
                tradotto, trovato = traduci(it[c], lingua, frasi, modelli)
                if not trovato:
                    esito.mancate.add(str(it[c]).strip())
                aggiornamenti[c] = tradotto
        if aggiornamenti:
            conn.execute('UPDATE us_table SET %s WHERE id_us = ?'
                         % ", ".join('"%s" = ?' % c for c in aggiornamenti),
                         list(aggiornamenti.values()) + [d["id_us"]])
            esito.righe += len(aggiornamenti)
    return esito
