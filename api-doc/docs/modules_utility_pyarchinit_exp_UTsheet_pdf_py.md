# modules/utility/pyarchinit_exp_UTsheet_pdf.py

## Overview

This file contains 25 documented elements.

## Classes

### NumberedCanvas

Canvas with page numbers.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

Initializes a `NumberedCanvas` instance by extracting the `lang` keyword argument (defaulting to `'IT'` if not provided) and storing it as an instance attribute. Delegates the remaining initialization to the parent `canvas.Canvas.__init__` using all positional and keyword arguments. Initializes `_saved_page_states` as an empty list to track page states across the document.

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the entire instance state (`self.__dict__`) to the `_saved_page_states` list. After preserving the current page state, it calls `_startPage()` to initialize a new blank page for subsequent drawing operations.

##### save(self)

*No description available.*
Finalizes the document by iterating over all saved page states and restoring each one before rendering the page number and committing the page via `canvas.Canvas.showPage`. The total page count, derived from the length of `_saved_page_states`, is passed to `draw_page_number` for each page. Once all pages have been processed, `canvas.Canvas.save` is called to complete and write the document.

##### draw_page_number(self, page_count)

Renders a page number string in the bottom-right corner of the current page using the default font at size 8. The string is formatted as "{page} {current page number} {of} {total page count}", where the "page" and "of" labels are retrieved via `get_label` using the instance's language setting. The text is right-aligned at a horizontal position of `PAGE_WIDTH - MARGIN` and a vertical position of `MARGIN / 2`.

### single_UT_pdf_sheet

Generates a single UT PDF sheet with modern layout.

#### Methods

##### __init__(self, data)

Initialize with data tuple from database.

##### create_sheet(self, lang)

Create the PDF sheet elements.

### generate_pdf

Main PDF generator class.

#### Methods

##### __init__(self)

Initializes an instance of the class by ensuring the PDF output directory exists. If the path defined by `PDF_path` does not already exist on the filesystem, it creates the full directory tree using `os.makedirs`.

##### build_UT_sheets(self, records, lang)

Build PDF sheets for multiple UT records.

##### build_UT_sheets_en(self, records)

Build PDF sheets for multiple UT records (English).

##### build_UT_sheets_de(self, records)

Build PDF sheets for multiple UT records (German).

##### build_UT_sheets_fr(self, records)

Build PDF sheets for multiple UT records (French).

##### build_UT_sheets_es(self, records)

Build PDF sheets for multiple UT records (Spanish).

##### build_UT_sheets_ar(self, records)

Build PDF sheets for multiple UT records (Arabic).

##### build_UT_sheets_ca(self, records)

Build PDF sheets for multiple UT records (Catalan).

##### build_UT_list(self, records, lang)

Build a list/index of all UT records.

## Functions

### get_label(key, lang)

Get label for key in specified language.

**Parameters:**
- `key`
- `lang`

### make_header()

Create header with logo and title.

### make_section_header(text)

Create a section header.

**Parameters:**
- `text`

### make_field_row(fields, widths)

Create a row with label-value pairs.

**Parameters:**
- `fields`
- `widths`

### make_text_field(label, value)

Create a text field spanning full width.

**Parameters:**
- `label`
- `value`

### make_score_display(label, score, score_type)

Create a colored score display.

**Parameters:**
- `label`
- `score`
- `score_type`

