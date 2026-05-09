# modules/db/entities/PYINDIVIDUI.py

## Overview

This file contains 4 documented elements.

## Classes

### PYINDIVIDUI

*No description available.*
A data model class representing an individual unit within an archaeological or structural context. It encapsulates six attributes — `id`, `sito`, `sigla_struttura`, `note`, `id_individuo`, and `the_geom` — assigned directly during instantiation. The class exposes a `__repr__` property that returns a formatted string representation of all stored attribute values.

**Inherits from**: object

#### Methods

##### __init__(self, id, sito, sigla_struttura, note, id_individuo, the_geom)

## `__init__` — `PYINDIVIDUI`

Initializes a new instance of the `PYINDIVIDUI` class by assigning the provided arguments to their corresponding instance attributes.

Accepts six parameters — `id`, `sito`, `sigla_struttura`, `note`, `id_individuo`, and `the_geom` — and binds each directly to `self`, making them accessible as instance-level attributes for the lifetime of the object.

##### __repr__(self)

*No description available.*
A property that returns the official string representation of a `PYINDIVIDUI` instance. The returned string follows the format `<PYINDIVIDUI('id','sito', 'sigla_struttura', 'note', 'id_individuo','the_geom')>`, embedding the values of those six fields using `%`-style string formatting. Note that `__repr__` is implemented as a `@property` rather than a standard method, so it is accessed without parentheses.

