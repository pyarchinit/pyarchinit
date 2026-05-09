# modules/utility/pyarchinit_i18n_stratigraphic.py

## Overview

This file contains 18 documented elements.

## Functions

### get_unit_type_items(lang)

Return full tuple of items for the unit-type picker dialog.

**Parameters:**
- `lang`

### is_us_type(abbrev)

Check if *abbrev* is any language's US equivalent.

**Parameters:**
- `abbrev`

### is_usm_type(abbrev)

Check if *abbrev* is any language's USM equivalent.

**Parameters:**
- `abbrev`

### is_any_unit_prefix(text)

Check if *text* starts with any known US or USM abbreviation.

**Parameters:**
- `text`

### get_unit_type_label(unit_type, lang)

Return a localized label for *unit_type* (used by change_label).

**Parameters:**
- `unit_type`
- `lang`

### get_relationship_values(lang)

Return the full list for combobox delegates (10 terms + symbols).

**Parameters:**
- `lang`

### get_inverse_relationship(term)

Return the inverse/reciprocal of *term*. Falls back to *term* itself.

**Parameters:**
- `term`

### is_covers_group(term)

Term is any language's 'Covers' equivalent.

**Parameters:**
- `term`

### is_covered_by_group(term)

Term is any language's 'Covered by' equivalent.

**Parameters:**
- `term`

### is_fills_group(term)

Term is any language's 'Fills' equivalent.

**Parameters:**
- `term`

### is_filled_by_group(term)

Term is any language's 'Filled by' equivalent.

**Parameters:**
- `term`

### is_cuts_group(term)

Term is any language's 'Cuts' equivalent.

**Parameters:**
- `term`

### is_cut_by_group(term)

Term is any language's 'Cut by' equivalent.

**Parameters:**
- `term`

### is_contemporary_group(term)

Term is any language's 'Same as' equivalent.

**Parameters:**
- `term`

### is_connected_group(term)

Term is any language's 'Connected to' equivalent.

**Parameters:**
- `term`

### is_abuts_group(term)

Term is any language's 'Abuts' equivalent.

**Parameters:**
- `term`

### is_supports_group(term)

Term is any language's 'Supports' equivalent.

**Parameters:**
- `term`

