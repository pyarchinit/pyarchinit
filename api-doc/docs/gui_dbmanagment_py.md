# gui/dbmanagment.py

## Overview

This file contains 23 documented elements.

## Classes

### BackupThread

Thread for running backup operations with progress tracking

**Inherits from**: QThread

#### Methods

##### __init__(self, command, env, file_path)

Initializes the worker thread instance by calling the parent class constructor and storing the provided `command`, `env`, and `file_path` arguments as instance attributes. Sets `self.process` to `None` as the initial state for the process handle. This constructor prepares the object to execute a backup command within a controlled environment when the thread is started.

##### run(self)

Run the backup command

### pyarchinit_dbmanagment

*No description available.*
A `QDialog` subclass that provides a graphical interface for managing PyArchInit database backup and restore operations. It supports both PostgreSQL (via `pg_dump`/`pg_restore`) and SQLite (via file copy) databases, with controls for creating backups, selecting and restoring existing backup files, and displaying backup history through a calendar widget and list view. Database configuration is loaded from a `config.cfg` file at initialization, and the available GUI controls are enabled or disabled according to the detected database type.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, iface)

Initializes the database management dialog by calling the parent constructor, setting up the UI, and storing the provided `iface` reference. Connects button signals (`backup`, `backupsqlite`, `upload`, `restore`) and, where the corresponding widgets exist, connects `calendarWidget` and `listWidget_backups` to their respective slot methods. Completes initialization by loading the database configuration, configuring the GUI based on the database type, populating the backup list and calendar, setting `currentLayerId` to `None`, and applying the active theme via `ThemeManager`.

##### load_db_config(self)

Load database configuration from config file

##### setup_gui_by_db_type(self)

Setup GUI elements based on database type

##### enable_button(self, n)

*No description available.*
Sets the enabled state of the `backup` button by passing the parameter `n` directly to its `setEnabled` method. The value of `n` controls whether the button is interactive or disabled. This method provides a direct interface for toggling the `backup` button's availability from external callers.

##### enable_button_search(self, n)

*No description available.*
Enables or disables the `backup` widget by passing the value `n` to its `setEnabled` method. The behavior of this method is identical to `enable_button`, both directly delegating to `self.backup.setEnabled(n)`.

##### on_backupsqlite_pressed(self)

*No description available.*
Handles the SQLite database backup action triggered by the corresponding UI button. It reads the current database connection string and application configuration from `config.cfg` to resolve the source SQLite file path, then copies it to the `pyarchinit_db_backup/` directory under `PYARCHINIT_HOME` with a timestamped filename in the format `backup_<database>_<YYYYMMDD_HH_MM>.sqlite`. On success, the progress bar is set to 100%, a summary message box displaying the backup filename and file size is shown, and the backup list and calendar widgets are refreshed; on failure, a critical error message box is displayed with the exception details.

##### on_backup_pressed(self)

*No description available.*
Handles the backup button press event by reading database connection settings from `config.cfg`, constructing a `pg_dump` command with compression level 9 in custom format (`-Fc`), and writing the output to a timestamped `.backup` file in the `pyarchinit_db_backup/` directory under `PYARCHINIT_HOME`. The backup is executed asynchronously via a `BackupThread` instance, whose `progress_update`, `message_update`, and `finished_signal` signals are connected to the corresponding UI update slots. During the operation, the progress bar is initialised and the backup button is disabled; if `pg_dump` is not found or an exception occurs before the thread starts, a warning dialog is displayed and the method returns early.

##### update_progress(self, value)

Update progress bar

##### update_message(self, message)

Update status message

##### backup_finished(self, success, message)

Handle backup completion

##### update_backup_list(self)

Update the list of available backups

##### update_calendar(self)

Update calendar to show backup dates

##### on_calendar_date_selected(self, date)

Handle calendar date selection

##### on_backup_selected(self, item)

Handle backup selection from list

##### on_upload_pressed(self)

Opens a file dialog prompting the user to select a backup file (`.backup` or `.sql`) starting from the default backup directory (`self.BK`). If a file is selected, the chosen path is written to the `lineEdit_bk_path` field and persisted in `QgsSettings` under the key `'pyArchInit/last_backup_path'`, and the restore button is enabled. An informational message box is then displayed showing the selected file's name and size in megabytes.

##### show_restore_options_dialog(self, current_db_name)

Show dialog to choose restore options

##### on_restore_pressed(self)

Handles the database restore operation triggered by the restore button, reading the backup file path from `lineEdit_bk_path` and database connection parameters from the corresponding UI fields or the application configuration file. It presents the user with restore mode options (overwrite existing database or create new) via `show_restore_options_dialog`, then sequentially executes the necessary PostgreSQL command-line tools (`dropdb`, `createdb`, `pg_restore`, `psql`) to drop, recreate, and restore the target database, including PostGIS extension setup, sequence correction, and user management table creation. Upon completion, it updates `progressBar_db` and displays a success or error message via `QMessageBox` depending on whether critical errors were detected in the restore output.

## Functions

### on_radio_changed()

*No description available.*
Callback function triggered when the state of the `radio_overwrite` toggle changes. It enables or disables the `new_db_input` field based on whether `radio_new` is selected, and updates `warning_label` accordingly — displaying a blue informational message when a new database will be created, or a red warning message when the overwrite option is active. This function is connected to the `toggled` signal of `radio_overwrite`.

