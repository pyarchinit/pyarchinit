'''
Created on 17 11 2020

@author: Enzo Cocca
'''

from sqlalchemy import Table, Column, Integer, Text,  UniqueConstraint
from geoalchemy2 import Geometry


# Vector layer representing polygonal representations of archaeological sites
class pysito_polygon:
    @classmethod
    def define_table(cls, metadata):
        return Table('pyarchinit_siti_polygonal', metadata,
                     # Unique identifier for each polygonal site record
                     Column('gid', Integer, primary_key=True),  # 0

                     # Identifier for the archaeological site
                     Column('sito_id', Text),  # 1

                     # Geometry of the site location (polygon)
                     Column('the_geom', Geometry(geometry_type='POLYGON')),  # 2

                     # Unique constraint ensuring the gid is unique
                     UniqueConstraint('gid')  # 3
                     )
