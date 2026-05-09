# modules/db/structures/Site_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Site_table

*No description available.*
Defines the SQLAlchemy table schema for the `site_table` database table, which stores archaeological site records. The table includes columns for site identification (`id_sito`, `sito`), geographic information (`nazione`, `regione`, `provincia`, `comune`), descriptive fields (`descrizione`, `definizione_sito`), a file path reference (`sito_path`), a find check flag (`find_check`), and a UUID (`entity_uuid`). A unique constraint named `ID_sito_unico` is enforced on the `sito` column to prevent duplicate site entries.

