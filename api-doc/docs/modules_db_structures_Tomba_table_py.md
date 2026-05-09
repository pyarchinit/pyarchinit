# modules/db/structures/Tomba_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Tomba_table

*No description available.*
Defines the SQLAlchemy table schema for `tomba_table`, which stores archaeological burial (tomb) records within the pyarchinit system. The table includes columns for site identification (`sito`, `area`), structural references (`sigla_struttura`, `nr_struttura`), burial attributes (`rito`, `tipo_deposizione`, `tipo_sepoltura`), grave goods (`corredo_presenza`, `corredo_tipo`, `corredo_descrizione`), chronological data (`periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`), and a unique identifier (`entity_uuid`). A composite unique constraint (`ID_tomba_unico`) is enforced on the combination of `sito` and `nr_scheda_taf` to prevent duplicate burial record entries per site.

