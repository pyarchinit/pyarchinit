# modules/db/structures/Pottery_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Pottery_table

*No description available.*
Defines the SQLAlchemy table schema for `pottery_table`, which stores archaeological pottery records within a pyArchInit database. The table captures a comprehensive set of attributes per pottery find, including site context fields (`sito`, `area`, `us`), physical characteristics (`fabric`, `material`, `form`, `ware`, `munsell`), decorative details (`exdeco`, `intdeco`, `descrip_ex_deco`, `descrip_in_deco`, `decoration_type`, `decoration_motif`, `decoration_position`), dimensional measurements stored as `Numeric(7,3)` (`diametro_max`, `diametro_rim`, `diametro_bottom`, `diametro_height`, `diametro_preserved`), and a composite unique constraint on `('sito', 'id_number')` named `ID_rep_unico`. Table creation is intentionally deferred and not executed at module import time.

