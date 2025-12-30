'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, String, Text, Numeric, MetaData, create_engine, UniqueConstraint
from geoalchemy2 import Geometry
from modules.db.pyarchinit_conn_strings import Connection
from modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility

class pysito_point:
    
    

    
    #engine.connect()
    metadata = MetaData()

    # define tables check per verifica fill fields 20/10/2016 OK
    pysito_point = Table('pyarchinit_siti', metadata,
                     Column('gid', Integer, primary_key=True),  # 0
                     Column('sito_nome', Text),
                     Column('the_geom', Geometry(geometry_type='POINT')),
                     # explicit/composite unique constraint.  'name' is optional.
                     UniqueConstraint('gid')
                     )



    # DO NOT create tables at module import time!
    # metadata.create_all(engine)  # This line was causing connection errors
    
