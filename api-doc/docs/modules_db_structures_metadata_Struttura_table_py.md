# modules/db/structures_metadata/Struttura_table.py

## Overview

This file contains 3 documented elements.

## Classes

### Struttura_table

*No description available.*
A SQLAlchemy table definition class representing structural data of archaeological findings. It exposes a single class method, `define_table`, which constructs and returns the `struttura_table` `Table` object bound to the provided `metadata`, comprising columns for site identification, structural classification, chronological phasing, materials, measurements, interpretations, and a UUID-based persistent identifier. A `UniqueConstraint` named `ID_struttura_unico` enforces uniqueness across the combination of `sito`, `sigla_struttura`, and `numero_struttura`.

#### Methods

##### define_table(cls, metadata)

*No description available.*
A class method that defines and returns a SQLAlchemy `Table` object named `'struttura_table'` bound to the provided `metadata`, representing the structural data of archaeological findings. The table includes columns for site identification, structural classification (`sigla_struttura`, `categoria_struttura`, `tipologia_struttura`, `definizione_struttura`), chronological phasing (`periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`), descriptive and interpretive fields, materials, measurements, relational data, and a UUID-based entity identifier. A `UniqueConstraint` named `'ID_struttura_unico'` enforces uniqueness across the combination of `sito`, `sigla_struttura`, and `numero_struttura`.

