# modules/utility/pyarchinit_exp_Tafonomiasheet_pdf.py

## Overview

This file contains 37 documented elements.

## Classes

### NumberedCanvas_TOMBAsheet

*No description available.*
A subclass of `canvas.Canvas` that extends the ReportLab canvas with multi-page tracking and automatic page numbering for TOMBA sheet documents. It accumulates page states during rendering by overriding `showPage`, then on `save` iterates over all saved states to stamp each page with a "Pag. X di Y" footer string rendered in 8pt Helvetica at position 200mm × 20mm. The `draw_page_number` method performs the actual footer rendering, using the total page count and the internal `_pageNumber` value to compose the pagination label.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

## `__init__` Method

Initializes a `NumberedCanvas_TOMBAsheet` instance by delegating to the parent `canvas.Canvas` constructor with all provided positional and keyword arguments. After the parent initialization, it sets up an instance-level `_saved_page_states` attribute as an empty list, which is used to track page states across the canvas lifecycle.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to `self.page_position(pos)`. This method serves as a named wrapper, accepting a single `pos` argument and forwarding it unchanged to the underlying `page_position` call.

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current canvas state to the `_saved_page_states` list. After preserving the state, it initializes a new page by calling `_startPage()`. This method is typically called to mark the end of a page before beginning content on the next one.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Sets the font to Helvetica at size 8, then draws a right-aligned page indicator string at position `(200 mm, 20 mm)` on the canvas. The string is formatted as `"Pag. %d di %d"`, displaying the current page number (`self._pageNumber`) and the total page count (`page_count`).

### NumberedCanvas_TOMBAindex

*No description available.*
A subclass of `canvas.Canvas` that extends the ReportLab canvas to support total page count in page numbering. It defers page rendering by saving each page's state in `_saved_page_states` during `showPage()`, then iterates over all saved states at `save()` time to call `draw_page_number()` on each page before finalising the document. The `draw_page_number()` method renders a right-aligned pagination string in Helvetica 8pt at position `(270mm, 10mm)`, formatted as `"Pag. %d di %d"` with the current page number and total page count.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

*No description available.*
Initializes a `NumberedCanvas_TOMBAindex` instance by delegating to the parent `canvas.Canvas` constructor with all provided positional and keyword arguments. After the parent initialization, it sets up the `_saved_page_states` attribute as an empty list, which is used to track page state information across the canvas instance.

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
Renders a page number indicator onto the current canvas page using an 8-point Helvetica font. The text is right-aligned at position `(270 mm, 10 mm)` and is formatted as `"Pag. %d di %d"`, displaying the current page number (`self._pageNumber`) alongside the total page count (`page_count`).

**Parameters:**
- `page_count` (`int`): The total number of pages in the document.

### Tomba_index_pdf_sheet

*No description available.*
A data container and PDF table-row generator for tomb (burial) index records. It stores burial-related fields extracted from a positional data array — including record number, structure identifiers, individual number, rite, container type, orientation, grave goods presence, completeness/disturbance flags, stratigraphic period and phase ranges, and extended dating — and exposes three locale-specific table-building methods (`getTable`, `getTable_de`, `getTable_en`) that produce lists of styled `Paragraph` objects for Italian, German, and English output respectively. A `makeStyles` method returns a `TableStyle` defining a black grid with top vertical alignment for use when rendering the generated data in a ReportLab table.

**Inherits from**: object

#### Methods

##### __init__(self, data)

*No description available.*
Initializes a `Tomba_index_pdf_sheet` instance by extracting and assigning a fixed set of fields from the provided `data` sequence using explicit index positions. The assigned attributes include `nr_scheda_taf`, `sigla_struttura`, `nr_struttura`, `nr_individuo`, `rito`, `tipo_contenitore_resti`, `orientamento_asse`, `orientamento_azimut`, `corredo_presenza`, `completo_si_no`, `disturbato_si_no`, `in_connessione_si_no`, `periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`, and `datazione_estesa`, drawn from indices 1 through 32 of `data`. Note that not all intermediate indices are used; the mapping follows a non-contiguous selection as defined in the source.

##### getTable(self)

Builds and returns a list of formatted `Paragraph` objects representing the fields of a burial record (tafonomia scheda) for use in a PDF report. Each field — including card number, structure identifier, individual number, rite, grave goods, completeness, disturbance, connection status, and chronological phase data — is rendered with a bold label and its corresponding instance attribute value, using a 7-point Cambria `Normal` style with defined spacing and left alignment. Fields whose instance attributes are `None` are rendered with an empty value rather than omitted.

##### getTable_de(self)

Builds and returns a list of German-language `Paragraph` objects representing the fields of a burial record (tafonomia) for use in a PDF table. Each field label is rendered in German (e.g., "N° Feld", "Ritus", "Grabbeigabe", "Anfangszeitraum") using a `Normal` style with a font size of 7 and left alignment. Fields whose corresponding instance attribute is `None` are rendered with an empty value, while non-`None` values are appended to the label string.

##### getTable_en(self)

*No description available.*
Builds and returns a list of English-language `Paragraph` objects representing the fields of a burial record, formatted using a `Normal` stylesheet with a font size of 7 and left alignment. Each field — including Field Nr., Structure code, Structure Nr., Individual Nr., Rite, Container type, Axes orientation, Azimut, Trousseau, Complete, Hampered, In connection, Start period, Start phase, Final period, Final phase, and Litteral datation — is rendered as a bold label followed by its corresponding instance attribute value. Fields whose instance attributes are `None` are rendered with an empty value rather than the string `"None"`.

##### makeStyles(self)

*No description available.*
Constructs and returns a `TableStyle` object configured with two style directives: a `GRID` rule that applies a black border of width `0.0` across all cells (from `(0, 0)` to `(-1, -1)`), and a `VALIGN` rule that sets the vertical alignment of all cells to `'TOP'`. The style is applied uniformly to the entire table range. Returns the resulting `TableStyle` instance.

### Tomba_index_II_pdf_sheet

*No description available.*
Generates a structured PDF index sheet for a burial record (tomba) containing fields such as record number, structure code, individual number, rite, grave goods presence, orientation axis and azimuth, stratigraphic units (individual and structural), minimum/maximum elevations, and extended dating. The class provides three locale-specific variants of the data table — `getTable()` for Italian, `getTable_de()` for German, and `getTable_en()` for English — each returning a list of formatted `Paragraph` objects styled at 7pt with left alignment. The `makeStyles()` method returns a `TableStyle` applying a black grid border and top vertical alignment across all cells.

**Inherits from**: object

#### Methods

##### __init__(self, data)

*No description available.*
Initializes an instance by extracting and assigning specific fields from the `data` sequence to their corresponding instance attributes. Fields assigned include `nr_scheda_taf`, `sigla_struttura`, `nr_struttura`, `nr_individuo`, `rito`, `corredo_presenza`, `orientamento_asse`, `orientamento_azimut`, `quota_min_strutt`, `quota_max_strutt`, `misure_tomba`, and `datazione_estesa`, mapped to fixed indices within `data`. The attributes `us_ind_list` and `us_str_list` are assigned from `data[38]` and `data[39]` respectively within a `try/except` block, leaving them at their class-level defaults if those indices are unavailable.

##### getTable(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` objects representing the key fields of a burial record (scheda tafonomica) for use in a PDF report. Each field — including card number, structure identifier, individual number, rite, grave goods presence, orientation, stratigraphic units, elevation range, and extended dating — is rendered with a bold label and its corresponding data value using a 7-point left-aligned Normal style. Fields whose values are `None` or empty are rendered with the label only, and azimuth values undergo a numeric conversion before display.

##### getTable_de(self)

*No description available.*
Builds and returns a list of German-language `Paragraph` objects representing the fields of a burial record, formatted using ReportLab's `getSampleStyleSheet` with a 7pt left-aligned `Normal` style. Each paragraph contains a bold German label and the corresponding instance attribute value, covering fields such as field number (`N° Feld`), structure code (`Strukturcode`), individual number (`Nr Individuel`), rite (`Ritus`), grave goods (`Grabbeigabe`), axis orientation (`Achse`), azimuth (`Azimut`), stratigraphic units, elevation range (`Höhe Min-max`), and extended dating (`Erweiterte Datierung`). Fields whose instance attributes are `None` or `"None"` are rendered with an empty value, and the azimuth value is converted via `self.PU.conversione_numeri` before display.

##### getTable_en(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` objects representing the English-language version of a burial record table. Each paragraph is styled using a `Normal` stylesheet with left alignment, 7pt font size, and defined spacing, and contains a bold field label paired with its corresponding instance attribute value. Fields covered include field number, structure code, individual number, rite, trousseau, axis orientation, azimuth, stratigraphic units (individual and structural), elevation min/max, and literal datation; `None` values are handled gracefully by rendering an empty field.

##### makeStyles(self)

*No description available.*
Constructs and returns a `TableStyle` object defining the visual formatting rules for a PDF table. The style applies a black grid border across all cells (from the top-left cell `(0, 0)` to the bottom-right cell `(-1, -1)`) with a line width of `0.0`, and sets the vertical alignment of all cell content to `'TOP'`.

### single_Tomba_pdf_sheet

*No description available.*
A PDF sheet generator for a single taphonomic burial record (scheda tafonomica), used within the pyArchInit QGIS plugin. The class is initialized with a positional data list of 38 fields covering burial identification, periodization, structural elements, depositional and post-depositional data, skeletal position, grave goods, measurements, and elevation quotas. It exposes three sheet-generation methods — `create_sheet`, `create_sheet_de`, and `create_sheet_en` — which produce a ReportLab `Table` object containing all field data formatted in Italian, German, and English respectively, incorporating a configurable logo loaded via the `Connection` class.

**Inherits from**: object

#### Methods

##### __init__(self, data)

*No description available.*
Initializes an instance by unpacking a sequential `data` collection (indexed 0–37) into 38 named instance attributes representing the fields of a burial record (*scheda di tafonomia*). The attributes cover site identification, structural references, burial rite, skeletal description, grave goods, conservation state, orientation, stratigraphic phasing, and elevation measurements. The `data` parameter must be an ordered sequence with at least 38 elements corresponding exactly to the expected field positions.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year). The formatted date string is returned as the method's result.

##### create_sheet(self)

Builds and returns a formatted ReportLab `Table` object representing a taphonomic record sheet ("Scheda Tafonomica") for a single individual. The method constructs all cell content as styled `Paragraph` elements covering identification data, periodization, structural elements, depositional and post-depositional data, taphonomic characteristics, grave goods, measurements, and elevation readings, then arranges them into a 22-row by 10-column grid with a corresponding span and alignment style definition. A logo image is loaded from a path resolved via the `Connection` class or a default location, and the current date is included in the sheet header via `datestrfdate()`.

##### create_sheet_de(self)

Generates a German-language (`de`) taphonomy field sheet as a ReportLab `Table` object for a burial record. The method constructs a 22-row, 10-column table containing formatted `Paragraph` elements covering burial identification, periodization, structural characteristics, depositional and post-depositional data, taphonomic features, grave goods, measurements, and elevation data — all labeled in German. Cell spanning, grid styling, and top vertical alignment are applied via a defined `table_style`, and a logo image is loaded from a configurable path resolved through the `Connection` class.

##### create_sheet_en(self)

Generates an English-language taphonomy form as a ReportLab `Table` object for a single burial record. The method constructs styled `Paragraph` elements for all form fields — including site identification, periodization, structural elements, depositional and post-depositional data, taphonomic features, trousseau details, measurements, and elevation data — using labels translated into English. It assembles these elements into a 22-row, 10-column `cell_schema` with defined span rules and a uniform grid style, then returns the resulting `Table` instance with a column width of 50 units.

### generate_tomba_pdf

*No description available.*
A PDF generation class responsible for producing taphonomic record sheets and index documents in multiple languages (Italian, German, and English). It provides methods to build individual taphonomic form PDFs (`build_Tomba_sheets`, `build_Tomba_sheets_de`, `build_Tomba_sheets_en`) and a consolidated index document (`build_index_Tomba`) containing two formatted tables summarising taphonomic records and taphonomic structure records for a given excavation site. Output files are written to the `pyarchinit_PDF_folder` directory resolved from the `PYARCHINIT_HOME` environment variable, with filenames and content language determined by the active QGIS locale setting.

**Inherits from**: object

#### Methods

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, e.g., `"31-12-2024"`). No parameters are accepted beyond the implicit `self`.

##### build_Tomba_sheets(self, records)

*No description available.*
Iterates over a collection of records and generates a single PDF document containing one taphonomic sheet per page, separated by page breaks. For each record, an instance of `single_Tomba_pdf_sheet` is created and its `create_sheet()` method is called to produce the page content. The resulting PDF is written to a file named `scheda_Tafonomica.pdf` located at `self.PDF_path`, using `SimpleDocTemplate` and `NumberedCanvas_TOMBAsheet` as the canvas maker.

##### build_Tomba_sheets_de(self, records)

Generates a German-language taphonomy PDF report (`Formular_taphonomie.pdf`) from a collection of records. For each record, it instantiates a `single_Tomba_pdf_sheet` object, calls `create_sheet_de()` to produce the German sheet content, and appends a `PageBreak` after each sheet. The resulting elements are compiled into a `SimpleDocTemplate` document using `NumberedCanvas_TOMBAsheet` and written to the configured `PDF_path` directory.

##### build_Tomba_sheets_en(self, records)

Builds an English-language taphonomic form PDF document from a list of records. Iterates over the provided `records`, creating a `single_Tomba_pdf_sheet` instance for each record and appending its English sheet representation along with a `PageBreak` to the elements list. The resulting elements are compiled into a file named `Taphonomic_form.pdf` at the path specified by `self.PDF_path`, using `SimpleDocTemplate` and `NumberedCanvas_TOMBAsheet` as the canvas maker.

##### build_index_Tomba(self, records, sito)

*No description available.*
Generates two separate paginated PDF index documents for taphonomic form records associated with a given excavation site. The first PDF lists primary taphonomic sheet data (`Tomba_index_pdf_sheet`) and the second lists secondary taphonomic structure data (`Tomba_index_II_pdf_sheet`), each formatted as a landscape-oriented table (`29 cm × 21 cm`) with a site logo, a localized heading, and column widths defined per document. Output filenames, table content, and heading text are determined by the instance's language setting (`self.L`), supporting Italian (`'it'`), German (`'de'`), and a default English fallback.

