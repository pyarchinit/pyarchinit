"""
Created on 17 11 2020

@author: Enzo Cocca
"""

from sqlalchemy import Table, Column, Integer,  Text,  MetaData, create_engine, UniqueConstraint
from geoalchemy2 import Geometry
from modules.db.pyarchinit_conn_strings import Connection


# Questo codice definisce una classe chiamata 'pyripartizioni_spaziali'.
# All'interno di questa classe, viene stabilita una connessione a un database PostgreSQL
# e viene creato un motore di database. Viene quindi definita una tabella
# 'pyarchinit_ripartizioni_spaziali' con diverse colonne. Infine,
# tutte le modifiche vengono applicate al database.

class pyripartizioni_spaziali:
    # Connessione a postgres
    internal_connection = Connection()
    # Creazione del motore e dei metadati
    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    metadata = MetaData(engine)
    # Definizione della tabella per verifica fill fields 20/10/2016 OK
    pyripartizioni_spaziali = Table('pyarchinit_ripartizioni_spaziali', metadata,
                     Column('gid', Integer, primary_key=True),  # 0
                     Column('id_rs', Text),
                     Column('sito_rs', Text),
                     Column('tip_rip', Text),
                     Column('descr_rs', Text),
                     Column('the_geom', Geometry(geometry_type='POLYGON')),
                     # Vincolo unico esplicito/composito. 'name' è opzionale.
                     UniqueConstraint('gid')
                     )
    # Applicazione delle modifiche al database

    # Only create the table if it doesn't exist
    try:
        metadata.create_all(engine, checkfirst=True)
        
        # For SQLite, add geometry column using Spatialite if not exists
        if 'sqlite' in conn_str.lower():
            try:
                # Check if geometry column already exists
                from sqlalchemy import inspect
                inspector = inspect(engine)
                columns = [col['name'] for col in inspector.get_columns('pyarchinit_ripartizioni_spaziali')]
                
                if 'the_geom' not in columns:
                    # Add geometry column using raw SQL
                    with engine.connect() as conn:
                        # Ensure Spatialite is loaded
                        try:
                            conn.execute("SELECT InitSpatialMetadata(1)")
                        except:
                            pass  # Already initialized
                        
                        # Add geometry column
                        conn.execute("SELECT AddGeometryColumn('pyarchinit_ripartizioni_spaziali', 'the_geom', -1, 'POLYGON', 'XY')")
            except Exception as e:
                # Geometry column might already exist or Spatialite not available
                pass
    except Exception as e:
        # Table creation failed, but continue
        pass
    
