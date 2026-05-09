# modules/utility/pyarchinit_exp_Periodosheet_pdf.py

## Overview

This file contains 28 documented elements.

## Classes

### NumberedCanvas_USsheet

A `canvas.Canvas` subclass that renders a multi-page PDF document with sequential page numbering for US (Unità Stratigrafica) sheet output. It accumulates page states during rendering by overriding `showPage`, then on `save` iterates through all saved states to stamp each page with a right-aligned "Pag. X di Y" label in Cambria 5pt at position 200 mm × 20 mm. The `define_position` method delegates to `page_position` to set the current page position.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

Initializes a `NumberedCanvas_USsheet` instance by delegating to the parent `canvas.Canvas.__init__` with all provided positional and keyword arguments. After the parent constructor completes, it initializes the `_saved_page_states` instance attribute as an empty list.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to `self.page_position(pos)` with the provided argument. This method serves as a named wrapper around `page_position`, accepting a single parameter `pos` that is passed through without modification.

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current canvas state to the `_saved_page_states` list. After preserving the state, it initializes a new page by calling `_startPage()`. This method is typically called to mark the end of a page before beginning content on the next one.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Sets the font to "Cambria" at size 5, then draws a right-aligned pagination string in the format `"Pag. <current_page> di <total_pages>"` at the fixed position `(200 mm, 20 mm)` on the canvas. The current page number is retrieved from the instance attribute `self._pageNumber`, while `page_count` represents the total number of pages passed as an argument. This method is intended for use on a vertically oriented "scheda us" layout of 200 mm × 20 mm.

### NumberedCanvas_USindex

*No description available.*
A custom ReportLab `canvas.Canvas` subclass that defers page rendering in order to support total page count pagination. It accumulates each page's state via an overridden `showPage` method, then finalises all pages on `save`, injecting a "Pag. X di Y" string (rendered in Cambria 5pt, right-aligned at 270 mm × 10 mm) onto each page via `draw_page_number`. This class is intended for use with US index documents requiring accurate total-page-count footers at save time.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

*No description available.*
Initializes a `NumberedCanvas_USindex` instance by delegating to the parent `canvas.Canvas` constructor with all provided positional and keyword arguments. After the parent initialization, it sets up the `_saved_page_states` instance attribute as an empty list.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to `self.page_position(pos)`. This method serves as a named wrapper around `page_position`, accepting a single positional argument `pos` that is forwarded without modification.

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current canvas state to the `_saved_page_states` list. After preserving the state, it initializes a new page by calling `_startPage()`. This method is typically called to mark the end of a page before beginning content on a new one.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Renders a right-aligned page number string onto the current canvas page using the "Cambria" font at size 5. The string is formatted as `"Pag. %d di %d"` (displaying the current page number and the total page count) and is positioned at coordinates `(270 mm, 10 mm)` from the origin. The `page_count` parameter specifies the total number of pages in the document.

### single_US_pdf_sheet

Represents a single stratigraphic unit (US — *Unità Stratigrafica*) record formatted as a PDF sheet. It is initialized with a 29-element data sequence covering site identification, stratigraphic and interpretive definitions, physical attributes, periodization, excavation metadata, and documentation. The `create_sheet()` method assembles all fields into a ReportLab `Table` object with a defined cell schema and style, after first unpacking stratigraphic relationships and documentation entries via `unzip_rapporti_stratigrafici()` and `unzip_documentazione()`.

**Inherits from**: object

#### Methods

##### __init__(self, data)

Initializes an instance by unpacking a sequential data structure into named instance attributes representing archaeological stratigraphic unit (US) record fields. The `data` parameter must be an ordered sequence of exactly 29 elements, each mapped positionally to attributes ranging from site identification fields (`sito`, `area`, `us`) through stratigraphic and interpretive descriptions, chronological phases, excavation metadata, physical characteristics, and documentation references. No validation or transformation is applied to the input values during assignment.

##### unzip_rapporti_stratigrafici(self)

Parses and distributes the stratigraphic relationship data stored in `self.rapporti` into individual instance attributes representing specific relationship types (e.g., `copre`, `coperto_da`, `taglia`, `tagliato_da`). The method evaluates the serialized `rapporti` string into a list, then maps each relationship term to its corresponding attribute using locale-aware group constants imported from `pyarchinit_i18n_stratigraphic`. For each recognized relationship, the associated value is either assigned directly to the attribute if it is currently empty, or appended as a comma-separated entry if the attribute already holds a value.

##### unzip_documentazione(self)

*No description available.*
Processes the `documentazione` attribute by evaluating its string representation as a Python literal and iterating over the resulting list of entries. For each entry, it formats the content into an HTML-friendly string: two-element entries are rendered as `"key: value<br/>"`, while single-element entries are rendered as `"value<br/>"`. The formatted output is appended to `documentazione_print`; if `documentazione` is empty, the method takes no action.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the `"%d-%m-%Y"` pattern (day-month-year, e.g., `"31-12-2024"`). The formatted date string is returned as the method's output.

##### create_sheet(self)

*No description available.*
Generates and returns a formatted PDF table (`Table`) representing a stratigraphic unit (US) record sheet. The method first extracts zipped stratigraphic and documentation resources, then constructs a series of styled `Paragraph` elements covering fields such as site identification, stratigraphic definitions, conservation state, inclusions, samples, stratigraphic relationships, periodization, and excavation metadata. These elements are arranged into an 18-row, 10-column cell schema with a defined table style including grid lines, cell spanning, and alignment rules, and the resulting `Table` object is returned.

### US_index_pdf_sheet

*No description available.*
A data container and PDF table-row generator for a single Stratigraphic Unit (US) record, used in archaeological index PDF reports. It initializes with a data array, extracting site, area, US identifier, stratigraphic definition, and raw stratigraphic relationships, then parses those relationships via `unzip_rapporti_stratigrafici` into typed class-level fields (`copre`, `coperto_da`, `taglia`, `tagliato_da`, `riempie`, `riempito_da`, `si_appoggia_a`, `gli_si_appoggia`, `uguale_a`, `si_lega_a`). The `getTable` method returns a list of styled `Paragraph` objects representing the unit's fields for use in a ReportLab table, while `makeStyles` returns a `TableStyle` defining grid and vertical alignment for that table.

**Inherits from**: object

#### Methods

##### __init__(self, data)

*No description available.*
Initializes a stratigraphic unit instance from a sequential data collection. Assigns the first four elements of `data` to `self.sito`, `self.area`, `self.us`, and `self.d_stratigrafica` respectively, and assigns the element at index 17 to `self.rapporti`.

##### unzip_rapporti_stratigrafici(self)

Parses and distributes the stratigraphic relationships stored in `self.rapporti` into their respective instance attributes. The method evaluates the serialized `rapporti` string, sorts the resulting list, and iterates over each two-element entry, appending the associated value (comma-separated if multiple) to the corresponding relationship field (`si_lega_a`, `uguale_a`, `copre`, `coperto_da`, `riempie`, `riempito_da`, `taglia`, `tagliato_da`, `si_appoggia_a`, `gli_si_appoggia`) based on a case-insensitive match of the relationship type label. If `self.rapporti` is empty or falsy, the method treats the relationship list as empty and performs no assignments.

##### getTable(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` objects representing the stratigraphic relationship fields of a stratigraphic unit (US). The method first configures a `Normal` paragraph style using `getSampleStyleSheet()` — setting font, size, spacing, and left alignment — then calls `self.unzip_rapporti_stratigrafici()` to populate the relationship attributes before constructing each labeled paragraph. The resulting list contains thirteen entries covering fields such as area, US identifier, stratigraphic definition, and all stratigraphic relationships (covers, cut by, fills, leans against, etc.).

##### makeStyles(self)

*No description available.*
Defines and returns a `TableStyle` object configured with two style directives applied across the entire table (from cell `(0, 0)` to `(-1, -1)`): a `GRID` style that draws black grid lines with a line width of `0.0`, and a `VALIGN` style that aligns cell content to the top. The method takes no parameters beyond `self` and returns the constructed `TableStyle` instance directly.

### generate_US_pdf

*No description available.*
Generates PDF documents related to Stratigraphic Units (US — *Unità Stratigrafiche*) for archaeological excavation records. The class provides two primary methods: `build_US_sheets`, which produces a multi-page A4 PDF of individual US record sheets from a list of records, and `build_index_US`, which produces a landscape-format index table of US records for a given excavation site, including a logo and formatted header. Output files are written to the directory defined by the `PDF_path` attribute, which is derived from the `PYARCHINIT_HOME` environment variable.

**Inherits from**: object

#### Methods

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year). The formatted date string is then returned to the caller.

##### build_US_sheets(self, records)

Builds a multi-page PDF document containing individual US (Stratigraphic Unit) sheets for a collection of records. Iterates over the provided `records`, creating a `single_US_pdf_sheet` for each entry and appending a `PageBreak` between sheets. The resulting document is written to a file named `'Scheda US.pdf'` in the instance's `PDF_path` directory, using `SimpleDocTemplate` with A4 page size and `NumberedCanvas_USsheet` as the canvas maker.

##### build_index_US(self, records, sito)

*No description available.*
Generates a PDF index document listing stratigraphic units ("Unità Stratigrafiche") for a given excavation site. The method constructs the document by assembling a logo, a heading paragraph containing the site name (`sito`), and a formatted table built from the provided `records` using `US_index_pdf_sheet` and fixed column widths. The resulting PDF is written to a file named `'Elenco US.pdf'` within the configured PDF output path, rendered on a landscape A4-sized page using `NumberedCanvas_USindex`.

