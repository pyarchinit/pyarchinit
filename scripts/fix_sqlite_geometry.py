#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to fix SQLite geometry issues in PyArchInit structure files
"""

import os
import re

def fix_geometry_in_file(file_path):
    """Fix geometry handling for SQLite in a structure file"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file already imports Geometry from geoalchemy2
    if 'from geoalchemy2 import Geometry' not in content:
        return False, "No geometry import found"
    
    # Check if already fixed
    if "'sqlite' in conn_str.lower()" in content:
        return False, "Already fixed"
    
    # Find the table definition with geometry
    table_pattern = r'(\s+)(\w+)\s*=\s*Table\s*\(.*?\n\s*\)'
    table_matches = list(re.finditer(table_pattern, content, re.DOTALL))
    
    if not table_matches:
        return False, "No table definition found"
    
    # Process each table that has geometry
    modified = False
    for match in reversed(table_matches):  # Process in reverse to maintain positions
        table_content = match.group(0)
        if 'Geometry(' in table_content:
            indent = match.group(1)
            table_name = match.group(2)
            
            # Extract the table definition
            table_start = match.start()
            table_end = match.end()
            
            # Build new conditional table definition
            new_table_def = f"""{indent}# Check if SQLite to handle geometry differently
{indent}conn_str = internal_connection.conn_str()
{indent}if 'sqlite' in conn_str.lower():
{indent}    # For SQLite, skip geometry column
"""
            
            # Create SQLite version without geometry column
            sqlite_table = table_content
            # Remove the geometry column line
            sqlite_table = re.sub(r'.*Column\s*\(\s*[\'"]the_geom[\'"].*?Geometry.*?\).*?\n', '', sqlite_table)
            # Add extra indent
            sqlite_table = sqlite_table.replace('\n', '\n    ')
            new_table_def += sqlite_table
            
            new_table_def += f"""
{indent}else:
{indent}    # For PostgreSQL/PostGIS
{indent}    from geoalchemy2 import Geometry
"""
            # Add the original table with extra indent
            postgres_table = table_content.replace('\n', '\n    ')
            new_table_def += postgres_table
            
            # Replace in content
            content = content[:table_start] + new_table_def + content[table_end:]
            modified = True
    
    if modified:
        # Move the geoalchemy2 import inside the conditional
        content = content.replace('from geoalchemy2 import Geometry\n', '')
        
        # Write the modified content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, "Fixed successfully"
    
    return False, "No modifications needed"

def main():
    structures_dir = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/modules/db/structures"
    
    # List of files that need fixing
    files_to_fix = [
        'pyreperti.py',
        'pyquote.py',
        'pysito_point.py',
        'pytomba.py',
        'pyquote_usm.py',
        'pyindividui.py',
        'pyunitastratigrafiche.py',
        'pyunitastratigrafiche_usm.py',
        'pystrutture.py',
        'pysezioni.py',
        'pyripartizioni_spaziali.py',
        'pylineeriferimento.py',
        'pysito_polygon.py',
        'pydocumentazione.py',
        'pyus_negative.py'
    ]
    
    print("Fixing SQLite geometry issues in structure files...")
    
    for filename in files_to_fix:
        file_path = os.path.join(structures_dir, filename)
        if os.path.exists(file_path):
            print(f"\nProcessing {filename}...")
            success, message = fix_geometry_in_file(file_path)
            if success:
                print(f"  ✓ {message}")
            else:
                print(f"  - {message}")
        else:
            print(f"\n{filename} not found")
    
    print("\nDone!")

if __name__ == "__main__":
    main()