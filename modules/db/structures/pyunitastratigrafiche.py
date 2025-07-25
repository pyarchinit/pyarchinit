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
                     Column('the_geom', Geometry(geometry_type='MULTIPOLYGON')),
                     Column('unita_tipo_s', Text),
                     # explicit/composite unique constraint.  'name' is optional.
                     UniqueConstraint('gid', name='ID_us_unico_s')
                     )


    # Only create the table if it doesn't exist
    try:
        metadata.create_all(engine, checkfirst=True)
        
        # For SQLite, add geometry column using Spatialite if not exists
        if 'sqlite' in conn_str.lower():
            try:
                # Check if geometry column already exists
                from sqlalchemy import inspect
                inspector = inspect(engine)
                columns = [col['name'] for col in inspector.get_columns('pyunitastratigrafiche')]
                
                if 'the_geom' not in columns:
                    # Add geometry column using raw SQL
                    with engine.connect() as conn:
                        # Ensure Spatialite is loaded
                        try:
                            conn.execute("SELECT InitSpatialMetadata(1)")
                        except:
                            pass  # Already initialized
                        
                        # Add geometry column
                        conn.execute("SELECT AddGeometryColumn('pyunitastratigrafiche', 'the_geom', -1, 'MULTIPOLYGON', 'XY')")
            except Exception as e:
                # Geometry column might already exist or Spatialite not available
                pass
    except Exception as e:
        # Table creation failed, but continue
        pass
    # def load_spatialite(self,dbapi_conn, connection_record):
        # dbapi_conn.enable_load_extension(True)
        
        # if Pyarchinit_OS_Utility.isWindows()== True:
            # dbapi_conn.load_extension('mod_spatialite.dll')
        
        # elif Pyarchinit_OS_Utility.isMac()== True:
            # dbapi_conn.load_extension('mod_spatialite')
        # else:
            # dbapi_conn.load_extension('mod_spatialite.so')
            
            
