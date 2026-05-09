# modules/db/db_createdump.py

## Overview

This file contains 21 documented elements.

## Classes

### PyArchInitDBLogger

Simple file logger for database operations

#### Methods

##### __init__(self)

Initializes a new instance of `PyArchInitDBLogger` by setting the `log_file` attribute to the hardcoded path `'/Users/enzo/pyarchinit_db_debug.log'`. This path designates the target file where database operation log messages will be written.

##### log(self, message)

Write a log message with timestamp

##### log_exception(self, exc, context)

Log an exception with traceback

### SchemaDump

*No description available.*
Captures the DDL schema of an existing database and writes it to a file. It reflects the database structure from the provided `db_url` using SQLAlchemy's `MetaData`, intercepts the generated SQL statements via a mock engine executor, and accumulates them in an in-memory `BytesIO` buffer. The resulting SQL is then written to the file path specified by `schema_file_path`.

**Inherits from**: object

#### Methods

##### __init__(self, db_url, schema_file_path)

*No description available.*
Initializes a `SchemaDump` instance with the provided database URL and schema file path. Stores `db_url` and `schema_file_path` as instance attributes and initializes an in-memory binary buffer (`self.buf`) as an `io.BytesIO` object.

##### dump_shema(self)

Reflects the existing database schema from the URL specified in `self.db_url` using SQLAlchemy's `MetaData.reflect`, then captures the corresponding DDL SQL statements into an in-memory buffer (`self.buf`) by executing `metadata.create_all` against a mock engine. Each compiled SQL statement is written to the buffer followed by a semicolon and newline. The accumulated buffer contents are then written to the file at `self.schema_file_path` in binary mode.

### RestoreSchema

*No description available.*
`RestoreSchema` restores a SQL schema to a target database from a schema file, using a database URL and an optional file path provided at construction. It exposes methods to execute the raw SQL schema against the database (`restore_schema`), update geometry column SRIDs for PostGIS-compatible tables (`update_geom_srid`, `update_geom_srid_sl`), and reassign table ownership within the `public` schema (`set_owner`). All database operations are executed within explicit transactions and rolled back on failure; logging is performed via `PyArchInitDBLogger`.

**Inherits from**: object

#### Methods

##### __init__(self, db_url, schema_file_path)

Initializes a `RestoreSchema` instance with the provided database URL and an optional schema file path. Assigns `db_url` and `schema_file_path` to their respective instance attributes, and instantiates a `PyArchInitDBLogger` object stored as `self.logger`.

##### restore_schema(self)

*No description available.*
Reads a SQL schema definition from the file path specified by `self.schema_file_path` and executes it against the database identified by `self.db_url`. The method opens a connection via SQLAlchemy's `create_engine`, executes the raw SQL within an explicit transaction, and commits on success. If an error occurs during execution, the transaction is rolled back and the exception is re-raised; all major steps are logged via `self.logger`.

##### update_geom_srid(self, schema, crs)

*No description available.*
Queries the `geometry_columns` view to retrieve all geometry table names and their corresponding geometry types, then executes an `ALTER TABLE` statement for each table to redefine the `the_geom` column with the specified CRS (SRID) using `ST_SetSRID`. All alterations are executed within a single transaction, which is committed on success or rolled back if an exception occurs. Returns `True` upon successful completion.

##### set_owner(self, owner)

*No description available.*
Transfers ownership of all tables in the `public` schema of the connected database to the specified `owner`. It queries `information_schema.tables` to retrieve all public table names, then executes an `ALTER TABLE ... OWNER TO ...` statement for each one within a single transaction. Returns `True` on success; rolls back the transaction and re-raises any exception encountered during execution.

##### update_geom_srid_sl(self, crs)

*No description available.*
Updates the `srid` field in the `geometry_columns` table for all entries to the specified coordinate reference system value. The method queries all records from `geometry_columns`, iterates over each table entry, and executes an `UPDATE` statement setting `srid` to the provided `crs` value. The operation is executed within a transaction that is committed on success or rolled back on failure, and returns `True` upon successful completion.

### CreateDatabase

*No description available.*
Encapsulates the creation of a PostgreSQL database using connection parameters supplied at instantiation, including host, port, database name, user credentials, and SSL mode. The `createdb` method constructs a SQLAlchemy engine from these parameters, checks whether the target database already exists, and creates it if it does not, returning `(True, db_url_string)` on successful creation or `(False, None)` if the database already exists. All operations are logged via a `PyArchInitDBLogger` instance, with the password masked in log output; any exception raised during the process is logged and re-raised.

**Inherits from**: object

#### Methods

##### __init__(self, db_name, db_host, db_port, db_user, db_passwd, sslmode)

Initializes a `CreateDatabase` instance with the database connection parameters required to establish a connection. Stores the database name, host, port, user credentials, and SSL mode as instance attributes, defaulting `sslmode` to `"allow"` if not provided. Also instantiates a `PyArchInitDBLogger` object assigned to `self.logger` for use by the instance.

##### createdb(self)

*No description available.*
Attempts to create a PostgreSQL database using the connection parameters configured on the instance (host, port, user, password, database name, and SSL mode). If the database does not already exist, it constructs a SQLAlchemy engine and invokes `create_database` to provision it, returning `(True, db_url_string)` on success. If the database already exists, the method returns `(False, None)` without modification; any exception encountered during the process is logged and re-raised.

### DropDatabase

*No description available.*
A utility class that manages the removal of a database identified by a given URL. Upon instantiation, it accepts a `db_url` parameter that is stored for use by the `dropdb` method. The `dropdb` method checks whether the specified database exists and, if so, drops it using the `drop_database` function.

**Inherits from**: object

#### Methods

##### __init__(self, db_url)

*No description available.*
Initializes a new `DropDatabase` instance with the provided database URL. Stores the given `db_url` value as an instance attribute for use by subsequent operations on the object.

**Parameters:**
- `db_url` — The URL of the target database.

##### dropdb(self)

*No description available.*
Checks whether the database specified by `self.db_url` exists and, if so, drops it. The existence check is performed via `database_exists`, and the removal is performed via `drop_database`, both called with `self.db_url`. If the database does not exist, no action is taken.

## Functions

### dump(sql)

*No description available.*
An executor callback passed to a mock SQLAlchemy engine that intercepts SQL expression objects before they reach a real database. It compiles each SQL statement against the engine's dialect and writes the resulting string, followed by a semicolon and newline, to the instance's buffer (`self.buf`). This function is used internally as the `executor` argument to the mock engine strategy, enabling DDL statements to be serialized as text rather than executed against a live database.

**Parameters:**
- `sql`

