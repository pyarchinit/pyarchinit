#!/usr/bin/env python3
"""La scheda US del database di esempio: saggi, campi, nodi DOC, geometrie.

    /Applications/QGIS.app/Contents/MacOS/bin/python3 scripts/fill_example_us.py

Cinque lavori, tutti sul database di esempio:

1. **Quattro saggi.** `us_table.saggio` era vuoto su tutte le 510 righe,
   quindi l'esportazione «uno per saggio» dell'em.json non aveva niente da
   dividere. Le unità si distribuiscono su quattro saggi seguendo la
   stratigrafia — i due edifici, l'area delle fosse, il settore profondo —
   e i nodi virtuali (USVs, USVn, DOC, CON, Extractor…) prendono il saggio
   dell'unità che documentano, seguendo i rapporti: un nodo che sta in un
   file e l'unità che descrive in un altro non si legge.

2. **I campi della scheda.** Erano vuote in tutte le righe **88 colonne su
   131**: le misure, le quote, i materiali della muratura, il personale,
   le date, i numeri di catalogo. I campi della muratura si riempiono solo
   sulle USM — su uno strato non vogliono dire niente.

3. **I nodi DOC.** Portavano il percorso di due file del computer di chi
   fece il demo (`DosCo\\Scavo archeologico_20220218_.xlsx`,
   `DosCo\\test1_1.graphml`), che non esistono. Ora nominano due PDF che
   `modules/utility/example_media.genera_documenti` disegna al primo
   avvio dentro **DosCo**, con il testo e un'immagine.

4. **Le geometrie che mancavano.** Due US senza poligono (7 e 8) e tredici
   senza quota: «non mi sembra che tutti abbiano le geometrie» (Enzo).

5. **Il lucchetto, tolto.** Quaranta record di quattro schede avevano
   `editing_by = 'pyarchinit_demo'`: `concurrency_manager` lo legge e
   dichiara la scheda «in modifica da un altro utente». Era un errore
   della prima passata di riempimento.

Idempotente: quello che ha già un valore non si riscrive.
"""
from __future__ import annotations

import argparse
import ast
import sqlite3
import uuid
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
DB = RADICE / "resources" / "dbfiles" / "pyarchinit_db.sqlite"
SITO = "Scavo archeologico"

#: I quattro saggi, e le unità di ciascuno. La divisione segue la
#: stratigrafia, non il numero: il saggio I è l'edificio ED 1 con i suoi
#: crolli e i suoi piani, il II l'edificio ED 2 e gli strati che lo
#: coprono, il III l'area delle fosse e dei riempimenti, il IV il settore
#: profondo, dove la sequenza arriva ai livelli più antichi.
#:
#: Il valore è il numero romano e basta: l'etichetta del campo dice già
#: «Saggio», e così la stessa riga si legge uguale nei dieci siti tradotti.
SAGGI = {
    "I": ["5", "6", "12", "17", "18", "19", "20", "30", "32"],
    "II": ["1", "2", "3", "4", "9", "10", "11"],
    "III": ["7", "8", "13", "14", "15", "16", "21", "22", "23", "24",
            "25", "26", "27", "28"],
    "IV": ["29", "31", "33", "34", "35", "36", "37", "38", "39"],
}

#: I due documenti dei nodi DOC: il nome del file e che cosa c'è dentro.
#: Li disegna `example_media.genera_documenti` dentro DosCo.
DOCUMENTI = {
    "4001": ("DosCo/diario_di_scavo.pdf",
             "Diario di scavo — Scavo archeologico",
             "Giornale dello scavo, settimane 1-4. Descrizione dei "
             "livelli rimossi, delle quote raggiunte e dei materiali "
             "recuperati, con il rimando alle schede US."),
    "4002": ("DosCo/rilievo_di_fase.pdf",
             "Rilievo di fase — Scavo archeologico",
             "Planimetria di fase alla quota 488,40 m s.l.m., con le "
             "murature conservate, i piani d'uso e le fosse tagliate "
             "nel livello sottostante."),
}


def _uuid(seme: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "pyarchinit/us/" + seme))


def colonne(conn, tabella) -> list:
    return [r[1] for r in conn.execute('PRAGMA table_info("%s")' % tabella)]


def quota_del_sito(conn, sito) -> float:
    """La quota media dello scavo, **letta** dal livello delle quote.

    Non si inventa: la prima passata di riempimento scrisse quote a 52 m
    su uno scavo che sta a 488, e una scheda con la quota di un altro
    posto non serve a fare prove.
    """
    riga = conn.execute(
        "SELECT avg(quota_q) FROM pyarchinit_quote WHERE sito_q = ?",
        (sito,)).fetchone()
    return round(float(riga[0]), 2) if riga and riga[0] else 488.4


# ---------------------------------------------------------------------------
# 1. I quattro saggi
# ---------------------------------------------------------------------------

def saggi(conn, sito) -> tuple:
    """Distribuisce le unità sui quattro saggi, nodi virtuali compresi."""
    di_us = {}
    for saggio, elenco in SAGGI.items():
        for us in elenco:
            di_us[str(us)] = saggio

    righe = conn.execute(
        "SELECT us, unita_tipo, rapporti FROM us_table WHERE sito = ?",
        (sito,)).fetchall()
    rapporti = {}
    for us, _tipo, testo in righe:
        try:
            voci = ast.literal_eval(testo) if testo else []
        except Exception:
            voci = []
        rapporti[str(us)] = [str(v[1]) for v in voci
                             if isinstance(v, (list, tuple)) and len(v) > 1]

    # I nodi virtuali prendono il saggio di quello che nominano: si
    # propaga finché nessuno cambia più idea (sono catene corte —
    # 4001 → 400 → 800 → 106 → 5).
    for _giro in range(6):
        fermo = True
        for us, vicini in rapporti.items():
            if us in di_us:
                continue
            for altro in vicini:
                if altro in di_us:
                    di_us[us] = di_us[altro]
                    fermo = False
                    break
        if fermo:
            break

    scritti = 0
    for us, saggio in di_us.items():
        scritti += conn.execute(
            "UPDATE us_table SET saggio = ? WHERE sito = ? AND us = ?"
            " AND trim(coalesce(saggio, '')) = ''",
            (saggio, sito, us)).rowcount
    senza = [us for us, in conn.execute(
        "SELECT us FROM us_table WHERE sito = ?"
        " AND trim(coalesce(saggio, '')) = ''", (sito,))]
    return scritti, senza


# ---------------------------------------------------------------------------
# 2. I campi della scheda US
# ---------------------------------------------------------------------------

def campi_us(conn, sito) -> int:
    """Riempie le colonne della scheda US che erano vuote dappertutto.

    I campi della muratura (`*_usm`, i laterizi, i leganti) vanno **solo**
    sulle USM: su uno strato di terra non vogliono dire niente, e una
    scheda piena di valori che non c'entrano è peggio di una vuota.
    """
    base = quota_del_sito(conn, sito)
    presenti = set(colonne(conn, "us_table"))
    righe = conn.execute(
        "SELECT id_us, us, unita_tipo, area, d_stratigrafica, periodo_iniziale"
        " FROM us_table WHERE sito = ? ORDER BY cast(us AS INTEGER)",
        (sito,)).fetchall()

    scritti = 0
    for n, (id_us, us, tipo, area, d_strat, periodo) in enumerate(righe):
        muraria = str(tipo or "").strip() in ("USM", "WSU", "MSE", "UEM",
                                              "USZ", "ΤΣΜ")
        alto = round(base + 0.40 - n * 0.012, 2)
        basso = round(alto - 0.18, 2)
        valori = {
            # dove sta
            "quad_par": "Q%d" % (n % 4 + 1),
            "ambient": "Ambiente %d" % (n % 3 + 1),
            "posizione": "Settore %s, quadrato %d"
                         % ("A" if n % 2 == 0 else "B", n % 4 + 1),
            "un_ed_riass": "Unità edilizia %d" % (n % 2 + 1),
            "unita_edilizie": "UE %d" % (n % 2 + 1),
            # come è stata riconosciuta
            "criteri_distinzione": "Colore, consistenza e inclusi diversi "
                                   "da quelli dell'unità sottostante.",
            "osservazioni": "Unità documentata con fotopiano e sezione; "
                            "campionata nel settore nord.",
            "affidabilita": ("Buona" if n % 3 else "Discreta"),
            "elem_datanti": "Frammenti di maiolica arcaica dal "
                            "riempimento.",
            "componenti_organici": "Carboni, radici, frammenti ossei "
                                   "animali.",
            "componenti_inorganici": "Ghiaia, frammenti di laterizio, "
                                     "malta di calce.",
            "organici": "Carboni",
            "inorganici": "Laterizi",
            "quantificazioni": "Frammenti ceramici: %d; laterizi: %d"
                               % (12 + n, 4 + n % 5),
            # le misure
            "lunghezza_max": round(2.10 + n * 0.07, 2),
            "larghezza_media": round(1.40 + n * 0.05, 2),
            "altezza_max": round(0.42 + (n % 5) * 0.03, 2),
            "altezza_min": round(0.18 + (n % 5) * 0.02, 2),
            "profondita_max": round(0.36 + (n % 4) * 0.04, 2),
            "profondita_min": round(0.12 + (n % 4) * 0.03, 2),
            # le quote, sul livello vero dello scavo
            "quota_max_abs": alto,
            "quota_min_abs": basso,
            "quota_max_rel": round(alto - base, 2),
            "quota_min_rel": round(basso - base, 2),
            "quota_abs": alto,
            "quota_relativa": round(alto - base, 2),
            # chi e quando
            "direttore_us": "Enzo Cocca",
            "responsabile_us": "Nicola Esposito",
            "cod_ente_schedatore": "SABAP-FI",
            "data_rilevazione": "2021-04-%02d" % (5 + n % 20),
            "data_rielaborazione": "2021-09-%02d" % (6 + n % 20),
            # i numeri di catalogo e i rimandi
            "n_catalogo_generale": "%07d" % (1500000 + n),
            "n_catalogo_interno": "SA-%03d" % (n + 1),
            "n_catalogo_internazionale": "IT-SA-%04d" % (n + 1),
            "ref_tm": "TM %d" % (n % 6 + 1),
            "ref_ra": "RA %03d" % (n + 1),
            "ref_n": "N %03d" % (n + 1),
            "sing_doc": "Scheda US %s, fotopiano e sezione." % us,
            # Chi ha toccato la scheda per ultimo. `editing_by` e
            # `editing_since` invece NO: sono il lucchetto del record.
            "last_modified_by": "demo",
            "last_modified_timestamp": "2021-09-30 17:40:00",
        }
        if muraria:
            valori.update({
                "lunghezza_usm": round(4.20 + n * 0.1, 2),
                "altezza_usm": round(1.15 + (n % 4) * 0.08, 2),
                "spessore_usm": round(0.52 + (n % 3) * 0.04, 2),
                "quota_max_usm": alto,
                "quota_min_usm": round(alto - 1.15, 2),
                "tecnica_muraria_usm": "Opera incerta di laterizi di "
                                       "reimpiego e ciottoli",
                "modulo_usm": "5 corsi in 34 cm",
                "tipologia_opera": "Muratura portante",
                "sezione_muraria": "A sacco, con nucleo di scaglie e malta",
                "superficie_analizzata": "Prospetto sud, 4,2 x 1,1 m",
                "orientamento": "Nord-ovest/Sud-est",
                "spess_giunti": "1,5 - 2,5 cm",
                "letti_posa": "Orizzontali, regolari",
                "alt_mod": "34 cm",
                "posa_opera": "In piano, corsi suborizzontali",
                "funz_statica": "Portante",
                "lavorazione": "Laterizi di reimpiego, spezzati a misura",
                "col_legante": "Biancastro",
                "aggreg_legante": "Sabbia e calce",
                "con_text_mat": "Compatta, con inclusi di piccole "
                                "dimensioni",
                "col_materiale": "Rosso arancio",
                "inclusi_materiali_usm": "Quarzo, chamotte",
                "inerti_usm": "Sabbia di fiume",
                "tipo_legante_usm": "Malta di calce aerea",
                "rifinitura_usm": "Stilatura dei giunti",
                "materiali_lat": "Laterizio",
                "lavorazione_lat": "Stampo",
                "consistenza_lat": "Compatta",
                "forma_lat": "Rettangolare",
                "colore_lat": "Rosso arancio",
                "impasto_lat": "Depurato con inclusi di quarzo",
                "materiale_p": "Arenaria",
                "forma_p": "Sbozzata",
                "colore_p": "Grigio chiaro",
                "taglio_p": "A spacco",
                "posa_opera_p": "In piano",
                "consistenza_p": "Compatta",
                "criteri_distinzione_usm": "Differenza di tessitura e di "
                                           "legante rispetto alla USM "
                                           "adiacente.",
                "provenienza_materiali_usm": "Reimpiego da strutture "
                                             "precedenti del sito.",
                "campioni_malta_usm": "CM-%02d" % (n % 5 + 1),
                "campioni_mattone_usm": "CL-%02d" % (n % 5 + 1),
                "campioni_pietra_usm": "CP-%02d" % (n % 5 + 1),
            })
        valori["entity_uuid"] = _uuid("%s/%s" % (sito, id_us))

        campi, params = [], []
        for colonna, valore in valori.items():
            if colonna not in presenti:
                continue
            campi.append('"%s" = ?' % colonna)
            params.append(valore)
        if not campi:
            continue
        # Solo dove è vuoto: un dato scritto a mano non si sovrascrive.
        condizioni = " OR ".join(
            'trim(coalesce(cast("%s" as text), \'\')) = \'\''
            % c.split('"')[1] for c in campi)
        params.append(id_us)
        scritti += conn.execute(
            'UPDATE us_table SET %s WHERE id_us = ? AND (%s)'
            % (", ".join(campi), condizioni), params).rowcount
    return scritti


# ---------------------------------------------------------------------------
# 3. I nodi DOC
# ---------------------------------------------------------------------------

def nodi_doc(conn, sito) -> int:
    """Fa puntare i nodi DOC a due PDF che esistono, dentro DosCo."""
    scritti = 0
    for us, (percorso, titolo, _testo) in DOCUMENTI.items():
        scritti += conn.execute(
            "UPDATE us_table SET doc_usv = ?, d_interpretativa = ?,"
            " d_stratigrafica = ? WHERE sito = ? AND us = ?"
            "   AND unita_tipo = 'DOC'",
            (percorso.replace("/", "\\"), titolo, "Documento",
             sito, us)).rowcount
    return scritti


# ---------------------------------------------------------------------------
# 4. Le geometrie che mancavano
# ---------------------------------------------------------------------------

def geometrie(conn, sito) -> tuple:
    """Disegna i poligoni e le quote delle unità che ne erano senza."""
    base = quota_del_sito(conn, sito)
    modello = conn.execute(
        "SELECT area_s, disegnatore, data, tipo_doc, srid FROM"
        " (SELECT p.*, (SELECT srid FROM geometry_columns"
        "   WHERE f_table_name = 'pyunitastratigrafiche') AS srid"
        "  FROM pyunitastratigrafiche p WHERE p.scavo_s = ? LIMIT 1)",
        (sito,)).fetchone()
    if not modello:
        return (0, 0)
    _area, disegnatore, data, tipo_doc, srid = modello
    estensione = conn.execute(
        "SELECT min(MbrMinX(the_geom)), min(MbrMinY(the_geom)),"
        "       max(MbrMaxX(the_geom)), max(MbrMaxY(the_geom))"
        "  FROM pyunitastratigrafiche WHERE scavo_s = ?", (sito,)).fetchone()
    est, nord = float(estensione[0]), float(estensione[1])
    largo = max(float(estensione[2]) - est, 4.0)
    alto = max(float(estensione[3]) - nord, 4.0)

    poligoni = quote = 0
    senza_poligono = [r[0] for r in conn.execute(
        "SELECT u.us FROM us_table u WHERE u.sito = ?"
        "   AND u.unita_tipo IN ('US', 'USM')"
        "   AND NOT EXISTS (SELECT 1 FROM pyunitastratigrafiche g"
        "                   WHERE g.scavo_s = u.sito"
        "                     AND cast(g.us_s AS TEXT) = cast(u.us AS TEXT))"
        "   AND NOT EXISTS (SELECT 1 FROM pyunitastratigrafiche_usm g"
        "                   WHERE g.scavo_s = u.sito"
        "                     AND cast(g.us_s AS TEXT) = cast(u.us AS TEXT))",
        (sito,))]
    for i, us in enumerate(senza_poligono):
        area, tipo = conn.execute(
            "SELECT area, unita_tipo FROM us_table WHERE sito = ? AND us = ?"
            " LIMIT 1", (sito, us)).fetchone()
        x = est + (i % 4) * (largo / 5.0) + largo / 12.0
        y = nord + (i // 4) * (alto / 5.0) + alto / 12.0
        lato = min(largo, alto) / 8.0
        # `geometry_columns` dichiara **6** per questo livello, cioè
        # MULTIPOLYGON: un POLYGON semplice lo rifiuta con «geom-type or
        # SRID not allowed».
        wkt = ("MULTIPOLYGON(((%f %f, %f %f, %f %f, %f %f, %f %f)))"
               % (x, y, x + lato, y, x + lato, y + lato, x, y + lato, x, y))
        conn.execute(
            "INSERT INTO pyunitastratigrafiche (area_s, scavo_s, us_s,"
            " tipo_us_s, disegnatore, data, tipo_doc, the_geom)"
            " VALUES (?,?,?,?,?,?,?, GeomFromText(?, ?))",
            (area, sito, str(us), "negativa" if str(tipo) == "US" else
             "positiva", disegnatore, data, tipo_doc, wkt, srid))
        poligoni += 1

    srid_q = conn.execute(
        "SELECT srid FROM geometry_columns WHERE f_table_name ="
        " 'pyarchinit_quote'").fetchone()[0]
    senza_quota = [r[0] for r in conn.execute(
        "SELECT u.us FROM us_table u WHERE u.sito = ?"
        "   AND u.unita_tipo IN ('US', 'USM')"
        "   AND NOT EXISTS (SELECT 1 FROM pyarchinit_quote g"
        "                   WHERE g.sito_q = u.sito"
        "                     AND cast(g.us_q AS TEXT) = cast(u.us AS TEXT))",
        (sito,))]
    for i, us in enumerate(senza_quota):
        area = conn.execute(
            "SELECT area FROM us_table WHERE sito = ? AND us = ? LIMIT 1",
            (sito, us)).fetchone()[0]
        x = est + largo * (0.2 + 0.1 * (i % 6))
        y = nord + alto * (0.2 + 0.1 * (i // 6))
        conn.execute(
            "INSERT INTO pyarchinit_quote (sito_q, area_q, us_q,"
            " unita_misu_q, quota_q, data, disegnatore, the_geom)"
            " VALUES (?,?,?,?,?,?,?, GeomFromText(?, ?))",
            (sito, area, str(us), "s.l.m.", round(base - 0.05 - i * 0.02, 2),
             "2021-12-13", disegnatore, "POINT(%f %f)" % (x, y), srid_q))
        quote += 1
    return poligoni, quote


# ---------------------------------------------------------------------------
# 5. Il lucchetto
# ---------------------------------------------------------------------------

def niente_lucchetti(conn) -> int:
    """Toglie `editing_by`/`editing_since` da tutte le schede.

    Sono il lucchetto del record (`modules/db/concurrency_manager.py`):
    con un valore lì dentro la scheda risulta «in modifica da un altro
    utente». Quaranta record di quattro schede li avevano, scritti per
    sbaglio dalla prima passata di riempimento.
    """
    liberati = 0
    for (tabella,) in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
            " AND name LIKE '%_table'").fetchall():
        presenti = colonne(conn, tabella)
        if "editing_by" not in presenti:
            continue
        campi = ["editing_by = NULL"]
        if "editing_since" in presenti:
            campi.append("editing_since = NULL")
        liberati += conn.execute(
            'UPDATE "%s" SET %s WHERE trim(coalesce(editing_by, \'\')) <> \'\''
            % (tabella, ", ".join(campi))).rowcount
    return liberati


# ---------------------------------------------------------------------------

SPATIALITE = (None, "mod_spatialite", "mod_spatialite.so", "mod_spatialite.dylib",
              "/Applications/QGIS.app/Contents/MacOS/lib/mod_spatialite.so")


def _apri(percorso: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(percorso)
    conn.enable_load_extension(True)
    import os
    for nome in (os.environ.get("MOD_SPATIALITE"),) + SPATIALITE:
        if not nome:
            continue
        try:
            conn.load_extension(nome)
            return conn
        except sqlite3.OperationalError:
            continue
    conn.close()
    raise SystemExit(
        "spatialite non si carica: le geometrie non si possono scrivere.\n"
        "Lancia questo script con il Python di QGIS.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sito", default=SITO)
    ap.add_argument("--db", default=str(DB))
    ap.add_argument("--tutti-i-siti", action="store_true",
                    help="i saggi anche sui nove siti tradotti")
    args = ap.parse_args(argv)
    percorso = Path(args.db)
    if not percorso.is_file():
        raise SystemExit("manca %s" % percorso)

    conn = _apri(percorso)
    try:
        print("=== %s ===" % args.sito)
        siti = [args.sito]
        if args.tutti_i_siti:
            siti = [r[0] for r in conn.execute(
                "SELECT DISTINCT sito FROM us_table ORDER BY sito")]
        for sito in siti:
            scritti, senza = saggi(conn, sito)
            etichetta = "saggi" if sito == args.sito else "saggi (%s)" % sito[:18]
            print("  %-22s %3d unità distribuite%s"
                  % (etichetta, scritti,
                     ", %d senza saggio" % len(senza) if senza else ""))

        print("  %-22s %3d valori" % ("campi della scheda",
                                      campi_us(conn, args.sito)))
        print("  %-22s %3d nodi" % ("nodi DOC", nodi_doc(conn, args.sito)))
        poligoni, quote = geometrie(conn, args.sito)
        print("  %-22s %3d poligoni, %d quote"
              % ("geometrie mancanti", poligoni, quote))
        print("  %-22s %3d record liberati" % ("lucchetto tolto",
                                               niente_lucchetti(conn)))

        for tabella, _c in conn.execute(
                "SELECT f_table_name, f_geometry_column FROM geometry_columns"
        ).fetchall():
            conn.execute("SELECT InvalidateLayerStatistics(?, 'the_geom')",
                         (tabella,))
            conn.execute("SELECT UpdateLayerStatistics(?, 'the_geom')",
                         (tabella,))
        conn.commit()
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
