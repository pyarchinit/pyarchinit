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

from qgis.PyQt.QtWidgets import QMessageBox

from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_update_thesaurus import update_thesaurus_table


class DB_update(object):
    # connection string postgres"
    def __init__(self, conn_str):
        # create engine and metadata
        self.engine = create_engine(conn_str, echo=False)
        self.metadata = MetaData(self.engine)

    def update_table(self):
        def safe_load_table(table_name):
            """Carica una tabella gestendo errori di encoding UTF-8"""
            try:
                return Table(table_name, self.metadata, autoload=True)
            except UnicodeDecodeError as e:
                QMessageBox.warning(None, "Errore Encoding", 
                                  f"Errore di encoding UTF-8 nella tabella {table_name}.\n"
                                  f"Verificare che il database PostgreSQL sia configurato con encoding UTF-8.\n"
                                  f"Dettagli: {str(e)}", QMessageBox.Ok)
                return None
            except Exception as e:
                # Gestisci altri errori di caricamento tabella
                QMessageBox.warning(None, "Errore Tabella", 
                                  f"Impossibile caricare la tabella {table_name}.\n"
                                  f"Dettagli: {str(e)}", QMessageBox.Ok)
                return None
        
        # Check if we're using SQLite
        is_sqlite = 'sqlite' in str(self.engine.url).lower()
        
        # TMA table migration and ensure new tables exist
        try:
            # Ensure TMA tables exist in correct order
            self._ensure_tma_tables_exist()
            
            # Now check if old tma_table exists and needs migration
            if is_sqlite:
                result = self.engine.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tma_table'")
                old_tma_exists = result.fetchone() is not None
            else:
                result = self.engine.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'tma_table'
                    )
                """)
                old_tma_exists = result.fetchone()[0]
            
            if old_tma_exists:
                self._migrate_tma_table()
                
            # Check if localita field exists in tma_materiali_archeologici and remove it
            #self._remove_localita_field()
        except Exception as e:
            print(f"Error in TMA table setup: {str(e)}")
        
        # Update thesaurus table structure
        try:
            update_thesaurus_table(self.engine, self.metadata)
        except Exception as e:
            print(f"Error updating thesaurus table: {str(e)}")
        
        # SQLite US field migration
        if is_sqlite:
            self._migrate_us_fields_sqlite()
            return
        # ####invetario_materiali_table
        # table = Table("pyunitastratigrafiche", self.metadata, autoload=True)
        # table_column_names_list = []
        #
        # for i in table.columns:
        #     table_column_names_list.append(str(i.name))
        # if table_column_names_list.__contains__('coord'):
        #     self.engine.execute(
        #         "ALTER TABLE pyunitastratigrafiche ALTER COLUMN coord TYPE text")
        #
        # table = Table("pyunitastratigrafiche_usm", self.metadata, autoload=True)
        # table_column_names_list = []
        #
        # for i in table.columns:
        #     table_column_names_list.append(str(i.name))
        # if table_column_names_list.__contains__('coord'):
        #     self.engine.execute(
        #         "ALTER TABLE pyunitastratigrafiche ALTER COLUMN coord TYPE text")

        ####pottery_table
        try:
            table = Table("pottery_table", self.metadata, autoload=True)
        except UnicodeDecodeError as e:
            # Gestisci errore di encoding
            QMessageBox.warning(None, "Errore Encoding", 
                              f"Errore di encoding UTF-8 nella tabella pottery_table.\n"
                              f"Verificare che il database PostgreSQL sia configurato con encoding UTF-8.\n"
                              f"Dettagli: {str(e)}", QMessageBox.Ok)
            return
        table_column_names_list = []

        for i in table.columns:
            table_column_names_list.append(str(i.name))
        
        # Change US column from INTEGER to TEXT
        try:
            if table_column_names_list.__contains__('us'):
                # Check if the column is still INTEGER type
                us_column = None
                for col in table.columns:
                    if col.name == 'us':
                        us_column = col
                        break
                
                if us_column is not None:
                    # Check if column type needs conversion
                    col_type = str(us_column.type)
                    if 'INTEGER' in col_type.upper() or 'BIGINT' in col_type.upper():
                        # Convert the column type
                        self.engine.execute("ALTER TABLE pottery_table ALTER COLUMN us TYPE TEXT USING us::TEXT")
        except Exception as e:
            # Log the error but continue with other updates
            pass
        
        if not table_column_names_list.__contains__('sector'):
            self.engine.execute(
                "ALTER TABLE pottery_table ADD COLUMN sector text")
        try:
            if table_column_names_list.__contains__('diametro_max'):
                self.engine.execute(
                    "ALTER TABLE pottery_table ALTER COLUMN diametro_max TYPE Numeric(7,3)")

            if table_column_names_list.__contains__('diametro_rim'):
                self.engine.execute(
                    "ALTER TABLE pottery_table ALTER COLUMN diametro_rim TYPE Numeric(7,3)")

            if table_column_names_list.__contains__('diametro_bottom'):
                self.engine.execute(
                    "ALTER TABLE pottery_table ALTER COLUMN diametro_bottom TYPE Numeric(7,3)")

            if table_column_names_list.__contains__('diametro_height'):
                self.engine.execute(
                    "ALTER TABLE pottery_table ALTER COLUMN diametro_height TYPE Numeric(7,3)")

            if table_column_names_list.__contains__('diametro_preserved'):
                self.engine.execute(
                    "ALTER TABLE pottery_table ALTER COLUMN diametro_preserved TYPE Numeric(7,3)")


        except:
            pass


        ####inventario_materiali_table
        table = safe_load_table("inventario_materiali_table")
        if table is None:
            return
        table_column_names_list = []

        for i in table.columns:
            table_column_names_list.append(str(i.name))

        # Change area and us columns from INTEGER to TEXT
        try:
            if table_column_names_list.__contains__('area'):
                self.engine.execute(
                    "ALTER TABLE inventario_materiali_table ALTER COLUMN area TYPE TEXT")

            if table_column_names_list.__contains__('us'):
                self.engine.execute(
                    "ALTER TABLE inventario_materiali_table ALTER COLUMN us TYPE TEXT")
        except:
            pass

        if not table_column_names_list.__contains__('years'):
            self.engine.execute(
                "ALTER TABLE inventario_materiali_table ADD COLUMN years BIGINT")

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
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN forme_minime BIGINT DEFAULT 0")

        if not table_column_names_list.__contains__('forme_massime'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN forme_massime BIGINT DEFAULT 0")

        if not table_column_names_list.__contains__('totale_frammenti'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN totale_frammenti BIGINT DEFAULT 0")

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
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN repertato varchar(3)")
            self.engine.execute("update inventario_materiali_table set repertato = ''No")

        if not table_column_names_list.__contains__('diagnostico'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN diagnostico varchar(3)")
            self.engine.execute("update inventario_materiali_table set diagnostico = ''No")
        if not table_column_names_list.__contains__('n_reperto'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN n_reperto BIGINT")
        if not table_column_names_list.__contains__('tipo_contenitore'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN tipo_contenitore varchar DEFAULT ''")
        if not table_column_names_list.__contains__('struttura'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN struttura text")

        # Add new columns for inventario_materiali_table
        if not table_column_names_list.__contains__('schedatore'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN schedatore TEXT")

        if not table_column_names_list.__contains__('date_scheda'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN date_scheda TEXT")

        if not table_column_names_list.__contains__('punto_rinv'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN punto_rinv TEXT")

        if not table_column_names_list.__contains__('negativo_photo'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN negativo_photo TEXT")

        if not table_column_names_list.__contains__('diapositiva'):
            self.engine.execute("ALTER TABLE inventario_materiali_table ADD COLUMN diapositiva TEXT")

        # Update the pyarchinit_reperti_view to include the new fields
        try:
            self.engine.execute("""
            CREATE OR REPLACE VIEW pyarchinit_reperti_view AS 
            SELECT
            gid,
            the_geom,
            id_rep,
            siti,
            id_invmat,
            sito,
            numero_inventario,
            tipo_reperto,
            criterio_schedatura,
            definizione,
            descrizione,
            area,
            us,
            lavato,
            nr_cassa,
            luogo_conservazione,
            stato_conservazione,
            datazione_reperto,
            elementi_reperto,
            misurazioni,
            rif_biblio,
            tecnologie,
            forme_minime,
            forme_massime,
            totale_frammenti,
            corpo_ceramico,
            rivestimento,
            diametro_orlo,
            peso,
            tipo,
            eve_orlo,
            repertato,
            diagnostico,
            n_reperto,
            tipo_contenitore,
            struttura,
            years,
            schedatore,
            date_scheda,
            punto_rinv,
            negativo_photo,
            diapositiva
            FROM pyarchinit_reperti
            JOIN inventario_materiali_table ON siti::text = sito AND id_rep = numero_inventario;
            """)
        except:
            pass






        ####site_table
        table = safe_load_table("site_table")
        if table is None:
            return
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('provincia'):
            self.engine.execute("ALTER TABLE site_table ADD COLUMN provincia varchar DEFAULT 'inserici un valore' ")

        if not table_column_names_list.__contains__('definizione_sito'):
            self.engine.execute(
                "ALTER TABLE site_table ADD COLUMN definizione_sito varchar DEFAULT 'inserici un valore' ")

        if not table_column_names_list.__contains__('sito_path'):
            self.engine.execute("ALTER TABLE site_table ADD COLUMN sito_path varchar DEFAULT 'inserisci path' ")

        if not table_column_names_list.__contains__('find_check'):
            self.engine.execute("ALTER TABLE site_table ADD COLUMN find_check BIGINT DEFAULT 0")

        ####US_table
        table = safe_load_table("us_table")
        if table is None:
            return
        table_column_names_list = []

        for i in table.columns:
            table_column_names_list.append(str(i.name))

        # Change US column from INTEGER to TEXT
        try:
            # Check if the column is still INTEGER type
            # Get column type from database metadata
            us_column = None
            for col in table.columns:
                if col.name == 'us':
                    us_column = col
                    break
            
            if us_column is not None:
                # Check if column type needs conversion
                col_type = str(us_column.type)
                if 'INTEGER' in col_type.upper() or 'BIGINT' in col_type.upper():
                    # Drop dependent views first
                    try:
                        self.engine.execute("DROP VIEW IF EXISTS pyarchinit_quote_view CASCADE")
                        self.engine.execute("DROP VIEW IF EXISTS pyarchinit_us_view CASCADE")
                        self.engine.execute("DROP VIEW IF EXISTS pyarchinit_uscaratterizzazioni_view CASCADE")
                    except:
                        pass
                    
                    # Convert the column type
                    self.engine.execute("ALTER TABLE us_table ALTER COLUMN us TYPE TEXT USING us::TEXT")
                    
                    # Recreate views
                    try:
                        self.engine.execute("""
                        CREATE VIEW pyarchinit_us_view AS
                        SELECT 
                            pyunitastratigrafiche.gid, 
                            pyunitastratigrafiche.the_geom, 
                            pyunitastratigrafiche.tipo_us_s, 
                            pyunitastratigrafiche.scavo_s, 
                            pyunitastratigrafiche.area_s, 
                            pyunitastratigrafiche.us_s, 
                            pyunitastratigrafiche.stratigraph_index_us,
                            us_table.id_us, 
                            us_table.sito, 
                            us_table.area, 
                            us_table.us, 
                            us_table.struttura, 
                            us_table.d_stratigrafica, 
                            us_table.d_interpretativa, 
                            us_table.descrizione, 
                            us_table.interpretazione, 
                            us_table.rapporti, 
                            us_table.periodo_iniziale, 
                            us_table.fase_iniziale, 
                            us_table.periodo_finale, 
                            us_table.fase_finale, 
                            us_table.anno_scavo
                        FROM pyunitastratigrafiche
                        JOIN us_table ON 
                            pyunitastratigrafiche.scavo_s = us_table.sito 
                            AND pyunitastratigrafiche.area_s::TEXT = us_table.area::TEXT 
                            AND pyunitastratigrafiche.us_s = us_table.us
                        """)
                    except:
                        pass
        except Exception as e:
            # Log the error but continue with other updates
            pass

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
            self.engine.execute("ALTER TABLE us_table ADD COLUMN col_legante text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('aggreg_legante'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN aggreg_legante text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('con_text_mat'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN con_text_mat text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('col_materiale'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN col_materiale text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('inclusi_materiali_usm'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN inclusi_materiali_usm text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('n_catalogo_generale'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN n_catalogo_generale text DEFAULT '' ")

        if not table_column_names_list.__contains__('n_catalogo_interno'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN n_catalogo_interno text DEFAULT '' ")

        if not table_column_names_list.__contains__('n_catalogo_internazionale'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN n_catalogo_internazionale text DEFAULT '' ")

        if not table_column_names_list.__contains__('soprintendenza'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN soprintendenza text DEFAULT '' ")

        if not table_column_names_list.__contains__('quota_relativa'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN quota_relativa NUMERIC(6,2)")

        if not table_column_names_list.__contains__('quota_abs'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN quota_abs   NUMERIC(6,2)")

        if not table_column_names_list.__contains__('ref_tm'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN ref_tm text DEFAULT '' ")

        if not table_column_names_list.__contains__('ref_ra'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN ref_ra text DEFAULT '' ")

        if not table_column_names_list.__contains__('ref_n'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN ref_n text DEFAULT '' ")

        if not table_column_names_list.__contains__('posizione'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN posizione text DEFAULT '' ")

        if not table_column_names_list.__contains__('criteri_distinzione'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN criteri_distinzione text DEFAULT '' ")

        if not table_column_names_list.__contains__('modo_formazione'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN modo_formazione text DEFAULT '' ")

        if not table_column_names_list.__contains__('componenti_organici'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN componenti_organici text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('componenti_inorganici'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN componenti_inorganici text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('lunghezza_max'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN lunghezza_max NUMERIC(6,2)")

        if not table_column_names_list.__contains__('altezza_max'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN altezza_max NUMERIC(6,2)")

        if not table_column_names_list.__contains__('altezza_min'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN altezza_min NUMERIC(6,2)")

        if not table_column_names_list.__contains__('profondita_max'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN profondita_max NUMERIC(6,2)")

        if not table_column_names_list.__contains__('profondita_min'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN profondita_min NUMERIC(6,2)")

        if not table_column_names_list.__contains__('larghezza_media'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN larghezza_media NUMERIC(6,2)")

        if not table_column_names_list.__contains__('quota_max_abs'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN quota_max_abs NUMERIC(6,2)")

        if not table_column_names_list.__contains__('quota_max_rel'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN quota_max_rel NUMERIC(6,2)")

        if not table_column_names_list.__contains__('quota_min_abs'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN quota_min_abs NUMERIC(6,2)")

        if not table_column_names_list.__contains__('quota_min_rel'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN quota_min_rel NUMERIC(6,2)")

        if not table_column_names_list.__contains__('osservazioni'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN osservazioni text DEFAULT '' ")

        if not table_column_names_list.__contains__('datazione'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN datazione text DEFAULT '' ")

        if not table_column_names_list.__contains__('flottazione'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN flottazione text DEFAULT '' ")

        if not table_column_names_list.__contains__('setacciatura'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN setacciatura text DEFAULT '' ")

        if not table_column_names_list.__contains__('affidabilita'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN affidabilita text DEFAULT '' ")

        if not table_column_names_list.__contains__('direttore_us'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN direttore_us text DEFAULT '' ")

        if not table_column_names_list.__contains__('responsabile_us'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN responsabile_us text DEFAULT '' ")

        if not table_column_names_list.__contains__('cod_ente_schedatore'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN cod_ente_schedatore text DEFAULT '' ")

        if not table_column_names_list.__contains__('data_rilevazione'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN data_rilevazione text DEFAULT '' ")

        if not table_column_names_list.__contains__('data_rielaborazione'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN data_rielaborazione text DEFAULT '' ")

        if not table_column_names_list.__contains__('lunghezza_usm'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN lunghezza_usm NUMERIC(6,2)")

        if not table_column_names_list.__contains__('altezza_usm'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN altezza_usm NUMERIC(6,2)")

        if not table_column_names_list.__contains__('spessore_usm'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN spessore_usm NUMERIC(6,2)")

        if not table_column_names_list.__contains__('tecnica_muraria_usm'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN tecnica_muraria_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('modulo_usm'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN modulo_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('campioni_malta_usm'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN campioni_malta_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('campioni_mattone_usm'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN campioni_mattone_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('campioni_pietra_usm'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN campioni_pietra_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('provenienza_materiali_usm'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN provenienza_materiali_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('criteri_distinzione_usm'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN criteri_distinzione_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('uso_primario_usm'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN uso_primario_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('doc_usv'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN doc_usv text DEFAULT '' ")

        #############nuovi##############################################################
        if not table_column_names_list.__contains__('tipologia_opera'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN tipologia_opera text DEFAULT '' ")

        if not table_column_names_list.__contains__('sezione_muraria'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN sezione_muraria text DEFAULT '' ")
        if not table_column_names_list.__contains__('superficie_analizzata'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN superficie_analizzata text DEFAULT '' ")
        if not table_column_names_list.__contains__('orientamento'):
                self.engine.execute("ALTER TABLE us_table ADD COLUMN orientamento text DEFAULT '' ")
        if not table_column_names_list.__contains__('materiali_lat'):
                self.engine.execute("ALTER TABLE us_table ADD COLUMN materiali_lat text DEFAULT '' ")
        if not table_column_names_list.__contains__('lavorazione_lat'):
                self.engine.execute("ALTER TABLE us_table ADD COLUMN lavorazione_lat text DEFAULT '' ")
        if not table_column_names_list.__contains__('consistenza_lat'):
                self.engine.execute("ALTER TABLE us_table ADD COLUMN consistenza_lat text DEFAULT '' ")
        if not table_column_names_list.__contains__('forma_lat'):
                self.engine.execute("ALTER TABLE us_table ADD COLUMN forma_lat text DEFAULT '' ")
        if not table_column_names_list.__contains__('colore_lat'):
                self.engine.execute("ALTER TABLE us_table ADD COLUMN colore_lat text DEFAULT '' ")
        if not table_column_names_list.__contains__('impasto_lat'):
                self.engine.execute("ALTER TABLE us_table ADD COLUMN impasto_lat text DEFAULT '' ")


        if not table_column_names_list.__contains__('forma_p'):
                self.engine.execute("ALTER TABLE us_table ADD COLUMN forma_p text DEFAULT '' ")
        if not table_column_names_list.__contains__('colore_p'):
                self.engine.execute("ALTER TABLE us_table ADD COLUMN colore_p text DEFAULT '' ")
        if not table_column_names_list.__contains__('taglio_p'):
                self.engine.execute("ALTER TABLE us_table ADD COLUMN taglio_p text DEFAULT '' ")
        if not table_column_names_list.__contains__('posa_opera_p'):
                self.engine.execute("ALTER TABLE us_table ADD COLUMN posa_opera_p text DEFAULT '' ")
        if not table_column_names_list.__contains__('inerti_usm'):
                self.engine.execute("ALTER TABLE us_table ADD COLUMN inerti_usm text DEFAULT '' ")
        if not table_column_names_list.__contains__('tipo_legante_usm'):
                self.engine.execute("ALTER TABLE us_table ADD COLUMN tipo_legante_usm text DEFAULT '' ")
        if not table_column_names_list.__contains__('rifinitura_usm'):
                self.engine.execute("ALTER TABLE us_table ADD COLUMN rifinitura_usm text DEFAULT '' ")
        if not table_column_names_list.__contains__('materiale_p'):
                self.engine.execute("ALTER TABLE us_table ADD COLUMN materiale_p text DEFAULT '' ")
        if not table_column_names_list.__contains__('consistenza_p'):
                self.engine.execute("ALTER TABLE us_table ADD COLUMN consistenza_p text DEFAULT '' ")                    
        if not table_column_names_list.__contains__('rapporti2'):
            self.engine.execute("ALTER TABLE us_table ADD COLUMN rapporti2 text DEFAULT '' ")

        # try:
            # self.engine.execute("ALTER TABLE us_table ADD CONSTRAINT ID_us_unico UNIQUE (unita_tipo);")
        # except:
            # pass
        ####pyarchinit_thesaurus_sigle
        table = safe_load_table("pyarchinit_thesaurus_sigle")
        if table is None:
            return
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('lingua'):
            self.engine.execute("ALTER TABLE pyarchinit_thesaurus_sigle ADD COLUMN lingua text DEFAULT '' ")



        ####periodizzazione_table
        table = safe_load_table("periodizzazione_table")
        if table is None:
            return
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('cont_per'):
            self.engine.execute("ALTER TABLE periodizzazione_table ADD COLUMN cont_per BIGINT DEFAULT '' ")
        # if not table_column_names_list.__contains__('area'):
            # self.engine.execute("ALTER TABLE periodizzazione_table ADD COLUMN area BIGINT")

        ####tomba_table
        table = safe_load_table("tomba_table")
        if table is None:
            return
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('periodo_iniziale'):
            self.engine.execute("ALTER TABLE tomba_table ADD COLUMN periodo_iniziale BIGINT")

        if not table_column_names_list.__contains__('fase_iniziale'):
            self.engine.execute("ALTER TABLE tomba_table ADD COLUMN fase_iniziale BIGINT")

        if not table_column_names_list.__contains__('periodo_finale'):
            self.engine.execute("ALTER TABLE tomba_table ADD COLUMN periodo_finale BIGINT")

        if not table_column_names_list.__contains__('fase_finale'):
            self.engine.execute("ALTER TABLE tomba_table ADD COLUMN fase_finale BIGINT")

        if not table_column_names_list.__contains__('datazione_estesa'):
            self.engine.execute("ALTER TABLE tomba_table ADD COLUMN datazione_estesa text")

        ####individui_table
        table = safe_load_table("individui_table")
        if table is None:
            return
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('sigla_struttura'):
            self.engine.execute("ALTER TABLE individui_table ADD COLUMN sigla_struttura text")

        if not table_column_names_list.__contains__('nr_struttura'):
            self.engine.execute("ALTER TABLE individui_table ADD COLUMN nr_struttura text")

        if not table_column_names_list.__contains__('completo_si_no'):
            self.engine.execute("ALTER TABLE individui_table ADD COLUMN completo_si_no varchar")

        if not table_column_names_list.__contains__('disturbato_si_no'):
            self.engine.execute("ALTER TABLE individui_table ADD COLUMN disturbato_si_no varchar")

        if not table_column_names_list.__contains__('in_connessione_si_no'):
            self.engine.execute("ALTER TABLE individui_table ADD COLUMN in_connessione_si_no varchar")

        if not table_column_names_list.__contains__('lunghezza_scheletro'):
            self.engine.execute("ALTER TABLE individui_table ADD COLUMN lunghezza_scheletro NUMERIC(6,2)")

        if not table_column_names_list.__contains__('posizione_scheletro'):
            self.engine.execute("ALTER TABLE individui_table ADD COLUMN posizione_scheletro varchar")

        if not table_column_names_list.__contains__('posizione_cranio'):
            self.engine.execute("ALTER TABLE individui_table ADD COLUMN posizione_cranio varchar")

        if not table_column_names_list.__contains__('posizione_arti_superiori'):
            self.engine.execute("ALTER TABLE individui_table ADD COLUMN posizione_arti_superiori varchar")

        if not table_column_names_list.__contains__('posizione_arti_inferiori'):
            self.engine.execute("ALTER TABLE individui_table ADD COLUMN posizione_arti_inferiori varchar")

        if not table_column_names_list.__contains__('orientamento_asse'):
            self.engine.execute("ALTER TABLE individui_table ADD COLUMN orientamento_asse text")

        if not table_column_names_list.__contains__('orientamento_azimut'):
            self.engine.execute("ALTER TABLE individui_table ADD COLUMN orientamento_azimut text")
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
        table = safe_load_table("periodizzazione_table")
        if table is None:
            return
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
        table = safe_load_table("pyunitastratigrafiche")
        if table is None:
            return
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))
        # if table_column_names_list.__contains__('rilievo_orginale'):
            # self.engine.execute("ALTER TABLE pyunitastratigrafiche RENAME COLUMN rilievo_orginale TO rilievo_originale")   

        if not table_column_names_list.__contains__('coord'):
            self.engine.execute("ALTER TABLE pyunitastratigrafiche ADD COLUMN coord text")
        if not table_column_names_list.__contains__('unita_tipo_s'):
            self.engine.execute("ALTER TABLE pyunitastratigrafiche ADD COLUMN unita_tipo_s text")
        # if table_column_names_list.__contains__('id'):
            # self.engine.execute("ALTER TABLE pyunitastratigrafiche RENAME COLUMN id TO gid")

        table = safe_load_table("pyunitastratigrafiche_usm")
        if table is None:
            return
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('unita_tipo_s'):
            self.engine.execute("ALTER TABLE pyunitastratigrafiche_usm ADD COLUMN unita_tipo_s text")


        table = safe_load_table("pyarchinit_quote_usm")
        if table is None:
            return
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('unita_tipo_q'):
            self.engine.execute("ALTER TABLE pyarchinit_quote_usm ADD COLUMN unita_tipo_q text")


        table = safe_load_table("pyarchinit_quote")
        if table is None:
            return
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('unita_tipo_q'):
            self.engine.execute("ALTER TABLE pyarchinit_quote ADD COLUMN unita_tipo_q text")

        table = safe_load_table("pyarchinit_strutture_ipotesi")
        if table is None:
            return
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('sigla_strut'):

            self.engine.execute( "ALTER TABLE pyarchinit_strutture_ipotesi ADD COLUMN sigla_strut varchar(3) DEFAULT 'NoD'")

        if not table_column_names_list.__contains__('nr_strut'):
            self.engine.execute("ALTER TABLE pyarchinit_strutture_ipotesi ADD COLUMN nr_strut BIGINT DEFAULT 0 ")


        table = safe_load_table("pyarchinit_sezioni")
        if table is None:
            return
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('tipo_doc'):
            self.engine.execute("ALTER TABLE pyarchinit_sezioni  ADD COLUMN tipo_doc text")   

        if not table_column_names_list.__contains__('nome_doc'):
            self.engine.execute("ALTER TABLE pyarchinit_sezioni  ADD COLUMN nome_doc text")

        ####campioni_table - Convert US column from INTEGER to TEXT
        table = safe_load_table("campioni_table")
        if table is not None:
            table_column_names_list = []
            for i in table.columns:
                table_column_names_list.append(str(i.name))
            
            # Change US column from INTEGER to TEXT
            try:
                if table_column_names_list.__contains__('us'):
                    # Check if the column is still INTEGER type
                    us_column = None
                    for col in table.columns:
                        if col.name == 'us':
                            us_column = col
                            break
                    
                    if us_column is not None:
                        # Check if column type needs conversion
                        col_type = str(us_column.type)
                        if 'INTEGER' in col_type.upper() or 'BIGINT' in col_type.upper():
                            # Convert the column type
                            self.engine.execute("ALTER TABLE campioni_table ALTER COLUMN us TYPE TEXT USING us::TEXT")
            except Exception as e:
                # Log the error but continue with other updates
                pass

        ####us_table_toimp - Convert US column from INTEGER to TEXT (if table exists)
        try:
            table = safe_load_table("us_table_toimp")
            if table is not None:
                table_column_names_list = []
                for i in table.columns:
                    table_column_names_list.append(str(i.name))
                
                # Change US column from INTEGER to TEXT
                try:
                    if table_column_names_list.__contains__('us'):
                        # Check if the column is still INTEGER type
                        us_column = None
                        for col in table.columns:
                            if col.name == 'us':
                                us_column = col
                                break
                        
                        if us_column is not None:
                            # Check if column type needs conversion
                            col_type = str(us_column.type)
                            if 'INTEGER' in col_type.upper() or 'BIGINT' in col_type.upper():
                                # Convert the column type
                                self.engine.execute("ALTER TABLE us_table_toimp ALTER COLUMN us TYPE TEXT USING us::TEXT")
                except Exception as e:
                    # Log the error but continue with other updates
                    pass
        except:
            # Table might not exist
            pass

        ####pyarchinit_quote - Convert us_q column from INTEGER to TEXT
        table = safe_load_table("pyarchinit_quote")
        if table is not None:
            table_column_names_list = []
            for i in table.columns:
                table_column_names_list.append(str(i.name))
            
            # Change us_q column from INTEGER to TEXT
            try:
                if table_column_names_list.__contains__('us_q'):
                    # Check if the column is still INTEGER type
                    us_column = None
                    for col in table.columns:
                        if col.name == 'us_q':
                            us_column = col
                            break
                    
                    if us_column is not None:
                        # Check if column type needs conversion
                        col_type = str(us_column.type)
                        if 'INTEGER' in col_type.upper() or 'BIGINT' in col_type.upper():
                            # Drop dependent views first
                            try:
                                self.engine.execute("DROP VIEW IF EXISTS pyarchinit_quote_view CASCADE")
                            except:
                                pass
                            
                            # Convert the column type
                            self.engine.execute("ALTER TABLE pyarchinit_quote ALTER COLUMN us_q TYPE TEXT USING us_q::TEXT")
                            
                            # Recreate view
                            try:
                                self.engine.execute("""
                                CREATE VIEW pyarchinit_quote_view AS
                                SELECT 
                                    pyarchinit_quote.gid,
                                    pyarchinit_quote.sito_q, 
                                    pyarchinit_quote.area_q, 
                                    pyarchinit_quote.us_q, 
                                    pyarchinit_quote.unita_misu_q, 
                                    pyarchinit_quote.quota_q, 
                                    pyarchinit_quote.the_geom, 
                                    us_table.id_us, 
                                    us_table.sito, 
                                    us_table.area, 
                                    us_table.us, 
                                    us_table.struttura, 
                                    us_table.d_stratigrafica, 
                                    us_table.d_interpretativa, 
                                    us_table.descrizione, 
                                    us_table.interpretazione, 
                                    us_table.rapporti, 
                                    us_table.periodo_iniziale, 
                                    us_table.fase_iniziale, 
                                    us_table.periodo_finale, 
                                    us_table.fase_finale, 
                                    us_table.anno_scavo
                                FROM pyarchinit_quote
                                JOIN us_table ON 
                                    pyarchinit_quote.sito_q = us_table.sito 
                                    AND pyarchinit_quote.area_q::TEXT = us_table.area::TEXT 
                                    AND pyarchinit_quote.us_q = us_table.us
                                """)
                            except:
                                pass
            except Exception as e:
                # Log the error but continue with other updates
                pass

        ####pyarchinit_quote_usm - Convert us_q column from INTEGER to TEXT
        table = safe_load_table("pyarchinit_quote_usm")
        if table is not None:
            table_column_names_list = []
            for i in table.columns:
                table_column_names_list.append(str(i.name))
            
            # Change us_q column from INTEGER to TEXT
            try:
                if table_column_names_list.__contains__('us_q'):
                    # Check if the column is still INTEGER type
                    us_column = None
                    for col in table.columns:
                        if col.name == 'us_q':
                            us_column = col
                            break
                    
                    if us_column is not None:
                        # Check if column type needs conversion
                        col_type = str(us_column.type)
                        if 'INTEGER' in col_type.upper() or 'BIGINT' in col_type.upper():
                            # Convert the column type
                            self.engine.execute("ALTER TABLE pyarchinit_quote_usm ALTER COLUMN us_q TYPE TEXT USING us_q::TEXT")
            except Exception as e:
                # Log the error but continue with other updates
                pass

        ####pyunitastratigrafiche - Convert us_s column from INTEGER to TEXT
        table = safe_load_table("pyunitastratigrafiche")
        if table is not None:
            table_column_names_list = []
            for i in table.columns:
                table_column_names_list.append(str(i.name))
            
            # Change us_s column from INTEGER to TEXT
            try:
                if table_column_names_list.__contains__('us_s'):
                    # Check if the column is still INTEGER type
                    us_column = None
                    for col in table.columns:
                        if col.name == 'us_s':
                            us_column = col
                            break
                    
                    if us_column is not None:
                        # Check if column type needs conversion
                        col_type = str(us_column.type)
                        if 'INTEGER' in col_type.upper() or 'BIGINT' in col_type.upper():
                            # Drop dependent views first if they exist
                            try:
                                self.engine.execute("DROP VIEW IF EXISTS pyarchinit_us_view CASCADE")
                            except:
                                pass
                            
                            # Convert the column type
                            self.engine.execute("ALTER TABLE pyunitastratigrafiche ALTER COLUMN us_s TYPE TEXT USING us_s::TEXT")
                            
                            # Recreate the view if us_table has already been converted
                            try:
                                self.engine.execute("""
                                CREATE VIEW pyarchinit_us_view AS
                                SELECT 
                                    pyunitastratigrafiche.gid, 
                                    pyunitastratigrafiche.the_geom, 
                                    pyunitastratigrafiche.tipo_us_s, 
                                    pyunitastratigrafiche.scavo_s, 
                                    pyunitastratigrafiche.area_s, 
                                    pyunitastratigrafiche.us_s, 
                                    pyunitastratigrafiche.stratigraph_index_us,
                                    us_table.id_us, 
                                    us_table.sito, 
                                    us_table.area, 
                                    us_table.us, 
                                    us_table.struttura, 
                                    us_table.d_stratigrafica, 
                                    us_table.d_interpretativa, 
                                    us_table.descrizione, 
                                    us_table.interpretazione, 
                                    us_table.rapporti, 
                                    us_table.periodo_iniziale, 
                                    us_table.fase_iniziale, 
                                    us_table.periodo_finale, 
                                    us_table.fase_finale, 
                                    us_table.anno_scavo
                                FROM pyunitastratigrafiche
                                JOIN us_table ON 
                                    pyunitastratigrafiche.scavo_s = us_table.sito 
                                    AND pyunitastratigrafiche.area_s::TEXT = us_table.area::TEXT 
                                    AND pyunitastratigrafiche.us_s = us_table.us
                                """)
                            except:
                                pass
            except Exception as e:
                # Log the error but continue with other updates
                pass

        ####pyunitastratigrafiche_usm - Convert us_s column from INTEGER to TEXT
        table = safe_load_table("pyunitastratigrafiche_usm")
        if table is not None:
            table_column_names_list = []
            for i in table.columns:
                table_column_names_list.append(str(i.name))
            
            # Change us_s column from INTEGER to TEXT
            try:
                if table_column_names_list.__contains__('us_s'):
                    # Check if the column is still INTEGER type
                    us_column = None
                    for col in table.columns:
                        if col.name == 'us_s':
                            us_column = col
                            break
                    
                    if us_column is not None:
                        # Check if column type needs conversion
                        col_type = str(us_column.type)
                        if 'INTEGER' in col_type.upper() or 'BIGINT' in col_type.upper():
                            # Convert the column type
                            self.engine.execute("ALTER TABLE pyunitastratigrafiche_usm ALTER COLUMN us_s TYPE TEXT USING us_s::TEXT")
            except Exception as e:
                # Log the error but continue with other updates
                pass

        ####pyarchinit_us_negative_doc - Convert us_n column from INTEGER to TEXT (if table exists)
        try:
            table = safe_load_table("pyarchinit_us_negative_doc")
            if table is not None:
                table_column_names_list = []
                for i in table.columns:
                    table_column_names_list.append(str(i.name))
                
                # Change us_n column from INTEGER to TEXT
                try:
                    if table_column_names_list.__contains__('us_n'):
                        # Check if the column is still INTEGER type
                        us_column = None
                        for col in table.columns:
                            if col.name == 'us_n':
                                us_column = col
                                break
                        
                        if us_column is not None:
                            # Check if column type needs conversion
                            col_type = str(us_column.type)
                            if 'INTEGER' in col_type.upper() or 'BIGINT' in col_type.upper():
                                # Convert the column type
                                self.engine.execute("ALTER TABLE pyarchinit_us_negative_doc ALTER COLUMN us_n TYPE TEXT USING us_n::TEXT")
                except Exception as e:
                    # Log the error but continue with other updates
                    pass
        except:
            # Table might not exist
            pass

        ####pyuscaratterizzazioni - Convert us_c column from INTEGER to TEXT (if table exists)
        # try:
        #     table = safe_load_table("pyuscaratterizzazioni")
        #     if table is not None:
        #         table_column_names_list = []
        #         for i in table.columns:
        #             table_column_names_list.append(str(i.name))
        #
        #         # Change us_c column from INTEGER to TEXT
        #         try:
        #             if table_column_names_list.__contains__('us_c'):
        #                 # Check if the column is still INTEGER type
        #                 us_column = None
        #                 for col in table.columns:
        #                     if col.name == 'us_c':
        #                         us_column = col
        #                         break
        #
        #                 if us_column is not None:
        #                     # Check if column type needs conversion
        #                     col_type = str(us_column.type)
        #                     if 'INTEGER' in col_type.upper() or 'BIGINT' in col_type.upper():
        #                         # Drop dependent views first if they exist
        #                         try:
        #                             self.engine.execute("DROP VIEW IF EXISTS pyarchinit_uscaratterizzazioni_view CASCADE")
        #                         except:
        #                             pass
        #
        #                         # Convert the column type
        #                         self.engine.execute("ALTER TABLE pyuscaratterizzazioni ALTER COLUMN us_c TYPE TEXT USING us_c::TEXT")
        #
        #                         # Recreate view
        #                         # try:
        #                         #     self.engine.execute("""
        #                         #     CREATE VIEW pyarchinit_uscaratterizzazioni_view AS
        #                         #     SELECT
        #                         #         pyuscaratterizzazioni.gid,
        #                         #         pyuscaratterizzazioni.the_geom,
        #                         #         pyuscaratterizzazioni.tipo_us_c,
        #                         #         pyuscaratterizzazioni.scavo_c,
        #                         #         pyuscaratterizzazioni.area_c,
        #                         #         pyuscaratterizzazioni.us_c,
        #                         #         us_table.sito,
        #                         #         us_table.id_us,
        #                         #         us_table.area,
        #                         #         us_table.us,
        #                         #         us_table.struttura,
        #                         #         us_table.d_stratigrafica,
        #                         #         us_table.d_interpretativa,
        #                         #         us_table.descrizione,
        #                         #         us_table.interpretazione,
        #                         #         us_table.rapporti,
        #                         #         us_table.periodo_iniziale,
        #                         #         us_table.fase_iniziale,
        #                         #         us_table.periodo_finale,
        #                         #         us_table.fase_finale,
        #                         #         us_table.anno_scavo
        #                         #     FROM pyuscaratterizzazioni
        #                         #     JOIN us_table ON
        #                         #         pyuscaratterizzazioni.scavo_c = us_table.sito
        #                         #         AND pyuscaratterizzazioni.area_c::TEXT = us_table.area::TEXT
        #                         #         AND pyuscaratterizzazioni.us_c = us_table.us
        #                         #     """)
        #                         # except:
        #                         #     pass
        #         except Exception as e:
        #             # Log the error but continue with other updates
        #             pass
        # except:
        #     # Table might not exist
        #     pass
        
        # Update thesaurus table structure for PostgreSQL
        try:
            update_thesaurus_table(self.engine, self.metadata)
        except Exception as e:
            print(f"Error updating thesaurus table: {str(e)}")
    
    def _migrate_us_fields_sqlite(self):
        """SQLite-specific migration for US fields from INTEGER to TEXT"""
        try:
            # First, clean up any leftover _new tables from previous failed migrations
            result = self.engine.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_new'")
            for row in result:
                try:
                    self.engine.execute(f"DROP TABLE IF EXISTS {row[0]}")
                except:
                    pass
            
            # Drop all views that depend on tables we're migrating
            views_to_drop = [
                'pyarchinit_quote_usm_view',
                'pyarchinit_quote_view', 
                'pyarchinit_us_view',
                'pyarchinit_usm_view',
                'pyarchinit_uscaratterizzazioni_view',
                'pyarchinit_us_negative_doc_view',
                'pyarchinit_reperti_view',  # This view depends on inventario_materiali_table
                'pyarchinit_tomba_view'  # This view depends on tomba_table
            ]
            
            for view in views_to_drop:
                try:
                    self.engine.execute(f"DROP VIEW IF EXISTS {view}")
                except:
                    pass
            
            # Define tables and fields to migrate
            # Migrate both US and area fields where needed
            migrations = [
                # US field migrations
                ('us_table', ['us', 'area']),
                ('campioni_table', ['us', 'area']),
                ('pottery_table', ['us', 'area']),
                ('inventario_materiali_table', ['us', 'area']),
                ('tomba_table', ['area']),  # Only area field
                # Other tables with US fields
                ('us_table_toimp', ['us']),
                ('pyarchinit_quote', ['us_q']),
                ('pyarchinit_quote_usm', ['us_q']),
                ('pyunitastratigrafiche', ['us_s']),
                ('pyunitastratigrafiche_usm', ['us_s']),
                ('pyarchinit_us_negative_doc', ['us_n']),
                ('pyuscaratterizzazioni', ['us_c'])
            ]
            
            # Process each table
            for table_name, fields_to_migrate in migrations:
                try:
                    # Check if table exists
                    check_exists = self.engine.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                    if not check_exists.fetchone():
                        continue
                    
                    # Check which fields need migration
                    needs_migration = False
                    result = self.engine.execute(f"PRAGMA table_info({table_name})")
                    columns_info = result.fetchall()
                    
                    for col in columns_info:
                        col_name = col[1]
                        col_type = col[2].upper()
                        if col_name in fields_to_migrate and ('INTEGER' in col_type or 'BIGINT' in col_type):
                            needs_migration = True
                            break
                    
                    if needs_migration:
                        self._migrate_sqlite_table_fields(table_name, fields_to_migrate, columns_info)
                        
                except Exception as e:
                    print(f"Error migrating table {table_name}: {str(e)}")
                    continue
            
            # Recreate views
            self._recreate_sqlite_views()
            
            # Final cleanup - remove any remaining _new tables
            result = self.engine.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_new'")
            for row in result:
                try:
                    self.engine.execute(f"DROP TABLE IF EXISTS {row[0]}")
                except:
                    pass
            
            # Migration completed silently - no message box needed
            
        except Exception as e:
            QMessageBox.warning(None, "Errore Migrazione SQLite", 
                              f"Errore durante la migrazione SQLite del campo US.\n"
                              f"Dettagli: {str(e)}", QMessageBox.Ok)
    
    def _migrate_sqlite_table(self, table_name, us_field):
        """Migrate a single SQLite table by recreating it with TEXT type for US field"""
        try:
            # Get current table structure
            result = self.engine.execute(f"PRAGMA table_info({table_name})")
            columns = result.fetchall()
            
            # Build new table definition
            new_table_sql = f"CREATE TABLE {table_name}_new ("
            column_defs = []
            
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                col_notnull = col[3]
                col_default = col[4]
                col_pk = col[5]
                
                # Change US field type to TEXT
                if col_name == us_field:
                    col_type = 'TEXT'
                
                col_def = f"{col_name} {col_type}"
                
                if col_pk:
                    col_def += " PRIMARY KEY"
                    if table_name in ['us_table', 'campioni_table', 'pottery_table'] and col_name.startswith('id_'):
                        col_def += " AUTOINCREMENT"
                
                if col_notnull and not col_pk:
                    col_def += " NOT NULL"
                    
                if col_default is not None:
                    col_def += f" DEFAULT {col_default}"
                    
                column_defs.append(col_def)
            
            new_table_sql += ", ".join(column_defs) + ")"
            
            # Create new table
            self.engine.execute(new_table_sql)
            
            # Copy data, converting US field to TEXT
            columns_list = [col[1] for col in columns]
            columns_str = ", ".join(columns_list)
            
            # Build select list with CAST for US field
            select_list = []
            for col_name in columns_list:
                if col_name == us_field:
                    select_list.append(f"CAST({col_name} AS TEXT)")
                else:
                    select_list.append(col_name)
            select_str = ", ".join(select_list)
            
            self.engine.execute(f"INSERT INTO {table_name}_new SELECT {select_str} FROM {table_name}")
            
            # Drop old table and rename new one
            self.engine.execute(f"DROP TABLE {table_name}")
            self.engine.execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name}")
            
            # Create index on US field
            self.engine.execute(f"CREATE INDEX idx_{table_name}_{us_field} ON {table_name}({us_field})")
            
        except Exception as e:
            raise Exception(f"Errore durante la migrazione della tabella {table_name}: {str(e)}")
    
    def _migrate_sqlite_table_fields(self, table_name, fields_to_migrate, columns_info):
        """Migrate multiple fields in a single SQLite table by recreating it with TEXT type"""
        try:
            # Build new table definition
            new_table_sql = f"CREATE TABLE {table_name}_new ("
            column_defs = []
            
            for col in columns_info:
                col_id = col[0]
                col_name = col[1]
                col_type = col[2]
                col_notnull = col[3]
                col_default = col[4]
                col_pk = col[5]
                
                # Change field type to TEXT if it's in the migration list
                if col_name in fields_to_migrate:
                    col_type = 'TEXT'
                
                col_def = f"{col_name} {col_type}"
                
                if col_pk:
                    col_def += " PRIMARY KEY"
                    if table_name in ['us_table', 'campioni_table', 'pottery_table', 'inventario_materiali_table', 'tomba_table'] and col_name.startswith('id_'):
                        col_def += " AUTOINCREMENT"
                
                if col_notnull and not col_pk:
                    col_def += " NOT NULL"
                    
                if col_default is not None:
                    col_def += f" DEFAULT {col_default}"
                    
                column_defs.append(col_def)
            
            new_table_sql += ", ".join(column_defs) + ")"
            
            # Create new table
            self.engine.execute(new_table_sql)
            
            # Copy data, converting fields to TEXT
            columns_list = [col[1] for col in columns_info]
            
            # Build select list with CAST for fields to migrate
            select_list = []
            for col_name in columns_list:
                if col_name in fields_to_migrate:
                    # Handle NULL values properly
                    select_list.append(f"CASE WHEN {col_name} IS NULL THEN NULL ELSE CAST({col_name} AS TEXT) END")
                else:
                    select_list.append(col_name)
            select_str = ", ".join(select_list)
            
            # Use INSERT with explicit column list to handle potential column order differences
            columns_str = ", ".join(columns_list)
            self.engine.execute(f"INSERT INTO {table_name}_new ({columns_str}) SELECT {select_str} FROM {table_name}")
            
            # Drop old table and rename new one
            self.engine.execute(f"DROP TABLE {table_name}")
            self.engine.execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name}")
            
            # Create indexes on migrated fields
            for field in fields_to_migrate:
                try:
                    self.engine.execute(f"CREATE INDEX idx_{table_name}_{field} ON {table_name}({field})")
                except:
                    pass  # Index might already exist
            
        except Exception as e:
            # If something goes wrong, clean up the _new table
            try:
                self.engine.execute(f"DROP TABLE IF EXISTS {table_name}_new")
            except:
                pass
            raise Exception(f"Errore durante la migrazione della tabella {table_name}: {str(e)}")
    
    def _recreate_sqlite_views(self):
        """Recreate SQLite views after migration"""
        views_sql = {
            'pyarchinit_quote_view': """
                CREATE VIEW pyarchinit_quote_view AS
                SELECT 
                    pyarchinit_quote.gid,
                    pyarchinit_quote.sito_q, 
                    pyarchinit_quote.area_q, 
                    pyarchinit_quote.us_q, 
                    pyarchinit_quote.unita_misu_q, 
                    pyarchinit_quote.quota_q, 
                    pyarchinit_quote.the_geom, 
                    us_table.id_us, 
                    us_table.sito, 
                    us_table.area, 
                    us_table.us, 
                    us_table.struttura, 
                    us_table.d_stratigrafica, 
                    us_table.d_interpretativa, 
                    us_table.descrizione, 
                    us_table.interpretazione, 
                    us_table.rapporti, 
                    us_table.periodo_iniziale, 
                    us_table.fase_iniziale, 
                    us_table.periodo_finale, 
                    us_table.fase_finale, 
                    us_table.anno_scavo
                FROM pyarchinit_quote
                JOIN us_table ON 
                    pyarchinit_quote.sito_q = us_table.sito 
                    AND pyarchinit_quote.area_q = us_table.area 
                    AND pyarchinit_quote.us_q = us_table.us
            """,
            
            'pyarchinit_us_view': """
                CREATE VIEW pyarchinit_us_view AS 
                SELECT 
                    CAST(pyunitastratigrafiche.gid AS INTEGER) as gid, 
                    pyunitastratigrafiche.the_geom as the_geom, 
                    pyunitastratigrafiche.tipo_us_s as tipo_us_s, 
                    pyunitastratigrafiche.scavo_s as scavo_s, 
                    pyunitastratigrafiche.area_s as area_s, 
                    pyunitastratigrafiche.us_s as us_s, 
                    pyunitastratigrafiche.stratigraph_index_us as stratigraph_index_us,
                    us_table.id_us as id_us, 
                    us_table.sito as sito, 
                    us_table.area as area, 
                    us_table.us as us, 
                    us_table.struttura as struttura, 
                    us_table.d_stratigrafica as d_stratigrafica, 
                    us_table.d_interpretativa as d_interpretativa, 
                    us_table.descrizione as descrizione, 
                    us_table.interpretazione as interpretazione, 
                    us_table.rapporti as rapporti, 
                    us_table.periodo_iniziale as periodo_iniziale, 
                    us_table.fase_iniziale as fase_iniziale, 
                    us_table.periodo_finale as periodo_finale, 
                    us_table.fase_finale as fase_finale, 
                    us_table.anno_scavo as anno_scavo,
                    pyunitastratigrafiche.ROWID as ROWID
                FROM pyunitastratigrafiche
                JOIN us_table ON 
                    pyunitastratigrafiche.scavo_s = us_table.sito 
                    AND pyunitastratigrafiche.area_s = us_table.area 
                    AND pyunitastratigrafiche.us_s = us_table.us
            """,
            
            'pyarchinit_uscaratterizzazioni_view': """
                CREATE VIEW pyarchinit_uscaratterizzazioni_view AS
                SELECT 
                    pyuscaratterizzazioni.gid,
                    pyuscaratterizzazioni.the_geom, 
                    pyuscaratterizzazioni.tipo_us_c, 
                    pyuscaratterizzazioni.scavo_c, 
                    pyuscaratterizzazioni.area_c, 
                    pyuscaratterizzazioni.us_c, 
                    us_table.sito, 
                    us_table.id_us, 
                    us_table.area, 
                    us_table.us, 
                    us_table.struttura, 
                    us_table.d_stratigrafica, 
                    us_table.d_interpretativa, 
                    us_table.descrizione, 
                    us_table.interpretazione, 
                    us_table.rapporti, 
                    us_table.periodo_iniziale, 
                    us_table.fase_iniziale, 
                    us_table.periodo_finale, 
                    us_table.fase_finale, 
                    us_table.anno_scavo
                FROM pyuscaratterizzazioni
                JOIN us_table ON 
                    pyuscaratterizzazioni.scavo_c = us_table.sito 
                    AND pyuscaratterizzazioni.area_c = us_table.area 
                    AND pyuscaratterizzazioni.us_c = us_table.us
            """,
            
            'pyarchinit_reperti_view': """
                CREATE VIEW pyarchinit_reperti_view AS 
                SELECT
                    a.gid,
                    a.the_geom,
                    a.id_rep,
                    a.siti,
                    b.id_invmat,
                    b.sito,
                    b.numero_inventario,
                    b.tipo_reperto,
                    b.criterio_schedatura,
                    b.definizione,
                    b.descrizione,
                    b.area,
                    b.us,
                    b.lavato,
                    b.nr_cassa,
                    b.luogo_conservazione,
                    b.stato_conservazione,
                    b.datazione_reperto,
                    b.elementi_reperto,
                    b.misurazioni,
                    b.rif_biblio,
                    b.tecnologie,
                    b.forme_minime,
                    b.forme_massime,
                    b.totale_frammenti,
                    b.corpo_ceramico,
                    b.rivestimento,
                    b.diametro_orlo,
                    b.peso,
                    b.tipo,
                    b.eve_orlo,
                    b.repertato,
                    b.diagnostico,
                    b.n_reperto,
                    b.tipo_contenitore,
                    b.struttura,
                    b.years,
                    b.schedatore,
                    b.date_scheda,
                    b.punto_rinv,
                    b.negativo_photo,
                    b.diapositiva
                FROM pyarchinit_reperti a
                JOIN inventario_materiali_table b ON 
                    a.siti = b.sito AND 
                    a.id_rep = b.numero_inventario
            """,
            
            'pyarchinit_tomba_view': """
                CREATE VIEW pyarchinit_tomba_view AS
                SELECT 
                    a.id_tomba,
                    a.sito,
                    a.nr_scheda_taf,
                    a.sigla_struttura,
                    a.nr_struttura,
                    a.nr_individuo,
                    a.rito,
                    a.descrizione_taf,
                    a.interpretazione_taf,
                    a.segnacoli,
                    a.canale_libatorio_si_no,
                    a.oggetti_rinvenuti_esterno,
                    a.stato_conservazione,
                    a.copertura_tipo,
                    a.tipo_contenitore_resti,
                    a.orientamento_asse,
                    a.orientamento_azimut,
                    a.corredo_presenza,
                    a.corredo_tipo,
                    a.corredo_descrizione,
                    a.periodo_iniziale,
                    a.fase_iniziale,
                    a.periodo_finale,
                    a.fase_finale,
                    a.datazione_estesa,
                    a.misure_tomba,
                    a.quote,
                    a.area,
                    b.gid,
                    b.id_tafonomia_pk,
                    b.sito AS sito_1,
                    b.nr_scheda,
                    b.the_geom
                FROM tomba_table a
                LEFT JOIN pyarchinit_tafonomia b ON 
                    a.sito = b.sito::text AND 
                    a.nr_scheda_taf = b.nr_scheda
            """
        }
        
        for view_name, view_sql in views_sql.items():
            try:
                self.engine.execute(view_sql)
            except:
                # View might not be needed or table might not exist
                pass
        
        # Register views in SpatiaLite geometry metadata
        self._register_spatialite_views()
    
    def _register_spatialite_views(self):
        """Register views in SpatiaLite geometry metadata tables"""
        try:
            # Check if we have views_geometry_columns table (newer SpatiaLite)
            result = self.engine.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='views_geometry_columns'
            """)
            
            if result.fetchone():
                # Register pyarchinit_us_view
                try:
                    # Remove any existing registration
                    self.engine.execute("""
                        DELETE FROM views_geometry_columns 
                        WHERE view_name = 'pyarchinit_us_view'
                    """)
                    
                    # Register the view (view_rowid must be lowercase)
                    self.engine.execute("""
                        INSERT INTO views_geometry_columns 
                        (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only)
                        VALUES 
                        ('pyarchinit_us_view', 'the_geom', 'rowid', 'pyunitastratigrafiche', 'the_geom', 1)
                    """)
                except:
                    pass
            else:
                # Fallback: Register directly in geometry_columns for older SpatiaLite
                try:
                    # Get geometry info from source table
                    result = self.engine.execute("""
                        SELECT coord_dimension, srid, geometry_type 
                        FROM geometry_columns 
                        WHERE f_table_name = 'pyunitastratigrafiche' 
                        AND f_geometry_column = 'the_geom'
                    """)
                    
                    geo_info = result.fetchone()
                    if geo_info:
                        # Remove any existing registration
                        self.engine.execute("""
                            DELETE FROM geometry_columns 
                            WHERE f_table_name = 'pyarchinit_us_view'
                        """)
                        
                        # Register the view
                        self.engine.execute("""
                            INSERT INTO geometry_columns 
                            (f_table_name, f_geometry_column, coord_dimension, srid, geometry_type)
                            VALUES 
                            ('pyarchinit_us_view', 'the_geom', ?, ?, ?)
                        """, geo_info)
                except:
                    pass
                
                # Register other geometry views
                other_views = [
                    ('pyarchinit_quote_view', 'pyarchinit_quote'),
                    ('pyarchinit_uscaratterizzazioni_view', 'pyuscaratterizzazioni'),
                    ('pyarchinit_reperti_view', 'pyarchinit_reperti'),
                    ('pyarchinit_tomba_view', 'pyarchinit_tafonomia')
                ]
                
                for view_name, source_table in other_views:
                    try:
                        self.engine.execute(f"""
                            DELETE FROM views_geometry_columns 
                            WHERE view_name = '{view_name}'
                        """)
                        
                        self.engine.execute(f"""
                            INSERT INTO views_geometry_columns 
                            (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only)
                            VALUES 
                            ('{view_name}', 'the_geom', 'gid', '{source_table}', 'the_geom', 1)
                        """)
                    except:
                        pass
            
            # Also update geometry_columns_auth if it exists
            result = self.engine.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='geometry_columns_auth'
            """)
            
            if result.fetchone():
                # Register views in geometry_columns_auth
                views_to_register = [
                    'pyarchinit_us_view',
                    'pyarchinit_quote_view',
                    'pyarchinit_uscaratterizzazioni_view',
                    'pyarchinit_reperti_view',
                    'pyarchinit_tomba_view'
                ]
                
                for view_name in views_to_register:
                    try:
                        # Get SRID from source table
                        if view_name == 'pyarchinit_us_view':
                            source_table = 'pyunitastratigrafiche'
                        elif view_name == 'pyarchinit_quote_view':
                            source_table = 'pyarchinit_quote'
                        elif view_name == 'pyarchinit_uscaratterizzazioni_view':
                            source_table = 'pyuscaratterizzazioni'
                        elif view_name == 'pyarchinit_reperti_view':
                            source_table = 'pyarchinit_reperti'
                        elif view_name == 'pyarchinit_tomba_view':
                            source_table = 'pyarchinit_tafonomia'
                        else:
                            continue
                        
                        # Get SRID from source
                        result = self.engine.execute(f"""
                            SELECT srid FROM geometry_columns_auth 
                            WHERE f_table_name = '{source_table}' 
                            AND f_geometry_column = 'the_geom'
                        """)
                        
                        row = result.fetchone()
                        if row:
                            srid = row[0]
                            
                            # Remove existing entry
                            self.engine.execute(f"""
                                DELETE FROM geometry_columns_auth 
                                WHERE f_table_name = '{view_name}'
                            """)
                            
                            # Add new entry
                            self.engine.execute(f"""
                                INSERT INTO geometry_columns_auth 
                                (f_table_name, f_geometry_column, read_only, hidden, srid, auth_name, auth_srid)
                                VALUES 
                                ('{view_name}', 'the_geom', 1, 0, {srid}, 'EPSG', {srid})
                            """)
                    except:
                        pass
        
        except Exception as e:
            # Log but don't fail - view registration is not critical
            print(f"Warning: Could not register views in SpatiaLite metadata: {str(e)}")
    
    def _migrate_tma_table(self):
        """Migrate old TMA table structure to new structure with separate materials table"""
        try:
            print("Starting TMA table migration...")
            
            # Backup existing data
            old_data = self.engine.execute("SELECT * FROM tma_table").fetchall()
            print(f"Found {len(old_data)} records to migrate")
            
            # Drop the old table
            self.engine.execute("DROP TABLE IF EXISTS tma_table")
            
            # The new tables will be created automatically by the mapper
            # Force import to trigger table creation
            from modules.db.structures.Tma_table import Tma_table
            from modules.db.structures.Tma_materiali_table import Tma_materiali_table
            
            # Migrate data
            from sqlalchemy.orm import sessionmaker
            Session = sessionmaker(bind=self.engine)
            session = Session()
            
            migrated_count = 0
            for row in old_data:
                try:
                    # Map old fields to new structure
                    # Insert main TMA record
                    new_values = {
                        'id': row[0] if len(row) > 0 else None,
                        'sito': row[1] if len(row) > 1 else '',
                        'area': row[2] if len(row) > 2 else '',
                        'ogtm': row[4] if len(row) > 4 else '',  # oggetto field
                        'ldct': '',
                        'ldcn': row[3] if len(row) > 3 else '',  # us field
                        'vecchia_collocazione': row[34] if len(row) > 34 else '',
                        'cassetta': row[33] if len(row) > 33 else '',  # nr_cassa
                        'localita': row[5] if len(row) > 5 else '',
                        'scan': row[7] if len(row) > 7 else '',  # nome_scavo
                        'saggio': row[6] if len(row) > 6 else '',
                        'vano_locus': row[8] if len(row) > 8 else '',  # vano
                        'dscd': row[9] if len(row) > 9 else '',  # data_scavo
                        'dscu': row[3] if len(row) > 3 else '',  # us
                        'rcgd': '',
                        'rcgz': '',
                        'aint': '',
                        'aind': '',
                        'dtzg': row[32] if len(row) > 32 else '',  # cronologia
                        'deso': row[20] if len(row) > 20 else '',  # definizione
                        'nsc': '',
                        'ftap': '',
                        'ftan': '',
                        'drat': '',
                        'dran': '',
                        'draa': '',
                        'created_at': '',
                        'updated_at': '',
                        'created_by': 'migration',
                        'updated_by': 'migration'
                    }
                    
                    # Remove localita from new_values if present
                    if 'localita' in new_values:
                        del new_values['localita']
                    
                    # Insert the main record
                    self.engine.execute("""
                        INSERT INTO tma_materiali_archeologici 
                        (id, sito, area, ogtm, ldct, ldcn, vecchia_collocazione, cassetta,
                         scan, saggio, vano_locus, dscd, dscu, rcgd, rcgz,
                         aint, aind, dtzg, deso, nsc, ftap, ftan, drat, dran, draa,
                         created_at, updated_at, created_by, updated_by)
                        VALUES 
                        (:id, :sito, :area, :ogtm, :ldct, :ldcn, :vecchia_collocazione, :cassetta,
                         :scan, :saggio, :vano_locus, :dscd, :dscu, :rcgd, :rcgz,
                         :aint, :aind, :dtzg, :deso, :nsc, :ftap, :ftan, :drat, :dran, :draa,
                         :created_at, :updated_at, :created_by, :updated_by)
                    """, new_values)
                    
                    # Create material record if there's material data
                    if len(row) > 10 and row[10]:  # elemento field
                        material_values = {
                            'id_tma': new_values['id'],
                            'madi': row[18] if len(row) > 18 else '',  # numero_inventario_serie
                            'macc': row[10] if len(row) > 10 else '',  # elemento
                            'macl': row[11] if len(row) > 11 else '',  # tipo
                            'macp': '',
                            'macd': row[20] if len(row) > 20 else '',  # definizione
                            'cronologia_mac': row[32] if len(row) > 32 else '',  # cronologia
                            'macq': str(row[16]) if len(row) > 16 else '0',  # quantita
                            'peso': float(row[25]) if len(row) > 25 and row[25] else 0.0,
                            'created_at': '',
                            'updated_at': '',
                            'created_by': 'migration',
                            'updated_by': 'migration'
                        }
                        
                        self.engine.execute("""
                            INSERT INTO tma_materiali_ripetibili
                            (id_tma, madi, macc, macl, macp, macd, cronologia_mac, macq, peso,
                             created_at, updated_at, created_by, updated_by)
                            VALUES
                            (:id_tma, :madi, :macc, :macl, :macp, :macd, :cronologia_mac, :macq, :peso,
                             :created_at, :updated_at, :created_by, :updated_by)
                        """, material_values)
                    
                    migrated_count += 1
                    
                except Exception as e:
                    print(f"Error migrating record {row[0] if row else 'unknown'}: {str(e)}")
                    continue
            
            session.close()
            print(f"TMA migration completed. Migrated {migrated_count} out of {len(old_data)} records")
            
        except Exception as e:
            print(f"TMA migration failed: {str(e)}")
            # Don't raise - let the process continue
    

    
    def _ensure_tma_tables_exist(self):
        """Ensure TMA tables exist with correct structure and in correct order"""
        try:
            from sqlalchemy import MetaData, inspect
            
            # Get the inspector to check existing tables
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names()
            
            # Check if parent table exists
            if 'tma_materiali_archeologici' not in existing_tables:
                # Import and create parent table first
                from modules.db.structures_metadata.Tma_table import Tma_table
                metadata = MetaData()
                tma_table = Tma_table.define_table(metadata)
                metadata.create_all(self.engine)
                print("Created tma_materiali_archeologici table")
            
            # Check if child table exists
            if 'tma_materiali_ripetibili' not in existing_tables:
                # Import and create child table
                from modules.db.structures_metadata.Tma_materiali_table import Tma_materiali_table
                metadata = MetaData()
                tma_materiali_table = Tma_materiali_table.define_table(metadata)
                metadata.create_all(self.engine)
                print("Created tma_materiali_ripetibili table")
            
        except Exception as e:
            print(f"Error ensuring TMA tables exist: {str(e)}")
