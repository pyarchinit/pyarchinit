# modules/db/entities/PYDOCUMENTAZIONE.py

## Overview

This file contains 4 documented elements.

## Classes

### PYDOCUMENTAZIONE

*No description available.*
**Authors:** Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>

A data model class representing a documentation record associated with an archaeological or geographic site. It stores six attributes — `pkuid`, `sito`, `nome_doc`, `tipo_doc`, `path_qgis_pj`, and `the_geom` — corresponding respectively to a primary key identifier, site name, document name, document type, QGIS project path, and geometry. The `__repr__` property returns a formatted string representation of all six fields.

**Inherits from**: object

#### Methods

##### __init__(self, pkuid, sito, nome_doc, tipo_doc, path_qgis_pj, the_geom)

## `__init__` — `PYDOCUMENTAZIONE`

Initializes a new instance of the `PYDOCUMENTAZIONE` class by assigning the provided arguments to their corresponding instance attributes. Accepts six parameters — `pkuid`, `sito`, `nome_doc`, `tipo_doc`, `path_qgis_pj`, and `the_geom` — and binds each directly to `self`. No validation or transformation is applied to the supplied values during initialization.

##### __repr__(self)

*No description available.*
A property that returns the official string representation of a `PYDOCUMENTAZIONE` instance. The returned string follows the format `<PYDOCUMENTAZIONE('pkuid','sito', 'nome_doc', 'tipo_doc', 'path_qgis_pj', 'the_geom')>`, embedding the values of those six fields. Note that this is implemented as a `@property` rather than a standard method.

