# modules/db/entities/PYQUOTEUSM.py

## Overview

This file contains 4 documented elements.

## Classes

### PYQUOTEUSM

*No description available.*
A data model class representing an elevation measurement record associated with a stratigraphic unit (US — *Unità Stratigrafica Muraria*) within an archaeological site. It stores attributes including site, area, and unit identifiers, unit of measurement, elevation value, survey date, draughtsman, original survey reference, geometry, and unit type. The `__repr__` property returns a formatted string representation of the instance's field values.

**Inherits from**: object

#### Methods

##### __init__(self, id, sito_q, area_q, us_q, unita_misu_q, quota_q, data, disegnatore, rilievo_originale, the_geom, unita_tipo_q)

Initializes a new instance of the `PYQUOTEUSM` class by accepting eleven parameters and assigning each directly to the corresponding instance attribute. The parameters cover identification and spatial data fields: `id`, `sito_q`, `area_q`, `us_q`, `unita_misu_q`, `quota_q`, `data`, `disegnatore`, `rilievo_originale`, `the_geom`, and `unita_tipo_q`. No validation or transformation is applied to any of the provided values during initialization.

##### __repr__(self)

*No description available.*
A property that returns the official string representation of a `PYQUOTEUSM` instance. The returned string follows the format `<PYQUOTEUSM('id','sito_q', 'area_q', 'us_q', 'unita_misu_q', 'quota_q', 'data', 'disegnatore', 'rilievo_originale', 'the_geom', 'unita_tipo_q')>`, embedding the values of all eleven instance attributes. This method is implemented as a `@property` rather than a standard method.

