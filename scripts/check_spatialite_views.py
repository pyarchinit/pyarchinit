#!/usr/bin/env python3
"""
Check SpatiaLite views registration status
"""

import os
import sys
import sqlite3

def check_spatialite_views(db_path):
    """Check the registration status of SpatiaLite views"""
    
    print(f"Checking database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if views_geometry_columns exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='views_geometry_columns'
        """)
        
        if cursor.fetchone():
            print("\n✓ views_geometry_columns table exists")
            
            # Check registrations
            cursor.execute("""
                SELECT view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only
                FROM views_geometry_columns
                WHERE view_name = 'pyarchinit_us_view'
            """)
            
            result = cursor.fetchone()
            if result:
                print(f"\n✓ pyarchinit_us_view is registered:")
                print(f"  - Geometry column: {result[1]}")
                print(f"  - ROWID column: {result[2]}")
                print(f"  - Source table: {result[3]}")
                print(f"  - Source geometry: {result[4]}")
                print(f"  - Read only: {result[5]}")
            else:
                print("\n✗ pyarchinit_us_view is NOT registered in views_geometry_columns")
        else:
            print("\n✗ views_geometry_columns table does not exist")
        
        # Check if geometry_columns exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='geometry_columns'
        """)
        
        if cursor.fetchone():
            print("\n✓ geometry_columns table exists")
            
            # Check if view is registered here too
            cursor.execute("""
                SELECT f_table_name, f_geometry_column, coord_dimension, srid, geometry_type
                FROM geometry_columns
                WHERE f_table_name = 'pyarchinit_us_view'
            """)
            
            result = cursor.fetchone()
            if result:
                print(f"\n✓ pyarchinit_us_view is also in geometry_columns:")
                print(f"  - Geometry column: {result[1]}")
                print(f"  - Dimensions: {result[2]}")
                print(f"  - SRID: {result[3]}")
                print(f"  - Type: {result[4]}")
            else:
                print("\n✗ pyarchinit_us_view is NOT in geometry_columns")
        
        # Check if the view exists
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='view' AND name='pyarchinit_us_view'
        """)
        
        result = cursor.fetchone()
        if result:
            print("\n✓ pyarchinit_us_view exists")
            print("\nView definition:")
            print(result[0])
        else:
            print("\n✗ pyarchinit_us_view does NOT exist")
        
        # Check if source table has geometry
        cursor.execute("""
            SELECT f_table_name, f_geometry_column, coord_dimension, srid, geometry_type
            FROM geometry_columns
            WHERE f_table_name = 'pyunitastratigrafiche'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"\n✓ Source table pyunitastratigrafiche has geometry:")
            print(f"  - Geometry column: {result[1]}")
            print(f"  - Dimensions: {result[2]}")
            print(f"  - SRID: {result[3]}")
            print(f"  - Type: {result[4]}")
        
        # Try to manually register the view if needed
        print("\n" + "="*80)
        print("Attempting to fix registration...")
        
        # First ensure the view is properly registered
        try:
            # For views_geometry_columns
            cursor.execute("""
                DELETE FROM views_geometry_columns 
                WHERE view_name = 'pyarchinit_us_view'
            """)
            
            cursor.execute("""
                INSERT INTO views_geometry_columns 
                (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only)
                VALUES 
                ('pyarchinit_us_view', 'the_geom', 'rowid', 'pyunitastratigrafiche', 'the_geom', 1)
            """)
            
            print("✓ Registered in views_geometry_columns")
        except Exception as e:
            print(f"Could not register in views_geometry_columns: {e}")
        
        # Also try geometry_columns
        try:
            # Get geometry info from source
            cursor.execute("""
                SELECT coord_dimension, srid, geometry_type 
                FROM geometry_columns 
                WHERE f_table_name = 'pyunitastratigrafiche' 
                AND f_geometry_column = 'the_geom'
            """)
            
            geo_info = cursor.fetchone()
            if geo_info:
                cursor.execute("""
                    DELETE FROM geometry_columns 
                    WHERE f_table_name = 'pyarchinit_us_view'
                """)
                
                # Check if spatial_index_enabled column exists
                cursor.execute("PRAGMA table_info(geometry_columns)")
                cols = [col[1] for col in cursor.fetchall()]
                
                if 'spatial_index_enabled' in cols:
                    cursor.execute("""
                        INSERT INTO geometry_columns 
                        (f_table_name, f_geometry_column, coord_dimension, srid, geometry_type, spatial_index_enabled)
                        VALUES 
                        ('pyarchinit_us_view', 'the_geom', ?, ?, ?, 0)
                    """, geo_info)
                else:
                    cursor.execute("""
                        INSERT INTO geometry_columns 
                        (f_table_name, f_geometry_column, coord_dimension, srid, geometry_type)
                        VALUES 
                        ('pyarchinit_us_view', 'the_geom', ?, ?, ?)
                    """, geo_info)
                
                print("✓ Registered in geometry_columns")
        except Exception as e:
            print(f"Could not register in geometry_columns: {e}")
        
        conn.commit()
        conn.close()
        
        print("\n✓ Registration check complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

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
    
    check_spatialite_views(db_path)

if __name__ == "__main__":
    main()