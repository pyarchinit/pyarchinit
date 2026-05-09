# modules/stratigraph/connectivity_monitor.py

## Overview

This file contains 8 documented elements.

## Classes

### ConnectivityMonitor

Monitors network connectivity to the StratiGraph server.

Emits signals when connectivity status changes.  Uses a debounce
counter so that N consecutive identical results are required
before the reported state actually flips.

**Inherits from**: QObject

#### Methods

##### __init__(self, parent, check_interval_ms, debounce_count)

Initializes the connectivity monitor instance, configuring its check interval and debounce count either from the provided arguments or from `QgsSettings` values (falling back to module-level defaults). Also reads the health-check URL from `QgsSettings` and initializes internal state fields (`_is_online`, `_consecutive_same`, `_last_probe_result`) to their default values. A `QTimer` is created and connected to `_do_check`, which will drive periodic connectivity probing once started.

##### is_online(self)

*No description available.*
**Type:** `property` → `bool`

Returns the current online connectivity status of the instance. This read-only property exposes the internal `_is_online` flag, reflecting the result of the most recent connectivity check performed by the periodic checking mechanism.

##### start(self)

Start periodic connectivity checks.

##### stop(self)

Stop periodic checks.

##### check_now(self)

Force an immediate connectivity check.

##### set_check_interval(self, ms)

Update the check interval (milliseconds).

