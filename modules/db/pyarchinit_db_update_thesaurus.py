# -*- coding: utf-8 -*-
"""
Thesaurus table update module for PyArchInit
Adds missing columns to pyarchinit_thesaurus_sigle table
"""

from sqlalchemy import text
from sqlalchemy.orm import Session
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsMessageLog, Qgis


def update_thesaurus_table(engine, metadata):
    """Update thesaurus table with new columns if they don't exist"""
    
    # Check if we're using SQLite or PostgreSQL
    is_sqlite = 'sqlite' in str(engine.url).lower()
    
    try:
        # Get existing columns
        with Session(engine) as session:
            if is_sqlite:
                result = session.execute(text("PRAGMA table_info(pyarchinit_thesaurus_sigle)"))
                existing_columns = [row[1] for row in result]
            else:
                # PostgreSQL
                result = session.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'pyarchinit_thesaurus_sigle'
                """))
                existing_columns = [row[0] for row in result]
        
        QgsMessageLog.logMessage(f"Existing columns in thesaurus: {existing_columns}", "PyArchInit", Qgis.Info)
        
        # Define columns to add if missing
        columns_to_add = []
        
        if 'order_layer' not in existing_columns:
            columns_to_add.append(('order_layer', 'INTEGER'))
            
        if 'id_parent' not in existing_columns:
            columns_to_add.append(('id_parent', 'INTEGER'))
            
        if 'parent_sigla' not in existing_columns:
            columns_to_add.append(('parent_sigla', 'VARCHAR(30)' if not is_sqlite else 'TEXT'))
            
        if 'hierarchy_level' not in existing_columns:
            columns_to_add.append(('hierarchy_level', 'INTEGER'))
        
            # Add missing columns
            for column_name, column_type in columns_to_add:
                try:
                    session.execute(text(f"ALTER TABLE pyarchinit_thesaurus_sigle ADD COLUMN {column_name} {column_type}"))
                    session.commit()
                        
                    QgsMessageLog.logMessage(f"Added column {column_name} to pyarchinit_thesaurus_sigle", "PyArchInit", Qgis.Info)
                    
                except Exception as e:
                    session.rollback()
                    if "duplicate column" not in str(e).lower() and "already exists" not in str(e).lower():
                        QgsMessageLog.logMessage(f"Error adding column {column_name}: {str(e)}", "PyArchInit", Qgis.Warning)
        
        # Update table aliases if needed
        update_thesaurus_aliases(engine, is_sqlite)
        
        return True
        
    except Exception as e:
        QgsMessageLog.logMessage(f"Error updating thesaurus table: {str(e)}", "PyArchInit", Qgis.Critical)
        return False


def update_thesaurus_aliases(engine, is_sqlite):
    """Update table name aliases in thesaurus"""
    try:
        # List of table name mappings
        table_mappings = [
            ('inventario_materiali_table', 'Inventario Materiali'),
            ('tomba_table', 'Tomba'),
            ('struttura_table', 'Struttura'),
            ('us_table', 'US'),
            ('us_table_usm', 'USM'),
            ('site_table', 'Sito'),
            ('pyarchinit_reperti', 'REPERTI'),
            ('tma_materiali_archeologici', 'TMA materiali archeologici'),
            ('tma_materiali_ripetibili', 'TMA Materiali Ripetibili'),
            ('tma_table', 'TMA materiali archeologici'),
            ('tma_materiali_table', 'TMA Materiali Ripetibili'),
            ('TMA materiali ripetibili', 'TMA Materiali Ripetibili'),
            ('individui_table', 'Individui'),
            ('pottery_table', 'Pottery'),
            ('campioni_table', 'Campioni'),
            ('documentazione_table', 'Documentazione')
        ]
        
        with Session(engine) as session:
            for db_name, alias in table_mappings:
                # Check if old name exists
                result = session.execute(text(
                    "SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle WHERE nome_tabella = :old_name"
                ).bindparams(old_name=db_name))
                
                count = result.scalar()
                
                if count > 0:
                    # Update to new alias
                    session.execute(text(
                        "UPDATE pyarchinit_thesaurus_sigle SET nome_tabella = :new_name WHERE nome_tabella = :old_name"
                    ).bindparams(new_name=alias, old_name=db_name))
                    
                    QgsMessageLog.logMessage(f"Updated table alias from {db_name} to {alias}", "PyArchInit", Qgis.Info)
            
            # Commit all changes
            session.commit()
            
    except Exception as e:
        QgsMessageLog.logMessage(f"Error updating table aliases: {str(e)}", "PyArchInit", Qgis.Warning)