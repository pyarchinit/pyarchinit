#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test finale per verificare che tutti i fix del Thesaurus siano applicati correttamente
"""

import sqlite3
import os
import sys


def test_database_updated(cursor):
    """Verifica che il database sia stato aggiornato con le nuove colonne"""
    print("\n=== Test Struttura Database ===")
    
    cursor.execute("PRAGMA table_info(pyarchinit_thesaurus_sigle)")
    columns = [row[1] for row in cursor.fetchall()]
    
    required_columns = ['order_layer', 'id_parent', 'parent_sigla', 'hierarchy_level']
    missing = [col for col in required_columns if col not in columns]
    
    if missing:
        print(f"❌ Colonne mancanti: {missing}")
        print("   Riavviare QGIS e riconnettersi al database!")
        return False
    else:
        print("✅ Tutte le colonne richieste esistono")
        return True


def test_table_names_updated(cursor):
    """Verifica che i nomi delle tabelle siano stati aggiornati"""
    print("\n=== Test Nomi Tabelle ===")
    
    cursor.execute("""
        SELECT DISTINCT nome_tabella 
        FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella LIKE '%TMA%' OR nome_tabella LIKE '%tma%'
        ORDER BY nome_tabella
    """)
    
    table_names = [row[0] for row in cursor.fetchall()]
    
    correct = True
    for name in table_names:
        if name == 'TMA materiali archeologici':
            print(f"✅ '{name}' (corretto)")
        elif name == 'TMA materiali ripetibili':
            print(f"✅ '{name}' (corretto)")
        elif name in ['tma_materiali_archeologici', 'tma_materiali_ripetibili']:
            print(f"❌ '{name}' (nome vecchio - deve essere aggiornato)")
            correct = False
        else:
            print(f"? '{name}'")
    
    return correct


def test_hierarchy_data(cursor):
    """Verifica che i dati gerarchici siano corretti"""
    print("\n=== Test Dati Gerarchici ===")
    
    # Test località (10.3) - no parent
    cursor.execute("""
        SELECT COUNT(*) 
        FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'TMA materiali archeologici'
        AND tipologia_sigla = '10.3'
        AND parent_sigla IS NULL
    """)
    
    localita_no_parent = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'TMA materiali archeologici'
        AND tipologia_sigla = '10.3'
    """)
    
    localita_total = cursor.fetchone()[0]
    
    print(f"Località (10.3): {localita_no_parent}/{localita_total} senza parent (corretto)")
    
    # Test area (10.7) - with località parent
    cursor.execute("""
        SELECT COUNT(*) 
        FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'TMA materiali archeologici'
        AND tipologia_sigla = '10.7'
        AND parent_sigla IS NOT NULL
        AND parent_sigla LIKE 'LOC%'
    """)
    
    area_with_loc_parent = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'TMA materiali archeologici'
        AND tipologia_sigla = '10.7'
    """)
    
    area_total = cursor.fetchone()[0]
    
    print(f"Area (10.7): {area_with_loc_parent}/{area_total} con parent località")
    
    # Test settore (10.15) - with area parent
    cursor.execute("""
        SELECT COUNT(*) 
        FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'TMA materiali archeologici'
        AND tipologia_sigla = '10.15'
        AND parent_sigla IS NOT NULL
        AND parent_sigla LIKE 'AREA%'
    """)
    
    settore_with_area_parent = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'TMA materiali archeologici'
        AND tipologia_sigla = '10.15'
    """)
    
    settore_total = cursor.fetchone()[0]
    
    print(f"Settore (10.15): {settore_with_area_parent}/{settore_total} con parent area")
    
    return (localita_no_parent == localita_total and 
            area_with_loc_parent == area_total and 
            settore_with_area_parent == settore_total)


def test_widget_functionality(cursor):
    """Test simulato del funzionamento dei widget"""
    print("\n=== Test Funzionalità Widget ===")
    
    # Simula selezione di località per area
    print("\n1. Simulazione selezione località per Area:")
    cursor.execute("""
        SELECT sigla, sigla_estesa 
        FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'TMA materiali archeologici'
        AND tipologia_sigla = '10.3'
        ORDER BY sigla
        LIMIT 3
    """)
    
    print("   Opzioni località disponibili:")
    for sigla, nome in cursor.fetchall():
        print(f"   - {sigla} - {nome}")
    
    # Simula filtro area per località
    print("\n2. Simulazione filtro area per località 'LOC01':")
    cursor.execute("""
        SELECT sigla, sigla_estesa 
        FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'TMA materiali archeologici'
        AND tipologia_sigla = '10.7'
        AND parent_sigla = 'LOC01'
        ORDER BY sigla
        LIMIT 5
    """)
    
    results = cursor.fetchall()
    if results:
        print("   Aree filtrate per LOC01:")
        for sigla, nome in results:
            print(f"   - {sigla} - {nome}")
        return True
    else:
        print("   ❌ Nessuna area trovata per LOC01")
        return False


def main():
    # Database path
    db_path = os.path.expanduser("~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite")
    
    if not os.path.exists(db_path):
        print(f"Database non trovato in: {db_path}")
        return 1
        
    print(f"Test finale Thesaurus fix in: {db_path}")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        db_ok = test_database_updated(cursor)
        names_ok = test_table_names_updated(cursor)
        hierarchy_ok = test_hierarchy_data(cursor)
        widgets_ok = test_widget_functionality(cursor)
        
        print("\n" + "=" * 60)
        print("RIEPILOGO")
        print("=" * 60)
        
        all_ok = db_ok and names_ok and hierarchy_ok and widgets_ok
        
        if all_ok:
            print("\n✅ TUTTI I TEST PASSATI!")
            print("\nI widget area e settore nel Thesaurus dovrebbero ora:")
            print("- Mostrarsi quando si seleziona tipologia 10.7 o 10.15")
            print("- Permettere la selezione dei parent corretti")
            print("- Salvare correttamente le relazioni gerarchiche")
        else:
            print("\n⚠️  ALCUNI TEST FALLITI")
            if not db_ok:
                print("\n1. Riavviare QGIS")
                print("2. Riconnettersi al database")
                print("3. L'update dovrebbe eseguirsi automaticamente")
        
    except sqlite3.Error as e:
        print(f"\n❌ Errore: {e}")
        return 1
        
    finally:
        conn.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())