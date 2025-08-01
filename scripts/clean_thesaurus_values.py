#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per pulire i valori del thesaurus dopo la correzione
"""

import sqlite3
import os
import sys

def clean_thesaurus_values(db_path):
    """Pulisce i valori None e sistema le tipologie."""
    print(f"Pulizia valori thesaurus: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Pulisci i valori 'None' nella descrizione
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET descrizione = ''
            WHERE descrizione = 'None' OR descrizione IS NULL
        """)
        print(f"✅ Puliti {cursor.rowcount} record con descrizione 'None'")
        
        # Sistema la lingua
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET lingua = UPPER(lingua)
            WHERE lingua = 'it'
        """)
        print(f"✅ Sistemata lingua per {cursor.rowcount} record")
        
        # Correggi tipologia_sigla per i record TMA basandosi sui pattern
        print("\nCorrezione tipologia_sigla per TMA...")
        
        # OGTM - Materiali
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET tipologia_sigla = '10.1'
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND sigla IN ('CER', 'VET', 'MET', 'MAF', 'MAL', 'INL', 'OSS', 'AVO', 
                         'ROU', 'LEG', 'MAO', 'CAT', 'ALT')
        """)
        print(f"  OGTM: {cursor.rowcount} record")
        
        # LDCT - Tipo contenitore
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET tipologia_sigla = '10.2'
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND sigla IN ('cassetta', 'cassa', 'busta')
        """)
        print(f"  LDCT: {cursor.rowcount} record")
        
        # LDCN - Nome contenitore
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET tipologia_sigla = '10.3'
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND sigla LIKE 'MAG%'
        """)
        print(f"  LDCN: {cursor.rowcount} record")
        
        # LOCALITÀ
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET tipologia_sigla = '10.13'
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND sigla LIKE 'LOC%'
        """)
        print(f"  Località: {cursor.rowcount} record")
        
        # AREA
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET tipologia_sigla = '10.14'
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND sigla LIKE 'AREA%'
        """)
        print(f"  Area: {cursor.rowcount} record")
        
        # SETTORE
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET tipologia_sigla = '10.15'
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND sigla LIKE 'SET%'
        """)
        print(f"  Settore: {cursor.rowcount} record")
        
        # SCAN - Nome scavo
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET tipologia_sigla = '10.4'
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND sigla LIKE 'SC%'
        """)
        print(f"  SCAN: {cursor.rowcount} record")
        
        # AINT - Tipo acquisizione
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET tipologia_sigla = '10.5'
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND sigla IN ('scavo', 'superficie', 'sporadico', 'campione', 'prospezione', 
                         'controllo lavori', 'pulizia', 'sconosciuto', 'altro')
        """)
        print(f"  AINT: {cursor.rowcount} record")
        
        # DTZG - Fascia cronologica
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET tipologia_sigla = '10.6'
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND (sigla LIKE 'PREI%' OR sigla LIKE 'NEO%' OR sigla LIKE 'ENE%' 
                OR sigla LIKE 'BRO%' OR sigla LIKE 'FER%' OR sigla LIKE 'ROM%'
                OR sigla LIKE 'MED%' OR sigla LIKE 'MOD%' OR sigla LIKE 'CON%')
        """)
        print(f"  DTZG: {cursor.rowcount} record")
        
        # MACC - Categoria (usando sigla_estesa)
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET tipologia_sigla = '10.7'
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND sigla_estesa IN ('ceramica', 'vetro', 'metallo', 'materiale fittile', 
                                'materiale litico', 'industria litica', 'osso', 'avorio', 
                                'resti osteologici', 'legno', 'materiale organico', 
                                'campioni di terra', 'altri materiali')
        """)
        print(f"  MACC: {cursor.rowcount} record")
        
        # MACL - Classe
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET tipologia_sigla = '10.8'
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND sigla IN ('ARG', 'BRO', 'CER', 'OSS', 'LEG', 'LAT', 'PIE', 'VET',
                         'INT', 'LAV', 'TER', 'MAM', 'COP', 'FER', 'TES', 'MET')
        """)
        print(f"  MACL: {cursor.rowcount} record")
        
        # MACP - Precisazione tipologica
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET tipologia_sigla = '10.9'
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND sigla IN ('frammenti', 'monete', 'mosaico', 'ornamenti', 'strumenti', 
                         'utensili', 'laterizi', 'malacofauna', 'scultura', 
                         'intonaco dipinto', 'coroplastica', 'lucerne', 'anfore', 
                         'epigrafi', 'affreschi', 'armi', 'ossa umane', 
                         'ossa animali', 'ceramica fine', 'ceramica comune', 'ceramica grezza')
        """)
        print(f"  MACP: {cursor.rowcount} record")
        
        # FTAP - Tipo foto
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET tipologia_sigla = '10.12'
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND sigla IN ('dettaglio', 'insieme', 'particolare', 'generale', 
                         'fronte-retro', 'profilo')
        """)
        print(f"  FTAP: {cursor.rowcount} record")
        
        # CRONOLOGIA
        cursor.execute("""
            UPDATE pyarchinit_thesaurus_sigle 
            SET tipologia_sigla = '10.11'
            WHERE nome_tabella = 'tma_materiali_archeologici'
            AND sigla LIKE 'CRON%'
        """)
        print(f"  Cronologia: {cursor.rowcount} record")
        
        # Commit
        conn.commit()
        
        # Mostra alcuni esempi del risultato
        print("\nEsempi del risultato finale:")
        
        # Per ogni tipo
        for tipo, nome in [('10.1', 'OGTM'), ('10.7', 'MACC'), ('10.13', 'Località'), 
                          ('10.14', 'Area'), ('10.15', 'Settore')]:
            cursor.execute("""
                SELECT sigla, sigla_estesa, tipologia_sigla, lingua 
                FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = 'tma_materiali_archeologici'
                AND tipologia_sigla = ?
                LIMIT 3
            """, (tipo,))
            
            print(f"\n{nome} (tipo {tipo}):")
            for row in cursor.fetchall():
                print(f"  {row[0]}: {row[1]} | tipo={row[2]} | lingua={row[3]}")
                
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
    
    print("Pulizia valori thesaurus")
    print("=" * 60)
    
    if clean_thesaurus_values(db_path):
        print("\n✅ Processo completato con successo!")
    else:
        print("\n❌ Processo fallito.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())