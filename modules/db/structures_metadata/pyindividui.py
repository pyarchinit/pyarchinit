"""
Created on 17 11 2020

@author: Enzo Cocca
"""

from geoalchemy2 import Geometry
from sqlalchemy import Table, Column, Integer, Text, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class pyindividui:
    @classmethod
    def define_table(cls, metadata):
        return Table('pyarchinit_individui', metadata,
                        Column('gid', Integer, primary_key=True),  # 0
                        Column('sito', Text),
                        Column('sigla_struttura', Text),
                        Column('note', Text),
                        Column('id_individuo', Integer),
                        Column('the_geom', Geometry(geometry_type='POINT')),
                        # explicit/composite unique constraint.  'name' is optional.
                        UniqueConstraint('gid')
                        )