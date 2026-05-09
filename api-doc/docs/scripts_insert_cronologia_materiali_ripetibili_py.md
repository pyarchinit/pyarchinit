# scripts/insert_cronologia_materiali_ripetibili.py

## Overview

This file contains 2 documented elements.

## Functions

### insert_cronologia_values()

*No description available.*
Connects to a hardcoded SQLite database at `/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite` and copies chronology records (`tipologia_sigla = '10.4'`) from the `pyarchinit_thesaurus_sigle` table where `nome_tabella` equals `'TMA materiali archeologici'` into the same table under `nome_tabella = 'TMA materiali ripetibili'`. After insertion, the function verifies the operation by querying the count of copied records and printing up to ten examples of the inserted `sigla`/`sigla_estesa` pairs. If the database file does not exist or an `sqlite3.Error` is raised, the function prints a diagnostic message and, in the error case, rolls back the transaction before closing the connection.

