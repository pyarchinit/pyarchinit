'''
Created on 19 feb 2018

@author: Serena Sensini
'''

from sqlalchemy import Table, Column, Integer, Text, Numeric, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class Archeozoology_table:
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    metadata = MetaData(engine)

    # define tables
    archeozoology_table = Table('archeozoology_table', metadata,
                                Column('id_archzoo', Integer, primary_key=True),
                                Column('sito', Text),
                                Column('area', Text),
                                Column('us', Integer),
                                Column('quadrato', Text),
                                Column('coord_x', Numeric(12, 6)),
                                Column('coord_y', Numeric(12, 6)),
                                Column('coord_z', Numeric(12, 6)),
                                Column('bos_bison', Integer),
                                Column('calcinati', Integer),
                                Column('camoscio', Integer),
                                Column('capriolo', Integer),
                                Column('cervo', Integer),
                                Column('combusto', Integer),
                                Column('coni', Integer),
                                Column('pdi', Integer),
                                Column('stambecco', Integer),
                                Column('strie', Integer),
                                Column('canidi', Integer),
                                Column('ursidi', Integer),
                                Column('megacero', Integer),

                                # explicit/composite unique constraint.  'name' is optional.
                                UniqueConstraint('sito', 'quadrato', name='ID_archzoo_unico')
                                )

    metadata.create_all(engine)
