# modules/db/structures/pyunitastratigrafiche.py

## Overview

This file contains 2 documented elements.

## Classes

### pyunitastratigrafiche

*No description available.*
A data model class that defines the database table schema for stratigraphic units (`pyunitastratigrafiche`) using SQLAlchemy's `MetaData` and `Table` constructs. The table stores archaeological stratigraphic unit records, including fields for area, excavation site, unit identifiers, stratigraphic index, documentation metadata, and a `MULTIPOLYGON` geometry column (`the_geom`) managed via GeoAlchemy2. A unique constraint is enforced on the `gid` primary key column under the name `ID_us_unico_s`.

