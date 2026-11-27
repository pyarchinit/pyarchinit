# PyArchInit - StratiGraph: Sync Panel

> The panel and the room window follow the language of the QGIS interface; the buttons are quoted here as they appear in English.

## Index
1. [Introduction](#introduction)
2. [Accessing the Panel](#accessing-the-panel)
3. [Understanding the Interface](#understanding-the-interface)
4. [Exporting Bundles](#exporting-bundles)
5. [Synchronization](#synchronization)
6. [Queue Management](#queue-management)
7. [Sending a Site to a StratiGraph Room](#sending-a-site-to-a-stratigraph-room)
8. [Configuration](#configuration)
9. [Troubleshooting](#troubleshooting)
10. [Frequently Asked Questions](#frequently-asked-questions)

---

## Introduction

Starting from version **5.0.2-alpha**, PyArchInit includes a **StratiGraph Sync** panel that enables offline-first data synchronization with the StratiGraph Knowledge Graph. This panel is part of the European **StratiGraph** project (Horizon Europe) and implements the offline-first workflow: you work locally without internet, export bundles when ready, and the system synchronizes automatically when connectivity is restored.

<!-- VIDEO: Introduction to StratiGraph Sync -->
> **Video Tutorial**: [Insert video link StratiGraph Sync introduction]

### Workflow Overview

```
1. Work offline         2. Export Bundle       3. Auto-sync
   (OFFLINE_EDITING)       (LOCAL_EXPORT)        (QUEUED_FOR_SYNC)
        |                      |                      |
   Normal data entry     Export + Validate      Upload when online
   in PyArchInit         + Enqueue              with auto-retry
```

---

## Accessing the Panel

The StratiGraph Sync panel is hidden by default and can be toggled via a toolbar button.

### From the Toolbar

1. Look for the **StratiGraph Sync** button in the PyArchInit toolbar -- it has a green icon with sync arrows and the letter "S"
2. Click the button to **show** the panel (it is a checkable toggle button)
3. Click the button again to **hide** the panel

The panel appears as a **left dock widget** in the QGIS interface. You can drag and reposition it as with any QGIS dock panel.

<!-- IMAGE: Toolbar button for StratiGraph Sync -->
> **Fig. 1**: The StratiGraph Sync toolbar button (green icon with sync arrows and "S")

<!-- IMAGE: Panel docked on the left side of QGIS -->
> **Fig. 2**: The StratiGraph Sync panel docked on the left side of the QGIS window

---

## Understanding the Interface

> **Since version 5.18.1 the panel shows only «Send site to a room…» and the log.** Status, connection, queue, «Export Bundle», «Sync Now» and «Queue…» are hidden: they belong to the Phase 2 bundle sync, while the StratiGraph node exchanges **rooms and operations**, not bundles. The sections below, up to «Sending a Site to a StratiGraph Room», describe that mechanism: it will come back, or be removed, once node-to-node sync is decided.

The StratiGraph Sync panel is divided into several sections, from top to bottom.

### State Indicator

The **state indicator** at the top of the panel shows the current synchronization state of your data. The possible states are:

| State | Icon | Description |
|-------|------|-------------|
| **OFFLINE_EDITING** | Pencil | You are working locally, editing data normally |
| **LOCAL_EXPORT** | Package | A bundle is being exported from local data |
| **LOCAL_VALIDATION** | Checkmark | The exported bundle is being validated |
| **QUEUED_FOR_SYNC** | Clock | The bundle has been validated and is waiting to be uploaded |
| **SYNC_SUCCESS** | Green circle | The most recent synchronization completed successfully |
| **SYNC_FAILED** | Red circle | The most recent synchronization attempt failed |

### Connection Indicator

Below the state indicator, the **connection indicator** shows whether the system can reach the StratiGraph server:

| Status | Meaning |
|--------|---------|
| **Online** | The health check endpoint is reachable; automatic sync is active |
| **Offline** | The health check endpoint is not reachable; bundles will be queued |

The system automatically checks connectivity every **30 seconds** (configurable).

### Queue Counter

The **queue counter** displays two numbers:

- **Pending bundles**: Number of bundles waiting to be uploaded
- **Failed bundles**: Number of bundles whose upload has failed (these will be retried automatically)

### Last Sync

Shows the **timestamp** and **result** (success or failure) of the most recent synchronization attempt.

### Action Buttons

| Button | Action |
|--------|--------|
| **Export Bundle** | Creates a bundle from your local data, validates it, and adds it to the sync queue |
| **Sync Now** | Forces an immediate synchronization attempt (only available when online) |
| **Queue...** | Opens the queue management dialog showing all entries |
| **Send site to a room...** | Signs in to a StratiGraph node and brings a site into a room (see below) |

### Activity Log

At the bottom of the panel, a scrollable **activity log** displays timestamped entries of recent activity, including state changes, exports, validations, and sync attempts.

<!-- IMAGE: Full panel with all sections annotated -->
> **Fig. 3**: The complete StratiGraph Sync panel with all sections labeled

---

## Exporting Bundles

Exporting a bundle packages your local archaeological data into a structured format ready for upload to the StratiGraph Knowledge Graph.

### Step-by-Step Export

1. Ensure you have saved all your current work in PyArchInit
2. Open the StratiGraph Sync panel (if not already visible)
3. Click the **Export Bundle** button
4. The system performs three operations automatically:
   - **Export**: Local data is packaged into a bundle file
   - **Validate**: The bundle is checked for completeness and data integrity
   - **Enqueue**: The validated bundle is added to the sync queue
5. Watch the **state indicator** cycle through: `LOCAL_EXPORT` -> `LOCAL_VALIDATION` -> `QUEUED_FOR_SYNC`
6. The **activity log** records each step with a timestamp

### What Is Included in a Bundle

A bundle contains all archaeological entities that have UUIDs (see Tutorial 31 for UUID details). Each entity is identified by its `entity_uuid`, ensuring that the same record is always recognized on the server.

<!-- IMAGE: Export Bundle button and state transition -->
> **Fig. 4**: Clicking "Export Bundle" and observing the state changes in the panel

---

## Synchronization

### Automatic Synchronization

When the system detects that you are **online** (health check succeeds), it automatically uploads all pending bundles from the queue. No manual intervention is required.

The automatic sync process:

1. Connectivity check passes (health check endpoint responds)
2. The connection indicator switches to **Online**
3. Pending bundles in the queue are uploaded one by one
4. Successfully uploaded bundles are marked as `SYNC_SUCCESS`
5. The **last sync** timestamp and result are updated

### Manual Synchronization

If you want to force an immediate sync attempt:

1. Ensure the connection indicator shows **Online**
2. Click the **Sync Now** button
3. The system immediately attempts to upload all pending bundles

The **Sync Now** button is only effective when the system is online.

### Automatic Retry with Exponential Backoff

If an upload fails, the system does **not** give up. Instead, it retries automatically with increasing delays:

| Attempt | Delay |
|---------|-------|
| 1st retry | 30 seconds |
| 2nd retry | 60 seconds |
| 3rd retry | 120 seconds |
| 4th retry | 5 minutes |
| 5th retry | 15 minutes |

This prevents overloading the server when it is temporarily unavailable while ensuring eventual delivery.

<!-- IMAGE: Sync Now button and connection indicator -->
> **Fig. 5**: The "Sync Now" button and connection status indicator

---

## Queue Management

The **Queue...** button opens a detailed dialog where you can inspect all bundles in the sync queue.

### Queue Dialog Columns

| Column | Description |
|--------|-------------|
| **ID** | Unique identifier for the queue entry |
| **Status** | Current status of the entry (pending, syncing, success, failed) |
| **Attempts** | Number of upload attempts made so far |
| **Created** | Timestamp when the bundle was first added to the queue |
| **Last Error** | Error message from the most recent failed attempt (empty if no error) |
| **Bundle path** | File system path to the bundle file |

### Interpreting Queue Entries

- **Pending** entries are waiting to be uploaded
- **Success** entries have been uploaded and confirmed by the server
- **Failed** entries will be retried automatically; check the **Last Error** column for details
- The **Attempts** count helps you understand how many times the system has tried to upload a particular bundle

### Queue Storage

The queue database is stored as a SQLite file at:

```
$PYARCHINIT_HOME/stratigraph_sync_queue.sqlite
```

This file persists between QGIS sessions, so pending bundles are not lost if you close QGIS.

<!-- IMAGE: Queue dialog showing several entries -->
> **Fig. 6**: The queue management dialog with bundle entries

---

## Sending a Site to a StratiGraph Room

Since version **5.14.0-alpha** the **Send site to a room...** button brings a site into a *room* of a StratiGraph node (StratiGraph Server). The site's graph becomes the room's content, where EMStudio, EM Tools and the project's other tools see it and work on it.

![StratiGraph Sync panel](images/32_stratigraph_sync/06_sync_panel_send_button.png)

> **Fig. 7**: The StratiGraph Sync panel with the **Send site to a room...** button

### Step-by-Step Procedure

1. In the **StratiGraph Sync** panel, click **Send site to a room...**
2. **Node**: the node's address, for example `https://node.example.org/em`. It is remembered between sessions.
3. **Site**: choose the site. **Room id** and **Room title** are filled in from the site name and can be changed; the room id is one word, without spaces.
4. Click **Sign in...**: the node's sign-in page opens in the browser. Sign in with your account and go back to QGIS: the **Identity** line shows your name and whether you may create rooms. If the node has a Keycloak client dedicated to pyArchInit, its name goes in the QGIS setting `pyArchInit/stratigraph/client_id`; otherwise the client the node names is used.
5. Optional: **Plan only** shows what would be sent without writing anything on the node.
6. Click **Send site**: the log reports the exported nodes and edges and the result.

![Send site to a room window](images/32_stratigraph_sync/07_send_site_dialog.png)

> **Fig. 8**: The window after signing in and sending the sample site to a development node: 745 operations applied, 0 refused, the database kept as a reference

### What Is Sent

- The whole site's graph, as one graph even when the site has several trenches: this way relations between units of different trenches travel with the rest.
- Files cited by the graph are uploaded once. Sending the same site again duplicates nothing.
- **Database files are never uploaded** (sqlite, spatialite, gpkg): the room keeps only a reference. The other sites in your database stay on your computer.
- Your password never passes through pyArchInit: you type it only on the node's page. The access token stays in memory and is gone when the window closes.

### From the Command Line

The same transfer without QGIS (without `--dry-run` it really writes; without `--token` it opens the browser to sign in):

```bash
python scripts/stratigraph_send_site.py --db ~/pyarchinit_5/pyarchinit_DB_folder/pyarchinit_db.sqlite \
    --site "Scavo archeologico" --node https://nodo.example.org/em --room scavo-2026 --dry-run
```

### Working with a Room That Already Holds Data

When others work in the room too (EMStudio, StratiField, EM Tools), after signing in:

1. **Compare with room** compares the site with the room in both directions, writing nothing: what the room has that is new for pyArchInit (new units, changed definitions, relations) and what pyArchInit adds to the room.
2. **Send changes** sends the room the work done here: new units and relations, fields changed here, relations removed here. What changed only in the room is not touched; a field changed on both sides is a conflict and is only shown (see «Sync with memory»).
3. **Pull from room** brings the room into pyArchInit's records (SU, definitions, periodisation, relations), recognising each record by its identifier. If the pull would remove local relations the room does not know, the window lists them and asks for confirmation.

**Pull from room** can also rebuild a site in a database that does not have it: the units come back with number, type, definitions and periodisation. Continuity units (CON) do not travel: pyArchInit regenerates them with **Genera continuita**.

The room receives the whole SU record, not only the graph's fields: description, interpretation, colour, consistency, levels, measures, trench, room, square, sector, the masonry (USM) fields. A record rebuilt from a room equals the original; relations change only in how they are written (with area and site). A room sent with an earlier pyArchInit version holds only the graph's fields: the comparison shows many differing fields; a new **Send site** completes it.

All of this works with both SQLite and PostgreSQL. To rebuild a site an empty pyArchInit database, created and opened in pyArchInit, is enough: **Pull from room** fills it (site, records, periodisation, relations, media). Relations always have four elements: type, SU, area, site.

![Compare with room](images/32_stratigraph_sync/08_compare_with_room.png)

> **Fig. 9**: Comparing with a room that was also worked on in EMStudio: a new SU and a revised definition in the room, a new pyArchInit SU to send

### Photos and Media in the Room

Photos, videos, 3D models and documents linked to SU records travel with the site, in both directions. Orthophotos and other rasters stay out: they are QGIS layers, not pyArchInit media.

- **Send site** and **Send changes** upload each file to the room's store only once: a file the room already has (same content) is not sent again. If the original is no longer on disk, the copy in the Resize folder is used.
- **Pull from room** downloads new media into the `stratigraph_media/<room>` folder of the pyArchInit home, makes thumbnail and copy as when a file is loaded from the form, and links them to their SU with description and tags. A medium the database already has (recognised by its identifier) is not downloaded again: only its link is checked.
- Media of finds, pottery, tombs and structures stay local for now: the window counts them.

![A new photo sent to the room](images/32_stratigraph_sync/09_room_media.png)

> **Fig. 10**: A photo added to SU 3 after the site was sent: the comparison finds it and Send changes uploads the file and its link

### Sync with Memory

After the first **Pull from room** (or the first **Send site**) pyArchInit remembers the room as it was at that moment: the common *base*, saved in the `stratigraph_rooms` folder of the pyArchInit home, one per database, site and room. From then on:

- the comparison reads from the room **only what is new** since the last sync, not the whole document;
- every difference has an author: **changed here** (sent), **changed in the room** (the pull brings it), **changed on both sides** (a conflict, shown with both values), **removed in the room** (the pull removes it here too), **removed here** (sent);
- **Pull from room** never silently overwrites work not yet sent: if there are local edits, conflicts, relations removed here, the window lists them and suggests sending them first. In a confirmed conflict the room's value wins.
- the fields pyArchInit **computes** (stratigraphic order, period code, dating) are never edits nor conflicts: at the end of the pull pyArchInit recomputes them by itself, as the SU form's buttons do;
- **relations are a set**: those added here and not yet sent stay after the pull, together with those others added in the room;
- if you confirm a pull that replaces local values, those values **are not lost**: **Restore replaced values** puts them back, and they become changes to send again.

Units the pull leaves out on purpose (generated CON continuity units and their media) stay in the room and do not count as removals. It works the same with SQLite and PostgreSQL.

![Three-way comparison](images/32_stratigraph_sync/10_three_way_compare.png)

> **Fig. 11**: The comparison after a sync: a field changed here to send, one changed in the room to pull, a conflict on the same field

### Geometries: site, trenches, areas and cuts

The drawings of pyArchInit's GIS layers travel with the site too, as footprints in their own reference system: the **site** polygon (`pyarchinit_siti_polygonal`), the **trenches** (`pyarchinit_sondaggi`), **areas and sectors** (`pyarchinit_ripartizioni_spaziali`) and the **cuts**, i.e. the negative SU (`pyunitastratigrafiche`). They leave from SQLite and from PostGIS.

**Pull from room** writes them back into the layers, SpatiaLite or PostGIS, in the layer's reference system: a missing feature is added, an identical one is left alone, and a feature **drawn differently here stays as it is** and is reported: the pull never overwrites a local drawing.

Orthophotos and rasters stay in QGIS.

### Excavation plans: the polygons of positive SU

The polygons of positive SU are not the unit's geometry (for the Extended Matrix that is the 3D model) but its **documentation**: they travel as **excavation plans**, in the shape agreed with the s3dgraphy team.

- The site has **one document**, «Piante di scavo · *site*», which stays open while the excavation goes on.
- Each **plan** is the set of polygons drawn for one SU on one date, in the SU layer or in the USM layer. In the room it is a documentary representation model (RMDoc) of the document, linked to its SU.
- The geometry is a **GeoJSON file** with its reference system, one per plan, uploaded to the room's store like the photos. The graph only carries the node, its links and the file's address.

**Send site** sends the plans with the records. **Pull from room** downloads the ones missing here and writes them into the `pyunitastratigrafiche` and `pyunitastratigrafiche_usm` layers, with their columns (type, draughtsman, date…). A plan that already exists here, the same or not, is never touched: a different one is reported in the log. A polygon drawn on a SU the records do not have stays out, and the log says so.

Plans are documentation, not records: they never appear among the changes to send. A new plan drawn here goes to the room with a new **Send site**.

### Common Problems

| Message | What to do |
|---------|------------|
| `401` or sign-in expired | The session renews itself while you work; if it has expired completely (many hours unused) click **Sign in...** again |
| ⚠ «Number … belongs to several units» | In the same area two units share a number with different types: rapporti name a unit only by number, area and site, so in the room they reach both. Renumber one of them before sending |
| `403` / *may create rooms: False* | Your account has no role in the room or may not create rooms: ask the node's administrator |
| `CERTIFICATE_VERIFY_FAILED` | The node uses a local certificate (development or field node): install its CA on your computer, or use `--ca-file` on the command line |
| `409 ... already declared` | The room exists and belongs to another user: choose another id |

---

## Configuration

### Health Check URL

The system uses a health check URL to determine connectivity to the StratiGraph server. You can configure this in QGIS settings:

| Setting | Key | Default |
|---------|-----|---------|
| Health check URL | `pyArchInit/stratigraph/health_check_url` | `http://localhost:8080/health` |

To change the health check URL:

1. Open **QGIS** -> **Settings** -> **Options** (or use the QGIS Python console)
2. Navigate to the PyArchInit settings or set via:

```python
from qgis.core import QgsSettings
s = QgsSettings()
s.setValue("pyArchInit/stratigraph/health_check_url", "https://your-server.example.com/health")
```

### Check Interval

The default connectivity check interval is **30 seconds**. This can also be configured via QgsSettings.

---

## Troubleshooting

### The panel does not appear

- Ensure you are using PyArchInit version **5.0.2-alpha** or later
- Check that the StratiGraph Sync toolbar button is visible in the toolbar
- Try toggling the button off and on again
- Check **View** -> **Panels** in QGIS to see if the dock widget is listed

### Connection indicator always shows "Offline"

- Verify that the StratiGraph server is running and reachable
- Check the health check URL in settings (default: `http://localhost:8080/health`)
- Test the URL manually in a browser or with `curl`:

```bash
curl http://localhost:8080/health
```

- If the server is on a different machine, ensure there are no firewall rules blocking the connection

### Export Bundle fails

- Ensure the database is connected and accessible
- Verify that your records have valid UUIDs (Tutorial 31)
- Check the activity log for specific error messages
- Ensure sufficient disk space for the bundle file

### Sync fails repeatedly

- Check the **Last Error** column in the Queue dialog for details
- Common causes:
  - Server is temporarily unavailable (the system will retry automatically)
  - Network connectivity issues
  - Server rejected the bundle (check server logs)
- If a bundle consistently fails after many attempts, consider re-exporting it

### Queue database issues

- The queue database is at `$PYARCHINIT_HOME/stratigraph_sync_queue.sqlite`
- If corrupted, you can safely delete it -- pending bundles will be lost, but you can re-export them
- Back up this file if you need to preserve the queue state

---

## Frequently Asked Questions

### Do I need internet to use PyArchInit?

**No.** PyArchInit is fully functional offline. The StratiGraph Sync panel only handles synchronization with the StratiGraph server. You can work entirely offline and export/sync when ready.

### What happens if I close QGIS with pending bundles?

Pending bundles are saved in the queue database and will be available when you restart QGIS. The system will resume synchronization automatically when connectivity is restored.

### Can I export multiple bundles?

Yes. Each time you click "Export Bundle", a new bundle is created and added to the queue. Multiple bundles can be queued and will be uploaded sequentially.

### How do I know if my data has been synced?

Check the **last sync** indicator in the panel for the most recent result. You can also open the **Queue...** dialog to see the status of each individual bundle.

### Does StratiGraph Sync work with both PostgreSQL and SQLite?

Yes. The sync system works with both database backends supported by PyArchInit. Bundles are exported in a database-independent format.

### What is the relationship between UUIDs and sync?

UUIDs (Tutorial 31) provide the stable identifiers that make synchronization possible. Each entity in a bundle is identified by its UUID, allowing the server to correctly match, create, or update records.

---

*PyArchInit Documentation - StratiGraph Sync*
*Version: 5.0.2-alpha*
*Last update: February 2026*

---

## Interactive Animation

Explore the interactive animation to learn more about this topic.

[Open Interactive Animation](../../animations/stratigraph_sync_animation.html)
