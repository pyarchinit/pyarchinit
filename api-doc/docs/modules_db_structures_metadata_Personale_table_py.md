# modules/db/structures_metadata/Personale_table.py

## Overview

This file contains 3 documented elements.

## Classes

### Personale_table

*No description available.*
Defines the SQLAlchemy table schema for storing personnel records associated with archaeological sites. The class exposes a single class method, `define_table(cls, metadata)`, which constructs and returns a `Table` object named `'personale_table'` containing columns for personal details (name, date of birth, fiscal code, address, contact information), site role and professional qualification, contract information (type, start/end dates, hourly and daily rates, IBAN), activity status, and a StratiGraph UUID. A `UniqueConstraint` named `'ID_personale_unico'` enforces that the combination of `sito` and `codice_fiscale` is unique across all records.

#### Methods

##### define_table(cls, metadata)

*No description available.*
A class method that defines and returns a SQLAlchemy `Table` object named `'personale_table'` bound to the provided `metadata` instance. The table represents archaeological site personnel records and contains columns for personal details (`nome`, `cognome`, `data_nascita`, `indirizzo`, `codice_fiscale`), contact information (`email`, `telefono`), site assignment (`sito`, `ruolo`, `qualifica`), contract data (`tipo_contratto`, `data_inizio_contratto`, `data_fine_contratto`, `tariffa_oraria`, `tariffa_giornaliera`, `iban`), and administrative fields (`attivo`, `note`, `entity_uuid`), with `id_personale` as the integer primary key. A `UniqueConstraint` named `'ID_personale_unico'` enforces uniqueness on the combination of `sito` and `codice_fiscale`.

