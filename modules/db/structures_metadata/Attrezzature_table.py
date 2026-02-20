'''
Created on 20 feb 2026

@author: Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, Float, Text, UniqueConstraint


# Table representing archaeological site equipment inventory
class Attrezzature_table:
    @classmethod
    def define_table(cls, metadata):
        return Table('attrezzature_table', metadata,
                     # Unique identifier for each equipment record
                     Column('id_attrezzatura', Integer, primary_key=True),

                     # Archaeological site name
                     Column('sito', Text),

                     # Inventory code
                     Column('codice_inventario', Text),

                     # Equipment name
                     Column('nome', Text),

                     # Equipment category
                     Column('categoria', Text),

                     # Brand/manufacturer
                     Column('marca', Text),

                     # Model
                     Column('modello', Text),

                     # Serial number
                     Column('numero_serie', Text),

                     # Ownership (owned, rented, etc.)
                     Column('proprieta', Text),

                     # Purchase date
                     Column('data_acquisto', Text),

                     # Purchase cost
                     Column('costo_acquisto', Float),

                     # Daily rental cost
                     Column('costo_noleggio_giorno', Float),

                     # Current status (active, in maintenance, etc.)
                     Column('stato', Text),

                     # Assigned to personnel ID
                     Column('assegnato_a', Integer),

                     # Last maintenance date
                     Column('data_ultima_manutenzione', Text),

                     # Next scheduled maintenance date
                     Column('data_prossima_manutenzione', Text),

                     # Notes
                     Column('note', Text),

                     # StratiGraph persistent identifier (UUID v4)
                     Column('entity_uuid', Text),

                     # Unique constraint ensuring the combination of site and inventory code is unique
                     UniqueConstraint('sito', 'codice_inventario', name='ID_attrezzatura_unico')
                     )
