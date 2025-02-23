'''
Created on 19 feb 2018

@author: Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, String, Text,  UniqueConstraint


# Table representing archaeological periodization data
class Periodizzazione_table:
    @classmethod
    def define_table(cls, metadata):
        return Table('periodizzazione_table', metadata,
                     # Unique identifier for each periodization record
                     Column('id_perfas', Integer, primary_key=True),

                     # Archaeological site name
                     Column('sito', Text),

                     # Period number
                     Column('periodo', Integer),

                     # Phase within the period
                     Column('fase', Text),

                     # Initial chronological date
                     Column('cron_iniziale', Integer),

                     # Final chronological date
                     Column('cron_finale', Integer),

                     # Description of the period/phase
                     Column('descrizione', Text),

                     # Extended dating information
                     Column('datazione_estesa', String(300)),

                     # Period context reference
                     Column('cont_per', Integer),

                     # Unique constraint ensuring the combination of site, period and phase is unique
                     UniqueConstraint('sito', 'periodo', 'fase', name='ID_perfas_unico')
                     )



