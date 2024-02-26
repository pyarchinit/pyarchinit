'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, String, Text, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class Media_table:
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    metadata = MetaData(engine)

    # define tables
    media_table = Table('media_table', metadata,
                        Column('id_media', Integer, primary_key=True),
                        Column('mediatype', Text),
                        Column('filename', Text),
                        Column('filetype', String(10)),
                        Column('filepath', Text),
                        Column('descrizione', Text),
                        Column('tags', Text),

                        # explicit/composite unique constraint.  'name' is optional.
                        UniqueConstraint('filepath', name='ID_media_unico')
                        )

    metadata.create_all(engine)
