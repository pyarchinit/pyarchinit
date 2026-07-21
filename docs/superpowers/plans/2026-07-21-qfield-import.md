# QField Import Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** "Importa da QField" in pyArchInit: pipeline riusabile che riversa i GPKG del progetto QField nel DB corrente (PostGIS/SpatiaLite) con dedup, fill-empty, uuid7, media su StorageManager e thumbnail automatiche; CLI + dialog QGIS.

**Architecture:** Pipeline pura (zero Qt) in `modules/utility/qfield_importer.py` che lavora su liste di dict (seam testabile senza GDAL); lettura GPKG con import lazy di `osgeo`; CLI sottile in `scripts/import_qfield.py`; `gui/qfield_import_dialog.py` = QDialog + worker QThread che chiama la stessa pipeline con `dry_run=True/False`; voce menu in `pyarchinitPlugin.py`.

**Tech Stack:** Python 3, SQLAlchemy ≥2.0 (branch), OGR/GDAL (solo runtime QGIS), PIL (solo thumbnails runtime), PyQt5/QGIS (solo GUI).

**Spec:** `docs/superpowers/specs/2026-07-21-qfield-import-design.md` (leggila prima di ogni task).

## Global Constraints

- Branch `Stratigraph_00001`; SQLAlchemy ≥2.0 (NON portare nulla su master, che è capped <2.0).
- `modules/utility/qfield_importer.py` NON deve importare Qt/QGIS a livello modulo; `osgeo`, `Media_utility` e storage vanno importati LAZY (dentro le funzioni).
- Test in `tests/qfield/` (`/tests/*` è gitignorato: i test restano locali, MAI `git add tests/`).
- Test eseguiti con python3 di sistema (senza osgeo/mod_spatialite/qgis): ogni test che richiede osgeo o spatialite usa `pytest.mark.skipif`.
- Tabelle target: `us_table`, `inventario_materiali_table`, `pyunitastratigrafiche`, `pyarchinit_quote`, `media_table`, `media_to_entity_table`.
- Fill-empty SOLO su us_table e inventario_materiali_table; "vuoto" = NULL o stringa vuota/whitespace; mai toccare PK, chiavi dedup, `node_uuid`, `version_number`, `sync_status`, `editing_by`, `editing_since`, `schedatore`.
- Provenienza: `created_by='qfield_import'` se la colonna esiste, altrimenti `last_modified_by='qfield_import'` se esiste.
- Commit frequenti con `git -c commit.gpgsign=false commit --no-verify`; NIENTE footer AI/Co-Authored-By nei commit.
- i18n GUI: dict `TRANSLATIONS` a 10 lingue (it,en,de,es,fr,ar,ca,ro,pt,el) + `self.L` da `QgsSettings "locale/userLocale"` (pattern `gui/user_management_dialog.py`).
- Convenzione thumbnail (da `tabs/Image_viewer.py:1362-1380`): suffissi `'_thumb.png'` e `'.png'`; `media_thumb_filename = f"{id_media}_{filename}_thumb.png"`; in `media_thumb_table` i path thumb sono SOLO filename (relativi a thumb_path/thumb_resize).
- Comando test: `cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" && python3 -m pytest tests/qfield -q`

---

### Task 1: Fondamenta pipeline — helpers, result, lettura GPKG

**Files:**
- Create: `modules/utility/qfield_importer.py`
- Create: `tests/qfield/__init__.py` (vuoto)
- Test: `tests/qfield/test_helpers.py`

**Interfaces:**
- Produces: `normalize_key(v) -> str`, `is_empty(v) -> bool`, `row_payload(row, table, exclude=()) -> dict`, `next_id(conn, table, pk) -> int`, `reflected(metadata, engine, name) -> Table`, `TableCounts` (dataclass: `inserted/updated/skipped/errors: int`), `QFieldImportResult` (dataclass: campi `us, materiali, geometrie, quote, media, links, thumbs: TableCounts`, `filled_fields: list`, `media_upload_failures: list`, `warnings: list`, metodo `summary_lines() -> list[str]`), `SOURCE_TABLES` (dict), `find_gpkg_layers(qfield_dir) -> dict`, `read_features(gpkg_path, layer_name, with_geometry=False, force_multi=True) -> list[dict]`
- Consumes: nulla (primo task)

- [ ] **Step 1: Scrivi i test failing**

```python
# tests/qfield/test_helpers.py
import os
import sys

import pytest

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PLUGIN_DIR not in sys.path:
    sys.path.insert(0, PLUGIN_DIR)

from modules.utility.qfield_importer import (
    QFieldImportResult, TableCounts, is_empty, normalize_key, row_payload,
)
from sqlalchemy import Column, Integer, MetaData, Table, Text


def _fake_table():
    md = MetaData()
    return Table('t', md,
                 Column('id_us', Integer, primary_key=True),
                 Column('sito', Text), Column('area', Text),
                 Column('us', Text), Column('descrizione', Text))


def test_normalize_key():
    assert normalize_key('  Festòs ') == 'Festòs'
    assert normalize_key(None) == ''
    assert normalize_key(7) == '7'


def test_is_empty():
    assert is_empty(None) and is_empty('') and is_empty('   ')
    assert not is_empty('x') and not is_empty(0)


def test_row_payload_intersects_and_drops_empty():
    t = _fake_table()
    row = {'_fid': 3, 'sito': 'F', 'area': '', 'us': None,
           'descrizione': 'd', 'campo_estraneo': 'x', 'id_us': 9}
    p = row_payload(row, t, exclude=('id_us',))
    assert p == {'sito': 'F', 'descrizione': 'd'}


def test_result_counters_and_summary():
    r = QFieldImportResult()
    r.us.inserted += 2
    r.quote.skipped += 1
    assert isinstance(r.us, TableCounts)
    lines = r.summary_lines()
    assert any('US' in l for l in lines)
    assert any('Quote' in l for l in lines)
```

- [ ] **Step 2: Verifica che falliscano**

Run: `cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" && python3 -m pytest tests/qfield/test_helpers.py -q`
Expected: FAIL / errore import `ModuleNotFoundError: modules.utility.qfield_importer`

- [ ] **Step 3: Crea il modulo con helpers + result + lettura GPKG**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qfield_importer.py — pipeline riusabile per importare in pyArchInit i dati
raccolti in campo con QField (plugin companion pyarchinit-qfield).

Zero dipendenze Qt/QGIS a livello modulo: osgeo (GDAL/OGR), Media_utility e
lo storage manager vengono importati lazy dentro le funzioni che li usano,
così il modulo resta importabile e testabile con un python qualsiasi.

Spec: docs/superpowers/specs/2026-07-21-qfield-import-design.md
Origine: script standalone pyarchinit_qfield_import.py (Enzo Cocca, GPL-2.0).
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy import MetaData, Table, create_engine, func, select, text

log = logging.getLogger("qfield_importer")

#: layer cercati nei GPKG del progetto QField (nome layer -> tabella DB)
SOURCE_TABLES = {
    "us_table": "us_table",
    "inventario_materiali_table": "inventario_materiali_table",
    "media_table": "media_table",
    "media_to_entity_table": "media_to_entity_table",
    "pyunitastratigrafiche": "pyunitastratigrafiche",
    "pyarchinit_quote": "pyarchinit_quote",
}

US_KEY = ("sito", "area", "us")
MAT_KEY = ("sito", "numero_inventario")
GEOM_KEY = ("scavo_s", "area_s", "us_s")
QUOTE_KEY = ("sito_q", "area_q", "us_q", "quota_q")

#: marcatore di provenienza sui record inseriti
PROVENANCE = "qfield_import"

#: colonne mai toccate dalla policy fill-empty
FILL_EMPTY_PROTECTED = {
    "node_uuid", "entity_uuid", "version_number", "sync_status",
    "editing_by", "editing_since", "schedatore", "created_by",
    "last_modified_by", "last_modified_timestamp", "created_at",
}


@dataclass
class TableCounts:
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0


@dataclass
class QFieldImportResult:
    us: TableCounts = field(default_factory=TableCounts)
    materiali: TableCounts = field(default_factory=TableCounts)
    geometrie: TableCounts = field(default_factory=TableCounts)
    quote: TableCounts = field(default_factory=TableCounts)
    media: TableCounts = field(default_factory=TableCounts)
    links: TableCounts = field(default_factory=TableCounts)
    thumbs: TableCounts = field(default_factory=TableCounts)
    #: (tabella, chiave leggibile, campo, valore) riempiti dalla fill-empty
    filled_fields: list = field(default_factory=list)
    #: file foto non copiati/caricati (post-commit)
    media_upload_failures: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    dry_run: bool = True

    def summary_lines(self):
        rows = [
            ("US", self.us), ("Reperti", self.materiali),
            ("Geometrie", self.geometrie), ("Quote", self.quote),
            ("Media", self.media), ("Collegamenti", self.links),
            ("Thumbnail", self.thumbs),
        ]
        out = []
        for label, c in rows:
            out.append(f"{label:<13}{c.inserted:>4} inseriti, {c.updated:>3} "
                       f"aggiornati, {c.skipped:>3} saltati, {c.errors:>2} errori")
        return out


# --------------------------------------------------------------------------
#  Helper generici
# --------------------------------------------------------------------------

def normalize_key(value):
    return str(value).strip() if value is not None else ""


def is_empty(value):
    """True per NULL / stringa vuota o solo whitespace (policy fill-empty)."""
    if value is None:
        return True
    return isinstance(value, str) and value.strip() == ""


def reflected(metadata, engine, table_name):
    return Table(table_name, metadata, autoload_with=engine)


def next_id(conn, table, pk_name):
    value = conn.execute(select(func.max(table.c[pk_name]))).scalar()
    return (value or 0) + 1


def row_payload(row, table, exclude=()):
    """Interseca i campi del GPKG con le colonne reali della tabella DB,
    scartando None/stringhe vuote e le colonne escluse."""
    payload = {}
    for column in table.columns:
        name = column.name
        if name in exclude or name.startswith("_"):
            continue
        if name in row and row[name] is not None and row[name] != "":
            payload[name] = row[name]
    return payload


def new_node_uuid():
    """uuid7 come stringa; stesso generatore della migrazione node_uuid."""
    try:
        from modules.s3dgraphy.sync.uuid7 import uuid7
    except ImportError:
        from ..s3dgraphy.sync.uuid7 import uuid7
    return str(uuid7())


def apply_provenance(payload, table):
    """created_by='qfield_import' se esiste, altrimenti last_modified_by."""
    if "created_by" in table.columns:
        payload.setdefault("created_by", PROVENANCE)
    elif "last_modified_by" in table.columns:
        payload.setdefault("last_modified_by", PROVENANCE)
    return payload


# --------------------------------------------------------------------------
#  Lettura GPKG (osgeo importato lazy: disponibile solo nel python di QGIS)
# --------------------------------------------------------------------------

def find_gpkg_layers(qfield_dir):
    """Scansiona i .gpkg della cartella QField:
    {nome_tabella: (percorso_gpkg, nome_layer)} per i layer di interesse.

    Se la cartella non contiene .gpkg ritorna {} SENZA importare osgeo:
    così l'errore "nessun layer" resta pulito anche fuori da QGIS."""
    gpkg_files = sorted(Path(qfield_dir).rglob("*.gpkg"))
    if not gpkg_files:
        return {}
    from osgeo import ogr
    found = {}
    for gpkg in gpkg_files:
        ds = ogr.Open(str(gpkg))
        if ds is None:
            continue
        for i in range(ds.GetLayerCount()):
            layer = ds.GetLayer(i)
            name = layer.GetName()
            for wanted in SOURCE_TABLES:
                if name.lower() == wanted or name.lower().endswith(wanted):
                    if wanted in found:
                        log.warning("Layer %s trovato anche in %s (uso %s)",
                                    wanted, gpkg, found[wanted][0])
                    else:
                        found[wanted] = (str(gpkg), name)
        ds = None
    return found


def read_features(gpkg_path, layer_name, with_geometry=False, force_multi=True):
    """Legge le feature di un layer come lista di dict. Aggiunge '_fid';
    con with_geometry anche '_wkt' e '_srid' (MULTIPOLYGON se force_multi)."""
    from osgeo import ogr
    ds = ogr.Open(gpkg_path)
    layer = ds.GetLayerByName(layer_name)
    defn = layer.GetLayerDefn()
    field_names = [defn.GetFieldDefn(i).GetName()
                   for i in range(defn.GetFieldCount())]

    srid = None
    if with_geometry:
        sref = layer.GetSpatialRef()
        if sref is not None:
            sref.AutoIdentifyEPSG()
            code = sref.GetAuthorityCode(None)
            srid = int(code) if code else None

    rows = []
    for feature in layer:
        row = {"_fid": feature.GetFID()}
        for fname in field_names:
            row[fname] = feature.GetField(fname)
        if with_geometry:
            geom = feature.GetGeometryRef()
            if geom is not None:
                geom = (ogr.ForceToMultiPolygon(geom.Clone())
                        if force_multi else geom.Clone())
                row["_wkt"] = geom.ExportToWkt()
            else:
                row["_wkt"] = None
            row["_srid"] = srid
        rows.append(row)
    ds = None
    return rows
```

- [ ] **Step 4: Verifica che i test passino**

Run: `cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" && python3 -m pytest tests/qfield/test_helpers.py -q`
Expected: 4 passed

- [ ] **Step 5: Commit (solo il modulo — tests/ è gitignorato)**

```bash
git -C "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" add modules/utility/qfield_importer.py
git -C "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" -c commit.gpgsign=false commit --no-verify -m "feat(qfield): import pipeline foundations — helpers, result dataclass, GPKG readers"
```

---

### Task 2: Import US + reperti (dedup, fill-empty, uuid7, provenienza)

**Files:**
- Modify: `modules/utility/qfield_importer.py` (append dopo `read_features`)
- Create: `tests/qfield/conftest.py`
- Test: `tests/qfield/test_import_us_materiali.py`

**Interfaces:**
- Consumes: helpers Task 1 (`normalize_key`, `is_empty`, `row_payload`, `next_id`, `reflected`, `new_node_uuid`, `apply_provenance`, `TableCounts`, `QFieldImportResult`, `US_KEY`, `MAT_KEY`, `FILL_EMPTY_PROTECTED`)
- Produces: `import_us(conn, metadata, engine, rows, result, dry_run, log_fn) -> dict` (ritorna id_map sorgente→id_us DB), `import_materiali(conn, metadata, engine, rows, result, dry_run, log_fn) -> None`, `fill_empty_fields(conn, table, pk_name, pk_value, db_row, src_row, result, counts, table_label, key_label, dry_run, log_fn) -> int` (`counts` = il TableCounts della tabella, es. `result.us`)

- [ ] **Step 1: Scrivi conftest con mini-schema SQLite in-memory**

```python
# tests/qfield/conftest.py
import os
import sys

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PLUGIN_DIR not in sys.path:
    sys.path.insert(0, PLUGIN_DIR)

SCHEMA = [
    """CREATE TABLE us_table (
        id_us INTEGER PRIMARY KEY, sito TEXT, area TEXT, us TEXT,
        d_stratigrafica TEXT, d_interpretativa TEXT, anno_scavo TEXT,
        schedatore TEXT, node_uuid TEXT, created_by TEXT,
        UNIQUE (sito, area, us))""",
    """CREATE TABLE inventario_materiali_table (
        id_invmat INTEGER PRIMARY KEY, sito TEXT, numero_inventario TEXT,
        tipo_reperto TEXT, definizione TEXT, node_uuid TEXT,
        last_modified_by TEXT)""",
    """CREATE TABLE media_table (
        id_media INTEGER PRIMARY KEY, mediatype TEXT,
        filename TEXT, filetype TEXT, filepath TEXT, descrizione TEXT)""",
    """CREATE TABLE media_to_entity_table (
        "id_mediaToEntity" INTEGER PRIMARY KEY, id_entity INTEGER,
        entity_type TEXT, table_name TEXT, id_media INTEGER,
        filepath TEXT, media_name TEXT)""",
    """CREATE TABLE media_thumb_table (
        id_media_thumb INTEGER PRIMARY KEY, id_media INTEGER,
        mediatype TEXT, media_filename TEXT, media_thumb_filename TEXT,
        filetype TEXT, filepath TEXT, path_resize TEXT)""",
]


@pytest.fixture()
def engine():
    eng = create_engine("sqlite://",
                        connect_args={"check_same_thread": False},
                        poolclass=StaticPool)
    with eng.begin() as conn:
        for ddl in SCHEMA:
            conn.execute(text(ddl))
    return eng
```

- [ ] **Step 2: Scrivi i test failing**

```python
# tests/qfield/test_import_us_materiali.py
from sqlalchemy import MetaData, text

from modules.utility.qfield_importer import (
    QFieldImportResult, import_materiali, import_us,
)


def _us_row(fid, sito="F", area="1", us="100", **extra):
    row = {"_fid": fid, "id_us": None, "sito": sito, "area": area, "us": us}
    row.update(extra)
    return row


def test_import_us_inserts_with_uuid_and_provenance(engine):
    md, res = MetaData(), QFieldImportResult()
    with engine.begin() as conn:
        id_map = import_us(conn, md, engine,
                           [_us_row(1, d_stratigrafica="strato")],
                           res, dry_run=False, log_fn=lambda m: None)
    assert res.us.inserted == 1 and id_map[1] == 1
    with engine.connect() as conn:
        r = conn.execute(text(
            "SELECT node_uuid, created_by, d_stratigrafica FROM us_table"
        )).fetchone()
    assert r[0] and len(r[0]) == 36
    assert r[1] == "qfield_import"
    assert r[2] == "strato"


def test_import_us_fill_empty_only(engine):
    with engine.begin() as conn:
        conn.execute(text(
            "INSERT INTO us_table (id_us, sito, area, us, d_stratigrafica,"
            " anno_scavo, schedatore) VALUES "
            "(5, 'F', '1', '100', 'esistente', '', 'Marta')"))
    md, res = MetaData(), QFieldImportResult()
    with engine.begin() as conn:
        id_map = import_us(conn, md, engine,
                           [_us_row(9, d_stratigrafica="NUOVA",
                                    anno_scavo="2026", schedatore="EVIL")],
                           res, dry_run=False, log_fn=lambda m: None)
    assert id_map[9] == 5
    assert res.us.updated == 1 and res.us.inserted == 0
    with engine.connect() as conn:
        r = conn.execute(text(
            "SELECT d_stratigrafica, anno_scavo, schedatore FROM us_table"
            " WHERE id_us=5")).fetchone()
    assert r[0] == "esistente"      # campo pieno: intatto
    assert r[1] == "2026"           # campo vuoto: riempito
    assert r[2] == "Marta"          # protetto: mai toccato
    assert ("us_table", "F/1/100", "anno_scavo", "2026") in res.filled_fields


def test_import_us_dry_run_writes_nothing(engine):
    md, res = MetaData(), QFieldImportResult()
    with engine.connect() as conn:
        tx = conn.begin()
        import_us(conn, md, engine, [_us_row(1)], res,
                  dry_run=True, log_fn=lambda m: None)
        tx.rollback()
    assert res.us.inserted == 1  # contatore anteprima
    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM us_table")).scalar() == 0


def test_import_materiali_dedup_and_provenance(engine):
    md, res = MetaData(), QFieldImportResult()
    rows = [{"_fid": 1, "sito": "F", "numero_inventario": "10",
             "tipo_reperto": "ceramica"},
            {"_fid": 2, "sito": "F", "numero_inventario": "10"}]
    with engine.begin() as conn:
        import_materiali(conn, md, engine, rows, res,
                         dry_run=False, log_fn=lambda m: None)
    assert res.materiali.inserted == 1 and res.materiali.skipped == 1
    with engine.connect() as conn:
        r = conn.execute(text(
            "SELECT node_uuid, last_modified_by FROM"
            " inventario_materiali_table")).fetchone()
    assert r[0] and r[1] == "qfield_import"
```

- [ ] **Step 3: Verifica che falliscano**

Run: `cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" && python3 -m pytest tests/qfield/test_import_us_materiali.py -q`
Expected: FAIL con `ImportError: cannot import name 'import_us'`

- [ ] **Step 4: Implementa fill_empty_fields + import_us + import_materiali** (append al modulo)

```python
# --------------------------------------------------------------------------
#  Import US + reperti (con policy fill-empty)
# --------------------------------------------------------------------------

def fill_empty_fields(conn, table, pk_name, pk_value, db_row, src_row,
                      result, counts, table_label, key_label, dry_run, log_fn):
    """Riempi i soli campi vuoti del record DB con i valori dal campo.

    db_row: dict colonna->valore del record esistente nel DB.
    Ritorna il numero di campi riempiti (e aggiorna counts.updated di 1
    se almeno un campo è stato riempito).
    """
    updates = {}
    for column in table.columns:
        name = column.name
        if (name == pk_name or name in FILL_EMPTY_PROTECTED
                or name in table.primary_key.columns):
            continue
        src_value = src_row.get(name)
        if is_empty(src_value):
            continue
        if is_empty(db_row.get(name)):
            updates[name] = src_value
    if not updates:
        return 0
    if not dry_run:
        conn.execute(table.update()
                     .where(table.c[pk_name] == pk_value)
                     .values(**updates))
    counts.updated += 1
    for name, value in sorted(updates.items()):
        result.filled_fields.append((table.name, key_label, name, value))
        log_fn(f"  ~ {table_label} {key_label}: campo vuoto '{name}' <- {value!r}")
    return len(updates)


def import_us(conn, metadata, engine, rows, result, dry_run, log_fn):
    """Importa us_table. Ritorna id_map {id sorgente -> id_us DB}.
    Chiave sorgente: id_us del GPKG se valorizzato, altrimenti il fid."""
    table = reflected(metadata, engine, "us_table")
    existing = {}
    for record in conn.execute(select(table)):
        row = dict(record._mapping)
        key = (normalize_key(row["sito"]), normalize_key(row["area"]),
               normalize_key(row["us"]))
        existing[key] = row

    id_map = {}
    new_id = next_id(conn, table, "id_us")
    for row in rows:
        try:
            source_id = (row.get("id_us")
                         if row.get("id_us") not in (None, "", 0)
                         else row["_fid"])
            key = (normalize_key(row.get("sito")), normalize_key(row.get("area")),
                   normalize_key(row.get("us")))
            key_label = "/".join(key)
            if key in existing:
                db_row = existing[key]
                id_map[source_id] = db_row["id_us"]
                filled = fill_empty_fields(
                    conn, table, "id_us", db_row["id_us"], db_row, row,
                    result, result.us, "US", key_label, dry_run, log_fn)
                if not filled:
                    result.us.skipped += 1
                    log_fn(f"  US {key_label} già presente "
                           f"(id_us={db_row['id_us']}): salto")
                continue
            payload = row_payload(row, table, exclude=("id_us",))
            payload["id_us"] = new_id
            if "node_uuid" in table.columns:
                payload["node_uuid"] = new_node_uuid()
            apply_provenance(payload, table)
            if not dry_run:
                conn.execute(table.insert().values(**payload))
            id_map[source_id] = new_id
            existing[key] = dict(payload)
            log_fn(f"  + US {key_label} -> id_us={new_id}")
            new_id += 1
            result.us.inserted += 1
        except Exception as e:
            result.us.errors += 1
            log_fn(f"  ! US fid={row.get('_fid')}: {e}")
    return id_map


def import_materiali(conn, metadata, engine, rows, result, dry_run, log_fn):
    table = reflected(metadata, engine, "inventario_materiali_table")
    existing = {}
    for record in conn.execute(select(table)):
        row = dict(record._mapping)
        key = (normalize_key(row["sito"]),
               normalize_key(row["numero_inventario"]))
        existing[key] = row

    new_id = next_id(conn, table, "id_invmat")
    for row in rows:
        try:
            key = (normalize_key(row.get("sito")),
                   normalize_key(row.get("numero_inventario")))
            key_label = " n.inv ".join(key)
            if key in existing:
                db_row = existing[key]
                filled = fill_empty_fields(
                    conn, table, "id_invmat", db_row["id_invmat"], db_row, row,
                    result, result.materiali, "Reperto", key_label,
                    dry_run, log_fn)
                if not filled:
                    result.materiali.skipped += 1
                    log_fn(f"  Reperto {key_label} già presente: salto")
                continue
            payload = row_payload(row, table, exclude=("id_invmat",))
            payload["id_invmat"] = new_id
            if "node_uuid" in table.columns:
                payload["node_uuid"] = new_node_uuid()
            apply_provenance(payload, table)
            if not dry_run:
                conn.execute(table.insert().values(**payload))
            existing[key] = dict(payload)
            log_fn(f"  + Reperto {key_label} -> id_invmat={new_id}")
            new_id += 1
            result.materiali.inserted += 1
        except Exception as e:
            result.materiali.errors += 1
            log_fn(f"  ! Reperto fid={row.get('_fid')}: {e}")
```

- [ ] **Step 5: Verifica che passino (+ regressione Task 1)**

Run: `cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" && python3 -m pytest tests/qfield -q`
Expected: 8 passed

- [ ] **Step 6: Commit**

```bash
git -C "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" add modules/utility/qfield_importer.py
git -C "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" -c commit.gpgsign=false commit --no-verify -m "feat(qfield): US + finds import — dedup, fill-empty policy, uuid7, provenance"
```

---

### Task 3: Geometrie (poligoni US + punti quota) con SRID transform

**Files:**
- Modify: `modules/utility/qfield_importer.py` (append)
- Test: `tests/qfield/test_geometrie.py`

**Interfaces:**
- Consumes: Task 1-2 helpers, `GEOM_KEY`, `QUOTE_KEY`
- Produces: `target_srid(conn, engine, table_name, geom_column) -> int|None`, `build_geom_sql(is_postgres, force_multi, needs_transform, target) -> str`, `import_geometrie(conn, metadata, engine, rows, result, dry_run, log_fn, dedup=True, srid_override=None) -> None`, `import_quote(conn, metadata, engine, rows, result, dry_run, log_fn, srid_override=None) -> None`

- [ ] **Step 1: Scrivi i test failing (SQL builder puro + skip live)**

```python
# tests/qfield/test_geometrie.py
from modules.utility.qfield_importer import build_geom_sql


def test_build_geom_sql_pg_multi_no_transform():
    assert build_geom_sql(True, True, False, None) == \
        "ST_Multi(ST_GeomFromText(:wkt, :srid))"


def test_build_geom_sql_pg_multi_transform():
    assert build_geom_sql(True, True, True, 3004) == \
        "ST_Multi(ST_Transform(ST_GeomFromText(:wkt, :srid), 3004))"


def test_build_geom_sql_sqlite_point_transform():
    assert build_geom_sql(False, False, True, 32633) == \
        "Transform(GeomFromText(:wkt, :srid), 32633)"


def test_build_geom_sql_sqlite_multi_no_transform():
    assert build_geom_sql(False, True, False, None) == \
        "CastToMultiPolygon(GeomFromText(:wkt, :srid))"
```

- [ ] **Step 2: Verifica che falliscano**

Run: `cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" && python3 -m pytest tests/qfield/test_geometrie.py -q`
Expected: FAIL con ImportError `build_geom_sql`

- [ ] **Step 3: Implementa** (append al modulo)

```python
# --------------------------------------------------------------------------
#  Geometrie: pyunitastratigrafiche (MULTIPOLYGON) + pyarchinit_quote (POINT)
# --------------------------------------------------------------------------

def target_srid(conn, engine, table_name, geom_column):
    """SRID della colonna geometrica nel DB (geometry_columns), o None."""
    try:
        if engine.dialect.name.startswith("postgres"):
            q = text("SELECT srid FROM geometry_columns WHERE "
                     "f_table_name = :t AND f_geometry_column = :g")
        else:
            q = text("SELECT srid FROM geometry_columns WHERE "
                     "f_table_name = :t AND f_geometry_column = :g")
        value = conn.execute(q, {"t": table_name, "g": geom_column}).scalar()
        return int(value) if value else None
    except Exception:
        return None


def build_geom_sql(is_postgres, force_multi, needs_transform, target):
    """Espressione SQL per la INSERT della geometria da :wkt/:srid."""
    if is_postgres:
        expr = "ST_GeomFromText(:wkt, :srid)"
        if needs_transform:
            expr = f"ST_Transform({expr}, {int(target)})"
        if force_multi:
            expr = f"ST_Multi({expr})"
    else:
        expr = "GeomFromText(:wkt, :srid)"
        if needs_transform:
            expr = f"Transform({expr}, {int(target)})"
        if force_multi:
            expr = f"CastToMultiPolygon({expr})"
    return expr


def _insert_geom_row(conn, table, row, payload, geom_column,
                     is_postgres, force_multi, srid, tgt):
    needs_transform = bool(tgt) and int(srid) != int(tgt)
    geom_sql = build_geom_sql(is_postgres, force_multi, needs_transform, tgt)
    columns = ", ".join([f'"{c}"' for c in payload] + [f'"{geom_column}"'])
    params = ", ".join(":" + c for c in payload)
    statement = text(
        f'INSERT INTO {table.name} ({columns}) VALUES ({params}, {geom_sql})')
    conn.execute(statement, {**payload, "wkt": row["_wkt"], "srid": int(srid)})


def import_geometrie(conn, metadata, engine, rows, result, dry_run, log_fn,
                     dedup=True, srid_override=None):
    table = reflected(metadata, engine, "pyunitastratigrafiche")
    is_postgres = engine.dialect.name.startswith("postgres")
    geom_column = "the_geom" if "the_geom" in table.columns else "geom"
    tgt = target_srid(conn, engine, "pyunitastratigrafiche", geom_column)

    existing = set()
    if dedup:
        for record in conn.execute(select(
                table.c.scavo_s, table.c.area_s, table.c.us_s)):
            existing.add((normalize_key(record.scavo_s),
                          normalize_key(record.area_s),
                          normalize_key(record.us_s)))

    new_gid = next_id(conn, table, "gid")
    for row in rows:
        try:
            key = (normalize_key(row.get("scavo_s")),
                   normalize_key(row.get("area_s")),
                   normalize_key(row.get("us_s")))
            if dedup and key in existing:
                result.geometrie.skipped += 1
                log_fn(f"  Geometria US {'/'.join(key)} già presente: salto")
                continue
            if not row.get("_wkt"):
                result.geometrie.skipped += 1
                log_fn(f"  Feature fid={row['_fid']} senza geometria: salto")
                continue
            srid = srid_override or row.get("_srid")
            if not srid:
                raise QFieldImportError(
                    "SRID non determinabile dal GPKG: specifica lo SRID")
            payload = row_payload(row, table, exclude=("gid", geom_column))
            payload["gid"] = new_gid
            if not dry_run:
                _insert_geom_row(conn, table, row, payload, geom_column,
                                 is_postgres, True, srid, tgt)
            existing.add(key)
            log_fn(f"  + Geometria US {'/'.join(key)} -> gid={new_gid} "
                   f"(SRID {srid}{f'->{tgt}' if tgt and int(tgt) != int(srid) else ''})")
            new_gid += 1
            result.geometrie.inserted += 1
        except QFieldImportError:
            raise
        except Exception as e:
            result.geometrie.errors += 1
            log_fn(f"  ! Geometria fid={row.get('_fid')}: {e}")


def import_quote(conn, metadata, engine, rows, result, dry_run, log_fn,
                 srid_override=None):
    """Punti quota. Dedup su sito_q+area_q+us_q+quota_q; POINT nativo."""
    table = reflected(metadata, engine, "pyarchinit_quote")
    is_postgres = engine.dialect.name.startswith("postgres")
    geom_column = "the_geom" if "the_geom" in table.columns else "geom"
    tgt = target_srid(conn, engine, "pyarchinit_quote", geom_column)

    existing = set()
    for record in conn.execute(select(
            table.c.sito_q, table.c.area_q, table.c.us_q, table.c.quota_q)):
        existing.add((normalize_key(record.sito_q), normalize_key(record.area_q),
                      normalize_key(record.us_q), normalize_key(record.quota_q)))

    new_gid = next_id(conn, table, "gid")
    for row in rows:
        try:
            key = (normalize_key(row.get("sito_q")), normalize_key(row.get("area_q")),
                   normalize_key(row.get("us_q")), normalize_key(row.get("quota_q")))
            if key in existing:
                result.quote.skipped += 1
                log_fn(f"  Quota {row.get('quota_q')} (US {row.get('us_q')})"
                       " già presente: salto")
                continue
            if not row.get("_wkt"):
                result.quote.skipped += 1
                continue
            srid = srid_override or row.get("_srid")
            if not srid:
                raise QFieldImportError(
                    "SRID non determinabile dal GPKG quote: specifica lo SRID")
            payload = row_payload(row, table, exclude=("gid", geom_column))
            payload["gid"] = new_gid
            if not dry_run:
                _insert_geom_row(conn, table, row, payload, geom_column,
                                 is_postgres, False, srid, tgt)
            existing.add(key)
            log_fn(f"  + Quota {row.get('quota_q')} m (US {row.get('us_q')})"
                   f" -> gid={new_gid}")
            new_gid += 1
            result.quote.inserted += 1
        except QFieldImportError:
            raise
        except Exception as e:
            result.quote.errors += 1
            log_fn(f"  ! Quota fid={row.get('_fid')}: {e}")
```

E in testa al modulo (dopo `log = logging.getLogger(...)`) aggiungi l'eccezione strutturale:

```python
class QFieldImportError(Exception):
    """Errore strutturale: interrompe l'import (rollback totale)."""
```

- [ ] **Step 4: Verifica**

Run: `cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" && python3 -m pytest tests/qfield -q`
Expected: 12 passed

- [ ] **Step 5: Commit**

```bash
git -C "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" add modules/utility/qfield_importer.py
git -C "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" -c commit.gpgsign=false commit --no-verify -m "feat(qfield): US polygons + elevation points import with SRID transform"
```

---

### Task 4: Media + collegamenti via StorageManager (locale + WebDAV)

**Files:**
- Modify: `modules/utility/qfield_importer.py` (append)
- Test: `tests/qfield/test_media.py`

**Interfaces:**
- Consumes: Task 1-2 (`normalize_key`, `row_payload`, `next_id`, `reflected`, `QFieldImportResult`)
- Produces: `default_media_dest(thumb_path_str) -> str` (parent di thumb_path: `webdav://h:p/pyarchinit_media/thumb/` → `webdav://h:p/pyarchinit_media/`, `/x/thumb/` → `/x/`), `store_media_file(src_path, dest_root, filename) -> str` (path finale; solleva su fallimento), `import_media(conn, metadata, engine, media_rows, link_rows, us_id_map, qfield_dir, media_dest, result, dry_run, log_fn, copy_media=True) -> list[dict]` (ritorna i record media INSERITI: `{"id_media", "filename", "filetype", "filepath", "mediatype"}` per il Task 5)
- Nota: la copia file avviene DOPO il commit (chiamata separata `copy_media_files(pending, result, log_fn)` — vedi sotto); durante la transazione si calcola solo il path finale.

- [ ] **Step 1: Scrivi i test failing**

```python
# tests/qfield/test_media.py
from pathlib import Path

from sqlalchemy import MetaData, text

import modules.utility.qfield_importer as qi
from modules.utility.qfield_importer import (
    QFieldImportResult, default_media_dest, import_media, copy_media_files,
)


def test_default_media_dest():
    assert default_media_dest(
        "webdav://151.97.253.92:5006/pyarchinit_media/thumb/"
    ) == "webdav://151.97.253.92:5006/pyarchinit_media/"
    assert default_media_dest("/Users/enzo/pyarchinit_5/thumb/") == \
        "/Users/enzo/pyarchinit_5/"
    assert default_media_dest("") == ""


def _media_rows():
    return [{"_fid": 1, "id_media": 11, "mediatype": "image",
             "filename": "us100", "filetype": "jpg",
             "filepath": "DCIM/pyarchinit/us100.jpg"}]


def _link_rows():
    return [{"_fid": 1, "id_entity": 77, "entity_type": "US",
             "table_name": "us_table", "id_media": 11,
             "filepath": "DCIM/pyarchinit/us100.jpg", "media_name": "us100"}]


def test_import_media_remaps_links_and_returns_pending(engine, tmp_path):
    (tmp_path / "DCIM" / "pyarchinit").mkdir(parents=True)
    (tmp_path / "DCIM" / "pyarchinit" / "us100.jpg").write_bytes(b"JPG")
    dest = tmp_path / "media_store"
    md, res = MetaData(), QFieldImportResult()
    with engine.begin() as conn:
        inserted = import_media(conn, md, engine, _media_rows(), _link_rows(),
                                us_id_map={77: 5}, qfield_dir=str(tmp_path),
                                media_dest=str(dest) + "/", result=res,
                                dry_run=False, log_fn=lambda m: None)
    assert res.media.inserted == 1 and res.links.inserted == 1
    assert inserted[0]["filepath"] == str(dest) + "/us100.jpg"
    with engine.connect() as conn:
        link = conn.execute(text(
            'SELECT id_entity, id_media FROM media_to_entity_table')).fetchone()
        assert link[0] == 5 and link[1] == 1

    # copia post-commit
    copy_media_files(res, log_fn=lambda m: None)
    assert (dest / "us100.jpg").read_bytes() == b"JPG"
    assert res.media_upload_failures == []


def test_import_media_link_unmappable_skipped(engine, tmp_path):
    md, res = MetaData(), QFieldImportResult()
    with engine.begin() as conn:
        import_media(conn, md, engine, [], _link_rows(), us_id_map={},
                     qfield_dir=str(tmp_path), media_dest=None, result=res,
                     dry_run=False, log_fn=lambda m: None)
    assert res.links.skipped == 1 and res.links.inserted == 0


def test_store_media_file_remote_uses_backend(engine, tmp_path, monkeypatch):
    written = {}

    class FakeBackend:
        def write(self, rel, data):
            written[rel] = data

    class FakeStorage:
        def get_backend(self, path):
            return FakeBackend()
        def parse_path(self, path):
            return ("webdav", "host", path.split("/", 3)[-1])

    monkeypatch.setattr(qi, "_get_storage", lambda: FakeStorage())
    src = tmp_path / "p.jpg"
    src.write_bytes(b"X")
    final = qi.store_media_file(str(src), "webdav://h:1/media/", "p.jpg")
    assert final == "webdav://h:1/media/p.jpg"
    assert written["media/p.jpg"] == b"X"
```

- [ ] **Step 2: Verifica che falliscano**

Run: `cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" && python3 -m pytest tests/qfield/test_media.py -q`
Expected: FAIL con ImportError `default_media_dest`

- [ ] **Step 3: Implementa** (append al modulo)

```python
# --------------------------------------------------------------------------
#  Media: copia locale/WebDAV + record + collegamenti alle US
# --------------------------------------------------------------------------

def _get_storage():
    """StorageManager del plugin (lazy: dipende dall'ambiente QGIS)."""
    try:
        from modules.utility.pyarchinit_media_utility import get_storage_manager
    except ImportError:
        from .pyarchinit_media_utility import get_storage_manager
    return get_storage_manager()


#: stessi prefissi di pyarchinit_media_utility.is_remote_path — duplicati
#: qui perché quel modulo importa la catena qgis a livello top e questo
#: modulo deve restare importabile con un python qualsiasi.
REMOTE_PREFIXES = ('gdrive://', 'dropbox://', 's3://', 'r2://', 'webdav://',
                   'http://', 'https://', 'sftp://', 'cloudinary://',
                   'unibo://')


def _is_remote(path):
    if not path:
        return False
    return any(path.lower().startswith(p) for p in REMOTE_PREFIXES)


def default_media_dest(thumb_path_str):
    """Cartella/URL media di default = parent della cartella thumb.

    'webdav://h:p/pyarchinit_media/thumb/' -> 'webdav://h:p/pyarchinit_media/'
    '/percorso/thumb/'                     -> '/percorso/'
    """
    if not thumb_path_str:
        return ""
    trimmed = thumb_path_str.rstrip("/")
    parent = trimmed.rsplit("/", 1)[0]
    return parent + "/"


def store_media_file(src_path, dest_root, filename):
    """Copia/carica un file nel backend di destinazione. Ritorna il path
    finale. Solleva su errore (chiamare DOPO il commit, mai dentro)."""
    final_path = dest_root.rstrip("/") + "/" + filename
    if _is_remote(final_path):
        storage = _get_storage()
        if storage is None:
            raise RuntimeError("Storage manager non disponibile per "
                               f"destinazione remota {dest_root}")
        with open(src_path, "rb") as fh:
            data = fh.read()
        backend = storage.get_backend(final_path)
        _, _, relative = storage.parse_path(final_path)
        backend.write(relative or filename, data)
    else:
        import shutil
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        if not os.path.exists(final_path):
            shutil.copy2(src_path, final_path)
    return final_path


def import_media(conn, metadata, engine, media_rows, link_rows, us_id_map,
                 qfield_dir, media_dest, result, dry_run, log_fn,
                 copy_media=True):
    """Importa media_table + media_to_entity_table.

    La copia file NON avviene qui: i file da copiare vengono accodati in
    result._pending_copies e copiati da copy_media_files() dopo il commit.
    Ritorna la lista dei record media inseriti (per le thumbnail).
    """
    media_table = reflected(metadata, engine, "media_table")
    link_table = reflected(metadata, engine, "media_to_entity_table")

    existing_paths = {}
    for record in conn.execute(select(media_table.c.id_media,
                                      media_table.c.filepath)):
        existing_paths[normalize_key(record.filepath)] = record.id_media

    inserted_media = []
    media_id_map = {}
    new_media_id = next_id(conn, media_table, "id_media")

    if not hasattr(result, "_pending_copies"):
        result._pending_copies = []

    for row in media_rows:
        try:
            source_id = (row.get("id_media")
                         if row.get("id_media") not in (None, "", 0)
                         else row["_fid"])
            filepath = row.get("filepath") or ""
            filename_full = row.get("filename") or os.path.basename(filepath)
            if "." in os.path.basename(filepath) and not row.get("filetype"):
                row["filetype"] = os.path.basename(filepath).rsplit(".", 1)[1]
            source_file = str(Path(qfield_dir) / filepath)

            final_path = filepath
            if copy_media and media_dest:
                basename = os.path.basename(filepath) or filename_full
                final_path = media_dest.rstrip("/") + "/" + basename
                if os.path.exists(source_file):
                    result._pending_copies.append(
                        (source_file, media_dest, basename))
                else:
                    result.warnings.append(
                        f"Foto {basename} non trovata in {source_file} "
                        "(registro comunque il record)")
                    log_fn(f"  ? Foto {basename} non trovata in {source_file}")

            key = normalize_key(final_path)
            if key in existing_paths:
                media_id_map[source_id] = existing_paths[key]
                result.media.skipped += 1
                log_fn(f"  Media {filename_full} già presente "
                       f"(id_media={existing_paths[key]}): salto")
                continue

            payload = row_payload(row, media_table,
                                  exclude=("id_media", "filepath"))
            payload["id_media"] = new_media_id
            payload["filepath"] = final_path
            if not dry_run:
                conn.execute(media_table.insert().values(**payload))
            existing_paths[key] = new_media_id
            media_id_map[source_id] = new_media_id
            inserted_media.append({
                "id_media": new_media_id,
                "filename": os.path.splitext(
                    os.path.basename(final_path))[0],
                "filetype": payload.get("filetype", ""),
                "filepath": final_path,
                "mediatype": payload.get("mediatype", "image"),
            })
            log_fn(f"  + Media {filename_full} -> id_media={new_media_id}")
            new_media_id += 1
            result.media.inserted += 1
        except Exception as e:
            result.media.errors += 1
            log_fn(f"  ! Media fid={row.get('_fid')}: {e}")

    # collegamenti
    existing_links = set()
    for record in conn.execute(select(link_table.c.id_entity,
                                      link_table.c.entity_type,
                                      link_table.c.id_media)):
        existing_links.add((record.id_entity,
                            normalize_key(record.entity_type),
                            record.id_media))

    link_pk = ("id_mediaToEntity"
               if "id_mediaToEntity" in link_table.columns
               else "id_media_to_entity")
    new_link_id = next_id(conn, link_table, link_pk)
    for row in link_rows:
        try:
            id_entity = us_id_map.get(row.get("id_entity"))
            id_media = media_id_map.get(row.get("id_media"))
            if id_entity is None:
                result.links.skipped += 1
                log_fn("  Collegamento media: id_entity sorgente "
                       f"{row.get('id_entity')} non rimappabile: salto")
                continue
            if id_media is None:
                result.links.skipped += 1
                log_fn("  Collegamento media: id_media sorgente "
                       f"{row.get('id_media')} non rimappabile: salto")
                continue
            entity_type = row.get("entity_type") or "US"
            if (id_entity, normalize_key(entity_type), id_media) in existing_links:
                result.links.skipped += 1
                continue
            payload = row_payload(row, link_table,
                                  exclude=(link_pk, "id_entity", "id_media"))
            payload[link_pk] = new_link_id
            payload["id_entity"] = id_entity
            payload["id_media"] = id_media
            if not dry_run:
                conn.execute(link_table.insert().values(**payload))
            existing_links.add((id_entity, normalize_key(entity_type), id_media))
            log_fn(f"  + Collegamento media {id_media} -> US id_us={id_entity}")
            new_link_id += 1
            result.links.inserted += 1
        except Exception as e:
            result.links.errors += 1
            log_fn(f"  ! Collegamento fid={row.get('_fid')}: {e}")

    return inserted_media


def copy_media_files(result, log_fn):
    """Copia/carica i file accodati da import_media (chiamare DOPO il
    commit). I fallimenti finiscono in result.media_upload_failures."""
    pending = getattr(result, "_pending_copies", [])
    for source_file, dest_root, basename in pending:
        try:
            final = store_media_file(source_file, dest_root, basename)
            log_fn(f"  Foto {basename} -> {final}")
        except Exception as e:
            result.media_upload_failures.append(f"{source_file}: {e}")
            log_fn(f"  ! Copia {basename} fallita: {e}")
    result._pending_copies = []
```

- [ ] **Step 4: Verifica**

Run: `cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" && python3 -m pytest tests/qfield -q`
Expected: 16 passed

- [ ] **Step 5: Commit**

```bash
git -C "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" add modules/utility/qfield_importer.py
git -C "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" -c commit.gpgsign=false commit --no-verify -m "feat(qfield): media + entity links import via StorageManager (local + WebDAV)"
```

---

### Task 5: Thumbnail automatiche per i media importati

**Files:**
- Modify: `modules/utility/qfield_importer.py` (append)
- Test: `tests/qfield/test_thumbs.py`

**Interfaces:**
- Consumes: Task 4 (`inserted_media`: list di dict `{"id_media","filename","filetype","filepath","mediatype"}`), conftest `media_thumb_table`
- Produces: `make_thumbnails(engine, inserted_media, thumb_path_str, thumb_resize_str, result, log_fn, resampler=None) -> None` — `resampler(mid, input_path, infile_name, out_dir, suffix)` iniettabile nei test; default = `Media_utility`/`Media_utility_resize` (lazy import). Convenzione nomi (Image_viewer): `media_thumb_filename = f"{id_media}_{filename}_thumb.png"`, resize `f"{id_media}_{filename}.png"`; in `media_thumb_table` i path sono i soli filename.

- [ ] **Step 1: Scrivi i test failing**

```python
# tests/qfield/test_thumbs.py
from sqlalchemy import text

from modules.utility.qfield_importer import QFieldImportResult, make_thumbnails


def test_make_thumbnails_inserts_rows_with_naming_convention(engine):
    calls = []

    def fake_resampler(mid, ip, i, o, ts):
        calls.append((mid, ip, i, o, ts))

    media = [{"id_media": 42, "filename": "us100", "filetype": "jpg",
              "filepath": "/x/us100.jpg", "mediatype": "image"}]
    res = QFieldImportResult()
    make_thumbnails(engine, media, "/thumb/", "/resize/", res,
                    log_fn=lambda m: None, resampler=fake_resampler)
    assert res.thumbs.inserted == 1
    # due chiamate: thumb + resize, con le convenzioni di Image_viewer
    assert (42, "/x/us100.jpg", "us100", "/thumb/", "_thumb.png") in calls
    assert (42, "/x/us100.jpg", "us100", "/resize/", ".png") in calls
    with engine.connect() as conn:
        r = conn.execute(text(
            "SELECT id_media, media_filename, media_thumb_filename,"
            " filepath, path_resize FROM media_thumb_table")).fetchone()
    assert r[0] == 42 and r[1] == "us100"
    assert r[2] == "42_us100_thumb.png"
    assert r[3] == "42_us100_thumb.png" and r[4] == "42_us100.png"


def test_make_thumbnails_resampler_failure_counts_error(engine):
    def broken(mid, ip, i, o, ts):
        raise RuntimeError("no image")

    media = [{"id_media": 1, "filename": "f", "filetype": "jpg",
              "filepath": "/x/f.jpg", "mediatype": "image"}]
    res = QFieldImportResult()
    make_thumbnails(engine, media, "/t/", "/r/", res,
                    log_fn=lambda m: None, resampler=broken)
    assert res.thumbs.errors == 1 and res.thumbs.inserted == 0
```

- [ ] **Step 2: Verifica che falliscano**

Run: `cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" && python3 -m pytest tests/qfield/test_thumbs.py -q`
Expected: FAIL con ImportError `make_thumbnails`

- [ ] **Step 3: Implementa** (append al modulo)

```python
# --------------------------------------------------------------------------
#  Thumbnail (convenzioni di tabs/Image_viewer.py, glue via reflection)
# --------------------------------------------------------------------------

THUMB_SUFFIX = "_thumb.png"
RESIZE_SUFFIX = ".png"


def _default_resamplers():
    try:
        from modules.utility.pyarchinit_media_utility import (
            Media_utility, Media_utility_resize)
    except ImportError:
        from .pyarchinit_media_utility import Media_utility, Media_utility_resize
    return Media_utility().resample_images, Media_utility_resize().resample_images


def make_thumbnails(engine, inserted_media, thumb_path_str, thumb_resize_str,
                    result, log_fn, resampler=None):
    """Genera thumb+resize e inserisce le righe in media_thumb_table per i
    soli media inseriti. Chiamare DOPO il commit dell'import (transazione
    propria); i fallimenti contano in result.thumbs.errors, non bloccano."""
    if not inserted_media:
        return
    if not thumb_path_str or not thumb_resize_str:
        result.warnings.append(
            "thumb_path/thumb_resize non configurati: thumbnail saltate")
        return
    if resampler is None:
        thumb_fn, resize_fn = _default_resamplers()
    else:
        thumb_fn = resize_fn = resampler

    metadata = MetaData()
    thumb_table = reflected(metadata, engine, "media_thumb_table")
    with engine.begin() as conn:
        new_thumb_id = next_id(conn, thumb_table, "id_media_thumb")
        for m in inserted_media:
            try:
                thumb_fn(m["id_media"], m["filepath"], m["filename"],
                         thumb_path_str, THUMB_SUFFIX)
                resize_fn(m["id_media"], m["filepath"], m["filename"],
                          thumb_resize_str, RESIZE_SUFFIX)
                filename_thumb = f"{m['id_media']}_{m['filename']}{THUMB_SUFFIX}"
                filename_resize = f"{m['id_media']}_{m['filename']}{RESIZE_SUFFIX}"
                conn.execute(thumb_table.insert().values(
                    id_media_thumb=new_thumb_id,
                    id_media=m["id_media"],
                    mediatype=m.get("mediatype", "image"),
                    media_filename=m["filename"],
                    media_thumb_filename=filename_thumb,
                    filetype=m.get("filetype", ""),
                    filepath=filename_thumb,
                    path_resize=filename_resize,
                ))
                log_fn(f"  + Thumbnail {filename_thumb}")
                new_thumb_id += 1
                result.thumbs.inserted += 1
            except Exception as e:
                result.thumbs.errors += 1
                log_fn(f"  ! Thumbnail id_media={m['id_media']}: {e}")
```

- [ ] **Step 4: Verifica**

Run: `cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" && python3 -m pytest tests/qfield -q`
Expected: 18 passed

- [ ] **Step 5: Commit**

```bash
git -C "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" add modules/utility/qfield_importer.py
git -C "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" -c commit.gpgsign=false commit --no-verify -m "feat(qfield): auto thumbnails for imported media (Image_viewer naming convention)"
```

---

### Task 6: Orchestratore `run_qfield_import` + CLI `scripts/import_qfield.py`

**Files:**
- Modify: `modules/utility/qfield_importer.py` (append)
- Create: `scripts/import_qfield.py`
- Test: `tests/qfield/test_run_import.py`

**Interfaces:**
- Consumes: tutte le funzioni Task 1-5
- Produces: `run_qfield_import(db, qfield_dir, *, sito=None, srid=None, dry_run=True, geom_dedup=True, copy_media=True, make_thumbs=True, media_dest=None, thumb_path=None, thumb_resize=None, log=print, layers_override=None, rows_override=None) -> QFieldImportResult`. `db` = engine SQLAlchemy, conn-str, o oggetto con `.engine` (db_manager). `rows_override` = dict `{nome_tabella: rows}` che salta la lettura GPKG (seam per test/GUI-anteprima). `sito_field_for(name) -> str`.

- [ ] **Step 1: Scrivi i test failing**

```python
# tests/qfield/test_run_import.py
from sqlalchemy import text

from modules.utility.qfield_importer import run_qfield_import, sito_field_for


def _rows():
    return {
        "us_table": [{"_fid": 1, "id_us": None, "sito": "F", "area": "1",
                      "us": "100", "d_stratigrafica": "s"}],
        "inventario_materiali_table": [
            {"_fid": 1, "sito": "F", "numero_inventario": "10"}],
        "media_table": [{"_fid": 1, "id_media": 11, "mediatype": "image",
                         "filename": "us100", "filetype": "jpg",
                         "filepath": "DCIM/pyarchinit/us100.jpg"}],
        "media_to_entity_table": [
            {"_fid": 1, "id_entity": 1, "entity_type": "US",
             "table_name": "us_table", "id_media": 11,
             "filepath": "DCIM/pyarchinit/us100.jpg", "media_name": "us100"}],
    }


def test_sito_field_for():
    assert sito_field_for("pyunitastratigrafiche") == "scavo_s"
    assert sito_field_for("pyarchinit_quote") == "sito_q"
    assert sito_field_for("us_table") == "sito"


def test_run_dry_run_counts_but_writes_nothing(engine, tmp_path):
    res = run_qfield_import(engine, str(tmp_path), dry_run=True,
                            copy_media=False, make_thumbs=False,
                            log=lambda m: None, rows_override=_rows())
    assert res.dry_run is True
    assert res.us.inserted == 1 and res.materiali.inserted == 1
    assert res.media.inserted == 1 and res.links.inserted == 1
    with engine.connect() as conn:
        for t in ("us_table", "inventario_materiali_table", "media_table"):
            assert conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar() == 0


def test_run_apply_then_rerun_is_idempotent(engine, tmp_path):
    kw = dict(copy_media=False, make_thumbs=False, log=lambda m: None,
              rows_override=_rows())
    res1 = run_qfield_import(engine, str(tmp_path), dry_run=False, **kw)
    assert res1.us.inserted == 1 and res1.links.inserted == 1
    res2 = run_qfield_import(engine, str(tmp_path), dry_run=False, **kw)
    assert res2.us.inserted == 0 and res2.us.skipped == 1
    assert res2.media.skipped == 1 and res2.links.skipped == 1
    with engine.connect() as conn:
        assert conn.execute(
            text("SELECT COUNT(*) FROM us_table")).scalar() == 1


def test_run_sito_filter(engine, tmp_path):
    rows = _rows()
    rows["us_table"].append({"_fid": 2, "id_us": None, "sito": "Altro",
                             "area": "1", "us": "1"})
    res = run_qfield_import(engine, str(tmp_path), sito="F", dry_run=True,
                            copy_media=False, make_thumbs=False,
                            log=lambda m: None, rows_override=rows)
    assert res.us.inserted == 1  # solo il sito F
```

- [ ] **Step 2: Verifica che falliscano**

Run: `cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" && python3 -m pytest tests/qfield/test_run_import.py -q`
Expected: FAIL con ImportError `run_qfield_import`

- [ ] **Step 3: Implementa l'orchestratore** (append al modulo)

```python
# --------------------------------------------------------------------------
#  Orchestratore
# --------------------------------------------------------------------------

def sito_field_for(table_name):
    return {"pyunitastratigrafiche": "scavo_s",
            "pyarchinit_quote": "sito_q"}.get(table_name, "sito")


def _resolve_engine(db):
    """Accetta engine, conn-str o oggetto con .engine (db_manager)."""
    if isinstance(db, str):
        return create_engine(db)
    if hasattr(db, "engine"):
        return db.engine
    return db


def _wire_spatialite(engine, warnings):
    if engine.dialect.name != "sqlite":
        return
    from sqlalchemy import event

    @event.listens_for(engine, "connect")
    def _load_spatialite(dbapi_conn, _record):
        try:
            dbapi_conn.enable_load_extension(True)
            dbapi_conn.load_extension("mod_spatialite")
        except Exception as error:
            warnings.append(f"mod_spatialite non caricato ({error}): "
                            "import geometrie non disponibile su SpatiaLite")


def run_qfield_import(db, qfield_dir, *, sito=None, srid=None, dry_run=True,
                      geom_dedup=True, copy_media=True, make_thumbs=True,
                      media_dest=None, thumb_path=None, thumb_resize=None,
                      log=print, layers_override=None, rows_override=None):
    """Esegue l'intero import QField. Vedi spec 2026-07-21.

    Scritture DB in un'unica transazione (dry_run -> rollback).
    Copia foto e thumbnail avvengono DOPO il commit e non lo annullano.
    """
    result = QFieldImportResult()
    result.dry_run = dry_run
    engine = _resolve_engine(db)

    # --- lettura sorgenti -------------------------------------------------
    if rows_override is not None:
        data = {name: list(rows_override.get(name, []))
                for name in SOURCE_TABLES}
    else:
        layers = layers_override or find_gpkg_layers(qfield_dir)
        if not layers:
            raise QFieldImportError(
                "Nessun layer pyArchInit trovato nei GPKG della cartella")
        log("Layer trovati:")
        for name, (path, layer_name) in layers.items():
            log(f"  {name:<28} {path} ({layer_name})")
        data = {}
        for name in SOURCE_TABLES:
            if name not in layers:
                data[name] = []
                continue
            path, layer_name = layers[name]
            with_geom = name in ("pyunitastratigrafiche", "pyarchinit_quote")
            data[name] = read_features(
                path, layer_name, with_geometry=with_geom,
                force_multi=(name == "pyunitastratigrafiche"))

    if sito:
        wanted = str(sito).strip()
        for name in ("us_table", "inventario_materiali_table",
                     "pyunitastratigrafiche", "pyarchinit_quote"):
            f = sito_field_for(name)
            data[name] = [r for r in data[name]
                          if normalize_key(r.get(f)) == wanted]
        # media/link non filtrati: passano dalla rimappatura id

    log(f"\nRecord letti: {len(data['us_table'])} US, "
        f"{len(data['inventario_materiali_table'])} reperti, "
        f"{len(data['pyunitastratigrafiche'])} geometrie, "
        f"{len(data['pyarchinit_quote'])} quote, "
        f"{len(data['media_table'])} media, "
        f"{len(data['media_to_entity_table'])} collegamenti")
    if dry_run:
        log(">>> DRY RUN: nessuna scrittura sul database <<<")

    _wire_spatialite(engine, result.warnings)
    metadata = MetaData()
    inserted_media = []

    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            log("\n== us_table ==")
            us_id_map = import_us(conn, metadata, engine, data["us_table"],
                                  result, dry_run, log)

            log("\n== inventario_materiali_table ==")
            import_materiali(conn, metadata, engine,
                             data["inventario_materiali_table"],
                             result, dry_run, log)

            if data["pyunitastratigrafiche"]:
                log("\n== pyunitastratigrafiche ==")
                import_geometrie(conn, metadata, engine,
                                 data["pyunitastratigrafiche"], result,
                                 dry_run, log, dedup=geom_dedup,
                                 srid_override=srid)

            if data["pyarchinit_quote"]:
                log("\n== pyarchinit_quote ==")
                import_quote(conn, metadata, engine, data["pyarchinit_quote"],
                             result, dry_run, log, srid_override=srid)

            if data["media_table"] or data["media_to_entity_table"]:
                log("\n== media_table / media_to_entity_table ==")
                inserted_media = import_media(
                    conn, metadata, engine, data["media_table"],
                    data["media_to_entity_table"], us_id_map, qfield_dir,
                    media_dest, result, dry_run, log, copy_media=copy_media)

            if dry_run:
                log("\nDRY RUN completato: rollback della transazione.")
                transaction.rollback()
            else:
                transaction.commit()
        except Exception:
            transaction.rollback()
            raise

    # --- post-commit: file e thumbnail (mai dentro la transazione) --------
    if not dry_run:
        if copy_media:
            copy_media_files(result, log)
        if make_thumbs and inserted_media:
            log("\n== thumbnails ==")
            make_thumbnails(engine, inserted_media, thumb_path, thumb_resize,
                            result, log)

    log("\n================= RIEPILOGO =================")
    for line in result.summary_lines():
        log(line)
    if result.media_upload_failures:
        log("\nFile NON copiati (da recuperare a mano):")
        for f in result.media_upload_failures:
            log(f"  - {f}")
    if not dry_run:
        log("\nFatto. Ricontrolla i rapporti stratigrafici delle US importate.")
    return result
```

- [ ] **Step 4: Verifica orchestratore**

Run: `cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" && python3 -m pytest tests/qfield -q`
Expected: 22 passed

- [ ] **Step 5: Crea il CLI**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import_qfield.py — CLI per importare i dati QField nel DB pyArchInit.

Wrapper sottile su modules.utility.qfield_importer.run_qfield_import.
DRY-RUN È IL DEFAULT: usare --apply per scrivere davvero.

Esempi:
  # anteprima sul DB configurato nel plugin (config.cfg)
  python3 scripts/import_qfield.py --qfield-dir ~/qfield/scavo2026

  # import vero su PostGIS esplicito, foto su WebDAV di default
  python3 scripts/import_qfield.py --qfield-dir ~/qfield/scavo2026 \
      --conn-str postgresql://user:pw@host:5432/pyarchinit --apply

  # SpatiaLite esplicito, senza thumbnails
  python3 scripts/import_qfield.py --qfield-dir ~/qfield/scavo2026 \
      --db /percorso/pyarchinit_db.sqlite --apply --no-thumbs
"""
import argparse
import sys
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent.parent
if str(PLUGIN_DIR) not in sys.path:
    sys.path.insert(0, str(PLUGIN_DIR))

from modules.utility.qfield_importer import (  # noqa: E402
    QFieldImportError, default_media_dest, run_qfield_import,
)


def _plugin_conn():
    """(conn_str, thumb_path, thumb_resize) dal config.cfg del plugin."""
    from modules.db.pyarchinit_conn_strings import Connection
    conn = Connection()
    return (conn.conn_str(),
            conn.thumb_path()["thumb_path"],
            conn.thumb_resize()["thumb_resize"])


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Importa i dati QField (pyarchinit-qfield) nel DB "
                    "pyArchInit. Dry-run di default: --apply per scrivere.")
    parser.add_argument("--qfield-dir", required=True,
                        help="Cartella del progetto QField (contiene i .gpkg)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--db", help="Percorso SQLite/SpatiaLite")
    group.add_argument("--conn-str", help="postgresql://user:pw@host/db")
    parser.add_argument("--apply", action="store_true",
                        help="Scrive davvero (default: dry-run)")
    parser.add_argument("--sito", default=None)
    parser.add_argument("--srid", type=int, default=None)
    parser.add_argument("--media-dest", default=None,
                        help="Cartella/URL destinazione foto "
                             "(default: parent della cartella thumb)")
    parser.add_argument("--no-geom-dedup", action="store_true")
    parser.add_argument("--no-media", action="store_true",
                        help="Non copiare le foto")
    parser.add_argument("--no-thumbs", action="store_true",
                        help="Non generare thumbnail")
    args = parser.parse_args(argv)

    if not Path(args.qfield_dir).is_dir():
        sys.exit(f"Cartella non trovata: {args.qfield_dir}")

    thumb_path = thumb_resize = None
    if args.db:
        db = f"sqlite:///{Path(args.db).expanduser().resolve()}"
    elif args.conn_str:
        db = args.conn_str
    else:
        db, thumb_path, thumb_resize = _plugin_conn()
    if thumb_path is None:
        try:
            _, thumb_path, thumb_resize = _plugin_conn()
        except Exception:
            thumb_path = thumb_resize = ""

    media_dest = args.media_dest or default_media_dest(thumb_path or "")

    try:
        result = run_qfield_import(
            db, args.qfield_dir, sito=args.sito, srid=args.srid,
            dry_run=not args.apply, geom_dedup=not args.no_geom_dedup,
            copy_media=not args.no_media, make_thumbs=not args.no_thumbs,
            media_dest=media_dest, thumb_path=thumb_path,
            thumb_resize=thumb_resize)
    except QFieldImportError as e:
        sys.exit(f"Errore: {e}")

    errors = (result.us.errors + result.materiali.errors +
              result.geometrie.errors + result.quote.errors +
              result.media.errors + result.links.errors)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 6: Test CLI (aggiungi in fondo a `tests/qfield/test_run_import.py`)**

```python
def test_cli_dry_run_on_sqlite(tmp_path):
    import sqlite3
    import subprocess
    import sys as _sys
    from tests.qfield.conftest import SCHEMA, PLUGIN_DIR
    db = tmp_path / "t.sqlite"
    c = sqlite3.connect(db)
    for ddl in SCHEMA:
        c.execute(ddl)
    c.commit(); c.close()
    (tmp_path / "empty_qfield").mkdir()
    proc = subprocess.run(
        [_sys.executable, "scripts/import_qfield.py",
         "--qfield-dir", str(tmp_path / "empty_qfield"), "--db", str(db)],
        capture_output=True, text=True, cwd=PLUGIN_DIR)
    # cartella senza GPKG -> errore strutturale pulito, exit != 0
    assert proc.returncode != 0
    assert "Nessun layer" in (proc.stdout + proc.stderr)
```

- [ ] **Step 7: Verifica tutto**

Run: `cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" && python3 -m pytest tests/qfield -q`
Expected: 23 passed

- [ ] **Step 8: Commit**

```bash
git -C "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" add modules/utility/qfield_importer.py scripts/import_qfield.py
git -C "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" -c commit.gpgsign=false commit --no-verify -m "feat(qfield): run_qfield_import orchestrator + import_qfield CLI (dry-run default)"
```

---

### Task 7: Dialog GUI `gui/qfield_import_dialog.py`

**Files:**
- Create: `gui/qfield_import_dialog.py`
- Test: `tests/qfield/test_dialog_import.py` (solo sanity import headless)

**Interfaces:**
- Consumes: `run_qfield_import`, `find_gpkg_layers`, `read_features`, `default_media_dest`, `sito_field_for`, `QFieldImportError` (Task 6); `Connection` + `get_db_manager` (pattern `rapporti_check_dialog.py:56-64`)
- Produces: `QFieldImportDialog(QDialog)` con costruttore `(db_manager=None, parent=None)`; usato dal Task 8

- [ ] **Step 1: Scrivi il dialog completo**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dialog "Importa da QField" — GUI sopra modules.utility.qfield_importer.

Anteprima (dry-run) e Importa girano nello stesso worker QThread: QGIS non
si blocca durante la copia foto/WebDAV. DB risolto dal config del plugin
(pattern rapporti_check_dialog): nessun campo URL in interfaccia.
"""

import os

from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QCheckBox, QDialog, QFileDialog, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QMessageBox, QProgressBar, QPushButton,
    QTextEdit, QVBoxLayout)
from qgis.core import QgsSettings

TRANSLATIONS = {
    'window_title': {
        'it': "Importa da QField - PyArchInit",
        'en': "Import from QField - PyArchInit",
        'de': "Aus QField importieren - PyArchInit",
        'es': "Importar desde QField - PyArchInit",
        'fr': "Importer depuis QField - PyArchInit",
        'ar': "استيراد من QField - PyArchInit",
        'ca': "Importa des de QField - PyArchInit",
        'ro': "Import din QField - PyArchInit",
        'pt': "Importar do QField - PyArchInit",
        'el': "Εισαγωγή από QField - PyArchInit",
    },
    'qfield_dir': {
        'it': "Cartella progetto QField:", 'en': "QField project folder:",
        'de': "QField-Projektordner:", 'es': "Carpeta del proyecto QField:",
        'fr': "Dossier du projet QField :", 'ar': "مجلد مشروع QField:",
        'ca': "Carpeta del projecte QField:", 'ro': "Folder proiect QField:",
        'pt': "Pasta do projeto QField:", 'el': "Φάκελος έργου QField:",
    },
    'browse': {
        'it': "Sfoglia…", 'en': "Browse…", 'de': "Durchsuchen…",
        'es': "Examinar…", 'fr': "Parcourir…", 'ar': "تصفح…",
        'ca': "Navega…", 'ro': "Răsfoiește…", 'pt': "Procurar…",
        'el': "Αναζήτηση…",
    },
    'site': {
        'it': "Sito:", 'en': "Site:", 'de': "Fundort:", 'es': "Sitio:",
        'fr': "Site :", 'ar': "الموقع:", 'ca': "Jaciment:", 'ro': "Sit:",
        'pt': "Sítio:", 'el': "Θέση:",
    },
    'all_sites': {
        'it': "Tutti i siti", 'en': "All sites", 'de': "Alle Fundorte",
        'es': "Todos los sitios", 'fr': "Tous les sites",
        'ar': "كل المواقع", 'ca': "Tots els jaciments",
        'ro': "Toate siturile", 'pt': "Todos os sítios",
        'el': "Όλες οι θέσεις",
    },
    'srid': {
        'it': "SRID (vuoto = dal GPKG):", 'en': "SRID (empty = from GPKG):",
        'de': "SRID (leer = aus GPKG):", 'es': "SRID (vacío = del GPKG):",
        'fr': "SRID (vide = du GPKG) :", 'ar': "SRID (فارغ = من GPKG):",
        'ca': "SRID (buit = del GPKG):", 'ro': "SRID (gol = din GPKG):",
        'pt': "SRID (vazio = do GPKG):", 'el': "SRID (κενό = από GPKG):",
    },
    'media_dest': {
        'it': "Destinazione foto:", 'en': "Photo destination:",
        'de': "Foto-Ziel:", 'es': "Destino de fotos:",
        'fr': "Destination des photos :", 'ar': "وجهة الصور:",
        'ca': "Destinació de fotos:", 'ro': "Destinație foto:",
        'pt': "Destino das fotos:", 'el': "Προορισμός φωτογραφιών:",
    },
    'opt_geom_dedup': {
        'it': "Deduplica geometrie", 'en': "Deduplicate geometries",
        'de': "Geometrien deduplizieren", 'es': "Deduplicar geometrías",
        'fr': "Dédupliquer les géométries", 'ar': "إزالة تكرار الأشكال",
        'ca': "Dedueix geometries", 'ro': "Deduplică geometriile",
        'pt': "Desduplicar geometrias", 'el': "Αφαίρεση διπλών γεωμετριών",
    },
    'opt_copy_media': {
        'it': "Copia foto", 'en': "Copy photos", 'de': "Fotos kopieren",
        'es': "Copiar fotos", 'fr': "Copier les photos", 'ar': "نسخ الصور",
        'ca': "Copia fotos", 'ro': "Copiază fotografiile",
        'pt': "Copiar fotos", 'el': "Αντιγραφή φωτογραφιών",
    },
    'opt_thumbs': {
        'it': "Genera thumbnail", 'en': "Generate thumbnails",
        'de': "Thumbnails erzeugen", 'es': "Generar miniaturas",
        'fr': "Générer les vignettes", 'ar': "إنشاء مصغرات",
        'ca': "Genera miniatures", 'ro': "Generează miniaturi",
        'pt': "Gerar miniaturas", 'el': "Δημιουργία μικρογραφιών",
    },
    'preview': {
        'it': "Anteprima (dry-run)", 'en': "Preview (dry-run)",
        'de': "Vorschau (Testlauf)", 'es': "Vista previa (simulación)",
        'fr': "Aperçu (simulation)", 'ar': "معاينة (تجريبي)",
        'ca': "Previsualització (simulació)", 'ro': "Previzualizare (test)",
        'pt': "Pré-visualização (simulação)", 'el': "Προεπισκόπηση (δοκιμή)",
    },
    'import_btn': {
        'it': "Importa", 'en': "Import", 'de': "Importieren",
        'es': "Importar", 'fr': "Importer", 'ar': "استيراد",
        'ca': "Importa", 'ro': "Importă", 'pt': "Importar",
        'el': "Εισαγωγή",
    },
    'close': {
        'it': "Chiudi", 'en': "Close", 'de': "Schließen", 'es': "Cerrar",
        'fr': "Fermer", 'ar': "إغلاق", 'ca': "Tanca", 'ro': "Închide",
        'pt': "Fechar", 'el': "Κλείσιμο",
    },
    'confirm_import': {
        'it': "Confermi l'import nel database corrente? L'operazione "
              "aggiunge record e riempie i campi vuoti delle schede "
              "esistenti (mai sovrascrive valori).",
        'en': "Confirm import into the current database? The operation "
              "appends records and fills empty fields of existing sheets "
              "(never overwrites values).",
        'de': "Import in die aktuelle Datenbank bestätigen? Es werden "
              "Datensätze angehängt und leere Felder gefüllt (nie "
              "überschrieben).",
        'es': "¿Confirmar la importación en la base de datos actual? "
              "Añade registros y rellena campos vacíos (nunca sobrescribe).",
        'fr': "Confirmer l'import dans la base actuelle ? Ajoute des "
              "enregistrements et remplit les champs vides (jamais "
              "d'écrasement).",
        'ar': "تأكيد الاستيراد إلى قاعدة البيانات الحالية؟ تضاف السجلات "
              "وتملأ الحقول الفارغة فقط (لا استبدال).",
        'ca': "Confirmes la importació a la base de dades actual? Afegeix "
              "registres i omple camps buits (mai sobreescriu).",
        'ro': "Confirmi importul în baza de date curentă? Adaugă "
              "înregistrări și completează câmpurile goale (nu suprascrie).",
        'pt': "Confirmar a importação na base de dados atual? Acrescenta "
              "registos e preenche campos vazios (nunca sobrescreve).",
        'el': "Επιβεβαίωση εισαγωγής στην τρέχουσα βάση; Προσθέτει "
              "εγγραφές και συμπληρώνει κενά πεδία (ποτέ αντικατάσταση).",
    },
    'error': {
        'it': "Errore", 'en': "Error", 'de': "Fehler", 'es': "Error",
        'fr': "Erreur", 'ar': "خطأ", 'ca': "Error", 'ro': "Eroare",
        'pt': "Erro", 'el': "Σφάλμα",
    },
    'done': {
        'it': "Import completato", 'en': "Import complete",
        'de': "Import abgeschlossen", 'es': "Importación completada",
        'fr': "Import terminé", 'ar': "اكتمل الاستيراد",
        'ca': "Importació completada", 'ro': "Import finalizat",
        'pt': "Importação concluída", 'el': "Η εισαγωγή ολοκληρώθηκε",
    },
    'choose_dir_first': {
        'it': "Scegli prima la cartella del progetto QField.",
        'en': "Choose the QField project folder first.",
        'de': "Wähle zuerst den QField-Projektordner.",
        'es': "Elige primero la carpeta del proyecto QField.",
        'fr': "Choisissez d'abord le dossier du projet QField.",
        'ar': "اختر مجلد مشروع QField أولاً.",
        'ca': "Tria primer la carpeta del projecte QField.",
        'ro': "Alege mai întâi folderul proiectului QField.",
        'pt': "Escolha primeiro a pasta do projeto QField.",
        'el': "Επιλέξτε πρώτα τον φάκελο του έργου QField.",
    },
}


def _lang():
    code = QgsSettings().value("locale/userLocale", "it", type=str)[:2]
    return code if code in ('it', 'en', 'de', 'es', 'fr',
                            'ar', 'ca', 'ro', 'pt', 'el') else 'en'


class QFieldImportWorker(QThread):
    """Esegue scan/anteprima/import fuori dal main thread."""
    log_message = pyqtSignal(str)
    finished_ok = pyqtSignal(object)   # QFieldImportResult
    failed = pyqtSignal(str)

    def __init__(self, db_manager, params, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.params = params

    def run(self):
        try:
            from ..modules.utility.qfield_importer import run_qfield_import
        except ImportError:
            from modules.utility.qfield_importer import run_qfield_import
        try:
            result = run_qfield_import(
                self.db_manager, self.params["qfield_dir"],
                sito=self.params["sito"], srid=self.params["srid"],
                dry_run=self.params["dry_run"],
                geom_dedup=self.params["geom_dedup"],
                copy_media=self.params["copy_media"],
                make_thumbs=self.params["make_thumbs"],
                media_dest=self.params["media_dest"],
                thumb_path=self.params["thumb_path"],
                thumb_resize=self.params["thumb_resize"],
                log=self.log_message.emit)
            self.finished_ok.emit(result)
        except Exception as e:
            self.failed.emit(str(e))


class QFieldImportDialog(QDialog):
    """Importa da QField. db_manager opzionale: se assente si auto-risolve
    dal config del plugin (pattern rapporti_check_dialog)."""

    def __init__(self, db_manager=None, parent=None):
        super().__init__(parent)
        self.L = _lang()
        self.worker = None
        self._thumb_path = ""
        self._thumb_resize = ""
        self.db_manager = db_manager or self._resolve_db()
        self.setWindowTitle(self.tr_('window_title'))
        self.resize(760, 620)
        self._build_ui()

    def tr_(self, key):
        entry = TRANSLATIONS.get(key, {})
        return entry.get(self.L, entry.get('en', key))

    # -- setup -------------------------------------------------------------

    def _resolve_db(self):
        try:
            from ..modules.db.pyarchinit_conn_strings import Connection
            from ..modules.db.pyarchinit_db_manager import get_db_manager
        except ImportError:
            from modules.db.pyarchinit_conn_strings import Connection
            from modules.db.pyarchinit_db_manager import get_db_manager
        conn = Connection()
        self._thumb_path = conn.thumb_path().get("thumb_path", "")
        self._thumb_resize = conn.thumb_resize().get("thumb_resize", "")
        return get_db_manager(conn.conn_str(), use_singleton=True)

    def _build_ui(self):
        try:
            from ..modules.utility.qfield_importer import default_media_dest
        except ImportError:
            from modules.utility.qfield_importer import default_media_dest

        layout = QVBoxLayout(self)

        grid = QGridLayout()
        grid.addWidget(QLabel(self.tr_('qfield_dir')), 0, 0)
        self.dir_edit = QLineEdit()
        grid.addWidget(self.dir_edit, 0, 1)
        browse = QPushButton(self.tr_('browse'))
        browse.clicked.connect(self._choose_dir)
        grid.addWidget(browse, 0, 2)

        grid.addWidget(QLabel(self.tr_('site')), 1, 0)
        self.site_combo = QComboBox()
        self.site_combo.addItem(self.tr_('all_sites'), None)
        grid.addWidget(self.site_combo, 1, 1)

        grid.addWidget(QLabel(self.tr_('srid')), 2, 0)
        self.srid_edit = QLineEdit()
        grid.addWidget(self.srid_edit, 2, 1)

        grid.addWidget(QLabel(self.tr_('media_dest')), 3, 0)
        self.media_dest_edit = QLineEdit(
            default_media_dest(self._thumb_path))
        grid.addWidget(self.media_dest_edit, 3, 1)
        layout.addLayout(grid)

        opts = QGroupBox()
        opts_layout = QHBoxLayout(opts)
        self.geom_dedup_check = QCheckBox(self.tr_('opt_geom_dedup'))
        self.geom_dedup_check.setChecked(True)
        self.copy_media_check = QCheckBox(self.tr_('opt_copy_media'))
        self.copy_media_check.setChecked(True)
        self.thumbs_check = QCheckBox(self.tr_('opt_thumbs'))
        self.thumbs_check.setChecked(True)
        for w in (self.geom_dedup_check, self.copy_media_check,
                  self.thumbs_check):
            opts_layout.addWidget(w)
        layout.addWidget(opts)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view, stretch=1)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        layout.addWidget(self.progress)

        buttons = QHBoxLayout()
        self.preview_btn = QPushButton(self.tr_('preview'))
        self.preview_btn.clicked.connect(lambda: self._start(dry_run=True))
        self.import_btn = QPushButton(self.tr_('import_btn'))
        self.import_btn.clicked.connect(lambda: self._start(dry_run=False))
        close_btn = QPushButton(self.tr_('close'))
        close_btn.clicked.connect(self.close)
        buttons.addWidget(self.preview_btn)
        buttons.addWidget(self.import_btn)
        buttons.addStretch()
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)

    # -- interazioni ---------------------------------------------------------

    def _choose_dir(self):
        directory = QFileDialog.getExistingDirectory(
            self, self.tr_('qfield_dir'), os.path.expanduser("~"))
        if not directory:
            return
        self.dir_edit.setText(directory)
        self._scan_sites(directory)

    def _scan_sites(self, directory):
        """Popola la combo siti dai GPKG (scan veloce, main thread ok)."""
        try:
            from ..modules.utility.qfield_importer import (
                find_gpkg_layers, read_features, sito_field_for)
        except ImportError:
            from modules.utility.qfield_importer import (
                find_gpkg_layers, read_features, sito_field_for)
        self.site_combo.clear()
        self.site_combo.addItem(self.tr_('all_sites'), None)
        try:
            layers = find_gpkg_layers(directory)
            self.log_view.append("Layer trovati:")
            sites = set()
            for name, (path, layer_name) in layers.items():
                self.log_view.append(f"  {name}: {os.path.basename(path)}")
                if name == "us_table":
                    f = sito_field_for(name)
                    for r in read_features(path, layer_name):
                        v = r.get(f)
                        if v:
                            sites.add(str(v).strip())
            for s in sorted(sites):
                self.site_combo.addItem(s, s)
        except Exception as e:
            self.log_view.append(f"Scan fallito: {e}")

    def _params(self, dry_run):
        srid_text = self.srid_edit.text().strip()
        return {
            "qfield_dir": self.dir_edit.text().strip(),
            "sito": self.site_combo.currentData(),
            "srid": int(srid_text) if srid_text else None,
            "dry_run": dry_run,
            "geom_dedup": self.geom_dedup_check.isChecked(),
            "copy_media": self.copy_media_check.isChecked(),
            "make_thumbs": self.thumbs_check.isChecked(),
            "media_dest": self.media_dest_edit.text().strip() or None,
            "thumb_path": self._thumb_path,
            "thumb_resize": self._thumb_resize,
        }

    def _start(self, dry_run):
        if not self.dir_edit.text().strip():
            QMessageBox.warning(self, self.tr_('error'),
                                self.tr_('choose_dir_first'))
            return
        if not dry_run:
            reply = QMessageBox.question(
                self, self.tr_('import_btn'), self.tr_('confirm_import'),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return
        self.log_view.clear()
        self._set_running(True)
        self.worker = QFieldImportWorker(self.db_manager,
                                         self._params(dry_run), self)
        self.worker.log_message.connect(self.log_view.append)
        self.worker.finished_ok.connect(self._on_done)
        self.worker.failed.connect(self._on_failed)
        self.worker.start()

    def _set_running(self, running):
        for w in (self.preview_btn, self.import_btn, self.dir_edit,
                  self.site_combo, self.srid_edit, self.media_dest_edit,
                  self.geom_dedup_check, self.copy_media_check,
                  self.thumbs_check):
            w.setEnabled(not running)
        self.progress.setVisible(running)

    def _on_done(self, result):
        self._set_running(False)
        if not result.dry_run:
            QMessageBox.information(self, self.tr_('done'),
                                    "\n".join(result.summary_lines()))

    def _on_failed(self, message):
        self._set_running(False)
        QMessageBox.critical(self, self.tr_('error'), message)
```

- [ ] **Step 2: Test sanity headless (il modulo GUI non deve rompere l'import del pacchetto)**

```python
# tests/qfield/test_dialog_import.py
import ast
import os

import pytest

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIALOG = os.path.join(PLUGIN_DIR, 'gui', 'qfield_import_dialog.py')


def test_dialog_syntax_ok():
    ast.parse(open(DIALOG).read())


def test_translations_cover_10_languages():
    tree = ast.parse(open(DIALOG).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and \
                getattr(node.targets[0], 'id', '') == 'TRANSLATIONS':
            d = ast.literal_eval(node.value)
            for key, entry in d.items():
                assert set(entry) == {'it', 'en', 'de', 'es', 'fr',
                                      'ar', 'ca', 'ro', 'pt', 'el'}, key
            return
    pytest.fail("TRANSLATIONS non trovato")
```

- [ ] **Step 3: Verifica**

Run: `cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" && python3 -m pytest tests/qfield -q`
Expected: 25 passed

- [ ] **Step 4: Commit**

```bash
git -C "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" add gui/qfield_import_dialog.py
git -C "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" -c commit.gpgsign=false commit --no-verify -m "feat(qfield): import dialog — QThread worker, dry-run preview, 10-language i18n"
```

---

### Task 8: Voce di menu + verifica finale

**Files:**
- Modify: `pyarchinitPlugin.py` (dentro `_init_migrations_menu()`, dopo l'ultima QAction esistente, ~line 2808; il numero esatto va verificato con `grep -n "_init_migrations_menu" pyarchinitPlugin.py`)

**Interfaces:**
- Consumes: `QFieldImportDialog` (Task 7)
- Produces: voce menu "Importa da QField (GPKG)" + handler `_open_qfield_import`

- [ ] **Step 1: Aggiungi la QAction** (dentro `_init_migrations_menu`, stesso pattern delle 6 esistenti, prima della chiusura del try)

```python
            # --- Importa da QField (GPKG) --------------------------------
            self.actionQFieldImport = QAction(
                "Importa da QField (GPKG)",
                self.iface.mainWindow())
            self.actionQFieldImport.triggered.connect(
                self._open_qfield_import)
            self.iface.addPluginToMenu(
                "&pyArchInit - Archaeological GIS Tools",
                self.actionQFieldImport)
```

- [ ] **Step 2: Aggiungi l'handler** (metodo della classe plugin, accanto a `_run_uuid_backfill_migration`)

```python
    def _open_qfield_import(self):
        """Apre il dialog Importa da QField (DB auto-risolto dal config)."""
        try:
            from .gui.qfield_import_dialog import QFieldImportDialog
        except ImportError:
            from gui.qfield_import_dialog import QFieldImportDialog
        try:
            dialog = QFieldImportDialog(parent=self.iface.mainWindow())
            dialog.exec()
        except Exception as e:
            from qgis.PyQt.QtWidgets import QMessageBox
            QMessageBox.critical(
                self.iface.mainWindow(), "Importa da QField",
                f"Impossibile aprire il dialog:\n{e}")
```

Verifica anche che la QAction venga rimossa in `unload()`: cerca il blocco dove le action Migrazioni vengono rimosse (`grep -n "removePluginMenu" pyarchinitPlugin.py`) e aggiungi lì:

```python
        if hasattr(self, 'actionQFieldImport'):
            self.iface.removePluginMenu(
                "&pyArchInit - Archaeological GIS Tools",
                self.actionQFieldImport)
```

- [ ] **Step 3: Syntax check + suite completa**

Run:
```bash
cd "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit"
python3 -c "import ast; ast.parse(open('pyarchinitPlugin.py').read()); print('OK')"
python3 -m pytest tests/qfield tests/sync tests/migrations tests/modules -q
```
Expected: `OK`; tests/qfield tutti verdi; tests/sync+migrations+modules con gli stessi fail/error pre-esistenti del baseline (9 failed/14 errors al 2026-07-20, tutti ambiente PG locale/qgis) — ZERO nuovi fail.

- [ ] **Step 4: Commit**

```bash
git -C "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" add pyarchinitPlugin.py
git -C "/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit" -c commit.gpgsign=false commit --no-verify -m "feat(qfield): 'Importa da QField (GPKG)' menu entry"
```

- [ ] **Step 5: Verifica manuale in QGIS (utente)**

Chiedere a Enzo di: ricaricare il plugin, aprire menu → "Importa da QField (GPKG)", scegliere una cartella progetto QField reale, eseguire **Anteprima** e verificare conteggi + campi fill-empty nel log; poi Importa su DB di test (villa_romana o copia), controllare foto in scheda US e thumbnail nel Media Manager.

- [ ] **Step 6: Changelog + tutorial (obbligatori da CLAUDE.md)**

Al termine (feature user-facing): invocare `tutorial-updater` (10 lingue, nuova voce menu + dialog) e poi l'agente changelog (entry bilingue IT/EN con i 4 commit). Se gli agenti non sono registrati nella sessione, usare un agente general-purpose con le stesse istruzioni (come fatto il 2026-07-20).

---

## Note per l'esecutore

- Il numero di riga esatto di `_init_migrations_menu` può essere slittato: ancorarsi SEMPRE con grep, mai fidarsi dei numeri.
- `tests/qfield/` NON si committa (`/tests/*` gitignorato) — i comandi git dei task non lo includono mai.
- Se un test `tests/sync`/`tests/migrations` fallisce, confrontare col baseline del 2026-07-20 (9 failed/14 errors, env) prima di attribuirlo a queste modifiche.
- La GUI non ha test automatici oltre syntax/i18n: la verifica funzionale è manuale in QGIS (Task 8 Step 5).
