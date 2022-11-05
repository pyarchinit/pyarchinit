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


        self.engine = create_engine(conn_str, echo=False)
        self.metadata = MetaData(self.engine)

    def update_table(self):
        ''' convert column name from italian to english. In order from table to vector '''

        ####################################
        # archeozoology_table
        ####################################
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

        ####################################
        # site_table
        ####################################
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

        ####################################
        # invetario_materiali_table
        ####################################
        table = Table("inventario_materiali_table", self.metadata, autoload=True)
        table_column_names_list = []
        
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('site'):
            self.engine.execute(
                "ALTER TABLE inventario_materiali_table RENAME COLUMN sito To site")
        if not table_column_names_list.__contains__('inventory'):
            self.engine.execute(
                "ALTER TABLE inventario_materiali_table RENAME COLUMN numero_inventario To inventory")
        if not table_column_names_list.__contains__('artifact_type'):
            self.engine.execute(
                "ALTER TABLE inventario_materiali_table RENAME COLUMN tipo_reperto To artifact_type")

        if not table_column_names_list.__contains__('material_class'):
            self.engine.execute(
                "ALTER TABLE inventario_materiali_table RENAME COLUMN criterio_schedatura To material_class")

        if not table_column_names_list.__contains__('definition_artefact'):
            self.engine.execute(
                "ALTER TABLE inventario_materiali_table RENAME COLUMN definizione To definition_artefact")

        if not table_column_names_list.__contains__('description_artefact'):
            self.engine.execute(
                "ALTER TABLE inventario_materiali_table RENAME COLUMN descrizione To description_artefact")

        if not table_column_names_list.__contains__('su'):
            self.engine.execute(
                "ALTER TABLE inventario_materiali_table RENAME COLUMN us To su")

        if not table_column_names_list.__contains__('washed'):
            self.engine.execute(
                "ALTER TABLE inventario_materiali_table RENAME COLUMN lavato To washed")

        if not table_column_names_list.__contains__('box_number'):
            self.engine.execute(
                "ALTER TABLE inventario_materiali_table RENAME COLUMN nr_cassa To box_number")

        if not table_column_names_list.__contains__('place_conservation'):
            self.engine.execute(
                "ALTER TABLE inventario_materiali_table RENAME COLUMN luogo_conservazione To place_conservation")


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
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN corpo_ceramico TO pottery_body")

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
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN diagnostico TO diagnostic")

        if not table_column_names_list.__contains__('number_find'):
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN n_reperto TO number_find")

        if not table_column_names_list.__contains__('container_type'):
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN tipo_contenitore TO container_type")

        if not table_column_names_list.__contains__('structure'):
            self.engine.execute("ALTER TABLE inventario_materiali_table RENAME COLUMN struttura TO structure")

        ####################################
        # us_table
        ####################################
        table = Table("us_table", self.metadata, autoload=True)
        table_column_names_list = []

        for i in table.columns:
            table_column_names_list.append(str(i.name))
        if not table_column_names_list.__contains__('site'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN sito TO site")

        if not table_column_names_list.__contains__('su'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN us TO su")

        if not table_column_names_list.__contains__('def_strat'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN d_stratigrafica TO def_strat")

        if not table_column_names_list.__contains__('def_interpretation'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN d_interpretativa TO def_interpretation")

        if not table_column_names_list.__contains__('description'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN descrizione TO description")

        if not table_column_names_list.__contains__('interpretation'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN interpretazione TO interpretation")

        if not table_column_names_list.__contains__('per_start'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN periodo_iniziale TO per_start")

        if not table_column_names_list.__contains__('phase_start'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN fase_iniziale TO phase_start")

        if not table_column_names_list.__contains__('per_end'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN periodo_finale TO per_end")

        if not table_column_names_list.__contains__('phase_end'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN fase_finale TO phase_end")

        if not table_column_names_list.__contains__('excavated'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN scavato TO excavated")

        if not table_column_names_list.__contains__('activities'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN attivita TO activities")

        if not table_column_names_list.__contains__('year_excavation'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN anno_scavo TO year_excavation")

        if not table_column_names_list.__contains__('digging_type'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN metodo_di_scavo TO digging_type")

        if not table_column_names_list.__contains__('inclusion'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN inclusi TO inclusion")

        if not table_column_names_list.__contains__('sample'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN campioni TO sample")

        if not table_column_names_list.__contains__('relationships'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN rapporti TO relationships")

        if not table_column_names_list.__contains__('date_filing'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN data_schedatura TO date_filing")

        if not table_column_names_list.__contains__('cataloguer'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN schedatore TO cataloguer")

        if not table_column_names_list.__contains__('formation'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN formazione TO formation")

        if not table_column_names_list.__contains__('preservation'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN stato_di_conservazione TO preservation")

        if not table_column_names_list.__contains__('su_color'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN colore TO su_color")

        if not table_column_names_list.__contains__('su_texture'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN consistenza TO su_texture")

        if not table_column_names_list.__contains__('building'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN struttura TO building")

        if not table_column_names_list.__contains__('count_per'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN cont_per TO count_per")

        if not table_column_names_list.__contains__('documentation'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN documentazione TO documentation")

            # nuovi campi per USM 1/9/2016 generati correttamente
        if not table_column_names_list.__contains__('type_unit'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN unita_tipo TO type_unit")

        if not table_column_names_list.__contains__('sector'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN settore TO sector ")

        if not table_column_names_list.__contains__('square'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN quad_par TO square ")

        if not table_column_names_list.__contains__('room'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN ambient TO room ")

        if not table_column_names_list.__contains__('test_pit'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN saggio TO test_pit ")

        if not table_column_names_list.__contains__('dating_element'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN elem_datanti TO dating_element ")

        if not table_column_names_list.__contains__('static_function'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN funz_statica TO static_function ")

        if not table_column_names_list.__contains__('processing_of'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN lavorazione TO processing_of ")

        if not table_column_names_list.__contains__('thickness_joint'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN spess_giunti TO thickness_joint ")

        if not table_column_names_list.__contains__('laying_bed_masonry'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN letti_posa TO laying_bed_masonry ")

        if not table_column_names_list.__contains__('heigth_mod'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN alt_mod TO heigth_mod ")

        if not table_column_names_list.__contains__('un_ed_riass'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN un_ed_riass text DEFAULT '' ")

        if not table_column_names_list.__contains__('filling'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN reimp TO filling ")

        if not table_column_names_list.__contains__('laying_masonry_work'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN posa_opera TO laying_masonry_work ")

        if not table_column_names_list.__contains__('elev_min_usm'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN quota_min_usm TO elev_min_usm")

        if not table_column_names_list.__contains__('elev_max_usm'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN quota_max_usm TO elev_max_usm")

        if not table_column_names_list.__contains__('binding_consistency'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN cons_legante To binding_consistency")

        if not table_column_names_list.__contains__('color_binder'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN col_legante To color_binder")

        if not table_column_names_list.__contains__('aggreg_binder'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN aggreg_legante To aggreg_binder ")

        if not table_column_names_list.__contains__('consistency_texture_mat'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN con_text_mat TO consistency_texture_mat ")

        if not table_column_names_list.__contains__('color_material'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN col_materiale TO color_material ")

        if not table_column_names_list.__contains__('inclusion_material_usm'):
            self.engine.execute(
                "ALTER TABLE us_table RENAME COLUMN inclusi_materiali_usm TO inclusion_material_usm ")

        if not table_column_names_list.__contains__('n_catalog_general'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN n_catalogo_generale TO n_catalog_general ")

        if not table_column_names_list.__contains__('n_catalog_internal'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN n_catalogo_interno TO n_catalog_internal ")

        if not table_column_names_list.__contains__('n_catalog_international'):
            self.engine.execute(
                "ALTER TABLE us_table RENAME COLUMN n_catalogo_internazionale TO n_catalog_international ")

        if not table_column_names_list.__contains__('elev_relative'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN quota_relativa TO elev_relative")

        if not table_column_names_list.__contains__('elev_abs'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN quota_abs TO elev_abs")

        if not table_column_names_list.__contains__('placement'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN posizione TO placement ")

        if not table_column_names_list.__contains__('criteria_diff'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN criteri_distinzione TO criteria_diff ")

        if not table_column_names_list.__contains__('mode_formation'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN modo_formazione TO mode_formation ")

        if not table_column_names_list.__contains__('organic_component'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN componenti_organici TO organic_component ")

        if not table_column_names_list.__contains__('inorganic_component'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN componenti_inorganici TO  inorganic_component")

        if not table_column_names_list.__contains__('max_lenght'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN lunghezza_max TO max_lenght")

        if not table_column_names_list.__contains__('max_elevation'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN altezza_max TO max_elevation")

        if not table_column_names_list.__contains__('min_elevation'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN altezza_min TO min_elevation")

        if not table_column_names_list.__contains__('max_deep'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN profondita_max TO max_deep")

        if not table_column_names_list.__contains__('min_deep'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN profondita_min TO min_deep")

        if not table_column_names_list.__contains__('average_width'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN larghezza_media TO average_width")

        if not table_column_names_list.__contains__('max_elevation_abs'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN quota_max_abs TO max_elevation_abs")

        if not table_column_names_list.__contains__('max_elevation_rel'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN quota_max_rel TO max_elevation_rel")

        if not table_column_names_list.__contains__('min_elevation_abs'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN quota_min_abs TO min_elevation_abs")

        if not table_column_names_list.__contains__('min_elevation_rel'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN quota_min_rel TO min_elevation_rel")

        if not table_column_names_list.__contains__('observation'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN osservazioni TO observation ")

        if not table_column_names_list.__contains__('datazione'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN datazione TO dating")

        if not table_column_names_list.__contains__('flotation'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN flottazione TO flotation")

        if not table_column_names_list.__contains__('sieving'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN setacciatura TO sieving")

        if not table_column_names_list.__contains__('reliability'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN affidabilita TO reliability")

        if not table_column_names_list.__contains__('su_director'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN direttore_us TO su_director")

        if not table_column_names_list.__contains__('su_responsible'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN responsabile_us TO su_responsible   ")

        if not table_column_names_list.__contains__('cod_scheduler'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN cod_ente_schedatore TO cod_scheduler")

        if not table_column_names_list.__contains__('survey_date'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN data_rilevazione TO survey_date")

        if not table_column_names_list.__contains__('processing_date'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN data_rielaborazione TO processing_date")

        if not table_column_names_list.__contains__('wsu_lenght'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN lunghezza_usm TO wsu_lenght")

        if not table_column_names_list.__contains__('wsu_elevation'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN altezza_usm TO wsu_elevation")

        if not table_column_names_list.__contains__('wsu_thickness'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN spessore_usm TO wsu_thickness")

        if not table_column_names_list.__contains__('masonry_technique'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN tecnica_muraria_usm TO masonry_technique")

        if not table_column_names_list.__contains__('wsu_module'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN modulo_usm TO wsu_module")

        if not table_column_names_list.__contains__('mortar_sample'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN campioni_malta_usm TO mortar_sample")

        if not table_column_names_list.__contains__('brick_sample'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN campioni_mattone_usm TO brick_sample")

        if not table_column_names_list.__contains__('stone_sample'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN campioni_pietra_usm TO stone_sample")

        if not table_column_names_list.__contains__('provenance_material'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN provenienza_materiali_usm TO provenance_material")

        if not table_column_names_list.__contains__('distinction_criteria'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN criteri_distinzione_usm TO distinction_criteria")

        if not table_column_names_list.__contains__('primary_use'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN uso_primario_usm TO primary_use")


        if not table_column_names_list.__contains__('typology_work'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN tipologia_opera TO typology_work")

        if not table_column_names_list.__contains__('masonry_section'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN sezione_muraria TO masonry_section")

        if not table_column_names_list.__contains__('surface_analysed'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN superficie_analizzata TO surface_analysed")

        if not table_column_names_list.__contains__('orientation'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN orientamento TO orientation")

        if not table_column_names_list.__contains__('material_lat'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN materiali_lat TO material_lat")

        if not table_column_names_list.__contains__('works_lat'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN lavorazione_lat TO works_lat")

        if not table_column_names_list.__contains__('texture_lat'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN consistenza_lat TO texture_lat")

        if not table_column_names_list.__contains__('shape_lat'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN forma_lat TO shape_lat")

        if not table_column_names_list.__contains__('color_lat'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN colore_lat TO color_lat")

        if not table_column_names_list.__contains__('mixture_lat'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN impasto_lat TO mixture_lat")

        if not table_column_names_list.__contains__('shape_p'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN forma_p TO shape_p")

        if not table_column_names_list.__contains__('color_p'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN colore_p TO color_p")

        if not table_column_names_list.__contains__('cut_p'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN taglio_p TO cut_p")

        if not table_column_names_list.__contains__('laying_masonry_work_p'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN posa_opera_p TO laying_masonry_work_p")

        if not table_column_names_list.__contains__('inert_wsu'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN inerti_usm TO inert_wsu")

        if not table_column_names_list.__contains__('type_binder_wsu'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN tipo_legante_usm TO type_binder_wsu")

        if not table_column_names_list.__contains__('refinement_wsu'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN rifinitura_usm TO refinement_wsu")

        if not table_column_names_list.__contains__('material_p'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN materiale_p TO material_p")

        if not table_column_names_list.__contains__('texture_p'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN consistenza_p TO texture_p")

        if not table_column_names_list.__contains__('relationship_em'):
            self.engine.execute("ALTER TABLE us_table RENAME COLUMN rapporti2 TO relationship_em")

        ####################################
        # pyarchinit_thesaurus_sigle
        ####################################
        table = Table("pyarchinit_thesaurus_sigle", self.metadata, autoload=True)
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('name_tab'):
            self.engine.execute("ALTER TABLE pyarchinit_thesaurus_sigle RENAME COLUMN nome_tabella TO name_tab")
        if not table_column_names_list.__contains__('code'):
            self.engine.execute("ALTER TABLE pyarchinit_thesaurus_sigle RENAME COLUMN sigla TO code")
        if not table_column_names_list.__contains__('extended_code'):
            self.engine.execute("ALTER TABLE pyarchinit_thesaurus_sigle RENAME COLUMN sigla_estesa TO extended_code")
        if not table_column_names_list.__contains__('description'):
            self.engine.execute("ALTER TABLE pyarchinit_thesaurus_sigle RENAME COLUMN descrizione TO description")
        if not table_column_names_list.__contains__('number_code'):
            self.engine.execute("ALTER TABLE pyarchinit_thesaurus_sigle RENAME COLUMN tipologia_sigla TO number_code")
        if not table_column_names_list.__contains__('language'):
            self.engine.execute("ALTER TABLE pyarchinit_thesaurus_sigle RENAME COLUMN lingua TO language")

        ####################################
        # periodizzazione_table
        ####################################
        table = Table("periodizzazione_table", self.metadata, autoload=True)
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))
        if not table_column_names_list.__contains__('site'):
            self.engine.execute("ALTER TABLE periodizzazione_table RENAME COLUMN sito TO site")
        if not table_column_names_list.__contains__('period'):
            self.engine.execute("ALTER TABLE periodizzazione_table RENAME COLUMN periodo TO period")
        if not table_column_names_list.__contains__('phase'):
            self.engine.execute("ALTER TABLE periodizzazione_table RENAME COLUMN fase TO phase")
        if not table_column_names_list.__contains__('chrono_start'):
            self.engine.execute("ALTER TABLE periodizzazione_table RENAME COLUMN cron_iniziale TO chrono_start")
        if not table_column_names_list.__contains__('chrono_end'):
            self.engine.execute("ALTER TABLE periodizzazione_table RENAME COLUMN cron_finale TO chrono_end")
        if not table_column_names_list.__contains__('description'):
            self.engine.execute("ALTER TABLE periodizzazione_table RENAME COLUMN descrizione TO description")
        if not table_column_names_list.__contains__('dating'):
            self.engine.execute("ALTER TABLE periodizzazione_table RENAME COLUMN datazione_estesa TO dating")

        # ####################################
        # # tomba_table
        # ####################################
        # table = Table("tomba_table", self.metadata, autoload=True)
        # table_column_names_list = []
        # for i in table.columns:
        #     table_column_names_list.append(str(i.name))
        #
        # if not table_column_names_list.__contains__('site'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN periodo_iniziale integer")
        #
        # if not table_column_names_list.__contains__('nr_taph'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN periodo_finale integer")
        #
        # if not table_column_names_list.__contains__('code_structure'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN fase_finale integer")
        #
        # if not table_column_names_list.__contains__('nr_structure'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN datazione_estesa text")
        #
        # if not table_column_names_list.__contains__('nr_individual'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN periodo_iniziale integer")
        #
        # if not table_column_names_list.__contains__('fase_iniziale'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN fase_iniziale integer")
        #
        # if not table_column_names_list.__contains__('periodo_finale'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN periodo_finale integer")
        #
        # if not table_column_names_list.__contains__('fase_finale'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN fase_finale integer")
        #
        # if not table_column_names_list.__contains__('datazione_estesa'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN datazione_estesa text")
        #
        # if not table_column_names_list.__contains__('periodo_iniziale'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN periodo_iniziale integer")
        #
        # if not table_column_names_list.__contains__('fase_iniziale'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN fase_iniziale integer")
        #
        # if not table_column_names_list.__contains__('periodo_finale'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN periodo_finale integer")
        #
        # if not table_column_names_list.__contains__('fase_finale'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN fase_finale integer")
        #
        # if not table_column_names_list.__contains__('datazione_estesa'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN datazione_estesa text")
        #
        # if not table_column_names_list.__contains__('periodo_iniziale'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN periodo_iniziale integer")
        #
        # if not table_column_names_list.__contains__('fase_iniziale'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN fase_iniziale integer")
        #
        # if not table_column_names_list.__contains__('periodo_finale'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN periodo_finale integer")
        #
        # if not table_column_names_list.__contains__('fase_finale'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN fase_finale integer")
        #
        # if not table_column_names_list.__contains__('datazione_estesa'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN datazione_estesa text")
        # if not table_column_names_list.__contains__('periodo_iniziale'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN periodo_iniziale integer")
        #
        # if not table_column_names_list.__contains__('fase_iniziale'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN fase_iniziale integer")
        #
        # if not table_column_names_list.__contains__('periodo_finale'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN periodo_finale integer")
        #
        # if not table_column_names_list.__contains__('fase_finale'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN fase_finale integer")
        #
        # if not table_column_names_list.__contains__('datazione_estesa'):
        #     self.engine.execute("ALTER TABLE tomba_table RENAME COLUMN datazione_estesa text")
        ####################################
        # ####individui_table
        ####################################
        # table = Table("individui_table", self.metadata, autoload=True)
        # table_column_names_list = []
        # for i in table.columns:
        #     table_column_names_list.append(str(i.name))
        #
        # if not table_column_names_list.__contains__('sigla_struttura'):
        #     self.engine.execute("ALTER TABLE individui_table RENAME COLUMN sigla_struttura text")
        #
        # if not table_column_names_list.__contains__('nr_struttura'):
        #     self.engine.execute("ALTER TABLE individui_table RENAME COLUMN nr_struttura text")
        #
        # if not table_column_names_list.__contains__('completo_si_no'):
        #     self.engine.execute("ALTER TABLE individui_table RENAME COLUMN completo_si_no varchar")
        #
        # if not table_column_names_list.__contains__('disturbato_si_no'):
        #     self.engine.execute("ALTER TABLE individui_table RENAME COLUMN disturbato_si_no varchar")
        #
        # if not table_column_names_list.__contains__('in_connessione_si_no'):
        #     self.engine.execute("ALTER TABLE individui_table RENAME COLUMN in_connessione_si_no varchar")
        #
        # if not table_column_names_list.__contains__('lunghezza_scheletro'):
        #     self.engine.execute("ALTER TABLE individui_table RENAME COLUMN lunghezza_scheletro NUMERIC(6,2)")
        #
        # if not table_column_names_list.__contains__('posizione_scheletro'):
        #     self.engine.execute("ALTER TABLE individui_table RENAME COLUMN posizione_scheletro varchar")
        #
        # if not table_column_names_list.__contains__('posizione_cranio'):
        #     self.engine.execute("ALTER TABLE individui_table RENAME COLUMN posizione_cranio varchar")
        #
        # if not table_column_names_list.__contains__('posizione_arti_superiori'):
        #     self.engine.execute("ALTER TABLE individui_table RENAME COLUMN posizione_arti_superiori varchar")
        #
        # if not table_column_names_list.__contains__('posizione_arti_inferiori'):
        #     self.engine.execute("ALTER TABLE individui_table RENAME COLUMN posizione_arti_inferiori varchar")
        #
        # if not table_column_names_list.__contains__('orientamento_asse'):
        #     self.engine.execute("ALTER TABLE individui_table RENAME COLUMN orientamento_asse text")
        #
        # if not table_column_names_list.__contains__('orientamento_azimut'):
        #     self.engine.execute("ALTER TABLE individui_table RENAME COLUMN orientamento_azimut text")
        # try:
        #     if table_column_names_list.__contains__('nr_struttura'):
        #         self.engine.execute("ALTER TABLE individui_table ALTER COLUMN nr_struttura  TYPE text")
        #     if table_column_names_list.__contains__('orientamento_azimut'):
        #         self.engine.execute("ALTER TABLE individui_table ALTER COLUMN orientamento_azimut TYPE text")
        #     if table_column_names_list.__contains__('us'):
        #         self.engine.execute("ALTER TABLE individui_table ALTER COLUMN us TYPE text")
        #     if table_column_names_list.__contains__('eta_min'):
        #         self.engine.execute("ALTER TABLE individui_table ALTER COLUMN eta_min TYPE text")
        #     if table_column_names_list.__contains__('eta_max'):
        #         self.engine.execute("ALTER TABLE individui_table ALTER COLUMN eta_max TYPE text")
        # except:
        #     pass
        #
        #
        #
        # ####periodizzazione_table
        # table = Table("periodizzazione_table", self.metadata, autoload=True)
        # table_column_names_list = []
        # for i in table.columns:
        #     table_column_names_list.append(str(i.name))
        # try:
        #     if table_column_names_list.__contains__('fase'):
        #         self.engine.execute("ALTER TABLE periodizzazione_table ALTER COLUMN fase TYPE text")
        # except:
        #     pass
        # ####aggiornamento tabelle geografiche
        # ####pyunitastratigrafiche
        # table = Table("pyunitastratigrafiche", self.metadata, autoload=True)
        # table_column_names_list = []
        # for i in table.columns:
        #     table_column_names_list.append(str(i.name))
        # # if table_column_names_list.__contains__('rilievo_orginale'):
        #     # self.engine.execute("ALTER TABLE pyunitastratigrafiche RENAME COLUMN rilievo_orginale TO rilievo_originale")
        #
        # if not table_column_names_list.__contains__('coord'):
        #     self.engine.execute("ALTER TABLE pyunitastratigrafiche RENAME COLUMN coord text")
        # if not table_column_names_list.__contains__('unita_tipo_s'):
        #     self.engine.execute("ALTER TABLE pyunitastratigrafiche RENAME COLUMN unita_tipo_s text")
        # # if table_column_names_list.__contains__('id'):
        #     # self.engine.execute("ALTER TABLE pyunitastratigrafiche RENAME COLUMN id TO gid")
        #
        # table = Table("pyunitastratigrafiche_usm", self.metadata, autoload=True)
        # table_column_names_list = []
        # for i in table.columns:
        #     table_column_names_list.append(str(i.name))
        #
        # if not table_column_names_list.__contains__('unita_tipo_s'):
        #     self.engine.execute("ALTER TABLE pyunitastratigrafiche_usm RENAME COLUMN unita_tipo_s text")
        #
        #
        # table = Table("pyarchinit_quote_usm", self.metadata, autoload=True)
        # table_column_names_list = []
        # for i in table.columns:
        #     table_column_names_list.append(str(i.name))
        #
        # if not table_column_names_list.__contains__('unita_tipo_q'):
        #     self.engine.execute("ALTER TABLE pyarchinit_quote_usm RENAME COLUMN unita_tipo_q text")
        #
        #
        # table = Table("pyarchinit_quote", self.metadata, autoload=True)
        # table_column_names_list = []
        # for i in table.columns:
        #     table_column_names_list.append(str(i.name))
        #
        # if not table_column_names_list.__contains__('unita_tipo_q'):
        #     self.engine.execute("ALTER TABLE pyarchinit_quote RENAME COLUMN unita_tipo_q text")
        #
        # table = Table("pyarchinit_strutture_ipotesi", self.metadata, autoload=True)
        # table_column_names_list = []
        # for i in table.columns:
        #     table_column_names_list.append(str(i.name))
        #
        # if not table_column_names_list.__contains__('sigla_strut'):
        #
        #     self.engine.execute( "ALTER TABLE pyarchinit_strutture_ipotesi RENAME COLUMN sigla_strut varchar(3) DEFAULT 'NoD'")
        #
        # if not table_column_names_list.__contains__('nr_strut'):
        #     self.engine.execute("ALTER TABLE pyarchinit_strutture_ipotesi RENAME COLUMN nr_strut integer DEFAULT 0 ")
        #
        #
        # table = Table("pyarchinit_sezioni", self.metadata, autoload=True)
        # table_column_names_list = []
        # for i in table.columns:
        #     table_column_names_list.append(str(i.name))
        #
        # if not table_column_names_list.__contains__('tipo_doc'):
        #     self.engine.execute("ALTER TABLE pyarchinit_sezioni  RENAME COLUMN tipo_doc text")
        #
        # if not table_column_names_list.__contains__('nome_doc'):
        #     self.engine.execute("ALTER TABLE pyarchinit_sezioni  RENAME COLUMN nome_doc text")
        
      