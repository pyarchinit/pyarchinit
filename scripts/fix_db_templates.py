#!/usr/bin/env python3
"""Ripara i due database che il plugin distribuisce.

    /Applications/QGIS.app/Contents/MacOS/bin/python3 scripts/fix_db_templates.py

I due file sono `resources/dbfiles/`:

* **`pyarchinit.sqlite`** — il database **vuoto**, quello da cui il plugin
  crea i nuovi. È il più importante dei due: ogni sua lacuna si ripete in
  ogni database che un utente crea da oggi in avanti.
* **`pyarchinit_db.sqlite`** — quello **con i dati di esempio**, distribuito
  con gli esempi nelle dieci lingue.

Che cosa ripara, e perché.

**Nel vuoto mancavano le Unità Topografiche** (`pyarchinit_ut_point`,
`_line`, `_polygon`) con le loro tre viste: ci sono nel distribuito e non nel
vuoto, quindi la scheda UT non funziona su nessun database creato di nuovo.
Si registrano a `srid = -1` come le altre diciannove registrazioni di questo
file e come stanno già nel distribuito: lo SRID del template non si cambia
qui, perché deciderlo vorrebbe dire imporre un sistema di riferimento
italiano a ogni scavo del mondo.

**Nel vuoto mancava `pyarchinit_doc_view`**, la vista che `tabs/US_USM.py`
nomina (`view_name`) per la documentazione. Il vuoto ha al suo posto
`pyarchinit_doc_view_b`, che il plugin non chiama: i due file sono
divergenti, non uno la versione piena dell'altro.

**Nel distribuito c'erano tre tabelle di spazzatura** lasciate dagli editor
SQLite — un backup con il timestamp nel nome e due tabelle temporanee — e
stavano arrivando agli utenti.

**Nel distribuito le statistiche erano stantie**: `geometry_columns_statistics`
diceva che `pyunitastratigrafiche` ha 482 righe quando ne ha 4820, un fattore
dieci. `row_count` è quello che QGIS e OGR leggono invece di contare, e OGR
infatti riportava 482 feature.

Lo script è idempotente: rilanciarlo non fa niente di nuovo.
"""
from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
VUOTO = RADICE / "resources" / "dbfiles" / "pyarchinit.sqlite"
DISTRIBUITO = RADICE / "resources" / "dbfiles" / "pyarchinit_db.sqlite"

#: Le UT e il tipo di geometria con cui vanno registrate.
UT = (("pyarchinit_ut_point", "POINT"),
      ("pyarchinit_ut_line", "LINESTRING"),
      ("pyarchinit_ut_polygon", "MULTIPOLYGON"))

#: Viste che il plugin usa e che al vuoto mancano.
VISTE = ("pyarchinit_doc_view",)

#: Avanzi degli editor SQLite, da non distribuire.
SPAZZATURA = ("inventario_materiali_table_backup_1760259102",
              "inventario_materiali_table_dg_tmp_dg_tmp",
              "sqlitestudio_temp_table2")

SPATIALITE = (
    os.environ.get("MOD_SPATIALITE", ""),
    "/Applications/QGIS.app/Contents/MacOS/lib/mod_spatialite.so",
    "/Applications/QGIS-LTR.app/Contents/MacOS/lib/mod_spatialite.so",
    "mod_spatialite", "mod_spatialite.so", "libspatialite.so.7",
)


def _apri(percorso: Path) -> sqlite3.Connection:
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
        "spatialite non si carica. Lancia questo script con il Python di "
        "QGIS, o di' dov'è con MOD_SPATIALITE=/percorso/mod_spatialite.so")


def _esiste(conn, nome: str, tipo: str = "table") -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type=? AND name=?",
        (tipo, nome)).fetchone() is not None


def _srid_del_file(conn) -> int:
    """Lo SRID con cui questo file registra le sue geometrie.

    Si legge invece di deciderlo: nel vuoto è -1, nel distribuito 3004, e le
    UT devono stare come sta il resto del file in cui finiscono.
    """
    riga = conn.execute(
        "SELECT srid FROM geometry_columns WHERE f_table_name="
        "'pyunitastratigrafiche'").fetchone()
    return int(riga[0]) if riga else -1


def ripara_vuoto(sorgente: Path = DISTRIBUITO) -> list:
    """Porta nel vuoto le UT e le viste che gli mancano. Dice che ha fatto."""
    fatto = []
    src = sqlite3.connect(sorgente)
    conn = _apri(VUOTO)
    try:
        srid = _srid_del_file(conn)
        for tabella, tipo in UT:
            if _esiste(conn, tabella):
                continue
            ddl = src.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
                (tabella,)).fetchone()
            if not ddl or not ddl[0]:
                continue
            conn.execute(ddl[0])
            # `RecoverGeometryColumn`: il DDL copiato porta già `the_geom`, e
            # `AddGeometryColumn` fallirebbe con «duplicate column name»
            # lasciando la geometria non registrata.
            conn.execute("SELECT RecoverGeometryColumn(?, 'the_geom', ?, ?, 2)",
                         (tabella, srid, tipo))
            conn.execute("SELECT CreateSpatialIndex(?, 'the_geom')", (tabella,))
            fatto.append("tabella %s (srid %d)" % (tabella, srid))

            vista = "%s_view" % tabella
            if not _esiste(conn, vista, "view"):
                if _copia_vista(conn, src, vista):
                    fatto.append("vista %s" % vista)

        for nome in VISTE:
            if not _esiste(conn, nome, "view") and _copia_vista(conn, src, nome):
                fatto.append("vista %s" % nome)
        conn.commit()
    finally:
        conn.close()
        src.close()
    return fatto


def _copia_vista(conn, src, nome: str) -> bool:
    ddl = src.execute(
        "SELECT sql FROM sqlite_master WHERE type='view' AND name=?",
        (nome,)).fetchone()
    if not ddl or not ddl[0]:
        return False
    conn.execute("DROP VIEW IF EXISTS %s" % nome)
    conn.execute(ddl[0])
    reg = src.execute(
        "SELECT view_name, view_geometry, view_rowid, f_table_name,"
        " f_geometry_column, read_only FROM views_geometry_columns"
        " WHERE view_name=?", (nome,)).fetchone()
    if reg:
        conn.execute(
            "INSERT OR REPLACE INTO views_geometry_columns (view_name,"
            " view_geometry, view_rowid, f_table_name, f_geometry_column,"
            " read_only) VALUES (?,?,?,?,?,?)", reg)
    return True


def ripara_distribuito() -> list:
    """Butta la spazzatura e rifà le statistiche. Dice che ha fatto."""
    fatto = []
    conn = _apri(DISTRIBUITO)
    try:
        for nome in SPAZZATURA:
            if _esiste(conn, nome):
                conn.execute('DROP TABLE "%s"' % nome)
                fatto.append("buttata la tabella %s" % nome)
        prima = conn.execute(
            "SELECT f_table_name, row_count FROM geometry_columns_statistics"
        ).fetchall()
        # `UpdateLayerStatistics` da sola risponde «1» e **non aggiorna
        # niente** quando le statistiche sono marcate come valide: il
        # `row_count` sbagliato resta. Prima va invalidata la riga, poi
        # ricalcolata. (Misurato: 482 → 482 con la sola Update, 482 → 4820
        # con Invalidate + Update.)
        for tabella, _n in prima:
            conn.execute("SELECT InvalidateLayerStatistics(?, 'the_geom')",
                         (tabella,))
            conn.execute("SELECT UpdateLayerStatistics(?, 'the_geom')",
                         (tabella,))
        conn.commit()
        dopo = dict(conn.execute(
            "SELECT f_table_name, row_count FROM geometry_columns_statistics"
        ).fetchall())
        for tabella, n in prima:
            if dopo.get(tabella) != n:
                fatto.append("statistiche di %s: %s → %s"
                             % (tabella, n, dopo.get(tabella)))
    finally:
        conn.close()
    return fatto


def main() -> int:
    for percorso in (VUOTO, DISTRIBUITO):
        if not percorso.is_file():
            raise SystemExit("manca %s" % percorso)

    print("=== %s (il vuoto, da cui nascono i nuovi) ===" % VUOTO.name)
    fatto = ripara_vuoto()
    print("\n".join("  " + r for r in fatto) if fatto
          else "  niente da fare")

    print("=== %s (quello con gli esempi) ===" % DISTRIBUITO.name)
    fatto = ripara_distribuito()
    print("\n".join("  " + r for r in fatto) if fatto
          else "  niente da fare")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
