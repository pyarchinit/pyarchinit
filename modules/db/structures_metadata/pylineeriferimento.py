"""
Created on 17 11 2020

@author: Enzo Cocca
"""

from geoalchemy2 import Geometry
from sqlalchemy import Table, Column, Integer, Text,  UniqueConstraint

# Vector layer Definition of the reference line table
class pylineeriferimento:
    @classmethod
    def define_table(cls, metadata):
        return Table('pyarchinit_linee_rif', metadata,
                     # Unique identifier for each reference line record
                     Column('gid', Integer, primary_key=True),  # 0

                     # Name of the archaeological site
                     Column('sito', Text),  # 1

                     # Definition of the reference line
                     Column('definizion', Text),  # 2

                     # Description of the reference line
                     Column('descrizion', Text),  # 3

                     # Geometry of the reference line (line string)
                     Column('the_geom', Geometry(geometry_type='LINESTRING')),  # 4

                     # Unique constraint ensuring the gid is unique
                     UniqueConstraint('gid')  # 5
                     )
