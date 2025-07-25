#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to fix SQLite geometry issues in PyArchInit structure files
This version properly handles Spatialite geometry columns
"""

import os
import re

# Template for the fixed code
FIX_TEMPLATE = """
    # Only create the table if it doesn't exist
    try:
        metadata.create_all(engine, checkfirst=True)
        
        # For SQLite, add geometry column using Spatialite if not exists
        if 'sqlite' in conn_str.lower():
            try:
                # Check if geometry column already exists
                from sqlalchemy import inspect
                inspector = inspect(engine)
                columns = [col['name'] for col in inspector.get_columns('{table_name}')]
                
                if 'the_geom' not in columns:
                    # Add geometry column using raw SQL
                    with engine.connect() as conn:
                        # Ensure Spatialite is loaded
                        try:
                            conn.execute("SELECT InitSpatialMetadata(1)")
                        except:
                            pass  # Already initialized
                        
                        # Add geometry column
                        conn.execute("SELECT AddGeometryColumn('{table_name}', 'the_geom', -1, '{geom_type}', 'XY')")
            except Exception as e:
                # Geometry column might already exist or Spatialite not available
                pass
    except Exception as e:
        # Table creation failed, but continue
        pass"""

def get_table_name_and_geom_type(content):
    """Extract table name and geometry type from the file content"""
    # Find table name
    table_match = re.search(r"Table\s*\(\s*['\"]([^'\"]+)['\"]", content)
    if not table_match:
        return None, None
    table_name = table_match.group(1)
    
    # Find geometry type
    geom_match = re.search(r"Geometry\s*\(\s*geometry_type\s*=\s*['\"]([^'\"]+)['\"]", content)
    geom_type = geom_match.group(1) if geom_match else 'POINT'
    
    return table_name, geom_type

def fix_geometry_in_file(file_path):
    """Fix geometry handling for SQLite in a structure file"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file already imports Geometry from geoalchemy2
    if 'from geoalchemy2 import Geometry' not in content:
        return False, "No geometry import found"
    
    # Check if already fixed
    if "'sqlite' in conn_str.lower():" in content:
        return False, "Already fixed"
    
    # Get table name and geometry type
    table_name, geom_type = get_table_name_and_geom_type(content)
    if not table_name:
        return False, "Could not find table name"
    
    # Replace metadata.create_all(engine) with our fixed version
    if 'metadata.create_all(engine)' in content:
        fix_code = FIX_TEMPLATE.format(table_name=table_name, geom_type=geom_type)
        content = content.replace('    metadata.create_all(engine)', fix_code)
        
        # Write the modified content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, f"Fixed successfully for table {table_name} with {geom_type} geometry"
    
    return False, "Could not find metadata.create_all"

def main():
    structures_dir = "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/modules/db/structures"
    
    # List of files that need fixing - all files with geometry
    files_to_fix = [
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
        'pyus_negative.py',
        'pyuscaratterizzazioni.py'
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