# gui/stratigraph_sync_panel.py

## Overview

This file contains 5 documented elements.

## Classes

### QueueDialog

Modal dialog listing all queue entries.

**Inherits from**: QDialog

#### Methods

##### __init__(self, queue, parent)

Initializes a `QueueDialog` instance by calling the parent `QDialog` constructor with the optional `parent` widget. Sets the window title to `"StratiGraph — Sync Queue"`, resizes the dialog to 700×400 pixels, and stores the provided `queue` reference in `self._queue`. Completes initialization by invoking `_build_ui()` to construct the interface and `_refresh()` to populate it with current queue data.

### StratiGraphSyncPanel

Dock widget providing a quick overview and controls for
the StratiGraph sync system.

**Inherits from**: QDockWidget

#### Methods

##### __init__(self, orchestrator, parent)

Initializes the `StratiGraphSyncPanel` dock widget with the title `"StratiGraph Sync"` and object name `"StratiGraphSyncPanel"`, storing the provided `orchestrator` reference as `_orch` and setting `_last_sync_msg` to an empty string. Calls `_build_ui()` and `_connect_signals()` to construct the interface and wire up event handlers, then starts a `QTimer` that triggers `_refresh_stats()` every 5000 milliseconds. Concludes by invoking `_refresh_all()` to populate the panel with its initial state.

