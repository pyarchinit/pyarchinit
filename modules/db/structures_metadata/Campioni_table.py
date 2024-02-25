'''
Created on 15 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, String, Text,  UniqueConstraint




class Campioni_table:
    # Definizione della tabella come metodo di classe che accetta `metadata` esterno
    @classmethod
    def define_table(cls, metadata):
        return Table('campioni_table', metadata,
                               Column('id_campione', Integer, primary_key=True),
                               Column('sito', Text),
                               Column('nr_campione', Integer),
                               Column('tipo_campione', Text),
                               Column('descrizione', Text),
                               Column('area', String(20)),
                               Column('us', Integer),
                               Column('numero_inventario_materiale', Integer),
                               Column('nr_cassa', Integer),
                               Column('luogo_conservazione', Text),

                               # explicit/composite unique constraint.  'name' is optional.
                               UniqueConstraint('sito', 'nr_campione', name='ID_invcamp_unico')
                               )


