'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, Text, Numeric, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class Fauna:
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=True, convert_unicode=True)
    metadata = MetaData(engine)

    # define tables
    fauna = Table('fauna', metadata,
    Column( 'id_', Integer, primary_key=True),
    Column( 'code', Integer),
    Column( 'n_rilievo', Text),
    Column( 'n_codice', Text),
    Column( 'anno', Text),
    Column( 'sito', Text),
    Column( 'quadrato', Text), 
    Column( 'us', Integer),
    Column( 'periodo', Integer),
    Column( 'fase', Integer), 
    Column( 'specie', Text),
    Column( 'classe', Text),
    Column( 'ordine', Text),
    Column( 'famiglia', Text),
    Column( 'elemnto_anat_generico', Text),
    Column( 'elem_specifici', Text),
    Column( 'taglia', Text),
    Column( 'eta', Text),
    Column( 'lato', Text),
    Column( 'lunghezza', Integer),
    Column( 'larghezza', Integer),
    Column( 'spessore', Integer),
    Column( 'porzione', Text),
    Column( 'peso', Numeric(12,6)),
    Column( 'coord_x', Numeric(12,6)),
    Column( 'coord_y', Numeric(12,6)),
    Column( 'coord_z', Numeric(12,6)),
    Column( 'azione', Text),
    Column( 'modulo_osso', Text))

    # explicit/composite unique constraint.  'name' is optional.
    #UniqueConstraint('sito', 'quadrato', name='ID_archzoo_unico')
    

    metadata.create_all(engine)
