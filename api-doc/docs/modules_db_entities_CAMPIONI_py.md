# modules/db/entities/CAMPIONI.py

## Overview

This file contains 4 documented elements.

## Classes

### CAMPIONI

*No description available.*
Represents a archaeological sample (campione) record, encapsulating all descriptive and locational metadata associated with a single sample collected from an excavation site. Each instance stores attributes including a unique sample identifier (`id_campione`), site name (`sito`), sample number (`nr_campione`), sample type (`tipo_campione`), description, area, stratigraphic unit (`us`), material inventory number (`numero_inventario_materiale`), crate number (`nr_cassa`), and storage location (`luogo_conservazione`). A UUID is automatically generated for `entity_uuid` if one is not explicitly provided at instantiation.

**Inherits from**: object

#### Methods

##### __init__(self, id_campione, sito, nr_campione, tipo_campione, descrizione, area, us, numero_inventario_materiale, nr_cassa, luogo_conservazione, entity_uuid)

Initializes a new instance of the `CAMPIONI` class, representing an archaeological sample record with its associated metadata. Accepts ten required positional parameters — `id_campione`, `sito`, `nr_campione`, `tipo_campione`, `descrizione`, `area`, `us`, `numero_inventario_materiale`, `nr_cassa`, and `luogo_conservazione` — along with an optional `entity_uuid` parameter. If `entity_uuid` is not provided or evaluates to a falsy value, a new UUID4 string is automatically generated and assigned to `self.entity_uuid`.

##### __repr__(self)

Returns the official string representation of a `CAMPIONI` instance, formatted as a structured tuple-like string containing the ten core fields of the record. The output includes `id_campione`, `sito`, `nr_campione`, `tipo_campione`, `descrizione`, `area`, `us`, `numero_inventario_materiale`, `nr_cassa`, and `luogo_conservazione`, in that order. The resulting string follows the pattern `<CAMPIONI('...', '...', ...)>`.

