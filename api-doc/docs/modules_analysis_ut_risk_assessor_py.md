# modules/analysis/ut_risk_assessor.py

## Overview

This file contains 7 documented elements.

## Classes

### UTRiskAssessor

Calculates archaeological risk score for UT records.

The risk score ranges from 0-100 and indicates the level of threat
to archaeological heritage from various sources including development,
erosion, and agricultural activities.

#### Methods

##### __init__(self, db_manager, weights, potential_calculator)

Initialize the risk assessor.

Args:
    db_manager: PyArchInit database manager instance
    weights: Optional custom weights dictionary
    potential_calculator: Optional UTPotentialCalculator for discovery probability

##### log_message(self, message, level)

Log message to QGIS if available.

##### calculate_risk(self, ut_record, geometry, potential_score)

Calculate the archaeological risk score for a UT record.

Args:
    ut_record: Dictionary or object with UT data fields
    geometry: Optional QgsGeometry for spatial calculations
    potential_score: Optional pre-calculated potential score (0-100)

Returns:
    Dictionary containing:
        - total_score: Overall risk score (0-100)
        - factor_scores: Individual factor scores
        - factor_contributions: Weighted contributions
        - interpretation: Text interpretation
        - recommendations: Risk mitigation recommendations
        - analysis_date: Timestamp of analysis

##### to_json(self, result)

Convert assessment result to JSON string.

Args:
    result: Dictionary from calculate_risk()

Returns:
    JSON string

##### from_json(json_str)

Parse JSON string to result dictionary.

Args:
    json_str: JSON string

Returns:
    Dictionary

