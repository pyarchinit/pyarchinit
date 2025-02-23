'''
Created on 17 11 2020

@author: Enzo Cocca
'''

from sqlalchemy import Table, Column, Integer,  Text, UniqueConstraint
from geoalchemy2 import Geometry


# Vector layer representing sections in archaeological contexts
class pysezioni:
    @classmethod
    def define_table(cls, metadata):
        return Table('pyarchinit_sezioni', metadata,
                     # Unique identifier for each section record
                     Column('gid', Integer, primary_key=True),  # 0

                     # Identifier for the section
                     Column('id_sezione', Text),  # 1

                     # Name of the archaeological site associated with the section
                     Column('sito', Text),  # 2

                     # Area associated with the section
                     Column('area', Integer),  # 3

                     # Description of the section
                     Column('descr', Text),  # 4

                     # Geometry of the section (line string)
                     Column('the_geom', Geometry(geometry_type='LINESTRING')),  # 5

                     # Type of document associated with the section
                     Column('tipo_doc', Text),  # 6

                     # Name of the document associated with the section
                     Column('nome_doc', Text),  # 7

                     # Unique constraint ensuring the gid is unique
                     UniqueConstraint('gid')  # 8
                     )

