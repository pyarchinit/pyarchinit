# scripts/fixes/fix_tma_foreign_key.py

## Overview

This file contains 2 documented elements.

## Functions

### fix_foreign_key()

*No description available.*
Repairs the foreign key constraint on the `tma_materiali_ripetibili` table in the SQLite database located at the default path by rebuilding the table with the correct `FOREIGN KEY (id_tma) REFERENCES tma_materiali_archeologici(id) ON DELETE CASCADE` definition. The function backs up all existing records, drops any associated triggers, replaces the original table with a correctly structured temporary table, restores the data and triggers, then commits the changes. If the database file is not found, either of the two required tables is missing, or any step fails, the function prints a diagnostic message and rolls back all changes before closing the connection.

