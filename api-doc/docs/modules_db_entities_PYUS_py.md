# modules/db/entities/PYUS.py

## Overview

This file contains 4 documented elements.

## Classes

### PYUS

*No description available.*
**Authors:** Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>

`PYUS` is a plain Python data class representing a stratigraphic unit (US — *Unità Stratigrafica*) record, encapsulating both descriptive and spatial attributes associated with an archaeological excavation context. Each instance stores fields including the unit identifier (`gid`), area and excavation references (`area_s`, `scavo_s`), stratigraphic index (`stratigraph_index_us`), unit type information (`tipo_us_s`, `unita_tipo_s`), survey and documentation metadata (`rilievo_originale`, `disegnatore`, `data`, `tipo_doc`, `nome_doc`), and geometric data (`coord`, `the_geom`). The `__repr__` property returns a formatted string representation of all stored attributes.

**Inherits from**: object

#### Methods

##### __init__(self, gid, area_s, scavo_s, us_s, stratigraph_index_us, tipo_us_s, rilievo_originale, disegnatore, data, tipo_doc, nome_doc, coord, the_geom, unita_tipo_s)

Initializes a new instance of the `PYUS` class by assigning the provided arguments to their corresponding instance attributes. The constructor accepts fourteen parameters representing stratigraphic unit data, including identifiers (`gid`, `area_s`, `scavo_s`, `us_s`), classification fields (`tipo_us_s`, `unita_tipo_s`, `stratigraph_index_us`), survey metadata (`rilievo_originale`, `disegnatore`, `data`), documentation references (`tipo_doc`, `nome_doc`), and geometric data (`coord`, `the_geom`). Each parameter is stored directly as an instance attribute with no additional transformation or validation.

##### __repr__(self)

*No description available.*
A property that returns the official string representation of a `PYUS` instance. It formats a string containing the object's fourteen attributes — `gid`, `area_s`, `scavo_s`, `us_s`, `stratigraph_index_us`, `tipo_us_s`, `rilievo_originale`, `disegnatore`, `data`, `tipo_doc`, `nome_doc`, `coord`, `the_geom`, and `unita_tipo_s` — enclosed within `<PYUS(...)>` angle brackets. Note that this is implemented as a `@property` rather than a standard method.

