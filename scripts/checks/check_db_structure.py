#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script per verificare la struttura completa dei database SQLite rispetto a PostgreSQL
"""

import sqlite3
import os

def check_table_structure(db_path, table_name):
    """Verifica la struttura di una tabella"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ottieni colonne
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    # Ottieni trigger
    cursor.execute(f"SELECT name, sql FROM sqlite_master WHERE type='trigger' AND tbl_name='{table_name}'")
    triggers = cursor.fetchall()
    
    conn.close()
    
    return columns, triggers

def check_all_databases():
    """Verifica struttura di tutti i database"""
    
    # Colonne di us_table in PostgreSQL (dal file SQL)
    postgres_us_table_columns = [
        'id_us', 'sito', 'area', 'us', 'd_stratigrafica', 'd_interpretativa', 
        'descrizione', 'interpretazione', 'periodo_iniziale', 'fase_iniziale', 
        'periodo_finale', 'fase_finale', 'scavato', 'attivita', 'anno_scavo', 
        'metodo_di_scavo', 'inclusi', 'campioni', 'rapporti', 'data_schedatura', 
        'schedatore', 'formazione', 'stato_di_conservazione', 'colore', 'consistenza', 
        'struttura', 'cont_per', 'order_layer', 'documentazione', 'unita_tipo', 
        'settore', 'quad_par', 'ambient', 'saggio', 'elem_datanti', 'funz_statica', 
        'lavorazione', 'spess_giunti', 'letti_posa', 'alt_mod', 'un_ed_riass', 
        'reimp', 'posa_opera', 'quota_min_usm', 'quota_max_usm', 'cons_legante', 
        'col_legante', 'aggreg_legante', 'con_text_mat', 'col_materiale', 
        'inclusi_materiali_usm', 'n_catalogo_generale', 'n_catalogo_interno', 
        'n_catalogo_internazionale', 'soprintendenza', 'quota_relativa', 'quota_abs', 
        'ref_tm', 'ref_ra', 'ref_n', 'posizione', 'criteri_distinzione', 
        'modo_formazione', 'componenti_organici', 'componenti_inorganici', 
        'lunghezza_max', 'altezza_max', 'altezza_min', 'profondita_max', 
        'profondita_min', 'larghezza_media', 'quota_max_abs', 'quota_max_rel', 
        'quota_min_abs', 'quota_min_rel', 'osservazioni', 'datazione', 'flottazione', 
        'setacciatura', 'affidabilita', 'direttore_us', 'responsabile_us', 
        'cod_ente_schedatore', 'data_rilevazione', 'data_rielaborazione', 
        'lunghezza_usm', 'altezza_usm', 'spessore_usm', 'tecnica_muraria_usm', 
        'modulo_usm', 'campioni_malta_usm', 'campioni_mattone_usm', 'campioni_pietra_usm', 
        'provenienza_materiali_usm', 'criteri_distinzione_usm', 'uso_primario_usm',
        'doc_usv', 'version_number', 'editing_by', 'editing_since', 
        'last_modified_by', 'last_modified_timestamp'
    ]
    
    # Altri campi aggiunti da PyArchInit
    additional_columns = [
        'epoca', 'avv_interpretazione', 'tipologia_opera', 'sezione_muraria',
        'superficie_analizzata', 'orientamento', 'materiali_lat', 'lavorazione_lat',
        'consistenza_lat', 'forma_lat', 'colore_lat', 'impasto_lat', 'forma_p',
        'colore_p', 'taglio_p', 'posa_opera_p', 'inerti_usm', 'tipo_legante_usm',
        'rifinitura_usm', 'materiale_p', 'consistenza_p', 'rapporti2',
        'organici', 'inorganici', 'quantificazioni', 'unita_edilizie', 
        'quota_min', 'quota_max'
    ]
    
    databases = [
        "/Users/enzo/pyarchinit/pyarchinit_DB_folder/ktm24.sqlite",
        "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/resources/dbfiles/pyarchinit.sqlite",
        "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/resources/dbfiles/pyarchinit_db.sqlite"
    ]
    
    print("VERIFICA STRUTTURA DATABASE RISPETTO A POSTGRESQL")
    print("="*80)
    
    for db_path in databases:
        if not os.path.exists(db_path):
            continue
            
        print(f"\n{os.path.basename(db_path)}")
        print("-"*80)
        
        # Verifica us_table
        columns, triggers = check_table_structure(db_path, 'us_table')
        sqlite_columns = [col[1] for col in columns]
        
        print(f"\nNumero colonne us_table:")
        print(f"  PostgreSQL: {len(postgres_us_table_columns)} colonne base")
        print(f"  SQLite: {len(sqlite_columns)} colonne")
        
        # Trova differenze
        missing_in_sqlite = set(postgres_us_table_columns) - set(sqlite_columns)
        extra_in_sqlite = set(sqlite_columns) - set(postgres_us_table_columns)
        
        if missing_in_sqlite:
            print(f"\n  Colonne PostgreSQL mancanti in SQLite ({len(missing_in_sqlite)}):")
            for col in sorted(missing_in_sqlite):
                print(f"    - {col}")
        
        if extra_in_sqlite:
            print(f"\n  Colonne extra in SQLite ({len(extra_in_sqlite)}):")
            for col in sorted(extra_in_sqlite):
                if col in additional_columns:
                    print(f"    + {col} (PyArchInit specific)")
                else:
                    print(f"    + {col}")
        
        # Verifica tipi di campo critici
        print(f"\n  Tipi di campo critici:")
        for col in columns:
            if col[1] in ['area', 'us', 'us_n', 'area_n']:
                print(f"    {col[1]}: {col[2]}")
        
        # Verifica trigger
        print(f"\n  Trigger trovati: {len(triggers)}")
        for trigger_name, trigger_sql in triggers:
            print(f"    - {trigger_name}")
        
        # Verifica altre tabelle importanti
        print(f"\n  Verifica struttura altre tabelle:")
        
        # pyarchinit_quote
        try:
            cols, _ = check_table_structure(db_path, 'pyarchinit_quote')
            print(f"    pyarchinit_quote: {len(cols)} colonne")
            # Verifica campo quota_q vs quota_min/quota_max
            col_names = [col[1] for col in cols]
            if 'quota_q' in col_names:
                print(f"      ✓ Ha campo quota_q (come PostgreSQL)")
            elif 'quota_min' in col_names and 'quota_max' in col_names:
                print(f"      ✗ Ha quota_min/quota_max (diverso da PostgreSQL)")
        except:
            print(f"    pyarchinit_quote: NON TROVATA")
        
        # pyunitastratigrafiche
        try:
            cols, _ = check_table_structure(db_path, 'pyunitastratigrafiche')
            col_names = [col[1] for col in cols]
            expected_cols = ['gid', 'area_s', 'scavo_s', 'us_s', 'stratigraph_index_us', 
                           'tipo_us_s', 'rilievo_originale', 'disegnatore', 'data', 
                           'tipo_doc', 'nome_doc', 'coord', 'the_geom', 'unita_tipo_s']
            missing = set(expected_cols) - set(col_names)
            if missing:
                print(f"    pyunitastratigrafiche: mancano colonne: {missing}")
            else:
                print(f"    pyunitastratigrafiche: ✓ struttura corretta")
        except:
            print(f"    pyunitastratigrafiche: NON TROVATA")
    
    print("\n" + "="*80)
    print("\nTRIGGER IN POSTGRESQL (da pyarchinit_schema_updated.sql):")
    print("  - create_geom (su pyunitastratigrafiche)")
    print("  - create_doc (su us_table)")
    print("  - delete_media_table (su media_thumb_table)")
    print("  - pottery_table_id_rep_update (su pottery_table)")
    print("  - version_us_table (su us_table) - per versionamento")
    print("\nNOTA: SQLite potrebbe non supportare tutti i trigger di PostgreSQL")

if __name__ == "__main__":
    check_all_databases()