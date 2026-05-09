# modules/db/structures/Computo_metrico_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Computo_metrico_table

*No description available.*
Defines the SQLAlchemy table schema for `computo_metrico_table`, which stores metric computation records associated with archaeological excavation sites. Each record captures spatial and volumetric calculation data, including pre- and post-intervention DEMs, polygon layer references, area (m²), volume (m³), elevation bounds, excavation phase, calculation date, and notes. The class uses a shared `MetaData` instance and relies on the `Connection` module from `pyarchinit_conn_strings` for database connectivity.

