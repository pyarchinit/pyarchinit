# modules/db/structures_metadata/Documentazione_table.py

## Overview

This file contains 3 documented elements.

## Classes

### Documentazione_table

*No description available.*
A SQLAlchemy table definition class representing archaeological documentation records. It exposes a single class method, `define_table`, which constructs and returns a `Table` object named `'documentazione_table'` bound to the provided `MetaData` instance, comprising columns for a primary key (`id_documentazione`), site name (`sito`), document name (`nome_doc`), date (`data`), documentation type (`tipo_documentazione`), source (`sorgente`), scale (`scala`), drafter (`disegnatore`), notes (`note`), and a StratiGraph UUID (`entity_uuid`). A `UniqueConstraint` named `'ID_invdoc_unico'` enforces uniqueness across the combination of `sito`, `tipo_documentazione`, and `nome_doc`.

#### Methods

##### define_table(cls, metadata)

*No description available.*
A class method that defines and returns a SQLAlchemy `Table` object named `'documentazione_table'` bound to the provided `metadata` instance. The table represents archaeological documentation records and contains columns for a primary key (`id_documentazione`), site name (`sito`), document name (`nome_doc`), date (`data`), documentation type (`tipo_documentazione`), source (`sorgente`), scale (`scala`), drafter (`disegnatore`), notes (`note`), and a UUID-based persistent identifier (`entity_uuid`). A `UniqueConstraint` named `'ID_invdoc_unico'` enforces uniqueness across the combination of `sito`, `tipo_documentazione`, and `nome_doc`.

