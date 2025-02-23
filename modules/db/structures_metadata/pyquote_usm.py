'''
Created on 17 11 2020

@author: Enzo Cocca
'''

from sqlalchemy import Table, Column, Integer,  Text, Numeric,  UniqueConstraint
from geoalchemy2 import Geometry


# Vector layer representing quotes related to archaeological contexts with specific measurements
class pyquote_usm:
    @classmethod
    def define_table(cls, metadata):
        return Table('pyarchinit_quote_usm', metadata,
                     # Unique identifier for each quote record
                     Column('gid', Integer, primary_key=True),  # 0

                     # Name of the archaeological site for the quote
                     Column('sito_q', Text),  # 1

                     # Area associated with the quote
                     Column('area_q', Integer),  # 2

                     # Stratigraphic unit (US) associated with the quote
                     Column('us_q', Integer),  # 3

                     # Measurement unit for the quote
                     Column('unita_misu_q', Text),  # 4

                     # Elevation associated with the quote
                     Column('quota_q', Numeric(2, 2)),  # 5

                     # Date of the quote record
                     Column('data', Integer),  # 6

                     # Name of the person who created the quote
                     Column('disegnatore', Text),  # 7

                     # Original survey related to the quote
                     Column('rilievo_originale', Text),  # 8

                     # Geometry of the quote location (point)
                     Column('the_geom', Geometry(geometry_type='POINT')),  # 9

                     # Type of unit associated with the quote
                     Column('unita_tipo_q', Text),  # 10

                     # Unique constraint ensuring the gid is unique
                     UniqueConstraint('gid')  # 11
                     )
