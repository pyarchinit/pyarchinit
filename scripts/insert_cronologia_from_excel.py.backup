#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per inserire i valori cronologia dall'Excel
"""

import sqlite3
import os
import sys

def insert_cronologia_values(cursor):
    """Inserisce i valori cronologia dal file Excel."""
    
    # Prima rimuovi i valori cronologia esistenti
    cursor.execute("""
        DELETE FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'tma_materiali_archeologici' 
        AND tipologia_sigla = '10.16'
    """)
    print("✓ Rimossi valori cronologia (10.16) esistenti")
    
    # Valori esatti dall'Excel (stessi di dtzg)
    cronologia_values = [
        (1, 'Neolitico', ''),
        (2, 'Neolitico Iniziale', '6800-6400'),
        (3, 'Neolitico Antico', '6400-5800'),
        (4, 'Neolitico Medio', '5800-5300'),
        (5, 'Neolitico Tardo', '5300-4500'),
        (6, 'Neolitico Finale', '4500-3200'),
        (7, 'Prepalaziale', ''),
        (8, 'Antico Minoico I', '3200-2900'),
        (9, 'Antico Minoico IIA', '2900-2650'),
        (10, 'Antico Minoico IIB', '2650-2200'),
        (11, 'Antico Minoico III', '2200-2050'),
        (12, 'Medio Minoico IA', '2050-1950/1900'),
        (13, 'Protopalaziale', ''),
        (14, 'Medio Minoico IB', '1950/1900-1800'),
        (15, 'Medio Minoico IIA', '1800-1750'),
        (16, 'Medio Minoico IIB', '1750-1700'),
        (17, 'Neopalaziale', ''),
        (18, 'Medio Minoico III', '1700-1600'),
        (19, 'Medio Minoico IIIA', '1700-1650/30'),
        (20, 'Medio Minoico IIIB', '1650/30-1600'),
        (21, 'Tardo Minoico I', '1600-1475'),
        (22, 'Tardo Minoico IA', '1600-1525'),
        (23, 'Tardo Minoico IB', '1525-1475'),
        (24, 'Tardo Minoico II', '1475-1425'),
        (25, 'Tardo Minoico IIIA', '1425-1300'),
        (26, 'Tardo Minoico IIIA1', '1425-1370'),
        (27, 'Tardo Minoico IIIA2', '1370-1300'),
        (28, 'Tardo Minoico IIIB', '1300-1200'),
        (29, 'Tardo Minoico IIIB iniziale', '1300-1250'),
        (30, 'Tardo Minoico IIIB finale', '1250/30-1200/1180'),
        (31, 'Tardo Minoico IIIC', '1200-1070'),
        (32, 'Tardo Minoico IIIC iniziale', '1200/1180-1150/30'),
        (33, 'Tardo Minoico IIIC finale (tardo)', '1150/30-1100/1070'),
        (34, 'Subminoico', '1100/1070-1000/970'),
        (35, 'PG/G/OR', ''),
        (36, 'Protogeometrico', '1050/970-810'),
        (37, 'Geometrico', '810-710'),
        (38, 'Orientalizzante', '710-600'),
        (39, 'Arcaico', '600-480'),
        (40, 'Cl/Ell', ''),
        (41, 'Classico', '480-323'),
        (42, 'Ellenistico', '323-74'),
        (43, 'Rom/Med', ''),
        (44, 'Romano', '74 a.C.-300 d.C.'),
        (45, 'Protobizantino', '300-824 d.C.'),
        (46, 'Arabo', '824-961 d.C.'),
        (47, 'Neobizantino', '961-1204 d.C.'),
        (48, 'Moderno', ''),
        (49, 'Epoca veneziana', '1204-1669 d.C.'),
        (50, 'Epoca turca', '1669-1899 d.C.'),
        (51, 'Moderno', ''),
        (52, 'Incerti', ''),
    ]
    
    print("\nInserimento valori cronologia (10.16):")
    inserted = 0
    
    for id_val, periodo, cronologia_assoluta in cronologia_values:
        # Usa CRON + numero come sigla
        sigla = f"CRON{id_val:02d}"
        
        # Combina periodo e cronologia per sigla_estesa
        if cronologia_assoluta:
            sigla_estesa = f"{periodo} ({cronologia_assoluta})"
        else:
            sigla_estesa = periodo
        
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('tma_materiali_archeologici', ?, ?, '10.16', 'it')
        """, (sigla, sigla_estesa))
        
        if inserted < 15 or inserted % 10 == 0:  # Mostra solo alcuni per non inondare l'output
            print(f"  ✓ {id_val}. {periodo}" + (f" ({cronologia_assoluta})" if cronologia_assoluta else ""))
        inserted += 1
    
    print(f"  ... (totale {inserted} cronologie inserite)")
    
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
        print("Inserimento valori cronologia dall'Excel...")
        print("=" * 60)
        
        inserted = insert_cronologia_values(cursor)
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Operazione completata!")
        print(f"   Totale valori inseriti: {inserted}")
        
        # Verifica per periodo
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = '10.16' AND sigla_estesa LIKE '%Neolitico%'
        """)
        neolitico_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = '10.16' AND sigla_estesa LIKE '%Minoico%'
        """)
        minoico_count = cursor.fetchone()[0]
        
        print(f"\nRiepilogo per periodo:")
        print(f"   Periodi Neolitico: {neolitico_count}")
        print(f"   Periodi Minoico: {minoico_count}")
        print(f"   Altri periodi: {inserted - neolitico_count - minoico_count}")
            
    except sqlite3.Error as e:
        print(f"\n❌ Errore: {e}")
        conn.rollback()
        return 1
        
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())