'''
Created on 17 11 2020

@author: Enzo Cocca
'''

from sqlalchemy import Table, Column, Integer, Text,  UniqueConstraint


# Vector layer representing polygonal representations of archaeological sites
class pysito_polygon:
    @classmethod
    def define_table(cls, metadata):
        # Check if SQLite to handle geometry differently
        from modules.db.pyarchinit_conn_strings import Connection
        conn_str = internal_connection.conn_str()
        
        if 'sqlite' in conn_str.lower():
            # For SQLite/Spatialite, create table without geometry column
            return Table('pyarchinit_siti_polygonal', metadata,
                     # Unique identifier for each polygonal site record
                     Column('gid', Integer, primary_key=True))
        else:
            # For PostgreSQL/PostGIS
                        return Table('pyarchinit_siti_polygonal', metadata,
                     # Unique identifier for each polygonal site record
                     Column('gid', Integer, primary_key=True))