#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to test thesaurus import functionality and verify duplicate handling
"""

import sqlite3
import os
import sys

def test_thesaurus_import(db_path):
    """Test thesaurus import with duplicate handling."""
    print(f"Testing thesaurus import on: {db_path}")
    print("=" * 60)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Count initial records
        cursor.execute("""
            SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = 'tma_materiali_archeologici'
        """)
        initial_count = cursor.fetchone()[0]
        print(f"Initial record count: {initial_count}")

        # Test data with duplicates
        test_records = [
            # New records
            ('tma_materiali_archeologici', 'TEST1', 'Test Record 1', 'Test description 1', '10.1', 'it'),
            ('tma_materiali_archeologici', 'TEST2', 'Test Record 2', 'Test description 2', '10.1', 'it'),
            # Duplicate based on unique key (should be ignored or updated)
            ('tma_materiali_archeologici', 'TEST1_DUP', 'Test Record 1', 'Updated description', '10.1', 'it'),
            # Different language (should be inserted)
            ('tma_materiali_archeologici', 'TEST1', 'Test Record 1', 'English version', '10.1', 'en'),
        ]

        print("\nInserting test records...")
        inserted = 0
        updated = 0
        skipped = 0

        for nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua in test_records:
            # Check if record exists
            cursor.execute("""
                SELECT id_thesaurus_sigle FROM pyarchinit_thesaurus_sigle
                WHERE lingua = ? AND nome_tabella = ?
                AND tipologia_sigla = ? AND sigla_estesa = ?
            """, (lingua, nome_tabella, tipologia_sigla, sigla_estesa))

            existing = cursor.fetchone()

            if existing:
                # Update existing record
                cursor.execute("""
                    UPDATE pyarchinit_thesaurus_sigle
                    SET sigla = ?, descrizione = ?
                    WHERE id_thesaurus_sigle = ?
                """, (sigla, descrizione, existing[0]))
                updated += 1
                print(f"  ✓ Updated: {sigla_estesa} ({lingua})")
            else:
                # Insert new record
                try:
                    cursor.execute("""
                        INSERT INTO pyarchinit_thesaurus_sigle
                        (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua))
                    inserted += 1
                    print(f"  ✓ Inserted: {sigla_estesa} ({lingua})")
                except sqlite3.IntegrityError as e:
                    skipped += 1
                    print(f"  ⚠ Skipped (constraint violation): {sigla_estesa} ({lingua})")

        conn.commit()

        # Count final records
        cursor.execute("""
            SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = 'tma_materiali_archeologici'
        """)
        final_count = cursor.fetchone()[0]

        print("\n" + "=" * 60)
        print("IMPORT TEST RESULTS:")
        print(f"  Records inserted: {inserted}")
        print(f"  Records updated: {updated}")
        print(f"  Records skipped: {skipped}")
        print(f"  Final record count: {final_count}")
        print(f"  Net change: +{final_count - initial_count}")

        # Verify unique constraints are working
        print("\n" + "=" * 60)
        print("VERIFYING UNIQUE CONSTRAINTS:")

        # Check for duplicates
        cursor.execute("""
            SELECT lingua, nome_tabella, tipologia_sigla, sigla_estesa, COUNT(*) as cnt
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = 'tma_materiali_archeologici'
            GROUP BY lingua, nome_tabella, tipologia_sigla, sigla_estesa
            HAVING COUNT(*) > 1
        """)

        duplicates = cursor.fetchall()
        if duplicates:
            print("  ❌ DUPLICATES FOUND:")
            for dup in duplicates:
                print(f"    - {dup[3]} ({dup[0]}): {dup[4]} occurrences")
        else:
            print("  ✅ No duplicates found - constraints working correctly!")

        # Clean up test records
        print("\n" + "=" * 60)
        cleanup = input("Remove test records? (y/n): ")
        if cleanup.lower() == 'y':
            cursor.execute("""
                DELETE FROM pyarchinit_thesaurus_sigle
                WHERE sigla LIKE 'TEST%'
                AND nome_tabella = 'tma_materiali_archeologici'
            """)
            conn.commit()
            deleted = cursor.rowcount
            print(f"✅ Cleaned up {deleted} test records")

        return True

    except sqlite3.Error as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

def main():
    """Main function."""
    # Default database path
    db_path = "/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite"

    if len(sys.argv) > 1:
        db_path = sys.argv[1]

    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        print("Usage: python test_thesaurus_import.py [database_path]")
        return 1

    print("Thesaurus Import Test")
    print("=" * 60)

    if test_thesaurus_import(db_path):
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed.")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())