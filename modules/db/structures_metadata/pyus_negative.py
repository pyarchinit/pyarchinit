"""
Created on 17 11 2020

@author: Enzo Cocca
"""

from sqlalchemy import Table, Column, Integer, Text,  UniqueConstraint


# Vector layer representing negative archaeological units and their associated documentation
class pyus_negative:
    @classmethod
    def define_table(cls, metadata):
        # Check if SQLite to handle geometry differently
        from modules.db.pyarchinit_conn_strings import Connection
        internal_connection = Connection()
        conn_str = internal_connection.conn_str()
        
        if 'sqlite' in conn_str.lower():
            # For SQLite/Spatialite, create table without geometry column
            return Table('pyarchinit_us_negative_doc', metadata,
                     # Unique identifier for each negative unit record
                     Column('gid', Integer, primary_key=True))
        else:
            # For PostgreSQL/PostGIS
                        return Table('pyarchinit_us_negative_doc', metadata,
                     # Unique identifier for each negative unit record
                     Column('gid', Integer, primary_key=True))