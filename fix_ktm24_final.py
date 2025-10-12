#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script finale per sistemare ktm24.sqlite
- Converte pyarchinit_quote e pyarchinit_quote_usm da tabelle a view
- Ripristina tomba_table
- Corregge campo area in tomba_table
"""

import sqlite3
import os
from datetime import datetime

def final_fix_ktm24(db_path):
    """Sistema definitivamente il database ktm24"""
    
    print(f"\n{'='*60}")
    print(f"Correzione finale database: {os.path.basename(db_path)}")
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
    
    # 1. Ripristina tomba_table se mancante
    print("1. Verifica e ripristino tomba_table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tomba_table'")
    if not cursor.fetchone():
        # Cerca backup
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE 'tomba_table_backup_%'
            ORDER BY name DESC LIMIT 1
        """)
        backup = cursor.fetchone()
        if backup:
            backup_name = backup[0]
            try:
                cursor.execute(f"CREATE TABLE tomba_table AS SELECT * FROM {backup_name}")
                print(f"   ✓ Ripristinata tomba_table da {backup_name}")
            except Exception as e:
                print(f"   ✗ Errore: {e}")
        else:
            print("   ✗ Nessun backup trovato per tomba_table")
    else:
        print("   ✓ tomba_table già presente")
    
    # 2. Correggi campo area in tomba_table (approccio semplificato)
    print("\n2. Correzione campo area in tomba_table...")
    try:
        cursor.execute("PRAGMA table_info(tomba_table)")
        columns = cursor.fetchall()
        
        area_type = None
        for col in columns:
            if col[1] == 'area':
                area_type = col[2]
                break
        
        if area_type and area_type != 'TEXT':
            print(f"   Campo area è {area_type}, conversione necessaria")
            
            # Disabilita trigger temporaneamente
            cursor.execute("PRAGMA foreign_keys = OFF")
            cursor.execute("PRAGMA triggers = OFF")
            
            # Crea nuova colonna temporanea
            cursor.execute("ALTER TABLE tomba_table ADD COLUMN area_temp TEXT")
            
            # Copia i dati
            cursor.execute("UPDATE tomba_table SET area_temp = CAST(area AS TEXT)")
            
            # Ora dobbiamo ricreare la tabella senza la colonna area originale
            # Ottieni lista colonne senza 'area'
            cols_without_area = [col[1] for col in columns if col[1] != 'area']
            cols_without_area.append('area_temp')
            
            # Crea tabella temporanea
            cursor.execute(f"""
                CREATE TABLE tomba_table_fixed AS 
                SELECT {', '.join(cols_without_area)} FROM tomba_table
            """)
            
            # Rinomina area_temp ad area nella nuova tabella  
            # Prima ottieni lo schema della nuova tabella
            cursor.execute("PRAGMA table_info(tomba_table_fixed)")
            new_columns = cursor.fetchall()
            
            # Costruisci lista colonne con area_temp rinominato
            final_cols = []
            select_cols = []
            for col in new_columns:
                if col[1] == 'area_temp':
                    final_cols.append('area TEXT')
                    select_cols.append('area_temp as area')
                else:
                    col_def = f"{col[1]} {col[2]}"
                    if col[3]:  # NOT NULL
                        col_def += " NOT NULL"
                    if col[4]:  # Default
                        col_def += f" DEFAULT {col[4]}"
                    final_cols.append(col_def)
                    select_cols.append(col[1])
            
            # Crea tabella finale
            cursor.execute(f"DROP TABLE IF EXISTS tomba_table_final")
            cursor.execute(f"""
                CREATE TABLE tomba_table_final AS
                SELECT {', '.join(select_cols)} FROM tomba_table_fixed
            """)
            
            # Sostituisci tabella originale
            cursor.execute("DROP TABLE tomba_table")
            cursor.execute("DROP TABLE tomba_table_fixed")
            cursor.execute("ALTER TABLE tomba_table_final RENAME TO tomba_table")
            
            # Riabilita trigger
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("PRAGMA triggers = ON")
            
            print("   ✓ Campo area convertito a TEXT")
            
    except Exception as e:
        print(f"   ✗ Errore: {e}")
        # Riabilita trigger in caso di errore
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("PRAGMA triggers = ON")
    
    # 3. Converti pyarchinit_quote e pyarchinit_quote_usm da tabelle a view
    print("\n3. Conversione tabelle quote in view...")
    
    quote_views = [
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
        ''')
    ]
    
    for view_name, create_sql in quote_views:
        # Verifica se esiste come tabella
        cursor.execute(f"""
            SELECT type FROM sqlite_master 
            WHERE name='{view_name}'
        """)
        result = cursor.fetchone()
        
        if result and result[0] == 'table':
            try:
                # Drop tabella
                cursor.execute(f"DROP TABLE {view_name}")
                # Crea come view
                cursor.execute(create_sql)
                print(f"   ✓ Convertita {view_name} da tabella a view")
            except Exception as e:
                print(f"   ✗ Errore convertendo {view_name}: {e}")
        elif result and result[0] == 'view':
            print(f"   ✓ {view_name} già una view")
        else:
            # Non esiste, crea
            try:
                cursor.execute(create_sql)
                print(f"   ✓ Creata view {view_name}")
            except Exception as e:
                print(f"   ✗ Errore creando {view_name}: {e}")
    
    # 4. Verifica finale
    print("\n4. Verifica finale...")
    
    # Controlla tipi di campo
    cursor.execute("PRAGMA table_info(tomba_table)")
    for col in cursor.fetchall():
        if col[1] == 'area':
            print(f"   tomba_table.area: {col[2]}")
    
    # Controlla che siano view
    for view_name in ['pyarchinit_quote', 'pyarchinit_quote_usm']:
        cursor.execute(f"SELECT type FROM sqlite_master WHERE name='{view_name}'")
        result = cursor.fetchone()
        if result:
            print(f"   {view_name}: {result[0]}")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print("✓ Correzione finale completata!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/ktm24.sqlite"
    final_fix_ktm24(db_path)