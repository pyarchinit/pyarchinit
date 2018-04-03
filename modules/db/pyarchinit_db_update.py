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
from msilib import Table
from sqlalchemy.engine import create_engine
from sqlalchemy.sql.schema import MetaData

from modules.db.pyarchinit_conn_strings import Connection


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

        if not table_column_names_list.__contains__('provincia'):
            self.engine.execute("ALTER TABLE site_table ADD COLUMN provincia varchar DEFAULT 'inserici un valore' ")

        if not table_column_names_list.__contains__('definizione_sito'):
            self.engine.execute(
                "ALTER TABLE site_table ADD COLUMN definizione_sito varchar DEFAULT 'inserici un valore' ")

        if not table_column_names_list.__contains__('find_check'):
            self.engine.execute("ALTER TABLE site_table ADD COLUMN find_check INTEGER DEFAULT 0")

        ####US_table
        table = Table("us_table", self.metadata, autoload=True)
        table_column_names_list = []

        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('cont_per'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN cont_per varchar DEFAULT")

        if not table_column_names_list.__contains__('documentazione'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN documentazione varchar")

            # nuovi campi per USM 1/9/2016 generati correttamente
        if not table_column_names_list.__contains__('unita_tipo'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN unita_tipo varchar DEFAULT 'US' ")

        if not table_column_names_list.__contains__('settore'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN settore text DEFAULT '' ")

        if not table_column_names_list.__contains__('quad_par'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN quad_par text DEFAULT '' ")

        if not table_column_names_list.__contains__('ambient'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN ambient text DEFAULT '' ")

        if not table_column_names_list.__contains__('saggio'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN saggio text DEFAULT '' ")

        if not table_column_names_list.__contains__('elem_datanti'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN elem_datanti text DEFAULT '' ")

        if not table_column_names_list.__contains__('funz_statica'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN funz_statica text DEFAULT '' ")

        if not table_column_names_list.__contains__('lavorazione'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN lavorazione text DEFAULT '' ")

        if not table_column_names_list.__contains__('spess_giunti'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN spess_giunti text DEFAULT '' ")

        if not table_column_names_list.__contains__('letti_posa'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN letti_posa text DEFAULT '' ")

        if not table_column_names_list.__contains__('alt_mod'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN alt_mod text DEFAULT '' ")

        if not table_column_names_list.__contains__('un_ed_riass'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN un_ed_riass text DEFAULT '' ")

        if not table_column_names_list.__contains__('reimp'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN reimp text DEFAULT '' ")

        if not table_column_names_list.__contains__('posa_opera'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN posa_opera text DEFAULT '' ")

        if not table_column_names_list.__contains__('quota_min_usm'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN quota_min_usm NUMERIC(6,2)")

        if not table_column_names_list.__contains__('quota_max_usm'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN quota_max_usm NUMERIC(6,2)")

        if not table_column_names_list.__contains__('cons_legante'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN cons_legante text DEFAULT '' ")

        if not table_column_names_list.__contains__('col_legante'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN col_legante text DEFAULT '' ")

        if not table_column_names_list.__contains__('aggreg_legante'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN aggreg_legante text DEFAULT '' ")

        if not table_column_names_list.__contains__('con_text_mat'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN con_text_mat text DEFAULT '' ")

        if not table_column_names_list.__contains__('col_materiale'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN col_materiale text DEFAULT '' ")

        if not table_column_names_list.__contains__('inclusi_materiali_usm'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN inclusi_materiali_usm text DEFAULT '[]' ")

        ####periodizzazione_table
        table = Table("periodizzazione_table", self.metadata, autoload=True)
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('cont_per'):
            self.engine.execute("ALTER TABLE periodizzazione_table ADD COLUMN cont_per integer DEFAULT 0 ")

        ####inventario_materiali_table
        table = Table("inventario_materiali_table", self.metadata, autoload=True)
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('stato_conservazione'):
            self.engine.execute(
                "ALTER TABLE inventario_materiali_table ADD COLUMN stato_conservazione varchar DEFAULT ''")

        if not table_column_names_list.__contains__('datazione_reperto'):
            self.engine.execute(
                "ALTER TABLE inventario_materiali_table ADD COLUMN datazione_reperto varchar(30) DEFAULT 'inserisci un valore'")

        if not table_column_names_list.__contains__('elementi_reperto'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN elementi_reperto text")

        if not table_column_names_list.__contains__('misurazioni'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN misurazioni text")

        if not table_column_names_list.__contains__('rif_biblio'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN rif_biblio text")

        if not table_column_names_list.__contains__('tecnologie'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN tecnologie text")

        if not table_column_names_list.__contains__('forme_minime'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN forme_minime integer DEFAULT 0")

        if not table_column_names_list.__contains__('forme_massime'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN forme_massime integer DEFAULT 0")

        if not table_column_names_list.__contains__('totale_frammenti'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN totale_frammenti integer DEFAULT 0")

        if not table_column_names_list.__contains__('corpo_ceramico'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN corpo_ceramico varchar(20)")
            self.engine.execute("update inventario_materiali_table set corpo_ceramico = ''")

        if not table_column_names_list.__contains__('rivestimento'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN rivestimento varchar(20)")
            self.engine.execute("update inventario_materiali_table set rivestimento = ''")

        if not table_column_names_list.__contains__('diametro_orlo'):
            self.engine.execute(
                "ALTER TABLE inventario_materiali_table ADD COLUMN diametro_orlo Numeric(7,3) DEFAULT 0")

        if not table_column_names_list.__contains__('peso'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN peso Numeric(9,3) DEFAULT 0")

        if not table_column_names_list.__contains__('tipo'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN tipo varchar(20)")
            self.engine.execute("update inventario_materiali_table set tipo = ''")

        if not table_column_names_list.__contains__('eve_orlo'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN eve_orlo Numeric(7,3) DEFAULT 0")

        if not table_column_names_list.__contains__('repertato'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN repertato varchar(2)")
            self.engine.execute("update inventario_materiali_table set repertato = ''No")

        if not table_column_names_list.__contains__('diagnostico'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN diagnostico varchar(2)")
            self.engine.execute("update inventario_materiali_table set diagnostico = ''No")

        ####tafonomia_table
        table = Table("tafonomia_table", self.metadata, autoload=True)
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('periodo_iniziale'):
            self.engine.execute("ALTER TABLE tafonomia_table ADD COLUMN periodo_iniziale integer")

        if not table_column_names_list.__contains__('fase_iniziale'):
            self.engine.execute("ALTER TABLE tafonomia_table ADD COLUMN fase_iniziale integer")

        if not table_column_names_list.__contains__('periodo_finale'):
            self.engine.execute("ALTER TABLE tafonomia_table ADD COLUMN periodo_finale integer")

        if not table_column_names_list.__contains__('fase_finale'):
            self.engine.execute("ALTER TABLE tafonomia_table ADD COLUMN fase_finale integer")

        if not table_column_names_list.__contains__('datazione_estesa'):
            self.engine.execute("ALTER TABLE tafonomia_table ADD COLUMN datazione_estesa text")

        if not table_column_names_list.__contains__('misure_tafonomia'):
            self.engine.execute("ALTER TABLE tafonomia_table ADD COLUMN misure_tafonomia text DEFAULT '[]' ")

        ####aggiornamento tabelle geografiche
        try:
            self.engine.execute("ALTER TABLE pyarchinit_strutture_ipotesi ADD COLUMN nr_strut integer DEFAULT 0 ")
            self.engine.execute(
                "ALTER TABLE pyarchinit_strutture_ipotesi ADD COLUMN sigla_strut varchar(3) DEFAULT 'NoD'")
        except:
            pass
            # verificare se aggiorna le tabelle con i campi nuovi


if __name__ == '__main__':
    dbup = DB_update()
    dbup.update_table()
