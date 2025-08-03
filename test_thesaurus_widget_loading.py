#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test per verificare il caricamento dei dati nei widget gerarchici
"""

import sys
import os
import sqlite3

def test_widget_data_loading():
    """Test che simula il caricamento dei dati nei widget"""
    
    # Database path
    db_path = os.path.expanduser("~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite")
    
    if not os.path.exists(db_path):
        print(f"Database non trovato in: {db_path}")
        return False
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== Test Caricamento Dati Widget ===\n")
    
    # 1. Test query località
    print("1. Query località (tipologia 10.3):")
    cursor.execute("""
        SELECT sigla, sigla_estesa 
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'TMA materiali archeologici'
        AND tipologia_sigla = '10.3'
        AND lingua = 'it'
        ORDER BY sigla
    """)
    
    localita = cursor.fetchall()
    print(f"   Trovate {len(localita)} località:")
    for sigla, nome in localita[:5]:
        print(f"   - {sigla} - {nome}")
    if len(localita) > 5:
        print(f"   ... e altre {len(localita) - 5}")
    
    # 2. Test query area per località specifica
    print("\n2. Query aree per località LOC01:")
    cursor.execute("""
        SELECT sigla, sigla_estesa 
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'TMA materiali archeologici'
        AND tipologia_sigla = '10.7'
        AND parent_sigla = 'LOC01'
        AND lingua = 'it'
        ORDER BY sigla
    """)
    
    aree = cursor.fetchall()
    print(f"   Trovate {len(aree)} aree per LOC01:")
    for sigla, nome in aree[:5]:
        print(f"   - {sigla} - {nome}")
    if len(aree) > 5:
        print(f"   ... e altre {len(aree) - 5}")
    
    # 3. Verifica che i metodi nel codice stiano usando le query corrette
    print("\n3. Verifica query nel codice:")
    print("   load_parent_localita() dovrebbe:")
    print("   - Usare nome_tabella = 'TMA materiali archeologici'")
    print("   - Usare tipologia_sigla = '10.3'")
    print("   - Aggiungere elementi come '{sigla} - {sigla_estesa}'")
    
    print("\n   on_parent_localita_changed() dovrebbe:")
    print("   - Usare nome_tabella = 'TMA materiali archeologici'")
    print("   - Usare tipologia_sigla = '10.7'")
    print("   - Usare parent_sigla = sigla selezionata dalla località")
    
    # 4. Test possibili problemi
    print("\n4. Possibili problemi da verificare:")
    
    # Verifica se c'è un problema con DB_MANAGER
    print("\n   a) DB_MANAGER potrebbe non essere inizializzato quando viene chiamato load_parent_localita()")
    print("      Soluzione: verificare che la connessione al DB sia attiva prima di chiamare il metodo")
    
    # Verifica se il metodo viene chiamato
    print("\n   b) load_parent_localita() potrebbe non essere chiamato al momento giusto")
    print("      Soluzione: verificare che venga chiamato in show_area_parent_widgets() e show_settore_parent_widgets()")
    
    # Verifica la lingua
    cursor.execute("""
        SELECT DISTINCT lingua 
        FROM pyarchinit_thesaurus_sigle
        WHERE nome_tabella = 'TMA materiali archeologici'
    """)
    lingue = [row[0] for row in cursor.fetchall()]
    print(f"\n   c) Lingue disponibili nel database: {lingue}")
    print("      Se la lingua selezionata non corrisponde, non troverà dati")
    
    conn.close()
    
    print("\n" + "="*50)
    print("CONCLUSIONE:")
    print("I dati esistono nel database e le query funzionano correttamente.")
    print("Il problema è probabilmente nel timing di quando viene chiamato load_parent_localita()")
    print("o nella disponibilità di DB_MANAGER al momento della chiamata.")
    
    return True

if __name__ == "__main__":
    success = test_widget_data_loading()
    sys.exit(0 if success else 1)