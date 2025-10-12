#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per aggiornare database SQLite vecchi di PyArchInit
Aggiunge le colonne mancanti per renderli compatibili con la versione attuale
"""

import os
import sys
import sqlite3
import argparse
from datetime import datetime

class PyArchInitDBUpdater:
    """Classe per aggiornare database SQLite vecchi di PyArchInit"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.updates_made = []
        
    def connect(self):
        """Connette al database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"✓ Connesso a: {self.db_path}")
            return True
        except Exception as e:
            print(f"✗ Errore connessione: {e}")
            return False
    
    def check_column_exists(self, table_name, column_name):
        """Verifica se una colonna esiste in una tabella"""
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [column[1] for column in self.cursor.fetchall()]
            return column_name in columns
        except:
            return False
    
    def check_table_exists(self, table_name):
        """Verifica se una tabella esiste"""
        try:
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
                (table_name,)
            )
            return self.cursor.fetchone() is not None
        except:
            return False
    
    def add_column(self, table_name, column_name, column_type, default_value=None):
        """Aggiunge una colonna a una tabella se non esiste"""
        if not self.check_table_exists(table_name):
            print(f"  ⚠ Tabella {table_name} non esiste, skip")
            return False
            
        if self.check_column_exists(table_name, column_name):
            print(f"  - Colonna {table_name}.{column_name} già esiste")
            return False
        
        try:
            if default_value is not None:
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} DEFAULT {default_value}"
            else:
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            
            self.cursor.execute(sql)
            self.conn.commit()
            print(f"  ✓ Aggiunta colonna {table_name}.{column_name}")
            self.updates_made.append(f"{table_name}.{column_name}")
            return True
        except Exception as e:
            print(f"  ✗ Errore aggiungendo {table_name}.{column_name}: {e}")
            return False
    
    def update_pyarchinit_thesaurus_sigle(self):
        """Aggiorna la tabella pyarchinit_thesaurus_sigle"""
        print("\n▶ Aggiornamento tabella pyarchinit_thesaurus_sigle...")
        
        # Colonne mancanti per pyarchinit_thesaurus_sigle
        columns_to_add = [
            ('n_tipologia', 'INTEGER', 'NULL'),
            ('n_sigla', 'INTEGER', 'NULL'),
            ('id_parent', 'INTEGER', 'NULL'),
            ('parent_sigla', 'TEXT', 'NULL'),
            ('hierarchy_level', 'INTEGER', '0'),
            ('order_layer', 'INTEGER', '0')
        ]
        
        for column_name, column_type, default in columns_to_add:
            self.add_column('pyarchinit_thesaurus_sigle', column_name, column_type, default)
    
    def update_us_table(self):
        """Aggiorna la tabella us_table"""
        print("\n▶ Aggiornamento tabella us_table...")
        
        # Colonne che potrebbero mancare nelle versioni vecchie
        columns_to_add = [
            ('order_layer', 'INTEGER', '0'),
            ('settore', 'TEXT', 'NULL'),
            ('attivita', 'TEXT', 'NULL'),
            ('anno_scavo', 'TEXT', 'NULL'),
            ('metodo_di_scavo', 'TEXT', 'NULL'),
            ('data_schedatura', 'TEXT', 'NULL'),
            ('schedatore', 'TEXT', 'NULL'),
            ('quota_min_usm', 'REAL', 'NULL'),
            ('quota_max_usm', 'REAL', 'NULL'),
            ('ref_tm', 'TEXT', 'NULL'),
            ('ref_ra', 'TEXT', 'NULL'),
            ('ref_n', 'TEXT', 'NULL'),
            ('posizione', 'TEXT', 'NULL'),
            ('criteri_distinzione', 'TEXT', 'NULL'),
            ('modo_formazione', 'TEXT', 'NULL'),
            ('colore', 'TEXT', 'NULL'),
            ('consistenza', 'TEXT', 'NULL'),
            ('struttura', 'TEXT', 'NULL'),
            ('soprintendenza', 'TEXT', 'NULL'),
            ('responsabile', 'TEXT', 'NULL'),
            ('rapporti2', 'TEXT', 'NULL'),
            ('sing_doc', 'TEXT', 'NULL'),
            ('unita_edilizie', 'TEXT', 'NULL'),
            ('quantificazioni', 'TEXT', 'NULL'),
            ('alt_mod', 'TEXT', 'NULL'),
            # Colonne aggiuntive dallo schema PostgreSQL
            ('documentazione', 'TEXT', 'NULL'),
            ('unita_tipo', 'TEXT', "'US'"),
            ('quad_par', 'TEXT', "''"),
            ('ambient', 'TEXT', "''"),
            ('saggio', 'TEXT', "''"),
            ('elem_datanti', 'TEXT', "''"),
            ('funz_statica', 'TEXT', "''"),
            ('lavorazione', 'TEXT', "''"),
            ('spess_giunti', 'TEXT', "''"),
            ('letti_posa', 'TEXT', "''"),
            ('un_ed_riass', 'TEXT', "''"),
            ('reimp', 'TEXT', "''"),
            ('posa_opera', 'TEXT', "''"),
            ('cons_legante', 'TEXT', "''"),
            ('col_legante', 'TEXT', "''"),
            ('aggreg_legante', 'TEXT', "''"),
            ('con_text_mat', 'TEXT', "''"),
            ('col_materiale', 'TEXT', "''"),
            ('inclusi_materiali_usm', 'TEXT', "''"),
            ('n_catalogo_generale', 'TEXT', 'NULL'),
            ('n_catalogo_interno', 'TEXT', 'NULL'),
            ('n_catalogo_internazionale', 'TEXT', 'NULL'),
            ('soprintendenza', 'TEXT', 'NULL'),
            ('quota_relativa', 'REAL', 'NULL'),
            ('quota_abs', 'REAL', 'NULL'),
            ('ref_tm', 'TEXT', 'NULL'),
            ('ref_ra', 'TEXT', 'NULL'),
            ('ref_n', 'TEXT', 'NULL'),
            ('posizione', 'TEXT', 'NULL'),
            ('criteri_distinzione_usm', 'TEXT', 'NULL'),
            ('uso_primario_usm', 'TEXT', 'NULL'),
            ('tipologia_avanzata', 'TEXT', 'NULL'),
            ('tecnica_muraria_usm', 'TEXT', 'NULL'),
            ('modulo_usm', 'TEXT', 'NULL'),
            ('campioni_malta_usm', 'TEXT', 'NULL'),
            ('campioni_mattone_usm', 'TEXT', 'NULL'),
            ('campioni_pietra_usm', 'TEXT', 'NULL'),
            ('provenienza_materiali_usm', 'TEXT', 'NULL'),
            ('criteri_distinzione_usm', 'TEXT', 'NULL'),
            ('spessore_usm', 'TEXT', 'NULL'),
            ('organici', 'TEXT', 'NULL'),
            ('inorganici', 'TEXT', 'NULL'),
            ('doc_usv', 'TEXT', "''")
        ]
        
        for column_name, column_type, default in columns_to_add:
            self.add_column('us_table', column_name, column_type, default)
    
    def update_site_table(self):
        """Aggiorna la tabella site_table"""
        print("\n▶ Aggiornamento tabella site_table...")
        
        columns_to_add = [
            ('provincia', 'TEXT', 'NULL'),
            ('comune', 'TEXT', 'NULL'),
            ('toponimo', 'TEXT', 'NULL'),
            ('indirizzo', 'TEXT', 'NULL'),
            ('cap', 'TEXT', 'NULL'),
            ('localita', 'TEXT', 'NULL'),
            ('stagione', 'TEXT', 'NULL'),
            ('settore', 'TEXT', 'NULL'),
            ('tipo_ricerca', 'TEXT', 'NULL'),
            ('organizzazione', 'TEXT', 'NULL'),
            ('responsabile_sito', 'TEXT', 'NULL'),
            ('responsabile_scavo', 'TEXT', 'NULL'),
            ('direttore', 'TEXT', 'NULL'),
            ('assistente', 'TEXT', 'NULL'),
            ('sponsor', 'TEXT', 'NULL'),
            ('data_inizio', 'TEXT', 'NULL'),
            ('data_fine', 'TEXT', 'NULL'),
            ('datazione_generale', 'TEXT', 'NULL'),
            ('latitudine', 'REAL', 'NULL'),
            ('longitudine', 'REAL', 'NULL'),
            ('quota', 'REAL', 'NULL'),
            ('geom', 'TEXT', 'NULL'),
            ('sistema_ricognizione', 'TEXT', 'NULL'),
            ('geometria', 'TEXT', 'NULL'),
            ('bibliografia', 'TEXT', 'NULL'),
            ('note', 'TEXT', 'NULL')
        ]
        
        for column_name, column_type, default in columns_to_add:
            self.add_column('site_table', column_name, column_type, default)
    
    def update_inventario_materiali(self):
        """Aggiorna la tabella inventario_materiali_table"""
        print("\n▶ Aggiornamento tabella inventario_materiali_table...")
        
        columns_to_add = [
            ('stato_conservazione', 'TEXT', 'NULL'),
            ('datazione', 'TEXT', 'NULL'),
            ('years', 'TEXT', 'NULL'),  # Anno di scavo
            ('quantita_frr', 'INTEGER', 'NULL'),
            ('weight', 'REAL', 'NULL'),
            ('diametro', 'REAL', 'NULL'),
            ('lunghezza', 'REAL', 'NULL'),
            ('larghezza', 'REAL', 'NULL'),
            ('spessore', 'REAL', 'NULL'),
            ('disegno', 'TEXT', 'NULL'),
            ('numero_cassa', 'TEXT', 'NULL'),
            ('soprintendenza', 'TEXT', 'NULL'),
            ('schedatore', 'TEXT', 'NULL'),
            ('data_repertazione', 'TEXT', 'NULL'),
            ('tecnologie', 'TEXT', 'NULL'),
            ('forme_minime', 'INTEGER', 'NULL'),
            ('forme_massime', 'INTEGER', 'NULL'),
            ('totale_frammenti', 'INTEGER', 'NULL'),
            ('tipo', 'TEXT', 'NULL'),
            ('rif_biblio', 'TEXT', 'NULL'),
            ('cronologia', 'TEXT', 'NULL'),
            ('compilatore', 'TEXT', 'NULL'),
            ('data_compilazione', 'TEXT', 'NULL')
        ]
        
        for column_name, column_type, default in columns_to_add:
            self.add_column('inventario_materiali_table', column_name, column_type, default)
    
    def update_pottery_table(self):
        """Aggiorna la tabella pottery_table"""
        print("\n▶ Aggiornamento tabella pottery_table...")
        
        columns_to_add = [
            ('anno', 'TEXT', 'NULL'),
            ('fabric', 'TEXT', 'NULL'),
            ('percent', 'TEXT', 'NULL'),
            ('material', 'TEXT', 'NULL'),
            ('form', 'TEXT', 'NULL'),
            ('specific_form', 'TEXT', 'NULL'),
            ('surface_treatment', 'TEXT', 'NULL'),
            ('diagnostic', 'TEXT', 'NULL'),
            ('ware', 'TEXT', 'NULL'),
            ('comments', 'TEXT', 'NULL'),
            ('illustration', 'TEXT', 'NULL'),
            ('museo', 'TEXT', 'NULL'),
            ('catalogo', 'TEXT', 'NULL'),
            ('disegno', 'TEXT', 'NULL'),
            ('diametro', 'REAL', 'NULL'),
            ('peso', 'REAL', 'NULL'),
            ('spessore', 'REAL', 'NULL'),
            ('altezza', 'REAL', 'NULL'),
            ('larghezza', 'REAL', 'NULL'),
            ('conservazione', 'TEXT', 'NULL'),
            ('frammenti', 'INTEGER', 'NULL'),
            ('frr_extravascolari', 'INTEGER', 'NULL')
        ]
        
        for column_name, column_type, default in columns_to_add:
            self.add_column('pottery_table', column_name, column_type, default)
    
    def update_struttura_table(self):
        """Aggiorna la tabella struttura_table"""
        print("\n▶ Aggiornamento tabella struttura_table...")
        
        columns_to_add = [
            ('sigla_struttura', 'TEXT', 'NULL'),
            ('numero_struttura', 'INTEGER', 'NULL'),
            ('categoria_struttura', 'TEXT', 'NULL'),
            ('tipologia_struttura', 'TEXT', 'NULL'),
            ('definizione_struttura', 'TEXT', 'NULL'),
            ('descrizione', 'TEXT', 'NULL'),
            ('interpretazione', 'TEXT', 'NULL'),
            ('periodo_iniziale', 'TEXT', 'NULL'),
            ('fase_iniziale', 'TEXT', 'NULL'),
            ('periodo_finale', 'TEXT', 'NULL'),
            ('fase_finale', 'TEXT', 'NULL'),
            ('datazione_estesa', 'TEXT', 'NULL'),
            ('materiali_impiegati', 'TEXT', 'NULL'),
            ('elementi_strutturali', 'TEXT', 'NULL'),
            ('rapporti_struttura', 'TEXT', 'NULL'),
            ('misurazioni_struttura', 'TEXT', 'NULL'),
            ('criteri_distinzione', 'TEXT', 'NULL'),
            ('uso', 'TEXT', 'NULL'),
            ('funzione', 'TEXT', 'NULL'),
            ('quota_min', 'REAL', 'NULL'),
            ('quota_max', 'REAL', 'NULL'),
            ('stato_di_conservazione', 'TEXT', 'NULL'),
            ('ref_n', 'TEXT', 'NULL'),
            ('ref_ra', 'TEXT', 'NULL')
        ]
        
        for column_name, column_type, default in columns_to_add:
            self.add_column('struttura_table', column_name, column_type, default)
    
    def update_periodizzazione_table(self):
        """Aggiorna la tabella periodizzazione_table"""
        print("\n▶ Aggiornamento tabella periodizzazione_table...")
        
        columns_to_add = [
            ('datazione_estesa', 'TEXT', 'NULL'),
            ('data_calibrated', 'INTEGER', 'NULL'),
            ('descrizione', 'TEXT', 'NULL'),
            ('cronologia_generica', 'TEXT', 'NULL'),
            ('cronologia_specifica', 'TEXT', 'NULL'),
            ('anno_inizio', 'INTEGER', 'NULL'),
            ('anno_fine', 'INTEGER', 'NULL'),
            ('ref_tm', 'TEXT', 'NULL'),
            ('ref_n', 'TEXT', 'NULL')
        ]
        
        for column_name, column_type, default in columns_to_add:
            self.add_column('periodizzazione_table', column_name, column_type, default)
    
    def fix_vector_layer_views(self):
        """Corregge i tipi di campo nelle view dei layer vettoriali"""
        print("\n▶ Correzione view layer vettoriali...")
        
        # Lista delle view che devono essere ricreate
        views_to_fix = [
            'pyarchinit_quote',
            'pyarchinit_quote_usm', 
            'pyunitasratigrafiche',
            'pyunistarstigrafiche_usm'
        ]
        
        for view_name in views_to_fix:
            try:
                # Prima verifica se la view esiste
                self.cursor.execute(
                    "SELECT sql FROM sqlite_master WHERE type='view' AND name=?", 
                    (view_name,)
                )
                result = self.cursor.fetchone()
                
                if result:
                    old_sql = result[0]
                    print(f"  ⚠ Drop view {view_name}")
                    self.cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
                    
                    # Ricrea la view con i campi convertiti a integer
                    if 'pyarchinit_quote' in view_name:
                        # Gestione specifica per view quote
                        new_sql = self._create_quote_view_sql(view_name)
                    elif 'pyunit' in view_name:
                        # Gestione specifica per view unità stratigrafiche
                        new_sql = self._create_us_view_sql(view_name)
                    else:
                        # Tentativo generico di conversione
                        new_sql = old_sql.replace('us_s', 'CAST(us_s AS INTEGER) as us_s')
                        new_sql = new_sql.replace('us_q', 'CAST(us_q AS INTEGER) as us_q')
                        new_sql = new_sql.replace('area,', 'CAST(area AS INTEGER) as area,')
                        new_sql = new_sql.replace('area ', 'CAST(area AS INTEGER) as area ')
                    
                    print(f"  ✓ Ricreazione view {view_name} con campi INTEGER")
                    self.cursor.execute(new_sql)
                    self.updates_made.append(f"RECREATE VIEW {view_name}")
                    
            except Exception as e:
                print(f"  ✗ Errore correggendo view {view_name}: {e}")
    
    def _create_quote_view_sql(self, view_name):
        """Crea SQL per ricreare le view quote con campi corretti"""
        if view_name == 'pyarchinit_quote':
            return '''
                CREATE VIEW pyarchinit_quote AS
                SELECT 
                    sito,
                    CAST(area AS INTEGER) as area,
                    CAST(us AS INTEGER) as us,
                    unita_tipo,
                    quota_min,
                    quota_max,
                    the_geom
                FROM us_table
                WHERE quota_min IS NOT NULL OR quota_max IS NOT NULL
            '''
        elif view_name == 'pyarchinit_quote_usm':
            return '''
                CREATE VIEW pyarchinit_quote_usm AS
                SELECT 
                    sito,
                    CAST(area AS INTEGER) as area,
                    CAST(us AS INTEGER) as us,
                    unita_tipo,
                    quota_min_usm,
                    quota_max_usm,
                    the_geom
                FROM us_table
                WHERE unita_tipo = 'USM' AND (quota_min_usm IS NOT NULL OR quota_max_usm IS NOT NULL)
            '''
        return ''
    
    def _create_us_view_sql(self, view_name):
        """Crea SQL per ricreare le view unità stratigrafiche con campi corretti"""
        if view_name == 'pyunitasratigrafiche':
            return '''
                CREATE VIEW pyunitasratigrafiche AS
                SELECT 
                    id_us,
                    sito,
                    CAST(area AS INTEGER) as area,
                    CAST(us AS INTEGER) as us,
                    d_stratigrafica,
                    d_interpretativa,
                    descrizione,
                    interpretazione,
                    periodo_iniziale,
                    fase_iniziale,
                    periodo_finale,
                    fase_finale,
                    scavato,
                    attivita,
                    anno_scavo,
                    metodo_di_scavo,
                    inclusi,
                    campioni,
                    rapporti,
                    organici,
                    inorganici,
                    data_schedatura,
                    schedatore,
                    formazione,
                    stato_di_conservazione,
                    colore,
                    consistenza,
                    struttura,
                    cont_per,
                    order_layer,
                    the_geom
                FROM us_table
                WHERE unita_tipo = 'US'
            '''
        elif view_name == 'pyunistarstigrafiche_usm':
            return '''
                CREATE VIEW pyunistarstigrafiche_usm AS
                SELECT 
                    id_us,
                    sito,
                    CAST(area AS INTEGER) as area,
                    CAST(us AS INTEGER) as us,
                    unita_tipo,
                    d_stratigrafica,
                    d_interpretativa,
                    descrizione,
                    interpretazione,
                    periodo_iniziale,
                    fase_iniziale,
                    periodo_finale,
                    fase_finale,
                    scavato,
                    attivita,
                    anno_scavo,
                    metodo_di_scavo,
                    inclusi,
                    campioni,
                    rapporti,
                    organici,
                    inorganici,
                    data_schedatura,
                    schedatore,
                    formazione,
                    stato_di_conservazione,
                    colore,
                    consistenza,
                    struttura,
                    cont_per,
                    order_layer,
                    the_geom
                FROM us_table
                WHERE unita_tipo = 'USM'
            '''
        return ''

    def create_missing_tables(self):
        """Crea tabelle che potrebbero mancare completamente"""
        print("\n▶ Verifica e creazione tabelle mancanti...")
        
        # Tabella pyarchinit_thesaurus_sigle
        if not self.check_table_exists('pyarchinit_thesaurus_sigle'):
            print("  ✓ Creazione tabella pyarchinit_thesaurus_sigle...")
            self.cursor.execute('''
                CREATE TABLE pyarchinit_thesaurus_sigle (
                    id_thesaurus_sigle INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_tabella TEXT,
                    sigla TEXT,
                    sigla_estesa TEXT,
                    descrizione TEXT,
                    tipologia_sigla TEXT,
                    lingua TEXT,
                    order_layer INTEGER DEFAULT 0,
                    id_parent INTEGER,
                    parent_sigla TEXT,
                    hierarchy_level INTEGER DEFAULT 0,
                    n_tipologia INTEGER,
                    n_sigla INTEGER
                )
            ''')
            self.conn.commit()
            self.updates_made.append("CREATE TABLE pyarchinit_thesaurus_sigle")
            
            # Inserisci alcuni valori di default
            self.cursor.execute('''
                INSERT INTO pyarchinit_thesaurus_sigle 
                (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
                VALUES 
                ('us_table', '1', 'Strato', 'Unità stratigrafica di accumulo', '2.19', 'IT'),
                ('us_table', '2', 'Taglio', 'Unità stratigrafica negativa', '2.19', 'IT'),
                ('us_table', '3', 'Struttura', 'Unità stratigrafica muraria', '2.19', 'IT')
            ''')
            self.conn.commit()
        else:
            # Aggiungi le colonne del thesaurus se mancano
            self.update_pyarchinit_thesaurus_sigle()
    
    def create_triggers(self):
        """Crea i trigger necessari per il database"""
        print("\n▶ Creazione trigger...")
        
        # Drop trigger esistente se presente
        try:
            self.cursor.execute("DROP TRIGGER IF EXISTS create_doc")
            print("  ⚠ Drop trigger create_doc esistente")
        except:
            pass
        
        # Crea il trigger create_doc per SQLite
        # Nota: SQLite non supporta IF/EXCEPTION come PostgreSQL, quindi semplifichiamo
        try:
            self.cursor.execute('''
                CREATE TRIGGER create_doc
                AFTER UPDATE OF d_interpretativa ON us_table
                FOR EACH ROW
                WHEN NEW.d_interpretativa != OLD.d_interpretativa
                BEGIN
                    UPDATE us_table
                    SET d_interpretativa = NEW.doc_usv
                    WHERE sito = NEW.sito
                      AND area = NEW.area
                      AND us = NEW.us
                      AND unita_tipo = 'DOC';
                END
            ''')
            self.updates_made.append("CREATE TRIGGER create_doc")
            print("  ✓ Creato trigger create_doc")
        except Exception as e:
            print(f"  ✗ Errore creando trigger create_doc: {e}")
    
    def backup_database(self):
        """Crea un backup del database prima delle modifiche"""
        backup_path = self.db_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            print(f"✓ Backup creato: {backup_path}")
            return True
        except Exception as e:
            print(f"✗ Errore creazione backup: {e}")
            return False
    
    def update_database(self):
        """Esegue tutti gli aggiornamenti necessari"""
        print(f"\n{'='*60}")
        print(f"PyArchInit Database Updater")
        print(f"Database: {os.path.basename(self.db_path)}")
        print(f"{'='*60}")
        
        if not self.connect():
            return False
        
        # Crea backup
        if not self.backup_database():
            response = input("Continuare senza backup? (s/n): ")
            if response.lower() != 's':
                return False
        
        # Crea tabelle mancanti
        self.create_missing_tables()
        
        # Correggi le view dei layer vettoriali
        self.fix_vector_layer_views()
        
        # Aggiorna le tabelle
        self.update_pyarchinit_thesaurus_sigle()
        self.update_us_table()
        self.update_site_table()
        self.update_inventario_materiali()
        self.update_pottery_table()
        self.update_struttura_table()
        self.update_periodizzazione_table()
        
        # Crea i trigger
        self.create_triggers()
        
        # Altri aggiornamenti possono essere aggiunti qui
        
        # Chiudi connessione
        self.conn.close()
        
        # Report finale
        print(f"\n{'='*60}")
        print(f"✓ Aggiornamento completato!")
        print(f"  Modifiche effettuate: {len(self.updates_made)}")
        if self.updates_made:
            print("\n  Dettagli modifiche:")
            for update in self.updates_made:
                print(f"    - {update}")
        print(f"{'='*60}\n")
        
        return True


def main():
    """Funzione principale"""
    parser = argparse.ArgumentParser(
        description='Aggiorna database SQLite vecchi di PyArchInit'
    )
    parser.add_argument(
        'database', 
        help='Percorso del database SQLite da aggiornare'
    )
    parser.add_argument(
        '--batch', 
        action='store_true',
        help='Modalità batch (aggiorna tutti i .sqlite nella directory)'
    )
    
    args = parser.parse_args()
    
    if args.batch:
        # Modalità batch - aggiorna tutti i database nella directory
        if os.path.isdir(args.database):
            db_dir = args.database
            sqlite_files = [f for f in os.listdir(db_dir) 
                          if f.endswith('.sqlite') and not f.endswith('.backup')]
            
            print(f"Trovati {len(sqlite_files)} database da aggiornare")
            
            for db_file in sqlite_files:
                db_path = os.path.join(db_dir, db_file)
                updater = PyArchInitDBUpdater(db_path)
                updater.update_database()
        else:
            print("In modalità batch, specificare una directory")
            return 1
    else:
        # Modalità singolo file
        if not os.path.exists(args.database):
            print(f"File non trovato: {args.database}")
            return 1
            
        updater = PyArchInitDBUpdater(args.database)
        updater.update_database()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())