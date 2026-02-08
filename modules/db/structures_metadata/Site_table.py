'''
Created on 15 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, String, Text,  UniqueConstraint


# Table representing archaeological sites
class Site_table:
    @classmethod
    def define_table(cls, metadata):
        return Table('site_table', metadata,
                     # Unique identifier for each archaeological site
                     Column('id_sito', Integer, primary_key=True),

                     # Name of the archaeological site
                     Column('sito', Text),

                     # Country where the site is located
                     Column('nazione', String(100)),

                     # Region where the site is located
                     Column('regione', String(100)),

                     # Municipality where the site is located
                     Column('comune', String(100)),

                     # Detailed description of the site
                     Column('descrizione', Text),

                     # Province where the site is located
                     Column('provincia', Text),

                     # Definition or classification of the site
                     Column('definizione_sito', Text),

                     # Path to the site documentation or resources
                     Column('sito_path', Text),

                     # Check for finds at the site (e.g., inventory check)
                     Column('find_check', Integer),

                     # StratiGraph persistent identifier (UUID v4)
                     Column('entity_uuid', Text),

                     # Unique constraint ensuring the site name is unique
                     UniqueConstraint('sito', name='ID_sito_unico')
                     )
