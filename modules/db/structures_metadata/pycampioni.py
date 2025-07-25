"""
Created on 17 11 2020

@author: Enzo Cocca
"""

from sqlalchemy import Table, Column, Integer, Text,  UniqueConstraint

# Vector layer representing the samples collected during the archaeological surveyTable representing the samples collected during the archaeological survey
class pycampioni:
    @classmethod
    def define_table(cls, metadata):
        # Check if SQLite to handle geometry differently
        from modules.db.pyarchinit_conn_strings import Connection
        internal_connection = Connection()
        conn_str = internal_connection.conn_str()
        
        if 'sqlite' in conn_str.lower():
            # For SQLite/Spatialite, create table without geometry column
            return Table('pyarchinit_campionature', metadata,
                     # Unique identifier for each sample record
                     Column('gid', Integer, primary_key=True))
        else:
            # For PostgreSQL/PostGIS
                        return Table('pyarchinit_campionature', metadata,
                     # Unique identifier for each sample record
                     Column('gid', Integer, primary_key=True))