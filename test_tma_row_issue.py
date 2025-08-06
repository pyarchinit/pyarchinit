#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to debug TMA row numbering issue
"""

print("\n" + "="*60)
print("TEST: TMA Row Numbering Issue")
print("="*60)

print("\nISSUE DESCRIPTION:")
print("1. User creates new TMA record")
print("2. Adds a material row and enters category") 
print("3. Saves the record")
print("4. Gets error: 'Le righe 2 non sono state salvate' (row 2 not saved)")
print("5. But the row is actually saved with the category filled")
print("6. When adding a second row, it doesn't save")

print("\nPOSSIBLE CAUSES:")
print("1. Row numbering mismatch (0-based vs 1-based indexing)")
print("   - Table uses 0-based indexing internally")
print("   - Error message shows 1-based numbering for users")
print("   - Issue: empty_rows.append(row + 1) might be wrong")

print("\n2. First save doesn't properly detect the entered data")
print("   - ComboBoxDelegate hasn't committed data yet")
print("   - get_cell_value() can't read uncommitted data")
print("   - Data gets saved later but error is shown first")

print("\n3. materials_loaded flag confusion")
print("   - For new records, materials_loaded = True")
print("   - But there might be timing issues")

print("\nRECOMMENDED SOLUTION:")
print("The issue seems to be that the error message is shown incorrectly.")
print("When the first row (index 0) has data, it's being reported as")
print("'row 2' in the error message, but it's actually being saved.")

print("\nThe fix should:")
print("1. Ensure ComboBox data is committed before reading")
print("2. Fix the row numbering in error messages")
print("3. Only show error for rows that truly fail to save")

print("\n" + "="*60)