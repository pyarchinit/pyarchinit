# Tutorial 13: Thesaurus Management

## Introduction

The **Thesaurus** in PyArchInit is the centralized system for managing controlled vocabularies. It allows you to define and maintain the value lists used in all plugin forms, ensuring terminological consistency and facilitating searching.

### Main Functions

- Vocabulary management for each form
- Multilingual support
- Codes and extended descriptions
- GPT integration for suggestions
- CSV file import/export

---

## Accessing the Thesaurus

### Via Menu
1. **PyArchInit** menu in QGIS menu bar
2. Select **Thesaurus** (or **Thesaurus form**)

### Via Toolbar
1. Locate the PyArchInit toolbar
2. Click on the **Thesaurus** icon (book/dictionary)

---

## Interface Overview

### Main Areas

| # | Area | Description |
|---|------|-------------|
| 1 | DBMS Toolbar | Navigation, search, save |
| 2 | Table Selection | Choice of form to configure |
| 3 | Code Fields | Code, extension, type |
| 4 | Description | Detailed term description |
| 5 | Language | Language selection |
| 6 | Tools | CSV import, GPT suggestions |

---

## Thesaurus Fields

### Table Name

**Field**: `comboBox_nome_tabella`
**Database**: `nome_tabella`

Select the form for which to define values.

**Available tables:**
| Table | Description |
|-------|-------------|
| `us_table` | SU/WSU Form |
| `site_table` | Site Form |
| `periodizzazione_table` | Periodization |
| `inventario_materiali_table` | Materials Inventory |
| `pottery_table` | Pottery Form |
| `campioni_table` | Samples Form |
| `documentazione_table` | Documentation |
| `tomba_table` | Grave Form |
| `individui_table` | Individual Form |
| `fauna_table` | Archaeozoology |
| `ut_table` | UT Form |

### Code

**Field**: `comboBox_sigla`
**Database**: `sigla`

Short code/abbreviation for the term.

**Examples:**
- `WL` for Wall
- `SU` for Stratigraphic Unit
- `CR` for Ceramic

### Extended Code

**Field**: `comboBox_sigla_estesa`
**Database**: `sigla_estesa`

Complete form of the term.

**Examples:**
- `Perimeter wall`
- `Stratigraphic Unit`
- `Common ware`

### Description

**Field**: `textEdit_descrizione_sigla`
**Database**: `descrizione`

Detailed term description, definition, usage notes.

### Code Type

**Field**: `comboBox_tipologia_sigla`
**Database**: `tipologia_sigla`

Numeric code identifying the destination field.

**Code structure:**
```
X.Y where:
X = table number
Y = field number
```

**Examples for us_table:**
| Code | Field |
|------|-------|
| 1.1 | Stratigraphic definition |
| 1.2 | Formation mode |
| 1.3 | SU type |

### Language

**Field**: `comboBox_lingua`
**Database**: `lingua`

Term language.

**Supported languages:**
- IT (Italian)
- EN_US (English)
- DE (German)
- FR (French)
- ES (Spanish)
- AR (Arabic)
- CA (Catalan)

---

## Hierarchy Fields

### Parent ID

**Field**: `comboBox_id_parent`
**Database**: `id_parent`

Parent term ID (for hierarchical structures).

### Parent Code

**Field**: `comboBox_parent_sigla`
**Database**: `parent_sigla`

Parent term code.

### Hierarchy Level

**Field**: `spinBox_hierarchy`
**Database**: `hierarchy_level`

Level in hierarchy (0=root, 1=first level, etc.).

---

## Special Features

### GPT Suggestions

The "Suggestions" button uses OpenAI GPT to:
- Generate automatic descriptions
- Provide reference Wikipedia links
- Suggest definitions in archaeological context

**Usage:**
1. Select or enter a term in "Extended code"
2. Click "Suggestions"
3. Select GPT model
4. Wait for generation
5. Review and save

**Note:** Requires configured OpenAI API key.

### CSV Import

For SQLite database, vocabularies can be imported from CSV files.

**Required CSV format:**
```csv
nome_tabella,sigla,sigla_estesa,descrizione,tipologia_sigla,lingua
us_table,WL,Wall,Wall structure,1.3,EN_US
us_table,FL,Floor,Walking surface,1.3,EN_US
```

**Procedure:**
1. Click "Import CSV"
2. Select file
3. Confirm import
4. Verify imported data

---

## Operational Workflow

### Adding New Term

1. **Open Thesaurus**
   - Via menu or toolbar

2. **New record**
   - Click "New Record"

3. **Table selection**
   ```
   Table name: us_table
   ```

4. **Term definition**
   ```
   Code: WE
   Extended code: Well
   Code type: 1.3
   Language: EN_US
   ```

5. **Description**
   ```
   Structure dug into the ground for
   water supply. Generally circular
   in shape with stone or brick lining.
   ```

6. **Save**
   - Click "Save"

### Searching Terms

1. Click "New Search"
2. Fill in criteria:
   - Table name
   - Code or extended code
   - Language
3. Click "Search"
4. Navigate through results

### Modifying Existing Term

1. Search for term to modify
2. Modify necessary fields
3. Click "Save"

---

## Code Type Organization

### Recommended Structure

For each table, organize codes systematically:

**us_table (1.x):**
| Code | Field |
|------|-------|
| 1.1 | Stratigraphic definition |
| 1.2 | Formation mode |
| 1.3 | SU type |
| 1.4 | Consistency |
| 1.5 | Color |

**inventario_materiali_table (2.x):**
| Code | Field |
|------|-------|
| 2.1 | Find type |
| 2.2 | Material class |
| 2.3 | Definition |
| 2.4 | Conservation status |

**pottery_table (3.x):**
| Code | Field |
|------|-------|
| 3.1 | Form |
| 3.2 | Ware |
| 3.3 | Fabric |
| 3.4 | Surface treatment |

---

## Best Practices

### Terminological Consistency

- Always use the same terms for the same concepts
- Avoid undocumented synonyms
- Document adopted conventions

### Multilingual

- Create terms in all necessary languages
- Maintain correspondences between languages
- Use official translations when available

### Hierarchy

- Use hierarchical structure for related terms
- Clearly define levels
- Document relationships

### Maintenance

- Periodically review vocabularies
- Remove obsolete terms
- Update descriptions

---

## Troubleshooting

### Problem: Term not visible in ComboBoxes

**Cause:** Incorrect type code or non-matching language.

**Solution:**
1. Verify tipologia_sigla code
2. Check set language
3. Verify record is saved

### Problem: CSV import failed

**Cause:** Incorrect file format.

**Solution:**
1. Verify CSV structure
2. Check delimiters (comma)
3. Verify encoding (UTF-8)

### Problem: GPT suggestions not working

**Cause:** Missing or invalid API key.

**Solution:**
1. Verify API key configuration
2. Check internet connection
3. Verify OpenAI credit

---

## References

### Database

- **Table**: `pyarchinit_thesaurus_sigle`
- **Mapper class**: `PYARCHINIT_THESAURUS_SIGLE`
- **ID**: `id_thesaurus_sigle`

### Source Files

- **UI**: `gui/ui/Thesaurus.ui`
- **Controller**: `tabs/Thesaurus.py`

---

## Video Tutorial

### Vocabulary Management
**Duration**: 10-12 minutes
- Thesaurus structure
- Adding terms
- Code organization

[Video placeholder: video_thesaurus_gestione.mp4]

### Multilingual and Import
**Duration**: 8-10 minutes
- Language configuration
- CSV import
- GPT suggestions

[Video placeholder: video_thesaurus_avanzato.mp4]

---

*Last updated: January 2026*
*PyArchInit - Archaeological Data Management System*

---

## Interactive Animation

Explore the interactive animation to learn more about this topic.

[Open Interactive Animation](../../animations/pyarchinit_thesaurus_animation.html)
