# modules/db/entities/PYSEZIONI.py

## Overview

This file contains 4 documented elements.

## Classes

### PYSEZIONI

*No description available.*
A data model class representing a section (*sezione*) record, encapsulating spatial and documentary attributes associated with an archaeological or survey site. Each instance stores a unique identifier (`id`), a section identifier (`id_sezione`), site and area references (`sito`, `area`), a description (`descr`), a geometry field (`the_geom`), and document metadata (`tipo_doc`, `nome_doc`). The class exposes a `__repr__` property that returns a formatted string representation of all eight fields.

**Inherits from**: object

#### Methods

##### __init__(self, id, id_sezione, sito, area, descr, the_geom, tipo_doc, nome_doc)

## `__init__` — `PYSEZIONI`

Initializes a new instance of the `PYSEZIONI` class by accepting eight parameters and assigning each directly to the corresponding instance attribute. The parameters are `id`, `id_sezione`, `sito`, `area`, `descr`, `the_geom`, `tipo_doc`, and `nome_doc`, which represent the section's identifier, section reference, site, area, description, geometry, document type, and document name respectively.

##### __repr__(self)

*No description available.*
**Type:** `property`

Returns a formatted string representation of a `PYSEZIONI` instance. The string follows the pattern `<PYSEZIONI('id','id_sezione', 'sito', 'area', 'descr', 'the_geom', 'tipo_doc', 'nome_doc')>`, embedding the instance's `id`, `id_sezione`, `sito`, `area`, `descr`, `the_geom`, `tipo_doc`, and `nome_doc` fields in order. Note that `__repr__` is implemented as a `property` rather than a standard method.

