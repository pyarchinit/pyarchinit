# modules/db/structures/Inventario_Lapidei_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Inventario_Lapidei_table

*No description available.*
Defines the SQLAlchemy table schema for `inventario_lapidei_table`, which stores inventory records of lapidary (stone) artifacts within the pyarchinit archaeological information system. The table captures descriptive, typological, and dimensional attributes of each artifact — including fields for site (`sito`), object type, material, numeric measurements (e.g., `toro`, `spessore`, `larghezza`, `lunghezza`, `h`), conservation state, chronology, and bibliography. A composite unique constraint (`ID_invlap_unico`) is enforced on the combination of `sito` and `scheda_numero` to prevent duplicate records per site and card number.

