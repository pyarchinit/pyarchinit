#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per analizzare i conflitti nel campo sigla
e capire quali record hanno la stessa sigla ma sigla_estesa diversa
"""

import sqlite3
import psycopg2
import sys

def analyze_postgres(host, port, dbname, user, password):
    """Analizza conflitti sigla in PostgreSQL."""
    print(f"Connessione a PostgreSQL: {dbname}@{host}")

    conn = psycopg2.connect(
        host=host, port=port, dbname=dbname,
        user=user, password=password
    )
    cursor = conn.cursor()

    try:
        print("\n" + "=" * 120)
        print("ANALISI CONFLITTI SIGLA")
        print("=" * 120)

        # Trova sigle duplicate con sigla_estesa diversa
        cursor.execute("""
            SELECT
                lingua, nome_tabella, tipologia_sigla, sigla,
                COUNT(*) as occorrenze,
                STRING_AGG(DISTINCT sigla_estesa, ' | ' ORDER BY sigla_estesa) as sigle_estese,
                STRING_AGG(id_thesaurus_sigle::text, ', ' ORDER BY id_thesaurus_sigle) as ids
            FROM public.pyarchinit_thesaurus_sigle
            GROUP BY lingua, nome_tabella, tipologia_sigla, sigla
            HAVING COUNT(*) > 1
            ORDER BY COUNT(*) DESC, nome_tabella, tipologia_sigla, sigla
            LIMIT 30
        """)

        conflicts = cursor.fetchall()

        if not conflicts:
            print("✅ Nessun conflitto trovato nel campo sigla!")
            return True

        print(f"\n⚠️ Trovati conflitti - stessa SIGLA con SIGLA_ESTESA diversa:\n")
        print(f"{'Lingua':<7} {'Tabella':<25} {'Tipo':<7} {'Sigla':<10} {'Num':<5} {'Sigle Estese':<50} {'IDs'}")
        print("-" * 120)

        for row in conflicts:
            lingua = row[0] or 'NULL'
            tabella = (row[1] or 'NULL')[:23]
            tipo = row[2] or 'NULL'
            sigla = row[3] or 'NULL'
            count = row[4]
            estese = (row[5] or 'NULL')[:48]
            ids = row[6]

            print(f"{lingua:<7} {tabella:<25} {tipo:<7} {sigla:<10} {count:<5} {estese:<50} {ids}")

        # Mostra dettaglio per un caso specifico
        cursor.execute("""
            SELECT id_thesaurus_sigle, lingua, nome_tabella, tipologia_sigla,
                   sigla, sigla_estesa, descrizione
            FROM public.pyarchinit_thesaurus_sigle
            WHERE lingua = 'IT'
            AND nome_tabella = 'STRUTTURA'
            AND tipologia_sigla = '6.6'
            AND sigla = 'CL'
            ORDER BY id_thesaurus_sigle
        """)

        cl_records = cursor.fetchall()
        if cl_records:
            print(f"\n📋 ESEMPIO DETTAGLIATO - Record con sigla='CL':")
            print(f"{'ID':<10} {'Sigla':<10} {'Sigla Estesa':<30} {'Descrizione':<40}")
            print("-" * 90)
            for row in cl_records:
                print(f"{row[0]:<10} {row[4]:<10} {row[5]:<30} {(row[6] or '')[:38]:<40}")

        print("\n" + "=" * 120)
        print("POSSIBILI SOLUZIONI:")
        print("=" * 120)
        print("\n1. MANTENERE SOLO UN RECORD PER SIGLA (consigliato):")
        print("   - Mantiene il primo record per ogni sigla")
        print("   - Elimina gli altri anche se hanno sigla_estesa diversa")
        print("\n2. RENDERE LE SIGLE UNIVOCHE:")
        print("   - Aggiunge un suffisso numerico (es: CL, CL2, CL3)")
        print("   - Mantiene tutti i record")
        print("\n3. RIMUOVERE IL VINCOLO SULLA SIGLA:")
        print("   - Mantiene solo il vincolo su sigla_estesa")
        print("   - Permette sigle duplicate")

        return conflicts

    except Exception as e:
        print(f"\n❌ Errore: {e}")
        return None
    finally:
        conn.close()

def fix_conflicts_postgres(host, port, dbname, user, password, method='keep_first'):
    """Risolve i conflitti secondo il metodo scelto."""
    print(f"\nApplicazione fix con metodo: {method}")

    conn = psycopg2.connect(
        host=host, port=port, dbname=dbname,
        user=user, password=password
    )
    cursor = conn.cursor()

    try:
        if method == 'keep_first':
            # Mantiene solo il primo record per ogni sigla
            cursor.execute("""
                DELETE FROM public.pyarchinit_thesaurus_sigle
                WHERE id_thesaurus_sigle IN (
                    SELECT id_thesaurus_sigle
                    FROM (
                        SELECT id_thesaurus_sigle,
                               ROW_NUMBER() OVER (
                                   PARTITION BY lingua, nome_tabella, tipologia_sigla, sigla
                                   ORDER BY id_thesaurus_sigle
                               ) AS row_num
                        FROM public.pyarchinit_thesaurus_sigle
                    ) t
                    WHERE t.row_num > 1
                )
            """)

            deleted = cursor.rowcount
            conn.commit()
            print(f"✅ Rimossi {deleted} record duplicati mantenendo il primo per ogni sigla")

        elif method == 'make_unique':
            # Rende univoche le sigle aggiungendo suffissi
            cursor.execute("""
                WITH numbered AS (
                    SELECT id_thesaurus_sigle, sigla,
                           ROW_NUMBER() OVER (
                               PARTITION BY lingua, nome_tabella, tipologia_sigla, sigla
                               ORDER BY id_thesaurus_sigle
                           ) AS row_num
                    FROM public.pyarchinit_thesaurus_sigle
                )
                UPDATE public.pyarchinit_thesaurus_sigle
                SET sigla = sigla || '_' || numbered.row_num
                FROM numbered
                WHERE public.pyarchinit_thesaurus_sigle.id_thesaurus_sigle = numbered.id_thesaurus_sigle
                AND numbered.row_num > 1
            """)

            updated = cursor.rowcount
            conn.commit()
            print(f"✅ Aggiornate {updated} sigle rendendole univoche")

        elif method == 'remove_constraint':
            print("ℹ️ Per rimuovere il vincolo, non applicarlo o rimuovilo manualmente")
            print("   ALTER TABLE public.pyarchinit_thesaurus_sigle")
            print("   DROP CONSTRAINT IF EXISTS thesaurus_unique_sigla;")

        return True

    except Exception as e:
        print(f"\n❌ Errore: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    print("=" * 120)
    print("ANALISI E FIX CONFLITTI SIGLA")
    print("=" * 120)
    print("\nQuesto script analizza i casi dove record diversi hanno la stessa SIGLA")
    print("ma SIGLA_ESTESA diversa (es: CL = Colluvio, CL = Colombario)")

    print("\nConnessione PostgreSQL:")
    host = input("Host (es. localhost): ")
    port = input("Porta (es. 5432): ")
    dbname = input("Nome database: ")
    user = input("Username: ")
    password = input("Password: ")

    conflicts = analyze_postgres(host, port, dbname, user, password)

    if conflicts:
        print("\nCosa vuoi fare?")
        print("1. Mantenere solo il primo record per ogni sigla (CONSIGLIATO)")
        print("2. Rendere univoche le sigle aggiungendo suffissi")
        print("3. Non fare nulla (dovrai rimuovere il vincolo manualmente)")

        choice = input("\nScelta (1-3): ")

        if choice == '1':
            fix_conflicts_postgres(host, port, dbname, user, password, 'keep_first')
        elif choice == '2':
            fix_conflicts_postgres(host, port, dbname, user, password, 'make_unique')
        else:
            print("Nessuna modifica applicata.")

    return 0

if __name__ == "__main__":
    sys.exit(main())