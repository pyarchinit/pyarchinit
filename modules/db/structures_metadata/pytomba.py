'''
Created on 17 11 2020

@author: Enzo Cocca
'''

from sqlalchemy import Table, Column, Integer,  Text, UniqueConstraint
from geoalchemy2 import Geometry


# Vector layer representing taxonomy records related to archaeological contexts
class pytomba:
    @classmethod
    def define_table(cls, metadata):
        return Table('pyarchinit_tafonomia', metadata,
                     # Unique identifier for each taxonomy record
                     Column('gid', Integer, primary_key=True),  # 0

                     # Name of the archaeological site associated with the taxonomy
                     Column('sito', Text),  # 1

                     # Number assigned to the record
                     Column('nr_scheda', Integer),  # 2

                     # Geometry of the taxonomy location (point)
                     Column('the_geom', Geometry(geometry_type='POINT')),  # 3

                     # Unique constraint ensuring the gid is unique
                     UniqueConstraint('gid')  # 4
                     )

