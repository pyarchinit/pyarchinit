#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to fix SQLite geometry issues in PyArchInit structures_metadata files
"""

import os
import re

def fix_geometry_in_metadata_file(file_path):
    """Fix geometry handling for SQLite in a structures_metadata file"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file already imports Geometry from geoalchemy2
    if 'from geoalchemy2 import Geometry' not in content:
        return False, "No geometry import found"
    
    # Check if already fixed
    if "'sqlite' in conn_str.lower():" in content:
        return False, "Already fixed"
    
    # Find the define_table method
    define_pattern = r'@classmethod\s+def\s+define_table\(cls,\s*metadata\):(.*?)(?=\n    @|\n\s*class|\Z)'
    define_match = re.search(define_pattern, content, re.DOTALL)
    
    if not define_match:
        return False, "Could not find define_table method"
    
    method_content = define_match.group(1)
    
    # Find the table name and geometry type
    table_match = re.search(r"Table\s*\(\s*['\"]([^'\"]+)['\"]", method_content)
    if not table_match:
        return False, "Could not find table name"
    table_name = table_match.group(1)
    
    # Find geometry type
    geom_match = re.search(r"Geometry\s*\(\s*geometry_type\s*=\s*['\"]([^'\"]+)['\"]", method_content)
    if not geom_match:
        return False, "Could not find geometry type"
    geom_type = geom_match.group(1)
    
    # Extract the Table definition
    table_pattern = r'(return\s+Table\s*\(.*?\))'
    table_match = re.search(table_pattern, method_content, re.DOTALL)
    if not table_match:
        return False, "Could not find Table definition"
    
    original_table = table_match.group(1)
    
    # Create SQLite version without geometry column
    sqlite_table = original_table
    # Remove the geometry column line and the comma before it
    sqlite_table = re.sub(r',\s*Column\s*\(\s*[\'"]the_geom[\'"].*?Geometry.*?\)[^\)]*', '', sqlite_table)
    
    # Build new method content
    new_method = f"""@classmethod
    def define_table(cls, metadata):
        # Check if SQLite to handle geometry differently
        from modules.db.pyarchinit_conn_strings import Connection
        internal_connection = Connection()
        conn_str = internal_connection.conn_str()
        
        if 'sqlite' in conn_str.lower():
            # For SQLite/Spatialite, create table without geometry column
            {sqlite_table}
        else:
            # For PostgreSQL/PostGIS
            from geoalchemy2 import Geometry
            {original_table}"""
    
    # Replace the method in content
    content = content[:define_match.start()] + new_method + content[define_match.end():]
    
    # Remove the top-level geoalchemy2 import and add Connection import
    content = content.replace('from geoalchemy2 import Geometry\n', '')
    
    # Add Connection import if not present
    if 'from modules.db.pyarchinit_conn_strings import Connection' not in content:
        # Find where to insert the import (after other imports)
        import_pattern = r'(from sqlalchemy import.*?\n)'
        import_match = re.search(import_pattern, content)
        if import_match:
            insert_pos = import_match.end()
            content = content[:insert_pos] + 'from modules.db.pyarchinit_conn_strings import Connection\n' + content[insert_pos:]
    
    # Write the modified content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True, f"Fixed {table_name} with {geom_type} geometry"

def main():
    structures_dir = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/modules/db/structures_metadata"
    
    print("Fixing SQLite geometry issues in structures_metadata files...")
    
    # Get all .py files in the directory
    py_files = [f for f in os.listdir(structures_dir) if f.endswith('.py') and not f.startswith('__')]
    
    for filename in sorted(py_files):
        file_path = os.path.join(structures_dir, filename)
        print(f"\nProcessing {filename}...")
        success, message = fix_geometry_in_metadata_file(file_path)
        if success:
            print(f"  ✓ {message}")
        else:
            print(f"  - {message}")
    
    print("\nDone!")

if __name__ == "__main__":
    main()