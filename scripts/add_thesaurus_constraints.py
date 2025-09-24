#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to add unique constraints to the thesaurus table
This prevents duplicate records during import operations
"""

import os
import sys
import sqlite3
import psycopg2
from psycopg2 import sql

def add_constraints_sqlite(db_path):
    """Add unique constraints to SQLite database."""
    print(f"Adding constraints to SQLite database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='pyarchinit_thesaurus_sigle'
        """)

        if not cursor.fetchone():
            print("Table pyarchinit_thesaurus_sigle not found")
            return False

        # Add columns if they don't exist
        cursor.execute("PRAGMA table_info(pyarchinit_thesaurus_sigle)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'lingua' not in columns:
            cursor.execute("""
                ALTER TABLE pyarchinit_thesaurus_sigle
                ADD COLUMN lingua VARCHAR(10) DEFAULT 'it'
            """)
            print("Added lingua column")

        if 'n_tipologia' not in columns:
            cursor.execute("""
                ALTER TABLE pyarchinit_thesaurus_sigle
                ADD COLUMN n_tipologia INTEGER
            """)
            print("Added n_tipologia column")

        if 'n_sigla' not in columns:
            cursor.execute("""
                ALTER TABLE pyarchinit_thesaurus_sigle
                ADD COLUMN n_sigla INTEGER
            """)
            print("Added n_sigla column")

        # SQLite doesn't support adding constraints to existing tables
        # We need to recreate the table with constraints
        print("Recreating table with unique constraints...")

        # Create new table with constraints
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pyarchinit_thesaurus_sigle_new (
                id_thesaurus_sigle INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_tabella TEXT,
                sigla TEXT,
                sigla_estesa TEXT,
                descrizione TEXT,
                tipologia_sigla TEXT,
                lingua TEXT DEFAULT 'it',
                n_tipologia INTEGER,
                n_sigla INTEGER,
                order_layer INTEGER DEFAULT 0,
                id_parent INTEGER,
                parent_sigla TEXT,
                hierarchy_level INTEGER DEFAULT 0,
                UNIQUE(lingua, nome_tabella, tipologia_sigla, sigla_estesa),
                UNIQUE(lingua, nome_tabella, tipologia_sigla, sigla)
            )
        """)

        # Copy data from old table
        cursor.execute("""
            INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle_new
            SELECT * FROM pyarchinit_thesaurus_sigle
        """)

        # Drop old table and rename new one
        cursor.execute("DROP TABLE pyarchinit_thesaurus_sigle")
        cursor.execute("ALTER TABLE pyarchinit_thesaurus_sigle_new RENAME TO pyarchinit_thesaurus_sigle")

        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_thesaurus_lingua
            ON pyarchinit_thesaurus_sigle(lingua)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_thesaurus_nome_tabella
            ON pyarchinit_thesaurus_sigle(nome_tabella)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_thesaurus_tipologia_sigla
            ON pyarchinit_thesaurus_sigle(tipologia_sigla)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_thesaurus_composite
            ON pyarchinit_thesaurus_sigle(lingua, nome_tabella, tipologia_sigla)
        """)

        conn.commit()
        print("✅ Constraints added successfully to SQLite database")
        return True

    except sqlite3.Error as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

def add_constraints_postgres(host, port, dbname, user, password):
    """Add unique constraints to PostgreSQL database."""
    print(f"Adding constraints to PostgreSQL database: {dbname}@{host}")

    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    cursor = conn.cursor()

    try:
        # Add columns if they don't exist
        cursor.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                               WHERE table_schema = 'public'
                               AND table_name = 'pyarchinit_thesaurus_sigle'
                               AND column_name = 'lingua') THEN
                    ALTER TABLE public.pyarchinit_thesaurus_sigle
                    ADD COLUMN lingua character varying(10) DEFAULT 'it';
                END IF;
            END $$;
        """)

        cursor.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                               WHERE table_schema = 'public'
                               AND table_name = 'pyarchinit_thesaurus_sigle'
                               AND column_name = 'n_tipologia') THEN
                    ALTER TABLE public.pyarchinit_thesaurus_sigle
                    ADD COLUMN n_tipologia integer;
                END IF;

                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                               WHERE table_schema = 'public'
                               AND table_name = 'pyarchinit_thesaurus_sigle'
                               AND column_name = 'n_sigla') THEN
                    ALTER TABLE public.pyarchinit_thesaurus_sigle
                    ADD COLUMN n_sigla integer;
                END IF;
            END $$;
        """)

        # Drop existing constraints if they exist
        cursor.execute("""
            ALTER TABLE public.pyarchinit_thesaurus_sigle
            DROP CONSTRAINT IF EXISTS thesaurus_unique_key;
        """)

        cursor.execute("""
            ALTER TABLE public.pyarchinit_thesaurus_sigle
            DROP CONSTRAINT IF EXISTS thesaurus_unique_sigla;
        """)

        # Add UNIQUE constraint for the main key
        cursor.execute("""
            ALTER TABLE public.pyarchinit_thesaurus_sigle
            ADD CONSTRAINT thesaurus_unique_key
            UNIQUE (lingua, nome_tabella, tipologia_sigla, sigla_estesa);
        """)

        # Add UNIQUE constraint for sigla within same context
        cursor.execute("""
            ALTER TABLE public.pyarchinit_thesaurus_sigle
            ADD CONSTRAINT thesaurus_unique_sigla
            UNIQUE (lingua, nome_tabella, tipologia_sigla, sigla);
        """)

        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_thesaurus_lingua
            ON public.pyarchinit_thesaurus_sigle(lingua);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_thesaurus_nome_tabella
            ON public.pyarchinit_thesaurus_sigle(nome_tabella);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_thesaurus_tipologia_sigla
            ON public.pyarchinit_thesaurus_sigle(tipologia_sigla);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_thesaurus_composite
            ON public.pyarchinit_thesaurus_sigle(lingua, nome_tabella, tipologia_sigla);
        """)

        # Add comment
        cursor.execute("""
            COMMENT ON TABLE public.pyarchinit_thesaurus_sigle IS
            'Thesaurus table with unique constraints on (lingua, nome_tabella, tipologia_sigla, sigla_estesa) to prevent duplicates during import';
        """)

        conn.commit()
        print("✅ Constraints added successfully to PostgreSQL database")
        return True

    except psycopg2.Error as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

def main():
    """Main function to add constraints based on user choice."""
    print("Add Unique Constraints to Thesaurus Table")
    print("=" * 60)
    print("\nThis script adds unique constraints to prevent duplicate")
    print("thesaurus records during import operations.")
    print("\nThe unique key is: (lingua, nome_tabella, tipologia_sigla, sigla_estesa)")
    print("=" * 60)

    print("\nSelect database type:")
    print("1. SQLite")
    print("2. PostgreSQL")

    choice = input("\nEnter choice (1 or 2): ")

    if choice == '1':
        # SQLite
        db_path = input("Enter SQLite database path: ")
        if not os.path.exists(db_path):
            print(f"Database not found: {db_path}")
            return 1

        if add_constraints_sqlite(db_path):
            print("\n✅ Constraints added successfully!")
        else:
            print("\n❌ Failed to add constraints.")
            return 1

    elif choice == '2':
        # PostgreSQL
        host = input("Enter PostgreSQL host (e.g., localhost): ")
        port = input("Enter PostgreSQL port (e.g., 5432): ")
        dbname = input("Enter database name: ")
        user = input("Enter username: ")
        password = input("Enter password: ")

        if add_constraints_postgres(host, port, dbname, user, password):
            print("\n✅ Constraints added successfully!")
        else:
            print("\n❌ Failed to add constraints.")
            return 1

    else:
        print("Invalid choice!")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())