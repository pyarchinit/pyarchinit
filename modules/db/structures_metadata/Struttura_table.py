'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, String, Text,  UniqueConstraint


# Table representing structural data of archaeological findings
class Struttura_table:
    @classmethod
    def define_table(cls, metadata):
        return Table('struttura_table', metadata,
                     # Unique identifier for each structure record
                     Column('id_struttura', Integer, primary_key=True),

                     # Archaeological site name
                     Column('sito', Text),

                     # Abbreviation for the structure
                     Column('sigla_struttura', Text),

                     # Number assigned to the structure
                     Column('numero_struttura', Integer),

                     # Category of the structure (e.g., building, wall)
                     Column('categoria_struttura', Text),

                     # Typology of the structure (e.g., residential, public)
                     Column('tipologia_struttura', Text),

                     # Definition or classification of the structure
                     Column('definizione_struttura', Text),

                     # Detailed description of the structure
                     Column('descrizione', Text),

                     # Archaeological interpretation of the structure
                     Column('interpretazione', Text),

                     # Initial chronological period
                     Column('periodo_iniziale', Integer),

                     # Initial phase within the period
                     Column('fase_iniziale', Integer),

                     # Final chronological period
                     Column('periodo_finale', Integer),

                     # Final phase within the period
                     Column('fase_finale', Integer),

                     # Extended dating information
                     Column('datazione_estesa', String(300)),

                     # Materials used in the structure
                     Column('materiali_impiegati', Text),

                     # Structural elements present
                     Column('elementi_strutturali', Text),

                     # Relationships with other structures
                     Column('rapporti_struttura', Text),

                     # Measurements of the structure
                     Column('misure_struttura', Text),

                     # Unique constraint ensuring the combination of site, structure abbreviation, and structure number is unique
                     UniqueConstraint('sito', 'sigla_struttura', 'numero_struttura', name='ID_struttura_unico')
                     )



