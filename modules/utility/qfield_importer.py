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


# --------------------------------------------------------------------------
#  Import US + reperti (con policy fill-empty)
# --------------------------------------------------------------------------

def fill_empty_fields(conn, table, pk_name, pk_value, db_row, src_row,
                      result, counts, table_label, key_label, dry_run, log_fn):
    """Riempi i soli campi vuoti del record DB con i valori dal campo.

    db_row: dict colonna->valore del record esistente nel DB.
    Ritorna il dict updates applicato (vuoto se nessun campo è stato
    riempito) e aggiorna counts.updated di 1 se almeno un campo è stato
    riempito. Il chiamante deve usare il dict ritornato per rinfrescare
    la propria cache `existing[key]`, così una riga successiva con la
    stessa chiave non trova più questi campi come vuoti.
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
        return updates
    if not dry_run:
        with conn.begin_nested():
            conn.execute(table.update()
                         .where(table.c[pk_name] == pk_value)
                         .values(**updates))
    counts.updated += 1
    for name, value in sorted(updates.items()):
        result.filled_fields.append((table.name, key_label, name, value))
        log_fn(f"  ~ {table_label} {key_label}: campo vuoto '{name}' <- {value!r}")
    return updates


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
                updates = fill_empty_fields(
                    conn, table, "id_us", db_row["id_us"], db_row, row,
                    result, result.us, "US", key_label, dry_run, log_fn)
                if updates:
                    existing[key] = {**db_row, **updates}
                else:
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
                with conn.begin_nested():
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
                updates = fill_empty_fields(
                    conn, table, "id_invmat", db_row["id_invmat"], db_row, row,
                    result, result.materiali, "Reperto", key_label,
                    dry_run, log_fn)
                if updates:
                    existing[key] = {**db_row, **updates}
                else:
                    result.materiali.skipped += 1
                    log_fn(f"  Reperto {key_label} già presente: salto")
                continue
            payload = row_payload(row, table, exclude=("id_invmat",))
            payload["id_invmat"] = new_id
            if "node_uuid" in table.columns:
                payload["node_uuid"] = new_node_uuid()
            apply_provenance(payload, table)
            if not dry_run:
                with conn.begin_nested():
                    conn.execute(table.insert().values(**payload))
            existing[key] = dict(payload)
            log_fn(f"  + Reperto {key_label} -> id_invmat={new_id}")
            new_id += 1
            result.materiali.inserted += 1
        except Exception as e:
            result.materiali.errors += 1
            log_fn(f"  ! Reperto fid={row.get('_fid')}: {e}")
