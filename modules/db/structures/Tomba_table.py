'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, String, Text, Float, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class Tomba_table:
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    metadata = MetaData(engine)

    # define tables
    tomba_table = Table('tomba_table', metadata,
                            Column('id_tomba', Integer, primary_key=True),
                            Column('sito', Text),
                            Column('area', Integer),
                            Column('nr_scheda_taf', Integer),
                            Column('sigla_struttura', Text),
                            Column('nr_struttura', Integer),
                            Column('nr_individuo', Text),
                            Column('rito', Text),
                            Column('descrizione_taf', Text),
                            Column('interpretazione_taf', Text),
                            Column('segnacoli', Text),
                            Column('canale_libatorio_si_no', Text),
                            Column('oggetti_rinvenuti_esterno', Text),
                            Column('stato_di_conservazione', Text),
                            Column('copertura_tipo', Text),
                            Column('tipo_contenitore_resti', Text),
                            Column('tipo_deposizione', Text),
                            Column('tipo_sepoltura', Text),
                            Column('corredo_presenza', Text),
                            Column('corredo_tipo', Text),
                            Column('corredo_descrizione', Text),
                            Column('periodo_iniziale', Integer),
                            Column('fase_iniziale', Integer),
                            Column('periodo_finale', Integer),
                            Column('fase_finale', Integer),
                            Column('datazione_estesa', String(300)),
                            

                            # explicit/composite unique constraint.  'name' is optional.
                            UniqueConstraint('sito', 'nr_scheda_taf', name='ID_tomba_unico')
                            )

    metadata.create_all(engine)
