#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test delle query per ldct e aint
"""

import sqlite3
import os

def test_queries():
    # Database path
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database non trovato in: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== TEST QUERY LDCT E AINT ===\n")
    
    # Test con diverse varianti di lingua
    test_languages = ["it", "'it'", '"it"', "IT", "'IT'"]
    
    for lang in test_languages:
        print(f"\nTest con lingua = {repr(lang)}:")
        print("-" * 40)
        
        # Test ldct (10.2)
        query = """
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = 'TMA materiali archeologici' 
            AND tipologia_sigla = '10.2'
            AND lingua = ?
        """
        
        cursor.execute(query, (lang,))
        count_ldct = cursor.fetchone()[0]
        print(f"  ldct (10.2): {count_ldct} valori")
        
        # Test aint (10.6)
        query = """
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = 'TMA materiali archeologici' 
            AND tipologia_sigla = '10.6'
            AND lingua = ?
        """
        
        cursor.execute(query, (lang,))
        count_aint = cursor.fetchone()[0]
        print(f"  aint (10.6): {count_aint} valori")
    
    # Test senza filtro lingua
    print("\n\nTest SENZA filtro lingua:")
    print("-" * 40)
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'TMA materiali archeologici' 
        AND tipologia_sigla = '10.2'
    """)
    count_ldct_all = cursor.fetchone()[0]
    print(f"  ldct (10.2): {count_ldct_all} valori totali")
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'TMA materiali archeologici' 
        AND tipologia_sigla = '10.6'
    """)
    count_aint_all = cursor.fetchone()[0]
    print(f"  aint (10.6): {count_aint_all} valori totali")
    
    conn.close()

if __name__ == "__main__":
    test_queries()