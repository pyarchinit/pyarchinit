#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per correggere i campi geometrici nelle tabelle ripristinate
"""

import sqlite3
import os
from datetime import datetime

def fix_geometry_fields(db_path):
    """Corregge i campi geometrici nelle tabelle spatiali"""
    
    print(f"\n{'='*60}")
    print(f"Correzione campi geometrici: {os.path.basename(db_path)}")
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
            print("✗ Impossibile caricare spatialite")
            return False
    
    cursor = conn.cursor()
    
    # Inizializza spatialite se necessario
    cursor.execute("SELECT InitSpatialMetaData(1)")
    
    # Definizione delle tabelle e dei loro tipi geometrici
    geometry_tables = {
        'pyunitastratigrafiche': ('the_geom', 'MULTIPOLYGON'),
        'pyunitastratigrafiche_usm': ('the_geom', 'MULTIPOLYGON'),
        'pyarchinit_quote': ('the_geom', 'POINT'),
        'pyarchinit_quote_usm': ('the_geom', 'POINT'),
        'pyarchinit_us_negative_doc': ('the_geom', 'MULTIPOLYGON'),
        'pyarchinit_reperti': ('the_geom', 'POINT'),
        'pyarchinit_siti_polygonal': ('the_geom', 'MULTIPOLYGON'),
        'pyarchinit_documentazione': ('the_geom', 'POINT'),
        'pyarchinit_tafonomia': ('the_geom', 'POINT'),
        'pyarchinit_individui': ('the_geom', 'POINT')
    }
    
    # Ottieni SRID dal database (di solito 3004 per Italia)
    cursor.execute("SELECT srid FROM geometry_columns LIMIT 1")
    result = cursor.fetchone()
    srid = result[0] if result else 3004  # Default SRID Italia
    print(f"SRID rilevato: {srid}\n")
    
    for table_name, (geom_col, geom_type) in geometry_tables.items():
        # Verifica se la tabella esiste
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))
        
        if not cursor.fetchone():
            print(f"⚠ Tabella {table_name} non trovata")
            continue
        
        # Verifica se la colonna geometrica è già registrata correttamente
        cursor.execute("""
            SELECT * FROM geometry_columns 
            WHERE f_table_name = ? AND f_geometry_column = ?
        """, (table_name, geom_col))
        
        if cursor.fetchone():
            print(f"✓ {table_name}.{geom_col} già registrata correttamente")
            continue
        
        # Controlla se la colonna esiste nella tabella
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [(col[1], col[2]) for col in cursor.fetchall()]
        
        has_geom_column = False
        needs_recovery = False
        
        for col_name, col_type in columns:
            if col_name == geom_col:
                has_geom_column = True
                if col_type != 'BLOB':  # Spatialite usa BLOB per geometrie
                    needs_recovery = True
                break
        
        if not has_geom_column:
            print(f"✗ {table_name} non ha colonna {geom_col}")
            continue
        
        if needs_recovery:
            print(f"⚠ {table_name}.{geom_col} necessita recupero (tipo attuale: {col_type})")
            
            # Crea una nuova tabella temporanea con struttura corretta
            temp_table = f"{table_name}_temp"
            
            # Ottieni struttura della tabella
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            
            # Crea lista colonne senza the_geom
            col_defs = []
            col_names = []
            for col in columns_info:
                if col[1] != geom_col:
                    col_type = col[2]
                    if col[3]:  # NOT NULL
                        col_type += " NOT NULL"
                    if col[4]:  # Default value
                        col_type += f" DEFAULT {col[4]}"
                    col_defs.append(f"{col[1]} {col_type}")
                    col_names.append(col[1])
            
            # Crea tabella temporanea
            create_sql = f"CREATE TABLE {temp_table} ({', '.join(col_defs)})"
            cursor.execute(create_sql)
            
            # Copia i dati non geometrici
            copy_sql = f"INSERT INTO {temp_table} ({', '.join(col_names)}) SELECT {', '.join(col_names)} FROM {table_name}"
            cursor.execute(copy_sql)
            
            # Aggiungi colonna geometrica
            cursor.execute(f"SELECT AddGeometryColumn('{temp_table}', '{geom_col}', {srid}, '{geom_type}', 'XY')")
            
            # Elimina tabella originale e rinomina
            cursor.execute(f"DROP TABLE {table_name}")
            cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {table_name}")
            
            print(f"✓ {table_name}.{geom_col} ricreata come {geom_type}")
        else:
            # Registra la colonna geometrica esistente
            try:
                cursor.execute(f"SELECT RecoverGeometryColumn('{table_name}', '{geom_col}', {srid}, '{geom_type}', 'XY')")
                print(f"✓ {table_name}.{geom_col} recuperata come {geom_type}")
            except Exception as e:
                print(f"✗ Errore recuperando {table_name}.{geom_col}: {e}")
    
    # Crea indici spaziali
    print("\nCreazione indici spaziali...")
    cursor.execute("""
        SELECT f_table_name, f_geometry_column 
        FROM geometry_columns
    """)
    
    for table, geom_col in cursor.fetchall():
        try:
            cursor.execute(f"SELECT CreateSpatialIndex('{table}', '{geom_col}')")
            print(f"✓ Indice spaziale creato per {table}.{geom_col}")
        except:
            # Indice potrebbe già esistere
            pass
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print("✓ Correzione completata!")
    print(f"{'='*60}\n")
    
    return True

if __name__ == "__main__":
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/ktm24.sqlite"
    fix_geometry_fields(db_path)