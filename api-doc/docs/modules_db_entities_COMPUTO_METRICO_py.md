# modules/db/entities/COMPUTO_METRICO.py

## Overview

This file contains 3 documented elements.

## Classes

### COMPUTO_METRICO

*No description available.*
Represents a metric computation record associated with a specific archaeological or excavation site, storing the parameters and results of a volumetric/area calculation performed on digital elevation models (DEMs). Each instance captures the pre- and post-intervention DEM references, the polygon layer used, computed area in square metres (`area_mq`), volume in cubic metres (`volume_mc`), minimum and maximum elevation values, and contextual metadata such as calculation date, excavation phase, and notes. A unique identifier (`entity_uuid`) is automatically generated via `uuid.uuid4()` if one is not explicitly provided at instantiation.

**Inherits from**: object

#### Methods

##### __init__(self, id_computo, sito, nome_calcolo, tipo_calcolo, dem_pre, dem_post, layer_poligono, area_mq, volume_mc, quota_min, quota_max, data_calcolo, fase_scavo, note, entity_uuid)

## `__init__` — `COMPUTO_METRICO`

Initializes a new instance of the `COMPUTO_METRICO` class, assigning all provided arguments directly to their corresponding instance attributes. Accepts fourteen required positional parameters — `id_computo`, `sito`, `nome_calcolo`, `tipo_calcolo`, `dem_pre`, `dem_post`, `layer_poligono`, `area_mq`, `volume_mc`, `quota_min`, `quota_max`, `data_calcolo`, `fase_scavo`, and `note` — along with one optional keyword parameter, `entity_uuid`. If `entity_uuid` is not supplied or evaluates to a falsy value, a new UUID4 string is automatically generated via `str(uuid.uuid4())` and assigned to `self.entity_uuid`.

##### __repr__(self)

*No description available.*
Returns an unambiguous string representation of the `COMPUTO_METRICO` instance. The output follows the format `<COMPUTO_METRICO('id_computo','sito','nome_calcolo')>`, embedding the instance's `id_computo`, `sito`, and `nome_calcolo` fields. This method is intended for debugging and logging purposes.

