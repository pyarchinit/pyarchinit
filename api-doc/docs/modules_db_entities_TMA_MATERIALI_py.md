# modules/db/entities/TMA_MATERIALI.py

## Overview

This file contains 4 documented elements.

## Classes

### TMA_MATERIALI

*No description available.*
A data model class representing a material record associated with a TMA entity. It stores material attributes including identifiers (`id`, `id_tma`), material classification fields (`madi`, `macc`, `macl`, `macp`, `macd`, `macq`), chronological data (`cronologia_mac`), weight (`peso`), and audit metadata (`created_at`, `updated_at`, `created_by`, `updated_by`). Each instance is assigned a unique identifier via `entity_uuid`, which defaults to a newly generated UUID v4 if not explicitly provided.

**Inherits from**: object

#### Methods

##### __init__(self, id, id_tma, madi, macc, macl, macp, macd, cronologia_mac, macq, peso, created_at, updated_at, created_by, updated_by, entity_uuid)

## `__init__` — `TMA_MATERIALI`

Initializes a new instance of the `TMA_MATERIALI` class, assigning the provided arguments to their corresponding instance attributes. Accepts fourteen required parameters (`id`, `id_tma`, `madi`, `macc`, `macl`, `macp`, `macd`, `cronologia_mac`, `macq`, `peso`, `created_at`, `updated_at`, `created_by`, `updated_by`) and one optional parameter (`entity_uuid`). If `entity_uuid` is not supplied or evaluates to a falsy value, a new UUID4 string is automatically generated and assigned to `self.entity_uuid`.

##### __repr__(self)

Returns the official string representation of a `TMA_MATERIALI` instance. The output is a formatted string containing the fields `id`, `id_tma`, `madi`, `macc`, `macl`, `macp`, `macd`, `cronologia_mac`, `macq`, and `peso`, enclosed in angle brackets and prefixed with the class name. The `id` and `id_tma` fields are formatted as integers, `peso` as a float, and the remaining fields as strings.

