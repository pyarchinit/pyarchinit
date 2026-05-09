# modules/analysis/ut_potential_calculator.py

## Overview

This file contains 7 documented elements.

## Classes

### UTPotentialCalculator

Calculates archaeological potential score for UT records.

The potential score ranges from 0-100 and is based on a weighted
combination of factors that indicate the likelihood of finding
archaeological remains in a given topographic unit.

#### Methods

##### __init__(self, db_manager, weights)

Initialize the potential calculator.

Args:
    db_manager: PyArchInit database manager instance
    weights: Optional custom weights dictionary

##### log_message(self, message, level)

Log message to QGIS if available.

##### calculate_potential(self, ut_record, geometry)

Calculate the archaeological potential score for a UT record.

Args:
    ut_record: Dictionary or object with UT data fields
    geometry: Optional QgsGeometry for spatial calculations

Returns:
    Dictionary containing:
        - total_score: Overall potential score (0-100)
        - factor_scores: Individual factor scores
        - factor_contributions: Weighted contributions
        - interpretation: Text interpretation of score
        - analysis_date: Timestamp of analysis

##### to_json(self, result)

Convert calculation result to JSON string.

Args:
    result: Dictionary from calculate_potential()

Returns:
    JSON string

##### from_json(json_str)

Parse JSON string to result dictionary.

Args:
    json_str: JSON string

Returns:
    Dictionary

