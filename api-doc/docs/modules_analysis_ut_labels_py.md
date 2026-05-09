# modules/analysis/ut_labels.py

## Overview

This file contains 4 documented elements.

## Classes

### UTAnalysisLabels

Centralized labels for UT analysis in 7 languages.

#### Methods

##### get_labels(cls, lang)

Get all labels for a specific language.

Args:
    lang: Language code (IT, EN, DE, ES, FR, AR, CA)

Returns:
    Dictionary containing all label categories for the language

##### get_score_level(cls, score, lang)

Get the score level label based on the numeric score.

Args:
    score: Numeric score (0-100)
    lang: Language code

Returns:
    Localized score level string

