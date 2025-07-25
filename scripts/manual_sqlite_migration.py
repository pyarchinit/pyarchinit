#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Manual SQLite US field migration script
Run this script to manually migrate US and area fields from INTEGER to TEXT
"""

import sqlite3
import sys
import os
import shutil
from datetime import datetime

def backup_database(db_path):
    """Create a backup of the database"""
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path

def clean_new_tables(conn):
    """Remove any leftover _new tables"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_new'")
    new_tables = cursor.fetchall()
    
    for table in new_tables:
        table_name = table[0]
        print(f"Removing leftover table: {table_name}")
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    
    conn.commit()

def migrate_table_fields(conn, table_name, fields_to_migrate):
    """Migrate specific fields in a table to TEXT type"""
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if not cursor.fetchone():
        print(f"Table {table_name} not found, skipping...")
        return False
    
    # Get table structure
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    # Check if migration is needed
    needs_migration = False
    for col in columns:
        col_name = col[1]
        col_type = col[2].upper()
        if col_name in fields_to_migrate and ('INTEGER' in col_type or 'BIGINT' in col_type):
            needs_migration = True
            print(f"  Field {col_name} needs migration from {col_type} to TEXT")
    
    if not needs_migration:
        print(f"Table {table_name} already migrated, skipping...")
        return True
    
    try:
        # Drop ALL views before ANY table migration
        views_to_drop = [
            'pyarchinit_quote_view',
            'pyarchinit_us_view',
            'pyarchinit_uscaratterizzazioni_view',
            'pyarchinit_quote_usm_view',
            'pyarchinit_usm_view',
            'pyarchinit_us_negative_doc_view',
            'pyarchinit_reperti_view'
        ]
        
        for view in views_to_drop:
            try:
                cursor.execute(f"DROP VIEW IF EXISTS {view}")
                print(f"  Dropped view: {view}")
            except:
                pass
        
        # Build new table definition
        new_table_sql = f"CREATE TABLE {table_name}_new ("
        column_defs = []
        
        for col in columns:
            col_id, col_name, col_type, col_notnull, col_default, col_pk = col
            
            # Change field type to TEXT if it's in the migration list
            if col_name in fields_to_migrate:
                col_type = 'TEXT'
            
            col_def = f"{col_name} {col_type}"
            
            if col_pk:
                col_def += " PRIMARY KEY"
                if col_name.startswith('id_'):
                    col_def += " AUTOINCREMENT"
            
            if col_notnull and not col_pk:
                col_def += " NOT NULL"
                
            if col_default is not None:
                col_def += f" DEFAULT {col_default}"
                
            column_defs.append(col_def)
        
        new_table_sql += ", ".join(column_defs) + ")"
        
        print(f"Creating new table structure for {table_name}...")
        cursor.execute(new_table_sql)
        
        # Copy data
        columns_list = [col[1] for col in columns]
        select_list = []
        for col_name in columns_list:
            if col_name in fields_to_migrate:
                select_list.append(f"CAST({col_name} AS TEXT)")
            else:
                select_list.append(col_name)
        
        columns_str = ", ".join(columns_list)
        select_str = ", ".join(select_list)
        
        print(f"Copying data to new table...")
        cursor.execute(f"INSERT INTO {table_name}_new ({columns_str}) SELECT {select_str} FROM {table_name}")
        
        # Drop old table and rename new one
        print(f"Replacing old table with new one...")
        cursor.execute(f"DROP TABLE {table_name}")
        cursor.execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name}")
        
        # Create indexes
        for field in fields_to_migrate:
            try:
                cursor.execute(f"CREATE INDEX idx_{table_name}_{field} ON {table_name}({field})")
            except:
                pass
        
        conn.commit()
        print(f"✓ Table {table_name} migrated successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error migrating table {table_name}: {e}")
        conn.rollback()
        # Clean up if migration failed
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}_new")
        conn.commit()
        return False

def recreate_views(conn):
    """Recreate views after migration"""
    cursor = conn.cursor()
    
    views = {
        'pyarchinit_quote_view': """
            CREATE VIEW pyarchinit_quote_view AS
            SELECT 
                pyarchinit_quote.sito_q, 
                pyarchinit_quote.area_q, 
                pyarchinit_quote.us_q, 
                pyarchinit_quote.unita_misu, 
                pyarchinit_quote.quota_q, 
                pyarchinit_quote.geometry, 
                us_table.id_us, 
                us_table.sito, 
                us_table.area, 
                us_table.us, 
                us_table.struttura, 
                us_table.d_stratigrafica AS definizione_stratigrafica, 
                us_table.d_interpretativa AS definizione_interpretativa, 
                us_table.descrizione, 
                us_table.interpretazione, 
                us_table.rapporti, 
                us_table.periodo_iniziale, 
                us_table.fase_iniziale, 
                us_table.periodo_finale, 
                us_table.fase_finale, 
                us_table.anno_scavo
            FROM pyarchinit_quote
            JOIN us_table ON 
                pyarchinit_quote.sito_q = us_table.sito 
                AND pyarchinit_quote.area_q = us_table.area 
                AND pyarchinit_quote.us_q = us_table.us
        """,
        
        'pyarchinit_us_view': """
            CREATE VIEW pyarchinit_us_view AS 
            SELECT 
                pyunitastratigrafiche.PK_UID, 
                pyunitastratigrafiche.geometry, 
                pyunitastratigrafiche.tipo_us_s, 
                pyunitastratigrafiche.scavo_s, 
                pyunitastratigrafiche.area_s, 
                pyunitastratigrafiche.us_s, 
                us_table.id_us, 
                us_table.sito, 
                us_table.area, 
                us_table.us, 
                us_table.struttura, 
                us_table.d_stratigrafica AS definizione_stratigrafica, 
                us_table.d_interpretativa AS definizione_interpretativa, 
                us_table.descrizione, 
                us_table.interpretazione, 
                us_table.rapporti, 
                us_table.periodo_iniziale, 
                us_table.fase_iniziale, 
                us_table.periodo_finale, 
                us_table.fase_finale, 
                us_table.anno_scavo
            FROM pyunitastratigrafiche
            JOIN us_table ON 
                pyunitastratigrafiche.scavo_s = us_table.sito 
                AND pyunitastratigrafiche.area_s = us_table.area 
                AND pyunitastratigrafiche.us_s = us_table.us
        """,
        
        'pyarchinit_reperti_view': """
            CREATE VIEW pyarchinit_reperti_view AS 
            SELECT
                a.gid,
                a.the_geom,
                a.id_rep,
                a.siti,
                b.id_invmat,
                b.sito,
                b.numero_inventario,
                b.tipo_reperto,
                b.criterio_schedatura,
                b.definizione,
                b.descrizione,
                b.area,
                b.us,
                b.lavato,
                b.nr_cassa,
                b.luogo_conservazione,
                b.stato_conservazione,
                b.datazione_reperto,
                b.elementi_reperto,
                b.misurazioni,
                b.rif_biblio,
                b.tecnologie,
                b.forme_minime,
                b.forme_massime,
                b.totale_frammenti,
                b.corpo_ceramico,
                b.rivestimento,
                b.diametro_orlo,
                b.peso,
                b.tipo,
                b.eve_orlo,
                b.repertato,
                b.diagnostico,
                b.n_reperto,
                b.tipo_contenitore,
                b.struttura,
                b.years,
                b.schedatore,
                b.date_scheda,
                b.punto_rinv,
                b.negativo_photo,
                b.diapositiva
            FROM pyarchinit_reperti a
            JOIN inventario_materiali_table b ON 
                a.siti = b.sito AND 
                a.id_rep = b.numero_inventario
        """
    }
    
    for view_name, view_sql in views.items():
        try:
            print(f"Creating view {view_name}...")
            cursor.execute(view_sql)
        except Exception as e:
            print(f"  Warning: Could not create view {view_name}: {e}")
    
    conn.commit()

def main():
    if len(sys.argv) < 2:
        print("Usage: python manual_sqlite_migration.py <path_to_sqlite_db>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        sys.exit(1)
    
    print(f"\n=== PyArchInit SQLite Migration Tool ===")
    print(f"Database: {db_path}")
    
    # Create backup
    backup_path = backup_database(db_path)
    
    conn = sqlite3.connect(db_path)
    
    try:
        print("\n=== Starting migration ===")
        
        # Clean up any leftover _new tables
        clean_new_tables(conn)
        
        # Define migrations
        migrations = [
            ('us_table', ['us', 'area']),
            ('campioni_table', ['us', 'area']),
            ('pottery_table', ['us', 'area']),
            ('inventario_materiali_table', ['us', 'area']),
            ('tomba_table', ['area']),
            ('us_table_toimp', ['us']),
            ('pyarchinit_quote', ['us_q']),
            ('pyarchinit_quote_usm', ['us_q']),
            ('pyunitastratigrafiche', ['us_s']),
            ('pyunitastratigrafiche_usm', ['us_s']),
            ('pyarchinit_us_negative_doc', ['us_n']),
            ('pyuscaratterizzazioni', ['us_c'])
        ]
        
        # Perform migrations
        success_count = 0
        for table_name, fields in migrations:
            print(f"\nMigrating {table_name}...")
            if migrate_table_fields(conn, table_name, fields):
                success_count += 1
        
        # Recreate views
        print("\n=== Recreating views ===")
        recreate_views(conn)
        
        # Final cleanup
        clean_new_tables(conn)
        
        print(f"\n=== Migration completed ===")
        print(f"Successfully migrated {success_count} tables")
        print(f"Backup saved at: {backup_path}")
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        print(f"Database backup is at: {backup_path}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()