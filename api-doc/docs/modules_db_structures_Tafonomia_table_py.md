# modules/db/structures/Tafonomia_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Tomba_table

*No description available.*
Defines the SQLAlchemy table schema for `tomba_table`, which stores archaeological burial (tomb) records within the pyArchInit system. The table captures a comprehensive set of burial attributes, including site identification (`sito`), burial rite, skeletal position and condition, grave goods, stratigraphic references, chronological phasing, and structural details. A composite unique constraint (`ID_tomba_unico`) is enforced on the `sito` and `nr_scheda_taf` columns to prevent duplicate burial card entries per site.

