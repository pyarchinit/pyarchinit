# modules/db/entities/INVENTARIO_LAPIDEI.py

## Overview

This file contains 4 documented elements.

## Classes

### INVENTARIO_LAPIDEI

*No description available.*
A data model class representing an inventory record for lapidary (stone) artifacts within an archaeological context. Each instance encapsulates descriptive, physical, and bibliographic attributes of a stone object, including site (`sito`), card number (`scheda_numero`), material (`materiale`), dimensional measurements (`spessore`, `larghezza`, `lunghezza`, `h`), working and conservation state (`lavorazione_e_stato_di_conservazione`), chronology (`cronologia`), and compiler (`compilatore`). A unique entity identifier (`entity_uuid`) is automatically generated via `uuid.uuid4()` if one is not explicitly provided at instantiation.

**Inherits from**: object

#### Methods

##### __init__(self, id_invlap, sito, scheda_numero, collocazione, oggetto, tipologia, materiale, d_letto_posa, d_letto_attesa, toro, spessore, larghezza, lunghezza, h, descrizione, lavorazione_e_stato_di_conservazione, confronti, cronologia, bibliografia, compilatore, entity_uuid)

Initializes a new instance of the `INVENTARIO_LAPIDEI` class, representing an inventory record for a stone artifact (lapidary inventory). Assigns the provided values to twenty instance attributes covering identification, physical dimensions (`spessore`, `larghezza`, `lunghezza`, `h`, `d_letto_posa`, `d_letto_attesa`, `toro`), descriptive fields (`oggetto`, `tipologia`, `materiale`, `descrizione`, `lavorazione_e_stato_di_conservazione`, `confronti`, `cronologia`, `bibliografia`), and administrative fields (`sito`, `scheda_numero`, `collocazione`, `compilatore`). If `entity_uuid` is not provided or evaluates to a falsy value, a new UUID4 string is automatically generated and assigned to `self.entity_uuid`.

##### __repr__(self)

Returns a string representation of an `INVENTARIO_LAPIDEI` instance, formatting all twenty fields of the object into a structured, human-readable string.

The output follows the pattern `<INVENTARIO_LAPIDEI('...') >`, embedding the values of `id_invlap`, `sito`, `scheda_numero`, `collocazione`, `oggetto`, `tipologia`, `materiale`, `d_letto_posa`, `d_letto_attesa`, `toro`, `spessore`, `larghezza`, `lunghezza`, `h`, `descrizione`, `lavorazione_e_stato_di_conservazione`, `confronti`, `cronologia`, `bibliografia`, and `compilatore` using `%`-style string formatting. Integer fields are formatted with `%d` and string fields with `%s`.

