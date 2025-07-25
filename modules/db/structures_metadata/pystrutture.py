'''
Created on 17 11 2020

@author: Enzo Cocca
'''

from sqlalchemy import Table, Column, Integer, Text, UniqueConstraint


# Class representing structures or hypotheses related to archaeological contexts
class pystrutture:
    @classmethod
    def define_table(cls, metadata):
        # Check if SQLite to handle geometry differently
        from modules.db.pyarchinit_conn_strings import Connection
        internal_connection = Connection()
        conn_str = internal_connection.conn_str()
        
        if 'sqlite' in conn_str.lower():
            # For SQLite/Spatialite, create table without geometry column
            return Table('pyarchinit_strutture_ipotesi', metadata,
                     # Unique identifier for each structure record
                     Column('gid', Integer, primary_key=True))
        else:
            # For PostgreSQL/PostGIS
                        return Table('pyarchinit_strutture_ipotesi', metadata,
                     # Unique identifier for each structure record
                     Column('gid', Integer, primary_key=True))