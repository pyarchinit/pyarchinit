# modules/db/structures_metadata/Tma_materiali_table.py

## Overview

This file contains 3 documented elements.

## Classes

### Tma_materiali_table

TMA Materiali - Table for repetitive material data

#### Methods

##### define_table(cls, metadata)

Constructs and returns a SQLAlchemy `Table` object named `'tma_materiali_ripetibili'` bound to the provided `metadata`, defining the schema for repetitive material data associated with TMA (Tavola dei Materiali Archeologici) records. The table includes a primary key `id`, a non-nullable foreign key `id_tma` referencing `tma_materiali_archeologici.id`, material description and component columns (`madi`, `macc`, `macl`, `macp`, `macd`, `cronologia_mac`, `macq`, `peso`), standard audit fields (`created_at`, `updated_at`, `created_by`, `updated_by`), and a UUID v4 persistent identifier column (`entity_uuid`). This is a class method that accepts `metadata` as its sole parameter and delegates table creation entirely to SQLAlchemy's `Table` constructor.

