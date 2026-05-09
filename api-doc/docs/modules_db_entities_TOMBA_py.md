# modules/db/entities/TOMBA.py

## Overview

This file contains 4 documented elements.

## Classes

### TOMBA

*No description available.*
A data model class representing an archaeological tomb (burial) record within an excavation context. It encapsulates descriptive, structural, and chronological attributes of a burial, including site and area identifiers, burial rite, deposition type, conservation state, grave goods (corredo), coverage type, and dating information. Each instance is assigned a unique identifier via `entity_uuid`, defaulting to a newly generated UUID v4 if none is provided.

**Inherits from**: object

#### Methods

##### __init__(self, id_tomba, sito, area, nr_scheda_taf, sigla_struttura, nr_struttura, nr_individuo, rito, descrizione_taf, interpretazione_taf, segnacoli, canale_libatorio_si_no, oggetti_rinvenuti_esterno, stato_di_conservazione, copertura_tipo, tipo_contenitore_resti, tipo_deposizione, tipo_sepoltura, corredo_presenza, corredo_tipo, corredo_descrizione, periodo_iniziale, fase_iniziale, periodo_finale, fase_finale, datazione_estesa, misure_tomba, entity_uuid)

Initializes a new instance of the `TOMBA` class, representing a burial record with all associated archaeological attributes. Assigns each provided argument to the corresponding instance attribute, covering identification fields (`id_tomba`, `sito`, `area`, `nr_scheda_taf`, `sigla_struttura`, `nr_struttura`, `nr_individuo`), burial characteristics (`rito`, `descrizione_taf`, `interpretazione_taf`, `segnacoli`, `canale_libatorio_si_no`, `oggetti_rinvenuti_esterno`, `stato_di_conservazione`, `copertura_tipo`, `tipo_contenitore_resti`, `tipo_deposizione`, `tipo_sepoltura`), grave goods (`corredo_presenza`, `corredo_tipo`, `corredo_descrizione`), chronological data (`periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`, `datazione_estesa`), and physical measurements (`misure_tomba`). The optional `entity_uuid` parameter is assigned directly if provided; otherwise, a new UUID4 string is generated automatically via `uuid.uuid4()`.

##### __repr__(self)

Returns a string representation of a `TOMBA` instance in a formatted `<TOMBA(...)>` notation. The output includes all primary fields of the object, such as `id_tomba`, `sito`, `area`, `nr_scheda_taf`, `sigla_struttura`, `nr_struttura`, `nr_individuo`, `rito`, `descrizione_taf`, `interpretazione_taf`, `segnacoli`, `canale_libatorio_si_no`, `oggetti_rinvenuti_esterno`, `stato_di_conservazione`, `copertura_tipo`, `tipo_contenitore_resti`, `tipo_deposizione`, `tipo_sepoltura`, `corredo_presenza`, `corredo_tipo`, `corredo_descrizione`, `periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`, and `datazione_estesa`. Integer fields are formatted with `%d` and string fields with `%s`.

