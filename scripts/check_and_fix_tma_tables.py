#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to check and fix TMA tables structure
"""

import sqlite3
import os

def check_table_exists(cursor, table_name):
    """Check if table exists"""
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    return cursor.fetchone() is not None

def get_table_columns(cursor, table_name):
    """Get columns of a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [(row[1], row[2]) for row in cursor.fetchall()]

def main():
    # Database path
    db_path = os.path.expanduser("~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/pyarchinit_db.sqlite")
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if main TMA table exists
        if not check_table_exists(cursor, 'tma_materiali_archeologici'):
            print("Creating tma_materiali_archeologici table...")
            cursor.execute('''
            CREATE TABLE tma_materiali_archeologici (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sito TEXT,
                area TEXT,
                ogtm TEXT NOT NULL,
                ldct TEXT,
                ldcn TEXT NOT NULL,
                vecchia_collocazione TEXT,
                cassetta VARCHAR(15) NOT NULL,
                scan TEXT,
                saggio TEXT,
                vano_locus TEXT,
                dscd VARCHAR(20),
                dscu TEXT NOT NULL,
                rcgd VARCHAR(20),
                rcgz TEXT,
                aint TEXT,
                aind TEXT,
                dtzg TEXT NOT NULL,
                deso TEXT,
                nsc TEXT,
                ftap TEXT,
                ftan TEXT,
                drat TEXT,
                dran TEXT,
                draa TEXT,
                created_at TEXT,
                updated_at TEXT,
                created_by TEXT,
                updated_by TEXT
            )
            ''')
            print("✓ tma_materiali_archeologici table created")
        else:
            print("✓ tma_materiali_archeologici table exists")
            
        # Check columns
        columns = get_table_columns(cursor, 'tma_materiali_archeologici')
        print(f"  Columns: {len(columns)}")
        
        # Check if materials table exists
        if not check_table_exists(cursor, 'tma_materiali_ripetibili'):
            print("Creating tma_materiali_ripetibili table...")
            cursor.execute('''
            CREATE TABLE tma_materiali_ripetibili (
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
            print("✓ tma_materiali_ripetibili table created")
        else:
            print("✓ tma_materiali_ripetibili table exists")
            
        # Check columns
        columns = get_table_columns(cursor, 'tma_materiali_ripetibili')
        print(f"  Columns: {len(columns)}")
        
        # Check foreign key
        cursor.execute("PRAGMA foreign_key_list(tma_materiali_ripetibili)")
        fks = cursor.fetchall()
        if fks:
            print("✓ Foreign key constraint exists")
            for fk in fks:
                print(f"  FK: {fk[3]} -> {fk[2]}.{fk[4]}")
        else:
            print("⚠ No foreign key constraint found (normal for SQLite)")
            
        # Test insert
        print("\nTesting insert operations...")
        
        # Insert test TMA record
        cursor.execute('''
        INSERT INTO tma_materiali_archeologici 
        (sito, area, ogtm, ldcn, cassetta, dscu, dtzg) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('TEST_SITE', 'TEST_AREA', 'ceramica', 'test location', 'TEST001', '1', 'Test Period'))
        
        tma_id = cursor.lastrowid
        print(f"✓ Test TMA record created with ID: {tma_id}")
        
        # Insert test material
        cursor.execute('''
        INSERT INTO tma_materiali_ripetibili 
        (id_tma, macc) 
        VALUES (?, ?)
        ''', (tma_id, 'ceramica'))
        
        print("✓ Test material record created")
        
        # Clean up test data
        cursor.execute('DELETE FROM tma_materiali_ripetibili WHERE id_tma = ?', (tma_id,))
        cursor.execute('DELETE FROM tma_materiali_archeologici WHERE id = ?', (tma_id,))
        print("✓ Test data cleaned up")
        
        conn.commit()
        print("\n✅ All checks passed! Tables are properly configured.")
        
    except sqlite3.Error as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()