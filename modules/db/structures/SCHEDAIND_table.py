'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, Float, Numeric,String, Text, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class SCHEDAIND_table:
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    metadata = MetaData(engine)

    # define tables
    individui_table = Table('individui_table', metadata,
                            Column('id_scheda_ind', Integer, primary_key=True),
                            Column('sito', Text),
                            Column('area', Text),
                            Column('us', Text),
                            Column('nr_individuo', Integer),
                            Column('data_schedatura', String(100)),
                            Column('schedatore', String(100)),
                            Column('sesso', String(100)),
                            Column('eta_min', Text),
                            Column('eta_max', Text),
                            Column('classi_eta', String(100)),
                            Column('osservazioni', Text),
                            Column('sigla_struttura', Text),
                            Column('nr_struttura', Integer),
                            Column('completo_si_no', String(5)),
                            Column('disturbato_si_no', String(5)),
                            Column('in_connessione_si_no', String(5)),
                            Column('lunghezza_scheletro', Numeric(6,2)),
                            Column('posizione_scheletro', String(50)),
                            Column('posizione_cranio', String(50)),
                            Column('posizione_arti_superiori', String(50)),
                            Column('posizione_arti_inferiori', String(50)),
                            Column('orientamento_asse', Text),
                            Column('orientamento_azimut',Text),

                            # explicit/composite unique constraint.  'name' is optional.
                            UniqueConstraint('sito', 'nr_individuo', name='ID_individuo_unico')
                            )

    metadata.create_all(engine)
