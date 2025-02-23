'''
Created on 17 11 2020

@author: Enzo Cocca
'''

from sqlalchemy import Table, Column, Integer, Text, UniqueConstraint
from geoalchemy2 import Geometry


# Class representing structures or hypotheses related to archaeological contexts
class pystrutture:
    @classmethod
    def define_table(cls, metadata):
        return Table('pyarchinit_strutture_ipotesi', metadata,
                     # Unique identifier for each structure record
                     Column('gid', Integer, primary_key=True),  # 0

                     # Name of the archaeological site associated with the structure
                     Column('sito', Text),  # 1

                     # Identifier for the structure
                     Column('id_strutt', Text),  # 2

                     # Initial period associated with the structure
                     Column('per_iniz', Integer),  # 3

                     # Final period associated with the structure
                     Column('per_fin', Integer),  # 4

                     # External dating information
                     Column('dataz_ext', Text),  # 5

                     # Initial phase associated with the structure
                     Column('fase_iniz', Integer),  # 6

                     # Final phase associated with the structure
                     Column('fase_fin', Integer),  # 7

                     # Description of the structure
                     Column('descrizione', Text),  # 8

                     # Geometry of the structure (polygon)
                     Column('the_geom', Geometry(geometry_type='POLYGON')),  # 9

                     # Abbreviation for the structure
                     Column('sigla_strut', Text),  # 10

                     # Number assigned to the structure
                     Column('nr_strut', Integer),  # 11

                     # Unique constraint ensuring the gid is unique
                     UniqueConstraint('gid')  # 12
                     )
