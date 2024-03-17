"""
Created on 17 11 2020

@author: Enzo Cocca
"""

from geoalchemy2 import Geometry
from sqlalchemy import Table, Column, Integer, Text, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class pydocumentazione:
    @classmethod
    def define_table(cls, metadata):
        return Table('pyarchinit_documentazione', metadata,
                             Column('gid', Integer, primary_key=True),  # 0
                             Column('sito', Text),
                             Column('nome_doc', Text),
                             Column('tipo_doc', Text),
                             Column('path_qgis_pj', Text),
                             Column('the_geom', Geometry(geometry_type='LINESTRING')),
                             # explicit/composite unique constraint.  'name' is optional.
                             UniqueConstraint('gid')
                             )