"""
Created on 17 11 2020

@author: Enzo Cocca
"""

from sqlalchemy import Table, Column, Integer, Text,  UniqueConstraint

# Vector layer containing the documentation records
class pydocumentazione:
    @classmethod
    def define_table(cls, metadata):
        # Check if SQLite to handle geometry differently
        from modules.db.pyarchinit_conn_strings import Connection
        conn_str = internal_connection.conn_str()
        
        if 'sqlite' in conn_str.lower():
            # For SQLite/Spatialite, create table without geometry column
            return Table('pyarchinit_documentazione', metadata,
                     # Unique identifier for each documentation record
                     Column('gid', Integer, primary_key=True))
        else:
            # For PostgreSQL/PostGIS
                        return Table('pyarchinit_documentazione', metadata,
                     # Unique identifier for each documentation record
                     Column('gid', Integer, primary_key=True))