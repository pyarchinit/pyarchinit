'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, String, Text, Float, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class Struttura_table:

    metadata = MetaData()

    # define tables
    struttura_table = Table('struttura_table', metadata,
                            Column('id_struttura', Integer, primary_key=True),
                            Column('sito', Text),
                            Column('sigla_struttura', Text),
                            Column('numero_struttura', Integer),
                            Column('categoria_struttura', Text),
                            Column('tipologia_struttura', Text),
                            Column('definizione_struttura', Text),
                            Column('descrizione', Text),
                            Column('interpretazione', Text),
                            Column('periodo_iniziale', Integer),
                            Column('fase_iniziale', Integer),
                            Column('periodo_finale', Integer),
                            Column('fase_finale', Integer),
                            Column('datazione_estesa', String(300)),
                            Column('materiali_impiegati', Text),
                            Column('elementi_strutturali', Text),
                            Column('rapporti_struttura', Text),
                            Column('misure_struttura', Text),
                            # Nuovi campi aggiunti per scheda struttura AR
                            Column('data_compilazione', Text),
                            Column('nome_compilatore', Text),
                            Column('stato_conservazione', Text),  # JSON: [[stato, grado, fattori_agenti], ...]
                            Column('quota', Float),
                            Column('relazione_topografica', Text),
                            Column('prospetto_ingresso', Text),  # JSON: [[prospetto], ...]
                            Column('orientamento_ingresso', Text),
                            Column('articolazione', Text),
                            Column('n_ambienti', Integer),
                            Column('orientamento_ambienti', Text),  # JSON: [[orientamento], ...]
                            Column('sviluppo_planimetrico', Text),
                            Column('elementi_costitutivi', Text),  # JSON: [[elemento], ...]
                            Column('motivo_decorativo', Text),
                            Column('potenzialita_archeologica', Text),
                            Column('manufatti', Text),  # JSON: [[manufatto], ...]
                            Column('elementi_datanti', Text),
                            Column('fasi_funzionali', Text),  # JSON: [[ambiente, periodizzazione, definizione], ...]

                            # explicit/composite unique constraint.  'name' is optional.
                            UniqueConstraint('sito', 'sigla_struttura', 'numero_struttura', name='ID_struttura_unico')
                            )

    # DO NOT create tables at module import time!


    # metadata.create_all(engine)  # This line was causing connection errors
