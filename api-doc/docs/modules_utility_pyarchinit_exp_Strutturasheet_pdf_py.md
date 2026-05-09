# modules/utility/pyarchinit_exp_Strutturasheet_pdf.py

## Overview

This file contains 49 documented elements.

## Classes

### NumberedCanvas_STRUTTURAindex

*No description available.*
A subclass of `canvas.Canvas` that extends ReportLab's canvas with multi-page state tracking and automatic page numbering for STRUTTURA index documents. It accumulates page states on each call to `showPage()`, then on `save()` iterates over all saved states to render a "Pag. X di Y" label in Cambria 5pt font, right-aligned at position (270 mm, 10 mm) on every page. The total page count is determined from the number of saved page states collected during document generation.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

Initializes a `NumberedCanvas_STRUTTURAindex` instance by delegating to the parent `canvas.Canvas.__init__` method with all provided positional and keyword arguments. After the parent class is initialized, an empty list `_saved_page_states` is assigned to the instance to track page states.

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
Renders a right-aligned page number string onto the current canvas page using the "Cambria" font at size 5. The text is drawn at a fixed position of 270 mm from the left and 10 mm from the bottom of the page, formatted as `"Pag. %d di %d"` using the current page number (`self._pageNumber`) and the total page count (`page_count`).

### NumberedCanvas_STRUTTURAsheet

*No description available.*
A subclass of `canvas.Canvas` that extends the ReportLab canvas to support total page count in page numbering. It defers page rendering by saving each page's state in `_saved_page_states` during `showPage()`, then iterates over all saved states at `save()` time to inject the "Pag. X di Y" string before finalising the document. The page number label is drawn using the `"Cambria"` font at size 5, right-aligned at the position `200 mm × 20 mm` on each page.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

Initializes a `NumberedCanvas_STRUTTURAsheet` instance by delegating to the parent `canvas.Canvas.__init__` method, passing through all positional and keyword arguments. It also initializes the `_saved_page_states` instance attribute as an empty list.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to `self.page_position(pos)`. This method serves as a named wrapper around `page_position`, accepting a single positional argument `pos` and forwarding it without modification.

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current canvas state to the `_saved_page_states` list. After preserving the state, it initializes a new page by calling `_startPage()`. This method is typically called to mark the end of a page before proceeding to define content on a subsequent page.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Sets the font to "Cambria" at size 5, then draws a right-aligned page number string at the position 200 mm from the left and 20 mm from the bottom of the canvas. The string is formatted as `"Pag. %d di %d"`, displaying the current page number (`self._pageNumber`) and the total page count (`page_count`).

**Parameters:**
- `page_count` *(int)*: The total number of pages in the document.

### Struttura_index_pdf_sheet

*No description available.*
A data container and PDF table-row builder for a single archaeological structure index entry. It is initialized from a data sequence, extracting fields such as structure code, number, category, typology, definition, initial and final period and phase, and extended dating. It provides locale-specific `getTable` methods (Italian, German, English, French, Spanish, Arabic, Catalan) that return a list of styled `Paragraph` objects for use in a ReportLab PDF table, along with a `makeStyles` method that returns a `TableStyle` applying a black grid and top vertical alignment.

**Inherits from**: object

#### Methods

##### __init__(self, data)

Initializes a `Struttura_index_pdf_sheet` instance by extracting and assigning structural record fields from the provided `data` sequence. The constructor maps specific indexed elements of `data` to instance attributes representing the structure's identifier (`sigla_struttura`), number (`numero_struttura`), category (`categoria_struttura`), typology (`tipologia_struttura`), definition (`definizione_struttura`), initial and final period and phase (`periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`), and extended dating (`datazione_estesa`). Note that indices 0, 6, and 7 of `data` are not assigned to any attribute.

##### getTable(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` objects representing the structural record's fields, using a customised `Normal` stylesheet with predefined font, size, and alignment settings. Each paragraph contains a bold label and the corresponding instance attribute value, covering: sigla, structure number, category, typology, definition, initial period, initial phase, final period, final phase, and extended dating. The returned list is intended for use in report table generation.

##### getTable_de(self)

*No description available.*
Generates a list of formatted `Paragraph` objects containing structural record data with German-language labels, intended for use in a PDF table. The method applies a `Normal` stylesheet with left alignment, font size 7, and defined spacing, then constructs labelled fields for the structure's code, number, category, typology, definition, initial and final period and phase, and extended dating. Returns a list of ten `Paragraph` elements representing these fields.

##### getTable_en(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` objects representing the English-language version of a structure's data table. Each paragraph is styled using the `'Normal'` stylesheet with left alignment, a font size of 7, and 20-unit spacing before and after, with bold field labels rendered above their corresponding instance attribute values. The returned list contains ten entries covering: code (`sigla_struttura`), structure number, category, typology, definition, starting period, starting phase, final period, final phase, and literal datation.

##### getTable_fr(self)

*No description available.*
Generates a list of formatted `Paragraph` objects containing French-language labels and their corresponding structural data fields, intended for use in a PDF table. The method applies a custom `Normal` style derived from `getSampleStyleSheet()`, configured with specific spacing, font size (`7`), alignment (`LEFT`), and font (`Cambria`). The returned list includes ten fields: code (`sigla_struttura`), structure number, category, typology, definition, initial period, initial phase, final period, final phase, and extended dating.

##### getTable_es(self)

Builds and returns a list of formatted `Paragraph` objects representing structural record fields with Spanish-language labels, intended for use in a PDF table. Each paragraph is styled using a `Normal` stylesheet entry configured with `Cambria` font at size 7, left alignment, and 20-unit spacing before and after. The returned list contains ten fields: code (`Código`), structure number (`N° estructura`), category (`Categoría`), typology (`Tipología`), definition (`Definición`), initial period (`Período inicial`), initial phase (`Fase inicial`), final period (`Período final`), final phase (`Fase final`), and extended dating (`Datación extendida`).

##### getTable_ar(self)

Builds and returns a list of formatted `Paragraph` objects representing structure data fields with English-language labels for use in a report table. Each paragraph is styled using the `'Normal'` stylesheet with 7-point Cambria font, left alignment, and fixed spacing, and contains a bold label followed by the corresponding instance attribute value. The returned list includes ten fields: code, structure number, category, typology, definition, starting period, starting phase, final period, final phase, and extended dating.

##### getTable_ca(self)

*No description available.*
Builds and returns a list of `Paragraph` objects representing a structure record with Catalan-language field labels. Each paragraph is formatted using a `Normal` style derived from `getSampleStyleSheet`, configured with a font size of 7, `Cambria` font, left alignment, and 20-unit spacing before and after. The returned list contains ten fields: `Codi`, `N° estructura`, `Categoria`, `Tipologia`, `Definició`, `Període inicial`, `Fase inicial`, `Període final`, `Fase final`, and `Datació estesa`, each rendered with a bold label followed by the corresponding instance attribute value.

##### makeStyles(self)

*No description available.*
Defines and returns a `TableStyle` object configured with a uniform grid and top vertical alignment applied across all cells of a table. The style applies a black grid border with a line width of `0.0` and sets the vertical alignment to `'TOP'` for the entire cell range from `(0, 0)` to `(-1, -1)`.

### single_Struttura_pdf_sheet

*No description available.*
A PDF report sheet generator for a single archaeological structure record, used within the pyArchInit system. The class accepts a 19-element data sequence via its constructor, populating instance attributes that describe the structure's identification, classification, periodization, materials, structural elements, relationships, measurements, and elevation values. It exposes multiple `create_sheet_*` methods — `create_sheet`, `create_sheet_de`, `create_sheet_en`, `create_sheet_fr`, `create_sheet_es`, `create_sheet_ar`, and `create_sheet_ca` — each producing a ReportLab `Table` object rendering the structure data in a localized layout (Italian, German, English, French, Spanish, Arabic, and Catalan respectively).

**Inherits from**: object

#### Methods

##### __init__(self, data)

*No description available.*
Initializes an instance by unpacking a sequential `data` collection into nineteen named instance attributes. The attributes cover structural identification fields (`sito`, `sigla_struttura`, `numero_struttura`), classification fields (`categoria_struttura`, `tipologia_struttura`, `definizione_struttura`), descriptive fields (`descrizione`, `interpretazione`), chronological fields (`periodo_iniziale`, `fase_iniziale`, `periodo_finale`, `fase_finale`, `datazione_estesa`), and physical/relational fields (`materiali_impiegati`, `elementi_strutturali`, `rapporti_struttura`, `misure_struttura`, `quota_min`, `quota_max`). Each attribute is assigned directly by positional index from `data[0]` through `data[18]`.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, e.g., `"31-12-2024"`). The formatted date string is then returned as the method's output.

##### create_sheet(self)

Builds and returns a formatted ReportLab `Table` object representing a structural record sheet ("Scheda Struttura"). The method defines paragraph styles, constructs labeled `Paragraph` elements from the instance's fields (site, structure identifiers, category, typology, description, periodization, materials, structural elements, relationships, measurements, and elevation data), and assembles them into a 13-row, 10-column cell schema. A table style with grid lines, cell spanning, and vertical alignment is applied before the completed `Table` is returned.

##### create_sheet_de(self)

Generates a German-language structural record sheet as a formatted PDF `Table` object. The method constructs a 13-row, 10-column layout containing site identification, structural category, typology, description, interpretation, periodization, materials, structural elements, structural relationships, measurements, and elevation data, with all labels and field headings rendered in German. Paragraph styles, cell spanning rules, and a grid style are applied before the table is returned.

##### create_sheet_en(self)

Builds and returns a ReportLab `Table` object representing an English-language structure form sheet. The method constructs all paragraph cells using `getSampleStyleSheet` styles, populating fields such as site, structure code, category, typology, definition, description, interpretation, periodization, materials, structural elements, relationships, measurements, and elevation data from the instance's attributes. A `table_style` defining grid lines, cell spans, and vertical alignment is applied before the table is returned.

##### create_sheet_fr(self)

French version of Struttura sheet

##### create_sheet_es(self)

Spanish version of Struttura sheet

##### create_sheet_ar(self)

Arabic version of Struttura sheet - uses English labels as Arabic fonts may not be available

##### create_sheet_ca(self)

Catalan version of Struttura sheet

### generate_struttura_pdf

*No description available.*
A PDF generation class for archaeological structure records within the pyarchinit system. It produces two types of output documents — individual structure data sheets and tabular index listings — in multiple languages (Italian, German, English, French, Spanish, Arabic, and Catalan), writing the resulting files to the directory defined by `PDF_path`. Output files are built using ReportLab's `SimpleDocTemplate` with numbered canvas makers, and the output path is derived from the `PYARCHINIT_HOME` environment variable.

**Inherits from**: object

#### Methods

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the `"%d-%m-%Y"` pattern (day-month-year, e.g., `"31-12-2024"`). The formatted date string is then returned to the caller.

##### build_Struttura_sheets(self, records)

*No description available.*
Iterates over a collection of records to generate individual PDF sheets for each entry by instantiating a `single_Struttura_pdf_sheet` object and appending its output along with a `PageBreak` to an elements list. Assembles all elements into a single PDF document named `'Scheda Struttura.pdf'`, written to the path defined by `self.PDF_path`, using `SimpleDocTemplate` and `NumberedCanvas_STRUTTURAsheet` as the canvas maker.

**Parameters:**
- `records` — a sequence of record objects, each passed individually to `single_Struttura_pdf_sheet` for sheet creation.

##### build_index_Struttura(self, records, sito)

*No description available.*
Generates a PDF index document listing all structural records (*Elenco Strutture*) associated with a given excavation site (`sito`). The method resolves the logo image path via a `Connection` object (falling back to a default `logo.jpg` if no custom path is configured), then iterates over `records` to build a formatted table using `Struttura_index_pdf_sheet` instances with predefined column widths `[60, 60, 80, 80, 80, 50, 50, 50, 50, 100]`. The resulting document is written in landscape A3-like format (`29 cm × 21 cm`) to `Elenco Strutture.pdf` within `self.PDF_path`, using `NumberedCanvas_STRUTTURAindex` as the canvas maker.

##### build_Struttura_sheets_de(self, records)

Iterates over a list of records, generating a German-language PDF sheet for each entry by invoking `create_sheet_de()` on a `single_Struttura_pdf_sheet` instance and appending a `PageBreak` after each sheet. All generated elements are assembled into a single PDF document named `Fromular_strukture.pdf`, written to the path defined by `self.PDF_path`. The document is built using `SimpleDocTemplate` with `NumberedCanvas_STRUTTURAsheet` as the canvas maker.

##### build_index_Struttura_de(self, records, sito)

*No description available.*
Generates a German-language PDF index document listing structural records for a given excavation site. The method resolves the logo path via a `Connection` object, constructs a formatted table by iterating over the provided `records` using `Struttura_index_pdf_sheet` and its `getTable_de()` method, and assembles the document with a header paragraph containing the site name (`sito`) and current date. The resulting PDF is written to `liste_struktur.pdf` in the configured PDF output path, rendered in landscape A4 format (`29 cm × 21 cm`) using `NumberedCanvas_STRUTTURAindex`.

##### build_Struttura_sheets_en(self, records)

Builds an English-language PDF document containing individual structure sheets, one per page, from a list of records. For each record, it instantiates a `single_Struttura_pdf_sheet` object, calls its `create_sheet_en()` method to generate the sheet content, and appends a `PageBreak` after each sheet. The resulting document is written to a file named `Structure_form.pdf` in the configured PDF output path, using `NumberedCanvas_STRUTTURAsheet` as the canvas maker.

##### build_Struttura_sheets_fr(self, records)

French version

##### build_Struttura_sheets_es(self, records)

Spanish version

##### build_Struttura_sheets_ar(self, records)

Arabic version

##### build_Struttura_sheets_ca(self, records)

Catalan version

##### build_index_Struttura_en(self, records, sito)

Builds a PDF index document listing structural records in English for a given site. The method retrieves the logo path from the database connection settings, constructs a formatted table of structure entries using `Struttura_index_pdf_sheet` and its `getTable_en()` method, and assembles the document with a header containing the site name and current date. The resulting PDF is written to `structure_list.pdf` in the configured PDF output path, rendered in landscape A4 format (`29 cm × 21 cm`) using `NumberedCanvas_STRUTTURAindex` as the canvas maker.

##### build_index_Struttura_fr(self, records, sito)

French version of structure index

##### build_index_Struttura_es(self, records, sito)

Spanish version of structure index

##### build_index_Struttura_ar(self, records, sito)

Arabic version of structure index - uses English labels

##### build_index_Struttura_ca(self, records, sito)

Catalan version of structure index

