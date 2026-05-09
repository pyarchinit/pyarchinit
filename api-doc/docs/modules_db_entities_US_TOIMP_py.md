# modules/db/entities/US_TOIMP.py

## Overview

This file contains 4 documented elements.

## Classes

### US_TOIMP

*No description available.*
A data model class representing a stratigraphic unit (Unità Stratigrafica) record for archaeological excavation documentation. It encapsulates all attributes associated with a stratigraphic unit, including identification fields (`id_us`, `sito`, `area`, `us`), stratigraphic and interpretative definitions (`d_stratigrafica`, `d_interpretativa`), chronological phasing (`periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`), excavation metadata (`scavato`, `attivita`, `anno_scavo`, `metodo_di_scavo`), physical characteristics (`colore`, `consistenza`, `struttura`, `formazione`, `stato_di_conservazione`), and recording information (`data_schedatura`, `schedatore`, `inclusi`, `campioni`, `rapporti`). The `__repr__` method returns a formatted string representation of all 26 instance attributes.

**Inherits from**: object

#### Methods

##### __init__(self, id_us, sito, area, us, d_stratigrafica, d_interpretativa, descrizione, interpretazione, periodo_iniziale, fase_iniziale, periodo_finale, fase_finale, scavato, attivita, anno_scavo, metodo_di_scavo, inclusi, campioni, rapporti, data_schedatura, schedatore, formazione, stato_di_conservazione, colore, consistenza, struttura)

## `__init__` — `US_TOIMP`

Initializes a new instance of the `US_TOIMP` class by assigning all 26 provided arguments to their corresponding instance attributes. The parameters cover the full set of stratigraphic unit (US) record fields, including identification data (`id_us`, `sito`, `area`, `us`), stratigraphic and interpretive descriptions (`d_stratigrafica`, `d_interpretativa`, `descrizione`, `interpretazione`), chronological information (`periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`), excavation details (`scavato`, `attivita`, `anno_scavo`, `metodo_di_scavo`), associated finds and samples (`inclusi`, `campioni`, `rapporti`), cataloguing metadata (`data_schedatura`, `schedatore`), and physical characteristics (`formazione`, `stato_di_conservazione`, `colore`, `consistenza`, `struttura`). Each parameter is stored directly as an instance attribute with the same name.

##### __repr__(self)

*No description available.*
Returns an unambiguous string representation of the `US_TOIMP` instance. The output is formatted as `<US_TOIMP('...', '...', ...)>` and includes all 26 instance attributes in declaration order: `id_us`, `sito`, `area`, `us`, `d_stratigrafica`, `d_interpretativa`, `descrizione`, `interpretazione`, `periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`, `scavato`, `attivita`, `anno_scavo`, `metodo_di_scavo`, `inclusi`, `campioni`, `rapporti`, `data_schedatura`, `schedatore`, `formazione`, `stato_di_conservazione`, `colore`, `consistenza`, and `struttura`. Note that `id_us` and `us` are formatted as integers (`%d`), while all remaining fields are formatted as strings (`%s`).

