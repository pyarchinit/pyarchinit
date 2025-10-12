#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per allineare pyarchinit_quote con lo schema PostgreSQL
PostgreSQL ha pyarchinit_quote come tabella, non come view
"""

import sqlite3
import os
from datetime import datetime

def align_quote_tables(db_path):
    """Allinea le tabelle quote con lo schema PostgreSQL"""
    
    print(f"\n{'='*60}")
    print(f"Allineamento quote con PostgreSQL: {os.path.basename(db_path)}")
    print(f"{'='*60}\n")
    
    conn = sqlite3.connect(db_path)
    conn.enable_load_extension(True)
    
    # Carica spatialite
    try:
        conn.load_extension("mod_spatialite")
    except:
        try:
            conn.load_extension("mod_spatialite.so")
        except:
            pass
    
    cursor = conn.cursor()
    
    # Disabilita constraints
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    # 1. Drop le view se esistono
    print("1. Rimozione view quote...")
    cursor.execute("DROP VIEW IF EXISTS pyarchinit_quote")
    cursor.execute("DROP VIEW IF EXISTS pyarchinit_quote_usm")
    print("   ✓ View rimosse")
    
    # 2. Crea le tabelle pyarchinit_quote e pyarchinit_quote_usm come nello schema PostgreSQL
    print("\n2. Creazione tabelle quote...")
    
    # pyarchinit_quote
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pyarchinit_quote (
            gid INTEGER PRIMARY KEY AUTOINCREMENT,
            sito_q TEXT,
            area_q TEXT,
            us_q TEXT,
            unita_misu_q TEXT,
            quota_q REAL,
            the_geom BLOB,
            data TEXT,
            disegnatore TEXT,
            rilievo_originale TEXT,
            unita_tipo_q TEXT
        )
    """)
    print("   ✓ Creata tabella pyarchinit_quote")
    
    # pyarchinit_quote_usm
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pyarchinit_quote_usm (
            gid INTEGER PRIMARY KEY AUTOINCREMENT,
            sito_q TEXT,
            area_q TEXT,
            us_q TEXT,
            unita_misu_q TEXT,
            quota_q REAL,
            the_geom BLOB,
            data TEXT,
            disegnatore TEXT,
            rilievo_originale TEXT,
            unita_tipo_q TEXT
        )
    """)
    print("   ✓ Creata tabella pyarchinit_quote_usm")
    
    # 3. Registra geometrie se spatialite è disponibile
    try:
        # Ottieni SRID
        cursor.execute("SELECT srid FROM geometry_columns LIMIT 1")
        result = cursor.fetchone()
        srid = result[0] if result else 3004
        
        # Registra geometrie
        cursor.execute(f"SELECT RecoverGeometryColumn('pyarchinit_quote', 'the_geom', {srid}, 'POINT', 'XY')")
        cursor.execute(f"SELECT RecoverGeometryColumn('pyarchinit_quote_usm', 'the_geom', {srid}, 'POINT', 'XY')")
        print("\n   ✓ Geometrie registrate")
    except:
        pass
    
    # 4. Crea le view _view come nello schema PostgreSQL
    print("\n3. Creazione view _view...")
    
    # pyarchinit_quote_view
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS pyarchinit_quote_view AS
        SELECT 
            pyarchinit_quote.gid,
            pyarchinit_quote.sito_q,
            pyarchinit_quote.area_q,
            pyarchinit_quote.us_q,
            pyarchinit_quote.unita_misu_q,
            pyarchinit_quote.quota_q,
            pyarchinit_quote.the_geom,
            pyarchinit_quote.unita_tipo_q,
            us_table.id_us,
            us_table.sito,
            us_table.area,
            us_table.us,
            us_table.struttura,
            us_table.d_stratigrafica,
            us_table.d_interpretativa,
            us_table.descrizione,
            us_table.interpretazione,
            us_table.rapporti,
            us_table.periodo_iniziale,
            us_table.fase_iniziale,
            us_table.periodo_finale,
            us_table.fase_finale,
            us_table.anno_scavo,
            us_table.cont_per
        FROM pyarchinit_quote
        JOIN us_table ON 
            pyarchinit_quote.sito_q = us_table.sito AND 
            pyarchinit_quote.area_q = us_table.area AND 
            pyarchinit_quote.us_q = us_table.us AND 
            pyarchinit_quote.unita_tipo_q = us_table.unita_tipo
    """)
    print("   ✓ Creata view pyarchinit_quote_view")
    
    # pyarchinit_quote_usm_view
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS pyarchinit_quote_usm_view AS
        SELECT 
            pyarchinit_quote_usm.gid,
            pyarchinit_quote_usm.sito_q,
            pyarchinit_quote_usm.area_q,
            pyarchinit_quote_usm.us_q,
            pyarchinit_quote_usm.unita_misu_q,
            pyarchinit_quote_usm.quota_q,
            pyarchinit_quote_usm.the_geom,
            pyarchinit_quote_usm.unita_tipo_q,
            us_table.id_us,
            us_table.sito,
            us_table.area,
            us_table.us,
            us_table.struttura,
            us_table.d_stratigrafica,
            us_table.d_interpretativa,
            us_table.descrizione,
            us_table.interpretazione,
            us_table.rapporti,
            us_table.periodo_iniziale,
            us_table.fase_iniziale,
            us_table.periodo_finale,
            us_table.fase_finale,
            us_table.anno_scavo,
            us_table.cont_per
        FROM pyarchinit_quote_usm
        JOIN us_table ON 
            pyarchinit_quote_usm.sito_q = us_table.sito AND 
            pyarchinit_quote_usm.area_q = us_table.area AND 
            pyarchinit_quote_usm.us_q = us_table.us AND 
            pyarchinit_quote_usm.unita_tipo_q = us_table.unita_tipo
    """)
    print("   ✓ Creata view pyarchinit_quote_usm_view")
    
    # Commit
    conn.commit()
    
    # 5. Verifica
    print("\n4. Verifica finale...")
    
    # Verifica tabelle
    for table in ['pyarchinit_quote', 'pyarchinit_quote_usm']:
        cursor.execute(f"SELECT type FROM sqlite_master WHERE name='{table}'")
        result = cursor.fetchone()
        if result:
            print(f"   ✓ {table}: {result[0]}")
    
    # Verifica view
    for view in ['pyarchinit_quote_view', 'pyarchinit_quote_usm_view']:
        cursor.execute(f"SELECT type FROM sqlite_master WHERE name='{view}'")
        result = cursor.fetchone()
        if result:
            print(f"   ✓ {view}: {result[0]}")
    
    conn.close()
    
    print(f"\n{'='*60}")
    print("✓ Allineamento completato!")
    print(f"{'='*60}")


def process_all_databases():
    """Processa tutti i database"""
    databases = [
        "/Users/enzo/pyarchinit/pyarchinit_DB_folder/ktm24.sqlite",
        "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/resources/dbfiles/pyarchinit.sqlite",
        "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/resources/dbfiles/pyarchinit_db.sqlite"
    ]
    
    for db_path in databases:
        if os.path.exists(db_path):
            try:
                align_quote_tables(db_path)
            except Exception as e:
                print(f"\n✗ Errore processando {os.path.basename(db_path)}: {e}")
        else:
            print(f"\n⚠ Database non trovato: {db_path}")


if __name__ == "__main__":
    process_all_databases()