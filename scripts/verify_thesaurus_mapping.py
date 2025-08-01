#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per verificare la mappatura completa del thesaurus
"""

import sqlite3
import os
import sys

def verify_mapping(db_path):
    """Verifica la mappatura del thesaurus."""
    print(f"Verifica mappatura thesaurus: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Mappatura corretta secondo il codice TMA
        correct_mapping = {
            '10.1': 'OGTM - Tipo materiale (MAT)',
            '10.2': 'LDCT - Tipo contenitore',  
            '10.3': 'LDCN - Nome contenitore/magazzino (MAG)',
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
        
        print("\n" + "=" * 100)
        print("VERIFICA MAPPATURA TIPOLOGIA_SIGLA")
        print("=" * 100)
        print(f"{'Codice':<10} {'Campo DB':<20} {'Descrizione':<40} {'Record':<10} {'Prefissi':<20}")
        print("-" * 100)
        
        for code, description in sorted(correct_mapping.items()):
            # Conta record per questo tipo
            cursor.execute("""
                SELECT COUNT(*), GROUP_CONCAT(DISTINCT SUBSTR(sigla, 1, 4)) as prefixes
                FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = 'tma_materiali_archeologici' 
                AND tipologia_sigla = ?
            """, (code,))
            
            count, prefixes = cursor.fetchone()
            
            # Mappa codice a campo DB
            field_map = {
                '10.1': 'ogtm',
                '10.2': 'ldct',
                '10.3': 'ldcn',
                '10.4': 'scan',
                '10.5': 'aint',
                '10.6': 'dtzg',
                '10.7': 'macc',
                '10.8': 'macl',
                '10.9': 'macp',
                '10.10': 'macd',
                '10.11': 'cronologia',
                '10.12': 'ftap',
                '10.13': 'localita',
                '10.14': 'area',
                '10.15': 'settore'
            }
            
            field = field_map.get(code, '???')
            print(f"{code:<10} {field:<20} {description:<40} {count or 0:<10} {prefixes or 'N/A':<20}")
        
        # Verifica problemi con settore
        print("\n" + "=" * 100)
        print("VERIFICA SETTORE E RELAZIONI GERARCHICHE")
        print("=" * 100)
        
        # Settori con parent
        cursor.execute("""
            SELECT sigla, sigla_estesa, parent_sigla 
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici' 
            AND tipologia_sigla = '10.15'
            AND parent_sigla IS NOT NULL
            LIMIT 5
        """)
        
        print("\nSettori con parent_sigla:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} -> parent: {row[2]}")
        
        # Verifica che i parent esistano
        cursor.execute("""
            SELECT s.sigla, s.parent_sigla, a.sigla as area_sigla, a.sigla_estesa as area_nome
            FROM pyarchinit_thesaurus_sigle s
            LEFT JOIN pyarchinit_thesaurus_sigle a 
                ON s.parent_sigla = a.sigla 
                AND a.nome_tabella = 'tma_materiali_archeologici'
                AND a.tipologia_sigla = '10.14'
            WHERE s.nome_tabella = 'tma_materiali_archeologici' 
            AND s.tipologia_sigla = '10.15'
            AND s.parent_sigla IS NOT NULL
            LIMIT 10
        """)
        
        print("\nVerifica collegamenti settore->area:")
        for row in cursor.fetchall():
            if row[2]:
                print(f"  ✓ {row[0]} -> {row[1]} trovato come {row[2]} ({row[3]})")
            else:
                print(f"  ✗ {row[0]} -> {row[1]} NON TROVATO!")
        
        # Verifica campi usati nella tabwidget_materiali
        print("\n" + "=" * 100)
        print("CAMPI PER TABWIDGET_MATERIALI")
        print("=" * 100)
        
        material_fields = [
            ('10.1', 'ogtm', 'Tipo materiale'),
            ('10.7', 'macc', 'Categoria'),
            ('10.8', 'macl', 'Classe'),
            ('10.9', 'macp', 'Precisazione tipologica'),
            ('10.10', 'macd', 'Definizione'),
            ('10.11', 'cronologia', 'Cronologia')
        ]
        
        for code, field, desc in material_fields:
            cursor.execute("""
                SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = 'tma_materiali_archeologici' 
                AND tipologia_sigla = ?
            """, (code,))
            count = cursor.fetchone()[0]
            
            # Mostra alcuni esempi
            cursor.execute("""
                SELECT sigla, sigla_estesa 
                FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = 'tma_materiali_archeologici' 
                AND tipologia_sigla = ?
                LIMIT 3
            """, (code,))
            
            examples = cursor.fetchall()
            ex_str = ", ".join([f"{e[0]}:{e[1]}" for e in examples])
            
            print(f"{field:<15} {desc:<30} {count:<10} es: {ex_str}")
        
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
    
    print("Verifica mappatura thesaurus TMA")
    print("=" * 60)
    
    if verify_mapping(db_path):
        print("\n✅ Verifica completata!")
    else:
        print("\n❌ Errore nella verifica.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())