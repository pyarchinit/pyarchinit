'''
Created on 19 feb 2018

@author: Serena Sensini
'''
from modules.db.pyarchinit_conn_strings import Connection
from sqlalchemy import Table, Column, Integer, Date, String, Text, Float, Numeric, MetaData, ForeignKey, engine, create_engine, UniqueConstraint


class Media_thumb_table:
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
    metadata = MetaData(engine)

    # define tables
    media_thumb_table = Table('media_thumb_table', metadata,
    Column('id_media_thumb', Integer, primary_key=True),
    Column('id_media', Integer),
    Column('mediatype', Text),
    Column('media_filename', Text),
    Column('media_thumb_filename', Text),
    Column('filetype', String(10)),
    Column('filepath', Text),

    # explicit/composite unique constraint.  'name' is optional.
    UniqueConstraint('media_thumb_filename', name='ID_media_thumb_unico')
    )

    metadata.create_all(engine)

