'''
PostgreSQL Database Updater for PyArchInit
Handles database schema updates and migrations for PostgreSQL databases

Created on 2024
@author: Enzo Cocca <enzo.ccc@gmail.com>
'''

from datetime import datetime

try:
    from qgis.PyQt.QtWidgets import QMessageBox
    from qgis.core import Qgis, QgsMessageLog
    QGIS_AVAILABLE = True
except:
    QGIS_AVAILABLE = False


class PostgresDbUpdater:
    def __init__(self, db_manager, parent=None):
        """
        Inizializza l'updater per PostgreSQL

        Args:
            db_manager: istanza di Pyarchinit_db_management
            parent: widget parent per i messaggi (opzionale)
        """
        self.db_manager = db_manager
        self.parent = parent
        self.updates_made = []

    def log_message(self, message, level=None):
        """Log dei messaggi tramite QgsMessageLog"""
        if QGIS_AVAILABLE:
            QgsMessageLog.logMessage(message, "PyArchInit DB Updater", level or Qgis.Info)
        self.updates_made.append(message)

    def run_essential_migrations(self):
        """
        Esegue migrazioni essenziali (leggere) necessarie per evitare errori.
        Questa funzione è pensata per essere veloce e sicura da eseguire ad ogni connessione.
        """
        try:
            # Aggiorna struttura_table con nuovi campi AR
            self.update_struttura_table()
            # Aggiorna la view pyarchinit_strutture_view con i nuovi campi
            self.update_strutture_view()
            # Crea fauna_table se non esiste
            self.update_fauna_table()
            # Aggiunge voci thesaurus per fauna_table
            self.update_fauna_thesaurus()
            # Aggiunge voci thesaurus per ut_table
            self.update_ut_thesaurus()
            # Fix thesaurus entries with display names instead of table names
            self.fix_thesaurus_nome_tabella()
            # Aggiorna ut_table con nuovi campi analisi (v4.9.67+)
            self.update_ut_table()
        except Exception as e:
            self.log_message(f"Errore durante migrazioni essenziali: {e}")

    def check_and_update_database(self):
        """Controlla e aggiorna il database PostgreSQL"""
        try:
            # FAST PATH: Run essential column migrations only (lightweight)
            # These are needed to prevent errors when accessing forms
            self.run_essential_migrations()

            # PERFORMANCE FIX: Skip heavy checks on connection
            # These should only run on explicit user request (menu "Update Database")
            self.log_message("Database check skipped for performance - use 'Update Database' menu if needed")
            return True

            # === DISABLED FOR PERFORMANCE ===
            # All the code below is disabled to speed up connection
            # Uncomment if you need to force database updates

            self.log_message("Controllo database PostgreSQL per aggiornamenti necessari...")

            # Quick check if views already exist with correct columns - skip heavy operations
            from sqlalchemy import text
            try:
                us_view_check = text("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'pyarchinit_us_view'")
                usm_view_check = text("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'pyarchinit_usm_view'")
                us_cols = self.db_manager._execute_sql(us_view_check).scalar() or 0
                usm_cols = self.db_manager._execute_sql(usm_view_check).scalar() or 0
                views_exist = us_cols >= 80 and usm_cols >= 60  # Views have ~85 and ~66 columns
            except:
                views_exist = False

            # Aggiorna la tabella thesaurus
            self.update_thesaurus_table()

            # Aggiorna la tabella reperti
            self.update_reperti_table()

            # Skip heavy VIEW operations if they already exist
            if not views_exist:
                # Aggiorna la view pyarchinit_us_view
                self.update_us_view()

                # Aggiorna la view pyarchinit_usm_view
                self.update_usm_view()
            else:
                self.log_message("Views già esistenti e aggiornate - skip ricreazione")

            # Installa/aggiorna i trigger per il tracking delle attività
            self.update_activity_triggers()

            # Installa/aggiorna le voci thesaurus per Pottery
            self.update_pottery_thesaurus()

            # Aggiorna pottery_table con nuovi campi decorazione
            self.update_pottery_table()

            # Installa/aggiorna le funzioni per la sincronizzazione automatica dei GRANT
            self.install_grant_sync_functions()

            # Aggiorna inventario_materiali_table con nuovi campi photo_id e drawing_id
            self.update_inventario_materiali_table()

            # Aggiorna struttura_table con nuovi campi Architettura Rupestre
            self.update_struttura_table()

            # Crea indici di performance per query frequenti
            self.create_performance_indexes()

            if self.updates_made:
                message = f"Database PostgreSQL aggiornato con successo!\n\nModifiche effettuate:\n" + \
                         "\n".join(f"- {update}" for update in self.updates_made)
                if QGIS_AVAILABLE and self.parent:
                    QMessageBox.information(self.parent, "Aggiornamento Completato", message)
                else:
                    print(message)
            else:
                self.log_message("Nessun aggiornamento necessario per il database PostgreSQL")

            return True

        except Exception as e:
            error_msg = f"Errore durante l'aggiornamento del database PostgreSQL: {str(e)}"
            self.log_message(error_msg)
            if QGIS_AVAILABLE and self.parent:
                QMessageBox.critical(self.parent, "Errore Aggiornamento", error_msg)
            return False
    
    def column_exists(self, table_name, column_name):
        """Verifica se una colonna esiste nella tabella"""
        try:
            from sqlalchemy import text
            # Use direct query with values interpolated (safe for known table/column names)
            query = text(f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                AND column_name = '{column_name}'
            """)
            result = self.db_manager._execute_sql(query)
            return result.fetchone() is not None
        except Exception as e:
            self.log_message(f"Errore verificando colonna {column_name} in {table_name}: {e}")
            return False
    
    def add_column_if_missing(self, table_name, column_name, column_type, default_value=None):
        """Aggiunge una colonna se non esiste"""
        if not self.column_exists(table_name, column_name):
            try:
                from sqlalchemy import text
                if default_value is not None:
                    sql = text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} DEFAULT {default_value}")
                else:
                    sql = text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")

                # Use connection context for proper transaction handling
                with self.db_manager.engine.connect() as conn:
                    conn.execute(sql)
                    conn.execute(text("COMMIT"))
                self.log_message(f"Aggiunta colonna {column_name} a tabella {table_name}")
                return True
            except Exception as e:
                self.log_message(f"Errore aggiungendo colonna {column_name} a {table_name}: {e}")
                return False
        return False

    def get_column_position(self, table_name, column_name):
        """Restituisce la posizione ordinale di una colonna"""
        try:
            from sqlalchemy import text
            # Use direct query with values interpolated (safe for known table/column names)
            query = text(f"""
                SELECT ordinal_position
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                AND column_name = '{column_name}'
            """)
            result = self.db_manager._execute_sql(query)
            row = result.fetchone()
            return row[0] if row else None
        except Exception as e:
            self.log_message(f"Errore verificando posizione colonna {column_name} in {table_name}: {e}")
            return None

    def reorder_pottery_datazione_column(self):
        """
        Riordina la colonna datazione nella pottery_table se si trova dopo i campi audit.
        La colonna datazione deve essere in posizione 36 (dopo decoration_position e prima di editing_by).
        """
        try:
            from sqlalchemy import text

            # Verifica se datazione esiste e se è dopo editing_by
            datazione_pos = self.get_column_position('pottery_table', 'datazione')
            editing_by_pos = self.get_column_position('pottery_table', 'editing_by')

            if datazione_pos is None:
                return False  # datazione non esiste ancora

            if editing_by_pos is None:
                return False  # audit fields non esistono ancora

            if datazione_pos < editing_by_pos:
                self.log_message("Colonna datazione già nella posizione corretta")
                return False  # datazione è già prima di editing_by

            self.log_message("Riordinamento colonna datazione in pottery_table...")

            # Esegui il riordinamento ricreando la tabella
            reorder_sql = text("""
                DO $$
                DECLARE
                    v_view_def TEXT;
                BEGIN
                    -- Salva la definizione della view se esiste
                    SELECT pg_get_viewdef('active_editing_sessions', true) INTO v_view_def;

                    -- Drop della view
                    DROP VIEW IF EXISTS active_editing_sessions;

                    -- Crea tabella temporanea con ordine corretto
                    CREATE TABLE pottery_table_reorder (
                        id_rep BIGINT NOT NULL,
                        id_number BIGINT,
                        sito text,
                        area text,
                        us TEXT,
                        box BIGINT,
                        photo text,
                        drawing text,
                        anno BIGINT,
                        fabric text,
                        percent text,
                        material text,
                        form text,
                        specific_form text,
                        ware text,
                        munsell text,
                        surf_trat text,
                        exdeco character varying(4),
                        intdeco character varying(4),
                        wheel_made character varying(4),
                        descrip_ex_deco text,
                        descrip_in_deco text,
                        note text,
                        diametro_max numeric(7,3),
                        qty BIGINT,
                        diametro_rim numeric(7,3),
                        diametro_bottom numeric(7,3),
                        diametro_height numeric(7,3),
                        diametro_preserved numeric(7,3),
                        specific_shape text,
                        bag BIGINT,
                        sector text,
                        decoration_type text,
                        decoration_motif text,
                        decoration_position text,
                        datazione text,
                        editing_by varchar(100),
                        editing_since timestamp,
                        version_number int4 DEFAULT 1,
                        last_modified_by varchar(100),
                        last_modified_timestamp timestamp,
                        audit_trail jsonb DEFAULT '[]'::jsonb
                    );

                    -- Copia i dati
                    INSERT INTO pottery_table_reorder
                    SELECT id_rep, id_number, sito, area, us, box, photo, drawing, anno,
                           fabric, percent, material, form, specific_form, ware, munsell,
                           surf_trat, exdeco, intdeco, wheel_made, descrip_ex_deco,
                           descrip_in_deco, note, diametro_max, qty, diametro_rim,
                           diametro_bottom, diametro_height, diametro_preserved,
                           specific_shape, bag, sector, decoration_type, decoration_motif,
                           decoration_position, datazione, editing_by, editing_since,
                           version_number, last_modified_by, last_modified_timestamp, audit_trail
                    FROM pottery_table;

                    -- Drop vecchia tabella
                    DROP TABLE pottery_table;

                    -- Rinomina nuova tabella
                    ALTER TABLE pottery_table_reorder RENAME TO pottery_table;

                    -- Ricrea constraints
                    ALTER TABLE pottery_table ADD PRIMARY KEY (id_rep);

                    -- Ricollega sequence se esiste
                    IF EXISTS (SELECT 1 FROM pg_sequences WHERE schemaname = 'public' AND sequencename = 'pottery_table_id_rep_seq') THEN
                        ALTER SEQUENCE pottery_table_id_rep_seq OWNED BY pottery_table.id_rep;
                        ALTER TABLE pottery_table ALTER COLUMN id_rep SET DEFAULT nextval('pottery_table_id_rep_seq');
                    END IF;

                    -- Ricrea unique constraint
                    ALTER TABLE pottery_table ADD CONSTRAINT ID_rep_unico UNIQUE (sito, id_number);

                    -- Ricrea la view
                    CREATE VIEW active_editing_sessions AS
                    SELECT 'pottery_table'::text AS table_name,
                        pottery_table.id_rep,
                        pottery_table.editing_by,
                        pottery_table.editing_since
                    FROM pottery_table
                    WHERE pottery_table.editing_by IS NOT NULL
                    UNION ALL
                    SELECT 'us_table'::text AS table_name,
                        us_table.id_us AS id_rep,
                        us_table.editing_by,
                        us_table.editing_since
                    FROM us_table
                    WHERE us_table.editing_by IS NOT NULL;

                    -- Sincronizza i permessi
                    PERFORM sync_grants_for_table('pottery_table');

                END $$;
            """)

            with self.db_manager.engine.connect() as conn:
                conn.execute(reorder_sql)
                conn.execute(text("COMMIT"))

            self.log_message("Colonna datazione riordinata correttamente in pottery_table")
            return True

        except Exception as e:
            self.log_message(f"Errore durante il riordinamento della colonna datazione: {e}")
            return False
    
    def update_thesaurus_table(self):
        """Aggiorna la tabella pyarchinit_thesaurus_sigle"""
        self.log_message("Controllo tabella pyarchinit_thesaurus_sigle...")
        
        try:
            # Verifica se la tabella esiste
            from sqlalchemy import text
            query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'pyarchinit_thesaurus_sigle' 
                AND table_schema = 'public'
            """)
            result = self.db_manager._execute_sql(query).fetchone()
            
            if not result:
                self.log_message("Tabella pyarchinit_thesaurus_sigle non trovata, skip")
                return
            
            # Aggiungi colonne mancanti
            updated = False
            
            # Colonne base che potrebbero mancare
            updated |= self.add_column_if_missing('pyarchinit_thesaurus_sigle', 'lingua', 'VARCHAR(10)', "'it'")
            updated |= self.add_column_if_missing('pyarchinit_thesaurus_sigle', 'order_layer', 'INTEGER', '0')
            updated |= self.add_column_if_missing('pyarchinit_thesaurus_sigle', 'id_parent', 'INTEGER', 'NULL')
            updated |= self.add_column_if_missing('pyarchinit_thesaurus_sigle', 'parent_sigla', 'VARCHAR(100)', 'NULL')
            updated |= self.add_column_if_missing('pyarchinit_thesaurus_sigle', 'hierarchy_level', 'INTEGER', '0')
            
            # Colonne richieste dal codice PyArchInit
            updated |= self.add_column_if_missing('pyarchinit_thesaurus_sigle', 'n_tipologia', 'INTEGER', 'NULL')
            updated |= self.add_column_if_missing('pyarchinit_thesaurus_sigle', 'n_sigla', 'INTEGER', 'NULL')
            
            if updated:
                self.log_message("Tabella pyarchinit_thesaurus_sigle aggiornata con successo")
            else:
                self.log_message("Tabella pyarchinit_thesaurus_sigle già aggiornata")
                
        except Exception as e:
            self.log_message(f"Errore durante l'aggiornamento della tabella thesaurus: {e}")
            raise
    
    def update_reperti_table(self):
        """Aggiorna la tabella pyarchinit_reperti"""
        self.log_message("Controllo tabella pyarchinit_reperti...")
        
        try:
            # Verifica se la tabella esiste
            from sqlalchemy import text
            query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'pyarchinit_reperti' 
                AND table_schema = 'public'
            """)
            result = self.db_manager._execute_sql(query).fetchone()
            
            if not result:
                self.log_message("Tabella pyarchinit_reperti non trovata, skip")
                return
            
            # Aggiungi campo quota se mancante
            updated = self.add_column_if_missing('pyarchinit_reperti', 'quota', 'REAL', 'NULL')
            
            if updated:
                self.log_message("Tabella pyarchinit_reperti aggiornata con successo")
                # Ricrea la view con il nuovo campo quota
                self._recreate_reperti_view()
            else:
                self.log_message("Tabella pyarchinit_reperti già aggiornata")
                # Controlla comunque se la view ha il campo quota
                self._check_and_update_reperti_view()
                
        except Exception as e:
            self.log_message(f"Errore durante l'aggiornamento della tabella reperti: {e}")
            raise
    
    def _recreate_reperti_view(self):
        """Ricrea la view pyarchinit_reperti_view con il campo quota"""
        try:
            from sqlalchemy import text
            
            # Drop existing view if any
            drop_query = text("DROP VIEW IF EXISTS pyarchinit_reperti_view CASCADE")
            self.db_manager._execute_sql(drop_query)
            
            # Create view with all fields including quota
            create_query = text("""
                CREATE VIEW pyarchinit_reperti_view AS 
                SELECT
                    a.gid,
                    a.the_geom,
                    a.id_rep,
                    a.siti,
                    a.quota,
                    b.id_invmat,
                    b.sito,
                    b.numero_inventario,
                    b.tipo_reperto,
                    b.criterio_schedatura,
                    b.definizione,
                    b.descrizione,
                    b.area::text,
                    b.us::text,
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
                    b.years::text as years,
                    b.schedatore,
                    b.date_scheda,
                    b.punto_rinv,
                    b.negativo_photo,
                    b.diapositiva
                FROM pyarchinit_reperti a
                JOIN inventario_materiali_table b ON 
                    a.siti = b.sito AND 
                    a.id_rep = b.numero_inventario
            """)
            self.db_manager._execute_sql(create_query)
            
            self.log_message("Ricreata view pyarchinit_reperti_view con campo quota")
            self.updates_made.append("pyarchinit_reperti_view")
            
        except Exception as e:
            self.log_message(f"Errore ricreando pyarchinit_reperti_view: {e}")
    
    def _check_and_update_reperti_view(self):
        """Controlla se la view ha il campo quota e la ricrea se necessario"""
        try:
            from sqlalchemy import text
            
            # Check if view exists and has quota field
            check_query = text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'pyarchinit_reperti_view'
                AND column_name = 'quota'
            """)
            result = self.db_manager._execute_sql(check_query).fetchone()
            
            if not result:
                self.log_message("Campo quota mancante nella view, ricreazione...")
                self._recreate_reperti_view()
            
        except Exception as e:
            self.log_message(f"Errore controllando pyarchinit_reperti_view: {e}")
    
    def update_us_view(self):
        """Crea o aggiorna la view pyarchinit_us_view - gestisce colonne mancanti"""
        self.log_message("Controllo view pyarchinit_us_view...")

        try:
            from sqlalchemy import text

            # Prima verifica quali colonne esistono effettivamente
            check_columns_query = text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'us_table' AND table_schema = 'public'
            """)
            result = self.db_manager._execute_sql(check_columns_query)
            existing_us_columns = {row[0] for row in result}

            check_geo_columns_query = text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'pyunitastratigrafiche' AND table_schema = 'public'
            """)
            result = self.db_manager._execute_sql(check_geo_columns_query)
            existing_geo_columns = {row[0] for row in result}

            # Colonne obbligatorie dalla tabella geometrica
            geo_columns = [
                ('gid', 'pyunitastratigrafiche.gid::INTEGER as gid'),
                ('the_geom', 'pyunitastratigrafiche.the_geom'),
                ('tipo_us_s', 'pyunitastratigrafiche.tipo_us_s'),
                ('scavo_s', 'pyunitastratigrafiche.scavo_s'),
                ('area_s', 'pyunitastratigrafiche.area_s'),
                ('us_s', 'pyunitastratigrafiche.us_s'),
                ('stratigraph_index_us', 'pyunitastratigrafiche.stratigraph_index_us'),
            ]

            # Colonne dalla us_table - tutte opzionali
            us_columns = [
                'id_us', 'sito', 'area', 'us', 'struttura', 'd_stratigrafica',
                'd_interpretativa', 'descrizione', 'interpretazione', 'rapporti',
                'periodo_iniziale', 'fase_iniziale', 'periodo_finale', 'fase_finale',
                'attivita', 'anno_scavo', 'metodo_di_scavo', 'inclusi', 'campioni',
                'organici', 'inorganici', 'data_schedatura', 'schedatore', 'formazione',
                'stato_di_conservazione', 'colore', 'consistenza', 'unita_tipo',
                'settore', 'quad_par', 'ambient', 'saggio', 'elem_datanti',
                'funz_statica', 'lavorazione', 'spess_giunti', 'letti_posa', 'alt_mod',
                'un_ed_riass', 'reimp', 'posa_opera', 'quota_min_usm', 'quota_max_usm',
                'cons_legante', 'col_legante', 'aggreg_legante', 'con_text_mat',
                'col_materiale', 'inclusi_materiali_usm', 'n_catalogo_generale',
                'n_catalogo_interno', 'n_catalogo_internazionale', 'soprintendenza',
                'quota_relativa', 'quota_abs', 'ref_tm', 'ref_ra', 'ref_n', 'posizione',
                'criteri_distinzione', 'modo_formazione', 'componenti_organici',
                'componenti_inorganici', 'lunghezza_max', 'altezza_max', 'altezza_min',
                'profondita_max', 'profondita_min', 'larghezza_media', 'quota_max',
                'quota_min', 'piante', 'documentazione', 'scavato', 'cont_per',
                'order_layer', 'rapporti2', 'sing_doc', 'unita_edilizie',
                'quantificazioni', 'doc_usv'
            ]

            # Costruisci la lista di colonne disponibili
            select_parts = []

            # Aggiungi colonne geometriche esistenti
            for col_name, col_expr in geo_columns:
                if col_name in existing_geo_columns:
                    select_parts.append(col_expr)

            # Aggiungi colonne us_table esistenti
            for col in us_columns:
                if col in existing_us_columns:
                    select_parts.append(f'us_table.{col}')

            if not select_parts:
                self.log_message("Errore: nessuna colonna disponibile per la view")
                return

            # Costruisci e esegui la query CREATE VIEW
            select_clause = ',\n                    '.join(select_parts)
            create_query = f"""
                CREATE OR REPLACE VIEW pyarchinit_us_view AS
                SELECT
                    {select_clause}
                FROM pyunitastratigrafiche
                JOIN us_table ON
                    pyunitastratigrafiche.scavo_s = us_table.sito AND
                    pyunitastratigrafiche.area_s::text = us_table.area AND
                    pyunitastratigrafiche.us_s = us_table.us
            """

            self.db_manager._execute_sql(text(create_query))
            self.log_message(f"View pyarchinit_us_view creata/aggiornata con successo ({len(select_parts)} colonne)")

        except Exception as e:
            self.log_message(f"Errore creando/aggiornando pyarchinit_us_view: {e}")

    def update_usm_view(self):
        """Crea o aggiorna la view pyarchinit_usm_view - gestisce colonne mancanti"""
        self.log_message("Controllo view pyarchinit_usm_view...")

        try:
            from sqlalchemy import text

            # Prima verifica quali colonne esistono effettivamente
            check_columns_query = text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'us_table' AND table_schema = 'public'
            """)
            result = self.db_manager._execute_sql(check_columns_query)
            existing_us_columns = {row[0] for row in result}

            check_geo_columns_query = text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'pyunitastratigrafiche_usm' AND table_schema = 'public'
            """)
            result = self.db_manager._execute_sql(check_geo_columns_query)
            existing_geo_columns = {row[0] for row in result}

            # Colonne obbligatorie dalla tabella geometrica USM
            geo_columns = [
                ('gid', 'pyunitastratigrafiche_usm.gid::INTEGER as gid'),
                ('the_geom', 'pyunitastratigrafiche_usm.the_geom'),
                ('tipo_us_s', 'pyunitastratigrafiche_usm.tipo_us_s'),
                ('scavo_s', 'pyunitastratigrafiche_usm.scavo_s'),
                ('area_s', 'pyunitastratigrafiche_usm.area_s'),
                ('us_s', 'pyunitastratigrafiche_usm.us_s'),
                ('stratigraph_index_us', 'pyunitastratigrafiche_usm.stratigraph_index_us'),
            ]

            # Colonne dalla us_table - tutte opzionali
            us_columns = [
                'id_us', 'sito', 'area', 'us', 'struttura', 'd_stratigrafica',
                'd_interpretativa', 'descrizione', 'interpretazione', 'rapporti',
                'periodo_iniziale', 'fase_iniziale', 'periodo_finale', 'fase_finale',
                'attivita', 'anno_scavo', 'metodo_di_scavo', 'inclusi', 'campioni',
                'data_schedatura', 'schedatore', 'formazione', 'stato_di_conservazione',
                'colore', 'consistenza', 'unita_tipo', 'settore', 'quad_par', 'ambient',
                'saggio', 'elem_datanti', 'funz_statica', 'lavorazione', 'spess_giunti',
                'letti_posa', 'alt_mod', 'un_ed_riass', 'reimp', 'posa_opera',
                'quota_min_usm', 'quota_max_usm', 'cons_legante', 'col_legante',
                'aggreg_legante', 'con_text_mat', 'col_materiale', 'inclusi_materiali_usm',
                'n_catalogo_generale', 'n_catalogo_interno', 'n_catalogo_internazionale',
                'soprintendenza', 'quota_relativa', 'quota_abs', 'documentazione',
                'scavato', 'cont_per', 'order_layer', 'rapporti2', 'doc_usv'
            ]

            # Costruisci la lista di colonne disponibili
            select_parts = []

            # Aggiungi colonne geometriche esistenti
            for col_name, col_expr in geo_columns:
                if col_name in existing_geo_columns:
                    select_parts.append(col_expr)

            # Aggiungi colonne us_table esistenti
            for col in us_columns:
                if col in existing_us_columns:
                    select_parts.append(f'us_table.{col}')

            if not select_parts:
                self.log_message("Errore: nessuna colonna disponibile per la view USM")
                return

            # Costruisci e esegui la query CREATE VIEW
            select_clause = ',\n                    '.join(select_parts)
            create_query = f"""
                CREATE OR REPLACE VIEW pyarchinit_usm_view AS
                SELECT
                    {select_clause}
                FROM pyunitastratigrafiche_usm
                JOIN us_table ON
                    pyunitastratigrafiche_usm.scavo_s::text = us_table.sito AND
                    pyunitastratigrafiche_usm.area_s::text = us_table.area AND
                    pyunitastratigrafiche_usm.us_s = us_table.us
            """

            self.db_manager._execute_sql(text(create_query))
            self.log_message(f"View pyarchinit_usm_view creata/aggiornata con successo ({len(select_parts)} colonne)")

        except Exception as e:
            self.log_message(f"Errore creando/aggiornando pyarchinit_usm_view: {e}")

    def update_activity_triggers(self):
        """Installa/aggiorna i trigger per il tracking delle attività"""
        self.log_message("Controllo trigger per tracking attività...")

        try:
            import os
            import re
            from sqlalchemy import text

            # Path to trigger SQL file
            trigger_file = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir,
                                       'sql', 'create_activity_triggers.sql')

            if not os.path.exists(trigger_file):
                self.log_message(f"File trigger non trovato: {trigger_file}")
                return

            # Read the trigger SQL file
            with open(trigger_file, 'r', encoding='utf-8') as f:
                trigger_sql = f.read()

            # Execute the entire SQL file as a single transaction
            # PL/pgSQL functions use $$ delimiters so we can't split by ;
            with self.db_manager.engine.connect() as conn:
                try:
                    # Execute the entire script at once
                    conn.execute(text(trigger_sql))
                    conn.execute(text("COMMIT"))
                    self.log_message("Trigger per tracking attività installati/aggiornati")
                except Exception as exec_error:
                    error_str = str(exec_error).lower()
                    # Ignore "already exists" errors
                    if 'already exists' in error_str or 'già esiste' in error_str:
                        self.log_message("Trigger per tracking attività già presenti")
                    else:
                        self.log_message(f"Warning eseguendo trigger: {str(exec_error)[:200]}")

        except Exception as e:
            self.log_message(f"Errore installando trigger attività: {e}")

    def update_pottery_table(self):
        """Aggiorna la tabella pottery_table con i nuovi campi decorazione"""
        self.log_message("Controllo tabella pottery_table...")

        try:
            # Verifica se la tabella esiste
            from sqlalchemy import text
            query = text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_name = 'pottery_table'
                AND table_schema = 'public'
            """)
            result = self.db_manager._execute_sql(query).fetchone()

            if not result:
                self.log_message("Tabella pottery_table non trovata, skip")
                return

            # Aggiungi colonne mancanti per la decorazione
            updated = False
            updated |= self.add_column_if_missing('pottery_table', 'decoration_type', 'TEXT')
            updated |= self.add_column_if_missing('pottery_table', 'decoration_motif', 'TEXT')
            updated |= self.add_column_if_missing('pottery_table', 'decoration_position', 'TEXT')
            updated |= self.add_column_if_missing('pottery_table', 'datazione', 'TEXT')

            # Se datazione è stata aggiunta ma si trova dopo i campi audit, riordina
            self.reorder_pottery_datazione_column()

            if updated:
                self.log_message("Tabella pottery_table aggiornata con nuovi campi (decorazione, datazione)")
            else:
                self.log_message("Tabella pottery_table già aggiornata")

        except Exception as e:
            self.log_message(f"Errore durante l'aggiornamento della tabella pottery: {e}")

    def update_pottery_thesaurus(self):
        """Installa/aggiorna le voci thesaurus per la tabella Pottery"""
        self.log_message("Controllo voci thesaurus Pottery...")

        try:
            import os
            from sqlalchemy import text

            # Check if new decoration thesaurus entries exist (11.14, 11.15, 11.16)
            check_query = text("""
                SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle
                WHERE nome_tabella = 'Pottery' AND tipologia_sigla IN ('11.14', '11.15', '11.16')
            """)
            result = self.db_manager._execute_sql(check_query)
            count = result.fetchone()[0]

            if count >= 30:  # Expected ~31 entries for decoration fields
                self.log_message(f"Voci thesaurus Pottery decorazione già presenti ({count} voci)")
                return

            # Path to pottery thesaurus SQL file
            thesaurus_file = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir,
                                          'sql', 'pottery_thesaurus.sql')

            if not os.path.exists(thesaurus_file):
                self.log_message(f"File thesaurus pottery non trovato: {thesaurus_file}")
                return

            # Read and execute the thesaurus SQL
            with open(thesaurus_file, 'r', encoding='utf-8') as f:
                thesaurus_sql = f.read()

            # Execute the SQL script - split by semicolons
            statements = thesaurus_sql.split(';')
            inserted_count = 0

            # Use connection context for proper transaction handling
            with self.db_manager.engine.connect() as conn:
                for stmt in statements:
                    stmt = stmt.strip()
                    if stmt and not stmt.startswith('--') and 'INSERT' in stmt.upper():
                        try:
                            conn.execute(text(stmt))
                            inserted_count += 1
                        except Exception as stmt_error:
                            # Skip errors for duplicate entries
                            if 'duplicate' not in str(stmt_error).lower() and 'conflict' not in str(stmt_error).lower():
                                self.log_message(f"Warning inserendo voce thesaurus: {str(stmt_error)[:100]}")

                # Commit all inserts
                conn.execute(text("COMMIT"))

            if inserted_count > 0:
                self.log_message(f"Voci thesaurus Pottery installate ({inserted_count} voci)")

        except Exception as e:
            self.log_message(f"Errore installando voci thesaurus Pottery: {e}")

    def install_grant_sync_functions(self):
        """
        Installa le funzioni e l'event trigger per la sincronizzazione automatica dei GRANT.
        Quando una tabella viene ricreata (DROP + CREATE), i permessi GRANT vengono
        automaticamente ripristinati dalla tabella pyarchinit_permissions.
        """
        try:
            from sqlalchemy import text

            # Verifica se le tabelle necessarie esistono
            check_tables = text("""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_name IN ('pyarchinit_permissions', 'pyarchinit_users')
                AND table_schema = 'public'
            """)
            result = self.db_manager._execute_sql(check_tables)
            table_count = result.fetchone()[0]

            if table_count < 2:
                # Le tabelle dei permessi non esistono ancora
                return

            # Verifica se l'event trigger esiste già
            check_trigger = text("""
                SELECT 1 FROM pg_event_trigger WHERE evtname = 'trg_sync_grants_on_create'
            """)
            result = self.db_manager._execute_sql(check_trigger)
            trigger_exists = result.fetchone() is not None

            if trigger_exists:
                # Le funzioni sono già installate
                return

            self.log_message("Installazione funzioni sincronizzazione GRANT...")

            # Funzione 1: sync_grants_for_table - sincronizza i GRANT per una singola tabella
            func1_sql = text("""
                CREATE OR REPLACE FUNCTION sync_grants_for_table(p_table_name TEXT)
                RETURNS void AS $func$
                DECLARE
                    perm_record RECORD;
                    grant_perms TEXT;
                    v_username TEXT;
                BEGIN
                    FOR perm_record IN
                        SELECT u.username, p.can_view, p.can_insert, p.can_update, p.can_delete
                        FROM pyarchinit_permissions p
                        JOIN pyarchinit_users u ON u.id = p.user_id
                        WHERE p.table_name = p_table_name
                    LOOP
                        v_username := perm_record.username;

                        IF EXISTS (SELECT 1 FROM pg_user WHERE usename = v_username) THEN
                            grant_perms := '';

                            IF perm_record.can_view THEN
                                grant_perms := 'SELECT';
                            END IF;

                            IF perm_record.can_insert THEN
                                IF grant_perms <> '' THEN grant_perms := grant_perms || ', '; END IF;
                                grant_perms := grant_perms || 'INSERT';
                            END IF;

                            IF perm_record.can_update THEN
                                IF grant_perms <> '' THEN grant_perms := grant_perms || ', '; END IF;
                                grant_perms := grant_perms || 'UPDATE';
                            END IF;

                            IF perm_record.can_delete THEN
                                IF grant_perms <> '' THEN grant_perms := grant_perms || ', '; END IF;
                                grant_perms := grant_perms || 'DELETE';
                            END IF;

                            IF grant_perms <> '' THEN
                                EXECUTE format('GRANT %s ON %I TO %I', grant_perms, p_table_name, v_username);
                            END IF;
                        END IF;
                    END LOOP;
                END;
                $func$ LANGUAGE plpgsql
            """)
            self.db_manager._execute_sql(func1_sql)

            # Funzione 2: sync_all_grants - sincronizza tutti i GRANT
            func2_sql = text("""
                CREATE OR REPLACE FUNCTION sync_all_grants()
                RETURNS void AS $func$
                DECLARE
                    table_rec RECORD;
                BEGIN
                    FOR table_rec IN
                        SELECT DISTINCT table_name FROM pyarchinit_permissions
                    LOOP
                        IF EXISTS (SELECT 1 FROM information_schema.tables
                                   WHERE table_name = table_rec.table_name AND table_schema = 'public') THEN
                            PERFORM sync_grants_for_table(table_rec.table_name);
                        END IF;
                    END LOOP;
                END;
                $func$ LANGUAGE plpgsql
            """)
            self.db_manager._execute_sql(func2_sql)

            # Funzione 3: on_table_created - event trigger function
            func3_sql = text("""
                CREATE OR REPLACE FUNCTION on_table_created()
                RETURNS event_trigger AS $func$
                DECLARE
                    obj record;
                    v_table_name TEXT;
                BEGIN
                    FOR obj IN SELECT * FROM pg_event_trigger_ddl_commands() WHERE command_tag = 'CREATE TABLE'
                    LOOP
                        v_table_name := split_part(obj.object_identity, '.', 2);
                        IF v_table_name IS NULL OR v_table_name = '' THEN
                            v_table_name := obj.object_identity;
                        END IF;

                        IF EXISTS (SELECT 1 FROM pyarchinit_permissions WHERE table_name = v_table_name) THEN
                            PERFORM sync_grants_for_table(v_table_name);
                        END IF;
                    END LOOP;
                END;
                $func$ LANGUAGE plpgsql
            """)
            self.db_manager._execute_sql(func3_sql)

            # Crea l'event trigger
            create_trigger_sql = text("""
                CREATE EVENT TRIGGER trg_sync_grants_on_create
                ON ddl_command_end
                WHEN TAG IN ('CREATE TABLE')
                EXECUTE FUNCTION on_table_created()
            """)
            self.db_manager._execute_sql(create_trigger_sql)

            # Aggiungi commenti
            self.db_manager._execute_sql(text(
                "COMMENT ON FUNCTION sync_grants_for_table(TEXT) IS "
                "'Sincronizza i GRANT PostgreSQL da pyarchinit_permissions per una tabella specifica'"
            ))
            self.db_manager._execute_sql(text(
                "COMMENT ON FUNCTION sync_all_grants() IS "
                "'Sincronizza tutti i GRANT PostgreSQL da pyarchinit_permissions'"
            ))
            self.db_manager._execute_sql(text(
                "COMMENT ON EVENT TRIGGER trg_sync_grants_on_create IS "
                "'Sincronizza automaticamente i GRANT quando una tabella viene creata'"
            ))

            self.log_message("Funzioni sincronizzazione GRANT installate")

        except Exception as e:
            self.log_message(f"Errore installando funzioni sincronizzazione GRANT: {e}")

    def update_inventario_materiali_table(self):
        """Aggiorna la tabella inventario_materiali_table con nuovi campi photo_id e drawing_id"""
        self.log_message("Controllo tabella inventario_materiali_table...")

        try:
            # Verifica se la tabella esiste
            from sqlalchemy import text
            query = text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_name = 'inventario_materiali_table'
                AND table_schema = 'public'
            """)
            result = self.db_manager._execute_sql(query).fetchone()

            if not result:
                self.log_message("Tabella inventario_materiali_table non trovata, skip")
                return

            # Aggiungi nuove colonne se mancanti
            updated = False

            # photo_id - per i nomi delle foto (immagini che NON iniziano con D_)
            updated |= self.add_column_if_missing('inventario_materiali_table', 'photo_id', 'TEXT', 'NULL')

            # drawing_id - per i nomi dei disegni (immagini che iniziano con D_)
            updated |= self.add_column_if_missing('inventario_materiali_table', 'drawing_id', 'TEXT', 'NULL')

            if updated:
                self.log_message("Tabella inventario_materiali_table aggiornata con campi photo_id e drawing_id")
                self.updates_made.append("inventario_materiali_table: photo_id, drawing_id")
            else:
                self.log_message("Tabella inventario_materiali_table già aggiornata")

        except Exception as e:
            self.log_message(f"Errore durante l'aggiornamento della tabella inventario_materiali: {e}")

    def update_struttura_table(self):
        """Aggiorna la tabella struttura_table con i nuovi campi Architettura Rupestre (AR)"""
        self.log_message("Controllo tabella struttura_table...")

        try:
            # Verifica se la tabella esiste
            from sqlalchemy import text
            query = text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_name = 'struttura_table'
                AND table_schema = 'public'
            """)
            result = self.db_manager._execute_sql(query).fetchone()

            if not result:
                self.log_message("Tabella struttura_table non trovata, skip")
                return

            # Aggiungi nuove colonne Architettura Rupestre (AR) se mancanti
            updated = False

            # Campi generali
            updated |= self.add_column_if_missing('struttura_table', 'data_compilazione', 'TEXT')
            updated |= self.add_column_if_missing('struttura_table', 'nome_compilatore', 'TEXT')

            # Stato conservazione (JSON: [[stato, grado, fattori_agenti], ...])
            updated |= self.add_column_if_missing('struttura_table', 'stato_conservazione', 'TEXT')

            # Dati generali architettura
            updated |= self.add_column_if_missing('struttura_table', 'quota', 'REAL')
            updated |= self.add_column_if_missing('struttura_table', 'relazione_topografica', 'TEXT')
            updated |= self.add_column_if_missing('struttura_table', 'prospetto_ingresso', 'TEXT')  # JSON
            updated |= self.add_column_if_missing('struttura_table', 'orientamento_ingresso', 'TEXT')
            updated |= self.add_column_if_missing('struttura_table', 'articolazione', 'TEXT')
            updated |= self.add_column_if_missing('struttura_table', 'n_ambienti', 'INTEGER')
            updated |= self.add_column_if_missing('struttura_table', 'orientamento_ambienti', 'TEXT')  # JSON
            updated |= self.add_column_if_missing('struttura_table', 'sviluppo_planimetrico', 'TEXT')
            updated |= self.add_column_if_missing('struttura_table', 'elementi_costitutivi', 'TEXT')  # JSON
            updated |= self.add_column_if_missing('struttura_table', 'motivo_decorativo', 'TEXT')

            # Dati archeologici
            updated |= self.add_column_if_missing('struttura_table', 'potenzialita_archeologica', 'TEXT')
            updated |= self.add_column_if_missing('struttura_table', 'manufatti', 'TEXT')  # JSON
            updated |= self.add_column_if_missing('struttura_table', 'elementi_datanti', 'TEXT')
            updated |= self.add_column_if_missing('struttura_table', 'fasi_funzionali', 'TEXT')  # JSON

            if updated:
                self.log_message("Tabella struttura_table aggiornata con nuovi campi Architettura Rupestre")
                self.updates_made.append("struttura_table: campi AR aggiunti")
            else:
                self.log_message("Tabella struttura_table già aggiornata")

        except Exception as e:
            self.log_message(f"Errore durante l'aggiornamento della tabella struttura: {e}")

    def update_ut_table(self):
        """Aggiorna la tabella ut_table con i nuovi campi analisi (v4.9.67+)"""
        self.log_message("Controllo tabella ut_table per campi analisi...")

        try:
            from sqlalchemy import text

            # Verifica se la tabella esiste
            query = text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_name = 'ut_table'
                AND table_schema = 'public'
            """)
            result = self.db_manager._execute_sql(query).fetchone()

            if not result:
                self.log_message("Tabella ut_table non trovata, skip")
                return

            # Aggiungi nuove colonne analisi se mancanti
            updated = False

            # Analysis fields (v4.9.67+)
            updated |= self.add_column_if_missing('ut_table', 'potential_score', 'NUMERIC(5,2)')
            updated |= self.add_column_if_missing('ut_table', 'risk_score', 'NUMERIC(5,2)')
            updated |= self.add_column_if_missing('ut_table', 'potential_factors', 'TEXT')
            updated |= self.add_column_if_missing('ut_table', 'risk_factors', 'TEXT')
            updated |= self.add_column_if_missing('ut_table', 'analysis_date', 'VARCHAR(100)')
            updated |= self.add_column_if_missing('ut_table', 'analysis_method', 'VARCHAR(100)')

            if updated:
                self.log_message("Tabella ut_table aggiornata con nuovi campi analisi")
                self.updates_made.append("ut_table: campi analisi aggiunti")
            else:
                self.log_message("Tabella ut_table già aggiornata con campi analisi")

        except Exception as e:
            self.log_message(f"Errore durante l'aggiornamento della tabella ut_table: {e}")

    def update_strutture_view(self):
        """Aggiorna/ricrea la view pyarchinit_strutture_view con i nuovi campi AR"""
        self.log_message("Controllo view pyarchinit_strutture_view...")

        try:
            from sqlalchemy import text

            # Verifica se la view esiste e se ha i nuovi campi AR
            check_query = text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'pyarchinit_strutture_view'
                AND column_name = 'data_compilazione'
            """)
            result = self.db_manager._execute_sql(check_query).fetchone()

            if result:
                self.log_message("View pyarchinit_strutture_view già aggiornata con campi AR")
                return

            # Verifica se le tabelle necessarie esistono
            check_tables = text("""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_name IN ('pyarchinit_strutture_ipotesi', 'struttura_table')
                AND table_schema = 'public'
            """)
            table_count = self.db_manager._execute_sql(check_tables).scalar()

            if table_count < 2:
                self.log_message("Tabelle necessarie per la view non trovate, skip")
                return

            # Ricrea la view con i nuovi campi AR
            create_view_sql = text("""
                CREATE OR REPLACE VIEW public.pyarchinit_strutture_view AS
                SELECT a.gid,
                    a.sito,
                    a.id_strutt,
                    a.per_iniz,
                    a.per_fin,
                    a.dataz_ext,
                    a.fase_iniz,
                    a.fase_fin,
                    a.descrizione,
                    a.the_geom,
                    a.sigla_strut,
                    a.nr_strut,
                    b.id_struttura,
                    b.sito AS sito_1,
                    b.sigla_struttura,
                    b.numero_struttura,
                    b.categoria_struttura,
                    b.tipologia_struttura,
                    b.definizione_struttura,
                    b.descrizione AS descrizione_1,
                    b.interpretazione,
                    b.periodo_iniziale,
                    b.fase_iniziale,
                    b.periodo_finale,
                    b.fase_finale,
                    b.datazione_estesa,
                    b.materiali_impiegati,
                    b.elementi_strutturali,
                    b.rapporti_struttura,
                    b.misure_struttura,
                    b.data_compilazione,
                    b.nome_compilatore,
                    b.stato_conservazione,
                    b.quota,
                    b.relazione_topografica,
                    b.prospetto_ingresso,
                    b.orientamento_ingresso,
                    b.articolazione,
                    b.n_ambienti,
                    b.orientamento_ambienti,
                    b.sviluppo_planimetrico,
                    b.elementi_costitutivi,
                    b.motivo_decorativo,
                    b.potenzialita_archeologica,
                    b.manufatti,
                    b.elementi_datanti,
                    b.fasi_funzionali
                FROM pyarchinit_strutture_ipotesi a
                JOIN struttura_table b ON a.sito::text = b.sito
                    AND a.sigla_strut::text = b.sigla_struttura
                    AND a.nr_strut = b.numero_struttura
            """)

            with self.db_manager.engine.connect() as conn:
                conn.execute(create_view_sql)
                conn.execute(text("COMMIT"))

            self.log_message("View pyarchinit_strutture_view aggiornata con campi AR")
            self.updates_made.append("pyarchinit_strutture_view: aggiornata con campi AR")

        except Exception as e:
            self.log_message(f"Errore durante l'aggiornamento della view strutture: {e}")

    def table_exists(self, table_name):
        """Verifica se una tabella esiste nel database"""
        try:
            from sqlalchemy import text
            query = text(f"""
                SELECT 1 FROM information_schema.tables
                WHERE table_name = '{table_name}' AND table_schema = 'public'
            """)
            result = self.db_manager._execute_sql(query)
            return result.fetchone() is not None
        except Exception as e:
            self.log_message(f"Errore verificando esistenza tabella {table_name}: {e}")
            return False

    def update_fauna_table(self):
        """Crea fauna_table se non esiste (v4.9.21+)"""
        if self.table_exists('fauna_table'):
            return

        self.log_message("Creazione tabella fauna_table...")

        try:
            from sqlalchemy import text
            create_sql = text("""
                CREATE TABLE IF NOT EXISTS fauna_table (
                    id_fauna BIGSERIAL PRIMARY KEY,
                    id_us BIGINT,
                    sito TEXT,
                    area TEXT,
                    saggio TEXT,
                    us TEXT,
                    datazione_us TEXT,
                    responsabile_scheda TEXT,
                    data_compilazione DATE,
                    documentazione_fotografica TEXT,
                    metodologia_recupero TEXT,
                    contesto TEXT,
                    descrizione_contesto TEXT,
                    resti_connessione_anatomica TEXT,
                    tipologia_accumulo TEXT,
                    deposizione TEXT,
                    numero_stimato_resti TEXT,
                    numero_minimo_individui INTEGER,
                    specie TEXT,
                    parti_scheletriche TEXT,
                    specie_psi TEXT,
                    misure_ossa TEXT,
                    stato_frammentazione TEXT,
                    tracce_combustione TEXT,
                    combustione_altri_materiali_us BOOLEAN,
                    tipo_combustione TEXT,
                    segni_tafonomici_evidenti TEXT,
                    caratterizzazione_segni_tafonomici TEXT,
                    stato_conservazione TEXT,
                    alterazioni_morfologiche TEXT,
                    note_terreno_giacitura TEXT,
                    campionature_effettuate TEXT,
                    affidabilita_stratigrafica TEXT,
                    classi_reperti_associazione TEXT,
                    osservazioni TEXT,
                    interpretazione TEXT,
                    UNIQUE (sito, area, us, id_fauna)
                )
            """)

            with self.db_manager.engine.connect() as conn:
                conn.execute(create_sql)
                conn.execute(text("COMMIT"))

            self.log_message("Tabella fauna_table creata con successo")
            self.updates_made.append("CREATE TABLE fauna_table")

        except Exception as e:
            self.log_message(f"Errore creando fauna_table: {e}")

    def update_fauna_thesaurus(self):
        """Installa/aggiorna le voci thesaurus per la tabella fauna_table (v4.9.21+)"""
        try:
            from sqlalchemy import text

            # Check if fauna thesaurus entries exist
            check_query = text("""
                SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle
                WHERE nome_tabella = 'fauna_table'
            """)
            result = self.db_manager._execute_sql(check_query)
            fauna_count = result.fetchone()[0]

            if fauna_count >= 50:  # Expected ~65 entries for fauna fields
                return

            self.log_message("Aggiunta voci thesaurus per fauna_table...")

            # Fauna thesaurus entries
            fauna_entries = [
                # 13.1 - Contesto
                ('fauna_table', 'DOMESTICO', 'Contesto domestico', 'Contesto residenziale/abitativo', '13.1', 'IT'),
                ('fauna_table', 'RITUALE', 'Contesto rituale', 'Contesto cerimoniale/rituale', '13.1', 'IT'),
                ('fauna_table', 'FUNERARIO', 'Contesto funerario', 'Contesto sepolcrale/funerario', '13.1', 'IT'),
                ('fauna_table', 'PRODUTTIVO', 'Contesto produttivo', 'Contesto artigianale/industriale', '13.1', 'IT'),
                ('fauna_table', 'RIFIUTI', 'Deposito rifiuti', 'Scarico/deposito di rifiuti', '13.1', 'IT'),
                # 13.2 - Metodologia Recupero
                ('fauna_table', 'MANUALE', 'Raccolta manuale', 'Recupero manuale durante lo scavo', '13.2', 'IT'),
                ('fauna_table', 'SETACCIO', 'Setacciatura', 'Recupero mediante setacciatura', '13.2', 'IT'),
                ('fauna_table', 'FLOTTAZIONE', 'Flottazione', 'Recupero mediante flottazione', '13.2', 'IT'),
                # 13.3 - Tipologia Accumulo
                ('fauna_table', 'NATURALE', 'Accumulo naturale', 'Accumulo per cause naturali', '13.3', 'IT'),
                ('fauna_table', 'ANTROPICO', 'Accumulo antropico', 'Accumulo per attività umana', '13.3', 'IT'),
                ('fauna_table', 'MISTO', 'Accumulo misto', 'Accumulo di origine mista', '13.3', 'IT'),
                # 13.4 - Deposizione
                ('fauna_table', 'PRIMARIA', 'Deposizione primaria', 'Deposizione in situ', '13.4', 'IT'),
                ('fauna_table', 'SECONDARIA', 'Deposizione secondaria', 'Deposizione dopo spostamento', '13.4', 'IT'),
                ('fauna_table', 'RIMANEGGIATA', 'Deposizione rimaneggiata', 'Deposizione disturbata', '13.4', 'IT'),
                # 13.5 - Stato Frammentazione
                ('fauna_table', 'INTEGRO', 'Integro', 'Osso completo', '13.5', 'IT'),
                ('fauna_table', 'FRAMMENTATO', 'Frammentato', 'Osso frammentato', '13.5', 'IT'),
                ('fauna_table', 'PARZIALE', 'Parziale', 'Osso parzialmente conservato', '13.5', 'IT'),
                # 13.6 - Stato Conservazione
                ('fauna_table', 'BUONO', 'Buono', 'Buono stato di conservazione', '13.6', 'IT'),
                ('fauna_table', 'MEDIOCRE', 'Mediocre', 'Stato di conservazione mediocre', '13.6', 'IT'),
                ('fauna_table', 'CATTIVO', 'Cattivo', 'Cattivo stato di conservazione', '13.6', 'IT'),
                # 13.7 - Affidabilità Stratigrafica
                ('fauna_table', 'ALTA', 'Alta affidabilità', 'Alta affidabilità stratigrafica', '13.7', 'IT'),
                ('fauna_table', 'MEDIA', 'Media affidabilità', 'Media affidabilità stratigrafica', '13.7', 'IT'),
                ('fauna_table', 'BASSA', 'Bassa affidabilità', 'Bassa affidabilità stratigrafica', '13.7', 'IT'),
                # 13.8 - Tracce Combustione
                ('fauna_table', 'ASSENTI', 'Assenti', 'Nessuna traccia di combustione', '13.8', 'IT'),
                ('fauna_table', 'PRESENTI', 'Presenti', 'Tracce di combustione presenti', '13.8', 'IT'),
                ('fauna_table', 'DIFFUSE', 'Diffuse', 'Tracce di combustione diffuse', '13.8', 'IT'),
                # 13.9 - Tipo Combustione
                ('fauna_table', 'CARBONIZZAZIONE', 'Carbonizzazione', 'Combustione con carbonizzazione', '13.9', 'IT'),
                ('fauna_table', 'CALCINAZIONE', 'Calcinazione', 'Combustione con calcinazione', '13.9', 'IT'),
                ('fauna_table', 'PARZIALE', 'Parziale', 'Combustione parziale', '13.9', 'IT'),
                # 13.10 - Connessione Anatomica
                ('fauna_table', 'SI', 'In connessione', 'Ossa in connessione anatomica', '13.10', 'IT'),
                ('fauna_table', 'NO', 'Non in connessione', 'Ossa disarticolate', '13.10', 'IT'),
                ('fauna_table', 'PARZIALE', 'Parziale', 'Connessione anatomica parziale', '13.10', 'IT'),
                # 13.11 - Specie
                ('fauna_table', 'BOS_TAURUS', 'Bos taurus', 'Bovino domestico', '13.11', 'IT'),
                ('fauna_table', 'OVIS_ARIES', 'Ovis aries', 'Pecora domestica', '13.11', 'IT'),
                ('fauna_table', 'CAPRA_HIRCUS', 'Capra hircus', 'Capra domestica', '13.11', 'IT'),
                ('fauna_table', 'SUS_DOMESTICUS', 'Sus domesticus', 'Maiale domestico', '13.11', 'IT'),
                ('fauna_table', 'OVIS_CAPRA', 'Ovis/Capra', 'Ovicaprino indeterminato', '13.11', 'IT'),
                ('fauna_table', 'CERVUS_ELAPHUS', 'Cervus elaphus', 'Cervo', '13.11', 'IT'),
                ('fauna_table', 'EQUUS_CABALLUS', 'Equus caballus', 'Cavallo', '13.11', 'IT'),
                ('fauna_table', 'CANIS_FAMILIARIS', 'Canis familiaris', 'Cane domestico', '13.11', 'IT'),
                ('fauna_table', 'INDET', 'Indeterminato', 'Specie indeterminata', '13.11', 'IT'),
                # 13.12 - Parti Scheletriche (PSI)
                ('fauna_table', 'CRANIO', 'Cranio', 'Cranio/elementi craniali', '13.12', 'IT'),
                ('fauna_table', 'MANDIBOLA', 'Mandibola', 'Mandibola/mascella', '13.12', 'IT'),
                ('fauna_table', 'VERTEBRE', 'Vertebre', 'Elementi vertebrali', '13.12', 'IT'),
                ('fauna_table', 'COSTE', 'Coste', 'Costole', '13.12', 'IT'),
                ('fauna_table', 'SCAPOLA', 'Scapola', 'Scapola', '13.12', 'IT'),
                ('fauna_table', 'OMERO', 'Omero', 'Omero', '13.12', 'IT'),
                ('fauna_table', 'RADIO', 'Radio', 'Radio', '13.12', 'IT'),
                ('fauna_table', 'ULNA', 'Ulna', 'Ulna', '13.12', 'IT'),
                ('fauna_table', 'PELVI', 'Pelvi', 'Bacino', '13.12', 'IT'),
                ('fauna_table', 'FEMORE', 'Femore', 'Femore', '13.12', 'IT'),
                ('fauna_table', 'TIBIA', 'Tibia', 'Tibia', '13.12', 'IT'),
                ('fauna_table', 'METAPODIO', 'Metapodio', 'Metacarpo/Metatarso', '13.12', 'IT'),
                ('fauna_table', 'FALANGI', 'Falangi', 'Falangi', '13.12', 'IT'),
                # 13.13 - Elemento Anatomico
                ('fauna_table', 'HUM', 'Humerus', 'Omero', '13.13', 'IT'),
                ('fauna_table', 'RAD', 'Radius', 'Radio', '13.13', 'IT'),
                ('fauna_table', 'FEM', 'Femur', 'Femore', '13.13', 'IT'),
                ('fauna_table', 'TIB', 'Tibia', 'Tibia', '13.13', 'IT'),
                ('fauna_table', 'MTC', 'Metacarpus', 'Metacarpo', '13.13', 'IT'),
                ('fauna_table', 'MTT', 'Metatarsus', 'Metatarso', '13.13', 'IT'),
                ('fauna_table', 'AST', 'Astragalus', 'Astragalo', '13.13', 'IT'),
                ('fauna_table', 'CAL', 'Calcaneus', 'Calcagno', '13.13', 'IT'),
                ('fauna_table', 'PHI', 'Phalanx I', 'Prima falange', '13.13', 'IT'),
                ('fauna_table', 'PHII', 'Phalanx II', 'Seconda falange', '13.13', 'IT'),
                ('fauna_table', 'PHIII', 'Phalanx III', 'Terza falange', '13.13', 'IT'),
            ]

            inserted_count = 0
            with self.db_manager.engine.connect() as conn:
                for entry in fauna_entries:
                    try:
                        insert_sql = text("""
                            INSERT INTO pyarchinit_thesaurus_sigle
                            (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
                            VALUES (:nome_tabella, :sigla, :sigla_estesa, :descrizione, :tipologia_sigla, :lingua)
                            ON CONFLICT DO NOTHING
                        """)
                        conn.execute(insert_sql, {
                            'nome_tabella': entry[0],
                            'sigla': entry[1],
                            'sigla_estesa': entry[2],
                            'descrizione': entry[3],
                            'tipologia_sigla': entry[4],
                            'lingua': entry[5]
                        })
                        inserted_count += 1
                    except Exception as e:
                        pass  # Ignore duplicates

                conn.execute(text("COMMIT"))

            if inserted_count > 0:
                self.log_message(f"Voci thesaurus fauna_table inserite ({inserted_count} voci)")
                self.updates_made.append(f"fauna_table thesaurus ({inserted_count} voci)")

        except Exception as e:
            self.log_message(f"Errore aggiungendo voci thesaurus fauna: {e}")

    def update_ut_thesaurus(self):
        """Installa/aggiorna le voci thesaurus per la tabella ut_table in tutte le 7 lingue supportate (v4.9.68+)"""
        try:
            from sqlalchemy import text

            # Check if UT thesaurus entries exist
            check_query = text("""
                SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle
                WHERE nome_tabella = 'ut_table'
            """)
            result = self.db_manager._execute_sql(check_query)
            ut_count = result.fetchone()[0]

            if ut_count >= 100:  # Expected ~150+ entries for all languages
                return

            self.log_message("Aggiunta voci thesaurus per ut_table in tutte le lingue...")

            # UT thesaurus entries in all 7 languages
            ut_entries = [
                # ========== 12.1 - Survey Type ==========
                # Italian
                ('ut_table', 'intensive', 'Ricognizione intensiva', 'Ricognizione sistematica intensiva del territorio', '12.1', 'IT'),
                ('ut_table', 'extensive', 'Ricognizione estensiva', 'Ricognizione estensiva a campionamento', '12.1', 'IT'),
                ('ut_table', 'targeted', 'Ricognizione mirata', 'Indagine mirata su aree specifiche', '12.1', 'IT'),
                ('ut_table', 'random', 'Campionamento casuale', 'Metodologia a campionamento casuale', '12.1', 'IT'),
                # English
                ('ut_table', 'intensive', 'Intensive Survey', 'Intensive systematic field walking survey', '12.1', 'en_US'),
                ('ut_table', 'extensive', 'Extensive Survey', 'Extensive reconnaissance survey', '12.1', 'en_US'),
                ('ut_table', 'targeted', 'Targeted Survey', 'Targeted investigation of specific areas', '12.1', 'en_US'),
                ('ut_table', 'random', 'Random Sampling', 'Random sampling methodology', '12.1', 'en_US'),
                # German
                ('ut_table', 'intensive', 'Intensive Begehung', 'Intensive systematische Feldbegehung', '12.1', 'de_DE'),
                ('ut_table', 'extensive', 'Extensive Begehung', 'Extensive Erkundungsbegehung', '12.1', 'de_DE'),
                ('ut_table', 'targeted', 'Gezielte Untersuchung', 'Gezielte Untersuchung bestimmter Gebiete', '12.1', 'de_DE'),
                ('ut_table', 'random', 'Zufallsstichprobe', 'Zufällige Stichprobenmethodik', '12.1', 'de_DE'),
                # Spanish
                ('ut_table', 'intensive', 'Prospección intensiva', 'Prospección sistemática intensiva del territorio', '12.1', 'es_ES'),
                ('ut_table', 'extensive', 'Prospección extensiva', 'Prospección extensiva por muestreo', '12.1', 'es_ES'),
                ('ut_table', 'targeted', 'Prospección dirigida', 'Investigación dirigida en áreas específicas', '12.1', 'es_ES'),
                ('ut_table', 'random', 'Muestreo aleatorio', 'Metodología de muestreo aleatorio', '12.1', 'es_ES'),
                # French
                ('ut_table', 'intensive', 'Prospection intensive', 'Prospection pédestre systématique intensive', '12.1', 'fr_FR'),
                ('ut_table', 'extensive', 'Prospection extensive', 'Prospection de reconnaissance extensive', '12.1', 'fr_FR'),
                ('ut_table', 'targeted', 'Prospection ciblée', 'Investigation ciblée de zones spécifiques', '12.1', 'fr_FR'),
                ('ut_table', 'random', 'Échantillonnage aléatoire', "Méthodologie d'échantillonnage aléatoire", '12.1', 'fr_FR'),
                # Arabic
                ('ut_table', 'intensive', 'مسح مكثف', 'مسح ميداني منهجي مكثف', '12.1', 'ar_LB'),
                ('ut_table', 'extensive', 'مسح موسع', 'مسح استطلاعي موسع', '12.1', 'ar_LB'),
                ('ut_table', 'targeted', 'مسح موجه', 'تحقيق موجه لمناطق محددة', '12.1', 'ar_LB'),
                ('ut_table', 'random', 'عينة عشوائية', 'منهجية أخذ العينات العشوائية', '12.1', 'ar_LB'),
                # Catalan
                ('ut_table', 'intensive', 'Prospecció intensiva', 'Prospecció sistemàtica intensiva del territori', '12.1', 'ca_ES'),
                ('ut_table', 'extensive', 'Prospecció extensiva', 'Prospecció extensiva per mostreig', '12.1', 'ca_ES'),
                ('ut_table', 'targeted', 'Prospecció dirigida', 'Investigació dirigida en àrees específiques', '12.1', 'ca_ES'),
                ('ut_table', 'random', 'Mostreig aleatori', 'Metodologia de mostreig aleatori', '12.1', 'ca_ES'),

                # ========== 12.2 - Vegetation Coverage ==========
                # Italian
                ('ut_table', 'none', 'Assente', 'Terreno nudo senza vegetazione', '12.2', 'IT'),
                ('ut_table', 'sparse', 'Rada', 'Copertura vegetale inferiore al 25%', '12.2', 'IT'),
                ('ut_table', 'moderate', 'Moderata', 'Copertura vegetale tra 25% e 50%', '12.2', 'IT'),
                ('ut_table', 'dense', 'Densa', 'Copertura vegetale tra 50% e 75%', '12.2', 'IT'),
                ('ut_table', 'very_dense', 'Molto densa', 'Copertura vegetale superiore al 75%', '12.2', 'IT'),
                # English
                ('ut_table', 'none', 'No vegetation', 'Bare ground with no vegetation', '12.2', 'en_US'),
                ('ut_table', 'sparse', 'Sparse vegetation', 'Less than 25% vegetation coverage', '12.2', 'en_US'),
                ('ut_table', 'moderate', 'Moderate vegetation', '25-50% vegetation coverage', '12.2', 'en_US'),
                ('ut_table', 'dense', 'Dense vegetation', '50-75% vegetation coverage', '12.2', 'en_US'),
                ('ut_table', 'very_dense', 'Very dense vegetation', 'Over 75% vegetation coverage', '12.2', 'en_US'),
                # German
                ('ut_table', 'none', 'Keine Vegetation', 'Kahler Boden ohne Vegetation', '12.2', 'de_DE'),
                ('ut_table', 'sparse', 'Spärliche Vegetation', 'Weniger als 25% Vegetationsbedeckung', '12.2', 'de_DE'),
                ('ut_table', 'moderate', 'Mäßige Vegetation', '25-50% Vegetationsbedeckung', '12.2', 'de_DE'),
                ('ut_table', 'dense', 'Dichte Vegetation', '50-75% Vegetationsbedeckung', '12.2', 'de_DE'),
                ('ut_table', 'very_dense', 'Sehr dichte Vegetation', 'Über 75% Vegetationsbedeckung', '12.2', 'de_DE'),
                # Spanish
                ('ut_table', 'none', 'Sin vegetación', 'Suelo desnudo sin vegetación', '12.2', 'es_ES'),
                ('ut_table', 'sparse', 'Vegetación dispersa', 'Cobertura vegetal inferior al 25%', '12.2', 'es_ES'),
                ('ut_table', 'moderate', 'Vegetación moderada', 'Cobertura vegetal entre 25% y 50%', '12.2', 'es_ES'),
                ('ut_table', 'dense', 'Vegetación densa', 'Cobertura vegetal entre 50% y 75%', '12.2', 'es_ES'),
                ('ut_table', 'very_dense', 'Vegetación muy densa', 'Cobertura vegetal superior al 75%', '12.2', 'es_ES'),
                # French
                ('ut_table', 'none', 'Absente', 'Sol nu sans végétation', '12.2', 'fr_FR'),
                ('ut_table', 'sparse', 'Clairsemée', 'Couverture végétale inférieure à 25%', '12.2', 'fr_FR'),
                ('ut_table', 'moderate', 'Modérée', 'Couverture végétale entre 25% et 50%', '12.2', 'fr_FR'),
                ('ut_table', 'dense', 'Dense', 'Couverture végétale entre 50% et 75%', '12.2', 'fr_FR'),
                ('ut_table', 'very_dense', 'Très dense', 'Couverture végétale supérieure à 75%', '12.2', 'fr_FR'),
                # Arabic
                ('ut_table', 'none', 'لا نباتات', 'أرض جرداء بدون نباتات', '12.2', 'ar_LB'),
                ('ut_table', 'sparse', 'نباتات متناثرة', 'تغطية نباتية أقل من 25%', '12.2', 'ar_LB'),
                ('ut_table', 'moderate', 'نباتات معتدلة', 'تغطية نباتية بين 25% و50%', '12.2', 'ar_LB'),
                ('ut_table', 'dense', 'نباتات كثيفة', 'تغطية نباتية بين 50% و75%', '12.2', 'ar_LB'),
                ('ut_table', 'very_dense', 'نباتات كثيفة جداً', 'تغطية نباتية أكثر من 75%', '12.2', 'ar_LB'),
                # Catalan
                ('ut_table', 'none', 'Absent', 'Terreny nu sense vegetació', '12.2', 'ca_ES'),
                ('ut_table', 'sparse', 'Escassa', 'Cobertura vegetal inferior al 25%', '12.2', 'ca_ES'),
                ('ut_table', 'moderate', 'Moderada', 'Cobertura vegetal entre 25% i 50%', '12.2', 'ca_ES'),
                ('ut_table', 'dense', 'Densa', 'Cobertura vegetal entre 50% i 75%', '12.2', 'ca_ES'),
                ('ut_table', 'very_dense', 'Molt densa', 'Cobertura vegetal superior al 75%', '12.2', 'ca_ES'),

                # ========== 12.3 - GPS Method ==========
                # Italian
                ('ut_table', 'handheld', 'GPS portatile', 'Dispositivo GPS portatile', '12.3', 'IT'),
                ('ut_table', 'dgps', 'GPS differenziale', 'DGPS con correzione da stazione base', '12.3', 'IT'),
                ('ut_table', 'rtk', 'GPS RTK', 'GPS cinematico in tempo reale', '12.3', 'IT'),
                ('ut_table', 'total_station', 'Stazione totale', 'Rilievo con stazione totale', '12.3', 'IT'),
                # English
                ('ut_table', 'handheld', 'Handheld GPS', 'Handheld GPS device', '12.3', 'en_US'),
                ('ut_table', 'dgps', 'Differential GPS', 'DGPS with base station correction', '12.3', 'en_US'),
                ('ut_table', 'rtk', 'RTK GPS', 'Real-time kinematic GPS', '12.3', 'en_US'),
                ('ut_table', 'total_station', 'Total Station', 'Total station survey', '12.3', 'en_US'),
                # German
                ('ut_table', 'handheld', 'Hand-GPS', 'Tragbares GPS-Gerät', '12.3', 'de_DE'),
                ('ut_table', 'dgps', 'Differentielles GPS', 'DGPS mit Basisstationskorrektur', '12.3', 'de_DE'),
                ('ut_table', 'rtk', 'RTK-GPS', 'Echtzeit-kinematisches GPS', '12.3', 'de_DE'),
                ('ut_table', 'total_station', 'Totalstation', 'Vermessung mit Totalstation', '12.3', 'de_DE'),
                # Spanish
                ('ut_table', 'handheld', 'GPS portátil', 'Dispositivo GPS portátil', '12.3', 'es_ES'),
                ('ut_table', 'dgps', 'GPS diferencial', 'DGPS con corrección de estación base', '12.3', 'es_ES'),
                ('ut_table', 'rtk', 'GPS RTK', 'GPS cinemático en tiempo real', '12.3', 'es_ES'),
                ('ut_table', 'total_station', 'Estación total', 'Levantamiento con estación total', '12.3', 'es_ES'),
                # French
                ('ut_table', 'handheld', 'GPS portable', 'Appareil GPS portable', '12.3', 'fr_FR'),
                ('ut_table', 'dgps', 'GPS différentiel', 'DGPS avec correction de station de base', '12.3', 'fr_FR'),
                ('ut_table', 'rtk', 'GPS RTK', 'GPS cinématique en temps réel', '12.3', 'fr_FR'),
                ('ut_table', 'total_station', 'Station totale', 'Levé avec station totale', '12.3', 'fr_FR'),
                # Arabic
                ('ut_table', 'handheld', 'GPS محمول', 'جهاز GPS محمول باليد', '12.3', 'ar_LB'),
                ('ut_table', 'dgps', 'GPS تفاضلي', 'DGPS مع تصحيح محطة القاعدة', '12.3', 'ar_LB'),
                ('ut_table', 'rtk', 'GPS RTK', 'GPS حركي في الوقت الحقيقي', '12.3', 'ar_LB'),
                ('ut_table', 'total_station', 'محطة كاملة', 'مسح بالمحطة الكاملة', '12.3', 'ar_LB'),
                # Catalan
                ('ut_table', 'handheld', 'GPS portàtil', 'Dispositiu GPS portàtil', '12.3', 'ca_ES'),
                ('ut_table', 'dgps', 'GPS diferencial', "DGPS amb correcció d'estació base", '12.3', 'ca_ES'),
                ('ut_table', 'rtk', 'GPS RTK', 'GPS cinemàtic en temps real', '12.3', 'ca_ES'),
                ('ut_table', 'total_station', 'Estació total', 'Aixecament amb estació total', '12.3', 'ca_ES'),

                # ========== 12.4 - Surface Condition ==========
                # Italian
                ('ut_table', 'ploughed', 'Arato', 'Campo arato di recente', '12.4', 'IT'),
                ('ut_table', 'stubble', 'Stoppie', 'Presenza di stoppie', '12.4', 'IT'),
                ('ut_table', 'pasture', 'Pascolo', 'Terreno a pascolo/prato', '12.4', 'IT'),
                ('ut_table', 'woodland', 'Bosco', 'Area boscata', '12.4', 'IT'),
                ('ut_table', 'urban', 'Urbano', 'Area urbana/edificata', '12.4', 'IT'),
                # English
                ('ut_table', 'ploughed', 'Ploughed', 'Recently ploughed field', '12.4', 'en_US'),
                ('ut_table', 'stubble', 'Stubble', 'Crop stubble present', '12.4', 'en_US'),
                ('ut_table', 'pasture', 'Pasture', 'Grassland/pasture', '12.4', 'en_US'),
                ('ut_table', 'woodland', 'Woodland', 'Wooded area', '12.4', 'en_US'),
                ('ut_table', 'urban', 'Urban', 'Urban/built area', '12.4', 'en_US'),
                # German
                ('ut_table', 'ploughed', 'Gepflügt', 'Kürzlich gepflügtes Feld', '12.4', 'de_DE'),
                ('ut_table', 'stubble', 'Stoppelfeld', 'Stoppeln vorhanden', '12.4', 'de_DE'),
                ('ut_table', 'pasture', 'Weideland', 'Grünland/Weide', '12.4', 'de_DE'),
                ('ut_table', 'woodland', 'Waldgebiet', 'Bewaldetes Gebiet', '12.4', 'de_DE'),
                ('ut_table', 'urban', 'Städtisch', 'Städtisches/bebautes Gebiet', '12.4', 'de_DE'),
                # Spanish
                ('ut_table', 'ploughed', 'Arado', 'Campo arado recientemente', '12.4', 'es_ES'),
                ('ut_table', 'stubble', 'Rastrojo', 'Presencia de rastrojo', '12.4', 'es_ES'),
                ('ut_table', 'pasture', 'Pasto', 'Pradera/pastizal', '12.4', 'es_ES'),
                ('ut_table', 'woodland', 'Bosque', 'Zona boscosa', '12.4', 'es_ES'),
                ('ut_table', 'urban', 'Urbano', 'Zona urbana/edificada', '12.4', 'es_ES'),
                # French
                ('ut_table', 'ploughed', 'Labouré', 'Champ labouré récemment', '12.4', 'fr_FR'),
                ('ut_table', 'stubble', 'Chaume', 'Présence de chaume', '12.4', 'fr_FR'),
                ('ut_table', 'pasture', 'Pâturage', 'Prairie/pâturage', '12.4', 'fr_FR'),
                ('ut_table', 'woodland', 'Boisé', 'Zone boisée', '12.4', 'fr_FR'),
                ('ut_table', 'urban', 'Urbain', 'Zone urbaine/bâtie', '12.4', 'fr_FR'),
                # Arabic
                ('ut_table', 'ploughed', 'محروث', 'حقل محروث حديثاً', '12.4', 'ar_LB'),
                ('ut_table', 'stubble', 'قش', 'وجود بقايا المحاصيل', '12.4', 'ar_LB'),
                ('ut_table', 'pasture', 'مرعى', 'أرض عشبية/مرعى', '12.4', 'ar_LB'),
                ('ut_table', 'woodland', 'غابة', 'منطقة حرجية', '12.4', 'ar_LB'),
                ('ut_table', 'urban', 'حضري', 'منطقة حضرية/مبنية', '12.4', 'ar_LB'),
                # Catalan
                ('ut_table', 'ploughed', 'Llautat', 'Camp llautat recentment', '12.4', 'ca_ES'),
                ('ut_table', 'stubble', 'Rostoll', 'Presència de rostoll', '12.4', 'ca_ES'),
                ('ut_table', 'pasture', 'Pastura', 'Prat/pastura', '12.4', 'ca_ES'),
                ('ut_table', 'woodland', 'Bosc', 'Àrea boscosa', '12.4', 'ca_ES'),
                ('ut_table', 'urban', 'Urbà', 'Àrea urbana/edificada', '12.4', 'ca_ES'),

                # ========== 12.5 - Accessibility ==========
                # Italian
                ('ut_table', 'easy', 'Facile accesso', 'Nessuna restrizione di accesso', '12.5', 'IT'),
                ('ut_table', 'moderate_access', 'Accesso moderato', 'Alcune restrizioni o difficoltà', '12.5', 'IT'),
                ('ut_table', 'difficult', 'Accesso difficile', 'Significativi problemi di accesso', '12.5', 'IT'),
                ('ut_table', 'restricted', 'Accesso ristretto', 'Accesso solo su autorizzazione', '12.5', 'IT'),
                # English
                ('ut_table', 'easy', 'Easy access', 'No restrictions on access', '12.5', 'en_US'),
                ('ut_table', 'moderate_access', 'Moderate access', 'Some restrictions or difficulties', '12.5', 'en_US'),
                ('ut_table', 'difficult', 'Difficult access', 'Significant access problems', '12.5', 'en_US'),
                ('ut_table', 'restricted', 'Restricted access', 'Access by permission only', '12.5', 'en_US'),
                # German
                ('ut_table', 'easy', 'Leichter Zugang', 'Keine Zugangsbeschränkungen', '12.5', 'de_DE'),
                ('ut_table', 'moderate_access', 'Mäßiger Zugang', 'Einige Einschränkungen oder Schwierigkeiten', '12.5', 'de_DE'),
                ('ut_table', 'difficult', 'Schwieriger Zugang', 'Erhebliche Zugangsprobleme', '12.5', 'de_DE'),
                ('ut_table', 'restricted', 'Eingeschränkter Zugang', 'Zugang nur mit Genehmigung', '12.5', 'de_DE'),
                # Spanish
                ('ut_table', 'easy', 'Acceso fácil', 'Sin restricciones de acceso', '12.5', 'es_ES'),
                ('ut_table', 'moderate_access', 'Acceso moderado', 'Algunas restricciones o dificultades', '12.5', 'es_ES'),
                ('ut_table', 'difficult', 'Acceso difícil', 'Problemas significativos de acceso', '12.5', 'es_ES'),
                ('ut_table', 'restricted', 'Acceso restringido', 'Acceso solo con permiso', '12.5', 'es_ES'),
                # French
                ('ut_table', 'easy', 'Accès facile', "Aucune restriction d'accès", '12.5', 'fr_FR'),
                ('ut_table', 'moderate_access', 'Accès modéré', 'Quelques restrictions ou difficultés', '12.5', 'fr_FR'),
                ('ut_table', 'difficult', 'Accès difficile', "Problèmes d'accès importants", '12.5', 'fr_FR'),
                ('ut_table', 'restricted', 'Accès restreint', 'Accès sur autorisation uniquement', '12.5', 'fr_FR'),
                # Arabic
                ('ut_table', 'easy', 'وصول سهل', 'لا قيود على الوصول', '12.5', 'ar_LB'),
                ('ut_table', 'moderate_access', 'وصول معتدل', 'بعض القيود أو الصعوبات', '12.5', 'ar_LB'),
                ('ut_table', 'difficult', 'وصول صعب', 'مشاكل وصول كبيرة', '12.5', 'ar_LB'),
                ('ut_table', 'restricted', 'وصول مقيد', 'الوصول بإذن فقط', '12.5', 'ar_LB'),
                # Catalan
                ('ut_table', 'easy', 'Accés fàcil', "Sense restriccions d'accés", '12.5', 'ca_ES'),
                ('ut_table', 'moderate_access', 'Accés moderat', 'Algunes restriccions o dificultats', '12.5', 'ca_ES'),
                ('ut_table', 'difficult', 'Accés difícil', "Problemes significatius d'accés", '12.5', 'ca_ES'),
                ('ut_table', 'restricted', 'Accés restringit', 'Accés només amb permís', '12.5', 'ca_ES'),

                # ========== 12.6 - Weather Conditions ==========
                # Italian
                ('ut_table', 'sunny', 'Soleggiato', 'Tempo sereno e soleggiato', '12.6', 'IT'),
                ('ut_table', 'cloudy', 'Nuvoloso', 'Condizioni nuvolose', '12.6', 'IT'),
                ('ut_table', 'rainy', 'Piovoso', 'Pioggia durante la ricognizione', '12.6', 'IT'),
                ('ut_table', 'windy', 'Ventoso', 'Vento forte', '12.6', 'IT'),
                # English
                ('ut_table', 'sunny', 'Sunny', 'Clear and sunny weather', '12.6', 'en_US'),
                ('ut_table', 'cloudy', 'Cloudy', 'Overcast conditions', '12.6', 'en_US'),
                ('ut_table', 'rainy', 'Rainy', 'Rain during survey', '12.6', 'en_US'),
                ('ut_table', 'windy', 'Windy', 'Strong winds', '12.6', 'en_US'),
                # German
                ('ut_table', 'sunny', 'Sonnig', 'Klares und sonniges Wetter', '12.6', 'de_DE'),
                ('ut_table', 'cloudy', 'Bewölkt', 'Bedeckte Verhältnisse', '12.6', 'de_DE'),
                ('ut_table', 'rainy', 'Regnerisch', 'Regen während der Begehung', '12.6', 'de_DE'),
                ('ut_table', 'windy', 'Windig', 'Starker Wind', '12.6', 'de_DE'),
                # Spanish
                ('ut_table', 'sunny', 'Soleado', 'Tiempo despejado y soleado', '12.6', 'es_ES'),
                ('ut_table', 'cloudy', 'Nublado', 'Condiciones nubladas', '12.6', 'es_ES'),
                ('ut_table', 'rainy', 'Lluvioso', 'Lluvia durante la prospección', '12.6', 'es_ES'),
                ('ut_table', 'windy', 'Ventoso', 'Vientos fuertes', '12.6', 'es_ES'),
                # French
                ('ut_table', 'sunny', 'Ensoleillé', 'Temps clair et ensoleillé', '12.6', 'fr_FR'),
                ('ut_table', 'cloudy', 'Nuageux', 'Conditions nuageuses', '12.6', 'fr_FR'),
                ('ut_table', 'rainy', 'Pluvieux', 'Pluie pendant la prospection', '12.6', 'fr_FR'),
                ('ut_table', 'windy', 'Venteux', 'Vents forts', '12.6', 'fr_FR'),
                # Arabic
                ('ut_table', 'sunny', 'مشمس', 'طقس صافٍ ومشمس', '12.6', 'ar_LB'),
                ('ut_table', 'cloudy', 'غائم', 'ظروف غائمة', '12.6', 'ar_LB'),
                ('ut_table', 'rainy', 'ممطر', 'أمطار أثناء المسح', '12.6', 'ar_LB'),
                ('ut_table', 'windy', 'عاصف', 'رياح قوية', '12.6', 'ar_LB'),
                # Catalan
                ('ut_table', 'sunny', 'Assolellat', 'Temps clar i assolellat', '12.6', 'ca_ES'),
                ('ut_table', 'cloudy', 'Ennuvolat', 'Condicions ennuvolades', '12.6', 'ca_ES'),
                ('ut_table', 'rainy', 'Plujós', 'Pluja durant la prospecció', '12.6', 'ca_ES'),
                ('ut_table', 'windy', 'Ventós', 'Vents forts', '12.6', 'ca_ES'),
            ]

            inserted_count = 0
            with self.db_manager.engine.connect() as conn:
                for entry in ut_entries:
                    try:
                        insert_sql = text("""
                            INSERT INTO pyarchinit_thesaurus_sigle
                            (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
                            VALUES (:nome_tabella, :sigla, :sigla_estesa, :descrizione, :tipologia_sigla, :lingua)
                            ON CONFLICT DO NOTHING
                        """)
                        conn.execute(insert_sql, {
                            'nome_tabella': entry[0],
                            'sigla': entry[1],
                            'sigla_estesa': entry[2],
                            'descrizione': entry[3],
                            'tipologia_sigla': entry[4],
                            'lingua': entry[5]
                        })
                        inserted_count += 1
                    except Exception as e:
                        pass  # Ignore duplicates

                conn.execute(text("COMMIT"))

            if inserted_count > 0:
                self.log_message(f"Voci thesaurus ut_table inserite ({inserted_count} voci)")
                self.updates_made.append(f"ut_table thesaurus ({inserted_count} voci)")

        except Exception as e:
            self.log_message(f"Errore aggiungendo voci thesaurus UT: {e}")

    def fix_thesaurus_nome_tabella(self):
        """Fix thesaurus entries that have display names instead of actual table names.

        This migration fixes a bug where the Thesaurus form was saving entries with
        display names (e.g., 'Fauna') instead of actual table names (e.g., 'fauna_table').
        Forms query using actual table names, so entries with display names were not found.
        """
        try:
            from sqlalchemy import text

            # Mapping from display names to actual table names
            display_to_table = {
                'Fauna': 'fauna_table',
                'US': 'us_table',
                'USM': 'us_table_usm',
                'Sito': 'site_table',
                'Periodizzazione': 'periodizzazione_table',
                'Inventario Materiali': 'inventario_materiali_table',
                'Inventario Lapidei': 'inventario_lapidei_table',
                'Struttura': 'struttura_table',
                'Tomba': 'tomba_table',
                'Campioni': 'campioni_table',
                'UT': 'ut_table',
                'Tafonomia': 'tafonomia_table',
                'Individui': 'individui_table',
                'Pottery': 'pottery_table',
                'Archeozoologia': 'archeozoo_table',
            }

            total_fixed = 0
            with self.db_manager.engine.connect() as conn:
                for display_name, table_name in display_to_table.items():
                    try:
                        update_sql = text("""
                            UPDATE pyarchinit_thesaurus_sigle
                            SET nome_tabella = :table_name
                            WHERE nome_tabella = :display_name
                        """)
                        result = conn.execute(update_sql, {
                            'table_name': table_name,
                            'display_name': display_name
                        })
                        rows_updated = result.rowcount
                        if rows_updated > 0:
                            total_fixed += rows_updated
                            self.log_message(f"Fixed {rows_updated} thesaurus entries: '{display_name}' -> '{table_name}'")
                    except Exception as e:
                        self.log_message(f"Error fixing '{display_name}': {e}")

                conn.execute(text("COMMIT"))

            if total_fixed > 0:
                self.log_message(f"Thesaurus nome_tabella fix: {total_fixed} entries corrected")
                self.updates_made.append(f"thesaurus nome_tabella fix ({total_fixed} voci)")

        except Exception as e:
            self.log_message(f"Error fixing thesaurus nome_tabella: {e}")

    def create_performance_indexes(self):
        """Crea indici di performance per query frequenti"""
        self.log_message("Controllo indici di performance...")

        try:
            from sqlalchemy import text

            # Lista degli indici da creare con formato: (nome_indice, tabella, colonne)
            indexes = [
                # Indici principali per ricerche per sito
                ('idx_us_table_sito', 'us_table', 'sito'),
                ('idx_inventario_sito', 'inventario_materiali_table', 'sito'),
                ('idx_site_table_sito', 'site_table', 'sito'),
                ('idx_thesaurus_tipologia', 'pyarchinit_thesaurus_sigle', 'tipologia_sigla'),
                ('idx_quote_sito', 'pyarchinit_quote', 'sito_q, area_q, us_q'),
                ('idx_reperti_siti', 'pyarchinit_reperti', 'siti'),

                # Indici aggiuntivi per query comuni
                ('idx_us_table_area', 'us_table', 'area'),
                ('idx_us_table_sito_area', 'us_table', 'sito, area'),
                ('idx_inventario_area', 'inventario_materiali_table', 'area'),
                ('idx_tomba_sito', 'tomba_table', 'sito'),
                ('idx_periodizzazione_sito', 'periodizzazione_table', 'sito'),
                ('idx_struttura_sito', 'struttura_table', 'sito'),
                ('idx_documentazione_sito', 'documentazione_table', 'sito'),
                ('idx_campioni_sito', 'campioni_table', 'sito'),
            ]

            indexes_created = 0

            with self.db_manager.engine.connect() as conn:
                for idx_name, table_name, columns in indexes:
                    try:
                        # Verifica se la tabella esiste
                        check_table = text("""
                            SELECT 1 FROM information_schema.tables
                            WHERE table_name = :table_name AND table_schema = 'public'
                        """)
                        result = conn.execute(check_table, {'table_name': table_name})
                        if not result.fetchone():
                            continue  # Tabella non esiste, skip

                        # Verifica se l'indice esiste già
                        check_idx = text("""
                            SELECT 1 FROM pg_indexes
                            WHERE indexname = :idx_name AND schemaname = 'public'
                        """)
                        result = conn.execute(check_idx, {'idx_name': idx_name})
                        if result.fetchone():
                            continue  # Indice già esiste, skip

                        # Crea l'indice
                        create_sql = f"CREATE INDEX {idx_name} ON {table_name}({columns})"
                        conn.execute(text(create_sql))
                        indexes_created += 1

                    except Exception as idx_error:
                        # Ignora errori per singoli indici (es. colonna non esiste)
                        pass

                if indexes_created > 0:
                    conn.execute(text("COMMIT"))
                    self.log_message(f"Creati {indexes_created} indici di performance")

                    # Esegui ANALYZE sulle tabelle principali
                    analyze_tables = ['us_table', 'inventario_materiali_table', 'site_table',
                                     'pyarchinit_thesaurus_sigle', 'tomba_table', 'periodizzazione_table']
                    for table in analyze_tables:
                        try:
                            conn.execute(text(f"ANALYZE {table}"))
                        except:
                            pass
                    conn.execute(text("COMMIT"))

        except Exception as e:
            self.log_message(f"Errore creando indici di performance: {e}")


def check_and_update_postgres_db(db_manager, parent=None):
    """
    Funzione di utilità per controllare e aggiornare un database PostgreSQL
    
    Args:
        db_manager: istanza di Pyarchinit_db_management
        parent: widget parent per i messaggi (opzionale)
    
    Returns:
        bool: True se l'aggiornamento è riuscito, False altrimenti
    """
    updater = PostgresDbUpdater(db_manager, parent)
    return updater.check_and_update_database()