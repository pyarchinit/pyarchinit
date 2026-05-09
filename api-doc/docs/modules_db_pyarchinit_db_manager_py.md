# modules/db/pyarchinit_db_manager.py

## Overview

This file contains 165 documented elements.

## Classes

### DbConnectionSingleton

Singleton per gestire connessioni database globali

#### Methods

##### get_instance(cls, conn_str)

Ottieni istanza singleton per una specifica connection string

##### clear_instances(cls)

Pulisci tutte le istanze (per reset/disconnessione)
NON resetta _db_checked per evitare controlli ripetuti durante la stessa sessione

##### force_db_recheck(cls)

Forza un nuovo controllo del database alla prossima connessione

### Pyarchinit_db_management

`Pyarchinit_db_management` is the central database management class for the PyArchInit archaeological information system, providing a unified interface for connecting to and interacting with both SQLite/SpatiaLite and PostgreSQL/PostGIS databases via SQLAlchemy. It encapsulates all data access operations including session management, CRUD operations, raw SQL execution, and entity instantiation for the full range of archaeological record types (US, UT, SITE, POTTERY, STRUTTURA, TOMBA, INVENTARIO_MATERIALI, and others). The class also handles database schema initialization and maintenance tasks such as ensuring required tables and geometry columns exist, loading the SpatiaLite extension, and providing query caching to improve performance.

**Inherits from**: object

#### Methods

##### __init__(self, c, _singleton)

*No description available.*
Initializes a new instance of the class by storing the provided connection string and setting up placeholder attributes for the database session, engine, and metadata. The `_singleton` flag is stored to indicate whether this instance operates as a singleton, and a local cache dictionary (`_local_cache`) is initialized as an empty mapping for instance-level caching. All session-related attributes (`Session`, `engine`, `metadata`) are set to `None` pending further configuration.

##### clear_cache(self)

Clear all cached query results. Call this after insert/update/delete operations.

##### load_spatialite(self, dbapi_conn, connection_record)

*No description available.*
SQLAlchemy event listener that loads the SpatiaLite extension into a raw DBAPI connection upon establishment. It first enables extension loading on the connection, then resolves and loads the appropriate `mod_spatialite` library based on the current operating system: `mod_spatialite.dll` on Windows, `mod_spatialite.so` on Linux, and on macOS a prioritized search across QGIS built-in paths, QGIS installation directories, Homebrew, and MacPorts locations — raising a `sqlite3.OperationalError` if no library is found. After loading the extension, it enforces referential integrity by executing `PRAGMA foreign_keys=ON`.

##### connection(self)

Establishes a database connection using the configured `conn_str` connection string, creating a SQLAlchemy engine, `MetaData` instance, and `Session` factory bound to that engine. For singleton instances with an existing engine, the method returns immediately without reconnecting; otherwise it selects engine parameters appropriate for SQLite (with SpatiaLite listener), remote cloud databases (larger pool, longer timeouts), or local non-SQLite databases. On first use per session, the method also invokes database schema updaters for SQLite or PostgreSQL and adds UUID column support to all tables, returning `True` on success or `False` if an error occurs during connection.

##### session_scope(self)

Provide a transactional scope around a series of operations.

##### get_session(self)

Get a new session - use session_scope() for transactions

##### ensure_tma_tables_exist(self)

Ensure TMA tables are created if they don't exist

##### ensure_fauna_table_exists(self)

Ensure Fauna table is created if it doesn't exist (works for both PostgreSQL and SQLite)

##### ensure_ut_geometry_tables_exist(self)

Ensure UT geometry tables and views are created if they don't exist (works for both PostgreSQL and SQLite)

##### fix_macc_field_sqlite(self)

Fix macc field in tma_materiali_ripetibili table for SQLite databases

##### insert_pottery_values(self)

Istanzia la classe POTTERY da pyarchinit_db_mapper

##### insert_pottery_embedding_metadata(self, id_rep, id_media, image_hash, model_name, search_type, embedding_version)

Insert a new pottery embedding metadata record

##### get_pottery_embedding_metadata(self, id_media, model_name, search_type)

Get embedding metadata for a specific media/model/search_type combination

##### get_all_pottery_embedding_metadata(self, model_name, search_type)

Get all embedding metadata, optionally filtered by model and search type

##### get_unindexed_pottery_images(self, model_name, search_type)

Get pottery images that don't have embeddings for the specified model/search_type

##### get_all_pottery_with_images(self)

Get all pottery records that have associated images.
Returns path_resize from media_thumb_table (relative filename to be joined with THUMB_RESIZE from config)

##### delete_pottery_embedding_metadata(self, id_media, model_name, search_type)

Delete embedding metadata for a media item

##### count_pottery_embeddings(self, model_name, search_type)

Count total embeddings, optionally by model/search_type

##### get_pottery_by_id_rep(self, id_rep)

Get a single pottery record by id_rep

##### get_pottery_image_path(self, id_rep)

Get the first image path_resize for a pottery record (relative filename)

##### get_image_path_by_media_id(self, media_id)

Get image path_resize by media_id (for similarity search results)

##### get_all_pottery_images(self, id_rep)

Get ALL image paths for a pottery record (for multi-image similarity search)

##### insert_pyus(self)

*No description available.*
Constructs and returns a `PYUS` object instance using positional arguments passed via a variable-length argument tuple. The method maps exactly fourteen arguments (`arg[0]` through `arg[13]`) to the `PYUS` constructor in sequential order. The resulting `PYUS` instance is returned directly to the caller without any additional processing or persistence.

##### insert_pyusm(self)

*No description available.*
Constructs and returns a new `PYUSM` instance using a variable-length argument list, passing the first fourteen positional arguments (`arg[0]` through `arg[13]`) to the `PYUSM` constructor. The method accepts its parameters via `*arg` and maps each index directly to the corresponding constructor parameter in order. The resulting `PYUSM` object is returned to the caller upon successful instantiation.

##### insert_pysito_point(self)

*No description available.*
Constructs and returns a `PYSITO_POINT` instance using the first three elements of the provided variable-length argument list (`arg[0]`, `arg[1]`, `arg[2]`). The method accepts positional arguments via `*arg` and passes them directly to the `PYSITO_POINT` constructor without additional processing. The resulting `PYSITO_POINT` object is returned to the caller.

##### insert_pysito_polygon(self)

*No description available.*
Constructs and returns a `PYSITO_POLYGON` instance using the first three elements of the provided variable-length argument list (`arg[0]`, `arg[1]`, `arg[2]`). The method accepts positional arguments via `*arg` and passes them directly to the `PYSITO_POLYGON` constructor without modification. The newly created `PYSITO_POLYGON` object is returned to the caller.

##### insert_pyquote(self)

*No description available.*
Creates and returns a `PYQUOTE` instance by accepting a variable number of positional arguments and passing the first eleven elements (`arg[0]` through `arg[10]`) to the `PYQUOTE` constructor. The method requires at least eleven arguments to be provided; no validation or default handling is visible in the source. Returns the constructed `PYQUOTE` object.

##### insert_pyquote_usm(self)

*No description available.*
Creates and returns a `PYQUOTEUSM` instance by accepting a variable number of positional arguments and passing the first eleven elements (`arg[0]` through `arg[10]`) to the `PYQUOTEUSM` constructor. The method returns the newly constructed `PYQUOTEUSM` object directly without additional processing or validation.

##### insert_pyus_negative(self)

*No description available.*
```python
def insert_pyus_negative(self, *arg)
```

Constructs and returns a `PYUS_NEGATIVE` instance using a variable-length argument list. The method passes exactly seven positional arguments (`arg[0]` through `arg[6]`) to the `PYUS_NEGATIVE` constructor. The resulting `PYUS_NEGATIVE` object is returned to the caller.

##### insert_pystrutture(self)

*No description available.*
Accepts a variable number of positional arguments and constructs a `PYSTRUTTURE` instance using the first twelve elements (`arg[0]` through `arg[11]`). Returns the newly created `PYSTRUTTURE` object.

##### insert_pyreperti(self)

*No description available.*
Constructs and returns a `PYREPERTI` instance using the first five elements of the provided variadic argument list (`arg[0]` through `arg[4]`). The method accepts a variable number of positional arguments and passes them positionally to the `PYREPERTI` constructor. The newly created `PYREPERTI` object is returned directly to the caller.

##### insert_pyindividui(self)

*No description available.*
Creates and returns a `PYINDIVIDUI` instance constructed from six positional arguments passed via the variable-length `*arg` parameter. The arguments are unpacked in order (`arg[0]` through `arg[5]`) and forwarded directly to the `PYINDIVIDUI` constructor. The resulting `PYINDIVIDUI` object is returned to the caller.

##### insert_pycampioni(self)

*No description available.*
Creates and returns a `PYCAMPIONI` instance by accepting a variable number of positional arguments and passing the first nine elements (`arg[0]` through `arg[8]`) to the `PYCAMPIONI` constructor. The constructed object is returned directly to the caller without any additional processing or validation.

**Signature:** `insert_pycampioni(self, *arg) -> PYCAMPIONI`

##### insert_pytomba(self)

*No description available.*
Creates and returns a `PYTOMBA` instance using the first four elements of the provided positional arguments (`arg[0]` through `arg[3]`). The method accepts a variable number of arguments via `*arg` and passes them positionally to the `PYTOMBA` constructor. The constructed `PYTOMBA` object is returned directly to the caller.

##### insert_pydocumentazione(self)

*No description available.*
Creates and returns a `PYDOCUMENTAZIONE` instance by accepting a variable number of positional arguments. Exactly seven arguments are expected, passed via `*arg`, which are forwarded positionally (`arg[0]` through `arg[6]`) to the `PYDOCUMENTAZIONE` constructor. The constructed object is returned directly to the caller.

##### insert_pylineeriferimento(self)

*No description available.*
Creates and returns a `PYLINEERIFERIMENTO` instance by accepting a variable number of positional arguments and passing the first five elements (`arg[0]` through `arg[4]`) to the `PYLINEERIFERIMENTO` constructor. The method takes no keyword arguments and relies entirely on the positional ordering of the provided argument sequence. Returns the newly constructed `PYLINEERIFERIMENTO` object.

##### insert_pyripartizioni_spaziali(self)

*No description available.*
Creates and returns a `PYRIPARTIZIONI_SPAZIALI` instance by accepting a variable-length argument list and passing the first six positional arguments (`arg[0]` through `arg[5]`) to the `PYRIPARTIZIONI_SPAZIALI` constructor. The method returns the newly created `PYRIPARTIZIONI_SPAZIALI` object.

##### insert_pysezioni(self)

*No description available.*
Instantiates and returns a `PYSEZIONI` object using the provided positional arguments. The method accepts a variable-length argument list and passes the first eight elements (`arg[0]` through `arg[7]`) as positional parameters to the `PYSEZIONI` constructor. The resulting `PYSEZIONI` instance is then returned to the caller.

##### insert_values(self)

Istanzia la classe US da pyarchinit_db_mapper

##### insert_ut_values(self)

Istanzia la classe UT da pyarchinit_db_mapper

##### insert_site_values(self)

Istanzia la classe SITE da pyarchinit_db_mapper

##### insert_periodizzazione_values(self)

Istanzia la classe Periodizzazione da pyarchinit_db_mapper

##### insert_values_reperti(self)

Istanzia la classe Reperti da pyarchinit_db_mapper

##### insert_struttura_values(self)

Istanzia la classe Struttura da pyarchinit_db_mapper

##### insert_values_ind(self)

Istanzia la classe SCHEDAIND da pyarchinit_db_mapper

##### insert_values_detsesso(self)

Istanzia la classe DETSESSO da pyarchinit_db_mapper

##### insert_values_deteta(self)

Istanzia la classe DETETA da pyarchinit_db_mapper

##### insert_media_values(self)

Istanzia la classe MEDIA da pyarchinit_db_mapper

##### insert_mediathumb_values(self)

Istanzia la classe MEDIA da pyarchinit_db_mapper

##### insert_media2entity_values(self)

Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper

##### insert_media2entity_view_values(self)

Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper

##### insert_values_tomba(self)

Istanzia la classe TOMBA da pyarchinit_db_mapper

##### insert_values_campioni(self)

Istanzia la classe CAMPIONI da pyarchinit_db_mapper

##### insert_values_thesaurus(self)

Istanzia la classe PYARCHINIT_THESAURUS_SIGLE da pyarchinit_db_mapper

##### insert_values_Lapidei(self)

Istanzia la classe Inventario_Lapidei da pyarchinit_db_mapper

##### insert_values_documentazione(self)

Istanzia la classe DOCUMENTAZIONE da pyarchinit_db_mapper

##### insert_pdf_administrator_values(self)

Istanzia la classe PDF_ADMINISTRATOR da pyarchinit_db_mapper

##### insert_campioni_values(self)

Istanzia la classe CAMPIONI da pyarchinit_db_mapper

##### insert_values_fauna(self)

Istanzia la classe FAUNA da pyarchinit_db_mapper

##### insert_tma_values(self)

Istanzia la classe TMA da pyarchinit_db_mapper

##### insert_tma_materiali_values(self)

Istanzia la classe TMA_MATERIALI da pyarchinit_db_mapper

##### insert_media_to_entity_values(self)

Istanzia la classe MEDIATOENTITY da pyarchinit_db_mapper

##### insert_personale_values(self)

Istanzia la classe PERSONALE

##### insert_presenze_values(self)

Istanzia la classe PRESENZE

##### insert_attrezzature_values(self)

Istanzia la classe ATTREZZATURE

##### insert_budget_values(self)

Istanzia la classe BUDGET

##### insert_computo_metrico_values(self)

Istanzia la classe COMPUTO_METRICO

##### execute_sql_create_db(self)

*No description available.*
Reads and executes a SQL script (`pyarchinit_create_db.sql`) located in the `query_sql` subdirectory relative to the current file's directory. Before executing the script, it sets the database connection's isolation level to `ISOLATION_LEVEL_AUTOCOMMIT` using the underlying `psycopg2` connection obtained from the SQLAlchemy engine. The SQL content is read from the file, passed to the engine as a text statement, and executed in a single operation.

##### execute_sql_create_spatialite_db(self)

Reads and executes the SQL script `pyarchinit_create_spatialite_db.sql`, located in the `query_sql` subdirectory relative to the current file, to create a SpatiaLite database schema. The method opens a SQLAlchemy session bound to `self.engine` with autoflush enabled, executes the full SQL string within an explicit transaction, and commits the changes before closing the session.

##### execute_sql_create_layers(self)

Reads a SQL script file named `pyarchinit_layers_postgis.sql` from the `query_sql` subdirectory relative to the current module's location, then executes its contents against the configured database engine within a managed session. The session is explicitly begun, committed, and closed after execution.

##### execute_sql(self, query_string, params)

Execute a raw SQL query and return results

##### query(self, n)

Executes a database query that retrieves all records for the ORM class identified by the string `n`, which is resolved to a class reference via `eval`. A fresh SQLAlchemy session is created directly from the engine for each call, with `populate_existing=True` set to bypass the identity map cache and force re-reading from the database. The session is closed in a `finally` block after all records are returned, and performance timing is logged at the start and end of the operation.

##### query_ordered(self, table_class_name, order_column, order_dir)

Single query with ORDER BY - replaces the double query pattern.

Args:
    table_class_name: Name of the entity class (e.g., 'US', 'SITE')
    order_column: Column name to order by (e.g., 'id_us')
    order_dir: 'asc' or 'desc'

Returns:
    List of records ordered by the specified column

##### query_limit_offset(self, table_name, filter_text, limit, offset)

*No description available.*
Queries a specified database table with optional filtering, pagination, or both. If `filter_text` is provided, results are filtered by a case-insensitive partial match against the `media_filename` column and ordered by that column. If both `limit` and `offset` are provided, the query results are paginated accordingly; all matching records are returned as a list of row objects.

##### count_total_images(self, table_name, filter_text)

*No description available.*
Counts the total number of records in the specified database table. If the optional `filter_text` parameter is provided, the count is restricted to rows whose `title` column matches the given text using a case-insensitive `LIKE` pattern (`%filter_text%`). Returns the resulting integer count as a scalar value.

##### query_bool_us(self, params, table_class)

Queries a database table by constructing a set of filter conditions from the provided `params` dictionary, applying all conditions as a boolean AND conjunction. Before building the query, empty items are removed from `params` using `Utility.remove_empty_items_fr_dict`; string values are matched using a `LIKE` condition, while non-string values are matched using strict equality. The method opens a SQLAlchemy session, executes the query against the specified `table_class`, and returns all matching records before closing the session.

##### query_bool_like(self, params, table, join_operator)

*No description available.*
Queries a specified database table using case-insensitive `ILIKE` pattern matching (`%value%`) against the provided parameter dictionary, after first removing empty entries from it. For columns named `settore`, `struttura`, `quad_par`, `ambient`, `saggio`, or `area`, the value is split on `", "` and matched against multiple sub-values using `OR`; the `sito` column filter, if present, is always applied first using `AND`, while the remaining filters are combined using the operator specified by `join_operator` (`'or'` by default, or `'and'`). Returns all matching rows as a list of result tuples and closes the session before returning.

##### query_bool_postgres(self, params, table)

*No description available.*
Queries a PostgreSQL database table by constructing a filtered SQLAlchemy query from the provided parameter dictionary, combining all key-value conditions using a boolean `AND` expression. Before building the query, empty items are removed from `params` using `Utility.remove_empty_items_fr_dict`. Returns a list of all matching records, or an empty list if a `SQLAlchemyError` or any other exception occurs during execution.

##### query_sql(self, query)

Execute raw SQL query and return results

##### query_thesaurus_batch(self, nome_tabella, lingua)

Carica TUTTI i valori del thesaurus per una tabella in UNA sola query.
Ritorna un dizionario: {tipologia_sigla: [lista di risultati]}

Questo metodo è MOLTO più veloce rispetto a chiamare query_bool 40+ volte.

##### query_media_thumb_batch(self, id_media_list)

Carica TUTTI i MEDIA_THUMB per una lista di id_media in UNA sola query.
Ritorna un dizionario: {id_media: record_media_thumb}

Questo metodo è MOLTO più veloce rispetto a fare N query separate.

##### query_bool(self, params, table_class_name)

*No description available.*
Queries a mapped database table identified by `table_class_name` using a set of equality conditions derived from the `params` dictionary, returning all matching ORM instances. Empty items are removed from `params` before query construction, and each remaining key-value pair is matched against the corresponding column via a boolean AND filter. Results are cached for 300 seconds; for the `PYARCHINIT_THESAURUS_SIGLE` table, an optional compatibility layer is applied to expand a single `nome_tabella` value into multiple compatible names, deduplicating the combined results by `sigla`.

##### select_mediapath_from_id(self, media_id)

Retrieves the file path associated with a given media record from `media_table`.

Executes a SQL query against `media_table` using the provided `media_id` to locate the corresponding `filepath` column value. Returns the file path string if a matching record is found, or `None` if no record exists for the given identifier.

##### query_all_us(self, table_class_str, column_name)

Retrieve all records from a specified table and return values of a specific column.

:param table_class_str: The name of the table class as a string.
:param column_name: The name of the column to retrieve values from.
:return: A list of values from the specified column of all records.

##### query_all(self, table_class_str)

Retrieve all records from a specified table.

:param table_class_str: The name of the table class as a string.
:return: A list of all records from the specified table.

##### query_bool_special(self, params, table)

*No description available.*
Queries a database table using SQLAlchemy by constructing and evaluating a dynamic filter expression from a dictionary of field-value pairs. Before building the query, empty items are removed from `params` using `Utility.remove_empty_items_fr_dict`; the remaining key-value pairs are then assembled into a comma-separated equality condition string and combined with SQLAlchemy's `and_` operator. The method opens a new session, executes the constructed query string via `eval`, closes the session, and returns all matching records.

##### query_operator(self, params, table)

*No description available.*
Queries a database table by constructing and evaluating a dynamic SQLAlchemy filter expression using a list of field-operator-value triplets provided in `params`. Each triplet `(field, operator, value)` is assembled into a `table.field operator value` string, and all conditions are combined using SQLAlchemy's `and_()` function. The method opens a session bound to the existing engine, evaluates the constructed query string, and returns all matching records.

##### query_distinct(self, table, query_params, distinct_field_name_params)

*No description available.*
Executes a distinct SQLAlchemy query against the specified table, filtering rows by the conditions defined in `query_params` and returning only unique combinations of the fields specified in `distinct_field_name_params`. Internally, it constructs a filter string from `query_params` (a list of `[field, value]` pairs) and a column selection string from `distinct_field_name_params` (a list of field names), then assembles and evaluates a SQLAlchemy session query using `filter(and_(...))`, `.distinct()`, and `.order_by()`. Results are ordered by the same distinct fields and returned as a query result set.

##### query_distinct_sql(self, table, query_params, distinct_field_name_params)

*No description available.*
Constructs and executes a raw SQL `SELECT DISTINCT` query against a specified table, filtering results based on a list of field-value pairs provided in `query_params`. The `distinct_field_name_params` parameter specifies the fields to include in the `DISTINCT` projection, which are assembled into a comma-separated list. The resulting SQL command is executed via `_execute_sql` and its result is returned directly.

##### insert_data_session(self, data)

*No description available.*
Inserts a data object into the database within a managed session scope by adding it to the session and flushing to validate the operation before the session scope commits the transaction. If an exception occurs during the flush, it is re-raised after optional inspection of the error origin. Upon successful completion, the internal cache is cleared to ensure subsequent queries reflect the newly inserted data.

##### insert_data_conflict(self, data)

*No description available.*
Inserts or merges a data object into the database within a nested transaction, handling conflicts by merging the provided data with any existing record. The operation is performed inside a session scope, which manages the commit automatically. After the operation completes, the cache is cleared to ensure subsequent queries retrieve fresh data.

##### update(self, table_class_str, id_table_str, value_id_list, columns_name_list, values_update_list)

Receives 5 values then putted in a list. The values must be passed
in this order: table name->string, column_name_where->list containin'
one value
('site_table', 'id_sito', [1], ['sito', 'nazione', 'regione', 'comune', 'descrizione', 'provincia'], ['Sito archeologico 1', 'Italiauiodsds', 'Emilia-Romagna', 'Riminijk', 'Sito di epoca altomedievale....23', 'Riminikljlks'])
self.set_update = arg
#self.connection()
table = Table(self.set_update[0], self.metadata, autoload=True)
changes_dict= {}
u = Utility()
set_update_4 = u.deunicode_list(self.set_update[4])

u.add_item_to_dict(changes_dict,zip(self.set_update[3], set_update_4))

f = open("test_update.txt", "w")
f.write(str(self.set_update))
f.close()

exec_str = ('%s%s%s%s%s%s%s') % ("table.update(table.c.",
                                  self.set_update[1],
                                 " == '",
                                 self.set_update[2][0],
                                 "').execute(",
                                 changes_dict ,")")

#session.query(SITE).filter(and_(SITE.id_sito == '1')).update(values = {SITE.sito:"updatetest"})

##### update_tomba_dating_from_periodizzazione(self, site_name)

Updates the `datazione_estesa` field in `tomba_table` for all tomb records belonging to the specified `site_name` by looking up corresponding dating information from `periodizzazione_table`. For each tomb record with non-empty `periodo_iniziale` and `fase_iniziale` values, it constructs a dating string from the matched `periodizzazione` record(s); if both an initial and a final period are present, the two `datazione_estesa` values are concatenated with a `/` separator. Returns the total count of updated records, rolls back the transaction and raises the exception on error, and displays a `QMessageBox` warning if an exception occurs.

##### update_us_dating_from_periodizzazione(self, site_name)

*No description available.*
Updates the `datazione` field in `us_table` for all records belonging to the specified site by deriving dating strings from corresponding entries in `periodizzazione_table`. For each US record, it looks up the initial (and optionally final) period/phase combination; if a matching `periodizzazione_iniziale` record is found, it constructs a `datazione_estesa` string (combining initial and final extended dating values separated by `/` when both exist), otherwise it sets `datazione` to `None`. Returns the total count of updated records on success, rolls back the transaction and re-raises the exception on failure, and closes the session in all cases.

##### update_find_check(self, table_class_str, id_table_str, value_id, find_check_value)

*No description available.*
Updates the `find_check` field of a record in the specified database table by matching a row using a given ID column and value. A SQLAlchemy session is constructed dynamically via `eval`, querying the table class identified by `table_class_str`, filtering on the column `id_table_str` where it equals `value_id`, and setting `find_check` to `find_check_value`. The session is closed immediately after the update is executed.

##### empty_find_check(self, table_class_str, find_check_value)

Updates the `find_check` column to `0` for all records in the table specified by `table_class_str`. It establishes a SQLAlchemy session bound to the instance's engine, constructs and evaluates a query string that performs a bulk update setting `find_check` to `0`, then closes the session. The `find_check_value` parameter is assigned to the instance but is not used in the executed update expression.

##### delete_one_record(self, tn, id_col, id_rec)

Delete a single record from a table - SQLAlchemy 2.0 compatible

##### delete_record_by_field(self, table_name, field_name, field_value)

Delete records from a table where field matches value

##### max_num_id(self, tc, f)

*No description available.*
Queries the database to retrieve the maximum value of a specified field within a given table class. It constructs and evaluates a SQLAlchemy `func.max()` query string dynamically using the provided table class `tc` and field name `f`. Returns the maximum value as an integer, or `0` if no value is found.

##### dir_query(self)

*No description available.*
Opens a database session bound to the current engine with `autoflush` enabled, then immediately closes it without performing any query or returning a value. The method body contains commented-out query examples but executes no active database operations. Returns `None`.

##### fields_list(self, t, s)

return the list of columns in a table. If s is set a int,
return only one column

##### query_in_idus(self, id_list)

*No description available.*
Queries the database for all `US` records whose `id_us` field matches any value in the provided `id_list`. A session is created using the bound engine with autoflush enabled, the filtered results are retrieved, and the session is closed before returning. Returns a list of `US` objects matching the given identifiers.

##### query_sort(self, id_list, op, to, tc, idn)

*No description available.*
Queries a database table for records whose primary-key column matches the provided `id_list`, returning the results sorted according to the specified ordering parameters. The target table is resolved from the string identifier `tc` against a fixed class map supporting types such as `US`, `UT`, `SITE`, `TOMBA`, `POTTERY`, and others; an unsupported value raises a `ValueError`. Sort columns are supplied as the list `op`, sort direction as the string `to` (`'asc'` or `'desc'`, defaulting to ascending), and the primary-key column name as `idn`.

##### run(self, stmt)

*No description available.*
Executes the provided SQL statement object and collects the results into a list. Iterates over each row in the result set, extracting the first column value (`row[0]`) from each row. Returns a list containing all extracted first-column values.

##### update_for(self)

table = Table('us_table_toimp', self.metadata, autoload=True)
s = table.select(table.c.id_us > 0)
res_list = self.run(s)
cont = 11900
for i in res_list:
    self.update('US_toimp', 'id_us', [i], ['id_us'], [cont])
    cont = cont+1

##### group_by(self, tn, fn, CD)

Group by the values by table name - string, field name - string, table class DB from mapper - string

##### query_where_text(self, c, v)

*No description available.*
Queries the `PERIODIZZAZIONE` table by dynamically constructing and evaluating a SQLAlchemy filter expression using the provided column name `c` and value `v`. The method opens a new database session bound to the instance's engine, builds a `filter_by` query string via string formatting, and executes it using `eval`. The resulting query object is returned after the session is closed.

##### update_cont_per(self, s)

Optimized: pre-loads all periodizzazione data in 1 query,
computes all cont_per values in memory, then batch-updates in 1 SQL.
~100x faster than the old per-record query approach.

##### remove_alltags_from_db_sql(self, s)

*No description available.*
Deletes all records from the `media_to_entity_table` database table where the `media_name` column matches the provided value `s`. Executes the constructed `DELETE` SQL query via the internal `_execute_sql` method and returns the result of that execution.

##### remove_tags_from_db_sql(self, s)

*No description available.*
Executes a SQL `DELETE` statement against `media_to_entity_table`, removing all rows whose `id_entity` column matches the provided value `s`. The query is built as a formatted string and passed to the internal `_execute_sql` method. Returns the result object produced by `_execute_sql`.

##### remove_tags_from_db_sql_scheda(self, s, n)

*No description available.*
Deletes a record from the `media_to_entity_table` where both the `id_entity` column matches the value `s` and the `media_name` column matches the value `n`. The DELETE statement is constructed as a formatted SQL string and executed via the internal `_execute_sql` method. Returns the result object produced by `_execute_sql`.

##### delete_thumb_from_db_sql(self, s)

*No description available.*
Deletes a record from the `media_thumb_table` database table where the `media_filename` column matches the provided string value `s`. Constructs and executes a `DELETE` SQL query using `_execute_sql`, then returns the resulting execution object.

**Parameters:**
- `s` *(str)*: The media filename value used as the filter condition in the `WHERE` clause.

**Returns:** The result object returned by `_execute_sql`.

##### select_medianame_from_st_sql(self, sito, sigla, numero)

*No description available.*
Queries the database to retrieve media file paths and media names associated with a specific structure record, identified by the combination of `sito`, `sigla` (structure abbreviation), and `numero` (structure number). The method performs a join across `media_to_entity_table`, `struttura_table`, and `media_thumb_table`, filtering results where the entity type is `'STRUTTURA'`. Returns all matching rows as a list of tuples via `fetchall()`.

##### select_medianame_from_db_sql(self, sito, area)

Queries the database to retrieve media file paths, stratigraphic unit (US) identifiers, and media names associated with a given site and area. It joins `media_to_entity_table`, `us_table`, and `media_thumb_table` on their respective foreign keys, filtering results by the provided `sito` and `area` parameters. Returns all matching rows as a list of tuples.

##### select_medianame_tb_from_db_sql(self, sito, area)

Queries the database to retrieve media file paths and media names associated with tomb entities (`TOMBA`) for a given site and area. It joins `media_to_entity_table`, `tomba_table`, and `media_thumb_table` on their respective identifiers, filtering by the provided `sito` and `area` parameters and restricting results to records where `entity_type` equals `'TOMBA'`. Returns all matching rows as a list of tuples via `fetchall()`.

##### select_medianame_pot_from_db_sql(self, sito, area, us)

*No description available.*
Queries the database to retrieve media file paths and media names associated with pottery records matching the specified site, area, and stratigraphic unit. The method performs a join across `media_to_entity_table`, `pottery_table`, and `media_thumb_table`, filtering results by the provided `sito`, `area`, and `us` parameters, and restricts matches to entities of type `'CERAMICA'`. Returns all matching rows as a list fetched from the query result.

##### select_medianame_ra_from_db_sql(self, sito, area, us)

*No description available.*
Executes a SQL query that retrieves the file path and media name for all media records associated with a specific archaeological find (*reperto*), identified by the combination of `sito`, `area`, and `us` parameters. The query joins `media_to_entity_table`, `inventario_materiali_table`, and `media_thumb_table`, filtering results where `entity_type` equals `'REPERTO'`. Returns all matching rows as a list of tuples fetched from the result set.

##### select_medianame_2_from_db_sql(self, sito, area, us)

*No description available.*
Queries the database to retrieve media file paths and media names associated with a specific stratigraphic unit (US) identified by the combination of `sito`, `area`, and `us` parameters. The method performs a three-table join across `media_to_entity_table`, `us_table`, and `media_thumb_table`, filtering results where the entity type is `'US'`. Returns all matching rows as a list of tuples containing the `filepath` and `media_name` fields.

##### search_untagged_media(self, text_filter)

Search for untagged images (not associated with any entity).
Returns images in media_table that have no entry in media_to_entity_table.

Args:
    text_filter: Optional text to filter by filename (LIKE pattern)

##### search_tagged_media_flexible(self, entity_type, sito, area, us, numero_inventario, text_filter, use_like)

Flexible search for tagged images with optional parameters and LIKE patterns.

Args:
    entity_type: 'US', 'CERAMICA', 'REPERTO', 'TOMBA', 'STRUTTURA', 'UT' or None for all
    sito: Site name (exact or LIKE pattern if use_like=True)
    area: Area (exact or LIKE pattern if use_like=True)
    us: Stratigraphic unit (exact or LIKE pattern if use_like=True)
    numero_inventario: Inventory number for materials (exact or LIKE)
    text_filter: Text to filter by filename/description
    use_like: If True, use LIKE for partial matching

##### search_all_media(self, text_filter, tagged_only)

Search all media with optional text filter and tagged/untagged filter.

Args:
    text_filter: Text to filter by filename
    tagged_only: True=only tagged, False=only untagged, None=all

##### search_media_by_inventario(self, sito, numero_inventario, text_filter)

Search media specifically for Inventario Materiali by numero_inventario.

##### get_total_pages(self, filter_query, page_size)

*No description available.*
Executes a `COUNT(*)` SQL query against `media_thumb_table` joined with `media_to_entity_table`, applying the provided `filter_query` to determine the total number of matching records. Divides the resulting record count by `page_size` and returns the ceiling value as the total number of pages using `math.ceil`.

**Parameters:**
- `filter_query` — A SQL fragment appended to the base query to filter the counted records.
- `page_size` — The number of records per page used to calculate the total page count.

**Returns:** An integer representing the total number of pages required to accommodate all matching records at the given page size.

##### select_thumb(self, page_number, page_size)

*No description available.*
Retrieves a paginated set of records from the `media_thumb_table` database table. The starting row offset is calculated from `page_number` and `page_size` using the expression `(page_number - 1) * page_size`, and the query is executed with the corresponding `LIMIT` and `OFFSET` clauses. Returns all fetched rows as a list of row objects.

##### select_original(self, page_number, page_size)

*No description available.*
Retrieves a paginated set of all records from `media_to_entity_table` using SQL `LIMIT` and `OFFSET` clauses. The starting index is calculated from the given `page_number` and `page_size` parameters using the expression `(page_number - 1) * page_size`. Returns all fetched rows as a list of results from the executed query.

##### select_ra_from_db_sql(self, sito, area, us)

*No description available.*
Queries the `inventario_materiali_table` database table to retrieve all `n_reperto` values matching the specified combination of `sito`, `area`, and `us` parameters. Executes the constructed SQL `SELECT` statement via `_execute_sql` and fetches all resulting rows. Returns the complete set of matching rows as a collection of results.

##### select_coord_from_db_sql(self, sito, area, us)

*No description available.*
Queries the `pyunitastratigrafiche` table to retrieve the `coord` field for a specific stratigraphic unit identified by the combination of site (`scavo_s`), area (`area_s`), and stratigraphic unit number (`us_s`). Accepts three parameters — `sito`, `area`, and `us` — which are interpolated directly into the SQL query string. Returns all matching rows as a list fetched via `fetchall()`.

##### select_medianame_3_from_db_sql(self, sito, area, us)

Executes a SQL query that retrieves media file path, stratigraphic unit (`us`), and media name from the database by joining `media_to_entity_table`, `inventario_materiali_table`, and `media_thumb_table`. The query filters results based on the provided `sito`, `area`, and `us` parameters. Returns all matching rows as a list of tuples via `fetchall()`.

##### select_thumbnail_from_db_sql(self, sito)

*No description available.*
Queries the database to retrieve thumbnail and media information associated with stratigraphic units for a given site (`sito`). The SQL query joins `media_to_entity_table`, `us_table`, and `media_thumb_table`, selecting the file path, concatenated US identifiers, media name, area, and unit type, grouped and ordered by media name in ascending order. Returns all resulting rows as a list of tuples via `fetchall()`.

##### select_quote_from_db_sql(self, sito, area, us)

*No description available.*
Queries the `pyarchinit_quote` table for all records matching the specified site (`sito`), area (`area`), and stratigraphic unit (`us`) identifiers. Constructs a raw SQL `SELECT *` statement using the provided parameters and executes it via the internal `_execute_sql` method. Returns the raw result object produced by the SQL execution.

##### select_us_from_db_sql(self, sito, area, us, stratigraph_index_us)

Executes a SQL `SELECT` query against the `pyunitastratigrafiche` table, retrieving all columns for records that match the provided `sito`, `area`, `us`, and `stratigraph_index_us` values. The query filters rows using the corresponding database columns `scavo_s`, `area_s`, `us_s`, and `stratigraph_index_us`. Returns the result set produced by the internal `_execute_sql` method.

##### select_us_doc_from_db_sql(self, sito, tipo_doc, nome_doc)

Queries the `pyunitastratigrafiche` table to retrieve all records matching the specified site, document type, and document name. Accepts `sito`, `tipo_doc`, and `nome_doc` as parameters, which are bound to the SQL query via named placeholders `:sito`, `:tipo_doc`, and `:nome_doc`. Returns the result set produced by `_execute_sql`.

##### select_usneg_doc_from_db_sql(self, sito, tipo_doc, nome_doc)

*No description available.*
Queries the `pyarchinit_us_negative_doc` database table for records matching the specified site, document type, and document name. It constructs a parameterized SQL `SELECT` statement using the named parameters `:sito`, `:tipo_doc`, and `:nome_doc`, bound to the columns `sito_n`, `tipo_doc_n`, and `nome_doc_n` respectively. The method delegates execution to `_execute_sql` and returns the resulting records.

**Parameters:**
- `sito` — The site identifier to filter by (`sito_n`).
- `tipo_doc` — The document type to filter by (`tipo_doc_n`).
- `nome_doc` — The document name to filter by (`nome_doc_n`).

**Returns:** The result set returned by `_execute_sql`.

##### select_db_sql(self, table)

*No description available.*
Executes a `SELECT *` query against the specified database table, retrieving all rows and columns. The table name is interpolated directly into the SQL query string, which is then passed to `_execute_sql` for execution. Returns the result object produced by `_execute_sql`.

##### select_db_sql_2(self, sito, area, us, d_stratigrafica)

*No description available.*
Queries the `us_table` database table for records matching the specified combination of `sito`, `area`, `us`, and `d_stratigrafica` values. Constructs a parameterized `SELECT *` SQL statement filtering on all four fields using exact string equality, executes it via `_execute_sql`, and fetches all matching rows. Returns the complete result set as a list of rows.

##### test_ut_sql(self, unita_tipo)

*No description available.*
Executes a SQL `SELECT` query against the `us_table` table, using the provided `unita_tipo` parameter as the column or expression to select. The query is constructed by formatting `unita_tipo` directly into the SQL string and then passed to the internal `_execute_sql` method for execution. Returns the result set produced by the executed query.

##### query_in_contains_onlysqlite(self, value_list, sitof, areaf, chunk_size)

Esegue una query suddividendo la lista dei valori in chunk per evitare il limite di profondità di SQLite.

Args:
    value_list (list): Lista di valori da cercare.
    sitof (str): Valore per il filtro 'sito'.
    areaf (str): Valore per il filtro 'area'.
    chunk_size (int): Dimensione dei chunk. Default è 100.

Returns:
    list: Lista dei risultati della query.

##### query_in_contains(self, value_list, sitof, areaf)

*No description available.*
Queries the database for `US` records matching the specified `sito` and `area` filter values, where the `rapporti` field contains at least one value from `value_list`. The input list is processed in chunks of 500 entries to avoid query size limitations, using an `OR` condition across all values in each chunk. Returns a flat list of all matching `US` objects accumulated across all chunks.

##### insert_arbitrary_number_of_us_records(self, us_range, sito, area, n_us, unita_tipo)

Inserts a specified number of US (Stratigraphic Unit) records into the database by iterating over a range defined by `us_range`. For each iteration, it retrieves and increments the current maximum `id_us` value, constructs a new record using `insert_values` with the provided `sito`, `area`, `n_us`, and `unita_tipo` parameters alongside default empty or placeholder values, and persists it via `insert_data_session`. The `n_us` value is incremented after each insertion to ensure each new record receives a unique unit number.

##### insert_number_of_rapporti_records(self, sito, area, n_us, n_rapporti, unita_tipo)

*No description available.*
```python
def insert_number_of_rapporti_records(self, sito, area, n_us, n_rapporti, unita_tipo)
```

Inserts a single US (Unità Stratigrafica) record into the data session, automatically assigning the next available `id_us` and populating the rapporti (relationships) field from the provided `n_rapporti` data. The `n_rapporti` parameter is expected to be an iterable of tuples containing `(rapporto_tipo, rapporto_n_us, rapporto_area, rapporto_sito)`, which are converted into a list of lists and stored as a string. The auto-generated description field is set to either `"SCHEDA CREATA IN AUTOMATICO"` or `"FORM MADE AUTOMATIC"` depending on the active locale.

##### insert_number_of_us_records(self, sito, area, n_us, unita_tipo)

*No description available.*
Inserts a new US (Unità Stratigrafica) record into the database for a given site, area, unit number, and unit type. It determines the next available `id_us` by retrieving the current maximum ID and incrementing it by one, then constructs a default descriptive text based on the user's locale (`"SCHEDA CREATA IN AUTOMATICO"` for Italian, `"FORM MADE AUTOMATIC"` otherwise). The method populates the record with the provided parameters alongside empty or default placeholder values via `insert_values`, and commits the record to the session using `insert_data_session`.

##### insert_number_of_reperti_records(self, sito, numero_inventario)

*No description available.*
**Signature:** `insert_number_of_reperti_records(self, sito, numero_inventario)`

Inserts a new record into the `INVENTARIO_MATERIALI` table by first retrieving the current maximum `id_invmat` value and incrementing it by one to generate the next identifier. It constructs the record by calling `insert_values_reperti` with the new `id_invmat`, the provided `sito` and `numero_inventario` values, and empty or `None` defaults for all remaining fields. The resulting data is then persisted via `insert_data_session`.

##### insert_number_of_pottery_records(self, id_number, sito, area, us)

Inserts a new pottery record into the database for a given combination of `id_number`, `sito`, `area`, and `us` parameters. It first retrieves the current maximum `id_rep` value from the `POTTERY` table and increments it by one to generate the next identifier, then constructs a new pottery entry by calling `insert_pottery_values` with the generated ID and default/empty values for all remaining fields. The resulting data object is persisted to the current session via `insert_data_session`.

##### insert_number_of_tomba_records(self, sito, nr_scheda_taf)

*No description available.*
Inserts a new tomb (`TOMBA`) record into the data session using the provided site (`sito`) and tomb card number (`nr_scheda_taf`). The method first retrieves the current maximum `id_tomba` value and increments it by one to generate the next sequential identifier. All remaining fields of the tomb record are populated with empty strings, and the constructed record is then passed to `insert_data_session` for persistence.

##### insert_struttura_records(self, sito, sigla_struttura, numero_struttura)

*No description available.*
**Signature:** `insert_struttura_records(self, sito, sigla_struttura, numero_struttura)`

Inserts a new record into the `STRUTTURA` table by first retrieving the next available identifier via `max_num_id`, incrementing it by one, and then constructing the record using `insert_struttura_values` with the provided `sito`, `sigla_struttura`, and `numero_struttura` parameters alongside empty string placeholders for the remaining fields. The resulting data is then persisted to the database via `insert_data_session`. The method also retrieves the current user locale from `QgsSettings` though this value is not directly used in the visible logic.

##### select_like_from_db_sql(self, rapp_list, us_rapp_list)

*No description available.*
This method accepts two parameters, `rapp_list` and `us_rapp_list`, intended to support a database query operation filtering records based on the provided lists. The current implementation is a stub and contains no active logic, as the method body consists solely of a `pass` statement. The commented-out code suggests a planned implementation involving SQLAlchemy session queries with `OR`-based filtering, but this functionality is not documented in source.

##### select_not_like_from_db_sql(self, sitof, areaf)

*No description available.*
Queries the database for `US` records matching the specified `sitof` (site) and `areaf` (area) values, excluding any records whose `rapporti` field matches a set of relationship pattern strings. The exclusion patterns are built from a fixed literal (`"%'>>'%"`) combined with patterns derived from the union of `COVERS_GROUP`, `FILLS_GROUP`, `CUTS_GROUP`, and `ABUTS_GROUP` term sets sourced from the central i18n module. The method iterates over all filters sequentially, with each iteration overwriting `res`, and returns the query result of the final filter applied before closing the session.

##### query_in_idusb(self)

*No description available.*
Defines a query operation intended to retrieve records by USB ID within the database management context. The method body is not implemented in the provided source (`pass`), and no parameters, return values, or internal logic are documented. See implementation for details.

### ANSI

# ANSI

A utility class that provides static methods for generating ANSI escape sequences used to format terminal output. The class exposes three methods — `background`, `style_text`, and `color_text` — each accepting a numeric `code` parameter and returning a formatted escape sequence string in the form `\33[{code}m`. These sequences can be used to control text color, background color, and text styling in ANSI-compatible terminal environments.

#### Methods

##### background(code)

*No description available.*
Returns an ANSI escape sequence string for setting a terminal background color. The method formats the provided `code` value into the escape sequence `"\33[{code}m"`, where `\33` is the ESC character. The resulting string can be used to control background color rendering in ANSI-compatible terminals.

##### style_text(code)

*No description available.*
Returns an ANSI escape sequence string for applying a text style, formatted as `\33[{code}m` where `{code}` is the provided style code. The method accepts a single parameter, `code`, which represents the ANSI style code to be embedded in the escape sequence. This is a static-style method defined on the `ANSI` class and produces output in the same format as `background` and `color_text`.

##### color_text(code)

*No description available.*
Formats the given `code` value into an ANSI escape sequence string using the template `"\33[{code}m"`. Returns the resulting string, which can be used to apply terminal color or styling when printed to a compatible output. Accepts a single parameter, `code`, representing the ANSI code to embed in the escape sequence.

### ResultWrapper

Wrapper to maintain compatibility with old engine.execute() API

#### Methods

##### __init__(self, rows)

*No description available.*
Initializes a `ResultWrapper` instance by consuming the provided `rows` iterable into an internal list. If `rows` is falsy or empty, the internal list is set to an empty list. Also initializes an internal index counter `_index` to `0` for tracking the current position.

##### fetchall(self)

*No description available.*
Returns all rows stored in the result set as a list. The returned value is the complete `_rows` list, regardless of the current internal index position. No advancement of the internal cursor occurs as a result of this call.

##### fetchone(self)

*No description available.*
Returns the next row from the result set at the current index position, then advances the internal index by one. If no more rows are available (i.e., the index has reached or exceeded the total number of rows), the method returns `None`.

##### scalar(self)

*No description available.*
Returns the first column value of the first row in the result set. If `_rows` is empty or the first row contains no elements, the method returns `None`. This is useful for retrieving a single value from a query result without iterating over the full row structure.

##### __iter__(self)

*No description available.*
Returns an iterator over the `_rows` collection. This method enables iteration over the object's rows using standard Python iteration protocols, such as `for` loops or other iterator-consuming constructs. It delegates directly to the built-in `iter()` function applied to `_rows`.

## Functions

### get_db_manager(conn_str, use_singleton)

Factory function per ottenere DB Manager
Se use_singleton=True usa il singleton (per performance)
Se use_singleton=False crea nuova istanza (per operazioni specifiche)

**Parameters:**
- `conn_str`
- `use_singleton`

