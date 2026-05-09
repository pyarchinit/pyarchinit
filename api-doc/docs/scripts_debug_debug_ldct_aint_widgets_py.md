# scripts/debug/debug_ldct_aint_widgets.py

## Overview

This file contains 2 documented elements.

## Functions

### debug_widgets()

*No description available.*
Connects to a hardcoded SQLite database at `/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite` and queries the `pyarchinit_thesaurus_sigle` table to inspect thesaurus entries for the `TMA materiali archeologici` table, specifically for typology codes `10.2` (Tipologia Collocazione / `ldct`) and `10.6` (Tipologia Acquisizione / `aint`). It prints the retrieved `sigla`, `sigla_estesa`, and `lingua` values for each code, along with a count of distinct languages used across both codes. Additionally, it performs a case-sensitivity check on the `lingua` field by querying for the variants `'it'`, `'IT'`, `'It'`, and `'iT'`, printing the result count for each. If the database file does not exist, the function prints an error message and returns early.

