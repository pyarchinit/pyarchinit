# modules/db/structures/Struttura_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Struttura_table

*No description available.*
Defines the SQLAlchemy table schema for `struttura_table`, which stores archaeological structure records within the pyarchinit system. The table captures a comprehensive set of attributes for each structure, including identification fields (`id_struttura`, `sito`, `sigla_struttura`, `numero_struttura`), classification fields (`categoria_struttura`, `tipologia_struttura`, `definizione_struttura`), chronological data (`periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`), and extended descriptive fields such as conservation state, topographic relations, decorative motifs, and functional phases — several of which store serialized JSON data. A composite unique constraint (`ID_struttura_unico`) is enforced on the combination of `sito`, `sigla_struttura`, and `numero_struttura` to prevent duplicate structure entries.

