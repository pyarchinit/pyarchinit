#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per aggiornare la lunghezza del campo sigla nella tabella pyarchinit_thesaurus_sigle
"""

import sqlite3
import os
import sys

def update_sigla_length_sqlite(db_path):
    """Aggiorna la lunghezza del campo sigla per SQLite."""
    print(f"Aggiornamento database SQLite: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # SQLite non supporta ALTER COLUMN, quindi dobbiamo ricreare la tabella
        print("Creazione tabella temporanea con nuovo schema...")
        
        # Crea tabella temporanea con la nuova struttura
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pyarchinit_thesaurus_sigle_new (
                id_thesaurus_sigle INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_tabella TEXT,
                sigla VARCHAR(100),  -- Aumentato da 3 a 100
                sigla_estesa TEXT,
                tipologia_sigla VARCHAR(100),
                lingua VARCHAR(10),
                order_layer INTEGER DEFAULT 0,
                id_parent INTEGER,
                parent_sigla VARCHAR(100),
                hierarchy_level INTEGER DEFAULT 0
            )
        """)
        
        # Copia i dati dalla vecchia tabella
        print("Copia dei dati esistenti...")
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle_new 
            SELECT * FROM pyarchinit_thesaurus_sigle
        """)
        
        # Elimina la vecchia tabella
        print("Rimozione vecchia tabella...")
        cursor.execute("DROP TABLE pyarchinit_thesaurus_sigle")
        
        # Rinomina la nuova tabella
        print("Rinomina nuova tabella...")
        cursor.execute("ALTER TABLE pyarchinit_thesaurus_sigle_new RENAME TO pyarchinit_thesaurus_sigle")
        
        # Ricrea gli indici se esistevano
        print("Ricreazione indici...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_thesaurus_nome_tabella 
            ON pyarchinit_thesaurus_sigle(nome_tabella)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_thesaurus_tipologia 
            ON pyarchinit_thesaurus_sigle(tipologia_sigla)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_thesaurus_parent 
            ON pyarchinit_thesaurus_sigle(id_parent)
        """)
        
        conn.commit()
        print("✅ Aggiornamento SQLite completato!")
        
    except sqlite3.Error as e:
        print(f"❌ Errore SQLite: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()
    
    return True

def create_postgres_update_script():
    """Crea script SQL per PostgreSQL."""
    
    postgres_script = """
-- Script per aggiornare la lunghezza del campo sigla in PostgreSQL
-- Esegui questo script nel tuo database PostgreSQL

-- Aggiorna la lunghezza del campo sigla
ALTER TABLE pyarchinit_thesaurus_sigle 
ALTER COLUMN sigla TYPE VARCHAR(100);

-- Aggiorna anche parent_sigla se esiste
ALTER TABLE pyarchinit_thesaurus_sigle 
ALTER COLUMN parent_sigla TYPE VARCHAR(100);

-- Verifica
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'pyarchinit_thesaurus_sigle'
AND column_name IN ('sigla', 'parent_sigla');
"""
    
    script_path = "update_thesaurus_sigla_postgres.sql"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(postgres_script)
    
    print(f"\n📄 Script PostgreSQL creato: {script_path}")
    print("   Esegui questo script nel tuo database PostgreSQL per aggiornare la struttura.")

def main():
    # Database SQLite path
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
    
    print("Aggiornamento lunghezza campo sigla in pyarchinit_thesaurus_sigle")
    print("Da VARCHAR(3) a VARCHAR(100)")
    print("=" * 60)
    
    # Verifica struttura attuale
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Ottieni info sulla tabella
        cursor.execute("PRAGMA table_info(pyarchinit_thesaurus_sigle)")
        columns = cursor.fetchall()
        
        print("\nStruttura attuale della tabella:")
        for col in columns:
            if col[1] in ['sigla', 'parent_sigla']:
                print(f"  {col[1]}: {col[2]}")
        
        conn.close()
        
        # Aggiorna SQLite
        if update_sigla_length_sqlite(db_path):
            # Verifica dopo l'aggiornamento
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA table_info(pyarchinit_thesaurus_sigle)")
            columns = cursor.fetchall()
            
            print("\nNuova struttura della tabella:")
            for col in columns:
                if col[1] in ['sigla', 'parent_sigla']:
                    print(f"  {col[1]}: {col[2]}")
            
            # Verifica che i dati siano ancora presenti
            cursor.execute("SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle")
            count = cursor.fetchone()[0]
            print(f"\nRecord totali nella tabella: {count}")
            
            conn.close()
    else:
        print(f"Database non trovato: {db_path}")
    
    # Crea script per PostgreSQL
    create_postgres_update_script()
    
    print("\n" + "=" * 60)
    print("✅ Processo completato!")
    print("\nNOTA: Se usi PostgreSQL, esegui lo script SQL generato.")

if __name__ == "__main__":
    main()