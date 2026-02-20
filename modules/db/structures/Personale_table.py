'''
Created on 20 feb 2026

@author: Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, Float, Text, MetaData, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class Personale_table:

    metadata = MetaData()

    # define tables
    personale_table = Table('personale_table', metadata,
                            Column('id_personale', Integer, primary_key=True),
                            Column('sito', Text),
                            Column('nome', Text),
                            Column('cognome', Text),
                            Column('ruolo', Text),
                            Column('qualifica', Text),
                            Column('codice_fiscale', Text),
                            Column('email', Text),
                            Column('telefono', Text),
                            Column('data_nascita', Text),
                            Column('indirizzo', Text),
                            Column('tipo_contratto', Text),
                            Column('data_inizio_contratto', Text),
                            Column('data_fine_contratto', Text),
                            Column('tariffa_oraria', Float),
                            Column('tariffa_giornaliera', Float),
                            Column('iban', Text),
                            Column('note', Text),
                            Column('attivo', Integer),
                            Column('entity_uuid', Text),

                            # explicit/composite unique constraint.  'name' is optional.
                            UniqueConstraint('sito', 'codice_fiscale', name='ID_personale_unico')
                            )

    # DO NOT create tables at module import time!
