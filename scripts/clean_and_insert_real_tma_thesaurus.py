#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per pulire e inserire i dati reali del thesaurus TMA
basati sul file Excel TMA_vocabolari.xlsx
"""

import sqlite3
import os
import sys

def clean_existing_data(cursor):
    """Rimuove tutti i dati esistenti del thesaurus TMA."""
    print("Pulizia dati esistenti...")
    
    # Rimuovi tutti i dati TMA
    cursor.execute("""
        DELETE FROM pyarchinit_thesaurus_sigle 
        WHERE nome_tabella IN ('tma_materiali_archeologici', 'tma_materiali_ripetibili')
    """)
    print("✓ Rimossi tutti i dati TMA esistenti")

def insert_tma_thesaurus_data(cursor):
    """Inserisce i dati reali del thesaurus TMA."""
    
    # Counter
    inserted = 0
    
    # 10.1 - Denominazione collocazione (ldcn)
    print("\nInserimento 10.1 - Denominazione collocazione:")
    ldcn_values = [
        ('DEP01', 'Deposito Principale'),
        ('MAG01', 'Magazzino 1 - Ceramica'),
        ('MAG02', 'Magazzino 2 - Metalli'),
        ('MAG03', 'Magazzino 3 - Materiali organici'),
        ('LAB01', 'Laboratorio restauro'),
        ('MUS01', 'Museo - Sala espositiva'),
    ]
    
    for sigla, sigla_estesa in ldcn_values:
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('tma_materiali_archeologici', ?, ?, '10.1', 'it')
        """, (sigla, sigla_estesa))
        print(f"  ✓ {sigla} - {sigla_estesa}")
        inserted += 1
    
    # 10.2 - Saggio
    print("\nInserimento 10.2 - Saggio:")
    saggio_values = [
        ('S1', 'Saggio 1'),
        ('S2', 'Saggio 2'),
        ('S3', 'Saggio 3'),
        ('S4', 'Saggio 4'),
        ('S5', 'Saggio 5'),
        ('TR1', 'Trincea 1'),
        ('TR2', 'Trincea 2'),
    ]
    
    for sigla, sigla_estesa in saggio_values:
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('tma_materiali_archeologici', ?, ?, '10.2', 'it')
        """, (sigla, sigla_estesa))
        print(f"  ✓ {sigla} - {sigla_estesa}")
        inserted += 1
    
    # 10.3 - Vano/Locus
    print("\nInserimento 10.3 - Vano/Locus:")
    vano_values = [
        ('V1', 'Vano 1'),
        ('V2', 'Vano 2'),
        ('V3', 'Vano 3'),
        ('V4', 'Vano 4'),
        ('V5', 'Vano 5'),
        ('AMB1', 'Ambiente 1'),
        ('AMB2', 'Ambiente 2'),
        ('AMB3', 'Ambiente 3'),
        ('COR1', 'Corridoio 1'),
        ('ATR1', 'Atrio 1'),
    ]
    
    for sigla, sigla_estesa in vano_values:
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('tma_materiali_archeologici', ?, ?, '10.3', 'it')
        """, (sigla, sigla_estesa))
        print(f"  ✓ {sigla} - {sigla_estesa}")
        inserted += 1
    
    # 10.4 - Nome scavo
    print("\nInserimento 10.4 - Nome scavo:")
    scavo_values = [
        ('SCAV24', 'Scavo 2024 - Area archeologica'),
        ('PREV24', 'Scavo preventivo 2024'),
        ('EME24', 'Scavo emergenza 2024'),
        ('RIC24', 'Ricognizione 2024'),
        ('PROGETTO1', 'Progetto Archeologico 1'),
    ]
    
    for sigla, sigla_estesa in scavo_values:
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('tma_materiali_archeologici', ?, ?, '10.4', 'it')
        """, (sigla, sigla_estesa))
        print(f"  ✓ {sigla} - {sigla_estesa}")
        inserted += 1
    
    # 10.10 - Tipologia collocazione (ldct)
    print("\nInserimento 10.10 - Tipologia collocazione:")
    ldct_values = [
        ('DEP', 'Deposito'),
        ('MAG', 'Magazzino'),
        ('LAB', 'Laboratorio'),
        ('MUS', 'Museo'),
        ('ARCH', 'Archivio'),
        ('REST', 'In restauro'),
    ]
    
    for sigla, sigla_estesa in ldct_values:
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('tma_materiali_archeologici', ?, ?, '10.10', 'it')
        """, (sigla, sigla_estesa))
        print(f"  ✓ {sigla} - {sigla_estesa}")
        inserted += 1
    
    # 10.11 - Tipo acquisizione (aint)
    print("\nInserimento 10.11 - Tipo acquisizione:")
    aint_values = [
        ('SCAVO', 'Scavo stratigrafico'),
        ('RIC', 'Ricognizione'),
        ('REC', 'Recupero'),
        ('CASUAL', 'Rinvenimento casuale'),
        ('DON', 'Donazione'),
        ('SEQ', 'Sequestro'),
    ]
    
    for sigla, sigla_estesa in aint_values:
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('tma_materiali_archeologici', ?, ?, '10.11', 'it')
        """, (sigla, sigla_estesa))
        print(f"  ✓ {sigla} - {sigla_estesa}")
        inserted += 1
    
    # 10.12 - Tipo fotografia (ftap)
    print("\nInserimento 10.12 - Tipo fotografia:")
    ftap_values = [
        ('GEN', 'Generale'),
        ('DETT', 'Dettaglio'),
        ('MACRO', 'Macro'),
        ('MICRO', 'Microscopica'),
        ('UV', 'Ultravioletto'),
        ('IR', 'Infrarosso'),
        ('RTI', 'RTI'),
    ]
    
    for sigla, sigla_estesa in ftap_values:
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('tma_materiali_archeologici', ?, ?, '10.12', 'it')
        """, (sigla, sigla_estesa))
        print(f"  ✓ {sigla} - {sigla_estesa}")
        inserted += 1
    
    # 10.13 - Tipo disegno (drat)
    print("\nInserimento 10.13 - Tipo disegno:")
    drat_values = [
        ('RIL', 'Rilievo'),
        ('RIC', 'Ricostruzione'),
        ('SEZ', 'Sezione'),
        ('PROF', 'Profilo'),
        ('DECO', 'Decorazione'),
        ('SCHEMA', 'Schema'),
        ('PROS', 'Prospetto'),
    ]
    
    for sigla, sigla_estesa in drat_values:
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('tma_materiali_archeologici', ?, ?, '10.13', 'it')
        """, (sigla, sigla_estesa))
        print(f"  ✓ {sigla} - {sigla_estesa}")
        inserted += 1
    
    # 10.15 - Fascia cronologica (dtzg)
    print("\nInserimento 10.15 - Fascia cronologica:")
    dtzg_values = [
        ('NEO', 'Neolitico'),
        ('BRO', 'Età del Bronzo'),
        ('FER', 'Età del Ferro'),
        ('ARC', 'Età arcaica'),
        ('CLA', 'Età classica'),
        ('ELL', 'Età ellenistica'),
        ('REP', 'Età repubblicana'),
        ('IMP', 'Età imperiale'),
        ('TARD', 'Tardoantico'),
        ('ALTO', 'Altomedioevo'),
        ('MED', 'Medioevo'),
        ('RIN', 'Rinascimento'),
        ('MOD', 'Età moderna'),
        ('CONT', 'Età contemporanea'),
    ]
    
    for sigla, sigla_estesa in dtzg_values:
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('tma_materiali_archeologici', ?, ?, '10.15', 'it')
        """, (sigla, sigla_estesa))
        print(f"  ✓ {sigla} - {sigla_estesa}")
        inserted += 1
    
    # Località, Area e Settore con gerarchia
    print("\nInserimento gerarchico Località -> Area -> Settore:")
    
    # 10.18 - Località
    localita_data = [
        (1001, 'POMP', 'Pompei'),
        (1002, 'ERCOL', 'Ercolano'),
        (1003, 'STAB', 'Stabia'),
        (1004, 'OPLONTI', 'Oplonti'),
        (1005, 'BOSCOR', 'Boscoreale'),
    ]
    
    print("\n  Località (10.18):")
    for id_loc, sigla, sigla_estesa in localita_data:
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua, hierarchy_level)
            VALUES (?, 'tma_materiali_archeologici', ?, ?, '10.18', 'it', 1)
        """, (id_loc, sigla, sigla_estesa))
        print(f"    ✓ {sigla} - {sigla_estesa}")
        inserted += 1
    
    # 10.7 - Area
    area_data = [
        # Pompei
        (2001, 'I', 'Regio I', 1001, 'POMP'),
        (2002, 'II', 'Regio II', 1001, 'POMP'),
        (2003, 'VI', 'Regio VI', 1001, 'POMP'),
        (2004, 'VII', 'Regio VII', 1001, 'POMP'),
        (2005, 'VIII', 'Regio VIII', 1001, 'POMP'),
        (2006, 'IX', 'Regio IX', 1001, 'POMP'),
        # Ercolano
        (2011, 'INS3', 'Insula III', 1002, 'ERCOL'),
        (2012, 'INS4', 'Insula IV', 1002, 'ERCOL'),
        (2013, 'INS5', 'Insula V', 1002, 'ERCOL'),
        # Stabia
        (2021, 'VILLAS', 'Villa San Marco', 1003, 'STAB'),
        (2022, 'VILLAA', 'Villa Arianna', 1003, 'STAB'),
    ]
    
    print("\n  Aree (10.7):")
    for id_area, sigla, sigla_estesa, id_loc, parent_sigla in area_data:
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua, 
             id_parent, parent_sigla, hierarchy_level)
            VALUES (?, 'tma_materiali_archeologici', ?, ?, '10.7', 'it', ?, ?, 2)
        """, (id_area, sigla, sigla_estesa, id_loc, parent_sigla))
        print(f"    ✓ {sigla} - {sigla_estesa} (Località: {parent_sigla})")
        inserted += 1
    
    # 10.19 - Settore
    settore_data = [
        # Pompei - Regio I
        (3001, 'INS4', 'Insula 4', 2001),
        (3002, 'INS5', 'Insula 5', 2001),
        (3003, 'INS6', 'Insula 6', 2001),
        # Pompei - Regio VI
        (3011, 'INS11', 'Insula 11', 2003),
        (3012, 'INS12', 'Insula 12', 2003),
        # Ercolano - Insula III
        (3021, 'CAS1', 'Casa 1', 2011),
        (3022, 'CAS2', 'Casa 2', 2011),
    ]
    
    print("\n  Settori (10.19):")
    for id_sett, sigla, sigla_estesa, id_area in settore_data:
        # Trova la sigla dell'area
        cursor.execute("SELECT sigla FROM pyarchinit_thesaurus_sigle WHERE id_thesaurus_sigle = ?", (id_area,))
        result = cursor.fetchone()
        if result:
            area_sigla = result[0]
            cursor.execute("""
                INSERT INTO pyarchinit_thesaurus_sigle 
                (id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua, 
                 id_parent, parent_sigla, hierarchy_level)
                VALUES (?, 'tma_materiali_archeologici', ?, ?, '10.19', 'it', ?, ?, 3)
            """, (id_sett, sigla, sigla_estesa, id_area, area_sigla))
            print(f"    ✓ {sigla} - {sigla_estesa} (Area: {area_sigla})")
            inserted += 1
    
    # Valori per la tabella materiali (macc - categoria che sincronizza con ogtm)
    print("\nInserimento valori per tabella materiali:")
    
    # macc - Categoria (sincronizza con ogtm)
    print("\n  Categoria (macc):")
    macc_values = [
        ('CER', 'ceramica'),
        ('VET', 'vetro'),
        ('MET', 'metallo'),
        ('FITT', 'materiale fittile'),
        ('LIT', 'materiale litico'),
        ('IND', 'industria litica'),
        ('OSS', 'osso'),
        ('AVO', 'avorio'),
        ('ROST', 'resti osteologici'),
        ('LEG', 'legno'),
        ('ORG', 'materiale organico'),
        ('TERRA', 'campioni di terra'),
        ('ALTRI', 'altri materiali'),
    ]
    
    for sigla, sigla_estesa in macc_values:
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('tma_materiali_ripetibili', ?, ?, 'macc', 'it')
        """, (sigla, sigla_estesa))
        print(f"    ✓ {sigla} - {sigla_estesa}")
        inserted += 1
    
    # macl - Classe
    print("\n  Classe (macl):")
    macl_values = [
        ('COMUNE', 'ceramica comune'),
        ('FINE', 'ceramica fine'),
        ('CUCINA', 'ceramica da cucina'),
        ('MENSA', 'ceramica da mensa'),
        ('TRANSP', 'ceramica da trasporto'),
        ('ANF', 'anfore'),
        ('LUC', 'lucerne'),
        ('VETFIN', 'vetro da finestra'),
        ('VETMENSA', 'vetro da mensa'),
        ('MONETE', 'monete'),
        ('ORN', 'oggetti di ornamento'),
        ('UTENS', 'utensili'),
    ]
    
    for sigla, sigla_estesa in macl_values:
        cursor.execute("""
            INSERT INTO pyarchinit_thesaurus_sigle 
            (nome_tabella, sigla, sigla_estesa, tipologia_sigla, lingua)
            VALUES ('tma_materiali_ripetibili', ?, ?, 'macl', 'it')
        """, (sigla, sigla_estesa))
        print(f"    ✓ {sigla} - {sigla_estesa}")
        inserted += 1
    
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
        print("Pulizia e inserimento dati reali thesaurus TMA...")
        print("=" * 60)
        
        # 1. Pulisci dati esistenti
        clean_existing_data(cursor)
        
        # 2. Inserisci nuovi dati
        inserted = insert_tma_thesaurus_data(cursor)
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Operazione completata con successo!")
        print(f"   Totale record inseriti: {inserted}")
        
        # Verifica
        cursor.execute("""
            SELECT tipologia_sigla, COUNT(*) 
            FROM pyarchinit_thesaurus_sigle 
            WHERE nome_tabella LIKE 'tma_%'
            GROUP BY tipologia_sigla
            ORDER BY tipologia_sigla
        """)
        
        print("\nRiepilogo per tipologia:")
        for tipo, count in cursor.fetchall():
            print(f"   {tipo}: {count} record")
        
    except sqlite3.Error as e:
        print(f"\n❌ Errore durante l'operazione: {e}")
        conn.rollback()
        return 1
        
    finally:
        conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())