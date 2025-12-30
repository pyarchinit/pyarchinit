'''
Created on 17 11 2020

@author: Enzo Cocca
'''

from sqlalchemy import Table, Column, Integer,  Text, UniqueConstraint


# Vector layer representing taxonomy records related to archaeological contexts
class pytomba:
    @classmethod
    def define_table(cls, metadata):
        # Check if SQLite to handle geometry differently
        from modules.db.pyarchinit_conn_strings import Connection
        conn_str = internal_connection.conn_str()
        
        if 'sqlite' in conn_str.lower():
            # For SQLite/Spatialite, create table without geometry column
            return Table('pyarchinit_tafonomia', metadata,
                     # Unique identifier for each taxonomy record
                     Column('gid', Integer, primary_key=True))
        else:
            # For PostgreSQL/PostGIS
                        return Table('pyarchinit_tafonomia', metadata,
                     # Unique identifier for each taxonomy record
                     Column('gid', Integer, primary_key=True))