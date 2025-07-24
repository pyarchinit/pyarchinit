#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyArchInit Migration Test Script
This script tests the US field migration with various alphanumeric values

Author: PyArchInit Team
Date: 2025-07-24
"""

import sys
import os

# Add PyArchInit to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management

def test_us_values():
    """Test various US value formats"""
    
    test_values = [
        "001",           # Numeric string with leading zeros
        "US001",         # Prefix + number
        "2024/001",      # Year/number format
        "A1",            # Letter + number
        "US-A",          # Prefix with hyphen
        "1A",            # Number + letter
        "TEST_001",      # Underscore format
        "US.001",        # Dot notation
        "US 001",        # Space (may need validation)
        "αβγ",           # Unicode characters
    ]
    
    print("=" * 60)
    print("PyArchInit US Field Migration Test")
    print("=" * 60)
    
    # Connect to database
    conn = Connection()
    conn_str = conn.conn_str()
    
    try:
        db_manager = Pyarchinit_db_management(conn_str)
        db_manager.connection()
        print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return
    
    # Test 1: Check field types
    print("\n1. Checking field types...")
    
    if 'sqlite' in conn_str:
        # SQLite check
        query = "SELECT sql FROM sqlite_master WHERE name = 'us_table'"
        result = db_manager.execute_sql_query(query)
        if result:
            print(f"US table structure: {result[0][0]}")
    else:
        # PostgreSQL check
        query = """
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'us_table' AND column_name = 'us'
        """
        result = db_manager.execute_sql_query(query)
        if result:
            print(f"US field type: {result[0][1]}")
    
    # Test 2: Try inserting test values
    print("\n2. Testing US value formats...")
    
    for test_value in test_values:
        print(f"\nTesting value: '{test_value}'")
        
        # Create test query
        search_dict = {
            'sito': "'Test Site'",
            'area': "'1'", 
            'us': f"'{test_value}'"
        }
        
        try:
            # Try to query with the new value format
            result = db_manager.query_bool(search_dict, 'US')
            print(f"  ✓ Query successful - Found {len(result)} records")
        except Exception as e:
            print(f"  ✗ Query failed: {e}")
    
    # Test 3: Test sorting
    print("\n3. Testing alphanumeric sorting...")
    
    test_sort_values = ["1", "10", "2", "20", "3", "US001", "US002", "US010", "US100"]
    
    print("\nStandard sort:")
    for val in sorted(test_sort_values):
        print(f"  {val}")
    
    print("\nNatural sort (recommended for US):")
    import re
    def natural_sort_key(text):
        return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', text)]
    
    for val in sorted(test_sort_values, key=natural_sort_key):
        print(f"  {val}")
    
    print("\n" + "=" * 60)
    print("Migration test complete!")
    print("=" * 60)

if __name__ == '__main__':
    test_us_values()