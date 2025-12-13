# Pottery Decoration Fields - Guide and Suggestions

## Overview

Three new fields have been added to the pottery_table to improve AI-based similarity search and data organization:

1. **decoration_type** - The technique used to create the decoration
2. **decoration_motif** - The pattern or design of the decoration
3. **decoration_position** - Where on the vessel the decoration is located

## Field Values (Thesaurus)

### Decoration Type (11.14)
- PAINTED - Painted decoration
- INCISED - Incised decoration
- IMPRESSED - Impressed decoration
- STAMPED - Stamped decoration
- APPLIED - Applied decoration
- SLIPPED - Slipped/slip decoration
- BANDED - Banded decoration
- BURNISHED - Burnished decoration
- NONE - No decoration

### Decoration Motif (11.15)
- BANDS - Band motif
- LINES - Linear motif
- DOTS - Dotted motif
- GEOMETRIC - Geometric motif
- WAVE - Wave/wavy motif
- CROSS - Cross/crossed motif
- ZIGZAG - Zigzag motif
- TRIANGLES - Triangular motif
- CIRCLES - Circular motif
- FLORAL - Floral/vegetal motif
- ANIMAL - Animal/zoomorphic motif
- HUMAN - Human/anthropomorphic motif
- ABSTRACT - Abstract motif

### Decoration Position (11.16)
- RIM - Decoration on rim
- NECK - Decoration on neck
- SHOULDER - Decoration on shoulder
- BODY - Decoration on body
- HANDLE - Decoration on handle
- BASE - Decoration on base
- EXT - Decoration on external surface
- INT - Decoration on internal surface
- ALL - Decoration all over

## Analysis of Current Data

Based on analysis of the existing pottery_table data (ktm24.sqlite), here are the patterns found:

### Current Description Patterns

The `descrip_ex_deco` and `descrip_in_deco` fields contain valuable information that should be systematically captured:

**Examples found:**
- "Three horizontal bands under the rim black painted" -> Type: PAINTED, Motif: BANDS, Position: RIM
- "slipped red surface" -> Type: SLIPPED, Position: EXT
- "Four vertical lines black painted" -> Type: PAINTED, Motif: LINES, Position: BODY
- "wavy lines black painted" -> Type: PAINTED, Motif: WAVE
- "A frieze made of semicircular line red painted" -> Type: PAINTED, Motif: GEOMETRIC

### Recommendations for Data Entry

1. **Use Consistent Terminology**
   - Always specify color (black, red, brown) when applicable
   - Use standard terms: bands, lines, dots, wavy, geometric
   - Specify position: "under rim", "on body", "external surface"

2. **Separate Concerns**
   - Use `decoration_type` for HOW the decoration was made (painted, incised, slipped)
   - Use `decoration_motif` for WHAT the pattern looks like (bands, lines, dots)
   - Use `decoration_position` for WHERE on the vessel (rim, body, external)

3. **Keep Description Fields for Details**
   - Use `descrip_ex_deco` for detailed descriptions of external decorations
   - Include colors, number of elements, measurements
   - Use `descrip_in_deco` for internal decorations

### Example Migration

For a sherd described as: "Three horizontal bands under the rim black painted"
- **decoration_type**: PAINTED
- **decoration_motif**: BANDS
- **decoration_position**: RIM
- **descrip_ex_deco**: "Three horizontal black painted bands"

### Suggested Changes to Existing Data

Based on analysis, here's how to improve existing records:

1. **Records with "painted" in description:**
   - Set decoration_type = 'PAINTED'

2. **Records with "bands"/"banded" in description:**
   - Set decoration_motif = 'BANDS'

3. **Records with "lines"/"linear" in description:**
   - Set decoration_motif = 'LINES'

4. **Records with "wavy"/"wave"/"serpentine" in description:**
   - Set decoration_motif = 'WAVE'

5. **Records with "slipped"/"slip" in description:**
   - Set decoration_type = 'SLIPPED'

6. **Records with "under rim"/"on rim" in description:**
   - Set decoration_position = 'RIM'

7. **Records mentioning "inside"/"internal":**
   - Set decoration_position = 'INT'

8. **Records mentioning "outside"/"external":**
   - Set decoration_position = 'EXT'

## SQL Examples for Data Migration

### PostgreSQL

```sql
-- Set decoration_type to PAINTED where descrip_ex_deco or descrip_in_deco contains 'painted'
UPDATE pottery_table
SET decoration_type = 'PAINTED'
WHERE (LOWER(descrip_ex_deco) LIKE '%painted%'
   OR LOWER(descrip_in_deco) LIKE '%painted%')
   AND (decoration_type IS NULL OR decoration_type = '');

-- Set decoration_type to SLIPPED where description contains 'slipped' or 'slip'
UPDATE pottery_table
SET decoration_type = 'SLIPPED'
WHERE (LOWER(descrip_ex_deco) LIKE '%slip%'
   OR LOWER(descrip_in_deco) LIKE '%slip%')
   AND (decoration_type IS NULL OR decoration_type = '');

-- Set decoration_motif to BANDS where description contains 'band'
UPDATE pottery_table
SET decoration_motif = 'BANDS'
WHERE (LOWER(descrip_ex_deco) LIKE '%band%'
   OR LOWER(descrip_in_deco) LIKE '%band%')
   AND (decoration_motif IS NULL OR decoration_motif = '');

-- Set decoration_motif to LINES where description contains 'line'
UPDATE pottery_table
SET decoration_motif = 'LINES'
WHERE (LOWER(descrip_ex_deco) LIKE '%line%'
   OR LOWER(descrip_in_deco) LIKE '%line%')
   AND (decoration_motif IS NULL OR decoration_motif = '');

-- Set decoration_motif to WAVE where description contains 'wavy' or 'wave'
UPDATE pottery_table
SET decoration_motif = 'WAVE'
WHERE (LOWER(descrip_ex_deco) LIKE '%wav%'
   OR LOWER(descrip_in_deco) LIKE '%wav%')
   AND (decoration_motif IS NULL OR decoration_motif = '');

-- Set decoration_position to RIM where description contains 'rim'
UPDATE pottery_table
SET decoration_position = 'RIM'
WHERE (LOWER(descrip_ex_deco) LIKE '%rim%'
   OR LOWER(descrip_in_deco) LIKE '%rim%')
   AND (decoration_position IS NULL OR decoration_position = '');
```

### SQLite

```sql
-- Same queries work for SQLite, just use 'lower()' function
UPDATE pottery_table
SET decoration_type = 'PAINTED'
WHERE (lower(descrip_ex_deco) LIKE '%painted%'
   OR lower(descrip_in_deco) LIKE '%painted%')
   AND (decoration_type IS NULL OR decoration_type = '');
```

## Benefits for AI Similarity Search

With these structured fields, the AI similarity search will be able to:

1. **Better categorize decorations**: Find all painted pottery, all incised pottery, etc.
2. **Match decoration motifs**: Find pottery with similar band patterns, line patterns, etc.
3. **Filter by position**: Search for rim decorations vs. body decorations
4. **Combined searches**: Find "painted bands on rim" specifically

The new fields provide structured data that complements the free-text descriptions and significantly improves the accuracy of AI-powered similarity searches.
