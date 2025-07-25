#!/usr/bin/env python3
"""
Update the pyarchinit_us_view definition to use ROWID properly and ensure
only the specified columns are returned.
"""

import os
import sys
import sqlite3

def update_view_definition(db_path):
    """Update the pyarchinit_us_view to ensure proper column selection"""
    
    print(f"Connecting to database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # First check current view definition
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='view' AND name='pyarchinit_us_view'
        """)
        
        result = cursor.fetchone()
        if not result:
            print("View 'pyarchinit_us_view' not found!")
            return False
        
        print("Current view definition:")
        print(result[0])
        print("\n" + "="*80 + "\n")
        
        # Drop the existing view
        print("Dropping existing view...")
        cursor.execute("DROP VIEW IF EXISTS pyarchinit_us_view")
        
        # Create the view with explicit ROWID
        print("Creating updated view with explicit columns...")
        cursor.execute("""
            CREATE VIEW pyarchinit_us_view AS 
            SELECT 
                CAST(pyunitastratigrafiche.gid AS INTEGER) as gid,
                pyunitastratigrafiche.the_geom as the_geom,
                pyunitastratigrafiche.tipo_us_s as tipo_us_s,
                pyunitastratigrafiche.scavo_s as scavo_s,
                pyunitastratigrafiche.area_s as area_s,
                pyunitastratigrafiche.us_s as us_s,
                pyunitastratigrafiche.stratigraph_index_us as stratigraph_index_us,
                us_table.id_us as id_us,
                us_table.sito as sito,
                us_table.area as area,
                us_table.us as us,
                us_table.struttura as struttura,
                us_table.d_stratigrafica as d_stratigrafica,
                us_table.d_interpretativa as d_interpretativa,
                us_table.descrizione as descrizione,
                us_table.interpretazione as interpretazione,
                us_table.rapporti as rapporti,
                us_table.periodo_iniziale as periodo_iniziale,
                us_table.fase_iniziale as fase_iniziale,
                us_table.periodo_finale as periodo_finale,
                us_table.fase_finale as fase_finale,
                us_table.anno_scavo as anno_scavo,
                pyunitastratigrafiche.ROWID as ROWID
            FROM pyunitastratigrafiche
            JOIN us_table ON pyunitastratigrafiche.scavo_s = us_table.sito 
                AND pyunitastratigrafiche.area_s = us_table.area 
                AND pyunitastratigrafiche.us_s = us_table.us
        """)
        
        # Verify the new view
        cursor.execute("PRAGMA table_info(pyarchinit_us_view)")
        columns = cursor.fetchall()
        
        print("\nNew view columns:")
        for col in columns:
            print(f"  {col[0]}: {col[1]} ({col[2]})")
        
        # Test the view
        cursor.execute("SELECT COUNT(*) FROM pyarchinit_us_view")
        count = cursor.fetchone()[0]
        print(f"\nView contains {count} records")
        
        # Try to register in geometry columns if the table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='geometry_columns'
        """)
        
        if cursor.fetchone():
            print("\nRegistering view in geometry_columns...")
            # Remove any existing registration
            cursor.execute("""
                DELETE FROM geometry_columns 
                WHERE f_table_name = 'pyarchinit_us_view'
            """)
            
            # Get geometry info from source table
            cursor.execute("""
                SELECT coord_dimension, srid, type 
                FROM geometry_columns 
                WHERE f_table_name = 'pyunitastratigrafiche' 
                AND f_geometry_column = 'the_geom'
            """)
            
            geo_info = cursor.fetchone()
            if geo_info:
                cursor.execute("""
                    INSERT INTO geometry_columns 
                    (f_table_name, f_geometry_column, coord_dimension, srid, geometry_type)
                    VALUES 
                    ('pyarchinit_us_view', 'the_geom', ?, ?, ?)
                """, geo_info)
                print("View registered in geometry_columns")
        
        conn.commit()
        print("\nView updated successfully!")
        
        # Show sample data
        print("\nSample data from view (first 5 rows):")
        cursor.execute("""
            SELECT gid, tipo_us_s, scavo_s, area_s, us_s, sito, area, us 
            FROM pyarchinit_us_view 
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            print(f"  GID: {row[0]}, Tipo: {row[1]}, Scavo: {row[2]}, "
                  f"Area_s: {row[3]}, US_s: {row[4]}, Sito: {row[5]}, "
                  f"Area: {row[6]}, US: {row[7]}")
        
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
    
    update_view_definition(db_path)

if __name__ == "__main__":
    main()