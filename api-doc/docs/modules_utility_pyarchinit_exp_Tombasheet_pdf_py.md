# modules/utility/pyarchinit_exp_Tombasheet_pdf.py

## Overview

This file contains 45 documented elements.

## Classes

### NumberedCanvas_TOMBAsheet

*No description available.*
A subclass of `canvas.Canvas` that extends ReportLab's canvas with multi-page state tracking and automatic page numbering for TOMBA sheet documents. It accumulates page states on each call to `showPage()`, then on `save()` iterates over all saved states to render a "Pag. X di Y" label (using Cambria 5pt font, positioned at 200 mm × 20 mm) on every page before finalising the document. The `define_position` method delegates positioning to `self.page_position(pos)`.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

## `__init__` Method

Initializes a `NumberedCanvas_TOMBAsheet` instance by delegating to the parent `canvas.Canvas` constructor with all provided positional and keyword arguments. After the parent class is initialized, it sets up an instance-level `_saved_page_states` attribute as an empty list.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to `self.page_position(pos)`. This method serves as a named wrapper around `page_position`, accepting a single positional argument `pos` and forwarding it without modification.

##### showPage(self)

*No description available.*
Finalizes the current page by saving its state to the `_saved_page_states` list as a dictionary copy of the instance's current attribute dictionary. After preserving the page state, it initializes a new page by calling `_startPage()`.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Sets the font to "Cambria" at size 5, then draws a right-aligned pagination string in the format `"Pag. <current_page> di <total_pages>"` at the fixed position of 200 mm from the left and 20 mm from the bottom of the page. The `page_count` parameter represents the total number of pages, while the current page number is retrieved from the instance attribute `self._pageNumber`. This method is intended for use with a vertically oriented record sheet (scheda us verticale) sized 200 mm × 20 mm.

### NumberedCanvas_TOMBAindex

*No description available.*
A custom ReportLab canvas subclass that extends `canvas.Canvas` to support total page count numbering across a multi-page PDF document. It accumulates page states on each `showPage` call and, upon `save`, iterates over all saved states to render a right-aligned page indicator string ("Pag. X di Y") in Cambria 5pt font at position 270 mm × 10 mm before finalising the document. This class is intended for use as the canvas class in tomb index PDF report generation.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

*No description available.*
Initializes a `NumberedCanvas_TOMBAindex` instance by delegating to the parent `canvas.Canvas` constructor with all provided positional and keyword arguments. After the parent initialization, it sets up the `_saved_page_states` attribute as an empty list, which is used to track page state information across the canvas lifecycle.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to `self.page_position(pos)`. This method serves as a named wrapper around `page_position`, accepting a single positional argument `pos` and forwarding it without modification.

##### showPage(self)

*No description available.*
Finalizes the current page by saving its state to the `_saved_page_states` list as a copy of the current instance dictionary. After preserving the page state, it initializes a new page by calling `_startPage()`.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Draws a right-aligned page number string onto the current canvas page using the "Cambria" font at size 5. The text is formatted as `"Pag. %d di %d"`, displaying the current page number (`self._pageNumber`) and the total page count (`page_count`), positioned at coordinates `(270 mm, 10 mm)` from the origin.

**Parameters:**
- `page_count` (`int`): The total number of pages in the document.

### Tomba_index_pdf_sheet

*No description available.*
A data container and PDF table-row generator for burial record index sheets. Initialized with a data sequence, it stores burial-related fields including record number, structure code, individual number, rite, container type, deposition type, grave type, associated materials, chronological period and phase data, and extended dating. It exposes three locale-specific table-building methods — `getTable()` (Italian), `getTable_en()` (English), and `getTable_de()` (German) — each returning a list of formatted `Paragraph` objects for use in a ReportLab PDF table, as well as a `makeStyles()` method that returns a `TableStyle` with grid lines and top vertical alignment.

**Inherits from**: object

#### Methods

##### __init__(self, data)

*No description available.*
Initializes a `Tomba_index_pdf_sheet` instance by extracting and assigning specific fields from the provided `data` sequence to instance attributes. The mapped attributes include `nr_scheda_taf`, `sigla_struttura`, `nr_struttura`, `nr_individuo`, `rito`, `tipo_contenitore_resti`, `deposizione`, `sepoltura`, `materiali`, `periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`, and `datazione_estesa`, drawn from indices 1–5 and 13–23 of `data`. Several fields (indices 24–26) are present in the source but currently commented out and are not assigned.

##### getTable(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` objects representing the key fields of a burial record (tafonomia), styled using a customised `'Normal'` stylesheet entry with Cambria font at 7pt. Each field — including card number, structure identifier, individual number, rite, burial type, deposition type, extended dating, and associated materials — is rendered as a bold-labelled HTML-fragment paragraph, with `None`-valued fields producing an empty label. The method returns the assembled list as `data`, intended for use in PDF report generation via ReportLab.

##### getTable_en(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` objects representing the English-language version of a burial record table. Each paragraph is styled using a `Normal` stylesheet entry configured with Cambria font at size 7, left alignment, and defined spacing, and contains a bold label followed by the corresponding field value (e.g., form number, structure code, individual number, rite, container type, deposition type, grave type, associated materials, chronological periods, and extended dating). For fields that are `None`, an empty value is rendered; the materials field is assembled by iterating over an evaluated list of entries formatted as individual number, reference, and material type.

##### getTable_de(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` objects containing burial record fields rendered in German, intended for use in a PDF report table. Each field — including card number, structure code, individual number, rite, container type, deposition type, burial type, associated materials, chronological periods, and extended dating — is styled using a `Normal` stylesheet entry with left alignment, 7pt font size, and defined spacing. Fields sourced from instance attributes are checked for `None` before inclusion, and the materials list is parsed from a serialized string before being formatted into individual entries.

##### makeStyles(self)

*No description available.*
Constructs and returns a `TableStyle` object configured with two style directives: a `GRID` style applied to the entire table (from cell `(0, 0)` to `(-1, -1)`) using a line weight of `0.0` and black color, and a `VALIGN` style that sets the vertical alignment of all cells to `'TOP'`. The method takes no parameters beyond `self` and returns the resulting `TableStyle` instance directly.

### Tomba_index_II_pdf_sheet

*No description available.*
A PDF sheet model representing a tomb index record (type II) for archaeological burial documentation. The class accepts a structured data array in its constructor and extracts fields including tomb card number, structure code and number, individual number, burial rite, grave goods presence, orientation (axis and azimuth), stratigraphic unit references, elevation range, tomb measurements, and extended dating. It exposes three locale-specific table-generation methods — `getTable()` (Italian), `getTable_de()` (German), and `getTable_en()` (English) — each returning a list of formatted `Paragraph` objects for use in a ReportLab PDF layout, along with a `makeStyles()` method that returns a `TableStyle` defining grid and vertical alignment for the table.

**Inherits from**: object

#### Methods

##### __init__(self, data)

Initializes an instance of the class by extracting and assigning field values from a positional `data` sequence to the corresponding instance attributes. Attributes populated include `nr_scheda_taf`, `sigla_struttura`, `nr_struttura`, `nr_individuo`, `rito`, `corredo_presenza`, `orientamento_asse`, `orientamento_azimut`, `quota_min_strutt`, `quota_max_strutt`, `misure_tomba`, and `datazione_estesa`. The attributes `us_ind_list` and `us_str_list` are assigned from `data[28]` and `data[29]` respectively within a `try/except` block, silently ignoring any exception if those indices are unavailable.

##### getTable(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` objects representing the key fields of a burial record (scheda tafonomica) for use in a PDF report table. Each field — including card number, structure reference, individual number, associated stratigraphic units, min/max elevation, and extended dating — is styled using a `Normal` stylesheet entry configured with Cambria font at 7pt with left alignment. Fields whose values are `None` or empty are rendered as labelled paragraphs with blank content, while numeric values such as azimuth undergo unit conversion before display.

##### getTable_de(self)

*No description available.*
Builds and returns a list of German-language `Paragraph` objects representing the fields of a burial record, formatted using ReportLab's `getSampleStyleSheet` with a 7-point, left-aligned `Normal` style. Each paragraph corresponds to a specific data field — including field number, structure code, individual number, burial rite, grave goods, axis and azimuth orientation, stratigraphic units, elevation range, and extended dating — with bold German labels rendered as HTML within the paragraph markup. Fields whose underlying instance attributes are `None` or empty are rendered with the label only, omitting the value.

##### getTable_en(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` objects representing the English-language version of a burial record table. Each paragraph is styled using a `Normal` stylesheet with left alignment, 7pt font size, and defined spacing, and contains a bold field label paired with the corresponding instance attribute value (e.g., field number, structure code, individual number, rite, trousseau, axis orientation, azimuth, stratigraphic units, elevation range, and literal datation). Fields whose values are `None` or empty are rendered with the label only, and the azimuth value is converted via `self.PU.conversione_numeri` before display.

##### makeStyles(self)

*No description available.*
Constructs and returns a `TableStyle` object defining the visual formatting rules for a PDF table. The style applies a black grid border across all cells (from the top-left `(0, 0)` to the bottom-right `(-1, -1)`) with a line thickness of `0.0`, and sets the vertical alignment of all cell content to `'TOP'`.

### single_Tomba_pdf_sheet

*No description available.*
A PDF report generator for a single tomb (burial) record within the pyArchInit archaeological information system. The class accepts a structured data sequence in its constructor, storing burial attributes such as site identifier, structure code, individual number, burial rite, depositional data, grave goods, conservation state, and elevation measurements. It exposes locale-specific sheet generation methods (`create_sheet`, `create_sheet_de`, `create_sheet_en`, `create_sheet_fr`, `create_sheet_es`, `create_sheet_ar`, `create_sheet_ca`) that each compose and return a ReportLab `Table` object representing the formatted PDF record in Italian, German, English, or a fallback to English respectively.

**Inherits from**: object

#### Methods

##### __init__(self, data)

*No description available.*
Initializes an instance by unpacking a sequential `data` collection into 28 named instance attributes covering burial record fields. These attributes include site identification (`sito`), burial card and structure references (`nr_scheda_taf`, `sigla_struttura`, `nr_struttura`), individual and ritual details (`nr_individuo`, `rito`), descriptive and interpretive fields, physical characteristics of the burial, grave goods information, and chronological/stratigraphic data (`periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`, `datazione_estesa`). Elevation data for both the individual and the structure are stored in `quota_min_ind`, `quota_max_ind`, `quota_min_strutt`, and `quota_max_strutt`.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year). The formatted date string is returned as the method's result.

##### create_sheet(self)

Builds and returns a formatted ReportLab `Table` object representing a burial record sheet ("Scheda Tomba"). The method defines paragraph styles (normal, justified, and centered), constructs labeled `Paragraph` elements from the instance's fields (site information, periodization, structural elements, depositional data, grave goods, and elevation quotes), and assembles them into an 18-row, 10-column cell schema with corresponding span and grid table styles. A logo image is loaded from a path resolved via the `Connection` class and the `PYARCHINIT_HOME` environment variable, and is embedded in the header row of the table.

##### create_sheet_de(self)

Generates a German-language taphonomy field sheet as a ReportLab `Table` object, formatted with Cambria font and a 10-column grid layout spanning 22 rows. The method constructs styled `Paragraph` elements for all record fields — including site identification, periodization, structural characteristics, depositional and post-depositional data, taphonomic features, grave goods, measurements, and elevation data — with labels and values rendered in German. It applies a defined `table_style` specifying cell spanning, grid lines, and top vertical alignment, then returns the assembled `Table` with a fixed column width of 50 units.

##### create_sheet_en(self)

Generates and returns an English-language taphonomy form as a ReportLab `Table` object. The method constructs a 22-row, 10-column table populated with styled `Paragraph` elements covering site identification, periodization, structural elements, depositional and post-depositional data, taphonomic features, trousseau details, measurements, and elevation data. A logo image is loaded from a path resolved via the `Connection` class or a default directory, and all cell spanning and grid styling is applied through an explicit table style definition.

##### create_sheet_fr(self)

French version of Tomba sheet - uses English structure.
TODO: Add proper French translations for all labels.

##### create_sheet_es(self)

Spanish version of Tomba sheet - uses English structure.
TODO: Add proper Spanish translations for all labels.

##### create_sheet_ar(self)

Arabic version of Tomba sheet - uses English structure.
TODO: Add proper Arabic translations for all labels.

##### create_sheet_ca(self)

Catalan version of Tomba sheet - uses English structure.
TODO: Add proper Catalan translations for all labels.

### generate_tomba_pdf

*No description available.*
A PDF generation class responsible for producing taphonomic record sheets and index documents from tomb (tomba) records. It provides locale-aware build methods supporting Italian, German, English, French, Spanish, Arabic, and Catalan outputs, each writing a `SimpleDocTemplate`-based PDF to the `pyarchinit_PDF_folder` directory using `NumberedCanvas_TOMBAsheet` or `NumberedCanvas_TOMBAindex` as the canvas maker. The `build_index_Tomba` method additionally generates two index PDFs — a primary tomb listing and a stratigraphic reference listing — with column widths, headings, and output filenames determined by the value of the `L` class attribute, which is derived from the QGIS locale setting.

**Inherits from**: object

#### Methods

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, e.g., `"31-12-2024"`). The formatted date string is then returned to the caller.

##### build_Tomba_sheets(self, records)

Iterates over the provided `records` collection, generating an individual PDF sheet for each record by instantiating `single_Tomba_pdf_sheet` and calling its `create_sheet()` method, with a `PageBreak` appended after each sheet. Assembles all elements into a single PDF document named `'Scheda Tomba.pdf'`, written to the path defined by `self.PDF_path`. The document is built using `SimpleDocTemplate` with `NumberedCanvas_TOMBAsheet` as the canvas maker, and the output file is closed upon completion.

##### build_Tomba_sheets_de(self, records)

Generates a multi-page German-language taphonomy PDF document from a list of records. For each record, it instantiates a `single_Tomba_pdf_sheet` object, calls `create_sheet_de()` to produce the German sheet content, and appends a `PageBreak` after each sheet. The resulting elements are compiled into a PDF file named `Formular_taphonomie.pdf`, saved to `self.PDF_path`, and built using `SimpleDocTemplate` with `NumberedCanvas_TOMBAsheet` as the canvas maker.

##### build_Tomba_sheets_en(self, records)

Builds an English-language PDF document containing taphonomic form sheets from a collection of records. For each record, it instantiates a `single_Tomba_pdf_sheet` object, generates an English sheet via `create_sheet_en()`, and appends it to the element list followed by a `PageBreak`. The resulting document is written to a file named `Taphonomic_form.pdf` in the path specified by `self.PDF_path`, using `NumberedCanvas_TOMBAsheet` as the canvas maker.

##### build_Tomba_sheets_fr(self, records)

French version

##### build_Tomba_sheets_es(self, records)

Spanish version

##### build_Tomba_sheets_ar(self, records)

Arabic version

##### build_Tomba_sheets_ca(self, records)

Catalan version

##### build_index_Tomba(self, records, sito)

Generates two separate indexed PDF reports for tomb (taphonomic) records associated with a given excavation site. The first PDF lists tomb entries using `Tomba_index_pdf_sheet`, and the second lists their stratigraphic references using `Tomba_index_II_pdf_sheet`; both documents are built with `NumberedCanvas_TOMBAindex` and rendered in landscape A3-like format. Output filenames, header text, and table data are localized based on `self.L`, supporting Italian (`'it'`), German (`'de'`), and a default English variant; the logo is resolved either from a database connection path or a locale-specific default.

