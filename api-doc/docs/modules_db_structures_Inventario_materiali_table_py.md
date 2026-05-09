# modules/db/structures/Inventario_materiali_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Inventario_materiali_table

*No description available.*
Defines the SQLAlchemy table schema for `inventario_materiali_table`, which stores archaeological material inventory records. Each record captures detailed attributes of a recovered artefact, including site (`sito`), inventory number (`numero_inventario`), optional sub-inventory suffix (`sub_inv`), typological and descriptive fields, conservation state, physical measurements, and associated media references. A composite unique constraint (`ID_invmat_unico`) is enforced on the combination of `sito`, `numero_inventario`, and `sub_inv` to prevent duplicate inventory entries.

