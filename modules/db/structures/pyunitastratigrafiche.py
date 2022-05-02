'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, String, Text, Numeric, MetaData, create_engine, UniqueConstraint
from geoalchemy2 import Geometry
from modules.db.pyarchinit_conn_strings import Connection
from modules.utility.pyarchinit_OS_utility import Pyarchinit_OS_Utility

class pyunitastratigrafiche:
    
    
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    
    #engine.connect()
    metadata = MetaData(engine)

    # define tables check per verifica fill fields 20/10/2016 OK
    pyunitastratigrafiche = Table('pyunitastratigrafiche', metadata,
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
                     Column('the_geom', Text),
                     Column('unita_tipo_s', Text),
                     # explicit/composite unique constraint.  'name' is optional.
                     UniqueConstraint('gid', name='ID_us_unico_s')
                     )

    metadata.create_all(engine)
    # def load_spatialite(self,dbapi_conn, connection_record):
        # dbapi_conn.enable_load_extension(True)
        
        # if Pyarchinit_OS_Utility.isWindows()== True:
            # dbapi_conn.load_extension('mod_spatialite.dll')
        
        # elif Pyarchinit_OS_Utility.isMac()== True:
            # dbapi_conn.load_extension('mod_spatialite')
        # else:
            # dbapi_conn.load_extension('mod_spatialite.so')
            
            
