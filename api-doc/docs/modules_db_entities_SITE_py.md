# modules/db/entities/SITE.py

## Overview

This file contains 4 documented elements.

## Classes

### SITE

*No description available.*
Represents an archaeological or geographic site entity, encapsulating its identifying and descriptive attributes such as name, administrative location (nation, region, province, municipality), description, site type definition, and file system path. The class accepts an optional `entity_uuid` parameter; if not provided, a UUID4 string is automatically generated and assigned upon instantiation. The `__repr__` method returns a formatted string representation of the core site fields, excluding the `entity_uuid`.

**Inherits from**: object

#### Methods

##### __init__(self, id_sito, sito, nazione, regione, comune, descrizione, provincia, definizione_sito, sito_path, find_check, entity_uuid)

## `__init__` — `SITE`

Initializes a new instance of the `SITE` class with the provided site-related attributes. Accepts ten required parameters — `id_sito`, `sito`, `nazione`, `regione`, `comune`, `descrizione`, `provincia`, `definizione_sito`, `sito_path`, and `find_check` — along with an optional `entity_uuid` parameter. If `entity_uuid` is not supplied or evaluates to a falsy value, a new UUID4 string is automatically generated and assigned to `self.entity_uuid`.

##### __repr__(self)

*No description available.*
Returns an unambiguous string representation of the `SITE` object. The output is formatted as `<SITE('id_sito','sito', 'nazione',regione,'comune','descrizione', 'provincia', 'definizione_sito','sito_path', find_check)>`, embedding the values of all ten corresponding instance attributes. This method is intended for debugging and logging purposes, providing a complete snapshot of the site record's key fields.

