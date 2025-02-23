"""
Created on 17 11 2020

@author: Enzo Cocca
"""

from geoalchemy2 import Geometry
from sqlalchemy import Table, Column, Integer, Text,  UniqueConstraint

# Vector layer containing the documentation records
class pydocumentazione:
    @classmethod
    def define_table(cls, metadata):
        return Table('pyarchinit_documentazione', metadata,
                     # Unique identifier for each documentation record
                     Column('gid', Integer, primary_key=True),  # 0

                     # Name of the archaeological site
                     Column('sito', Text),  # 1

                     # Name of the document
                     Column('nome_doc', Text),  # 2

                     # Type of document (e.g., report, article)
                     Column('tipo_doc', Text),  # 3

                     # Path to the QGIS project file associated with the document
                     Column('path_qgis_pj', Text),  # 4

                     # Geometry of the document location (line string)
                     Column('the_geom', Geometry(geometry_type='LINESTRING')),  # 5

                     # Unique constraint ensuring the gid is unique
                     UniqueConstraint('gid')  # 6
                     )
