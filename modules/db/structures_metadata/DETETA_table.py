'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, Text,  UniqueConstraint


# Table representing age determination data for skeletal remains
class DETETA_table:
    # Class method that defines the table structure accepting external metadata
    @classmethod
    def define_table(cls, metadata):
        return Table('deteta_table', metadata,


                         # Unique identifier for each age determination record
                         Column('id_det_eta', Integer, primary_key=True),

                         # Archaeological site name
                         Column('sito', Text),

                         # Individual number
                         Column('nr_individuo', Integer),

                         # Minimum value for symphysis pubis
                         Column('sinf_min', Integer),

                         # Maximum value for symphysis pubis
                         Column('sinf_max', Integer),

                         # Secondary minimum value for symphysis pubis
                         Column('sinf_min_2', Integer),

                         # Secondary maximum value for symphysis pubis
                         Column('sinf_max_2', Integer),

                         # Sacro-sciatic pubic index A
                         Column('SSPIA', Integer),

                         # Sacro-sciatic pubic index B
                         Column('SSPIB', Integer),

                         # Sacro-sciatic pubic index C
                         Column('SSPIC', Integer),

                         # Sacro-sciatic pubic index D
                         Column('SSPID', Integer),

                         # Minimum value for auricular surface
                         Column('sup_aur_min', Integer),

                         # Maximum value for auricular surface
                         Column('sup_aur_max', Integer),

                         # Secondary minimum value for auricular surface
                         Column('sup_aur_min_2', Integer),

                         # Secondary maximum value for auricular surface
                         Column('sup_aur_max_2', Integer),

                         # Minimum value for superior maxillary suture
                         Column('ms_sup_min', Integer),

                         # Maximum value for superior maxillary suture
                         Column('ms_sup_max', Integer),

                         # Minimum value for inferior maxillary suture
                         Column('ms_inf_min', Integer),

                         # Maximum value for inferior maxillary suture
                         Column('ms_inf_max', Integer),

                         # Minimum dental wear value
                         Column('usura_min', Integer),

                         # Maximum dental wear value
                         Column('usura_max', Integer),

                         # Right first incisor endocranial suture
                         Column('Id_endo', Integer),

                         # Left first incisor endocranial suture
                         Column('Is_endo', Integer),

                         # Right second incisor endocranial suture
                         Column('IId_endo', Integer),

                         # Left second incisor endocranial suture
                         Column('IIs_endo', Integer),

                         # Right third incisor endocranial suture
                         Column('IIId_endo', Integer),

                         # Left third incisor endocranial suture
                         Column('IIIs_endo', Integer),

                         # Fourth endocranial suture
                         Column('IV_endo', Integer),

                         # Fifth endocranial suture
                         Column('V_endo', Integer),

                         # Sixth endocranial suture
                         Column('VI_endo', Integer),

                         # Seventh endocranial suture
                         Column('VII_endo', Integer),

                         # Right eighth endocranial suture
                         Column('VIIId_endo', Integer),

                         # Left eighth endocranial suture
                         Column('VIIIs_endo', Integer),

                         # Right ninth endocranial suture
                         Column('IXd_endo', Integer),

                         # Left ninth endocranial suture
                         Column('IXs_endo', Integer),

                         # Right tenth endocranial suture
                         Column('Xd_endo', Integer),

                         # Left tenth endocranial suture
                         Column('Xs_endo', Integer),

                         # Minimum endocranial value
                         Column('endo_min', Integer),

                         # Maximum endocranial value
                         Column('endo_max', Integer),

                         # Vault suture 1
                         Column('volta_1', Integer),

                         # Vault suture 2
                         Column('volta_2', Integer),

                         # Vault suture 3
                         Column('volta_3', Integer),

                         # Vault suture 4
                         Column('volta_4', Integer),

                         # Vault suture 5
                         Column('volta_5', Integer),

                         # Vault suture 6
                         Column('volta_6', Integer),

                         # Vault suture 7
                         Column('volta_7', Integer),

                         # Lateral suture 6
                         Column('lat_6', Integer),

                         # Lateral suture 7
                         Column('lat_7', Integer),

                         # Lateral suture 8
                         Column('lat_8', Integer),

                         # Lateral suture 9
                         Column('lat_9', Integer),

                         # Lateral suture 10
                         Column('lat_10', Integer),

                         # Minimum vault value
                         Column('volta_min', Integer),

                         # Maximum vault value
                         Column('volta_max', Integer),

                         # Minimum anterolateral value
                         Column('ant_lat_min', Integer),

                         # Maximum anterolateral value
                         Column('ant_lat_max', Integer),

                         # Minimum ectocranial value
                         Column('ecto_min', Integer),

                         # Maximum ectocranial value
                         Column('ecto_max', Integer),

                         # Unique constraint ensuring the combination of site and individual number is unique
                         UniqueConstraint('sito', 'nr_individuo', name='ID_det_eta_unico')
                         )



