#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to clean duplicate records from thesaurus table
before applying unique constraints
"""

import os
import sys
import sqlite3
import psycopg2
from psycopg2 import sql

def clean_duplicates_postgres(host, port, dbname, user, password):
    """Remove duplicate records from PostgreSQL thesaurus table."""
    print(f"Connecting to PostgreSQL database: {dbname}@{host}")

    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    cursor = conn.cursor()

    try:
        # Find duplicates
        print("\nSearching for duplicates...")
        cursor.execute("""
            WITH duplicates AS (
                SELECT id_thesaurus_sigle,
                       lingua, nome_tabella, tipologia_sigla, sigla_estesa,
                       ROW_NUMBER() OVER (
                           PARTITION BY lingua, nome_tabella, tipologia_sigla, sigla_estesa
                           ORDER BY id_thesaurus_sigle
                       ) AS row_num
                FROM public.pyarchinit_thesaurus_sigle
            )
            SELECT COUNT(*) FROM duplicates WHERE row_num > 1
        """)

        dup_count = cursor.fetchone()[0]

        if dup_count == 0:
            print("✅ No duplicates found!")
            return True

        print(f"⚠ Found {dup_count} duplicate records")

        # Show some examples
        cursor.execute("""
            WITH duplicates AS (
                SELECT lingua, nome_tabella, tipologia_sigla, sigla_estesa,
                       COUNT(*) as cnt
                FROM public.pyarchinit_thesaurus_sigle
                GROUP BY lingua, nome_tabella, tipologia_sigla, sigla_estesa
                HAVING COUNT(*) > 1
            )
            SELECT * FROM duplicates
            ORDER BY cnt DESC
            LIMIT 10
        """)

        print("\nTop duplicate groups:")
        print(f"{'Lingua':<10} {'Tabella':<30} {'Tipo':<10} {'Sigla Estesa':<40} {'Count':<10}")
        print("-" * 110)
        for row in cursor.fetchall():
            print(f"{row[0] or 'NULL':<10} {row[1][:28]:<30} {row[2]:<10} {row[3][:38]:<40} {row[4]:<10}")

        # Ask for confirmation
        response = input("\nDo you want to remove these duplicates? (y/n): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            return False

        # Remove duplicates
        print("\nRemoving duplicates...")
        cursor.execute("""
            DELETE FROM public.pyarchinit_thesaurus_sigle
            WHERE id_thesaurus_sigle IN (
                SELECT id_thesaurus_sigle
                FROM (
                    SELECT id_thesaurus_sigle,
                           ROW_NUMBER() OVER (
                               PARTITION BY lingua, nome_tabella, tipologia_sigla, sigla_estesa
                               ORDER BY id_thesaurus_sigle
                           ) AS row_num
                    FROM public.pyarchinit_thesaurus_sigle
                ) t
                WHERE t.row_num > 1
            )
        """)

        deleted = cursor.rowcount
        conn.commit()
        print(f"✅ Successfully removed {deleted} duplicate records")

        return True

    except psycopg2.Error as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

def clean_duplicates_sqlite(db_path):
    """Remove duplicate records from SQLite thesaurus table."""
    print(f"Cleaning duplicates from SQLite database: {db_path}")

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

        # Find duplicate groups
        print("\nSearching for duplicates...")
        cursor.execute("""
            SELECT lingua, nome_tabella, tipologia_sigla, sigla_estesa,
                   COUNT(*) as cnt
            FROM pyarchinit_thesaurus_sigle
            GROUP BY lingua, nome_tabella, tipologia_sigla, sigla_estesa
            HAVING COUNT(*) > 1
        """)

        duplicates = cursor.fetchall()

        if not duplicates:
            print("✅ No duplicates found!")
            return True

        print(f"⚠ Found {len(duplicates)} duplicate groups")

        # Show examples
        print("\nDuplicate groups:")
        print(f"{'Lingua':<10} {'Tabella':<30} {'Tipo':<10} {'Sigla Estesa':<40} {'Count':<10}")
        print("-" * 110)
        for row in duplicates[:10]:
            lingua = row[0] or 'NULL'
            tabella = (row[1] or 'NULL')[:28]
            tipo = (row[2] or 'NULL')[:8]
            sigla_estesa = (row[3] or 'NULL')[:38]
            cnt = row[4]
            print(f"{lingua:<10} {tabella:<30} {tipo:<10} {sigla_estesa:<40} {cnt:<10}")

        if len(duplicates) > 10:
            print(f"... and {len(duplicates) - 10} more groups")

        # Count total duplicate records
        cursor.execute("""
            SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle t1
            WHERE EXISTS (
                SELECT 1 FROM pyarchinit_thesaurus_sigle t2
                WHERE (t1.lingua = t2.lingua OR (t1.lingua IS NULL AND t2.lingua IS NULL))
                AND (t1.nome_tabella = t2.nome_tabella OR (t1.nome_tabella IS NULL AND t2.nome_tabella IS NULL))
                AND (t1.tipologia_sigla = t2.tipologia_sigla OR (t1.tipologia_sigla IS NULL AND t2.tipologia_sigla IS NULL))
                AND (t1.sigla_estesa = t2.sigla_estesa OR (t1.sigla_estesa IS NULL AND t2.sigla_estesa IS NULL))
                AND t1.id_thesaurus_sigle > t2.id_thesaurus_sigle
            )
        """)

        dup_count = cursor.fetchone()[0]
        print(f"\nTotal duplicate records to remove: {dup_count}")

        # Ask for confirmation
        response = input("\nDo you want to remove these duplicates? (y/n): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            return False

        # Create backup
        print("\nCreating backup table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pyarchinit_thesaurus_sigle_backup AS
            SELECT * FROM pyarchinit_thesaurus_sigle
        """)

        # Remove duplicates
        print("Removing duplicates...")
        cursor.execute("""
            DELETE FROM pyarchinit_thesaurus_sigle
            WHERE id_thesaurus_sigle NOT IN (
                SELECT MIN(id_thesaurus_sigle)
                FROM pyarchinit_thesaurus_sigle
                GROUP BY lingua, nome_tabella, tipologia_sigla, sigla_estesa
            )
        """)

        deleted = cursor.rowcount
        conn.commit()
        print(f"✅ Successfully removed {deleted} duplicate records")
        print("📋 Backup table created: pyarchinit_thesaurus_sigle_backup")

        return True

    except sqlite3.Error as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

def main():
    """Main function to clean duplicates based on user choice."""
    print("Clean Thesaurus Duplicates")
    print("=" * 60)
    print("\nThis script removes duplicate records from the thesaurus table")
    print("before applying unique constraints.")
    print("\nDuplicates are identified by:")
    print("  - lingua")
    print("  - nome_tabella")
    print("  - tipologia_sigla")
    print("  - sigla_estesa")
    print("\nThe record with the lowest ID will be kept.")
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

        if clean_duplicates_sqlite(db_path):
            print("\n✅ Cleanup completed successfully!")
        else:
            print("\n❌ Cleanup failed.")
            return 1

    elif choice == '2':
        # PostgreSQL
        host = input("Enter PostgreSQL host (e.g., localhost): ")
        port = input("Enter PostgreSQL port (e.g., 5432): ")
        dbname = input("Enter database name: ")
        user = input("Enter username: ")
        password = input("Enter password: ")

        if clean_duplicates_postgres(host, port, dbname, user, password):
            print("\n✅ Cleanup completed successfully!")
        else:
            print("\n❌ Cleanup failed.")
            return 1

    else:
        print("Invalid choice!")
        return 1

    print("\nYou can now apply unique constraints to prevent future duplicates.")
    return 0

if __name__ == "__main__":
    sys.exit(main())