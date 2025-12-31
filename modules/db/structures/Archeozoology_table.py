'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, BigInteger, Text, Numeric, MetaData, UniqueConstraint


class Archeozoology_table:

    metadata = MetaData()

    # define tables
    archeozoology_table = Table('archeozoology_table', metadata,
                                Column('id_archzoo', BigInteger, primary_key=True),  # 0
                                Column('sito', Text),  # 1
                                Column('area', Text),  # 2
                                Column('us', Text),  # 3
                                Column('quadrato', Text),  # 4
                                Column('coord_x', BigInteger),  # 5
                                Column('coord_y', BigInteger),  # 6
                                Column('coord_z', Numeric(12, 6)),  # 7
                                Column('bos_bison', BigInteger),  # 8
                                Column('calcinati', BigInteger),  # 9
                                Column('camoscio', BigInteger),  # 10
                                Column('capriolo', BigInteger),  # 11
                                Column('cervo', BigInteger),  # 12
                                Column('combusto', BigInteger),  # 13
                                Column('coni', BigInteger),  # 14
                                Column('pdi', BigInteger),  # 15
                                Column('stambecco', BigInteger),  # 16
                                Column('strie', BigInteger),  # 17
                                Column('canidi', BigInteger),  # 18
                                Column('ursidi', BigInteger),  # 19
                                Column('megacero', BigInteger),  # 20

                                # explicit/composite unique constraint
                                UniqueConstraint('sito', 'quadrato', name='ID_archzoo_unico')
                                )

    # DO NOT create tables at module import time!
