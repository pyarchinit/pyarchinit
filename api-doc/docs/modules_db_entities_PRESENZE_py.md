# modules/db/entities/PRESENZE.py

## Overview

This file contains 3 documented elements.

## Classes

### PRESENZE

*No description available.*
Represents a personnel attendance record, encapsulating a single work-day entry for a specific employee at a given site. Each instance stores attendance details including check-in and check-out times (`ora_ingresso`, `ora_uscita`), ordinary and overtime hours (`ore_ordinarie`, `ore_straordinario`), shift information (`turno`), work area, day type, notes, and daily cost. A unique identifier is automatically generated via `uuid.uuid4()` if no `entity_uuid` is provided at instantiation.

**Inherits from**: object

#### Methods

##### __init__(self, id_presenza, sito, id_personale, data, ora_ingresso, ora_uscita, ore_ordinarie, ore_straordinario, tipo_giornata, turno, area_lavoro, note, costo_giornata, entity_uuid)

## `__init__` — `PRESENZE`

Initializes a `PRESENZE` instance representing a personnel attendance record, assigning the provided values to the corresponding instance attributes: `id_presenza`, `sito`, `id_personale`, `data`, `ora_ingresso`, `ora_uscita`, `ore_ordinarie`, `ore_straordinario`, `tipo_giornata`, `turno`, `area_lavoro`, `note`, and `costo_giornata`. The optional `entity_uuid` parameter is assigned directly if supplied; otherwise, a new UUID4 string is automatically generated via `uuid.uuid4()` and assigned to `self.entity_uuid`.

##### __repr__(self)

*No description available.*
Returns an unambiguous string representation of the `PRESENZE` instance in the format `<PRESENZE('id_presenza','sito','id_personale','data')>`. The output string encodes the four identifying fields: `id_presenza` (integer), `sito` (string), `id_personale` (integer), and `data` (string). This method is intended for debugging and logging purposes, providing a concise snapshot of the key attributes that identify a presence record.

