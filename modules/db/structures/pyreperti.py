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
    
    
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    
    #engine.connect()
    metadata = MetaData(engine)

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

    try:
        metadata.create_all(engine)
    except:
        pass  # Table already exists or geometry type not supported
    
