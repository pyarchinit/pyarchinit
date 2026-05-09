# modules/utility/database_schema_knowledge.py

## Overview

This file contains 7 documented elements.

## Classes

### DatabaseSchemaKnowledge

Contains complete database schema information for AI context

#### Methods

##### get_full_schema()

Returns the complete database schema as a structured dictionary
that can be used by AI for understanding relationships

##### get_schema_prompt()

Returns a text prompt describing the database schema for AI context

##### get_table_list()

Returns list of all table names

##### get_table_fields(table_name)

Returns fields for a specific table

##### get_geometry_tables()

Returns list of tables with geometry

