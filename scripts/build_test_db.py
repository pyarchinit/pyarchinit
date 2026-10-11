#!/usr/bin/env python3
"""Costruisce il database di prova che si installa accanto a quello di esempio.

    python3 scripts/build_test_db.py

Scrive `resources/dbfiles/pyarchinit_db_test.sqlite`, che
`pyarchinit_Folder_installation.install_dir()` copia in
`<PYARCHINIT_HOME>/pyarchinit_DB_folder/` al primo avvio, accanto a
`pyarchinit_db.sqlite`. Da lì si apre come qualunque altro database SQLite
del plugin: basta scegliere quel file nella finestra di configurazione.

**Perché partire da `pyarchinit.sqlite`.** È il database vuoto da cui il
plugin crea i nuovi: ha tutte le 185 tabelle, le 19 registrazioni in
`geometry_columns` e i 3723 sistemi di riferimento, e **nessun dato**.
`pyarchinit_db.sqlite` è invece quello distribuito con gli esempi nelle dieci
lingue: partire da lui vorrebbe dire cancellargli 510 US, 4820 geometrie e
tutto il resto, e sperare di non dimenticare una tabella.

**Lo SRID.** Nel database vuoto le geometrie sono registrate con `srid = -1`,
cioè nessun sistema di riferimento: un layer così QGIS lo apre senza
proiezione e la pianta non si colloca da nessuna parte. Qui si registrano a
**3004** (Monte Mario / Italia zona 2), lo stesso del database di esempio,
con `RecoverGeometryColumn` — che rifà anche l'indice spaziale.

**I casi** sono gli stessi dei test, presi da `tests/fixtures/realistic_site_db.py`
(`popola`): una sola fonte, così il database di prova e la suite non possono
divergere. Oggi sono: la stessa US in due aree con fasi diverse, un reciproco
mancante, un reciproco in forma corta, tre disallineamenti di datazione, un
sito senza nessuna scheda, un paradosso temporale, e due coppie di rapporti
di uguaglianza.

**Le geometrie** le disegna questo script, perché i casi dei test non ne
hanno bisogno e l'anteprima della matrice sì: un quadrato di 10 m per ogni
unità su una griglia, più una quota al suo centro. Servono a vedere la pianta
sotto la matrice, non a somigliare a uno scavo.
"""
from __future__ import annotations

import os
import shutil
import sqlite3
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RADICE / "tests" / "fixtures"))

import realistic_site_db as RSD  # noqa: E402

VUOTO = RADICE / "resources" / "dbfiles" / "pyarchinit.sqlite"
#: Da dove si prendono le tabelle che al vuoto mancano (le UT).
DISTRIBUITO = RADICE / "resources" / "dbfiles" / "pyarchinit_db.sqlite"
USCITA = RADICE / "resources" / "dbfiles" / "pyarchinit_db_test.sqlite"

#: Le tabelle che `pyarchinit.sqlite` non ha e `pyarchinit_db.sqlite` sì: le
#: tre Unità Topografiche, col tipo di geometria con cui vanno registrate.
#: Si copiano perché il database di prova deve avere **tutte** le tabelle: su
#: uno a cui mancano, la scheda UT non si apre. Le altre quattro differenze
#: fra i due file NON si copiano, perché sono spazzatura lasciata dagli
#: editor SQLite — `inventario_materiali_table_backup_1760259102`,
#: `inventario_materiali_table_dg_tmp_dg_tmp`, `sqlitestudio_temp_table2` — e
#: `mediaentity_view`, che è una vista.
UT = (("pyarchinit_ut_point", "POINT"),
      ("pyarchinit_ut_line", "LINESTRING"),
      ("pyarchinit_ut_polygon", "MULTIPOLYGON"))

#: Viste che stanno nel distribuito e non nel vuoto, e che il plugin usa.
#: `pyarchinit_doc_view` la nomina `tabs/US_USM.py` (`view_name`) per la
#: documentazione: un database creato dal vuoto non ce l'ha, ed è una
#: mancanza che riguarda **ogni** database nuovo, non solo questo.
VISTE_MANCANTI = ("pyarchinit_doc_view",)

#: Monte Mario / Italia zona 2, come il database di esempio.
SRID = 3004
#: Un angolo verso Volterra, in metri: le unità stanno lì intorno.
EST, NORD = 1_650_000.0, 4_810_000.0
#: Lato del quadrato di una unità e passo della griglia, in metri.
LATO, PASSO = 10.0, 14.0

#: Dove cercare spatialite. La prima che si carica vince.
SPATIALITE = (
    os.environ.get("MOD_SPATIALITE", ""),
    "/Applications/QGIS.app/Contents/MacOS/lib/mod_spatialite.so",
    "/Applications/QGIS-LTR.app/Contents/MacOS/lib/mod_spatialite.so",
    "mod_spatialite",
    "mod_spatialite.so",
    "libspatialite.so.7",
)


def _apri(percorso: Path) -> sqlite3.Connection:
    """Una connessione con spatialite caricata, o un errore che lo dice."""
    conn = sqlite3.connect(percorso)
    conn.enable_load_extension(True)
    for nome in SPATIALITE:
        if not nome:
            continue
        try:
            conn.load_extension(nome)
            return conn
        except sqlite3.OperationalError:
            continue
    conn.close()
    raise SystemExit(
        "spatialite non si carica: le geometrie non si possono registrare.\n"
        "Prova a dire dov'è con MOD_SPATIALITE=/percorso/mod_spatialite.so,\n"
        "oppure lancia questo script con il Python di QGIS:\n"
        "  /Applications/QGIS.app/Contents/MacOS/bin/python3 "
        "scripts/build_test_db.py")


#: Dal numero di `geometry_columns.geometry_type` al nome che
#: `RecoverGeometryColumn` vuole.
_TIPI = {1: "POINT", 2: "LINESTRING", 3: "POLYGON", 4: "MULTIPOINT",
         5: "MULTILINESTRING", 6: "MULTIPOLYGON", 7: "GEOMETRYCOLLECTION"}


def _colonne_geometriche(conn) -> list:
    """Ogni colonna geometrica registrata, col nome del suo tipo.

    Si legge da `geometry_columns` invece di elencarle a mano: così una
    tabella spaziale aggiunta al template domani viene registrata anche
    qui, senza che nessuno se ne ricordi.
    """
    fuori = []
    for tabella, colonna, tipo in conn.execute(
            "SELECT f_table_name, f_geometry_column, geometry_type"
            " FROM geometry_columns").fetchall():
        nome = _TIPI.get(int(tipo))
        if nome:
            fuori.append((tabella, colonna, nome))
    return fuori


def _registra(conn, tabella: str, colonna: str = "the_geom",
              tipo: str = "MULTIPOLYGON") -> None:
    """Porta una colonna geometrica da `srid = -1` a 3004, indice compreso."""
    conn.execute("SELECT DiscardGeometryColumn(?, ?)", (tabella, colonna))
    # L'indice R*Tree della registrazione vecchia va **buttato**, non
    # riusato: `CreateSpatialIndex` su un `idx_…` che c'è già fallisce con
    # «table already exists», lascia `spatial_index_enabled = 0` e l'indice
    # vuoto — quattordici geometrie e zero righe nell'indice, cioè il
    # guasto delle «geometrie invisibili». Buttare la tabella virtuale porta
    # via anche le sue `_node`, `_parent`, `_rowid`.
    conn.execute("DROP TABLE IF EXISTS idx_%s_%s" % (tabella, colonna))
    conn.execute("SELECT RecoverGeometryColumn(?, ?, ?, ?, 2)",
                 (tabella, colonna, SRID, tipo))
    conn.execute("SELECT CreateSpatialIndex(?, ?)", (tabella, colonna))


def _copia_vista(conn, sorgente, nome: str) -> bool:
    """Porta una vista e la sua registrazione spaziale, se c'è."""
    riga = sorgente.execute(
        "SELECT sql FROM sqlite_master WHERE type='view' AND name=?",
        (nome,)).fetchone()
    if not riga or not riga[0]:
        return False
    conn.execute("DROP VIEW IF EXISTS %s" % nome)
    conn.execute(riga[0])
    reg = sorgente.execute(
        "SELECT view_name, view_geometry, view_rowid, f_table_name,"
        " f_geometry_column, read_only FROM views_geometry_columns"
        " WHERE view_name=?", (nome,)).fetchone()
    if reg:
        conn.execute(
            "INSERT OR REPLACE INTO views_geometry_columns (view_name,"
            " view_geometry, view_rowid, f_table_name, f_geometry_column,"
            " read_only) VALUES (?,?,?,?,?,?)", reg)
    return True


def _copia_ut(conn) -> int:
    """Crea le tabelle UT prendendone lo schema dal database distribuito."""
    if not DISTRIBUITO.is_file():
        print("  (nota: %s non c'è, le UT restano fuori)" % DISTRIBUITO.name)
        return 0
    sorgente = sqlite3.connect(DISTRIBUITO)
    try:
        fatte = 0
        for tabella, tipo in UT:
            riga = sorgente.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
                (tabella,)).fetchone()
            if not riga or not riga[0]:
                continue
            esiste = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                (tabella,)).fetchone()
            if esiste:
                continue
            conn.execute(riga[0])
            # `RecoverGeometryColumn` e non `AddGeometryColumn`: il DDL
            # copiato porta già la colonna `the_geom`, e aggiungerla di nuovo
            # fallisce con «duplicate column name» lasciando la geometria non
            # registrata — la tabella c'è e il layer non si apre.
            #
            # Nel distribuito le UT stanno a `srid = -1`; qui vanno a 3004
            # come tutto il resto, se no la scheda UT disegna in un sistema di
            # riferimento e la pianta in un altro.
            conn.execute("SELECT RecoverGeometryColumn(?, 'the_geom', ?, ?, 2)",
                         (tabella, SRID, tipo))
            conn.execute("SELECT CreateSpatialIndex(?, 'the_geom')",
                         (tabella,))
            # La vista che va con la tabella, e la sua registrazione in
            # `views_geometry_columns`: senza quella riga una vista spaziale
            # non si apre come layer.
            _copia_vista(conn, sorgente, "%s_view" % tabella)
            fatte += 1
        for nome in VISTE_MANCANTI:
            _copia_vista(conn, sorgente, nome)
        return fatte
    finally:
        sorgente.close()


def _quadrato(i: int, area: str) -> str:
    """Il WKT di un quadrato sulla griglia. Le aree stanno una accanto
    all'altra, staccate, così si vedono come due cose distinte."""
    colonna = i % 5
    riga = i // 5
    scarto_area = 0.0 if str(area).strip() == "1" else PASSO * 6
    x = EST + scarto_area + colonna * PASSO
    y = NORD - riga * PASSO
    return ("MULTIPOLYGON(((%f %f, %f %f, %f %f, %f %f, %f %f)))"
            % (x, y, x + LATO, y, x + LATO, y + LATO, x, y + LATO, x, y))


def _geometrie(conn) -> tuple:
    """Un quadrato e una quota per ogni unità del sito di prova."""
    righe = conn.execute(
        "SELECT sito, area, us, unita_tipo FROM us_table ORDER BY area, "
        "CAST(us AS INTEGER)").fetchall()
    for i, (sito, area, us, unita_tipo) in enumerate(righe):
        conn.execute(
            "INSERT INTO pyunitastratigrafiche (scavo_s, area_s, us_s,"
            " tipo_us_s, unita_tipo_s, stratigraph_index_us, tipo_doc,"
            " nome_doc, the_geom) VALUES (?,?,?,?,?,?,?,?,"
            " GeomFromText(?, ?))",
            (sito, area, us, "positiva", unita_tipo, 2, "Planimetria",
             "pianta di prova", _quadrato(i, area), SRID))
        conn.execute(
            "INSERT INTO pyarchinit_quote (sito_q, area_q, us_q,"
            " unita_misu_q, quota_q, unita_tipo_q, the_geom)"
            " VALUES (?,?,?,?,?,?, ST_Centroid(GeomFromText(?, ?)))",
            (sito, area, us, "m", round(12.0 + i * 0.15, 2), unita_tipo,
             _quadrato(i, area), SRID))
    return len(righe), len(righe)


def main() -> int:
    if not VUOTO.is_file():
        raise SystemExit("manca il database vuoto: %s" % VUOTO)
    if USCITA.exists():
        USCITA.unlink()
    shutil.copy2(VUOTO, USCITA)

    conn = _apri(USCITA)
    try:
        prima = conn.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table'"
        ).fetchone()[0]

        RSD.popola(conn)

        # **Tutte** le colonne geometriche, non solo quelle che si
        # riempiono: questo è un database concreto, non un template, e un
        # database con gli SRID misti è un progetto che non si inquadra —
        # un layer a 3004 e uno a -1 nello stesso scavo. Nel template lo
        # SRID resta -1 di proposito, perché lo assegna pyArchInit quando
        # crea il database nuovo; qui il database è già creato.
        for tabella, colonna, tipo in _colonne_geometriche(conn):
            _registra(conn, tabella, colonna, tipo)
        n_geom, n_quote = _geometrie(conn)
        n_ut = _copia_ut(conn)
        # Le statistiche: `row_count` e l'estensione che QGIS e OGR leggono
        # invece di contare. Nel database distribuito quelle di
        # `pyunitastratigrafiche` dicono 482 righe quando sono 4820 — un
        # fattore dieci — e il conteggio che l'utente vede è quello. Qui si
        # aggiornano, così il file nasce coerente.
        conn.execute("SELECT UpdateLayerStatistics()")
        conn.commit()

        dopo = conn.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table'"
        ).fetchone()[0]
        us = conn.execute("SELECT count(*) FROM us_table").fetchone()[0]
        siti = conn.execute("SELECT count(*) FROM site_table").fetchone()[0]
        fasi = conn.execute(
            "SELECT count(*) FROM periodizzazione_table").fetchone()[0]
        srid = conn.execute(
            "SELECT srid FROM geometry_columns WHERE f_table_name="
            "'pyunitastratigrafiche'").fetchone()[0]
    finally:
        conn.close()

    print("scritto %s" % USCITA.name)
    print("  tabelle: %d (il vuoto ne aveva %d)" % (dopo, prima))
    print("  siti: %d  ·  US: %d  ·  fasi: %d" % (siti, us, fasi))
    print("  geometrie: %d poligoni, %d quote, srid %s"
          % (n_geom, n_quote, srid))
    print("  tabelle UT aggiunte dal distribuito: %d" % n_ut)
    print("  siti dentro: %s" % ", ".join(RSD.siti()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
