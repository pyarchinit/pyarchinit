# modules/db/entities/INVENTARIO_MATERIALI.py

## Overview

This file contains 4 documented elements.

## Classes

### INVENTARIO_MATERIALI

*No description available.*
A data model class representing a single archaeological materials inventory record. It encapsulates a comprehensive set of attributes describing a find, including site identification (`sito`, `area`, `us`), artifact classification (`tipo_reperto`, `definizione`, `tipo`), physical characteristics (`corpo_ceramico`, `rivestimento`, `diametro_orlo`, `peso`), conservation details (`stato_conservazione`, `luogo_conservazione`), quantitative measurements (`forme_minime`, `forme_massime`, `totale_frammenti`, `eve_orlo`), and documentation references (`rif_biblio`, `photo_id`, `drawing_id`). Each instance is assigned a unique identifier via `entity_uuid`, defaulting to a newly generated UUID if none is provided, and supports an optional inventory suffix through the `sub_inv` field.

**Inherits from**: object

#### Methods

##### __init__(self, id_invmat, sito, numero_inventario, tipo_reperto, criterio_schedatura, definizione, descrizione, area, us, lavato, nr_cassa, luogo_conservazione, stato_conservazione, datazione_reperto, elementi_reperto, misurazioni, rif_biblio, tecnologie, forme_minime, forme_massime, totale_frammenti, corpo_ceramico, rivestimento, diametro_orlo, peso, tipo, eve_orlo, repertato, diagnostico, n_reperto, tipo_contenitore, struttura, years, schedatore, date_scheda, punto_rinv, negativo_photo, diapositiva, quota_usm, unita_misura_quota, photo_id, drawing_id, entity_uuid, sub_inv)

Initializes a new instance of the `INVENTARIO_MATERIALI` class, assigning all provided arguments to their corresponding instance attributes. The constructor accepts 42 required positional parameters covering material inventory record fields such as site information (`sito`), inventory number (`numero_inventario`), find type (`tipo_reperto`), conservation details, ceramic measurements, and photographic references, along with two optional keyword parameters: `entity_uuid` and `sub_inv`. If `entity_uuid` is not provided or evaluates to falsy, a new UUID is automatically generated via `uuid.uuid4()`; `sub_inv` defaults to `None` and is described in source as an optional suffix (e.g., `"a"`, `"b1"`, `"bis"`).

##### __repr__(self)

*No description available.*
Returns an unambiguous string representation of an `INVENTARIO_MATERIALI` instance, formatting all fields of the object into a structured template string prefixed with the class name. The output includes all 42 attributes — from `id_invmat` and `sito` through to `photo_id` and `drawing_id` — each enclosed in single quotes and separated by commas. This representation is intended for debugging and logging purposes, providing a complete snapshot of the object's state.

