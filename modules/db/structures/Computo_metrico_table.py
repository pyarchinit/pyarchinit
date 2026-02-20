'''
Created on 20 feb 2026

@author: Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, Float, Text, MetaData

from modules.db.pyarchinit_conn_strings import Connection


class Computo_metrico_table:

    metadata = MetaData()

    # define tables
    computo_metrico_table = Table('computo_metrico_table', metadata,
                                  Column('id_computo', Integer, primary_key=True),
                                  Column('sito', Text),
                                  Column('nome_calcolo', Text),
                                  Column('tipo_calcolo', Text),
                                  Column('dem_pre', Text),
                                  Column('dem_post', Text),
                                  Column('layer_poligono', Text),
                                  Column('area_mq', Float),
                                  Column('volume_mc', Float),
                                  Column('quota_min', Float),
                                  Column('quota_max', Float),
                                  Column('data_calcolo', Text),
                                  Column('fase_scavo', Text),
                                  Column('note', Text),
                                  Column('entity_uuid', Text),
                                  )

    # DO NOT create tables at module import time!
