# modules/db/entities/PYSITO_POLYGON.py

## Overview

This file contains 4 documented elements.

## Classes

### PYSITO_POLYGON

*No description available.*
A data class representing a polygon geometry associated with an archaeological or geographic site record. It encapsulates three attributes: a primary key identifier (`pkuid`), a site identifier (`sito_id`), and a geometry object (`the_geom`). The `__repr__` property returns a formatted string representation displaying all three field values.

**Inherits from**: object

#### Methods

##### __init__(self, pkuid, sito_id, the_geom)

## `__init__` — `PYSITO_POLYGON`

Initializes a new instance of the `PYSITO_POLYGON` class with the three provided arguments. Assigns `pkuid`, `sito_id`, and `the_geom` to the corresponding instance attributes `self.pkuid`, `self.sito_id`, and `self.the_geom`, respectively.

**Signature:**
```python
def __init__(self, pkuid, sito_id, the_geom)
```

| Parameter | Description |
|-----------|-------------|
| `pkuid` | Primary key identifier for the polygon record. |
| `sito_id` | Identifier associating the polygon with a site. |
| `the_geom` | Geometry data representing the polygon. |

##### __repr__(self)

*No description available.*
A property that returns the official string representation of a `PYSITO_POLYGON` instance. The returned string follows the format `<PYSITO_POLYGON('pkuid','sito_id', 'the_geom')>`, embedding the instance's `pkuid` (formatted as an integer), `sito_id`, and `the_geom` values. Note that `__repr__` is implemented as a `@property` rather than a standard method.

