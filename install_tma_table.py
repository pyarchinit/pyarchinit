#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per installare la tabella tma_materiali_archeologici
con indici e trigger su SQLite o PostgreSQL
"""

import argparse
import os
import sqlite3
import sys
from typing import Dict

# Per PostgreSQL
try:
    import psycopg2
    from psycopg2 import sql
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("psycopg2 non installato. Supporto PostgreSQL non disponibile.")
    print("Installa con: pip install psycopg2-binary")


class TMATableInstaller:
    """Gestisce l'installazione della tabella TMA"""

    def __init__(self, db_type: str, connection_params: Dict):
        self.db_type = db_type.lower()
        self.connection_params = connection_params
        self.connection = None
        self.cursor = None

    def connect(self):
        """Stabilisce la connessione al database"""
        try:
            if self.db_type == 'sqlite':
                db_path = self.connection_params.get('database', 'tma.db')
                self.connection = sqlite3.connect(db_path)
                self.cursor = self.connection.cursor()
                print(f"✓ Connesso a SQLite: {db_path}")

            elif self.db_type == 'postgresql' and POSTGRES_AVAILABLE:
                self.connection = psycopg2.connect(
                    host=self.connection_params.get('host', 'localhost'),
                    port=self.connection_params.get('port', 5432),
                    database=self.connection_params.get('database'),
                    user=self.connection_params.get('user'),
                    password=self.connection_params.get('password')
                )
                self.cursor = self.connection.cursor()
                print(f"✓ Connesso a PostgreSQL: {self.connection_params.get('database')}")

            else:
                raise ValueError(f"Tipo database non supportato: {self.db_type}")

        except Exception as e:
            print(f"✗ Errore di connessione: {e}")
            sys.exit(1)

    def disconnect(self):
        """Chiude la connessione al database"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def check_table_exists(self) -> bool:
        """Verifica se la tabella esiste già"""
        if self.db_type == 'sqlite':
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='tma_materiali_archeologici'"
            )
        else:  # postgresql
            self.cursor.execute(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tma_materiali_archeologici')"
            )

        return bool(self.cursor.fetchone())

    def drop_table_if_exists(self):
        """Elimina la tabella se esiste"""
        if self.check_table_exists():
            response = input("La tabella esiste già. Vuoi eliminarla e ricrearla? (s/n): ")
            if response.lower() == 's':
                self.cursor.execute("DROP TABLE IF EXISTS tma_materiali_archeologici CASCADE")
                self.connection.commit()
                print("✓ Tabella esistente eliminata")
                return True
            else:
                print("Installazione annullata")
                return False
        return True

    def create_table_sqlite(self):
        """Crea la tabella per SQLite"""
        create_table_sql = """
                           CREATE TABLE tma_materiali_archeologici (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,

                               -- Basic identification
                               sito TEXT,
                               area TEXT,
                               localita TEXT,
                               settore TEXT,
                               inventario TEXT,

                               -- Object data (OG)
                               ogtm TEXT,

                               -- Location data (LC)
                               ldct TEXT,
                               ldcn TEXT,
                               vecchia_collocazione TEXT,
                               cassetta TEXT,

                               -- Excavation data (RE - DSC)
                               scan TEXT,
                               saggio TEXT,
                               vano_locus TEXT,
                               dscd TEXT,
                               dscu TEXT,

                               -- Survey data (RE - RCG)
                               rcgd TEXT,
                               rcgz TEXT,

                               -- Other acquisition (RE - AIN)
                               aint TEXT,
                               aind TEXT,

                               -- Dating (DT)
                               dtzg TEXT,

                               -- Analytical data (DA)
                               deso TEXT,

                               -- Historical-critical notes (NSC)
                               nsc TEXT,

                               -- Documentation (DO)
                               ftap TEXT,
                               ftan TEXT,
                               drat TEXT,
                               dran TEXT,
                               draa TEXT,

                               -- System fields
                               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               created_by TEXT,
                               updated_by TEXT
                           ) \
                           """

        self.cursor.execute(create_table_sql)
        print("✓ Tabella creata con successo")

    def create_table_postgresql(self):
        """Crea la tabella per PostgreSQL"""
        create_table_sql = """
                           CREATE TABLE tma_materiali_archeologici (
                               id SERIAL PRIMARY KEY,

                               -- Basic identification
                               sito TEXT,
                               area TEXT,
                               localita TEXT,
                               settore TEXT,
                               inventario TEXT,

                               -- Object data (OG)
                               ogtm TEXT,

                               -- Location data (LC)
                               ldct TEXT,
                               ldcn TEXT,
                               vecchia_collocazione TEXT,
                               cassetta TEXT,

                               -- Excavation data (RE - DSC)
                               scan TEXT,
                               saggio TEXT,
                               vano_locus TEXT,
                               dscd TEXT,
                               dscu TEXT,

                               -- Survey data (RE - RCG)
                               rcgd TEXT,
                               rcgz TEXT,

                               -- Other acquisition (RE - AIN)
                               aint TEXT,
                               aind TEXT,

                               -- Dating (DT)
                               dtzg TEXT,

                               -- Analytical data (DA)
                               deso TEXT,

                               -- Historical-critical notes (NSC)
                               nsc TEXT,

                               -- Documentation (DO)
                               ftap TEXT,
                               ftan TEXT,
                               drat TEXT,
                               dran TEXT,
                               draa TEXT,

                               -- System fields
                               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               created_by TEXT,
                               updated_by TEXT
                           ) \
                           """

        self.cursor.execute(create_table_sql)

        print("✓ Tabella tma_materiali_archeologici creata con successo")

    def create_table_ripetibili_sqlite(self):
        """Crea la tabella tma_materiali_ripetibili per SQLite"""
        create_table_sql = """
                           CREATE TABLE tma_materiali_ripetibili (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,

                               -- Foreign key to main TMA record
                               id_tma INTEGER NOT NULL,

                               -- Material description data (MAD)
                               madi TEXT,

                               -- Material component data (MAC) - all repetitive
                               macc TEXT,
                               macl TEXT,
                               macp TEXT,
                               macd TEXT,
                               cronologia_mac TEXT,
                               macq TEXT,
                               peso REAL,

                               -- System fields
                               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               created_by TEXT,
                               updated_by TEXT,

                               FOREIGN KEY (id_tma) REFERENCES tma_materiali_archeologici(id) ON DELETE CASCADE
                           ) \
                           """

        self.cursor.execute(create_table_sql)
        print("✓ Tabella tma_materiali_ripetibili creata con successo")

    def create_table_ripetibili_postgresql(self):
        """Crea la tabella tma_materiali_ripetibili per PostgreSQL"""
        create_table_sql = """
                           CREATE TABLE tma_materiali_ripetibili (
                               id SERIAL PRIMARY KEY,

                               -- Foreign key to main TMA record
                               id_tma INTEGER NOT NULL,

                               -- Material description data (MAD)
                               madi TEXT,

                               -- Material component data (MAC) - all repetitive
                               macc TEXT,
                               macl TEXT,
                               macp TEXT,
                               macd TEXT,
                               cronologia_mac TEXT,
                               macq TEXT,
                               peso FLOAT,

                               -- System fields
                               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               created_by TEXT,
                               updated_by TEXT,

                               CONSTRAINT fk_tma_materiali_ripetibili_tma
                                   FOREIGN KEY (id_tma)
                                   REFERENCES tma_materiali_archeologici(id)
                                   ON DELETE CASCADE
                           ) \
                           """

        self.cursor.execute(create_table_sql)
        print("✓ Tabella tma_materiali_ripetibili creata con successo")

    def create_indices(self):
        """Crea gli indici sulla tabella"""
        indices = [
            "CREATE INDEX idx_tma_ogtm ON tma_materiali_archeologici(ogtm)",
            "CREATE INDEX idx_tma_ldcn ON tma_materiali_archeologici(ldcn)",
            "CREATE INDEX idx_tma_cassetta ON tma_materiali_archeologici(cassetta)",
            "CREATE INDEX idx_tma_localita ON tma_materiali_archeologici(localita)",
            "CREATE INDEX idx_tma_dscu ON tma_materiali_archeologici(dscu)",
            "CREATE INDEX idx_tma_dtzg ON tma_materiali_archeologici(dtzg)",
            "CREATE INDEX idx_tma_macc ON tma_materiali_archeologici(macc)"
        ]

        for idx_sql in indices:
            try:
                self.cursor.execute(idx_sql)
                print(f"✓ Indice creato: {idx_sql.split()[2]}")
            except Exception as e:
                print(f"✗ Errore creazione indice: {e}")

    def create_triggers_sqlite(self):
        """Crea i trigger per SQLite"""
        trigger_sql = """
                      CREATE TRIGGER update_tma_updated_at
                          AFTER UPDATE ON tma_materiali_archeologici
                      BEGIN
                          UPDATE tma_materiali_archeologici
                          SET updated_at = CURRENT_TIMESTAMP
                          WHERE id = NEW.id;
                      END \
                      """

        try:
            self.cursor.execute(trigger_sql)
            print("✓ Trigger update_tma_updated_at creato")
        except Exception as e:
            print(f"✗ Errore creazione trigger: {e}")

    def create_triggers_postgresql(self):
        """Crea i trigger per PostgreSQL"""
        # Crea la funzione
        function_sql = """
                       CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
                       BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
                       RETURN NEW;
                       END;
        $$ language 'plpgsql' \
                       """

        # Crea il trigger
        trigger_sql = """
                      CREATE TRIGGER update_tma_updated_at
                          BEFORE UPDATE ON tma_materiali_archeologici
                          FOR EACH ROW
                          EXECUTE FUNCTION update_updated_at_column() \
                      """

        try:
            self.cursor.execute(function_sql)
            self.cursor.execute(trigger_sql)
            print("✓ Funzione e trigger update_tma_updated_at creati")
        except Exception as e:
            print(f"✗ Errore creazione trigger: {e}")

    def insert_test_data(self):
        """Inserisce dati di test"""
        test_data = """
                    INSERT INTO tma_materiali_archeologici
                        (ogtm, ldcn, cassetta, localita, dscu, dtzg, macc, created_by)
                    VALUES
                        ('CERAMICA', 'Museo Archeologico', 'C001', 'Roma', 'US 101', 'Età Romana', 'Anfora', 'admin'),
                        ('METALLO', 'Deposito Centrale', 'M002', 'Pompei', 'US 205', 'I secolo d.C.', 'Moneta', 'admin'),
                        ('LITICA', 'Magazzino A', 'L003', 'Ostia', 'US 312', 'Età Imperiale', 'Strumento', 'admin') \
                    """

        try:
            self.cursor.execute(test_data)
            print("✓ Dati di test inseriti")
        except Exception as e:
            print(f"✗ Errore inserimento dati test: {e}")

    def verify_installation(self):
        """Verifica l'installazione"""
        # Conta record
        self.cursor.execute("SELECT COUNT(*) FROM tma_materiali_archeologici")
        count = self.cursor.fetchone()[0]
        print(f"\n📊 Statistiche installazione:")
        print(f"   - Record nella tabella: {count}")

        # Verifica indici
        if self.db_type == 'sqlite':
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='tma_materiali_archeologici'")
            indices = [row[0] for row in self.cursor.fetchall()]
        else:
            self.cursor.execute("""
                                SELECT indexname FROM pg_indexes
                                WHERE tablename = 'tma_materiali_archeologici'
                                """)
            indices = [row[0] for row in self.cursor.fetchall()]

        print(f"   - Indici creati: {len(indices)}")
        for idx in indices:
            print(f"     • {idx}")

        # Verifica trigger
        if self.db_type == 'sqlite':
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger' AND tbl_name='tma_materiali_archeologici'")
            triggers = [row[0] for row in self.cursor.fetchall()]
        else:
            self.cursor.execute("""
                                SELECT trigger_name FROM information_schema.triggers
                                WHERE event_object_table = 'tma_materiali_archeologici'
                                """)
            triggers = [row[0] for row in self.cursor.fetchall()]

        print(f"   - Trigger creati: {len(triggers)}")
        for trg in triggers:
            print(f"     • {trg}")

    def install(self, include_test_data: bool = False):
        """Esegue l'installazione completa"""
        print(f"\n🚀 Installazione tabella TMA su {self.db_type.upper()}")
        print("=" * 50)

        try:
            self.connect()

            # Verifica e gestisci tabella esistente
            if not self.drop_table_if_exists():
                return

            # Crea tabelle
            if self.db_type == 'sqlite':
                self.create_table_sqlite()
                self.create_table_ripetibili_sqlite()
            else:
                self.create_table_postgresql()
                self.create_table_ripetibili_postgresql()

            # Crea indici
            self.create_indices()

            # Crea trigger
            if self.db_type == 'sqlite':
                self.create_triggers_sqlite()
            else:
                self.create_triggers_postgresql()

            # Inserisci dati di test se richiesto
            if include_test_data:
                self.insert_test_data()

            # Commit delle modifiche
            self.connection.commit()

            # Verifica installazione
            self.verify_installation()

            print("\n✅ Installazione completata con successo!")

        except Exception as e:
            print(f"\n❌ Errore durante l'installazione: {e}")
            if self.connection:
                self.connection.rollback()

        finally:
            self.disconnect()


def get_sqlite_params() -> Dict:
    """Ottiene i parametri per SQLite"""
    print("\nConfigurazione SQLite:")
    db_path = input("Percorso database (default: tma.db): ").strip()
    if not db_path:
        db_path = "tma.db"

    # Crea directory se non esiste
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    return {'database': db_path}


def get_postgresql_params() -> Dict:
    """Ottiene i parametri per PostgreSQL"""
    print("\nConfigurazione PostgreSQL:")
    params = {
        'host': input("Host (default: localhost): ").strip() or 'localhost',
        'port': input("Porta (default: 5432): ").strip() or '5432',
        'database': input("Nome database: ").strip(),
        'user': input("Username: ").strip(),
        'password': input("Password: ").strip()
    }

    # Validazione
    if not params['database'] or not params['user']:
        print("❌ Database e username sono obbligatori!")
        sys.exit(1)

    return params


def main():
    """Funzione principale"""
    parser = argparse.ArgumentParser(
        description='Installa la tabella tma_materiali_archeologici con indici e trigger'
    )

    parser.add_argument(
        '--db-type',
        choices=['sqlite', 'postgresql'],
        help='Tipo di database'
    )

    parser.add_argument(
        '--test-data',
        action='store_true',
        help='Inserisce dati di test'
    )

    parser.add_argument(
        '--sqlite-path',
        help='Percorso del database SQLite'
    )

    parser.add_argument(
        '--pg-host',
        help='Host PostgreSQL'
    )

    parser.add_argument(
        '--pg-port',
        help='Porta PostgreSQL'
    )

    parser.add_argument(
        '--pg-database',
        help='Nome database PostgreSQL'
    )

    parser.add_argument(
        '--pg-user',
        help='Username PostgreSQL'
    )

    parser.add_argument(
        '--pg-password',
        help='Password PostgreSQL'
    )

    args = parser.parse_args()

    # Modalità interattiva se non ci sono argomenti
    if not args.db_type:
        print("=== Installatore Tabella TMA ===")
        print("\nSeleziona il tipo di database:")
        print("1. SQLite")
        print("2. PostgreSQL")

        choice = input("\nScelta (1-2): ").strip()

        if choice == '1':
            db_type = 'sqlite'
            params = get_sqlite_params()
        elif choice == '2':
            if not POSTGRES_AVAILABLE:
                print("❌ PostgreSQL non disponibile. Installa psycopg2-binary")
                sys.exit(1)
            db_type = 'postgresql'
            params = get_postgresql_params()
        else:
            print("❌ Scelta non valida")
            sys.exit(1)

        test_data = input("\nVuoi inserire dati di test? (s/n): ").strip().lower() == 's'

    else:
        # Modalità con argomenti
        db_type = args.db_type

        if db_type == 'sqlite':
            params = {'database': args.sqlite_path or 'tma.db'}
        else:
            params = {
                'host': args.pg_host or 'localhost',
                'port': args.pg_port or '5432',
                'database': args.pg_database,
                'user': args.pg_user,
                'password': args.pg_password
            }

            if not params['database'] or not params['user']:
                print("❌ Per PostgreSQL sono richiesti database e user")
                sys.exit(1)

        test_data = args.test_data

    # Esegui installazione
    installer = TMATableInstaller(db_type, params)
    installer.install(include_test_data=test_data)


if __name__ == "__main__":
    main()
