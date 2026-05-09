# modules/utility/pyarchinit_exp_Tmasheet_pdf.py

## Overview

This file contains 18 documented elements.

## Classes

### NumberedCanvas_TMAsheet

*No description available.*
A subclass of `canvas.Canvas` (ReportLab) that defers page rendering in order to add total page count information to each page. It accumulates page states via an overridden `showPage` method and, upon `save`, iterates through all saved states to render the page number footer before finalising the document. The page number is drawn as a centred string in Helvetica 8pt at the bottom of each A4 page, formatted as `"Pagina %d di %d"` (current page of total pages).

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

Initializes a `NumberedCanvas_TMAsheet` instance by delegating to the parent `canvas.Canvas.__init__` with all provided positional and keyword arguments. After the parent constructor completes, it initializes the `_saved_page_states` instance attribute as an empty list, which is used to track page states across the document.

##### showPage(self)

Saves the current page state by appending a copy of the instance's `__dict__` to the `_saved_page_states` list. After preserving the state, it calls `_startPage()` to initialize a new page. This deferred approach allows the total page count to be known at save time, enabling features such as "page X of Y" numbering.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Renders a centered page number indicator at the bottom of the current PDF page using an 8-point Helvetica font. The text is formatted as `"Pagina %d di %d"`, displaying the current page number (`self._pageNumber`) alongside the total page count (`page_count`), and is positioned horizontally at the center of an A4 page at a vertical offset of 20 mm from the bottom edge.

**Parameters:**
- `page_count` (`int`): The total number of pages in the document.

### generate_tma_pdf

Generates a PDF report ("Scheda TMA") for a single TMA (Tavola dei Materiali Archeologici) record by assembling structured sections covering basic information, localization, retrieval methods, analytical data, sources, compilation details, and associated materials. The output file is written to the `pyarchinit_PDF_folder` directory under the `PYARCHINIT_HOME` environment path, with the filename derived from the record's site and cassette identifiers. The class provides locale-specific entry points (`create_sheet_it`, `create_sheet_de`, `create_sheet_en`, `create_sheet_fr`, `create_sheet_es`, `create_sheet_ar`, `create_sheet_ca`), all of which currently delegate to the default `create_sheet` method.

#### Methods

##### __init__(self, data)

Initializes a `generate_tma_pdf` instance using a `data` sequence containing a TMA record, an optional list of materials, and an optional thumbnail path. Constructs the output PDF file name from the record's `sito` and `cassetta` attributes and resolves the full file path within the class-level `PDF_path` directory. Configures a set of ReportLab paragraph styles (`Center`, `Normal_small`, `Bold`, `Bold_large`) and two `TableStyle` objects — a standard grid style and a navy-blue-header variant — used for subsequent PDF generation.

##### datestrfdate(self)

Convert date for display

##### create_sheet(self)

Main method to create the PDF

##### create_sheet_it(self)

Italian version - same as default create_sheet

##### create_sheet_de(self)

German version of TMA sheet - uses Italian structure.
TODO: Add proper German translations for all labels.

##### create_sheet_en(self)

English version of TMA sheet - uses Italian structure.
TODO: Add proper English translations for all labels.

##### create_sheet_fr(self)

French version of TMA sheet - uses Italian structure.
TODO: Add proper French translations for all labels.

##### create_sheet_es(self)

Spanish version of TMA sheet - uses Italian structure.
TODO: Add proper Spanish translations for all labels.

##### create_sheet_ar(self)

Arabic version of TMA sheet - uses Italian structure.
TODO: Add proper Arabic translations for all labels.

##### create_sheet_ca(self)

Catalan version of TMA sheet - uses Italian structure.
TODO: Add proper Catalan translations for all labels.

## Functions

### single_TMA_pdf(data, lang)

Function to generate a single TMA PDF

Args:
    data: TMA data for the PDF
    lang: Language code ('it', 'de', 'en', 'fr', 'es', 'ar', 'ca')

**Parameters:**
- `data`
- `lang`

