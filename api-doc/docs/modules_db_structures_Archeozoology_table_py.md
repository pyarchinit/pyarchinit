# modules/db/structures/Archeozoology_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Archeozoology_table

*No description available.*
Defines the SQLAlchemy schema for the `archeozoology_table` database table, which stores archaeozoological find records associated with archaeological sites. Each record captures spatial context (site, area, stratigraphic unit, quadrant, and 3D coordinates) alongside counts of identified faunal taxa and bone modification attributes (e.g., `calcinati`, `combusto`, `strie`). A composite unique constraint (`ID_archzoo_unico`) is enforced on the `sito` and `quadrato` columns to prevent duplicate entries for the same site–quadrant combination.

