#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per correggere e inserire i dati mancanti del thesaurus TMA
Basato sui codici corretti dal database esistente
"""

import sqlite3
import os
import sys

def insert_missing_thesaurus_data(cursor):
    """Inserisce i dati mancanti del thesaurus TMA."""
    
    inserted = 0
    
    # 10.1 - Denominazione collocazione (ldcn) - MANCANTE
    print("\nInserimento 10.1 - Denominazione collocazione:")
    ldcn_values = [
        ('FES01', 'Festòs - Magazzino principale'),
        ('FES02', 'Festòs - Deposito ceramica'),
        ('HT01', 'Haghia Triada - Magazzino'),
        ('KAM01', 'Kamilari - Deposito'),
        ('MUS01', 'Museo Heraklion'),
        ('LAB01', 'Laboratorio restauro'),
    ]
    
    for sigla, sigla_estesa in ldcn_values:
        try:
            cursor.execute("""
                INSERT INTO pyarchinit_thesaurus_sigle 
                (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
                VALUES ('TMA materiali archeologici', ?, ?, '10.1', 'it')
            """, (sigla, sigla_estesa))
            print(f"  ✓ {sigla} - {sigla_estesa}")
            inserted += 1
        except sqlite3.IntegrityError:
            print(f"  ⚠ {sigla} già esistente")
    
    # 10.2 - Tipologia collocazione (ldct) - MANCANTE
    print("\nInserimento 10.2 - Tipologia collocazione:")
    ldct_values = [
        ('MAG', 'Magazzino'),
        ('DEP', 'Deposito'),
        ('LAB', 'Laboratorio'),
        ('MUS', 'Museo'),
        ('ARCH', 'Archivio'),
        ('TEMP', 'Collocazione temporanea'),
    ]
    
    for sigla, sigla_estesa in ldct_values:
        try:
            cursor.execute("""
                INSERT INTO pyarchinit_thesaurus_sigle 
                (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
                VALUES ('TMA materiali archeologici', ?, ?, '10.2', 'it')
            """, (sigla, sigla_estesa))
            print(f"  ✓ {sigla} - {sigla_estesa}")
            inserted += 1
        except sqlite3.IntegrityError:
            print(f"  ⚠ {sigla} già esistente")
    
    # 10.10 - Definizione materiali (macd) - MANCANTE
    print("\nInserimento 10.10 - Definizione materiali:")
    macd_values = [
        ('FR_ORLO', 'Frammento di orlo'),
        ('FR_PARETE', 'Frammento di parete'),
        ('FR_FONDO', 'Frammento di fondo'),
        ('FR_ANSA', 'Frammento di ansa'),
        ('INTERO', 'Vaso intero'),
        ('RICOMP', 'Vaso ricomponibile'),
        ('FR_DEC', 'Frammento decorato'),
    ]
    
    for sigla, sigla_estesa in macd_values:
        try:
            cursor.execute("""
                INSERT INTO pyarchinit_thesaurus_sigle 
                (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
                VALUES ('TMA materiali archeologici', ?, ?, '10.10', 'it')
            """, (sigla, sigla_estesa))
            print(f"  ✓ {sigla} - {sigla_estesa}")
            inserted += 1
        except sqlite3.IntegrityError:
            print(f"  ⚠ {sigla} già esistente")
    
    # 10.12 - Tipo foto/disegno (ftap/drat) - MANCANTE
    print("\nInserimento 10.12 - Tipo foto/disegno:")
    foto_values = [
        ('GEN', 'Vista generale'),
        ('DET', 'Dettaglio'),
        ('MACRO', 'Macrofotografia'),
        ('PROF', 'Profilo'),
        ('SUP', 'Superficie'),
        ('DEC', 'Decorazione'),
        ('RIL', 'Rilievo grafico'),
        ('SEZ', 'Sezione'),
    ]
    
    for sigla, sigla_estesa in foto_values:
        try:
            cursor.execute("""
                INSERT INTO pyarchinit_thesaurus_sigle 
                (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
                VALUES ('TMA materiali archeologici', ?, ?, '10.12', 'it')
            """, (sigla, sigla_estesa))
            print(f"  ✓ {sigla} - {sigla_estesa}")
            inserted += 1
        except sqlite3.IntegrityError:
            print(f"  ⚠ {sigla} già esistente")
    
    return inserted

def verify_all_codes(cursor):
    """Verifica che tutti i codici necessari siano presenti."""
    print("\n=== Verifica finale dei codici ===")
    
    required_codes = {
        '10.1': 'ldcn - Denominazione collocazione',
        '10.2': 'ldct - Tipologia collocazione',
        '10.3': 'località',
        '10.4': 'scan - Nome scavo',
        '10.5': 'macc/aint - Categoria/Tipo acquisizione',
        '10.6': 'dtzg/cronologia - Fascia cronologica',
        '10.7': 'area',
        '10.8': 'macl - Classe materiali',
        '10.9': 'macp - Prec. tipologica',
        '10.10': 'macd - Definizione materiali',
        '10.12': 'ftap/drat - Tipo foto/disegno',
        '10.15': 'settore'
    }
    
    for code, desc in sorted(required_codes.items()):
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = 'TMA materiali archeologici'
            AND tipologia_sigla = ?
        """, (code,))
        count = cursor.fetchone()[0]
        status = "✅" if count > 0 else "❌"
        print(f"{status} {code} - {desc}: {count} valori")

def main():
    # Database path
    db_path = os.path.expanduser("~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite")
    
    if not os.path.exists(db_path):
        print(f"Database non trovato in: {db_path}")
        return 1
        
    print(f"Uso database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("=== Inserimento dati mancanti thesaurus TMA ===")
        
        # Inserisci dati mancanti
        inserted = insert_missing_thesaurus_data(cursor)
        
        # Verifica finale
        verify_all_codes(cursor)
        
        # Commit
        conn.commit()
        
        print(f"\n✅ Operazione completata! Inseriti {inserted} nuovi valori.")
        
    except sqlite3.Error as e:
        print(f"\n❌ Errore: {e}")
        conn.rollback()
        return 1
        
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())