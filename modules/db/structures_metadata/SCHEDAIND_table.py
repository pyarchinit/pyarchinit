'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer,  Numeric,String, Text,  UniqueConstraint


# Table representing individual records in archaeological contexts
class SCHEDAIND_table:
    @classmethod
    def define_table(cls, metadata):
        return Table('individui_table', metadata,
                     # Unique identifier for each individual record
                     Column('id_scheda_ind', Integer, primary_key=True),

                     # Archaeological site name
                     Column('sito', Text),

                     # Excavation area
                     Column('area', Text),

                     # Stratigraphic unit (US) associated with the individual
                     Column('us', Text),

                     # Individual number
                     Column('nr_individuo', Integer),

                     # Date of record compilation
                     Column('data_schedatura', String(100)),

                     # Name of the person who compiled the record
                     Column('schedatore', String(100)),

                     # Gender of the individual
                     Column('sesso', String(100)),

                     # Minimum age estimate
                     Column('eta_min', Text),

                     # Maximum age estimate
                     Column('eta_max', Text),

                     # Age classes
                     Column('classi_eta', String(100)),

                     # General observations about the individual
                     Column('osservazioni', Text),

                     # Abbreviation for the associated structure
                     Column('sigla_struttura', Text),

                     # Number assigned to the structure
                     Column('nr_struttura', Integer),

                     # Indicates if the individual is complete (Yes/No)
                     Column('completo_si_no', String(5)),

                     # Indicates if the individual is disturbed (Yes/No)
                     Column('disturbato_si_no', String(5)),

                     # Indicates if the individual is in connection with other finds (Yes/No)
                     Column('in_connessione_si_no', String(5)),

                     # Length of the skeleton
                     Column('lunghezza_scheletro', Numeric(6, 2)),

                     # Position of the skeleton
                     Column('posizione_scheletro', String(50)),

                     # Position of the skull
                     Column('posizione_cranio', String(50)),

                     # Position of the upper limbs
                     Column('posizione_arti_superiori', String(50)),

                     # Position of the lower limbs
                     Column('posizione_arti_inferiori', String(50)),

                     # Orientation of the skeleton's axis
                     Column('orientamento_asse', Text),

                     # Azimuth orientation of the skeleton
                     Column('orientamento_azimut', Text),

                     # StratiGraph persistent identifier (UUID v4)
                     Column('entity_uuid', Text),

                     # Unique constraint ensuring the combination of site and individual number is unique
                     UniqueConstraint('sito', 'nr_individuo', name='ID_individuo_unico')
                     )



