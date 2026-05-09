# modules/db/entities/TAFONOMIA.py

## Overview

This file contains 4 documented elements.

## Classes

### TOMBA

*No description available.*
A data model class representing an archaeological burial record (Italian: *tomba* = tomb). It stores a comprehensive set of attributes describing a burial context, including structural identifiers (`id_tomba`, `sito`, `nr_scheda_taf`, `sigla_struttura`, `nr_struttura`, `nr_individuo`), funerary rite and depositional details (`rito`, `descrizione_taf`, `interpretazione_taf`), skeletal position and condition (`posizione_scheletro`, `posizione_cranio`, `posizione_arti_superiori`, `posizione_arti_inferiori`, `completo_si_no`, `disturbato_si_no`, `in_connessione_si_no`), grave goods (`corredo_presenza`, `corredo_tipo`, `corredo_descrizione`), and chronological data (`periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`, `datazione_estesa`). The `__repr__` method returns a formatted string representation of all instance attributes.

**Inherits from**: object

#### Methods

##### __init__(self, id_tomba, sito, nr_scheda_taf, sigla_struttura, nr_struttura, nr_individuo, rito, descrizione_taf, interpretazione_taf, segnacoli, canale_libatorio_si_no, oggetti_rinvenuti_esterno, stato_di_conservazione, copertura_tipo, tipo_contenitore_resti, orientamento_asse, orientamento_azimut, corredo_presenza, corredo_tipo, corredo_descrizione, lunghezza_scheletro, posizione_scheletro, posizione_cranio, posizione_arti_superiori, posizione_arti_inferiori, completo_si_no, disturbato_si_no, in_connessione_si_no, caratteristiche, periodo_iniziale, fase_iniziale, periodo_finale, fase_finale, datazione_estesa, misure_tomba)

Initializes a new instance of the `TOMBA` class, representing an archaeological burial record, by assigning all 35 provided parameters to their corresponding instance attributes. The parameters capture comprehensive burial data including identification fields (`id_tomba`, `sito`, `nr_scheda_taf`, `sigla_struttura`, `nr_struttura`, `nr_individuo`), funerary characteristics (`rito`, `descrizione_taf`, `interpretazione_taf`, `segnacoli`, `canale_libatorio_si_no`, `oggetti_rinvenuti_esterno`, `stato_di_conservazione`, `copertura_tipo`, `tipo_contenitore_resti`), spatial orientation (`orientamento_asse`, `orientamento_azimut`), grave goods (`corredo_presenza`, `corredo_tipo`, `corredo_descrizione`), skeletal position and condition (`lunghezza_scheletro`, `posizione_scheletro`, `posizione_cranio`, `posizione_arti_superiori`, `posizione_arti_inferiori`, `completo_si_no`, `disturbato_si_no`, `in_connessione_si_no`, `caratteristiche`), and chronological data (`periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`, `datazione_estesa`, `misure_tomba`). Each parameter is stored directly as an instance attribute with the same name, indexed in comments from 0 through 20 for the first 21 fields.

##### __repr__(self)

Returns an unambiguous string representation of a `TOMBA` instance, formatting all fields of the object into a structured, human-readable string enclosed in angle brackets. The output includes all tomb-related attributes such as identifiers, site information, burial rite, skeletal position, grave goods, structural details, chronological data, and measurements. The format string uses `%d` for integer fields (e.g., `id_tomba`, `nr_struttura`, period and phase values) and `%s`/`%r` for string and mixed-type fields respectively.

