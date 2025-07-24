#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyArchInit Migration Script: Update Entity Classes for US field type change
This script updates the SQLAlchemy table structures to change US fields from Integer to String

Author: PyArchInit Team
Date: 2025-07-24
"""

import os
import re
import shutil
from datetime import datetime

# Define the files to update and their US field mappings
FILES_TO_UPDATE = {
    'US_table.py': {
        'field': 'us',
        'old': 'Column(Integer)',
        'new': 'Column(String)'
    },
    'Campioni_table.py': {
        'field': 'us',
        'old': 'Column(Integer)',
        'new': 'Column(String)'
    },
    'Pottery_table.py': {
        'field': 'us', 
        'old': 'Column(Integer)',
        'new': 'Column(String)'
    },
    'US_table_toimp.py': {
        'field': 'us',
        'old': 'Column(Integer)',
        'new': 'Column(String)'
    },
    'pyquote.py': {
        'field': 'us_q',
        'old': 'Column(Integer)',
        'new': 'Column(String)'
    },
    'pyquote_usm.py': {
        'field': 'us_q',
        'old': 'Column(Integer)',
        'new': 'Column(String)'
    },
    'pyunitastratigrafiche.py': {
        'field': 'us_s',
        'old': 'Column(Integer)',
        'new': 'Column(String)'
    },
    'pyunitastratigrafiche_usm.py': {
        'field': 'us_s',
        'old': 'Column(Integer)',
        'new': 'Column(String)'
    },
    'pyus_negative.py': {
        'field': 'us_n',
        'old': 'Column(Integer)',
        'new': 'Column(String)'
    },
    'pyuscaratterizzazioni.py': {
        'field': 'us_c',
        'old': 'Column(Integer)', 
        'new': 'Column(String)'
    }
}

def update_file(filepath, field_name, old_pattern, new_pattern):
    """Update a single file to change field type"""
    
    # Create backup
    backup_path = filepath + '.backup_' + datetime.now().strftime('%Y%m%d_%H%M%S')
    shutil.copy2(filepath, backup_path)
    print(f"Created backup: {backup_path}")
    
    # Read file content
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create regex pattern to match the field definition
    # Match patterns like: us = Column(Integer)
    pattern = rf'^(\s*{re.escape(field_name)}\s*=\s*)Column\s*\(\s*Integer\s*\)'
    replacement = rf'\1Column(String)'
    
    # Count replacements
    new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
    
    if count > 0:
        # Write updated content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}: {count} occurrence(s) of '{field_name}' changed from Integer to String")
    else:
        print(f"No changes needed in {filepath} for field '{field_name}'")
        # Remove unnecessary backup
        os.remove(backup_path)
    
    return count

def main():
    """Main migration function"""
    print("=" * 60)
    print("PyArchInit Entity Classes Migration")
    print("Converting US fields from Integer to String")
    print("=" * 60)
    
    # Base directory for structures
    base_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'modules', 'db', 'structures'
    )
    
    total_changes = 0
    
    for filename, config in FILES_TO_UPDATE.items():
        filepath = os.path.join(base_dir, filename)
        
        if os.path.exists(filepath):
            changes = update_file(
                filepath, 
                config['field'], 
                config['old'], 
                config['new']
            )
            total_changes += changes
        else:
            print(f"WARNING: File not found: {filepath}")
    
    print("=" * 60)
    print(f"Migration complete. Total changes: {total_changes}")
    print("=" * 60)
    
    # Also update inventario_materiali_table.py if it has commented Integer version
    inv_materiali_path = os.path.join(base_dir, 'Inventario_materiali_table.py')
    if os.path.exists(inv_materiali_path):
        print("\nChecking inventario_materiali_table.py for commented Integer definitions...")
        
        with open(inv_materiali_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove commented Integer definition if exists
        pattern = r'#\s*us\s*=\s*Column\s*\(\s*Integer\s*\)'
        new_content = re.sub(pattern, '', content)
        
        if new_content != content:
            with open(inv_materiali_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("Removed commented Integer definition from inventario_materiali_table.py")

if __name__ == '__main__':
    main()