#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to debug TMA deletion issue
"""

import sqlite3
import os
from sqlalchemy import create_engine, text, MetaData

# Test with raw SQLite first
db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite"

print("=== Testing with raw SQLite ===")
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if foreign keys are enabled
    cursor.execute("PRAGMA foreign_keys")
    fk_status = cursor.fetchone()
    print(f"Foreign keys enabled: {fk_status[0] if fk_status else 'Unknown'}")
    
    # Enable foreign keys if not enabled
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Try a simple delete
    try:
        cursor.execute("DELETE FROM tma_materiali_ripetibili WHERE id_tma = 999999")
        print("✓ Raw SQLite delete successful")
    except Exception as e:
        print(f"✗ Raw SQLite delete failed: {e}")
    
    conn.close()

# Test with SQLAlchemy
print("\n=== Testing with SQLAlchemy ===")
conn_str = f"sqlite:///{db_path}"
engine = create_engine(conn_str, echo=False)

# Test 1: Using text() without metadata
try:
    with engine.connect() as conn:
        sql = text("DELETE FROM tma_materiali_ripetibili WHERE id_tma = :id_tma")
        result = conn.execute(sql, {"id_tma": 999999})
        conn.commit()
    print("✓ SQLAlchemy text() delete successful")
except Exception as e:
    print(f"✗ SQLAlchemy text() delete failed: {e}")

# Test 2: Check metadata reflection
try:
    metadata = MetaData()
    metadata.reflect(bind=engine)
    tables = list(metadata.tables.keys())
    print(f"\nTables found in metadata: {tables}")
    
    if 'tma_materiali_ripetibili' in metadata.tables:
        table = metadata.tables['tma_materiali_ripetibili']
        print(f"Columns in tma_materiali_ripetibili: {[c.name for c in table.columns]}")
        
        # Check foreign keys
        for fk in table.foreign_keys:
            print(f"Foreign key found: {fk.column} -> {fk.target_fullname}")
            
except Exception as e:
    print(f"✗ Metadata reflection error: {e}")

print("\n=== Checking existing data ===")
# Check if there are any orphaned records
with engine.connect() as conn:
    # Check TMA records
    result = conn.execute(text("SELECT COUNT(*) FROM tma_materiali_archeologici"))
    tma_count = result.scalar()
    print(f"TMA records: {tma_count}")
    
    # Check material records
    result = conn.execute(text("SELECT COUNT(*) FROM tma_materiali_ripetibili"))
    mat_count = result.scalar()
    print(f"Material records: {mat_count}")
    
    # Check for orphaned records
    result = conn.execute(text("""
        SELECT COUNT(*) 
        FROM tma_materiali_ripetibili 
        WHERE id_tma NOT IN (SELECT id FROM tma_materiali_archeologici)
    """))
    orphaned = result.scalar()
    print(f"Orphaned material records: {orphaned}")