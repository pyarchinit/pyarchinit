'''
Created on 17 11 2020

@author: Enzo Cocca
'''

from sqlalchemy import Table, Column, Integer, String, Text, Numeric, MetaData, create_engine, UniqueConstraint
from geoalchemy2 import Geometry
from modules.db.pyarchinit_conn_strings import Connection
from modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility

class pysito_polygon:

    @classmethod
    def define_table(cls, metadata):
        return Table('pyarchinit_siti_polygonal', metadata,
                     Column('gid', Integer, primary_key=True),  # 0
                     Column('sito_id', Text),
                     Column('the_geom', Geometry(geometry_type='POLYGON')),
                     # explicit/composite unique constraint.  'name' is optional.
                     UniqueConstraint('gid')
                     )