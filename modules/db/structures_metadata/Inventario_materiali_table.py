'''
Created on 15 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, String, Text, Numeric,  UniqueConstraint




class Inventario_materiali_table:
    @classmethod
    def define_table(cls, metadata):
        return Table('inventario_materiali_table', metadata,
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
                                       Column('years', Integer),
                                       # explicit/composite unique constraint.  'name' is optional.
                                       
                                       #Index('idx_n_reperto', 'sito', 'n_reperto', unique=True),
                                       
                                       UniqueConstraint('sito', 'numero_inventario', name='ID_invmat_unico'))
                                       
                                       




