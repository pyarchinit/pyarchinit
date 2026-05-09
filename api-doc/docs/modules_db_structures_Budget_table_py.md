# modules/db/structures/Budget_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Budget_table

*No description available.*
Defines the SQLAlchemy table schema for the `budget_table` database table, which stores budget and expenditure records associated with archaeological sites. The table captures financial data including planned and actual amounts (`importo_previsto`, `importo_effettivo`), supplier and invoice details, categorisation fields, and date information for both registration and expenditure events. It relies on a shared `MetaData` instance and the `Connection` class from `modules.db.pyarchinit_conn_strings`, and explicitly defers table creation to avoid execution at module import time.

