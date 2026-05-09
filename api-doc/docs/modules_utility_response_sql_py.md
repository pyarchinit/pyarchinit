# modules/utility/response_sql.py

## Overview

This file contains 3 documented elements.

## Classes

### ResponseSQL

*No description available.*
A utility class for executing SQL queries against relational databases, with built-in support for both standard SQLAlchemy-compatible connections and SpatiaLite spatial databases. The single static method `execute_sql_and_display_results` detects whether the target database requires SpatiaLite (based on the connection string and presence of spatial keywords such as `ST_` or `GEOMETRY`), loading the appropriate extension via `sqlite3` or falling back to SQLAlchemy accordingly. Query results are returned as a list of dictionaries for `SELECT` statements, a success string for non-`SELECT` statements, or `None` on error; an optional `results_widget` parameter accepts a widget whose `setText` method is called with accumulated debug messages.

#### Methods

##### __init__(self)

*No description available.*
Default constructor for the `ResponseSQL` class. Performs no initialization logic beyond object instantiation, as the method body consists solely of a `pass` statement.

##### execute_sql_and_display_results(con_string, sql, results_widget)

Executes a SQL query against a database specified by the given connection string, automatically selecting between a direct SpatiaLite (sqlite3) connection for SQLite databases containing spatial operations (`ST_` or `GEOMETRY` references) and a SQLAlchemy engine for all other databases. For `SELECT` statements, the method returns query results as a list of dictionaries mapping column names to row values; for non-`SELECT` statements executed via SQLAlchemy, it returns the string `'Query executed successfully'`; on error, it returns `None`. If a `results_widget` is provided, debug and error messages accumulated during execution are written to it via `setText`.

