# modules/stratigraph/sync_queue.py

## Overview

This file contains 13 documented elements.

## Classes

### QueueEntry

*No description available.*
A dataclass representing a single entry in a processing queue, storing the identity, state, and tracking information for a bundle awaiting or undergoing processing. Each entry holds a unique integer `id`, the bundle's file path and hash, creation timestamp, and current `status`, along with an `attempts` counter and optional fields for the last attempt timestamp, last error message, and arbitrary metadata. Default values are provided for `attempts` (0), `last_attempt_at` (None), `last_error` (None), and `metadata` (empty dict).

**Decorators**: dataclass

### SyncQueue

Persistent FIFO queue backed by SQLite.

Default database location:
    ``$PYARCHINIT_HOME/stratigraph_sync_queue.sqlite``

#### Methods

##### __init__(self, db_path)

Initializes the instance by resolving the SQLite database path and ensuring the required schema exists.

If `db_path` is not provided, the path defaults to `stratigraph_sync_queue.sqlite` located in the directory specified by the `PYARCHINIT_HOME` environment variable (or the current directory if the variable is not set). After storing the resolved path in `_db_path`, the method calls `_ensure_schema()` to set up the database structure.

##### enqueue(self, bundle_path, bundle_hash, metadata)

Add a bundle to the queue. Returns the new entry id.

##### dequeue(self)

Take the oldest pending entry and mark it 'uploading'.

Returns None if no pending entries exist.

##### mark_completed(self, entry_id)

Mark an entry as completed.

##### mark_failed(self, entry_id, error)

Mark an entry as failed.

If attempts < MAX_ATTEMPTS, status reverts to 'pending' for retry.
Otherwise it stays 'failed'.

##### retry_failed(self, entry_id)

Reset a failed entry back to pending.

##### get_pending(self)

Return all pending entries ordered by creation time.

##### get_all(self)

Return all entries ordered by creation time (newest first).

##### cleanup_completed(self, older_than_days)

Remove completed entries older than *older_than_days*.

##### get_stats(self)

Return counts by status.

