'''
Created on 17 11 2020

@author: Enzo Cocca
'''

from sqlalchemy import Table, Column, Integer, String, Text, Numeric, MetaData, create_engine, UniqueConstraint
from geoalchemy2 import Geometry
from modules.db.pyarchinit_conn_strings import Connection
from modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility

class pystrutture:
    
    
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    
    #engine.connect()
    metadata = MetaData(engine)

    # define tables check per verifica fill fields 20/10/2016 OK
    pystrutture = Table('pyarchinit_strutture_ipotesi', metadata,
                     Column('gid', Integer, primary_key=True),  # 0
                     Column('sito', Text),
                     Column('id_strutt', Text),
                     Column('per_iniz', Integer),
                     Column('per_fin', Integer),
                     Column('dataz_ext', Text),
                     Column('fase_iniz', Integer),
                     Column('fase_fin', Integer),
                     Column('descrizione', Text),
                     Column('the_geom', Text),
                     Column('sigla_strut', Text),
                     Column('nr_strut', Integer),
                     # explicit/composite unique constraint.  'name' is optional.
                     UniqueConstraint('gid')
                     )

    metadata.create_all(engine)
    
