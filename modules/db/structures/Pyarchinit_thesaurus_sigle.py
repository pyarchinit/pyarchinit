'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, String, Text, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class Pyarchinit_thesaurus_sigle:

    metadata = MetaData()

    # define tables
    pyarchinit_thesaurus_sigle = Table('pyarchinit_thesaurus_sigle', metadata,
                                       Column('id_thesaurus_sigle', Integer, primary_key=True),
                                       Column('nome_tabella', Text),
                                       Column('sigla', String(100)),
                                       Column('sigla_estesa', Text),
                                       Column('descrizione', Text),
                                       Column('tipologia_sigla', String(100)),
                                       Column('lingua', String(10), default='it'),
                                       Column('order_layer', Integer, default=0),
                                       Column('id_parent', Integer),
                                       Column('parent_sigla', String(100)),
                                       Column('hierarchy_level', Integer, default=0),
                                       Column('n_tipologia', Integer),
                                       Column('n_sigla', Integer),

                                       # explicit/composite unique constraint.  'name' is optional.
                                       UniqueConstraint('id_thesaurus_sigle', name='id_thesaurus_sigle_pk'),
                                       UniqueConstraint('lingua', 'nome_tabella', 'tipologia_sigla', 'sigla_estesa',
                                                       name='thesaurus_unique_key'),
                                       UniqueConstraint('lingua', 'nome_tabella', 'tipologia_sigla', 'sigla',
                                                       name='thesaurus_unique_sigla')
                                       )

    # DO NOT create tables at module import time!
    # Column updates are handled by pyarchinit_db_update.py
