# modules/db/structures/Campioni_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Campioni_table

*No description available.*
Defines the SQLAlchemy table schema for `campioni_table`, which stores sample (`campioni`) records within the pyarchinit database. The table includes columns for sample identification (`id_campione`, `nr_campione`), site and contextual information (`sito`, `area`, `us`), sample metadata (`tipo_campione`, `descrizione`), inventory and storage details (`numero_inventario_materiale`, `nr_cassa`, `luogo_conservazione`), and a UUID reference (`entity_uuid`). A composite unique constraint named `ID_invcamp_unico` is enforced on the combination of `sito` and `nr_campione` to prevent duplicate sample entries per site.

