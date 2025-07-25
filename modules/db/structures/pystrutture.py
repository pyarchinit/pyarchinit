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
                     Column('the_geom', Geometry(geometry_type='POLYGON')),
                     Column('sigla_strut', Text),
                     Column('nr_strut', Integer),
                     # explicit/composite unique constraint.  'name' is optional.
                     UniqueConstraint('gid')
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
                columns = [col['name'] for col in inspector.get_columns('pyarchinit_strutture_ipotesi')]
                
                if 'the_geom' not in columns:
                    # Add geometry column using raw SQL
                    with engine.connect() as conn:
                        # Ensure Spatialite is loaded
                        try:
                            conn.execute("SELECT InitSpatialMetadata(1)")
                        except:
                            pass  # Already initialized
                        
                        # Add geometry column
                        conn.execute("SELECT AddGeometryColumn('pyarchinit_strutture_ipotesi', 'the_geom', -1, 'POLYGON', 'XY')")
            except Exception as e:
                # Geometry column might already exist or Spatialite not available
                pass
    except Exception as e:
        # Table creation failed, but continue
        pass
    
