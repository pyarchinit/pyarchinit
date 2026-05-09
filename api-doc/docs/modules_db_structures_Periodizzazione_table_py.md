# modules/db/structures/Periodizzazione_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Periodizzazione_table

*No description available.*
Defines the SQLAlchemy table schema for `periodizzazione_table`, which stores archaeological periodization records associating sites (`sito`) with chronological periods (`periodo`), phases (`fase`), and date ranges (`cron_iniziale`, `cron_finale`). The table uses `id_perfas` as its integer primary key and enforces a composite unique constraint on the combination of `sito`, `periodo`, and `fase` (named `ID_perfas_unico`). Table creation is intentionally deferred and not executed at module import time.

