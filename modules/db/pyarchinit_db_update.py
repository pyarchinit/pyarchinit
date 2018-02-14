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
from sqlalchemy import *
from pyarchinit_conn_strings import *

class DB_update:

	# connection string postgres"

	# create engine and metadata
	internal_connection = Connection()
	engine = create_engine(internal_connection.conn_str(), echo=False)
	metadata = MetaData(engine)

	def update_table(self):
		####site_table
		table = Table("site_table", self.metadata, autoload=True)
		table_column_names_list = []
		for i in table.columns:
			table_column_names_list.append(str(i.name))

		if table_column_names_list.__contains__('provincia') == False:
			self.engine.execute("ALTER TABLE site_table ADD COLUMN provincia varchar DEFAULT 'inserici un valore' ")


		if table_column_names_list.__contains__('definizione_sito') == False:
			self.engine.execute("ALTER TABLE site_table ADD COLUMN definizione_sito varchar DEFAULT 'inserici un valore' ")


		if table_column_names_list.__contains__('find_check') == False:
			self.engine.execute("ALTER TABLE site_table ADD COLUMN find_check INTEGER DEFAULT 0")

		####US_table
		table = Table("us_table", self.metadata, autoload=True)
		table_column_names_list = []

		for i in table.columns:
			table_column_names_list.append(str(i.name))

		if table_column_names_list.__contains__('cont_per') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN cont_per varchar DEFAULT")

		if table_column_names_list.__contains__('documentazione') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN documentazione varchar")
		
		#nuovi campi per USM 1/9/2016 generati correttamente
		if table_column_names_list.__contains__('unita_tipo') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN unita_tipo varchar DEFAULT 'US' ")

		if table_column_names_list.__contains__('settore') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN settore text DEFAULT '' ")

		if table_column_names_list.__contains__('quad_par') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN quad_par text DEFAULT '' ")

		if table_column_names_list.__contains__('ambient') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN ambient text DEFAULT '' ")

		if table_column_names_list.__contains__('saggio') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN saggio text DEFAULT '' ")

		if table_column_names_list.__contains__('elem_datanti') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN elem_datanti text DEFAULT '' ")

		if table_column_names_list.__contains__('funz_statica') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN funz_statica text DEFAULT '' ")

		if table_column_names_list.__contains__('lavorazione') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN lavorazione text DEFAULT '' ")

		if table_column_names_list.__contains__('spess_giunti') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN spess_giunti text DEFAULT '' ")

		if table_column_names_list.__contains__('letti_posa') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN letti_posa text DEFAULT '' ")

		if table_column_names_list.__contains__('alt_mod') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN alt_mod text DEFAULT '' ")
		
		if table_column_names_list.__contains__('un_ed_riass') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN un_ed_riass text DEFAULT '' ")

		if table_column_names_list.__contains__('reimp') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN reimp text DEFAULT '' ")


		if table_column_names_list.__contains__('posa_opera') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN posa_opera text DEFAULT '' ")

		if table_column_names_list.__contains__('quota_min_usm') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN quota_min_usm NUMERIC(6,2)")


		if table_column_names_list.__contains__('quota_max_usm') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN quota_max_usm NUMERIC(6,2)")


		if table_column_names_list.__contains__('cons_legante') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN cons_legante text DEFAULT '' ")

		if table_column_names_list.__contains__('col_legante') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN col_legante text DEFAULT '' ")


		if table_column_names_list.__contains__('aggreg_legante') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN aggreg_legante text DEFAULT '' ")


		if table_column_names_list.__contains__('con_text_mat') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN con_text_mat text DEFAULT '' ")


		if table_column_names_list.__contains__('col_materiale') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN col_materiale text DEFAULT '' ")

		if table_column_names_list.__contains__('inclusi_materiali_usm') == False:
			self.engine.execute("ALTER TABLE us_table ADD COLUMN inclusi_materiali_usm text DEFAULT '[]' ")

		####periodizzazione_table
		table = Table("periodizzazione_table", self.metadata, autoload=True)
		table_column_names_list = []
		for i in table.columns:
			table_column_names_list.append(str(i.name))

		if table_column_names_list.__contains__('cont_per') == False:
			self.engine.execute("ALTER TABLE periodizzazione_table ADD COLUMN cont_per integer DEFAULT 0 ")
		
		####inventario_materiali_table
		table = Table("inventario_materiali_table", self.metadata, autoload=True)
		table_column_names_list = []
		for i in table.columns:
			table_column_names_list.append(str(i.name))

		if table_column_names_list.__contains__('stato_conservazione') == False:
			self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN stato_conservazione varchar DEFAULT ''")

		if table_column_names_list.__contains__('datazione_reperto') == False:
			self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN datazione_reperto varchar(30) DEFAULT 'inserisci un valore'")

		if table_column_names_list.__contains__('elementi_reperto') == False:
			self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN elementi_reperto text")

		if table_column_names_list.__contains__('misurazioni') == False:
			self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN misurazioni text")

		if table_column_names_list.__contains__('rif_biblio') == False:
			self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN rif_biblio text")

		if table_column_names_list.__contains__('tecnologie') == False:
			self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN tecnologie text")
		
		if table_column_names_list.__contains__('forme_minime') == False:
			self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN forme_minime integer DEFAULT 0")
		
		if table_column_names_list.__contains__('forme_massime') == False:
			self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN forme_massime integer DEFAULT 0")
		
		if table_column_names_list.__contains__('totale_frammenti') == False:
			self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN totale_frammenti integer DEFAULT 0")

		if table_column_names_list.__contains__('corpo_ceramico') == False:
			self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN corpo_ceramico varchar(20)")
			self.engine.execute("update inventario_materiali_table set corpo_ceramico = ''")
		
		if table_column_names_list.__contains__('rivestimento') == False:
			self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN rivestimento varchar(20)")
			self.engine.execute("update inventario_materiali_table set rivestimento = ''")
		
		if table_column_names_list.__contains__('diametro_orlo') == False:
			self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN diametro_orlo Numeric(7,3) DEFAULT 0")

		if table_column_names_list.__contains__('peso') == False:
			self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN peso Numeric(9,3) DEFAULT 0")

		if table_column_names_list.__contains__('tipo') == False:
			self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN tipo varchar(20)")
			self.engine.execute("update inventario_materiali_table set tipo = ''")

		if table_column_names_list.__contains__('eve_orlo') == False:
			self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN eve_orlo Numeric(7,3) DEFAULT 0")
			
		if table_column_names_list.__contains__('repertato') == False:
			self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN repertato varchar(2)")
			self.engine.execute("update inventario_materiali_table set repertato = ''No")

		if table_column_names_list.__contains__('diagnostico') == False:
			self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN diagnostico varchar(2)")
			self.engine.execute("update inventario_materiali_table set diagnostico = ''No")

		####tafonomia_table
		table = Table("tafonomia_table", self.metadata, autoload=True)
		table_column_names_list = []
		for i in table.columns:
			table_column_names_list.append(str(i.name))

		if table_column_names_list.__contains__('periodo_iniziale') == False:
			self.engine.execute("ALTER TABLE tafonomia_table ADD COLUMN periodo_iniziale integer")

		if table_column_names_list.__contains__('fase_iniziale') == False:
			self.engine.execute("ALTER TABLE tafonomia_table ADD COLUMN fase_iniziale integer")

		if table_column_names_list.__contains__('periodo_finale') == False:
			self.engine.execute("ALTER TABLE tafonomia_table ADD COLUMN periodo_finale integer")

		if table_column_names_list.__contains__('fase_finale') == False:
			self.engine.execute("ALTER TABLE tafonomia_table ADD COLUMN fase_finale integer")

		if table_column_names_list.__contains__('datazione_estesa') == False:
			self.engine.execute("ALTER TABLE tafonomia_table ADD COLUMN datazione_estesa text")

		if table_column_names_list.__contains__('misure_tafonomia') == False:
			self.engine.execute("ALTER TABLE tafonomia_table ADD COLUMN misure_tafonomia text DEFAULT '[]' ")

		####aggiornamento tabelle geografiche
		try:
			self.engine.execute("ALTER TABLE pyarchinit_strutture_ipotesi ADD COLUMN nr_strut integer DEFAULT 0 ")
			self.engine.execute("ALTER TABLE pyarchinit_strutture_ipotesi ADD COLUMN sigla_strut varchar(3) DEFAULT 'NoD'")
		except:
			pass
			#verificare se aggiorna le tabelle con i campi nuovi



if __name__ == '__main__':
	dbup=DB_update()
	dbup.update_table()