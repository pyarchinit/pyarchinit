# -*- coding: utf-8 -*-
"""
QGIS Python Console script
Rimuove il vincolo NOT NULL dal campo 'macc' nella tabella
'tma_materiali_ripetibili' di un database SpatiaLite/SQLite.

Funziona in due modalità:
- AUTO: se la layer 'tma_materiali_ripetibili' è caricata in QGIS, ricava il path dal datasource.
- MANUALE: altrimenti usa il db_path impostato sotto.

Cosa fa:
- Crea un backup del database (.bak con timestamp)
- Verifica se 'macc' è NOT NULL
- Ricrea la tabella rendendo 'macc' nullable, preservando la FK su id_tma
- Verifica a fine operazione

Autore: per Enzo
"""

import os
import re
import shutil
import sqlite3
from datetime import datetime

# ========= [1] CONFIG MANUALE (se non hai la layer caricata) =========
# Imposta qui il percorso del tuo .sqlite se la layer non è caricata.
db_path_manual = r"/Users/enzo/pyarchinit/pyarchinit_DB_folder/Festos_2025_US2022_23.sqlite"  # <-- MODIFICA SE NECESSARIO

# ========= [2] TENTA AUTO-DETEZIONE DAL PROGETTO =========
def find_db_from_loaded_layer(table_name="tma_materiali_ripetibili"):
    """Se la layer è caricata, prova a estrarre il path dal datasource."""
    try:
        from qgis.core import QgsProject
        for lyr in QgsProject.instance().mapLayers().values():
            if lyr.name() == table_name or lyr.name().endswith("." + table_name):
                ds = lyr.dataProvider().dataSourceUri()
                # Possibili formati dataSourceUri per SpatiaLite/GeoPackage
                # Esempi:
                #  - '/path/db.sqlite|layername=tma_materiali_ripetibili'
                #  - 'dbname=/path/db.sqlite table="tma_materiali_ripetibili" (geom)'
                m = re.search(r'^(.*?\.sqlite)\b', ds) or re.search(r'dbname=([^ ]*\.sqlite)\b', ds)
                if m:
                    return os.path.abspath(m.group(1))
    except Exception:
        pass
    return None

db_path = find_db_from_loaded_layer() or db_path_manual

# ========= [3] UTILITIES =========
def msg(txt, level='INFO'):
    """Messaggi su console e (se disponibile) sulla message bar di QGIS."""
    print(f"[{level}] {txt}")
    try:
        from qgis.PyQt.QtWidgets import QMessageBox
        from qgis.core import Qgis
        from qgis.utils import iface
        level_map = {'INFO': Qgis.Info, 'WARNING': Qgis.Warning, 'CRITICAL': Qgis.Critical, 'SUCCESS': Qgis.Success}
        iface.messageBar().pushMessage("Schema update", txt, level_map.get(level, Qgis.Info), 6)
    except Exception:
        pass

def backup_db(path):
    """Crea un backup del db con timestamp nella stessa cartella."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base, ext = os.path.splitext(path)
    bak = f"{base}.bak_{ts}{ext}"
    shutil.copy2(path, bak)
    return bak

def table_info(conn, table):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")
    return cur.fetchall()

def fk_list(conn, table):
    cur = conn.cursor()
    cur.execute(f"PRAGMA foreign_key_list({table});")
    return cur.fetchall()

# ========= [4] VALIDAZIONI INIZIALI =========
if not db_path or not os.path.isfile(db_path):
    msg("Percorso database non valido. Carica la layer in progetto o imposta 'db_path_manual'.", 'CRITICAL')
    raise SystemExit

msg(f"Database: {db_path}")

# ========= [5] APERTURA E ANALISI SCHEMA =========
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA foreign_keys = ON;")

tbl = "tma_materiali_ripetibili"
old_tbl = tbl + "__old"

info = table_info(conn, tbl)
if not info:
    msg(f"La tabella '{tbl}' non esiste nel database.", 'CRITICAL')
    conn.close()
    raise SystemExit

# Trova info su 'macc'
col_macc = None
for cid, name, ctype, notnull, dflt, pk in info:
    if name == 'macc':
        col_macc = dict(cid=cid, name=name, ctype=ctype, notnull=notnull, dflt=dflt, pk=pk)
        break

if not col_macc:
    msg("La colonna 'macc' non esiste nella tabella: nulla da fare.", 'CRITICAL')
    conn.close()
    raise SystemExit

if col_macc['notnull'] == 0:
    msg("La colonna 'macc' è già nullable: nessuna modifica necessaria.", 'SUCCESS')
    conn.close()
    raise SystemExit

# Verifica FK (informativa)
fks = fk_list(conn, tbl)
msg(f"FK trovate: {fks}")

# ========= [6] BACKUP =========
bak = backup_db(db_path)
msg(f"Backup creato: {bak}", 'INFO')

# ========= [7] MIGRAZIONE SCHEMA =========
# Nota: ricreiamo la tabella con 'macc' nullable e FK su id_tma.
schema_sql = f"""
CREATE TABLE {tbl} (
    id             INTEGER PRIMARY KEY,
    id_tma         INTEGER NOT NULL
                   REFERENCES tma_materiali_archeologici(id)
                   ON UPDATE NO ACTION
                   ON DELETE NO ACTION,
    madi           TEXT,
    macc           TEXT,        -- reso nullable
    macl           TEXT,
    macp           TEXT,
    macd           TEXT,
    cronologia_mac TEXT,
    macq           TEXT,
    peso           FLOAT,
    created_at     TEXT,
    updated_at     TEXT,
    created_by     TEXT,
    updated_by     TEXT
);
"""

copy_sql = f"""
INSERT INTO {tbl} (
    id, id_tma, madi, macc, macl, macp, macd, cronologia_mac, macq, peso,
    created_at, updated_at, created_by, updated_by
)
SELECT
    id, id_tma, madi, macc, macl, macp, macd, cronologia_mac, macq, peso,
    created_at, updated_at, created_by, updated_by
FROM {old_tbl};
"""

try:
    msg("Inizio migrazione (transazione)...", 'INFO')
    conn.isolation_level = None  # controllo manuale transazioni
    cur = conn.cursor()
    cur.execute("BEGIN IMMEDIATE;")
    cur.execute("PRAGMA foreign_keys = OFF;")
    cur.execute(f"ALTER TABLE {tbl} RENAME TO {old_tbl};")
    cur.execute(schema_sql)
    cur.execute(copy_sql)
    cur.execute(f"DROP TABLE {old_tbl};")
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute("COMMIT;")
    msg("Migrazione completata con successo.", 'SUCCESS')
except Exception as e:
    cur.execute("ROLLBACK;")
    msg(f"Errore durante la migrazione: {e}. Ripristina dal backup se necessario: {bak}", 'CRITICAL')
    conn.close()
    raise

# ========= [8] VERIFICHE FINALI =========
new_info = table_info(conn, tbl)
new_macc_notnull = None
for cid, name, ctype, notnull, dflt, pk in new_info:
    if name == 'macc':
        new_macc_notnull = notnull
        break

if new_macc_notnull == 0:
    msg("Verifica OK: 'macc' ora accetta NULL.", 'SUCCESS')
else:
    msg("Attenzione: 'macc' risulta ancora NOT NULL. Controlla lo schema.", 'WARNING')

# (Facoltativo) conta quanti record hanno macc NULL
try:
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {tbl} WHERE macc IS NULL;")
    null_count = cur.fetchone()[0]
    msg(f"Record con macc NULL: {null_count}", 'INFO')
except Exception:
    pass

conn.close()
msg("Operazione terminata.", 'INFO')