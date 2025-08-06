#!/usr/bin/env python3
"""
Script to add CASCADE DELETE to the foreign key constraint between 
tma_materiali_ripetibili and tma_materiali_archeologici tables.

This ensures that when a TMA record is deleted, all related material records
are automatically deleted as well.
"""

import sqlite3
import os
import sys

def add_cascade_delete(db_path):
    """Add CASCADE DELETE to TMA foreign key constraint"""
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return False
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Begin transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Check current foreign key status
        cursor.execute("PRAGMA foreign_keys")
        fk_status = cursor.fetchone()[0]
        print(f"Foreign keys enabled: {bool(fk_status)}")
        
        # Get current table structure
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='tma_materiali_ripetibili'")
        create_sql = cursor.fetchone()
        
        if create_sql:
            print(f"\nCurrent table structure:")
            print(create_sql[0])
            
            # Check if CASCADE already exists
            if "ON DELETE CASCADE" in create_sql[0]:
                print("\n✅ CASCADE DELETE already configured!")
                return True
        
        # Create temporary table with CASCADE DELETE
        print("\nCreating new table structure with CASCADE DELETE...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tma_materiali_ripetibili_new (
                id INTEGER PRIMARY KEY,
                id_tma INTEGER NOT NULL,
                madi VARCHAR(50),
                macc VARCHAR(30) NOT NULL,
                macl VARCHAR(30),
                macp VARCHAR(30),
                macd VARCHAR(30),
                cronologia_mac VARCHAR(50),
                macq VARCHAR(20),
                peso FLOAT,
                created_at VARCHAR(50),
                updated_at VARCHAR(50),
                created_by VARCHAR(100),
                updated_by VARCHAR(100),
                FOREIGN KEY (id_tma) REFERENCES tma_materiali_archeologici(id) ON DELETE CASCADE
            )
        """)
        
        # Copy data to new table
        print("Copying existing data...")
        cursor.execute("""
            INSERT INTO tma_materiali_ripetibili_new 
            SELECT * FROM tma_materiali_ripetibili
        """)
        
        rows_copied = cursor.rowcount
        print(f"Copied {rows_copied} rows")
        
        # Drop old table
        cursor.execute("DROP TABLE tma_materiali_ripetibili")
        
        # Rename new table
        cursor.execute("ALTER TABLE tma_materiali_ripetibili_new RENAME TO tma_materiali_ripetibili")
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Commit transaction
        conn.commit()
        print("\n✅ Successfully added CASCADE DELETE to foreign key constraint!")
        
        # Verify the change
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='tma_materiali_ripetibili'")
        new_sql = cursor.fetchone()
        print(f"\nNew table structure:")
        print(new_sql[0])
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    # Get the database path from command line or use default
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        # Try to find the pyarchinit database
        home = os.path.expanduser("~")
        db_path = os.path.join(home, "pyarchinit_DB_folder", "pyarchinit_db.sqlite")
    
    print(f"Database path: {db_path}")
    add_cascade_delete(db_path)