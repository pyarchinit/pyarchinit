"""
Created on 17 11 2020

@author: Enzo Cocca
"""

from geoalchemy2 import Geometry
from sqlalchemy import Table, Column, Integer, Text,  UniqueConstraint

# Vector layer representing the samples collected during the archaeological surveyTable representing the samples collected during the archaeological survey
class pycampioni:
    @classmethod
    def define_table(cls, metadata):
        return Table('pyarchinit_campionature', metadata,
                     # Unique identifier for each sample record
                     Column('gid', Integer, primary_key=True),  # 0

                     # Identifier for the sample
                     Column('id_campion', Integer),  # 1

                     # Name of the archaeological site
                     Column('sito', Text),  # 2

                     # Type of sample collected
                     Column('tipo_camp', Text),  # 3

                     # Date of sample collection
                     Column('dataz', Text),  # 4

                     # Chronological context of the sample
                     Column('cronologia', Integer),  # 5

                     # Link to an image associated with the sample
                     Column('link_immag', Text),  # 6

                     # Abbreviation for the sample
                     Column('sigla_camp', Text),  # 7

                     # Geometry of the sample location (point)
                     Column('the_geom', Geometry(geometry_type='POINT')),  # 8

                     # Unique constraint ensuring the gid is unique
                     UniqueConstraint('gid')  # 9
                     )
