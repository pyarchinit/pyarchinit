# gui/pyarchinitConfigDialog.py

## Overview

This file contains 93 documented elements.

## Classes

### PyArchInitLogger

Simple file-based logger for debugging

#### Methods

##### __init__(self)

Initializes a new `PyArchInitLogger` instance by determining the system's temporary directory using the `tempfile` module. Sets the `log_file` attribute to the full path of a file named `pyarchinit_debug.log` located within that temporary directory.

##### log(self, message)

Write a message to the log file with timestamp

##### log_exception(self, function_name, exception)

Log an exception with traceback

##### clear_log(self)

Clear the log file

### pyArchInitDialog_Config

`pyArchInitDialog_Config` is a QGIS configuration dialog (`QDialog`) for the PyArchInit archaeological data management plugin, combining UI setup from a Designer-generated class (`MAIN_DIALOG_CLASS`). It manages database connection parameters for both SQLite/SpatiaLite and PostgreSQL/PostGIS backends, including connection profiles, CRS selection, file path settings for thumbnails and external tools (Graphviz, PostgreSQL binaries), and duplicate-handling strategies for data import. The dialog also provides tabs for database installation, bidirectional data import/export between databases, database schema updates, local-to-remote database synchronization, and an optional Rust acceleration module management interface.

**Inherits from**: QDialog, MAIN_DIALOG_CLASS

#### Methods

##### __init__(self, parent, db)

Initializes the PyArchInit configuration dialog by setting up the user interface, applying theming, and configuring all dialog components including Supabase Sync, Rust Acceleration, and database connection profile tabs. Loads existing settings via `load_dict()`, `charge_data()`, and `summary()`, then establishes signal-slot connections for all interactive controls such as combo boxes, line edits, push buttons, and tool buttons. Also initializes the logger, configures CRS widgets, conditionally disables Graphviz and PostgreSQL path controls if the respective binaries are already detected, and sets up remote storage tooltips and configuration support.

##### setup_admin_features(self)

Setup admin-only features like user management

##### setup_db_connection_profiles(self)

Add connection profiles UI to the main database settings tab

##### setup_supabase_sync_tab(self)

Setup a dedicated tab for database synchronization (supports any PostgreSQL server)

##### setup_rust_acceleration_tab(self)

Setup a tab for optional Rust acceleration module management.

##### sync_analyze_differences(self)

Analyze differences between local and remote databases

##### save_all_sync_credentials(self)

Save both local and remote sync credentials

##### check_us_field_migration_needed(self)

Check if US, area, nr_cassa fields need migration from INTEGER to TEXT

##### check_if_updates_needed(self)

Check if database updates are needed

##### update_db_button_style(self)

Update the database update button style based on whether updates are needed

##### update_database_schema(self)

Apply all database schema updates for both SQLite and PostgreSQL

##### check_if_concurrency_installed(self)

Check if concurrency system is already installed

##### apply_concurrency_system(self)

Apply concurrency system to all tables

##### open_user_management(self)

Open user management dialog

##### open_activity_monitor(self)

Open real-time activity monitor

##### on_users_changed(self)

Called when users/permissions are changed

##### convert_db(self)

*No description available.*
Evaluates the currently selected source (`comboBox_server_rd`) and destination (`comboBox_server_wt`) database server types to determine which conversion button should be visible in the UI. If the source is `'postgres'`, the PostgreSQL conversion button is hidden and the SQLite conversion button is shown, and vice versa for `'sqlite'`. If both the source and destination are the same server type, or if the source selection is empty, both conversion buttons (`pushButton_convert_db_pg` and `pushButton_convert_db_sl`) are hidden.

##### on_pushButton_convert_db_sl_pressed(self)

*No description available.*
Handles the press event of the SQLite conversion button by prompting the user with a warning dialog (in Italian) asking whether to overwrite or update the target SQLite database. Retrieves the current database connection parameters and constructs the destination SQLite file path using the home directory, the `pyarchinit_DB_folder` subdirectory, and the value from `lineEdit_database_wt`. Depending on the user's response, executes an `ogr2ogr` system command to convert a PostgreSQL database to SpatiaLite format — using `-overwrite` if the user confirms with **Ok**, or `-append` if the user cancels — with `KeyError` exceptions caught and displayed via a warning dialog in the overwrite branch.

##### on_pushButton_convert_db_pg_pressed(self)

*No description available.*
Handles the conversion of a SQLite database to a PostgreSQL database using `ogr2ogr`, invoked when the corresponding push button is pressed. It first displays a warning dialog (`QMessageBox`) asking the user whether to overwrite or append to the target PostgreSQL database, then constructs and executes the appropriate `ogr2ogr` command via `os.system` based on the user's choice. If the user confirms with **Ok**, the command runs with the `-overwrite` flag; if cancelled, it runs with the `-append` flag instead. A `KeyError` is caught and reported via a warning dialog in the overwrite branch only.

##### sito_active(self)

*No description available.*
Establishes a database connection using the `Connection` class and retrieves the current site set configuration. It extracts the `'sito_set'` value from the dictionary returned by `conn.sito_set()` and returns it as a string. This method serves as a accessor for the active site set identifier associated with the current connection.

##### check_table(self)

Refreshes the `comboBox_mapper_read` and `comboBox_Database` UI controls, then establishes a database connection using the current `Connection` configuration to determine whether the backend is SQLite or PostgreSQL. Based on the selected index of `comboBox_mapper_read`, it loads the corresponding database table (indices 1–18, mapping to tables such as `site_table`, `us_table`, `periodizzazione_table`, and others) as a `QgsVectorLayer` and populates the `mFeature_field_rd` combo box with the field names retrieved from the table's data provider, excluding the first and last fields. After populating the field list, it attempts to clear and update `mFeature_value_rd` and invoke `value_check` with the resolved table name.

##### value_check(self, table)

*No description available.*
Refreshes and repopulates the `mFeature_value_rd` widget with distinct values retrieved from the specified `table`. It queries the database using `DB_MANAGER.group_by` with the current field and mapper selections, removes any empty entries from the result, sorts the list, and adds the sorted items back to the widget. All exceptions are silently suppressed.

##### check_geometry_table(self)

*No description available.*
Refreshes the geometry combo box and database combo box UI controls, then establishes a database connection to determine whether the backend is SQLite or PostgreSQL. Based on the current selection index of `comboBox_geometry_read` (indices 1–16), it opens the corresponding pyarchinit geometry table as a `QgsVectorLayer` using the appropriate provider (`spatialite` or `postgres`), retrieves the layer's field names via the data provider, and populates `mFeature_field_rd` with those field names. After updating the field list, it clears `mFeature_value_rd` and calls `value_check_geometry` with the resolved table name to populate the value selector, suppressing any exceptions that occur during that final step.

##### value_check_geometry(self, table)

*No description available.*
Populates the `mFeature_value_rd` list widget with distinct values retrieved from the specified `table`, grouped by the field currently selected in `mFeature_field_rd` and filtered by the current geometry selection in `comboBox_geometry_read`. The retrieved values are processed through `UTILITY.tup_2_list_III`, sorted alphabetically, and any empty string entries are removed before being added to the widget. The method clears and refreshes `mFeature_value_rd` both before and after the update; all exceptions are silently suppressed.

##### test3(self)

*No description available.*
Validates a SQLite database connection by constructing the database path from the home directory and the value entered in `lineEdit_dbname_sl`, then checks whether the `pyarchinit_quote_usm` table exists in the database. If the table is absent, a warning dialog is displayed prompting the user to update the database. When running QGIS version 3.20.0 or later, it additionally executes `CheckSpatialMetaData()` and warns the user if the SpatiaLite metadata version requires conversion.

##### test(self)

Connects to the configured SQLite database located in the `pyarchinit_DB_folder` directory and performs a schema migration on multiple pyarchinit spatial tables. For each affected table (`pyarchinit_us_negative_doc`, `pyarchinit_strutture_ipotesi`, `pyarchinit_sondaggi`, `pyarchinit_siti_polygonal`, `pyarchinit_siti`, `pyarchinit_ripartizioni_spaziali`, `pyarchinit_reperti`, `pyarchinit_quote`, `pyarchinit_punti_rif`, `pyarchinit_linee_rif`, `pyarchinit_individui`, `pyarchinit_documentazione`, `pyarchinit_campionature`, and `pyarchinit_sezioni`), the method recreates the table with an updated schema by copying existing data through a temporary table, then restores the associated geometry triggers. Any exception raised during execution is silently suppressed.

##### test2(self)

Attempts to apply schema modifications to a SQLite database by establishing a connection and verifying that the active connection string references a SQLite backend; if not, the method returns immediately. When a valid SQLite database file is found, it executes a SQL script that disables foreign key constraints, recreates the `pyarchinit_reperti_view` view with a join between `pyarchinit_reperti` and `inventario_materiali_table`, and creates the `pottery_table` table if it does not already exist, before re-enabling foreign key constraints. Any `KeyError` or general exception encountered during execution triggers an attempt to close the database connection before silently suppressing the error.

##### setComboBoxEnable(self, f, v)

*No description available.*
Iterates over a list of field names provided in `f` and dynamically calls `setEnabled(v)` on each corresponding widget by constructing and evaluating a command string. The boolean or truthy value `v` determines whether each named widget is enabled or disabled. Widget references are resolved at runtime via `eval`.

##### customize(self)

Enables the `lineEdit_DBname` field unconditionally for both SQLite and PostgreSQL database types by calling `setComboBoxEnable`. Guards against recursive invocations using a `_customizing` flag, which is set to `True` at entry and reset to `False` in a `finally` block. If a `logger` attribute is present, the method logs the current database type from `comboBox_Database` and the enabled state of the `DBname` field.

##### db_uncheck(self)

*No description available.*
Unchecks the `toolButton_active` toggle button by setting its checked state to `False`. This method provides a programmatic way to deactivate the active database toggle button in the UI.

##### upd_individui_table(self)

*No description available.*
Reconstructs the `individui_table` in a SQLite database by performing a four-step migration: copying the existing table into a temporary table (`sqlitestudio_temp_table_`), dropping the original, recreating it with the full schema definition (including primary key and unique constraint on `sito` and `nr_individuo`), and reinserting all data from the temporary table before dropping it. The method only executes if the active database connection string begins with `'sqlite'`, as determined by inspecting the URL returned from `Connection.conn_str()`. If any SQL operation fails, a `QMessageBox` warning dialog is displayed with the exception message.

##### geometry_conn(self)

*No description available.*
Handles connection-dependent state management for geometry-related UI controls. The method body and its commented-out logic suggest it was intended to enable or disable the `pushButton_import_geometry` button based on whether the currently selected server type in `comboBox_server_rd` is `'sqlite'`. Currently, the method contains no active implementation.

##### message(self)

*No description available.*
Displays a localized warning dialog based on the currently selected duplicate-handling option (`abort`, `ignore`, or `replace`). For each checked state, it presents a `QMessageBox.warning` with an appropriate message in Italian (`'it'`), German (`'de'`), or English (default), informing the user of the corresponding import behavior. Only the warning corresponding to the active checkbox is shown; multiple warnings may appear if more than one checkbox is checked simultaneously.

##### check(self)

*No description available.*
Evaluates the state of three mutually exclusive checkboxes (`checkBox_ignore`, `checkBox_replace`, and `checkBox_abort`) and registers a corresponding SQLAlchemy `Insert` compiler extension via `@compiles(Insert)` based on the selected option. For SQLite connections, the compiled insert statement is prefixed with `OR IGNORE`, `OR REPLACE`, or `OR ABORT` respectively; for PostgreSQL connections, the equivalent conflict-handling clause (`ON CONFLICT ... DO NOTHING` or `ON CONFLICT ... DO UPDATE SET`) is appended to the generated SQL. Any exceptions raised during this process are silently suppressed via a bare `except: pass` block.

##### summary(self)

Populates the `tableView_summary` widget with aggregate record counts per archaeological site by querying the active database (SQLite or PostgreSQL). For each site, it retrieves distinct counts of stratigraphic units, materials, structures, tombs, pottery records, and media thumbnails using subquery-based SQL. If a site filter is selected in `comboBox_sito`, results are restricted to that site; otherwise, all sites present in `us_table` are returned and ordered alphabetically.

##### check_if_admin(self)

Check if current user is admin

##### sync_download_from_supabase(self, tables, differential)

Download data from remote database to local database

Args:
    tables: Optional list of table names to sync. If None, syncs all tables.
    differential: If True, only sync new/modified records (preserves IDs).

##### sync_upload_to_supabase(self, tables, differential)

Upload data from local database to remote database

Args:
    tables: Optional list of table names to sync. If None, syncs all tables.
    differential: If True, only sync new/modified records (preserves IDs).

##### db_active(self)

*No description available.*
Updates the database-related UI controls based on the currently selected database type (`sqlite` or `postgres`) in `comboBox_Database`. Enables or disables toolbar buttons, backup/restore push buttons, and the database creation button according to both the selected database type and whether the current user has administrator privileges, setting appropriate tooltips for non-admin users on restricted controls. A reentrancy guard via `_db_active_running` prevents recursive invocations, and `comboBox_sito` is cleared regardless of the selected database type.

##### setPathDBsqlite1(self)

*No description available.*
Opens a file dialog prompting the user to select an existing SQLite database file (`.sqlite`) from the directory specified by `self.DBFOLDER`. If a file is selected, extracts the filename from the full path and updates the `lineEdit_database_rd` text field with the filename, then stores the value in `QgsSettings` under an empty key string.

##### setPathDBsqlite2(self)

Opens a file dialog allowing the user to select an existing SQLite database file (`.sqlite`) from the configured `DBFOLDER` directory. Extracts the filename from the selected path and populates the `lineEdit_database_wt` field with it. The selected filename is also persisted to `QgsSettings` with an empty key.

##### openthumbDir(self)

Opens a file dialog prompting the user to select a SQLite database file (`.sqlite`), using `self.DBFOLDER` as the initial directory. Extracts the filename from the selected path and, if a valid filename is obtained, updates `self.lineEdit_DBname` with the filename and persists the value via `QgsSettings`.

##### openresizeDir(self)

*No description available.*
Opens the directory specified in the `lineEdit_Thumb_resize` field using the system's default file manager via `QDesktopServices.openUrl`. Before attempting to open, the method verifies that the path exists using `os.path.exists`; if the directory is not found, a warning message box is displayed to the user with the text `"Directory not found"`.

##### db_name_change(self)

*No description available.*
Handles a database selection change event triggered by `comboBox_Database`. When the selected database type is `'sqlite'`, the method updates the combo box, saves and clears the site combo box state, refreshes the tool button via `tool_ok()`, and — if `DB_MANAGER` is connected — attempts to populate `comboBox_sito` with the first value retrieved from `site_table` grouped by `'sito'`; any exception during this fetch is logged via `QgsMessageLog` without interrupting execution. For all other database types, the method performs the update and save/clear operations without the site value lookup or tool button refresh.

##### save_and_clear_comboBox_sito(self)

Saves the current state, clears the `comboBox_sito` combo box, and then saves the state again after clearing. The method calls `save_p()` twice — once before and once after the `comboBox_sito.clear()` operation — to persist the state at both points in the sequence.

##### save_p(self)

Collects the current values from all database-related UI controls (including server type, host, database name, password, port, user, SSL mode, thumbnail settings, experimental flag, site selection, and logo path) and writes them to `self.PARAMS_DICT`, then persists the dictionary by calling `self.save_dict()`. If the selected database is `postgres` and no password has been entered, the save is skipped with a console warning. After saving, the method attempts to establish a database connection via `self.connection_up()`; if the PostgreSQL version is identified as `90313`, an informational warning is displayed prompting the user to upgrade, and any exception during the process raises a warning dialog indicating a connection problem.

##### on_pushButton_update_db_pressed(self)

Handler for the new update button that updates existing databases
without deleting data using the DB_update class

##### on_pushButton_fix_geometries_pressed(self)

Handler for fixing invalid geometries in the database.
First rebuilds geometry tables to fix column types (INT->TEXT),
then uses QGIS Processing 'Fix Geometries' algorithm (native:fixgeometries).

##### tool_ok(self)

*No description available.*
Checks the state of `toolButton_active` and conditionally invokes `charge_list()` based on the currently selected database type. If the `comboBox_Database` current text equals `'sqlite'`, the method calls `self.charge_list()`; otherwise, no action is taken.

##### setPathDB(self)

Opens a file dialog prompting the user to select a SQLite database file (`.sqlite`) from the path defined by `self.DBFOLDER`. If a file is selected, the method extracts the filename from the full path and updates `self.lineEdit_DBname` with the filename. The filename is also stored in `QgsSettings` via `s.setValue`.

##### setPathThumb(self)

Opens a directory selection dialog prompting the user to choose a thumbnail directory path. If a valid directory is selected, updates the `lineEdit_Thumb_path` field with the chosen path (appending a trailing slash) and persists the value to `QgsSettings` under the key `'pyArchInit/thumbpath'`.

##### setPathlogo(self)

Opens a file dialog prompting the user to select an image file of any format from the default database folder (`DBFOLDER`). If a file is selected, the chosen file path is written to the `lineEdit_logo` text field and persisted to `QgsSettings` with an empty string key. The method does not return a value.

##### setPathResize(self)

Opens a directory selection dialog that allows the user to choose a file system path for resized image storage. If a valid directory is selected, the chosen path (with a trailing slash appended) is displayed in the `lineEdit_Thumb_resize` field and persisted to `QgsSettings` under the key `'pyArchInit/risizepath'`.

##### openRemoteStorageConfig(self)

Open the remote storage configuration dialog.

Allows users to configure credentials for:
- Google Drive (gdrive://)
- Dropbox (dropbox://)
- Amazon S3 / Cloudflare R2 (s3://, r2://)
- WebDAV (webdav://)
- HTTP/HTTPS (http://, https://)

##### setPathGraphviz(self)

Opens a directory selection dialog that allows the user to browse and select the Graphviz binary directory path. If a directory is selected, it updates the `lineEditGraphviz` text field with the chosen path and persists the value to QGIS settings under the key `'pyArchInit/graphvizBinPath'`.

##### setPathPostgres(self)

*No description available.*
Opens a directory selection dialog prompting the user to choose the PostgreSQL binaries directory, starting from the user's home directory. If a valid directory is selected, it updates the `lineEditPostgres` text field with the chosen path and persists the value to the QGIS settings store under the key `'pyArchInit/postgresBinPath'`.

##### setEnvironPath(self)

*No description available.*
Appends the normalized `graphviz_bin` path to the system `PATH` environment variable using the appropriate path separator for the current operating system. After updating the environment variable, it displays a warning dialog box with the translated message `"The path has been set successfully"` to notify the user that the operation completed. The dialog requires acknowledgment via an `Ok` button before dismissal.

##### setEnvironPathPostgres(self)

*No description available.*
Appends the normalized PostgreSQL binary directory path (`self.postgres_bin`) to the system `PATH` environment variable using the OS-appropriate path separator. After updating the environment variable, it displays a warning dialog box informing the user that the path has been set successfully.

##### set_db_parameter(self)

Sets default database connection parameters in the UI form fields based on the currently selected database type in `comboBox_Database`. If `postgres` is selected, it populates `lineEdit_DBname`, `lineEdit_Host`, `lineEdit_Port`, and `lineEdit_User` with default PostgreSQL connection values. If `sqlite` is selected, it sets the database name to `"pyarchinit_db.sqlite"` and clears the host, password, port, and user fields. A re-entrancy guard using the `_setting_parameters` flag prevents recursive invocations of the method.

##### set_db_import_from_parameter(self)

*No description available.*
Populates the "import from" database connection fields in the UI with default parameter values based on the currently selected server type in `comboBox_server_rd`. For a `postgres` selection, it sets the host to `'localhost'`, username to `'postgres'`, database to `'pyarchinit'`, and port to `'5432'`. For a `sqlite` selection, it clears the host, username, and password fields and sets the database name to `'pyarchinit_db.sqlite'` with an empty port field.

##### set_db_import_to_parameter(self)

*No description available.*
Populates the import destination ("write to") connection fields based on the server type selected in `comboBox_server_wt` and the currently active database indicated by `comboBox_Database`. If the selected server type does not match the active database connection (e.g., `postgres` selected but `sqlite` is active, or vice versa), a warning dialog is displayed and `comboBox_server_wt` is cleared. When the server type and active database match, the corresponding connection fields (`lineEdit_host_wt`, `lineEdit_database_wt`, `lineEdit_username_wt`, `lineEdit_port_wt`, `lineEdit_pass_wt`) are populated from the current connection parameters, with SQLite leaving host, username, and password fields empty.

##### load_dict(self)

*No description available.*
Reads the configuration file `config.cfg` located in the `pyarchinit_DB_folder` directory under the user's home path (`self.HOME`). The file contents are read as a string and evaluated using `eval()`, with the resulting object stored in `self.PARAMS_DICT`. The file is closed after reading.

##### save_dict(self)

Writes the current `PARAMS_DICT` dictionary to the `config.cfg` file located in the `pyarchinit_DB_folder` directory under the user's home path. After saving, it attempts to clear the database connection cache by invoking `DbConnectionSingleton.clear_instances()`; any exception raised during this step is silently suppressed.

##### on_pushButton_save_pressed(self)

*No description available.*
Handles the save button press event by collecting database connection parameters from the UI form fields (`comboBox_Database`, `lineEdit_Host`, `lineEdit_DBname`, `lineEdit_Password`, `lineEdit_Port`, `lineEdit_User`, `comboBox_sslmode`, and others) and persisting them to `PARAMS_DICT` via `save_dict()`. A re-entry guard (`_save_in_progress`) prevents concurrent executions, and a warning is displayed if the `postgres` server type is selected without a password. After saving, the method invokes `try_connection()` to validate the connection, warns the user if an obsolete PostgreSQL version (`90313`) is detected, and displays an error message if any exception occurs during the process.

##### on_pushButton_crea_database_pressed(self)

Handles the "Create Database" button press event by orchestrating the full creation of a new PostgreSQL database for the application. It first verifies that the current user has administrator privileges and that a password has been provided, then sequentially creates the database, restores the schema from `pyarchinit_schema_updated.sql`, updates the geometry SRID, applies views from `create_view_updated.sql`, and optionally installs activity tracking triggers. Upon successful creation, the method prompts the user to connect to the newly created database, transferring the connection parameters to the main connection fields and triggering `on_pushButton_save_pressed` via a delayed `QTimer` call; re-entrant calls are blocked via a `creating_database` guard flag.

##### select_version_sql(self)

Check PostgreSQL server version. Returns version string or None on failure.

##### on_pushButton_upd_postgres_pressed(self)

*No description available.*
Handles the press event of the PostgreSQL update button. First verifies that the current user has administrator privileges, displaying a warning and aborting if not. Then retrieves the current PostgreSQL version via `select_version_sql()` and, if the version does not match the unsupported version code `"90313"`, executes a schema update by running the SQL script `pyarchinit_update_postgres.sql` against the active database connection via `RestoreSchema`; otherwise, it informs the user that the PostgreSQL version is too low to proceed.

##### load_spatialite(self, dbapi_conn, connection_record)

*No description available.*
Enables the SpatiaLite extension on an existing DBAPI connection by first activating extension loading via `enable_load_extension(True)`, then loading the appropriate SpatiaLite shared library based on the current operating system. On Windows, it loads `mod_spatialite.dll`; on macOS and all other platforms (including Linux), it loads `mod_spatialite.so`. The `connection_record` parameter is accepted but not used within the method body.

##### on_pushButton_upd_sqlite_pressed(self)

Slot handler triggered when the "update SQLite" push button is pressed. It first verifies that the current user has administrator privileges, then connects to the existing SQLite/SpatiaLite database (identified by the database name entered in `lineEdit_dbname_sl`) and executes a series of DDL statements to update the schema: creating the `pyarchinit_quote_usm` table with its geometry column and spatial index, recreating the `pyarchinit_quote_usm_view`, `pyarchinit_quote_view`, `pyarchinit_usm_view`, and `pyarchinit_us_view` spatial views with their corresponding entries in `views_geometry_columns`, creating the `pyunitastratigrafiche_usm` table with geometry column and spatial index, and installing or replacing geometry update triggers on `pyunitastratigrafiche`. Upon successful completion it calls `RestoreSchema.update_geom_srid_sl` with the CRS value from `lineEdit_crs` and displays a confirmation message; any exception is caught and reported via a warning dialog.

##### on_pushButton_crea_database_sl_pressed(self)

*No description available.*
Handles the press event of the SQLite database creation button. It constructs a new SQLite database file path from the name entered in `lineEdit_dbname_sl`, and if the file does not already exist, copies a template database from the package resources and updates its geometry SRID using the CRS selected in `selectorCrsWidget_sl`. Upon successful creation, a localized confirmation dialog (Italian, German, or English, based on `self.L`) prompts the user to connect to the newly created database by invoking `on_pushButton_save_pressed`; if the database file already exists, a localized warning message is displayed instead.

##### try_connection(self)

*No description available.*
Attempts to establish a database connection using the current configuration by calling `self.summary()`, constructing a `Connection` object, and invoking `Pyarchinit_db_management.connection()`. To prevent re-entrant execution, the method guards against recursive calls via a `_connection_in_progress` flag, and temporarily disconnects `comboBox_Database` signals before the attempt, restoring them in a `finally` block. On success, it notifies the user, updates UI controls, saves the current user to settings, and sets up admin features; on failure, it adjusts UI controls based on the selected database type (`sqlite` or `postgres`) and displays a warning message.

##### save_current_user_to_settings(self)

Save current database username to settings for admin checks

##### connection_up(self)

Initializes a database connection by invoking `summary()`, constructing a `Connection` object, and using the resulting connection string to instantiate a `Pyarchinit_db_management` instance. If the connection test succeeds, the PostgreSQL update button is disabled and the SQLite update button is enabled. If the connection fails, the UI controls are updated based on the currently selected database type (`sqlite` or `postgres`), and a warning dialog is displayed prompting the user to change parameters or use the database update function.

##### charge_data(self)

*No description available.*
Loads configuration values from `PARAMS_DICT` (populated from `config.cfg`) and populates the corresponding UI widgets with those values. Sets the database server, host, database name, password, port, user, SSL mode, thumbnail path, thumbnail resize value, experimental flag, site, and logo fields in the interface. If the `EXPERIMENTAL` key is missing or causes an error, the experimental combo box defaults to `"No"`.

##### test_def(self)

*No description available.*
A placeholder method with no implemented logic. The method body consists solely of a `pass` statement, indicating it is defined but currently performs no operations and returns `None`. It serves as a stub, likely reserved for future implementation or testing purposes.

##### on_toolButton_active_toggled(self)

*No description available.*
Slot handler triggered when `toolButton_active` is toggled. When the button is checked, it displays a localised informational message instructing the user to select a site and save parameters, then calls `self.charge_list()` to populate the site list; when unchecked, it clears `comboBox_sito` and displays a localised message indicating the query system has been deactivated. The displayed messages are localised for Italian (`'it'`), German (`'de'`), or a default language based on the value of `self.L`.

##### charge_list(self)

*No description available.*
Establishes a database connection using `Connection` and `Pyarchinit_db_management`, validating the connection before proceeding. Retrieves the list of sites from the `site_table` and, when connected to a PostgreSQL database, filters the list based on the active user's `site_filter` permissions defined in `pyarchinit_users`, bypassing the filter for privileged users such as `postgres` and `admin_pyarchinit`. Populates `comboBox_sito` with the resulting sorted site list, and calls `update_db_button_style()` to refresh the database update button appearance.

##### on_pushButton_import_geometry_pressed(self)

Slot triggered when the "Import Geometry" button is pressed. Displays a localized confirmation warning dialog (supporting Italian, German, and a default English variant) before proceeding; if the user cancels, an "action aborted" message is shown and no changes are made. If confirmed, the method establishes read and write database connections (PostgreSQL or SQLite) using credentials from the GUI, queries records from the source database filtered by a user-specified field/value pair, and inserts the retrieved geometry records into the target database for each supported mapper class (`PYUS`, `PYUSM`, `PYSITO_POINT`, `PYSITO_POLYGON`, `PYQUOTE`, `PYQUOTEUSM`, `PYUS_NEGATIVE`, `PYSTRUTTURE`, `PYREPERTI`, `PYINDIVIDUI`, `PYCAMPIONI`, `PYTOMBA`, `PYDOCUMENTAZIONE`, `PYLINEERIFERIMENTO`, `PYRIPARTIZIONI_SPAZIALI`, `PYSEZIONI`), updating a progress bar throughout the operation.

##### on_pushButton_apply_constraints_pressed(self)

Apply unique constraints to thesaurus table.

##### on_pushButton_import_pressed(self)

Handles the import button press event by first displaying a localized confirmation warning dialog (supporting Italian, German, and English based on `self.L`) that allows the user to abort the operation. If confirmed, it establishes read and write database connections using credentials from the GUI fields, queries records from the source database according to the selected mapper class and filter criteria, and inserts them into the destination database. The method supports importing individual tables (`SITE`, `US`, `UT`, `PERIODIZZAZIONE`, `INVENTARIO_MATERIALI`, `POTTERY`, `STRUTTURA`, `TOMBA`, `SCHEDAIND`, `CAMPIONI`, `DOCUMENTAZIONE`, `PYARCHINIT_THESAURUS_SIGLE`, `MEDIA`, `MEDIA_THUMB`, `MEDIATOENTITY`, `TMA`) or all tables sequentially when `ALL` is selected, updating a progress bar for each record inserted and displaying a localized result message upon completion.

##### check_sqlite_db_on_init(self)

Check and fix macc field when config dialog opens

##### fix_macc_field_for_current_db(self, conn_str)

Fix macc field in the current SQLite database

##### openthumbDir(self)

*No description available.*
Opens the thumbnail directory specified in the `lineEdit_Thumb_path` field using the system's default file manager via `QDesktopServices.openUrl`. Before attempting to open the directory, the method verifies that the path exists on the filesystem. If the directory does not exist, a warning dialog is displayed to the user with the message `"Directory not found"`.

##### openresizeDir(self)

Opens the directory path specified in the `lineEdit_Thumb_resize` text field using the system's default file manager via `QDesktopServices.openUrl`. If the specified path exists on the filesystem, it is opened as a local file URL; otherwise, a warning dialog is displayed to the user with the message "Directory not found".

##### on_pushButton_connect_pressed(self)

*No description available.*
Slot triggered when the connect button is pressed. Reads the IP address, username, and password from their respective `QLineEdit` fields (`lineEdit_ip`, `lineEdit_user`, `lineEdit_password`) and attempts to establish an FTP connection using those credentials. On success, inserts a confirmation message into `lineEdit_2` and navigates to the root directory (`'/'`), inserting the result into `listWidget`; on failure (either from a failed login check or a raised exception), inserts an error message into `lineEdit_2`.

## Functions

### reconnect_set_db_parameter()

*No description available.*
A locally defined function that reconnects the `set_db_parameter` slot to the `comboBox_Database.currentIndexChanged` signal after a successful database connection. It wraps the `connect` call in a `try/except` block, silently suppressing any exceptions that may occur during reconnection. The function reference is stored in `self.reconnect_set_db_param_func` so it can be invoked externally at the appropriate point following a successful connection.

