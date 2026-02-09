#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per aggiungere campi mancanti e trigger ai database SQLite
per allinearli completamente con PostgreSQL
"""

import sqlite3
import os
from datetime import datetime

def add_missing_fields_and_triggers(db_path):
    """Aggiunge campi e trigger mancanti"""
    
    print(f"\n{'='*60}")
    print(f"AGGIUNTA CAMPI E TRIGGER: {os.path.basename(db_path)}")
    print(f"{'='*60}\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. AGGIUNGI CAMPI MANCANTI A us_table
    print("1. Aggiunta campi mancanti a us_table...")
    
    # Verifica quali campi mancano
    cursor.execute("PRAGMA table_info(us_table)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    missing_fields = {
        'doc_usv': "TEXT DEFAULT ''",
        'version_number': "INTEGER DEFAULT 1",
        'editing_by': "TEXT",
        'editing_since': "TEXT",  # SQLite non ha TIMESTAMP nativo
        'last_modified_by': "TEXT DEFAULT 'system'",
        'last_modified_timestamp': "TEXT DEFAULT CURRENT_TIMESTAMP"
    }
    
    for field_name, field_type in missing_fields.items():
        if field_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE us_table ADD COLUMN {field_name} {field_type}")
                print(f"   ✓ Aggiunto campo {field_name}")
            except Exception as e:
                print(f"   ✗ Errore aggiungendo {field_name}: {e}")
    
    # 2. VERIFICA POSIZIONE doc_usv (dovrebbe essere dopo rapporti2)
    # Non possiamo riordinare colonne in SQLite, ma verifichiamo che ci sia
    cursor.execute("PRAGMA table_info(us_table)")
    columns = cursor.fetchall()
    col_names = [col[1] for col in columns]
    
    if 'doc_usv' in col_names and 'rapporti2' in col_names:
        doc_idx = col_names.index('doc_usv')
        rapporti2_idx = col_names.index('rapporti2')
        print(f"\n   Posizione campi:")
        print(f"   - rapporti2: posizione {rapporti2_idx}")
        print(f"   - doc_usv: posizione {doc_idx}")
    
    # 3. AGGIUNGI TRIGGER create_doc
    print("\n2. Aggiunta trigger create_doc...")
    
    # Prima elimina se esiste
    cursor.execute("DROP TRIGGER IF EXISTS create_doc_update")
    cursor.execute("DROP TRIGGER IF EXISTS create_doc_insert")
    
    # Trigger per UPDATE
    try:
        cursor.execute("""
            CREATE TRIGGER create_doc_update
            AFTER UPDATE OF d_interpretativa ON us_table
            FOR EACH ROW
            WHEN NEW.d_interpretativa != OLD.d_interpretativa
            BEGIN
                UPDATE us_table
                SET doc_usv = NEW.d_interpretativa
                WHERE sito = NEW.sito 
                  AND area = NEW.area 
                  AND us = NEW.us 
                  AND unita_tipo = 'DOC';
            END;
        """)
        print("   ✓ Creato trigger create_doc_update")
    except Exception as e:
        print(f"   ✗ Errore creando create_doc_update: {e}")
    
    # Trigger per INSERT
    try:
        cursor.execute("""
            CREATE TRIGGER create_doc_insert
            AFTER INSERT ON us_table
            FOR EACH ROW
            WHEN (NEW.d_interpretativa IS NULL OR NEW.d_interpretativa = '')
            BEGIN
                UPDATE us_table
                SET d_interpretativa = (
                    SELECT doc_usv FROM us_table 
                    WHERE sito = NEW.sito 
                      AND area = NEW.area 
                      AND us = NEW.us 
                      AND unita_tipo = 'DOC'
                    LIMIT 1
                )
                WHERE rowid = NEW.rowid;
            END;
        """)
        print("   ✓ Creato trigger create_doc_insert")
    except Exception as e:
        print(f"   ✗ Errore creando create_doc_insert: {e}")
    
    # 4. AGGIUNGI ALTRI TRIGGER IMPORTANTI
    print("\n3. Aggiunta altri trigger...")
    
    # Trigger per aggiornamento last_modified
    try:
        cursor.execute("DROP TRIGGER IF EXISTS update_last_modified")
        cursor.execute("""
            CREATE TRIGGER update_last_modified
            AFTER UPDATE ON us_table
            FOR EACH ROW
            BEGIN
                UPDATE us_table
                SET last_modified_timestamp = datetime('now')
                WHERE rowid = NEW.rowid;
            END;
        """)
        print("   ✓ Creato trigger update_last_modified")
    except Exception as e:
        print(f"   ✗ Errore creando update_last_modified: {e}")
    
    # 5. VERIFICA FINALE
    print("\n4. Verifica finale...")
    
    # Verifica campi
    cursor.execute("PRAGMA table_info(us_table)")
    columns = cursor.fetchall()
    col_names = [col[1] for col in columns]
    
    critical_fields = ['doc_usv', 'rapporti2', 'version_number', 
                      'last_modified_by', 'last_modified_timestamp']
    
    print("\n   Campi critici:")
    for field in critical_fields:
        if field in col_names:
            print(f"   ✓ {field} presente")
        else:
            print(f"   ✗ {field} MANCANTE")
    
    # Verifica trigger
    cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND tbl_name='us_table'")
    triggers = [row[0] for row in cursor.fetchall()]
    
    print("\n   Trigger su us_table:")
    for trigger in triggers:
        print(f"   ✓ {trigger}")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print("✓ COMPLETATO!")
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
                add_missing_fields_and_triggers(db_path)
            except Exception as e:
                print(f"\n✗ Errore processando {os.path.basename(db_path)}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"\n⚠ Database non trovato: {db_path}")


if __name__ == "__main__":
    process_all_databases()