# modules/db/pyarchinit_conn_strings.py

## Overview

This file contains 17 documented elements.

## Classes

### PyArchInitConnLogger

Simple file logger for connection operations

#### Methods

##### __init__(self)

Initializes a new instance of `PyArchInitConnLogger` by setting the `log_file` attribute to the hardcoded file path `'/Users/enzo/pyarchinit_conn_debug.log'`. This path designates the target file where connection operation log messages will be written. The constructor takes no parameters beyond the implicit `self`.

##### log(self, message)

Write a log message with timestamp

##### log_exception(self, exc, context)

Log an exception with traceback

### Connection

*No description available.*
Reads database and application configuration from a `config.cfg` file located under the `PYARCHINIT_HOME` environment variable and exposes its settings through dedicated accessor methods. The primary method `conn_str` constructs and returns a SQLAlchemy-compatible connection string for either a PostgreSQL or SQLite backend, logging call stack and masked connection parameters via `PyArchInitConnLogger`. Additional methods — `databasename`, `datauser`, `datahost`, `dataport`, `datapassword`, `thumb_path`, `thumb_resize`, `sito_set`, and `logo_path` — each independently parse the same configuration file and return a single-entry dictionary containing the corresponding setting value.

**Inherits from**: object

#### Methods

##### __init__(self)

Initializes a new instance of the class by creating and assigning a `PyArchInitConnLogger` object to the `self.logger` instance attribute. This logger instance is used by subsequent methods within the class, such as `conn_str`, for recording connection-related activity.

##### conn_str(self)

*No description available.*
Reads the application configuration file located at `<HOME>/pyarchinit_DB_folder/config.cfg` and constructs a database connection string based on the server type specified in the configuration. For a `postgres` server, it returns a SQLAlchemy-compatible PostgreSQL URL including SSL mode; for a `sqlite` server, it returns a SQLite URL using an absolute path derived from the home directory. Returns `None` if the server type is neither `postgres` nor `sqlite`, and raises any exception encountered during file reading or string construction.

##### databasename(self)

*No description available.*
Reads the application configuration file located at `<HOME>/pyarchinit_DB_folder/config.cfg` and parses it using the `Settings` class to extract the configured database name. Returns a dictionary with a single key `"db_name"` mapped to the value of `settings.DATABASE`.

##### datauser(self)

*No description available.*
Reads the application configuration file located at `<HOME>/pyarchinit_DB_folder/config.cfg` and parses its contents using the `Settings` class. Extracts the `USER` value from the parsed configuration after calling `set_configuration()`. Returns a dictionary of the form `{"user": settings.USER}`.

##### datahost(self)

*No description available.*
Reads the application configuration file located at `<HOME>/pyarchinit_DB_folder/config.cfg` and extracts the host setting. It instantiates a `Settings` object from the file contents, applies the configuration via `set_configuration()`, then closes the file. Returns a dictionary of the form `{"host": settings.HOST}` containing the configured host value.

##### dataport(self)

*No description available.*
Reads the application configuration file located at `pyarchinit_DB_folder/config.cfg` relative to `self.HOME`, parses its contents using a `Settings` instance, and applies the configuration via `set_configuration()`. Returns a dictionary with a single key `"port"` mapped to the value of `settings.PORT`.

##### datapassword(self)

*No description available.*
Reads the application configuration file located at `pyarchinit_DB_folder/config.cfg` relative to the instance's `HOME` directory. It parses the file contents using a `Settings` object, applies the configuration via `set_configuration()`, and extracts the `PASSWORD` value. Returns a dictionary of the form `{"password": settings.PASSWORD}`.

##### thumb_path(self)

Reads the application configuration file located at `<HOME>/pyarchinit_DB_folder/config.cfg` and extracts the thumbnail path setting. Instantiates a `Settings` object with the file contents, applies the configuration, and returns a dictionary with a single key `"thumb_path"` mapped to the value of `settings.THUMB_PATH`.

##### thumb_resize(self)

Reads the application configuration file located at `pyarchinit_DB_folder/config.cfg` relative to `self.HOME`, parses its contents using a `Settings` object, and applies the configuration via `set_configuration()`. Returns a dictionary with a single key `"thumb_resize"` whose value is `settings.THUMB_RESIZE` as read from the configuration file.

##### sito_set(self)

*No description available.*
Reads the application configuration file located at `pyarchinit_DB_folder/config.cfg` relative to `self.HOME`, and parses its contents using a `Settings` instance. Calls `set_configuration()` on the parsed settings object to apply the configuration, then closes the file. Returns a dictionary with the single key `"sito_set"` mapped to the value of `settings.SITE_SET`.

##### logo_path(self)

*No description available.*
Reads the application configuration file located at `<HOME>/pyarchinit_DB_folder/config.cfg` and parses its contents using a `Settings` object. After applying the configuration via `set_configuration()`, the method extracts the `LOGO` setting and returns it as a dictionary with the key `"logo"`.

