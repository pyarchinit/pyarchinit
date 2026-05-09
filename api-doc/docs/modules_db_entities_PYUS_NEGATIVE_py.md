# modules/db/entities/PYUS_NEGATIVE.py

## Overview

This file contains 4 documented elements.

## Classes

### PYUS_NEGATIVE

*No description available.*
A data model class representing a negative stratigraphic unit (US Negativa) record, authored by Serena Sensini and Enzo Cocca. It stores the following attributes upon instantiation: `pkuid`, `sito_n`, `area_n`, `us_n`, `tipo_doc_n`, `nome_doc_n`, and `the_geom`. The class exposes a `__repr__` property that returns a formatted string representation of these fields.

> **Note:** In the current implementation, only `self.pkuid` is correctly assigned as an instance attribute; the remaining parameters (`sito_n`, `area_n`, `us_n`, `tipo_doc_n`, `nome_doc_n`, `the_geom`) are assigned to local variables rather than instance attributes (`self`).

**Inherits from**: object

#### Methods

##### __init__(self, pkuid, sito_n, area_n, us_n, tipo_doc_n, nome_doc_n, the_geom)

## `__init__` — `PYUS_NEGATIVE`

Initializes a new instance of the `PYUS_NEGATIVE` class with the provided parameters: `pkuid`, `sito_n`, `area_n`, `us_n`, `tipo_doc_n`, `nome_doc_n`, and `the_geom`. Only `pkuid` is assigned to the instance (`self.pkuid`); the remaining parameters (`sito_n`, `area_n`, `us_n`, `tipo_doc_n`, `nome_doc_n`, `the_geom`) are assigned to local variables only and are not persisted on the instance.

##### __repr__(self)

*No description available.*
A read-only property that returns the official string representation of a `PYUS_NEGATIVE` instance. The returned string follows the format `<PYUS_NEGATIVE('pkuid','sito_n', 'area_n', 'us_n', 'tipo_doc_n', 'nome_doc_n', 'the_geom')>`, embedding the instance's `pkuid` field alongside the `sito_n`, `area_n`, `us_n`, `tipo_doc_n`, `nome_doc_n`, and `the_geom` values.

