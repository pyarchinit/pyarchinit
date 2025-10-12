#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script finale per allineare completamente SQLite con PostgreSQL
Corregge pyunitastratigrafiche, pyunitastratigrafiche_usm e pyarchinit_us_negative_doc
"""

import sqlite3
import os
from datetime import datetime

def final_postgres_alignment(db_path):
    """Allineamento finale con PostgreSQL"""
    
    print(f"\n{'='*60}")
    print(f"ALLINEAMENTO FINALE CON POSTGRESQL: {os.path.basename(db_path)}")
    print(f"{'='*60}\n")
    
    # Backup
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    import shutil
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
            pass
    
    cursor = conn.cursor()
    
    # Disabilita constraints
    cursor.execute("PRAGMA foreign_keys = OFF")
    cursor.execute("PRAGMA triggers = OFF")
    
    # 1. CORREGGI pyunitastratigrafiche e pyunitastratigrafiche_usm
    print("1. Correzione pyunitastratigrafiche...")
    
    # Drop view se esistono
    cursor.execute("DROP VIEW IF EXISTS pyunitastratigrafiche")
    cursor.execute("DROP VIEW IF EXISTS pyunitastratigrafiche_usm")
    
    # Drop tabelle esistenti
    cursor.execute("DROP TABLE IF EXISTS pyunitastratigrafiche")
    cursor.execute("DROP TABLE IF EXISTS pyunitastratigrafiche_usm")
    
    # Crea tabelle come in PostgreSQL
    cursor.execute("""
        CREATE TABLE pyunitastratigrafiche (
            gid INTEGER PRIMARY KEY AUTOINCREMENT,
            area_s TEXT,
            scavo_s TEXT,
            us_s TEXT,
            stratigraph_index_us INTEGER,
            tipo_us_s TEXT,
            rilievo_originale TEXT,
            disegnatore TEXT,
            data DATE,
            tipo_doc TEXT,
            nome_doc TEXT,
            coord TEXT,
            the_geom BLOB,
            unita_tipo_s TEXT
        )
    """)
    print("   ✓ Creata tabella pyunitastratigrafiche")
    
    cursor.execute("""
        CREATE TABLE pyunitastratigrafiche_usm (
            gid INTEGER PRIMARY KEY AUTOINCREMENT,
            area_s TEXT,
            scavo_s TEXT,
            us_s TEXT,
            stratigraph_index_us INTEGER,
            tipo_us_s TEXT,
            rilievo_originale TEXT,
            disegnatore TEXT,
            data DATE,
            tipo_doc TEXT,
            nome_doc TEXT,
            coord TEXT,
            the_geom BLOB,
            unita_tipo_s TEXT
        )
    """)
    print("   ✓ Creata tabella pyunitastratigrafiche_usm")
    
    # 2. CORREGGI pyarchinit_us_negative_doc
    print("\n2. Correzione pyarchinit_us_negative_doc...")
    
    # Verifica se esiste e che tipo di campo us_n ha
    table_exists = False
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pyarchinit_us_negative_doc'")
    if cursor.fetchone():
        table_exists = True
        cursor.execute("PRAGMA table_info(pyarchinit_us_negative_doc)")
        columns = cursor.fetchall()
        
        us_n_type = None
        for col in columns:
            if col[1] == 'us_n':
                us_n_type = col[2]
                break
        
        if us_n_type and us_n_type != 'TEXT':
            print(f"   Campo us_n è {us_n_type}, correzione necessaria...")
            
            # Salva dati
            cursor.execute("CREATE TABLE pyarchinit_us_negative_doc_backup AS SELECT * FROM pyarchinit_us_negative_doc")
            
            # Drop tabella
            cursor.execute("DROP TABLE pyarchinit_us_negative_doc")
            
            # Ricrea con us_n come TEXT
            cursor.execute("""
                CREATE TABLE pyarchinit_us_negative_doc (
                    gid INTEGER PRIMARY KEY,
                    the_geom BLOB,
                    sito_n TEXT,
                    area_n TEXT,
                    us_n TEXT,
                    tipo_doc_n TEXT,
                    nome_doc_n TEXT,
                    "LblSize" INTEGER,
                    "LblColor" TEXT,
                    "LblBold" INTEGER,
                    "LblItalic" INTEGER,
                    "LblUnderl" INTEGER,
                    "LblStrike" INTEGER,
                    "LblFont" TEXT,
                    "LblX" REAL,
                    "LblY" REAL,
                    "LblSclMin" INTEGER,
                    "LblSclMax" INTEGER,
                    "LblAlignH" TEXT,
                    "LblAlignV" TEXT,
                    "LblRot" REAL
                )
            """)
            
            # Ripristina dati
            col_names = [col[1] for col in columns]
            cursor.execute(f"""
                INSERT INTO pyarchinit_us_negative_doc ({', '.join(col_names)})
                SELECT {', '.join(col_names)} FROM pyarchinit_us_negative_doc_backup
            """)
            
            cursor.execute("DROP TABLE pyarchinit_us_negative_doc_backup")
            print("   ✓ Campo us_n convertito a TEXT")
    
    if not table_exists:
        # Crea la tabella se non esiste
        cursor.execute("""
            CREATE TABLE pyarchinit_us_negative_doc (
                gid INTEGER PRIMARY KEY,
                the_geom BLOB,
                sito_n TEXT,
                area_n TEXT,
                us_n TEXT,
                tipo_doc_n TEXT,
                nome_doc_n TEXT,
                "LblSize" INTEGER,
                "LblColor" TEXT,
                "LblBold" INTEGER,
                "LblItalic" INTEGER,
                "LblUnderl" INTEGER,
                "LblStrike" INTEGER,
                "LblFont" TEXT,
                "LblX" REAL,
                "LblY" REAL,
                "LblSclMin" INTEGER,
                "LblSclMax" INTEGER,
                "LblAlignH" TEXT,
                "LblAlignV" TEXT,
                "LblRot" REAL
            )
        """)
        print("   ✓ Creata tabella pyarchinit_us_negative_doc")
    
    # 3. REGISTRA GEOMETRIE
    if spatialite_loaded:
        print("\n3. Registrazione geometrie...")
        
        # Ottieni SRID
        cursor.execute("SELECT srid FROM geometry_columns LIMIT 1")
        result = cursor.fetchone()
        srid = result[0] if result else 3004
        
        geometry_registrations = [
            ('pyunitastratigrafiche', 'the_geom', 'MULTIPOLYGON'),
            ('pyunitastratigrafiche_usm', 'the_geom', 'MULTIPOLYGON'),
            ('pyarchinit_us_negative_doc', 'the_geom', 'LINESTRING')
        ]
        
        for table, geom_col, geom_type in geometry_registrations:
            try:
                # Verifica se già registrata
                cursor.execute(f"""
                    SELECT * FROM geometry_columns 
                    WHERE f_table_name = '{table}' AND f_geometry_column = '{geom_col}'
                """)
                
                if not cursor.fetchone():
                    cursor.execute(f"SELECT RecoverGeometryColumn('{table}', '{geom_col}', {srid}, '{geom_type}', 'XY')")
                    print(f"   ✓ Registrata geometria {table}.{geom_col}")
            except:
                pass
    
    # 4. CREA TRIGGER per pyunitastratigrafiche (come in PostgreSQL)
    print("\n4. Creazione trigger per coordinate...")
    
    # Trigger per aggiornare coord quando cambia the_geom
    try:
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_coord_on_geom
            AFTER UPDATE OF the_geom ON pyunitastratigrafiche
            FOR EACH ROW
            WHEN NEW.the_geom IS NOT NULL
            BEGIN
                UPDATE pyunitastratigrafiche 
                SET coord = (
                    SELECT AsText(Centroid(the_geom)) 
                    FROM pyunitastratigrafiche 
                    WHERE gid = NEW.gid
                )
                WHERE gid = NEW.gid;
            END;
        """)
        print("   ✓ Creato trigger update_coord_on_geom")
    except Exception as e:
        print(f"   ⚠ Trigger non creato (potrebbe non essere supportato): {e}")
    
    # 5. CREA LE VIEW necessarie
    print("\n5. Creazione view...")
    
    # pyarchinit_us_view
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS pyarchinit_us_view AS
        SELECT 
            pyunitastratigrafiche.gid,
            pyunitastratigrafiche.the_geom,
            pyunitastratigrafiche.area_s,
            pyunitastratigrafiche.scavo_s,
            pyunitastratigrafiche.us_s,
            pyunitastratigrafiche.stratigraph_index_us,
            pyunitastratigrafiche.tipo_us_s,
            pyunitastratigrafiche.rilievo_originale,
            pyunitastratigrafiche.disegnatore,
            pyunitastratigrafiche.data,
            pyunitastratigrafiche.tipo_doc,
            pyunitastratigrafiche.nome_doc,
            pyunitastratigrafiche.unita_tipo_s,
            us_table.*
        FROM pyunitastratigrafiche
        JOIN us_table ON 
            pyunitastratigrafiche.scavo_s = us_table.sito AND 
            pyunitastratigrafiche.area_s = us_table.area AND 
            pyunitastratigrafiche.us_s = us_table.us AND 
            pyunitastratigrafiche.unita_tipo_s = us_table.unita_tipo
        WHERE us_table.unita_tipo = 'US'
    """)
    print("   ✓ Creata view pyarchinit_us_view")
    
    # pyarchinit_usm_view  
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS pyarchinit_usm_view AS
        SELECT 
            pyunitastratigrafiche_usm.gid,
            pyunitastratigrafiche_usm.the_geom,
            pyunitastratigrafiche_usm.area_s,
            pyunitastratigrafiche_usm.scavo_s,
            pyunitastratigrafiche_usm.us_s,
            pyunitastratigrafiche_usm.stratigraph_index_us,
            pyunitastratigrafiche_usm.tipo_us_s,
            pyunitastratigrafiche_usm.rilievo_originale,
            pyunitastratigrafiche_usm.disegnatore,
            pyunitastratigrafiche_usm.data,
            pyunitastratigrafiche_usm.tipo_doc,
            pyunitastratigrafiche_usm.nome_doc,
            pyunitastratigrafiche_usm.unita_tipo_s,
            us_table.*
        FROM pyunitastratigrafiche_usm
        JOIN us_table ON 
            pyunitastratigrafiche_usm.scavo_s = us_table.sito AND 
            pyunitastratigrafiche_usm.area_s = us_table.area AND 
            pyunitastratigrafiche_usm.us_s = us_table.us AND 
            pyunitastratigrafiche_usm.unita_tipo_s = us_table.unita_tipo
        WHERE us_table.unita_tipo = 'USM'
    """)
    print("   ✓ Creata view pyarchinit_usm_view")
    
    # pyarchinit_us_negative_doc_view
    cursor.execute("""
        CREATE VIEW IF NOT EXISTS pyarchinit_us_negative_doc_view AS
        SELECT 
            pyarchinit_us_negative_doc.*,
            us_table.id_us,
            us_table.sito,
            us_table.area,
            us_table.us,
            us_table.d_stratigrafica,
            us_table.d_interpretativa,
            us_table.descrizione,
            us_table.interpretazione,
            us_table.periodo_iniziale,
            us_table.fase_iniziale,
            us_table.periodo_finale,
            us_table.fase_finale,
            us_table.scavato,
            us_table.attivita,
            us_table.anno_scavo,
            us_table.metodo_di_scavo,
            us_table.inclusi,
            us_table.campioni,
            us_table.rapporti,
            us_table.data_schedatura,
            us_table.schedatore,
            us_table.formazione,
            us_table.stato_di_conservazione,
            us_table.colore,
            us_table.consistenza,
            us_table.struttura,
            us_table.cont_per,
            us_table.order_layer,
            us_table.documentazione
        FROM pyarchinit_us_negative_doc
        JOIN us_table ON 
            pyarchinit_us_negative_doc.sito_n = us_table.sito AND 
            pyarchinit_us_negative_doc.area_n = us_table.area AND 
            pyarchinit_us_negative_doc.us_n = us_table.us
    """)
    print("   ✓ Creata view pyarchinit_us_negative_doc_view")
    
    # Riabilita constraints
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("PRAGMA triggers = ON")
    
    # Commit
    conn.commit()
    
    # 6. VERIFICA FINALE
    print("\n6. Verifica finale...")
    
    # Verifica tabelle
    for table in ['pyunitastratigrafiche', 'pyunitastratigrafiche_usm', 'pyarchinit_us_negative_doc']:
        cursor.execute(f"SELECT type FROM sqlite_master WHERE name='{table}'")
        result = cursor.fetchone()
        if result:
            print(f"   ✓ {table}: {result[0]}")
            
            # Verifica campo us_n in pyarchinit_us_negative_doc
            if table == 'pyarchinit_us_negative_doc':
                cursor.execute(f"PRAGMA table_info({table})")
                for col in cursor.fetchall():
                    if col[1] == 'us_n':
                        print(f"     - campo us_n: {col[2]}")
    
    conn.close()
    
    print(f"\n{'='*60}")
    print("✓ ALLINEAMENTO COMPLETATO!")
    print(f"{'='*60}")


def process_all_databases():
    """Processa tutti i database"""
    databases = [
        "/Users/enzo/pyarchinit/pyarchinit_DB_folder/ktm24.sqlite",
        "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/resources/dbfiles/pyarchinit.sqlite",
        "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/resources/dbfiles/pyarchinit_db.sqlite"
    ]
    
    for db_path in databases:
        if os.path.exists(db_path):
            try:
                final_postgres_alignment(db_path)
            except Exception as e:
                print(f"\n✗ Errore processando {os.path.basename(db_path)}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"\n⚠ Database non trovato: {db_path}")


if __name__ == "__main__":
    process_all_databases()