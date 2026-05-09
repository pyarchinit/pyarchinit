# modules/db/structures/Presenze_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Presenze_table

*No description available.*
Defines the SQLAlchemy table schema for `presenze_table`, which stores personnel attendance records within the pyarchinit database. The table captures per-entry data including site (`sito`), personnel identifier (`id_personale`), date, entry and exit times, ordinary and overtime hours, day type, shift, work area, notes, daily cost, and a UUID. A composite unique constraint named `ID_presenza_unico` enforces uniqueness across the combination of `sito`, `id_personale`, `data`, and `turno`.

