# modules/db/structures_metadata/UT_table.py

## Overview

This file contains 3 documented elements.

## Classes

### UT_table

*No description available.*
Defines the SQLAlchemy table schema for topographic unit (UT) records used in archaeological survey contexts. The class exposes a single class method, `define_table`, which constructs and returns a `Table` object named `'ut_table'` bound to the provided `MetaData` instance, declaring 43 columns that capture spatial, administrative, descriptive, chronological, and bibliographic attributes of each UT record. A unique constraint (`ID_ut_unico`) is enforced on the combination of `progetto`, `nr_ut`, and `ut_letterale` to prevent duplicate entries across project, unit number, and literal representation.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object named `'ut_table'` bound to the provided `metadata`, representing topographic units (UT) records in archaeological contexts. The table schema includes 42 columns covering identification, geographic location, survey methodology, chronological periods, bibliography, and documentation fields, with `id_ut` as the integer primary key and a `UniqueConstraint` named `'ID_ut_unico'` enforcing uniqueness across the combination of `progetto`, `nr_ut`, and `ut_letterale`. This is a class method of `UT_table` that accepts a single `metadata` parameter and returns the constructed `Table` instance.

