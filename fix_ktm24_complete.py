#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script completo per sistemare il database ktm24.sqlite
Corregge sia i tipi di campo che le geometrie
"""

import sqlite3
import os
from datetime import datetime
import shutil

def fix_ktm24_database(db_path):
    """Sistema completamente il database ktm24"""
    
    print(f"\n{'='*60}")
    print(f"Correzione completa database: {os.path.basename(db_path)}")
    print(f"{'='*60}\n")
    
    # Crea backup
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    print(f"✓ Backup creato: {backup_path}\n")
    
    conn = sqlite3.connect(db_path)
    conn.enable_load_extension(True)
    
    # Carica spatialite
    try:
        conn.load_extension("mod_spatialite")
        print("✓ Spatialite caricato\n")
    except:
        try:
            conn.load_extension("mod_spatialite.so")
            print("✓ Spatialite caricato\n")
        except:
            print("✗ Impossibile caricare spatialite")
            return False
    
    cursor = conn.cursor()
    
    # 1. Fix campo area in tomba_table
    print("1. Correzione campo area in tomba_table...")
    try:
        cursor.execute("PRAGMA table_info(tomba_table)")
        columns = cursor.fetchall()
        
        area_col_type = None
        for col in columns:
            if col[1] == 'area':
                area_col_type = col[2]
                break
        
        if area_col_type and area_col_type != 'TEXT':
            print(f"   Campo area è {area_col_type}, correzione in corso...")
            
            # Ottieni lista completa delle colonne
            col_names = [col[1] for col in columns]
            col_defs = []
            
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                
                # Correggi il tipo per area
                if col_name == 'area':
                    col_type = 'TEXT'
                
                # Aggiungi constraints
                if col[3]:  # NOT NULL
                    col_type += " NOT NULL"
                if col[4]:  # Default value
                    col_type += f" DEFAULT {col[4]}"
                    
                col_defs.append(f"{col_name} {col_type}")
            
            # Crea nuova tabella
            cursor.execute(f"""
                CREATE TABLE tomba_table_new (
                    {', '.join(col_defs)}
                )
            """)
            
            # Copia dati
            cursor.execute(f"""
                INSERT INTO tomba_table_new ({', '.join(col_names)})
                SELECT {', '.join(col_names)} FROM tomba_table
            """)
            
            # Sostituisci tabella
            cursor.execute("DROP TABLE tomba_table")
            cursor.execute("ALTER TABLE tomba_table_new RENAME TO tomba_table")
            
            print("   ✓ Campo area convertito a TEXT")
            
    except Exception as e:
        print(f"   ✗ Errore: {e}")
    
    # 2. Fix pyarchinit_quote e pyarchinit_quote_usm 
    print("\n2. Ripristino tabelle quote mancanti...")
    tables_to_restore = [
        ('pyarchinit_quote', 'pyarchinit_quote_backup_1760015737'),
        ('pyarchinit_quote_usm', 'pyarchinit_quote_usm_backup_1760015738')
    ]
    
    for table_name, backup_name in tables_to_restore:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not cursor.fetchone():
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{backup_name}'")
            if cursor.fetchone():
                try:
                    cursor.execute(f"CREATE TABLE {table_name} AS SELECT * FROM {backup_name}")
                    print(f"   ✓ Ripristinata {table_name}")
                except Exception as e:
                    print(f"   ✗ Errore ripristinando {table_name}: {e}")
    
    # 3. Drop e ricrea le view senza CAST
    print("\n3. Ricreazione view senza CAST...")
    views_to_recreate = [
        ('pyarchinit_quote', '''
            CREATE VIEW pyarchinit_quote AS
            SELECT 
                sito,
                area,
                us,
                unita_tipo,
                quota_min,
                quota_max,
                the_geom
            FROM us_table
            WHERE quota_min IS NOT NULL OR quota_max IS NOT NULL
        '''),
        ('pyarchinit_quote_usm', '''
            CREATE VIEW pyarchinit_quote_usm AS
            SELECT 
                sito,
                area,
                us,
                unita_tipo,
                quota_min_usm,
                quota_max_usm,
                the_geom
            FROM us_table
            WHERE unita_tipo = 'USM' AND (quota_min_usm IS NOT NULL OR quota_max_usm IS NOT NULL)
        '''),
        ('pyunitastratigrafiche', '''
            CREATE VIEW pyunitastratigrafiche AS
            SELECT 
                id_us,
                sito,
                area,
                us,
                d_stratigrafica,
                d_interpretativa,
                descrizione,
                interpretazione,
                periodo_iniziale,
                fase_iniziale,
                periodo_finale,
                fase_finale,
                scavato,
                attivita,
                anno_scavo,
                metodo_di_scavo,
                inclusi,
                campioni,
                rapporti,
                organici,
                inorganici,
                data_schedatura,
                schedatore,
                formazione,
                stato_di_conservazione,
                colore,
                consistenza,
                struttura,
                cont_per,
                order_layer,
                the_geom
            FROM us_table
            WHERE unita_tipo = 'US'
        '''),
        ('pyunitastratigrafiche_usm', '''
            CREATE VIEW pyunitastratigrafiche_usm AS
            SELECT 
                id_us,
                sito,
                area,
                us,
                unita_tipo,
                d_stratigrafica,
                d_interpretativa,
                descrizione,
                interpretazione,
                periodo_iniziale,
                fase_iniziale,
                periodo_finale,
                fase_finale,
                scavato,
                attivita,
                anno_scavo,
                metodo_di_scavo,
                inclusi,
                campioni,
                rapporti,
                organici,
                inorganici,
                data_schedatura,
                schedatore,
                formazione,
                stato_di_conservazione,
                colore,
                consistenza,
                struttura,
                cont_per,
                order_layer,
                the_geom
            FROM us_table
            WHERE unita_tipo = 'USM'
        ''')
    ]
    
    for view_name, create_sql in views_to_recreate:
        try:
            # Drop esistente
            cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
            # Ricrea
            cursor.execute(create_sql)
            print(f"   ✓ Ricreata view {view_name}")
        except Exception as e:
            print(f"   ✗ Errore con view {view_name}: {e}")
    
    # 4. Registra le geometrie
    print("\n4. Registrazione colonne geometriche...")
    
    # Ottieni SRID
    cursor.execute("SELECT srid FROM geometry_columns LIMIT 1")
    result = cursor.fetchone()
    srid = result[0] if result else 32640
    print(f"   SRID rilevato: {srid}")
    
    geometry_tables = {
        'pyunitastratigrafiche': ('the_geom', 'MULTIPOLYGON'),
        'pyunitastratigrafiche_usm': ('the_geom', 'MULTIPOLYGON'),
        'pyarchinit_quote': ('the_geom', 'POINT'),
        'pyarchinit_quote_usm': ('the_geom', 'POINT'),
        'pyarchinit_us_negative_doc': ('the_geom', 'MULTIPOLYGON')
    }
    
    for table_name, (geom_col, geom_type) in geometry_tables.items():
        # Verifica se la tabella esiste
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if cursor.fetchone():
            # Verifica se già registrata
            cursor.execute(f"""
                SELECT * FROM geometry_columns 
                WHERE f_table_name = '{table_name}' AND f_geometry_column = '{geom_col}'
            """)
            
            if not cursor.fetchone():
                try:
                    cursor.execute(f"SELECT RecoverGeometryColumn('{table_name}', '{geom_col}', {srid}, '{geom_type}', 'XY')")
                    print(f"   ✓ Registrata geometria {table_name}.{geom_col}")
                except Exception as e:
                    print(f"   ✗ Errore registrando {table_name}.{geom_col}: {e}")
    
    # 5. Verifica finale
    print("\n5. Verifica finale...")
    conn.commit()
    
    # Verifica campi
    cursor.execute("PRAGMA table_info(us_table)")
    for col in cursor.fetchall():
        if col[1] in ['area', 'us']:
            print(f"   us_table.{col[1]}: {col[2]}")
    
    cursor.execute("PRAGMA table_info(tomba_table)")
    for col in cursor.fetchall():
        if col[1] == 'area':
            print(f"   tomba_table.{col[1]}: {col[2]}")
    
    # Verifica view
    for view_name in ['pyarchinit_quote', 'pyunitastratigrafiche']:
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='view' AND name='{view_name}'")
        result = cursor.fetchone()
        if result and 'CAST' in result[0]:
            print(f"   ⚠ View {view_name} contiene ancora CAST")
        else:
            print(f"   ✓ View {view_name} OK (nessun CAST)")
    
    conn.close()
    
    print(f"\n{'='*60}")
    print("✓ Correzione completata!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/ktm24.sqlite"
    fix_ktm24_database(db_path)