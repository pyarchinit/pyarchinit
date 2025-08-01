#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script semplificato per aggiornare pyarchinit_thesaurus_sigle
"""

import sqlite3
import os
import sys

def backup_and_recreate(db_path):
    """Backup dei dati e ricreazione tabella."""
    print(f"Aggiornamento database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Prima fai backup dei dati
        print("Backup dei dati esistenti...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS thesaurus_backup AS 
            SELECT * FROM pyarchinit_thesaurus_sigle
        """)
        
        # Conta i record
        cursor.execute("SELECT COUNT(*) FROM thesaurus_backup")
        count = cursor.fetchone()[0]
        print(f"  Record salvati: {count}")
        
        # Elimina vecchia tabella
        print("Eliminazione vecchia tabella...")
        cursor.execute("DROP TABLE IF EXISTS pyarchinit_thesaurus_sigle")
        
        # Ricrea con nuovo schema
        print("Creazione nuova tabella con sigla VARCHAR(100)...")
        cursor.execute("""
            CREATE TABLE pyarchinit_thesaurus_sigle (
                id_thesaurus_sigle INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_tabella TEXT,
                sigla VARCHAR(100),
                sigla_estesa TEXT,
                tipologia_sigla VARCHAR(100),
                lingua VARCHAR(10),
                order_layer INTEGER DEFAULT 0,
                id_parent INTEGER,
                parent_sigla VARCHAR(100),
                hierarchy_level INTEGER DEFAULT 0
            )
        """)
        
        # Ripristina i dati
        print("Ripristino dati...")
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            SELECT * FROM thesaurus_backup
        """)
        
        # Verifica
        cursor.execute("SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle")
        new_count = cursor.fetchone()[0]
        print(f"  Record ripristinati: {new_count}")
        
        # Elimina backup
        cursor.execute("DROP TABLE thesaurus_backup")
        
        # Ricrea indici
        print("Ricreazione indici...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_thesaurus_nome_tabella 
            ON pyarchinit_thesaurus_sigle(nome_tabella)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_thesaurus_tipologia 
            ON pyarchinit_thesaurus_sigle(tipologia_sigla)
        """)
        
        conn.commit()
        print("✅ Aggiornamento completato!")
        
        # Test con una sigla lunga
        print("\nTest inserimento sigla lunga...")
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('test', 'TEST_SIGLA_MOLTO_LUNGA_PER_VERIFICARE_CHE_FUNZIONI_CORRETTAMENTE_123456', 
                    'Test sigla lunga', 'test', 'it')
        """)
        conn.commit()
        
        # Verifica
        cursor.execute("""
            SELECT sigla, LENGTH(sigla) as len 
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = 'test'
        """)
        result = cursor.fetchone()
        if result:
            print(f"  Sigla inserita: {result[0][:50]}...")
            print(f"  Lunghezza: {result[1]} caratteri")
            
            # Rimuovi test
            cursor.execute("DELETE FROM pyarchinit_thesaurus_sigle WHERE tipologia_sigla = 'test'")
            conn.commit()
        
    except sqlite3.Error as e:
        print(f"❌ Errore: {e}")
        conn.rollback()
        
        # Prova a ripristinare
        try:
            cursor.execute("SELECT COUNT(*) FROM thesaurus_backup")
            if cursor.fetchone()[0] > 0:
                print("\nTentativo di ripristino dal backup...")
                cursor.execute("DROP TABLE IF EXISTS pyarchinit_thesaurus_sigle")
                cursor.execute("""
                    CREATE TABLE pyarchinit_thesaurus_sigle AS 
                    SELECT * FROM thesaurus_backup
                """)
                conn.commit()
                print("Ripristino completato.")
        except:
            pass
            
        return False
        
    finally:
        conn.close()
    
    return True

def main():
    # Database path
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database non trovato: {db_path}")
        return 1
    
    print("Aggiornamento campo sigla da VARCHAR(3) a VARCHAR(100)")
    print("=" * 60)
    
    if backup_and_recreate(db_path):
        print("\n" + "=" * 60)
        print("Processo completato con successo!")
        print("\nLa colonna sigla ora può contenere fino a 100 caratteri.")
        print("Questo permette di usare sigle più descrittive nel thesaurus.")
    else:
        print("\nProcesso fallito. Controlla gli errori sopra.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())