#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to fix TMA tables creation order and foreign key issues
"""

import os
import sys

# Add parent directory to path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Text, ForeignKey
from modules.db.pyarchinit_conn_strings import Connection


def create_tma_tables():
    """Create TMA tables in the correct order"""
    
    # Get connection
    conn = Connection()
    engine = create_engine(conn.conn_str(), echo=True)
    metadata = MetaData()
    
    # First create the main TMA table
    tma_table = Table('tma_materiali_archeologici', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('sito', Text),
                      Column('area', Text),
                      Column('riferimenti_tm', Text),
                      Column('descrizione', Text),
                      Column('vano_locus', Text),
                      Column('periodo', String(150)),
                      Column('cronologia', String(50)),
                      Column('valore_stimato', Float),
                      Column('created_at', String(50)),
                      Column('updated_at', String(50)),
                      Column('created_by', String(100)),
                      Column('updated_by', String(100)),
                      extend_existing=True
                      )
    
    # Then create the materials table with foreign key
    tma_materiali_table = Table('tma_materiali_ripetibili', metadata,
                               Column('id', Integer, primary_key=True),
                               Column('id_tma', Integer, ForeignKey('tma_materiali_archeologici.id'), nullable=False),
                               Column('madi', String(50)),
                               Column('macc', String(30), nullable=False),
                               Column('macl', String(30)),
                               Column('macp', String(30)),
                               Column('macd', String(30)),
                               Column('cronologia_mac', String(50)),
                               Column('macq', String(20)),
                               Column('peso', Float),
                               Column('created_at', String(50)),
                               Column('updated_at', String(50)),
                               Column('created_by', String(100)),
                               Column('updated_by', String(100)),
                               extend_existing=True
                               )
    
    # Create all tables
    try:
        metadata.create_all(engine)
        print("TMA tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")
        
    # Test the connection
    with engine.connect() as conn:
        result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'tma%'")
        tables = result.fetchall()
        print("\nExisting TMA tables:")
        for table in tables:
            print(f"  - {table[0]}")


if __name__ == '__main__':
    create_tma_tables()