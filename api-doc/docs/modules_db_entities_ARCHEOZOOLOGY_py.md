# modules/db/entities/ARCHEOZOOLOGY.py

## Overview

This file contains 4 documented elements.

## Classes

### ARCHEOZOOLOGY

*No description available.*
Represents an archaeozoological record associated with a specific excavation context, identified by site (`sito`), area, stratigraphic unit (`us`), and grid square (`quadrato`), along with spatial coordinates (`coord_x`, `coord_y`, `coord_z`). The class stores faunal data for several animal taxa — including `bos_bison`, `camoscio`, `capriolo`, `cervo`, `stambecco`, `canidi`, `ursidi`, and `megacero` — as well as bone modification attributes such as `calcinati`, `combusto`, `coni`, `pdi`, and `strie`. Each instance is assigned a unique identifier via `entity_uuid`, defaulting to a newly generated UUID if none is provided.

**Inherits from**: object

#### Methods

##### __init__(self, id_archzoo, sito, area, us, quadrato, coord_x, coord_y, coord_z, bos_bison, calcinati, camoscio, capriolo, cervo, combusto, coni, pdi, stambecco, strie, canidi, ursidi, megacero, entity_uuid)

Initializes a new instance of the `ARCHEOZOOLOGY` class with all required archaeozoological record attributes. The parameters capture spatial context (`sito`, `area`, `us`, `quadrato`, `coord_x`, `coord_y`, `coord_z`) alongside faunal identification counts for various species and bone condition indicators (`bos_bison`, `calcinati`, `camoscio`, `capriolo`, `cervo`, `combusto`, `coni`, `pdi`, `stambecco`, `strie`, `canidi`, `ursidi`, `megacero`). The optional `entity_uuid` parameter is assigned the provided value if given, or a newly generated UUID string via `uuid.uuid4()` if omitted.

##### __repr__(self)

Returns a string representation of an `ARCHEOZOOLOGY` instance, formatted as a structured label containing all key fields of the object.

The output string includes the following attributes in order: `id_archzoo`, `sito`, `area`, `us`, `quadrato`, `coord_x`, `coord_y`, `coord_z`, `bos_bison`, `calcinati`, `camoscio`, `capriolo`, `cervo`, `combusto`, `coni`, `pdi`, `stambecco`, `strie`, `canidi`, `ursidi`, and `megacero`. This method is intended for debugging and logging purposes, providing an unambiguous textual snapshot of the instance's state.

