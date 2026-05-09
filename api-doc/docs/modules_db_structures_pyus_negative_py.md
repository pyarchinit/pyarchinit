# modules/db/structures/pyus_negative.py

## Overview

This file contains 2 documented elements.

## Classes

### pyus_negative

*No description available.*
Defines the SQLAlchemy table mapping for the `pyarchinit_us_negative_doc` database table, which stores negative stratigraphic unit documentation records. The table schema includes columns for site (`sito_n`), area (`area_n`), stratigraphic unit number (`us_n`), document type (`tipo_doc_n`), document name (`nome_doc_n`), and a `LINESTRING` geometry field (`the_geom`), with `gid` as the primary key and unique constraint. Table creation is intentionally deferred and not executed at module import time.

