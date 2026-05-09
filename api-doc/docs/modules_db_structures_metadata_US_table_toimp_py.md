# modules/db/structures_metadata/US_table_toimp.py

## Overview

This file contains 2 documented elements.

## Classes

### US_table_toimp

*No description available.*
Defines the SQLAlchemy table schema for a temporary import staging table named `us_table_toimp`, used to hold Stratigraphic Unit (US) records prior to import into the main database. The table includes columns covering site identification (`sito`, `area`, `us`), stratigraphic and interpretive descriptions, chronological phasing, excavation metadata, and physical attributes such as colour, consistency, and structure. A composite unique constraint (`ID_us_unico_toimp`) is enforced on the combination of `sito`, `area`, and `us` columns to prevent duplicate entries during the import process.

