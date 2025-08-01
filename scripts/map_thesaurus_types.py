#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per mappare correttamente i tipi del thesaurus TMA
"""

import sqlite3
import os
import sys

def map_thesaurus_types(db_path):
    """Mappa i tipi del thesaurus secondo la logica corretta."""
    print(f"Mappatura tipi thesaurus: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Prima vediamo quali sono i pattern
        print("\nAnalisi dei pattern esistenti...")
        
        cursor.execute("""
            SELECT SUBSTR(sigla, 1, 3) as prefix, COUNT(*) as count, MIN(sigla_estesa) as esempio
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici'
            GROUP BY SUBSTR(sigla, 1, 3)
            ORDER BY count DESC
            LIMIT 20
        """)
        
        print("\nPrefissi trovati:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} record (es: {row[2]})")
        
        # Mappa corretta basata sui prefissi
        type_mappings = [
            # OGTM - Materiali (MAT prefix)
            ("UPDATE pyarchinit_thesaurus_sigle SET tipologia_sigla = '10.1' WHERE nome_tabella = 'tma_materiali_archeologici' AND sigla LIKE 'MAT%'", "OGTM"),
            
            # LDCT - Tipo contenitore (LDC prefix per tipo)
            ("UPDATE pyarchinit_thesaurus_sigle SET tipologia_sigla = '10.2' WHERE nome_tabella = 'tma_materiali_archeologici' AND sigla LIKE 'LDCT%'", "LDCT"),
            
            # LDCN - Nome contenitore (MAG prefix)
            ("UPDATE pyarchinit_thesaurus_sigle SET tipologia_sigla = '10.3' WHERE nome_tabella = 'tma_materiali_archeologici' AND sigla LIKE 'MAG%'", "LDCN"),
            
            # SCAN - Nome scavo (SC prefix)
            ("UPDATE pyarchinit_thesaurus_sigle SET tipologia_sigla = '10.4' WHERE nome_tabella = 'tma_materiali_archeologici' AND sigla LIKE 'SC%'", "SCAN"),
            
            # AINT - Tipo acquisizione (AIN prefix)
            ("UPDATE pyarchinit_thesaurus_sigle SET tipologia_sigla = '10.5' WHERE nome_tabella = 'tma_materiali_archeologici' AND sigla LIKE 'AIN%'", "AINT"),
            
            # DTZG - Fascia cronologica (DTZ prefix)
            ("UPDATE pyarchinit_thesaurus_sigle SET tipologia_sigla = '10.6' WHERE nome_tabella = 'tma_materiali_archeologici' AND sigla LIKE 'DTZ%'", "DTZG"),
            
            # MACC - Categoria (MAC prefix per categoria)
            ("UPDATE pyarchinit_thesaurus_sigle SET tipologia_sigla = '10.7' WHERE nome_tabella = 'tma_materiali_archeologici' AND sigla LIKE 'MACC%'", "MACC"),
            
            # MACL - Classe (MACL prefix)
            ("UPDATE pyarchinit_thesaurus_sigle SET tipologia_sigla = '10.8' WHERE nome_tabella = 'tma_materiali_archeologici' AND sigla LIKE 'MACL%'", "MACL"),
            
            # MACP - Precisazione tipologica (MACP prefix)
            ("UPDATE pyarchinit_thesaurus_sigle SET tipologia_sigla = '10.9' WHERE nome_tabella = 'tma_materiali_archeologici' AND sigla LIKE 'MACP%'", "MACP"),
            
            # MACD - Definizione (MACD prefix)
            ("UPDATE pyarchinit_thesaurus_sigle SET tipologia_sigla = '10.10' WHERE nome_tabella = 'tma_materiali_archeologici' AND sigla LIKE 'MACD%'", "MACD"),
            
            # CRONOLOGIA (CRO prefix)
            ("UPDATE pyarchinit_thesaurus_sigle SET tipologia_sigla = '10.11' WHERE nome_tabella = 'tma_materiali_archeologici' AND sigla LIKE 'CRO%'", "CRONOLOGIA"),
            
            # FTAP - Tipo foto (FTA prefix)
            ("UPDATE pyarchinit_thesaurus_sigle SET tipologia_sigla = '10.12' WHERE nome_tabella = 'tma_materiali_archeologici' AND sigla LIKE 'FTA%'", "FTAP"),
            
            # Località (LOC prefix)
            ("UPDATE pyarchinit_thesaurus_sigle SET tipologia_sigla = '10.13' WHERE nome_tabella = 'tma_materiali_archeologici' AND sigla LIKE 'LOC%'", "LOCALITÀ"),
            
            # Area (ARE prefix)
            ("UPDATE pyarchinit_thesaurus_sigle SET tipologia_sigla = '10.14' WHERE nome_tabella = 'tma_materiali_archeologici' AND sigla LIKE 'AREA%'", "AREA"),
            
            # Settore (SET prefix)
            ("UPDATE pyarchinit_thesaurus_sigle SET tipologia_sigla = '10.15' WHERE nome_tabella = 'tma_materiali_archeologici' AND sigla LIKE 'SET%'", "SETTORE"),
        ]
        
        print("\nApplicazione mappature...")
        for query, tipo in type_mappings:
            cursor.execute(query)
            if cursor.rowcount > 0:
                print(f"  {tipo}: {cursor.rowcount} record aggiornati")
        
        # Verifica anche i valori che erano già stati sistemati ma con tipo sbagliato
        # Correggi DTZG che ora sono 10.10 ma dovrebbero essere 10.6
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET tipologia_sigla = '10.6'
            WHERE nome_tabella = 'tma_materiali_archeologici' 
            AND tipologia_sigla = '10.10'
            AND sigla LIKE 'DTZG%'
        """)
        if cursor.rowcount > 0:
            print(f"  Corretti DTZG: {cursor.rowcount} record")
        
        # Sistema anche quelli che hanno tipologia generica basandosi su sigla_estesa
        corrections = [
            ("ceramica", "10.7"),
            ("vetro", "10.7"),
            ("metallo", "10.7"),
            ("materiale fittile", "10.7"),
            ("materiale litico", "10.7"),
            ("industria litica", "10.7"),
            ("osso", "10.7"),
            ("avorio", "10.7"),
            ("resti osteologici", "10.7"),
            ("legno", "10.7"),
            ("materiale organico", "10.7"),
            ("campioni di terra", "10.7"),
            ("altri materiali", "10.7"),
        ]
        
        for sigla_est, tipo in corrections:
            cursor.execute("""
                UPDATE pyarchinit_thesaurus_sigle 
                SET tipologia_sigla = ?
                WHERE nome_tabella = 'tma_materiali_archeologici' 
                AND sigla_estesa = ?
                AND tipologia_sigla NOT LIKE '10.%'
            """, (tipo, sigla_est))
            if cursor.rowcount > 0:
                print(f"  Corretto '{sigla_est}': {cursor.rowcount} record")
        
        # Commit
        conn.commit()
        
        # Mostra il risultato finale
        print("\nRiepilogo finale per tipo:")
        cursor.execute("""
            SELECT tipologia_sigla, COUNT(*) as count
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici'
            GROUP BY tipologia_sigla
            ORDER BY tipologia_sigla
        """)
        
        for row in cursor.fetchall():
            cursor.execute("""
                SELECT MIN(sigla), MIN(sigla_estesa)
                FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = 'tma_materiali_archeologici'
                AND tipologia_sigla = ?
            """, (row[0],))
            esempio = cursor.fetchone()
            print(f"  {row[0]}: {row[1]} record (es: {esempio[0]} - {esempio[1]})")
        
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
    
    print("Mappatura tipi thesaurus TMA")
    print("=" * 60)
    
    if map_thesaurus_types(db_path):
        print("\n✅ Processo completato con successo!")
    else:
        print("\n❌ Processo fallito.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())