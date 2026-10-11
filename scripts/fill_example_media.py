#!/usr/bin/env python3
"""Mette i media nel database di esempio: tre per record, sei schede.

    /Applications/QGIS.app/Contents/MacOS/bin/python3 \\
        scripts/fill_example_media.py

Le schede che gestiscono i media sono sei, e si riconoscono dai tipi che
`tabs/Image_search.ENTITY_TYPE_MAP` elenca: **US**, **CERAMICA**
(Pottery), **REPERTO** (Inventario materiali), **TOMBA**, **STRUTTURA**,
**UT**. Ognuna mostra i media del record aperto cercando
`media_to_entity_table` per `(id_entity, entity_type)`, dove `id_entity`
è la **chiave primaria** del record.

Tre tabelle, e servono tutte tre:

``media_table``
    il media: `mediatype` ('image'), `filename` **senza estensione**,
    `filetype`, `filepath`, più descrizione e tag.
``media_thumb_table``
    i nomi dei due file derivati, **nudi**: `filepath` è
    ``<id>_<filename>_thumb.png`` e `path_resize` è
    ``<id>_<filename>.png``. La scheda li attacca ai percorsi configurati
    (`THUMB_PATH`, `THUMB_RESIZE`) per **concatenazione**.
``media_to_entity_table``
    il legame col record: `id_entity`, `entity_type`, `table_name`,
    `id_media`.

**Le immagini non si scrivono qui.** Le disegna
`modules/utility/example_media.py` al primo avvio, dentro le due
cartelle dei media, coi nomi che queste righe dichiarano: 564 segnaposto
non si spediscono dentro un plugin.

**Il trigger.** `media_entity_delete` scatta **dopo una DELETE** su
`media_thumb_table` e cancella le righe di `media_to_entity_table` con
quell'`id_media`. In inserimento non c'entra, ma è il trigger del
disastro di khutm2: se si rifà il popolamento, si cancella **prima**
`media_to_entity_table` e **poi** `media_thumb_table`, o il trigger porta
via righe che non erano sue.

Idempotente: i media già presenti si riconoscono dal tag `demo` e non si
rifanno.
"""
from __future__ import annotations

import argparse
import sqlite3
import uuid
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
DB = RADICE / "resources" / "dbfiles" / "pyarchinit_db.sqlite"
SITO = "Scavo archeologico"

#: Quanti media per record.
QUANTI = 3

#: Il tag che riconosce i media di esempio, per non rifarli due volte.
TAG = "demo"

#: Le sei schede che gestiscono i media. Per ognuna: il tipo che la
#: scheda scrive in `entity_type`, la tabella, la sua chiave primaria, la
#: colonna del sito (`ut_table` ha `progetto`, non `sito`) e la colonna
#: che dà il numero da scrivere nell'etichetta.
SCHEDE = (
    ("US", "us_table", "id_us", "sito", "us"),
    ("CERAMICA", "pottery_table", "id_rep", "sito", "id_number"),
    ("REPERTO", "inventario_materiali_table", "id_invmat", "sito",
     "numero_inventario"),
    ("TOMBA", "tomba_table", "id_tomba", "sito", "nr_scheda_taf"),
    # La struttura si nomina con sigla **e** numero: la sola sigla dà
    # «Struttura ED» a tutte e due le ED, e due media diversi finirebbero
    # a chiamarsi uguale.
    ("STRUTTURA", "struttura_table", "id_struttura", "sito",
     "sigla_struttura || '-' || numero_struttura"),
    ("UT", "ut_table", "id_ut", "progetto", "nr_ut"),
)

#: Tre media per record, e le tre inquadrature che un archeologo scatta
#: davvero: l'insieme, un dettaglio, una con la scala metrica accanto.
INQUADRATURE = (
    "veduta d'insieme da nord",
    "dettaglio da ovest",
    "veduta con scala metrica",
)


def _uuid(seme: str) -> str:
    """Un uuid stabile: lo stesso database rifatto dà gli stessi valori."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "pyarchinit/media/" + seme))


def _etichetta(tipo: str, numero, sito: str, n: int) -> str:
    """Quello che va scritto dentro l'immagine e nella descrizione.

    È una riga sola perché finisce **disegnata** nell'immagine grande:
    `example_media.disegna` prende la descrizione del media e la scrive
    nella banda in alto.
    """
    nome = {"US": "US", "CERAMICA": "Ceramica", "REPERTO": "Reperto",
            "TOMBA": "Tomba", "STRUTTURA": "Struttura",
            "UT": "UT"}.get(tipo, tipo)
    return "%s %s \u00b7 %s \u00b7 %s" % (
        nome, numero, sito, INQUADRATURE[n % len(INQUADRATURE)])


def _max(conn, tabella: str, colonna: str) -> int:
    return conn.execute(
        'SELECT COALESCE(MAX("%s"), 0) FROM "%s"' % (colonna, tabella)
    ).fetchone()[0] or 0


def record(conn, tabella, chiave, colonna_sito, colonna_numero, sito):
    """I record di quella scheda, col loro numero per l'etichetta."""
    colonne = {r[1] for r in conn.execute('PRAGMA table_info("%s")' % tabella)}
    if chiave not in colonne:
        return []
    dove, parametri = "", ()
    if colonna_sito in colonne:
        dove = ' WHERE "%s" = ?' % colonna_sito
        parametri = (sito,)
    # `colonna_numero` può essere un'espressione («sigla || '-' ||
    # numero»): si cita soltanto quando è il nome nudo di una colonna.
    if colonna_numero in colonne:
        numero = '"%s"' % colonna_numero
    elif any(c in colonna_numero for c in "|("):
        numero = colonna_numero
    else:
        numero = '"%s"' % chiave
    return conn.execute(
        'SELECT "%s", %s FROM "%s"%s ORDER BY "%s"'
        % (chiave, numero, tabella, dove, chiave), parametri).fetchall()


def esistono(conn) -> int:
    """Quanti media di esempio ci sono già."""
    return conn.execute(
        "SELECT count(*) FROM media_table WHERE tags LIKE ?",
        ("%" + TAG + "%",)).fetchone()[0]


def popola(conn, sito=SITO, quanti=QUANTI) -> dict:
    """Scrive i media. Ritorna quanti per tipo di scheda."""
    id_media = _max(conn, "media_table", "id_media")
    id_thumb = _max(conn, "media_thumb_table", "id_media_thumb")
    id_legame = _max(conn, "media_to_entity_table", "id_mediaToEntity")

    conto = {}
    for tipo, tabella, chiave, colonna_sito, colonna_numero in SCHEDE:
        righe = record(conn, tabella, chiave, colonna_sito, colonna_numero,
                       sito)
        for id_entity, numero in righe:
            for n in range(quanti):
                id_media += 1
                id_thumb += 1
                id_legame += 1
                nome = "%s_%s_%d" % (tipo, str(numero).replace(" ", "_"),
                                     n + 1)
                etichetta = _etichetta(tipo, numero, sito, n)
                thumb = "%d_%s_thumb.png" % (id_media, nome)
                grande = "%d_%s.png" % (id_media, nome)

                # `filepath` è il file **originale**. Nel database di
                # esempio l'originale non si spedisce: si punta
                # all'immagine ridimensionata, che è la più grande che
                # esiste. Le 19 righe che il demo aveva prima portavano
                # percorsi assoluti di un altro computer
                # (`C:/Users/Utente/Desktop/…`), che non aprono niente.
                conn.execute(
                    "INSERT INTO media_table (id_media, mediatype, filename,"
                    " filetype, filepath, descrizione, tags, entity_uuid)"
                    " VALUES (?,?,?,?,?,?,?,?)",
                    (id_media, "image", nome, "png", grande, etichetta,
                     "%s, %s, %s" % (tipo, sito, TAG),
                     _uuid("media/%d" % id_media)))
                conn.execute(
                    "INSERT INTO media_thumb_table (id_media_thumb, id_media,"
                    " mediatype, media_filename, media_thumb_filename,"
                    " filetype, filepath, path_resize, entity_uuid)"
                    " VALUES (?,?,?,?,?,?,?,?,?)",
                    (id_thumb, id_media, "image", nome, thumb, "png",
                     thumb, grande, _uuid("thumb/%d" % id_thumb)))
                conn.execute(
                    "INSERT INTO media_to_entity_table (id_mediaToEntity,"
                    " id_entity, entity_type, table_name, id_media, filepath,"
                    " media_name, entity_uuid) VALUES (?,?,?,?,?,?,?,?)",
                    (id_legame, int(id_entity), tipo, tabella, id_media,
                     grande, nome, _uuid("legame/%d" % id_legame)))
                conto[tipo] = conto.get(tipo, 0) + 1
    return conto


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sito", default=SITO)
    ap.add_argument("--db", default=str(DB))
    ap.add_argument("--quanti", type=int, default=QUANTI)
    args = ap.parse_args(argv)
    percorso = Path(args.db)
    if not percorso.is_file():
        raise SystemExit("manca %s" % percorso)

    conn = sqlite3.connect(percorso)
    try:
        gia = esistono(conn)
        if gia:
            print("ci sono già %d media di esempio: non si rifanno" % gia)
            return 0
        conto = popola(conn, args.sito, args.quanti)
        conn.commit()
        print("=== %s ===" % args.sito)
        for tipo, quanti in sorted(conto.items()):
            print("  %-12s %3d media" % (tipo, quanti))
        totale = sum(conto.values())
        print("  %-12s %3d media (%d file da disegnare)"
              % ("in tutto", totale, totale * 2))
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
