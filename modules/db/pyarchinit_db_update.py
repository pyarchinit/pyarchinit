# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
        					 stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi; Enzo Cocca <enzo.ccc@gmail.com>
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
from builtins import object
from builtins import str
from sqlalchemy import Table
from sqlalchemy.engine import create_engine
from sqlalchemy.sql.schema import MetaData

from modules.db.pyarchinit_conn_strings import Connection


class DB_update(object):
    # connection string postgres"
    def __init__(self, conn_str):
        # create engine and metadata


        self.engine = create_engine(conn_str, echo=True)
        self.metadata = MetaData(self.engine)

    def update_table(self):
        ''' convert column name from italian to english. In order from table to vector '''
        ####archeozoology_table
        table = Table("archeozoology_table", self.metadata, autoload=True)
        table_column_names_list = []

        for i in table.columns:
            table_column_names_list.append(str(i.name))
        if not table_column_names_list.__contains__('site'):
            self.engine.execute(
                "ALTER TABLE archeozoology_table RENAME COLUMN sito TO site")

        if not table_column_names_list.__contains__('su'):
            self.engine.execute(
                "ALTER TABLE archeozoology_table RENAME COLUMN us TO su")

        if not table_column_names_list.__contains__('square'):
            self.engine.execute(
                "ALTER TABLE archeozoology_table RENAME COLUMN quadrato TO square")



        ####site_table
        table = Table("site_table", self.metadata, autoload=True)
        table_column_names_list = []

        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('site'):
            self.engine.execute(
                "ALTER TABLE site_table RENAME COLUMN sito TO site")

        if not table_column_names_list.__contains__('nation'):
            self.engine.execute(
                "ALTER TABLE site_table RENAME COLUMN nazione TO nation")

        if not table_column_names_list.__contains__('region'):
            self.engine.execute(
                "ALTER TABLE site_table RENAME COLUMN regione TO region")

        if not table_column_names_list.__contains__('municipality'):
            self.engine.execute(
                "ALTER TABLE site_table RENAME COLUMN comune TO municipality")

        if not table_column_names_list.__contains__('description'):
            self.engine.execute(
                "ALTER TABLE site_table RENAME COLUMN descrizione TO description")

        if not table_column_names_list.__contains__('province'):
            self.engine.execute(
                "ALTER TABLE site_table RENAME COLUMN provincia TO province")

        if not table_column_names_list.__contains__('site_type'):
            self.engine.execute(
                "ALTER TABLE site_table RENAME COLUMN definizione_sito TO site_type")

        if not table_column_names_list.__contains__('site_path'):
            self.engine.execute(
                "ALTER TABLE site_table RENAME COLUMN sito_path TO site_path")


        ####invetario_materiali_table
        table = Table("inventario_materiali_table", self.metadata, autoload=True)
        table_column_names_list = []
        
        for i in table.columns:
            table_column_names_list.append(str(i.name))
        if not table_column_names_list.__contains__('conservation_status'):
            self.engine.execute(
                "ALTER TABLE inventario_materiali_table RENAME COLUMN stato_conservazione To conservation_status")

        if not table_column_names_list.__contains__('dating_artifact'):
            self.engine.execute(
                "ALTER TABLE inventario_materiali_table RENAME COLUMN datazione_reperto TO dating_artifact")

        if not table_column_names_list.__contains__('artifact_items'):
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN elementi_reperto TO artifact_items")

        if not table_column_names_list.__contains__('measurements'):
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN misurazioni TO measurements")

        if not table_column_names_list.__contains__('bibliography'):
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN rif_biblio TO bibliography")

        if not table_column_names_list.__contains__('technologies'):
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN tecnologie TO technologies")

        if not table_column_names_list.__contains__('min_shape'):
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN forme_minime TO min_shape")

        if not table_column_names_list.__contains__('max_shape'):
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN forme_massime TO max_shape")

        if not table_column_names_list.__contains__('total_fragments'):
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN totale_frammenti TO total_fragments")

        if not table_column_names_list.__contains__('pottery_body'):
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN corpo_ceramico pottery_body")

        if not table_column_names_list.__contains__('fabric'):
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN rivestimento TO fabric")

        if not table_column_names_list.__contains__('diameter_hem'):
            self.engine.execute(
                "ALTER TABLE inventario_materiali_table RENAME COLUMN diametro_orlo TO diameter_hem")

        if not table_column_names_list.__contains__('weight'):
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN peso TO weight")

        if not table_column_names_list.__contains__('type'):
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN tipo TO type")

        if not table_column_names_list.__contains__('eve_hem'):
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN eve_orlo To eve_hem")

        if not table_column_names_list.__contains__('retrieved'):
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN repertato TO retrieved")

        if not table_column_names_list.__contains__('diagnostic'):
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN diagnostico To diagnostic")

        if not table_column_names_list.__contains__('number_find'):
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN n_reperto TO number_find")

        if not table_column_names_list.__contains__('container_type'):
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN tipo_contenitore TO container_type")

        if not table_column_names_list.__contains__('structure'):
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN struttura TO structure")
         
        

        ####US_table
        table = Table("us_table", self.metadata, autoload=True)
        table_column_names_list = []

        for i in table.columns:
            table_column_names_list.append(str(i.name))
        
        
        if not table_column_names_list.__contains__('cont_per'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN cont_per varchar DEFAULT")

        if not table_column_names_list.__contains__('documentazione'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN documentazione varchar")

            # nuovi campi per USM 1/9/2016 generati correttamente
        if not table_column_names_list.__contains__('unita_tipo'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN unita_tipo varchar DEFAULT 'US' ")

        if not table_column_names_list.__contains__('settore'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN settore text DEFAULT '' ")

        if not table_column_names_list.__contains__('quad_par'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN quad_par text DEFAULT '' ")

        if not table_column_names_list.__contains__('ambient'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN ambient text DEFAULT '' ")

        if not table_column_names_list.__contains__('saggio'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN saggio text DEFAULT '' ")

        if not table_column_names_list.__contains__('elem_datanti'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN elem_datanti text DEFAULT '' ")

        if not table_column_names_list.__contains__('funz_statica'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN funz_statica text DEFAULT '' ")

        if not table_column_names_list.__contains__('lavorazione'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN lavorazione text DEFAULT '' ")

        if not table_column_names_list.__contains__('spess_giunti'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN spess_giunti text DEFAULT '' ")

        if not table_column_names_list.__contains__('letti_posa'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN letti_posa text DEFAULT '' ")

        if not table_column_names_list.__contains__('alt_mod'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN alt_mod text DEFAULT '' ")

        if not table_column_names_list.__contains__('un_ed_riass'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN un_ed_riass text DEFAULT '' ")

        if not table_column_names_list.__contains__('reimp'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN reimp text DEFAULT '' ")

        if not table_column_names_list.__contains__('posa_opera'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN posa_opera text DEFAULT '' ")

        if not table_column_names_list.__contains__('quota_min_usm'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN quota_min_usm NUMERIC(6,2)")

        if not table_column_names_list.__contains__('quota_max_usm'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN quota_max_usm NUMERIC(6,2)")

        if not table_column_names_list.__contains__('cons_legante'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN cons_legante text DEFAULT '' ")

        if not table_column_names_list.__contains__('col_legante'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN col_legante text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('aggreg_legante'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN aggreg_legante text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('con_text_mat'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN con_text_mat text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('col_materiale'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN col_materiale text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('inclusi_materiali_usm'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN inclusi_materiali_usm text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('n_catalogo_generale'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN n_catalogo_generale text DEFAULT '' ")

        if not table_column_names_list.__contains__('n_catalogo_interno'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN n_catalogo_interno text DEFAULT '' ")

        if not table_column_names_list.__contains__('n_catalogo_internazionale'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN n_catalogo_internazionale text DEFAULT '' ")

        if not table_column_names_list.__contains__('soprintendenza'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN soprintendenza text DEFAULT '' ")

        if not table_column_names_list.__contains__('quota_relativa'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN quota_relativa NUMERIC(6,2)")

        if not table_column_names_list.__contains__('quota_abs'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN quota_abs   NUMERIC(6,2)")

        if not table_column_names_list.__contains__('ref_tm'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN ref_tm text DEFAULT '' ")

        if not table_column_names_list.__contains__('ref_ra'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN ref_ra text DEFAULT '' ")

        if not table_column_names_list.__contains__('ref_n'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN ref_n text DEFAULT '' ")

        if not table_column_names_list.__contains__('posizione'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN posizione text DEFAULT '' ")

        if not table_column_names_list.__contains__('criteri_distinzione'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN criteri_distinzione text DEFAULT '' ")

        if not table_column_names_list.__contains__('modo_formazione'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN modo_formazione text DEFAULT '' ")

        if not table_column_names_list.__contains__('componenti_organici'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN componenti_organici text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('componenti_inorganici'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN componenti_inorganici text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('lunghezza_max'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN lunghezza_max NUMERIC(6,2)")

        if not table_column_names_list.__contains__('altezza_max'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN altezza_max NUMERIC(6,2)")

        if not table_column_names_list.__contains__('altezza_min'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN altezza_min NUMERIC(6,2)")

        if not table_column_names_list.__contains__('profondita_max'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN profondita_max NUMERIC(6,2)")

        if not table_column_names_list.__contains__('profondita_min'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN profondita_min NUMERIC(6,2)")

        if not table_column_names_list.__contains__('larghezza_media'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN larghezza_media NUMERIC(6,2)")

        if not table_column_names_list.__contains__('quota_max_abs'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN quota_max_abs NUMERIC(6,2)")

        if not table_column_names_list.__contains__('quota_max_rel'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN quota_max_rel NUMERIC(6,2)")

        if not table_column_names_list.__contains__('quota_min_abs'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN quota_min_abs NUMERIC(6,2)")

        if not table_column_names_list.__contains__('quota_min_rel'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN quota_min_rel NUMERIC(6,2)")

        if not table_column_names_list.__contains__('osservazioni'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN osservazioni text DEFAULT '' ")

        if not table_column_names_list.__contains__('datazione'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN datazione text DEFAULT '' ")

        if not table_column_names_list.__contains__('flottazione'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN flottazione text DEFAULT '' ")

        if not table_column_names_list.__contains__('setacciatura'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN setacciatura text DEFAULT '' ")

        if not table_column_names_list.__contains__('affidabilita'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN affidabilita text DEFAULT '' ")

        if not table_column_names_list.__contains__('direttore_us'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN direttore_us text DEFAULT '' ")

        if not table_column_names_list.__contains__('responsabile_us'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN responsabile_us text DEFAULT '' ")

        if not table_column_names_list.__contains__('cod_ente_schedatore'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN cod_ente_schedatore text DEFAULT '' ")

        if not table_column_names_list.__contains__('data_rilevazione'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN data_rilevazione text DEFAULT '' ")

        if not table_column_names_list.__contains__('data_rielaborazione'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN data_rielaborazione text DEFAULT '' ")

        if not table_column_names_list.__contains__('lunghezza_usm'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN lunghezza_usm NUMERIC(6,2)")

        if not table_column_names_list.__contains__('altezza_usm'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN altezza_usm NUMERIC(6,2)")

        if not table_column_names_list.__contains__('spessore_usm'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN spessore_usm NUMERIC(6,2)")

        if not table_column_names_list.__contains__('tecnica_muraria_usm'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN tecnica_muraria_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('modulo_usm'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN modulo_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('campioni_malta_usm'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN campioni_malta_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('campioni_mattone_usm'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN campioni_mattone_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('campioni_pietra_usm'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN campioni_pietra_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('provenienza_materiali_usm'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN provenienza_materiali_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('criteri_distinzione_usm'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN criteri_distinzione_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('uso_primario_usm'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN uso_primario_usm text DEFAULT '' ")
        
        if not table_column_names_list.__contains__('doc_usv'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN doc_usv text DEFAULT '' ")
        
        if not table_column_names_list.__contains__('tipologia_opera'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN tipologia_opera text DEFAULT '' ")
        
        if not table_column_names_list.__contains__('sezione_muraria'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN sezione_muraria text DEFAULT '' ")

        if not table_column_names_list.__contains__('superficie_analizzata'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN superficie_analizzata text DEFAULT '' ")

        if not table_column_names_list.__contains__('orientamento'):
                self.engine.execute("ALTER TABLE us_table RENAME COLUMN orientamento text DEFAULT '' ")

        if not table_column_names_list.__contains__('materiali_lat'):
                self.engine.execute("ALTER TABLE us_table RENAME COLUMN materiali_lat text DEFAULT '' ")

        if not table_column_names_list.__contains__('lavorazione_lat'):
                self.engine.execute("ALTER TABLE us_table RENAME COLUMN lavorazione_lat text DEFAULT '' ")

        if not table_column_names_list.__contains__('consistenza_lat'):
                self.engine.execute("ALTER TABLE us_table RENAME COLUMN consistenza_lat text DEFAULT '' ")

        if not table_column_names_list.__contains__('forma_lat'):
                self.engine.execute("ALTER TABLE us_table RENAME COLUMN forma_lat text DEFAULT '' ")

        if not table_column_names_list.__contains__('colore_lat'):
                self.engine.execute("ALTER TABLE us_table RENAME COLUMN colore_lat text DEFAULT '' ")

        if not table_column_names_list.__contains__('impasto_lat'):
                self.engine.execute("ALTER TABLE us_table RENAME COLUMN impasto_lat text DEFAULT '' ")

        if not table_column_names_list.__contains__('forma_p'):
                self.engine.execute("ALTER TABLE us_table RENAME COLUMN forma_p text DEFAULT '' ")

        if not table_column_names_list.__contains__('colore_p'):
                self.engine.execute("ALTER TABLE us_table RENAME COLUMN colore_p text DEFAULT '' ")

        if not table_column_names_list.__contains__('taglio_p'):
                self.engine.execute("ALTER TABLE us_table RENAME COLUMN taglio_p text DEFAULT '' ")

        if not table_column_names_list.__contains__('posa_opera_p'):
                self.engine.execute("ALTER TABLE us_table RENAME COLUMN posa_opera_p text DEFAULT '' ")

        if not table_column_names_list.__contains__('inerti_usm'):
                self.engine.execute("ALTER TABLE us_table RENAME COLUMN inerti_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('tipo_legante_usm'):
                self.engine.execute("ALTER TABLE us_table RENAME COLUMN tipo_legante_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('rifinitura_usm'):
                self.engine.execute("ALTER TABLE us_table RENAME COLUMN rifinitura_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('materiale_p'):
                self.engine.execute("ALTER TABLE us_table RENAME COLUMN materiale_p text DEFAULT '' ")

        if not table_column_names_list.__contains__('consistenza_p'):
                self.engine.execute("ALTER TABLE us_table RENAME COLUMN consistenza_p text DEFAULT '' ")                    

        if not table_column_names_list.__contains__('rapporti2'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN rapporti2 text DEFAULT '' ")
        
        
        ####pyarchinit_thesaurus_sigle
        table = Table("pyarchinit_thesaurus_sigle", self.metadata, autoload=True)
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('lingua'):
            self.engine.execute("ALTER TABLE pyarchinit_thesaurus_sigle RENAME COLUMN lingua text DEFAULT '' ")



        ####periodizzazione_table
        table = Table("periodizzazione_table", self.metadata, autoload=True)
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('cont_per'):
            self.engine.execute("ALTER TABLE periodizzazione_table RENAME COLUMN cont_per integer DEFAULT '' ")
        # if not table_column_names_list.__contains__('area'):
            # self.engine.execute("ALTER TABLE periodizzazione_table RENAME COLUMN area integer")
        
        ####tomba_table
        table = Table("tomba_table", self.metadata, autoload=True)
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('periodo_iniziale'):
            self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN periodo_iniziale integer")

        if not table_column_names_list.__contains__('fase_iniziale'):
            self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN fase_iniziale integer")

        if not table_column_names_list.__contains__('periodo_finale'):
            self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN periodo_finale integer")

        if not table_column_names_list.__contains__('fase_finale'):
            self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN fase_finale integer")

        if not table_column_names_list.__contains__('datazione_estesa'):
            self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN datazione_estesa text")

        ####individui_table
        table = Table("individui_table", self.metadata, autoload=True)
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('sigla_struttura'):
            self.engine.execute("ALTER TABLE individui_table RENAME COLUMN sigla_struttura text")

        if not table_column_names_list.__contains__('nr_struttura'):
            self.engine.execute("ALTER TABLE individui_table RENAME COLUMN nr_struttura text")

        if not table_column_names_list.__contains__('completo_si_no'):
            self.engine.execute("ALTER TABLE individui_table RENAME COLUMN completo_si_no varchar")

        if not table_column_names_list.__contains__('disturbato_si_no'):
            self.engine.execute("ALTER TABLE individui_table RENAME COLUMN disturbato_si_no varchar")

        if not table_column_names_list.__contains__('in_connessione_si_no'):
            self.engine.execute("ALTER TABLE individui_table RENAME COLUMN in_connessione_si_no varchar")

        if not table_column_names_list.__contains__('lunghezza_scheletro'):
            self.engine.execute("ALTER TABLE individui_table RENAME COLUMN lunghezza_scheletro NUMERIC(6,2)")

        if not table_column_names_list.__contains__('posizione_scheletro'):
            self.engine.execute("ALTER TABLE individui_table RENAME COLUMN posizione_scheletro varchar")

        if not table_column_names_list.__contains__('posizione_cranio'):
            self.engine.execute("ALTER TABLE individui_table RENAME COLUMN posizione_cranio varchar")

        if not table_column_names_list.__contains__('posizione_arti_superiori'):
            self.engine.execute("ALTER TABLE individui_table RENAME COLUMN posizione_arti_superiori varchar")

        if not table_column_names_list.__contains__('posizione_arti_inferiori'):
            self.engine.execute("ALTER TABLE individui_table RENAME COLUMN posizione_arti_inferiori varchar")
        
        if not table_column_names_list.__contains__('orientamento_asse'):
            self.engine.execute("ALTER TABLE individui_table RENAME COLUMN orientamento_asse text")

        if not table_column_names_list.__contains__('orientamento_azimut'):
            self.engine.execute("ALTER TABLE individui_table RENAME COLUMN orientamento_azimut text")
        try:
            if table_column_names_list.__contains__('nr_struttura'):
                self.engine.execute("ALTER TABLE individui_table ALTER COLUMN nr_struttura  TYPE text")
            if table_column_names_list.__contains__('orientamento_azimut'):
                self.engine.execute("ALTER TABLE individui_table ALTER COLUMN orientamento_azimut TYPE text")
            if table_column_names_list.__contains__('us'):
                self.engine.execute("ALTER TABLE individui_table ALTER COLUMN us TYPE text")
            if table_column_names_list.__contains__('eta_min'):
                self.engine.execute("ALTER TABLE individui_table ALTER COLUMN eta_min TYPE text")
            if table_column_names_list.__contains__('eta_max'):
                self.engine.execute("ALTER TABLE individui_table ALTER COLUMN eta_max TYPE text")
        except:
            pass
        
        
        
        ####periodizzazione_table
        table = Table("periodizzazione_table", self.metadata, autoload=True)
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))
        try: 
            if table_column_names_list.__contains__('fase'):
                self.engine.execute("ALTER TABLE periodizzazione_table ALTER COLUMN fase TYPE text")
        except:
            pass
        ####aggiornamento tabelle geografiche
        ####pyunitastratigrafiche
        table = Table("pyunitastratigrafiche", self.metadata, autoload=True)
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))
        # if table_column_names_list.__contains__('rilievo_orginale'):
            # self.engine.execute("ALTER TABLE pyunitastratigrafiche RENAME COLUMN rilievo_orginale TO rilievo_originale")   
        
        if not table_column_names_list.__contains__('coord'):
            self.engine.execute("ALTER TABLE pyunitastratigrafiche RENAME COLUMN coord text")
        if not table_column_names_list.__contains__('unita_tipo_s'):
            self.engine.execute("ALTER TABLE pyunitastratigrafiche RENAME COLUMN unita_tipo_s text")
        # if table_column_names_list.__contains__('id'):
            # self.engine.execute("ALTER TABLE pyunitastratigrafiche RENAME COLUMN id TO gid")

        table = Table("pyunitastratigrafiche_usm", self.metadata, autoload=True)
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))
        
        if not table_column_names_list.__contains__('unita_tipo_s'):
            self.engine.execute("ALTER TABLE pyunitastratigrafiche_usm RENAME COLUMN unita_tipo_s text")
       
        
        table = Table("pyarchinit_quote_usm", self.metadata, autoload=True)
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))
        
        if not table_column_names_list.__contains__('unita_tipo_q'):
            self.engine.execute("ALTER TABLE pyarchinit_quote_usm RENAME COLUMN unita_tipo_q text")
       
        
        table = Table("pyarchinit_quote", self.metadata, autoload=True)
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))
        
        if not table_column_names_list.__contains__('unita_tipo_q'):
            self.engine.execute("ALTER TABLE pyarchinit_quote RENAME COLUMN unita_tipo_q text")
        
        table = Table("pyarchinit_strutture_ipotesi", self.metadata, autoload=True)
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))
        
        if not table_column_names_list.__contains__('sigla_strut'):
        
            self.engine.execute( "ALTER TABLE pyarchinit_strutture_ipotesi RENAME COLUMN sigla_strut varchar(3) DEFAULT 'NoD'")
        
        if not table_column_names_list.__contains__('nr_strut'):
            self.engine.execute("ALTER TABLE pyarchinit_strutture_ipotesi RENAME COLUMN nr_strut integer DEFAULT 0 ")
        
       
        table = Table("pyarchinit_sezioni", self.metadata, autoload=True)
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))
                
        if not table_column_names_list.__contains__('tipo_doc'):
            self.engine.execute("ALTER TABLE pyarchinit_sezioni  RENAME COLUMN tipo_doc text")   
        
        if not table_column_names_list.__contains__('nome_doc'):
            self.engine.execute("ALTER TABLE pyarchinit_sezioni  RENAME COLUMN nome_doc text")
        
      