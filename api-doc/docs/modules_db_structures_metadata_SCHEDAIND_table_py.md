# modules/db/structures_metadata/SCHEDAIND_table.py

## Overview

This file contains 3 documented elements.

## Classes

### SCHEDAIND_table

*No description available.*
A SQLAlchemy table definition class representing individual archaeological records, mapped to the `individui_table` database table. It defines columns capturing identification, contextual, and physical attributes of skeletal individuals, including site and stratigraphic unit references, demographic estimates (sex, age range, age class), skeletal measurements, positional data, and a UUID-based persistent identifier. A unique constraint enforces that the combination of `sito` and `nr_individuo` remains distinct across all records.

#### Methods

##### define_table(cls, metadata)

*No description available.*
A class method that defines and returns a SQLAlchemy `Table` object named `'individui_table'` bound to the provided `metadata` instance. The table schema represents individual archaeological records and includes columns for site identification (`sito`, `area`, `us`), individual attributes (`sesso`, `eta_min`, `eta_max`, `classi_eta`), skeletal measurements and positional data (`lunghezza_scheletro`, `posizione_scheletro`, `posizione_cranio`, `posizione_arti_superiori`, `posizione_arti_inferiori`, `orientamento_asse`, `orientamento_azimut`), record metadata (`data_schedatura`, `schedatore`), and a StratiGraph UUID (`entity_uuid`). A `UniqueConstraint` named `'ID_individuo_unico'` enforces uniqueness on the combination of `sito` and `nr_individuo`.

