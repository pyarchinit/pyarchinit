'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer,  Text,  UniqueConstraint


# Vector layer representing vertical stratigraphic units in archaeological contexts with specific measurements
class pyunitastratigrafiche_usm:
    @classmethod
    def define_table(cls, metadata):
        # Check if SQLite to handle geometry differently
        from modules.db.pyarchinit_conn_strings import Connection
        conn_str = internal_connection.conn_str()
        
        if 'sqlite' in conn_str.lower():
            # For SQLite/Spatialite, create table without geometry column
            return Table('pyunitastratigrafiche_usm', metadata,
                     # Unique identifier for each stratigraphic unit record
                     Column('gid', Integer, primary_key=True))
        else:
            # For PostgreSQL/PostGIS
                        return Table('pyunitastratigrafiche_usm', metadata,
                     # Unique identifier for each stratigraphic unit record
                     Column('gid', Integer, primary_key=True))