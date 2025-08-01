#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to add localita and settore columns to existing TMA table in PostgreSQL
"""

import sys
from datetime import datetime

try:
    import psycopg2
except ImportError:
    print("Error: psycopg2 module not found. Please install it with: pip install psycopg2-binary")
    sys.exit(1)

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a PostgreSQL table."""
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = %s AND column_name = %s
    """, (table_name, column_name))
    return cursor.fetchone() is not None

def main():
    # Database connection parameters
    # Modify these according to your PostgreSQL setup
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "pyarchinit"
    DB_USER = "postgres"
    DB_PASSWORD = "postgres"
    
    # You can also pass connection parameters via command line
    if len(sys.argv) > 1:
        DB_HOST = sys.argv[1]
    if len(sys.argv) > 2:
        DB_NAME = sys.argv[2]
    if len(sys.argv) > 3:
        DB_USER = sys.argv[3]
    if len(sys.argv) > 4:
        DB_PASSWORD = sys.argv[4]
    
    try:
        # Connect to PostgreSQL
        print(f"Connecting to PostgreSQL database '{DB_NAME}' on {DB_HOST}...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        print("\nChecking TMA table structure...")
        
        # Check if table exists
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'tma_materiali_archeologici'
        """)
        if not cursor.fetchone():
            print("❌ Table 'tma_materiali_archeologici' does not exist!")
            print("Please create the table first using the PyArchInit interface.")
            return 1
        
        # Check if columns already exist
        localita_exists = check_column_exists(cursor, 'tma_materiali_archeologici', 'localita')
        settore_exists = check_column_exists(cursor, 'tma_materiali_archeologici', 'settore')
        
        if localita_exists and settore_exists:
            print("✓ Columns 'localita' and 'settore' already exist. No migration needed.")
            return 0
        
        # Add localita column if it doesn't exist
        if not localita_exists:
            print("Adding 'localita' column...")
            cursor.execute("""
                ALTER TABLE tma_materiali_archeologici 
                ADD COLUMN localita TEXT
            """)
            print("✓ Added 'localita' column")
        
        # Add settore column if it doesn't exist
        if not settore_exists:
            print("Adding 'settore' column...")
            cursor.execute("""
                ALTER TABLE tma_materiali_archeologici 
                ADD COLUMN settore TEXT
            """)
            print("✓ Added 'settore' column")
        
        # Commit changes
        conn.commit()
        
        # Verify the changes
        print("\nVerifying table structure...")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'tma_materiali_archeologici'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        column_names = [col[0] for col in columns]
        if 'localita' in column_names and 'settore' in column_names:
            print("✅ Migration completed successfully!")
            print("\nCurrent table structure:")
            for col_name, col_type in columns:
                print(f"  - {col_name} ({col_type})")
        else:
            print("❌ Migration may have failed. Please check the table structure.")
            return 1
        
    except psycopg2.Error as e:
        print(f"\n❌ PostgreSQL error during migration: {e}")
        if conn:
            conn.rollback()
        return 1
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        return 1
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return 0

if __name__ == "__main__":
    print("TMA Table Migration Script for PostgreSQL")
    print("=========================================")
    print("\nUsage: python add_tma_localita_settore_postgres.py [host] [database] [user] [password]")
    print("Default: localhost pyarchinit postgres postgres\n")
    
    sys.exit(main())