# modules/utility/pyarchinit_exp_USsheet_pdf.py

## Overview

This file contains 78 documented elements.

## Classes

### NumberedCanvas_USsheet

*No description available.*
A subclass of `reportlab.canvas.Canvas` that extends standard PDF canvas functionality to support multi-page documents with automatic page numbering. It accumulates page states during rendering by overriding `showPage()`, then replays them on `save()` to inject a "Pag. X di Y" footer string (rendered in Cambria 5pt, right-aligned at 200 mm × 8 mm) onto each page once the total page count is known. This class is specifically sized and formatted for a vertical US record sheet layout.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

## `__init__` Method

Initializes a `NumberedCanvas_USsheet` instance by delegating to the parent `canvas.Canvas` constructor with all provided positional and keyword arguments. After the parent initialization, it sets up the `_saved_page_states` instance attribute as an empty list.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to the `page_position` method with the provided `pos` argument. This method serves as a named wrapper, allowing callers to define the position of the current page through a semantically explicit interface.

**Parameters:**
- `pos` — The position value passed to `page_position`. Type and accepted values depend on the `page_position` implementation (see implementation).

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current instance state to the `_saved_page_states` list. After preserving the page state, it initializes a new page by calling `_startPage()`.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Renders a page number indicator on the current canvas page using the "Cambria" font at size 5. The string is drawn right-aligned at position (200 mm, 8 mm), formatted as `"Pag. %d di %d"` where the first value is the current page number (`self._pageNumber`) and the second is the total page count (`page_count`).

### NumberedCanvas_USindex

*No description available.*
A custom ReportLab `canvas.Canvas` subclass that defers page rendering in order to support total page count pagination. It accumulates each page's state via an overridden `showPage` method, then on `save` iterates over all saved states to stamp a right-aligned page indicator ("Pag. X di Y") in Cambria 5pt at position 270 mm × 10 mm before finalising the document. This class is intended for US index sheet layouts requiring accurate "page X of Y" footers across the full document.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

Initializes a `NumberedCanvas_USindex` instance by delegating to the parent `canvas.Canvas.__init__` with all positional and keyword arguments passed through. After the parent initialization, it sets up an instance attribute `_saved_page_states` as an empty list.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to the `page_position` method with the provided `pos` argument. This method serves as a named wrapper, offering a semantically descriptive interface for defining the position on the current page.

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current canvas state to the `_saved_page_states` list. After preserving the state, it initializes a new page by calling `_startPage()`. This method is typically called to mark the end of a page before beginning content on the next one.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Renders a right-aligned page number string onto the current canvas page using the "Cambria" font at size 5. The text is drawn at a fixed position of 270 mm from the left and 10 mm from the bottom of the page, formatted as `"Pag. %d di %d"` using the current page number and the total page count supplied via `page_count`.

**Parameters:**
- `page_count` *(int)* — The total number of pages, used to construct the pagination label.

### single_US_pdf_sheet

`single_US_pdf_sheet` is a data container and PDF layout generator for a single stratigraphic unit (US/USM) record, designed to produce structured archaeological recording sheets compliant with the Italian ICCD standard. It is initialized with a flat list of 115 data fields covering site identification, stratigraphic relationships, physical attributes, USM masonry properties, ICCD catalogue fields, and administrative metadata. The class provides methods to unpack serialized field values (stratigraphic relationships, components, documentation references, inclusions) and sheet-rendering methods (`create_sheet_archeo3_usm_fields_2`, `create_sheet_en`, `create_sheet_de`, and language stubs for French, Spanish, Arabic, and Catalan) that build ReportLab `Table` objects formatted for PDF output, branching on the unit type (`US`/`SU`/`SE` for sedimentary units and `USM`/`WSU`/`MSE` for masonry units).

**Inherits from**: object

#### Methods

##### escape_html(text)

Escape HTML characters in text for safe use in Paragraphs.

##### __init__(self, data)

Initializes an instance by unpacking a sequential data list of 115 elements into named instance attributes covering all fields of an archaeological stratigraphic unit (US/USM) record. The attributes span core stratigraphic descriptors (`sito`, `area`, `us`, `descrizione`, `interpretazione`, stratigraphic and interpretive definitions, chronological phases, excavation metadata), masonry unit (USM) fields (construction technique, mortar, materials, dimensions), and additional fields introduced for Archeo 3.0 and ICCD catalogue alignment (catalogue numbers, absolute and relative elevations, spatial references, organic and inorganic components, dating, and responsible personnel). Each attribute is assigned directly by index from the `data` parameter, with no transformation or validation applied.

##### unzip_componenti(self)

*No description available.*
Evaluates the `componenti_organici` and `componenti_inorganici` instance attributes, which are stored as serialized string representations of lists, converting them into plain comma-separated strings. Each list item is processed by stripping the surrounding bracket and quote characters (transforming the `['Stringa']` format into a bare string value), with trailing commas removed from the final result. Returns a tuple of two strings `(organici, inorganici)`, where either value is an empty string if the corresponding attribute is absent or evaluates to an empty list.

##### unzip_rapporti_stratigrafici(self)

Parses and distributes stratigraphic relationship data stored in the instance's `rapporti` attribute into individual relationship fields. The method evaluates `rapporti` as a Python literal to obtain a list of relationship entries, then performs case-insensitive matching of each entry's relationship term against a predefined group map covering ten stratigraphic relationship types (e.g., `copre`, `tagliato_da`, `si_lega_a`). Matched values are assigned to the corresponding instance attribute, appending to any existing value as a comma-separated string.

##### unzip_rapporti_stratigrafici_de(self)

Delegate to unified unzip_rapporti_stratigrafici (handles all languages).

##### unzip_rapporti_stratigrafici_en(self)

Delegate to unified unzip_rapporti_stratigrafici (handles all languages).

##### unzip_documentazione(self)

Parses and unpacks the `documentazione` field into its constituent ICCD documentation category fields (`piante_iccd`, `prospetti_iccd`, `sezioni_iccd`, `foto_iccd`). The field is evaluated as a list of entries, where each entry is a one- or two-element sequence whose first element identifies the ICCD category (`'ICCD-Piante'`, `'ICCD-Prospetti'`, `'ICCD-Sezioni'`, `'ICCD-Foto'`) and whose optional second element provides an associated value. If no value is present or the second element is an empty string, the corresponding instance attribute is set to `'Si'`; otherwise, the value is appended to the attribute, comma-separated if the attribute already holds a non-empty string.

##### unzip_documentazione_en(self)

Parses and distributes the serialized `documentazione` field into the corresponding ICCD documentation category attributes (`piante_iccd`, `prospetti_iccd`, `sezioni_iccd`, `foto_iccd`) using English-language type identifiers (`'Maps'`, `'Elevations'`, `'Sections'`, `'Photo'`). For each entry in the evaluated list, if only a type identifier is present or the secondary value is empty, the corresponding attribute is set to `'Yes'`; otherwise, the secondary value is appended to the attribute as a comma-separated string. If `documentazione` is an empty string, the method performs no operation.

##### unzip_documentazione_de(self)

Parses and unpacks the `documentazione` field (a serialized list of documentation entries in German) into separate ICCD-specific instance attributes: `piante_iccd`, `prospetti_iccd`, `sezioni_iccd`, and `foto_iccd`. Each entry is a one- or two-element sequence whose first element identifies the documentation type (`'Pflanzen'`, `'Prospekte'`, `'Sektionen'`, or `'Foto'`) and whose optional second element provides an associated value. If only the type is present or the second element is empty, the corresponding attribute is set to `'Ja'`; otherwise, the value is appended to the attribute as a comma-separated string.

##### unzip_inclusi(self)

*No description available.*
Processes the `inclusi` field by evaluating its stored string representation into a list of entries and formatting them into an HTML-ready string assigned to `inclusi_print`. Each entry is rendered as a line terminated with a `<br/>` tag: two-element entries are formatted as `"element[0]: element[1]"`, while single-element entries are formatted as `"element[0]"` alone. If `inclusi` is an empty string, the method takes no action.

##### unzip_inclusi_usm(self)

*No description available.*
Processes the `inclusi_usm` field and, if it is not empty, iterates over the evaluated list stored in `inclusi_materiali_usm` to build a formatted HTML string assigned to `inclusi_usm_print`. Each element in the list is rendered as an HTML line break-separated entry: two-element items are formatted as `"key: value<br/>"`, while single-element items are formatted as `"value<br/>"`. If `inclusi_usm` is an empty string, the method takes no action.

##### unzip_inerti_usm(self)

*No description available.*
Evaluates the `aggreg_legante` field as a Python literal to obtain a list of inorganic aggregate-binder entries. If the list contains one or more items, each entry is stripped of its surrounding list notation (removing the leading `['` and trailing `']'`) and concatenated into a comma-separated string. Returns the resulting string, or an empty string if `aggreg_legante` is falsy or the evaluated list is empty.

##### unzip_colore_usm(self)

*No description available.*
Deserializes and formats the `col_legante` field by evaluating its string representation into a list using `eval`. Iterates over the resulting list items, stripping the surrounding bracket and quote characters from each element and concatenating them into a comma-separated string. Returns the formatted string, or an empty string if `col_legante` is absent or the evaluated list is empty.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, e.g., `"31-12-2024"`). The formatted date string is then returned to the caller.

##### create_sheet_archeo3_usm_fields_2(self)

Generates a formatted PDF table representing an archaeological stratigraphic unit record sheet in the Italian ICCD (Istituto Centrale per il Catalogo e la Documentazione) style. The method branches on the value of `self.unita_tipo`, producing a distinct 18-column `Table` layout for `'US'` (stratigraphic unit) records and a separate, extended layout for `'USM'` (stratigraphic masonry unit) records, each populated with fields covering identification, location, documentation references, physical characteristics, stratigraphic relationships, interpretation, dating, and administrative data. Prior to building the table, the method unpacks stratigraphic relationships, documentation references, and USM-specific colour and aggregate data by calling `self.unzip_rapporti_stratigrafici()`, `self.unzip_documentazione()`, `self.unzip_colore_usm()`, and `self.unzip_inerti_usm()`.

##### create_sheet_en(self)

Generates an English-language stratigraphic unit (SU) record sheet as a formatted `Table` object, structured according to ICCD documentation standards. The method branches on the value of `self.unita_tipo`, producing a distinct table layout and field set for `'SU'` (standard stratigraphic unit) and `'WSU'` (wall stratigraphic unit) types, populating fields such as location, stratigraphy, components, materials, dating, and administrative data. It calls `self.unzip_rapporti_stratigrafici_en()` and `self.unzip_documentazione_en()` to prepare relational and documentation data before constructing the table, and returns the resulting `Table` object.

##### create_sheet_de(self)

Generates a German-language stratigraphic unit record sheet formatted as a ReportLab `Table`, branching on the value of `self.unita_tipo` to produce either an `'SE'` (stratigraphic unit) or `'MSE'` (masonry stratigraphic unit) layout. Each branch calls `self.unzip_rapporti_stratigrafici_de()` and `self.unzip_documentazione_de()`, then constructs styled `Paragraph` objects with German field labels and instance attribute values, assembles them into a multi-row `cell_schema`, and applies a corresponding `table_style` with cell spanning and alignment rules. The method returns the resulting `Table` object with fixed `colWidths` and `rowHeights=None`.

##### create_sheet_fr(self)

French version of US sheet - uses English structure for now.
TODO: Add proper French translations for all labels.

##### create_sheet_es(self)

Spanish version of US sheet - uses English structure for now.
TODO: Add proper Spanish translations for all labels.

##### create_sheet_ar(self)

Arabic version of US sheet - uses English structure for now.
TODO: Add proper Arabic translations for all labels.

##### create_sheet_ca(self)

Catalan version of US sheet - uses English structure for now.
TODO: Add proper Catalan translations for all labels.

### US_index_pdf_sheet

*No description available.*
A data container and PDF sheet generator for a single Stratigraphic Unit (US/SU) record, used to produce index sheet content for PDF reports. It accepts raw record data via its constructor, parses and distributes stratigraphic relationship data (such as covers, cuts, fills, abuts, and equivalence relations) into discrete instance attributes through `unzip_rapporti_stratigrafici`, and exposes table-building methods (`getTable`, `getTable_en`, `getTable_de`) that return lists of ReportLab `Paragraph` objects with field labels rendered in Italian, English, or German respectively. A `makeStyles` method returns a `TableStyle` defining grid and vertical alignment for use when rendering the data in a ReportLab table.

**Inherits from**: object

#### Methods

##### __init__(self, data)

Initializes an instance by extracting and assigning five attributes from a positional data sequence. Specifically, it maps `data[0]` through `data[3]` to `sito`, `area`, `us`, and `d_stratigrafica` respectively, and assigns `data[17]` to `rapporti`.

##### unzip_rapporti_stratigrafici(self)

*No description available.*
Parses and distributes the stratigraphic relationship data stored in `self.rapporti` into individual instance attributes corresponding to each relationship type (e.g., `copre`, `coperto_da`, `taglia`, `tagliato_da`). The method evaluates `self.rapporti` as a Python literal to obtain a list of `[term, value]` pairs, then performs a case-insensitive lookup against a predefined map of internationalised relationship group terms to determine the target attribute for each entry. Multiple values mapped to the same attribute are appended as a comma-separated string to the existing attribute value.

##### getTable(self)

*No description available.*
Builds and returns a flat list of formatted `Paragraph` objects representing the stratigraphic unit's key fields, intended for use in report generation. It first configures a `Normal` paragraph style (font, size, spacing, and alignment) using `getSampleStyleSheet`, then calls `self.unzip_rapporti_stratigrafici()` before constructing labelled paragraphs for thirteen fields: `area`, `us`, `d_stratigrafica`, `copre`, `coperto_da`, `taglia`, `tagliato_da`, `riempie`, `riempito_da`, `si_appoggia_a`, `gli_si_appoggia`, `uguale_a`, and `si_lega_a`. Each paragraph renders its field label in bold followed by the corresponding instance attribute value, and the complete list is returned as `data`.

##### unzip_rapporti_stratigrafici_en(self)

Delegate to unified unzip_rapporti_stratigrafici (handles all languages).

##### getTable_en(self)

Builds and returns a list of `Paragraph` objects representing stratigraphic relationship data formatted for an English-language report. Each paragraph is styled using a `Normal` stylesheet entry configured with specific font, size, and spacing settings, and displays a bold English label followed by the corresponding instance attribute value. The method first calls `unzip_rapporti_stratigrafici_en` to prepare the stratigraphic relationship data before constructing the list.

##### unzip_rapporti_stratigrafici_de(self)

Delegate to unified unzip_rapporti_stratigrafici (handles all languages).

##### getTable_de(self)

Builds and returns a list of German-language `Paragraph` objects representing stratigraphic relationship fields for a report table, using a `Normal` style configured with Cambria font at size 7 with left alignment. Before constructing the paragraphs, it calls `unzip_rapporti_stratigrafici_de()` to prepare the stratigraphic relationship data. Each paragraph combines a bold German label (e.g., `"Bereich"`, `"SE"`, `"Stratigrafische Definitie"`) with the corresponding instance attribute value, covering fields such as area, stratigraphic unit, and all defined stratigraphic relationships.

##### makeStyles(self)

Creates and returns a `TableStyle` object configured with two style directives: a `GRID` rule applying a black border of width `0.0` across all cells, and a `VALIGN` rule setting vertical alignment to `'TOP'` for all cells. Both rules span the entire table range from `(0, 0)` to `(-1, -1)`. The resulting `TableStyle` instance is returned for use in styling a table.

### FOTO_index_pdf_sheet

*No description available.*
A data container and PDF table-row builder for photographic index sheets. Initialized with a data sequence, it stores site, photo, thumbnail, stratigraphic unit, area, stratigraphic description, and unit type fields extracted by positional index. Provides three locale-specific methods — `getTable()` (Italian), `getTable_en()` (English), and `getTable_de()` (German) — each returning a list of formatted `Paragraph` and scaled `Image` elements representing a single photo record row, along with a `makeStyles()` method that returns a `TableStyle` defining grid lines and top vertical alignment for the rendered table.

**Inherits from**: object

#### Methods

##### __init__(self, data)

*No description available.*
Initializes a `FOTO_index_pdf_sheet` instance by unpacking a sequential data structure into named instance attributes. The `data` parameter is expected to be an indexable sequence, where positions `0`, `1`, `2`, `3`, `4`, `5`, and `6` are assigned to `sito`, `area`, `us`, `unita_tipo`, `d_stratigrafica`, `foto`, and `thumbnail` respectively.

##### getTable(self)

*No description available.*
Builds and returns a list of formatted data elements intended for use in a report table. The method configures a normal paragraph style (font: Cambria, size 7, left-aligned) and constructs `Paragraph` objects for the area, US or USM unit identifier (label determined by `self.unita_tipo`), photo ID, and stratigraphic description, alongside a thumbnail `Image` scaled to a width of 1 inch with centered horizontal alignment. The returned list contains these elements in the order: `foto`, `thumbnail`, `us`, `area`, `d_stratigrafica`.

##### getTable_en(self)

*No description available.*
Builds and returns a list of styled data elements for use in an English-language report table. The method configures a `Normal` paragraph style (Cambria, 7pt, left-aligned) and constructs labeled `Paragraph` objects for the photo ID, stratigraphic unit or wall stratigraphic unit (determined by `self.unita_tipo`), area, stratigraphic description, and a scaled thumbnail `Image` (1 inch wide, centre-aligned) loaded from `self.thumbnail`. The resulting list is ordered as: `foto`, `thumbnail`, `us`, `area`, `d_stratigrafica`.

##### getTable_de(self)

*No description available.*
Builds and returns a list of formatted report elements for a German-language stratigraphic unit table. The method configures a `Normal` paragraph style using `Cambria` font at 7pt with left alignment, then constructs labeled `Paragraph` objects for photo ID, unit type (SE or MSE), area, and stratigraphic description fields, with labels rendered in German (e.g., `"Beschreibung"`, `"SE-MSE in Liste"`). A thumbnail image is also loaded, scaled to a 1-inch width while preserving aspect ratio, and included in the returned data list alongside the paragraph elements.

##### makeStyles(self)

*No description available.*
Constructs and returns a `TableStyle` object configured with two style directives applied across the entire table (from cell `(0, 0)` to `(-1, -1)`): a black grid border with a line width of `0.0`, and top vertical alignment for all cells. The method takes no parameters beyond `self` and returns the fully constructed `TableStyle` instance.

### FOTO_index_pdf_sheet_2

*No description available.*
A ReportLab-based PDF sheet class that represents a single photographic index record for an archaeological excavation report. It is initialized with a data sequence providing site, photo ID, stratigraphic unit, area, stratigraphic description, and unit type fields, and exposes localized `getTable` methods (`getTable`, `getTable_en`, `getTable_de`, `getTable_fr`, `getTable_es`, `getTable_ar`, `getTable_ca`) that each return a list of styled `Paragraph` objects containing photo ID, stratigraphic unit (labeled according to unit type and language), area, and stratigraphic description. The `makeStyles` method returns a `TableStyle` applying a full grid border and top vertical alignment across all cells.

**Inherits from**: object

#### Methods

##### __init__(self, data)

Initializes an instance of `FOTO_index_pdf_sheet_2` by extracting and assigning field values from the provided `data` sequence. The following instance attributes are set: `sito` from `data[0]`, `area` from `data[1]`, `us` from `data[2]`, `unita_tipo` from `data[3]`, `d_stratigrafica` from `data[4]`, and `foto` from `data[5]`. The element at index 6 (`thumbnail`) is present in the source but commented out and therefore not assigned.

##### getTable(self)

*No description available.*
Builds and returns a list of `Paragraph` objects representing a formatted data row for use in a report table. The method applies a custom `Normal` style (Cambria, 7pt, left-aligned) to each field, then constructs labelled paragraphs for the photo ID, unit identifier (labelled `US` or `USM` depending on `self.unita_tipo`), area, and stratigraphic description. The resulting list is returned in the order: `foto`, `us`, `area`, `d_stratigrafica`.

##### getTable_en(self)

*No description available.*
Generates and returns a list of formatted `Paragraph` objects representing a table row in English for a photographic record entry. It applies a predefined `Normal` stylesheet with specific spacing and font settings, then constructs labeled fields for photo ID, stratigraphic unit (rendered as either `SU` or `WSU` depending on `self.unita_tipo`), area, and stratigraphic description. The method also establishes a database connection to retrieve a thumbnail path, though the thumbnail element is commented out and not included in the returned data list.

##### getTable_de(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` objects representing a stratigraphic unit record with German-language labels. The method applies a consistent `Normal` style (left-aligned, 7pt font, with defined spacing) to each field, and conditionally labels the unit identifier as either `"SE"` or `"MSE"` based on the value of `self.unita_tipo`. The returned list contains the photo ID, unit identifier, area, and stratigraphic description (`"Beschreibung"`) fields, intended for use in table or report generation.

##### getTable_fr(self)

Builds and returns a list of formatted `Paragraph` objects for a French-language table row, applying a predefined `Normal` style with specific spacing, alignment, and font size settings. The method retrieves a thumbnail path via a `Connection` instance, then constructs labelled paragraph cells for photo ID, stratigraphic unit (labelled "US" or "USM" depending on `self.unita_tipo`), zone, and stratigraphic description using French and mixed-language labels. The resulting list `[foto, us, area, d_stratigrafica]` is returned for use in report table generation.

##### getTable_es(self)

*No description available.*
Generates and returns a list of styled `Paragraph` objects containing Spanish-language photo record data for use in a table. The method applies a `Normal` stylesheet with left alignment and a font size of 7, then constructs labelled paragraphs for the photo ID (`ID Foto`), unit type (`UE` or `UEM`), area (`Área`), and stratigraphic description (`Descripción`). The returned list `[foto, us, area, d_stratigrafica]` represents a single row of formatted table data.

##### getTable_ar(self)

*No description available.*
Builds and returns a list of `Paragraph` objects formatted for Arabic-language report output using ReportLab's `getSampleStyleSheet`. The method applies a uniform `Normal` style with left alignment, 7-point font size, and defined spacing, then constructs labelled Arabic-text paragraphs for the photo number (`foto`), stratigraphic unit (`us`), area (`area`), and stratigraphic description (`d_stratigrafica`). The stratigraphic unit label differs based on the value of `self.unita_tipo`, rendering either `'وحدة طبقية'` or `'وحدة طبقية جدارية'` accordingly.

##### getTable_ca(self)

*No description available.*
Builds and returns a list of styled `Paragraph` objects intended for use as table cell data, using Catalan-language labels. The method configures a `Normal` paragraph style with specific spacing and font size settings, retrieves a thumbnail path via a `Connection` instance, and constructs four paragraph elements representing photo ID (`ID Foto`), stratigraphic unit (`UE` or `UEM`, depending on `self.unita_tipo`), area (`Àrea`), and stratigraphic description (`Descripció`). The returned list contains these four `Paragraph` objects in the order `[foto, us, area, d_stratigrafica]`.

##### makeStyles(self)

*No description available.*
Defines and returns a `TableStyle` object configured with two style directives applied across the entire table (from cell `(0, 0)` to `(-1, -1)`): a black grid border with a line width of `0.0`, and top vertical alignment for all cells. The method takes no parameters beyond `self` and returns the constructed `TableStyle` instance directly.

### generate_US_pdf

*No description available.*
A PDF generation class for producing stratigraphic unit (US/SU) documentation within the pyarchinit archaeological information system. It provides methods to build individual US record sheets in multiple languages (Italian, English, German, French, Spanish, Arabic, and Catalan) via language-specific `build_US_sheets_*` methods, as well as tabular index listings for stratigraphic units and photographs via corresponding `build_index_US_*` and `build_index_Foto_*` methods. Output PDF files are written to the directory defined by `PDF_path`, which is derived from the `PYARCHINIT_HOME` environment variable.

**Inherits from**: object

#### Methods

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the `"%d-%m-%Y"` pattern (day-month-year). The formatted date string is then returned to the caller.

##### build_US_sheets(self, records)

Generates a PDF document containing one or more US (Unità Stratigrafica) record sheets in ICCD ministerial format. For each record provided, the method constructs a single sheet using `single_US_pdf_sheet`, prepending a logo image and a spacer, and appending a page break between sheets. The resulting PDF is written to a file named `'Scheda USICCD.pdf'` within the configured PDF output path, using `SimpleDocTemplate` with A4-like page dimensions and `NumberedCanvas_USsheet` for page numbering.

##### build_US_sheets_en(self, records)

Generates English-language PDF report sheets for Stratigraphic Unit (SU) records by iterating over the provided `records` list and building individual sheet elements using `single_US_pdf_sheet`. Each sheet is assembled with a logo image, a spacer, the generated English sheet content, and a page break; a `QMessageBox` warning is issued and iteration halts if a `TypeError` is encountered for a record. The resulting elements are written to a timestamped PDF file named `Form SU` in `self.PDF_path`, rendered on A4-sized pages using `SimpleDocTemplate` and `NumberedCanvas_USsheet`.

##### build_US_sheets_de(self, records)

Generates a German-language PDF report (`Form SE`) containing one sheet per stratigraphic unit (US) record by iterating over the provided `records` list and composing each page with a logo, spacer, and a German-format US sheet created via `single_US_pdf_sheet.create_sheet_de()`.

The output file is written to `self.PDF_path` with a timestamped filename and built as an A4-sized document (21 × 29 cm) using `SimpleDocTemplate` with `NumberedCanvas_USsheet` as the canvas maker. If a `TypeError` is encountered while processing a record, a warning dialog is displayed and iteration stops.

##### build_US_sheets_fr(self, records)

Builds a French-language PDF report of US (Unità Stratigrafica) sheets from a list of records. For each record, it instantiates a `single_US_pdf_sheet` object, calls its `create_sheet_fr()` method, and assembles the resulting elements alongside a logo image and page breaks into a `SimpleDocTemplate` document sized at A4 (21 × 29 cm). The output file is written to `self.PDF_path` with a timestamped filename prefixed by `'Fiche_US'`; if a `TypeError` is encountered for any record, a warning dialog is displayed and generation stops.

##### build_US_sheets_es(self, records)

*No description available.*
Generates a Spanish-language PDF report of US (Unità Stratigrafica) sheets from a list of records. For each record, it instantiates a `single_US_pdf_sheet` object, calls `create_sheet_es()` to produce the Spanish sheet content, and assembles the elements — including a logo, spacer, sheet content, and page break — into a `SimpleDocTemplate` document sized at A4 (21 × 29 cm). The resulting PDF is written to `self.PDF_path` with a timestamped filename prefixed by `Ficha_UE`; if a `TypeError` is encountered for any record, a warning dialog is displayed and the build loop terminates.

##### build_US_sheets_ar(self, records)

Builds an Arabic-language PDF report of US (Unità Stratigrafica) sheets from a list of records. For each record, it instantiates a `single_US_pdf_sheet` object, calls `create_sheet_ar()` to generate the Arabic sheet content, and assembles the elements — including a logo image, spacer, sheet content, and page break — into a list. The resulting elements are rendered into a timestamped PDF file named with the prefix `Bitaqa_US`, saved to `self.PDF_path`, using `SimpleDocTemplate` with A4-like dimensions and `NumberedCanvas_USsheet` as the canvas maker; a warning dialog is displayed if a `TypeError` is encountered for any record.

##### build_US_sheets_ca(self, records)

Builds a PDF document containing Catalan-language US (Unità Stratigrafica) sheets for a given list of records. For each record, it instantiates a `single_US_pdf_sheet` object, calls `create_sheet_ca()` to generate the sheet content, and appends the logo, a spacer, the sheet, and a page break to the elements list; if a `TypeError` is encountered for any record, a warning dialog is displayed and the loop terminates. The resulting elements are written to a timestamped PDF file named `Fitxa_UE_<timestamp>.pdf` in `self.PDF_path`, using `SimpleDocTemplate` with A4-like dimensions and `NumberedCanvas_USsheet` as the canvas maker.

##### build_index_US(self, records, sito)

Generates a PDF index document listing stratigraphic units (Unità Stratigrafiche) for a given excavation site. It retrieves the logo path via a `Connection` object, constructs a formatted table from the provided `records` using `US_index_pdf_sheet`, and assembles the document with a site heading, logo, and styled table using ReportLab's `SimpleDocTemplate` on A3 page size. The resulting PDF is written to `self.PDF_path` under the filename `'Elenco US.pdf'` using `NumberedCanvas_USindex` as the canvas maker.

##### build_index_Foto(self, records, sito)

Generates a PDF index document listing stratigraphic photographs for a given excavation site. It resolves the logo path via the `Connection` class, constructs a formatted table from the provided `records` using `FOTO_index_pdf_sheet`, and assembles the document with a heading, logo, and data table using ReportLab's `SimpleDocTemplate`. The resulting PDF is written to `self.PDF_path` under the filename `'Elenco Foto.pdf'`.

##### build_index_Foto_2(self, records, sito)

Generates a PDF index document listing stratigraphic photos ("ELENCO FOTO STRATIGRAFICHE") for a given excavation site (`sito`). The method resolves the logo path via a `Connection` object, builds a formatted table from the provided `records` using `FOTO_index_pdf_sheet_2`, and assembles the document with a logo, heading, and data table. The resulting PDF is written to a file named `'Elenco Foto.pdf'` in `self.PDF_path`, rendered on A4 pages using `NumberedCanvas_USsheet`.

##### build_index_US_de(self, records, sito)

*No description available.*
Generates a German-language PDF index document listing stratigraphic units (Stratigraphische Einheiten) for a given excavation site. The method retrieves the application's logo, constructs a formatted A3-sized table using records processed through `US_index_pdf_sheet`, and assembles the document with a heading that includes the site name and current date. The resulting PDF file is written to `self.PDF_path` with a timestamped filename prefixed by `'LISTE SE'`, rendered using `NumberedCanvas_USindex`.

##### build_index_Foto_de(self, records, sito)

Generates a German-language PDF index document listing stratigraphic photos for a given excavation site. The method resolves the logo path via a `Connection` object, constructs a formatted table from the provided `records` using `FOTO_index_pdf_sheet` and its `getTable_de()` method, and assembles the document with a heading that includes the site name (`sito`) and current date. The resulting PDF file is written to `self.PDF_path` with a timestamped filename using `SimpleDocTemplate` and `NumberedCanvas_USsheet`.

##### build_index_Foto_2_de(self, records, sito)

Generates a German-language PDF index document listing stratigraphic photos for a given excavation site. The method retrieves the logo path via a `Connection` object, builds a formatted table from the provided `records` using `FOTO_index_pdf_sheet_2` and its `getTable_de()` method, and assembles the document with a heading containing the site name (`sito`) and current date. The resulting PDF file is written to `self.PDF_path` with a timestamped filename and rendered on A4 paper using `NumberedCanvas_USsheet`.

##### build_index_US_en(self, records, sito)

Generates a PDF index document of Stratigraphic Units (SU) in English for a given site, using the provided records and site name. It constructs the document with a logo, a heading displaying the site name and current date, and a formatted table built from `US_index_pdf_sheet` entries with predefined column widths. The resulting PDF is saved to `self.PDF_path` with a timestamped filename and rendered on A3 page size using `NumberedCanvas_USindex`.

##### build_index_Foto_en(self, records, sito)

Generates a PDF index document listing stratigraphic photos in English for a given site. It resolves the logo path via the `Connection` class, constructs a formatted table from the provided `records` using `FOTO_index_pdf_sheet` and `getTable_en()`, and assembles the document with a header containing the site name and current date. The resulting PDF is written to `self.PDF_path` with a timestamped filename using `SimpleDocTemplate` and `NumberedCanvas_USsheet`.

##### build_index_Foto_2_en(self, records, sito)

*No description available.*
Generates an English-language PDF index document listing stratigraphic photos for a given site. The method resolves the logo path via `Connection`, constructs a formatted A4 document containing a header with the site name and current date, and builds a table of photo records using `FOTO_index_pdf_sheet_2` with column widths `[100, 50, 50, 200]`. The resulting PDF is written to `self.PDF_path` with a timestamped filename and rendered using `NumberedCanvas_USsheet`.

