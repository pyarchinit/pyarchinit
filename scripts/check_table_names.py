#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per verificare i nomi delle tabelle nel thesaurus
"""

import sqlite3
import os

db_path = os.path.expanduser("~/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite")

print(f"Database: {db_path}")
print("=" * 80)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Mostra tutti i nomi tabella distinti nel thesaurus
    print("\nNOMI TABELLE NEL THESAURUS (pyarchinit_thesaurus_sigle):")
    cursor.execute("""
        SELECT DISTINCT nome_tabella, COUNT(*) as count
        FROM pyarchinit_thesaurus_sigle
        GROUP BY nome_tabella
        ORDER BY nome_tabella
    """)
    
    results = cursor.fetchall()
    print(f"\nTrovati {len(results)} nomi tabella distinti:\n")
    
    for nome, count in results:
        print(f"  '{nome}' - {count} record")
    
    # 2. Mostra esempi per ogni tabella
    print("\n\nESEMPI DI RECORD PER OGNI TABELLA:")
    
    for nome, _ in results[:10]:  # Prime 10 tabelle
        print(f"\n'{nome}':")
        cursor.execute("""
            SELECT tipologia_sigla, sigla, lingua
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = ?
            LIMIT 3
        """, (nome,))
        
        examples = cursor.fetchall()
        for tipo, sigla, lingua in examples:
            print(f"    Tipo: {tipo}, Sigla: '{sigla}', Lingua: {lingua}")
    
    # 3. Cerca specifici pattern
    print("\n\nRICERCA PATTERN SPECIFICI:")
    
    patterns = [
        ('US%', 'Pattern US'),
        ('%INVENTARIO%', 'Pattern Inventario'),
        ('%Inventario%', 'Pattern Inventario (case)'),
        ('%MATERIALI%', 'Pattern Materiali'),
        ('%Materiali%', 'Pattern Materiali (case)'),
        ('%TOMBA%', 'Pattern Tomba'),
        ('%Tomba%', 'Pattern Tomba (case)'),
        ('%INDIVIDUI%', 'Pattern Individui'),
        ('%TMA%', 'Pattern TMA')
    ]
    
    for pattern, desc in patterns:
        cursor.execute("""
            SELECT DISTINCT nome_tabella
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella LIKE ?
        """, (pattern,))
        
        results = cursor.fetchall()
        if results:
            print(f"\n{desc}:")
            for (nome,) in results:
                print(f"  '{nome}'")
    
    # 4. Verifica i mapper names dal codice
    print("\n\nMAPPER NAMES ATTESI (dal codice):")
    mapper_names = {
        'SITE': 'Sito',
        'US': 'US', 
        'INVENTARIO_MATERIALI': 'Inventario Materiali',
        'TOMBA': 'Tomba',
        'INDIVIDUI': 'Individui',
        'TMA': 'TMA materiali archeologici'
    }
    
    for mapper, display in mapper_names.items():
        # Cerca con display name
        cursor.execute("""
            SELECT COUNT(*)
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = ?
        """, (display,))
        count1 = cursor.fetchone()[0]
        
        # Cerca con mapper name
        cursor.execute("""
            SELECT COUNT(*)
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = ?
        """, (mapper,))
        count2 = cursor.fetchone()[0]
        
        print(f"\n{mapper}:")
        print(f"  Come '{display}': {count1} record")
        print(f"  Come '{mapper}': {count2} record")
    
    conn.close()
    
except Exception as e:
    print(f"ERRORE: {str(e)}")