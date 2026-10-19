# Tutorial 36: Extended Matrix Export and s3dgraphy Bridge

## Introduction

Starting with **5.2.0-alpha** PyArchInit integrates a **bidirectional bridge** with the **s3dgraphy** library (Extended Matrix data model by Emanuel Demetrescu). The bridge allows you to:

- **Export** the stratigraphic diagram as Extended Matrix in **em.json**, the format EMStudio opens (the old GraphML export is retired)
- **Re-import** changes made in yEd (US movements between periods/groups) updating the pyarchinit SQL database
- **Attach paradata** (Author / License / Embargo) at site level
- **Group** SUs by dimension (struttura, area, attivita, settore, ambient, saggio, quad_par or ad-hoc groups)

Current tag: `narrativa-3d-rifiniture-5.13.133-alpha` (2026-10-17).

---

## 1. Requirements

- SQLite/Spatialite **or PostgreSQL/PostGIS** database: the em.json export is the same on both engines (the connection is the project's own; `export_site` accepts `sqlite://` and `postgresql://`)
- **Phase 1 node_uuid migration** applied automatically when the DB is opened
- **EMStudio** to open the em.json (install it from **Extended Matrix → Installa EMStudio…**), or the **Vedi la matrice…** panel inside QGIS, which needs nothing else. **yEd** (https://www.yworks.com/products/yed) is only needed if you import GraphML files drawn there (§5)

> ⚠️ For DBs from before 5.2.0-alpha, the migration may require restarting QGIS.

---

## 2. Export Extended Matrix (green button)

### 2.1 Open the dialog

1. Open the **US Form** for your site
2. Click the green **"Esporta Extended Matrix"** button (under the Rapporti tab)

### 2.2 "Export" tab

The window states at the top what each format is for. It holds:

- **Formati** (Formats): **DOT (Graphviz) — matrice di Harris** and **em.json (Extended Matrix, per EMStudio)**, both checked to start with, plus **Matrice per fasi** (phased matrix, chronological analysis), optional. GraphML is no longer exported: the JSON of this window **is em.json**, the very file the **Extended Matrix → Esporta sito in em.json…** menu produces — same projector, same symbols.
- **Opzioni** (Options): **Controlla la sequenza stratigrafica e segnala i problemi** (check the stratigraphic sequence and report the problems). It is the only option left, and it is really read: unchecked, the check is not run. The two old boxes that spoke to yEd (auto-layout hints, period-based colouring) went away with the GraphML export.
- **Extended Matrix**: four buttons next to the export — **Apri in EMStudio** and **Vedi la matrice** (both light up after a successful em.json export; the second one draws the matrix inside QGIS, without EMStudio), **Consegna alla stanza…** and **Apri la stanza**. They are the same pyArchInit menu entries, within reach.

Pressing **Esporta** asks for the **destination folder**.

Authors, licences, embargoes and groups are handled in the **"Manage paradata"** window (§3).

### 2.2.1 Trenches: a single graph for the whole site

Starting with **5.13.109-alpha**, the em.json carries **a single graph**, with the units of all the trenches: there is nothing to choose. The "Esporta Extended Matrix" window no longer has the "Saggi" (trenches) group, and the menu entries **Esporta sito in em.json…** and **Vedi la matrice…** ask only for the site.

The trench is the **Saggio** field of the US form: it stays a field like the others, which can be used as a dimension to group the units (`saggio`, §4) and which goes into the narrative's *briefing* (§10.4), but it no longer splits the file. A file exported by earlier versions (up to 5.13.108-alpha), with one graph per trench, still opens in the matrix panel (§10.8).

### 2.3 Click "Esporta"

The files that are born, according to the formats checked:
- `<site>.em.json` — Extended Matrix, to open in EMStudio or to deliver to a room
- `Extended_Matrix_<site>[_<area>].dot` — Graphviz DOT, for the classic Harris matrix
- `Extended_Matrix_<site>[_<area>]_phased.json` — per-epoch view

> **Places are carried in the em.json.** The site's place, the toponym chain and the groups of areas, sectors, trenches and rooms come out together with the units, tied by `is_in_location` edges (§4).

The closing summary lists the files and, for em.json, **how many nodes and how many edges** came out, with any warnings.

> **From 5.13.122-alpha the em.json comes out cleaner.** Every unit has **only one** edge to the epoch it is born in (before, it had two identical ones: the library added its own after the importer's had already been re-attached); the node's **description** is the stratigraphic definition or, if that is empty, the description of the record (before, the word "None" came out); the graph has a **name**, that of the site (before, EMStudio opened it as "Untitled"); a unit that survives into a more recent epoch has the `survive_in_epoch` edge to **every** intermediate epoch, not only to the last one. For a site that comes from an EMStudio em.json see also §5.0, "The em.json is remembered".

> **GraphML is no longer exported**: the matrix is looked at and validated in EMStudio, which reads em.json. The temporal rows (swimlanes) of the old GraphML went away with it. GraphML survives only on the way **in**, for files drawn in yEd (§5).

---

## 3. "Manage paradata" Dialog (4 tabs)

### 3.1 Access
Click the **"Manage paradata"** button in the US form (next to the green Export button).

### 3.2 The 4 tabs

| Tab | Content | File generated |
|---|---|---|
| **Authors** | Add authors (name + ORCID + role) | `paradata_<site>.graphml` |
| **Licenses** | Dataset license (e.g. CC-BY-NC-4.0 + URL) | same |
| **Embargoes** | Embargo dates + reason | same |
| **Groups** | Ad-hoc groups (name + US member selection) | `groups_<site>.graphml` |

Files are saved next to the SQLite DB and are **Git-versionable**.

---

## 4. Dimensions and group types in the em.json

The em.json that pyArchInit exports carries the **location groups** (`LocationNodeGroup`) of the US form, told apart by the `kind` type: `toponym`, the nazione → regione → provincia → comune chain and the site's place (§4.1); `study`, the **areas**, **sectors** and **trenches**; `functional`, the **rooms**. Each unit is tied to the groups it belongs to by `is_in_location` edges; the group identifier tells the field it comes from (for example `loc::area::study::1`). The file carries no colours: whoever reads it decides them, EMStudio with its own style and the matrix panel in QGIS with the visual rules of the s3dgraphy library. The old GraphML export coloured the groups by dimension: that palette was retired together with it. The library can also group by **structure**, **activity**, **square** and by ad-hoc groups, with one primary membership and the others secondary (`is_primary`): pyArchInit does not ask it to today, and in the file that attribute appears only on the edges of the toponym chain, always false.

### 4.1 Toponym chain (5.6.0-alpha)

The fields `site_table.{nazione, regione, provincia, comune}` are auto-emitted as a recursive `LocationNodeGroup(kind="toponym")` chain (parent: nazione → regione → provincia → comune). Empty admin levels are skipped without breaking the chain. A cross-site dedupe ensures that the same `comune` present in 2 sites becomes **one shared node** in the em.json.

---

## 4.2 Multi-dimension membership (5.6.0-alpha)

A unit can sit in several groups at once — an area, a sector, a trench, a room, besides the site's place — and in the file it has one `is_in_location` edge for each, all on an equal footing. Example: an SU with `area=1`, `settore=1` and `ambient=Ambiente 3` has three edges, to "1" (area, `study`), "1" (sector, `study`) and "Ambiente 3" (`functional`), plus the one to the site's place, from which the toponym chain goes up. The distinction between primary and secondary membership (`is_primary`, with `struttura` first and `toponym` never primary) belongs to the library's model, for whoever asks it for groups by dimension: it is not in pyArchInit's em.json.

---

## 5. Round-trip (Import tab)

> **What can be imported**: the Import tab now also reads **em.json** — from EMStudio or from a StratiGraph node — and picks the reader from the file extension; a yEd `.graphml` is still accepted for older files. The procedure below, moving SUs between groups, concerns the yEd/GraphML route.

### 5.0 Importing an EMStudio em.json (even into an empty database)

An em.json written by **EMStudio** (not by pyArchInit) can be imported into the pyArchInit database **even when the database is empty** (since 5.13.121-alpha): the site, the periods, the records, the relationships and the media are born from the file, with no need to create a site first.

1. Open the menu **Plugins → pyArchInit - Archaeological GIS Tools** and choose the entry **Extended Matrix → Importa em.json…** (Import em.json): the Extended Matrix window opens already on the **Import** tab, even if the database has no site at all. From the US form you reach the same place: the green **Esporta Extended Matrix** button, with no site chosen, opens the same window on the Import tab instead of stopping (**exporting**, on the other hand, still asks for a site).
2. Press **Browse…** and choose the em.json.
3. Check the **Sito target:** (target site). If it is empty — the case of a database with no sites — the name of the graph written in the em.json is proposed (for example "Temple") or, if there is none, the file name without ".em.json"; you can edit it. If the field already shows a site (with a database that has sites: the site of the US form you started from or, from the menu, the first in alphabetical order), no name is proposed: type the name of the new site or pick the one to import into. Below there are two boxes, ticked by default: **Crea periodi mancanti se assenti** (Create missing periods if absent — if you untick it and the site does not already have the file's periods, the import stops with the error "MissingEpochError") and **Importa anche i media citati (immagini, video, 3D, documenti)** (Also import the cited media — images, videos, 3D, documents). Below there is the **Cartella dei file** field (Folder of the files), optional, with the **Sfoglia…** button (Browse…): it is needed when the em.json was copied on its own, far from the files it cites — point to the EMStudio project folder (the one with `EM/`, `DosCo`, `proxies`, `RB`…).
4. Press **Anteprima** (Preview): it writes nothing, and says how many records are new, updated and unchanged, how many periods are new and, as a list, how many records of which type, how many nodes of the file do not become records and how many units have their **3D proxy** (from 5.13.124-alpha; for TempluMare «65 unità su 112 hanno il loro proxy 3D.»: the same 65 that EMStudio shows, which counts 114 units because it also includes the 2 continuity nodes).
5. Press **Applica** (Apply; it is enabled after the preview): it imports and shows the same summary, plus the one for the media.

What happens, in short:

- **What becomes a record.** Only the units whose type pyArchInit knows (US, USM, USD, USVs, USVn, serUSVn, SF, VSF, RSF, USN, USNt…) and the paradata: properties (`property`), extractors (`Extractor`), combiners (`Combinar`) and documents (`DOC`). Resources, files, 3D models, semantic shapes, digital-twin processes, groups, epochs and the narrative do **not** become records: before 5.13.121-alpha they all became "US".
- **Names (the US field).** The name of the node without the type prefix: USV105 → 105, D.05 → 05, D.05.02 → 05.02. Properties that share a name (for example "height", which appears for many units) get, in brackets, the name of the unit they belong to: "height (105)". If two different types would give the same number — the combiner "C.10" and the document "D.10", the US "SU002" and the USD "USD002" — the stronger type (the US, then the other units, then documents, extractors, combiners) keeps the number and the other keeps EMStudio's full name ("C.10", "USD002"), so that the relationships do not get mixed up.
- **Relationships.** Between two US/USM they are the usual pyArchInit ones («Copre» (covers), «Taglia» (cuts)…), and the "comes after" relationship (`is_after`: the unit is later than the other, without saying it touches it) is written with the arrow `>` (`A > B`: A is later than B), between two US as between all the other types: up to 5.13.130-alpha between two US it became «Copre» (covers), a physical contact the file does not state, and the export turned it back into `overlies` (TempluMare's nine `is_after`). Between units of different types the physical relationships are written in full («Taglia», «Si appoggia a» (abuts)), and the paradata chain — unit → property → extractor or combiner → document, and a find that is «part of» a virtual find — with `>>`. Periods, activities, groups and resources are not relationships. On export these signs turn back into Extended Matrix edges (`is_after`, `has_property`, `has_data_provenance`, `extracted_from`, `combines`, `is_part_of`). Every relationship is written on **both** records, reversed on the second — «Copre»/«Coperto da» (covers/covered by), «Taglia»/«Tagliato da» (cuts/cut by), `>`/`<`, `>>`/`<<` — as the US form's relationship check requires; a record with no relationships has an empty list, not an empty field. Before 5.13.125-alpha the check gave «malformed node or string: None» and «Rapporto reciproco non trovato» (reciprocal relationship not found).
- **Activity and description.** The node's activity (the ActivityNodeGroup) goes into the **Activity** field of the record; the node's description into the **Description** field.
- **Periodization.** EMStudio's epochs, which have only a name and dates, are looked up by name in the site's periodization; the ones that are not there become new periods, from the oldest, numbered after the site's last period, in phase 1, with start and end dates and the name as the extended dating. Each unit takes its initial period and phase from the epoch where it is born and its final ones from the last epoch where it survives (or the same as the initial ones). Periods without a **period code** receive one in sequence, 1, 2, 3…, in order of period and phase; each unit takes the **dating** of its initial period and the **period code** as «Crea codice periodo» (Create period code) writes it — for example 1/2/3 for a unit that lives from period 1 to 3 — if it does not already have them (from 5.13.125-alpha).
- **Site record.** If the site does not exist it is created. The **definition** is the heritage asset the study is about, if the em.json declares it, otherwise the name of the graph (for TempluMare «Temple»); **nation, region, province and municipality** come from the em.json's chain of places, when there is one. All five also end up in the **thesaurus** (site form, codes 1.1–1.5), from which the site form reads them. The description comes from the graph: name, code, authors and position (EPSG and origin). If the site already exists only what is empty is filled in, and the definition «Extended Matrix», written by versions before 5.13.125-alpha, is replaced.
- **Media.** Following the em.json's links — record → resource → file, record → 3D model → resource → file, and the url of the document or of the extractor — the cited files become media of the record. They are searched for the way EMStudio searches for them: in the em.json's folder and in the tree of its EM project (`EM/`, `EM/DosCo`, `EM/proxies`, `RB`, `RM`, `SB`), plus the folder in the **Cartella dei file** field, if you have indicated it. Images, videos, 3D models (also **GLB** and **GLTF**) and documents (**PDF, Word, Excel, ODT, ODS, RTF, CSV, TXT**) are accepted. The media points to the **original file**, like those added from the record; the thumbnail and the copy go into the **Thumbnail path** and **Image resize** folders of the configuration (tutorial 01): 3D models have their own view, PDFs the first page, the other documents an icon showing the type. A unit's **3D proxy** — in the graph it sits on the unit's "geometry" property — goes onto the unit's record. If the property is shared by several units — a USV that inherits the geometry of the US it completes — the proxy goes to the unit that created it, as in EMStudio (before 5.13.124-alpha it went to the first unit found in the file). The summary says how many media are new and of what type, how many were already there, how many thumbnails, how many cited files were not found (with the advice to indicate the project folder), how many copies are empty (cloud placeholders, to be downloaded again), how many external references (web, network, cloud) remain addresses and which files are not media (`.blend`, `.mtl`, `.zip`…). A file stored in a bucket that also has a copy on disk (in the em.json, several addresses for the same resource) is imported from the copy on disk; before 5.13.124-alpha it remained an external reference. A second import duplicates nothing. Before 5.13.122-alpha the files were copied into pyArchInit's main folder, GLBs had no thumbnail (and the record did not show them), proxies sat on the property instead of on the unit, and PDFs were left out. From 5.13.127-alpha the views of the 3D models are drawn all together in a separate Python process, outside QGIS: before, on macOS, QGIS closed by itself when the import summary was closed.
- **Importing again.** Importing the same file again duplicates neither periods nor records: those already present come out as «invariate» (unchanged) or «aggiornate» (updated), and where the database and the file differ the file wins (the summary counts these as «conflitti», conflicts). The preview also counts as «aggiornate» the records to which the import adds relationships, dating or period code (they used to show as «invariate»). Re-importing the em.json into a database imported before 5.13.125-alpha repairs it: site definition, relationships on both records, dating and period codes.
- **The em.json is remembered.** pyArchInit keeps the units, the paradata, the relationships and the epochs in its tables; everything else in the graph — resources, files, models, semantic shapes, digital-twin processes, groups of paradata and of activities, authors, licenses, the narrative — together with the title, the **study code** (for example GT16: it is the prefix with which Blender re-attaches the proxies), the georeferencing (EPSG and offsets) and EMStudio's names, is remembered at import (table `pyarchinit_em_sources`, one row per site; the latest import wins). On **export** of the site's em.json all this comes back: the original names (SU006, D.07.08, height…) for the records that still have the number given at import — a record renamed in pyArchInit keeps the new name —, the nodes' data (for example the "geometry" property with its shape, from which EMStudio counts the proxies), and the nodes that are not records, with their edges, attached to the records that still exist: a branch left without a record (for example the shape of a deleted property) does not come back. Relationships, periods and descriptions always come from the database. The message at the end of the export says how much came back, for example «Dall'em.json importato tornano 851 nomi, 1090 nodi e 1969 archi, codice dello studio GT16.» (From the imported em.json come back 851 names, 1090 nodes and 1969 edges, study code GT16). Tested on TempluMare_v3.2 (1946 nodes): no name and no description different from the original, and in EMStudio 65 units out of 114 with the proxy and 2 epochs out of 3 with a model, as in the original. What stays different: the 9 "comes after" relationships between two US, which pyArchInit writes «Copre», and the place groups of the site and of the area with the study, which pyArchInit adds.

### 5.0.1 Exporting the EM project for EMStudio, with its files

From **5.13.131-alpha**. The em.json pyArchInit writes in `pyarchinit_EM_folder` carries the paths of the files (`proxies/SU002.glb`, `DosCo/D.05 ….pdf`, `../RB/…`) but not the files: opened from there, EMStudio finds neither the proxies nor the documents. The menu entry **Extended Matrix → Esporta progetto EM per EMStudio…** (Export EM project for EMStudio) builds the folder of a complete EM project, with the standard tree of the s3dgraphy library — the one in which EMStudio looks for the files:

```
<project>/
  EM/            the em.json
    DosCo/       the documents (D.01, D.02.03 …)
    proxies/     the 3D proxies of the units (<unit>.glb)
  RB/            the survey (LOD0, LOD1 …, textures, tiles)
  SB/            the models made from the sources
  RM/            the representation models
```

1. Choose the **site**.
2. Choose the **project folder**. If it is empty, or already an EM project (it has an `EM/` folder, or it is its `EM/`), it is the project; otherwise — the Desktop, a folder with other files — pyArchInit creates inside it a new folder named after the site (for example `Temple/`). The chosen folder is remembered for the next time.
3. pyArchInit exports the site like **Esporta sito in em.json…** — in the working folder `pyarchinit_EM_folder`, so with the narrative prepared in the panel (§10.8) — and copies the em.json into `EM/`. Then, next to it, at the path the em.json writes, it copies **every cited file the database knows**: the media imported with the em.json (§5.0). A file cited by its name alone — the url of documents and extractors, which EMStudio takes from `DosCo` — goes into `EM/DosCo/`. If the original cannot be reached (the external disk unplugged), the file is taken from the **Image resize** folder when the same file is there (3D models and PDFs, copied as they are); an image is not: there it is reduced to PNG, it is no longer the cited file. A progress bar counts the files.
4. The summary says how many files were copied and how many were already there, **how many resources of the em.json EMStudio finds from the project** — counted by the library's resolver, the same one EMStudio uses —, the cited files the database does not have, per folder, to be copied by hand from the original project, and the copied files whose **sha256** is not the one written in the em.json. **Show Details…** lists them one by one. The buttons: **Apri in EMStudio** (Open in EMStudio: opens the project's em.json), **Apri la cartella** (Open the folder), **Chiudi** (Close).

Exporting again into the same folder does not copy again what is already there and **does not overwrite a project file that differs** from the database's (it may be work done in EMStudio): the summary says so («lasciati come sono», left as they are); to replace it, delete it and export again. The previous em.json, if different, stays next to it as `<site>.em.json.bak`.

On TempluMare (the database of the §5.0 import, with the external disk unplugged): 96 files copied (238.7 MB: the 65 proxies and 31 documents, all with the sha256 written in the em.json); EMStudio finds 96 of the 536 resources from the project; left to copy by hand are the 343 files the database never had — the survey in `RB/` (158) and the models in `SB/` (175), which are not media, `.blend` files included — plus the 10 JPG photos of `DosCo`, which are copied from the originals when the disk is plugged in.

### 5.0.2 Plans and elevations from the 3D models

Since **5.13.134-alpha**. An EMStudio em.json has no GIS geometries of the excavation, but it has the units' **3D proxies** (`EM/proxies/<unit>.glb`) and the scene's **position**: EPSG and shifts. If you tick **Ricava piante e prospetti dai modelli 3D** ("derive plans and elevations from the 3D models") in the **Import** tab (below **Cartella dei file**, off by default), the import derives two things from the proxies.

- **The plan of each unit**, in the `pyunitastratigrafiche` layer (the "horizontal SUs"), in the em.json's CRS. It is the model's shadow seen from above, with its holes, simplified to 1 cm.
- **The vertical drawings**, in the `pyunitastratigrafiche_usm` layer (the "vertical SUs"). These are the **site elevations** from north, east, south and west, with every unit seen from that side, and the **elevation of each unit**. A unit is seen square-on to its long side, from the side of the site's centre; a nearly square unit is seen from the centre.

Vertical drawings are in drawing coordinates: **X = metres along the view, Y = elevation**. They sit side by side, 10 m apart. In the north elevation the viewer stands to the north, so east is on the left.

1. Tick the box. The **Scegli…** button opens the **Geometrie dai modelli 3D** window, with:
    - the position read from the em.json;
    - the **Spostamento Z** (Z shift), with the resulting elevations, updated as you change it;
    - the **Nord**, **Est**, **Sud**, **Ovest** boxes for the site elevations;
    - the table of the units with a proxy, with the columns **Pianta** (plan), **Prospetto** (elevation) and **Stato** (status). The status can be: ok, file not found, unsupported format, too large, uses another unit's 3D, already has a hand-drawn plan or vertical drawing.

    **Tutte** and **Nessuna** (all/none) tick and untick the boxes; **Conferma** keeps the choice. If you don't open the window, the default choice applies: every unit with a readable proxy, with plan and elevation, except those that already have a hand drawing; the four sides; the em.json's Z shift.
2. **Anteprima** (preview) adds the line "Dal 3D: … piante, … prospetti del sito, … prospetti di unità (si calcolano all'Applica)".
3. **Applica** (apply) writes the records, then the media, then the drawings, with a progress bar. The summary adds a "Dal 3D: …" line, listing the skipped units and the reason, including those whose model can't be found or read.

**The database's CRS.** When there are geometries to write, pyArchInit compares the CRS of the two layers with the em.json's before writing anything:

| Database layer | What happens |
|---|---|
| same EPSG as the em.json | imports |
| another metric CRS (e.g. 3004) | asks "Converto le piante in EPSG:3004 del database?" (convert the plans?), with **Converti** or **Annulla**. Elevations are never converted: they are in drawing coordinates |
| in degrees (4326) or without a CRS (-1) | stops: recreate the database in the em.json's CRS, or untick the box and import only the records. The message names the layer at fault: if it is only the vertical drawings layer, you can also untick elevations and sides in **Scegli…** and import only the plans (and vice versa) |

Cancelling, or the stop, leave the database as it was. Without the box, or without usable proxies, nothing is checked and only the records are imported, as before.

**Documents and links.** Each drawing is a document of the **Documentazione** form, of type **Planimetria** (plan) or **Prospetto** (elevation), the thesaurus terms in the plugin's language, with a code name:
- `3D-PLA` for the plan;
- `3D-PRO-N`, `3D-PRO-E`, `3D-PRO-S`, `3D-PRO-W` for the site's sides;
- `3D-PRO-<type><SU>` for a unit, e.g. `3D-PRO-US002`.

The same type and name are on the polygons (`tipo_doc`, `nome_doc`) and in the **Documentazione** list of the SU form. So from the Documentazione form the document loads its "horizontal SUs" or "vertical SUs", and from the SU form the document's row does the same. Each polygon has the drawer "pyArchInit 3D", the proxy file in **rilievo originale** and the centroid in **coord**.

**Re-importing.** A new import with the box ticked replaces only the site's derived drawings, i.e. those with drawer "pyArchInit 3D" and a name starting with `3D-`; hand-drawn ones are never touched. If you corrected a derived polygon and want to keep it, change its drawer. To add drawings to a site imported earlier, re-import the same em.json with the box ticked: the records don't change. The em.json doesn't change either: derived drawings and their Documentazione rows stay in pyArchInit and are not exported.

**The USM view.** SQLite databases created from the template had a `pyarchinit_usm_view` that showed only USM-type units. The first import that writes vertical drawings restores pyArchInit's definition, the same as PostgreSQL's, which shows the vertical drawings of every unit, and the summary says so. The narrative map (§10.10) takes every unit's plan from the plan layer, and never uses derived elevations.

On TempluMare, in a new database in EPSG:31700 with 851 records, the import produced in about a minute:
- 65 plans: the temple, 42 × 49 m, around X 327 285, Y 448 355;
- 4 site elevations and 64 unit elevations (USV105, which is flat, has none);
- 69 documents.

The em.json says to add **500 m** to the 3D elevations, which puts them between 991 and 1004 m, while the temple lies at about 495 m. The em.json's Z shift should therefore be checked; you can set it to 0 in the window.

### 5.0.3 Sections along lines, from the 3D models

Since **5.13.135-alpha**. After the import (§5.0, with the media, or with the **Cartella dei file**), the section lines you draw in the site's sections layer (`pyarchinit_sezioni`) cut the units' 3D proxies. Each line becomes a **section** in the vertical drawings layer `pyunitastratigrafiche_usm`, with the cut profile of every unit the line crosses.

1. Draw one or more lines in the `pyarchinit_sezioni` layer, with the **sito** and an **id_sezione** (e.g. "A"). A line may have several segments.
2. Choose **Extended Matrix → Sezioni dai modelli 3D…** and the site. The **Sezioni dai modelli 3D** window shows:
    - the position of the em.json remembered at import;
    - the **Spostamento Z** (Z shift), with the resulting elevations;
    - how many units have a 3D model;
    - the table of the site's lines: **Taglia** (cut), **Sezione**, **Descrizione**, **Area**, **Tratti** (segments), **Lunghezza (m)** and the **Documento** it will become.
3. **Taglia** computes and writes, with a progress bar; the summary says how many units each section cut, the skipped units and why, and the lines that already had another document.

**Reading a section.** In drawing coordinates: **X = metres along the line from its first point, Y = elevation**. The first point (A) is on the left, so for a line drawn west to east the viewer stands to the south; the document's note says at which X point A sits. The **Lunghezza (m)** column is always in metres, even when the sections layer is in degrees. A unit's profile is everything inside its cut outline. Sections sit to the left of the elevations (negative X), 10 m apart.

**Documents and links.** Each section is a **Sezione** document (the thesaurus term in the plugin's language) named `3D-SEZ-<id_sezione>`, e.g. `3D-SEZ-A`. The same type and name are:
- on the polygons;
- in the SU form's **Documentazione** list;
- and, if the line had none, on the section line too. So the Documentazione form loads the line and the section's "vertical SUs" together. A line that already has another document is left alone, and the summary says so.

**Redoing a section.** Running the command again on the same line replaces only that section, and leaves it in its place in the layer; if it has grown in the meantime until it would touch another section, it moves to the left of all of them. A line that was moved and no longer meets any unit loses its previous section. If the name changes (a corrected **id_sezione**, or a second line with the same id, which turns the names into `3D-SEZ-A-<gid>`), the section with the old name is removed and the line takes the new one. Re-importing the em.json with plans and elevations (§5.0.2) doesn't touch the sections.

**CRS.** Lines are brought into the em.json's CRS when the sections layer has another one. If the layer has no CRS (`-1`, as in the SQLite template), the coordinates are taken as they are, and the summary says so. The command stops if the site has no imported em.json, if the em.json doesn't say where the scene is, if no line is chosen, if no unit has a 3D model that can be found (import the em.json with the media, or connect the proxies' disk), or if the vertical drawings layer isn't metric. A unit the line crosses whose model isn't closed is skipped, and the summary says «la sezione non si chiude (modello aperto)» (the section doesn't close: open model).

On TempluMare, a west-to-east line across the cella cuts 21 units in about 3 seconds: walls, foundations, steps, the altar and the roof.

The yEd/GraphML route, for moving units between groups, is the one that follows.

To update the SQL database by moving SUs between groups in GraphML:

1. Open the GraphML in **yEd**
2. Drag an SU into a different group, save
3. Back to the dialog → **"Import"** tab
4. **Check** the *"Update SQL on import (struttura/area/...)"* checkbox
5. Load the modified GraphML

The system runs an atomic transaction: if anything fails, **full rollback** (the DB stays unchanged). `adhoc` groups never write SQL — they only update `groups_<site>.graphml`.

From 5.6.0-alpha the import walker is **recursive** and supports nested folders (e.g. toponym chain `nazione > regione > provincia > comune > SU`). When cycles are detected in the folder graph, a `CycleDetectedError` is raised and the import is aborted with rollback.

---

## 6. CLI (alternative to dialog)

For scripts / batch:

```bash
# Export
python scripts/s3dgraphy_sync.py export \
    --db <path> --sito <name> --mapping pyarchinit_us_mapping \
    --output <out.graphml> --group-by struttura

# List ad-hoc groups
python scripts/s3dgraphy_sync.py paradata list-groups \
    --db <path> --sito <name>

# Add author
python scripts/s3dgraphy_sync.py paradata add-author \
    --db <path> --sito <name> --name "Marco Pacifico" \
    --orcid "0000-0002-1234-5678" --role curator
```

Exit codes: 0 = success, 1 = bridge error, 2 = argparse error.

---

## 7. Troubleshooting

| Symptom | Cause | Solution |
|---|---|---|
| "no such column: node_uuid" | Phase 1 migration not run | Restart QGIS, reopen the DB |
| Empty GraphML | DB without rapporti / area filter too strict | Verify us_table.rapporti is populated |
| "rapporti fields must be TEXT" | Entered a number as integer | US/Area fields are **TEXT**, not integer |
| Wrong capitalization on rapporti | Lowercase "copre" in DB | Use "Copre", "Coperto da" capitalized |
| `DeprecationWarning` on 5.5.x file | Legacy `ActivityNodeGroup + group_kind` file | The projector promotes it in-memory to `LocationNodeGroup`. Re-export to migrate the file on disk. |
| Swimlane rows show a very long text | Older versions used the periodization Descrizione as label | Update the plugin and re-export, and/or fill **Datazione estesa** with a short name |
| Swimlane epochs are in the wrong order (e.g. Bronze Age above Late Antiquity) | Rows are sorted by **Initial Chronology**; BC years entered as positive numbers (1650 instead of -1650) sort as AD | In the Periodization form enter BC years as negative numbers and re-export. The export summary now shows a "⚠️ Periodizzazione: ..." warning listing the periods to fix |
| EMStudio opens the exported em.json but finds neither the 3D proxies nor the documents | The em.json in `pyarchinit_EM_folder` carries the paths of the files, not the files | Export with **Extended Matrix → Esporta progetto EM per EMStudio…** (§5.0.1) and open the project's em.json |

---

## 8. Technical documentation

For architecture deep dives, design decisions and roadmap:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Deferred carry-overs:
- **AI08-F3**: auto-layout heuristics (sub-group bin-packing) — still deferred
- **AI09**: TimeBranchNodeGroup mapping — future
- **Phase 3**: SyncEngine + REST API — future
- **Phase 4**: GraphDBBackend + SPARQL — future

Shipped:
- **AI07** (5.6.0-alpha, 2026-05-10): `LocationNodeGroup` migration with `kind` enum + toponym chain + multi-dim memberships
- **AI08-F1** (fused into AI07): native hierarchical nesting via `is_primary`

---

## 5. yEd-aware Import — importing externally-authored graphmls (5.8.x)

From **5.8.0-alpha** the bridge is **bidirectional even for graphmls authored directly in yEd** (i.e. without first going through a pyarchinit export). Pyarchinit auto-recognises "yEd-raw" graphmls — those without `pyarchinit.*` data keys — and imports them through a dedicated dispatch that maps node-label-prefix → stratigraphic type, recognises TableNode rows as periods, walks group folders as archaeological dimensions, and lets the user pick a policy for folder-touching edges.

### 5.1 6-milestone rollout

| Milestone | Tag | Adds |
|---|---|---|
| **yE-A** | `yed-import-foundation-5.7.5-alpha` | `yed_detector.py` — flavour flag `yed-raw` / `pyarchinit-projected` |
| **yE-B** | `yed-import-classifier-5.7.6-alpha` | `yed_classifier.py` — `ClassificationKind` enum 13 values (US/USV/SF/VSF/RSF/DOC/COMB/PROP/...) + order-sensitive regex |
| **yE-C** | `yed-import-parsers-5.7.7-alpha` | `yed_table_parser.py` (PeriodCandidate from TableNode rows) + `yed_group_walker.py` (FolderCandidate with auto-dimension from label prefix: VA01→attivita / AR01→area / etc.) |
| **yE-D** | `yed-import-pipeline-5.8.0-alpha` | `yed_import_pipeline.py` — `import_yed_raw()` orchestrator + 5 write functions + `FolderEdgePolicy` (SKIP/FAN_OUT/REPRESENTATIVE/SYNTHETIC) + paradata via `ParadataStore` + `_DryRunRollback` sentinel + DbHandle PG+SQLite |
| **yE-E** | `yed-import-dialog-5.8.2-alpha` | `gui/yed_import_dialog.py` — `YedImportDialog(QWizard)` 5 pages (classifier / periods / folders / policy / preview) + `YedOverrides` dataclass + sidecar `<graphml>.yed_overrides.json` persistence |
| **yE-Closure** | `yed-import-closure-5.8.3-alpha` | This documentation + dev-log + CHANGELOG. |

### 5.2 How it works — user flow

1. **Open a graphml in QGIS via the Import GraphML menu** (same path as the existing pyarchinit-projected flow).
2. Pyarchinit auto-detects it as yEd-raw (no `pyarchinit.*` keys) → dispatches to the new branch instead of falling through to the legacy path.
3. The `YedImportDialog` wizard opens with **5 pages**:
   - **1/5 Classifier** — table, 1 row per leaf. Each row shows `label` + `auto_kind` (e.g. `us_real` / `usv_virtual` / `property`) + a `user_kind` override combobox. **Accept auto** button resets every row to its `auto_kind` (clear all overrides).
   - **2/5 Periods** — 1 row per TableNode-row parsed, editable `periodo` + `fase` cells. Dates (`datazione_iniziale`/`finale`) stay empty: yEd-raw graphmls don't carry dates.
   - **3/5 Folders** — 1 row per group folder. `dimension` combobox (attivita / area / struttura / settore / ambient / saggio / quad_par / `skip` to exclude). `value` text-edit (default = `auto_value` derived from label prefix).
   - **4/5 Rapporti policy** — 4 radio buttons for how to treat folder-touching edges:
     - **SKIP** (default): drop folder-touching edges. Leaf-to-leaf edges pass through unchanged.
     - **FAN_OUT**: a `folder_A → folder_B` edge expands to `N×M` leaf pairs (cartesian product of members).
     - **REPRESENTATIVE**: use the first member of each folder as a proxy.
     - **SYNTHETIC**: create one us_table row per folder (`unita_tipo='VA'` virtual activity) + rewire edges through these anchors.
   - **5/5 Preview** — dry-run of `import_yed_raw(overrides=..., dry_run=True)`. Displays counts (us / inv / period / paradata) **without committing**. Click **Finish** to commit, **Cancel** to abort.
4. On **Finish** the wizard saves your overrides to a **sidecar JSON** `<graphml>.yed_overrides.json` next to the file. Re-opening the same graphml preloads the sidecar so your previous overrides come pre-applied.

### 5.3 Destination routing

The dispatch uses `_classify_destination` (in `yed_import_pipeline.py`) to bucket each leaf:

| ClassificationKind | Destination | Note |
|---|---|---|
| US_REAL | `us_table` (`unita_tipo='US'`) | from label `^US\d+` |
| US_MASONRY | `us_table` (`unita_tipo='USM'`) | from `^USM|USR|USS` |
| US_DOCUMENTARY | `us_table` (`unita_tipo='USD'`) | from `^USD\d+` |
| USV_VIRTUAL | `us_table` (`unita_tipo='USV'`) | from `^USV\d+` |
| USV_FORMAL | `us_table` (`unita_tipo` derived from label prefix: USVs/USVn/USVc) | from `^USVs|USVn\d*$` |
| **REUSED_SPECIAL_FIND** (RSF — **5.8.1**) | `us_table` (`unita_tipo='RSF'`) | from `^RSF\d+` (s3dgraphy 0.1.42, spolia) |
| SPECIAL_FIND | `inventario_materiali_table` | from `^SF\d+` |
| VIRTUAL_FIND | `paradata` (via `ParadataStore`) | from `^VSF\d+` |
| DOCUMENT | `paradata` | from `^D\.\d+` |
| COMBINER | `paradata` | from `^C\.\d+` |
| PROPERTY | `paradata` | label keyword (`material`/`position`/`width`/...) |

**User decision 2026-05-13**: USV* (virtual) are "unità tipo" (still stratigraphic units) and belong in `us_table`, not in paradata. Only DOC/COMB/PROP/VIRTUAL_FIND remain in paradata.

### 5.4 Sidecar JSON — schema

Versioned for forward-compat:

```json
{
  "version": 1,
  "saved_at": "2026-05-13T17:57:00+00:00",
  "graphml_path": "/absolute/path/to/file.graphml",
  "classifier": {
    "n0::n0::n0": "us_real",
    "n0::n0::n2": "us_real"
  },
  "periods": {
    "p0": {"periodo": 5, "fase": 7}
  },
  "folders": {
    "f0": {"dimension": "struttura", "value": "S01"}
  },
  "policy": "fan_out"
}
```

Only USER-MODIFIED fields are persisted (diff). Unknown `ClassificationKind` values (e.g. from future s3dgraphy releases) are skipped silently at load time.

### 5.5 CLI for scripted ingest

For CI / batch re-runs:

```bash
python scripts/import_yed_graphml.py /path/to/file.graphml \
    --site Al-Khutm \
    --db /path/to/khutm2.sqlite \
    --policy skip \
    --overrides /path/to/file.graphml.yed_overrides.json \
    --dry-run
```

Mutex `--db` / `--conn-str` for SQLite vs PostgreSQL backend. `--overrides` is optional (no overrides = yE-D defaults). `--auto-defaults` is a no-op forward-compat flag.

### 5.6 Known limits

- **No date editing in wizard**: yEd-raw graphmls don't carry `datazione_iniziale`/`datazione_finale`. The Periods page edits only `periodo` + `fase` (FK targets).
- **Partial ParadataStore API**: upstream s3dgraphy doesn't yet ship `add_virtual_us` / `add_document` / `add_combiner` / `add_property`. yE-D logs "skip — method missing" per paradata leaf but counts the attempts in the preview.
- **PropertyNode → Path B (no US linkage)**: PROPERTY nodes are written without a target US. The wizard emits a warning. Future: yE-Closure follow-up to add "assign target" in the UI.
- **Multi-DB**: the sidecar JSON is per-graphml, not per-DB. Importing the same graphml into different DBs uses the same overrides for both.

### 5.7 Final test coverage

| Suite | Test | Coverage |
|---|---|---|
| yE-A | `test_yed_detector.py` | flavour detection |
| yE-B | `test_yed_classifier.py` | 13 ClassificationKind + order-sensitive regex |
| yE-C | `test_yed_table_parser.py` + `test_yed_group_walker.py` | PeriodCandidate + FolderCandidate parse |
| yE-D | `test_yed_rapporti_policy.py` (7) + `test_yed_import_pipeline.py` (15) + `test_yed_pipeline_integration.py` (9 incl. 2 L1 overrides e2e) | policies + write functions + dispatch |
| yE-E | `test_yed_import_dialog.py` (5 sidecar JSON) + `test_import_yed_graphml_cli.py` (3) | sidecar persistence + CLI |

**Total suite post-rollout**: 354 passed / 42 skipped (PG-L1 require psycopg2).

### 5.8 Update 5.8.5-alpha (yed-fastfix)

Behavioural fix pack on top of `5.8.3-alpha` that improves the quality of the GraphML re-export after a yEd-aware import. End-user-relevant changes:

- **Multi-folder paradata**: DOC / Combinar / Extractor / property labels shared across yEd folders (e.g. `material` referenced from VA01 + VA04 + VA05) now create ONE `us_table` row PER occurrence — restored multi-folder visibility in the re-exported GraphML. Trade-off: identity-dedup (`D.01` / `D.01-2` / `D.01bis` collapsing into a single row) no longer applies for the second/third occurrence.
- **Reciprocal rapporti**: each yEd edge `a → b` writes the forward rapporto on `a`'s row AND the inverse on `b`'s row (`<<` / "Coperto da" / etc.). DOCs now show all incoming extractor connections in the Scheda US form.
- **Stripped `us` numeric prefix**: `US100` → `us='100'` `unita_tipo='US'` (was `us='US100'`). SF/VSF/RSF are dual-written to `us_table` + `inventario_materiali`.
- **Period/fase auto-fill**: yEd TableNode-row period membership propagates to `us_table.periodo_iniziale`/`fase_iniziale` + `periodizzazione.cont_per`.
- **BPMN-aware classifier**: `D.NN` (BPMN data-object) → `DocumentNode`, `D.NN.MM` (plain) → `ExtractorNode` — preserves the EM 1.5 semantic distinction.
- **Idempotent re-import**: re-running the same import skips rows that are already present; no UNIQUE-collision rollback on the repeat pass.
- **USV palette**: USV nodes now render with the EM canonical blue parallelogram (was rectangle with red border).

### 5.9 yE-F multi-folder paradata (5.9.0-alpha)

Structural evolution of `yed-fastfix-5.8.5-alpha`: the Bug R B1 trade-off (one `us_table` row per occurrence, with `us='D.01_2'` / `us='D.01_3'`) has been superseded. A paradata leaf (DOC / Combinar / Extractor / property) shared across multiple yEd folders now produces **a single row** in `us_table` per canonical label, and multi-membership is preserved in a new `other_locations` column.

End-user-visible changes:

1. **New "Other locations" widget in the US/USM form**: a `QListWidget` labelled "Other locations" appears in the *Periodizzazione* tab — visible **only** when `unita_tipo` is a paradata kind (`DOC`, `Combinar`, `Extractor`, `property`). The user can select multiple activity codes; the selection is serialised as a JSON list in the new `other_locations` column.
2. **New QGIS menu item**: `Plugins → pyArchInit → Migrazioni → Aggiungi colonna other_locations (yE-F)`. Must be run **once** on every pre-existing DB to add the new column (DBs created post-5.9 already have the column).
3. **Improved yEd-aware import**: a paradata leaf that appears in N yEd folders now produces **just 1** `us_table` row (no more N rows with `_2`/`_3` suffix as in 5.8.5). The first folder encountered becomes the primary `attivita`; secondary folders are listed in `other_locations`. On **export**, N visual yEd copies are emitted (one per folder), all sharing the same canonical `node_uuid` to guarantee round-trip identity.

**Backward compatibility**: data produced by Bug R B1 in 5.8.5-alpha (rows with `_2`/`_3` suffix) remain readable without any automatic conversion. The new logic applies to new imports; legacy rows continue to behave as before.

Predecessor: see section 5.8 (`yed-fastfix-5.8.5-alpha`) for the superseded behaviour.

---

## 6. Generate continuity (CON records)

In the **"Verifica rapporti"** panel — available as a tab inside the s3dgraphy import/export dialog — there is a **"Genera continuità"** button (label kept in Italian as in the plugin). For the currently selected site, this feature automatically builds the **continuity records** of the US/USM whose life spans more than one period.

If the window was opened without a database, the panel says so at the top and keeps its buttons disabled, without opening any message box: open a pyArchInit database and reopen the window. The panel reads the sites when you open its tab; if the database doesn't answer (a PostgreSQL server that is off), it says why and doesn't retry on its own: when the server is back on, press **Riprova** (retry).

### 6.1 What it does

1. It scans every US/USM in the site whose **initial period ≠ final period** (i.e. whose life spans more than one period).
2. For each one it creates or updates a continuity record named **`CON_<us>`** (e.g. `US5` → `CON_US5`).
3. The CON record **inherits** from the parent unit: site, area (plus any secondary areas), structure and the full period span (initial → final). Its description is auto-generated.
4. It writes a **reciprocal continuity relationship** on both sides: on the CON and on its parent unit.

> **The phase does not count on its own.** The rule looks at the **period**: a USM running from **2/3 to 2/4** — same period, only the phase changes — generates nothing. If your units survive from phase to phase inside the same period, tick **«anche i salti di fase»** («phase jumps too») next to the button: those jumps then count as well, provided **both** phases are filled in. A unit that does not move — same period and same phase — is never a continuity. The box starts **unticked**, and governs the preview and the writing together.

### 6.2 Idempotency

The operation is **idempotent**: re-running it does not duplicate existing records — it updates the existing `CON_<us>` if the parent unit's data has changed.

### 6.3 Dry-run preview and backup

Before writing, a **dry-run preview** is shown with the counts: how many records to **create**, to **update**, **unchanged** and how many **orphan**. Changes are applied **only after confirmation** (the "Genera" button). On apply, an automatic **database backup** is made first.

A CON record is **orphan** when its parent unit no longer spans periods (e.g. its initial and final period were made equal). By default orphans are only **flagged**; a **checkbox** ("Rimuovi anche le CON orfane") lets you opt into removing them.

**A hand-made continuity is recognised.** A CON record whose relationships name a single unit — `> 12`, or «Continuity after 12» — is that unit's continuity, whatever its name: the generator **updates** it (period span, canonical label) and the name stays its own. No second one is born: continuity is **one per unit**. If a canonical `CON_<us>` also exists, that one wins and the other remains an orphan to be decided by hand.

### 6.4 In the Extended Matrix export

The `CON_<us>` records produced this way appear in the Extended Matrix **em.json** as **continuity elements** (the outgoing GraphML export is retired, §2.3).

---

## 7. Temporal (stratigraphic) paradox check

In the **"Verifica rapporti"** panel (Check relationships — a tab of the s3dgraphy import/export dialog), the check now also flags **temporal paradoxes**: when the period/phase assigned to a unit contradicts the observed stratigraphy. Stratigraphy is the reference datum, so automatic corrections move the **periods**, not the relationships.

### 7.1 What it detects
- **Temporal inversion**: two dated units linked by an ordering relationship (e.g. US5 "covers" US7) in which the unit that is more recent in stratigraphy turns out to be entirely **older** by period.
- **Inconsistent contemporaneity**: units declared contemporaneous (physical equality / bond) but with **disjoint** chronological intervals.
- **Unevaluable**: an ordering relationship in which at least one of the two units has no datable period (flagged only, no correction).

Note on the boundary: two **adjacent periods that touch** at a single chronological point are considered overlapping → they are **not** a paradox (benefit of the doubt).

### 7.2 Automatic correction and suggestions
- When a single shift resolves the conflict, the check proposes moving the **single-period** unit that conflicts with the majority of its neighbours, choosing the period with the smallest shift; for contemporaneities with a non-datable unit it copies the period of the dated neighbour.
- In ambiguous cases — a tie, **multi-period** units (e.g. CON records), no valid period — it does not correct automatically: it provides a **"what + how" suggestion** (e.g. "Move US5 to a period ≥ 3, or US7 to a period ≤ 1, or verify the relationship").

### 7.3 Preview and backup
- The **preview** shows the proposed period changes before applying them.
- Before writing the periods, an **automatic database backup** is performed (SQLite and PostgreSQL).
- After applying, re-run the check to look for any residual paradoxes.

---

## 8. Chronology check (periodization and sheets)

In the same **"Verifica rapporti"** panel (Check relationships — a tab of the s3dgraphy import/export dialog), since version 5.13.64-alpha the check also finds and corrects **chronology** problems of the selected site. The temporal paradox check (section 7) compares the period of a unit with the stratigraphy; this one compares the periodization with itself and with the US sheets that copy it.

### 8.1 What it detects

The tree in the panel groups the problems by kind. Alongside the relationship groups there are four new ones:

| Group | What it reports | How it is handled |
|-------|-----------------|-------------------|
| **Phases with overlapping intervals** | Two periodization rows whose year ranges intersect | Manual: the panel proposes narrowing the intervals only when narrowing leaves a usable interval |
| **Sheet dating out of line** | The `datazione` field of the US sheet says something different from the `datazione_estesa` of its own period/phase | Automatic: the periodization is the source and the sheet is the copy, so the copy is rewritten from the source. An empty field is filled the same way. A US with no period is skipped, because there is nothing to copy from |
| **Periodization with start after end** | `cron_iniziale` greater than `cron_finale` | Manual: these are most likely BC dates without the minus sign — the panel proposes rewriting both years as negatives (`-1650` instead of `1650`); if it is a typo instead, swap the two values by hand |
| **Phase without years** | A phase whose years are missing or unreadable | Reported only: there is nothing to inherit them from |

An example for overlaps. The sample database has two, and neither carries a proposal: the two phases have **identical** intervals, and any narrowing would make a phase end before it begins. The panel simply tells you so; the decision (merge the phases, correct the years, leave things as they are) is the archaeologist's.

### 8.2 Automatic correction and suggestions

**Automatic corrections and proposals.** Automatic corrections are **already ticked**; proposals are **not**, and are applied only if you tick the checkbox. The rule used to be different: a problem whose fix needed a human decision could only be read. Now it has a checkbox, left unticked. This also applies to the two older relationship categories that offer a suggestion, namely the direct contradiction and the stratigraphic cycle.

To use the panel:

1. Select the **site** to verify in the panel. The verification is **per site**: it looks at the selected site and corrects only that one. On a database with ten sites this matters, because the same US numbers exist in all of them.
2. Read the **summary line** above the tree: it says how many problems there are, how many can be corrected automatically and **how many are proposals to tick by hand**.
3. Open the groups and select a problem to read its detail in the preview pane.
4. Check the checkboxes. Automatic corrections are already ticked: untick the ones you do not want to apply. Tick the proposals you agree with.
5. Apply the corrections. Before anything is written an **automatic backup** is taken (a copy of the SQLite file, or `pg_dump` for PostgreSQL into `~/pyarchinit_5/pyarchinit_DB_folder/_pga_backups`); the backup, which already existed for the period-field fixes, now also covers the chronology ones.
6. If the result is not what you wanted, press **Annulla ultimo fix** (undo last fix): the undo also reverts the corrections written to the periodization table.

### 8.3 Preview and backup

**The preview shows the computed date.** For each unit named by a problem, the preview pane shows its computed date in a line like this:

`US 4 · 1500–1549 · epoca · has_first_epoch → epoch_2_2`

The line gives, in order, the span of years, the rule that produced it, and the relation the constraint travelled along together with the node it came from. When the two ends of the span come from different routes, each end is labelled (`inizio …` and `fine …`), so a date is never attributed to the wrong relation. Today, in a normal database, every unit takes its dates from its own period, so most lines will read `epoca`. The point of the line is not to surprise you, but to let you see **where** a date comes from.

---

## 9. How to read the arcs of the matrix

Some choices in the matrix drawing may look odd, but they are not errors:

- **An arrow never passes under a node.** When the arrival column is occupied, the arrow enters the box **from the side**: this is normal.
- **Equality is not an overlap.** A «Uguale a» (Same as) or «Si lega a» (Bonds with) relationship puts the two units on the **same row**, side by side, joined by **two horizontal lines** (the equals sign) **with no arrowhead**.
- **Redundant arcs are not drawn.** If SU 1 covers 2 and 2 covers 3, the arrow from 1 to 3 does not appear, because it adds nothing. Inside a **cycle**, however, all arcs stay, because a cycle is an error you need to see.
- **The lines say which relationship they are.** Grey and solid: the sequence (covers, fills, abuts). **Dotted green**: a cut (`Taglia` / `Tagliato da`), whatever the stratigraphic definition and in any language. **Thick and black**: continuity — a small black diamond with no printed name (the name shows on hover), in its unit's column, so the line is straight. **Red**: an arrow climbing back up the bands, i.e. a contradiction between stratigraphy and chronology; a climbing cut is red **and** stays dotted.
- **Paradata are never a solid line.** They take colour and stroke from the Extended Matrix rules (`em_visual_rules.json`): brown-red dotted «extracted from», orange dashed «data provenance», gold dashed «property», grey dashed «generic connection», tomato dashed «combines» (solid in the file: the one deviation, because an arc towards a document must not look like an overlap).
- **Paradata sit under their unit.** The properties, extractors, combiners and documents of a unit are in its **group**, the dashed frame under its box, like EMStudio's paradata groups: one row for each step of the chain (the properties, then extractors and combiners, then the documents), and they do not count in the stratigraphic levels. A document used by several units appears in the group of each of them, as in EMStudio, and the paradata lines stay inside the group. Paradata that no unit reaches have a band of their own at the bottom («Paradati senza unità»). The panel header counts them apart: «114 unità · 739 paradati · 3 epoche · 90 rapporti» for TempluMare (from 5.13.126-alpha; before, paradata took part in the levels as units, and the matrix of a site like TempluMare became a tangle).
- **A brown border is masonry.** USM units — WSU, MSE, UEM, USZ, ΤΣΜ in the other languages — have the same box as the US, with a brown border instead of red.

---

## 10. Narrative with AI

Starting with **5.13.106-alpha**, the matrix panel inside QGIS (§2.2, "Vedi la matrice") has two tabs in its right-hand column: **Units** (*Unità*) — the details of the chosen unit, the zoom on the geometry and the media, as before — and **Narrative** (*Narrativa*), which is new. The Narrative tab has an AI write the **story of the site**, one chapter per epoch, and then lets you read it, have a person endorse it and export it to HTML, DOCX or PDF. It reads and writes **the same em.json** that EMStudio opens, in the s3dgraphy library format: the narrative you see here is the one EMStudio shows in its *Narrative* tab.

> **No new settings.** The tab has no configuration window of its own: it uses the AI you have already set up elsewhere in pyArchInit (§10.2).

> **The AI writes drafts, not final texts.** Every paragraph written by the model stays an "AI draft" until a person endorses it (§10.6), and in exported documents it carries the ⚠ mark.

The names of the tabs and buttons of the Narrative tab exist in Italian and in English: **they are in Italian if QGIS is in Italian, in English with any other language**. Both are always given here. The plugin's menu entries and dialog windows (such as "Vedi la matrice…" or the three buttons of §10.9) are, instead, in Italian only; the English translation is given in brackets.

### 10.1 Opening the Narrative tab

1. Open the menu **Plugins → pyArchInit - Archaeological GIS Tools** and choose the entry **Extended Matrix → Vedi la matrice…** (View the matrix).
2. Choose the **site**.
3. pyArchInit exports the site from the database to `<home>/pyarchinit_EM_folder/<site>.em.json` — `<home>` is `~/pyarchinit_5`, or the folder named by the `PYARCHINIT_HOME` environment variable — and opens the panel **"Matrice — `<site>`"**, docked to the right of the QGIS window. The file name is the site name, with special characters replaced by "_" (for example "Scavo 1" becomes `Scavo_1.em.json`).
4. In the right-hand column of the panel, click the **Narrative** tab.

<!-- IMMAGINE: Screenshot of the Plugins → pyArchInit - Archaeological GIS Tools menu with the entry "Extended Matrix → Vedi la matrice…" -->
![View the matrix menu](images/36_extended_matrix_s3dgraphy/01_menu_vedi_matrice.png)
*Figure 1: The "Extended Matrix → Vedi la matrice…" entry in the plugin menu*

<!-- IMMAGINE: Screenshot of the matrix panel docked on the right, with the Units and Narrative tabs -->
![Panel with two tabs](images/36_extended_matrix_s3dgraphy/03_pannello_due_schede.png)
*Figure 2: The matrix panel with the Units and Narrative tabs*

The file is **one per site and stays on disk**: it no longer lives in a temporary folder. It is the file EMStudio opens, and it is where the narrative is written. Every time you choose "Vedi la matrice…" the site is **exported again from the database** and the file is rewritten; the narrative already in it is kept (§10.8).

You can also reach the tab from two other places:

- from the **Extended Matrix → Esporta sito in em.json…** entry (Export site to em.json), which ends by offering the "Narrativa con l'AI" button (§10.9);
- from the **Vedi la matrice** button of the "Esporta Extended Matrix" window of the US form (§2.2): it opens the same panel on the file you have just exported, in the folder you chose.

### 10.2 Which AI is used

At the top of the Narrative tab a line says which AI it will use: **"Model: `<model>` (`<where it comes from>`)"**, followed by the reminder about EMStudio. If it finds none, it says **"No AI configured: set it in the US form with “Report” (AI provider) or with “Query AI Database”."** and the **Generate with AI** and **Regenerate chapter** buttons stay off.

The tab reads the AI settings **already saved** by the other pyArchInit windows, in this order, and uses the **first** one that has a model and — for network providers — the API key:

| # | Where it is set | What the tab calls it (en / it) |
|---|-----------------|----------------------------------|
| 1 | US form, "Report" button → "Generatore di Report" window (Report generator), "Provider AI" group | Report generator of the US form / Generatore di Report della scheda US |
| 2 | US form, "Query AI Database" button | Query AI Database / Query AI Database |
| 3 | palimpsestr window, "Report AI (analisi descrittiva)…" button, "Provider AI" selector | Palimpsest report / Relazione Palimpsest |
| 4 | "Generazione SQL con AI" window (text to SQL: see tutorial 30) | Text to SQL / Testo in SQL |

The providers are those of the "Provider AI" selectors: **OpenAI** and **Anthropic (Claude)** over the network, with the API key typed in the "API key" field; **Ollama** and **LM Studio** on your own computer, with no key. The selector saves your choice as soon as you change it. If you want another model, change it in the window the tab names in brackets (or in one that comes earlier in the list). The tab re-reads the settings **when the panel opens**: after changing them, open the matrix again.

### 10.3 The Narrative tab

```
┌─ Units ─┬─ Narrative ───────────────────────────────────────────────────────────────┐
│ Model: <model> (<where it comes from>) · If EMStudio has the                        │
│ file open, close it first: the last writer wins.                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ Presentation — to be written                                                        │
│ Early 15th century — AI draft                                                       │
│ 15th century — endorsed                                                             │
│ Modern age — AI draft, truncated                                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ The text of the chosen chapter, units quoted by name.                               │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ Chapter 3 of 9 · 15th century  *                                                    │
│ Language of the prose: [English ▾]                                                  │
│ [Generate with AI]  [Regenerate chapter]  [Endorse…]                                │
│ [Prepare the chapters]  [Choose the media]  [Show on the map]  [Export…]            │
│ [Open in EMStudio]  [Cancel]*                                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

\* The progress line and the "Cancel" button are visible only while the AI is writing. In this diagram the list rows are those of the sample site.

<!-- IMMAGINE: Screenshot of the Narrative tab with the chapter list, the text of the chosen chapter and the eight buttons -->
![Narrative tab](images/36_extended_matrix_s3dgraphy/04_scheda_narrativa.png)
*Figure 3: The Narrative tab*

From top to bottom:

- **the status line**: the model in use (§10.2) and the reminder *"If EMStudio has the file open, close it first: the last writer wins."*;
- **the chapter list**, one row per chapter: *Title — state*. A file from an earlier version, split by trench, shows all the graphs: each row is preceded by the graph name in square brackets, for example `[Saggio A] 15th century — AI draft`;
- **the text of the chosen chapter**: the prose, with units quoted by name — the names are **links**: a click shows the unit on the map (§10.10); under the paragraph where a unit is first named, up to two of its photos appear (§10.11). If the chapter has no prose yet you see its placeholder "[to be written: …]";
- **the progress line**, only while generating: "Chapter 3 of 9 · 15th century";
- **the language of the prose** (from 5.13.128-alpha): the language the AI writes the chapters in, and the one new chapter titles are born in (§10.4, "The language");
- **the buttons**, in two rows.

The result of every operation appears in the QGIS message bar, titled "Narrative".

When the file **has no narrative yet** the list is empty and a text says: *"No narrative in the file: “Prepare the chapters” builds the outline (N chapters over epochs and activities), “Generate with AI” writes it."*

#### The states of a chapter

| State (en / it) | What it means |
|-----------------|---------------|
| **to be written** / da scrivere | The chapter holds only the "[to be written: …]" placeholder. |
| **AI draft** / bozza AI | There is prose written by the model that no person has endorsed. One paragraph is enough: if the chapter has even a single unendorsed paragraph, this is its state, even if other prose is present. |
| **endorsed** / convalidato | All the AI's prose has been endorsed by a person. |
| **written** / scritto | Prose written by a person (in EMStudio). |
| **truncated** / troncato | Added to the state (for example "AI draft, truncated"): the model stopped because it reached the length limit, and the text ends halfway. |

#### The buttons

| Button (en) | In Italian | What it does |
|-------------|------------|--------------|
| **Generate with AI** | Genera con l'AI | Writes, **one at a time**, all the chapters still "to be written" — the **Presentation** first, then the epoch (and activity) ones; those already written are left alone. If there is no narrative yet, it first builds the outline. Shows the progress and the **Cancel** button. On only with a file open and an AI set up. On a narrative the file brings of its own — for instance TempluMare's, written in EMStudio — it adds no chapters: it writes only pyArchInit's chapters still to be written, if you added them with "Prepare the chapters" (up to 5.13.127-alpha it added them by itself). |
| **Regenerate chapter** | Rigenera capitolo | Rewrites **the chapter chosen** in the list: the unendorsed AI draft is replaced — but only once the model has answered: if the call fails, the earlier draft stays — and blocks already endorsed stay. It turns on when you choose the Presentation or an epoch or activity chapter and an AI is set up; for "Where it is" it stays off. The Presentation is pyArchInit's: the first chapter of a file's narrative (TempluMare's introduction) is not it, and is not regenerated. |
| **Endorse…** | Convalida… | Opens a menu with "This chapter" and "All chapters", then asks who endorses (§10.6). On when there is a narrative. |
| **Prepare the chapters** | Prepara i capitoli | Builds **only the outline** of the chapters, without AI: it works even if no AI is set up, so you can write by hand in EMStudio. It does not touch prose already written, and adds the chapters of new epochs. Result: "Chapters prepared: N." If the file brings a narrative of its own, it asks first: **Only the file's chapters** (nothing is added: "The file's N chapters stay as they are: no chapter added."), **Add pyArchInit's** (the Presentation, Where it is, one chapter for each epoch and each activity that has none, after the file's chapters, which stay untouched) or **Cancel**. It asks every time, until you add them. The new chapter titles are in the **language of the prose**. |
| **Choose the media** | Scegli i media | Since 5.13.130-alpha. For every chapter it chooses, among the media of the units it talks about — the records' 3D models, images and videos, and those of their evidence chain (the extractor's picture, the document's plate); not PDFs, which are sources —, those to put **inside the text**, after the paragraph that talks about them, with a caption in the **language of the prose**. With an AI set, the AI chooses, at **temperature zero**, only among those media, at most four per chapter; without an AI, or if its answer cannot be read, the choice is automatic: one medium per unit, in the order the text names them, at most three. The choice **stays in the file** (in the narrative's data) and the HTML export uses it, always the same, until you press the button again. The project database with the records' media is needed (for TempluMare, those imported from the em.json). Outcome: "Media chosen: N in M chapters (with the AI)". Enabled when there is a narrative. |
| **Show on the map** | Mostra sulla mappa | Selects and frames on the map, **all together**, the units the chosen chapter talks about (§10.10): those quoted in the prose or, if the chapter is not written yet, all those of its band. On only if at least one of the units the chosen chapter talks about is a row of the US form. |
| **Export…** | Esporta… | Saves the narrative as HTML (with the interactive map of the site, §10.7), DOCX or printable PDF (§10.7), with the photos of the cited units when there are any (§10.11). On when there is a narrative. |
| **Open in EMStudio** | Apri in EMStudio | Opens the em.json in EMStudio. If EMStudio is not there, the message bar points to the menu entry **Extended Matrix → Installa EMStudio…** (Install EMStudio). |
| **Cancel** | Annulla | Appears only while generating: the AI stops **after the chapter in progress** and what has been written is saved. |

While generating, every button is off except **Cancel**.

### 10.4 What the AI writes

**Which chapters.** The outline is the one from the s3dgraphy library (the "site_story" template):

- Since **5.13.110-alpha** the **Presentation** is a canonical chapter that the AI writes like the others, from a briefing of the whole site (see "The Presentation briefing" below); before, it stayed a placeholder. **Where it is** is the other canonical chapter and stays a "[to be written: …]" placeholder, to be written by hand in EMStudio: it is born from the site's position, and the library puts the map in it. It exists only if the graph carries a geographic position. The AI does not generate it.
- **One chapter per epoch** (period/phase) that has units, from the oldest to the most recent. The title is the name of the epoch, that is the "Datazione estesa" (extended dating) of the periodization; if it is missing, a generic name such as "Period 8 Phase 1" comes out: fill it in on the Periodization form to get readable titles. A unit appears in the chapter of the epoch where it is born and in those of the epochs where it survives.
- **One chapter per activity**, if the graph contains activity groups. A site exported from the database normally has none — the Activity field of the US form travels as a property of the unit — and then the chapters are the epoch ones.

**The file's narrative.** An EMStudio em.json can arrive with a narrative of its own: TempluMare brings 13 chapters by Emanuel Demetrescu, in English, written by him. pyArchInit keeps it as it is: its chapters are not touched, and those of the "site_story" template are added only with **Prepare the chapters** → **Add pyArchInit's** (up to 5.13.127-alpha "Generate with AI" and every export of the site added them too). A file chapter anchored to an activity counts as that activity's chapter: in TempluMare "Virtual Activity 2: colonnade" is anchored to activity VAct.03 and "Virtual Activity 4: Temple" to VAct.01, so VAct.02 and VAct.04 have no chapter and pyArchInit adds one ("VAct.02 Columnade", "VAct.04 Temple"): it is the file's anchors that need fixing.

**What the model receives.** For each epoch or activity chapter, a *briefing* with, for every unit: name, type and description; the filled-in fields of the US form (stratigraphic and interpretive definition, interpretation, period and phase, dating, activity, structure, trench, room, sector, area); the epochs; **the stratigraphic relationships** with the other units (covers, cuts, fills, abuts, equal to…) with their names; and, if there are any, the linked documentary sources. Units are listed **from the oldest to the most recent**, following the relationships. Beyond **80 units** per chapter the briefing is cut to the first 80. It also has a length cap (about 25,000 characters): beyond it, the long texts of the forms are shortened, repeated relationships and evidence chains are dropped and, if that is still not enough, the most recent units are left out. In both cases the model is told how many units are missing.

**The rules.** The model receives the library's five rules: write only what the context supports (no invented dates, materials, functions or events); keep uncertainty (a virtual unit is a hypothesis, not a fact); cite no source that is not there; write continuous prose, with no lists or headings; say openly when the context is too thin. It asks for one to three paragraphs.

**The Presentation briefing.** The Presentation has no units of its own: the model receives a briefing of the **whole site**, taken from the graph and not from the database, with the name of the site; the chain of place names (country → region → province → municipality); the places of the US form (areas, sectors, trenches, rooms); the epochs from the oldest to the most recent, each with how many units are present in it (the same unit can be in more than one epoch, so the sum can exceed the total); how many units there are and of what type, and how many stratigraphic relationships; the documents; the people named in the US forms; and the titles of the story's chapters. Its instructions are those of the Presentation, not the five rules above: they ask for two to four paragraphs saying what the site is and where it lies, which epochs the story covers, how the story is read (one chapter per epoch and per activity, units cited by name, and drafts marked as such until a person endorses them) and which sources it rests on; to use only the briefing, inventing no dates or facts, and to leave out a datum that looks odd rather than comment on it. The prose goes at the **top** of the chapter; the source cards (the documents) stay after it, and the placeholders "[to be written: a presentation of …]" and "[to be written: how this account is to be read…]" disappear.

**The language.** From 5.13.128-alpha it is chosen by whoever writes, in the **Language of the prose** drop-down of the tab: it starts from the language of the file's narrative, if it has one (TempluMare: English), otherwise from QGIS's. It applies to the prose the AI writes with "Generate with AI" and "Regenerate chapter" and to the titles of the new chapters "Prepare the chapters" adds ("Presentation", "Where it is"); chapters already written are not translated, and the same fixed chapter in another language is not added a second time. The model's instructions exist in Italian and English: for the other languages (German, French, Spanish, Catalan, Portuguese, Romanian, Greek, Arabic) the model receives the English ones with the request to write in that language. Up to 5.13.127-alpha the prose was always born in the language of the narrative: with TempluMare, in English even with QGIS in Italian.

**How it is saved.** In the library format, the one EMStudio reads: a narrative node (`NarrativeNode`) holding the chapters; every paragraph written by the model is an "AI draft" block attributed to that model's **AI author**; the **prompt** used is registered as an extractor linked to the sources, so you can trace what was asked. The units quoted in the text are **mentions** (`[[name]]`): in the file they stay linked to the unit's node, and in the tab and in the exports they appear with its name. A mention that matches no unit in the graph is reduced to plain words, without brackets.

**Costs and times.** The model is called **once per chapter**, the Presentation included. With a network provider each call has a cost and a waiting time (in trials with a network model, a few tens of seconds per chapter: a site with about ten epochs takes a few minutes); with Ollama or LM Studio nothing is paid, but times depend on your computer.

### 10.5 Step by step

1. Open the site's matrix (§10.1) and click the **Narrative** tab. Check at the top **which model** it will use.
2. **Close EMStudio** if it has the file open: pyArchInit and EMStudio write the same file, and whoever writes last wins.
3. Optional: **Prepare the chapters** to see the outline, without AI.
4. Click **Generate with AI**. Watch the progress: the Presentation, if it is still "to be written", goes first ("Chapter 1 of 9 · Presentation"), then the epoch chapters ("Chapter 3 of 9 · …"); you can keep using QGIS. At the end the message bar says, for example, *"7 chapters generated, 1 failed: Modern age — …"* (with *"(cancelled)"* if you cancelled) and the list reloads: the chapters written are "AI draft".
5. **Read**: pick one chapter after the other and read the text under the list. Check it against the stratigraphy: it is a draft built from the data of the US form. To see where the units it talks about lie, click their names or use **Show on the map** (§10.10).
6. If a chapter does not convince you, pick its row and click **Regenerate chapter**. The new draft **replaces** the previous unendorsed one: if you want to keep the earlier version, export it first. If a chapter is "truncated", regenerate it **before** endorsing.
7. When a chapter is right, click **Endorse…** (§10.6).
8. **Export…** to HTML, DOCX or PDF (§10.7), or **Open in EMStudio** to write "Where it is" by hand and polish the rest.
9. Later you can open the matrix again: the narrative stays (§10.8).

<!-- IMMAGINE: Screenshot of generation in progress: the progress line "Chapter 3 of 9 · …" and the Cancel button -->
![Generation in progress](images/36_extended_matrix_s3dgraphy/05_generazione_in_corso.png)
*Figure 4: Generation in progress, with the progress line and the Cancel button*

A chapter that fails does not stop the others: the summary says which. To retry, just click **Generate with AI** again, which writes only the chapters still "to be written".

### 10.6 Endorsing: who signs

Endorsing means that a **person** takes responsibility for the text the model wrote. It never happens on its own: not by generating, not by saving.

1. Click **Endorse…**. A small menu opens: **"This chapter"** — on only if the chosen chapter is an "AI draft" — or **"All chapters"**, that is all the AI drafts not yet endorsed, in every graph of the file. The Presentation is endorsed like any other chapter: choose it in the list and "This chapter" endorses it on its own.
2. A window asks **"Who endorses? Pick an author or type a new name."** The list holds the **human authors already in the graph** — the people named in the US form as compiler (*schedatore*), US director and US supervisor — and you can type a new name, which becomes a new author of the graph.
3. The message bar says **"N blocks endorsed by `<name>`."**, or "Nothing to endorse." The file is saved.

<!-- IMMAGINE: Screenshot of the Endorse… menu ("This chapter" / "All chapters") and of the window for choosing the author -->
![Endorse](images/36_extended_matrix_s3dgraphy/06_convalida.png)
*Figure 5: Endorse: the menu and the choice of author*

The blocks go from "AI draft" to "endorsed". In the exported document the person appears among those responsible ("a cura di", edited by) and the model as assistant ("con l'assistenza di", with the assistance of), and endorsed paragraphs no longer carry the ⚠ mark. Regenerating does not delete endorsed blocks: a signature is an act, and is not lost by rewriting.

### 10.7 Exporting to HTML, DOCX or PDF

Click **Export…**: the save window opens with three formats: "HTML page" (`.html`), "Word document" (`.docx`) and "Printable PDF" (`.pdf`). The suggested name is `<site>_narrativa`, with no extension, in the folder of the em.json: the extension is added by the format chosen in the window's filter; an extension typed by hand (`.html`, `.docx` or `.pdf`) wins over the filter. The message bar confirms: "Narrative exported to `<path>`".

The document contains:

- the title of the narrative (for example "Scavo archeologico — the story of the site"), those responsible ("a cura di") and the model as assistant ("con l'assistenza di");
- **the contents** (since 5.13.129-alpha), after the title: the chapters — grouped by part when the titles say so, as in "Rilievo e analisi — Introduction" —, under each its subheadings, and the Sources last. In the HTML every entry leads to its chapter; in the PDF the contents have page numbers and the chapters are also PDF bookmarks; in Word it is a real table of contents (a field), with the titles already written, which Word updates with page numbers when the file opens (answer "Yes" when it asks to update the fields; in LibreOffice: right-click the contents → Update);
- for each chapter the prose first, with the units quoted by their name, then the list of the units of the chapter; for quoted units that have photos, a strip of photos stands in place of their line (§10.11);
- the **subheadings** written in the prose with "### " (TempluMare has twelve, from "Past researches" on) become headings, in the HTML, in Word and in the PDF, and italics written "\*…\*" are italics in Word and in the PDF too (since 5.13.129-alpha; before, the marks were printed);
- at the end of each chapter the **Chapter sources** line (since 5.13.129-alpha): the documents the units the chapter talks about rest on — following the paradata: unit → property → extractor (or combiner) → document — and those the chapter cites itself. In the HTML every source is a **hotspot**: hovering it shows a card with the preview (the first page of the PDF or the picture), the type and the description; clicking it opens a panel on the right with the file — the PDF can be read there, the picture is shown whole —, the "Open the file" link, the path of the original and the **readings** that come from it (unit — property, with the extractor). Esc or the × close the panel. The file goes into the page if it weighs up to 2 MB (25 MB in all); beyond that, card and panel show the preview and the link to the original, which opens on the computer that exported the page. The files are found the way the record finds them: the media of the document's row, the original or its copy in the resized folder; with no database connected the sources have title, description and readings but not the files. In Word and in the PDF the line lists the sources with their description;
- **the chosen media** (since 5.13.130-alpha, in the HTML) with **Choose the media**: each after its paragraph, with the caption and, below, the unit and the file name. They are hotspots like the sources: hovering shows the card, clicking opens the panel on the right — the whole picture, the video with its player, and for a **3D model** (GLB) the **interactive viewer**: you turn it with the mouse or a finger and zoom with the wheel. The viewer uses the three.js that is inside the page (since 5.13.133-alpha): it works without a network too; before it was Google's model-viewer, which loaded from the internet. If a model does not open in the viewer the panel says so, and the file opens with "Open the file". The large views of the models are drawn at export time, in a separate process (a few seconds more); GLB models and videos go into the page up to 15 MB each and 60 MB in all. In Word and in the PDF the photo strips of the cited units stay (§10.11);
- **the units of the chapter** (since 5.13.130-alpha, in the HTML): instead of the library's cards in a row — units, paradata, documents and photo strips, in TempluMare's "II A.D." chapter 367 notes one below the other, the paradata without saying which unit they belong to — a **Units of the chapter** block ("104 units, 339 paradata"), with one row per unit — name, type, description — that opens onto the table of its paradata: property, value and where it comes from, one document at a time with its extractors, the document as a hotspot; and onto the unit's photo or model view, when there is one. The documents stay in the chapter's sources line;
- **the map of the site** (since 5.13.115-alpha, in the HTML only), in a fixed box: on the right on wide screens, at the top on a phone. With the map the page gets wider (since 5.13.116-alpha) and the text keeps a readable column. At rest it shows all the units of the graph in light grey; clicking the name of a unit in the text shows **only the units of that chapter's period** as outlines with the number on top, the clicked one **coloured**, and frames the group; clicking a chapter title does the same, without the coloured unit. The line under the map gives the period and how many units; "whole site" returns to the full view. The geometries come from the US and USM views of the project database at the moment of the export (the graph's site, units matched by area and number): a quoted unit with no drawing has the link and nothing on the map; with no database connected the document has no map;
- **the 3D scene of the proxies** (from 5.13.132-alpha, HTML only), in the map's fixed panel: with drawings and proxies, the **Map** and **3D** tabs; with proxies only — TempluMare — the panel has only the 3D. The proxies are those of the units, as EMStudio draws them (unit → «geometry» property → shape → `proxies/<unit>.glb`), taken from the database like the other media; each one carries its own position in the scene, and put together they fit. At rest they have the colours of their materials, the EM colour code. A click on a unit's name in the text — now a link even without the map — highlights its proxy, full and with an orange outline, makes those of the same period transparent and the others almost invisible, and frames it; a click on a chapter title shows the proxies of its period full or, for a chapter anchored to an activity, those of its units; «whole site» goes back to everything. You turn the scene with the mouse or a finger and zoom with the wheel or two fingers; hovering a proxy shows its name, clicking it selects its unit, on the map too. The caption gives the period, how many proxies and the unit («no 3D proxy» when it has none). With the keyboard too (since 5.13.133-alpha): Tab moves onto the scene, the arrows move the view, + and − zoom in and out, Esc goes back to the whole site. three.js is inside the page: the scene works without a network. A proxy goes into the page up to 15 MB, 40 MB in all; those left out are counted. On TempluMare: 65 proxies, 2.4 MB;
- at the end the **Fonti** (sources) section: the documents the story rests on and the "Prompt" entry, which points to the prompt recorded in the file. Since 5.13.129-alpha the list also has the chapters' sources, each with its description, and in the HTML they are hotspots like those of the chapters; so are the "fonte" cards inside the chapters and the documents cited in the text.

Things worth knowing:

- **unendorsed drafts go in**, each preceded by "⚠︎ non validato da una persona" (not validated by a person), and the header says how many blocks are in this state. For a document without marks, endorse first (§10.6). In the HTML the draft reads like the rest of the text, with the same font and background: above the paragraph there is the notice line and on the left an amber rule. In Word and in the PDF the notice sits in front of the paragraph (in the PDF on a line of its own, without the ⚠ sign, §10.11);
- **all chapters go in**, even those still "to be written": their "[to be written: …]" placeholder stays in the text;
- the prose sits **at the head** of the chapter, before the list of the units; in a narrative written with an earlier version it may still be at the bottom, and it is put right by exporting the site again (§10.8) or with **Prepare the chapters**;
- figures an author planned in EMStudio (for example the matrix of an epoch) are not drawn by pyArchInit's export: a placeholder stays in the document;
- the HTML is a single, self-contained file (the photos are embedded too, and the map is an SVG inside the file, with no external libraries: it also opens on a phone with no network); the DOCX opens with Word or LibreOffice and needs the `python-docx` package, and the PDF the ReportLab library (§10.11): both are among the plugin's requirements; since 5.13.129-alpha the HTML also carries the files of the sources, up to 2 MB each and 25 MB in all: with many PDFs the page weighs more.

<!-- IMMAGINE: Screenshot of the exported HTML document: a chapter with a draft preceded by "⚠︎ non validato da una persona" -->
![Exported HTML document](images/36_extended_matrix_s3dgraphy/07_documento_html.png)
*Figure 6: The exported HTML document, with an unendorsed draft marked*

### 10.8 Exporting the site again: the narrative stays

Exporting the site again from the database — with **Vedi la matrice…**, with **Esporta sito in em.json…** or with the "Esporta Extended Matrix" window of the US form — **keeps the narrative** already in the destination file: prose, endorsements, AI author and prompts. Epochs born in the meantime receive a chapter "to be written". A notice says so: **"Narrative kept from the previous file (N chapters)."** You see it in the message bar with "Vedi la matrice…", in the summary of the "Esporta Extended Matrix" window and, with "Esporta sito in em.json…", in the details of the final window.

**A site imported from an em.json** (§5) also has the imported file's narrative, which the import's memory puts back into the export. From 5.13.128-alpha the more recent one wins: if the working file was saved after the import — "Prepare the chapters", "Generate with AI", "Endorse…", or EMStudio on the same file — its narrative travels, with the usual notice; if the em.json was imported later, the imported one stays, and a notice says so: *"The previous file's narrative was not kept: the em.json imported on … is newer, and its narrative wins. Backup copy of the previous file in …."* Up to 5.13.127-alpha the imported one always won: the chapters prepared and written in the panel vanished at the next export, with a notice that wrongly blamed the file shape.

**Other changes** made to the file in EMStudio — node positions, rewritten descriptions — **do not survive**, as before: the file is regenerated from the database. Only the narrative is kept.

Before rewriting a file that holds a narrative, pyArchInit makes a **safety copy** next to it: `<site>.em.json.bak` (every new export replaces the previous copy).

If the earlier file was split by trench (versions up to 5.13.108-alpha could export one graph per trench), at the first re-export the new file has **a single graph** for the whole site: the graphs have different names and the narrative **cannot travel** into the new file. A notice says so: *"The previous file's narrative (graphs: …) did not travel into the new file (graphs: …): the file shape changed. Backup copy in …"*. The text is not lost: it is in the `.bak` copy, which however is replaced by the next export of a file that holds a narrative — put it somewhere safe. If you need the old narrative, open that copy (renamed to an `.em.json` file with a different name); otherwise generate the chapters again in the new file (§10.5). From 5.13.109-alpha on, the file always has a single graph and the narrative travels from one export to the next.

If the previous file cannot be read (for example a file left half-written), the export goes ahead anyway: the unreadable file is **renamed** `<site>.em.json.broken` and a notice says *"The previous file cannot be read (…): its narrative, if any, was not kept."*

> **The narrative is not in the pyArchInit database: it lives only in the em.json.** A database backup does not copy it. Copy the `pyarchinit_EM_folder` folder from time to time.

### 10.9 From the "Esporta sito in em.json…" entry

The entry **Extended Matrix → Esporta sito in em.json…** writes the same file `<site>.em.json` in `pyarchinit_EM_folder`. At the end it shows "Esportato `<path>`" (Exported), with the counts of nodes, edges and notices (the text of the notices is in the details of the window), and **three buttons**:

| Button | What it does |
|--------|--------------|
| **Apri in EMStudio** (Open in EMStudio) | Opens the file in EMStudio; if it is not installed, it offers to install it. |
| **Narrativa con l'AI** (Narrative with AI) | Appears **only if an AI is set up** (§10.2): opens the matrix panel already on the Narrative tab. |
| **Chiudi** (Close) | Closes the window. |

<!-- IMMAGINE: Screenshot of the final window of "Esporta sito in em.json…" with the three buttons -->
![Export site to em.json: three buttons](images/36_extended_matrix_s3dgraphy/08_esporta_tre_bottoni.png)
*Figure 7: The final window of "Esporta sito in em.json…"*

### 10.10 The units on the map

Starting with **5.13.108-alpha**, the Narrative tab brings the units a chapter talks about onto the **QGIS map**, in two ways:

- **One unit: click its name.** In the text of the chosen chapter the names of the quoted units are **links**: a click selects that unit on the loaded US layer and frames the map on it, with a flash. It opens nothing.
- **All together: "Show on the map"** (*Mostra sulla mappa*), in the second row of buttons, between "Prepare the chapters" and "Export…". It selects and frames together all the units the chosen chapter talks about: those quoted in the prose or, if the prose quotes none (for example because the chapter is not written yet), all the units of its band (the epoch). The selection is one per layer — it replaces the one that was there — and the framing takes in all the geometries found, which flash.

<!-- IMMAGINE: Screenshot of QGIS with the units of the chapter selected on the map and, at the top, the message bar "Highlighted 5 of 6 units in “US view” (7 geometries). Not drawn: 1.US9." -->
![The units of the chapter on the map](images/36_extended_matrix_s3dgraphy/09_unita_sulla_mappa.png)
*Figure 8: The units a chapter talks about, selected on the map, and the message bar*

A layer with the geometries of the US must already be loaded in the project, for example pyArchInit's **US view**: the tab looks for it among the loaded layers, like the "Zoom sulla geometria" button of the Units tab (tutorial 01), recognising the units by the `sito`, `area` and `us` fields. **The project is not modified**: no layer is added, only the selection and the framing of the map change. Since **5.13.110-alpha**, if more than one layer carries the same fields — as the US view (polygons) and the elevations view (points) do — the tab tries the fullest geometry first: polygons, then lines, then points; the order of the layers in the legend counts only when everything else is equal. The same goes for the "Zoom sulla geometria" button: the US view no longer needs to be moved to the top of the legend.

The message bar ("Narrative") says what was found, for example *"Highlighted 5 of 6 units in “US view” (7 geometries). Not drawn: 1.US9."* The name in quotes is the layer where the units were found, as it appears in QGIS's layers panel; a unit can have more than one geometry, so the geometries can outnumber the units. Only units that are rows of the US form are searched: a document or a continuity node has no geometry and does not enter the count. If more than five units are not drawn, the names stop at the first five, followed by "…" and the total.

A click on a name that is not a row of the US form finds nothing, and the message bar says so. If no loaded layer has the fields to recognise the units, the message says so: load the US view (§10.13).

### 10.11 The photos of the units and the PDF

Starting with **5.13.108-alpha**, the narrative also shows the **photos** of the units it talks about — in the text of the tab and in the exports — and can also be saved as a **printable PDF**.

**In the chapter text.** Under the paragraph where a unit is first named, **up to two thumbnails** of its media appear: they are the same ones as in the Units tab, read from the project's thumbnails folder, and under them, in small type, are the name of the unit and the names of the media. If the unit is named again in the same chapter, the photos are not repeated.

**In the exports.** In all three formats, for each unit quoted in the prose that has images on disk, a **strip with one or two photos side by side** stands in place of the unit's text line, with the unit's name as caption: the resized copy is used if there is one, otherwise the thumbnail. Units not quoted in the prose stay as a line of text. The photos are embedded in the file: HTML and DOCX are written by the s3dgraphy library, the PDF by pyArchInit.

**The printable PDF.** It is an A4 document written with ReportLab, in the Cambria font like the plugin's other PDFs (if the font file is not in pyArchInit's `bin` folder, it uses Helvetica). It holds the title, those responsible ("edited by") and the model as assistant ("with the assistance of"); at the top, if there are unendorsed drafts, a notice with their number also appears; then all the chapters, as in the other formats, each with its prose — the quoted units written by name, and before every unendorsed paragraph a line "non validato da una persona", without the ⚠ sign — followed by the photos with their caption and by the other units in small type; at the end the sources. The footer has "Generated by pyArchInit on …" with the date, and the page number.

<!-- IMMAGINE: Side-by-side screenshots: the text of a chapter with the thumbnails under the first mention of a unit, and a page of the printable PDF with the strip of photos and its caption -->
![Photos of the units in the text and in the PDF](images/36_extended_matrix_s3dgraphy/10_foto_e_pdf.png)
*Figure 9: The photos of the units in the chapter text and on a page of the PDF*

**What it needs.** The photos are not in the em.json: they are read from the project's database and folders. So you need the database linked (the matrix opened from the project), the **Thumbnail path** and **Image resize** paths set in the configuration (tutorial 01) and the files on disk; for the text, the thumbnails folder is enough. Images on remote storage are not used. If something is missing there is no message: the photos simply do not appear, and the export succeeds anyway (§10.13).

### 10.12 Warnings

- **Close EMStudio before generating or endorsing.** If EMStudio has the file open, whoever writes last wins.
- **An AI writes only from what it finds in the graph, and it can be wrong.** The rules restrain it, they do not make it infallible: read every chapter before endorsing it.
- **With a network provider the data leaves your computer.** The briefing of each chapter (names, definitions, descriptions and relationships of the units) and that of the Presentation (site name, place names, places, epochs, documents and the names of the people named in the US forms) are sent to the chosen service; with Ollama or LM Studio they stay local.
- **The file is written at the end.** Generation saves when it finishes, even if you cancelled it: do not close QGIS while the AI is writing. Saving is safe: the file is written alongside, read back, and only then replaces the real one; if anything goes wrong, **the previous file stays as it was**.
- **Do not open the matrix again while the AI is writing.** The tab stays on the previous file and warns: *"Generation in progress: wait for it to finish, or press Cancel, before changing file."*
- **The text is edited in EMStudio**, not in pyArchInit.
- The narrative and the nodes that carry it (AI author, prompts) **do not appear in the matrix drawing**.

### 10.13 Troubleshooting

| Message (en / it) | Cause | Remedy |
|-------------------|-------|--------|
| "No AI configured…" / «Nessuna AI impostata…» | None of the four windows of §10.2 has a model (and, for OpenAI and Anthropic, the API key). | Set provider and model — and the key — in one of those windows, then **open the matrix again**: the tab re-reads the settings only when it opens. Even without an AI you can prepare the chapters, endorse, export and open EMStudio. |
| "No narrative in the file…" / «Nessuna narrativa nel file…» | The file has no narrative yet (normal the first time). | Click **Prepare the chapters** (outline) or **Generate with AI** (outline and prose). The number N counts the epoch and activity chapters the outline will have (an epoch with no units gets none); the "Chapters prepared" message also counts "Presentation" and, if present, "Where it is". "Generate with AI" also writes the "Presentation", which N does not count: the progress counts one chapter more. |
| "EMStudio is not installed…" / «EMStudio non risulta installato…» | The program was not found on the computer. | Use the menu entry **Extended Matrix → Installa EMStudio…** (it has this name with any QGIS language). |
| "truncated" / «troncato» next to the state | The model stopped at the length limit and the text ends halfway. | Before endorsing, **Regenerate chapter**; if it happens again, finish the chapter in EMStudio. |
| "N chapters generated, M failed: `<title>` — `<reason>`" / «N capitoli generati, M falliti: …» | The provider refused the request (invalid key, quota, model not available) or the local server does not answer. "the model wrote nothing" means the reply was empty. | Remove the cause and click **Generate with AI** again: it writes only the chapters left "to be written". |
| "The previous file cannot be read (…)" / «Il file precedente non si legge (…)» | At re-export the existing file was not a readable em.json. | The export went ahead: the unreadable file was kept next to the new one as `….broken`, and the narrative it held, if any, did not travel into the new file. If you need it, recover it from that file or from a backup. |
| "The previous file's narrative (graphs: …) did not travel into the new file…" / «La narrativa del file precedente (grafi: …) non è passata nel file nuovo…» | The earlier file was split by trench (versions up to 5.13.108-alpha): the graphs have different names and the narrative cannot travel. | The earlier file is in the `.bak` copy: open that one if you need the old narrative, or generate the chapters again in the new file. |
| "Could not write … The previous file is intact." / «Non sono riuscito a scrivere … Il file precedente è intatto.» | Saving failed (full disk, locked file, permissions). | Fix it and repeat: the chapters generated in that session had not been saved. |
| "DocX export needs python-docx — install the extra: …" (always in English) | The `python-docx` package is not installed in QGIS's Python: it is needed only for DOCX. | Install `python-docx` (it is one of the plugin's requirements), or export to HTML, which needs nothing. |
| "None of the loaded layers has the fields to recognise the units…" / «Nessuno dei layer caricati porta i campi per riconoscere le unità…» | The open project has no layer carrying the `sito`, `area` and `us` fields of the units (for example pyArchInit's US view): the tab searches only among the layers already loaded. | **Load pyArchInit's US view** (or a layer with the same fields) into the project, then click the name or **Show on the map** again. The tab does not add layers by itself. Since 5.13.110-alpha there is no need to move it to the top of the legend: with the same fields the tab tries polygons first (§10.10). Loaded from the US form with a style chosen (the "Style Choice" window, tutorial 14), the US view also carries the unit number in a circle. Since 5.13.111-alpha the elevations view (points), loaded from the US form, also carries the elevation value (two decimals) above its symbol. The style and labels of the view are set in the "View styles" window (menu entry "View styles…", tutorial 14); since 5.13.112-alpha a default saved there takes precedence at load time. |
| No message: the photos do not appear in the chapter text or in the exports | The photos are read from the project's database and folders, and something is missing: the database is not linked (the matrix was opened without it), the **Thumbnail path** folder does not exist on this computer or is remote storage, the files are not on disk, or the unit is not a row of the US form or has no media. | Check the **Units** tab: if the unit shows its thumbnails there, you will find them here too. Otherwise open the matrix from the project, check **Thumbnail path** and **Image resize** in the configuration (tutorial 01) and that the files are on the computer: images on remote storage do not come in. The export succeeds anyway, without photos. |

---

## References

- Upstream issue LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- pyarchinit repository: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
