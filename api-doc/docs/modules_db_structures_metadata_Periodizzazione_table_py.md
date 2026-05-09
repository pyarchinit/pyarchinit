# modules/db/structures_metadata/Periodizzazione_table.py

## Overview

This file contains 3 documented elements.

## Classes

### Periodizzazione_table

*No description available.*
Defines the SQLAlchemy table schema for storing archaeological periodization records, mapping stratigraphic periods and phases to their corresponding chronological and descriptive data. The class exposes a single class method, `define_table`, which constructs and returns a `Table` object bound to the provided `metadata`, comprising columns for site name, period number, phase, initial and final chronological dates, description, extended dating information, a period context reference, and a UUID-based persistent identifier. A unique constraint (`ID_perfas_unico`) enforces that the combination of `sito`, `periodo`, and `fase` is unique across all records.

#### Methods

##### define_table(cls, metadata)

*No description available.*
A class method that defines and returns a SQLAlchemy `Table` object named `'periodizzazione_table'` bound to the provided `metadata`. The table schema includes columns for a primary key (`id_perfas`), archaeological site name (`sito`), period number (`periodo`), phase (`fase`), initial and final chronological dates (`cron_iniziale`, `cron_finale`), a textual description, extended dating information (`datazione_estesa`), a period context reference (`cont_per`), and a StratiGraph UUID (`entity_uuid`). A `UniqueConstraint` named `'ID_perfas_unico'` enforces uniqueness across the combination of `sito`, `periodo`, and `fase`.

