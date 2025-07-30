#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to test thesaurus entries
"""

import sqlite3
import os

def main():
    # Database path
    db_path = os.path.expanduser("/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite")
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Testing TMA thesaurus entries...\n")
    
    # Test materials table thesaurus
    print("Materials table thesaurus (tma_materiali_ripetibili):")
    print("-" * 60)
    
    for tipo, nome in [('10.4', 'Materiale'), ('10.5', 'Categoria'), ('10.6', 'Classe'), 
                       ('10.8', 'Prec. tipologica'), ('10.9', 'Definizione')]:
        cursor.execute("""
        SELECT COUNT(*), tipologia_sigla 
        FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'tma_materiali_ripetibili' 
        AND tipologia_sigla = ? 
        AND lingua = 'IT'
        """, (tipo,))
        
        result = cursor.fetchone()
        if result:
            print(f"{nome} ({tipo}): {result[0]} entries")
            
            # Show first 3 entries
            cursor.execute("""
            SELECT sigla, sigla_estesa 
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_ripetibili' 
            AND tipologia_sigla = ? 
            AND lingua = 'IT'
            LIMIT 3
            """, (tipo,))
            
            for row in cursor.fetchall():
                print(f"  - {row[0]}: {row[1]}")
    
    print("\n\nMain TMA table thesaurus (tma_materiali_archeologici):")
    print("-" * 60)
    
    for tipo, nome in [('10.10', 'Location type (ldct)'), ('10.11', 'Acquisition type (aint)'),
                       ('10.12', 'Photo type (ftap)'), ('10.13', 'Drawing type (drat)'),
                       ('10.14', 'Conservation status (stcc)')]:
        cursor.execute("""
        SELECT COUNT(*), tipologia_sigla 
        FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'tma_materiali_archeologici' 
        AND tipologia_sigla = ? 
        AND lingua = 'IT'
        """, (tipo,))
        
        result = cursor.fetchone()
        if result:
            print(f"{nome} ({tipo}): {result[0]} entries")
            
            # Show all entries for main table
            cursor.execute("""
            SELECT sigla, sigla_estesa 
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella = 'tma_materiali_archeologici' 
            AND tipologia_sigla = ? 
            AND lingua = 'IT'
            """, (tipo,))
            
            for row in cursor.fetchall():
                print(f"  - {row[0]}: {row[1]}")
    
    conn.close()

if __name__ == "__main__":
    main()