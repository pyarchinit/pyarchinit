'''
Created on 2024
Fauna table structure for SCHEDA FR (Fauna Record Sheet)

@author: Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, BigInteger, Text, Boolean, Date, MetaData, ForeignKey, UniqueConstraint


class Fauna_table:

    metadata = MetaData()

    # define tables
    fauna_table = Table('fauna_table', metadata,
                        Column('id_fauna', BigInteger, primary_key=True),  # 0
                        Column('id_us', BigInteger),  # 1 - FK to us_table
                        Column('sito', Text),  # 2
                        Column('area', Text),  # 3
                        Column('saggio', Text),  # 4
                        Column('us', Text),  # 5
                        Column('datazione_us', Text),  # 6
                        Column('responsabile_scheda', Text),  # 7
                        Column('data_compilazione', Date),  # 8
                        Column('documentazione_fotografica', Text),  # 9
                        Column('metodologia_recupero', Text),  # 10
                        Column('contesto', Text),  # 11
                        Column('descrizione_contesto', Text),  # 12
                        Column('resti_connessione_anatomica', Text),  # 13
                        Column('tipologia_accumulo', Text),  # 14
                        Column('deposizione', Text),  # 15
                        Column('numero_stimato_resti', Text),  # 16
                        Column('numero_minimo_individui', Integer),  # 17
                        Column('specie', Text),  # 18
                        Column('parti_scheletriche', Text),  # 19
                        Column('specie_psi', Text),  # 20 - JSON array
                        Column('misure_ossa', Text),  # 21 - JSON array
                        Column('stato_frammentazione', Text),  # 22
                        Column('tracce_combustione', Text),  # 23
                        Column('combustione_altri_materiali_us', Boolean),  # 24
                        Column('tipo_combustione', Text),  # 25
                        Column('segni_tafonomici_evidenti', Text),  # 26
                        Column('caratterizzazione_segni_tafonomici', Text),  # 27
                        Column('stato_conservazione', Text),  # 28
                        Column('alterazioni_morfologiche', Text),  # 29
                        Column('note_terreno_giacitura', Text),  # 30
                        Column('campionature_effettuate', Text),  # 31
                        Column('affidabilita_stratigrafica', Text),  # 32
                        Column('classi_reperti_associazione', Text),  # 33
                        Column('osservazioni', Text),  # 34
                        Column('interpretazione', Text),  # 35
                        Column('entity_uuid', Text),

                        # explicit/composite unique constraint
                        UniqueConstraint('sito', 'area', 'us', 'id_fauna', name='ID_fauna_unico')
                        )

    # DO NOT create tables at module import time!
