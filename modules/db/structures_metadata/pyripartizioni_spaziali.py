"""
Created on 17 11 2020

@author: Enzo Cocca
"""

from sqlalchemy import Table, Column, Integer,  Text,   UniqueConstraint
from geoalchemy2 import Geometry

# Vector layerrepresenting spatial partitions in archaeological contexts
class pyripartizioni_spaziali:
    @classmethod
    def define_table(cls, metadata):
        return Table('pyarchinit_ripartizioni_spaziali', metadata,
                     # Unique identifier for each spatial partition record
                     Column('gid', Integer, primary_key=True),  # 0

                     # Identifier for the spatial partition
                     Column('id_rs', Text),  # 1

                     # Name of the archaeological site associated with the partition
                     Column('sito_rs', Text),  # 2

                     # Type of spatial partition
                     Column('tip_rip', Text),  # 3

                     # Description of the spatial partition
                     Column('descr_rs', Text),  # 4

                     # Geometry of the spatial partition (polygon)
                     Column('the_geom', Geometry(geometry_type='POLYGON')),  # 5

                     # Unique constraint ensuring the gid is unique
                     UniqueConstraint('gid')  # 6
                     )
