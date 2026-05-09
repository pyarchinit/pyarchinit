# modules/db/structures_metadata/Presenze_table.py

## Overview

This file contains 3 documented elements.

## Classes

### Presenze_table

*No description available.*
Defines the SQLAlchemy table schema for personnel attendance records within an archaeological site management system. The class exposes a single class method, `define_table(cls, metadata)`, which constructs and returns a `Table` object named `'presenze_table'` containing columns for attendance identification (`id_presenza`), site name (`sito`), personnel reference (`id_personale`), date and time tracking (`data`, `ora_ingresso`, `ora_uscita`), hours worked (`ore_ordinarie`, `ore_straordinario`), shift and work area details (`tipo_giornata`, `turno`, `area_lavoro`), daily cost (`costo_giornata`), notes, and a StratiGraph UUID (`entity_uuid`). A `UniqueConstraint` named `'ID_presenza_unico'` enforces that no duplicate records exist for the same combination of site, personnel ID, date, and shift.

#### Methods

##### define_table(cls, metadata)

Defines and returns a SQLAlchemy `Table` object named `'presenze_table'` bound to the provided `metadata`, representing personnel attendance records. The table includes columns for a primary key (`id_presenza`), archaeological site (`sito`), personnel reference (`id_personale`), date (`data`), clock-in and clock-out times (`ora_ingresso`, `ora_uscita`), regular and overtime hours (`ore_ordinarie`, `ore_straordinario`), day type (`tipo_giornata`), shift (`turno`), work area (`area_lavoro`), notes (`note`), daily cost (`costo_giornata`), and a UUID-based persistent identifier (`entity_uuid`). A `UniqueConstraint` named `'ID_presenza_unico'` enforces that the combination of `sito`, `id_personale`, `data`, and `turno` is unique across all records.

