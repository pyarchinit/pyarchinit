'''
Created on 17 11 2020

@author: Enzo Cocca
'''

from sqlalchemy import Table, Column, Integer, String, Text, Numeric, MetaData, create_engine, UniqueConstraint
from geoalchemy2 import Geometry
from modules.db.pyarchinit_conn_strings import Connection
from modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility

class pyquote_usm:
    @classmethod
    def define_table(cls, metadata):
        return Table('pyarchinit_quote_usm', metadata,
                     Column('gid', Integer, primary_key=True),  # 0
                     Column('sito_q', Text),
                     Column('area_q', Integer),
                     Column('us_q', Integer),
                     Column('unita_misu_q', Text),
                     Column('quota_q', Numeric(2,2)),
                     Column('data', Integer),
                     Column('disegnatore', Text),
                     Column('rilievo_originale', Text),
                     Column('the_geom', Geometry(geometry_type='POINT')),
                     Column('unita_tipo_q', Text),
                     # explicit/composite unique constraint.  'name' is optional.
                     UniqueConstraint('gid')
                     )