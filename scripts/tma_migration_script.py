#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TMA Migration Script
Migrates the TMA table from 39 fields to 26 fields with a separate materials table
"""

import sys
import os
from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from modules.db.entities.TMA import TMA
from modules.db.entities.TMA_MATERIALI import TMA_MATERIALI


def execute_sql(engine, sql):
    """SQLAlchemy 2.0 compatible execute wrapper for migration script."""
    sql_str = str(sql).strip().upper() if isinstance(sql, str) else str(sql).strip().upper()
    is_write = sql_str.startswith(('INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE'))

    if isinstance(sql, str):
        sql = text(sql)

    if is_write:
        with engine.begin() as conn:
            result = conn.execute(sql)
            try:
                return result.fetchall()
            except:
                return []
    else:
        with engine.connect() as conn:
            result = conn.execute(sql)
            try:
                return result.fetchall()
            except:
                return []


def migrate_tma_database():
    """Main migration function"""
    try:
        # Get connection string
        conn = Connection()
        conn_str = conn.conn_str()
        
        # Create engine
        engine = create_engine(conn_str, echo=True)
        metadata = MetaData()
        
        # Check if we're using SQLite or PostgreSQL
        is_sqlite = 'sqlite' in conn_str.lower()
        
        # Check if old table exists
        if is_sqlite:
            result = execute_sql(engine, "SELECT name FROM sqlite_master WHERE type='table' AND name='tma_table'")
            old_table_exists = len(result) > 0
        else:
            result = execute_sql(engine, """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'tma_table'
                )
            """)
            old_table_exists = result[0][0] if result else False
        
        if not old_table_exists:
            print("Old tma_table not found. Creating new structure directly.")
            # The new tables will be created automatically by the mapper
            return True
        
        print("Found old tma_table. Starting migration...")
        
        # Step 1: Backup existing data
        print("Step 1: Backing up existing data...")
        old_data = execute_sql(engine, "SELECT * FROM tma_table")
        print(f"Found {len(old_data)} records to migrate")

        # Step 2: Drop the old table
        print("Step 2: Dropping old table...")
        execute_sql(engine, "DROP TABLE IF EXISTS tma_table")
        
        # Step 3: Create new tables (they will be created by the mapper when we import the entities)
        print("Step 3: Creating new table structure...")
        # Import the mapper to trigger table creation
        from modules.db import pyarchinit_db_mapper
        
        # Step 4: Migrate data
        print("Step 4: Migrating data...")
        Session = sessionmaker(bind=engine)
        session = Session()
        
        migrated_count = 0
        for row in old_data:
            try:
                # Create main TMA record with new 26-field structure
                tma_record = TMA(
                    id=row.id,
                    sito=row.sito,
                    area=row.area,
                    ogtm=row.oggetto if hasattr(row, 'oggetto') else '',
                    ldct='',  # New field
                    ldcn=row.us if hasattr(row, 'us') else '',
                    vecchia_collocazione=row.vecchia_collocazione if hasattr(row, 'vecchia_collocazione') else '',
                    cassetta=row.nr_cassa if hasattr(row, 'nr_cassa') else '',
                    scan=row.nome_scavo if hasattr(row, 'nome_scavo') else '',
                    saggio=row.saggio if hasattr(row, 'saggio') else '',
                    vano_locus=row.vano if hasattr(row, 'vano') else '',
                    dscd=row.data_scavo if hasattr(row, 'data_scavo') else '',
                    dscu=row.us if hasattr(row, 'us') else '',
                    rcgd='',  # New field
                    rcgz='',  # New field
                    aint='',  # New field
                    aind='',  # New field
                    dtzg=row.cronologia if hasattr(row, 'cronologia') else '',
                    deso=row.definizione if hasattr(row, 'definizione') else '',
                    nsc='',  # Historical notes - new field
                    ftap='',  # New field
                    ftan='',  # New field
                    drat='',  # New field
                    dran='',  # New field
                    draa='',  # New field
                    created_at='',
                    updated_at='',
                    created_by='migration',
                    updated_by='migration'
                )
                
                session.add(tma_record)
                session.flush()  # Get the ID
                
                # Create material records (if there's material data in the old record)
                if hasattr(row, 'elemento') and row.elemento:
                    material_record = TMA_MATERIALI(
                        id=None,  # Auto-increment
                        id_tma=tma_record.id,
                        madi=row.numero_inventario_serie if hasattr(row, 'numero_inventario_serie') else '',
                        macc=row.elemento if hasattr(row, 'elemento') else '',
                        macl=row.tipo if hasattr(row, 'tipo') else '',
                        macp='',  # New field
                        macd=row.definizione if hasattr(row, 'definizione') else '',
                        cronologia_mac=row.cronologia if hasattr(row, 'cronologia') else '',
                        macq=str(row.quantita) if hasattr(row, 'quantita') else '0',
                        peso=float(row.peso) if hasattr(row, 'peso') and row.peso else 0.0,
                        created_at='',
                        updated_at='',
                        created_by='migration',
                        updated_by='migration'
                    )
                    session.add(material_record)
                
                migrated_count += 1
                
            except Exception as e:
                print(f"Error migrating record {row.id}: {str(e)}")
                session.rollback()
                continue
        
        # Commit all changes
        session.commit()
        session.close()
        
        print(f"\nMigration completed successfully!")
        print(f"Migrated {migrated_count} out of {len(old_data)} records")
        
        return True
        
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = migrate_tma_database()
    sys.exit(0 if success else 1)