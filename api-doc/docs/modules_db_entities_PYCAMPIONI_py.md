# modules/db/entities/PYCAMPIONI.py

## Overview

This file contains 4 documented elements.

## Classes

### PYCAMPIONI

*No description available.*
A data model class representing a sample record (`campione`) within an archaeological or geospatial context. It stores attributes including a numeric identifier (`id`), a sample identifier (`id_campion`), site information (`sito`), sample type (`tipo_camp`), dating (`dataz`), chronology (`cronologia`), an image link (`link_immag`), a sample code (`sigla_camp`), and a geometry field (`the_geom`). The `__repr__` property returns a formatted string representation of all instance attributes.

**Inherits from**: object

#### Methods

##### __init__(self, id, id_campion, sito, tipo_camp, dataz, cronologia, link_immag, sigla_camp, the_geom)

## `__init__` — `PYCAMPIONI`

Initializes a new instance of the `PYCAMPIONI` class by assigning the provided arguments to their corresponding instance attributes. Accepts nine parameters: `id`, `id_campion`, `sito`, `tipo_camp`, `dataz`, `cronologia`, `link_immag`, `sigla_camp`, and `the_geom`, each mapped directly to a same-named attribute on the instance.

##### __repr__(self)

*No description available.*
A property that returns the official string representation of a `PYCAMPIONI` instance. The returned string follows the format `<PYCAMPIONI('id','id_campion', 'sito', 'tipo_camp', 'dataz','cronologia','link_immag','sigla_camp','the_geom')>`, embedding the values of all nine instance attributes. Note that this is implemented as a `@property` rather than a standard method.

