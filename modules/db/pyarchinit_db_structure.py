#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
        					 stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi
    email                : mandoluca at gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from sqlalchemy import Table, Column, Integer, Date, String, Text, Float, Numeric, MetaData, ForeignKey, engine, create_engine, UniqueConstraint
from pyarchinit_conn_strings import *


class US_table:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables check per verifica fill fields 20/10/2016 OK
	us_table = Table('us_table', metadata,
	Column('id_us', Integer, primary_key=True),		#0
	Column('sito', Text),								#1
	Column('area', String(4)),							#2
	Column('us', Integer),								#3
	Column('d_stratigrafica', String(100)),				#4
	Column('d_interpretativa', String(100)),			#5
	Column('descrizione', Text),						#6
	Column('interpretazione', Text),					#7
	Column('periodo_iniziale', String(4)),				#8
	Column('fase_iniziale', String(4)),					#9
	Column('periodo_finale', String(4)),				#10
	Column('fase_finale', String(4)),					#11
	Column('scavato', String(2)),						#12
	Column('attivita', String(4)),						#13
	Column('anno_scavo', String(4)),					#14
	Column('metodo_di_scavo', String(20)),				#15
	Column('inclusi', Text),							#16
	Column('campioni', Text),							#17
	Column('rapporti', Text),							#18
	Column('data_schedatura', String(20)),				#19
	Column('schedatore', String(25)),					#20
	Column('formazione', String(20)),					#21
	Column('stato_di_conservazione', String(20)),		#22
	Column('colore', String(20)),						#23
	Column('consistenza', String(20)),					#24
	Column('struttura', String(30)),					#25
	Column('cont_per', String(200)),					#26
	Column('order_layer', Integer),						#27
	Column('documentazione', Text),						#28
	Column('unita_tipo', Text), #campi aggiunti per USM	#29
	Column('settore', Text),							#30
	Column('quad_par', Text),							#31
	Column('ambient', Text),							#32
	Column('saggio', Text),								#33
	Column('elem_datanti', Text),						#34
	Column('funz_statica', Text),						#35
	Column('lavorazione', Text),						#36
	Column('spess_giunti', Text),						#37
	Column('letti_posa', Text),							#38
	Column('alt_mod', Text),							#39
	Column('un_ed_riass', Text),						#40
	Column('reimp', Text),								#41
	Column('posa_opera', Text),							#42
	Column('quota_min_usm', Numeric(6,2)),				#43
	Column('quota_max_usm', Numeric(6,2)),				#44
	Column('cons_legante', Text),						#45
	Column('col_legante', Text),						#46
	Column('aggreg_legante', Text),						#47
	Column('con_text_mat', Text),						#48
	Column('col_materiale', Text),						#49
	Column('inclusi_materiali_usm', Text),				#50
	
	# explicit/composite unique constraint.  'name' is optional.
	UniqueConstraint('sito', 'area', 'us', name='ID_us_unico')	
	)

	metadata.create_all(engine)
	
class UT_table:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables
	ut_table = Table('ut_table', metadata,
	Column('id_ut',Integer, primary_key=True), #0
	Column('progetto', String(100)), #1
	Column('nr_ut', Integer), #2
	Column('ut_letterale', String(100)), #3
	Column('def_ut', String(100)), #4
	Column('descrizione_ut', Text), #5
	Column('interpretazione_ut', String(100)), #6
	Column('nazione', String(100)), #7
	Column('regione', String(100)), #8
	Column('provincia', String(100)), #9
	Column('comune', String(100)), #10
	Column('frazione', String(100)), #11
	Column('localita', String(100)), #12
	Column('indirizzo', String(100)), #13
	Column('nr_civico', String(100)), #14
	Column('carta_topo_igm', String(100)), #15
	Column('carta_ctr', String(100)), #16
	Column('coord_geografiche', String(100)), #17
	Column('coord_piane', String(100)), #18
	Column('quota', Float(3,2)), #19
	Column('andamento_terreno_pendenza', String(100)), #20
	Column('utilizzo_suolo_vegetazione', String(100)), #21
	Column('descrizione_empirica_suolo', Text), #22
	Column('descrizione_luogo', Text), #23
	Column('metodo_rilievo_e_ricognizione', String(100)), #24
	Column('geometria', String(100)), #25
	Column('bibliografia', Text),#26
	Column('data', String(100)), #27
	Column('ora_meteo', String(100)), #28
	Column('responsabile', String(100)), #29
	Column('dimensioni_ut', String(100)), #30
	Column('rep_per_mq', String(100)), #31
	Column('rep_datanti', String(100)), #32
	Column('periodo_I', String(100)), #33
	Column('datazione_I', String(100)), #34
	Column('interpretazione_I', String(100)), #35
	Column('periodo_II', String(100)), #36
	Column('datazione_II', String(100)), #37
	Column('interpretazione_II', String(100)), #38
	Column('documentazione', Text), #39
	Column('enti_tutela_vincoli', String(100)), #40
	Column('indagini_preliminari', String(100)), #41
	
	# explicit/composite unique constraint.  'name' is optional.
	UniqueConstraint('progetto', 'nr_ut', 'ut_letterale', name='ID_ut_unico')
	)

	metadata.create_all(engine)

class US_table_toimp:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables
	us_table_toimp = Table('us_table_toimp', metadata,
	Column('id_us', Integer, primary_key=True),
	Column('sito', Text),
	Column('area', String(4)),
	Column('us', Integer),
	Column('d_stratigrafica', String(100)),
	Column('d_interpretativa', String(100)),
	Column('descrizione', Text),
	Column('interpretazione', Text),
	Column('periodo_iniziale', String(4)),
	Column('fase_iniziale', String(4)),
	Column('periodo_finale', String(4)),
	Column('fase_finale', String(4)),
	Column('scavato', String(2)),
	Column('attivita', String(4)),
	Column('anno_scavo', String(4)),
	Column('metodo_di_scavo', String(20)),
	Column('inclusi', Text),
	Column('campioni', Text),
	Column('rapporti', Text),
	Column('data_schedatura', String(20)),
	Column('schedatore', String(25)),
	Column('formazione', String(20)),
	Column('stato_di_conservazione', String(20)),
	Column('colore', String(20)),
	Column('consistenza', String(20)),
	Column('struttura', String(30)),
	Column('cont_per', Text),
	Column('order_layer', Integer),
	Column('documentazione', Text),

	# explicit/composite unique constraint.  'name' is optional.
    UniqueConstraint('sito', 'area', 'us', name='ID_us_unico_toimp')	
	)

	metadata.create_all(engine)

class Site_table:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=True, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables
	site_table = Table('site_table', metadata,
	Column('id_sito', Integer, primary_key=True),
	Column('sito', Text),
	Column('nazione', String(100)),
	Column('regione', String(100)),
	Column('comune', String(100)),
	Column('descrizione', Text),
	Column('provincia', Text),
	Column('definizione_sito', Text),
	Column('find_check', Integer),

	# explicit/composite unique constraint.  'name' is optional.
	UniqueConstraint('sito', name='ID_sito_unico')
	)

	metadata.create_all(engine)



class Periodizzazione_table:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
	metadata = MetaData(engine)

	# define tables
	periodizzazione_table = Table('periodizzazione_table', metadata,
	Column('id_perfas', Integer, primary_key=True),
	Column('sito', Text),
	Column('periodo', Integer),
	Column('fase', Integer),
	Column('cron_iniziale', Integer),
	Column('cron_finale', Integer),
	Column('descrizione', Text),
	Column('datazione_estesa', String(300)),
	Column('cont_per', Integer),

	# explicit/composite unique constraint.  'name' is optional.
	UniqueConstraint('sito', 'periodo', 'fase', name='ID_perfas_unico')
	)

	metadata.create_all(engine)


class Inventario_materiali_table:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables
	inventario_materiali_table = Table('inventario_materiali_table', metadata,
	Column('id_invmat', Integer, primary_key=True),
	Column('sito', Text),
	Column('numero_inventario', Integer),
	Column('tipo_reperto', Text),
	Column('criterio_schedatura', Text),
	Column('definizione', Text),
	Column('descrizione', Text),
	Column('area', Integer),
	Column('us', Integer),
	Column('lavato', String(2)),
	Column('nr_cassa', Integer),
	Column('luogo_conservazione', Text),
	Column('stato_conservazione', String(20)),
	Column('datazione_reperto', String(100)),
	Column('elementi_reperto', Text),
	Column('misurazioni', Text),
	Column('rif_biblio', Text),
	Column('tecnologie', Text),
	Column('forme_minime', Integer),
	Column('forme_massime', Integer),
	Column('totale_frammenti', Integer),
	Column('corpo_ceramico', String(20)),
	Column('rivestimento', String(20)),
	Column('diametro_orlo', Numeric(7,3)),
	Column('peso', Numeric(9,3)),
	Column('tipo', String(100)),
	Column('eve_orlo', Numeric(7,3)),
	Column('repertato', String(2)),
	Column('diagnostico', String(2)),
	# explicit/composite unique constraint.  'name' is optional.
	UniqueConstraint('sito', 'numero_inventario', name='ID_invmat_unico')
	)

	metadata.create_all(engine)

class Inventario_materiali_table_toimp:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables
	inventario_materiali_table_toimp = Table('inventario_materiali_table_toimp', metadata,
	Column('id_invmat', Integer, primary_key=True),
	Column('sito', Text),
	Column('numero_inventario', Integer),
	Column('tipo_reperto', Text),
	Column('criterio_schedatura', Text),
	Column('definizione', Text),
	Column('descrizione', Text),
	Column('area', Integer),
	Column('us', Integer),
	Column('lavato', String(2)),
	Column('nr_cassa', Integer),
	Column('luogo_conservazione', Text),
	Column('stato_conservazione', String(20)),
	Column('datazione_reperto', String(30)),
	Column('elementi_reperto', Text),
	Column('misurazioni', Text),
	Column('rif_biblio', Text),
	Column('tecnologie', Text),
	Column('forme_minime', Integer),
	Column('forme_massime', Integer),
	Column('totale_frammenti', Integer),
	Column('corpo_ceramico', String(20)),
	Column('rivestimento', String(20)),

	# explicit/composite unique constraint.  'name' is optional.
    UniqueConstraint('sito', 'numero_inventario', name='ID_invmat_unico_toimp')
	)

	metadata.create_all(engine)


class Struttura_table:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
	metadata = MetaData(engine)

	# define tables
	struttura_table = Table('struttura_table', metadata,
	Column('id_struttura', Integer, primary_key=True),
	Column('sito', Text),
	Column('sigla_struttura', Text),
	Column('numero_struttura', Integer),
	Column('categoria_struttura', Text),
	Column('tipologia_struttura', Text),
	Column('definizione_struttura', Text),
	Column('descrizione', Text),
	Column('interpretazione', Text),
	Column('periodo_iniziale', Integer),
	Column('fase_iniziale', Integer),
	Column('periodo_finale', Integer),
	Column('fase_finale', Integer),
	Column('datazione_estesa', String(300)),
	Column('materiali_impiegati', Text),
	Column('elementi_strutturali', Text),
	Column('rapporti_struttura', Text),
	Column('misure_struttura', Text),

	# explicit/composite unique constraint.  'name' is optional.
    UniqueConstraint('sito', 'sigla_struttura', 'numero_struttura', name='ID_struttura_unico')
	)

	metadata.create_all(engine)
	
class Media_table:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables
	media_table = Table('media_table', metadata,
	Column('id_media', Integer, primary_key=True),
	Column('mediatype', Text),
	Column('filename', Text),
	Column('filetype', String(10)),
	Column('filepath', Text),
	Column('descrizione', Text),
	Column('tags', Text),

	# explicit/composite unique constraint.  'name' is optional.
    UniqueConstraint('filepath', name='ID_media_unico')
	)

	metadata.create_all(engine)

class Media_thumb_table:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables
	media_thumb_table = Table('media_thumb_table', metadata,
	Column('id_media_thumb', Integer, primary_key=True),
	Column('id_media', Integer),
	Column('mediatype', Text),
	Column('media_filename', Text),
	Column('media_thumb_filename', Text),
	Column('filetype', String(10)),
	Column('filepath', Text),

	# explicit/composite unique constraint.  'name' is optional.
    UniqueConstraint('media_thumb_filename', name='ID_media_thumb_unico')
	)

	metadata.create_all(engine)

class Media_to_Entity_table:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables
	media_to_entity_table = Table('media_to_entity_table', metadata,
	Column('id_mediaToEntity', Integer, primary_key=True),
	Column('id_entity', Integer),
	Column('entity_type', Text),
	Column('table_name', Text),
	Column('id_media', Integer),
	Column('filepath', Text),
	Column('media_name', Text),

	# explicit/composite unique constraint.  'name' is optional.
    UniqueConstraint('id_entity','entity_type','id_media', name='ID_mediaToEntity_unico')
	)

	metadata.create_all(engine)
	

class Tafonomia_table:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables
	tafonomia_table = Table('tafonomia_table', metadata,
	Column('id_tafonomia', Integer, primary_key=True),
	Column('sito', Text),
	Column('nr_scheda_taf', Integer),
	Column('sigla_struttura', Text),
	Column('nr_struttura', Integer),
	Column('nr_individuo', Integer),
	Column('rito', Text),
	Column('descrizione_taf', Text),
	Column('interpretazione_taf', Text),
	Column('segnacoli', Text),
	Column('canale_libatorio_si_no',Text),
	Column('oggetti_rinvenuti_esterno', Text),
	Column('stato_di_conservazione', Text),
	Column('copertura_tipo', Text),
	Column('tipo_contenitore_resti', Text),
	Column('orientamento_asse', Text),
	Column('orientamento_azimut', Float(2,2)),
	Column('riferimenti_stratigrafici', Text),
	Column('corredo_presenza', Text),
	Column('corredo_tipo', Text),
	Column('corredo_descrizione', Text),
	Column('lunghezza_scheletro', Float(2,2)),
	Column('posizione_scheletro', String(50)),
	Column('posizione_cranio', String(50)),
	Column('posizione_arti_superiori', String(50)),
	Column('posizione_arti_inferiori', String(50)),
	Column('completo_si_no', String(2)),
	Column('disturbato_si_no',  String(2)),
	Column('in_connessione_si_no',  String(2)),	
	Column('caratteristiche', Text),
	Column('periodo_iniziale', Integer),
	Column('fase_iniziale', Integer),
	Column('periodo_finale', Integer),
	Column('fase_finale', Integer),
	Column('datazione_estesa', String(300)),
	Column('misure_tafonomia', Text),

	# explicit/composite unique constraint.  'name' is optional.
    UniqueConstraint('sito','nr_scheda_taf', name='ID_tafonomia_unico')
	)

	metadata.create_all(engine)

class Pyarchinit_thesaurus_sigle:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables
	pyarchinit_thesaurus_sigle = Table('pyarchinit_thesaurus_sigle', metadata,
	Column('id_thesaurus_sigle', Integer, primary_key=True),
	Column('nome_tabella', Text),
	Column('sigla', String(3)),
	Column('sigla_estesa', Text),
	Column('descrizione', Text),
	Column('tipologia_sigla', Text),

	# explicit/composite unique constraint.  'name' is optional.
	UniqueConstraint('id_thesaurus_sigle', name='id_thesaurus_sigle_pk')
	)

	metadata.create_all(engine)

class SCHEDAIND_table:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables
	individui_table = Table('individui_table', metadata,
	Column('id_scheda_ind', Integer, primary_key=True),
	Column('sito', Text),
	Column('area', String(4)),
	Column('us', Integer),
	Column('nr_individuo', Integer),
	Column('data_schedatura', String(100)),
	Column('schedatore', String(100)),
	Column('sesso', String(100)),
	Column('eta_min', Integer),
	Column('eta_max', Integer),
	Column('classi_eta', String(100)),
	Column('osservazioni', Text),

	# explicit/composite unique constraint.  'name' is optional.
	UniqueConstraint('sito', 'nr_individuo', name='ID_individuo_unico')
	)

	metadata.create_all(engine)

class DETSESSO_table:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
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
	Column('tub_grado_imp',Integer),
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
	Column('sex_cr_tot', Float(2,3)),
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

class DETETA_table:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables
	deteta_table = Table('deteta_table', metadata,
	Column('id_det_eta', Integer, primary_key=True),
	Column('sito', Text),
	Column('nr_individuo', Integer),
	Column('sinf_min',Integer),
	Column('sinf_max',Integer),
	Column('sinf_min_2',Integer),
	Column('sinf_max_2',Integer),
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


class Archeozoology_table:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables
	archeozoology_table = Table('archeozoology_table', metadata,
	Column('id_archzoo', Integer, primary_key=True),
	Column('sito', Text),
	Column('area', Text),
	Column('us', Integer),
	Column('quadrato', Text),
	Column('coord_x', Numeric(12,6)),
	Column('coord_y', Numeric(12,6)),
	Column('coord_z', Numeric(12,6)),
	Column('bos_bison', Integer),
	Column('calcinati', Integer),
	Column('camoscio', Integer),
	Column('capriolo', Integer),
	Column('cervo', Integer),
	Column('combusto', Integer),
	Column('coni', Integer),
	Column('pdi', Integer),
	Column('stambecco', Integer),
	Column('strie', Integer),
	Column('canidi', Integer),
	Column('ursidi', Integer),
	Column('megacero', Integer),

	# explicit/composite unique constraint.  'name' is optional.
	UniqueConstraint('sito', 'quadrato', name='ID_archzoo_unico')
	)

	metadata.create_all(engine)
	
##############################	

class Inventario_Lapidei_table:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables
	inventario_lapidei_table = Table('inventario_lapidei_table', metadata,
	Column('id_invlap', Integer, primary_key=True),
	Column('sito', Text),
	Column('scheda_numero', Integer),
	Column('collocazione', Text),
	Column('oggetto', Text),
	Column('tipologia', Text),
	Column('materiale', Text),
	Column('d_letto_posa', Numeric(4,2)),
	Column('d_letto_attesa', Numeric(4,2)),
	Column('toro', Numeric(4,2)),
	Column('spessore', Numeric(4,2)),
	Column('larghezza', Numeric(4,2)),
	Column('lunghezza', Numeric(4,2)),
	Column('h', Numeric(4,2)),
	Column('descrizione', Text),
	Column('lavorazione_e_stato_di_conservazione', Text),
	Column('confronti', Text),
	Column('cronologia', Text),
	Column('bibliografia', Text),
	Column('compilatore', Text),
	# explicit/composite unique constraint.  'name' is optional.
	UniqueConstraint('sito', 'scheda_numero', name='ID_invlap_unico')
	)

	metadata.create_all(engine)
##############################	


class PDF_administrator:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables
	pdf_administrator_table = Table('pdf_administrator_table', metadata,
	Column('id_pdf_administrator', Integer, primary_key=True),
	Column('table_name', Text),
	Column('schema_griglia', Text),
	Column('schema_fusione_celle', Text),
	Column('modello', Text),

	# explicit/composite unique constraint.  'name' is optional.
    UniqueConstraint('table_name','modello', name='ID_pdf_administrator_unico')
	)

	metadata.create_all(engine)
	
class Campioni_table:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=True, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables
	campioni_table = Table('campioni_table', metadata,
	Column('id_campione', Integer, primary_key=True),
	Column('sito', Text),
	Column('nr_campione', Integer),
	Column('tipo_campione', Text),
	Column('descrizione', Text),
	Column('area', String(4)),
	Column('us', Integer),
	Column('numero_inventario_materiale', Integer),
	Column('nr_cassa', Integer),
	Column('luogo_conservazione', Text),

	# explicit/composite unique constraint.  'name' is optional.
	UniqueConstraint('sito', 'nr_campione', name='ID_invcamp_unico')
	)

	metadata.create_all(engine)


class Documentazione_table:
	# connection string postgres"
	internal_connection = Connection()

	# create engine and metadata

	engine = create_engine(internal_connection.conn_str(), echo=True, convert_unicode = True)
	metadata = MetaData(engine)

	# define tables
	documentazione_table = Table('documentazione_table', metadata,
	Column('id_documentazione', Integer, primary_key=True),
	Column('sito', Text),
	Column('nome_doc', Text),
	Column('data', Text),
	Column('tipo_documentazione', Text),
	Column('sorgente', Text),
	Column('scala', Text),
	Column('disegnatore', Text),
	Column('note', Text),

	# explicit/composite unique constraint.  'name' is optional.
	UniqueConstraint('sito', 'tipo_documentazione', 'nome_doc', name='ID_invdoc_unico')
	)

	metadata.create_all(engine)
