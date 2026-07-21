# Tutorial 38: Import from QField (GPKG)

## Introduction

The **Import from QField (GPKG)** feature brings field data collected with
**QField** — through the companion **pyarchinit-qfield** plugin — into
pyArchInit. The command reads the GeoPackages (`.gpkg`) of the QField project
and the photos taken in the field, and **appends** the records to the pyArchInit
database without duplicating the SU and finds that already exist: for existing
records it fills **only the empty fields**, never overwriting values that are
already present.

The workflow is designed to be **safe**: first you run a **Preview (dry-run)**
that simulates everything without writing anything, then — only after
confirmation — you launch the real **Import** in a single transaction.

> Prerequisite: the data must have been collected in the field with **QField**
> using the companion **pyarchinit-qfield** plugin.

---

## 1. Prerequisites

- Data collected in the field with **QField** through the **pyarchinit-qfield**
  plugin.
- The QField project folder contains the **`.gpkg`** files and the photos under
  **`DCIM/pyarchinit`**.
- A configured pyArchInit database (SQLite/Spatialite or PostgreSQL/PostGIS):
  the DB is **resolved automatically** from the plugin configuration.

---

## 2. Open the dialog

Menu bar **pyArchInit → Import from QField (GPKG)**.

The *Import from QField* dialog opens: QGIS **does not freeze** during the
operation because copying photos and accessing WebDAV run in a separate thread.

---

## 3. Select the QField project folder

1. Click **Browse…** and choose the **QField project folder**.
2. The dialog **scans the GeoPackages** and automatically fills the **Site**
   combo box with the sites it finds.
3. Choose a specific site or leave **All sites** to import everything.

---

## 4. Import options

| Option | Meaning |
|---|---|
| **SRID (empty = from GPKG)** | reference system; leave empty to read it from the GeoPackage |
| **Photo destination** | pre-filled with the configured media folder (local or WebDAV) |
| **Deduplicate geometries** | avoids re-inserting identical geometries already present |
| **Copy photos** | copies the photos to the media backend |
| **Generate thumbnails** | automatically creates photo thumbnails |

The three checkboxes are **enabled by default**.

---

## 5. Preview (dry-run)

Click **Preview (dry-run)**: the entire import is run in **simulation**,
**writing nothing** to the database. The log shows:

- how many **SU**, **finds**, **geometries**, **elevation points**, **photos**
  and **links** would be imported;
- exactly **which empty fields** of existing records would be filled.

This is the step to always use to check the outcome before writing.

---

## 6. Import

Click **Import** (a **confirmation** is requested). The operation:

- **appends** the records in a **single transaction**;
- **does not duplicate** existing SU and finds: it fills **only their empty
  fields**, never overwriting values that are already present;
- **copies the photos** to the media backend and **generates their thumbnails**
  automatically;
- assigns imported records a **`node_uuid`** and marks them with
  **`created_by = 'qfield_import'`**.

---

## 7. After the import

Check the **stratigraphic relationships** of the imported SU: they are **not
derived automatically** and must be completed by hand in the SU form.

---

## 8. Command-line alternative (CLI)

For advanced or headless use a CLI script is available. **Dry-run is the default
behaviour**; add `--apply` to actually write:

```bash
# Preview (dry-run, default)
python3 scripts/import_qfield.py --qfield-dir <folder>

# Real import
python3 scripts/import_qfield.py --qfield-dir <folder> --apply
```

---

*PyArchInit Documentation — July 2026*
