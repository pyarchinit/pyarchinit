#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test TMA loading using PyArchInit DB Manager
"""

import sys
import os

# Add the plugin path to sys.path
plugin_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, plugin_path)

from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management

# Create connection
conn = Connection()
conn_str = conn.conn_str()
print(f"Connection string: {conn_str}")

# Create DB manager
db_manager = Pyarchinit_db_management(conn_str)
db_manager.connection()

# Query TMA records
print("\n=== Testing TMA query ===")
try:
    tma_records = db_manager.query("TMA")
    print(f"Found {len(tma_records)} TMA records using query()")
    
    for i, record in enumerate(tma_records):
        print(f"\nRecord {i+1}:")
        print(f"  ID: {record.id}")
        print(f"  Sito: {record.sito}")
        print(f"  Area: {record.area}")
        print(f"  US: {record.dscu}")
        print(f"  LDCN: {record.ldcn}")
except Exception as e:
    print(f"Error querying TMA: {e}")
    import traceback
    traceback.print_exc()

# Also check the raw database
print("\n=== Checking raw database ===")
try:
    from sqlalchemy import text
    from sqlalchemy.orm import sessionmaker
    
    Session = sessionmaker(bind=db_manager.engine)
    session = Session()
    
    result = session.execute(text("SELECT COUNT(*) FROM tma_materiali_archeologici"))
    count = result.scalar()
    print(f"Total records in tma_materiali_archeologici table: {count}")
    
    # Show all records
    result = session.execute(text("SELECT id, sito, area, dscu, ldcn FROM tma_materiali_archeologici"))
    for row in result:
        print(f"  ID {row[0]}: Sito='{row[1]}', Area='{row[2]}', US='{row[3]}', LDCN='{row[4]}'")
    
    session.close()
except Exception as e:
    print(f"Error checking raw database: {e}")
    import traceback
    traceback.print_exc()