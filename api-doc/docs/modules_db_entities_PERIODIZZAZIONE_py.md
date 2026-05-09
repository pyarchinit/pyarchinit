# modules/db/entities/PERIODIZZAZIONE.py

## Overview

This file contains 4 documented elements.

## Classes

### PERIODIZZAZIONE

*No description available.*
A data class representing an archaeological periodization record, encapsulating the chronological and phase-based classification of a site. Each instance stores identifying information (`id_perfas`, `sito`), period and phase designations (`periodo`, `fase`), chronological boundaries (`cron_iniziale`, `cron_finale`), descriptive fields (`descrizione`, `datazione_estesa`), a period counter (`cont_per`), and an automatically generated UUID (`entity_uuid`) if one is not explicitly provided. The `__repr__` method returns a formatted string representation of the core fields, excluding `entity_uuid`.

**Inherits from**: object

#### Methods

##### __init__(self, id_perfas, sito, periodo, fase, cron_iniziale, cron_finale, descrizione, datazione_estesa, cont_per, entity_uuid)

Initializes a new instance of the `PERIODIZZAZIONE` class, assigning the provided arguments to their corresponding instance attributes. Accepts parameters representing a periodization record, including `id_perfas`, `sito`, `periodo`, `fase`, `cron_iniziale`, `cron_finale`, `descrizione`, `datazione_estesa`, and `cont_per`. The optional `entity_uuid` parameter is assigned directly if provided; otherwise, a new UUID4 string is automatically generated and assigned.

##### __repr__(self)

Returns the official string representation of a `PERIODIZZAZIONE` instance.

The returned string follows the format `<PERIODIZZAZIONE('id_perfas', 'sito', 'periodo', 'fase', 'cron_iniziale', 'cron_finale', 'descrizione', 'datazione_estesa', 'cont_per')>`, embedding the nine corresponding field values in order. This representation is intended for unambiguous identification of the object, typically used in debugging and logging contexts.

