# modules/db/structures/Pyarchinit_thesaurus_sigle.py

## Overview

This file contains 2 documented elements.

## Classes

### Pyarchinit_thesaurus_sigle

*No description available.*
Defines the SQLAlchemy table mapping for `pyarchinit_thesaurus_sigle`, a thesaurus lookup table that stores abbreviations (`sigla`) and their extended forms (`sigla_estesa`) organised by table name, typology, language, and hierarchical level. The table enforces three unique constraints: a primary key on `id_thesaurus_sigle`, a composite key on `(lingua, nome_tabella, tipologia_sigla, sigla_estesa)`, and a composite key on `(lingua, nome_tabella, tipologia_sigla, sigla)`. Table creation is intentionally deferred from module import time, with schema updates delegated to `pyarchinit_db_update.py`.

