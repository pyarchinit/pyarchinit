# modules/stratigraph/sync_orchestrator.py

## Overview

This file contains 8 documented elements.

## Classes

### SyncOrchestrator

Ties together state machine, queue and connectivity.

Automatically processes the queue when connectivity is available
and retries failed uploads with exponential backoff.

**Inherits from**: QObject

#### Methods

##### __init__(self, parent)

Initializes the `SyncOrchestrator` instance by calling the parent constructor and setting up the core components: a `SyncStateMachine`, a `SyncQueue`, and a `ConnectivityMonitor`. Sets the `_running` and `_processing` flags to `False`, and reads the upload endpoint URL from `QgsSettings`, defaulting to `"http://localhost:8080/api/v1/bundles"` if no value is stored. Connects the `ConnectivityMonitor`'s `connection_available` signal to the `_process_queue` slot so that queue processing resumes automatically when connectivity is restored.

##### start(self)

Start the orchestrator and connectivity monitor.

##### stop(self)

Stop the orchestrator and connectivity monitor.

##### export_bundle(self, site_name)

Run the full export -> validate -> enqueue pipeline.

Returns a result dict with keys: success, bundle_path, errors.

##### sync_now(self)

Force an immediate sync attempt if online.

##### get_status(self)

Return a snapshot of the orchestrator's status.

