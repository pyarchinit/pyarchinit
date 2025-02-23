"""
Created on 17 11 2020

@author: Enzo Cocca
"""

from geoalchemy2 import Geometry
from sqlalchemy import Table, Column, Integer, Text,  UniqueConstraint


# Vector layer representing negative archaeological units and their associated documentation
class pyus_negative:
    @classmethod
    def define_table(cls, metadata):
        return Table('pyarchinit_us_negative_doc', metadata,
                     # Unique identifier for each negative unit record
                     Column('gid', Integer, primary_key=True),  # 0

                     # Name of the archaeological site associated with the negative unit
                     Column('sito_n', Text),  # 1

                     # Area associated with the negative unit
                     Column('area_n', Integer),  # 2

                     # Stratigraphic unit (US) identifier for the negative unit
                     Column('us_n', Integer),  # 3

                     # Type of document associated with the negative unit
                     Column('tipo_doc_n', Text),  # 4

                     # Name of the document associated with the negative unit
                     Column('nome_doc_n', Text),  # 5

                     # Geometry of the negative unit location (line string)
                     Column('the_geom', Geometry(geometry_type='LINESTRING')),  # 6

                     # Unique constraint ensuring the gid is unique
                     UniqueConstraint('gid')  # 7
                     )
