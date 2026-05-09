# modules/db/structures/pyquote_usm.py

## Overview

This file contains 2 documented elements.

## Classes

### pyquote_usm

*No description available.*
A SQLAlchemy-based data model class that defines the schema for the `pyarchinit_quote_usm` database table, which stores elevation quota measurements associated with stratigraphic units (USM). The table schema includes fields for site identification (`sito_q`), area and unit references (`area_q`, `us_q`), measurement unit (`unita_misu_q`), quota value (`quota_q`), surveyor metadata, and a PostGIS `POINT` geometry column (`the_geom`) for spatial representation. A unique constraint is applied to the primary key column `gid`, and table creation is intentionally deferred from module import time to avoid connection errors.

