'''
Created on 20 feb 2026

@author: Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, Float, Text, MetaData, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class Presenze_table:

    metadata = MetaData()

    # define tables
    presenze_table = Table('presenze_table', metadata,
                           Column('id_presenza', Integer, primary_key=True),
                           Column('sito', Text),
                           Column('id_personale', Integer),
                           Column('data', Text),
                           Column('ora_ingresso', Text),
                           Column('ora_uscita', Text),
                           Column('ore_ordinarie', Float),
                           Column('ore_straordinario', Float),
                           Column('tipo_giornata', Text),
                           Column('turno', Text),
                           Column('area_lavoro', Text),
                           Column('note', Text),
                           Column('costo_giornata', Float),
                           Column('entity_uuid', Text),

                           # explicit/composite unique constraint.  'name' is optional.
                           UniqueConstraint('sito', 'id_personale', 'data', 'turno', name='ID_presenza_unico')
                           )

    # DO NOT create tables at module import time!
