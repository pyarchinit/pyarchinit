'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, String, Text, Float, UniqueConstraint


# Table representing sex determination data for skeletal remains
class DETSESSO_table:
    @classmethod
    def define_table(cls, metadata):
        return Table('detsesso_table', metadata,
                     # Unique identifier for each sex determination record
                     Column('id_det_sesso', Integer, primary_key=True),

                     # Archaeological site name
                     Column('sito', Text),

                     # Individual number
                     Column('num_individuo', Integer),

                     # Importance degree of glabella
                     Column('glab_grado_imp', Integer),

                     # Importance degree of mastoid process
                     Column('pmast_grado_imp', Integer),

                     # Importance degree of nuchal plane
                     Column('pnuc_grado_imp', Integer),

                     # Importance degree of zygomatic process
                     Column('pzig_grado_imp', Integer),

                     # Importance degree of supraorbital arch
                     Column('arcsop_grado_imp', Integer),

                     # Importance degree of tuberosity
                     Column('tub_grado_imp', Integer),

                     # Importance degree of occipital protuberance
                     Column('pocc_grado_imp', Integer),

                     # Importance degree of frontal inclination
                     Column('inclfr_grado_imp', Integer),

                     # Importance degree of zygomatic bone
                     Column('zig_grado_imp', Integer),

                     # Importance degree of supraorbital margin
                     Column('msorb_grado_imp', Integer),

                     # Value of glabella
                     Column('glab_valori', Integer),

                     # Value of mastoid process
                     Column('pmast_valori', Integer),

                     # Value of nuchal plane
                     Column('pnuc_valori', Integer),

                     # Value of zygomatic process
                     Column('pzig_valori', Integer),

                     # Value of supraorbital arch
                     Column('arcsop_valori', Integer),

                     # Value of tuberosity
                     Column('tub_valori', Integer),

                     # Value of occipital protuberance
                     Column('pocc_valori', Integer),

                     # Value of frontal inclination
                     Column('inclfr_valori', Integer),

                     # Value of zygomatic bone
                     Column('zig_valori', Integer),

                     # Value of supraorbital margin
                     Column('msorb_valori', Integer),

                     # Importance degree of palate
                     Column('palato_grado_imp', Integer),

                     # Importance degree of mandibular morphology
                     Column('mfmand_grado_imp', Integer),

                     # Importance degree of mental protuberance
                     Column('mento_grado_imp', Integer),

                     # Importance degree of mandibular angle
                     Column('anmand_grado_imp', Integer),

                     # Importance degree of inferior margin
                     Column('minf_grado_imp', Integer),

                     # Importance degree of mandibular branch
                     Column('brmont_grado_imp', Integer),

                     # Importance degree of mandibular condyle
                     Column('condm_grado_imp', Integer),

                     # Value of palate
                     Column('palato_valori', Integer),

                     # Value of mandibular morphology
                     Column('mfmand_valori', Integer),

                     # Value of mental protuberance
                     Column('mento_valori', Integer),

                     # Value of mandibular angle
                     Column('anmand_valori', Integer),

                     # Value of inferior margin
                     Column('minf_valori', Integer),

                     # Value of mandibular branch
                     Column('brmont_valori', Integer),

                     # Value of mandibular condyle
                     Column('condm_valori', Integer),

                     # Total cranial sex score
                     Column('sex_cr_tot', Float(2, 3)),

                     # Cranial sex indicator
                     Column('ind_cr_sex', String(100)),

                     # Superior pubis indicator I
                     Column('sup_p_I', String(1)),

                     # Superior pubis indicator II
                     Column('sup_p_II', String(1)),

                     # Superior pubis indicator III
                     Column('sup_p_III', String(1)),

                     # Superior pubis sex determination
                     Column('sup_p_sex', String(1)),

                     # Ischium indicator I
                     Column('in_isch_I', String(1)),

                     # Ischium indicator II
                     Column('in_isch_II', String(1)),

                     # Ischium indicator III
                     Column('in_isch_III', String(1)),

                     # Ischium sex determination
                     Column('in_isch_sex', String(1)),

                     # Composite arch sex determination
                     Column('arco_c_sex', String(1)),

                     # Iliac branch indicator I
                     Column('ramo_ip_I', String(1)),

                     # Iliac branch indicator II
                     Column('ramo_ip_II', String(1)),

                     # Iliac branch indicator III
                     Column('ramo_ip_III', String(1)),

                     # Iliac branch sex determination
                     Column('ramo_ip_sex', String(1)),

                     # Iliac proportions sex determination
                     Column('prop_ip_sex', String(1)),

                     # Pelvic sex indicator
                     Column('ind_bac_sex', String(100)),

                     # Unique constraint ensuring the combination of site and individual number is unique
                     UniqueConstraint('sito', 'num_individuo', name='ID_det_sesso_unico')
                     )



