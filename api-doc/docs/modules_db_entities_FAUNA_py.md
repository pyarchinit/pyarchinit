# modules/db/entities/FAUNA.py

## Overview

This file contains 4 documented elements.

## Classes

### FAUNA

*No description available.*
A data model class representing a faunal remains record within an archaeological stratigraphic unit (US). It encapsulates a comprehensive set of zooarchaeological attributes, including species identification, skeletal parts, taphonomic indicators, combustion traces, fragmentation state, conservation status, and contextual/stratigraphic metadata. Each instance is assigned a unique identifier via `entity_uuid`, defaulting to a newly generated UUID if none is provided.

**Inherits from**: object

#### Methods

##### __init__(self, id_fauna, id_us, sito, area, saggio, us, datazione_us, responsabile_scheda, data_compilazione, documentazione_fotografica, metodologia_recupero, contesto, descrizione_contesto, resti_connessione_anatomica, tipologia_accumulo, deposizione, numero_stimato_resti, numero_minimo_individui, specie, parti_scheletriche, specie_psi, misure_ossa, stato_frammentazione, tracce_combustione, combustione_altri_materiali_us, tipo_combustione, segni_tafonomici_evidenti, caratterizzazione_segni_tafonomici, stato_conservazione, alterazioni_morfologiche, note_terreno_giacitura, campionature_effettuate, affidabilita_stratigrafica, classi_reperti_associazione, osservazioni, interpretazione, entity_uuid)

Initializes a new instance of the `FAUNA` class, representing a faunal remains record in an archaeological context. All positional parameters are assigned directly to their corresponding instance attributes, covering identification fields (`id_fauna`, `id_us`, `sito`, `area`, `saggio`, `us`), recording metadata (`datazione_us`, `responsabile_scheda`, `data_compilazione`), and analytical data such as taphonomic signs, combustion traces, skeletal parts, species, conservation state, and stratigraphic information. The optional `entity_uuid` parameter is assigned as the instance's unique identifier; if not provided, a new UUID4 string is generated automatically via `uuid.uuid4()`.

##### __repr__(self)

Returns a formatted string representation of a `FAUNA` instance, listing all its fields in a fixed-order, comma-separated format enclosed in angle brackets prefixed with `FAUNA`. The output includes 36 fields, ranging from identifiers such as `id_fauna` and `id_us` through contextual, taphonomic, and interpretive attributes, each formatted as a quoted string (`'%s'`) except for `id_fauna` and `numero_minimo_individui`, which are formatted as integers (`'%d'`).

