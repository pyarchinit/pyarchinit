# modules/db/structures/Personale_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Personale_table

*No description available.*
Defines the SQLAlchemy table metadata for the `personale_table` database table, which stores personnel records associated with archaeological sites. The table schema includes columns for personal details (`nome`, `cognome`, `data_nascita`, `codice_fiscale`, `indirizzo`, `email`, `telefono`), employment information (`ruolo`, `qualifica`, `tipo_contratto`, `data_inizio_contratto`, `data_fine_contratto`, `tariffa_oraria`, `tariffa_giornaliera`, `iban`), and administrative fields (`sito`, `attivo`, `note`, `entity_uuid`). A composite unique constraint (`ID_personale_unico`) is enforced on the combination of `sito` and `codice_fiscale` to prevent duplicate personnel entries per site.

