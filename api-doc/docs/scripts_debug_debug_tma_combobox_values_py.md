# scripts/debug/debug_tma_combobox_values.py

## Overview

This file contains 2 documented elements.

## Functions

### debug_thesaurus_values()

*No description available.*
Connects to a hardcoded SQLite database at `/Users/enzo/pyarchinit/pyarchinit_DB_folder/pyarchinitdddd.sqlite` and queries the `pyarchinit_thesaurus_sigle` table to inspect thesaurus entries for two predefined category groups: `'TMA materiali archeologici'` and `'TMA materiali ripetibili'`. For each mapped typology code within those groups, it prints up to ten matching records (`sigla`, `sigla_estesa`, `lingua`) and, when no records are found, searches for alternative table names containing `'TMA'` that share the same typology code. At the end, it prints a summary listing every code/table combination for which no thesaurus values exist, indicating which combobox entries will be non-functional.

