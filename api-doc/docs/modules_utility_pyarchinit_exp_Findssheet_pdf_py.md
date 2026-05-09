# modules/utility/pyarchinit_exp_Findssheet_pdf.py

## Overview

This file contains 83 documented elements.

## Classes

### NumberedCanvas_Findssheet

*No description available.*
A subclass of `canvas.Canvas` that extends the ReportLab canvas with multi-page awareness for finds sheet documents. It defers page rendering by capturing each page's state in `_saved_page_states` during `showPage()`, then iterates over all saved states at `save()` time to retroactively draw a page number indicator ("Pag. X di Y") on every page. The page number string is rendered right-aligned at coordinates `(200 mm, 20 mm)` using the "Cambria" font at size 5.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

*No description available.*
Initializes a `NumberedCanvas_Findssheet` instance by delegating to the parent `canvas.Canvas` constructor with all provided positional and keyword arguments. After the parent initialization, it sets up an empty list `_saved_page_states` to track page state data throughout the canvas lifecycle.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to `self.page_position(pos)`. This method serves as a named wrapper around `page_position`, accepting a single positional argument `pos` that is forwarded without modification.

##### showPage(self)

*No description available.*
Finalizes the current page by saving its state to the `_saved_page_states` list as a copy of the current instance dictionary. After preserving the page state, it initializes a new page by calling `_startPage()`.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Sets the font to "Cambria" at size 5, then draws a right-aligned pagination string in the format `"Pag. <current_page> di <total_pages>"` at the fixed position `(200 mm, 20 mm)` on the canvas. The current page number is retrieved from the instance attribute `self._pageNumber`, while `page_count` represents the total number of pages passed as an argument. This method is intended for use with a vertically oriented record sheet of dimensions 200 mm × 20 mm.

### NumberedCanvas_FINDSindex

*No description available.*
A subclass of `canvas.Canvas` that extends ReportLab's canvas with automatic page numbering support for FINDS index documents. It accumulates page states on each call to `showPage()` and, upon `save()`, iterates over all saved states to render a "Pag. X di Y" string — drawn right-aligned at position `(270 mm, 10 mm)` in Cambria 5pt font — reflecting the total page count. The `define_position` method delegates to `self.page_position(pos)` for additional positional configuration.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

Initializes a `NumberedCanvas_FINDSindex` instance by delegating to the parent `canvas.Canvas.__init__` with all provided positional and keyword arguments. After the parent initialization, it sets up an instance attribute `_saved_page_states` as an empty list.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to the `page_position` method with the provided `pos` argument. This method serves as a named wrapper, offering a semantically descriptive interface for defining the position on the current page.

**Parameters:**
- `pos` — The position value passed to `page_position`. See implementation for accepted types and format.

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current canvas state to the `_saved_page_states` list. After preserving the state, it initializes a new page by calling `_startPage()`. This method is typically called to mark the end of a page before proceeding to add content to a subsequent page.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Renders a page number string onto the current canvas page using the "Cambria" font at size 5. The string is drawn right-aligned at the fixed position `(270 mm, 10 mm)` and follows the format `"Pag. %d di %d"`, where the first value is the current page number (`self._pageNumber`) and the second is the total page count (`page_count`).

### NumberedCanvas_CASSEindex

*No description available.*
A custom ReportLab `canvas.Canvas` subclass that adds automatic page numbering to PDF documents. It accumulates page states during document generation via an overridden `showPage` method, then on `save` iterates over all saved states to render a right-aligned page indicator (formatted as `"Pag. X di Y"`) in Cambria 5pt font at position `(270 mm, 10 mm)` on each page. This deferred rendering approach allows the total page count to be known before any page number is drawn.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

*No description available.*
Initializes a new instance of `NumberedCanvas_CASSEindex`, which extends `canvas.Canvas`. Calls the parent class constructor via `canvas.Canvas.__init__` passing all positional and keyword arguments unchanged. Initializes the `_saved_page_states` instance attribute as an empty list.

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
Renders a page number indicator on the current canvas page using the "Cambria" font at size 5. The string is drawn right-aligned at position (270 mm, 10 mm) and follows the format `"Pag. <current_page> di <total_pages>"`, where `page_count` represents the total number of pages and `self._pageNumber` represents the current page number.

### single_Finds_pdf_sheet

*No description available.*
A data-holding and PDF-rendering class that represents a single archaeological finds record sheet. It accepts a positional data list in its constructor, mapping indexed elements to named attributes such as site, inventory number, find type, stratigraphic references, conservation state, measurements, technologies, and thumbnail image path. The class provides locale-specific sheet generation methods (`create_sheet`, `create_sheet_de`, `create_sheet_en`, `create_sheet_fr`, `create_sheet_es`, `create_sheet_ar`, `create_sheet_ca`) that each construct and return a ReportLab `Table` object representing the formatted finds record, with Italian, German, and English producing distinct label translations and the remaining locales delegating to the English implementation.

**Inherits from**: object

#### Methods

##### __init__(self, data)

*No description available.*
Initializes a `single_Finds_pdf_sheet` instance by unpacking a positional `data` sequence into named instance attributes representing the fields of an archaeological finds record. Each attribute corresponds to a specific index in `data`, covering properties such as `sito`, `numero_inventario`, `tipo_reperto`, `descrizione`, `area`, `us`, `stato_conservazione`, `misurazioni`, `tecnologie`, and others up to index 27. Note that indices 19, 20, and 24 are not mapped to any attribute, and index 27 is assigned to `thumbnail`.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, zero-padded). The formatted date string is then returned to the caller.

##### create_sheet(self)

Builds and returns a ReportLab `Table` object representing a single artefact record sheet ("SCHEDA REPERTI"). The method configures paragraph styles, loads a logo image from the configured path, and assembles labelled field values — including site, stratigraphic references, material class, description, measurements, technologies, bibliographic references, and storage details — into a structured 18-column table with defined column widths, row heights, and spanning/alignment styles. If `self.n_reperto` equals `'0'`, the method skips table construction and returns `None` implicitly.

##### create_sheet_de(self)

*No description available.*
Generates a German-language PDF table sheet for a material inventory form ("FORMULAR MATERIALINVENTAR"), assembling all artifact record fields — including site information, stratigraphic references, description, measurements, technologies, bibliographic references, and storage data — into a structured `Table` object with defined column widths, row heights, and cell spanning styles. The method retrieves a logo image from a configured path and, if available, a thumbnail image associated with the record, embedding both into the layout. If the record's `n_reperto` field is `0`, the method exits without returning a table; otherwise, it returns the fully constructed `Table` instance.

##### create_sheet_en(self)

Generates and returns a ReportLab `Table` object representing an English-language artefact (RA) record sheet for PDF output. The method configures paragraph styles, loads a logo from the configured path, and assembles a multi-row table containing artefact fields such as site name, stratigraphic references, typology, description, finds, measurements, technologies, bibliographic references, and storage information. If `self.n_reperto` equals `'0'`, no table is built and the method returns nothing; otherwise, it constructs the full 17-row, 18-column table with defined column widths, row heights, and spanning/alignment styles.

##### create_sheet_fr(self)

French version of Finds sheet - uses English structure.
TODO: Add proper French translations for all labels.

##### create_sheet_es(self)

Spanish version of Finds sheet - uses English structure.
TODO: Add proper Spanish translations for all labels.

##### create_sheet_ar(self)

Arabic version of Finds sheet - uses English structure.
TODO: Add proper Arabic translations for all labels.

##### create_sheet_ca(self)

Catalan version of Finds sheet - uses English structure.
TODO: Add proper Catalan translations for all labels.

### Box_labels_Finds_pdf_sheet

Generates PDF label sheets for archaeological finds storage boxes using ReportLab. The class accepts box metadata — including box number, site name, inventory/material type list, stratigraphic unit list, and storage location — and produces a formatted four-row table layout incorporating a site logo, styled paragraphs, and span-based column merging. Three sheet variants are available via `create_sheet` (Italian), `create_sheet_de` (German), and `create_sheet_en` (English), each returning a ReportLab `Table` object ready for inclusion in a PDF document.

**Inherits from**: object

#### Methods

##### __init__(self, data, sito)

*No description available.*
Initializes a `Box_labels_Finds_pdf_sheet` instance with site and box-related data. The `sito` parameter is stored directly, while the `data` sequence is unpacked into four fields: `cassa` (index 0), `elenco_inv_tip_rep` (index 1), `elenco_us` (index 2), and `luogo_conservazione` (index 3). No validation or transformation is applied to the provided arguments during initialization.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, e.g., `"31-12-2024"`). The formatted date string is then returned to the caller.

##### create_sheet(self)

*No description available.*
Builds and returns a formatted `Table` object representing a physical storage box label sheet for archaeological finds. The method configures a stylesheet with custom paragraph styles (`'Cassa Label'`, `'Sito Label'`, and `'Normal'`) using the Cambria font, then constructs labelled content blocks for the box number (`cassa`), site name (`sito`), inventory/material type list (`elenco_inv_tip_rep`), and stratigraphic unit list (`elenco_us`), handling `None` values for the latter two. A logo image is loaded from a path retrieved via `Connection.logo_path()` or a default fallback, scaled to 1.5 inches wide, and incorporated into a 4-row, 10-column table with defined span and alignment styles before being returned.

##### create_sheet_de(self)

Builds and returns a formatted ReportLab `Table` object representing a storage box label sheet with German-language field labels. The method defines custom paragraph styles for the box number, site name, inventory list, and stratigraphic unit list, then loads a logo image from a configured path (falling back to a default location if no custom logo is set). The resulting table arranges these elements in a four-row, ten-column grid with defined span and alignment rules suitable for printed archaeological storage box labels.

##### create_sheet_en(self)

Generates and returns an English-language PDF table sheet (`Table`) for a storage box (cassa) record. The method defines custom paragraph styles for labels and body text, resolves a logo image path via the `Connection` class and environment variables, and assembles a four-row, ten-column layout containing the logo, box number, site name, list of stratigraphic units (SU/Structure), and list of inventory numbers with material types. Cell spanning, alignment, and grid styling are applied via `table_style` before the `Table` object is constructed and returned.

### CASSE_index_pdf_sheet

*No description available.*
A PDF sheet class that represents a single row of data for a storage box (`cassa`) index report. It stores four fields — box number (`cassa`), inventory/material type list (`elenco_inv_tip_rep`), stratigraphic unit list (`elenco_us`), and conservation location (`luogo_conservazione`) — and provides locale-specific table row rendering via `getTable` (Italian), `getTable_de` (German), and `getTable_en` (English), each returning a list of formatted `Paragraph` objects. The `makeStyles` method returns a `TableStyle` with a full grid border and top vertical alignment for use when composing the row into a ReportLab table.

**Inherits from**: object

#### Methods

##### __init__(self, data)

Initializes a `CASSE_index_pdf_sheet` instance by unpacking four elements from the `data` sequence parameter into corresponding instance attributes. Assigns `data[0]` to `self.cassa`, `data[1]` to `self.elenco_inv_tip_rep`, `data[2]` to `self.elenco_us`, and `data[3]` to `self.luogo_conservazione`, representing the cassa identifier, the inventory type report list, the US list, and the conservation location respectively.

##### getTable(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` objects representing a single table row for a storage box record. The method applies a consistent `Normal` style (Cambria, 10pt, left-aligned) to four fields: box number (`cassa`), inventory number/material type (`elenco_inv_tip_rep`), stratigraphic unit/structure (`elenco_us`), and conservation location (`luogo_conservazione`). Fields `elenco_inv_tip_rep` and `elenco_us` are rendered as empty if their values are `None` or `'None'` respectively.

##### getTable_de(self)

*No description available.*
Generates a list of formatted `Paragraph` objects containing German-language table cell content for a storage box record. Each paragraph applies a consistent `Normal` style with predefined spacing and font settings, and renders labeled fields for box number (`Nr.`), inventory list and material type (`Liste N° Inv. / Art material`), stratigraphic unit (`SE(Struktur)`), and conservation location (`Ort der Erhaltung`). The fields for `elenco_inv_tip_rep` and `elenco_us` are conditionally populated based on whether the corresponding instance attributes are `None`, while `num_cassa` and `luogo_conservazione` are always included.

##### getTable_en(self)

*No description available.*
Builds and returns a list of `Paragraph` objects representing a table row with English-language labels for an archaeological finds record. The method applies a shared `Normal` style with predefined spacing, alignment, and font size settings, then constructs four fields: case number (`Nr.`), inventory number and material type (`N° Inv. / Material type`), stratigraphic unit (`SU(Structure)`), and place of conservation (`Place of conservation`). The `elenco_inv_tip_rep` and `elenco_us` fields render as empty labels if their corresponding instance attributes are `None`.

##### makeStyles(self)

*No description available.*
Creates and returns a `TableStyle` object configured with a uniform grid and top vertical alignment applied across all cells. The grid spans the entire table from the first cell `(0, 0)` to the last cell `(-1, -1)`, using a line width of `0.0` and black color. The vertical alignment for all cells is set to `'TOP'`.

### FINDS_index_pdf_sheet

`FINDS_index_pdf_sheet` is a data container and PDF rendering class that represents a single archaeological finds record as a formatted index sheet. It is initialized from a positional data sequence, extracting fields such as inventory number, find type, material class, definition, area, stratigraphic unit, washing status, box number, find number, and associated photo and drawing identifiers. The class provides three locale-specific table-generation methods — `getTable` (Italian), `getTable_de` (German), and `getTable_en` (English) — each returning a list of styled `Paragraph` objects for use in a ReportLab PDF table, along with a `makeStyles` method that returns a `TableStyle` defining grid and vertical alignment for that table.

**Inherits from**: object

#### Methods

##### __init__(self, data)

*No description available.*
Initializes a `FINDS_index_pdf_sheet` instance by extracting and assigning find record fields from the provided `data` sequence using fixed index positions. Fields populated include site (`data[1]`), inventory number (`data[2]`), find type (`data[3]`), cataloguing criterion (`data[4]`), definition (`data[5]`), area (`data[7]`), stratigraphic unit (`data[8]`), washed status (`data[9]`), box number (`data[10]`), repertoried status (`data[21]`), diagnostic flag (`data[22]`), find number (`data[23]`), photo ID (`data[28]`), and drawing ID (`data[29]`). The `photo_id` and `drawing_id` fields are conditionally assigned only if `data` contains sufficient elements, defaulting to an empty string otherwise.

##### getTable(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` objects representing the fields of an archaeological find record, intended for use in a PDF report table. Each field — including inventory number, find type, material class, definition, area, stratigraphic unit, washing status, collection status, diagnostic status, crate number, find number, photo ID, and drawing ID — is rendered with a bold label and its corresponding value, with `None` or empty values producing label-only entries. A standard `Normal` style (Cambria, 7pt, left-aligned) is applied to most fields, while `photo_id` and `drawing_id` use a smaller word-wrapping style (5pt, CJK wrap) with semicolon-delimited values converted to line breaks.

##### getTable_de(self)

*No description available.*
Generates and returns a list of formatted `Paragraph` objects containing artifact record fields with German-language labels, intended for use in a PDF table layout. Each field — including inventory number, find type, material class, definition, area, stratigraphic unit, washing status, inventory status, diagnostic status, box number, find number, photo ID, and drawing ID — is rendered using a `Normal` style (Cambria, 7pt) with `None` values producing empty label entries. Photo ID and drawing ID fields use a dedicated word-wrap style (`styWrap`, 5pt, CJK wrapping) and replace semicolon-separated values with line breaks.

##### getTable_en(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` objects representing the English-language field labels and values for an archaeological find record. Each field — including inventory number, find type, material class, definition, area, stratigraphic unit (SU), washed status, inventoried status, diagnostic status, box number, find number, photo ID, and drawing ID — is rendered with a bold label and its corresponding instance attribute value, with `None` or empty values producing label-only paragraphs. Text styling uses a `Cambria` font at 7pt for most fields, while `photo_id` and `drawing_id` use a reduced 5pt style with CJK word-wrap enabled to handle multi-value content delimited by line breaks.

##### makeStyles(self)

*No description available.*
Constructs and returns a `TableStyle` object configured with two style directives: a `GRID` rule that applies a black border of width `0.0` across all cells (from `(0, 0)` to `(-1, -1)`), and a `VALIGN` rule that sets the vertical alignment of all cells to `'TOP'`. This method takes no parameters beyond `self` and returns the resulting `TableStyle` instance directly.

### FOTO_index_pdf_sheet

*No description available.*
A PDF sheet class that encapsulates artefact record data for use in a photo index report. It stores artefact attributes — including site, find number, thumbnail path, stratigraphic unit, material type, dating, conservation state, container information, photo ID, and drawing ID — and provides methods to render these fields as formatted ReportLab `Paragraph` and `Image` elements. Three locale-specific table methods (`getTable`, `getTable_en`, `getTable_de`) produce Italian, English, and German label variants respectively, while `makeStyles` returns a `TableStyle` applying a full grid and top vertical alignment.

**Inherits from**: object

#### Methods

##### __init__(self, data)

Initializes a `FOTO_index_pdf_sheet` instance by unpacking a positional data sequence into individual instance attributes. The first nine elements (indices 0–8) are assigned unconditionally to `sito`, `n_reperto`, `thumbnail`, `us`, `definizione`, `datazione_reperto`, `stato_conservazione`, `tipo_contenitore`, and `nr_cassa`. The optional tenth and eleventh elements are assigned to `photo_id` and `drawing_id` respectively, defaulting to an empty string if the sequence does not contain those indices.

##### getTable(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` and `Image` objects representing the fields of an archaeological find record, intended for use in a PDF report table. Each field — including find number, stratigraphic unit, material type, date, conservation state, container type, container number, photo ID, and drawing ID — is rendered as a `Paragraph` using a customised 6pt Cambria style, while photo ID and drawing ID entries use a word-wrap style with 5pt font. If a thumbnail image is available, it is scaled to a 1-inch width and included in place of a placeholder paragraph; if unavailable or an error occurs, a fallback `Paragraph` is used instead.

##### getTable_en(self)

Builds and returns a list of formatted `Paragraph` (and optionally `Image`) objects representing artefact record fields with English-language labels, intended for use in a PDF table layout. Each field — including artefact number, SU, artefact type, dating, state of preservation, container type, container number, photo ID, and drawing ID — is rendered using a `Normal` style based on the Cambria font at 6pt, while photo ID and drawing ID use a smaller word-wrapping style. If a thumbnail image is available, it is scaled to a 1-inch width and included in place of a placeholder paragraph; otherwise, an appropriate fallback text is displayed.

##### getTable_de(self)

Builds and returns a list of formatted `Paragraph` (and optionally `Image`) objects representing artefact record fields with German-language labels, intended for use as table cell content in a PDF report. Each field — including artefact number, stratigraphic unit, artefact type, dating, conservation state, container type, container number, photo ID, and drawing ID — is rendered using a predefined `Normal` style (Cambria, 6pt), while photo ID and drawing ID use a word-wrap style (`styWrap`) with semicolons replaced by line breaks. The thumbnail field is rendered as a scaled `Image` if a valid thumbnail path exists; otherwise, a fallback `Paragraph` with a German error message is used.

##### makeStyles(self)

*No description available.*
Constructs and returns a `TableStyle` object defining the visual formatting rules for a table. The style applies a black grid border across all cells (from `(0, 0)` to `(-1, -1)`) with a line thickness of `0.0`, and sets the vertical alignment of all cell content to `'TOP'`.

### FOTO_index_pdf_sheet_2

PDF sheet for inventory list WITHOUT thumbnail

**Inherits from**: object

#### Methods

##### __init__(self, data)

*No description available.*
Initializes an instance of `FOTO_index_pdf_sheet_2`, which represents a PDF sheet for an inventory list without a thumbnail. Accepts a single sequence argument `data` and maps its positional elements to instance attributes: `sito`, `numero_inventario`, `area`, `us`, `tipo_reperto`, `repertato`, `n_reperto`, `tipo_contenitore`, `nr_cassa`, `luogo_conservazione`, `years`, `photo_id`, and `drawing_id`. The attributes `photo_id` and `drawing_id` are conditionally assigned from indices 11 and 12 respectively, defaulting to an empty string if the corresponding index does not exist in `data`.

##### getTable(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` objects representing the fields of an inventory record for use in a ReportLab PDF table. Each paragraph is styled using a customized `Normal` style (Cambria, 6pt, left-aligned) and contains a bold label followed by the corresponding instance attribute value. The `photo_id` and `drawing_id` fields use a dedicated word-wrap style (`styWrap`) with semicolon-delimited values replaced by line breaks; the `n_reperto` field is rendered empty when `repertato` equals `'No'`.

##### getTable_en(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` objects representing artefact record fields with English-language labels, intended for use in a PDF table. Each field — including inventory number, stratigraphic unit, artefact type, inventoried status, find number, container type, container number, storage location, year, photo ID, and drawing ID — is rendered using a Cambria 6pt normal style with defined spacing and left alignment. The find number is conditionally omitted when `self.repertato` equals `'No'`, and the photo ID and drawing ID fields use a word-wrap style with a reduced font size of 5pt, with semicolons replaced by line breaks.

##### getTable_de(self)

Builds and returns a list of formatted `Paragraph` objects containing archaeological find record fields with German-language labels, intended for use as table cell data in a PDF report. Each field — including inventory number, stratigraphic unit, artefact type, inventarisation status, find number, container type, container number, storage location, year, photo ID, and drawing ID — is rendered using a `Normal` style based on `getSampleStyleSheet`, configured with Cambria font at 6pt. Photo ID and drawing ID entries use a separate word-wrap style (`styWrap`) and replace semicolon-separated values with line breaks; the find number field is conditionally left blank when `self.repertato` equals `'No'`.

##### makeStyles(self)

*No description available.*
Constructs and returns a `TableStyle` object configured with two style directives applied to the entire table range (`(0, 0)` to `(-1, -1)`): a black grid border with a line width of `0.0`, and top vertical alignment (`'TOP'`) for all cells.

**Returns:** `TableStyle` — the configured table style instance.

### generate_reperti_pdf

*No description available.*
A PDF generation class for archaeological finds (reperti) reporting within the pyarchinit system. It produces multi-language PDF documents — in Italian, English, German, French, Spanish, Arabic, and Catalan — covering individual finds record sheets, artifact index lists, inventory lists, storage box indexes, and box label sheets. Output files are written to the directory defined by `PDF_path`, which is derived from the `PYARCHINIT_HOME` environment variable.

**Inherits from**: object

#### Methods

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, e.g., `"31-12-2024"`). The formatted date string is then returned to the caller.

##### build_index_Foto(self, records, sito)

*No description available.*
Generates a PDF index document listing photographic/find records for a given excavation site. The method retrieves the configured logo path via `Connection`, constructs a formatted table from the provided `records` using `FOTO_index_pdf_sheet`, and assembles the document with a site heading, logo, and paginated table using ReportLab's `SimpleDocTemplate`. The resulting PDF is written to `self.PDF_path` under the filename `'Elenco Reperti thumbnail.pdf'` with a landscape A3-style page size and `NumberedCanvas_FINDSindex` as the canvas maker.

##### build_index_Foto_en(self, records, sito)

Generates a PDF index document in English listing artifact photo records for a specified archaeological site. The method resolves the logo path via a database connection, constructs a formatted table from the provided `records` using `FOTO_index_pdf_sheet` and its `getTable_en()` method, and assembles the document with a header containing the site name and current date. The resulting PDF file is written to `self.PDF_path` with a timestamped filename in landscape A3 format (`29 cm × 21 cm`) using `SimpleDocTemplate` and `NumberedCanvas_FINDSindex`.

##### build_index_Foto_de(self, records, sito)

Generates a German-language PDF index document ("INVENTURLISTE gefertigter ARTIKEL") listing photo records for a given excavation site (`sito`). The method resolves the application's logo path via the `Connection` object, constructs a formatted table from the provided `records` using `FOTO_index_pdf_sheet` and a fixed set of ten column widths, and assembles the document with a header paragraph, the table, and a spacer. The resulting PDF is written to `self.PDF_path` with a timestamped filename and rendered using `NumberedCanvas_FINDSindex` on a landscape A3-sized page.

##### build_index_Foto_2(self, records, sito)

Generates a PDF inventory index document ("Elenco Inventario") for photographic records associated with a given excavation site. It resolves the logo path via a `Connection` object, constructs a styled table from the provided `records` using `FOTO_index_pdf_sheet_2`, and assembles the document with a header paragraph, logo, and formatted table with eleven columns of predefined widths. The resulting PDF is written to `self.PDF_path` under the filename `'Elenco Inventario.pdf'` using `SimpleDocTemplate` with a landscape A3-like page size and `NumberedCanvas_FINDSindex` as the canvas maker.

##### build_index_Foto_2_en(self, records, sito)

*No description available.*
Generates a paginated PDF inventory list in English for photographic records associated with a given site. The method resolves the logo path via a `Connection` object, constructs a styled document containing a header with the site name and current date, and builds a formatted table from the provided `records` using `FOTO_index_pdf_sheet_2` and its `getTable_en()` method. The resulting PDF is written to `self.PDF_path` with a timestamped filename and rendered using `NumberedCanvas_FINDSindex` on a landscape A3-equivalent page size (29 cm × 21 cm).

##### build_index_Foto_2_de(self, records, sito)

Generates a German-language PDF inventory list ("Inventurliste") for photographic records associated with a given excavation site (`sito`). The method resolves the logo path via a `Connection` object, constructs a styled document header containing the site name and current date, and builds a formatted table from the provided `records` using `FOTO_index_pdf_sheet_2` and its `getTable_de()` method. The resulting PDF is written to `self.PDF_path` with a timestamped filename and rendered using `SimpleDocTemplate` in landscape A4 format (`29 cm × 21 cm`) with `NumberedCanvas_FINDSindex` as the canvas maker.

##### build_Finds_sheets(self, records)

Builds a multi-page PDF document containing individual finds sheets for a collection of records. For each record, it instantiates a `single_Finds_pdf_sheet` object, generates a sheet via `create_sheet()`, and appends it followed by a `PageBreak` to the elements list. The resulting document is written to a file named `'Scheda Reperti.pdf'` in the configured `PDF_path` directory, built using `SimpleDocTemplate` with `NumberedCanvas_Findssheet` as the canvas maker.

##### build_Finds_sheets_de(self, records)

Generates a multi-page German-language finds sheet PDF document from a collection of records. For each record, it instantiates a `single_Finds_pdf_sheet` object, appends the German sheet variant (`create_sheet_de()`) and a `PageBreak` to the elements list. The resulting document is written to `Formular_Finds.pdf` in the configured PDF output path, built using `SimpleDocTemplate` with `NumberedCanvas_Findssheet` as the canvas maker.

##### build_Finds_sheets_en(self, records)

Builds an English-language finds sheet PDF document from a list of records. For each record, it instantiates a `single_Finds_pdf_sheet` object, generates an English sheet via `create_sheet_en()`, and appends it to the elements list followed by a `PageBreak()`. The resulting elements are compiled into a `SimpleDocTemplate` PDF file named `Finds_form.pdf`, written to the path specified by `self.PDF_path`, using `NumberedCanvas_Findssheet` as the canvas maker.

##### build_Finds_sheets_fr(self, records)

French version

##### build_Finds_sheets_es(self, records)

Spanish version

##### build_Finds_sheets_ar(self, records)

Arabic version

##### build_Finds_sheets_ca(self, records)

Catalan version

##### build_index_Finds(self, records, sito)

Generates a PDF index document listing archaeological finds ("Elenco Materiali") for a given excavation site. It resolves the logo path via a `Connection` object, constructs a styled table from the provided `records` using `FINDS_index_pdf_sheet`, and assembles the document with a logo, heading, and formatted table spanning 13 columns. The resulting PDF is written to `self.PDF_path` under the filename `'Elenco Materiali.pdf'` using a landscape page format and `NumberedCanvas_FINDSindex` as the canvas maker.

##### build_index_Finds_de(self, records, sito)

Generates a German-language PDF index document listing archaeological finds ("Liste Material") for a given excavation site. The method resolves the logo path via a `Connection` object, constructs a styled ReportLab document containing a header with the site name and current date, and builds a formatted table from the provided `records` using `FINDS_index_pdf_sheet` and its `getTable_de()` method with 13 predefined column widths. The resulting PDF is written to `self.PDF_path` under the filename `'Liste Material.pdf'` using a landscape A3-like page size and `NumberedCanvas_FINDSindex` as the canvas maker.

##### build_index_Finds_en(self, records, sito)

Generates an English-language PDF index report of material finds for a given site. The method resolves the logo path via the `Connection` class, constructs a styled document containing a header with the site name and current date, and builds a formatted table from the provided `records` using `FINDS_index_pdf_sheet` with English column layout (`getTable_en`) and 13 predefined column widths. The resulting document is written to a file named `'List Material.pdf'` within `self.PDF_path`, rendered on A3 landscape page size using `NumberedCanvas_FINDSindex` as the canvas maker.

##### build_index_Casse(self, records, sito)

*No description available.*
Generates a PDF index document listing storage boxes ("Casse") associated with a given excavation site (`sito`). The method retrieves the logo path via a `Connection` object, constructs a styled ReportLab document containing a heading, and populates a formatted table by iterating over the provided `records` using `CASSE_index_pdf_sheet`. The resulting PDF is written to a file named `'Elenco Casse.pdf'` within `self.PDF_path`, using a custom page size of 41 × 29 cm.

##### build_index_Casse_de(self, records, sito)

Builds a PDF index document listing box material records for a given excavation site in German ("de" locale). The method retrieves the logo path from the database connection, constructs a styled ReportLab document containing a header with the site name and current date, and formats the provided records into a table using `CASSE_index_pdf_sheet` and its `getTable_de()` method. The resulting PDF is written to `liste_box.pdf` within the configured PDF output path, using a landscape-oriented page size of 41 × 29 cm.

##### build_index_Casse_en(self, records, sito)

*No description available.*
Generates a PDF index document listing box materials (in English) for a given excavation site. The method resolves the logo path via a `Connection` object, constructs a formatted table by iterating over the provided `records` using `CASSE_index_pdf_sheet`, and assembles the document with a header paragraph containing the site name and current date. The resulting PDF is written to a file named `list_box.pdf` within the configured PDF output path, using a `SimpleDocTemplate` with a custom landscape page size of 41 × 29 cm.

##### build_box_labels_Finds(self, records, sito)

*No description available.*
Iterates over the provided `records` collection and generates a `Box_labels_Finds_pdf_sheet` instance for each record using the given `sito` value, appending the resulting sheet and a `PageBreak` to an elements list. Builds a PDF document named `'Etichette Casse Materiali.pdf'` in the instance's `PDF_path` directory, using a landscape A4-equivalent page size (`29 cm × 21 cm`) with fixed margin settings of 20 units on all sides. The output file is written in binary mode and closed upon completion.

##### build_box_labels_Finds_de(self, records, sito)

*No description available.*
Generates a German-language PDF document containing box labels for finds records. For each record in the provided `records` list, it instantiates a `Box_labels_Finds_pdf_sheet` object using the record and `sito` parameters, appends the result of `create_sheet_de()` followed by a `PageBreak` to the elements list. The resulting document is written to a file named `liste_box_material.pdf` within `self.PDF_path`, using a page size of 29 × 21 cm with 20-unit margins on all sides.

##### build_box_labels_Finds_en(self, records, sito)

*No description available.*
Iterates over the provided `records` collection and generates an English-language PDF document containing box labels for finds, using `Box_labels_Finds_pdf_sheet` to produce each individual sheet via `create_sheet_en()`. Each sheet is appended to the elements list followed by a `PageBreak`, resulting in one label per page. The final document is written to a file named `list_box_material.pdf` in the configured `PDF_path` directory, formatted as an A4-landscape page (`29 cm × 21 cm`) using `SimpleDocTemplate`.

