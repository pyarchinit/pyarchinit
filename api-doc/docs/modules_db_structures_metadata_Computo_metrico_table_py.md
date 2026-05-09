# modules/db/structures_metadata/Computo_metrico_table.py

## Overview

This file contains 3 documented elements.

## Classes

### Computo_metrico_table

*No description available.*
A SQLAlchemy table definition class representing volumetric and metric computation records associated with archaeological excavation sites. It exposes a single class method, `define_table`, which constructs and returns a `Table` object bound to the provided `metadata`, containing columns for a unique record identifier, site name, computation name and type, pre- and post-excavation DEM layers, polygon layer reference, area (square metres), volume (cubic metres), elevation bounds, computation date, excavation phase, notes, and a UUID v4 persistent entity identifier.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object named `'computo_metrico_table'` bound to the provided `metadata`, representing volumetric and metric computation records for archaeological excavation. The table schema includes columns for a primary key (`id_computo`), site and computation identifiers (`sito`, `nome_calcolo`, `tipo_calcolo`), pre- and post-excavation DEM layer references (`dem_pre`, `dem_post`), a polygon layer reference (`layer_poligono`), numeric measurement fields (`area_mq`, `volume_mc`, `quota_min`, `quota_max`), and descriptive fields (`data_calcolo`, `fase_scavo`, `note`, `entity_uuid`). The `entity_uuid` column stores a StratiGraph persistent identifier in UUID v4 format.

