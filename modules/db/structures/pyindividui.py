"""
Created on 17 11 2020

@author: Enzo Cocca
"""

from geoalchemy2 import Geometry
from sqlalchemy import Table, Column, Integer, Text, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class pyindividui:
    # connection string postgres
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)

    # engine.connect()
    metadata = MetaData(engine)

    # define tables check per verifica fill fields 20/10/2016 OK
    pyindividui = Table('pyarchinit_individui', metadata,
                        Column('gid', Integer, primary_key=True),  # 0
                        Column('sito', Text),
                        Column('sigla_struttura', Text),
                        Column('note', Text),
                        Column('id_individuo', Integer),
                        Column('the_geom', Geometry(geometry_type='POINT')),
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
                columns = [col['name'] for col in inspector.get_columns('pyarchinit_individui')]
                
                if 'the_geom' not in columns:
                    # Add geometry column using raw SQL
                    with engine.connect() as conn:
                        # Ensure Spatialite is loaded
                        try:
                            conn.execute("SELECT InitSpatialMetadata(1)")
                        except:
                            pass  # Already initialized
                        
                        # Add geometry column
                        conn.execute("SELECT AddGeometryColumn('pyarchinit_individui', 'the_geom', -1, 'POINT', 'XY')")
            except Exception as e:
                # Geometry column might already exist or Spatialite not available
                pass
    except Exception as e:
        # Table creation failed, but continue
        pass
