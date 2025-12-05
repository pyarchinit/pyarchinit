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

            # Installa/aggiorna i trigger per il tracking delle attività
            self.update_activity_triggers()

            # Installa/aggiorna le voci thesaurus per Pottery
            self.update_pottery_thesaurus()

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
            result = self.db_manager.engine.execute(query, {'table_name': table_name, 'column_name': column_name})
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
                
                self.db_manager.engine.execute(sql)
                self.log_message(f"Aggiunta colonna {column_name} a tabella {table_name}")
                return True
            except Exception as e:
                self.log_message(f"Errore aggiungendo colonna {column_name} a {table_name}: {e}")
                return False
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
            result = self.db_manager.engine.execute(query).fetchone()
            
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
            result = self.db_manager.engine.execute(query).fetchone()
            
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
            self.db_manager.engine.execute(drop_query)
            
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
            self.db_manager.engine.execute(create_query)
            
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
            result = self.db_manager.engine.execute(check_query).fetchone()
            
            if not result:
                self.log_message("Campo quota mancante nella view, ricreazione...")
                self._recreate_reperti_view()
            
        except Exception as e:
            self.log_message(f"Errore controllando pyarchinit_reperti_view: {e}")
    
    def update_us_view(self):
        """Crea o aggiorna la view pyarchinit_us_view"""
        self.log_message("Controllo view pyarchinit_us_view...")
        
        try:
            from sqlalchemy import text
            
            # Drop existing view if any
            drop_query = text("DROP VIEW IF EXISTS pyarchinit_us_view CASCADE")
            self.db_manager.engine.execute(drop_query)
            
            # Create view with all fields including order_layer and cont_per
            create_query = text("""
                CREATE VIEW pyarchinit_us_view AS
                SELECT 
                    pyunitastratigrafiche.gid::INTEGER as gid,
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
                    us_table.attivita,
                    us_table.anno_scavo,
                    us_table.metodo_di_scavo,
                    us_table.inclusi,
                    us_table.campioni,
                    us_table.organici,
                    us_table.inorganici,
                    us_table.data_schedatura,
                    us_table.schedatore,
                    us_table.formazione,
                    us_table.stato_di_conservazione,
                    us_table.colore,
                    us_table.consistenza,
                    us_table.unita_tipo,
                    us_table.settore,
                    us_table.quad_par,
                    us_table.ambient,
                    us_table.saggio,
                    us_table.elem_datanti,
                    us_table.funz_statica,
                    us_table.lavorazione,
                    us_table.spess_giunti,
                    us_table.letti_posa,
                    us_table.alt_mod,
                    us_table.un_ed_riass,
                    us_table.reimp,
                    us_table.posa_opera,
                    us_table.quota_min_usm,
                    us_table.quota_max_usm,
                    us_table.cons_legante,
                    us_table.col_legante,
                    us_table.aggreg_legante,
                    us_table.con_text_mat,
                    us_table.col_materiale,
                    us_table.inclusi_materiali_usm,
                    us_table.n_catalogo_generale,
                    us_table.n_catalogo_interno,
                    us_table.n_catalogo_internazionale,
                    us_table.soprintendenza,
                    us_table.quota_relativa,
                    us_table.quota_abs,
                    us_table.ref_tm,
                    us_table.ref_ra,
                    us_table.ref_n,
                    us_table.posizione,
                    us_table.criteri_distinzione,
                    us_table.modo_formazione,
                    us_table.componenti_organici,
                    us_table.componenti_inorganici,
                    us_table.lunghezza_max,
                    us_table.altezza_max,
                    us_table.altezza_min,
                    us_table.profondita_max,
                    us_table.profondita_min,
                    us_table.larghezza_media,
                    us_table.quota_max,
                    us_table.quota_min,
                    us_table.piante,
                    us_table.documentazione,
                    us_table.scavato,
                    us_table.cont_per,
                    us_table.order_layer,
                    us_table.rapporti2,
                    us_table.sing_doc,
                    us_table.unita_edilizie,
                    us_table.quantificazioni,
                    us_table.doc_usv
                FROM pyunitastratigrafiche
                JOIN us_table ON 
                    pyunitastratigrafiche.scavo_s = us_table.sito AND 
                    pyunitastratigrafiche.area_s = us_table.area AND 
                    pyunitastratigrafiche.us_s = us_table.us
            """)
            
            self.db_manager.engine.execute(create_query)
            self.log_message("View pyarchinit_us_view creata/aggiornata con successo")

        except Exception as e:
            self.log_message(f"Errore creando/aggiornando pyarchinit_us_view: {e}")

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
                        self.db_manager.engine.execute(text(stmt))
                    except Exception as stmt_error:
                        # Skip errors for already existing objects
                        if 'already exists' not in str(stmt_error).lower():
                            self.log_message(f"Warning eseguendo statement trigger: {str(stmt_error)[:100]}")

            self.log_message("Trigger per tracking attività installati/aggiornati")

        except Exception as e:
            self.log_message(f"Errore installando trigger attività: {e}")

    def update_pottery_thesaurus(self):
        """Installa/aggiorna le voci thesaurus per la tabella Pottery"""
        self.log_message("Controllo voci thesaurus Pottery...")

        try:
            import os
            from sqlalchemy import text

            # Check if pottery thesaurus entries already exist
            check_query = text("""
                SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle
                WHERE nome_tabella = 'pottery_table' AND tipologia_sigla LIKE '11.%'
            """)
            result = self.db_manager.engine.execute(check_query)
            count = result.fetchone()[0]

            if count > 0:
                self.log_message(f"Voci thesaurus Pottery già presenti ({count} voci)")
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
            for stmt in statements:
                stmt = stmt.strip()
                if stmt and not stmt.startswith('--') and 'INSERT' in stmt.upper():
                    try:
                        self.db_manager.engine.execute(text(stmt))
                        inserted_count += 1
                    except Exception as stmt_error:
                        # Skip errors for duplicate entries
                        if 'duplicate' not in str(stmt_error).lower() and 'conflict' not in str(stmt_error).lower():
                            self.log_message(f"Warning inserendo voce thesaurus: {str(stmt_error)[:100]}")

            if inserted_count > 0:
                self.log_message(f"Voci thesaurus Pottery installate ({inserted_count} voci)")

        except Exception as e:
            self.log_message(f"Errore installando voci thesaurus Pottery: {e}")


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