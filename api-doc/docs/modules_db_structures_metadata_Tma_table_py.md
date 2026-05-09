# modules/db/structures_metadata/Tma_table.py

## Overview

This file contains 3 documented elements.

## Classes

### Tma_table

*No description available.*
A SQLAlchemy table definition class representing archaeological material data (`tma_materiali_archeologici`). It exposes a single class method, `define_table`, which constructs and returns a `Table` object bound to the provided `metadata`, comprising columns for site identification, object classification, location, excavation and survey context, acquisition details, chronological dating, analytical descriptions, historical-critical notes, photographic and drawing documentation, and system audit fields. A UUID v4 column (`entity_uuid`) serves as a persistent StratiGraph identifier for each record.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object representing the `tma_materiali_archeologici` database table, which stores archaeological material records. The table includes columns for basic site identification (`sito`, `area`, `localita`, `settore`, `inventario`), object and location data, excavation and survey information, dating, analytical data, documentation references, and system audit fields. It accepts a SQLAlchemy `metadata` object as its sole parameter and is implemented as a class method.

