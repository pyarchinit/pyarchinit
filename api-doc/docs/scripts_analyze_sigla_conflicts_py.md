# scripts/analyze_sigla_conflicts.py

## Overview

This file contains 4 documented elements.

## Functions

### analyze_postgres(host, port, dbname, user, password)

Analizza conflitti sigla in PostgreSQL.

**Parameters:**
- `host`
- `port`
- `dbname`
- `user`
- `password`

### fix_conflicts_postgres(host, port, dbname, user, password, method)

Risolve i conflitti secondo il metodo scelto.

**Parameters:**
- `host`
- `port`
- `dbname`
- `user`
- `password`
- `method`

### main()

*No description available.*
Entry point of the SIGLA conflict analysis and fix utility. It prompts the user for PostgreSQL connection parameters, then calls `analyze_postgres` to detect records sharing the same `SIGLA` value but differing `SIGLA_ESTESA` values. If conflicts are found, it presents three resolution options — keeping only the first record per sigla, making sigle unique by adding suffixes, or applying no changes — and delegates execution to `fix_conflicts_postgres` based on the user's choice, returning `0` on completion.

