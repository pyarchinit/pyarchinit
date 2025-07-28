#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct test for TMA table structure
"""

import sqlite3
import os

# Default SQLite database path
db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== Testing TMA Table Structure ===")
    
    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'tma%'")
    tables = cursor.fetchall()
    print(f"TMA tables found: {tables}")
    
    # Check parent table structure
    if ('tma_materiali_archeologici',) in tables:
        print("\n--- tma_materiali_archeologici structure ---")
        cursor.execute("PRAGMA table_info(tma_materiali_archeologici)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else ''} {'PK' if col[5] else ''}")
        
        # Check if localita field exists
        has_localita = any(col[1] == 'localita' for col in columns)
        print(f"\nHas localita field: {has_localita}")
    
    # Check child table structure
    if ('tma_materiali_ripetibili',) in tables:
        print("\n--- tma_materiali_ripetibili structure ---")
        cursor.execute("PRAGMA table_info(tma_materiali_ripetibili)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else ''} {'PK' if col[5] else ''}")
        
        # Check foreign keys
        cursor.execute("PRAGMA foreign_key_list(tma_materiali_ripetibili)")
        fks = cursor.fetchall()
        print(f"\nForeign keys: {fks}")
    
    # Try to insert a test record
    print("\n--- Testing insert ---")
    try:
        # Insert parent record
        cursor.execute("""
            INSERT INTO tma_materiali_archeologici 
            (sito, area, ogtm, ldct, ldcn, vecchia_collocazione, cassetta,
             scan, saggio, vano_locus, dscd, dscu, rcgd, rcgz,
             aint, aind, dtzg, deso, nsc, ftap, ftan, drat, dran, draa,
             created_at, updated_at, created_by, updated_by)
            VALUES 
            ('Test', 'A1', 'Ceramica', '', 'US 100', '', 'TEST001',
             '', '', '', '', 'US 100', '', '',
             '', '', 'I sec. d.C.', 'Test description', '', '', '', '', '', '',
             '', '', 'test', 'test')
        """)
        parent_id = cursor.lastrowid
        print(f"✓ Parent record inserted with ID: {parent_id}")
        
        # Insert child record
        cursor.execute("""
            INSERT INTO tma_materiali_ripetibili
            (id_tma, madi, macc, macl, macp, macd, cronologia_mac, macq, peso,
             created_at, updated_at, created_by, updated_by)
            VALUES
            (?, '', 'ceramica', '', '', '', '', '1', 0.0,
             '', '', 'test', 'test')
        """, (parent_id,))
        print("✓ Child record inserted successfully")
        
        # Rollback test data
        conn.rollback()
        print("✓ Test data rolled back")
        
    except Exception as e:
        print(f"✗ Error during insert: {str(e)}")
        conn.rollback()
    
    conn.close()
else:
    print(f"Database not found at: {db_path}")