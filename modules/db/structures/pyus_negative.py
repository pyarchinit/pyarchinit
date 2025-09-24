"""
Created on 17 11 2020

@author: Enzo Cocca
"""

from geoalchemy2 import Geometry
from sqlalchemy import Table, Column, Integer, Text, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class pyus_negative:
    # connection string postgres
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)

    # engine.connect()
    metadata = MetaData(engine)

    # define tables check per verifica fill fields 20/10/2016 OK
    pyus_negative = Table('pyarchinit_us_negative_doc', metadata,
                          Column('gid', Integer, primary_key=True),
                          Column('sito_n', Text),
                          Column('area_n', Integer),
                          Column('us_n', Integer),
                          Column('tipo_doc_n', Text),
                          Column('nome_doc_n', Text),
                          Column('the_geom', Geometry(geometry_type='LINESTRING')),
                          # explicit/composite unique constraint.  'name' is optional.
                          UniqueConstraint('gid')
                          )



    # DO NOT create tables at module import time!
    # metadata.create_all(engine)  # This line was causing connection errors
