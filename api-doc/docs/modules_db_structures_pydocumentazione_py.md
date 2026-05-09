# modules/db/structures/pydocumentazione.py

## Overview

This file contains 2 documented elements.

## Classes

### pydocumentazione

*No description available.*
A data-mapping class that defines the SQLAlchemy table structure for `pyarchinit_documentazione`, a database table used to store documentation records within the pyArchInit system. The class declares a `Table` object with columns for a primary key (`gid`), site name (`sito`), document name (`nome_doc`), document type (`tipo_doc`), a QGIS project path (`path_qgis_pj`), and a `LINESTRING` geometry field (`the_geom`), along with a unique constraint on `gid`. Table creation is intentionally deferred and not triggered at module import time.

