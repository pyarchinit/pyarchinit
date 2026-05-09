# modules/db/structures/Documentazione_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Documentazione_table

*No description available.*
Defines the SQLAlchemy table schema for `documentazione_table`, which stores documentation records associated with archaeological sites. Each record captures metadata about a document, including its site (`sito`), name (`nome_doc`), date (`data`), type (`tipo_documentazione`), source (`sorgente`), scale (`scala`), drafter (`disegnatore`), notes (`note`), and a UUID (`entity_uuid`). A composite unique constraint named `ID_invdoc_unico` is enforced on the combination of `sito`, `tipo_documentazione`, and `nome_doc` to prevent duplicate documentation entries.

