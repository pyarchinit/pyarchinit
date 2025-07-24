#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyArchInit Migration Script: Update Form Classes for US field type change
This script documents the changes needed in form classes to handle US as string instead of integer

Author: PyArchInit Team
Date: 2025-07-24
"""

import os

# Define the form files and methods that need updating
FORMS_TO_UPDATE = {
    'US_USM.py': {
        'description': 'Main US/USM form',
        'changes': [
            {
                'method': 'insert_new_rec',
                'old': 'int(self.lineEdit_us.text())',
                'new': 'str(self.lineEdit_us.text())',
                'note': 'Change US field from int to str in insert'
            },
            {
                'method': 'on_pushButton_search_go_pressed',
                'old': "int(self.lineEdit_us.text())",
                'new': "str(self.lineEdit_us.text())",
                'note': 'Change US search from int to str'
            },
            {
                'method': 'fill_fields',
                'old': 'str(self.DATA_LIST[self.rec_num].us)',
                'new': 'self.DATA_LIST[self.rec_num].us',
                'note': 'Remove str() conversion as field is already string'
            },
            {
                'method': 'data_error_check',
                'note': 'Remove integer validation for US field'
            }
        ]
    },
    'Campioni.py': {
        'description': 'Samples form',
        'changes': [
            {
                'method': 'insert_new_rec',
                'old': 'int(self.lineEdit_us.text())',
                'new': 'str(self.lineEdit_us.text())',
                'note': 'Change US field from int to str'
            },
            {
                'method': 'fill_fields',
                'old': 'str(self.DATA_LIST[self.rec_num].us)',
                'new': 'self.DATA_LIST[self.rec_num].us',
                'note': 'Remove str() conversion'
            }
        ]
    },
    'pyarchinit_Pottery_mainapp.py': {
        'description': 'Pottery form',
        'changes': [
            {
                'method': 'insert_new_rec',
                'old': 'int(self.lineEdit_us.text())',
                'new': 'str(self.lineEdit_us.text())',
                'note': 'Change US field from int to str'
            }
        ]
    },
    'Inv_Materiali.py': {
        'description': 'Materials inventory form',
        'note': 'Already handles US as text - no changes needed'
    },
    'Schedaind.py': {
        'description': 'Individual form',
        'note': 'Already handles US as text - no changes needed'
    }
}

# Code replacements for validation methods
VALIDATION_UPDATES = """
# Old validation (remove this):
if EC.data_is_int(self.lineEdit_us.text()) == 0:
    QMessageBox.warning(self, "ATTENZIONE", "Campo US. Il valore deve essere di tipo numerico", QMessageBox.Ok)
    test = 1

# New validation (add this):
if EC.data_is_empty(self.lineEdit_us.text()) == 0:
    QMessageBox.warning(self, "ATTENZIONE", "Campo US. Il campo non deve essere vuoto", QMessageBox.Ok)
    test = 1
"""

# Generate migration instructions
def generate_migration_instructions():
    """Generate detailed migration instructions for developers"""
    
    instructions = """
PyArchInit US Field Migration Instructions
==========================================

This migration changes the US (Unità Stratigrafica) field from INTEGER to STRING
to support alphanumeric values (e.g., "US001", "US-A", "2024/001").

DATABASE MIGRATION:
------------------
1. BACKUP YOUR DATABASE FIRST!
2. Run the appropriate migration script:
   - PostgreSQL: migration_us_to_string.sql
   - SQLite: migration_us_to_string_sqlite.sql

ENTITY CLASSES:
---------------
Run: python update_entities_us_field.py
This will automatically update all SQLAlchemy table structures.

FORM UPDATES:
-------------
The following manual changes are needed in the form classes:

"""
    
    for filename, info in FORMS_TO_UPDATE.items():
        instructions += f"\n### {filename} - {info['description']}\n"
        
        if 'note' in info:
            instructions += f"Note: {info['note']}\n"
        
        if 'changes' in info:
            for change in info['changes']:
                instructions += f"\nMethod: {change['method']}\n"
                if 'old' in change and 'new' in change:
                    instructions += f"  Replace: {change['old']}\n"
                    instructions += f"  With:    {change['new']}\n"
                if 'note' in change:
                    instructions += f"  Note:    {change['note']}\n"
    
    instructions += f"\n\nVALIDATION UPDATES:\n{VALIDATION_UPDATES}"
    
    instructions += """

SEARCH AND FILTER UPDATES:
-------------------------
1. Update any numeric comparisons (>, <, >=, <=) to string comparisons
2. Update ORDER BY clauses to handle alphanumeric sorting
3. Consider adding a natural sort function for US values

TESTING CHECKLIST:
-----------------
[ ] Test inserting new US records with alphanumeric values
[ ] Test searching for US records
[ ] Test sorting US records
[ ] Test relationships with other tables
[ ] Test GIS views and joins
[ ] Test data export/import functions
[ ] Test report generation

ROLLBACK PROCEDURE:
------------------
If issues arise, restore from backup and run the reverse migration scripts.
"""
    
    return instructions

def main():
    """Generate migration documentation"""
    
    # Generate instructions
    instructions = generate_migration_instructions()
    
    # Save to file
    output_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'US_FIELD_MIGRATION_GUIDE.md'
    )
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"Migration guide generated: {output_file}")
    print("\nPlease review the guide and follow the instructions carefully.")

if __name__ == '__main__':
    main()