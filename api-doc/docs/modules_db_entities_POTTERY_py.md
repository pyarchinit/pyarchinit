# modules/db/entities/POTTERY.py

## Overview

This file contains 4 documented elements.

## Classes

### POTTERY

*No description available.*
A data model class representing a pottery find record within an archaeological context. It encapsulates a comprehensive set of attributes describing a pottery item's provenance (site, area, stratigraphic unit, sector), physical characteristics (fabric, material, form, ware, Munsell colour, dimensions), decorative properties (exterior/interior decoration, decoration type, motif, and position), and administrative metadata (repository ID, box, bag, photo, drawing, quantity, and dating). Each instance is assigned a unique identifier via `entity_uuid`, which defaults to a newly generated UUID4 string if not explicitly provided.

**Inherits from**: object

#### Methods

##### __init__(self, id_rep, id_number, sito, area, us, box, photo, drawing, anno, fabric, percent, material, form, specific_form, ware, munsell, surf_trat, exdeco, intdeco, wheel_made, descrip_ex_deco, descrip_in_deco, note, diametro_max, qty, diametro_rim, diametro_bottom, diametro_height, diametro_preserved, specific_shape, bag, sector, decoration_type, decoration_motif, decoration_position, datazione, entity_uuid)

## `__init__` — `POTTERY` Class Constructor

Initializes a new instance of the `POTTERY` class, representing an archaeological pottery record. Assigns all provided arguments directly to their corresponding instance attributes, covering identification fields (`id_rep`, `id_number`, `sito`, `area`, `us`), physical and typological descriptors (`fabric`, `material`, `form`, `specific_form`, `ware`, `munsell`), decorative attributes (`exdeco`, `intdeco`, `descrip_ex_deco`, `descrip_in_deco`, `decoration_type`, `decoration_motif`, `decoration_position`), and dimensional measurements (`diametro_max`, `diametro_rim`, `diametro_bottom`, `diametro_height`, `diametro_preserved`). The optional `entity_uuid` parameter is assigned its provided value if supplied; otherwise, a new UUID string is generated via `uuid.uuid4()`.

##### __repr__(self)

*No description available.*
Returns an unambiguous string representation of a `POTTERY` instance. The output is formatted as a `<POTTERY(...)>` string containing all recorded attributes of the object, including identifiers (`id_rep`, `id_number`), site information (`sito`, `area`, `us`), physical properties (`fabric`, `material`, `form`, `ware`, `munsell`), measurements (`diametro_max`, `diametro_rim`, `diametro_bottom`, `diametro_height`, `diametro_preserved`), decoration details (`exdeco`, `intdeco`, `decoration_type`, `decoration_motif`, `decoration_position`), and additional metadata (`photo`, `drawing`, `anno`, `qty`, `bag`, `sector`, `datazione`). This method is intended for debugging and logging purposes, providing a complete snapshot of the instance's state.

