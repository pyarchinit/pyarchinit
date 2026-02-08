'''
Created on 15 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, Text, MetaData, create_engine, UniqueConstraint


# Table representing archaeological documentation records
class Documentazione_table:
    @classmethod
    def define_table(cls, metadata):
        return Table('documentazione_table', metadata,
                     # Unique identifier for each documentation record
                     Column('id_documentazione', Integer, primary_key=True),

                     # Archaeological site name
                     Column('sito', Text),

                     # Document name/title
                     Column('nome_doc', Text),

                     # Date of documentation
                     Column('data', Text),

                     # Type of documentation (e.g., photo, drawing, map)
                     Column('tipo_documentazione', Text),

                     # Source of the documentation
                     Column('sorgente', Text),

                     # Scale of the documentation (for maps/drawings)
                     Column('scala', Text),

                     # Name of the person who created the drawing/documentation
                     Column('disegnatore', Text),

                     # Additional notes about the documentation
                     Column('note', Text),

                     # StratiGraph persistent identifier (UUID v4)
                     Column('entity_uuid', Text),

                     # Unique constraint ensuring the combination of site, documentation type and document name is unique
                     UniqueConstraint('sito', 'tipo_documentazione', 'nome_doc', name='ID_invdoc_unico')
                     )


