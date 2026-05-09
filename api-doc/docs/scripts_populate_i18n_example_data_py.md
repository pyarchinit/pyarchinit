# scripts/populate_i18n_example_data.py

## Overview

This file contains 19 documented elements.

## Functions

### translate_rel_term(term, lang)

Translate an Italian relationship term to the target language.

**Parameters:**
- `term`
- `lang`

### translate_unit_type(ut, lang)

Translate unit type abbreviation (only US/USM change).

**Parameters:**
- `ut`
- `lang`

### translate_d_interpretativa(val, lang)

Translate d_interpretativa, handling continuity references.

**Parameters:**
- `val`
- `lang`

### translate_long_text(text, lang)

Best-effort translation of long Italian text via term replacement.

**Parameters:**
- `text`
- `lang`

### safe_eval(text)

Safely parse a Python list literal stored as TEXT.

**Parameters:**
- `text`

### translate_inclusi(items, lang)

Translate inclusi list items.

**Parameters:**
- `items`
- `lang`

### translate_documentazione(items, lang)

Translate documentazione list items and Si/No values.

**Parameters:**
- `items`
- `lang`

### translate_rapporti(items, lang)

Translate rapporti: [['Copre', '2'], ...]

**Parameters:**
- `items`
- `lang`

### translate_rapporti2(items, lang)

Translate rapporti2: [['Copre', '2', 'US', 'Livellamento', '1-2'], ...]

**Parameters:**
- `items`
- `lang`

### translate_struttura_rel_term(term, lang)

Translate structure relationship term, checking extra dict first.

**Parameters:**
- `term`
- `lang`

### translate_struttura_materiali(items, lang)

Translate materiali_impiegati list: [['Ciottoli'], ['Laterizio'], ...]

**Parameters:**
- `items`
- `lang`

### translate_struttura_elementi(items, lang)

Translate elementi_strutturali: [['Tramezzo interno', '1'], ...]

**Parameters:**
- `items`
- `lang`

### translate_struttura_rapporti(items, lang, new_site)

Translate rapporti_struttura: [['term', 'site', 'sigla', 'num'], ...]

**Parameters:**
- `items`
- `lang`
- `new_site`

### translate_datazione_ext(val, lang)

Translate datazione_estesa using both PERIOD_DESC and PERIOD_DESC_EXTRA.

**Parameters:**
- `val`
- `lang`

### translate_field(val, dict_map, lang)

Generic single-value field translation.

**Parameters:**
- `val`
- `dict_map`
- `lang`

### insert_italian_example_data(conn)

Insert Italian example records for struttura, tomba, individui, pottery, inventario.

**Parameters:**
- `conn`

### get_column_names(cursor, table)

Get column names for a table.

**Parameters:**
- `cursor`
- `table`

### populate(db_path)

Populate the database with i18n example data.

**Parameters:**
- `db_path`

