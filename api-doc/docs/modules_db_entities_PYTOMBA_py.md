# modules/db/entities/PYTOMBA.py

## Overview

This file contains 4 documented elements.

## Classes

### PYTOMBA

*No description available.*
**Authors:** Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>

`PYTOMBA` is a plain Python object representing a tomb record, encapsulating the fields `id`, `sito`, `nr_scheda`, and `the_geom`. It is initialized with these four parameters, which are stored as instance attributes. The class defines a `__repr__` property that returns a formatted string representation of the instance in the form `<PYTOMBA('id','sito', 'nr_scheda', 'the_geom')>`.

**Inherits from**: object

#### Methods

##### __init__(self, id, sito, nr_scheda, the_geom)

## `__init__` Method

Initializes a new instance of the `PYTOMBA` class with the provided parameters. Assigns the four arguments directly to the corresponding instance attributes: `id`, `sito`, `nr_scheda`, and `the_geom`.

**Signature:**
```python
def __init__(self, id, sito, nr_scheda, the_geom)
```

**Parameters:**

| Parameter | Description |
|-----------|-------------|
| `id` | Unique identifier for the instance. |
| `sito` | Site associated with the record. |
| `nr_scheda` | Card or record number. |
| `the_geom` | Geometric data associated with the record. |

##### __repr__(self)

*No description available.*
A property that returns the official string representation of a `PYTOMBA` instance. The returned string follows the format `<PYTOMBA('id','sito', 'nr_scheda', 'the_geom')>`, interpolating the instance's `id`, `sito`, `nr_scheda`, and `the_geom` fields. Note that this is implemented as a `@property` rather than a standard method.

