'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, String, Text, Float, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class DETSESSO_table:
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    metadata = MetaData(engine)

    # define tables
    detsesso_table = Table('detsesso_table', metadata,
                           Column('id_det_sesso', Integer, primary_key=True),
                           Column('sito', Text),
                           Column('num_individuo', Integer),
                           Column('glab_grado_imp', Integer),
                           Column('pmast_grado_imp', Integer),
                           Column('pnuc_grado_imp', Integer),
                           Column('pzig_grado_imp', Integer),
                           Column('arcsop_grado_imp', Integer),
                           Column('tub_grado_imp', Integer),
                           Column('pocc_grado_imp', Integer),
                           Column('inclfr_grado_imp', Integer),
                           Column('zig_grado_imp', Integer),
                           Column('msorb_grado_imp', Integer),
                           Column('glab_valori', Integer),
                           Column('pmast_valori', Integer),
                           Column('pnuc_valori', Integer),
                           Column('pzig_valori', Integer),
                           Column('arcsop_valori', Integer),
                           Column('tub_valori', Integer),
                           Column('pocc_valori', Integer),
                           Column('inclfr_valori', Integer),
                           Column('zig_valori', Integer),
                           Column('msorb_valori', Integer),
                           Column('palato_grado_imp', Integer),
                           Column('mfmand_grado_imp', Integer),
                           Column('mento_grado_imp', Integer),
                           Column('anmand_grado_imp', Integer),
                           Column('minf_grado_imp', Integer),
                           Column('brmont_grado_imp', Integer),
                           Column('condm_grado_imp', Integer),
                           Column('palato_valori', Integer),
                           Column('mfmand_valori', Integer),
                           Column('mento_valori', Integer),
                           Column('anmand_valori', Integer),
                           Column('minf_valori', Integer),
                           Column('brmont_valori', Integer),
                           Column('condm_valori', Integer),
                           Column('sex_cr_tot', Float(2, 3)),
                           Column('ind_cr_sex', String(100)),
                           Column('sup_p_I', String(1)),
                           Column('sup_p_II', String(1)),
                           Column('sup_p_III', String(1)),
                           Column('sup_p_sex', String(1)),
                           Column('in_isch_I', String(1)),
                           Column('in_isch_II', String(1)),
                           Column('in_isch_III', String(1)),
                           Column('in_isch_sex', String(1)),
                           Column('arco_c_sex', String(1)),
                           Column('ramo_ip_I', String(1)),
                           Column('ramo_ip_II', String(1)),
                           Column('ramo_ip_III', String(1)),
                           Column('ramo_ip_sex', String(1)),
                           Column('prop_ip_sex', String(1)),
                           Column('ind_bac_sex', String(100)),

                           # explicit/composite unique constraint.  'name' is optional.
                           UniqueConstraint('sito', 'num_individuo', name='ID_det_sesso_unico')
                           )

    metadata.create_all(engine)
