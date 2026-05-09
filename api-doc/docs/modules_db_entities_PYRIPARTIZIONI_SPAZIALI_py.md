# modules/db/entities/PYRIPARTIZIONI_SPAZIALI.py

## Overview

This file contains 4 documented elements.

## Classes

### PYRIPARTIZIONI_SPAZIALI

*No description available.*
**Authors:** Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>

A data model class representing a spatial partition (*ripartizione spaziale*) record. It encapsulates the attributes `id`, `id_rs`, `sito_rs`, `tip_rip`, `descr_rs`, and `the_geom`, corresponding respectively to a unique identifier, a spatial partition reference identifier, a site reference, a partition type, a description, and a geometry field. The `__repr__` property returns a formatted string representation of all instance attributes.

**Inherits from**: object

#### Methods

##### __init__(self, id, id_rs, sito_rs, tip_rip, descr_rs, the_geom)

## `__init__` — `PYRIPARTIZIONI_SPAZIALI`

Initializes a new instance of the `PYRIPARTIZIONI_SPAZIALI` class by assigning the six provided arguments to their corresponding instance attributes. The parameters `id`, `id_rs`, `sito_rs`, `tip_rip`, `descr_rs`, and `the_geom` are stored directly on the instance without transformation or validation.

| Parameter | Assigned Attribute |
|---|---|
| `id` | `self.id` |
| `id_rs` | `self.id_rs` |
| `sito_rs` | `self.sito_rs` |
| `tip_rip` | `self.tip_rip` |
| `descr_rs` | `self.descr_rs` |
| `the_geom` | `self.the_geom` |

##### __repr__(self)

*No description available.*
**Type:** `property`

Returns a formatted string representation of a `PYRIPARTIZIONI_SPAZIALI` instance. The string follows the pattern `<PYRIPARTIZIONI_SPAZIALI('id','id_rs', 'sito_rs', 'tip_rip', 'descr_rs', 'the_geom')>`, interpolating the instance's corresponding attribute values. Implemented as a `property` rather than a standard method.

