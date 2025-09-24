#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per pulire i duplicati nel database SORGENTE prima dell'export/import
"""

import sqlite3
import psycopg2
import sys

def clean_source_database(db_type, conn_params):
    """Pulisce i duplicati nel database sorgente."""

    if db_type == 'postgres':
        conn = psycopg2.connect(**conn_params)
    else:
        conn = sqlite3.connect(conn_params['database'])

    cursor = conn.cursor()

    try:
        print("\n" + "=" * 80)
        print("PULIZIA DATABASE SORGENTE")
        print("=" * 80)

        # 1. Pulisci spazi
        print("\n1. Pulizia spazi in eccesso...")
        if db_type == 'postgres':
            cursor.execute("""
                UPDATE pyarchinit_thesaurus_sigle
                SET lingua = TRIM(lingua),
                    nome_tabella = TRIM(nome_tabella),
                    tipologia_sigla = TRIM(tipologia_sigla),
                    sigla = TRIM(sigla),
                    sigla_estesa = TRIM(sigla_estesa),
                    descrizione = TRIM(descrizione),
                    parent_sigla = TRIM(parent_sigla)
                WHERE lingua != TRIM(lingua)
                   OR nome_tabella != TRIM(nome_tabella)
                   OR tipologia_sigla != TRIM(tipologia_sigla)
                   OR sigla != TRIM(sigla)
                   OR sigla_estesa != TRIM(sigla_estesa)
            """)
        else:
            cursor.execute("""
                UPDATE pyarchinit_thesaurus_sigle
                SET lingua = TRIM(lingua),
                    nome_tabella = TRIM(nome_tabella),
                    tipologia_sigla = TRIM(tipologia_sigla),
                    sigla = TRIM(sigla),
                    sigla_estesa = TRIM(sigla_estesa),
                    descrizione = TRIM(descrizione),
                    parent_sigla = TRIM(parent_sigla)
            """)

        trimmed = cursor.rowcount
        print(f"   ✅ Puliti {trimmed} record con spazi")

        # 2. Trova duplicati esatti
        print("\n2. Ricerca duplicati esatti (stessa chiave univoca)...")

        if db_type == 'postgres':
            cursor.execute("""
                SELECT lingua, nome_tabella, tipologia_sigla, sigla_estesa,
                       COUNT(*) as cnt,
                       STRING_AGG(id_thesaurus_sigle::text, ', ' ORDER BY id_thesaurus_sigle) as ids
                FROM pyarchinit_thesaurus_sigle
                GROUP BY lingua, nome_tabella, tipologia_sigla, sigla_estesa
                HAVING COUNT(*) > 1
                ORDER BY COUNT(*) DESC
                LIMIT 20
            """)
        else:
            cursor.execute("""
                SELECT lingua, nome_tabella, tipologia_sigla, sigla_estesa,
                       COUNT(*) as cnt,
                       GROUP_CONCAT(id_thesaurus_sigle, ', ') as ids
                FROM pyarchinit_thesaurus_sigle
                GROUP BY lingua, nome_tabella, tipologia_sigla, sigla_estesa
                HAVING COUNT(*) > 1
                ORDER BY COUNT(*) DESC
                LIMIT 20
            """)

        duplicates = cursor.fetchall()

        if duplicates:
            print(f"\n   ⚠️ Trovati {len(duplicates)} gruppi di duplicati:")
            print(f"   {'Lingua':<7} {'Tabella':<20} {'Tipo':<7} {'Sigla Estesa':<30} {'Copie':<6} {'IDs'}")
            print("   " + "-" * 90)

            for row in duplicates[:10]:
                lingua = (row[0] or 'NULL')[:7]
                tabella = (row[1] or 'NULL')[:18]
                tipo = (row[2] or 'NULL')[:7]
                sigla_est = (row[3] or 'NULL')[:28]
                cnt = row[4]
                ids = row[5][:30] + ('...' if len(row[5]) > 30 else '')
                print(f"   {lingua:<7} {tabella:<20} {tipo:<7} {sigla_est:<30} {cnt:<6} {ids}")

            # Rimuovi duplicati
            response = input("\n   Rimuovere questi duplicati? (s/n): ")

            if response.lower() == 's':
                if db_type == 'postgres':
                    cursor.execute("""
                        DELETE FROM pyarchinit_thesaurus_sigle
                        WHERE id_thesaurus_sigle IN (
                            SELECT id_thesaurus_sigle
                            FROM (
                                SELECT id_thesaurus_sigle,
                                       ROW_NUMBER() OVER (
                                           PARTITION BY lingua, nome_tabella, tipologia_sigla, sigla_estesa
                                           ORDER BY id_thesaurus_sigle
                                       ) AS row_num
                                FROM pyarchinit_thesaurus_sigle
                            ) t
                            WHERE t.row_num > 1
                        )
                    """)
                else:
                    cursor.execute("""
                        DELETE FROM pyarchinit_thesaurus_sigle
                        WHERE id_thesaurus_sigle NOT IN (
                            SELECT MIN(id_thesaurus_sigle)
                            FROM pyarchinit_thesaurus_sigle
                            GROUP BY lingua, nome_tabella, tipologia_sigla, sigla_estesa
                        )
                    """)

                deleted = cursor.rowcount
                print(f"   ✅ Rimossi {deleted} record duplicati")
        else:
            print("   ✅ Nessun duplicato trovato")

        # 3. Conta record totali
        cursor.execute("SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle")
        total = cursor.fetchone()[0]

        print("\n" + "=" * 80)
        print(f"RIEPILOGO:")
        print(f"- Record totali nel thesaurus: {total}")
        print(f"- Spazi puliti: {trimmed}")
        if duplicates and response.lower() == 's':
            print(f"- Duplicati rimossi: {deleted}")
        print("\n✅ Database sorgente pronto per l'export!")
        print("=" * 80)

        conn.commit()
        return True

    except Exception as e:
        print(f"\n❌ Errore: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

def main():
    print("=" * 80)
    print("PULIZIA THESAURUS NEL DATABASE SORGENTE")
    print("=" * 80)
    print("\nQuesto script pulisce i duplicati nel database SORGENTE")
    print("PRIMA di fare l'export/import verso un altro database.")
    print("\n⚠️  IMPORTANTE: Usa questo sul database DA CUI esporti i dati!")

    print("\nTipo di database sorgente:")
    print("1. PostgreSQL")
    print("2. SQLite")

    db_type = input("\nScelta (1 o 2): ")

    if db_type == '1':
        conn_params = {
            'host': input("Host (es. localhost): "),
            'port': input("Porta (es. 5432): "),
            'database': input("Nome database: "),
            'user': input("Username: "),
            'password': input("Password: ")
        }

        if clean_source_database('postgres', conn_params):
            print("\n✅ Pulizia completata! Ora puoi esportare i dati.")
        else:
            print("\n❌ Pulizia fallita.")
            return 1

    elif db_type == '2':
        import os
        db_path = input("Percorso database SQLite: ")

        if not os.path.exists(db_path):
            print(f"Database non trovato: {db_path}")
            return 1

        conn_params = {'database': db_path}

        if clean_source_database('sqlite', conn_params):
            print("\n✅ Pulizia completata! Ora puoi esportare i dati.")
        else:
            print("\n❌ Pulizia fallita.")
            return 1

    else:
        print("Scelta non valida!")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())