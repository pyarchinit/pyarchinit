'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, String, Text,  UniqueConstraint


# Table representing thesaurus of archaeological abbreviations and codes
class Pyarchinit_thesaurus_sigle:
    @classmethod
    def define_table(cls, metadata):
        return Table('pyarchinit_thesaurus_sigle', metadata,
                     # Unique identifier for each thesaurus entry
                     Column('id_thesaurus_sigle', Integer, primary_key=True),

                     # Name of the related database table
                     Column('nome_tabella', Text),

                     # Abbreviation/code (max 3 characters)
                     Column('sigla', String(3)),

                     # Extended form of the abbreviation
                     Column('sigla_estesa', Text),

                     # Description of the abbreviation's meaning
                     Column('descrizione', Text),

                     # Type/category of the abbreviation
                     Column('tipologia_sigla', Text),

                     # Language of the abbreviation
                     Column('lingua', Text),

                     # Unique constraint on the thesaurus ID
                     UniqueConstraint('id_thesaurus_sigle', name='id_thesaurus_sigle_pk')
                     )
