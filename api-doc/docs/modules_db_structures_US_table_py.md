# modules/db/structures/US_table.py

## Overview

This file contains 2 documented elements.

## Classes

### US_table

*No description available.*
Defines the SQLAlchemy table schema for `us_table`, which stores stratigraphic unit (US/USM) records used in archaeological excavation documentation. The table encompasses a comprehensive set of fields covering stratigraphic, interpretive, physical, dimensional, and administrative data for each unit, including extended columns for masonry units (USM) and ICCD catalogue alignment. A composite unique constraint enforces uniqueness across `sito`, `area`, `us`, and `unita_tipo`, and an index on `order_layer` is defined to optimize ordering and filtering queries.

