"""
Created on 17 11 2020

@author: Enzo Cocca
"""

from geoalchemy2 import Geometry
from sqlalchemy import Table, Column, Integer, Text, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class pylineeriferimento:


    # engine.connect()
    metadata = MetaData()

    # define tables check per verifica fill fields 20/10/2016 OK
    pylineeriferimento = Table('pyarchinit_linee_rif', metadata,
                               Column('gid', Integer, primary_key=True),  # 0
                               Column('sito', Text),
                               Column('definizion', Text),
                               Column('descrizion', Text),
                               Column('the_geom', Geometry(geometry_type='LINESTRING')),
                               # explicit/composite unique constraint.  'name' is optional.
                               UniqueConstraint('gid')
                               )



    # DO NOT create tables at module import time!
    # metadata.create_all(engine)  # This line was causing connection errors
