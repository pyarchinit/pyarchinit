# PyArchInit - StratiGraph: Sync Panel

## Index
1. [Introduction](#introduction)
2. [Accessing the Panel](#accessing-the-panel)
3. [Understanding the Interface](#understanding-the-interface)
4. [Exporting Bundles](#exporting-bundles)
5. [Synchronization](#synchronization)
6. [Queue Management](#queue-management)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)
9. [Frequently Asked Questions](#frequently-asked-questions)

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

[Open Interactive Animation](../../stratigraph_sync_animation.html)
