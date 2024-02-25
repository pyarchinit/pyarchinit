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
                       Column('sito', Text),
                       Column('nazione', String(100)),
                       Column('regione', String(100)),
                       Column('comune', String(100)),
                       Column('descrizione', Text),
                       Column('provincia', Text),
                       Column('definizione_sito', Text),
                       Column('sito_path', Text),
                       Column('find_check', Integer),

                       # explicit/composite unique constraint.  'name' is optional.
                       UniqueConstraint('sito', name='ID_sito_unico')
                       )

    metadata.create_all(engine)
