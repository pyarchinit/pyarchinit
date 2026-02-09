#!/usr/bin/env python3
"""
Script per ricreare la view pyarchinit_us_view con ORDER BY corretto.
Eseguire dalla console Python di QGIS o come script standalone.
"""

import sqlite3
import os


def recreate_us_view(db_path):
    """
    Ricrea la view pyarchinit_us_view con ORDER BY order_layer ASC.

    Args:
        db_path: Percorso al database SQLite/Spatialite
    """

    if not os.path.exists(db_path):
        print(f"ERRORE: Database non trovato: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Drop existing view
        print("Eliminazione view esistente...")
        cursor.execute("DROP VIEW IF EXISTS pyarchinit_us_view")

        # Get columns from us_table to build the view dynamically
        cursor.execute("PRAGMA table_info(us_table)")
        us_columns = [row[1] for row in cursor.fetchall()]

        cursor.execute("PRAGMA table_info(pyunitastratigrafiche)")
        geo_columns = [row[1] for row in cursor.fetchall()]

        # Build SELECT clause
        select_parts = []

        # Geometry table columns
        if 'gid' in geo_columns:
            select_parts.append("CAST(pyunitastratigrafiche.gid AS INTEGER) as gid")
        if 'the_geom' in geo_columns:
            select_parts.append("pyunitastratigrafiche.the_geom")
        if 'tipo_us_s' in geo_columns:
            select_parts.append("pyunitastratigrafiche.tipo_us_s")
        if 'scavo_s' in geo_columns:
            select_parts.append("pyunitastratigrafiche.scavo_s")
        if 'area_s' in geo_columns:
            select_parts.append("pyunitastratigrafiche.area_s")
        if 'us_s' in geo_columns:
            select_parts.append("pyunitastratigrafiche.us_s")
        if 'stratigraph_index_us' in geo_columns:
            select_parts.append("pyunitastratigrafiche.stratigraph_index_us")

        # US table columns (excluding duplicates)
        skip_columns = ['gid', 'the_geom', 'tipo_us_s', 'scavo_s', 'area_s', 'us_s']
        for col in us_columns:
            if col not in skip_columns:
                select_parts.append(f"us_table.{col}")

        select_clause = ",\n                    ".join(select_parts)

        create_sql = f"""
            CREATE VIEW pyarchinit_us_view AS
            SELECT
                    {select_clause}
            FROM pyunitastratigrafiche
            JOIN us_table ON
                pyunitastratigrafiche.scavo_s = us_table.sito AND
                pyunitastratigrafiche.area_s = us_table.area AND
                pyunitastratigrafiche.us_s = us_table.us
            ORDER BY us_table.order_layer ASC, pyunitastratigrafiche.stratigraph_index_us ASC
        """

        print("Creazione nuova view con ORDER BY...")
        cursor.execute(create_sql)

        # Update views_geometry_columns if exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='views_geometry_columns'")
        if cursor.fetchone():
            cursor.execute("DELETE FROM views_geometry_columns WHERE view_name = 'pyarchinit_us_view'")
            cursor.execute("""
                INSERT OR REPLACE INTO views_geometry_columns
                (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only)
                VALUES ('pyarchinit_us_view', 'the_geom', 'gid', 'pyunitastratigrafiche', 'the_geom', 1)
            """)
            print("Registrata geometria in views_geometry_columns")

        conn.commit()
        print("View pyarchinit_us_view ricreata con successo!")

        # Verify
        cursor.execute("SELECT sql FROM sqlite_master WHERE name='pyarchinit_us_view'")
        result = cursor.fetchone()
        if result and 'ORDER BY' in result[0]:
            print("✓ ORDER BY presente nella view")

        return True

    except Exception as e:
        print(f"ERRORE: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def main():
    """Entry point - trova il database dalla configurazione."""
    import sys

    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        # Try to find from config
        home = os.path.expanduser("~")
        config_path = os.path.join(home, 'pyarchinit_DB_folder', 'config.cfg')

        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = f.read()
            # Parse config to find database
            for line in config.split('\n'):
                if 'DATABASE' in line and '=' in line:
                    db_name = line.split('=')[1].strip()
                    db_path = os.path.join(home, 'pyarchinit_DB_folder', db_name)
                    break
        else:
            # Default path
            db_path = os.path.join(home, 'pyarchinit_DB_folder', 'pyarchinit_db.sqlite')

    print(f"Database: {db_path}")
    recreate_us_view(db_path)


if __name__ == "__main__":
    main()
