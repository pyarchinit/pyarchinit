# modules/db/entities/ATTREZZATURE.py

## Overview

This file contains 3 documented elements.

## Classes

### ATTREZZATURE

*No description available.*
Represents an equipment (attrezzatura) record, encapsulating all attributes associated with a single piece of equipment tracked within a site. The class stores identifying and descriptive fields — including inventory code, name, category, brand, model, and serial number — alongside ownership, financial (purchase cost, daily rental cost), assignment, maintenance scheduling, and status information. Each instance is assigned a unique identifier via `entity_uuid`, which defaults to a newly generated UUID v4 if not explicitly provided.

**Inherits from**: object

#### Methods

##### __init__(self, id_attrezzatura, sito, codice_inventario, nome, categoria, marca, modello, numero_serie, proprieta, data_acquisto, costo_acquisto, costo_noleggio_giorno, stato, assegnato_a, data_ultima_manutenzione, data_prossima_manutenzione, note, entity_uuid)

## `__init__` — `ATTREZZATURE`

Initializes an `ATTREZZATURE` instance representing a piece of equipment, assigning the provided values to the corresponding instance attributes: `id_attrezzatura`, `sito`, `codice_inventario`, `nome`, `categoria`, `marca`, `modello`, `numero_serie`, `proprieta`, `data_acquisto`, `costo_acquisto`, `costo_noleggio_giorno`, `stato`, `assegnato_a`, `data_ultima_manutenzione`, `data_prossima_manutenzione`, and `note`. The optional `entity_uuid` parameter is assigned to `self.entity_uuid`; if not provided or evaluates to a falsy value, a new UUID4 string is automatically generated via `uuid.uuid4()`.

##### __repr__(self)

*No description available.*
Returns an unambiguous string representation of the `ATTREZZATURE` instance in the format `<ATTREZZATURE('id_attrezzatura','sito','codice_inventario','nome')>`. The output combines the `id_attrezzatura` (formatted as an integer), `sito`, `codice_inventario`, and `nome` fields into a single descriptive string. This method is intended for debugging and logging purposes.

