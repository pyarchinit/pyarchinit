'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, String, Text, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class Media_table:

    metadata = MetaData()

    # define tables
    media_table = Table('media_table', metadata,
                        Column('id_media', Integer, primary_key=True),
                        Column('mediatype', Text),
                        Column('filename', Text),
                        Column('filetype', String(10)),
                        Column('filepath', Text),
                        Column('descrizione', Text),
                        Column('tags', Text),
                        Column('entity_uuid', Text),

                        # explicit/composite unique constraint.  'name' is optional.
                        UniqueConstraint('filepath', name='ID_media_unico')
                        )

    # DO NOT create tables at module import time!


    # metadata.create_all(engine)  # This line was causing connection errors
