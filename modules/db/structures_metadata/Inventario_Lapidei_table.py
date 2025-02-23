'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, Text, Numeric,  UniqueConstraint


# Table representing stone artifacts inventory
class Inventario_Lapidei_table:
    @classmethod
    def define_table(cls, metadata):
        return Table('inventario_lapidei_table', metadata,
                     # Unique identifier for each stone artifact record
                     Column('id_invlap', Integer, primary_key=True),

                     # Archaeological site name
                     Column('sito', Text),

                     # Record sheet number
                     Column('scheda_numero', Integer),

                     # Location of the artifact
                     Column('collocazione', Text),

                     # Object description/name
                     Column('oggetto', Text),

                     # Typology of the stone artifact
                     Column('tipologia', Text),

                     # Material composition
                     Column('materiale', Text),

                     # Laying bed dimension
                     Column('d_letto_posa', Numeric(4, 2)),

                     # Waiting bed dimension
                     Column('d_letto_attesa', Numeric(4, 2)),

                     # Torus dimension
                     Column('toro', Numeric(4, 2)),

                     # Thickness of the artifact
                     Column('spessore', Numeric(4, 2)),

                     # Width of the artifact
                     Column('larghezza', Numeric(4, 2)),

                     # Length of the artifact
                     Column('lunghezza', Numeric(4, 2)),

                     # Height of the artifact
                     Column('h', Numeric(4, 2)),

                     # Detailed description of the artifact
                     Column('descrizione', Text),

                     # Workmanship and state of preservation
                     Column('lavorazione_e_stato_di_conservazione', Text),

                     # Comparative analysis references
                     Column('confronti', Text),

                     # Chronological dating
                     Column('cronologia', Text),

                     # Bibliographic references
                     Column('bibliografia', Text),

                     # Name of the person who compiled the record
                     Column('compilatore', Text),

                     # Unique constraint ensuring the combination of site and record number is unique
                     UniqueConstraint('sito', 'scheda_numero', name='ID_invlap_unico')
                     )


