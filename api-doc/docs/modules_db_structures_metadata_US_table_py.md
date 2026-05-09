# modules/db/structures_metadata/US_table.py

## Overview

This file contains 3 documented elements.

## Classes

### US_table

*No description available.*
Defines the SQLAlchemy table schema for stratigraphic units (*Unità Stratigrafiche* — US), used in archaeological data management. The class exposes a single `define_table` classmethod that constructs and returns a `Table` object bound to the provided `metadata`, comprising over 100 columns covering stratigraphic, interpretive, chronological, dimensional, masonry-specific (USM), and cataloging attributes. A unique constraint enforces the combination of `sito`, `area`, `us`, and `unita_tipo`, and an index on `order_layer` is created to optimize ordering and filtering queries.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object named `'us_table'` representing stratigraphic units (Unità Stratigrafiche) within an archaeological database, bound to the provided `metadata`. The table includes columns covering site identification, excavation context, stratigraphic classifications, chronological data, physical measurements, masonry unit attributes, and catalog references, with a composite unique constraint (`'ID_us_unico'`) enforced on the combination of `'sito'`, `'area'`, `'us'`, and `'unita_tipo'`. An index (`'idx_us_order_layer'`) is created on the `'order_layer'` column to optimize ordering and filtering queries.

