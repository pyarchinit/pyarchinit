'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, String, Text,  UniqueConstraint


# Table representing tomb data and associated archaeological findings
class Tomba_table:
    @classmethod
    def define_table(cls, metadata):
        return Table('tomba_table', metadata,
                     # Unique identifier for each tomb record
                     Column('id_tomba', Integer, primary_key=True),

                     # Archaeological site name
                     Column('sito', Text),

                     # Area of excavation
                     Column('area', Integer),

                     # Reference number for the record sheet
                     Column('nr_scheda_taf', Integer),

                     # Abbreviation for the structure associated with the tomb
                     Column('sigla_struttura', Text),

                     # Number assigned to the structure
                     Column('nr_struttura', Integer),

                     # Individual number associated with the tomb
                     Column('nr_individuo', Text),

                     # Burial rite description
                     Column('rito', Text),

                     # Description of the tomb record
                     Column('descrizione_taf', Text),

                     # Archaeological interpretation of the tomb
                     Column('interpretazione_taf', Text),

                     # Markers or signs associated with the tomb
                     Column('segnacoli', Text),

                     # Indicates if a libation channel is present (Yes/No)
                     Column('canale_libatorio_si_no', Text),

                     # Objects found outside the tomb
                     Column('oggetti_rinvenuti_esterno', Text),

                     # State of preservation of the tomb
                     Column('stato_di_conservazione', Text),

                     # Type of covering for the tomb
                     Column('copertura_tipo', Text),

                     # Type of container for remains
                     Column('tipo_contenitore_resti', Text),

                     # Type of deposition of the remains
                     Column('tipo_deposizione', Text),

                     # Type of burial
                     Column('tipo_sepoltura', Text),

                     # Presence of grave goods
                     Column('corredo_presenza', Text),

                     # Type of grave goods
                     Column('corredo_tipo', Text),

                     # Description of grave goods
                     Column('corredo_descrizione', Text),

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

                     # Unique constraint ensuring the combination of site and record sheet number is unique
                     UniqueConstraint('sito', 'nr_scheda_taf', name='ID_tomba_unico')
                     )



