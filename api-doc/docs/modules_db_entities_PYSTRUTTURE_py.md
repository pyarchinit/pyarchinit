# modules/db/entities/PYSTRUTTURE.py

## Overview

This file contains 4 documented elements.

## Classes

### PYSTRUTTURE

*No description available.*
**Authors:** Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>

A data model class representing an archaeological or architectural structure record. It stores identifying and chronological attributes — including site reference (`sito`), structure identifier (`id_strutt`), initial and final periods (`per_iniz`, `per_fin`), initial and final phases (`fase_iniz`, `fase_fin`), extended dating (`dataz_ext`), a textual description, geometry (`the_geom`), structure abbreviation (`sigla_strut`), and structure number (`nr_strut`). The `__repr__` property returns a formatted string representation of all twelve fields.

**Inherits from**: object

#### Methods

##### __init__(self, id, sito, id_strutt, per_iniz, per_fin, dataz_ext, fase_iniz, fase_fin, descrizione, the_geom, sigla_strut, nr_strut)

## `__init__` — `PYSTRUTTURE`

Initializes a new instance of the `PYSTRUTTURE` class by accepting twelve parameters and assigning each directly to the corresponding instance attribute. The parameters represent structural record data, including identifiers (`id`, `id_strutt`, `nr_strut`), site information (`sito`, `sigla_strut`), chronological range (`per_iniz`, `per_fin`, `fase_iniz`, `fase_fin`), extended dating (`dataz_ext`), a textual description (`descrizione`), and geometric data (`the_geom`). No validation or transformation is applied to any of the provided values during initialization.

##### __repr__(self)

*No description available.*
A property that returns a formatted string representation of a `PYSTRUTTURE` instance. The string includes the following fields in order: `id`, `sito`, `id_strutt`, `per_iniz`, `per_fin`, `dataz_ext`, `fase_iniz`, `fase_fin`, `descrizione`, `the_geom`, `sigla_strut`, and `nr_strut`, enclosed within `<PYSTRUTTURE(...)>` angle brackets. Note that this member is implemented as a `@property` rather than a standard method.

