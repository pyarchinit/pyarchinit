'''
Created on 20 feb 2026

@author: Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, Float, Text, MetaData

from modules.db.pyarchinit_conn_strings import Connection


class Budget_table:

    metadata = MetaData()

    # define tables
    budget_table = Table('budget_table', metadata,
                         Column('id_budget', Integer, primary_key=True),
                         Column('sito', Text),
                         Column('anno', Integer),
                         Column('categoria', Text),
                         Column('descrizione', Text),
                         Column('importo_previsto', Float),
                         Column('importo_effettivo', Float),
                         Column('data_registrazione', Text),
                         Column('data_spesa', Text),
                         Column('fornitore', Text),
                         Column('numero_fattura', Text),
                         Column('note', Text),
                         Column('entity_uuid', Text),
                         )

    # DO NOT create tables at module import time!
