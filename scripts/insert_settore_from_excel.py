#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per inserire i valori settore dall'Excel con relazioni alle aree
"""

import sqlite3
import os
import sys

def insert_settore_values(cursor):
    """Inserisce i valori settore dal file Excel con relazioni alle aree."""
    
    # Prima rimuovi i valori settore esistenti
    cursor.execute("""
        DELETE FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'tma_materiali_archeologici' 
        AND tipologia_sigla = '10.19'
    """)
    print("✓ Rimossi valori settore (10.19) esistenti")
    
    # Valori esatti dall'Excel
    settore_values = [
        (1, 1, 4, 'Area del muro Alì'),
        (2, 1, 4, 'Colmata Medio Minoica'),
        (3, 1, 4, 'Strada ad Ovest del Piazzale I'),
        (4, 1, 7, 'Area dei magazzini 4 e 5'),
        (5, 1, 7, 'Zona a S del magazzino 3'),
        (6, 1, 7, 'Zona Cisterna (a W del Museo)'),
        (7, 1, 12, 'Gradinata teatrale IV'),
        (8, 1, 12, 'Koulura I'),
        (9, 1, 12, 'Koulura II'),
        (10, 1, 12, 'Koulura III'),
        (11, 1, 17, 'Area 99'),
        (12, 1, 17, 'Canale a sud del Piazzale LXX'),
        (13, 1, 17, 'Capanna neolitica'),
        (14, 1, 17, 'Pozzo a Nord-Est del Vano LXXIII'),
        (15, 1, 19, 'Area della "cava di calcare"'),
        (16, 1, 19, 'Grotta M'),
        (17, 1, 20, 'Bastione Ovest'),
        (18, 1, 20, 'Canale Minoico'),
        (19, 1, 20, 'Casa A'),
        (20, 1, 20, 'Casa B'),
        (21, 1, 20, 'Casa C'),
        (22, 1, 20, 'Grande frana'),
        (23, 1, 20, 'Strada dal nord'),
        (24, 1, 21, 'Zona M'),
        (25, 1, 21, 'Zona N'),
        (26, 1, 23, 'Canale (Edificio 103/104)'),
        (27, 1, 23, 'Edificio XL/101'),
        (28, 1, 23, 'Edificio XLI/102'),
        (29, 1, 23, 'Edificio XLII/103'),
        (30, 1, 23, 'Edificio XLIII/104'),
        (31, 1, 26, 'Bastione II "immondezzaio"'),
        (32, 1, 26, 'Propileo II'),
        (33, 1, 26, 'Rampa LII'),
        (34, 1, 37, 'Grande Tholos'),
        (35, 1, 37, 'Piccola tholos δ'),
        (36, 1, 41, 'Settore Nord'),
        (37, 1, 41, 'Settore Sud'),
        (38, 1, 41, 'Settore Sud-Est'),
        (39, 2, 47, 'Forno'),
        (40, 2, 54, 'Magazzino dei sacelli'),
        (41, 2, 56, 'Edificio Ovest'),
        (42, 2, 57, 'Casa Est (Case Laviosa)'),
        (43, 2, 57, 'Casa Ovest (Case Laviosa)'),
        (44, 2, 58, 'Fornace B'),
        (45, 2, 73, 'Avancorpo Orientale'),
        (46, 2, 77, 'Portico'),
        (47, 2, 79, 'Complesso della Mazza di Breccia'),
        (48, 2, 79, 'Tomba degli Ori'),
        (49, 2, 80, 'Camerette a Sud'),
        (50, 2, 80, 'Vani ad est della Tholos A'),
        (51, 2, 81, 'Area a sud della Tholos B'),
        (52, 2, 81, 'Ossario a sud della Tholos B'),
    ]
    
    print("\nInserimento valori settore (10.19) con relazioni:")
    inserted = 0
    
    for id_settore, id_localita, id_area, settore_nome in settore_values:
        # Usa SETT + numero come sigla
        sigla = f"SETT{id_settore:03d}"
        # ID per la gerarchia (3000 + id)
        id_thesaurus = 3000 + id_settore
        # ID parent area (2000 + id_area)
        id_parent = 2000 + id_area
        parent_sigla = f"AREA{id_area:03d}"
        
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua, 
             id_parent, parent_sigla, hierarchy_level)
            VALUES (?, 'tma_materiali_archeologici', ?, ?, '10.19', 'it', ?, ?, 3)
        """, (id_thesaurus, sigla, settore_nome, id_parent, parent_sigla))
        
        if inserted < 15 or inserted % 10 == 0:  # Mostra solo alcuni per non inondare l'output
            print(f"  ✓ {id_settore}. {settore_nome} (Area: {parent_sigla})")
        inserted += 1
    
    print(f"  ... (totale {inserted} settori inseriti)")
    
    return inserted

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
        print("Inserimento valori settore dall'Excel...")
        print("=" * 60)
        
        inserted = insert_settore_values(cursor)
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Operazione completata!")
        print(f"   Totale valori inseriti: {inserted}")
        
        # Verifica per area
        print("\nRiepilogo settori per alcune aree principali:")
        cursor.execute("""
            SELECT parent_sigla, COUNT(*) as cnt
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = '10.19'
            GROUP BY parent_sigla
            ORDER BY cnt DESC
            LIMIT 10
        """)
        
        for parent, count in cursor.fetchall():
            cursor.execute("""
                SELECT sigla_estesa 
                FROM pyarchinit_thesaurus_sigle 
                WHERE sigla = ?
            """, (parent,))
            area_name = cursor.fetchone()
            if area_name:
                print(f"   {parent} ({area_name[0]}): {count} settori")
            
    except sqlite3.Error as e:
        print(f"\n❌ Errore: {e}")
        conn.rollback()
        return 1
        
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())