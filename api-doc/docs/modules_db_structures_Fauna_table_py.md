# modules/db/structures/Fauna_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Fauna_table

*No description available.*
Defines the SQLAlchemy `Table` schema for `fauna_table`, which stores faunal remains data recorded during archaeological excavations. The table captures contextual, taphonomic, and osteological attributes of animal remains, including site and stratigraphic unit references, species identification, skeletal parts, combustion traces, and conservation state. A composite unique constraint (`ID_fauna_unico`) is enforced on the `sito`, `area`, `us`, and `id_fauna` columns to prevent duplicate faunal records.

