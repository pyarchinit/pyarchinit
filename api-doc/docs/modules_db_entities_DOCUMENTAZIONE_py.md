# modules/db/entities/DOCUMENTAZIONE.py

## Overview

This file contains 4 documented elements.

## Classes

### DOCUMENTAZIONE

*No description available.*
Represents a documentation record associated with an archaeological or survey site, encapsulating metadata about a single document entry. The class stores nine core attributes — `id_documentazione`, `sito`, `nome_doc`, `data`, `tipo_documentazione`, `sorgente`, `scala`, `disegnatore`, and `note` — along with an optional `entity_uuid` that defaults to a newly generated UUID v4 if not provided. The `__repr__` method returns a formatted string representation of the first nine fields, excluding `entity_uuid`.

**Inherits from**: object

#### Methods

##### __init__(self, id_documentazione, sito, nome_doc, data, tipo_documentazione, sorgente, scala, disegnatore, note, entity_uuid)

## `__init__` — `DOCUMENTAZIONE`

Initializes a new instance of the `DOCUMENTAZIONE` class, assigning the provided arguments to their corresponding instance attributes: `id_documentazione`, `sito`, `nome_doc`, `data`, `tipo_documentazione`, `sorgente`, `scala`, `disegnatore`, and `note`. The optional `entity_uuid` parameter is assigned directly if supplied; otherwise, a new UUID4 string is generated automatically via `uuid.uuid4()` and assigned to `self.entity_uuid`.

**Parameters:**

| Parameter | Position | Optional |
|---|---|---|
| `id_documentazione` | 0 | No |
| `sito` | 1 | No |
| `nome_doc` | 2 | No |
| `data` | 3 | No |
| `tipo_documentazione` | 4 | No |
| `sorgente` | 5 | No |
| `scala` | 6 | No |
| `disegnatore` | 7 | No |
| `note` | 8 | No |
| `entity_uuid` | — | Yes (default: `None`) |

##### __repr__(self)

Returns a string representation of a `DOCUMENTAZIONE` instance in a structured format.

The output string follows the pattern `<DOCUMENTAZIONE('id', 'sito', 'nome_doc', 'data', 'tipo_documentazione', 'sorgente', 'scala', 'disegnatore', 'note')>`, embedding the values of nine instance attributes: `id_documentazione`, `sito`, `nome_doc`, `data`, `tipo_documentazione`, `sorgente`, `scala`, `disegnatore`, and `note`. `id_documentazione` is formatted as an integer (`%d`), while the remaining eight fields are formatted as strings (`%s`).

