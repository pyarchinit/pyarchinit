# modules/db/structures/pyquote.py

## Overview

This file contains 2 documented elements.

## Classes

### pyquote

*No description available.*
A SQLAlchemy table-mapping class that defines the schema for the `pyarchinit_quote` database table, which stores elevation/quota survey data associated with archaeological units. The class declares a `Table` object with columns representing site identifiers, area and stratigraphic unit references, measurement units, quota values, survey metadata (date, drafter, original survey reference), and a PostGIS `POINT` geometry column via GeoAlchemy2. Table creation is intentionally deferred from module import time to avoid premature database connection errors.

