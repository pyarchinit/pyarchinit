# modules/db/entities/PYREPERTI.py

## Overview

This file contains 4 documented elements.

## Classes

### PYREPERTI

*No description available.*
**Authors:** Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>

A data model class representing a finds/artefacts record (`reperti` in Italian), encapsulating spatial and relational attributes for a single entry. It stores five fields — `id`, `id_rep`, `siti`, `link`, and `the_geom` — assigned directly during instantiation. The `__repr__` property returns a formatted string representation of all five fields for identification and debugging purposes.

**Inherits from**: object

#### Methods

##### __init__(self, id, id_rep, siti, link, the_geom)

*No description available.*
Initializes a new instance of the `PYREPERTI` class by assigning the provided arguments to their corresponding instance attributes. Accepts five parameters — `id`, `id_rep`, `siti`, `link`, and `the_geom` — and binds each directly to `self.id`, `self.id_rep`, `self.siti`, `self.link`, and `self.the_geom` respectively. No validation or transformation is applied to the supplied values during initialization.

##### __repr__(self)

*No description available.*
A property that returns the official string representation of a `PYREPERTI` instance. The returned string follows the format `<PYREPERTI('id','id_rep', 'siti', 'link', 'the_geom')>`, embedding the instance's `id`, `id_rep`, `siti`, `link`, and `the_geom` attributes. Note that this is implemented as a `@property` rather than a standard method.

