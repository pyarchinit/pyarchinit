#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per correggere lo spostamento dei campi nel thesaurus
- tipologia_sigla -> descrizione
- lingua -> tipologia_sigla  
- order_layer -> lingua
"""

import sqlite3
import os
import sys

def fix_field_shift(db_path):
    """Corregge lo spostamento dei campi nel thesaurus."""
    print(f"Correzione campi thesaurus: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Prima facciamo un backup
        print("Creazione tabella di backup...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS thesaurus_backup_shift AS 
            SELECT * FROM pyarchinit_thesaurus_sigle
        """)
        
        # Verifica quanti record abbiamo
        cursor.execute("SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle")
        total_records = cursor.fetchone()[0]
        print(f"Record totali da correggere: {total_records}")
        
        # Mostra alcuni esempi prima della correzione
        print("\nEsempi PRIMA della correzione:")
        cursor.execute("""
            SELECT sigla, descrizione, tipologia_sigla, lingua, order_layer 
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici' 
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            print(f"  {row[0]}: desc='{row[1]}' | tipo='{row[2]}' | lingua='{row[3]}' | order={row[4]}")
        
        # Esegui la correzione
        print("\nEsecuzione correzione campi...")
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle
            SET descrizione = tipologia_sigla,
                tipologia_sigla = lingua,
                lingua = CAST(order_layer AS TEXT),
                order_layer = 0
        """)
        
        updated = cursor.rowcount
        print(f"Record aggiornati: {updated}")
        
        # Mostra alcuni esempi dopo la correzione
        print("\nEsempi DOPO la correzione:")
        cursor.execute("""
            SELECT sigla, descrizione, tipologia_sigla, lingua, order_layer 
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici' 
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            print(f"  {row[0]}: desc='{row[1]}' | tipo='{row[2]}' | lingua='{row[3]}' | order={row[4]}")
        
        # Correggi i valori di tipologia_sigla per TMA
        print("\nCorrezione valori tipologia_sigla per TMA...")
        
        # Mappa delle correzioni per tipologia_sigla
        tipo_corrections = {
            'tma_materiali_archeologici': {
                'ogtm': '10.1',  # Materiale
                'ldct': '10.2',  # Tipo contenitore  
                'ldcn': '10.3',  # Nome contenitore
                'scan': '10.4',  # Nome scavo
                'aint': '10.5',  # Tipo acquisizione
                'dtzg': '10.6',  # Fascia cronologica
                'macc': '10.7',  # Categoria
                'macl': '10.8',  # Classe
                'macp': '10.9',  # Precisazione tipologica
                'macd': '10.10', # Definizione
                'cronologia': '10.11', # Cronologia
                'ftap': '10.12', # Tipo foto
                'localita': '10.13', # Località
                'area': '10.14',  # Area
                'settore': '10.15' # Settore
            }
        }
        
        # Applica correzioni basate su pattern nella descrizione
        for field, tipo_val in tipo_corrections['tma_materiali_archeologici'].items():
            # Prima controlla se ci sono record con la vecchia descrizione
            cursor.execute("""
                SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = 'tma_materiali_archeologici' 
                AND descrizione = ?
            """, (field,))
            
            count = cursor.fetchone()[0]
            if count > 0:
                cursor.execute("""
                    UPDATE pyarchinit_thesaurus_sigle 
                    SET tipologia_sigla = ?
                    WHERE nome_tabella = 'tma_materiali_archeologici'
                    AND descrizione = ?
                """, (tipo_val, field))
                print(f"  Aggiornati {cursor.rowcount} record con descrizione '{field}' -> tipologia '{tipo_val}'")
        
        # Sistema anche la lingua (dovrebbe essere 'IT' per tutti)
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET lingua = 'IT'
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND (lingua IS NULL OR lingua = '' OR lingua = '0')
        """)
        print(f"  Sistemata lingua per {cursor.rowcount} record TMA")
        
        # Commit delle modifiche
        conn.commit()
        print("\n✅ Correzione completata con successo!")
        
        # Mostra il risultato finale per TMA
        print("\nRisultato finale per TMA:")
        cursor.execute("""
            SELECT sigla, sigla_estesa, descrizione, tipologia_sigla, lingua 
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND tipologia_sigla = '10.1'
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            print(f"  {row[0]} ({row[1]}): tipo={row[3]}, lingua={row[4]}")
            
    except sqlite3.Error as e:
        print(f"❌ Errore: {e}")
        conn.rollback()
        
        # Tentativo di ripristino
        try:
            print("\nTentativo di ripristino dal backup...")
            cursor.execute("DROP TABLE IF EXISTS pyarchinit_thesaurus_sigle")
            cursor.execute("""
                CREATE TABLE pyarchinit_thesaurus_sigle AS 
                SELECT * FROM thesaurus_backup_shift
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
    
    print("Correzione spostamento campi thesaurus")
    print("=" * 60)
    print("Spostamento da correggere:")
    print("- tipologia_sigla -> descrizione")
    print("- lingua -> tipologia_sigla")
    print("- order_layer -> lingua")
    print("=" * 60)
    
    if fix_field_shift(db_path):
        print("\n✅ Processo completato con successo!")
        print("\nI campi sono stati riorganizzati correttamente.")
    else:
        print("\n❌ Processo fallito.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())