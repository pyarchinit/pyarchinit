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
import time
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
        self.conn_str = conn_str
        self.engine = create_engine(conn_str, echo=False)
        self.metadata = MetaData()

    def _execute(self, sql):
        """SQLAlchemy 2.0 compatible execute wrapper.

        Handles common DDL errors gracefully (duplicate column, table exists, etc.)
        to maintain backward compatibility with the old engine.execute() behavior.
        """
        from sqlalchemy import text
        from sqlalchemy.exc import ProgrammingError, OperationalError

        class ResultWrapper:
            """Wrapper to maintain compatibility with old engine.execute() API"""
            def __init__(self, rows):
                self._rows = list(rows) if rows else []
                self._index = 0

            def fetchall(self):
                return self._rows

            def fetchone(self):
                if self._index < len(self._rows):
                    row = self._rows[self._index]
                    self._index += 1
                    return row
                return None

            def __iter__(self):
                return iter(self._rows)

        try:
            # Use begin() for auto-commit DDL statements
            with self.engine.begin() as conn:
                result = conn.execute(text(sql) if isinstance(sql, str) else sql)
                try:
                    rows = result.fetchall()
                    return ResultWrapper(rows)
                except:
                    return ResultWrapper([])
        except (ProgrammingError, OperationalError) as e:
            # Handle common DDL errors that should be ignored:
            # - DuplicateColumn: column already exists (PostgreSQL)
            # - duplicate column name (SQLite)
            # - table already exists
            error_str = str(e).lower()

            # Check for ignorable errors in all supported languages
            # English
            is_ignorable = (
                'duplicate column' in error_str or
                'already exists' in error_str or
                'duplicate key' in error_str or
                'duplicatecolumn' in error_str or  # psycopg2 error class name
                ('column' in error_str and 'exists' in error_str)
            )
            # Italian (it_IT)
            is_ignorable = is_ignorable or (
                'esiste già' in error_str or
                'colonna duplicata' in error_str or
                ('colonna' in error_str and 'esiste' in error_str)
            )
            # German (de_DE)
            is_ignorable = is_ignorable or (
                'existiert bereits' in error_str or
                'doppelte spalte' in error_str or
                'spalte bereits vorhanden' in error_str or
                ('spalte' in error_str and 'existiert' in error_str)
            )
            # Spanish (es_ES)
            is_ignorable = is_ignorable or (
                'ya existe' in error_str or
                'columna duplicada' in error_str or
                ('columna' in error_str and 'existe' in error_str)
            )
            # French (fr_FR)
            is_ignorable = is_ignorable or (
                'existe déjà' in error_str or
                'colonne en double' in error_str or
                'colonne dupliquée' in error_str or
                ('colonne' in error_str and 'existe' in error_str)
            )
            # Catalan (ca_ES)
            is_ignorable = is_ignorable or (
                'ja existeix' in error_str or
                'columna duplicada' in error_str or
                ('columna' in error_str and 'existeix' in error_str)
            )
            # Portuguese (common in some installations)
            is_ignorable = is_ignorable or (
                'já existe' in error_str or
                'coluna duplicada' in error_str or
                ('coluna' in error_str and 'existe' in error_str)
            )

            if is_ignorable:
                # Silently ignore - column/table already exists
                return ResultWrapper([])
            else:
                # Re-raise unexpected errors
                raise

    def update_table(self):
        # Add debug logging
        import datetime
        log_file = '/Users/enzo/pyarchinit_debug.log'
        def log_debug(msg):
            try:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{timestamp}] [DB_UPDATE] {msg}\n")
                    f.flush()
            except:
                pass

        log_debug("update_table() started")

        def safe_load_table(table_name):
            """Carica una tabella gestendo errori di encoding UTF-8"""
            try:
                # SQLAlchemy 2.0: use autoload_with instead of autoload=True
                return Table(table_name, self.metadata, autoload_with=self.engine)
            except UnicodeDecodeError as e:
                QMessageBox.warning(None, "Errore Encoding",
                                  f"Errore di encoding UTF-8 nella tabella {table_name}.\n"
                                  f"Verificare che il database PostgreSQL sia configurato con encoding UTF-8.\n"
                                  f"Dettagli: {str(e)}", QMessageBox.Ok)
                return None
            except Exception as e:
                # Gestisci altri errori di caricamento tabella
                log_debug(f"Error loading table {table_name}: {e}")
                # Temporarily disable QMessageBox to prevent event loops
                # QMessageBox.warning(None, "Errore Tabella",
                #                   f"Impossibile caricare la tabella {table_name}.\n"
                #                   f"Dettagli: {str(e)}", QMessageBox.Ok)
                return None

        # Check if we're using SQLite
        is_sqlite = 'sqlite' in str(self.engine.url).lower()
        log_debug(f"Database type: {'SQLite' if is_sqlite else 'PostgreSQL'}")
        
        # TMA table migration and ensure new tables exist
        try:
            log_debug("Calling _ensure_tma_tables_exist()")
            self._ensure_tma_tables_exist()
            log_debug("_ensure_tma_tables_exist() completed")

            log_debug("Checking if old tma_table exists")
            # Now check if old tma_table exists and needs migration
            if is_sqlite:
                result = self._execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tma_table'")
                old_tma_exists = result.fetchone() is not None
            else:
                result = self._execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'tma_table'
                    )
                """)
                old_tma_exists = result.fetchone()[0]

            log_debug(f"Old tma_table exists: {old_tma_exists}")
            if old_tma_exists:
                log_debug("Calling _migrate_tma_table()")
                self._migrate_tma_table()
                log_debug("_migrate_tma_table() completed")

            # Check if localita field exists in tma_materiali_archeologici and remove it
            #self._remove_localita_field()
        except Exception as e:
            log_debug(f"Error in TMA table setup: {str(e)}")
            print(f"Error in TMA table setup: {str(e)}")
        
        # Update thesaurus table structure
        try:
            log_debug("Calling update_thesaurus_table()")
            update_thesaurus_table(self.engine, self.metadata)
            log_debug("update_thesaurus_table() completed")
        except Exception as e:
            log_debug(f"Error updating thesaurus table: {str(e)}")
            print(f"Error updating thesaurus table: {str(e)}")

        # Ensure tma_materiali_archeologici has all required fields
        try:
            log_debug("Checking if tma_materiali_archeologici has all required fields")
            table = safe_load_table("tma_materiali_archeologici")
            if table is not None:
                column_names = [str(col.name) for col in table.columns]

                # Check and add missing fields
                missing_fields = {
                    'sito': 'TEXT',
                    'settore': 'TEXT',
                    'inventario': 'TEXT',
                    'nsc': 'TEXT'
                }

                for field, field_type in missing_fields.items():
                    if field not in column_names:
                        log_debug(f"Adding missing '{field}' field to tma_materiali_archeologici")
                        self._execute(f"ALTER TABLE tma_materiali_archeologici ADD COLUMN {field} {field_type}")
                        log_debug(f"'{field}' field added successfully")
                    else:
                        log_debug(f"'{field}' field already exists")
            else:
                log_debug("tma_materiali_archeologici table not found")
        except Exception as e:
            log_debug(f"Error checking/adding fields to tma_materiali_archeologici: {str(e)}")
            print(f"Error checking/adding fields to tma_materiali_archeologici: {str(e)}")

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
        #     self._execute(
        #         "ALTER TABLE pyunitastratigrafiche ALTER COLUMN coord TYPE text")
        #
        # table = Table("pyunitastratigrafiche_usm", self.metadata, autoload=True)
        # table_column_names_list = []
        #
        # for i in table.columns:
        #     table_column_names_list.append(str(i.name))
        # if table_column_names_list.__contains__('coord'):
        #     self._execute(
        #         "ALTER TABLE pyunitastratigrafiche ALTER COLUMN coord TYPE text")

        ####pottery_table
        log_debug("Processing pottery_table")
        try:
            # SQLAlchemy 2.0: use autoload_with instead of autoload=True
            table = Table("pottery_table", self.metadata, autoload_with=self.engine)
            log_debug("pottery_table loaded successfully")

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
                            self._execute("ALTER TABLE pottery_table ALTER COLUMN us TYPE TEXT USING us::TEXT")
            except Exception as e:
                # Log the error but continue with other updates
                log_debug(f"Error updating us column: {e}")
                pass

            if not table_column_names_list.__contains__('sector'):
                self._execute(
                    "ALTER TABLE pottery_table ADD COLUMN sector text")
            try:
                if table_column_names_list.__contains__('diametro_max'):
                    self._execute(
                        "ALTER TABLE pottery_table ALTER COLUMN diametro_max TYPE Numeric(7,3)")

                if table_column_names_list.__contains__('diametro_rim'):
                    self._execute(
                        "ALTER TABLE pottery_table ALTER COLUMN diametro_rim TYPE Numeric(7,3)")

                if table_column_names_list.__contains__('diametro_bottom'):
                    self._execute(
                        "ALTER TABLE pottery_table ALTER COLUMN diametro_bottom TYPE Numeric(7,3)")

                if table_column_names_list.__contains__('diametro_height'):
                    self._execute(
                        "ALTER TABLE pottery_table ALTER COLUMN diametro_height TYPE Numeric(7,3)")

                if table_column_names_list.__contains__('diametro_preserved'):
                    self._execute(
                        "ALTER TABLE pottery_table ALTER COLUMN diametro_preserved TYPE Numeric(7,3)")

            except:
                pass

        except UnicodeDecodeError as e:
            # Gestisci errore di encoding
            log_debug(f"UnicodeDecodeError loading pottery_table: {e}")
            QMessageBox.warning(None, "Errore Encoding",
                              f"Errore di encoding UTF-8 nella tabella pottery_table.\n"
                              f"Verificare che il database PostgreSQL sia configurato con encoding UTF-8.\n"
                              f"Dettagli: {str(e)}", QMessageBox.Ok)
            return
        except Exception as e:
            # La tabella potrebbe non esistere, non è un errore critico
            log_debug(f"pottery_table not found or other error: {e}")
            # Continue with other updates


        ####inventario_materiali_table
        log_debug("Processing inventario_materiali_table - TEMPORARILY SKIPPED TO TEST")
        # TEMPORARILY SKIP TO TEST IF THIS CAUSES THE LOOP
        # Re-enable inventario_materiali_table processing with simplified logic
        log_debug("Processing inventario_materiali_table")
        table = safe_load_table("inventario_materiali_table")

        # Initialize empty list in case table doesn't exist
        table_column_names_list = []

        if table is not None:
            log_debug("inventario_materiali_table found, processing columns")
            for i in table.columns:
                table_column_names_list.append(str(i.name))

            # Simple column type conversion for critical columns (without backup complexity)
            log_debug("Checking for column type conversions")
            try:
                for col_name in ['area', 'us', 'nr_cassa']:
                    if col_name in table_column_names_list:
                        try:
                            # Try to convert column to TEXT if it's not already
                            self._execute(
                                f"ALTER TABLE inventario_materiali_table ALTER COLUMN {col_name} TYPE TEXT USING {col_name}::TEXT")
                            log_debug(f"Converted {col_name} column to TEXT")
                        except Exception as e:
                            # Column might already be TEXT or conversion not needed
                            log_debug(f"Column {col_name} conversion skipped: {e}")
                            pass
            except Exception as e:
                log_debug(f"Error in column type conversion: {e}")
                pass

            if not table_column_names_list.__contains__('years'):
                self._execute(
                    "ALTER TABLE inventario_materiali_table ADD COLUMN years BIGINT")

            if not table_column_names_list.__contains__('stato_conservazione'):
                self._execute(
                    "ALTER TABLE inventario_materiali_table ADD COLUMN stato_conservazione varchar DEFAULT ''")

            if not table_column_names_list.__contains__('datazione_reperto'):
                self._execute(
                    "ALTER TABLE inventario_materiali_table ADD COLUMN datazione_reperto varchar(30) DEFAULT 'inserisci un valore'")

            if not table_column_names_list.__contains__('elementi_reperto'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN elementi_reperto text")

            if not table_column_names_list.__contains__('misurazioni'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN misurazioni text")

            if not table_column_names_list.__contains__('rif_biblio'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN rif_biblio text")

            if not table_column_names_list.__contains__('tecnologie'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN tecnologie text")

            if not table_column_names_list.__contains__('forme_minime'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN forme_minime BIGINT DEFAULT 0")

            if not table_column_names_list.__contains__('forme_massime'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN forme_massime BIGINT DEFAULT 0")

            if not table_column_names_list.__contains__('totale_frammenti'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN totale_frammenti BIGINT DEFAULT 0")

            if not table_column_names_list.__contains__('corpo_ceramico'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN corpo_ceramico varchar(20)")
                self._execute("update inventario_materiali_table set corpo_ceramico = ''")

            if not table_column_names_list.__contains__('rivestimento'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN rivestimento varchar(20)")
                self._execute("update inventario_materiali_table set rivestimento = ''")

            if not table_column_names_list.__contains__('diametro_orlo'):
                self._execute(
                    "ALTER TABLE inventario_materiali_table ADD COLUMN diametro_orlo Numeric(7,3) DEFAULT 0")

            if not table_column_names_list.__contains__('peso'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN peso Numeric(9,3) DEFAULT 0")

            if not table_column_names_list.__contains__('tipo'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN tipo varchar(20)")
                self._execute("update inventario_materiali_table set tipo = ''")

            if not table_column_names_list.__contains__('eve_orlo'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN eve_orlo Numeric(7,3) DEFAULT 0")

            if not table_column_names_list.__contains__('repertato'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN repertato varchar(3)")
                self._execute("update inventario_materiali_table set repertato = ''No")

            if not table_column_names_list.__contains__('diagnostico'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN diagnostico varchar(3)")
                self._execute("update inventario_materiali_table set diagnostico = ''No")
            if not table_column_names_list.__contains__('n_reperto'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN n_reperto BIGINT")
            if not table_column_names_list.__contains__('tipo_contenitore'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN tipo_contenitore varchar DEFAULT ''")
            if not table_column_names_list.__contains__('struttura'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN struttura text")

            # Add new columns for inventario_materiali_table
            if not table_column_names_list.__contains__('schedatore'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN schedatore TEXT")

            if not table_column_names_list.__contains__('date_scheda'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN date_scheda TEXT")

            if not table_column_names_list.__contains__('punto_rinv'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN punto_rinv TEXT")

            if not table_column_names_list.__contains__('negativo_photo'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN negativo_photo TEXT")

            if not table_column_names_list.__contains__('diapositiva'):
                self._execute("ALTER TABLE inventario_materiali_table ADD COLUMN diapositiva TEXT")

            # Update the pyarchinit_reperti_view to include the new fields
            try:
                self._execute("""
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



        # END OF TEMPORARILY DISABLED inventario_materiali_table SECTION

        ####site_table
        log_debug("Processing site_table")
        table = safe_load_table("site_table")
        if table is None:
            log_debug("site_table not found, skipping")
            # Continue with other updates instead of returning

        table_column_names_list = []
        if table is not None:
            for i in table.columns:
                table_column_names_list.append(str(i.name))

            # Only try to alter table if it exists
            if not table_column_names_list.__contains__('provincia'):
                self._execute("ALTER TABLE site_table ADD COLUMN provincia varchar DEFAULT 'inserici un valore' ")

            if not table_column_names_list.__contains__('definizione_sito'):
                self._execute(
                    "ALTER TABLE site_table ADD COLUMN definizione_sito varchar DEFAULT 'inserici un valore' ")

            if not table_column_names_list.__contains__('sito_path'):
                self._execute("ALTER TABLE site_table ADD COLUMN sito_path varchar DEFAULT 'inserisci path' ")

            if not table_column_names_list.__contains__('find_check'):
                self._execute("ALTER TABLE site_table ADD COLUMN find_check BIGINT DEFAULT 0")

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
                        self._execute("DROP VIEW IF EXISTS pyarchinit_quote_view CASCADE")
                        self._execute("DROP VIEW IF EXISTS pyarchinit_us_view CASCADE")
                        self._execute("DROP VIEW IF EXISTS pyarchinit_uscaratterizzazioni_view CASCADE")
                    except:
                        pass
                    
                    # Convert the column type
                    self._execute("ALTER TABLE us_table ALTER COLUMN us TYPE TEXT USING us::TEXT")
                    
                    # Recreate views
                    try:
                        self._execute("""
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
                            us_table.anno_scavo,
                            us_table.scavato,
                            us_table.attivita,
                            us_table.cont_per,
                            us_table.order_layer,
                            us_table.documentazione,
                            us_table.datazione
                        FROM pyunitastratigrafiche
                        JOIN us_table ON
                            pyunitastratigrafiche.scavo_s = us_table.sito
                            AND pyunitastratigrafiche.area_s::TEXT = us_table.area::TEXT
                            AND pyunitastratigrafiche.us_s = us_table.us
                        ORDER BY us_table.order_layer ASC
                        """)
                    except:
                        pass
        except Exception as e:
            # Log the error but continue with other updates
            pass

        if not table_column_names_list.__contains__('cont_per'):
            self._execute("ALTER TABLE us_table ADD COLUMN cont_per varchar DEFAULT")

        if not table_column_names_list.__contains__('documentazione'):
            self._execute("ALTER TABLE us_table ADD COLUMN documentazione varchar")

            # nuovi campi per USM 1/9/2016 generati correttamente
        if not table_column_names_list.__contains__('unita_tipo'):
            self._execute("ALTER TABLE us_table ADD COLUMN unita_tipo varchar DEFAULT 'US' ")

        if not table_column_names_list.__contains__('settore'):
            self._execute("ALTER TABLE us_table ADD COLUMN settore text DEFAULT '' ")

        if not table_column_names_list.__contains__('quad_par'):
            self._execute("ALTER TABLE us_table ADD COLUMN quad_par text DEFAULT '' ")

        if not table_column_names_list.__contains__('ambient'):
            self._execute("ALTER TABLE us_table ADD COLUMN ambient text DEFAULT '' ")

        if not table_column_names_list.__contains__('saggio'):
            self._execute("ALTER TABLE us_table ADD COLUMN saggio text DEFAULT '' ")

        if not table_column_names_list.__contains__('elem_datanti'):
            self._execute("ALTER TABLE us_table ADD COLUMN elem_datanti text DEFAULT '' ")

        if not table_column_names_list.__contains__('funz_statica'):
            self._execute("ALTER TABLE us_table ADD COLUMN funz_statica text DEFAULT '' ")

        if not table_column_names_list.__contains__('lavorazione'):
            self._execute("ALTER TABLE us_table ADD COLUMN lavorazione text DEFAULT '' ")

        if not table_column_names_list.__contains__('spess_giunti'):
            self._execute("ALTER TABLE us_table ADD COLUMN spess_giunti text DEFAULT '' ")

        if not table_column_names_list.__contains__('letti_posa'):
            self._execute("ALTER TABLE us_table ADD COLUMN letti_posa text DEFAULT '' ")

        if not table_column_names_list.__contains__('alt_mod'):
            self._execute("ALTER TABLE us_table ADD COLUMN alt_mod text DEFAULT '' ")

        if not table_column_names_list.__contains__('un_ed_riass'):
            self._execute("ALTER TABLE us_table ADD COLUMN un_ed_riass text DEFAULT '' ")

        if not table_column_names_list.__contains__('reimp'):
            self._execute("ALTER TABLE us_table ADD COLUMN reimp text DEFAULT '' ")

        if not table_column_names_list.__contains__('posa_opera'):
            self._execute("ALTER TABLE us_table ADD COLUMN posa_opera text DEFAULT '' ")

        if not table_column_names_list.__contains__('quota_min_usm'):
            self._execute("ALTER TABLE us_table ADD COLUMN quota_min_usm NUMERIC(6,2)")

        if not table_column_names_list.__contains__('quota_max_usm'):
            self._execute("ALTER TABLE us_table ADD COLUMN quota_max_usm NUMERIC(6,2)")

        if not table_column_names_list.__contains__('cons_legante'):
            self._execute("ALTER TABLE us_table ADD COLUMN cons_legante text DEFAULT '' ")

        if not table_column_names_list.__contains__('col_legante'):
            self._execute("ALTER TABLE us_table ADD COLUMN col_legante text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('aggreg_legante'):
            self._execute("ALTER TABLE us_table ADD COLUMN aggreg_legante text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('con_text_mat'):
            self._execute("ALTER TABLE us_table ADD COLUMN con_text_mat text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('col_materiale'):
            self._execute("ALTER TABLE us_table ADD COLUMN col_materiale text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('inclusi_materiali_usm'):
            self._execute("ALTER TABLE us_table ADD COLUMN inclusi_materiali_usm text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('n_catalogo_generale'):
            self._execute("ALTER TABLE us_table ADD COLUMN n_catalogo_generale text DEFAULT '' ")

        if not table_column_names_list.__contains__('n_catalogo_interno'):
            self._execute("ALTER TABLE us_table ADD COLUMN n_catalogo_interno text DEFAULT '' ")

        if not table_column_names_list.__contains__('n_catalogo_internazionale'):
            self._execute("ALTER TABLE us_table ADD COLUMN n_catalogo_internazionale text DEFAULT '' ")

        if not table_column_names_list.__contains__('soprintendenza'):
            self._execute("ALTER TABLE us_table ADD COLUMN soprintendenza text DEFAULT '' ")

        if not table_column_names_list.__contains__('quota_relativa'):
            self._execute("ALTER TABLE us_table ADD COLUMN quota_relativa NUMERIC(6,2)")

        if not table_column_names_list.__contains__('quota_abs'):
            self._execute("ALTER TABLE us_table ADD COLUMN quota_abs   NUMERIC(6,2)")

        if not table_column_names_list.__contains__('ref_tm'):
            self._execute("ALTER TABLE us_table ADD COLUMN ref_tm text DEFAULT '' ")

        if not table_column_names_list.__contains__('ref_ra'):
            self._execute("ALTER TABLE us_table ADD COLUMN ref_ra text DEFAULT '' ")

        if not table_column_names_list.__contains__('ref_n'):
            self._execute("ALTER TABLE us_table ADD COLUMN ref_n text DEFAULT '' ")

        if not table_column_names_list.__contains__('posizione'):
            self._execute("ALTER TABLE us_table ADD COLUMN posizione text DEFAULT '' ")

        if not table_column_names_list.__contains__('criteri_distinzione'):
            self._execute("ALTER TABLE us_table ADD COLUMN criteri_distinzione text DEFAULT '' ")

        if not table_column_names_list.__contains__('modo_formazione'):
            self._execute("ALTER TABLE us_table ADD COLUMN modo_formazione text DEFAULT '' ")

        if not table_column_names_list.__contains__('componenti_organici'):
            self._execute("ALTER TABLE us_table ADD COLUMN componenti_organici text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('componenti_inorganici'):
            self._execute("ALTER TABLE us_table ADD COLUMN componenti_inorganici text DEFAULT '[]' ")

        if not table_column_names_list.__contains__('lunghezza_max'):
            self._execute("ALTER TABLE us_table ADD COLUMN lunghezza_max NUMERIC(6,2)")

        if not table_column_names_list.__contains__('altezza_max'):
            self._execute("ALTER TABLE us_table ADD COLUMN altezza_max NUMERIC(6,2)")

        if not table_column_names_list.__contains__('altezza_min'):
            self._execute("ALTER TABLE us_table ADD COLUMN altezza_min NUMERIC(6,2)")

        if not table_column_names_list.__contains__('profondita_max'):
            self._execute("ALTER TABLE us_table ADD COLUMN profondita_max NUMERIC(6,2)")

        if not table_column_names_list.__contains__('profondita_min'):
            self._execute("ALTER TABLE us_table ADD COLUMN profondita_min NUMERIC(6,2)")

        if not table_column_names_list.__contains__('larghezza_media'):
            self._execute("ALTER TABLE us_table ADD COLUMN larghezza_media NUMERIC(6,2)")

        if not table_column_names_list.__contains__('quota_max_abs'):
            self._execute("ALTER TABLE us_table ADD COLUMN quota_max_abs NUMERIC(6,2)")

        if not table_column_names_list.__contains__('quota_max_rel'):
            self._execute("ALTER TABLE us_table ADD COLUMN quota_max_rel NUMERIC(6,2)")

        if not table_column_names_list.__contains__('quota_min_abs'):
            self._execute("ALTER TABLE us_table ADD COLUMN quota_min_abs NUMERIC(6,2)")

        if not table_column_names_list.__contains__('quota_min_rel'):
            self._execute("ALTER TABLE us_table ADD COLUMN quota_min_rel NUMERIC(6,2)")

        if not table_column_names_list.__contains__('osservazioni'):
            self._execute("ALTER TABLE us_table ADD COLUMN osservazioni text DEFAULT '' ")

        if not table_column_names_list.__contains__('datazione'):
            self._execute("ALTER TABLE us_table ADD COLUMN datazione text DEFAULT '' ")

        if not table_column_names_list.__contains__('flottazione'):
            self._execute("ALTER TABLE us_table ADD COLUMN flottazione text DEFAULT '' ")

        if not table_column_names_list.__contains__('setacciatura'):
            self._execute("ALTER TABLE us_table ADD COLUMN setacciatura text DEFAULT '' ")

        if not table_column_names_list.__contains__('affidabilita'):
            self._execute("ALTER TABLE us_table ADD COLUMN affidabilita text DEFAULT '' ")

        if not table_column_names_list.__contains__('direttore_us'):
            self._execute("ALTER TABLE us_table ADD COLUMN direttore_us text DEFAULT '' ")

        if not table_column_names_list.__contains__('responsabile_us'):
            self._execute("ALTER TABLE us_table ADD COLUMN responsabile_us text DEFAULT '' ")

        if not table_column_names_list.__contains__('cod_ente_schedatore'):
            self._execute("ALTER TABLE us_table ADD COLUMN cod_ente_schedatore text DEFAULT '' ")

        if not table_column_names_list.__contains__('data_rilevazione'):
            self._execute("ALTER TABLE us_table ADD COLUMN data_rilevazione text DEFAULT '' ")

        if not table_column_names_list.__contains__('data_rielaborazione'):
            self._execute("ALTER TABLE us_table ADD COLUMN data_rielaborazione text DEFAULT '' ")

        if not table_column_names_list.__contains__('lunghezza_usm'):
            self._execute("ALTER TABLE us_table ADD COLUMN lunghezza_usm NUMERIC(6,2)")

        if not table_column_names_list.__contains__('altezza_usm'):
            self._execute("ALTER TABLE us_table ADD COLUMN altezza_usm NUMERIC(6,2)")

        if not table_column_names_list.__contains__('spessore_usm'):
            self._execute("ALTER TABLE us_table ADD COLUMN spessore_usm NUMERIC(6,2)")

        if not table_column_names_list.__contains__('tecnica_muraria_usm'):
            self._execute("ALTER TABLE us_table ADD COLUMN tecnica_muraria_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('modulo_usm'):
            self._execute("ALTER TABLE us_table ADD COLUMN modulo_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('campioni_malta_usm'):
            self._execute("ALTER TABLE us_table ADD COLUMN campioni_malta_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('campioni_mattone_usm'):
            self._execute("ALTER TABLE us_table ADD COLUMN campioni_mattone_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('campioni_pietra_usm'):
            self._execute("ALTER TABLE us_table ADD COLUMN campioni_pietra_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('provenienza_materiali_usm'):
            self._execute("ALTER TABLE us_table ADD COLUMN provenienza_materiali_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('criteri_distinzione_usm'):
            self._execute("ALTER TABLE us_table ADD COLUMN criteri_distinzione_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('uso_primario_usm'):
            self._execute("ALTER TABLE us_table ADD COLUMN uso_primario_usm text DEFAULT '' ")

        if not table_column_names_list.__contains__('doc_usv'):
            self._execute("ALTER TABLE us_table ADD COLUMN doc_usv text DEFAULT '' ")

        #############nuovi##############################################################
        if not table_column_names_list.__contains__('tipologia_opera'):
            self._execute("ALTER TABLE us_table ADD COLUMN tipologia_opera text DEFAULT '' ")

        if not table_column_names_list.__contains__('sezione_muraria'):
            self._execute("ALTER TABLE us_table ADD COLUMN sezione_muraria text DEFAULT '' ")
        if not table_column_names_list.__contains__('superficie_analizzata'):
            self._execute("ALTER TABLE us_table ADD COLUMN superficie_analizzata text DEFAULT '' ")
        if not table_column_names_list.__contains__('orientamento'):
                self._execute("ALTER TABLE us_table ADD COLUMN orientamento text DEFAULT '' ")
        if not table_column_names_list.__contains__('materiali_lat'):
                self._execute("ALTER TABLE us_table ADD COLUMN materiali_lat text DEFAULT '' ")
        if not table_column_names_list.__contains__('lavorazione_lat'):
                self._execute("ALTER TABLE us_table ADD COLUMN lavorazione_lat text DEFAULT '' ")
        if not table_column_names_list.__contains__('consistenza_lat'):
                self._execute("ALTER TABLE us_table ADD COLUMN consistenza_lat text DEFAULT '' ")
        if not table_column_names_list.__contains__('forma_lat'):
                self._execute("ALTER TABLE us_table ADD COLUMN forma_lat text DEFAULT '' ")
        if not table_column_names_list.__contains__('colore_lat'):
                self._execute("ALTER TABLE us_table ADD COLUMN colore_lat text DEFAULT '' ")
        if not table_column_names_list.__contains__('impasto_lat'):
                self._execute("ALTER TABLE us_table ADD COLUMN impasto_lat text DEFAULT '' ")


        if not table_column_names_list.__contains__('forma_p'):
                self._execute("ALTER TABLE us_table ADD COLUMN forma_p text DEFAULT '' ")
        if not table_column_names_list.__contains__('colore_p'):
                self._execute("ALTER TABLE us_table ADD COLUMN colore_p text DEFAULT '' ")
        if not table_column_names_list.__contains__('taglio_p'):
                self._execute("ALTER TABLE us_table ADD COLUMN taglio_p text DEFAULT '' ")
        if not table_column_names_list.__contains__('posa_opera_p'):
                self._execute("ALTER TABLE us_table ADD COLUMN posa_opera_p text DEFAULT '' ")
        if not table_column_names_list.__contains__('inerti_usm'):
                self._execute("ALTER TABLE us_table ADD COLUMN inerti_usm text DEFAULT '' ")
        if not table_column_names_list.__contains__('tipo_legante_usm'):
                self._execute("ALTER TABLE us_table ADD COLUMN tipo_legante_usm text DEFAULT '' ")
        if not table_column_names_list.__contains__('rifinitura_usm'):
                self._execute("ALTER TABLE us_table ADD COLUMN rifinitura_usm text DEFAULT '' ")
        if not table_column_names_list.__contains__('materiale_p'):
                self._execute("ALTER TABLE us_table ADD COLUMN materiale_p text DEFAULT '' ")
        if not table_column_names_list.__contains__('consistenza_p'):
                self._execute("ALTER TABLE us_table ADD COLUMN consistenza_p text DEFAULT '' ")                    
        if not table_column_names_list.__contains__('rapporti2'):
            self._execute("ALTER TABLE us_table ADD COLUMN rapporti2 text DEFAULT '' ")

        # try:
            # self._execute("ALTER TABLE us_table ADD CONSTRAINT ID_us_unico UNIQUE (unita_tipo);")
        # except:
            # pass

        ####ut_table - New survey fields (v4.9.21+)
        log_debug("Processing ut_table")
        table = safe_load_table("ut_table")
        if table is not None:
            table_column_names_list = []
            for i in table.columns:
                table_column_names_list.append(str(i.name))

            # New survey fields for UT (Unità Topografica)
            if not table_column_names_list.__contains__('visibility_percent'):
                self._execute("ALTER TABLE ut_table ADD COLUMN visibility_percent INTEGER")

            if not table_column_names_list.__contains__('vegetation_coverage'):
                self._execute("ALTER TABLE ut_table ADD COLUMN vegetation_coverage VARCHAR(255)")

            if not table_column_names_list.__contains__('gps_method'):
                self._execute("ALTER TABLE ut_table ADD COLUMN gps_method VARCHAR(100)")

            if not table_column_names_list.__contains__('coordinate_precision'):
                self._execute("ALTER TABLE ut_table ADD COLUMN coordinate_precision REAL")

            if not table_column_names_list.__contains__('survey_type'):
                self._execute("ALTER TABLE ut_table ADD COLUMN survey_type VARCHAR(100)")

            if not table_column_names_list.__contains__('surface_condition'):
                self._execute("ALTER TABLE ut_table ADD COLUMN surface_condition VARCHAR(255)")

            if not table_column_names_list.__contains__('accessibility'):
                self._execute("ALTER TABLE ut_table ADD COLUMN accessibility VARCHAR(255)")

            if not table_column_names_list.__contains__('photo_documentation'):
                self._execute("ALTER TABLE ut_table ADD COLUMN photo_documentation INTEGER")

            if not table_column_names_list.__contains__('weather_conditions'):
                self._execute("ALTER TABLE ut_table ADD COLUMN weather_conditions VARCHAR(255)")

            if not table_column_names_list.__contains__('team_members'):
                self._execute("ALTER TABLE ut_table ADD COLUMN team_members TEXT")

            if not table_column_names_list.__contains__('foglio_catastale'):
                self._execute("ALTER TABLE ut_table ADD COLUMN foglio_catastale VARCHAR(100)")

            # Analysis fields (v4.9.70+)
            if not table_column_names_list.__contains__('potential_score'):
                self._execute("ALTER TABLE ut_table ADD COLUMN potential_score NUMERIC(5,2)")

            if not table_column_names_list.__contains__('risk_score'):
                self._execute("ALTER TABLE ut_table ADD COLUMN risk_score NUMERIC(5,2)")

            if not table_column_names_list.__contains__('potential_factors'):
                self._execute("ALTER TABLE ut_table ADD COLUMN potential_factors TEXT")

            if not table_column_names_list.__contains__('risk_factors'):
                self._execute("ALTER TABLE ut_table ADD COLUMN risk_factors TEXT")

            if not table_column_names_list.__contains__('analysis_date'):
                self._execute("ALTER TABLE ut_table ADD COLUMN analysis_date VARCHAR(100)")

            if not table_column_names_list.__contains__('analysis_method'):
                self._execute("ALTER TABLE ut_table ADD COLUMN analysis_method VARCHAR(100)")

        ####archeozoology_table - Add coord_z if missing
        log_debug("Processing archeozoology_table")
        table = safe_load_table("archeozoology_table")
        if table is not None:
            table_column_names_list = []
            for i in table.columns:
                table_column_names_list.append(str(i.name))

            if not table_column_names_list.__contains__('coord_z'):
                self._execute("ALTER TABLE archeozoology_table ADD COLUMN coord_z NUMERIC(12,6)")

        ####pyarchinit_thesaurus_sigle
        table = safe_load_table("pyarchinit_thesaurus_sigle")
        if table is None:
            return
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('lingua'):
            self._execute("ALTER TABLE pyarchinit_thesaurus_sigle ADD COLUMN lingua text DEFAULT '' ")



        ####periodizzazione_table
        table = safe_load_table("periodizzazione_table")
        if table is None:
            return
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('cont_per'):
            self._execute("ALTER TABLE periodizzazione_table ADD COLUMN cont_per BIGINT DEFAULT '' ")
        # if not table_column_names_list.__contains__('area'):
            # self._execute("ALTER TABLE periodizzazione_table ADD COLUMN area BIGINT")

        ####tomba_table
        table = safe_load_table("tomba_table")
        if table is None:
            return
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('periodo_iniziale'):
            self._execute("ALTER TABLE tomba_table ADD COLUMN periodo_iniziale BIGINT")

        if not table_column_names_list.__contains__('fase_iniziale'):
            self._execute("ALTER TABLE tomba_table ADD COLUMN fase_iniziale BIGINT")

        if not table_column_names_list.__contains__('periodo_finale'):
            self._execute("ALTER TABLE tomba_table ADD COLUMN periodo_finale BIGINT")

        if not table_column_names_list.__contains__('fase_finale'):
            self._execute("ALTER TABLE tomba_table ADD COLUMN fase_finale BIGINT")

        if not table_column_names_list.__contains__('datazione_estesa'):
            self._execute("ALTER TABLE tomba_table ADD COLUMN datazione_estesa text")

        ####individui_table
        table = safe_load_table("individui_table")
        if table is None:
            return
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('sigla_struttura'):
            self._execute("ALTER TABLE individui_table ADD COLUMN sigla_struttura text")

        if not table_column_names_list.__contains__('nr_struttura'):
            self._execute("ALTER TABLE individui_table ADD COLUMN nr_struttura text")

        if not table_column_names_list.__contains__('completo_si_no'):
            self._execute("ALTER TABLE individui_table ADD COLUMN completo_si_no varchar")

        if not table_column_names_list.__contains__('disturbato_si_no'):
            self._execute("ALTER TABLE individui_table ADD COLUMN disturbato_si_no varchar")

        if not table_column_names_list.__contains__('in_connessione_si_no'):
            self._execute("ALTER TABLE individui_table ADD COLUMN in_connessione_si_no varchar")

        if not table_column_names_list.__contains__('lunghezza_scheletro'):
            self._execute("ALTER TABLE individui_table ADD COLUMN lunghezza_scheletro NUMERIC(6,2)")

        if not table_column_names_list.__contains__('posizione_scheletro'):
            self._execute("ALTER TABLE individui_table ADD COLUMN posizione_scheletro varchar")

        if not table_column_names_list.__contains__('posizione_cranio'):
            self._execute("ALTER TABLE individui_table ADD COLUMN posizione_cranio varchar")

        if not table_column_names_list.__contains__('posizione_arti_superiori'):
            self._execute("ALTER TABLE individui_table ADD COLUMN posizione_arti_superiori varchar")

        if not table_column_names_list.__contains__('posizione_arti_inferiori'):
            self._execute("ALTER TABLE individui_table ADD COLUMN posizione_arti_inferiori varchar")

        if not table_column_names_list.__contains__('orientamento_asse'):
            self._execute("ALTER TABLE individui_table ADD COLUMN orientamento_asse text")

        if not table_column_names_list.__contains__('orientamento_azimut'):
            self._execute("ALTER TABLE individui_table ADD COLUMN orientamento_azimut text")
        try:
            if table_column_names_list.__contains__('nr_struttura'):
                self._execute("ALTER TABLE individui_table ALTER COLUMN nr_struttura  TYPE text")
            if table_column_names_list.__contains__('orientamento_azimut'):
                self._execute("ALTER TABLE individui_table ALTER COLUMN orientamento_azimut TYPE text")
            if table_column_names_list.__contains__('us'):
                self._execute("ALTER TABLE individui_table ALTER COLUMN us TYPE text")
            if table_column_names_list.__contains__('eta_min'):
                self._execute("ALTER TABLE individui_table ALTER COLUMN eta_min TYPE text")
            if table_column_names_list.__contains__('eta_max'):
                self._execute("ALTER TABLE individui_table ALTER COLUMN eta_max TYPE text")
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
                self._execute("ALTER TABLE periodizzazione_table ALTER COLUMN fase TYPE text")
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
            # self._execute("ALTER TABLE pyunitastratigrafiche RENAME COLUMN rilievo_orginale TO rilievo_originale")   

        if not table_column_names_list.__contains__('coord'):
            self._execute("ALTER TABLE pyunitastratigrafiche ADD COLUMN coord text")
        if not table_column_names_list.__contains__('unita_tipo_s'):
            self._execute("ALTER TABLE pyunitastratigrafiche ADD COLUMN unita_tipo_s text")
        # if table_column_names_list.__contains__('id'):
            # self._execute("ALTER TABLE pyunitastratigrafiche RENAME COLUMN id TO gid")

        table = safe_load_table("pyunitastratigrafiche_usm")
        if table is None:
            return
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('unita_tipo_s'):
            self._execute("ALTER TABLE pyunitastratigrafiche_usm ADD COLUMN unita_tipo_s text")


        table = safe_load_table("pyarchinit_quote_usm")
        if table is None:
            return
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('unita_tipo_q'):
            self._execute("ALTER TABLE pyarchinit_quote_usm ADD COLUMN unita_tipo_q text")


        table = safe_load_table("pyarchinit_quote")
        if table is None:
            return
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('unita_tipo_q'):
            self._execute("ALTER TABLE pyarchinit_quote ADD COLUMN unita_tipo_q text")

        table = safe_load_table("pyarchinit_strutture_ipotesi")
        if table is None:
            return
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('sigla_strut'):

            self._execute( "ALTER TABLE pyarchinit_strutture_ipotesi ADD COLUMN sigla_strut varchar(3) DEFAULT 'NoD'")

        if not table_column_names_list.__contains__('nr_strut'):
            self._execute("ALTER TABLE pyarchinit_strutture_ipotesi ADD COLUMN nr_strut BIGINT DEFAULT 0 ")


        table = safe_load_table("pyarchinit_sezioni")
        if table is None:
            return
        table_column_names_list = []
        for i in table.columns:
            table_column_names_list.append(str(i.name))

        if not table_column_names_list.__contains__('tipo_doc'):
            self._execute("ALTER TABLE pyarchinit_sezioni  ADD COLUMN tipo_doc text")   

        if not table_column_names_list.__contains__('nome_doc'):
            self._execute("ALTER TABLE pyarchinit_sezioni  ADD COLUMN nome_doc text")

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
                            self._execute("ALTER TABLE campioni_table ALTER COLUMN us TYPE TEXT USING us::TEXT")
            except Exception as e:
                # Log the error but continue with other updates
                pass
                
            # Change nr_cassa column from INTEGER to TEXT
            try:
                if table_column_names_list.__contains__('nr_cassa'):
                    # Check if the column is still INTEGER type
                    nr_cassa_column = None
                    for col in table.columns:
                        if col.name == 'nr_cassa':
                            nr_cassa_column = col
                            break
                    
                    if nr_cassa_column is not None:
                        # Check if column type needs conversion
                        col_type = str(nr_cassa_column.type)
                        if 'INTEGER' in col_type.upper() or 'BIGINT' in col_type.upper():
                            # Convert the column type
                            self._execute("ALTER TABLE campioni_table ALTER COLUMN nr_cassa TYPE TEXT USING nr_cassa::TEXT")
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
                                self._execute("ALTER TABLE us_table_toimp ALTER COLUMN us TYPE TEXT USING us::TEXT")
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
                                self._execute("DROP VIEW IF EXISTS pyarchinit_quote_view CASCADE")
                            except:
                                pass
                            
                            # Convert the column type
                            self._execute("ALTER TABLE pyarchinit_quote ALTER COLUMN us_q TYPE TEXT USING us_q::TEXT")
                            
                            # Recreate view
                            try:
                                self._execute("""
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
                                    us_table.anno_scavo,
                                    us_table.cont_per,
                                    us_table.order_layer,
                                    us_table.datazione
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
                            self._execute("ALTER TABLE pyarchinit_quote_usm ALTER COLUMN us_q TYPE TEXT USING us_q::TEXT")
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
                                self._execute("DROP VIEW IF EXISTS pyarchinit_us_view CASCADE")
                            except:
                                pass
                            
                            # Convert the column type
                            self._execute("ALTER TABLE pyunitastratigrafiche ALTER COLUMN us_s TYPE TEXT USING us_s::TEXT")
                            
                            # Recreate the view if us_table has already been converted
                            try:
                                self._execute("""
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
                                    us_table.anno_scavo,
                                    us_table.scavato,
                                    us_table.attivita,
                                    us_table.cont_per,
                                    us_table.order_layer,
                                    us_table.documentazione,
                                    us_table.datazione
                                FROM pyunitastratigrafiche
                                JOIN us_table ON
                                    pyunitastratigrafiche.scavo_s = us_table.sito
                                    AND pyunitastratigrafiche.area_s::TEXT = us_table.area::TEXT
                                    AND pyunitastratigrafiche.us_s = us_table.us
                                ORDER BY us_table.order_layer ASC
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
                            self._execute("ALTER TABLE pyunitastratigrafiche_usm ALTER COLUMN us_s TYPE TEXT USING us_s::TEXT")
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
                                self._execute("ALTER TABLE pyarchinit_us_negative_doc ALTER COLUMN us_n TYPE TEXT USING us_n::TEXT")
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
        #                             self._execute("DROP VIEW IF EXISTS pyarchinit_uscaratterizzazioni_view CASCADE")
        #                         except:
        #                             pass
        #
        #                         # Convert the column type
        #                         self._execute("ALTER TABLE pyuscaratterizzazioni ALTER COLUMN us_c TYPE TEXT USING us_c::TEXT")
        #
        #                         # Recreate view
        #                         # try:
        #                         #     self._execute("""
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
        
        # Add concurrency columns to all tables
        log_debug("Adding concurrency columns to all tables")
        self._add_concurrency_columns()

        # Update thesaurus table structure for PostgreSQL
        try:
            update_thesaurus_table(self.engine, self.metadata)
        except Exception as e:
            print(f"Error updating thesaurus table: {str(e)}")

        log_debug("update_table() completed successfully")

    def _migrate_us_fields_sqlite(self):
        """SQLite-specific migration for US fields from INTEGER to TEXT"""
        try:
            # First, clean up any leftover _new tables from previous failed migrations
            result = self._execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_new'")
            for row in result:
                try:
                    self._execute(f"DROP TABLE IF EXISTS {row[0]}")
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
                    self._execute(f"DROP VIEW IF EXISTS {view}")
                except:
                    pass
            
            # Define tables and fields to migrate
            # Migrate both US and area fields where needed
            migrations = [
                # US field migrations
                ('us_table', ['us', 'area']),
                ('campioni_table', ['us', 'area', 'nr_cassa']),
                ('pottery_table', ['us', 'area']),
                ('inventario_materiali_table', ['us', 'area', 'nr_cassa']),
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
                    check_exists = self._execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                    if not check_exists.fetchone():
                        continue
                    
                    # Check which fields need migration
                    needs_migration = False
                    result = self._execute(f"PRAGMA table_info({table_name})")
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

            # Fix invalid geometries
            print("Fixing invalid geometries...")
            fix_results = self.fix_invalid_geometries()
            total_fixed = sum(r.get('fixed', 0) for r in fix_results.values())
            if total_fixed > 0:
                print(f"Fixed {total_fixed} invalid geometries")

            # Final cleanup - remove any remaining _new tables
            result = self._execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_new'")
            for row in result:
                try:
                    self._execute(f"DROP TABLE IF EXISTS {row[0]}")
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
            result = self._execute(f"PRAGMA table_info({table_name})")
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
            self._execute(new_table_sql)
            
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
            
            self._execute(f"INSERT INTO {table_name}_new SELECT {select_str} FROM {table_name}")
            
            # Drop old table and rename new one
            self._execute(f"DROP TABLE {table_name}")
            self._execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name}")
            
            # Create index on US field
            self._execute(f"CREATE INDEX idx_{table_name}_{us_field} ON {table_name}({us_field})")
            
        except Exception as e:
            raise Exception(f"Errore durante la migrazione della tabella {table_name}: {str(e)}")
    
    def _migrate_sqlite_table_fields(self, table_name, fields_to_migrate, columns_info):
        """Migrate multiple fields in a single SQLite table by recreating it with TEXT type"""
        backup_table_name = f"{table_name}_backup_{int(time.time())}"
        
        try:
            # First, create a backup of the original table
            self._execute(f"CREATE TABLE {backup_table_name} AS SELECT * FROM {table_name}")
            
            # Count rows in backup to ensure data was copied
            result = self._execute(f"SELECT COUNT(*) FROM {backup_table_name}")
            backup_count = result.fetchone()[0]
            
            # Count rows in original table
            result = self._execute(f"SELECT COUNT(*) FROM {table_name}")
            original_count = result.fetchone()[0]
            
            # Verify backup has same number of rows
            if backup_count != original_count:
                raise Exception(f"Backup verification failed: {backup_count} rows in backup vs {original_count} in original")
            
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
            self._execute(new_table_sql)
            
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
            self._execute(f"INSERT INTO {table_name}_new ({columns_str}) SELECT {select_str} FROM {table_name}")
            
            # Verify data was copied to new table
            result = self._execute(f"SELECT COUNT(*) FROM {table_name}_new")
            new_count = result.fetchone()[0]
            
            if new_count != original_count:
                raise Exception(f"Migration verification failed: {new_count} rows in new table vs {original_count} in original")
            
            # Only drop old table and rename if everything is OK
            self._execute(f"DROP TABLE {table_name}")
            self._execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name}")
            
            # Drop backup table only after successful migration
            self._execute(f"DROP TABLE {backup_table_name}")
            
            # Log successful migration
            print(f"Successfully migrated {table_name} fields to TEXT: {', '.join(fields_to_migrate)}")
            
            # Create indexes on migrated fields
            for field in fields_to_migrate:
                try:
                    self._execute(f"CREATE INDEX idx_{table_name}_{field} ON {table_name}({field})")
                except:
                    pass  # Index might already exist
                    
        except Exception as e:
            # If anything goes wrong, try to restore from backup
            try:
                # Drop the failed new table if it exists
                self._execute(f"DROP TABLE IF EXISTS {table_name}_new")
                
                # Check if original table still exists
                result = self._execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                if not result.fetchone():
                    # Original table was dropped, restore from backup
                    self._execute(f"ALTER TABLE {backup_table_name} RENAME TO {table_name}")
                    print(f"Restored {table_name} from backup after migration failure")
                else:
                    # Original table still exists, just drop the backup
                    self._execute(f"DROP TABLE IF EXISTS {backup_table_name}")
            except Exception as restore_error:
                print(f"Error during restore: {restore_error}")
                # Leave backup table for manual recovery
                raise Exception(f"Migration failed for {table_name}. Backup table {backup_table_name} preserved for manual recovery.\nOriginal error: {str(e)}")
            
            raise Exception(f"Error migrating table {table_name}: {str(e)}")
        except Exception as e:
            # If something goes wrong, clean up the _new table
            try:
                self._execute(f"DROP TABLE IF EXISTS {table_name}_new")
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
                    us_table.anno_scavo,
                    us_table.cont_per,
                    us_table.order_layer,
                    us_table.datazione
                FROM pyarchinit_quote
                JOIN us_table ON
                    pyarchinit_quote.sito_q = us_table.sito
                    AND CAST(pyarchinit_quote.area_q AS TEXT) = us_table.area
                    AND CAST(pyarchinit_quote.us_q AS TEXT) = us_table.us
            """,

            'pyarchinit_quote_usm_view': """
                CREATE VIEW pyarchinit_quote_usm_view AS
                SELECT
                    a.rowid AS rowid,
                    a.id_us AS id_us,
                    a.sito AS sito,
                    a.area AS area,
                    a.us AS us,
                    a.d_stratigrafica AS d_stratigrafica,
                    a.d_interpretativa AS d_interpretativa,
                    a.descrizione AS descrizione,
                    a.interpretazione AS interpretazione,
                    a.periodo_iniziale AS periodo_iniziale,
                    a.fase_iniziale AS fase_iniziale,
                    a.periodo_finale AS periodo_finale,
                    a.fase_finale AS fase_finale,
                    a.scavato AS scavato,
                    a.attivita AS attivita,
                    a.anno_scavo AS anno_scavo,
                    a.metodo_di_scavo AS metodo_di_scavo,
                    a.inclusi AS inclusi,
                    a.campioni AS campioni,
                    a.rapporti AS rapporti,
                    a.data_schedatura AS data_schedatura,
                    a.schedatore AS schedatore,
                    a.formazione AS formazione,
                    a.stato_di_conservazione AS stato_di_conservazione,
                    a.colore AS colore,
                    a.consistenza AS consistenza,
                    a.struttura AS struttura,
                    a.cont_per AS cont_per,
                    a.order_layer AS order_layer,
                    a.documentazione AS documentazione,
                    b.rowid AS rowid_1,
                    b.sito_q AS sito_q,
                    b.area_q AS area_q,
                    b.us_q AS us_q,
                    b.unita_misu_q AS unita_misu_q,
                    b.quota_q AS quota_q,
                    b.data AS data,
                    b.disegnatore AS disegnatore,
                    b.rilievo_originale AS rilievo_originale,
                    b.the_geom AS the_geom
                FROM us_table AS a
                JOIN pyarchinit_quote_usm AS b ON
                    a.sito = b.sito_q
                    AND a.area = CAST(b.area_q AS TEXT)
                    AND a.us = CAST(b.us_q AS TEXT)
                ORDER BY a.order_layer DESC
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
                    us_table.attivita as attivita,
                    us_table.anno_scavo as anno_scavo,
                    us_table.metodo_di_scavo as metodo_di_scavo,
                    us_table.inclusi as inclusi,
                    us_table.campioni as campioni,
                    us_table.organici as organici,
                    us_table.inorganici as inorganici,
                    us_table.data_schedatura as data_schedatura,
                    us_table.schedatore as schedatore,
                    us_table.formazione as formazione,
                    us_table.stato_di_conservazione as stato_di_conservazione,
                    us_table.colore as colore,
                    us_table.consistenza as consistenza,
                    us_table.unita_tipo as unita_tipo,
                    us_table.settore as settore,
                    us_table.scavato as scavato,
                    us_table.cont_per as cont_per,
                    us_table.order_layer as order_layer,
                    us_table.documentazione as documentazione,
                    us_table.datazione as datazione,
                    pyunitastratigrafiche.ROWID as ROWID
                FROM pyunitastratigrafiche
                JOIN us_table ON
                    pyunitastratigrafiche.scavo_s = us_table.sito
                    AND CAST(pyunitastratigrafiche.area_s AS TEXT) = us_table.area
                    AND CAST(pyunitastratigrafiche.us_s AS TEXT) = us_table.us
                ORDER BY us_table.order_layer ASC
            """,

            'pyarchinit_usm_view': """
                CREATE VIEW pyarchinit_usm_view AS
                SELECT
                    CAST(pyunitastratigrafiche_usm.gid AS INTEGER) as gid,
                    pyunitastratigrafiche_usm.the_geom as the_geom,
                    pyunitastratigrafiche_usm.tipo_us_s as tipo_us_s,
                    pyunitastratigrafiche_usm.scavo_s as scavo_s,
                    pyunitastratigrafiche_usm.area_s as area_s,
                    pyunitastratigrafiche_usm.us_s as us_s,
                    pyunitastratigrafiche_usm.stratigraph_index_us as stratigraph_index_us,
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
                    us_table.attivita as attivita,
                    us_table.anno_scavo as anno_scavo,
                    us_table.metodo_di_scavo as metodo_di_scavo,
                    us_table.inclusi as inclusi,
                    us_table.campioni as campioni,
                    us_table.organici as organici,
                    us_table.inorganici as inorganici,
                    us_table.data_schedatura as data_schedatura,
                    us_table.schedatore as schedatore,
                    us_table.formazione as formazione,
                    us_table.stato_di_conservazione as stato_di_conservazione,
                    us_table.colore as colore,
                    us_table.consistenza as consistenza,
                    us_table.unita_tipo as unita_tipo,
                    us_table.settore as settore,
                    us_table.scavato as scavato,
                    us_table.cont_per as cont_per,
                    us_table.order_layer as order_layer,
                    us_table.documentazione as documentazione,
                    us_table.datazione as datazione,
                    pyunitastratigrafiche_usm.ROWID as ROWID
                FROM pyunitastratigrafiche_usm
                JOIN us_table ON
                    pyunitastratigrafiche_usm.scavo_s = us_table.sito
                    AND CAST(pyunitastratigrafiche_usm.area_s AS TEXT) = us_table.area
                    AND CAST(pyunitastratigrafiche_usm.us_s AS TEXT) = us_table.us
                ORDER BY us_table.order_layer ASC
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
                    a.sito = b.sito AND
                    a.nr_scheda_taf = b.nr_scheda
            """,

            'pyarchinit_us_negative_doc_view': """
                CREATE VIEW pyarchinit_us_negative_doc_view AS
                SELECT
                    a.rowid AS rowid,
                    a.sito_n AS sito_n,
                    a.area_n AS area_n,
                    a.us_n AS us_n,
                    a.tipo_doc_n AS tipo_doc_n,
                    a.nome_doc_n AS nome_doc_n,
                    a.the_geom AS the_geom,
                    b.rowid AS rowid_1,
                    b.id_us AS id_us,
                    b.sito AS sito,
                    b.area AS area,
                    b.us AS us,
                    b.d_stratigrafica AS d_stratigrafica,
                    b.d_interpretativa AS d_interpretativa,
                    b.descrizione AS descrizione,
                    b.interpretazione AS interpretazione,
                    b.periodo_iniziale AS periodo_iniziale,
                    b.fase_iniziale AS fase_iniziale,
                    b.periodo_finale AS periodo_finale,
                    b.fase_finale AS fase_finale,
                    b.scavato AS scavato,
                    b.attivita AS attivita,
                    b.anno_scavo AS anno_scavo,
                    b.metodo_di_scavo AS metodo_di_scavo,
                    b.inclusi AS inclusi,
                    b.campioni AS campioni,
                    b.rapporti AS rapporti,
                    b.data_schedatura AS data_schedatura,
                    b.schedatore AS schedatore,
                    b.formazione AS formazione,
                    b.stato_di_conservazione AS stato_di_conservazione,
                    b.colore AS colore,
                    b.consistenza AS consistenza,
                    b.struttura AS struttura,
                    b.cont_per AS cont_per,
                    b.order_layer AS order_layer,
                    b.documentazione AS documentazione,
                    b.unita_tipo AS unita_tipo,
                    b.settore AS settore
                FROM pyarchinit_us_negative_doc AS a
                JOIN us_table AS b ON
                    a.sito_n = b.sito
                    AND a.area_n = b.area
                    AND CAST(a.us_n AS TEXT) = b.us
            """
        }
        
        for view_name, view_sql in views_sql.items():
            try:
                self._execute(view_sql)
            except:
                # View might not be needed or table might not exist
                pass
        
        # Register views in SpatiaLite geometry metadata
        self._register_spatialite_views()
    
    def _register_spatialite_views(self):
        """Register views in SpatiaLite geometry metadata tables"""
        try:
            # Check if we have views_geometry_columns table (newer SpatiaLite)
            result = self._execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='views_geometry_columns'
            """)
            
            if result.fetchone():
                # Register pyarchinit_us_view
                try:
                    # Remove any existing registration
                    self._execute("""
                        DELETE FROM views_geometry_columns 
                        WHERE view_name = 'pyarchinit_us_view'
                    """)
                    
                    # Register the view (view_rowid must be lowercase)
                    self._execute("""
                        INSERT INTO views_geometry_columns
                        (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only)
                        VALUES
                        ('pyarchinit_us_view', 'the_geom', 'rowid', 'pyunitastratigrafiche', 'the_geom', 1)
                    """)
                except:
                    pass

                # Register pyarchinit_usm_view
                try:
                    self._execute("""
                        DELETE FROM views_geometry_columns
                        WHERE view_name = 'pyarchinit_usm_view'
                    """)

                    self._execute("""
                        INSERT INTO views_geometry_columns
                        (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only)
                        VALUES
                        ('pyarchinit_usm_view', 'the_geom', 'rowid', 'pyunitastratigrafiche_usm', 'the_geom', 1)
                    """)
                except:
                    pass
            else:
                # Fallback: Register directly in geometry_columns for older SpatiaLite
                try:
                    # Get geometry info from source table
                    result = self._execute("""
                        SELECT coord_dimension, srid, geometry_type 
                        FROM geometry_columns 
                        WHERE f_table_name = 'pyunitastratigrafiche' 
                        AND f_geometry_column = 'the_geom'
                    """)
                    
                    geo_info = result.fetchone()
                    if geo_info:
                        # Remove any existing registration
                        self._execute("""
                            DELETE FROM geometry_columns 
                            WHERE f_table_name = 'pyarchinit_us_view'
                        """)
                        
                        # Register the view
                        self._execute("""
                            INSERT INTO geometry_columns 
                            (f_table_name, f_geometry_column, coord_dimension, srid, geometry_type)
                            VALUES 
                            ('pyarchinit_us_view', 'the_geom', ?, ?, ?)
                        """, geo_info)
                except:
                    pass
                
                # Register other geometry views
                other_views = [
                    ('pyarchinit_usm_view', 'pyunitastratigrafiche_usm'),
                    ('pyarchinit_quote_view', 'pyarchinit_quote'),
                    ('pyarchinit_quote_usm_view', 'pyarchinit_quote_usm'),
                    ('pyarchinit_us_negative_doc_view', 'pyarchinit_us_negative_doc'),
                    ('pyarchinit_uscaratterizzazioni_view', 'pyuscaratterizzazioni'),
                    ('pyarchinit_reperti_view', 'pyarchinit_reperti'),
                    ('pyarchinit_tomba_view', 'pyarchinit_tafonomia')
                ]
                
                for view_name, source_table in other_views:
                    try:
                        self._execute(f"""
                            DELETE FROM views_geometry_columns 
                            WHERE view_name = '{view_name}'
                        """)
                        
                        self._execute(f"""
                            INSERT INTO views_geometry_columns 
                            (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only)
                            VALUES 
                            ('{view_name}', 'the_geom', 'gid', '{source_table}', 'the_geom', 1)
                        """)
                    except:
                        pass
            
            # Also update geometry_columns_auth if it exists
            result = self._execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='geometry_columns_auth'
            """)
            
            if result.fetchone():
                # Register views in geometry_columns_auth
                views_to_register = [
                    'pyarchinit_us_view',
                    'pyarchinit_usm_view',
                    'pyarchinit_quote_view',
                    'pyarchinit_quote_usm_view',
                    'pyarchinit_us_negative_doc_view',
                    'pyarchinit_uscaratterizzazioni_view',
                    'pyarchinit_reperti_view',
                    'pyarchinit_tomba_view'
                ]

                for view_name in views_to_register:
                    try:
                        # Get SRID from source table
                        if view_name == 'pyarchinit_us_view':
                            source_table = 'pyunitastratigrafiche'
                        elif view_name == 'pyarchinit_usm_view':
                            source_table = 'pyunitastratigrafiche_usm'
                        elif view_name == 'pyarchinit_quote_view':
                            source_table = 'pyarchinit_quote'
                        elif view_name == 'pyarchinit_quote_usm_view':
                            source_table = 'pyarchinit_quote_usm'
                        elif view_name == 'pyarchinit_us_negative_doc_view':
                            source_table = 'pyarchinit_us_negative_doc'
                        elif view_name == 'pyarchinit_uscaratterizzazioni_view':
                            source_table = 'pyuscaratterizzazioni'
                        elif view_name == 'pyarchinit_reperti_view':
                            source_table = 'pyarchinit_reperti'
                        elif view_name == 'pyarchinit_tomba_view':
                            source_table = 'pyarchinit_tafonomia'
                        else:
                            continue
                        
                        # Get SRID from source
                        result = self._execute(f"""
                            SELECT srid FROM geometry_columns_auth 
                            WHERE f_table_name = '{source_table}' 
                            AND f_geometry_column = 'the_geom'
                        """)
                        
                        row = result.fetchone()
                        if row:
                            srid = row[0]
                            
                            # Remove existing entry
                            self._execute(f"""
                                DELETE FROM geometry_columns_auth 
                                WHERE f_table_name = '{view_name}'
                            """)
                            
                            # Add new entry
                            self._execute(f"""
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

    def fix_invalid_geometries(self):
        """
        Repair invalid geometries in all geometry tables.
        Uses SpatiaLite's MakeValid() or ST_MakeValid() function.
        Returns a dict with counts of fixed geometries per table.
        """
        if 'postgresql' in self.conn_str.lower():
            return self._fix_invalid_geometries_postgres()
        else:
            return self._fix_invalid_geometries_sqlite()

    def _fix_invalid_geometries_sqlite(self):
        """Fix invalid geometries in SQLite/SpatiaLite database.

        Uses a raw connection with SpatiaLite extension loaded to ensure
        spatial functions are available.
        """
        import sqlite3
        import os
        import platform

        results = {}

        # Extract database path from connection string
        # Format: sqlite:///path/to/db.sqlite
        db_path = self.conn_str.replace('sqlite:///', '')

        if not os.path.exists(db_path):
            print(f"Database file not found: {db_path}")
            return results

        # List of geometry tables with their geometry column name
        geometry_tables = [
            ('pyunitastratigrafiche', 'the_geom'),
            ('pyunitastratigrafiche_usm', 'the_geom'),
            ('pyarchinit_quote', 'the_geom'),
            ('pyarchinit_quote_usm', 'the_geom'),
            ('pyarchinit_us_negative_doc', 'the_geom'),
            ('pyarchinit_reperti', 'the_geom'),
            ('pyarchinit_tafonomia', 'the_geom'),
            ('pyarchinit_campionature', 'the_geom'),
            ('pyarchinit_linee_rif', 'the_geom'),
            ('pyarchinit_punti_rif', 'the_geom'),
            ('pyarchinit_sezioni', 'the_geom'),
            ('pyarchinit_siti', 'the_geom'),
            ('pyarchinit_siti_polygonal', 'the_geom'),
            ('pyarchinit_ripartizioni_spaziali', 'the_geom'),
            ('pyarchinit_documentazione', 'the_geom'),
            ('pyarchinit_individui', 'the_geom'),
            ('pyarchinit_strutture_ipotesi', 'the_geom'),
        ]

        conn = None
        try:
            # Connect with extension loading enabled
            conn = sqlite3.connect(db_path)
            conn.enable_load_extension(True)

            # Try to load SpatiaLite extension
            spatialite_loaded = False
            spatialite_paths = []

            # Platform-specific paths for mod_spatialite
            if platform.system() == 'Darwin':  # macOS
                spatialite_paths = [
                    'mod_spatialite',
                    # QGIS bundle paths (most common on macOS)
                    '/Applications/QGIS.app/Contents/MacOS/lib/mod_spatialite.so',
                    '/Applications/QGIS.app/Contents/MacOS/lib/mod_spatialite',
                    '/Applications/QGIS-LTR.app/Contents/MacOS/lib/mod_spatialite.so',
                    '/Applications/QGIS-LTR.app/Contents/MacOS/lib/mod_spatialite',
                    # Homebrew paths
                    '/opt/homebrew/lib/mod_spatialite.dylib',
                    '/opt/homebrew/lib/mod_spatialite',
                    '/usr/local/lib/mod_spatialite.dylib',
                    '/usr/local/lib/mod_spatialite',
                    '/opt/homebrew/opt/libspatialite/lib/mod_spatialite.dylib',
                    '/usr/local/opt/libspatialite/lib/mod_spatialite.dylib',
                ]
            elif platform.system() == 'Windows':
                spatialite_paths = [
                    'mod_spatialite',
                    'mod_spatialite.dll',
                ]
            else:  # Linux
                spatialite_paths = [
                    'mod_spatialite',
                    '/usr/lib/x86_64-linux-gnu/mod_spatialite.so',
                    '/usr/lib/mod_spatialite.so',
                ]

            for sp_path in spatialite_paths:
                try:
                    conn.load_extension(sp_path)
                    spatialite_loaded = True
                    print(f"  SpatiaLite loaded from: {sp_path}")
                    break
                except Exception as e:
                    print(f"  Tried {sp_path}: {str(e)}")
                    continue

            if not spatialite_loaded:
                print("  Warning: Could not load SpatiaLite extension, trying with existing functions...")
                # Try using pyspatialite if available
                try:
                    from pyspatialite import dbapi2 as spatialite
                    conn.close()
                    conn = spatialite.connect(db_path)
                    spatialite_loaded = True
                    print("  Loaded using pyspatialite")
                except ImportError:
                    pass

            cursor = conn.cursor()

            # Check which repair function is available
            repair_function = None
            repair_functions_to_try = ['MakeValid', 'ST_MakeValid', 'GUnion']

            for func in repair_functions_to_try:
                try:
                    # Test if function exists by calling it on a simple geometry
                    cursor.execute(f"SELECT {func}(GeomFromText('POINT(0 0)'))")
                    repair_function = func
                    print(f"  Using repair function: {repair_function}")
                    break
                except Exception:
                    continue

            for table_name, geom_column in geometry_tables:
                try:
                    # Check if table exists
                    cursor.execute(f"""
                        SELECT name FROM sqlite_master
                        WHERE type='table' AND name=?
                    """, (table_name,))
                    if not cursor.fetchone():
                        continue

                    # Check if geometry column exists
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [row[1] for row in cursor.fetchall()]
                    if geom_column not in columns:
                        continue

                    # Count invalid geometries before fix
                    try:
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM {table_name}
                            WHERE {geom_column} IS NOT NULL
                            AND ST_IsValid({geom_column}) = 0
                        """)
                        invalid_count = cursor.fetchone()[0]
                    except Exception as e:
                        print(f"  {table_name}: Could not check validity - {str(e)}")
                        continue

                    if invalid_count > 0:
                        print(f"  {table_name}: {invalid_count} invalid geometries found, fixing...")

                        fixed = False
                        error_msg = None

                        # Try repair function if available
                        if repair_function:
                            try:
                                cursor.execute(f"""
                                    UPDATE {table_name}
                                    SET {geom_column} = {repair_function}({geom_column})
                                    WHERE {geom_column} IS NOT NULL
                                    AND ST_IsValid({geom_column}) = 0
                                """)
                                conn.commit()
                                fixed = True
                            except Exception as e:
                                error_msg = str(e)
                                print(f"    {repair_function} failed: {error_msg}")

                        # Try Buffer(0) as fallback - most reliable method
                        if not fixed:
                            try:
                                cursor.execute(f"""
                                    UPDATE {table_name}
                                    SET {geom_column} = ST_Buffer({geom_column}, 0)
                                    WHERE {geom_column} IS NOT NULL
                                    AND ST_IsValid({geom_column}) = 0
                                """)
                                conn.commit()
                                fixed = True
                            except Exception as e:
                                error_msg = str(e)
                                print(f"    ST_Buffer(0) failed: {error_msg}")

                        # Try Buffer with small positive then negative value
                        if not fixed:
                            try:
                                cursor.execute(f"""
                                    UPDATE {table_name}
                                    SET {geom_column} = ST_Buffer(ST_Buffer({geom_column}, 0.0001), -0.0001)
                                    WHERE {geom_column} IS NOT NULL
                                    AND ST_IsValid({geom_column}) = 0
                                """)
                                conn.commit()
                                fixed = True
                            except Exception as e:
                                error_msg = str(e)
                                print(f"    Double buffer failed: {error_msg}")

                        if not fixed:
                            results[table_name] = {'found': invalid_count, 'fixed': 0, 'error': error_msg}
                            continue

                        # Count remaining invalid geometries
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM {table_name}
                            WHERE {geom_column} IS NOT NULL
                            AND ST_IsValid({geom_column}) = 0
                        """)
                        remaining = cursor.fetchone()[0]
                        fixed_count = invalid_count - remaining

                        results[table_name] = {'found': invalid_count, 'fixed': fixed_count, 'remaining': remaining}
                        print(f"    Fixed {fixed_count} geometries, {remaining} still invalid")
                    else:
                        results[table_name] = {'found': 0, 'fixed': 0}

                except Exception as e:
                    print(f"  {table_name}: Error - {str(e)}")
                    results[table_name] = {'found': 0, 'fixed': 0, 'error': str(e)}

        except Exception as e:
            print(f"Database connection error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

        return results

    def _fix_invalid_geometries_postgres(self):
        """Fix invalid geometries in PostgreSQL/PostGIS database"""
        results = {}

        # List of geometry tables with their geometry column name
        geometry_tables = [
            ('pyunitastratigrafiche', 'the_geom'),
            ('pyunitastratigrafiche_usm', 'the_geom'),
            ('pyarchinit_quote', 'the_geom'),
            ('pyarchinit_quote_usm', 'the_geom'),
            ('pyarchinit_us_negative_doc', 'the_geom'),
            ('pyarchinit_reperti', 'the_geom'),
            ('pyarchinit_tafonomia', 'the_geom'),
            ('pyarchinit_campionature', 'the_geom'),
            ('pyarchinit_linee_rif', 'the_geom'),
            ('pyarchinit_punti_rif', 'the_geom'),
            ('pyarchinit_sezioni', 'the_geom'),
            ('pyarchinit_siti', 'the_geom'),
            ('pyarchinit_siti_polygonal', 'the_geom'),
            ('pyarchinit_ripartizioni_spaziali', 'the_geom'),
            ('pyarchinit_documentazione', 'the_geom'),
            ('pyarchinit_individui', 'the_geom'),
            ('pyarchinit_strutture_ipotesi', 'the_geom'),
        ]

        for table_name, geom_column in geometry_tables:
            try:
                # Check if table exists
                result = self._execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = '{table_name}'
                    )
                """)
                row = result.fetchone()
                if not row or not row[0]:
                    continue

                # Check if geometry column exists
                result = self._execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.columns
                        WHERE table_name = '{table_name}' AND column_name = '{geom_column}'
                    )
                """)
                row = result.fetchone()
                if not row or not row[0]:
                    continue

                # Count invalid geometries before fix
                result = self._execute(f"""
                    SELECT COUNT(*) FROM {table_name}
                    WHERE {geom_column} IS NOT NULL
                    AND NOT ST_IsValid({geom_column})
                """)
                row = result.fetchone()
                invalid_count = row[0] if row else 0

                if invalid_count > 0:
                    print(f"  {table_name}: {invalid_count} invalid geometries found, fixing...")

                    fixed = False
                    error_msg = None

                    # Use ST_MakeValid (PostGIS 2.0+)
                    try:
                        self._execute(f"""
                            UPDATE {table_name}
                            SET {geom_column} = ST_MakeValid({geom_column})
                            WHERE {geom_column} IS NOT NULL
                            AND NOT ST_IsValid({geom_column})
                        """)
                        fixed = True
                    except Exception as e:
                        error_msg = str(e)
                        print(f"    ST_MakeValid failed: {error_msg}")

                    # Fallback: try ST_Buffer(0)
                    if not fixed:
                        try:
                            self._execute(f"""
                                UPDATE {table_name}
                                SET {geom_column} = ST_Buffer({geom_column}, 0)
                                WHERE {geom_column} IS NOT NULL
                                AND NOT ST_IsValid({geom_column})
                            """)
                            fixed = True
                        except Exception as e:
                            error_msg = str(e)
                            print(f"    ST_Buffer(0) failed: {error_msg}")

                    if not fixed:
                        results[table_name] = {'found': invalid_count, 'fixed': 0, 'error': error_msg}
                        continue

                    # Count remaining invalid geometries
                    result = self._execute(f"""
                        SELECT COUNT(*) FROM {table_name}
                        WHERE {geom_column} IS NOT NULL
                        AND NOT ST_IsValid({geom_column})
                    """)
                    row = result.fetchone()
                    remaining = row[0] if row else 0
                    fixed_count = invalid_count - remaining

                    results[table_name] = {'found': invalid_count, 'fixed': fixed_count, 'remaining': remaining}
                    print(f"    Fixed {fixed_count} geometries, {remaining} still invalid")
                else:
                    results[table_name] = {'found': 0, 'fixed': 0}

            except Exception as e:
                print(f"  {table_name}: Error - {str(e)}")
                results[table_name] = {'found': 0, 'fixed': 0, 'error': str(e)}

        return results

    def rebuild_geometry_tables(self):
        """
        Rebuild geometry tables with correct column types (TEXT instead of INT).
        This fixes JOIN issues with views that expect TEXT columns.
        """
        if 'postgresql' in self.conn_str.lower():
            return self._rebuild_geometry_tables_postgres()
        else:
            return self._rebuild_geometry_tables_sqlite()

    def _rebuild_geometry_tables_sqlite(self):
        """Rebuild SQLite geometry tables with correct column types."""
        import sqlite3
        import os

        results = {}

        # Extract database path from connection string
        db_path = self.conn_str.replace('sqlite:///', '')

        if not os.path.exists(db_path):
            print(f"Database file not found: {db_path}")
            return results

        # Tables to rebuild with their SRID
        geometry_tables = [
            ('pyunitastratigrafiche', 3004),
            ('pyunitastratigrafiche_usm', 3004),
        ]

        conn = None
        try:
            conn = sqlite3.connect(db_path)
            conn.enable_load_extension(True)

            # Load SpatiaLite
            spatialite_paths = [
                'mod_spatialite',
                '/Applications/QGIS.app/Contents/MacOS/lib/mod_spatialite.so',
                '/Applications/QGIS-LTR.app/Contents/MacOS/lib/mod_spatialite.so',
                '/opt/homebrew/lib/mod_spatialite.dylib',
                '/usr/local/lib/mod_spatialite.dylib',
                '/usr/lib/x86_64-linux-gnu/mod_spatialite.so',
            ]

            spatialite_loaded = False
            for sp_path in spatialite_paths:
                try:
                    conn.load_extension(sp_path)
                    spatialite_loaded = True
                    print(f"  SpatiaLite loaded from: {sp_path}")
                    break
                except Exception:
                    continue

            if not spatialite_loaded:
                print("  ERROR: Could not load SpatiaLite extension")
                return results

            cursor = conn.cursor()

            for table_name, srid in geometry_tables:
                try:
                    # Check if table exists
                    cursor.execute(f"""
                        SELECT name FROM sqlite_master
                        WHERE type='table' AND name=?
                    """, (table_name,))
                    if not cursor.fetchone():
                        print(f"  {table_name}: table does not exist, skipping")
                        continue

                    print(f"  Rebuilding {table_name}...")

                    # Get current SRID from geometry_columns
                    cursor.execute("""
                        SELECT srid FROM geometry_columns
                        WHERE f_table_name = ?
                    """, (table_name,))
                    row = cursor.fetchone()
                    if row:
                        srid = row[0]
                    print(f"    Using SRID: {srid}")

                    # Backup data
                    cursor.execute(f"SELECT * FROM {table_name}")
                    data = cursor.fetchall()
                    print(f"    Backed up {len(data)} records")

                    # Get column names
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns_info = cursor.fetchall()
                    column_names = [col[1] for col in columns_info]

                    # Drop spatial index
                    cursor.execute(f"SELECT DisableSpatialIndex('{table_name}', 'the_geom')")
                    cursor.execute(f"DROP TABLE IF EXISTS idx_{table_name}_the_geom")

                    # Remove from geometry_columns
                    cursor.execute(f"SELECT DiscardGeometryColumn('{table_name}', 'the_geom')")

                    # Drop old table
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

                    # Create new table with correct types (TEXT for area_s, us_s, scavo_s)
                    cursor.execute(f"""
                        CREATE TABLE {table_name} (
                            gid INTEGER PRIMARY KEY AUTOINCREMENT,
                            area_s TEXT,
                            scavo_s TEXT,
                            us_s TEXT,
                            stratigraph_index_us INTEGER,
                            tipo_us_s TEXT,
                            rilievo_originale TEXT,
                            disegnatore TEXT,
                            data TEXT,
                            tipo_doc TEXT,
                            nome_doc TEXT,
                            coord TEXT,
                            unita_tipo_s TEXT
                        )
                    """)

                    # Add geometry column
                    cursor.execute(f"""
                        SELECT AddGeometryColumn('{table_name}', 'the_geom', {srid}, 'MULTIPOLYGON', 'XY')
                    """)

                    # Restore data with type conversion
                    if data:
                        for row in data:
                            # Convert values, handling the column order
                            # Original: gid, area_s, scavo_s, us_s, stratigraph_index_us, tipo_us_s,
                            #           rilievo_originale, disegnatore, data, tipo_doc, nome_doc, coord, the_geom, unita_tipo_s
                            values = list(row)

                            # Find the_geom position (should be index 12 based on original schema)
                            geom_idx = column_names.index('the_geom') if 'the_geom' in column_names else -1

                            if geom_idx >= 0 and len(values) > geom_idx:
                                geom_value = values[geom_idx]
                                # Remove geometry from values list for separate handling
                                values_without_geom = values[:geom_idx] + values[geom_idx+1:]

                                # Build column list without the_geom
                                cols_without_geom = [c for c in column_names if c != 'the_geom']

                                # Insert with geometry
                                placeholders = ', '.join(['?' for _ in cols_without_geom])
                                col_list = ', '.join(cols_without_geom)

                                cursor.execute(f"""
                                    INSERT INTO {table_name} ({col_list}, the_geom)
                                    VALUES ({placeholders}, ?)
                                """, values_without_geom + [geom_value])
                            else:
                                # No geometry column found, insert all values
                                placeholders = ', '.join(['?' for _ in values])
                                cursor.execute(f"""
                                    INSERT INTO {table_name} VALUES ({placeholders})
                                """, values)

                        print(f"    Restored {len(data)} records")

                    # Create spatial index
                    cursor.execute(f"SELECT CreateSpatialIndex('{table_name}', 'the_geom')")
                    print(f"    Created spatial index")

                    conn.commit()
                    results[table_name] = {'status': 'success', 'records': len(data)}
                    print(f"    {table_name} rebuilt successfully!")

                except Exception as e:
                    conn.rollback()
                    print(f"  {table_name}: Error - {str(e)}")
                    results[table_name] = {'status': 'error', 'error': str(e)}

            # Recreate views
            print("\n  Recreating views...")
            self._recreate_us_views_sqlite(cursor)
            conn.commit()
            print("  Views recreated successfully!")

        except Exception as e:
            print(f"Database error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

        return results

    def _recreate_us_views_sqlite(self, cursor):
        """Recreate the US-related views in SQLite."""

        # Drop existing views
        views_to_recreate = [
            'pyarchinit_us_view',
            'pyarchinit_usm_view',
        ]

        for view_name in views_to_recreate:
            cursor.execute(f"DROP VIEW IF EXISTS {view_name}")

        # Recreate pyarchinit_us_view
        cursor.execute("""
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
                us_table.attivita as attivita,
                us_table.anno_scavo as anno_scavo,
                us_table.metodo_di_scavo as metodo_di_scavo,
                us_table.inclusi as inclusi,
                us_table.campioni as campioni,
                us_table.organici as organici,
                us_table.inorganici as inorganici,
                us_table.data_schedatura as data_schedatura,
                us_table.schedatore as schedatore,
                us_table.formazione as formazione,
                us_table.stato_di_conservazione as stato_di_conservazione,
                us_table.colore as colore,
                us_table.consistenza as consistenza,
                us_table.unita_tipo as unita_tipo,
                us_table.settore as settore,
                us_table.scavato as scavato,
                us_table.cont_per as cont_per,
                us_table.order_layer as order_layer,
                us_table.documentazione as documentazione,
                us_table.datazione as datazione,
                pyunitastratigrafiche.ROWID as ROWID
            FROM pyunitastratigrafiche
            JOIN us_table ON
                pyunitastratigrafiche.scavo_s = us_table.sito
                AND pyunitastratigrafiche.area_s = us_table.area
                AND pyunitastratigrafiche.us_s = us_table.us
            ORDER BY us_table.order_layer ASC
        """)
        print("    Created pyarchinit_us_view")

        # Recreate pyarchinit_usm_view
        cursor.execute("""
            CREATE VIEW pyarchinit_usm_view AS
            SELECT
                CAST(pyunitastratigrafiche_usm.gid AS INTEGER) as gid,
                pyunitastratigrafiche_usm.the_geom as the_geom,
                pyunitastratigrafiche_usm.tipo_us_s as tipo_us_s,
                pyunitastratigrafiche_usm.scavo_s as scavo_s,
                pyunitastratigrafiche_usm.area_s as area_s,
                pyunitastratigrafiche_usm.us_s as us_s,
                pyunitastratigrafiche_usm.stratigraph_index_us as stratigraph_index_us,
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
                us_table.attivita as attivita,
                us_table.anno_scavo as anno_scavo,
                us_table.metodo_di_scavo as metodo_di_scavo,
                us_table.inclusi as inclusi,
                us_table.campioni as campioni,
                us_table.organici as organici,
                us_table.inorganici as inorganici,
                us_table.data_schedatura as data_schedatura,
                us_table.schedatore as schedatore,
                us_table.formazione as formazione,
                us_table.stato_di_conservazione as stato_di_conservazione,
                us_table.colore as colore,
                us_table.consistenza as consistenza,
                us_table.unita_tipo as unita_tipo,
                us_table.settore as settore,
                us_table.scavato as scavato,
                us_table.cont_per as cont_per,
                us_table.order_layer as order_layer,
                us_table.documentazione as documentazione,
                us_table.datazione as datazione,
                pyunitastratigrafiche_usm.ROWID as ROWID
            FROM pyunitastratigrafiche_usm
            JOIN us_table ON
                pyunitastratigrafiche_usm.scavo_s = us_table.sito
                AND pyunitastratigrafiche_usm.area_s = us_table.area
                AND pyunitastratigrafiche_usm.us_s = us_table.us
            ORDER BY us_table.order_layer ASC
        """)
        print("    Created pyarchinit_usm_view")

    def _rebuild_geometry_tables_postgres(self):
        """Rebuild PostgreSQL geometry tables with correct column types."""
        results = {}

        # For PostgreSQL, we need to alter the column types
        geometry_tables = [
            'pyunitastratigrafiche',
            'pyunitastratigrafiche_usm',
        ]

        for table_name in geometry_tables:
            try:
                # Check if table exists
                result = self._execute(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = '{table_name}'
                    )
                """)
                if not result.fetchone()[0]:
                    continue

                print(f"  Rebuilding {table_name}...")

                # Alter column types to TEXT
                for col in ['area_s', 'us_s', 'scavo_s']:
                    try:
                        self._execute(f"""
                            ALTER TABLE {table_name}
                            ALTER COLUMN {col} TYPE TEXT
                        """)
                        print(f"    Changed {col} to TEXT")
                    except Exception as e:
                        if 'already' not in str(e).lower():
                            print(f"    Warning changing {col}: {str(e)}")

                results[table_name] = {'status': 'success'}
                print(f"    {table_name} rebuilt successfully!")

            except Exception as e:
                print(f"  {table_name}: Error - {str(e)}")
                results[table_name] = {'status': 'error', 'error': str(e)}

        # Recreate views
        print("\n  Recreating views...")
        self._recreate_us_views_postgres()
        print("  Views recreated successfully!")

        return results

    def _recreate_us_views_postgres(self):
        """Recreate the US-related views in PostgreSQL."""

        # Drop and recreate views
        self._execute("DROP VIEW IF EXISTS pyarchinit_us_view CASCADE")
        self._execute("DROP VIEW IF EXISTS pyarchinit_usm_view CASCADE")

        # Recreate pyarchinit_us_view (same as SQLite version)
        self._execute("""
            CREATE VIEW pyarchinit_us_view AS
            SELECT
                pyunitastratigrafiche.gid::INTEGER as gid,
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
                us_table.attivita as attivita,
                us_table.anno_scavo as anno_scavo,
                us_table.metodo_di_scavo as metodo_di_scavo,
                us_table.inclusi as inclusi,
                us_table.campioni as campioni,
                us_table.organici as organici,
                us_table.inorganici as inorganici,
                us_table.data_schedatura as data_schedatura,
                us_table.schedatore as schedatore,
                us_table.formazione as formazione,
                us_table.stato_di_conservazione as stato_di_conservazione,
                us_table.colore as colore,
                us_table.consistenza as consistenza,
                us_table.unita_tipo as unita_tipo,
                us_table.settore as settore,
                us_table.scavato as scavato,
                us_table.cont_per as cont_per,
                us_table.order_layer as order_layer,
                us_table.documentazione as documentazione,
                us_table.datazione as datazione
            FROM pyunitastratigrafiche
            JOIN us_table ON
                pyunitastratigrafiche.scavo_s = us_table.sito
                AND pyunitastratigrafiche.area_s = us_table.area
                AND pyunitastratigrafiche.us_s = us_table.us
            ORDER BY us_table.order_layer ASC
        """)
        print("    Created pyarchinit_us_view")

        # Recreate pyarchinit_usm_view
        self._execute("""
            CREATE VIEW pyarchinit_usm_view AS
            SELECT
                pyunitastratigrafiche_usm.gid::INTEGER as gid,
                pyunitastratigrafiche_usm.the_geom as the_geom,
                pyunitastratigrafiche_usm.tipo_us_s as tipo_us_s,
                pyunitastratigrafiche_usm.scavo_s as scavo_s,
                pyunitastratigrafiche_usm.area_s as area_s,
                pyunitastratigrafiche_usm.us_s as us_s,
                pyunitastratigrafiche_usm.stratigraph_index_us as stratigraph_index_us,
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
                us_table.attivita as attivita,
                us_table.anno_scavo as anno_scavo,
                us_table.metodo_di_scavo as metodo_di_scavo,
                us_table.inclusi as inclusi,
                us_table.campioni as campioni,
                us_table.organici as organici,
                us_table.inorganici as inorganici,
                us_table.data_schedatura as data_schedatura,
                us_table.schedatore as schedatore,
                us_table.formazione as formazione,
                us_table.stato_di_conservazione as stato_di_conservazione,
                us_table.colore as colore,
                us_table.consistenza as consistenza,
                us_table.unita_tipo as unita_tipo,
                us_table.settore as settore,
                us_table.scavato as scavato,
                us_table.cont_per as cont_per,
                us_table.order_layer as order_layer,
                us_table.documentazione as documentazione,
                us_table.datazione as datazione
            FROM pyunitastratigrafiche_usm
            JOIN us_table ON
                pyunitastratigrafiche_usm.scavo_s = us_table.sito
                AND pyunitastratigrafiche_usm.area_s = us_table.area
                AND pyunitastratigrafiche_usm.us_s = us_table.us
            ORDER BY us_table.order_layer ASC
        """)
        print("    Created pyarchinit_usm_view")

    def _migrate_tma_table(self):
        """Migrate old TMA table structure to new structure with separate materials table"""
        try:
            print("Starting TMA table migration...")
            
            # Backup existing data
            old_data = self._execute("SELECT * FROM tma_table").fetchall()
            print(f"Found {len(old_data)} records to migrate")
            
            # Drop the old table
            self._execute("DROP TABLE IF EXISTS tma_table")
            
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
                    self._execute("""
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
                        
                        self._execute("""
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

    def _add_concurrency_columns(self):
        """Add concurrency columns to all PyArchInit tables if they don't exist"""

        # Helper function for safe table loading - define at the start
        def safe_load_table(table_name):
            """Load a table handling encoding errors"""
            try:
                # SQLAlchemy 2.0: use autoload_with instead of autoload=True
                return Table(table_name, self.metadata, autoload_with=self.engine)
            except Exception:
                return None

        try:
            # List of all PyArchInit tables that should have concurrency columns
            tables_to_update = [
                'us_table',
                'site_table',
                'periodizzazione_table',
                'inventario_materiali_table',
                'struttura_table',
                'tomba_table',
                'schedaind_table',
                'detsesso_table',
                'deteta_table',
                'documentazione_table',
                'campioni_table',
                'inventario_lapidei_table',
                'media_table',
                'media_thumb_table',
                'media_to_entity_table',
                'pyarchinit_thesaurus_sigle',
                'pottery_table',
                'tma_materiali_archeologici',
                'tma_materiali_ripetibili'
            ]

            # Concurrency columns to add
            concurrency_columns = [
                ('version_number', 'INTEGER', '1'),
                ('editing_by', 'VARCHAR(100)', None),
                ('editing_since', 'TIMESTAMP', None),
                ('last_modified_by', 'VARCHAR(100)', "'system'"),
                ('last_modified_timestamp', 'TIMESTAMP', 'CURRENT_TIMESTAMP')
            ]

            # Check if we're using SQLite
            is_sqlite = 'sqlite' in str(self.engine.url).lower()

            for table_name in tables_to_update:
                try:
                    # Load table metadata if it exists
                    table = safe_load_table(table_name)
                    if table is None:
                        continue

                    # Get existing columns
                    existing_columns = [col.name for col in table.columns]

                    # Add missing concurrency columns
                    for col_name, col_type, col_default in concurrency_columns:
                        if col_name not in existing_columns:
                            try:
                                if is_sqlite:
                                    # SQLite syntax
                                    if col_default:
                                        self._execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type} DEFAULT {col_default}")
                                    else:
                                        self._execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                                else:
                                    # PostgreSQL syntax
                                    if col_default:
                                        self._execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type} DEFAULT {col_default}")
                                    else:
                                        self._execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                                print(f"Added {col_name} to {table_name}")
                            except Exception as e:
                                # Column might already exist or table might have issues
                                pass

                except Exception as e:
                    # Skip tables that don't exist or have other issues
                    continue

            print("Concurrency columns check completed")

        except Exception as e:
            print(f"Error adding concurrency columns: {str(e)}")
            # Don't raise - let the process continue
#engine.execute