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