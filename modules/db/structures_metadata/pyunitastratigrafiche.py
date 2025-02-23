'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, Text,  UniqueConstraint
from geoalchemy2 import Geometry


# Vector layer representing stratigraphic units in archaeological contexts
class pyunitastratigrafiche:
    @classmethod
    def define_table(cls, metadata):
        return Table('pyunitastratigrafiche', metadata,
                     # Unique identifier for each stratigraphic unit record
                     Column('gid', Integer, primary_key=True),  # 0

                     # Area associated with the stratigraphic unit
                     Column('area_s', Integer),  # 1

                     # Excavation site associated with the stratigraphic unit
                     Column('scavo_s', Text),  # 2

                     # Stratigraphic unit (US) identifier
                     Column('us_s', Integer),  # 3

                     # Stratigraphic index for the unit
                     Column('stratigraph_index_us', Integer),  # 4

                     # Type of stratigraphic unit
                     Column('tipo_us_s', Text),  # 5

                     # Original survey related to the stratigraphic unit
                     Column('rilievo_originale', Text),  # 6

                     # Name of the person who created the record
                     Column('disegnatore', Text),  # 7

                     # Date of the record
                     Column('data', Text),  # 8

                     # Type of document associated with the stratigraphic unit
                     Column('tipo_doc', Text),  # 9

                     # Coordinates related to the stratigraphic unit
                     Column('coord', Text),  # 10

                     # Geometry of the stratigraphic unit (multi-polygon)
                     Column('the_geom', Geometry(geometry_type='MULTIPOLYGON')),  # 11

                     # Type of unit associated with the stratigraphic unit
                     Column('unita_tipo_s', Text),  # 12

                     # Unique constraint ensuring the gid is unique
                     UniqueConstraint('gid', name='ID_us_unico_s')  # 13
                     )



            
