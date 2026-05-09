# modules/db/entities/SCHEDAIND.py

## Overview

This file contains 4 documented elements.

## Classes

### SCHEDAIND

*No description available.*
A data model class representing an individual skeletal record (*scheda individuo*) in an archaeological context. It stores descriptive and observational attributes for a single individual, including site and stratigraphic unit identifiers (`sito`, `area`, `us`), recording metadata (`data_schedatura`, `schedatore`), biological profile fields (`sesso`, `eta_min`, `eta_max`, `classi_eta`), and skeletal position and orientation data (`posizione_scheletro`, `posizione_cranio`, `posizione_arti_superiori`, `posizione_arti_inferiori`, `orientamento_asse`, `orientamento_azimut`). Each instance is assigned a unique identifier via `entity_uuid`, generated automatically using `uuid.uuid4()` if not explicitly provided.

**Inherits from**: object

#### Methods

##### __init__(self, id_scheda_ind, sito, area, us, nr_individuo, data_schedatura, schedatore, sesso, eta_min, eta_max, classi_eta, osservazioni, sigla_struttura, nr_struttura, completo_si_no, disturbato_si_no, in_connessione_si_no, lunghezza_scheletro, posizione_scheletro, posizione_cranio, posizione_arti_superiori, posizione_arti_inferiori, orientamento_asse, orientamento_azimut, entity_uuid)

Initializes a new instance of the `SCHEDAIND` class, representing an individual skeletal record (scheda individuo) used in archaeological bioarchaeological documentation. All parameters are assigned directly to instance attributes, covering identification fields (`id_scheda_ind`, `sito`, `area`, `us`, `nr_individuo`), recording metadata (`data_schedatura`, `schedatore`), biological profile (`sesso`, `eta_min`, `eta_max`, `classi_eta`), skeletal context (`sigla_struttura`, `nr_struttura`, `completo_si_no`, `disturbato_si_no`, `in_connessione_si_no`), and osteological observations (`lunghezza_scheletro`, `posizione_scheletro`, `posizione_cranio`, `posizione_arti_superiori`, `posizione_arti_inferiori`, `orientamento_asse`, `orientamento_azimut`). Note that `classi_eta` is assigned the value of `eta_max` rather than its own parameter. The optional `entity_uuid` parameter is assigned as-is if provided; otherwise, a new UUID string is generated via `uuid.uuid4()`.

##### __repr__(self)

Returns a string representation of a `SCHEDAIND` instance, formatting all its fields into a structured, human-readable output enclosed in angle brackets. The representation includes the record's identifier, site, area, stratigraphic unit, individual number, scheduling metadata, biological profile fields (sex, age range, age class), structural references, skeletal condition flags, skeletal measurements, positional attributes, and orientation data. The format string uses `'%r'` for `lunghezza_scheletro` and `'%s'` for all other fields.

