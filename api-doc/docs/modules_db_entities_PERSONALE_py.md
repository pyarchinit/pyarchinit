# modules/db/entities/PERSONALE.py

## Overview

This file contains 3 documented elements.

## Classes

### PERSONALE

*No description available.*
Represents a personnel record associated with a specific site (`sito`), storing personal details (name, surname, date of birth, address, tax code), contact information (email, phone), and professional data (role, qualification, contract type, contract start/end dates, hourly and daily rates, IBAN). Each instance is uniquely identified by `id_personale` and automatically assigned a UUID (`entity_uuid`) if one is not explicitly provided. The `attivo` field indicates whether the personnel record is currently active, and `note` holds any additional free-text annotations.

**Inherits from**: object

#### Methods

##### __init__(self, id_personale, sito, nome, cognome, ruolo, qualifica, codice_fiscale, email, telefono, data_nascita, indirizzo, tipo_contratto, data_inizio_contratto, data_fine_contratto, tariffa_oraria, tariffa_giornaliera, iban, note, attivo, entity_uuid)

Initializes a `PERSONALE` instance representing a personnel record with all associated attributes. Accepts nineteen required positional parameters covering personal details (`nome`, `cognome`, `codice_fiscale`, `data_nascita`, `indirizzo`, `email`, `telefono`), organizational information (`sito`, `ruolo`, `qualifica`), contract data (`tipo_contratto`, `data_inizio_contratto`, `data_fine_contratto`, `tariffa_oraria`, `tariffa_giornaliera`, `iban`), and status fields (`attivo`, `note`, `id_personale`). The optional `entity_uuid` parameter is assigned the provided value if given, or a newly generated UUID4 string if omitted.

##### __repr__(self)

*No description available.*
Returns an unambiguous string representation of the `PERSONALE` instance in the format `<PERSONALE('id_personale','sito','nome','cognome')>`. The output includes the record's primary key (`id_personale`), site (`sito`), first name (`nome`), and last name (`cognome`), formatted as a tuple-like string enclosed in angle brackets. This method is intended for debugging and logging purposes, providing a concise summary of the object's key identifying attributes.

