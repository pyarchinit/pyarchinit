'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, String, Text, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class Pyarchinit_thesaurus_sigle:
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    metadata = MetaData(engine)

    # define tables
    pyarchinit_thesaurus_sigle = Table('pyarchinit_thesaurus_sigle', metadata,
                                       Column('id_thesaurus_sigle', Integer, primary_key=True),
                                       Column('nome_tabella', Text),
                                       Column('sigla', String(100)),
                                       Column('sigla_estesa', Text),
                                       Column('descrizione', Text),
                                       Column('tipologia_sigla', String(100)),
                                       Column('lingua', String(10)),
                                       Column('order_layer', Integer, default=0),
                                       Column('id_parent', Integer),
                                       Column('parent_sigla', String(100)),
                                       Column('hierarchy_level', Integer, default=0),

                                       # explicit/composite unique constraint.  'name' is optional.
                                       UniqueConstraint('id_thesaurus_sigle', name='id_thesaurus_sigle_pk')
                                       )

    try:
        metadata.create_all(engine)
    except:
        pass  # Table already exists or geometry type not supported
    
    # Check and add missing columns for both SQLite and PostgreSQL
    try:
        conn = engine.connect()
        
        if 'sqlite' in internal_connection.conn_str().lower():
            # SQLite: Check existing columns
            result = conn.execute("PRAGMA table_info(pyarchinit_thesaurus_sigle)")
            existing_columns = [row[1] for row in result]
            
            # Add missing columns if needed
            if 'order_layer' not in existing_columns:
                conn.execute("ALTER TABLE pyarchinit_thesaurus_sigle ADD COLUMN order_layer INTEGER DEFAULT 0")
            if 'id_parent' not in existing_columns:
                conn.execute("ALTER TABLE pyarchinit_thesaurus_sigle ADD COLUMN id_parent INTEGER")
            if 'parent_sigla' not in existing_columns:
                conn.execute("ALTER TABLE pyarchinit_thesaurus_sigle ADD COLUMN parent_sigla VARCHAR(100)")
            if 'hierarchy_level' not in existing_columns:
                conn.execute("ALTER TABLE pyarchinit_thesaurus_sigle ADD COLUMN hierarchy_level INTEGER DEFAULT 0")
        else:
            # PostgreSQL: Check existing columns
            result = conn.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'pyarchinit_thesaurus_sigle'
            """)
            existing_columns = [row[0] for row in result]
            
            # Add missing columns if needed
            if 'order_layer' not in existing_columns:
                conn.execute("ALTER TABLE pyarchinit_thesaurus_sigle ADD COLUMN order_layer INTEGER DEFAULT 0")
            if 'id_parent' not in existing_columns:
                conn.execute("ALTER TABLE pyarchinit_thesaurus_sigle ADD COLUMN id_parent INTEGER")
            if 'parent_sigla' not in existing_columns:
                conn.execute("ALTER TABLE pyarchinit_thesaurus_sigle ADD COLUMN parent_sigla VARCHAR(100)")
            if 'hierarchy_level' not in existing_columns:
                conn.execute("ALTER TABLE pyarchinit_thesaurus_sigle ADD COLUMN hierarchy_level INTEGER DEFAULT 0")
                
        conn.close()
    except:
        pass  # Silently ignore any errors
