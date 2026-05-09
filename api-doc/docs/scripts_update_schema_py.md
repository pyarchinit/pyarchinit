# scripts/update_schema.py

## Overview

This file contains 6 documented elements.

## Functions

### update_us_fields(content)

Update US fields from BIGINT to TEXT

**Parameters:**
- `content`

### add_tma_table(content)

Add TMA table definition

**Parameters:**
- `content`

### verify_inventario_materiali(content)

Verify and update inventario_materiali table structure

**Parameters:**
- `content`

### add_constraints_and_indexes(content)

Add constraints and indexes for updated schema

**Parameters:**
- `content`

### main()

Reads a SQL schema file from a hardcoded path, applies a series of schema transformations via `update_us_fields`, `add_tma_table`, `verify_inventario_materiali`, and `add_constraints_and_indexes`, then writes the modified content to a separate output file. The function prints progress messages and a summary of the key changes applied, including the conversion of US fields from `BIGINT` to `TEXT`, the addition of the `tma_materiali_archeologici` table, and verification of the `inventario_materiali` table structure. It serves as the entry point for the script when executed directly.

