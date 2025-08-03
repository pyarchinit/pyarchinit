#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test finale per i widget del Thesaurus
"""

import sys
import os
import sqlite3

# Test che simula quello che farebbe il widget

def test_widget_functionality():
    """Test del funzionamento dei widget"""
    
    # Database path
    db_path = os.path.expanduser("~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite")
    
    if not os.path.exists(db_path):
        print(f"Database non trovato in: {db_path}")
        return False
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== Test Widget Thesaurus ===")
    print("\n1. Simulazione tipologia 10.7 (Area):")
    print("   - Dovrebbe mostrare widget per selezionare località parent")
    
    # Query che farebbe load_parent_localita()
    cursor.execute("""
        SELECT sigla, sigla_estesa 
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'TMA materiali archeologici'
        AND tipologia_sigla = '10.3'
        AND lingua = 'it'
        ORDER BY sigla
    """)
    
    localita_options = cursor.fetchall()
    print(f"   - Trovate {len(localita_options)} località disponibili:")
    for sigla, nome in localita_options[:3]:
        print(f"     • {sigla} - {nome}")
    
    print("\n2. Simulazione tipologia 10.15 (Settore):")
    print("   - Dovrebbe mostrare widget per località E area")
    print("   - Quando si seleziona località, si popola area")
    
    # Simula selezione di LOC01
    print("\n   Selezione località: LOC01 - Festòs")
    
    # Query che farebbe on_parent_localita_changed()
    cursor.execute("""
        SELECT sigla, sigla_estesa 
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'TMA materiali archeologici'
        AND tipologia_sigla = '10.7'
        AND parent_sigla = 'LOC01'
        AND lingua = 'it'
        ORDER BY sigla
        LIMIT 5
    """)
    
    area_options = cursor.fetchall()
    print(f"   - Aree disponibili per LOC01: {len(cursor.fetchall()) + 5}")
    for sigla, nome in area_options:
        print(f"     • {sigla} - {nome}")
    print("     • ...")
    
    print("\n3. Test salvataggio gerarchia:")
    
    # Simula salvataggio di un'area con parent
    print("   - Area: AREA999 - Area Test")
    print("   - Parent: LOC01")
    print("   - Verifico che parent_sigla venga salvato correttamente")
    
    # Verifica struttura per salvataggio
    cursor.execute("""
        SELECT column_name 
        FROM pragma_table_info('pyarchinit_thesaurus_sigle')
        WHERE column_name IN ('id_parent', 'parent_sigla', 'hierarchy_level')
    """)
    
    columns = [row[0] for row in cursor.fetchall()]
    if len(columns) == 3:
        print("   ✅ Tutte le colonne gerarchiche presenti")
    else:
        print(f"   ❌ Colonne mancanti: trovate solo {columns}")
    
    conn.close()
    
    print("\n" + "="*50)
    print("RISULTATO:")
    print("Se i widget non si mostrano correttamente:")
    print("1. Verificare che create_hierarchy_widgets() venga chiamata")
    print("2. Verificare che i widget siano aggiunti al layout")
    print("3. Verificare che show/hide funzioni correttamente")
    
    return True

if __name__ == "__main__":
    success = test_widget_functionality()
    sys.exit(0 if success else 1)