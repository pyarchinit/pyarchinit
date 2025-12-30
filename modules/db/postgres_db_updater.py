'''
PostgreSQL Database Updater for PyArchInit
Handles database schema updates and migrations for PostgreSQL databases

Created on 2024
@author: Enzo Cocca <enzo.ccc@gmail.com>
'''

from datetime import datetime

try:
    from qgis.PyQt.QtWidgets import QMessageBox
    from qgis.core import Qgis
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
        """Log dei messaggi"""
        print(message)
        self.updates_made.append(message)

    def check_and_update_database(self):
        """Controlla e aggiorna il database PostgreSQL"""
        try:
            self.log_message("Controllo database PostgreSQL per aggiornamenti necessari...")

            # Aggiorna la tabella thesaurus
            self.update_thesaurus_table()

            # Aggiorna la tabella reperti
            self.update_reperti_table()

            # Aggiorna la view pyarchinit_us_view
            self.update_us_view()

            # Aggiorna la view pyarchinit_usm_view
            self.update_usm_view()

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

            # Altri aggiornamenti possono essere aggiunti qui in futuro

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
            query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = :table_name 
                AND column_name = :column_name
            """)
            result = self.db_manager._execute_sql(query, {'table_name': table_name, 'column_name': column_name})
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
            query = text("""
                SELECT ordinal_position
                FROM information_schema.columns
                WHERE table_name = :table_name
                AND column_name = :column_name
            """)
            result = self.db_manager._execute_sql(query, {'table_name': table_name, 'column_name': column_name})
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
            from sqlalchemy import text

            # Path to trigger SQL file
            trigger_file = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir,
                                       'sql', 'create_activity_triggers.sql')

            if not os.path.exists(trigger_file):
                self.log_message(f"File trigger non trovato: {trigger_file}")
                return

            # Read and execute the trigger SQL
            with open(trigger_file, 'r', encoding='utf-8') as f:
                trigger_sql = f.read()

            # Execute the SQL script
            # Split by statements for proper execution
            statements = trigger_sql.split(';')
            for stmt in statements:
                stmt = stmt.strip()
                if stmt and not stmt.startswith('--'):
                    try:
                        self.db_manager._execute_sql(text(stmt))
                    except Exception as stmt_error:
                        # Skip errors for already existing objects
                        if 'already exists' not in str(stmt_error).lower():
                            self.log_message(f"Warning eseguendo statement trigger: {str(stmt_error)[:100]}")

            self.log_message("Trigger per tracking attività installati/aggiornati")

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