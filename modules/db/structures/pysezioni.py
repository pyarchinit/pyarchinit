'''
Created on 17 11 2020

@author: Enzo Cocca
'''

from sqlalchemy import Table, Column, Integer, String, Text, Numeric, MetaData, create_engine, UniqueConstraint
from geoalchemy2 import Geometry
from modules.db.pyarchinit_conn_strings import Connection
from modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility

class pysezioni:
    
    
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    
    #engine.connect()
    metadata = MetaData(engine)

    # define tables
    pysezioni = Table('pyarchinit_sezioni', metadata,
                     Column('gid', Integer, primary_key=True),  # 0
                     Column('id_sezione', Text),
                     Column('sito', Text),
                     Column('area', Text),
                     Column('descr', Text),
                     Column('the_geom', Geometry(geometry_type='LINESTRING')),
                     # explicit/composite unique constraint.  'name' is optional.
                     UniqueConstraint('gid')
                     )

    # DO NOT create tables at module import time!
    # metadata.create_all(engine)  # This line was causing connection errors
