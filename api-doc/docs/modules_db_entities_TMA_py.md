# modules/db/entities/TMA.py

## Overview

This file contains 4 documented elements.

## Classes

### TMA

*No description available.*
A data model class representing an archaeological material or artifact record, encapsulating fields related to site provenance, inventory classification, physical location, descriptive attributes, dating, and drawing references. Each instance stores identifiers such as `sito`, `area`, `localita`, `settore`, and `inventario` alongside descriptive and chronological fields including `deso`, `dtzg`, `dscd`, `dscu`, and drawing data (`drat`, `dran`, `draa`). A unique entity identifier is automatically assigned via `uuid.uuid4()` if no `entity_uuid` is provided at instantiation, and audit fields (`created_at`, `updated_at`, `created_by`, `updated_by`) are maintained for record tracking.

**Inherits from**: object

#### Methods

##### __init__(self, id, sito, area, localita, settore, inventario, ogtm, ldct, ldcn, vecchia_collocazione, cassetta, scan, saggio, vano_locus, dscd, dscu, rcgd, rcgz, aint, aind, dtzg, deso, nsc, ftap, ftan, drat, dran, draa, created_at, updated_at, created_by, updated_by, entity_uuid)

Initializes a new `TMA` instance by assigning all provided arguments to their corresponding instance attributes. Accepts 32 required positional parameters covering identification, location, classification, descriptive, and audit fields, plus an optional `entity_uuid` parameter. If `entity_uuid` is not supplied or evaluates to a falsy value, a new UUID4 string is automatically generated and assigned to `self.entity_uuid`.

##### __repr__(self)

Returns an unambiguous string representation of a `TMA` instance, formatted as `<TMA('...', '...', ...)>`. The output includes 32 fields in the following order: `id`, `sito`, `area`, `localita`, `settore`, `inventario`, `ogtm`, `ldct`, `ldcn`, `vecchia_collocazione`, `cassetta`, `scan`, `saggio`, `vano_locus`, `dscd`, `dscu`, `rcgd`, `rcgz`, `aint`, `aind`, `dtzg`, `deso`, `nsc`, `ftap`, `ftan`, `drat`, `dran`, `draa`, `created_at`, `updated_at`, `created_by`, and `updated_by`. All field values are interpolated as strings using `%` formatting.

