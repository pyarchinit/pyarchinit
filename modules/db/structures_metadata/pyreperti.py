'''
Created on 17 11 2020

@author: Enzo Cocca
'''

from sqlalchemy import Table, Column, Integer, Text,  UniqueConstraint
from geoalchemy2 import Geometry


# Vector layer representing artifacts or finds in archaeological contexts
class pyreperti:
    @classmethod
    def define_table(cls, metadata):
        return Table('pyarchinit_reperti', metadata,
                     # Unique identifier for each artifact record
                     Column('gid', Integer, primary_key=True),  # 0

                     # Identifier for the artifact
                     Column('id_rep', Integer),  # 1

                     # Name of the archaeological site where the artifact was found
                     Column('siti', Text),  # 2

                     # Link to additional information or documentation about the artifact
                     Column('link', Text),  # 3

                     # Geometry of the artifact's location (point)
                     Column('the_geom', Geometry(geometry_type='POINT')),  # 4

                     # Unique constraint ensuring the gid is unique
                     UniqueConstraint('gid')  # 5
                     )

