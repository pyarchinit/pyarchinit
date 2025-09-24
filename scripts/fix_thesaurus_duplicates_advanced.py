#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script avanzato per rimuovere TUTTI i duplicati dal thesaurus,
inclusi quelli con campi NULL
"""

import sqlite3
import psycopg2
import sys

def analyze_and_fix_postgres(host, port, dbname, user, password):
    """Analizza e rimuove tutti i duplicati da PostgreSQL."""
    print(f"Connessione a PostgreSQL: {dbname}@{host}")

    conn = psycopg2.connect(
        host=host, port=port, dbname=dbname,
        user=user, password=password
    )
    cursor = conn.cursor()

    try:
        print("\n" + "=" * 80)
        print("ANALISI DUPLICATI NEL THESAURUS")
        print("=" * 80)

        # Mostra alcuni esempi di duplicati
        cursor.execute("""
            SELECT
                COALESCE(lingua, 'NULL') as lingua,
                COALESCE(nome_tabella, 'NULL') as nome_tabella,
                COALESCE(tipologia_sigla, 'NULL') as tipologia_sigla,
                COALESCE(sigla_estesa, 'NULL') as sigla_estesa,
                COUNT(*) as duplicates,
                MIN(id_thesaurus_sigle) as keep_id,
                STRING_AGG(id_thesaurus_sigle::text, ', ' ORDER BY id_thesaurus_sigle) as all_ids
            FROM public.pyarchinit_thesaurus_sigle
            GROUP BY
                COALESCE(lingua, 'NULL'),
                COALESCE(nome_tabella, 'NULL'),
                COALESCE(tipologia_sigla, 'NULL'),
                COALESCE(sigla_estesa, 'NULL')
            HAVING COUNT(*) > 1
            ORDER BY COUNT(*) DESC, MIN(id_thesaurus_sigle)
            LIMIT 20
        """)

        duplicates = cursor.fetchall()

        if not duplicates:
            print("✅ Nessun duplicato trovato!")
            return True

        print(f"\nTrovati gruppi di duplicati. Ecco i primi 20:\n")
        print(f"{'Lingua':<10} {'Tabella':<25} {'Tipo':<10} {'Sigla Estesa':<30} {'Copie':<8} {'IDs da rimuovere'}")
        print("-" * 120)

        for row in duplicates:
            ids_list = row[6].split(', ')
            ids_to_remove = ', '.join(ids_list[1:])  # Tutti tranne il primo
            print(f"{row[0]:<10} {row[1][:23]:<25} {row[2]:<10} {row[3][:28]:<30} {row[4]:<8} {ids_to_remove}")

        # Conta totali
        cursor.execute("""
            WITH duplicates AS (
                SELECT id_thesaurus_sigle,
                       ROW_NUMBER() OVER (
                           PARTITION BY
                               COALESCE(lingua, ''),
                               COALESCE(nome_tabella, ''),
                               COALESCE(tipologia_sigla, ''),
                               COALESCE(sigla_estesa, '')
                           ORDER BY id_thesaurus_sigle
                       ) AS row_num
                FROM public.pyarchinit_thesaurus_sigle
            )
            SELECT COUNT(*) FROM duplicates WHERE row_num > 1
        """)

        total_to_remove = cursor.fetchone()[0]

        print(f"\n{'=' * 80}")
        print(f"TOTALE RECORD DA RIMUOVERE: {total_to_remove}")
        print(f"{'=' * 80}")

        response = input("\nVuoi rimuovere TUTTI questi duplicati? (s/n): ")
        if response.lower() != 's':
            print("Operazione annullata.")
            return False

        print("\nRimozione duplicati in corso...")

        # RIMOZIONE EFFETTIVA
        cursor.execute("""
            DELETE FROM public.pyarchinit_thesaurus_sigle
            WHERE id_thesaurus_sigle IN (
                SELECT id_thesaurus_sigle
                FROM (
                    SELECT id_thesaurus_sigle,
                           ROW_NUMBER() OVER (
                               PARTITION BY
                                   COALESCE(lingua, ''),
                                   COALESCE(nome_tabella, ''),
                                   COALESCE(tipologia_sigla, ''),
                                   COALESCE(sigla_estesa, '')
                               ORDER BY id_thesaurus_sigle
                           ) AS row_num
                    FROM public.pyarchinit_thesaurus_sigle
                ) t
                WHERE t.row_num > 1
            )
        """)

        removed = cursor.rowcount

        # Verifica
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT 1
                FROM public.pyarchinit_thesaurus_sigle
                GROUP BY
                    COALESCE(lingua, ''),
                    COALESCE(nome_tabella, ''),
                    COALESCE(tipologia_sigla, ''),
                    COALESCE(sigla_estesa, '')
                HAVING COUNT(*) > 1
            ) t
        """)

        remaining = cursor.fetchone()[0]

        if remaining == 0:
            conn.commit()
            print(f"\n✅ SUCCESSO! Rimossi {removed} record duplicati.")
            print("   Ora puoi applicare i vincoli di unicità.")
        else:
            conn.rollback()
            print(f"\n⚠️ ATTENZIONE: Ancora {remaining} gruppi di duplicati presenti!")
            print("   Operazione annullata.")
            return False

        return True

    except Exception as e:
        print(f"\n❌ Errore: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def analyze_and_fix_sqlite(db_path):
    """Analizza e rimuove tutti i duplicati da SQLite."""
    print(f"Apertura database SQLite: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("\n" + "=" * 80)
        print("ANALISI DUPLICATI NEL THESAURUS")
        print("=" * 80)

        # Mostra alcuni esempi di duplicati come nel tuo caso
        cursor.execute("""
            SELECT
                COALESCE(lingua, 'NULL') as lingua,
                COALESCE(nome_tabella, 'NULL') as nome_tabella,
                COALESCE(tipologia_sigla, 'NULL') as tipologia_sigla,
                COALESCE(sigla_estesa, 'NULL') as sigla_estesa,
                COUNT(*) as duplicates,
                MIN(id_thesaurus_sigle) as keep_id,
                GROUP_CONCAT(id_thesaurus_sigle, ', ') as all_ids
            FROM pyarchinit_thesaurus_sigle
            GROUP BY
                COALESCE(lingua, ''),
                COALESCE(nome_tabella, ''),
                COALESCE(tipologia_sigla, ''),
                COALESCE(sigla_estesa, '')
            HAVING COUNT(*) > 1
            ORDER BY COUNT(*) DESC, MIN(id_thesaurus_sigle)
            LIMIT 20
        """)

        duplicates = cursor.fetchall()

        if not duplicates:
            print("✅ Nessun duplicato trovato!")
            return True

        print(f"\nTrovati gruppi di duplicati. Ecco i primi 20:\n")
        print(f"{'Lingua':<10} {'Tabella':<25} {'Tipo':<10} {'Sigla Estesa':<30} {'Copie':<8} {'IDs'}")
        print("-" * 120)

        for row in duplicates:
            print(f"{row[0]:<10} {row[1][:23]:<25} {row[2]:<10} {row[3][:28]:<30} {row[4]:<8} {row[6]}")

        # Conta totali
        cursor.execute("""
            SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle
            WHERE id_thesaurus_sigle NOT IN (
                SELECT MIN(id_thesaurus_sigle)
                FROM pyarchinit_thesaurus_sigle
                GROUP BY
                    COALESCE(lingua, ''),
                    COALESCE(nome_tabella, ''),
                    COALESCE(tipologia_sigla, ''),
                    COALESCE(sigla_estesa, '')
            )
        """)

        total_to_remove = cursor.fetchone()[0]

        print(f"\n{'=' * 80}")
        print(f"TOTALE RECORD DA RIMUOVERE: {total_to_remove}")
        print(f"{'=' * 80}")

        # Mostra esempio specifico come quello fornito dall'utente
        cursor.execute("""
            SELECT id_thesaurus_sigle, nome_tabella, sigla, sigla_estesa,
                   descrizione, tipologia_sigla, lingua
            FROM pyarchinit_thesaurus_sigle
            WHERE nome_tabella = 'INVENTARIO MATERIALI'
            AND sigla = 'BR'
            AND sigla_estesa = 'Brocca'
            ORDER BY id_thesaurus_sigle
        """)

        brocche = cursor.fetchall()
        if len(brocche) > 1:
            print(f"\nESEMPIO - Record 'Brocca' trovati: {len(brocche)}")
            print("IDs:", ', '.join(str(b[0]) for b in brocche))
            print(f"Verrà mantenuto solo ID: {brocche[0][0]}")

        response = input("\nVuoi rimuovere TUTTI questi duplicati? (s/n): ")
        if response.lower() != 's':
            print("Operazione annullata.")
            return False

        # Backup
        print("\nCreazione backup...")
        cursor.execute("DROP TABLE IF EXISTS pyarchinit_thesaurus_sigle_backup")
        cursor.execute("""
            CREATE TABLE pyarchinit_thesaurus_sigle_backup AS
            SELECT * FROM pyarchinit_thesaurus_sigle
        """)

        print("Rimozione duplicati in corso...")

        # RIMOZIONE EFFETTIVA - mantiene solo il record con ID minimo per ogni gruppo
        cursor.execute("""
            DELETE FROM pyarchinit_thesaurus_sigle
            WHERE id_thesaurus_sigle NOT IN (
                SELECT MIN(id_thesaurus_sigle)
                FROM pyarchinit_thesaurus_sigle
                GROUP BY
                    COALESCE(lingua, ''),
                    COALESCE(nome_tabella, ''),
                    COALESCE(tipologia_sigla, ''),
                    COALESCE(sigla_estesa, '')
            )
        """)

        removed = cursor.rowcount

        # Verifica
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT 1
                FROM pyarchinit_thesaurus_sigle
                GROUP BY
                    COALESCE(lingua, ''),
                    COALESCE(nome_tabella, ''),
                    COALESCE(tipologia_sigla, ''),
                    COALESCE(sigla_estesa, '')
                HAVING COUNT(*) > 1
            )
        """)

        remaining = cursor.fetchone()[0]

        if remaining == 0:
            conn.commit()
            print(f"\n✅ SUCCESSO! Rimossi {removed} record duplicati.")
            print("   Backup salvato in: pyarchinit_thesaurus_sigle_backup")
            print("   Ora puoi applicare i vincoli di unicità.")
        else:
            conn.rollback()
            print(f"\n⚠️ ATTENZIONE: Ancora {remaining} gruppi di duplicati presenti!")
            print("   Operazione annullata. Backup non modificato.")
            return False

        return True

    except Exception as e:
        print(f"\n❌ Errore: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    print("=" * 80)
    print("PULIZIA AVANZATA DUPLICATI THESAURUS")
    print("=" * 80)
    print("\nQuesto script rimuove TUTTI i duplicati, inclusi quelli con campi NULL")
    print("La chiave di unicità è: (lingua, nome_tabella, tipologia_sigla, sigla_estesa)")
    print("Viene mantenuto solo il record con ID più basso per ogni gruppo.")

    print("\nSeleziona il tipo di database:")
    print("1. SQLite")
    print("2. PostgreSQL")

    choice = input("\nScelta (1 o 2): ")

    if choice == '1':
        import os
        db_path = input("Percorso database SQLite: ")
        if not os.path.exists(db_path):
            print(f"Database non trovato: {db_path}")
            return 1

        if analyze_and_fix_sqlite(db_path):
            return 0
        else:
            return 1

    elif choice == '2':
        host = input("Host PostgreSQL (es. localhost): ")
        port = input("Porta PostgreSQL (es. 5432): ")
        dbname = input("Nome database: ")
        user = input("Username: ")
        password = input("Password: ")

        if analyze_and_fix_postgres(host, port, dbname, user, password):
            return 0
        else:
            return 1
    else:
        print("Scelta non valida!")
        return 1

if __name__ == "__main__":
    sys.exit(main())