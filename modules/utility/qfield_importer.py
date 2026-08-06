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
import shutil
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy import MetaData, Table, create_engine, func, select, text

log = logging.getLogger("qfield_importer")


class QFieldImportError(Exception):
    """Errore strutturale: interrompe l'import (rollback totale)."""


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
    #: (source_file, dest_root, basename) accodati da import_media, copiati
    #: da copy_media_files() dopo il commit.
    _pending_copies: list = field(default_factory=list)

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


def _resolve_qfield_source(path):
    """Risolve la sorgente dell'import: cartella o archivio .zip.

    Ritorna (source_dir, cleanup):
    - cartella          -> (path, None)
    - file .zip valido  -> estrae TUTTO l'archivio in una temp dir
                           (prefisso pyarchinit_qfield_zip_) e ritorna
                           (temp_dir, cleanup); cleanup() la rimuove
    - altrimenti        -> ValueError con messaggio esplicito

    extract()/extractall() di zipfile sanificano percorsi assoluti e
    componenti '..': zip-slip coperto dalla stdlib.
    """
    p = Path(path)
    if p.is_dir():
        return str(p), None
    if p.is_file() and p.suffix.lower() == ".zip":
        tmpdir = tempfile.mkdtemp(prefix="pyarchinit_qfield_zip_")

        def cleanup():
            shutil.rmtree(tmpdir, ignore_errors=True)

        try:
            with zipfile.ZipFile(str(p)) as zf:
                zf.extractall(tmpdir)
        except zipfile.BadZipFile as exc:
            cleanup()
            raise ValueError(
                f"Archivio ZIP non valido o corrotto: {path}") from exc
        except Exception:
            cleanup()
            raise
        return tmpdir, cleanup
    raise ValueError(
        f"Sorgente QField non valida (né cartella né archivio .zip): {path}")


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
    # SAVEPOINT per-riga: su PostgreSQL un errore senza savepoint
    # avvelenerebbe l'intera transazione (InFailedSqlTransaction).
    with conn.begin_nested():
        conn.execute(statement,
                     {**payload, "wkt": row["_wkt"], "srid": int(srid)})


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
            basename = None
            if copy_media and media_dest:
                basename = os.path.basename(filepath) or filename_full
                final_path = media_dest.rstrip("/") + "/" + basename

            key = normalize_key(final_path)
            if key in existing_paths:
                media_id_map[source_id] = existing_paths[key]
                result.media.skipped += 1
                log_fn(f"  Media {filename_full} già presente "
                       f"(id_media={existing_paths[key]}): salto")
                continue

            if copy_media and media_dest:
                if os.path.exists(source_file):
                    if not dry_run:
                        result._pending_copies.append(
                            (source_file, media_dest, basename))
                else:
                    result.warnings.append(
                        f"Foto {basename} non trovata in {source_file} "
                        "(registro comunque il record)")
                    log_fn(f"  ? Foto {basename} non trovata in {source_file}")

            payload = row_payload(row, media_table,
                                  exclude=("id_media", "filepath"))
            payload["id_media"] = new_media_id
            payload["filepath"] = final_path
            if not dry_run:
                # SAVEPOINT per-riga (vedi _insert_geom_row): senza, un
                # errore su PG abortirebbe l'intera transazione.
                with conn.begin_nested():
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
                msg = ("Collegamento media: id_entity sorgente "
                       f"{row.get('id_entity')} non rimappabile: salto")
                result.warnings.append(msg)
                log_fn(f"  {msg}")
                continue
            if id_media is None:
                result.links.skipped += 1
                msg = ("Collegamento media: id_media sorgente "
                       f"{row.get('id_media')} non rimappabile: salto")
                result.warnings.append(msg)
                log_fn(f"  {msg}")
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
                with conn.begin_nested():
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
    pending = result._pending_copies
    for source_file, dest_root, basename in pending:
        try:
            final = store_media_file(source_file, dest_root, basename)
            log_fn(f"  Foto {basename} -> {final}")
        except Exception as e:
            result.media_upload_failures.append(f"{source_file}: {e}")
            log_fn(f"  ! Copia {basename} fallita: {e}")
    result._pending_copies = []


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
                with conn.begin_nested():
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
    """Registra il listener 'connect' per mod_spatialite UNA SOLA VOLTA per
    engine (guardia via attributo sull'oggetto engine): con un engine
    riutilizzato tra più import (es. il db_manager di sessione della GUI),
    richiamare questa funzione ad ogni run non deve accumulare listener
    duplicati, ognuno chiuso su una `warnings` list di un run precedente.

    Il flag di fallimento va comunque riportato nel `warnings` del run
    CORRENTE: per questo il controllo `qfield_spatialite_failed` avviene ad
    ogni chiamata, anche quando la registrazione è già stata fatta in un
    run precedente (solo la registrazione del listener è guardata)."""
    if engine.dialect.name != "sqlite":
        return
    if not getattr(engine, "_qfield_spatialite_wired", False):
        engine._qfield_spatialite_wired = True
        from sqlalchemy import event

        @event.listens_for(engine, "connect")
        def _load_spatialite(dbapi_conn, _record):
            try:
                dbapi_conn.enable_load_extension(True)
                dbapi_conn.load_extension("mod_spatialite")
            except Exception as error:
                engine._qfield_spatialite_failed = str(error)
                log.warning("mod_spatialite non caricato (%s): import "
                           "geometrie non disponibile su SpatiaLite", error)

    failed = getattr(engine, "_qfield_spatialite_failed", None)
    if failed:
        warnings.append(f"mod_spatialite non caricato ({failed}): "
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
        layers = (layers_override if layers_override is not None
                  else find_gpkg_layers(qfield_dir))
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
