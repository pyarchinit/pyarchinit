# modules/db/structures/SCHEDAIND_table.py

## Overview

This file contains 2 documented elements.

## Classes

### SCHEDAIND_table

*No description available.*
Defines the SQLAlchemy table metadata for `individui_table`, which stores individual skeletal record data used in archaeological excavation documentation. The table schema includes columns for site identification (`sito`, `area`, `us`), individual attributes (`sesso`, `eta_min`, `eta_max`, `classi_eta`), skeletal condition flags (`completo_si_no`, `disturbato_si_no`, `in_connessione_si_no`), positional measurements, and a UUID field for entity tracking. A composite unique constraint (`ID_individuo_unico`) is enforced on the `sito` and `nr_individuo` columns to prevent duplicate individual records per site; table creation is intentionally deferred and not triggered at module import time.

