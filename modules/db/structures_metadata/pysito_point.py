'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer,  Text,  UniqueConstraint
from geoalchemy2 import Geometry


# Vector layer representing points of archaeological sites
class pysito_point:
    @classmethod
    def define_table(cls, metadata):
        return Table('pyarchinit_siti', metadata,
                     # Unique identifier for each site record
                     Column('gid', Integer, primary_key=True),  # 0

                     # Name of the archaeological site
                     Column('sito_nome', Text),  # 1

                     # Geometry of the site location (point)
                     Column('the_geom', Geometry(geometry_type='POINT')),  # 2

                     # Unique constraint ensuring the gid is unique
                     UniqueConstraint('gid')  # 3
                     )

