# modules/db/entities/PDF_ADMINISTRATOR.py

## Overview

This file contains 4 documented elements.

## Classes

### PDF_ADMINISTRATOR

*No description available.*
A data model class representing a PDF administration record, encapsulating configuration metadata for PDF generation. It stores five attributes — `id_pdf_administrator`, `table_name`, `schema_griglia`, `schema_fusione_celle`, and `modello` — corresponding to a unique identifier, a table name, a grid schema, a cell-merge schema, and a template model respectively. The `__repr__` method returns a formatted string representation of all five fields for identification and debugging purposes.

**Inherits from**: object

#### Methods

##### __init__(self, id_pdf_administrator, table_name, schema_griglia, schema_fusione_celle, modello)

## `__init__` — `PDF_ADMINISTRATOR`

Initializes a `PDF_ADMINISTRATOR` instance with five parameters that define a PDF administration configuration. The parameters `id_pdf_administrator`, `table_name`, `schema_griglia`, `schema_fusione_celle`, and `modello` are assigned directly to the corresponding instance attributes at positions 0 through 4. No validation or transformation is applied to the provided values during initialization.

##### __repr__(self)

*No description available.*
Returns an unambiguous string representation of the `PDF_ADMINISTRATOR` instance. The output follows the format `<PDF_ADMINISTRATOR('id', 'table_name', 'schema_griglia', 'schema_fusione_celle', 'modello')>`, embedding the values of the five instance attributes `id_pdf_administrator`, `table_name`, `schema_griglia`, `schema_fusione_celle`, and `modello` in that order.

