#!/usr/bin/env python3
"""
Fix SpatiaLite view registration for pyarchinit_us_view
This script ensures the view is properly registered in SpatiaLite's geometry metadata
so that QGIS only shows the columns defined in the view, not all columns from joined tables.
"""

import os
import sys
import sqlite3
from pathlib import Path

def fix_view_registration(db_path):
    """Fix the registration of pyarchinit_us_view in SpatiaLite metadata tables"""
    
    print(f"Connecting to database: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        conn.enable_load_extension(True)
        
        # Try to load SpatiaLite extension
        try:
            conn.load_extension('mod_spatialite')
        except:
            # Try alternative paths for different systems
            spatialite_paths = [
                'mod_spatialite.so',
                'mod_spatialite',
                '/usr/lib/x86_64-linux-gnu/mod_spatialite.so',
                '/usr/local/lib/mod_spatialite.dylib',
                'libspatialite.so',
                'libspatialite.dylib'
            ]
            loaded = False
            for path in spatialite_paths:
                try:
                    conn.load_extension(path)
                    loaded = True
                    break
                except:
                    continue
            if not loaded:
                print("Warning: Could not load SpatiaLite extension. Proceeding without it.")
        
        cursor = conn.cursor()
        
        # First, check if the view exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view' AND name='pyarchinit_us_view'
        """)
        
        if not cursor.fetchone():
            print("View 'pyarchinit_us_view' not found in database")
            return False
        
        print("View found. Checking geometry metadata...")
        
        # Check if views_geometry_columns table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='views_geometry_columns'
        """)
        
        if cursor.fetchone():
            # Remove any existing registration
            cursor.execute("""
                DELETE FROM views_geometry_columns 
                WHERE view_name = 'pyarchinit_us_view'
            """)
            
            # Register the view properly
            cursor.execute("""
                INSERT INTO views_geometry_columns 
                (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only)
                VALUES 
                ('pyarchinit_us_view', 'the_geom', 'ROWID', 'pyunitastratigrafiche', 'the_geom', 1)
            """)
            
            print("View registered in views_geometry_columns")
        else:
            print("views_geometry_columns table not found. This might be an older SpatiaLite version.")
        
        # Check if geometry_columns_auth table exists and update it
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='geometry_columns_auth'
        """)
        
        if cursor.fetchone():
            # Remove any existing entries
            cursor.execute("""
                DELETE FROM geometry_columns_auth 
                WHERE f_table_name = 'pyarchinit_us_view'
            """)
            
            # Get the SRID from the original table
            cursor.execute("""
                SELECT srid FROM geometry_columns_auth 
                WHERE f_table_name = 'pyunitastratigrafiche' 
                AND f_geometry_column = 'the_geom'
            """)
            
            result = cursor.fetchone()
            if result:
                srid = result[0]
                cursor.execute("""
                    INSERT INTO geometry_columns_auth 
                    (f_table_name, f_geometry_column, read_only, hidden, srid, auth_name, auth_srid)
                    VALUES 
                    ('pyarchinit_us_view', 'the_geom', 1, 0, ?, 'EPSG', ?)
                """, (srid, srid))
                
                print(f"View registered in geometry_columns_auth with SRID {srid}")
        
        # Alternative approach: Create a wrapper view with explicit column selection
        print("\nCreating explicit column view as pyarchinit_us_view_clean...")
        
        # Drop the view if it exists
        cursor.execute("DROP VIEW IF EXISTS pyarchinit_us_view_clean")
        
        # Create the view with explicit columns
        cursor.execute("""
            CREATE VIEW pyarchinit_us_view_clean AS 
            SELECT 
                gid,
                the_geom,
                tipo_us_s,
                scavo_s,
                area_s,
                us_s,
                stratigraph_index_us,
                id_us,
                sito,
                area,
                us,
                struttura,
                d_stratigrafica,
                d_interpretativa,
                descrizione,
                interpretazione,
                rapporti,
                periodo_iniziale,
                fase_iniziale,
                periodo_finale,
                fase_finale,
                anno_scavo
            FROM pyarchinit_us_view
        """)
        
        # Register the clean view
        if cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='views_geometry_columns'").fetchone():
            cursor.execute("""
                DELETE FROM views_geometry_columns 
                WHERE view_name = 'pyarchinit_us_view_clean'
            """)
            
            cursor.execute("""
                INSERT INTO views_geometry_columns 
                (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only)
                VALUES 
                ('pyarchinit_us_view_clean', 'the_geom', 'gid', 'pyarchinit_us_view', 'the_geom', 1)
            """)
        
        conn.commit()
        print("\nView registration completed successfully!")
        print("\nYou can now use 'pyarchinit_us_view_clean' in QGIS which will show only the defined columns.")
        
        # Show the columns in the clean view
        cursor.execute("PRAGMA table_info(pyarchinit_us_view_clean)")
        columns = cursor.fetchall()
        print("\nColumns in pyarchinit_us_view_clean:")
        for col in columns:
            print(f"  - {col[1]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # Default database path
    default_db = os.path.join(
        os.path.expanduser("~"),
        "pyarchinit_DB_folder",
        "pyarchinit_db.sqlite"
    )
    
    # Get database path from command line or use default
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = default_db
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        print("Please provide the correct path to your pyarchinit database")
        print(f"Usage: python {sys.argv[0]} /path/to/pyarchinit_db.sqlite")
        sys.exit(1)
    
    fix_view_registration(db_path)

if __name__ == "__main__":
    main()