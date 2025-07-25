"""
Created on 17 11 2020

@author: Enzo Cocca
"""

from geoalchemy2 import Geometry
from sqlalchemy import Table, Column, Integer, Text, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class pycampioni:
    # connection string postgres
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)

    # engine.connect()
    metadata = MetaData(engine)

    # define tables check per verifica fill fields 20/10/2016 OK
    pycampioni = Table('pyarchinit_campionature', metadata,
                       Column('gid', Integer, primary_key=True),  # 0
                       Column('id_campion', Integer),
                       Column('sito', Text),
                       Column('tipo_camp', Text),
                       Column('dataz', Text),
                       Column('cronologia', Integer),
                       Column('link_immag', Text),
                       Column('sigla_camp', Text),
                       Column('the_geom', Geometry(geometry_type='POINT')),
                       # explicit/composite unique constraint.  'name' is optional.
                       UniqueConstraint('gid')
                       )

    try:
        metadata.create_all(engine)
    except:
        pass  # Table already exists or geometry type not supported
