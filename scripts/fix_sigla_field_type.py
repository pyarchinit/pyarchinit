#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per sistemare il campo sigla che è definito come CHAR(255)
invece che VARCHAR, causando spazi in eccesso
"""

import psycopg2
import sys

def fix_sigla_field(host, port, dbname, user, password):
    """Sistema il tipo del campo sigla e rimuove gli spazi."""
    print(f"Connessione a PostgreSQL: {dbname}@{host}")

    conn = psycopg2.connect(
        host=host, port=port, dbname=dbname,
        user=user, password=password
    )
    cursor = conn.cursor()

    try:
        print("\n" + "=" * 80)
        print("FIX CAMPO SIGLA NEL THESAURUS")
        print("=" * 80)

        # Controlla il tipo attuale del campo sigla
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'pyarchinit_thesaurus_sigle'
            AND column_name = 'sigla'
        """)

        result = cursor.fetchone()
        if result:
            print(f"\nTipo attuale del campo sigla: {result[1]}({result[2]})")

        # Conta record con spazi in eccesso
        cursor.execute("""
            SELECT COUNT(*)
            FROM public.pyarchinit_thesaurus_sigle
            WHERE sigla != TRIM(sigla)
        """)

        spaces_count = cursor.fetchone()[0]
        print(f"Record con spazi in eccesso nel campo sigla: {spaces_count}")

        if spaces_count > 0:
            # Mostra alcuni esempi
            cursor.execute("""
                SELECT id_thesaurus_sigle,
                       '|' || sigla || '|' as sigla_with_spaces,
                       LENGTH(sigla) as lunghezza,
                       '|' || TRIM(sigla) || '|' as sigla_trimmed,
                       LENGTH(TRIM(sigla)) as lunghezza_trimmed
                FROM public.pyarchinit_thesaurus_sigle
                WHERE sigla != TRIM(sigla)
                LIMIT 5
            """)

            print("\nEsempi di record con spazi (primi 5):")
            print(f"{'ID':<10} {'Sigla con spazi':<40} {'Len':<5} {'Sigla pulita':<20} {'Len':<5}")
            print("-" * 85)
            for row in cursor.fetchall():
                print(f"{row[0]:<10} {row[1]:<40} {row[2]:<5} {row[3]:<20} {row[4]:<5}")

        response = input("\nVuoi procedere con il fix? (s/n): ")
        if response.lower() != 's':
            print("Operazione annullata.")
            return False

        print("\n1. Rimozione spazi in eccesso...")
        cursor.execute("""
            UPDATE public.pyarchinit_thesaurus_sigle
            SET sigla = TRIM(sigla),
                sigla_estesa = TRIM(sigla_estesa),
                nome_tabella = TRIM(nome_tabella),
                tipologia_sigla = TRIM(tipologia_sigla),
                lingua = TRIM(lingua),
                descrizione = TRIM(descrizione),
                parent_sigla = TRIM(parent_sigla)
        """)

        updated = cursor.rowcount
        print(f"   ✅ Aggiornati {updated} record")

        print("\n2. Cambio tipo campo sigla da CHAR a VARCHAR...")
        cursor.execute("""
            ALTER TABLE public.pyarchinit_thesaurus_sigle
            ALTER COLUMN sigla TYPE VARCHAR(100)
        """)
        print("   ✅ Campo sigla convertito a VARCHAR(100)")

        print("\n3. Rimozione duplicati dopo la pulizia...")

        # Conta duplicati
        cursor.execute("""
            WITH duplicates AS (
                SELECT id_thesaurus_sigle,
                       ROW_NUMBER() OVER (
                           PARTITION BY
                               COALESCE(lingua, ''),
                               COALESCE(nome_tabella, ''),
                               COALESCE(tipologia_sigla, ''),
                               COALESCE(sigla, '')
                           ORDER BY id_thesaurus_sigle
                       ) AS row_num
                FROM public.pyarchinit_thesaurus_sigle
            )
            SELECT COUNT(*) FROM duplicates WHERE row_num > 1
        """)

        dup_count = cursor.fetchone()[0]

        if dup_count > 0:
            print(f"   Trovati {dup_count} duplicati dopo la pulizia")

            # Rimuovi duplicati
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
                                       COALESCE(sigla, '')
                                   ORDER BY id_thesaurus_sigle
                               ) AS row_num
                        FROM public.pyarchinit_thesaurus_sigle
                    ) t
                    WHERE t.row_num > 1
                )
            """)

            deleted = cursor.rowcount
            print(f"   ✅ Rimossi {deleted} duplicati")
        else:
            print("   ✅ Nessun duplicato trovato")

        conn.commit()
        print("\n" + "=" * 80)
        print("✅ FIX COMPLETATO CON SUCCESSO!")
        print("Ora puoi applicare i vincoli di unicità.")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n❌ Errore: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    print("=" * 80)
    print("FIX CAMPO SIGLA THESAURUS")
    print("=" * 80)
    print("\nQuesto script:")
    print("1. Rimuove gli spazi in eccesso da tutti i campi")
    print("2. Converte il campo sigla da CHAR(255) a VARCHAR(100)")
    print("3. Rimuove eventuali duplicati creati dopo la pulizia")

    print("\nConnessione PostgreSQL:")
    host = input("Host (es. localhost): ")
    port = input("Porta (es. 5432): ")
    dbname = input("Nome database: ")
    user = input("Username: ")
    password = input("Password: ")

    if fix_sigla_field(host, port, dbname, user, password):
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())