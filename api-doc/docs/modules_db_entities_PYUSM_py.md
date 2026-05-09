# modules/db/entities/PYUSM.py

## Overview

This file contains 4 documented elements.

## Classes

### PYUSM

*No description available.*
A data model class representing a stratigraphic masonry unit (USM — *Unità Stratigrafica Muraria*) record, encapsulating spatial and documentary attributes associated with an archaeological excavation context. The constructor accepts fourteen parameters — `gid`, `area_s`, `scavo_s`, `us_s`, `stratigraph_index_us`, `tipo_us_s`, `rilievo_originale`, `disegnatore`, `data`, `tipo_doc`, `nome_doc`, `coord`, `the_geom`, and `unita_tipo_s` — and assigns each directly to the corresponding instance attribute. The `__repr__` property returns a formatted string representation of all instance attributes.

**Inherits from**: object

#### Methods

##### __init__(self, gid, area_s, scavo_s, us_s, stratigraph_index_us, tipo_us_s, rilievo_originale, disegnatore, data, tipo_doc, nome_doc, coord, the_geom, unita_tipo_s)

Initializes a `PYUSM` instance representing a stratigraphic mapping unit with its associated spatial and documentary attributes. Accepts fourteen parameters — `gid`, `area_s`, `scavo_s`, `us_s`, `stratigraph_index_us`, `tipo_us_s`, `rilievo_originale`, `disegnatore`, `data`, `tipo_doc`, `nome_doc`, `coord`, `the_geom`, and `unita_tipo_s` — and assigns each directly to the corresponding instance attribute. No validation or transformation is applied to the provided values during initialization.

##### __repr__(self)

*No description available.*
A property that returns the official string representation of a `PYUSM` instance. The returned string follows the format `<PYUSM('gid','area_s','scavo_s','us_s','stratigraph_index_us','tipo_us_s','rilievo_originale','disegnatore','data','tipo_doc','nome_doc','coord','the_geom','unita_tipo_s')>`, interpolating the corresponding instance attributes into a fixed template. Note that this is implemented as a `@property` rather than a standard method.

