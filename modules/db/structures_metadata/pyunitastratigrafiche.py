'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, String, Text, Numeric, MetaData, create_engine, UniqueConstraint
from geoalchemy2 import Geometry
from modules.db.pyarchinit_conn_strings import Connection
from modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility

class pyunitastratigrafiche:
    @classmethod
    def define_table(cls, metadata):
        return Table('pyunitastratigrafiche', metadata,
                     Column('gid', Integer, primary_key=True),  # 0
                     Column('area_s', Integer),  # 1
                     Column('scavo_s', Text),  # 2
                     Column('us_s', Integer),  # 3
                     Column('stratigraph_index_us', Integer),  # 5
                     Column('tipo_us_s', Text),  # 6
                     Column('rilievo_originale', Text),  # 7
                     Column('disegnatore', Text),  # 8
                     Column('data', Text),  # 8
                     Column('tipo_doc', Text),  # 9
                     Column('nome_doc', Text),  # 10
                     Column('coord', Text),
                     Column('the_geom', Geometry(geometry_type='MULTIPOLYGON')),
                     Column('unita_tipo_s', Text),
                     # explicit/composite unique constraint.  'name' is optional.
                     UniqueConstraint('gid', name='ID_us_unico_s')
                     )


            
