# modules/db/permission_handler.py

## Overview

This file contains 7 documented elements.

## Classes

### PermissionHandler

Handles permission errors and provides user-friendly messages

#### Methods

##### __init__(self, parent_form, language)

Initializes a permission error handler instance with a reference to the parent form and an optional language setting. Sets `self.form` to the provided `parent_form`, `self.L` to the specified `language` (defaulting to `'it'`), and `self.db_manager` to `None`.

##### set_db_manager(self, db_manager)

Set the database manager

##### has_permission(self, table_name, permission_type)

Check if user has specific permission on table
Returns True if permission exists, False otherwise

##### handle_permission_error(self, error, operation, show_message)

Handle permission errors with user-friendly messages
Returns True if error was handled, False otherwise

##### handle_database_error(self, error, context, show_message)

Handle database errors with user-friendly messages
Returns True if error was handled, False otherwise

