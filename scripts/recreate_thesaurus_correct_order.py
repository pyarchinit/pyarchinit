#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per ricreare la tabella thesaurus con l'ordine corretto delle colonne
"""

import sqlite3
import os
import sys

def recreate_thesaurus_table(db_path):
    """Ricrea la tabella con l'ordine corretto delle colonne."""
    print(f"Ricreazione tabella thesaurus: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Backup dei dati
        print("Backup dei dati esistenti...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS thesaurus_backup_correct AS 
            SELECT * FROM pyarchinit_thesaurus_sigle
        """)
        
        cursor.execute("SELECT COUNT(*) FROM thesaurus_backup_correct")
        count = cursor.fetchone()[0]
        print(f"  Record salvati: {count}")
        
        # Elimina vecchia tabella
        print("Eliminazione vecchia tabella...")
        cursor.execute("DROP TABLE IF EXISTS pyarchinit_thesaurus_sigle")
        
        # Ricrea con ordine corretto
        print("Creazione nuova tabella con ordine corretto...")
        cursor.execute("""
            CREATE TABLE pyarchinit_thesaurus_sigle (
                id_thesaurus_sigle INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_tabella TEXT,
                sigla VARCHAR(100),
                sigla_estesa TEXT,
                descrizione TEXT,
                tipologia_sigla VARCHAR(100),
                lingua VARCHAR(10),
                order_layer INTEGER DEFAULT 0,
                id_parent INTEGER,
                parent_sigla VARCHAR(100),
                hierarchy_level INTEGER DEFAULT 0
            )
        """)
        
        # Ripristina i dati nell'ordine corretto
        print("Ripristino dati...")
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, descrizione, 
             tipologia_sigla, lingua, order_layer, id_parent, parent_sigla, hierarchy_level)
            SELECT id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, 
                   COALESCE(descrizione, ''), tipologia_sigla, lingua, 
                   order_layer, id_parent, parent_sigla, hierarchy_level
            FROM thesaurus_backup_correct
        """)
        
        # Verifica
        cursor.execute("SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle")
        new_count = cursor.fetchone()[0]
        print(f"  Record ripristinati: {new_count}")
        
        # Elimina backup
        cursor.execute("DROP TABLE thesaurus_backup_correct")
        
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
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_thesaurus_parent 
            ON pyarchinit_thesaurus_sigle(id_parent)
        """)
        
        conn.commit()
        print("✅ Tabella ricreata con successo!")
        
        # Verifica struttura
        cursor.execute("PRAGMA table_info(pyarchinit_thesaurus_sigle)")
        columns = cursor.fetchall()
        
        print("\nNuova struttura della tabella:")
        for col in columns:
            print(f"  {col[0]}. {col[1]}: {col[2]}")
            
        # Test query
        cursor.execute("""
            SELECT id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, 
                   descrizione, tipologia_sigla, lingua
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici' 
            AND tipologia_sigla = '10.1'
            LIMIT 3
        """)
        
        print("\nEsempio record:")
        for row in cursor.fetchall():
            print(f"  ID: {row[0]}, Sigla: {row[2]}, Estesa: {row[3]}, Desc: '{row[4]}', Tipo: {row[5]}")
            
    except sqlite3.Error as e:
        print(f"❌ Errore: {e}")
        conn.rollback()
        
        # Prova a ripristinare
        try:
            cursor.execute("SELECT COUNT(*) FROM thesaurus_backup_correct")
            if cursor.fetchone()[0] > 0:
                print("\nTentativo di ripristino dal backup...")
                cursor.execute("DROP TABLE IF EXISTS pyarchinit_thesaurus_sigle")
                cursor.execute("""
                    CREATE TABLE pyarchinit_thesaurus_sigle AS 
                    SELECT * FROM thesaurus_backup_correct
                """)
                cursor.execute("DROP TABLE thesaurus_backup_correct")
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
    
    print("Ricreazione tabella thesaurus con ordine corretto delle colonne")
    print("=" * 60)
    
    if recreate_thesaurus_table(db_path):
        print("\n✅ Processo completato con successo!")
        print("\nLa tabella ora ha l'ordine corretto delle colonne:")
        print("1. id_thesaurus_sigle")
        print("2. nome_tabella")
        print("3. sigla")
        print("4. sigla_estesa")
        print("5. descrizione")
        print("6. tipologia_sigla")
        print("7. lingua")
        print("8. order_layer")
        print("9. id_parent")
        print("10. parent_sigla")
        print("11. hierarchy_level")
    else:
        print("\n❌ Processo fallito.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())