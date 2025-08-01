#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per pulire e correggere il thesaurus TMA
"""

import sqlite3
import os
import sys

def clean_tma_thesaurus(db_path):
    """Pulisce e corregge il thesaurus TMA."""
    print(f"Pulizia thesaurus TMA: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Prima elimina le tabelle sbagliate (refusi)
        print("\n1. Eliminazione tabelle refusi...")
        cursor.execute("""
            DELETE FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella IN ('tma_table', 'tma_materiali_table')
        """)
        print(f"   Eliminati {cursor.rowcount} record da tabelle refusi")
        
        # 2. Unifica tutto sotto tma_materiali_archeologici
        print("\n2. Unificazione tabelle...")
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET nome_tabella = 'tma_materiali_archeologici'
            WHERE nome_tabella = 'tma_materiali_ripetibili'
        """)
        print(f"   Unificati {cursor.rowcount} record da tma_materiali_ripetibili")
        
        # 3. Correggi le tipologie che hanno lettere invece che numeri
        print("\n3. Correzione tipologie con lettere...")
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET tipologia_sigla = '10.7'
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND tipologia_sigla = 'macc'
        """)
        print(f"   Corretti MACC: {cursor.rowcount} record")
        
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET tipologia_sigla = '10.8'
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND tipologia_sigla = 'macl'
        """)
        print(f"   Corretti MACL: {cursor.rowcount} record")
        
        # 4. Verifica le categorie attuali
        print("\n4. Verifica categorie (10.7)...")
        cursor.execute("""
            SELECT sigla, sigla_estesa 
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND tipologia_sigla = '10.7'
            ORDER BY sigla
        """)
        
        current_categories = cursor.fetchall()
        print(f"   Categorie attuali trovate: {len(current_categories)}")
        for cat in current_categories:
            print(f"     - {cat[0]}: {cat[1]}")
        
        # 5. Elimina categorie non valide
        valid_categories = [
            'ceramica', 'vetro', 'metallo', 'materiale fittile', 
            'materiale litico', 'industria litica', 'osso', 'avorio', 
            'resti osteologici', 'legno', 'materiale organico', 
            'campioni di terra', 'altri materiali'
        ]
        
        # Crea stringa per query SQL
        valid_cat_string = "', '".join(valid_categories)
        
        cursor.execute(f"""
            DELETE FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND tipologia_sigla = '10.7'
            AND sigla_estesa NOT IN ('{valid_cat_string}')
        """)
        print(f"\n5. Eliminate {cursor.rowcount} categorie non valide")
        
        # 6. Verifica e sistema i codici tipologia
        print("\n6. Verifica codici tipologia...")
        
        # Controlla che tutte le tipologie TMA abbiano il formato corretto
        cursor.execute("""
            SELECT DISTINCT tipologia_sigla 
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND tipologia_sigla NOT LIKE '10.%'
        """)
        
        wrong_types = cursor.fetchall()
        if wrong_types:
            print(f"   Trovate tipologie sbagliate: {wrong_types}")
            # Correggi eventuali altri problemi...
        
        # 7. Verifica finale
        print("\n7. Riepilogo finale:")
        cursor.execute("""
            SELECT tipologia_sigla, COUNT(*) as count
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici'
            GROUP BY tipologia_sigla
            ORDER BY tipologia_sigla
        """)
        
        for row in cursor.fetchall():
            print(f"   {row[0]}: {row[1]} record")
        
        # Commit
        conn.commit()
        
        # 8. Mostra le categorie finali
        print("\n8. Categorie finali (10.7):")
        cursor.execute("""
            SELECT sigla, sigla_estesa 
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND tipologia_sigla = '10.7'
            ORDER BY sigla
        """)
        
        for row in cursor.fetchall():
            print(f"   {row[0]}: {row[1]}")
            
    except sqlite3.Error as e:
        print(f"❌ Errore: {e}")
        conn.rollback()
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
    
    print("Pulizia completa thesaurus TMA")
    print("=" * 60)
    
    if clean_tma_thesaurus(db_path):
        print("\n✅ Processo completato con successo!")
    else:
        print("\n❌ Processo fallito.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())