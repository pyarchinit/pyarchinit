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

The command can be reached in **two ways**:

1. **Menu**: **Plugin → pyArchInit - Archaeological GIS Tools → Importa da
   QField (GPKG)**.
2. **Toolbar** (new): in the pyArchInit toolbar, open the **analysis-tools
   drop-down button** — the same one that hosts GeoArchaeo, MoveCost,
   Palimpsest and other tools — and choose **Importa da QField (GPKG)**. The
   entry is easy to spot thanks to its **new dedicated icon**: a green
   QField-style rounded tile with a white map pin descending into an import
   tray.

In both cases the *Import from QField* dialog opens: QGIS **does not freeze**
during the operation because copying photos and accessing WebDAV run in a
separate thread.

---

## 3. Select the source: folder or ZIP archive

1. Click **Browse…** and choose the **QField project folder**, or click
   **ZIP archive…** and choose a **`.zip`** archive of the QField project
   (the file picker filters on `*.zip`). Either way, the chosen path appears
   in the same source field.
2. If you choose a folder, the dialog **scans the GeoPackages** and
   automatically fills the **Site** combo box with the sites it finds.
3. If you choose a ZIP archive, it is **extracted automatically** to a
   temporary folder and the **Site** combo box resets to **All sites** (no
   site pre-scan is performed from a zip): the import (Preview/dry-run or
   Import, photos and thumbnails included) runs on the extracted tree, and
   the temporary folder is **automatically removed** at the end of the run,
   even on error.
4. Choose a specific site or leave **All sites** to import everything.

> While an import is running, both **Browse…** and **ZIP archive…** are
> **disabled**, like all the other dialog controls.

> If the chosen archive is **corrupt or invalid**, a clear error is shown:
> **"Archivio ZIP non valido o corrotto: …"**. If the zip contains no
> **`.gpkg`** file, the usual "no layers found" error is shown instead.

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
behaviour**; add `--apply` to actually write. The `--qfield-dir` parameter
accepts either the **project folder** or a **`.zip`** archive: if it points to
a zip, the archive is extracted automatically to a temporary folder, which is
removed at the end of the run. A source that does not exist exits with the
error **"Sorgente non trovata (cartella o archivio .zip): …"**.

```bash
# Preview (dry-run, default) from a folder
python3 scripts/import_qfield.py --qfield-dir <folder>

# Preview (dry-run, default) from a ZIP archive
python3 scripts/import_qfield.py --qfield-dir <archive.zip>

# Real import
python3 scripts/import_qfield.py --qfield-dir <folder> --apply
```

---

*PyArchInit Documentation — July 2026*
