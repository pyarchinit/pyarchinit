'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, Text, MetaData, create_engine, UniqueConstraint

from modules.db.pyarchinit_conn_strings import Connection


class DETETA_table:
    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    metadata = MetaData(engine)

    # define tables
    deteta_table = Table('deteta_table', metadata,
                         Column('id_det_eta', Integer, primary_key=True),
                         Column('sito', Text),
                         Column('nr_individuo', Integer),
                         Column('sinf_min', Integer),
                         Column('sinf_max', Integer),
                         Column('sinf_min_2', Integer),
                         Column('sinf_max_2', Integer),
                         Column('SSPIA', Integer),
                         Column('SSPIB', Integer),
                         Column('SSPIC', Integer),
                         Column('SSPID', Integer),
                         Column('sup_aur_min', Integer),
                         Column('sup_aur_max', Integer),
                         Column('sup_aur_min_2', Integer),
                         Column('sup_aur_max_2', Integer),
                         Column('ms_sup_min', Integer),
                         Column('ms_sup_max', Integer),
                         Column('ms_inf_min', Integer),
                         Column('ms_inf_max', Integer),
                         Column('usura_min', Integer),
                         Column('usura_max', Integer),
                         Column('Id_endo', Integer),
                         Column('Is_endo', Integer),
                         Column('IId_endo', Integer),
                         Column('IIs_endo', Integer),
                         Column('IIId_endo', Integer),
                         Column('IIIs_endo', Integer),
                         Column('IV_endo', Integer),
                         Column('V_endo', Integer),
                         Column('VI_endo', Integer),
                         Column('VII_endo', Integer),
                         Column('VIIId_endo', Integer),
                         Column('VIIIs_endo', Integer),
                         Column('IXd_endo', Integer),
                         Column('IXs_endo', Integer),
                         Column('Xd_endo', Integer),
                         Column('Xs_endo', Integer),
                         Column('endo_min', Integer),
                         Column('endo_max', Integer),
                         Column('volta_1', Integer),
                         Column('volta_2', Integer),
                         Column('volta_3', Integer),
                         Column('volta_4', Integer),
                         Column('volta_5', Integer),
                         Column('volta_6', Integer),
                         Column('volta_7', Integer),
                         Column('lat_6', Integer),
                         Column('lat_7', Integer),
                         Column('lat_8', Integer),
                         Column('lat_9', Integer),
                         Column('lat_10', Integer),
                         Column('volta_min', Integer),
                         Column('volta_max', Integer),
                         Column('ant_lat_min', Integer),
                         Column('ant_lat_max', Integer),
                         Column('ecto_min', Integer),
                         Column('ecto_max', Integer),
                         # explicit/composite unique constraint.  'name' is optional.
                         UniqueConstraint('sito', 'nr_individuo', name='ID_det_eta_unico')
                         )

    metadata.create_all(engine)
