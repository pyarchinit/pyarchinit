# modules/db/structures/pyunitastratigrafiche_usm.py

## Overview

This file contains 2 documented elements.

## Classes

### pyunitastratigrafiche_usm

*No description available.*
Defines the SQLAlchemy table mapping for the `pyunitastratigrafiche_usm` database table, which stores stratigraphic unit (USM) records associated with archaeological excavations. The table schema includes fields for area, excavation site, stratigraphic unit identifiers, documentation metadata, and a `MULTIPOLYGON` geometry column (`the_geom`) managed via GeoAlchemy2. A unique constraint named `ID_us_unico_s` is applied to the `gid` primary key column.

