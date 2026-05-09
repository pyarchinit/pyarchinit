# modules/db/structures_metadata/Budget_table.py

## Overview

This file contains 3 documented elements.

## Classes

### Budget_table

*No description available.*
Defines the SQLAlchemy table schema for archaeological site budget and expense records. The class exposes a single class method, `define_table`, which accepts a `metadata` object and returns a `Table` instance mapped to `budget_table`, containing columns for a unique record identifier (`id_budget`), site name, budget year, expense category, description, planned and actual amounts, registration and expense dates, supplier name, invoice number, notes, and a StratiGraph persistent UUID. All fields use `Integer`, `Float`, or `Text` types, with `id_budget` serving as the primary key.

#### Methods

##### define_table(cls, metadata)

*No description available.*
A class method that constructs and returns a SQLAlchemy `Table` object named `'budget_table'` using the provided `metadata` instance. The table schema defines columns for tracking archaeological site budget and expense records, including fields for site name (`sito`), budget year (`anno`), expense category (`categoria`), planned and actual amounts (`importo_previsto`, `importo_effettivo`), supplier and invoice details, registration and expense dates, notes, and a UUID v4 persistent identifier (`entity_uuid`). The primary key is defined on the `id_budget` integer column.

