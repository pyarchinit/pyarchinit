# modules/db/db_createdump.py

## Overview

This file contains 84 documented elements.

## Classes

### PyArchInitDBLogger

Simple file logger for database operations

#### Methods

##### __init__(self)

##### log(self, message)

Write a log message with timestamp

##### log_exception(self, exc, context)

Log an exception with traceback

### SchemaDump

**Inherits from**: object

#### Methods

##### __init__(self, db_url, schema_file_path)

##### dump_shema(self)

### RestoreSchema

**Inherits from**: object

#### Methods

##### __init__(self, db_url, schema_file_path)

##### restore_schema(self)

##### update_geom_srid(self, schema, crs)

##### set_owner(self, owner)

##### update_geom_srid_sl(self, crs)

### CreateDatabase

**Inherits from**: object

#### Methods

##### __init__(self, db_name, db_host, db_port, db_user, db_passwd)

##### createdb(self)

### DropDatabase

**Inherits from**: object

#### Methods

##### __init__(self, db_url)

##### dropdb(self)

### PyArchInitDBLogger

Simple file logger for database operations

#### Methods

##### __init__(self)

##### log(self, message)

Write a log message with timestamp

##### log_exception(self, exc, context)

Log an exception with traceback

### SchemaDump

**Inherits from**: object

#### Methods

##### __init__(self, db_url, schema_file_path)

##### dump_shema(self)

### RestoreSchema

**Inherits from**: object

#### Methods

##### __init__(self, db_url, schema_file_path)

##### restore_schema(self)

##### update_geom_srid(self, schema, crs)

##### set_owner(self, owner)

##### update_geom_srid_sl(self, crs)

### CreateDatabase

**Inherits from**: object

#### Methods

##### __init__(self, db_name, db_host, db_port, db_user, db_passwd)

##### createdb(self)

### DropDatabase

**Inherits from**: object

#### Methods

##### __init__(self, db_url)

##### dropdb(self)

### PyArchInitDBLogger

Simple file logger for database operations

#### Methods

##### __init__(self)

##### log(self, message)

Write a log message with timestamp

##### log_exception(self, exc, context)

Log an exception with traceback

### SchemaDump

**Inherits from**: object

#### Methods

##### __init__(self, db_url, schema_file_path)

##### dump_shema(self)

### RestoreSchema

**Inherits from**: object

#### Methods

##### __init__(self, db_url, schema_file_path)

##### restore_schema(self)

##### update_geom_srid(self, schema, crs)

##### set_owner(self, owner)

##### update_geom_srid_sl(self, crs)

### CreateDatabase

**Inherits from**: object

#### Methods

##### __init__(self, db_name, db_host, db_port, db_user, db_passwd)

##### createdb(self)

### DropDatabase

**Inherits from**: object

#### Methods

##### __init__(self, db_url)

##### dropdb(self)

### PyArchInitDBLogger

Simple file logger for database operations

#### Methods

##### __init__(self)

##### log(self, message)

Write a log message with timestamp

##### log_exception(self, exc, context)

Log an exception with traceback

### SchemaDump

**Inherits from**: object

#### Methods

##### __init__(self, db_url, schema_file_path)

##### dump_shema(self)

### RestoreSchema

**Inherits from**: object

#### Methods

##### __init__(self, db_url, schema_file_path)

##### restore_schema(self)

##### update_geom_srid(self, schema, crs)

##### set_owner(self, owner)

##### update_geom_srid_sl(self, crs)

### CreateDatabase

**Inherits from**: object

#### Methods

##### __init__(self, db_name, db_host, db_port, db_user, db_passwd)

##### createdb(self)

### DropDatabase

**Inherits from**: object

#### Methods

##### __init__(self, db_url)

##### dropdb(self)

## Functions

### dump(sql)

**Parameters:**
- `sql`

### dump(sql)

**Parameters:**
- `sql`

### dump(sql)

**Parameters:**
- `sql`

### dump(sql)

**Parameters:**
- `sql`

