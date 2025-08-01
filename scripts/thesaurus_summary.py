#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per generare un riepilogo del thesaurus TMA
"""

import sqlite3
import os
import sys

def generate_summary(db_path):
    """Genera un riepilogo del thesaurus."""
    print(f"Generazione riepilogo thesaurus: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Mappa dei tipi
        type_map = {
            '10.1': 'OGTM - Tipo materiale',
            '10.2': 'LDCT - Tipo contenitore',
            '10.3': 'LDCN - Nome contenitore (magazzino)',
            '10.4': 'SCAN - Nome scavo/campagna',
            '10.5': 'AINT - Tipo acquisizione',
            '10.6': 'DTZG - Fascia cronologica',
            '10.7': 'MACC - Categoria materiale',
            '10.8': 'MACL - Classe',
            '10.9': 'MACP - Precisazione tipologica',
            '10.10': 'MACD - Definizione',
            '10.11': 'CRONOLOGIA',
            '10.12': 'FTAP - Tipo foto',
            '10.13': 'LOCALITÀ',
            '10.14': 'AREA',
            '10.15': 'SETTORE'
        }
        
        print("\n" + "=" * 80)
        print("RIEPILOGO THESAURUS TMA (tma_materiali_archeologici)")
        print("=" * 80)
        
        # Per ogni tipo
        for tipo_code, tipo_name in sorted(type_map.items()):
            cursor.execute("""
                SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = 'tma_materiali_archeologici' 
                AND tipologia_sigla = ?
            """, (tipo_code,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                print(f"\n{tipo_name} (codice: {tipo_code}) - {count} record")
                print("-" * 60)
                
                # Mostra alcuni esempi
                cursor.execute("""
                    SELECT sigla, sigla_estesa 
                    FROM pyarchinit_thesaurus_sigle 
                    WHERE nome_tabella = 'tma_materiali_archeologici' 
                    AND tipologia_sigla = ?
                    ORDER BY sigla
                    LIMIT 5
                """, (tipo_code,))
                
                for row in cursor.fetchall():
                    print(f"  {row[0]}: {row[1]}")
                
                if count > 5:
                    print(f"  ... e altri {count - 5} record")
        
        # Verifica relazioni gerarchiche
        print("\n" + "=" * 80)
        print("RELAZIONI GERARCHICHE")
        print("=" * 80)
        
        # Località -> Area
        cursor.execute("""
            SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici' 
            AND tipologia_sigla = '10.14'
            AND parent_sigla IS NOT NULL
        """)
        area_with_parent = cursor.fetchone()[0]
        print(f"\nAree collegate a località: {area_with_parent}")
        
        # Area -> Settore  
        cursor.execute("""
            SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici' 
            AND tipologia_sigla = '10.15'
            AND parent_sigla IS NOT NULL
        """)
        settore_with_parent = cursor.fetchone()[0]
        print(f"Settori collegati ad aree: {settore_with_parent}")
        
        # Totale record
        cursor.execute("""
            SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici'
        """)
        total = cursor.fetchone()[0]
        
        print(f"\n{'=' * 80}")
        print(f"TOTALE RECORD NEL THESAURUS TMA: {total}")
        print(f"{'=' * 80}")
        
    except sqlite3.Error as e:
        print(f"❌ Errore: {e}")
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
    
    print("Riepilogo Thesaurus TMA")
    print("=" * 60)
    
    if generate_summary(db_path):
        print("\n✅ Riepilogo completato!")
    else:
        print("\n❌ Errore nella generazione del riepilogo.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())