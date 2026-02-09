#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script completo per sistemare tutti i database PyArchInit
Corregge i tipi di campo e le geometrie in tutti i database
"""

import sqlite3
import os
from datetime import datetime
import shutil

def fix_database_complete(db_path):
    """Sistema completamente un database PyArchInit"""
    
    print(f"\n{'='*60}")
    print(f"Correzione completa: {os.path.basename(db_path)}")
    print(f"{'='*60}\n")
    
    # Crea backup
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    print(f"✓ Backup creato: {os.path.basename(backup_path)}\n")
    
    conn = sqlite3.connect(db_path)
    conn.enable_load_extension(True)
    
    # Carica spatialite
    spatialite_loaded = False
    try:
        conn.load_extension("mod_spatialite")
        spatialite_loaded = True
    except:
        try:
            conn.load_extension("mod_spatialite.so")
            spatialite_loaded = True
        except:
            print("⚠ Spatialite non caricato - alcune funzioni geometriche potrebbero non funzionare")
    
    cursor = conn.cursor()
    
    # Disabilita constraints per permettere modifiche
    cursor.execute("PRAGMA foreign_keys = OFF")
    cursor.execute("PRAGMA legacy_alter_table = ON")
    
    # 1. RIPRISTINO TABELLE MANCANTI
    print("1. Ripristino tabelle mancanti dai backup...")
    tables_to_restore = [
        'inventario_materiali_table',
        'pottery_table', 
        'pyarchinit_us_negative_doc',
        'tomba_table'
    ]
    
    for table_name in tables_to_restore:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not cursor.fetchone():
            # Cerca backup più recente
            cursor.execute(f"""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name LIKE '{table_name}_backup_%'
                ORDER BY name DESC LIMIT 1
            """)
            backup = cursor.fetchone()
            if backup:
                try:
                    cursor.execute(f"CREATE TABLE {table_name} AS SELECT * FROM {backup[0]}")
                    print(f"   ✓ Ripristinata {table_name}")
                except Exception as e:
                    print(f"   ✗ Errore ripristinando {table_name}: {e}")
    
    # 2. CORREZIONE TIPI DI CAMPO
    print("\n2. Correzione tipi di campo...")
    
    # Lista tabelle e campi da correggere
    field_corrections = {
        'tomba_table': [('area', 'TEXT')],
        'inventario_materiali_table': [('area', 'TEXT'), ('us', 'TEXT')],
        'pottery_table': [('area', 'TEXT'), ('us', 'TEXT')],
        'campioni_table': [('area', 'TEXT'), ('us', 'TEXT')],
        'documentazione_table': [('area', 'TEXT'), ('us', 'TEXT')],
        'lineeriferimento_table': [('area', 'TEXT'), ('us', 'TEXT')],
        'ripartizioni_spaziali_table': [('area', 'TEXT'), ('us', 'TEXT')],
        'struttura_table': [('area', 'TEXT'), ('us', 'TEXT')]
    }
    
    for table_name, corrections in field_corrections.items():
        if not table_exists(cursor, table_name):
            continue
            
        needs_fix = False
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # Verifica se servono correzioni
        for field_name, expected_type in corrections:
            for col in columns:
                if col[1] == field_name and col[2] != expected_type:
                    needs_fix = True
                    break
        
        if needs_fix:
            print(f"\n   Correzione {table_name}...")
            try:
                # Crea nuova tabella con tipi corretti
                new_table_sql = generate_corrected_table_sql(cursor, table_name, corrections)
                if new_table_sql:
                    # Crea tabella temporanea
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name}_new")
                    cursor.execute(new_table_sql)
                    
                    # Copia dati
                    col_names = [col[1] for col in columns]
                    cursor.execute(f"""
                        INSERT INTO {table_name}_new ({', '.join(col_names)})
                        SELECT {', '.join(col_names)} FROM {table_name}
                    """)
                    
                    # Sostituisci tabella
                    cursor.execute(f"DROP TABLE {table_name}")
                    cursor.execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name}")
                    
                    print(f"   ✓ Corretti campi in {table_name}")
            except Exception as e:
                print(f"   ✗ Errore correggendo {table_name}: {e}")
    
    # 3. RICREAZIONE VIEW CORRETTE
    print("\n3. Ricreazione view senza CAST...")
    
    view_definitions = [
        ('pyarchinit_quote', '''
            CREATE VIEW pyarchinit_quote AS
            SELECT 
                sito,
                area,
                us,
                unita_tipo,
                quota_min,
                quota_max,
                the_geom
            FROM us_table
            WHERE quota_min IS NOT NULL OR quota_max IS NOT NULL
        '''),
        ('pyarchinit_quote_usm', '''
            CREATE VIEW pyarchinit_quote_usm AS
            SELECT 
                sito,
                area,
                us,
                unita_tipo,
                quota_min_usm,
                quota_max_usm,
                the_geom
            FROM us_table
            WHERE unita_tipo = 'USM' AND (quota_min_usm IS NOT NULL OR quota_max_usm IS NOT NULL)
        '''),
        ('pyunitastratigrafiche', '''
            CREATE VIEW pyunitastratigrafiche AS
            SELECT 
                id_us,
                sito,
                area,
                us,
                d_stratigrafica,
                d_interpretativa,
                descrizione,
                interpretazione,
                periodo_iniziale,
                fase_iniziale,
                periodo_finale,
                fase_finale,
                scavato,
                attivita,
                anno_scavo,
                metodo_di_scavo,
                inclusi,
                campioni,
                rapporti,
                organici,
                inorganici,
                data_schedatura,
                schedatore,
                formazione,
                stato_di_conservazione,
                colore,
                consistenza,
                struttura,
                cont_per,
                order_layer,
                documentazione,
                unita_tipo,
                settore,
                quad_par,
                ambient,
                saggio,
                elem_datanti,
                funz_statica,
                lavorazione,
                spess_giunti,
                letti_posa,
                alt_mod,
                un_ed_riass,
                reimp,
                posa_opera,
                quota_min_usm,
                quota_max_usm,
                cons_legante,
                col_legante,
                aggreg_legante,
                con_text_mat,
                col_materiale,
                inclusi_materiali_usm,
                n_catalogo_generale,
                n_catalogo_interno,
                n_catalogo_internazionale,
                soprintendenza,
                quota_relativa,
                quota_abs,
                ref_tm,
                ref_ra,
                ref_n,
                posizione,
                criteri_distinzione,
                modo_formazione,
                componenti_organici,
                componenti_inorganici,
                lunghezza_max,
                altezza_max,
                altezza_min,
                profondita_max,
                profondita_min,
                larghezza_media,
                quota_max_abs,
                quota_max_rel,
                quota_min_abs,
                quota_min_rel,
                osservazioni,
                datazione,
                flottazione,
                setacciatura,
                affidabilita,
                direttore_us,
                responsabile_us,
                cod_ente_schedatore,
                data_rilevazione,
                data_rielaborazione,
                lunghezza_usm,
                altezza_usm,
                spessore_usm,
                tecnica_muraria_usm,
                modulo_usm,
                campioni_malta_usm,
                campioni_mattone_usm,
                campioni_pietra_usm,
                provenienza_materiali_usm,
                criteri_distinzione_usm,
                uso_primario_usm,
                tipologia_opera,
                sezione_muraria,
                superficie_analizzata,
                orientamento,
                materiali_lat,
                lavorazione_lat,
                consistenza_lat,
                forma_lat,
                colore_lat,
                impasto_lat,
                forma_p,
                colore_p,
                taglio_p,
                posa_opera_p,
                inerti_usm,
                tipo_legante_usm,
                rifinitura_usm,
                materiale_p,
                consistenza_p,
                rapporti2,
                doc_usv,
                the_geom,
                epoca
            FROM us_table
            WHERE unita_tipo = 'US'
        '''),
        ('pyunitastratigrafiche_usm', '''
            CREATE VIEW pyunitastratigrafiche_usm AS
            SELECT 
                id_us,
                sito,
                area,
                us,
                unita_tipo,
                d_stratigrafica,
                d_interpretativa,
                descrizione,
                interpretazione,
                periodo_iniziale,
                fase_iniziale,
                periodo_finale,
                fase_finale,
                scavato,
                attivita,
                anno_scavo,
                metodo_di_scavo,
                inclusi,
                campioni,
                rapporti,
                organici,
                inorganici,
                data_schedatura,
                schedatore,
                formazione,
                stato_di_conservazione,
                colore,
                consistenza,
                struttura,
                cont_per,
                order_layer,
                documentazione,
                settore,
                quad_par,
                ambient,
                saggio,
                elem_datanti,
                funz_statica,
                lavorazione,
                spess_giunti,
                letti_posa,
                alt_mod,
                un_ed_riass,
                reimp,
                posa_opera,
                quota_min_usm,
                quota_max_usm,
                cons_legante,
                col_legante,
                aggreg_legante,
                con_text_mat,
                col_materiale,
                inclusi_materiali_usm,
                n_catalogo_generale,
                n_catalogo_interno,
                n_catalogo_internazionale,
                soprintendenza,
                quota_relativa,
                quota_abs,
                ref_tm,
                ref_ra,
                ref_n,
                posizione,
                criteri_distinzione,
                modo_formazione,
                componenti_organici,
                componenti_inorganici,
                lunghezza_max,
                altezza_max,
                altezza_min,
                profondita_max,
                profondita_min,
                larghezza_media,
                quota_max_abs,
                quota_max_rel,
                quota_min_abs,
                quota_min_rel,
                osservazioni,
                datazione,
                flottazione,
                setacciatura,
                affidabilita,
                direttore_us,
                responsabile_us,
                cod_ente_schedatore,
                data_rilevazione,
                data_rielaborazione,
                lunghezza_usm,
                altezza_usm,
                spessore_usm,
                tecnica_muraria_usm,
                modulo_usm,
                campioni_malta_usm,
                campioni_mattone_usm,
                campioni_pietra_usm,
                provenienza_materiali_usm,
                criteri_distinzione_usm,
                uso_primario_usm,
                tipologia_opera,
                sezione_muraria,
                superficie_analizzata,
                orientamento,
                materiali_lat,
                lavorazione_lat,
                consistenza_lat,
                forma_lat,
                colore_lat,
                impasto_lat,
                forma_p,
                colore_p,
                taglio_p,
                posa_opera_p,
                inerti_usm,
                tipo_legante_usm,
                rifinitura_usm,
                materiale_p,
                consistenza_p,
                rapporti2,
                doc_usv,
                the_geom,
                epoca
            FROM us_table
            WHERE unita_tipo = 'USM'
        ''')
    ]
    
    for view_name, create_sql in view_definitions:
        try:
            # Drop esistente (tabella o view)
            cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
            cursor.execute(f"DROP TABLE IF EXISTS {view_name}")
            
            # Ricrea come view
            cursor.execute(create_sql)
            print(f"   ✓ Creata/ricreata view {view_name}")
        except Exception as e:
            print(f"   ✗ Errore con view {view_name}: {e}")
    
    # 4. REGISTRAZIONE GEOMETRIE (se spatialite è caricato)
    if spatialite_loaded:
        print("\n4. Registrazione colonne geometriche...")
        
        # Ottieni SRID
        cursor.execute("SELECT srid FROM geometry_columns LIMIT 1")
        result = cursor.fetchone()
        srid = result[0] if result else 3004
        
        geometry_tables = {
            'pyunitastratigrafiche': ('the_geom', 'MULTIPOLYGON'),
            'pyunitastratigrafiche_usm': ('the_geom', 'MULTIPOLYGON'),
            'pyarchinit_quote': ('the_geom', 'POINT'),
            'pyarchinit_quote_usm': ('the_geom', 'POINT'),
            'pyarchinit_us_negative_doc': ('the_geom', 'MULTIPOLYGON')
        }
        
        for table_name, (geom_col, geom_type) in geometry_tables.items():
            if table_exists(cursor, table_name):
                # Verifica se già registrata
                cursor.execute(f"""
                    SELECT * FROM geometry_columns 
                    WHERE f_table_name = '{table_name}' AND f_geometry_column = '{geom_col}'
                """)
                
                if not cursor.fetchone():
                    try:
                        cursor.execute(f"SELECT RecoverGeometryColumn('{table_name}', '{geom_col}', {srid}, '{geom_type}', 'XY')")
                        print(f"   ✓ Registrata {table_name}.{geom_col}")
                    except:
                        pass
    
    # Riabilita constraints
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("PRAGMA legacy_alter_table = OFF")
    
    # Commit
    conn.commit()
    
    # 5. VERIFICA FINALE
    print("\n5. Verifica finale...")
    verify_database(cursor)
    
    conn.close()
    
    print(f"\n{'='*60}")
    print("✓ Correzione completata!")
    print(f"{'='*60}")
    
    return True


def table_exists(cursor, table_name):
    """Verifica se una tabella esiste"""
    cursor.execute(f"""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='{table_name}'
    """)
    return cursor.fetchone() is not None


def generate_corrected_table_sql(cursor, table_name, corrections):
    """Genera SQL per creare tabella con tipi corretti"""
    # Ottieni SQL originale
    cursor.execute(f"""
        SELECT sql FROM sqlite_master 
        WHERE type='table' AND name='{table_name}'
    """)
    result = cursor.fetchone()
    if not result:
        return None
    
    original_sql = result[0]
    
    # Applica correzioni
    corrected_sql = original_sql.replace(table_name, f"{table_name}_new", 1)
    
    for field_name, new_type in corrections:
        # Pattern per trovare definizioni di campo
        patterns = [
            f"{field_name} INTEGER",
            f"{field_name} INT",
            f"{field_name} REAL",
            f"{field_name} NUMERIC",
            f"{field_name} NUMBER"
        ]
        
        for pattern in patterns:
            if pattern in corrected_sql:
                corrected_sql = corrected_sql.replace(pattern, f"{field_name} {new_type}")
                break
    
    return corrected_sql


def verify_database(cursor):
    """Verifica lo stato finale del database"""
    # Verifica campi area/us
    tables_to_check = ['tomba_table', 'inventario_materiali_table', 'pottery_table', 'us_table']
    
    for table in tables_to_check:
        if table_exists(cursor, table):
            cursor.execute(f"PRAGMA table_info({table})")
            for col in cursor.fetchall():
                if col[1] in ['area', 'us']:
                    status = "✓" if col[2] == 'TEXT' else "✗"
                    print(f"   {status} {table}.{col[1]}: {col[2]}")
    
    # Verifica view
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
    views = cursor.fetchall()
    for view in views:
        view_name = view[0]
        if view_name.startswith('pyarchinit_') or view_name.startswith('pyunita'):
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='view' AND name='{view_name}'")
            sql = cursor.fetchone()[0]
            if 'CAST' in sql.upper():
                print(f"   ⚠ View {view_name} contiene CAST")
            else:
                print(f"   ✓ View {view_name} OK (no CAST)")


def process_all_databases():
    """Processa tutti i database necessari"""
    databases = [
        "/Users/enzo/pyarchinit/pyarchinit_DB_folder/ktm24.sqlite",
        "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/resources/dbfiles/pyarchinit.sqlite",
        "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/resources/dbfiles/pyarchinit_db.sqlite"
    ]
    
    for db_path in databases:
        if os.path.exists(db_path):
            try:
                fix_database_complete(db_path)
            except Exception as e:
                print(f"\n✗ Errore processando {os.path.basename(db_path)}: {e}")
        else:
            print(f"\n⚠ Database non trovato: {db_path}")


if __name__ == "__main__":
    process_all_databases()