# modules/db/entities/UT.py

## Overview

This file contains 4 documented elements.

## Classes

### UT

## `UT` Class

Represents a topographic unit (Unità Topografica) record in an archaeological survey system, encapsulating all data associated with a single surveyed location. The class stores 60 fields covering identification, geographic and administrative location, terrain and environmental characteristics, survey methodology, chronological interpretation, and documentation references. Extended fields introduced in v4.9.21 capture additional survey metadata (visibility, GPS method, surface condition, team members, etc.), while fields added in v4.9.67 store archaeological potential and risk analysis scores along with their factor breakdowns; a UUID is automatically generated for `entity_uuid` if none is provided.

**Inherits from**: object

#### Methods

##### __init__(self, id_ut, progetto, nr_ut, ut_letterale, def_ut, descrizione_ut, interpretazione_ut, nazione, regione, provincia, comune, frazione, localita, indirizzo, nr_civico, carta_topo_igm, carta_ctr, coord_geografiche, coord_piane, quota, andamento_terreno_pendenza, utilizzo_suolo_vegetazione, descrizione_empirica_suolo, descrizione_luogo, metodo_rilievo_e_ricognizione, geometria, bibliografia, data, ora_meteo, responsabile, dimensioni_ut, rep_per_mq, rep_datanti, periodo_I, datazione_I, interpretazione_I, periodo_II, datazione_II, interpretazione_II, documentazione, enti_tutela_vincoli, indagini_preliminari, visibility_percent, vegetation_coverage, gps_method, coordinate_precision, survey_type, surface_condition, accessibility, photo_documentation, weather_conditions, team_members, foglio_catastale, potential_score, risk_score, potential_factors, risk_factors, analysis_date, analysis_method, entity_uuid)

Initializes a `UT` (Unità Topografica) instance by assigning all provided arguments to their corresponding instance attributes. The first 42 parameters (indices 0–41) are required and cover core record data including identification, administrative location, cartographic references, geographic and planar coordinates, terrain and soil descriptions, survey methodology, bibliography, chronological periods, and documentation fields. Optional parameters introduced in v4.9.21+ (indices 42–52) capture extended survey details such as visibility, GPS method, and weather conditions, while optional analysis fields introduced in v4.9.67+ (indices 53–58) store archaeological potential and risk scores along with their factor breakdowns; `entity_uuid` (index 59) defaults to a newly generated UUID v4 if not provided.

##### __repr__(self)

*No description available.*
Returns an unambiguous string representation of the `UT` instance. The returned string follows the format `<UT(id_ut={self.id_ut}, progetto={self.progetto}, nr_ut={self.nr_ut})>`, exposing the instance's `id_ut`, `progetto`, and `nr_ut` attributes. This method is intended for debugging and logging purposes.

