'''
Created on 19 feb 2018

@author: Serena Sensini
'''

from modules.db.pyarchinit_conn_strings import Connection
from sqlalchemy import Table, Column, Integer, Date, String, Text, Float, Numeric, MetaData, ForeignKey, engine, create_engine, UniqueConstraint


class SCHEDAIND_table:
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
    metadata = MetaData(engine)

    # define tables
    individui_table = Table('individui_table', metadata,
    Column('id_scheda_ind', Integer, primary_key=True),
    Column('sito', Text),
    Column('area', String(4)),
    Column('us', Integer),
    Column('nr_individuo', Integer),
    Column('data_schedatura', String(100)),
    Column('schedatore', String(100)),
    Column('sesso', String(100)),
    Column('eta_min', Integer),
    Column('eta_max', Integer),
    Column('classi_eta', String(100)),
    Column('osservazioni', Text),

    # explicit/composite unique constraint.  'name' is optional.
    UniqueConstraint('sito', 'nr_individuo', name='ID_individuo_unico')
    )

    metadata.create_all(engine)

