# modules/db/entities/BUDGET.py

## Overview

This file contains 3 documented elements.

## Classes

### BUDGET

## `BUDGET` Class

A data model class representing a budget record that encapsulates both planned and actual expenditure information for a given site and year. Each instance stores fields including `id_budget`, `sito`, `anno`, `categoria`, `descrizione`, `importo_previsto`, `importo_effettivo`, `data_registrazione`, `data_spesa`, `fornitore`, `numero_fattura`, and `note`. A unique identifier (`entity_uuid`) is automatically generated via `uuid.uuid4()` if one is not explicitly provided at instantiation.

**Inherits from**: object

#### Methods

##### __init__(self, id_budget, sito, anno, categoria, descrizione, importo_previsto, importo_effettivo, data_registrazione, data_spesa, fornitore, numero_fattura, note, entity_uuid)

## `__init__` — `BUDGET` Constructor

Initializes a `BUDGET` instance with twelve required positional parameters representing budget record fields: `id_budget`, `sito`, `anno`, `categoria`, `descrizione`, `importo_previsto`, `importo_effettivo`, `data_registrazione`, `data_spesa`, `fornitore`, `numero_fattura`, and `note`. Each parameter is assigned directly to the corresponding instance attribute. The optional `entity_uuid` parameter is assigned to `self.entity_uuid` if provided; otherwise, a new UUID4 string is automatically generated via `uuid.uuid4()`.

##### __repr__(self)

Returns an unambiguous string representation of the `BUDGET` instance in the format `<BUDGET('id_budget','sito','anno','categoria')>`. The output encodes the instance's `id_budget` (integer), `sito` (string), `anno` (integer), and `categoria` (string) fields, formatted via `%`-style interpolation.

