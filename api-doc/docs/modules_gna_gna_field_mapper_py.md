# modules/gna/gna_field_mapper.py

## Overview

This file contains 6 documented elements.

## Classes

### GNAFieldMapper

Maps PyArchInit UT fields to GNA MOSI fields.

#### Methods

##### __init__(self, language)

Initialize field mapper.

Args:
    language: Language code for vocabulary translations

##### map_ut_record_to_mosi(self, ut_record, geometry)

Map a complete UT record to GNA MOSI fields.

Args:
    ut_record: UT database record (dict or SQLAlchemy object)
    geometry: Optional QgsGeometry for geometry type determination

Returns:
    dict with GNA MOSI field names and values

##### validate_mosi_record(self, mosi_record)

Validate a MOSI record against GNA constraints.

Args:
    mosi_record: Dict of MOSI field values

Returns:
    dict with 'valid' bool and 'errors' list

##### get_mopr_fields(self, project_info)

Map project information to MOPR fields.

Args:
    project_info: Dict with project metadata

Returns:
    dict with MOPR field values

