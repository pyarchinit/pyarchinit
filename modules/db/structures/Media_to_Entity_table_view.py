'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, Text, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class Media_to_Entity_table_view:
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    metadata = MetaData(engine)

    # define tables
    mediaentity_view = Table('mediaentity_view', metadata,
                                    Column('id_media_thumb', Integer, primary_key=True),
                                    Column('id_media', Integer),
                                    Column('filepath', Text),
                                    Column('path_resize', Text),
                                    Column('entity_type', Text),
                                    Column('id_media_m', Integer),
                                    Column('id_entity', Integer),
                                    
                                  # # explicit/composite unique constraint.  'name' is optional.
                                  # UniqueConstraint('id_entity', 'entity_type', 'id_media',
                                                   # name='ID_mediaToEntity_unico')
                                   )

    metadata.create_all(engine)
