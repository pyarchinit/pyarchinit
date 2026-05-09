# modules/utility/pyarchinit_exp_Campsheet_pdf.py

## Overview

This file contains 57 documented elements.

## Classes

### NumberedCanvas_Campionisheet

*No description available.*
A subclass of `canvas.Canvas` that extends the ReportLab canvas with multi-page awareness for campioni (sample) sheets. It defers page rendering by capturing each page's state in `_saved_page_states` during `showPage()`, then replays all states at `save()` time to inject a page number footer ("Pag. X di Y") on every page. The page number string is drawn right-aligned at coordinates `(200 mm, 20 mm)` using the "Cambria" font at size 5.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

Initializes a `NumberedCanvas_Campionisheet` instance by delegating to the parent `canvas.Canvas.__init__` method with all provided positional and keyword arguments. After the parent constructor completes, it initializes the `_saved_page_states` instance attribute as an empty list.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to `self.page_position(pos)` with the provided argument. This method serves as a named wrapper around `page_position`, accepting a single positional parameter `pos` whose type and valid values are determined by the underlying `page_position` implementation.

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current instance state to the `_saved_page_states` list. After preserving the state, it calls `_startPage()` to initialize a new page for subsequent content.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Sets the font to "Cambria" at size 5, then draws a right-aligned pagination string in the format `"Pag. <current_page> di <total_pages>"` at the fixed position of 200 mm from the left and 20 mm from the bottom of the page. The `page_count` parameter represents the total number of pages, while the current page number is retrieved from the instance attribute `self._pageNumber`.

### NumberedCanvas_Campioniindex

*No description available.*
A subclass of `canvas.Canvas` that extends the ReportLab canvas with automatic page numbering support. It accumulates page states during document generation via `showPage()`, then finalises the document in `save()` by iterating over all saved states and calling `draw_page_number()` on each page. The `draw_page_number()` method renders a right-aligned pagination string in Cambria 5pt font at position `(270 mm, 10 mm)`, formatted as `"Pag. X di Y"`.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

## `__init__` — `NumberedCanvas_Campioniindex`

Initializes a new instance of `NumberedCanvas_Campioniindex` by delegating to the parent `canvas.Canvas.__init__` with all provided positional and keyword arguments. After the parent constructor completes, it initializes the instance attribute `_saved_page_states` as an empty list.

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
Renders a page number string onto the current canvas page using the "Cambria" font at size 5. The string is drawn right-aligned at the fixed position `(270 mm, 10 mm)` and follows the format `"Pag. %d di %d"`, where the first value is the current page number (`self._pageNumber`) and the second is the total page count (`page_count`).

### NumberedCanvas_CASSEindex

*No description available.*
A subclass of `canvas.Canvas` that extends the ReportLab canvas with automatic page numbering support. It accumulates page states during document generation via `showPage`, then iterates over all saved states at `save` time to render a "Pag. X di Y" string (in Cambria 5pt, right-aligned at position 270mm × 10mm) on each page once the total page count is known. This deferred rendering pattern ensures the total page count is available before any page number footer is drawn.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

*No description available.*
Initializes a `NumberedCanvas_CASSEindex` instance by delegating to the parent `canvas.Canvas` constructor with all provided positional and keyword arguments. After the parent initialization, it sets up the `_saved_page_states` instance attribute as an empty list.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to `self.page_position(pos)`. This method serves as a named wrapper around `page_position`, accepting a single positional argument `pos` and forwarding it without modification.

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current canvas state to the `_saved_page_states` list. After preserving the state, it initializes a new page by calling `_startPage()`. This method is typically called to mark the end of a page before proceeding to add content to the next one.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Renders a page number indicator on the current canvas page using the "Cambria" font at size 5. The string is drawn right-aligned at position (270 mm, 10 mm) in the format `"Pag. X di Y"`, where `X` is the current page number (`self._pageNumber`) and `Y` is the total page count supplied via the `page_count` parameter.

### single_Campioni_pdf_sheet

*No description available.*
A data container and PDF sheet generator for a single archaeological sample (campione) record. It stores nine sample-related fields — site (`sito`), sample number (`numero_campione`), sample type (`tipo_campione`), description (`descrizione`), area (`area`), stratigraphic unit (`us`), inventory number (`numero_inventario`), conservation location (`luogo_conservazione`), and box number (`nr_cassa`) — populated from a positional data list passed to the constructor. It provides three locale-specific methods (`create_sheet`, `create_sheet_de`, `create_sheet_en`) that each build and return a ReportLab `Table` representing the formatted sample record sheet in Italian, German, and English respectively, along with a `datestrfdate` utility method that returns the current date as a `DD-MM-YYYY` string.

**Inherits from**: object

#### Methods

##### __init__(self, data)

*No description available.*
Initializes a `single_Campioni_pdf_sheet` instance by unpacking a sequential data structure into nine named instance attributes. The `data` parameter is expected to be an indexed collection whose elements map positionally to: `sito` (index 0), `numero_campione` (index 1), `tipo_campione` (index 2), `descrizione` (index 3), `area` (index 4), `us` (index 5), `numero_inventario` (index 6), `luogo_conservazione` (index 7), and `nr_cassa` (index 8). Each attribute corresponds to a field of an archaeological sample (campione) record intended for PDF sheet generation.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year). The formatted date string is returned as the method's output.

##### create_sheet(self)

*No description available.*
Generates and returns a formatted PDF table (`Table`) representing a sample record sheet ("SCHEDA CAMPIONI"). The method defines two paragraph styles (`styNormal` and `styDescrizione`) using ReportLab's `getSampleStyleSheet`, then constructs a series of labeled `Paragraph` elements populated with instance attributes such as `sito`, `tipo_campione`, `numero_campione`, `area`, `us`, `numero_inventario`, `descrizione`, `luogo_conservazione`, and `nr_cassa`. A logo image is loaded from a path resolved via the `Connection` class and environment variables, scaled to 1.5 inches wide, and incorporated into a 10-column, 6-row cell schema with defined span and alignment styles applied through `table_style`.

##### create_sheet_de(self)

Generates and returns a formatted PDF table (`Table`) representing a German-language sample record sheet ("FORMULAR PROBEN"). The method defines two paragraph styles (`styNormal` and `styDescrizione`) using `getSampleStyleSheet`, then constructs labelled `Paragraph` fields for excavation site details, sample type, area, stratigraphic unit, inventory number, description, storage location, and box number, all rendered in German. It also loads a logo image from a configurable path, arranges all elements into a six-row, ten-column cell schema with defined span and alignment rules, and returns the resulting `Table` object.

##### create_sheet_en(self)

Builds and returns an English-language PDF sheet for a sample form as a ReportLab `Table` object. The method defines paragraph styles, constructs labelled `Paragraph` elements for fields such as site, sample type, sample number, area, SU, inventory number, description, place of conservation, and box number, and retrieves a logo image from a configurable path resolved via `Connection`. The resulting table is assembled from a six-row cell schema with defined column spans, grid styling, and uniform column widths of 50 units.

### Box_labels_Campioni_pdf_sheet

*No description available.*
A PDF label sheet generator for archaeological sample storage boxes. The class accepts box metadata — including box number (`cassa`), site name (`sito`), inventory/sample type list (`elenco_inv_tip_rep`), stratigraphic unit list (`elenco_us`), and conservation location (`luogo_conservazione`) — and uses ReportLab to compose a formatted, logo-bearing table layout. It exposes three locale-specific sheet creation methods (`create_sheet`, `create_sheet_de`, `create_sheet_en`) that produce equivalent Italian, German, and English label tables respectively, each returning a ReportLab `Table` object.

**Inherits from**: object

#### Methods

##### __init__(self, data, sito)

*No description available.*
Initializes a `Box_labels_Campioni_pdf_sheet` instance with site and box data. The `sito` parameter is stored directly, while the `data` parameter is a sequence from which four fields are unpacked by index: `cassa` (index 0), `elenco_inv_tip_rep` (index 1), `elenco_us` (index 2), and `luogo_conservazione` (index 3). No return value is produced, as is standard for `__init__`.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, e.g., `"31-12-2024"`). The formatted date string is then returned to the caller.

##### create_sheet(self)

*No description available.*
Builds and returns a formatted `Table` object representing a physical label sheet for an archaeological storage box (*cassa*). The method configures custom paragraph styles using ReportLab's `getSampleStyleSheet`, loads a logo image from a path resolved via environment variables and a database connection, and assembles labelled content including the box number (`cassa`), site name (`sito`), US list (`elenco_us`), and inventory/sample type list (`elenco_inv_tip_rep`) into a structured cell schema. Table styling defines column spans, alignment, and grid properties before the completed `Table` instance is returned.

##### create_sheet_de(self)

*No description available.*
Generates a German-language PDF table sheet for a storage box label using ReportLab. The method configures custom paragraph styles (`Cassa Label`, `Sito Label`, and `Normal`) with Cambria font settings, then constructs labelled content including a logo image, box number, excavation site (`Ausgrabungsstätte`), stratigraphic unit list (`Listen SE/(Struktur)`), and inventory/find type list (`Listen N° Inv. / Probentyp`). The content is arranged in a 4-row, 10-column `Table` with defined span and alignment styles, and the completed table is returned.

##### create_sheet_en(self)

Generates an English-language PDF sheet layout for a storage box label by constructing styled paragraph elements and a logo image using ReportLab. The method configures custom paragraph styles (`'Cassa Label'`, `'Sito Label'`, and `'Normal'`) with the `'Cambria'` font, then assembles a four-row `Table` containing the site logo, box number, site name, SU/Structure list, and inventory/sample type list. The logo path is resolved via a `Connection` object or a default fallback, and the completed `Table` object is returned.

### CASSE_index_pdf_sheet

*No description available.*
A data container and PDF rendering class for generating storage box (cassa) index sheet rows in a ReportLab-based PDF report. It stores four fields — box number (`cassa`), inventory/sample type list (`elenco_inv_tip_camp`), stratigraphic unit list (`elenco_us`), and conservation location (`luogo_conservazione`) — and exposes three locale-specific table data methods (`getTable` for Italian, `getTable_de` for German, `getTable_en` for English), each returning a list of formatted `Paragraph` objects. The `makeStyles` method returns a `TableStyle` applying a full grid with top vertical alignment for use when rendering the row data in a ReportLab `Table`.

**Inherits from**: object

#### Methods

##### __init__(self, data)

*No description available.*
Initializes a `CASSE_index_pdf_sheet` instance by unpacking a positional `data` sequence into four instance attributes. Assigns `data[0]` to `self.cassa` (Cassa), `data[1]` to `self.elenco_inv_tip_camp` (elenco US), `data[2]` to `self.elenco_us` (elenco Inventari), and `data[3]` to `self.luogo_conservazione` (luogo conservazione).

##### getTable(self)

Builds and returns a list of formatted `Paragraph` objects representing a single table row for a storage box record. Each paragraph applies a consistent `Normal` style (Cambria, 10pt, left-aligned) with bold labels followed by the corresponding field values for box number (`cassa`), inventory number/sample type (`elenco_inv_tip_camp`), stratigraphic unit (`elenco_us`), and storage location (`luogo_conservazione`). The fields `elenco_inv_tip_camp` and `elenco_us` are handled defensively, rendering an empty value when their stored data is `None`.

##### getTable_de(self)

*No description available.*
Generates a list of styled `Paragraph` objects containing German-language labels and field values for use in a table row. The method applies a consistent `Normal` style (Cambria, 10pt, left-aligned) to each cell, covering the fields: case number (`N.`), inventory number/sample type (`N° Inv./Probentyp`), stratigraphic unit (`SE(Struktur)`), and storage location (`Ort der Erhaltung`). Fields `elenco_inv_tip_camp` and `elenco_us` are rendered as empty if their values are `None`; the returned list contains four `Paragraph` elements in that order.

##### getTable_en(self)

*No description available.*
Builds and returns a list of `Paragraph` objects representing a table row with English-language field labels for a storage/conservation record. The method applies a consistent `Normal` paragraph style using the `Cambria` font at size 10 with left alignment, and formats four fields: box number (`N.`), inventory number and sample type (`Inv. N° /Sample Type`), stratigraphic unit or structure (`SU(Structure)`), and place of conservation (`Place of conservation`). Fields `elenco_inv_tip_camp` and `elenco_us` are rendered as empty labeled paragraphs when their corresponding instance attributes are `None`.

##### makeStyles(self)

*No description available.*
Creates and returns a `TableStyle` object configured with a uniform grid and top vertical alignment applied across all cells. The grid spans the entire table from the first cell `(0, 0)` to the last cell `(-1, -1)`, using a line width of `0.0` and black color. The vertical alignment for all cells is set to `'TOP'`.

### Campioni_index_pdf_sheet

*No description available.*
Represents a single sample record row for a PDF index sheet, encapsulating archaeological sample data including site, sample number, sample type, description, area, stratigraphic unit, material inventory number, conservation location, and crate number. The class provides three localized variants of its table data builder — `getTable()` (Italian), `getTable_de()` (German), and `getTable_en()` (English) — each returning a list of `Paragraph` objects with labeled field values formatted using a 7pt Cambria `Normal` style. The `makeStyles()` method returns a `TableStyle` applying a full black grid and top vertical alignment across all cells.

**Inherits from**: object

#### Methods

##### __init__(self, data)

*No description available.*
Initializes a `Campioni_index_pdf_sheet` instance by unpacking a sequential `data` collection into nine named instance attributes. The attributes populated are `sito`, `numero_campione`, `tipo_campione`, `descrizione`, `area`, `us`, `numero_inventario_materiale`, `luogo_conservazione`, and `nr_cassa`, mapped respectively to indices 0 through 8 of the input data. Each attribute corresponds to a specific field of a sample record, including site, sample number, sample type, description, area, stratigraphic unit, material inventory number, conservation location, and crate number.

##### getTable(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` objects representing the fields of a sample record for use in a report table. Each field — sample number, sample type, area, US, material inventory number, storage location, and box number — is rendered with a bold label and its corresponding value using a configured `Normal` style (Cambria, 7pt, left-aligned, with defined spacing). Fields whose values are `None` or `"None"` are rendered with the bold label only, leaving the value portion empty.

##### getTable_de(self)

*No description available.*
Generates a list of formatted `Paragraph` objects containing sample and conservation data with German-language labels, intended for use in a table layout. Each field — including sample number, sample type, area, stratigraphic unit (SE), material inventory number, conservation location, and box number — is rendered using a consistent `styNormal` style derived from `getSampleStyleSheet`, with 7pt Cambria font and left alignment. Fields with `None` values are rendered with the label only and an empty value, while non-`None` values are included as strings alongside their respective labels.

##### getTable_en(self)

*No description available.*
Builds and returns a list of `Paragraph` objects representing sample record fields with English-language labels, formatted using a `Cambria` font style at size 7 with left alignment. Each field — including sample number, sample type, area, stratigraphic unit (SU), material inventory number, place of conservation, and box number — is rendered as a bold label followed by its corresponding instance attribute value. Fields whose attribute values are `None` or `"None"` are rendered with an empty value, and the resulting list is returned as `data`.

##### makeStyles(self)

*No description available.*
Defines and returns a `TableStyle` object configured with two style directives: a full-grid border (`'GRID'`) applied across all cells with a line width of `0.0` using black color, and top vertical alignment (`'VALIGN'`) applied across all cells. The style spans the entire table range from cell `(0, 0)` to `(-1, -1)`. The returned `TableStyle` instance is intended for use in formatting a ReportLab table.

### generate_campioni_pdf

*No description available.*
A PDF generation class for archaeological sample (*campioni*) documentation within the pyarchinit system. It produces three categories of PDF output — individual sample record sheets, sample index lists, sample box (*casse*) index lists, and box label sheets — each available in Italian, German (`_de`), and English (`_en`) variants. Output files are written to the directory defined by `PDF_path`, which is derived from the `PYARCHINIT_HOME` environment variable.

**Inherits from**: object

#### Methods

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it as `"%d-%m-%Y"` (day-month-year, e.g., `"31-12-2024"`). It takes no parameters beyond `self` and returns the formatted date string.

##### build_Champ_sheets(self, records)

*No description available.*
Iterates over the provided `records` collection and generates an individual PDF sheet for each record using `single_Campioni_pdf_sheet`, appending each created sheet followed by a `PageBreak` to an elements list. Assembles all elements into a single PDF document named `'Scheda Campioni.pdf'`, written to the path defined by `self.PDF_path`, using `SimpleDocTemplate` and `NumberedCanvas_Campionisheet` as the canvas maker. The output file is opened, built, and closed upon completion.

##### build_Champ_sheets_de(self, records)

Builds a multi-page PDF document named `Formular_proben.pdf` in the configured `PDF_path` directory, containing one German-language Campioni sheet per record. For each entry in `records`, it instantiates a `single_Campioni_pdf_sheet`, calls `create_sheet_de()` to generate the sheet content, and appends a `PageBreak` after each sheet. The resulting elements are compiled into a PDF using `SimpleDocTemplate` with `NumberedCanvas_Campionisheet` as the canvas maker.

##### build_Champ_sheets_en(self, records)

Builds a PDF document containing English-language sample (Campioni) sheets from a list of records. For each record, it instantiates a `single_Campioni_pdf_sheet` object, generates the English sheet via `create_sheet_en()`, and appends it to the element list followed by a `PageBreak`. The resulting elements are compiled into a `SimpleDocTemplate` PDF file named `Sample_form.pdf`, written to the path defined by `self.PDF_path`, using `NumberedCanvas_Campionisheet` as the canvas maker.

##### build_index_Campioni(self, records, sito)

Builds a PDF index document listing all sample records (*Campioni*) associated with a given excavation site. It resolves the logo path via a `Connection` object (falling back to a default `logo.jpg` if none is configured), constructs a formatted table from the provided `records` using `Campioni_index_pdf_sheet`, and assembles the final document with a heading, logo, and styled table using `SimpleDocTemplate` with `NumberedCanvas_Campioniindex`. The output is written to a file named `'Elenco Campioni.pdf'` in the instance's `PDF_path` directory, using a landscape A3-style page size of 29 × 21 cm.

##### build_index_Campioni_de(self, records, sito)

Generates a German-language PDF index report of sample records ("Proben") for a given excavation site. The method resolves the logo path via the `Connection` object, constructs a document header with the site name and current date, and builds a formatted table from the provided `records` using `Campioni_index_pdf_sheet.getTable_de()` and associated styles. The resulting PDF is written to `listen_proben.pdf` in the configured PDF output path, rendered on A4-landscape pages using `NumberedCanvas_Campioniindex`.

##### build_index_Campioni_en(self, records, sito)

Generates an English-language PDF index document listing sample records for a given site. It retrieves the logo path via `Connection`, builds a formatted table using `Campioni_index_pdf_sheet` and `getTable_en()` for each record, and assembles the document with a header containing the site name and current date. The resulting PDF is written to `list_samples.pdf` within the instance's `PDF_path` directory, rendered on A4-landscape pages using `NumberedCanvas_Campioniindex`.

##### build_index_Casse(self, records, sito)

Generates a PDF index document listing sample boxes ("Casse Campioni") for a given excavation site. It retrieves the logo path from the database connection, constructs a styled document containing a header with the site name, and builds a formatted table from the provided records using `CASSE_index_pdf_sheet`. The resulting PDF is written to a landscape A4-sized file named `'Elenco Casse Campioni.pdf'` in the configured PDF output path.

##### build_index_Casse_de(self, records, sito)

*No description available.*
Generates a German-language PDF index report ("LISTEN BOX PROBEN") for box/sample records associated with a given excavation site. The method resolves the logo path via the `Connection` object, constructs a formatted table by iterating over the provided `records` using `CASSE_index_pdf_sheet`, and assembles the document elements — including the logo, a heading with site name and date, and the styled table — into a `SimpleDocTemplate`. The resulting PDF is written to a file named `liste_box_proben.pdf` within the configured PDF output path.

##### build_index_Casse_en(self, records, sito)

*No description available.*
Generates a PDF index report of box samples in English for a given site, writing the output to a file named `list_box_samples.pdf` within the configured PDF path. The method resolves the logo image from the connection's configured logo path (falling back to a default location), constructs a headed table by iterating over the provided `records` using `CASSE_index_pdf_sheet`, and applies column widths of `[20, 350, 250, 100]` with styles derived from `exp_index.makeStyles()`. The document is built as a landscape A3-sized PDF (`29 cm × 21 cm`) using `SimpleDocTemplate` with fixed margin settings.

##### build_box_labels_Campioni(self, records, sito)

Generates a PDF file containing box labels for sample finds (*Campioni*) by iterating over the provided `records` and creating individual label sheets using `Box_labels_Campioni_pdf_sheet`. Each sheet is appended to the elements list followed by a `PageBreak`, then compiled into a single PDF document named `'Etichette Casse Campioni.pdf'` saved to the instance's `PDF_path` directory. The document is rendered with a landscape A4-equivalent page size (`29 cm × 21 cm`) and fixed margin settings via `SimpleDocTemplate`.

##### build_box_labels_Campioni_de(self, records, sito)

Generates a PDF document containing box labels for sample records (*Campioni*) in German, using the `Box_labels_Campioni_pdf_sheet` class to produce individual label sheets via `create_sheet_de()`. Each record in the provided `records` list is rendered as a separate page, separated by a `PageBreak()`. The resulting PDF is written to a file named `labels_box_proben.pdf` located in `self.PDF_path`, formatted as a landscape A4 page (29 × 21 cm) with 20-unit margins on all sides.

##### build_box_labels_Campioni_en(self, records, sito)

Generates a PDF file containing English-language box labels for sample records (`Campioni`), iterating over the provided `records` list to create one `Box_labels_Campioni_pdf_sheet` sheet per record using `create_sheet_en()`, with each sheet separated by a `PageBreak`. The resulting document is built using `SimpleDocTemplate` with a landscape A4 page size (`29 cm × 21 cm`) and uniform margins of 20 units on all sides. The output file is written in binary mode to `labels_box_samples.pdf` within the instance's configured `PDF_path` directory.

