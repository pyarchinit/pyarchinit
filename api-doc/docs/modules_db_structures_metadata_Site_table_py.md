# modules/db/structures_metadata/Site_table.py

## Overview

This file contains 3 documented elements.

## Classes

### Site_table

*No description available.*
A SQLAlchemy table definition class representing archaeological sites in a database. It exposes a single class method, `define_table`, which constructs and returns a `Table` object named `'site_table'` bound to the provided `metadata`, containing columns for site identification (`id_sito`), name (`sito`), geographic location (`nazione`, `regione`, `comune`, `provincia`), descriptive fields (`descrizione`, `definizione_sito`), a documentation path (`sito_path`), a finds inventory check (`find_check`), and a StratiGraph persistent identifier (`entity_uuid`). A `UniqueConstraint` named `'ID_sito_unico'` enforces uniqueness on the `sito` column.

#### Methods

##### define_table(cls, metadata)

*No description available.*
A class method that defines and returns a SQLAlchemy `Table` object named `'site_table'` bound to the provided `metadata` instance. The table schema includes columns for a primary key (`id_sito`), site name (`sito`), geographic location fields (`nazione`, `regione`, `comune`, `provincia`), descriptive fields (`descrizione`, `definizione_sito`), a file path (`sito_path`), an inventory check flag (`find_check`), and a StratiGraph UUID (`entity_uuid`). A `UniqueConstraint` named `'ID_sito_unico'` is enforced on the `sito` column to ensure each archaeological site name is unique within the table.

