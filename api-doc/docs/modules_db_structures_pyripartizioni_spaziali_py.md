# modules/db/structures/pyripartizioni_spaziali.py

## Overview

This file contains 2 documented elements.

## Classes

### pyripartizioni_spaziali

*No description available.*
A data model class that defines the database schema for the `pyarchinit_ripartizioni_spaziali` table using SQLAlchemy's `MetaData` and `Table` constructs. The table contains columns for a primary key (`gid`), spatial partition identifier (`id_rs`), site name (`sito_rs`), partition type (`tip_rip`), description (`descr_rs`), and a polygon geometry field (`the_geom`), along with a unique constraint on `gid`. Table creation is not executed at import time; schema application to the database must be handled explicitly elsewhere.

