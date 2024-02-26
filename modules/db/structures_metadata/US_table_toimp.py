'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, String, Text, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class US_table_toimp:
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    metadata = MetaData(engine)

    # define tables
    us_table_toimp = Table('us_table_toimp', metadata,
                           Column('id_us', Integer, primary_key=True),
                           Column('sito', Text),
                           Column('area', String(4)),
                           Column('us', Integer),
                           Column('d_stratigrafica', String(100)),
                           Column('d_interpretativa', String(100)),
                           Column('descrizione', Text),
                           Column('interpretazione', Text),
                           Column('periodo_iniziale', String(4)),
                           Column('fase_iniziale', String(4)),
                           Column('periodo_finale', String(4)),
                           Column('fase_finale', String(4)),
                           Column('scavato', String(2)),
                           Column('attivita', String(4)),
                           Column('anno_scavo', String(4)),
                           Column('metodo_di_scavo', String(20)),
                           Column('inclusi', Text),
                           Column('campioni', Text),
                           Column('rapporti', Text),
                           Column('data_schedatura', String(20)),
                           Column('schedatore', String(25)),
                           Column('formazione', String(20)),
                           Column('stato_di_conservazione', String(20)),
                           Column('colore', String(20)),
                           Column('consistenza', String(20)),
                           Column('struttura', String(30)),
                           Column('cont_per', Text),
                           Column('order_layer', Integer),
                           Column('documentazione', Text),

                           # explicit/composite unique constraint.  'name' is optional.
                           UniqueConstraint('sito', 'area', 'us', name='ID_us_unico_toimp')
                           )

    metadata.create_all(engine)
