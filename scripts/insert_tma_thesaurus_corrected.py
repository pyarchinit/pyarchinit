#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per inserire i valori del thesaurus TMA nel database
Verifica prima se i valori esistono già per evitare duplicati
CORRECTED VERSION with proper tipologia_sigla codes
"""

import sqlite3
import os
import sys

# Definizione dei valori del thesaurus TMA con codici corretti
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
    '10.3': {  # Località (NOT Vano/Locus!)
        'description': 'Località',
        'values': [
            ('LOC01', 'Località 1'),
            ('LOC02', 'Località 2'),
            ('LOC03', 'Località 3'),
            ('CENTR', 'Centro storico'),
            ('PERIF', 'Periferia'),
        ]
    },
    '10.4': {  # Materiale (nome scavo was wrong)
        'description': 'Materiale',
        'values': [
            ('CER', 'Ceramica'),
            ('MET', 'Metallo'),
            ('VET', 'Vetro'),
            ('OSS', 'Osso'),
            ('PET', 'Pietra'),
            ('LATE', 'Laterizio'),
        ]
    },
    '10.5': {  # Categoria
        'description': 'Categoria',
        'values': [
            ('CER_COM', 'Ceramica comune'),
            ('CER_FIN', 'Ceramica fine'),
            ('MON', 'Moneta'),
            ('ORN', 'Ornamento'),
            ('STR', 'Strumento'),
        ]
    },
    '10.6': {  # Classe
        'description': 'Classe',
        'values': [
            ('SIG_IT', 'Sigillata italica'),
            ('SIG_AF', 'Sigillata africana'),
            ('VN', 'Vernice nera'),
            ('ANF', 'Anfora'),
            ('COM_DEP', 'Comune depurata'),
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
    '10.8': {  # Precisazione tipologica
        'description': 'Precisazione tipologica',
        'values': [
            ('HAYES_23', 'Hayes 23'),
            ('DRAG_18', 'Dragendorff 18'),
            ('LAMB_2', 'Lamboglia 2'),
            ('DRESSEL_1', 'Dressel 1'),
        ]
    },
    '10.9': {  # Definizione
        'description': 'Definizione',
        'values': [
            ('PIATTO', 'Piatto'),
            ('COPPA', 'Coppa'),
            ('OLLA', 'Olla'),
            ('BICCH', 'Bicchiere'),
            ('ANF', 'Anfora'),
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
    '10.11': {  # Tipo foto (NOT tipo acquisizione!)
        'description': 'Tipo foto',
        'values': [
            ('GEN', 'Generale'),
            ('DET', 'Dettaglio'),
            ('MAC', 'Macro'),
            ('MIC', 'Microscopica'),
            ('RAD', 'Radiografia'),
            ('UV', 'Ultravioletto'),
        ]
    },
    '10.12': {  # Tipo disegno
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
    '10.13': {  # Tipo disegno autore (NOT tipo disegno!)
        'description': 'Tipo disegno autore',
        'values': [
            ('AUT1', 'Autore 1'),
            ('AUT2', 'Autore 2'),
            ('AUT3', 'Autore 3'),
            ('ARCH', 'Archeologo'),
            ('DIS', 'Disegnatore'),
        ]
    },
    '10.14': {  # Tipologia acquisizione
        'description': 'Tipologia acquisizione',
        'values': [
            ('SCA', 'Scavo'),
            ('RIC', 'Ricognizione'),
            ('REC', 'Recupero'),
            ('RIN', 'Rinvenimento fortuito'),
            ('DON', 'Donazione'),
            ('ACQ', 'Acquisto'),
        ]
    },
    '10.15': {  # Settore (NOT fascia cronologica!)
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
    '10.16': {  # Cronologia (was missing!)
        'description': 'Cronologia',
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
}

def insert_thesaurus_values(cursor, nome_tabella='TMA materiali archeologici', lingua='it'):
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
        
        # Also insert for TMA materiali ripetibili table
        print("\n\nInserimento valori per TMA materiali ripetibili...")
        print("=" * 50)
        inserted_rip, skipped_rip = insert_thesaurus_values(cursor, nome_tabella='TMA materiali ripetibili', lingua='it')
        
        conn.commit()
        
        print("\n" + "=" * 50)
        print(f"✅ Operazione completata!")
        print(f"\nTabella TMA materiali archeologici:")
        print(f"   - Valori inseriti: {inserted_it}")
        print(f"   - Valori già esistenti: {skipped_it}")
        print(f"\nTabella TMA materiali ripetibili:")
        print(f"   - Valori inseriti: {inserted_rip}")
        print(f"   - Valori già esistenti: {skipped_rip}")
        print(f"\nTotale valori nel thesaurus: {inserted_it + skipped_it + inserted_rip + skipped_rip}")
        
    except sqlite3.Error as e:
        print(f"\n❌ Errore durante l'inserimento: {e}")
        conn.rollback()
        return 1
        
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())