# modules/db/concurrency_manager.py

## Overview

This file contains 21 documented elements.

## Classes

### ConcurrencyManager

Manager for handling concurrent database modifications

#### Methods

##### __init__(self, parent)

Initializes a new `ConcurrencyManager` instance for handling concurrent database modifications. Sets the `parent` attribute to the provided argument and initializes both `current_user` and `db_username` to `None`, where `db_username` is intended to be assigned upon establishing a database connection.

##### check_version_conflict(self, table_name, record_id, current_version, db_manager, id_field)

Check if there's a version conflict for a record

Args:
    table_name: Name of the table
    record_id: ID of the record
    current_version: Version number currently in the form
    db_manager: Database manager instance
    id_field: Name of the ID field (optional, will be guessed if not provided)

Returns:
    dict with conflict info or None

##### handle_conflict(self, table_name, record_data, conflict_info)

Handle a version conflict

Args:
    table_name: Name of the table
    record_data: Current form data
    conflict_info: Information about the conflict

Returns:
    User's choice ('overwrite', 'reload', 'cancel')

##### lock_record(self, table_name, record_id, db_manager)

Create a soft lock on a record (informational only)

Args:
    table_name: Name of the table
    record_id: ID of the record
    db_manager: Database manager instance

##### unlock_record(self, table_name, record_id, db_manager)

Remove soft lock from a record

Args:
    table_name: Name of the table
    record_id: ID of the record
    db_manager: Database manager instance

##### get_active_editors(self, table_name, record_id, db_manager)

Get list of users currently editing a record

Args:
    table_name: Name of the table
    record_id: ID of the record
    db_manager: Database manager instance

Returns:
    List of tuples (username, editing_since)

##### set_username(self, username)

Set the current username for the session

##### get_username(self)

Get the current username, preferring database username over OS username

### ConflictResolutionDialog

Dialog for resolving version conflicts

**Inherits from**: QDialog

#### Methods

##### __init__(self, parent, table_name, record_data, last_modified_by, last_modified_timestamp)

Initializes a `ConflictResolutionDialog` instance by calling the parent `QDialog` constructor with the given `parent` widget. Sets the default resolution choice to `'cancel'` and delegates UI construction to `init_ui`, passing `table_name`, `record_data`, `last_modified_by`, and `last_modified_timestamp`.

##### init_ui(self, table_name, record_data, last_modified_by, last_modified_timestamp)

Initialize the UI

##### reload_choice(self)

User chose to reload from database

##### overwrite_choice(self)

User chose to overwrite

##### cancel_choice(self)

User chose to cancel

##### get_choice(self)

Get the user's choice

### RecordLockIndicator

Visual indicator for record locks

#### Methods

##### __init__(self, parent_widget)

Initialize lock indicator

Args:
    parent_widget: The form widget to attach the indicator to

##### show_lock_status(self, editors)

Show who's currently editing the record

Args:
    editors: List of (username, editing_since) tuples

##### clear_lock_status(self)

Clear the lock status indicator

