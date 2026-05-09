# modules/db/structures/pyindividui.py

## Overview

This file contains 2 documented elements.

## Classes

### pyindividui

*No description available.*
A data-access class that defines the SQLAlchemy table mapping for the `pyarchinit_individui` database table. It declares a `Table` object with columns for a primary key (`gid`), site identifier (`sito`), structure code (`sigla_struttura`), notes (`note`), individual identifier (`id_individuo`), and a point geometry field (`the_geom`), along with a unique constraint on `gid`. Database connectivity is managed via the `Connection` class imported from `modules.db.pyarchinit_conn_strings`.

