'''
Created on 15 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, String, Text, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class Campioni_table:

    metadata = MetaData()

    # define tables
    campioni_table = Table('campioni_table', metadata,
                           Column('id_campione', Integer, primary_key=True),
                           Column('sito', Text),
                           Column('nr_campione', Integer),
                           Column('tipo_campione', Text),
                           Column('descrizione', Text),
                           Column('area', String(20)),
                           Column('us', Integer),
                           Column('numero_inventario_materiale', Integer),
                           Column('nr_cassa', Text),
                           Column('luogo_conservazione', Text),
                           Column('entity_uuid', Text),

                           # explicit/composite unique constraint.  'name' is optional.
                           UniqueConstraint('sito', 'nr_campione', name='ID_invcamp_unico')
                           )

    # DO NOT create tables at module import time!


    # metadata.create_all(engine)  # This line was causing connection errors
