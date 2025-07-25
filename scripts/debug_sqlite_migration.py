#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug script for SQLite US field migration
"""

import sqlite3
import sys
import os

def check_table_structure(conn, table_name):
    """Check the structure of a table"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"\n=== Table: {table_name} ===")
        for col in columns:
            col_id, col_name, col_type, col_notnull, col_default, col_pk = col
            print(f"  {col_name}: {col_type}")
            
        return columns
    except sqlite3.Error as e:
        print(f"  Error checking table {table_name}: {e}")
        return None

def check_for_new_tables(conn):
    """Check for any _new tables that might be left over"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_new'")
    new_tables = cursor.fetchall()
    
    if new_tables:
        print("\n=== WARNING: Found _new tables ===")
        for table in new_tables:
            print(f"  {table[0]}")
    else:
        print("\n=== No _new tables found ===")
    
    return new_tables

def check_specific_fields(conn):
    """Check specific fields that should be migrated"""
    tables_to_check = [
        ('inventario_materiali_table', ['us', 'area']),
        ('tomba_table', ['area']),
        ('us_table', ['us', 'area']),
        ('campioni_table', ['us', 'area']),
        ('pottery_table', ['us', 'area'])
    ]
    
    print("\n=== Checking specific fields ===")
    for table_name, fields in tables_to_check:
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if cursor.fetchone():
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                print(f"\n{table_name}:")
                for col in columns:
                    col_name = col[1]
                    col_type = col[2]
                    if col_name in fields:
                        status = "✓ TEXT" if col_type.upper() == "TEXT" else f"✗ {col_type}"
                        print(f"  {col_name}: {status}")
            else:
                print(f"\n{table_name}: Table not found")
        except sqlite3.Error as e:
            print(f"\n{table_name}: Error - {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python debug_sqlite_migration.py <path_to_sqlite_db>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        sys.exit(1)
    
    print(f"Checking database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    
    try:
        # Check for _new tables
        check_for_new_tables(conn)
        
        # Check specific fields
        check_specific_fields(conn)
        
        # Check full structure of key tables
        tables = ['inventario_materiali_table', 'tomba_table', 'us_table']
        for table in tables:
            check_table_structure(conn, table)
    
    finally:
        conn.close()

if __name__ == "__main__":
    main()