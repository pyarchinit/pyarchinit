'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, Text, Numeric, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class Inventario_Lapidei_table:

    metadata = MetaData()

    # define tables
    inventario_lapidei_table = Table('inventario_lapidei_table', metadata,
                                     Column('id_invlap', Integer, primary_key=True),
                                     Column('sito', Text),
                                     Column('scheda_numero', Integer),
                                     Column('collocazione', Text),
                                     Column('oggetto', Text),
                                     Column('tipologia', Text),
                                     Column('materiale', Text),
                                     Column('d_letto_posa', Numeric(4, 2)),
                                     Column('d_letto_attesa', Numeric(4, 2)),
                                     Column('toro', Numeric(4, 2)),
                                     Column('spessore', Numeric(4, 2)),
                                     Column('larghezza', Numeric(4, 2)),
                                     Column('lunghezza', Numeric(4, 2)),
                                     Column('h', Numeric(4, 2)),
                                     Column('descrizione', Text),
                                     Column('lavorazione_e_stato_di_conservazione', Text),
                                     Column('confronti', Text),
                                     Column('cronologia', Text),
                                     Column('bibliografia', Text),
                                     Column('compilatore', Text),
                                     Column('entity_uuid', Text),
                                     # explicit/composite unique constraint.  'name' is optional.
                                     UniqueConstraint('sito', 'scheda_numero', name='ID_invlap_unico')
                                     )

    # DO NOT create tables at module import time!


    # metadata.create_all(engine)  # This line was causing connection errors
