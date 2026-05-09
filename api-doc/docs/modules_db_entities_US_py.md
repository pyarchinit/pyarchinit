# modules/db/entities/US.py

## Overview

This file contains 4 documented elements.

## Classes

### US

## `US` Class

Represents a stratigraphic unit (Unità Stratigrafica) record in an archaeological information system, encapsulating all descriptive, interpretive, and physical attributes associated with a single unit. The class stores a comprehensive set of fields covering general stratigraphy, masonry unit (USM) characteristics, ICCD-aligned catalogue identifiers, dimensional measurements, material properties, and relational data. Each instance is assigned a unique identifier via `entity_uuid`, defaulting to a newly generated UUID if none is provided.

**Inherits from**: object

#### Methods

##### __init__(self, id_us, sito, area, us, d_stratigrafica, d_interpretativa, descrizione, interpretazione, periodo_iniziale, fase_iniziale, periodo_finale, fase_finale, scavato, attivita, anno_scavo, metodo_di_scavo, inclusi, campioni, rapporti, data_schedatura, schedatore, formazione, stato_di_conservazione, colore, consistenza, struttura, cont_per, order_layer, documentazione, unita_tipo, settore, quad_par, ambient, saggio, elem_datanti, funz_statica, lavorazione, spess_giunti, letti_posa, alt_mod, un_ed_riass, reimp, posa_opera, quota_min_usm, quota_max_usm, cons_legante, col_legante, aggreg_legante, con_text_mat, col_materiale, inclusi_materiali_usm, n_catalogo_generale, n_catalogo_interno, n_catalogo_internazionale, soprintendenza, quota_relativa, quota_abs, ref_tm, ref_ra, ref_n, posizione, criteri_distinzione, modo_formazione, componenti_organici, componenti_inorganici, lunghezza_max, altezza_max, altezza_min, profondita_max, profondita_min, larghezza_media, quota_max_abs, quota_max_rel, quota_min_abs, quota_min_rel, osservazioni, datazione, flottazione, setacciatura, affidabilita, direttore_us, responsabile_us, cod_ente_schedatore, data_rilevazione, data_rielaborazione, lunghezza_usm, altezza_usm, spessore_usm, tecnica_muraria_usm, modulo_usm, campioni_malta_usm, campioni_mattone_usm, campioni_pietra_usm, provenienza_materiali_usm, criteri_distinzione_usm, uso_primario_usm, tipologia_opera, sezione_muraria, superficie_analizzata, orientamento, materiali_lat, lavorazione_lat, consistenza_lat, forma_lat, colore_lat, impasto_lat, forma_p, colore_p, taglio_p, posa_opera_p, inerti_usm, tipo_legante_usm, rifinitura_usm, materiale_p, consistenza_p, rapporti2, doc_usv, entity_uuid)

Initializes a new instance of the `US` (Stratigraphic Unit) class, assigning all provided arguments directly to their corresponding instance attributes. The constructor accepts over 100 parameters covering the full range of archaeological recording fields, including site identification (`id_us`, `sito`, `area`, `us`), stratigraphic and interpretive descriptions, chronological data, excavation metadata, physical measurements, masonry unit (USM) attributes, ICCD catalogue alignment fields, and material characterization properties. The optional `entity_uuid` parameter is assigned its provided value if given, or a newly generated UUID string via `uuid.uuid4()` if omitted or falsy.

##### __repr__(self)

*No description available.*
A property that returns a formatted string representation of a US (Unità Stratigrafica) object instance. The string is structured as `<US(...)>` and interpolates all instance fields — spanning stratigraphic, interpretive, dimensional, chronological, masonry (USM), and cataloguing attributes — into a fixed-format template using `%`-style formatting. This property covers over 110 fields, including identifiers such as `id_us`, `sito`, `area`, and `us`, through to extended masonry and material descriptors such as `tipo_legante_usm`, `rifinitura_usm`, and `doc_usv`.

