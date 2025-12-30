'''
Created on 17 11 2020

@author: Enzo Cocca
'''

'''
Created on 17 11 2020

@author: Enzo Cocca
'''

from sqlalchemy import Table, Column, Integer, String, Text, Numeric, MetaData, create_engine, UniqueConstraint
from geoalchemy2 import Geometry
from modules.db.pyarchinit_conn_strings import Connection
from modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility

class pyreperti:
    
    

    
    #engine.connect()
    metadata = MetaData()

    # define tables check per verifica fill fields 20/10/2016 OK
    pyreperti = Table('pyarchinit_reperti', metadata,
                     Column('gid', Integer, primary_key=True),  # 0
                     Column('id_rep', Integer),
                     Column('siti', Text),
                     Column('link', Text),
                     Column('the_geom', Geometry(geometry_type='POINT')),
                     # explicit/composite unique constraint.  'name' is optional.
                     UniqueConstraint('gid')
                     )

    # DO NOT create tables at module import time!


    # metadata.create_all(engine)  # This line was causing connection errors
    
