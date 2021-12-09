'''
Created on 15 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Index, Table, Column, Integer, String, Text, Numeric, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class Inventario_materiali_table:
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    metadata = MetaData(engine)

    # define tables
    inventario_materiali_table = Table('inventario_materiali_table', metadata,
                                       Column('id_invmat', Integer, primary_key=True),
                                       Column('sito', Text),
                                       Column('numero_inventario', Integer),
                                       Column('tipo_reperto', Text),
                                       Column('criterio_schedatura', Text),
                                       Column('definizione', Text),
                                       Column('descrizione', Text),
                                       Column('area', Integer),
                                       Column('us', Integer),
                                       Column('lavato', String(3)),
                                       Column('nr_cassa', Integer),
                                       Column('luogo_conservazione', Text),
                                       Column('stato_conservazione', String(200)),
                                       Column('datazione_reperto', String(200)),
                                       Column('elementi_reperto', Text),
                                       Column('misurazioni', Text),
                                       Column('rif_biblio', Text),
                                       Column('tecnologie', Text),
                                       Column('forme_minime', Integer),
                                       Column('forme_massime', Integer),
                                       Column('totale_frammenti', Integer),
                                       Column('corpo_ceramico', String(200)),
                                       Column('rivestimento', String(200)),
                                       Column('diametro_orlo', Numeric(7, 3)),
                                       Column('peso', Numeric(9, 3)),
                                       Column('tipo', String(200)),
                                       Column('eve_orlo', Numeric(7, 3)),
                                       Column('repertato', String(3)),
                                       Column('diagnostico', String(3)),
                                       Column('n_reperto', Integer),
                                       Column('tipo_contenitore', String(200)),
                                       Column('struttura', String(200)),
                                       # explicit/composite unique constraint.  'name' is optional.
                                       
                                       #Index('idx_n_reperto', 'sito', 'n_reperto', unique=True),
                                       
                                       UniqueConstraint('sito', 'numero_inventario', name='ID_invmat_unico'))
                                       
                                       

    metadata.create_all(engine)


class Inventario_materiali_table_toimp:
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    metadata = MetaData(engine)

    # define tables
    inventario_materiali_table_toimp = Table('inventario_materiali_table_toimp', metadata,
                                             Column('id_invmat', Integer, primary_key=True),
                                             Column('sito', Text),
                                             Column('numero_inventario', Integer),
                                             Column('tipo_reperto', Text),
                                             Column('criterio_schedatura', Text),
                                             Column('definizione', Text),
                                             Column('descrizione', Text),
                                             Column('area', Integer),
                                             Column('us', Integer),
                                             Column('lavato', String(2)),
                                             Column('nr_cassa', Integer),
                                             Column('luogo_conservazione', Text),
                                             Column('stato_conservazione', String(20)),
                                             Column('datazione_reperto', String(30)),
                                             Column('elementi_reperto', Text),
                                             Column('misurazioni', Text),
                                             Column('rif_biblio', Text),
                                             Column('tecnologie', Text),
                                             Column('forme_minime', Integer),
                                             Column('forme_massime', Integer),
                                             Column('totale_frammenti', Integer),
                                             Column('corpo_ceramico', String(20)),
                                             Column('rivestimento', String(20)),

                                             # explicit/composite unique constraint.  'name' is optional.
                                             UniqueConstraint('sito', 'numero_inventario', name='ID_invmat_unico_toimp')
                                             )

    metadata.create_all(engine)
