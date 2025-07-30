#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to create TMA tables in SQLite database
"""

import sqlite3
import os

# Path to the database
db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create TMA main table first
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tma_materiali_archeologici (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sito TEXT,
        area TEXT,
        riferimenti_tm TEXT,
        descrizione TEXT,
        vano_locus TEXT,
        periodo VARCHAR(150),
        cronologia VARCHAR(50),
        valore_stimato REAL,
        created_at VARCHAR(50),
        updated_at VARCHAR(50),
        created_by VARCHAR(100),
        updated_by VARCHAR(100)
    )
    ''')
    
    # Create TMA materials table with foreign key
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tma_materiali_ripetibili (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_tma INTEGER NOT NULL,
        madi VARCHAR(50),
        macc VARCHAR(30) NOT NULL,
        macl VARCHAR(30),
        macp VARCHAR(30),
        macd VARCHAR(30),
        cronologia_mac VARCHAR(50),
        macq VARCHAR(20),
        peso REAL,
        created_at VARCHAR(50),
        updated_at VARCHAR(50),
        created_by VARCHAR(100),
        updated_by VARCHAR(100),
        FOREIGN KEY (id_tma) REFERENCES tma_materiali_archeologici(id)
    )
    ''')
    
    conn.commit()
    
    # Verify tables were created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'tma%' ORDER BY name")
    tables = cursor.fetchall()
    
    print("TMA tables created successfully:")
    for table in tables:
        print(f"  - {table[0]}")
    
    conn.close()
else:
    print(f"Database not found at: {db_path}")