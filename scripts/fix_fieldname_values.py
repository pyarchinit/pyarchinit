#!/usr/bin/env python3
"""
Script per correggere i valori dei campi che contengono erroneamente il nome del campo stesso.
Problema: alcuni campi in pyunitastratigrafiche contengono 'rilievo_originale', 'disegnatore', etc.
invece di essere NULL o vuoti.

Eseguire da QGIS Python Console o come script standalone.
"""

import sqlite3
import os


def fix_fieldname_values(db_path):
    """
    Corregge i valori dei campi che contengono il nome del campo stesso.

    Args:
        db_path: Percorso al database SQLite/Spatialite
    """

    # Campi da controllare in pyunitastratigrafiche, pyunitastratigrafiche_usm e us_table
    fields_to_fix = [
        # Campi pyunitastratigrafiche
        'rilievo_originale',
        'disegnatore',
        'data',
        'tipo_doc',
        'nome_doc',
        'coord',
        'unita_tipo_s',
        # Campi us_table
        'settore',
        'quad_par',
        'ambient',
        'saggio',
        'elem_datanti',
        'funz_statica',
        'lavorazione',
        'spess_giunti',
        'letti_posa',
        'alt_mod',
        'un_ed_riass',
        'reimp',
        'posa_opera',
        'quota_min_usm',
        'quota_max_usm',
        'cons_legante',
        'col_legante',
        'aggreg_legante',
        'con_text_mat',
        'col_materiale',
        'inclusi_materiali_usm',
        'n_catalogo_generale',
        'n_catalogo_interno',
        'n_catalogo_internazionale',
        'soprintendenza',
        'quota_relativa',
        'quota_abs',
        'ref_tm',
        'ref_ra',
        'ref_n',
        'posizione',
        'criteri_distinzione',
        'modo_formazione',
        'componenti_organici',
        'componenti_inorganici',
        'lunghezza_max',
        'altezza_max',
        'altezza_min',
        'profondita_max',
        'profondita_min',
        'larghezza_media',
        'quota_max_abs',
        'quota_max_rel',
        'quota_min_abs',
        'quota_min_rel',
        'osservazioni',
        'flottazione',
        'setacciatura',
        'affidabilita',
        'direttore_us',
        'responsabile_us',
        'cod_ente_schedatore',
        'data_rilevazione',
        'data_rielaborazione',
        'lunghezza_usm',
        'altezza_usm',
        'spessore_usm',
        'tecnica_muraria_usm',
        'modulo_usm',
        'campioni_malta_usm',
        'campioni_mattone_usm',
        'campioni_pietra_usm',
        'provenienza_materiali_usm',
        'criteri_distinzione_usm',
        'uso_primario_usm',
        # Altri campi us_table comuni
        'd_stratigrafica',
        'd_interpretativa',
        'descrizione',
        'interpretazione',
        'periodo_iniziale',
        'fase_iniziale',
        'periodo_finale',
        'fase_finale',
        'scavato',
        'attivita',
        'anno_scavo',
        'metodo_di_scavo',
        'inclusi',
        'campioni',
        'rapporti',
        'data_schedatura',
        'schedatore',
        'formazione',
        'stato_di_conservazione',
        'colore',
        'consistenza',
        'struttura',
        'documentazione',
        'datazione',
        'rapporti2',
    ]

    tables_to_fix = ['pyunitastratigrafiche', 'pyunitastratigrafiche_usm', 'us_table']

    if not os.path.exists(db_path):
        print(f"ERRORE: Database non trovato: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    total_fixed = 0

    for table in tables_to_fix:
        # Verifica se la tabella esiste
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not cursor.fetchone():
            print(f"Tabella {table} non trovata, salto...")
            continue

        # Ottieni la lista dei campi effettivamente presenti nella tabella
        cursor.execute(f"PRAGMA table_info({table})")
        existing_columns = {row[1] for row in cursor.fetchall()}

        print(f"\nProcesso tabella: {table}")

        for field in fields_to_fix:
            if field not in existing_columns:
                continue

            # Conta i record da correggere
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {field} = ?", (field,))
                count = cursor.fetchone()[0]

                if count > 0:
                    # Correggi i valori
                    cursor.execute(f"UPDATE {table} SET {field} = NULL WHERE {field} = ?", (field,))
                    print(f"  - {field}: corretti {count} record")
                    total_fixed += count
            except Exception as e:
                print(f"  - {field}: errore - {e}")

    conn.commit()
    conn.close()

    print(f"\n{'='*50}")
    print(f"Totale record corretti: {total_fixed}")
    print(f"{'='*50}")

    return True


def main():
    """Entry point per esecuzione standalone."""
    import sys

    if len(sys.argv) < 2:
        # Prova a trovare il database di default
        home = os.path.expanduser("~")
        default_path = os.path.join(home, 'pyarchinit_DB_folder', 'pyarchinit_db.sqlite')

        if os.path.exists(default_path):
            db_path = default_path
            print(f"Uso database di default: {db_path}")
        else:
            print("Uso: python fix_fieldname_values.py <percorso_database.sqlite>")
            print("Oppure assicurati che esista: ~/pyarchinit_DB_folder/pyarchinit_db.sqlite")
            sys.exit(1)
    else:
        db_path = sys.argv[1]

    fix_fieldname_values(db_path)


if __name__ == "__main__":
    main()
