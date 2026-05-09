# modules/utility/pyarchinit_exp_Invlapsheet_pdf.py

## Overview

This file contains 18 documented elements.

## Classes

### NumberedCanvas_Invlapsheet

*No description available.*
A subclass of `canvas.Canvas` that extends the ReportLab canvas with multi-page awareness for inventory lap sheets. It defers page rendering by capturing each page's state in `_saved_page_states`, then replays all states at save time to inject a page number footer ("Pag. x di y") formatted in Cambria 5pt, right-aligned at coordinates 200 mm × 20 mm. The `save` method resolves the total page count before finalising the document, enabling accurate "page x of y" annotations across all pages.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

*No description available.*
Initializes a `NumberedCanvas_Invlapsheet` instance by delegating to the parent `canvas.Canvas` constructor with all provided positional and keyword arguments. After the parent initialization, it sets up an instance-level attribute `_saved_page_states` as an empty list, intended to track page state information across the canvas lifecycle.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to `self.page_position(pos)`. This method accepts a single argument, `pos`, and passes it unchanged to the underlying `page_position` call. The behavior and accepted values of `pos` depend on the implementation of `page_position`; see implementation for details.

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current instance state to the `_saved_page_states` list. After preserving the state, it calls `_startPage()` to initialize a new page for subsequent content.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Renders a page number string onto the current canvas page using the "Cambria" font at size 5. The string is formatted as `"Pag. %d di %d"` — combining the current page number (`self._pageNumber`) and the total page count (`page_count`) — and is drawn right-aligned at the position `200 mm` from the left and `20 mm` from the bottom of the page.

**Parameters:**
- `page_count` *(int)*: The total number of pages, used to construct the pagination label.

### single_Invlap_pdf_sheet

*No description available.*
A data container and PDF sheet generator for individual stone artefact (reperti lapidei) records within the pyArchInit archaeological information system. The class is initialized with a positional data sequence populating twenty fields — including site context, object typology, material, physical dimensions (`d_letto_posa`, `d_letto_attesa`, `toro`, `spessore`, `larghezza`, `lunghezza`, `h`), description, conservation state, comparisons, chronology, bibliography, and compiler — and exposes three sheet-generation methods (`create_sheet`, `create_sheet_de`, `create_sheet_en`) that each produce a ReportLab `Table` object representing the record layout in Italian, German, and English respectively. Each generated table follows an identical 19-row, 10-column grid schema incorporating a project logo, a dated header, and merged cells for all data fields.

#### Methods

##### __init__(self, data)

*No description available.*
Initializes a `single_Invlap_pdf_sheet` instance by unpacking a sequential `data` collection into twenty named instance attributes. Each index position in `data` maps to a specific field: `id_invlap` (index 0), `sito` (1), `scheda_numero` (2), `collocazione` (3), `oggetto` (4), `tipologia` (5), `materiale` (6), `d_letto_posa` (7), `d_letto_attesa` (8), `toro` (9), `spessore` (10), `larghezza` (11), `lunghezza` (12), `h` (13), `descrizione` (14), `lavorazione_e_stato_di_conservazione` (15), `confronti` (16), `cronologia` (17), `bibliografia` (18), and `compilatore` (19). The `data` argument must therefore contain at least 20 elements in the expected order for correct attribute assignment.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, e.g., `"31-12-2024"`). The formatted date string is then returned as the method's output.

##### create_sheet(self)

*No description available.*
Constructs and returns a formatted ReportLab `Table` object representing a stone artefact record sheet ("SCHEDA REPERTI LAPIDEI"). The method defines paragraph styles, builds labelled `Paragraph` elements for all record fields (including site context, material, object type, typology, dimensions, description, bibliography, and compiler), and loads a logo image from the configured path. All elements are arranged in a 19-row, 10-column cell schema with corresponding span and grid table styles applied.

##### create_sheet_de(self)

Builds and returns a German-language (`de`) PDF table sheet for a stone artefact form ("STEINARTEFAKTFORMULAR") using ReportLab's `Table`, `Paragraph`, and `Image` components. The method constructs a 19-row, 10-column layout containing labelled fields such as site context, material, typology, dimensions, description, bibliography, and compiler, with all labels and headings rendered in German. Cell spanning, grid styling, and top vertical alignment are applied via a defined `table_style`, and the institution logo is loaded from a path retrieved via a `Connection` object.

##### create_sheet_en(self)

Builds and returns a ReportLab `Table` object representing an English-language "STONE FORM" record sheet. The method constructs styled `Paragraph` elements for each field — including context, material, object, typology, dimensions, description, bibliography, and chronology — using left-aligned and justified `Normal` styles, and incorporates a logo image loaded from the configured logo path. The resulting 19-row, 10-column table is assembled with a defined cell schema, column width of 50 units, and a grid style that applies appropriate cell spans and top vertical alignment throughout.

### generate_reperti_pdf

*No description available.*
A PDF generation class responsible for producing archaeological stone/lapidary inventory report sheets from structured records. It resolves the output directory from the `PYARCHINIT_HOME` environment variable and writes paginated PDF documents to the `pyarchinit_PDF_folder` subdirectory. The class provides locale-specific build methods (`build_Invlap_sheets`, `build_Invlap_sheets_de`, `build_Invlap_sheets_en`) that iterate over records, delegate sheet creation to `single_Invlap_pdf_sheet`, and assemble the resulting elements into a `SimpleDocTemplate` document with page numbering via `NumberedCanvas_Invlapsheet`.

#### Methods

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year). The formatted date string is then returned to the caller.

##### build_Invlap_sheets(self, records)

Builds a multi-page PDF document containing inventory lapidary record sheets from a list of records. For each record, it instantiates a `single_Invlap_pdf_sheet` object, generates its sheet content via `create_sheet()`, and appends a `PageBreak` after each sheet. The resulting PDF is written to a file named `scheda_reperti_lapidei.pdf` located in `self.PDF_path`, using `SimpleDocTemplate` and `NumberedCanvas_Invlapsheet` as the canvas maker.

##### build_Invlap_sheets_de(self, records)

Builds a German-language inventory lap sheet PDF document from a list of records. For each record, it instantiates a `single_Invlap_pdf_sheet` object, generates a German sheet via `create_sheet_de()`, and appends a `PageBreak()` between entries. The resulting elements are compiled into a `SimpleDocTemplate` and written to a file named `Stoneformular.pdf` in the configured `PDF_path` directory, using `NumberedCanvas_Invlapsheet` as the canvas maker.

##### build_Invlap_sheets_en(self, records)

*No description available.*
Iterates over the provided `records` collection and generates an English-language PDF document containing one inventory lap sheet per page, separated by page breaks. Each individual sheet is created via `single_Invlap_pdf_sheet.create_sheet_en()` and assembled into a list of elements. The resulting document is written to a file named `Stone_form.pdf` in the path specified by `self.PDF_path`, built using `SimpleDocTemplate` with `NumberedCanvas_Invlapsheet` as the canvas maker.

