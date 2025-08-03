#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per inserire i valori macd (Definizione) dall'Excel
"""

import sqlite3
import os
import sys

def insert_macd_values(cursor):
    """Inserisce i valori macd dal file Excel."""
    
    # Prima rimuovi i valori macd esistenti
    cursor.execute("""
        DELETE FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella = 'tma_materiali_archeologici' 
        AND tipologia_sigla = '10.15'
    """)
    print("✓ Rimossi valori macd (10.15) esistenti")
    
    # Valori esatti dall'Excel
    macd_values = [
        (1, 'aperta generica'),
        (2, 'pentola'),
        (3, 'pentola tripodata'),
        (4, 'louter'),
        (5, 'bacino'),
        (6, 'scodellone'),
        (7, 'vassoio'),
        (8, 'vassoio tripodato'),
        (9, 'piatto'),
        (10, 'fruttiera'),
        (11, 'cratere'),
        (12, 'craterisco'),
        (13, 'kalathos'),
        (14, 'vaso a cestello'),
        (15, 'pisside'),
        (16, 'vaso portafiori'),
        (17, 'bicchiere'),
        (18, 'tazza'),
        (19, 'boccale'),
        (20, 'coppa'),
        (21, 'coppa a basso piede'),
        (22, 'coppa ad alto piede'),
        (23, 'coppa da champagne'),
        (24, 'skyphos'),
        (25, 'skouteli'),
        (26, 'ciotola'),
        (27, 'chiusa generica'),
        (28, 'pithos'),
        (29, 'pitharaki'),
        (30, 'vasi pithoidi'),
        (31, 'anfora'),
        (32, 'anfora a staffa'),
        (33, 'amphoriskos'),
        (34, 'hydria'),
        (35, 'hydrietta'),
        (36, 'fiasca'),
        (37, 'brocca'),
        (38, 'brocchetta'),
        (39, 'lattiera'),
        (40, 'stamnos'),
        (41, 'olla'),
        (42, 'olletta'),
        (43, 'teiera'),
        (44, 'bricco'),
        (45, 'poppatoio'),
        (46, 'unguentario'),
        (47, 'alabastron'),
        (48, 'lucerna'),
        (49, 'lampada'),
        (50, 'candeliere'),
        (51, 'braciere'),
        (52, 'portabraci'),
        (53, 'paletta da fuoco'),
        (54, 'fire-box'),
        (55, 'incensiere'),
        (56, 'alare'),
        (57, 'vaso a corna'),
        (58, 'attingitoio'),
        (59, 'colatoio'),
        (60, 'grattugia'),
        (61, 'coperchio'),
        (62, 'piedistallo'),
        (63, 'tubi'),
        (64, 'rhyton'),
        (65, 'vasi askoidi'),
        (66, 'kernos'),
        (67, 'vaso ad anello'),
        (68, 'saliera'),
        (69, 'vasi multipli'),
        (70, 'vasi a scomparti'),
        (71, 'vasi a gabbietta'),
        (72, 'tavola d\'offerta'),
        (73, 'larnax'),
        (74, 'ruota da vasaio'),
        (75, 'peso'),
        (76, 'fuseruola'),
    ]
    
    print("\nInserimento valori macd (Definizione - 10.15):")
    inserted = 0
    
    for id_val, definizione in macd_values:
        # Usa MACD + numero come sigla
        sigla = f"MACD{id_val:02d}"
        
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('tma_materiali_archeologici', ?, ?, '10.15', 'it')
        """, (sigla, definizione))
        
        if inserted < 20 or inserted % 20 == 0:  # Mostra solo alcuni per non inondare l'output
            print(f"  ✓ {id_val}. {definizione}")
        inserted += 1
    
    print(f"  ... (totale {inserted} definizioni inserite)")
    
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
        print("Inserimento valori macd (Definizione) dall'Excel...")
        print("=" * 60)
        
        inserted = insert_macd_values(cursor)
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Operazione completata!")
        print(f"   Totale valori inseriti: {inserted}")
        
        # Verifica per categoria
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = '10.15' AND (sigla_estesa LIKE '%coppa%' OR sigla_estesa LIKE '%tazza%')
        """)
        coppe_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle 
            WHERE tipologia_sigla = '10.15' AND sigla_estesa LIKE '%vaso%'
        """)
        vasi_count = cursor.fetchone()[0]
        
        print(f"\nRiepilogo per tipo:")
        print(f"   Coppe e tazze: {coppe_count}")
        print(f"   Vasi vari: {vasi_count}")
        print(f"   Altri tipi: {inserted - coppe_count - vasi_count}")
            
    except sqlite3.Error as e:
        print(f"\n❌ Errore: {e}")
        conn.rollback()
        return 1
        
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())