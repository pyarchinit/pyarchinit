# modules/db/entities/STRUTTURA.py

## Overview

This file contains 4 documented elements.

## Classes

### STRUTTURA

*No description available.*
Represents an archaeological structure record, encapsulating all descriptive, chronological, and physical attributes associated with a structural find at an excavation site. The class stores core fields such as site identifier, structure code, category, typology, materials, stratigraphic relationships, and chronological phasing, alongside an extended set of optional fields introduced for the AR structure form (`scheda struttura AR`), including conservation state, topographic relations, planimetric development, and decorative motifs. Each instance is assigned a unique identifier via `entity_uuid`, defaulting to a newly generated UUID4 if none is provided.

**Inherits from**: object

#### Methods

##### __init__(self, id_struttura, sito, sigla_struttura, numero_struttura, categoria_struttura, tipologia_struttura, definizione_struttura, descrizione, interpretazione, periodo_iniziale, fase_iniziale, periodo_finale, fase_finale, datazione_estesa, materiali_impiegati, elementi_strutturali, rapporti_struttura, misure_struttura, data_compilazione, nome_compilatore, stato_conservazione, quota, relazione_topografica, prospetto_ingresso, orientamento_ingresso, articolazione, n_ambienti, orientamento_ambienti, sviluppo_planimetrico, elementi_costitutivi, motivo_decorativo, potenzialita_archeologica, manufatti, elementi_datanti, fasi_funzionali, entity_uuid)

## `__init__` — `STRUTTURA`

Initializes a `STRUTTURA` instance representing an archaeological structure record. The constructor accepts 18 required positional parameters covering core structural attributes — including identifiers (`id_struttura`, `sito`, `sigla_struttura`, `numero_struttura`), classification fields (`categoria_struttura`, `tipologia_struttura`, `definizione_struttura`), chronological data (`periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`, `datazione_estesa`), and descriptive/relational fields (`descrizione`, `interpretazione`, `materiali_impiegati`, `elementi_strutturali`, `rapporti_struttura`, `misure_struttura`) — along with 18 optional keyword parameters (defaulting to `None`) introduced for the AR structure form, such as `data_compilazione`, `stato_conservazione`, `quota`, and `fasi_funzionali`. If `entity_uuid` is not provided, a new UUID4 string is automatically generated and assigned to `self.entity_uuid`.

##### __repr__(self)

Returns a string representation of a `STRUTTURA` instance, formatted as a structured tag containing 18 fields. The output includes `id_struttura`, `sito`, `sigla_struttura`, `numero_struttura`, `categoria_struttura`, `tipologia_struttura`, `definizione_struttura`, `descrizione`, `interpretazione`, `periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`, `datazione_estesa`, `materiali_impiegati`, `elementi_strutturali`, `rapporti_struttura`, and `misure_struttura`. The integer field `id_struttura` and `numero_struttura` are formatted with `%d`, while all remaining fields are formatted as strings with `%s`.

