# modules/utility/pyarchinit_exp_UT_analysis_pdf.py

## Overview

This file contains 5 documented elements.

## Functions

### get_labels(lang)

Get labels for the specified language.

**Parameters:**
- `lang`

### get_score_level(score, lang)

Get the score level (low/medium/high) based on score value.

**Parameters:**
- `score`
- `lang`

### format_factor_list(contributions, factor_labels, lang)

Format factor contributions as a bulleted list.

**Parameters:**
- `contributions`
- `factor_labels`
- `lang`

### generate_analysis_pdf(file_path, record_data, potential_result, risk_result, lang, potential_map_path, risk_map_path)

Generate a professional PDF report for UT analysis.

Args:
    file_path: Output PDF file path
    record_data: Dictionary with UT record data
    potential_result: Dictionary from UTPotentialCalculator
    risk_result: Dictionary from UTRiskAssessor
    lang: Language code (IT, EN, DE, ES, FR, AR, CA)
    potential_map_path: Optional path to potential heatmap image
    risk_map_path: Optional path to risk heatmap image

**Parameters:**
- `file_path`
- `record_data`
- `potential_result`
- `risk_result`
- `lang`
- `potential_map_path`
- `risk_map_path`

