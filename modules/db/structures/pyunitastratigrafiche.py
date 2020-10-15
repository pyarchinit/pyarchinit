'''
Created on 19 feb 2018

@author: Serena Sensini
'''
from sqlalchemy import Table, Column, Integer, String, Text, Numeric, MetaData, create_engine, UniqueConstraint
# from geoalchemy2 import Geometry
from modules.db.pyarchinit_conn_strings import Connection


class pyunitastratigrafiche:
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
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
                     Column('coord', Text),  # 7
                     Column('the_geom', Text),
                     # explicit/composite unique constraint.  'name' is optional.
                     UniqueConstraint('scavo_s', 'area_s', 'us_s', name='ID_us_unico_s')
                     )

    metadata.create_all(engine)
