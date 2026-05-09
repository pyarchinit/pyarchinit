# modules/db/structures_metadata/Inventario_Lapidei_table.py

## Overview

This file contains 3 documented elements.

## Classes

### Inventario_Lapidei_table

*No description available.*
A SQLAlchemy table definition class representing an inventory of stone artifacts (`lapidei`) within an archaeological data management system. It exposes a single class method, `define_table`, which constructs and returns a `Table` object bound to the provided `metadata`, comprising columns for site identification, artifact classification, physical dimensions (laying bed, waiting bed, torus, thickness, width, length, and height as `Numeric(4, 2)` values), descriptive and bibliographic fields, and a UUID-based persistent identifier. A `UniqueConstraint` named `ID_invlap_unico` enforces the uniqueness of the combination of `sito` and `scheda_numero` across all records.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object named `'inventario_lapidei_table'` bound to the provided `metadata`, representing an inventory of stone artifacts. The table includes columns for a primary key (`id_invlap`), archaeological site information, artifact attributes (typology, material, dimensions as `Numeric(4, 2)` values, description, workmanship, chronology), bibliographic and comparative references, a compiler name, and a UUID-based persistent identifier. A `UniqueConstraint` named `'ID_invlap_unico'` enforces uniqueness on the combination of `sito` and `scheda_numero`.

