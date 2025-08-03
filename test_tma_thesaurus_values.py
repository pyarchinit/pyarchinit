#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test per verificare i valori del thesaurus TMA
"""

import sys
import os
import sqlite3

def test_tma_thesaurus_values():
    """Test che verifica i valori del thesaurus per TMA"""
    
    # Database path
    db_path = os.path.expanduser("~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite")
    
    if not os.path.exists(db_path):
        print(f"Database non trovato in: {db_path}")
        return False
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== Test Valori Thesaurus TMA ===\n")
    
    # Test per ogni tipologia
    test_cases = [
        ('10.1', 'Denominazione collocazione'),
        ('10.2', 'Tipologia collocazione'),
        ('10.3', 'Località'),
        ('10.4', 'Denominazione scavo'),
        ('10.5', 'Categoria (macc)'),
        ('10.6', 'Fascia cronologica / Cronologia'),
        ('10.7', 'Area'),
        ('10.8', 'Classe (macl)'),
        ('10.9', 'Prec. tipologica (macp)'),
        ('10.10', 'Definizione (macd)'),
        ('10.11', 'Cronologia specifica'),
        ('10.12', 'Tipo foto/disegno'),
        ('10.15', 'Settore')
    ]
    
    for tipologia, descrizione in test_cases:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = 'TMA materiali archeologici'
            AND tipologia_sigla = ?
            AND lingua = 'it'
        """, (tipologia,))
        
        count = cursor.fetchone()[0]
        print(f"{tipologia} - {descrizione}: {count} valori")
        
        # Mostra alcuni esempi
        if count > 0:
            cursor.execute("""
                SELECT sigla, sigla_estesa 
                FROM pyarchinit_thesaurus_sigle
                WHERE nome_tabella = 'TMA materiali archeologici'
                AND tipologia_sigla = ?
                AND lingua = 'it'
                LIMIT 3
            """, (tipologia,))
            
            for sigla, estesa in cursor.fetchall():
                print(f"   - {sigla}: {estesa}")
            if count > 3:
                print(f"   ... e altri {count - 3}")
        print()
    
    # Test specifico per i campi della tabella materiali
    print("\n=== Test Campi Tabella Materiali ===")
    
    material_fields = {
        '10.5': 'Categoria (macc)',
        '10.8': 'Classe (macl)', 
        '10.9': 'Prec. tipologica (macp)',
        '10.10': 'Definizione (macd)',
        '10.6': 'Cronologia (cronologia_mac)'
    }
    
    print("I delegates della tabella materiali dovrebbero usare:")
    for tip, desc in material_fields.items():
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = 'TMA materiali archeologici'
            AND tipologia_sigla = ?
            AND lingua = 'IT'  -- Uppercase per test
        """, (tip,))
        
        count_upper = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = 'TMA materiali archeologici'
            AND tipologia_sigla = ?
            AND lingua = 'it'  -- Lowercase
        """, (tip,))
        
        count_lower = cursor.fetchone()[0]
        
        print(f"   {tip} - {desc}:")
        print(f"      Lingua 'IT': {count_upper} valori")
        print(f"      Lingua 'it': {count_lower} valori")
    
    conn.close()
    
    print("\n" + "="*50)
    print("CONCLUSIONE:")
    print("Se i delegates non mostrano valori, verificare:")
    print("1. Che il codice della lingua sia corretto (IT vs it)")
    print("2. Che i codici tipologia siano corretti")
    print("3. Che il nome tabella sia 'TMA materiali archeologici'")
    print("4. Che il DB_MANAGER sia inizializzato quando vengono caricati i delegates")
    
    return True

if __name__ == "__main__":
    success = test_tma_thesaurus_values()
    sys.exit(0 if success else 1)