# modules/utility/pyarchinit_exp_Documentazionesheet_pdf.py

## Overview

This file contains 33 documented elements.

## Classes

### NumberedCanvas_Documentazionesheet

*No description available.*
A subclass of `canvas.Canvas` that extends ReportLab's canvas with multi-page tracking and automatic page numbering for documentation sheets. It accumulates page states on each `showPage` call and, upon `save`, iterates over all saved states to render a right-aligned page indicator in the format `"Pag. X di Y"` at position `(200 mm, 20 mm)` using the Cambria font at 5pt. The class also exposes a `define_position` method that delegates to `self.page_position`.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

## `__init__` Method

Initializes a `NumberedCanvas_Documentazionesheet` instance by delegating to the parent `canvas.Canvas` constructor with all provided positional and keyword arguments. After the parent initialization, it sets up an instance-level attribute `_saved_page_states` as an empty list, which is used to track page state information across the canvas lifecycle.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to the `page_position` method with the provided `pos` argument. This method serves as a named wrapper, offering a semantically explicit interface for defining the position on the current page.

**Parameters:**
- `pos` — The position value passed to `page_position`. See implementation for accepted types and format.

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current canvas state to the `_saved_page_states` list. After preserving the state, it initializes a new page by calling `_startPage()`.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Renders a right-aligned page number string onto the current canvas page using the "Cambria" font at size 5. The text is drawn at position `(200 mm, 20 mm)` and follows the format `"Pag. %d di %d"`, displaying the current page number (`self._pageNumber`) alongside the total page count (`page_count`).

**Parameters:**
- `page_count` (`int`): The total number of pages in the document, used to construct the pagination label.

### NumberedCanvas_Documentazioneindex

*No description available.*
A subclass of `canvas.Canvas` that provides paginated PDF rendering with total page count support for documentation index output. It accumulates page states during document generation via `showPage`, then iterates over all saved states during `save` to stamp each page with a "Pag. X di Y" string rendered in Cambria 5pt font at position `(270mm, 10mm)`. The `define_position` method delegates to `self.page_position`, and page numbering is finalized only at save time, once the total page count is known.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

*No description available.*
Initializes a `NumberedCanvas_Documentazioneindex` instance by delegating to the parent `canvas.Canvas` constructor with all provided positional and keyword arguments. After the parent initialization, it sets up an instance attribute `_saved_page_states` as an empty list.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to `self.page_position(pos)`. This method serves as a named wrapper around `page_position`, accepting a single positional argument `pos` and forwarding it without modification.

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current canvas state to the `_saved_page_states` list. After preserving the state, it initializes a new page by calling `_startPage()`. This method is typically called to mark the end of a page before proceeding to define content for the next one.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Renders a right-aligned page number string onto the canvas at a fixed position of 270 mm from the left and 10 mm from the bottom of the page. The text is formatted as `"Pag. %d di %d"` using the current page number (`self._pageNumber`) and the total page count (`page_count`), rendered in the "Cambria" font at size 5.

**Parameters:**
- `page_count` (`int`): The total number of pages in the document.

### single_Documentazione_pdf_sheet

*No description available.*
Represents a single documentation record sheet for PDF generation within the pyarchinit archaeological information system. The class is initialized with a data sequence mapping to eight fields — `sito`, `nome_doc`, `data`, `tipo_documentazione`, `sorgente`, `scala`, `disegnatore`, and `note` — and provides three locale-specific sheet rendering methods (`create_sheet` for Italian, `create_sheet_de` for German, and `create_sheet_en` for English). Each rendering method constructs and returns a ReportLab `Table` object composed of styled `Paragraph` elements and a dynamically resolved logo image, laid out in a five-row, ten-column grid schema.

#### Methods

##### __init__(self, data)

## `__init__` Method — `single_Documentazione_pdf_sheet`

Initializes a `single_Documentazione_pdf_sheet` instance by unpacking a sequential `data` collection into eight named instance attributes. The assigned attributes are `sito` (index 0), `nome_doc` (index 1), `data` (index 2), `tipo_documentazione` (index 3), `sorgente` (index 4), `scala` (index 5), `disegnatore` (index 6), and `note` (index 7). The element at index 8 is present in the source but commented out and therefore not assigned.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, e.g., `"31-12-2024"`). The formatted date string is then returned to the caller.

##### create_sheet(self)

*No description available.*
Builds and returns a formatted ReportLab `Table` object representing a documentation record sheet ("SCHEDA DOCUMENTAZIONE"). The method defines two paragraph styles (`styNormal` and `styDescrizione`) using Cambria font at size 7, then constructs labeled `Paragraph` elements for fields including site (`sito`), document name (`nome_doc`), date (`data`), documentation type (`tipo_documentazione`), source (`sorgente`), scale (`scala`), draughtsman (`disegnatore`), and notes (`note`), alongside a logo image loaded from a path resolved via the `Connection` class or a default location. These elements are arranged in a five-row cell schema with defined column spans, grid styling, and vertical alignment applied through a table style list before the completed `Table` is returned.

##### create_sheet_de(self)

*No description available.*
Generates a German-language PDF table sheet for documentation records using ReportLab. The method constructs styled `Paragraph` elements for fields such as site (`Ausgrabungsstätte`), documentation type (`Documentationtyp`), source (`Quelle`), scale (`Maßstab`), draughtsman (`Zeichner`), date (`Datum`), and notes, alongside a dynamically resolved logo image. It assembles these elements into a five-row `Table` with defined column widths, cell spanning, and grid styling, then returns the resulting `Table` object.

##### create_sheet_en(self)

*No description available.*
Generates and returns a formatted ReportLab `Table` object representing an English-language documentation form sheet. The method constructs a five-row layout containing fields for site, documentation name, date, documentation type, source, scale, draftsman, and notes, along with a header paragraph and a logo image loaded from a configurable path. Cell spanning and grid styling are applied via a defined table style, with all column widths set to 50 units.

### Documentazione_index_pdf_sheet

*No description available.*
Represents a single documentation index record for PDF sheet generation, encapsulating fields such as site (`sito`), documentation name (`nome_doc`), date (`data`), documentation type (`tipo_documentazione`), source (`sorgente`), scale (`scala`), drafter (`disegnatore`), and notes (`us`), populated from a positional data sequence.

Provides three locale-specific table-rendering methods — `getTable()` (Italian), `getTable_de()` (German), and `getTable_en()` (English) — each returning a list of `Paragraph` objects with bold field labels and their corresponding values, formatted using a `Normal` stylesheet style at 7pt font size.

The `makeStyles()` method returns a `TableStyle` applying a full grid border and top vertical alignment across all cells, intended for use when embedding the generated data list into a ReportLab PDF table.

#### Methods

##### __init__(self, data)

Initializes a `Documentazione_index_pdf_sheet` instance by unpacking a sequential data list into named instance attributes representing documentation record fields. The assigned attributes are `sito` (site), `nome_doc` (documentation name), `data` (date), `tipo_documentazione` (documentation type), `sorgente` (source), `scala` (scale), `disegnatore` (draughtsman), and `us` (notes), mapped from indices 0 through 6 and 8 of the input list. Note that index 7 of the input list is skipped, and the `nr_cassa` field (index 8) is present in the source but commented out.

##### getTable(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` objects representing documentation record fields for use in a ReportLab-generated table. Each field — type (`tipo_documentazione`), documentation name (`nome_doc`), scale (`scala`), source (`sorgente`), date (`data`), drafter (`disegnatore`), and notes (`us`) — is rendered with a bold label and its corresponding instance value, or an empty label if the value is an empty string. All paragraphs share a common `Normal` style configured with 7pt Cambria font, left alignment, and 20-unit spacing before and after.

##### getTable_de(self)

*No description available.*
Generates a list of formatted `Paragraph` objects containing documentation metadata fields rendered in German labels, using ReportLab's sample stylesheet. Each field — including type (`Typ`), document name (`Nomen documentation`), scale (`Maßstab`), source (`Quelle`), date (`Datum`), draughtsman (`Zeichner`), and notes (`Notes`) — is conditionally populated with the corresponding instance attribute value or left with an empty body if the attribute is an empty string. The method returns a list of these `Paragraph` objects intended for use in table construction.

##### getTable_en(self)

*No description available.*
Builds and returns a list of `Paragraph` objects representing documentation record fields with English-language labels, formatted using a `Normal` style sheet with a font size of 7, left alignment, and defined spacing. Each field — **Type**, **Documentation name**, **Scale**, **Source**, **Date**, **Draftman**, and **Note** — is rendered as a bold label followed by the corresponding instance attribute value, or left empty if the attribute holds an empty string. The returned list is intended for use as row or cell data within a ReportLab table.

##### makeStyles(self)

*No description available.*
Constructs and returns a `TableStyle` object defining the visual formatting rules for a table. The style applies a black grid border with a line weight of `0.0` across all cells (from `(0, 0)` to `(-1, -1)`) and sets the vertical alignment of all cell content to `'TOP'`.

### generate_documentazione_pdf

*No description available.*
A PDF generation class for archaeological documentation records within the pyarchinit system. It provides methods to build individual documentation record sheets (`build_Documentazione_sheets`, `build_Documentazione_sheets_de`, `build_Documentazione_sheets_en`) and tabular index documents (`build_index_Documentazione`, `build_index_Documentazione_de`, `build_index_Documentazione_en`) in three languages — Italian, German, and English. Output PDF files are written to the directory defined by `PDF_path`, which is derived from the `PYARCHINIT_HOME` environment variable.

#### Methods

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, e.g., `"31-12-2024"`). The formatted date string is then returned to the caller.

##### build_Documentazione_sheets(self, records)

Iterates over a list of records and generates a single PDF document named `'Scheda Documentazione.pdf'` by building one sheet per record using `single_Documentazione_pdf_sheet`. Each sheet is created via `create_sheet()` and followed by a `PageBreak()` element before being assembled into a `SimpleDocTemplate`. The resulting PDF is written to the file path defined by `self.PDF_path` and built with `NumberedCanvas_Documentazionesheet` as the canvas maker.

##### build_Documentazione_sheets_de(self, records)

Builds a multi-page PDF documentation form file named `'Dodumentation_formular.pdf'` in the directory specified by `self.PDF_path`. It iterates over the provided `records` sequence, creating a `single_Documentazione_pdf_sheet` for each record and appending the resulting sheet followed by a `PageBreak` to the elements list. The compiled elements are then written to the output file using `SimpleDocTemplate` with `NumberedCanvas_Documentazionesheet` as the canvas maker.

##### build_Documentazione_sheets_en(self, records)

Generates a multi-page PDF document named `Documentation_form.pdf` from a list of records in English. For each record, it instantiates a `single_Documentazione_pdf_sheet` object, calls its `create_sheet()` method to produce a page element, and appends a `PageBreak` after each sheet. The resulting document is built using `SimpleDocTemplate` with `NumberedCanvas_Documentazionesheet` as the canvas maker and written in binary format to the path defined by `self.PDF_path`.

##### build_index_Documentazione(self, records, sito)

Builds a PDF index document listing documentation records for a given excavation site. It resolves the logo path via a `Connection` object (falling back to a default `logo.jpg` if no custom path is configured), constructs a formatted table from the provided `records` using `Documentazione_index_pdf_sheet` and `Table`, and assembles the final document with a heading that includes the `sito` (site) name. The resulting PDF is written to `self.PDF_path` under the filename `'Elenco Documentazione.pdf'` using a landscape A3-style page size (`29 cm × 21 cm`) and the `NumberedCanvas_Documentazioneindex` canvas maker.

##### build_index_Documentazione_de(self, records, sito)

Generates a German-language PDF index document ("LISTE DOCUMENTATION") for site documentation records. It resolves the logo path from the database connection or falls back to a default, constructs a styled document containing the logo, a heading with the site name (`sito`) and current date, and a formatted table built from the provided `records` using `Documentazione_index_pdf_sheet`. The resulting PDF is written to `liste_documentation.pdf` within the configured PDF output path, rendered on A4-landscape pages (`29 cm × 21 cm`) using `NumberedCanvas_Documentazioneindex`.

##### build_index_Documentazione_en(self, records, sito)

Generates a PDF index document listing documentation records in English for a given site. The method resolves the logo path from the database connection settings, constructs a formatted table of documentation entries using `Documentazione_index_pdf_sheet`, and assembles the final document with a header containing the site name and current date. The resulting PDF is written to `documentation_list.pdf` in the configured PDF output path, rendered in landscape A3 format using `NumberedCanvas_Documentazioneindex` for page numbering.

