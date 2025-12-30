"""
Created on 17 11 2020

@author: Enzo Cocca
"""

from sqlalchemy import Table, Column, Integer,  Text,  MetaData, create_engine, UniqueConstraint
from geoalchemy2 import Geometry
from modules.db.pyarchinit_conn_strings import Connection


# Questo codice definisce una classe chiamata 'pyripartizioni_spaziali'.
# All'interno di questa classe, viene stabilita una connessione a un database PostgreSQL
# e viene creato un motore di database. Viene quindi definita una tabella
# 'pyarchinit_ripartizioni_spaziali' con diverse colonne. Infine,
# tutte le modifiche vengono applicate al database.

class pyripartizioni_spaziali:
    # Connessione a postgres
    # Creazione del motore e dei metadati
    metadata = MetaData()
    # Definizione della tabella per verifica fill fields 20/10/2016 OK
    pyripartizioni_spaziali = Table('pyarchinit_ripartizioni_spaziali', metadata,
                     Column('gid', Integer, primary_key=True),  # 0
                     Column('id_rs', Text),
                     Column('sito_rs', Text),
                     Column('tip_rip', Text),
                     Column('descr_rs', Text),
                     Column('the_geom', Geometry(geometry_type='POLYGON')),
                     # Vincolo unico esplicito/composito. 'name' è opzionale.
                     UniqueConstraint('gid')
                     )
    # Applicazione delle modifiche al database


    # DO NOT create tables at module import time!
    # metadata.create_all(engine)  # This line was causing connection errors
    
