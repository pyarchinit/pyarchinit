# modules/db/entities/PYSITO_POINT.py

## Overview

This file contains 4 documented elements.

## Classes

### PYSITO_POINT

*No description available.*
A data class representing a geographic site as a point geometry. It stores three attributes — `gid` (a numeric identifier), `sito_nome` (the site name), and `the_geom` (the point geometry) — assigned directly during instantiation. The `__repr__` property returns a formatted string representation combining all three fields.

**Inherits from**: object

#### Methods

##### __init__(self, gid, sito_nome, the_geom)

## `__init__` — `PYSITO_POINT`

Initializes a new instance of the `PYSITO_POINT` class with the provided spatial point data. Accepts three parameters — `gid`, `sito_nome`, and `the_geom` — and assigns each to the corresponding instance attributes `self.gid`, `self.sito_nome`, and `self.the_geom`. These attributes represent a numeric identifier, a site name, and a geometry object respectively.

##### __repr__(self)

*No description available.*
A property that returns the official string representation of a `PYSITO_POINT` instance. The returned string follows the format `<PYSITO_POINT('gid','sito_nome', 'the_geom')>`, embedding the instance's `gid`, `sito_nome`, and `the_geom` attribute values. Note that this method is implemented as a `@property` rather than a standard method.

