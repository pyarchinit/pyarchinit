#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to reproduce the TMA type comparison error
"""

import sys
import os

# Add the plugin path to sys.path
plugin_path = os.path.expanduser("~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit")
if plugin_path not in sys.path:
    sys.path.insert(0, plugin_path)

from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management

def test_query_bool_error():
    """Test to reproduce the query_bool type comparison error."""
    try:
        # Get connection
        conn = Connection()
        conn_str = conn.conn_str()
        
        # Create DB manager
        db_manager = Pyarchinit_db_management(conn_str)
        db_manager.connection()
        
        print("Testing query_bool with different parameter types...")
        
        # Test 1: Query with string value (this might cause the error)
        print("\nTest 1: Query with string id_tma='1'")
        try:
            search_dict = {'id_tma': '1'}  # String value
            result = db_manager.query_bool(search_dict, 'TMA_MATERIALI')
            print(f"Success! Found {len(result)} records")
        except Exception as e:
            print(f"Error with string value: {str(e)}")
            print(f"Error type: {type(e).__name__}")
        
        # Test 2: Query with integer value
        print("\nTest 2: Query with integer id_tma=1")
        try:
            search_dict = {'id_tma': 1}  # Integer value
            result = db_manager.query_bool(search_dict, 'TMA_MATERIALI')
            print(f"Success! Found {len(result)} records")
        except Exception as e:
            print(f"Error with integer value: {str(e)}")
            print(f"Error type: {type(e).__name__}")
        
        # Test 3: Query with quoted string value
        print("\nTest 3: Query with quoted string id_tma='1'")
        try:
            search_dict = {'id_tma': "'1'"}  # Quoted string value
            result = db_manager.query_bool(search_dict, 'TMA_MATERIALI')
            print(f"Success! Found {len(result)} records")
        except Exception as e:
            print(f"Error with quoted string value: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            
        # Test 4: Check the actual column type
        print("\nChecking column types in TMA_MATERIALI table...")
        from modules.db.entities.TMA_MATERIALI import TMA_MATERIALI
        
        # Get column info
        for col in TMA_MATERIALI.__table__.columns:
            print(f"  {col.name}: {col.type}")
            
    except Exception as e:
        print(f"\nGeneral error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_query_bool_error()