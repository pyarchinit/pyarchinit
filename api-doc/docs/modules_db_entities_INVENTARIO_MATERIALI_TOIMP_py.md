# modules/db/entities/INVENTARIO_MATERIALI_TOIMP.py

## Overview

This file contains 4 documented elements.

## Classes

### INVENTARIO_MATERIALI_TOIMP

*No description available.*
A plain Python data class representing a single material inventory record for archaeological import purposes. It stores 23 fields describing a catalogued find, including site identification (`sito`), inventory number (`numero_inventario`), find type (`tipo_reperto`), stratigraphic unit (`us`), conservation details (`stato_conservazione`, `luogo_conservazione`), dating (`datazione_reperto`), and ceramic-specific attributes (`corpo_ceramico`, `rivestimento`, `forme_minime`, `forme_massime`, `totale_frammenti`). The `__repr__` method returns a formatted string representation of all fields in their defined order.

**Inherits from**: object

#### Methods

##### __init__(self, id_invmat, sito, numero_inventario, tipo_reperto, criterio_schedatura, definizione, descrizione, area, us, lavato, nr_cassa, luogo_conservazione, stato_conservazione, datazione_reperto, elementi_reperto, misurazioni, rif_biblio, tecnologie, forme_minime, forme_massime, totale_frammenti, corpo_ceramico, rivestimento)

Initializes an instance of `INVENTARIO_MATERIALI_TOIMP` by accepting 23 parameters and assigning each to the corresponding instance attribute. The parameters represent fields of a material inventory record, including identification data (`id_invmat`, `numero_inventario`), site and context information (`sito`, `area`, `us`), artifact descriptors (`tipo_reperto`, `definizione`, `descrizione`, `criterio_schedatura`), conservation details (`lavato`, `nr_cassa`, `luogo_conservazione`, `stato_conservazione`), and ceramic-specific attributes (`elementi_reperto`, `misurazioni`, `tecnologie`, `forme_minime`, `forme_massime`, `totale_frammenti`, `corpo_ceramico`, `rivestimento`). Additional fields cover bibliographic references (`rif_biblio`) and artifact dating (`datazione_reperto`).

##### __repr__(self)

Returns a string representation of an `INVENTARIO_MATERIALI_TOIMP` instance, formatting all 23 fields of the object into a structured, human-readable string. The output includes identifiers, site information, inventory details, conservation data, and ceramic-specific attributes such as `corpo_ceramico` and `rivestimento`, enclosed in angle brackets. This representation is primarily intended for debugging and logging purposes.

