#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script aggressivo per correggere completamente i database PyArchInit
Forza la conversione di tutti i campi area/us a TEXT
"""

import sqlite3
import os
from datetime import datetime
import shutil

def aggressive_fix_database(db_path):
    """Correzione aggressiva del database"""
    
    print(f"\n{'='*60}")
    print(f"CORREZIONE AGGRESSIVA: {os.path.basename(db_path)}")
    print(f"{'='*60}\n")
    
    # Crea backup
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    print(f"✓ Backup creato: {os.path.basename(backup_path)}\n")
    
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
    
    # Disabilita tutti i constraints
    cursor.execute("PRAGMA foreign_keys = OFF")
    cursor.execute("PRAGMA legacy_alter_table = ON")
    cursor.execute("PRAGMA defer_foreign_keys = ON")
    
    # 1. DROP TUTTE LE VIEW CHE POTREBBERO INTERFERIRE
    print("1. Rimozione view esistenti...")
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='view' AND (
            name LIKE 'pyarchinit_%' OR 
            name LIKE 'pyunita%'
        )
    """)
    views = cursor.fetchall()
    for view in views:
        try:
            cursor.execute(f"DROP VIEW IF EXISTS {view[0]}")
            print(f"   ✓ Rimossa view {view[0]}")
        except:
            pass
    
    # 2. DROP TABELLE CHE SONO DIVENTATE VIEW
    tables_that_should_be_views = [
        'pyarchinit_quote',
        'pyarchinit_quote_usm',
        'pyunitastratigrafiche',
        'pyunitastratigrafiche_usm'
    ]
    
    for table in tables_that_should_be_views:
        cursor.execute(f"SELECT type FROM sqlite_master WHERE name='{table}'")
        result = cursor.fetchone()
        if result and result[0] == 'table':
            cursor.execute(f"DROP TABLE {table}")
            print(f"   ✓ Rimossa tabella {table} (diventerà view)")
    
    # 3. CORREGGI US_TABLE
    print("\n2. Correzione us_table...")
    if table_exists(cursor, 'us_table'):
        cursor.execute("PRAGMA table_info(us_table)")
        columns = cursor.fetchall()
        
        area_type = None
        us_type = None
        
        for col in columns:
            if col[1] == 'area':
                area_type = col[2]
            elif col[1] == 'us':
                us_type = col[2]
        
        if area_type != 'TEXT' or us_type != 'TEXT':
            print(f"   area: {area_type}, us: {us_type} - Correzione necessaria")
            fix_us_table(cursor)
        else:
            print("   ✓ us_table già corretta")
    
    # 4. CORREGGI TUTTE LE ALTRE TABELLE
    print("\n3. Correzione altre tabelle...")
    tables_to_fix = [
        'tomba_table',
        'inventario_materiali_table',
        'pottery_table',
        'campioni_table',
        'documentazione_table',
        'lineeriferimento_table',
        'ripartizioni_spaziali_table',
        'struttura_table',
        'sondaggi_table',
        'sezioni_table',
        'quota_table'
    ]
    
    for table_name in tables_to_fix:
        if table_exists(cursor, table_name):
            fix_table_fields(cursor, table_name)
    
    # 5. RICREA LE VIEW CORRETTE
    print("\n4. Creazione view corrette...")
    create_correct_views(cursor)
    
    # 6. RICREA VIEW CHE USANO CAST
    print("\n5. Correzione view con CAST...")
    fix_views_with_cast(cursor)
    
    # Commit
    conn.commit()
    
    # 7. VERIFICA FINALE
    print("\n6. Verifica finale...")
    verify_final_state(cursor)
    
    conn.close()
    
    print(f"\n{'='*60}")
    print("✓ CORREZIONE AGGRESSIVA COMPLETATA!")
    print(f"{'='*60}")


def table_exists(cursor, table_name):
    """Verifica se una tabella esiste"""
    cursor.execute(f"""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='{table_name}'
    """)
    return cursor.fetchone() is not None


def fix_us_table(cursor):
    """Corregge us_table forzando area e us a TEXT"""
    try:
        # Salva i dati
        cursor.execute("CREATE TABLE us_table_backup AS SELECT * FROM us_table")
        
        # Ottieni struttura colonne
        cursor.execute("PRAGMA table_info(us_table)")
        columns = cursor.fetchall()
        
        # Costruisci nuova struttura con area e us come TEXT
        col_defs = []
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            
            # Forza TEXT per area e us
            if col_name in ['area', 'us']:
                col_type = 'TEXT'
            
            # Primary key
            if col[5]:  # is PK
                col_defs.append(f"{col_name} {col_type} PRIMARY KEY")
            else:
                col_def = f"{col_name} {col_type}"
                if col[3]:  # NOT NULL
                    col_def += " NOT NULL"
                if col[4]:  # Default
                    col_def += f" DEFAULT {col[4]}"
                col_defs.append(col_def)
        
        # Ricrea tabella
        cursor.execute("DROP TABLE us_table")
        cursor.execute(f"CREATE TABLE us_table ({', '.join(col_defs)})")
        
        # Ripristina dati
        col_names = [col[1] for col in columns]
        cursor.execute(f"""
            INSERT INTO us_table ({', '.join(col_names)})
            SELECT {', '.join(col_names)} FROM us_table_backup
        """)
        
        cursor.execute("DROP TABLE us_table_backup")
        print("   ✓ us_table corretta")
        
    except Exception as e:
        print(f"   ✗ Errore correggendo us_table: {e}")
        # Ripristina se fallisce
        try:
            cursor.execute("DROP TABLE IF EXISTS us_table")
            cursor.execute("ALTER TABLE us_table_backup RENAME TO us_table")
        except:
            pass


def fix_table_fields(cursor, table_name):
    """Corregge i campi area/us in una tabella"""
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        needs_fix = False
        for col in columns:
            if col[1] in ['area', 'us'] and col[2] != 'TEXT':
                needs_fix = True
                break
        
        if not needs_fix:
            print(f"   ✓ {table_name} già corretta")
            return
        
        print(f"   Correzione {table_name}...")
        
        # Salva dati
        cursor.execute(f"CREATE TABLE {table_name}_backup AS SELECT * FROM {table_name}")
        
        # Costruisci nuova struttura
        col_defs = []
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            
            # Forza TEXT per area e us
            if col_name in ['area', 'us']:
                col_type = 'TEXT'
            
            # Primary key
            if col[5]:  # is PK
                col_defs.append(f"{col_name} {col_type} PRIMARY KEY")
            else:
                col_def = f"{col_name} {col_type}"
                if col[3]:  # NOT NULL
                    col_def += " NOT NULL"
                if col[4]:  # Default
                    col_def += f" DEFAULT {col[4]}"
                col_defs.append(col_def)
        
        # Ricrea tabella
        cursor.execute(f"DROP TABLE {table_name}")
        cursor.execute(f"CREATE TABLE {table_name} ({', '.join(col_defs)})")
        
        # Ripristina dati
        col_names = [col[1] for col in columns]
        cursor.execute(f"""
            INSERT INTO {table_name} ({', '.join(col_names)})
            SELECT {', '.join(col_names)} FROM {table_name}_backup
        """)
        
        cursor.execute(f"DROP TABLE {table_name}_backup")
        print(f"   ✓ {table_name} corretta")
        
    except Exception as e:
        print(f"   ✗ Errore correggendo {table_name}: {e}")
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            cursor.execute(f"ALTER TABLE {table_name}_backup RENAME TO {table_name}")
        except:
            pass


def create_correct_views(cursor):
    """Crea le view corrette senza CAST"""
    views = [
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
            SELECT * FROM us_table WHERE unita_tipo = 'US'
        '''),
        ('pyunitastratigrafiche_usm', '''
            CREATE VIEW pyunitastratigrafiche_usm AS
            SELECT * FROM us_table WHERE unita_tipo = 'USM'
        ''')
    ]
    
    for view_name, create_sql in views:
        try:
            cursor.execute(create_sql)
            print(f"   ✓ Creata view {view_name}")
        except Exception as e:
            print(f"   ✗ Errore creando {view_name}: {e}")


def fix_views_with_cast(cursor):
    """Corregge le view che usano CAST"""
    # Trova view con CAST
    cursor.execute("""
        SELECT name, sql FROM sqlite_master 
        WHERE type='view' AND sql LIKE '%CAST%'
    """)
    
    views = cursor.fetchall()
    for view_name, view_sql in views:
        try:
            # Rimuovi tutti i CAST(... AS INTEGER)
            new_sql = view_sql
            
            # Pattern per CAST(campo AS INTEGER)
            import re
            cast_pattern = r'CAST\s*\(\s*(\w+)\s+AS\s+INTEGER\s*\)\s+as\s+(\w+)'
            new_sql = re.sub(cast_pattern, r'\1 as \2', new_sql)
            
            # Pattern per CAST senza alias
            cast_pattern2 = r'CAST\s*\(\s*(\w+)\s+AS\s+INTEGER\s*\)'
            new_sql = re.sub(cast_pattern2, r'\1', new_sql)
            
            if new_sql != view_sql:
                # Ricrea view
                cursor.execute(f"DROP VIEW {view_name}")
                cursor.execute(new_sql)
                print(f"   ✓ Corretta view {view_name}")
        except Exception as e:
            print(f"   ✗ Errore correggendo view {view_name}: {e}")


def verify_final_state(cursor):
    """Verifica lo stato finale"""
    # Verifica tabelle
    critical_tables = ['us_table', 'tomba_table', 'inventario_materiali_table', 'pottery_table']
    
    for table in critical_tables:
        if table_exists(cursor, table):
            cursor.execute(f"PRAGMA table_info({table})")
            for col in cursor.fetchall():
                if col[1] in ['area', 'us']:
                    status = "✓" if col[2] == 'TEXT' else "✗"
                    print(f"   {status} {table}.{col[1]}: {col[2]}")
    
    # Verifica view con CAST
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='view' AND sql LIKE '%CAST%'
    """)
    
    cast_views = cursor.fetchall()
    if cast_views:
        print("\n   View con CAST rimanenti:")
        for view in cast_views:
            print(f"   ⚠ {view[0]}")


def process_databases():
    """Processa tutti i database"""
    databases = [
        "/Users/enzo/pyarchinit/pyarchinit_DB_folder/ktm24.sqlite",
        "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/resources/dbfiles/pyarchinit.sqlite",
        "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/resources/dbfiles/pyarchinit_db.sqlite"
    ]
    
    for db_path in databases:
        if os.path.exists(db_path):
            try:
                aggressive_fix_database(db_path)
            except Exception as e:
                print(f"\n✗ ERRORE CRITICO in {os.path.basename(db_path)}: {e}")
        else:
            print(f"\n⚠ Database non trovato: {db_path}")


if __name__ == "__main__":
    process_databases()