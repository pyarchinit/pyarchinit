#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per inserire i valori del thesaurus TMA nel database
Verifica prima se i valori esistono già per evitare duplicati
"""

import sqlite3
import os
import sys

# Definizione dei valori del thesaurus TMA
THESAURUS_DATA = {
    '10.1': {  # Denominazione collocazione (ldcn)
        'description': 'Denominazione collocazione',
        'values': [
            ('MAG01', 'Magazzino 1'),
            ('MAG02', 'Magazzino 2'),
            ('DEP01', 'Deposito 1'),
            ('LAB01', 'Laboratorio 1'),
        ]
    },
    '10.2': {  # Saggio
        'description': 'Saggio',
        'values': [
            ('SAG1', 'Saggio 1'),
            ('SAG2', 'Saggio 2'),
            ('SAG3', 'Saggio 3'),
            ('SAGA', 'Saggio A'),
            ('SAGB', 'Saggio B'),
        ]
    },
    '10.3': {  # Vano/Locus
        'description': 'Vano/Locus',
        'values': [
            ('V1', 'Vano 1'),
            ('V2', 'Vano 2'),
            ('V3', 'Vano 3'),
            ('L1', 'Locus 1'),
            ('L2', 'Locus 2'),
            ('AMB1', 'Ambiente 1'),
            ('AMB2', 'Ambiente 2'),
        ]
    },
    '10.4': {  # Nome scavo
        'description': 'Nome scavo',
        'values': [
            ('SCA01', 'Scavo archeologico 2024'),
            ('SCA02', 'Scavo di emergenza'),
            ('RIC01', 'Ricognizione superficiale'),
            ('PREV01', 'Scavo preventivo'),
        ]
    },
    '10.7': {  # Area
        'description': 'Area',
        'values': [
            ('A', 'Area A'),
            ('B', 'Area B'),
            ('C', 'Area C'),
            ('D', 'Area D'),
            ('1000', 'Area 1000'),
            ('2000', 'Area 2000'),
            ('3000', 'Area 3000'),
        ]
    },
    '10.10': {  # Tipologia collocazione (ldct)
        'description': 'Tipologia collocazione',
        'values': [
            ('MAG', 'Magazzino'),
            ('DEP', 'Deposito'),
            ('LAB', 'Laboratorio'),
            ('MUS', 'Museo'),
            ('ARCH', 'Archivio'),
        ]
    },
    '10.11': {  # Tipo acquisizione (aint)
        'description': 'Tipo acquisizione',
        'values': [
            ('SCA', 'Scavo'),
            ('RIC', 'Ricognizione'),
            ('REC', 'Recupero'),
            ('RIN', 'Rinvenimento fortuito'),
            ('DON', 'Donazione'),
            ('ACQ', 'Acquisto'),
        ]
    },
    '10.12': {  # Tipo fotografia (ftap)
        'description': 'Tipo fotografia',
        'values': [
            ('GEN', 'Generale'),
            ('DET', 'Dettaglio'),
            ('MAC', 'Macro'),
            ('MIC', 'Microscopica'),
            ('RAD', 'Radiografia'),
            ('UV', 'Ultravioletto'),
        ]
    },
    '10.13': {  # Tipo disegno (drat)
        'description': 'Tipo disegno',
        'values': [
            ('RIL', 'Rilievo'),
            ('RIC', 'Ricostruzione'),
            ('SEZ', 'Sezione'),
            ('PRO', 'Profilo'),
            ('DEC', 'Decorazione'),
            ('SCH', 'Schema'),
        ]
    },
    '10.15': {  # Fascia cronologica (dtzg)
        'description': 'Fascia cronologica',
        'values': [
            ('PREI', 'Preistoria'),
            ('PROT', 'Protostoria'),
            ('ARC', 'Età arcaica'),
            ('CLA', 'Età classica'),
            ('ELL', 'Età ellenistica'),
            ('ROM', 'Età romana'),
            ('TARD', 'Tardoantico'),
            ('MED', 'Medioevo'),
            ('RIN', 'Rinascimento'),
            ('MOD', 'Età moderna'),
            ('CONT', 'Età contemporanea'),
        ]
    },
    '10.18': {  # Località
        'description': 'Località',
        'values': [
            ('LOC01', 'Località 1'),
            ('LOC02', 'Località 2'),
            ('LOC03', 'Località 3'),
            ('CENTR', 'Centro storico'),
            ('PERIF', 'Periferia'),
        ]
    },
    '10.19': {  # Settore
        'description': 'Settore',
        'values': [
            ('S1', 'Settore 1'),
            ('S2', 'Settore 2'),
            ('S3', 'Settore 3'),
            ('S4', 'Settore 4'),
            ('SA', 'Settore A'),
            ('SB', 'Settore B'),
            ('SC', 'Settore C'),
            ('SD', 'Settore D'),
            ('NE', 'Nord-Est'),
            ('NO', 'Nord-Ovest'),
            ('SE', 'Sud-Est'),
            ('SO', 'Sud-Ovest'),
        ]
    },
}

def insert_thesaurus_values(cursor, nome_tabella='tma_materiali_archeologici', lingua='it'):
    """Insert thesaurus values into database."""
    inserted_count = 0
    skipped_count = 0
    
    for tipologia_sigla, data in THESAURUS_DATA.items():
        print(f"\n{tipologia_sigla} - {data['description']}:")
        
        for sigla, sigla_estesa in data['values']:
            # Check if value already exists
            cursor.execute("""
                SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = ? AND tipologia_sigla = ? AND sigla = ? AND lingua = ?
            """, (nome_tabella, tipologia_sigla, sigla, lingua))
            
            exists = cursor.fetchone()[0] > 0
            
            if not exists:
                cursor.execute("""
                    INSERT INTO pyarchinit_thesaurus_sigle 
                    (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
                    VALUES (?, ?, ?, ?, ?)
                """, (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua))
                print(f"  ✓ Inserito: {sigla} - {sigla_estesa}")
                inserted_count += 1
            else:
                print(f"  - Esiste già: {sigla} - {sigla_estesa}")
                skipped_count += 1
    
    return inserted_count, skipped_count

def main():
    # Database path
    db_path = os.path.expanduser("~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite")
    
    # Alternative path if running from plugin directory
    if not os.path.exists(db_path):
        plugin_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(plugin_dir, "pyarchinit_db.sqlite")
    
    if not os.path.exists(db_path):
        print(f"Database non trovato in: {db_path}")
        return 1
        
    print(f"Uso database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if thesaurus table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='pyarchinit_thesaurus_sigle'
        """)
        if not cursor.fetchone():
            print("❌ La tabella 'pyarchinit_thesaurus_sigle' non esiste!")
            print("Assicurati che il database PyArchInit sia stato inizializzato correttamente.")
            return 1
        
        print("\nInserimento valori thesaurus TMA...")
        print("=" * 50)
        
        # Insert Italian values
        inserted_it, skipped_it = insert_thesaurus_values(cursor, lingua='it')
        
        # Optionally insert English values (you can customize these)
        # inserted_en, skipped_en = insert_thesaurus_values(cursor, lingua='en')
        
        conn.commit()
        
        print("\n" + "=" * 50)
        print(f"✅ Operazione completata!")
        print(f"   - Valori inseriti: {inserted_it}")
        print(f"   - Valori già esistenti: {skipped_it}")
        print(f"   - Totale valori nel thesaurus: {inserted_it + skipped_it}")
        
    except sqlite3.Error as e:
        print(f"\n❌ Errore durante l'inserimento: {e}")
        conn.rollback()
        return 1
        
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())