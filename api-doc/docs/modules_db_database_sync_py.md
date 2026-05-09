# modules/db/database_sync.py

## Overview

This file contains 61 documented elements.

## Classes

### TableDiff

Differences for a single table

**Decorators**: dataclass

### SyncConfig

Configuration for synchronization

**Decorators**: dataclass

### DatabaseAdapter

Abstract base class for database operations

**Inherits from**: ABC

#### Methods

##### get_table_count(self, table)

*No description available.*
Abstract method that returns the total number of records in the specified table. Accepts a single string parameter `table` identifying the target table and returns an integer count. Concrete subclasses of `DatabaseAdapter` must provide an implementation of this method.

##### get_primary_key(self, table)

*No description available.*
Abstract method that retrieves the primary key column name for the specified table. Accepts a table name as a string parameter and returns the corresponding primary key as a string. Concrete subclasses must provide an implementation of this method.

##### get_record_ids(self, table, pk)

*No description available.*
```python
@abstractmethod
def get_record_ids(self, table: str, pk: str) -> List[str]
```

Abstract method that retrieves a list of record identifiers from the specified table, using the provided primary key column. Returns a `List[str]` containing the values of the primary key field for all records in the given table. Concrete subclasses must provide an implementation of this method.

##### get_table_columns(self, table)

*No description available.*
Abstract method that retrieves the column names of a specified database table. Accepts a single `table` parameter of type `str` identifying the target table, and returns a `List[str]` containing the names of all columns found in that table. Concrete subclasses must provide an implementation of this method.

##### is_view(self, table)

*No description available.*
```python
@abstractmethod
def is_view(self, table: str) -> bool
```

Abstract method that determines whether the specified table is a database view. Accepts a table name as a string and returns `True` if the table is a view, or `False` otherwise. Concrete subclasses must provide an implementation of this method.

##### table_exists(self, table)

*No description available.*
An abstract method that checks whether the specified table exists. Accepts a single string parameter `table` representing the table name to look up, and returns a boolean indicating its existence. Concrete subclasses must provide an implementation of this method.

##### export_records(self, table, columns, pk, ids)

*No description available.*
```python
@abstractmethod
def export_records(self, table: str, columns: List[str], pk: str, ids: List[str]) -> List[List[Any]]
```

Abstract method that retrieves records from the specified table, returning only the given columns for rows whose primary key matches the provided list of IDs. The results are returned as a list of rows, where each row is itself a list of values corresponding to the requested columns. Concrete subclasses must provide an implementation of this method.

##### import_records(self, table, columns, records)

*No description available.*
Abstract method that imports a set of records into the specified table. Accepts the target table name, a list of column names, and a two-dimensional list of record data to be inserted. Returns an integer indicating the number of records imported.

##### truncate_table(self, table)

*No description available.*
```python
@abstractmethod
def truncate_table(self, table: str) -> bool:
```

Abstract method that truncates the specified database table, removing all of its rows. Accepts the table name as a string parameter. Returns a boolean indicating whether the operation was successful.

##### disable_triggers(self, table)

*No description available.*
```python
@abstractmethod
def disable_triggers(self, table: str) -> bool
```

Abstract method that disables triggers on the specified database table. Implementations must override this method to provide the concrete logic for deactivating triggers associated with the given table name. Returns a boolean indicating whether the operation was successful.

##### enable_triggers(self, table)

*No description available.*
Abstract method that enables triggers on the specified database table. Serves as the counterpart to `disable_triggers`, accepting a table name as a string parameter. Returns a boolean indicating the outcome of the operation.

### PostgreSQLAdapter

PostgreSQL database adapter

**Inherits from**: DatabaseAdapter

#### Methods

##### __init__(self, host, port, database, user, password, engine)

Initializes a `PostgreSQLAdapter` instance with the provided connection parameters, storing `host`, `port`, `database`, `user`, `password`, and an optional `engine` as instance attributes. It locates the `psql` executable via `_find_psql()` and copies the current OS environment, setting the `PGPASSWORD` environment variable if a password is provided.

##### get_table_count(self, table)

*No description available.*
Executes a `SELECT COUNT(*)` query against the specified table and returns the total number of rows as an integer. If the query succeeds and the output can be parsed as an integer, that value is returned; otherwise, returns `-1` to indicate failure or an unparseable result.

##### get_primary_key(self, table)

*No description available.*
Queries the PostgreSQL system catalog to retrieve the primary key column name for the specified table. It executes a query joining `pg_index` and `pg_attribute` to find the attribute marked as the primary index (`i.indisprimary`) for the given table, resolved via `::regclass`. Returns the first line of the query output as a string, or an empty string if the query fails or returns no results.

##### get_record_ids(self, table, pk)

Retrieves all primary key values from the specified database table by executing a `SELECT` query ordered by the primary key column. Returns a list of stripped, non-empty string values parsed from the query output. If the query fails or produces no output, an empty list is returned.

##### get_table_columns(self, table)

*No description available.*
Queries the `information_schema.columns` view to retrieve all column names for the specified table within the `public` schema, ordered by their ordinal position. Executes the query via `_run_query` and, on success, parses the output by splitting on newlines and stripping whitespace from each entry. Returns a list of column name strings, or an empty list if the query fails or produces no output.

##### is_view(self, table)

Checks whether a specified table in the public schema is a database view by querying the `information_schema.tables` system catalog for its `table_type`. Returns `True` if the query succeeds and the result contains the string `'VIEW'` (case-insensitive), otherwise returns `False`.

##### table_exists(self, table)

Checks whether a table with the specified name exists in the `public` schema of the database.

Executes a query against `information_schema.tables` using an `EXISTS` subclause and returns `True` if the table is found, based on the query output equaling `'t'`. Returns `False` if the query fails or the table does not exist.

##### export_records(self, table, columns, pk, ids)

Export records as list of rows

##### import_records(self, table, columns, records)

Import records into table

##### truncate_table(self, table)

*No description available.*
Executes a `TRUNCATE ... CASCADE;` SQL statement against the specified table by invoking `psql` as a subprocess with the configured host, port, user, and database credentials. The command is run with a 60-second timeout, and the method returns `True` if the process exits with a return code of `0`, indicating success. Returns `False` if the subprocess call fails for any reason or an exception is raised.

##### disable_triggers(self, table)

Disables all triggers on the specified database table by executing an `ALTER TABLE ... DISABLE TRIGGER ALL` statement. Accepts a table name as a string parameter and returns a boolean indicating whether the operation completed successfully.

##### enable_triggers(self, table)

*No description available.*
Executes an `ALTER TABLE ... ENABLE TRIGGER ALL` statement on the specified table, re-enabling all triggers that were previously disabled. Accepts a single `table` parameter identifying the target table by name. Returns a boolean indicating whether the query executed successfully.

### SQLiteAdapter

SQLite database adapter

**Inherits from**: DatabaseAdapter

#### Methods

##### __init__(self, db_path)

Initializes a new `SQLiteAdapter` instance with the specified database file path. Sets `self.db_path` to the provided path and `self._conn` to `None`, deferring the actual connection until needed. Raises `FileNotFoundError` if no file exists at the given `db_path`.

##### close(self)

Close the persistent connection

##### get_table_count(self, table)

Executes a `SELECT COUNT(*)` query against the specified table and returns the total number of rows as an integer. If an exception occurs during execution, the error is printed to standard output and `-1` is returned to indicate failure.

##### get_primary_key(self, table)

*No description available.*
Retrieves the name of the primary key column for the specified database table by querying the SQLite `PRAGMA table_info` statement and identifying the column where `pk` equals `1`. Returns the column name as a string if a primary key is found, or an empty string if no primary key column is identified or an exception occurs. Any exception encountered during execution is caught and printed in the format `"PK error for {table}: {e}"`.

##### get_record_ids(self, table, pk)

*No description available.*
Queries the specified database table and retrieves all values from the given primary key column, returning them as an ordered list of strings. Results are sorted in ascending order by the primary key column. If an error occurs during execution, it prints an error message identifying the affected table and returns an empty list.

##### get_table_columns(self, table)

*No description available.*
Retrieves the column names for the specified SQLite table by querying the `PRAGMA table_info` statement. Returns a list of column name strings extracted from the pragma result rows. If an error occurs during the operation, it prints a diagnostic message identifying the table and returns an empty list.

##### is_view(self, table)

Checks whether the specified table name corresponds to a view in the SQLite database by querying the `sqlite_master` system table for an entry matching the given name with type `'view'`. Returns `True` if such an entry exists, or `False` if it does not or if an exception occurs during execution.

##### table_exists(self, table)

*No description available.*
Checks whether a table with the specified name exists in the SQLite database by querying the `sqlite_master` system table. Returns `True` if a matching table entry is found, or `False` if no match exists or an exception occurs during execution.

##### export_records(self, table, columns, pk, ids)

Export records as list of rows

##### import_records(self, table, columns, records)

Import records into table using batch executemany

##### truncate_table(self, table)

Removes all rows from the specified table by executing a `DELETE FROM` statement on the active database connection and committing the transaction. Returns `True` if the operation completes successfully, or `False` if an exception occurs, printing the error details to standard output.

##### disable_triggers(self, table)

*No description available.*
Handles trigger disabling for a specified table. In this SQLite implementation, triggers cannot be disabled, so the method performs no operation and unconditionally returns `True`. This serves as a compatibility stub to satisfy a common interface shared with other database backends that support trigger management.

##### enable_triggers(self, table)

Enables triggers for the specified table and returns a boolean indicating success.

In this SQLite implementation, triggers are always enabled and cannot be disabled at the table level, so this method unconditionally returns `True`. This method mirrors the interface established by `disable_triggers`, maintaining API consistency across database adapter implementations.

### SyncAnalyzer

Thread to analyze differences between databases

**Inherits from**: QThread

#### Methods

##### __init__(self, config, parent)

Initializes a new instance of the worker object by calling the parent class constructor with the optional `parent` argument. Stores the provided `SyncConfig` instance as `self.config` and sets the `_cancelled` flag to `False`.

##### cancel(self)

*No description available.*
Sets the internal `_cancelled` flag to `True`, signalling that the current operation should be cancelled. This method provides a way to interrupt the execution of the associated `run()` process by marking the instance's cancelled state.

##### run(self)

Executes the table comparison workflow by iterating over all tables defined in the configuration and computing differences between local and remote database adapters. For each non-view table, it collects record counts and, when a primary key is available, determines the number of records present exclusively in the local or remote database; any per-table errors are captured in the corresponding `TableDiff` object rather than halting execution. Progress is reported incrementally via the `progress` signal, and upon completion the full list of `TableDiff` results is emitted through the `finished` signal, or an error message is emitted via the `error` signal if a fatal exception occurs. The method respects cancellation requests by checking the `_cancelled` flag before processing each table.

### SyncWorker

Worker thread for sync operations

**Inherits from**: QThread

#### Methods

##### __init__(self, operation, config, tables_to_sync, parent)

Initializes a new instance of the worker thread, setting up the required configuration for a synchronization operation. Accepts an `operation` string, a `SyncConfig` object, an optional list of table names to synchronize, and an optional parent object. If `tables_to_sync` is not provided, it defaults to the value defined in the supplied `config` object; the `_cancelled` flag is initialized to `False`.

##### cancel(self)

*No description available.*
Sets the internal `_cancelled` flag to `True`, signalling that the current operation should be cancelled. This method provides a mechanism to interrupt an in-progress `run()` operation by marking the instance as cancelled.

##### run(self)

Executes the file synchronization operation determined by the `operation` attribute, dispatching to one of four internal methods: `_download_from_remote`, `_upload_to_remote`, `_differential_download`, or `_differential_upload`. If any exception is raised during execution, the error message is emitted via the `error` signal and the `finished` signal is emitted with `False` and the error message string.

### DatabaseSyncManager

Manager for database synchronization

**Inherits from**: QObject

#### Methods

##### __init__(self, parent)

Initializes a new instance of the class by calling the parent constructor with the optional `parent` argument. Sets the instance attributes `worker`, `analyzer`, and `config` to `None`.

##### configure(self, local_config, remote_config, tables)

Configure sync connections

##### analyze_differences(self)

Analyze differences between local and remote databases

##### download_from_remote(self, tables, differential)

Download from remote to local

##### upload_to_remote(self, tables, differential)

Upload from local to remote

##### cancel(self)

Cancel current operation

##### is_running(self)

Check if an operation is running

## Functions

### create_adapter(config, is_local, engine)

Factory function to create the appropriate database adapter

**Parameters:**
- `config: SyncConfig`
- `is_local: bool`
- `engine`

**Returns:** `DatabaseAdapter`

### get_sync_config_from_settings()

Get sync configurations from QGIS settings

**Returns:** `Tuple[Dict, Dict]`

### save_sync_config_to_settings(local_config, remote_config)

Save sync configurations to QGIS settings

**Parameters:**
- `local_config: Dict`
- `remote_config: Dict`

