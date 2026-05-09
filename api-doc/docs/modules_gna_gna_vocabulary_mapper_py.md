# modules/gna/gna_vocabulary_mapper.py

## Overview

This file contains 16 documented elements.

## Classes

### GNAVocabularyMapper

Maps PyArchInit vocabularies to GNA controlled vocabularies.

#### Methods

##### __init__(self, language)

Initialize vocabulary mapper.

Args:
    language: Language code ('it', 'en', etc.)

##### map_def_ut_to_ama(self, def_ut_value)

Map def_ut thesaurus value to GNA AMA code.

Args:
    def_ut_value: PyArchInit def_ut field value (internal code like 'scatter', 'site')

Returns:
    dict with 'code' and 'label' or None if not found

##### map_survey_type_to_mtdm(self, survey_type_value)

Map survey_type to GNA MTDM code.

##### map_vegetation_to_vgtc(self, vegetation_value)

Map vegetation_coverage to GNA VGTC code.

##### map_gps_method_to_gpmt(self, gps_value)

Map gps_method to GNA GPMT code.

##### map_surface_to_mcnd(self, surface_value)

Map surface_condition to GNA MCND code.

##### map_accessibility_to_accb(self, accessibility_value)

Map accessibility to GNA ACCB code.

##### map_weather_to_wthr(self, weather_value)

Map weather_conditions to GNA WTHR code.

##### map_geometry_type_to_ogt(self, geom_type)

Map QGIS geometry type to GNA OGT code.

Args:
    geom_type: QgsWkbTypes geometry type or string ('Point', 'Polygon', etc.)

Returns:
    dict with 'code' and 'label'

##### classify_potential(self, score)

Classify potential score to VRP category.

Args:
    score: Potential score (0-100)

Returns:
    dict with 'code', 'label', 'color', 'rgb', 'min', 'max'

##### classify_risk(self, score)

Classify risk score to VRD category.

Args:
    score: Risk score (0-100)

Returns:
    dict with 'code', 'label', 'color', 'rgb', 'min', 'max'

##### get_vrp_classification_scheme(self)

Get VRP classification scheme for heatmap generation.

Returns:
    dict suitable for classify_to_multipolygon method

##### get_vrd_classification_scheme(self)

Get VRD classification scheme for heatmap generation.

Returns:
    dict suitable for classify_to_multipolygon method

##### get_all_ama_codes(self)

Get all available AMA codes with labels.

