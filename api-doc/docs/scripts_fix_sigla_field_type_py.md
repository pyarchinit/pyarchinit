# scripts/fix_sigla_field_type.py

## Overview

This file contains 3 documented elements.

## Functions

### fix_sigla_field(host, port, dbname, user, password)

Sistema il tipo del campo sigla e rimuove gli spazi.

**Parameters:**
- `host`
- `port`
- `dbname`
- `user`
- `password`

### main()

*No description available.*
Entry point for the *FIX CAMPO SIGLA THESAURUS* script. Displays a summary of the three operations to be performed — removing excess whitespace from all fields, converting the `sigla` column from `CHAR(255)` to `VARCHAR(100)`, and removing any duplicates created after cleanup — then prompts the user interactively for PostgreSQL connection parameters (`host`, `port`, `dbname`, `user`, `password`). Delegates execution to `fix_sigla_field()` and returns `0` on success or `1` on failure, intended to be passed directly to `sys.exit()`.

