# modules/db/structures_metadata/Inventario_materiali_table.py

## Overview

This file contains 3 documented elements.

## Classes

### Inventario_materiali_table

*No description available.*
Defines the SQLAlchemy table schema for an archaeological materials inventory, mapping to the `inventario_materiali_table` database table. The class exposes a single class method, `define_table`, which accepts a `metadata` object and returns a `Table` instance containing columns for recording artifact attributes such as site, inventory number, find type, stratigraphic unit, measurements, conservation state, dating, photo and drawing references, and a UUID-based persistent identifier. A `UniqueConstraint` named `ID_invmat_unico` enforces uniqueness on the combination of `sito` and `numero_inventario`.

#### Methods

##### define_table(cls, metadata)

*No description available.*
```python
@classmethod
def define_table(cls, metadata):
```

A class method that constructs and returns a SQLAlchemy `Table` object named `'inventario_materiali_table'` bound to the provided `metadata` instance, defining the full schema for an archaeological materials inventory. The table includes columns covering artifact identification, site and stratigraphic context, physical characteristics, measurements, conservation state, cataloging metadata, and media references, using types such as `Integer`, `Text`, `String`, and `Numeric`. A `UniqueConstraint` named `'ID_invmat_unico'` enforces uniqueness on the combination of `sito` and `numero_inventario`.

