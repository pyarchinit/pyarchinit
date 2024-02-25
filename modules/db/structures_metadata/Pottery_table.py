'''
Created on 05 dic 2022

@author:  Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, Numeric, Text,  UniqueConstraint


class PotteryTable:
    # Definizione della tabella come metodo di classe che accetta `metadata` esterno
    @classmethod
    def define_table(cls, metadata):
        return Table('pottery_table', metadata,
                     Column('id_rep', Integer, primary_key=True),
                     Column('id_number', Integer),
                     Column('sito', Text),
                     Column('area', Text),
                     Column('us', Integer),
                     Column('box', Integer),
                     Column('photo', Text),
                     Column('drawing', Text),
                     Column('anno', Integer),
                     Column('fabric', Text),
                     Column('percent', Text),
                     Column('material', Text),
                     Column('form', Text),
                     Column('specific_form', Text),
                     Column('ware', Text),
                     Column('munsell', Text),
                     Column('surf_trat', Text),
                     Column('exdeco', Text),
                     Column('intdeco', Text),
                     Column('wheel_made', Text),
                     Column('descrip_ex_deco', Text),
                     Column('descrip_in_deco', Text),
                     Column('note', Text),
                     Column('diametro_max', Numeric(7,3)),
                     Column('qty', Integer),
                     Column('diametro_rim', Numeric(7,3)),
                     Column('diametro_bottom', Numeric(7,3)),
                     Column('diametro_height', Numeric(7,3)),
                     Column('diametro_preserved', Numeric(7,3)),
                     Column('specific_shape', Text),
                     Column('bag', Integer),
                     Column('sector', Text),
                     UniqueConstraint('sito', 'id_number', name='ID_rep_unico')
                    )


