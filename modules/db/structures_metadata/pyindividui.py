"""
Created on 17 11 2020

@author: Enzo Cocca
"""

from geoalchemy2 import Geometry
from sqlalchemy import Table, Column, Integer, Text, UniqueConstraint

# Vector layer for the individui table
class pyindividui:
    @classmethod
    def define_table(cls, metadata):
        return Table('pyarchinit_individui', metadata,
                     # Unique identifier for each individual record
                     Column('gid', Integer, primary_key=True),  # 0

                     # Name of the archaeological site
                     Column('sito', Text),  # 1

                     # Abbreviation for the associated structure
                     Column('sigla_struttura', Text),  # 2

                     # General notes about the individual
                     Column('note', Text),  # 3

                     # Identifier for the individual
                     Column('id_individuo', Integer),  # 4

                     # Geometry of the individual's location (point)
                     Column('the_geom', Geometry(geometry_type='POINT')),  # 5

                     # Unique constraint ensuring the gid is unique
                     UniqueConstraint('gid')  # 6
                     )
