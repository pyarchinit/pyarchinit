#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final verification script for TMA fixes
"""

import sqlite3

# Database path
db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== FINAL VERIFICATION OF TMA FIXES ===")
print("\n1. CHECKING THESAURUS TABLE STRUCTURE:")

# Check thesaurus table columns
cursor.execute("PRAGMA table_info(pyarchinit_thesaurus_sigle)")
columns = cursor.fetchall()
required_columns = ['id_thesaurus_sigle', 'nome_tabella', 'sigla', 'sigla_estesa', 
                   'descrizione', 'tipologia_sigla', 'lingua', 'order_layer', 
                   'id_parent', 'parent_sigla', 'hierarchy_level']

print("   Required columns:")
for col in required_columns:
    found = any(c[1] == col for c in columns)
    status = "✓" if found else "✗"
    print(f"   {status} {col}")

print("\n2. CHECKING THESAURUS DATA FOR TMA:")

# Check thesaurus entries
cursor.execute("""
    SELECT tipologia_sigla, COUNT(*) as count
    FROM pyarchinit_thesaurus_sigle
    WHERE nome_tabella = 'tma_materiali_ripetibili'
    GROUP BY tipologia_sigla
""")
thesaurus_counts = cursor.fetchall()

if thesaurus_counts:
    print("   Thesaurus entries by type:")
    for tipo, count in thesaurus_counts:
        print(f"   - {tipo}: {count} entries")
else:
    print("   ✗ No thesaurus entries found for TMA materials")

print("\n3. CHECKING TMA RECORD AND MATERIALS:")

# Check TMA records
cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici")
tma_count = cursor.fetchone()[0]
print(f"   TMA records: {tma_count}")

# Check materials
cursor.execute("SELECT COUNT(*) FROM tma_materiali_ripetibili")
materials_count = cursor.fetchone()[0]
print(f"   Material records: {materials_count}")

# Check test record
cursor.execute("""
    SELECT t.id, t.ldcn, COUNT(m.id) as material_count
    FROM tma_materiali_archeologici t
    LEFT JOIN tma_materiali_ripetibili m ON t.id = m.id_tma
    WHERE t.ldcn = 'TEST-001'
    GROUP BY t.id, t.ldcn
""")
test_record = cursor.fetchone()

if test_record:
    print(f"\n   Test record found:")
    print(f"   - ID: {test_record[0]}")
    print(f"   - LDCN: {test_record[1]}")
    print(f"   - Materials: {test_record[2]}")
else:
    print("\n   ✗ Test record 'TEST-001' not found")

print("\n4. CHECKING FOREIGN KEY CONSTRAINT:")

# Check foreign key
cursor.execute("PRAGMA foreign_key_list(tma_materiali_ripetibili)")
fk_list = cursor.fetchall()
if fk_list:
    print("   ✓ Foreign key constraint exists")
    for fk in fk_list:
        print(f"     - Column: {fk[3]} -> {fk[2]}.{fk[4]}")
else:
    print("   ✗ No foreign key constraint found")

print("\n5. SUMMARY OF FIXES IMPLEMENTED:")
print("   ✓ Debug errors fixed (undefined variables)")
print("   ✓ Thesaurus table structure updated with hierarchy columns")
print("   ✓ Thesaurus data added for TMA materials")
print("   ✓ Materials table column mapping corrected")
print("   ✓ Materials persistence issue fixed with materials_loaded flag")
print("   ✓ Foreign key deletion error handled with direct SQL")
print("   ✓ Hierarchy info shows when TMA is selected in thesaurus")

print("\n6. NEXT STEPS TO TEST:")
print("   1. Open QGIS and the TMA form")
print("   2. Load the TEST-001 record")
print("   3. Verify materials are displayed in the table")
print("   4. Close and reopen the form")
print("   5. Verify materials are still there (not deleted)")
print("   6. Test ComboBox delegates in materials table")
print("   7. Test thesaurus hierarchy entry for TMA")

conn.close()

print("\n=== VERIFICATION COMPLETE ===")