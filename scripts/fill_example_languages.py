# -*- coding: utf-8 -*-
"""Il database di esempio nelle altre nove lingue.

    python3 scripts/fill_example_languages.py --conta     # misura, su una copia
    python3 scripts/fill_example_languages.py --scrivi    # scrive nel demo

«Riempi il db di esempio anche nelle altre lingue» (Enzo, 12 ottobre 2026).
Il sito italiano, «Scavo archeologico», ha 27 tabelle che gli altri nove
siti non hanno, i media, e decine di colonne della scheda US che altrove
sono vuote. Qui si copia tutto dall'italiano a ciascuno dei nove siti,
traducendo il testo col dizionario di `scripts/example_i18n_testi.py`
(`--conta` dice che cosa manca ancora), con chiavi e uuid nuovi, le
presenze rimappate sulle persone copiate e la fauna sulle US del sito.

Lanciare con il Python di QGIS: le undici tabelle spaziali vogliono
spatialite caricata.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
if str(RADICE) not in sys.path:
    sys.path.insert(0, str(RADICE))

from scripts.example_i18n import (  # noqa: E402
    LINGUA_DEL_SITO, SITO_IT, copia_tabella, riempi_us,
)
from scripts.fill_example_us import _apri  # noqa: E402

DB = RADICE / "resources" / "dbfiles" / "pyarchinit_db.sqlite"

#: Le tabelle da copiare, nell'ordine in cui vanno copiate: chi punta a
#: un'altra per id viene dopo di lei, e dice a quale.
TABELLE = (
    ("personale_table", None),
    ("presenze_table", ("id_personale", "personale_table")),
    ("attrezzature_table", None),
    ("budget_table", None),
    ("computo_metrico_table", None),
    ("campioni_table", None),
    ("pyarchinit_campionature", None),
    ("documentazione_table", None),
    ("pyarchinit_documentazione", None),
    ("archeozoology_table", None),
    ("fauna", None),
    ("fauna_table", ("id_us", "us_table")),
    ("inventario_lapidei_table", None),
    ("detsesso_table", None),
    ("deteta_table", None),
    ("tafonomia_table", None),
    ("pyarchinit_tafonomia", None),
    ("pyarchinit_individui", None),
    ("pyarchinit_strutture_ipotesi", None),
    ("pyarchinit_quote_usm", None),
    ("pyarchinit_linee_rif", None),
    ("pyarchinit_punti_rif", None),
    ("pyarchinit_sezioni", None),
    ("pyarchinit_ut_line", None),
    ("pyarchinit_ut_point", None),
    ("pyarchinit_ut_polygon", None),
    ("tma_materiali_archeologici", None),
)

#: I due documenti dei nodi DOC, gli stessi PDF per tutti i siti.
DOC_PDF = {"4001": "DosCo\\diario_di_scavo.pdf",
           "4002": "DosCo\\rilievo_di_fase.pdf"}


def mappa_us(conn, sito_it, sito_dest) -> dict:
    """id_us italiano → id_us del sito, per la stessa (area, us, tipo)."""
    def chiavi(sito):
        return {(str(a), str(u), str(t or "")): i for i, a, u, t in conn.execute(
            "SELECT id_us, area, us, unita_tipo FROM us_table WHERE sito = ?", (sito,))}
    it, dest = chiavi(sito_it), chiavi(sito_dest)
    return {it[k]: dest[k] for k in it if k in dest}


def nodi_doc(conn, sito) -> int:
    scritti = 0
    for us, pdf in DOC_PDF.items():
        scritti += conn.execute(
            "UPDATE us_table SET doc_usv = ? WHERE sito = ? AND us = ? "
            "AND unita_tipo = 'DOC' AND COALESCE(doc_usv, '') <> ?",
            (pdf, sito, us, pdf)).rowcount
    return scritti


def media(conn, sito) -> int:
    from scripts.fill_example_media import esistono, popola
    if esistono(conn, sito):
        return 0
    return sum(popola(conn, sito).values())


def statistiche_spaziali(conn) -> int:
    """Rimette a posto `geometry_columns_statistics` per le tabelle copiate.

    QGIS e OGR leggono `row_count` e l'estensione da lì invece di contare;
    dopo le copie dicevano 10 righe dove ce n'erano 100.
    `UpdateLayerStatistics` da sola non aggiorna una riga marcata valida:
    va invalidata prima (vedi `tests/utility/test_db_templates.py`)."""
    aggiornate = 0
    for tabella, _rif in TABELLE:
        if not tabella.startswith("pyarchinit_"):
            continue
        try:
            conn.execute("SELECT InvalidateLayerStatistics(?, 'the_geom')", (tabella,))
            conn.execute("SELECT UpdateLayerStatistics(?, 'the_geom')", (tabella,))
            aggiornate += 1
        except sqlite3.Error:
            pass
    return aggiornate


def giro(conn, siti, scrivere: bool) -> dict:
    """Tutto il giro su ogni sito. Ritorna il rendiconto per tabella."""
    rendiconto = {}
    for sito in siti:
        lingua = LINGUA_DEL_SITO[sito]
        mappe = {}
        es = riempi_us(conn, SITO_IT, sito, lingua)
        voce = rendiconto.setdefault("us_table", {"righe": 0, "mancate": set()})
        voce["righe"] += es.righe
        voce["mancate"] |= es.mancate
        for tabella, riferimento in TABELLE:
            rimappa = None
            if riferimento:
                colonna, origine = riferimento
                rimappa = {colonna: (mappa_us(conn, SITO_IT, sito)
                                     if origine == "us_table" else mappe[origine])}
            es = copia_tabella(conn, tabella, SITO_IT, sito, lingua, rimappa=rimappa)
            mappe[tabella] = es.mappa_pk
            voce = rendiconto.setdefault(tabella, {"righe": 0, "mancate": set()})
            voce["righe"] += es.righe
            voce["mancate"] |= es.mancate
        voce = rendiconto.setdefault("nodi DOC", {"righe": 0, "mancate": set()})
        voce["righe"] += nodi_doc(conn, sito)
        voce = rendiconto.setdefault("media", {"righe": 0, "mancate": set()})
        voce["righe"] += media(conn, sito)
    voce = rendiconto.setdefault("statistiche spaziali", {"righe": 0, "mancate": set()})
    voce["righe"] += statistiche_spaziali(conn)
    return rendiconto


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--conta", action="store_true", help="misura su una copia, non scrive")
    g.add_argument("--scrivi", action="store_true", help="scrive nel database di esempio")
    ap.add_argument("--db", default=str(DB))
    ap.add_argument("--rapporto", default=None, help="dove scrivere le frasi mancanti (json)")
    args = ap.parse_args(argv)

    percorso = Path(args.db)
    if not percorso.is_file():
        raise SystemExit("manca %s" % percorso)
    lavoro = percorso
    if args.conta:
        lavoro = Path(tempfile.mkdtemp(prefix="demo-lingue-")) / percorso.name
        shutil.copy2(percorso, lavoro)

    siti = [s for s in LINGUA_DEL_SITO if s != SITO_IT]
    conn = _apri(lavoro)
    try:
        rendiconto = giro(conn, siti, scrivere=args.scrivi)
        if args.scrivi:
            conn.commit()
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        else:
            conn.rollback()
    finally:
        conn.close()

    mancate_tot = 0
    for tabella, voce in rendiconto.items():
        mancate_tot += len(voce["mancate"])
        print("  %-30s righe=%-5d frasi mancanti=%d" % (tabella, voce["righe"], len(voce["mancate"])))
    print("  %-30s frasi mancanti in tutto: %d" % ("", mancate_tot))
    if args.rapporto:
        Path(args.rapporto).write_text(json.dumps(
            {t: sorted(v["mancate"]) for t, v in rendiconto.items() if v["mancate"]},
            ensure_ascii=False, indent=1), encoding="utf-8")
        print("  frasi mancanti scritte in %s" % args.rapporto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
