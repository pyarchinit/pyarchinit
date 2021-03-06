'''
Created on 19 feb 2018

@author: Serena Sensini
'''

from sqlalchemy import Table, Column, Integer, String, Text, Numeric, MetaData, create_engine, UniqueConstraint
from geoalchemy2 import Geometry
from modules.db.pyarchinit_conn_strings import Connection
from modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility

class pysito_point:
    
    
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    
    #engine.connect()
    metadata = MetaData(engine)

    # define tables check per verifica fill fields 20/10/2016 OK
    pysito_point = Table('pyarchinit_siti', metadata,
                     Column('id', Integer, primary_key=True),  # 0
                     Column('sito_nome', Text),
                     Column('the_geom', Geometry('POINT',-1)),
                     # explicit/composite unique constraint.  'name' is optional.
                     UniqueConstraint('id')
                     )

    metadata.create_all(engine)
    