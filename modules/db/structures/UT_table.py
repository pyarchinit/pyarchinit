'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, String, Text, Float, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class UT_table:

    metadata = MetaData()

    # define tables
    ut_table = Table('ut_table', metadata,
                     Column('id_ut', Integer, primary_key=True),  # 0
                     Column('progetto', String(100)),  # 1
                     Column('nr_ut', Integer),  # 2
                     Column('ut_letterale', String(100)),  # 3
                     Column('def_ut', String(100)),  # 4
                     Column('descrizione_ut', Text),  # 5
                     Column('interpretazione_ut', String(100)),  # 6
                     Column('nazione', String(100)),  # 7
                     Column('regione', String(100)),  # 8
                     Column('provincia', String(100)),  # 9
                     Column('comune', String(100)),  # 10
                     Column('frazione', String(100)),  # 11
                     Column('localita', String(100)),  # 12
                     Column('indirizzo', String(100)),  # 13
                     Column('nr_civico', String(100)),  # 14
                     Column('carta_topo_igm', String(100)),  # 15
                     Column('carta_ctr', String(100)),  # 16
                     Column('coord_geografiche', String(100)),  # 17
                     Column('coord_piane', String(100)),  # 18
                     Column('quota', Float(3, 2)),  # 19
                     Column('andamento_terreno_pendenza', String(100)),  # 20
                     Column('utilizzo_suolo_vegetazione', String(100)),  # 21
                     Column('descrizione_empirica_suolo', Text),  # 22
                     Column('descrizione_luogo', Text),  # 23
                     Column('metodo_rilievo_e_ricognizione', String(100)),  # 24
                     Column('geometria', String(100)),  # 25
                     Column('bibliografia', Text),  # 26
                     Column('data', String(100)),  # 27
                     Column('ora_meteo', String(100)),  # 28
                     Column('responsabile', String(100)),  # 29
                     Column('dimensioni_ut', String(100)),  # 30
                     Column('rep_per_mq', String(100)),  # 31
                     Column('rep_datanti', String(100)),  # 32
                     Column('periodo_I', String(100)),  # 33
                     Column('datazione_I', String(100)),  # 34
                     Column('interpretazione_I', String(100)),  # 35
                     Column('periodo_II', String(100)),  # 36
                     Column('datazione_II', String(100)),  # 37
                     Column('interpretazione_II', String(100)),  # 38
                     Column('documentazione', Text),  # 39
                     Column('enti_tutela_vincoli', String(100)),  # 40
                     Column('indagini_preliminari', String(100)),  # 41
                     # New survey fields (v4.9.21+)
                     Column('visibility_percent', Integer),  # 42 - Survey visibility (0-100%)
                     Column('vegetation_coverage', String(255)),  # 43 - Vegetation type/coverage
                     Column('gps_method', String(100)),  # 44 - GPS method (RTK, DGPS, handheld)
                     Column('coordinate_precision', Float),  # 45 - GPS precision in meters
                     Column('survey_type', String(100)),  # 46 - topographic, archaeological, mixed
                     Column('surface_condition', String(255)),  # 47 - plowed, grass, forest, etc.
                     Column('accessibility', String(255)),  # 48 - Site accessibility
                     Column('photo_documentation', Integer),  # 49 - Has photo doc (0/1 boolean)
                     Column('weather_conditions', String(255)),  # 50 - Weather during survey
                     Column('team_members', Text),  # 51 - Survey team names
                     Column('foglio_catastale', String(100)),  # 52 - Cadastral sheet

                     # explicit/composite unique constraint.  'name' is optional.
                     UniqueConstraint('progetto', 'nr_ut', 'ut_letterale', name='ID_ut_unico')
                     )

    # DO NOT create tables at module import time!


    # metadata.create_all(engine)  # This line was causing connection errors
