'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, String, Text, Float, MetaData, create_engine, UniqueConstraint

# Table representing topographic units (UT) records in archaeological contexts
class UT_table:
    @classmethod
    def define_table(cls, metadata):
        return Table('ut_table', metadata,
                     # Unique identifier for each UT record
                     Column('id_ut', Integer, primary_key=True),  # 0

                     # Project name associated with the UT
                     Column('progetto', String(100)),  # 1

                     # Number of the UT
                     Column('nr_ut', Integer),  # 2

                     # Literal representation of the UT
                     Column('ut_letterale', String(100)),  # 3

                     # Definition of the UT
                     Column('def_ut', String(100)),  # 4

                     # Description of the UT
                     Column('descrizione_ut', Text),  # 5

                     # Interpretation of the UT
                     Column('interpretazione_ut', String(100)),  # 6

                     # Nation where the UT is located
                     Column('nazione', String(100)),  # 7

                     # Region where the UT is located
                     Column('regione', String(100)),  # 8

                     # Province where the UT is located
                     Column('provincia', String(100)),  # 9

                     # Municipality where the UT is located
                     Column('comune', String(100)),  # 10

                     # Fraction or subdivision of the municipality
                     Column('frazione', String(100)),  # 11

                     # Locality name
                     Column('localita', String(100)),  # 12

                     # Address of the UT
                     Column('indirizzo', String(100)),  # 13

                     # Civic number of the address
                     Column('nr_civico', String(100)),  # 14

                     # Topographic map reference (IGM)
                     Column('carta_topo_igm', String(100)),  # 15

                     # CTR map reference
                     Column('carta_ctr', String(100)),  # 16

                     # Geographic coordinates of the UT
                     Column('coord_geografiche', String(100)),  # 17

                     # Plane coordinates of the UT
                     Column('coord_piane', String(100)),  # 18

                     # Elevation of the UT
                     Column('quota', Float(3, 2)),  # 19

                     # Terrain slope characteristics
                     Column('andamento_terreno_pendenza', String(100)),  # 20

                     # Land use and vegetation description
                     Column('utilizzo_suolo_vegetazione', String(100)),  # 21

                     # Empirical soil description
                     Column('descrizione_empirica_suolo', Text),  # 22

                     # Description of the location
                     Column('descrizione_luogo', Text),  # 23

                     # Method of survey and reconnaissance
                     Column('metodo_rilievo_e_ricognizione', String(100)),  # 24

                     # Geometry of the UT
                     Column('geometria', String(100)),  # 25

                     # Bibliography related to the UT
                     Column('bibliografia', Text),  # 26

                     # Date of record
                     Column('data', String(100)),  # 27

                     # Weather conditions at the time of record
                     Column('ora_meteo', String(100)),  # 28

                     # Responsible person for the record
                     Column('responsabile', String(100)),  # 29

                     # Dimensions of the UT
                     Column('dimensioni_ut', String(100)),  # 30

                     # Representation per square meter
                     Column('rep_per_mq', String(100)),  # 31

                     # Dating references
                     Column('rep_datanti', String(100)),  # 32

                     # Period I associated with the UT
                     Column('periodo_I', String(100)),  # 33

                     # Dating for Period I
                     Column('datazione_I', String(100)),  # 34

                     # Interpretation for Period I
                     Column('interpretazione_I', String(100)),  # 35

                     # Period II associated with the UT
                     Column('periodo_II', String(100)),  # 36

                     # Dating for Period II
                     Column('datazione_II', String(100)),  # 37

                     # Interpretation for Period II
                     Column('interpretazione_II', String(100)),  # 38

                     # Documentation related to the UT
                     Column('documentazione', Text),  # 39

                     # Entities responsible for protection and constraints
                     Column('enti_tutela_vincoli', String(100)),  # 40

                     # Preliminary investigations conducted
                     Column('indagini_preliminari', String(100)),  # 41

                     # StratiGraph persistent identifier (UUID v4)
                     Column('entity_uuid', Text),

                     # Unique constraint ensuring the combination of project, UT number, and literal representation is unique
                     UniqueConstraint('progetto', 'nr_ut', 'ut_letterale', name='ID_ut_unico')
                     )
