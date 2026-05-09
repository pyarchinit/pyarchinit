# modules/utility/pyarchinit_exp_Individui_pdf.py

## Overview

This file contains 33 documented elements.

## Classes

### NumberedCanvas_Individuisheet

*No description available.*
A subclass of `canvas.Canvas` that extends the ReportLab canvas with multi-page state tracking and automatic page numbering for individual record sheets. It accumulates page states on each `showPage` call and, upon `save`, iterates over all saved states to render a page number string in the format `"Pag. X di Y"` at a fixed position (200 mm × 20 mm), drawn right-aligned in Cambria 5pt font. The class also exposes a `define_position` method that delegates to `page_position`.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

*No description available.*
Initializes a `NumberedCanvas_Individuisheet` instance by delegating to the parent `canvas.Canvas` constructor with all provided positional and keyword arguments. After the parent initialization, it sets up an instance-level attribute `_saved_page_states` as an empty list, intended to track page state data across the canvas lifecycle.

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
Renders a page number indicator on the current canvas page using the "Cambria" font at size 5. The text is right-aligned at position (200 mm, 20 mm) and follows the format `"Pag. %d di %d"`, displaying the current page number (`self._pageNumber`) alongside the total page count (`page_count`).

### NumberedCanvas_Individuiindex

*No description available.*
A custom ReportLab canvas class that extends `canvas.Canvas` to support total page count numbering across a generated PDF document. It accumulates page states during rendering and, upon saving, iterates over all stored states to annotate each page with a "Pag. X di Y" string drawn in Cambria 5pt font at position (270 mm, 10 mm). The `save` method finalizes the document by replaying each saved page state, applying the page number footer, and delegating to the base `canvas.Canvas.save`.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

*No description available.*
Initializes a new instance of the `NumberedCanvas_Individuiindex` class by delegating to the parent `canvas.Canvas` constructor with all provided positional and keyword arguments. Following the parent initialization, it sets up the `_saved_page_states` instance attribute as an empty list.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to `self.page_position(pos)` with the provided argument. This method serves as a named wrapper around `page_position`, accepting a single positional parameter `pos`.

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current canvas state to the `_saved_page_states` list. After preserving the state, it initializes a new page by calling `_startPage()`. This method is typically called when the content of the current page is complete and rendering should continue on a new page.

##### save(self)

Finalizes the document by iterating over all saved page states and injecting the total page count into each page via `draw_page_number` before committing it to the canvas. For each saved state, the instance dictionary is restored, `draw_page_number` is called with the total number of pages, and `canvas.Canvas.showPage` is invoked to close that page. Once all pages have been processed, `canvas.Canvas.save` is called to complete and write the final document.

##### draw_page_number(self, page_count)

*No description available.*
Renders a right-aligned page number string onto the current canvas page using the "Cambria" font at size 5. The text is formatted as `"Pag. %d di %d"` — displaying the current page number (`self._pageNumber`) and the total page count (`page_count`) — and is positioned at coordinates `(270 mm, 10 mm)`.

**Parameters:**
- `page_count` *(int)*: The total number of pages in the document.

### Individui_index_pdf_sheet

**`Individui_index_pdf_sheet`**

A data container and PDF table-row builder for individual (skeletal/burial) records in an archaeological context. It is initialised from a data sequence, extracting fields such as individual number, area, stratigraphic unit (US), structure reference, sex, and minimum/maximum age with age class. It exposes three locale-specific table-generation methods — `getTable` (Italian), `getTable_de` (German), and `getTable_en` (English) — each returning a list of styled `Paragraph` objects suitable for use in a ReportLab table, along with a `makeStyles` method that returns a `TableStyle` defining grid lines and top vertical alignment.

**Inherits from**: object

#### Methods

##### __init__(self, data)

Initializes an `Individui_index_pdf_sheet` instance by extracting and assigning individual record fields from the provided `data` sequence using positional indices. The assigned attributes include `area`, `us`, `nr_individuo`, `sesso`, `eta_min`, `eta_max`, `classi_eta`, `sigla_struttura`, and `nr_struttura`, mapped respectively from indices 1, 2, 3, 6, 7, 8, 9, 11, and 12 of `data`. Note that indices 0, 4, 5, and 10 are not mapped to any attribute.

##### getTable(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` objects representing the key fields of an individual archaeological record, styled using a 'Normal' stylesheet with 7pt Cambria font and left alignment. Each paragraph contains a bold label and its corresponding field value, covering: individual number, structure (sigla and number), area, stratigraphic unit (US), minimum age, maximum age, and age class. Fields whose values are `None` or the string `"None"` are rendered with an empty value rather than the literal null representation.

##### getTable_de(self)

*No description available.*
Generates a list of formatted `Paragraph` objects containing German-language labels and their corresponding instance field values, intended for use in a PDF report table. Each field — individual number (`nr_individuo`), area (`area`), stratigraphic unit (`us`), minimum age estimate (`eta_min`), maximum age estimate (`eta_max`), and age class (`classi_eta`) — is rendered with a bold German label followed by its value, using a configured `Normal` style with 7pt font size and left alignment. `None` or `"None"` values result in paragraphs with the label only and no value text.

##### getTable_en(self)

*No description available.*
Builds and returns a list of English-language `Paragraph` objects representing the fields of an individual record, formatted for use in a PDF report table. Each field — individual number, area, stratigraphic unit (SU), minimum age, maximum age, and age class — is rendered using a `Cambria` font style at size 7 with left alignment, and displays an empty value when the corresponding instance attribute is `None`. The returned list follows the order: `individuo`, `area`, `us`, `eta_min`, `eta_max`, `classi_eta`.

##### makeStyles(self)

*No description available.*
Creates and returns a `TableStyle` object configured with two style directives: a `GRID` rule that applies a black border with `0.0` line width across all cells (from `(0, 0)` to `(-1, -1)`), and a `VALIGN` rule that sets the vertical alignment to `'TOP'` for all cells. The style is applied uniformly to the entire table range.

### single_Individui_pdf_sheet

*No description available.*
A PDF sheet generator for individual skeletal records in an archaeological context. The class is initialized with a positional data sequence mapped to fields covering site identification (`sito`, `area`, `us`, `nr_individuo`), biological profile (`sesso`, `eta_min`, `eta_max`, `classi_eta`), skeletal condition and position (`completo`, `disturbato`, `connessione`, `posizione_scheletro`, `posizione_cranio`, `posizione_arti_sup`, `posizione_arti_inf`), orientation (`orientamento_asse`, `orientamento_azimut`), and recording metadata (`data_schedatura`, `schedatore`, `osservazioni`). It exposes three table-building methods — `create_sheet`, `create_sheet_de`, and `create_sheet_en` — which produce a ReportLab `Table` object rendering the individual's data in Italian, German, and English respectively, each incorporating a configurable logo image resolved via a `Connection` instance.

**Inherits from**: object

#### Methods

##### __init__(self, data)

Initializes a `single_Individui_pdf_sheet` instance by unpacking a sequential `data` list into named instance attributes representing an individual's archaeological record. The attributes cover site identification fields (`sito`, `area`, `us`, `nr_individuo`), scheduling metadata (`data_schedatura`, `schedatore`), biological profile (`sesso`, `eta_min`, `eta_max`, `classi_eta`), structural references (`sigla_struttura`, `nr_struttura`), and skeletal observation fields (`completo`, `disturbato`, `connessione`, `lunghezza_scheletro`, `posizione_scheletro`, `posizione_cranio`, `posizione_arti_sup`, `posizione_arti_inf`, `orientamento_asse`, `orientamento_azimut`, `osservazioni`). The `data` parameter must contain at least 23 elements indexed from `0` to `22`.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the `"%d-%m-%Y"` pattern (day-month-year). The formatted date string is then returned to the caller.

##### create_sheet(self)

Builds and returns a formatted ReportLab `Table` object representing an individual archaeological record sheet ("SCHEDA INDIVIDUI"). The method defines two paragraph styles (left-aligned and justified), constructs `Paragraph` objects for all record fields (site, area, stratigraphic unit, individual number, sex, age, skeletal attributes, observations, and scheduling metadata), and loads a logo image from a path resolved via the `Connection` class or a default location. The resulting table is assembled using a predefined cell schema and a table style that specifies grid lines, cell spanning, and vertical alignment across a 10-column, 12-row layout.

##### create_sheet_de(self)

Generates a German-language PDF table sheet for an individual archaeological record using ReportLab. The method builds styled `Paragraph` objects for fields such as excavation site, area, stratigraphic unit, individual number, sex, estimated age range, age class, observations, date, and recorder — with labels rendered in German. It assembles these elements into a 10-column `Table` with defined span and alignment styles and returns the resulting `Table` object.

##### create_sheet_en(self)

Builds and returns a ReportLab `Table` object representing an English-language individual (anthropological) record sheet. The method constructs styled `Paragraph` elements for fields including site, area, stratigraphic unit, individual number, sex, minimum and maximum age, age class, notes, recording date, and recorder, loading a configurable logo image from the pyArchInit home directory. The resulting table is assembled with a predefined cell schema, column width of 50, and a grid-based style that applies appropriate cell spanning and vertical alignment.

### generate_pdf

*No description available.*
A PDF generation class for producing archaeological individual (Individui) record documents within the pyarchinit system. It exposes methods to build both detailed per-record sheets and tabular index listings in three languages — Italian, German (`_de`), and English (`_en`) — writing the resulting files to the directory defined by `PDF_path`, which is derived from the `PYARCHINIT_HOME` environment variable. The class also provides a `datestrfdate` helper that returns the current date formatted as `DD-MM-YYYY`.

**Inherits from**: object

#### Methods

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it as `DD-MM-YYYY` via `strftime("%d-%m-%Y")`. The formatted date string is then returned to the caller.

##### build_Individui_sheets(self, records)

*No description available.*
Iterates over the provided `records` collection and generates an individual PDF sheet for each record by instantiating `single_Individui_pdf_sheet` and calling its `create_sheet()` method, appending a `PageBreak` after each sheet. All generated elements are compiled into a single PDF file named `'Scheda Individui.pdf'`, written to the path defined by `self.PDF_path`. The document is built using `SimpleDocTemplate` with `NumberedCanvas_Individuisheet` as the canvas maker, and the output file is closed upon completion.

##### build_Individui_sheets_de(self, records)

Generates a multi-page PDF document containing individual sheets in German, one per record, from the provided `records` collection. For each record, it instantiates a `single_Individui_pdf_sheet` object, calls its `create_sheet_de()` method to produce the German-language sheet content, and appends a `PageBreak` after each sheet. The resulting elements are compiled into a PDF file named `Formular_individuel.pdf`, written to `self.PDF_path`, and built using `SimpleDocTemplate` with `NumberedCanvas_Individuisheet` as the canvas maker.

##### build_Individui_sheets_en(self, records)

Builds a multi-page PDF document containing individual sheets in English for a collection of records. Iterates over the provided `records` list, instantiating a `single_Individui_pdf_sheet` for each record and appending its English-language sheet along with a `PageBreak` to the elements list. The resulting document is written to `Individual_form.pdf` in the configured PDF output path, using `NumberedCanvas_Individuisheet` as the canvas maker.

##### build_index_individui(self, records, sito)

Builds a PDF index document listing all individuals (*individui*) associated with a given excavation site. It resolves the logo path via a database connection, constructs a styled ReportLab document containing a header with the site name and a formatted table of records generated from `Individui_index_pdf_sheet`, and writes the output to a file named `'Elenco Individui.pdf'` in the configured PDF path. The document is rendered in landscape A3-like format (`29 cm × 21 cm`) using `NumberedCanvas_Individuiindex` as the canvas maker.

##### build_index_individui_de(self, records, sito)

Generates a German-language PDF index document listing individual records for a given excavation site. It retrieves the logo path via `Connection`, constructs a formatted table using `Individui_index_pdf_sheet` instances with German-style column layout (`getTable_de()`), and assembles the document with a heading in German ("LISTE INDIVIDUEL", "Ausgrabungsstätte") before writing the output to `liste_individuel.pdf` in the configured PDF path. The document is built on A3 landscape page size (`29 cm × 21 cm`) using `SimpleDocTemplate` with `NumberedCanvas_Individuiindex` as the canvas maker.

##### build_index_individui_en(self, records, sito)

Generates a PDF index document in English listing individual records for a given site. The method constructs a landscape-oriented PDF (29 × 21 cm) containing a logo, a heading with the site name and current date, and a formatted table built from the provided `records` using `Individui_index_pdf_sheet` with column widths `[60, 60, 60, 60, 60, 250]`. The output is written to `individual_list.pdf` in the configured PDF path, rendered with `NumberedCanvas_Individuiindex` as the canvas maker.

