'''
Created on 15 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, Text, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class Documentazione_table:

    metadata = MetaData()

    # define tables
    documentazione_table = Table('documentazione_table', metadata,
                                 Column('id_documentazione', Integer, primary_key=True),
                                 Column('sito', Text),
                                 Column('nome_doc', Text),
                                 Column('data', Text),
                                 Column('tipo_documentazione', Text),
                                 Column('sorgente', Text),
                                 Column('scala', Text),
                                 Column('disegnatore', Text),
                                 Column('note', Text),
                                 Column('entity_uuid', Text),

                                 # explicit/composite unique constraint.  'name' is optional.
                                 UniqueConstraint('sito', 'tipo_documentazione', 'nome_doc', name='ID_invdoc_unico')
                                 )

