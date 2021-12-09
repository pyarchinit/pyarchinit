'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, Text, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class PDF_administrator_table:
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    metadata = MetaData(engine)

    # define tables
    pdf_administrator_table = Table('pdf_administrator_table', metadata,
                                    Column('id_pdf_administrator', Integer, primary_key=True),
                                    Column('table_name', Text),
                                    Column('schema_griglia', Text),
                                    Column('schema_fusione_celle', Text),
                                    Column('modello', Text),

                                    # explicit/composite unique constraint.  'name' is optional.
                                    UniqueConstraint('table_name', 'modello', name='ID_pdf_administrator_unico')
                                    )

    metadata.create_all(engine)
