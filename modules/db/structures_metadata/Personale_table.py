'''
Created on 20 feb 2026

@author: Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, Float, Text, UniqueConstraint


# Table representing archaeological site personnel data
class Personale_table:
    @classmethod
    def define_table(cls, metadata):
        return Table('personale_table', metadata,
                     # Unique identifier for each personnel record
                     Column('id_personale', Integer, primary_key=True),

                     # Archaeological site name
                     Column('sito', Text),

                     # First name
                     Column('nome', Text),

                     # Last name
                     Column('cognome', Text),

                     # Role on site
                     Column('ruolo', Text),

                     # Professional qualification
                     Column('qualifica', Text),

                     # Italian fiscal code (tax ID)
                     Column('codice_fiscale', Text),

                     # Email address
                     Column('email', Text),

                     # Phone number
                     Column('telefono', Text),

                     # Date of birth
                     Column('data_nascita', Text),

                     # Address
                     Column('indirizzo', Text),

                     # Contract type
                     Column('tipo_contratto', Text),

                     # Contract start date
                     Column('data_inizio_contratto', Text),

                     # Contract end date
                     Column('data_fine_contratto', Text),

                     # Hourly rate
                     Column('tariffa_oraria', Float),

                     # Daily rate
                     Column('tariffa_giornaliera', Float),

                     # Bank account IBAN
                     Column('iban', Text),

                     # Notes
                     Column('note', Text),

                     # Active status (1=active, 0=inactive)
                     Column('attivo', Integer),

                     # StratiGraph persistent identifier (UUID v4)
                     Column('entity_uuid', Text),

                     # Unique constraint ensuring the combination of site and fiscal code is unique
                     UniqueConstraint('sito', 'codice_fiscale', name='ID_personale_unico')
                     )
