'''
Created on 15 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, String, Text, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class Site_table:
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=True, convert_unicode=True)
    metadata = MetaData(engine)

    # define tables
    site_table = Table('site_table', metadata,
                       Column('id_sito', Integer, primary_key=True),
                       Column('site', Text),
                       Column('nation', String(100)),
                       Column('region', String(100)),
                       Column('municipality', String(100)),
                       Column('description', Text),
                       Column('province', Text),
                       Column('site_type', Text),                       
                       Column('find_check', Integer),
                       Column('site_path', Text),
                       # explicit/composite unique constraint.  'name' is optional.
                       UniqueConstraint('site', name='ID_sito_unico')
                       )

    metadata.create_all(engine)
