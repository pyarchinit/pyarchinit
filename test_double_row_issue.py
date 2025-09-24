#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug script for double row addition/removal issue
"""

print("\n" + "="*60)
print("ISSUE: Double Row Addition/Removal in TMA Materials Table")
print("="*60)

print("\nPROBLEM DESCRIPTION:")
print("1. When clicking 'Add Material', two rows are added instead of one")
print("2. When clicking 'Remove Material', two rows are removed instead of one")
print("3. Empty rows are not being removed properly")

print("\nPOSSIBLE CAUSES:")

print("\n1. DUPLICATE SIGNAL CONNECTIONS:")
print("   - The clicked signal might be connected twice")
print("   - Check if setupUi() or __init__ is called multiple times")
print("   - Check if signals are connected in multiple places")

print("\n2. EVENT PROPAGATION:")
print("   - The button click might trigger multiple events")
print("   - Parent/child widget event handling issues")

print("\n3. TABLE RELOAD AFTER ACTION:")
print("   - After adding/removing a row, the table might be reloaded")
print("   - If load_materials_table() is called, it might add rows again")

print("\n4. DELEGATE ISSUES:")
print("   - ComboBoxDelegate might be triggering additional row operations")
print("   - Focus changes might cause unexpected behavior")

print("1. Add logging to track how many times methods are called")
print("2. Check if signals are connected multiple times")
print("3. Track table row count before and after operations")
print("4. Monitor if fill_fields() or load_materials_table() is called")

print("\nSOLUTION:")
print("Need to ensure signals are connected only once and that")
print("table operations don't trigger cascading updates.")

print("="*60)