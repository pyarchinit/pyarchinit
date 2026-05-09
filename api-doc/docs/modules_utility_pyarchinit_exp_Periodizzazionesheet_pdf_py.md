# modules/utility/pyarchinit_exp_Periodizzazionesheet_pdf.py

## Overview

This file contains 33 documented elements.

## Classes

### NumberedCanvas_Periodizzazioneindex

*No description available.*
A subclass of `canvas.Canvas` that extends the ReportLab canvas with automatic page numbering support for the Periodizzazione index report. It accumulates page states during rendering by overriding `showPage`, then on `save` iterates over all saved states to annotate each page with a "Pag. X di Y" label drawn in Cambria 5pt font at the bottom-right of the page. The `draw_page_number` method renders the page indicator at coordinates `(270 * mm, 10 * mm)` using the total page count resolved only at save time.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

Initializes a `NumberedCanvas_Periodizzazioneindex` instance by delegating to the parent `canvas.Canvas.__init__` with all provided positional and keyword arguments. After the parent class is initialized, an empty list `_saved_page_states` is assigned to the instance to track page states.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to `self.page_position(pos)`. This method serves as a named wrapper around `page_position`, accepting a single positional argument `pos` and forwarding it without modification.

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current instance state to the `_saved_page_states` list. After preserving the page state, it calls `_startPage()` to initialize a new page for subsequent content.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Sets the font to "Cambria" at size 5, then draws a right-aligned page indicator string at the fixed position of 270 mm from the left and 10 mm from the bottom of the page. The string is formatted as `"Pag. %d di %d"`, displaying the current page number (`self._pageNumber`) and the total page count (`page_count`).

### NumberedCanvas_Periodizzazionesheet

*No description available.*
A custom ReportLab canvas subclass that extends `canvas.Canvas` to support total page count numbering across a multi-page document. It accumulates page states on each `showPage` call and, upon `save`, iterates over all saved states to render a page indicator string in the format `"Pag. X di Y"` at position `200mm × 20mm` using the "Cambria" font at size 5. The class also exposes a `define_position` method that delegates to `self.page_position`.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

Initializes a `NumberedCanvas_Periodizzazionesheet` instance by delegating to the parent `canvas.Canvas.__init__` method, passing through all positional and keyword arguments. After the parent initialization, it sets up an instance attribute `_saved_page_states` as an empty list.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to `self.page_position(pos)`. This method serves as a named wrapper around `page_position`, accepting a single positional argument `pos` and forwarding it without modification.

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current canvas state to the `_saved_page_states` list. After preserving the state, it initializes a new page by calling `_startPage()`. This method is typically called to mark the end of a page before beginning content on the next one.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Renders a page number indicator onto the current canvas page using the "Cambria" font at size 5. The string is drawn right-aligned at position `(200 mm, 20 mm)` and follows the format `"Pag. %d di %d"`, displaying the current page number (`self._pageNumber`) alongside the total page count (`page_count`).

**Parameters:**
- `page_count` *(int)*: The total number of pages in the document, used to construct the page indicator string.

### Periodizzazione_index_pdf_sheet

*No description available.*
A data container and PDF rendering class that represents a single periodization index record for report generation. It stores five archaeological periodization fields — `periodo`, `fase`, `cron_iniziale`, `cron_finale`, and `datazione_estesa` — extracted from a positional data sequence passed to the constructor. The class provides three localized variants of a table row builder (`getTable` for Italian, `getTable_de` for German, `getTable_en` for English), each returning a list of styled `Paragraph` objects, along with a `makeStyles` method that returns a `TableStyle` defining grid lines and top vertical alignment for use in ReportLab PDF tables.

**Inherits from**: object

#### Methods

##### __init__(self, data)

*No description available.*
Initializes a `Periodizzazione_index_pdf_sheet` instance by extracting and assigning periodization data from the provided `data` sequence. Maps indexed elements to the instance attributes `periodo` (index 1), `fase` (index 2), `cron_iniziale` (index 3), `cron_finale` (index 4), and `datazione_estesa` (index 5). Note that index 0 of `data` is not consumed by this initializer.

##### getTable(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` objects representing the chronological and phase data of the record. Each paragraph is styled using a `Normal` stylesheet entry configured with specific font (`Cambria`, size 7), spacing, and left alignment settings. The fields included are `periodo`, `fase`, `cron_iniziale`, `cron_finale`, and `datazione_estesa`; for `cron_iniziale` and `cron_finale`, an empty label is rendered if the value is `None`.

##### getTable_de(self)

*No description available.*
Generates a list of formatted `Paragraph` objects containing chronological and stratigraphic data with German-language labels, intended for use in a PDF report table. The method applies a `Normal` stylesheet with a font size of 7 and left alignment, and constructs paragraphs for period (`Period`), phase (`Phase`), initial chronology (`Anfangschronologie`), final chronology (`Letzte Chronologie`), and extended dating (`Erweiterte Datierung`). For `cron_iniziale` and `cron_finale`, the instance values are included in the label only when their string representation equals `"None"`; otherwise, an empty label is rendered.

##### getTable_en(self)

*No description available.*
Builds and returns a list of `Paragraph` objects representing English-language chronological data fields for use in a PDF table, using ReportLab's `getSampleStyleSheet` for styling. Each paragraph is formatted with a bold label and the corresponding instance attribute value, covering **Period**, **Phase**, **Start chronology**, **Final chronology**, and **Letteral datation**. For `cron_iniziale` and `cron_finale`, the method conditionally omits the attribute value from the paragraph content when the field is not `None`.

##### makeStyles(self)

*No description available.*
Constructs and returns a `TableStyle` object defining the visual formatting rules for a table. The style applies a black grid border across all cells (from the top-left `(0, 0)` to the bottom-right `(-1, -1)`) with a line thickness of `0.0`, and sets the vertical alignment of all cell content to `'TOP'`.

### single_Periodizzazione_pdf_sheet

*No description available.*
Represents a single periodization record as a formatted PDF sheet within the pyArchInit system. The class is initialized with a data sequence providing the fields `sito`, `periodo`, `fase`, `cron_iniziale`, `cron_finale`, `datazione_estesa`, and `descrizione`. It exposes three sheet-generation methods — `create_sheet` (Italian), `create_sheet_de` (German), and `create_sheet_en` (English) — each producing a ReportLab `Table` object containing the periodization data arranged in a structured, multi-row layout with a logo, header, site information, chronology fields, and description.

**Inherits from**: object

#### Methods

##### __init__(self, data)

*No description available.*
Initializes a `single_Periodizzazione_pdf_sheet` instance by unpacking a sequential `data` collection into seven instance attributes. The attributes assigned are `sito`, `periodo`, `fase`, `cron_iniziale`, `cron_finale`, `datazione_estesa`, and `descrizione`, mapped respectively to indices `0` through `6` of the provided `data` argument.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, e.g., `31-12-2024`). The formatted date string is then returned to the caller.

##### create_sheet(self)

*No description available.*
Generates and returns a formatted PDF table (`Table`) representing a periodization record sheet ("SCHEDA PERIODIZZAZIONE"). The method defines paragraph styles using `getSampleStyleSheet`, constructs labeled `Paragraph` elements for site, period, phase, chronology, and description fields, and loads a logo image from a path resolved via the `Connection` configuration or a default fallback. The resulting `Table` is built from a structured cell schema with explicit column spans and alignment rules applied through a defined table style.

##### create_sheet_de(self)

Generates and returns a formatted ReportLab `Table` object representing a period/phase data sheet with German-language labels. The method defines paragraph styles for normal and justified text using the Cambria font, constructs labelled `Paragraph` elements for fields such as site (`Ausgrabungsstätte`), period, phase, chronology, and description, and assembles them into a structured cell schema alongside a dynamically resolved logo image. A `table_style` list is applied to define grid lines, cell spanning, and vertical alignment across the five-row, ten-column layout.

##### create_sheet_en(self)

*No description available.*
Generates and returns a formatted English-language periodization data sheet as a ReportLab `Table` object. The method constructs a five-row layout containing a header with logo, site/period/phase identifiers, chronology labels, start and final chronology values with literal datation, and a description field. Cell spanning, grid styling, and text alignment are applied via a defined table style, with the logo path resolved from either a database connection setting or a default file in the home directory.

### generate_Periodizzazione_pdf

*No description available.*
Generates PDF documents for archaeological periodization (Periodizzazione) records, supporting Italian, German (`_de`), and English (`_en`) output variants. The class provides two categories of PDF output: individual record sheets built via `build_Periodizzazione_sheets` and its language variants, and summary index listings built via `build_index_Periodizzazione` and its language variants. Output files are written to the directory resolved from the `PYARCHINIT_HOME` environment variable under the `pyarchinit_PDF_folder` subdirectory, using `SimpleDocTemplate` with a numbered canvas maker for pagination.

**Inherits from**: object

#### Methods

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year). The formatted date string is then returned to the caller.

##### build_Periodizzazione_sheets(self, records)

Builds a multi-page PDF document containing periodizzazione (periodization) sheets from a collection of records. For each record, it instantiates a `single_Periodizzazione_pdf_sheet` object, generates its sheet content via `create_sheet()`, and appends a `PageBreak` between entries. The resulting document is written to a file named `'Scheda Periodizzazione.pdf'` in the configured `PDF_path` directory, using `SimpleDocTemplate` and `NumberedCanvas_Periodizzazionesheet` as the canvas maker.

##### build_Periodizzazione_sheets_de(self, records)

Builds a multi-page PDF document in German containing periodization sheets for a collection of records. For each record, it instantiates a `single_Periodizzazione_pdf_sheet` object, generates the German-language sheet via `create_sheet_de()`, and appends a `PageBreak` after each sheet. The resulting document is written to `formular_period.pdf` in the configured PDF output path, using `NumberedCanvas_Periodizzazionesheet` as the canvas maker.

##### build_Periodizzazione_sheets_en(self, records)

Builds an English-language PDF document containing periodization sheets for a collection of records. For each record in the provided `records` list, it instantiates a `single_Periodizzazione_pdf_sheet` object, generates an English sheet via `create_sheet_en()`, and appends a `PageBreak` after each sheet. The resulting elements are compiled into a `SimpleDocTemplate` PDF file named `form_Periodization.pdf`, written to the path defined by `self.PDF_path`, using `NumberedCanvas_Periodizzazionesheet` as the canvas maker.

##### build_index_Periodizzazione(self, records, sito)

Builds a PDF index document listing periodization records for a given excavation site. It resolves the logo path via a `Connection` object, constructs a formatted table from the provided `records` using `Periodizzazione_index_pdf_sheet`, and assembles the document with a logo, a heading displaying the site name, and the formatted table. The resulting PDF is written to `self.PDF_path` under the filename `'Elenco Periodizzazione.pdf'` using a landscape A3-style page size (`29 cm × 21 cm`) and the `NumberedCanvas_Periodizzazioneindex` canvas maker.

##### build_index_Periodizzazione_de(self, records, sito)

Generates a German-language PDF index document listing periodization records for a given excavation site. The method resolves the logo path via `Connection`, constructs a landscape-oriented A4 document (`29 cm × 21 cm`) containing the logo, a German-language heading with the site name and current date, and a formatted table built from `Periodizzazione_index_pdf_sheet` entries using the `getTable_de()` method. The resulting document is written to `Liste_period.pdf` in `self.PDF_path` using `SimpleDocTemplate` with `NumberedCanvas_Periodizzazioneindex` as the canvas maker.

##### build_index_Periodizzazione_en(self, records, sito)

Generates an English-language PDF index report of periodization records for a given site. The method resolves the logo path via a `Connection` object, builds a formatted table by iterating over the provided `records` using `Periodizzazione_index_pdf_sheet`, and assembles the document with a header containing the site name and current date. The resulting PDF is written to `list_periodization.pdf` within the configured `PDF_path` directory, using `SimpleDocTemplate` with a landscape A3-equivalent page size and `NumberedCanvas_Periodizzazioneindex` for page numbering.

