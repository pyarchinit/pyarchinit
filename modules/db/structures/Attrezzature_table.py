'''
Created on 20 feb 2026

@author: Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, Float, Text, MetaData, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class Attrezzature_table:

    metadata = MetaData()

    # define tables
    attrezzature_table = Table('attrezzature_table', metadata,
                               Column('id_attrezzatura', Integer, primary_key=True),
                               Column('sito', Text),
                               Column('codice_inventario', Text),
                               Column('nome', Text),
                               Column('categoria', Text),
                               Column('marca', Text),
                               Column('modello', Text),
                               Column('numero_serie', Text),
                               Column('proprieta', Text),
                               Column('data_acquisto', Text),
                               Column('costo_acquisto', Float),
                               Column('costo_noleggio_giorno', Float),
                               Column('stato', Text),
                               Column('assegnato_a', Integer),
                               Column('data_ultima_manutenzione', Text),
                               Column('data_prossima_manutenzione', Text),
                               Column('note', Text),
                               Column('entity_uuid', Text),

                               # explicit/composite unique constraint.  'name' is optional.
                               UniqueConstraint('sito', 'codice_inventario', name='ID_attrezzatura_unico')
                               )

    # DO NOT create tables at module import time!
