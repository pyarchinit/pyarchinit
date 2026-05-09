# modules/db/structures/US_table_toimp.py

## Overview

This file contains 2 documented elements.

## Classes

### US_table_toimp

*No description available.*
Defines the SQLAlchemy table schema for `us_table_toimp`, a staging or import-target table used to hold stratigraphic unit (US) records prior to or during import operations. The table contains columns covering site identification (`sito`, `area`, `us`), stratigraphic and interpretive descriptions, chronological phasing, excavation metadata, and physical attributes such as colour, consistency, and structure. A composite unique constraint named `ID_us_unico_toimp` is enforced on the combination of `sito`, `area`, and `us` to prevent duplicate records.

