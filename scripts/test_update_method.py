#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test the update method to understand the type comparison error
"""

import sqlite3

def test_update_behavior():
    """Test how the update method builds its query string."""
    
    # Simulate the update method's string building
    table_class_str = 'TMA_MATERIALI'
    id_table_str = 'id'
    
    # Test with different value types
    test_cases = [
        ('String ID', ['1']),
        ('Int ID', [1]),
        ('String in list', '1'),
        ('Direct int', 1)
    ]
    
    for name, value_id_list in test_cases:
        print(f"\n{name}: value_id_list = {value_id_list}, type = {type(value_id_list)}")
        
        # Original code
        try:
            id_value = value_id_list[0] if isinstance(value_id_list, list) else value_id_list
            print(f"  Original id_value = {id_value}, type = {type(id_value)}")
            
            # Build the session string like the original
            session_exec_str = 'session.query(%s).filter(and_(%s.%s == %s)).update(values = %s)' % (
                table_class_str, table_class_str, id_table_str, id_value, {'test': 'value'})
            print(f"  Query string: {session_exec_str}")
        except Exception as e:
            print(f"  Error: {e}")
        
        # Modified code with type conversion
        try:
            id_value = value_id_list[0] if isinstance(value_id_list, list) else value_id_list
            # Convert to int if it's a numeric ID field
            if id_table_str.lower() in ['id', 'id_tma', 'id_us', 'id_site', 'id_invmat', 'id_media']:
                try:
                    id_value = int(id_value)
                except (ValueError, TypeError):
                    pass
            
            print(f"  Modified id_value = {id_value}, type = {type(id_value)}")
            
            # Build the session string
            session_exec_str = 'session.query(%s).filter(and_(%s.%s == %s)).update(values = %s)' % (
                table_class_str, table_class_str, id_table_str, id_value, {'test': 'value'})
            print(f"  Modified query: {session_exec_str}")
        except Exception as e:
            print(f"  Modified error: {e}")

    # Test the actual SQL that would be generated
    print("\n\nTesting actual SQL generation:")
    print("When id_value = '1' (string):")
    print("  SQL: TMA_MATERIALI.id == 1")
    print("  Problem: SQLAlchemy sees this as comparing column (int) with string '1'")
    print("\nWhen id_value = 1 (int):")
    print("  SQL: TMA_MATERIALI.id == 1") 
    print("  This works correctly as both sides are integers")

if __name__ == "__main__":
    test_update_behavior()