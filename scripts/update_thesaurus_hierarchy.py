#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per aggiungere campi gerarchici alla tabella thesaurus
e inserire dati con relazioni località->area->settore
"""

import sqlite3
import os
import sys

def add_hierarchy_fields(cursor):
    """Aggiunge i campi per la gerarchia se non esistono."""
    # Verifica campi esistenti
    cursor.execute("PRAGMA table_info(pyarchinit_thesaurus_sigle)")
    columns = [col[1] for col in cursor.fetchall()]
    
    fields_to_add = []
    if 'id_parent' not in columns:
        fields_to_add.append(('id_parent', 'INTEGER'))
    if 'parent_sigla' not in columns:
        fields_to_add.append(('parent_sigla', 'TEXT'))
    if 'hierarchy_level' not in columns:
        fields_to_add.append(('hierarchy_level', 'INTEGER'))
    
    for field_name, field_type in fields_to_add:
        try:
            cursor.execute(f"ALTER TABLE pyarchinit_thesaurus_sigle ADD COLUMN {field_name} {field_type}")
            print(f"✓ Aggiunto campo {field_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                raise

def clear_tma_thesaurus(cursor):
    """Rimuove i dati esistenti del thesaurus TMA per reimportarli con gerarchia."""
    cursor.execute("""
        DELETE FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'tma_materiali_archeologici' 
        AND tipologia_sigla IN ('10.18', '10.7', '10.19')
    """)
    print("✓ Rimossi dati esistenti per località, area e settore")

def insert_hierarchical_data(cursor):
    """Inserisce i dati con relazioni gerarchiche."""
    
    # 10.18 - Località (livello 1)
    localita_data = [
        # id, sigla, sigla_estesa
        (1, 'LOC1', 'Roma'),
        (2, 'LOC2', 'Milano'),
        (3, 'LOC3', 'Napoli'),
        (4, 'LOC4', 'Firenze'),
        (5, 'LOC5', 'Venezia'),
    ]
    
    print("\nInserimento Località (10.18):")
    for loc_id, sigla, sigla_estesa in localita_data:
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua, hierarchy_level)
            VALUES (?, 'tma_materiali_archeologici', ?, ?, '10.18', 'it', 1)
        """, (1000 + loc_id, sigla, sigla_estesa))
        print(f"  ✓ {sigla} - {sigla_estesa}")
    
    # 10.7 - Area (livello 2) con relazione a località
    area_data = [
        # id, sigla, sigla_estesa, id_localita, sigla_localita
        # Aree per Roma (LOC1)
        (11, 'A1', 'Area Fori', 1, 'LOC1'),
        (12, 'A2', 'Area Colosseo', 1, 'LOC1'),
        (13, 'A3', 'Area Palatino', 1, 'LOC1'),
        
        # Aree per Milano (LOC2)
        (21, 'A1', 'Area Duomo', 2, 'LOC2'),
        (22, 'A2', 'Area Castello', 2, 'LOC2'),
        
        # Aree per Napoli (LOC3)
        (31, 'A1', 'Area Porto', 3, 'LOC3'),
        (32, 'A2', 'Area Centro Storico', 3, 'LOC3'),
        
        # Aree per Firenze (LOC4)
        (41, 'A1', 'Area Santa Croce', 4, 'LOC4'),
        (42, 'A2', 'Area Signoria', 4, 'LOC4'),
        
        # Aree per Venezia (LOC5)
        (51, 'A1', 'Area San Marco', 5, 'LOC5'),
        (52, 'A2', 'Area Rialto', 5, 'LOC5'),
    ]
    
    print("\nInserimento Aree (10.7) con relazioni a Località:")
    for area_id, sigla, sigla_estesa, id_localita, sigla_localita in area_data:
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua, 
             id_parent, parent_sigla, hierarchy_level)
            VALUES (?, 'tma_materiali_archeologici', ?, ?, '10.7', 'it', ?, ?, 2)
        """, (2000 + area_id, sigla, sigla_estesa, 1000 + id_localita, sigla_localita))
        print(f"  ✓ {sigla} - {sigla_estesa} (Località: {sigla_localita})")
    
    # 10.19 - Settore (livello 3) con relazione ad area e località
    settore_data = [
        # id, sigla, sigla_estesa, id_area, id_localita
        # Settori per Roma - Area Fori (A1)
        (111, 'S1', 'Settore Nord', 11, 1),
        (112, 'S2', 'Settore Sud', 11, 1),
        (113, 'S3', 'Settore Est', 11, 1),
        
        # Settori per Roma - Area Colosseo (A2)
        (121, 'S1', 'Settore Arena', 12, 1),
        (122, 'S2', 'Settore Sotterranei', 12, 1),
        
        # Settori per Milano - Area Duomo (A1)
        (211, 'S1', 'Settore Piazza', 21, 2),
        (212, 'S2', 'Settore Cattedrale', 21, 2),
        
        # Settori per Napoli - Area Porto (A1)
        (311, 'S1', 'Settore Molo', 31, 3),
        (312, 'S2', 'Settore Arsenale', 31, 3),
        
        # Altri settori...
    ]
    
    print("\nInserimento Settori (10.19) con relazioni ad Area:")
    for sett_id, sigla, sigla_estesa, id_area, id_localita in settore_data:
        # Trova la sigla dell'area
        cursor.execute("SELECT sigla FROM pyarchinit_thesaurus_sigle WHERE id_thesaurus_sigle = ?", (2000 + id_area,))
        area_sigla = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua, 
             id_parent, parent_sigla, hierarchy_level)
            VALUES (?, 'tma_materiali_archeologici', ?, ?, '10.19', 'it', ?, ?, 3)
        """, (3000 + sett_id, sigla, sigla_estesa, 2000 + id_area, area_sigla))
        print(f"  ✓ {sigla} - {sigla_estesa} (Area: {area_sigla})")

def main():
    # Database path
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database non trovato in: {db_path}")
        return 1
        
    print(f"Uso database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Aggiornamento struttura thesaurus per supportare gerarchie...")
        print("=" * 60)
        
        # 1. Aggiungi campi per gerarchia
        add_hierarchy_fields(cursor)
        
        # 2. Rimuovi dati esistenti
        clear_tma_thesaurus(cursor)
        
        # 3. Inserisci nuovi dati con gerarchia
        insert_hierarchical_data(cursor)
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ Operazione completata con successo!")
        print("\nLa gerarchia è ora:")
        print("  Località (10.18)")
        print("    └─> Area (10.7)")
        print("          └─> Settore (10.19)")
        
    except sqlite3.Error as e:
        print(f"\n❌ Errore durante l'aggiornamento: {e}")
        conn.rollback()
        return 1
        
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())