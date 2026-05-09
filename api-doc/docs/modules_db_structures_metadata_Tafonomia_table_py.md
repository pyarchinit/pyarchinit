# modules/db/structures_metadata/Tafonomia_table.py

## Overview

This file contains 2 documented elements.

## Classes

### Tomba_table

*No description available.*
Defines the SQLAlchemy table schema for `tomba_table`, which stores archaeological burial (tomb) records within the pyarchinit system. The table captures a comprehensive set of burial attributes, including site identification (`sito`), burial rite, skeletal position and condition, stratigraphic references, grave goods, structural details, chronological phasing, and spatial measurements. A composite unique constraint (`ID_tomba_unico`) is enforced on the `sito` and `nr_scheda_taf` columns to prevent duplicate burial card entries per site.

