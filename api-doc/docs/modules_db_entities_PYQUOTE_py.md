# modules/db/entities/PYQUOTE.py

## Overview

This file contains 4 documented elements.

## Classes

### PYQUOTE

*No description available.*
A data model class representing an elevation measurement (quota) record associated with an archaeological stratigraphic unit. Each instance stores spatial and descriptive attributes including site (`sito_q`), area (`area_q`), stratigraphic unit (`us_q`), unit of measurement (`unita_misu_q`), elevation value (`quota_q`), date (`data`), surveyor (`disegnatore`), original survey reference (`rilievo_originale`), geometry (`the_geom`), and unit type (`unita_tipo_q`). The `__repr__` property returns a formatted string representation of all stored fields.

**Inherits from**: object

#### Methods

##### __init__(self, id, sito_q, area_q, us_q, unita_misu_q, quota_q, data, disegnatore, rilievo_originale, the_geom, unita_tipo_q)

## `__init__` — `PYQUOTE`

Initializes a new instance of the `PYQUOTE` class by accepting eleven parameters and assigning each directly to the corresponding instance attribute. The parameters are `id`, `sito_q`, `area_q`, `us_q`, `unita_misu_q`, `quota_q`, `data`, `disegnatore`, `rilievo_originale`, `the_geom`, and `unita_tipo_q`. No validation or transformation is applied to any of the provided values during initialization.

##### __repr__(self)

*No description available.*
A property that returns the official string representation of a `PYQUOTE` instance. The returned string follows the format `<PYQUOTE('id','sito_q', 'area_q', 'us_q', 'unita_misu_q', 'quota_q', 'data', 'disegnatore', 'rilievo_originale', 'the_geom', 'unita_tipo_q')>`, embedding the instance's fields using `%`-style string formatting. Note that this is implemented as a `@property` rather than a standard method.

