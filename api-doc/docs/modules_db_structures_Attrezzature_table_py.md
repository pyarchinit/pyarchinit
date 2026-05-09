# modules/db/structures/Attrezzature_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Attrezzature_table

*No description available.*
Defines the SQLAlchemy table schema for `attrezzature_table`, which stores equipment inventory records within the pyArchInit database. The table captures equipment attributes including inventory code, name, category, brand, model, serial number, ownership, acquisition data, rental and purchase costs, maintenance dates, assignment, status, and notes. A composite unique constraint (`ID_attrezzatura_unico`) is enforced on the `sito` and `codice_inventario` columns to prevent duplicate equipment entries per site.

