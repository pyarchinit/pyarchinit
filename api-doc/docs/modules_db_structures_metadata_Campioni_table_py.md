# modules/db/structures_metadata/Campioni_table.py

## Overview

This file contains 3 documented elements.

## Classes

### Campioni_table

*No description available.*
A SQLAlchemy table definition class representing archaeological samples (*campioni*). It exposes a single class method, `define_table(cls, metadata)`, which accepts an external `MetaData` object and returns a `Table` named `'campioni_table'` with columns for sample identification (`id_campione`), site (`sito`), sample number (`nr_campione`), sample type (`tipo_campione`), description (`descrizione`), excavation area (`area`), stratigraphic unit (`us`), material inventory number (`numero_inventario_materiale`), storage box (`nr_cassa`), conservation location (`luogo_conservazione`), and a StratiGraph UUID (`entity_uuid`). A `UniqueConstraint` named `'ID_invcamp_unico'` enforces the uniqueness of the combination of `sito` and `nr_campione` across all records.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object named `'campioni_table'` using the provided `metadata`, representing archaeological samples (Campioni). The table includes columns for a primary key (`id_campione`), site (`sito`), sample number (`nr_campione`), sample type, description, excavation area, stratigraphic unit, inventory number, storage box, storage location, and a StratiGraph UUID. A `UniqueConstraint` named `'ID_invcamp_unico'` enforces uniqueness on the combination of `sito` and `nr_campione`.

