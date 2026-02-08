'''
Created on 15 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, String, Text,  UniqueConstraint


# Table representing archaeological samples (Campioni)
class Campioni_table:
    # Class method that defines the table structure accepting external metadata
    @classmethod
    def define_table(cls, metadata):
        return Table('campioni_table', metadata,
                     # Unique identifier for each sample
                     Column('id_campione', Integer, primary_key=True),

                     # Archaeological site where the sample was collected
                     Column('sito', Text),

                     # Sample number
                     Column('nr_campione', Integer),

                     # Type of sample (e.g., soil, charcoal, bone)
                     Column('tipo_campione', Text),

                     # Detailed description of the sample
                     Column('descrizione', Text),

                     # Excavation area where the sample was collected
                     Column('area', String(20)),

                     # Stratigraphic unit (US) associated with the sample
                     Column('us', Integer),

                     # Inventory number of the material
                     Column('numero_inventario_materiale', Integer),

                     # Storage box number
                     Column('nr_cassa', Text),

                     # Storage location of the sample
                     Column('luogo_conservazione', Text),

                     # StratiGraph persistent identifier (UUID v4)
                     Column('entity_uuid', Text),

                     # Unique constraint ensuring the combination of site and sample number is unique
                     UniqueConstraint('sito', 'nr_campione', name='ID_invcamp_unico')
                     )



