# modules/utility/pyarchinit_exp_POTTERYsheet_pdf.py

## Overview

This file contains 49 documented elements.

## Classes

### NumberedCanvas_USsheet

*No description available.*
A subclass of `canvas.Canvas` that extends ReportLab's canvas with automatic page numbering support for US sheet documents. It accumulates page states during rendering by overriding `showPage`, then on `save` iterates through all saved states to draw a "Page X of Y" footer string at position `(200mm, 20mm)` in 8pt Helvetica before finalising the document. This design ensures the total page count is known before any page number labels are rendered.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

## `__init__` Method

Initializes a `NumberedCanvas_USsheet` instance by delegating to the parent `canvas.Canvas.__init__` method, passing through all positional and keyword arguments unchanged. Following the parent initialization, it sets up an instance-level attribute `_saved_page_states` as an empty list, which is used by `showPage` to accumulate page state snapshots.

##### define_position(self, pos)

*No description available.*
Accepts a position value `pos` and delegates directly to `self.page_position(pos)`. This method serves as a thin wrapper, forwarding the provided argument to the underlying `page_position` call without additional processing or transformation.

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current canvas state dictionary to the `_saved_page_states` list. After preserving the state, it calls `_startPage()` to initialize a new blank page for subsequent drawing operations. This deferred saving mechanism allows the total page count to be determined later, enabling features such as "page X of Y" numbering during the final `save()` call.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Sets the font to Helvetica at size 8, then draws a right-aligned string at the position `(200mm, 20mm)` on the canvas. The string is formatted as `"Page %d of %d"`, displaying the current page number (`self._pageNumber`) alongside the total page count (`page_count`).

### NumberedCanvas_USindex

*No description available.*
A custom ReportLab `canvas.Canvas` subclass that adds automatic "Page X of Y" pagination to generated PDF documents. It accumulates page states in `_saved_page_states` during rendering, then on `save()` iterates over all stored states to inject the total page count before finalising the document. Page numbers are rendered in Helvetica 8pt, right-aligned at position `(270mm, 10mm)` on each page.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

## `__init__` Method

Initializes a `NumberedCanvas_USindex` instance by delegating to the parent `canvas.Canvas` constructor with all provided positional and keyword arguments. After the parent initialization, it sets up an instance variable `_saved_page_states` as an empty list, which is used to track the state of each page as the document is built.

##### define_position(self, pos)

*No description available.*
Sets the page position for the canvas by delegating directly to the `page_position` method with the provided `pos` argument. This method serves as a thin wrapper, passing `pos` unchanged to the underlying `page_position` call. The behavior and accepted values of `pos` depend on the implementation of `page_position` (see implementation).

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current canvas state dictionary to the `_saved_page_states` list. After preserving the state, it calls `_startPage()` to initialize a new blank page for subsequent drawing operations. This deferred state-saving mechanism allows the `save()` method to later iterate over all recorded page states and apply page-level information (such as total page count) retroactively.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Sets the font to Helvetica at size 8, then renders a right-aligned page indicator string in the format `"Page {current} of {total}"` at the fixed position `(270mm, 10mm)` on the canvas. The current page number is read from `self._pageNumber` and the total page count is supplied via the `page_count` parameter.

### single_pottery_pdf_sheet

*No description available.*
A data container and PDF sheet generator for a single underwater archaeological pottery artefact record. The class is initialized with a positional data sequence of 36 fields covering identification (`divelog_id`, `artefact_id`), provenance (`sito`, `area`, `provenience`), typological attributes (`fabric`, `specific_shape`, `specific_part`, `category`, `typology`), physical measurements (`diametro_max`, `diametro_rim`, `diametro_bottom`, `total_height`, `preserved_height`, `base_height`, `thickmin`, `thickmax`), conservation and documentation metadata (`treatment`, `state`, `samples`, `photographed`, `drawing`, `wheel_made`), and chronological data (`period`, `data_`, `anno`). It exposes locale-specific sheet-generation methods — `create_sheet` / `create_sheet_en` (English), `create_sheet_it` (Italian), `create_sheet_de` (German), `create_sheet_fr` (French), `create_sheet_es` (Spanish), `create_sheet_ar` (Arabic), and `create_sheet_ca` (Catalan) — each returning a ReportLab `Table` object representing a formatted 18-column pottery recording form with project logos and a gridded layout, as well as a `makeStyles` method returning a base `TableStyle`.

#### Methods

##### __init__(self, data)

*No description available.*
Initializes a `single_pottery_pdf_sheet` instance by unpacking a sequential data structure into named instance attributes representing the fields of a pottery artefact record. The `data` parameter is expected to be an indexable sequence of 36 elements (indices `0` through `35`), each mapped to a specific attribute such as `divelog_id`, `artefact_id`, `sito`, `fabric`, physical measurements, descriptive metadata, and recording status fields. No validation or transformation is applied to the input values during initialization.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year). The formatted date string is returned to the caller.

##### create_sheet(self)

Builds and returns a formatted ReportLab `Table` object representing an Archaeological Underwater Survey pottery form sheet. The method defines multiple paragraph styles (for logo, header, normal text, and justified description), loads two logo images from the `pyarchinit_DB_folder` directory, and constructs labelled `Paragraph` cells for all pottery record fields (identifiers, physical measurements, material attributes, conservation data, and dates). The resulting table is configured with a fixed 18-column layout, explicit column widths, cell spanning rules, and a full grid border style.

##### makeStyles(self)

*No description available.*
Creates and returns a `TableStyle` object defining the visual formatting rules for a table. The style applies a black grid border (with line weight `0.0`) across all cells from the top-left `(0, 0)` to the bottom-right `(-1, -1)`, and sets the vertical alignment of all cell content to `'TOP'`.

##### create_sheet_it(self)

Italian version of Pottery sheet

##### create_sheet_de(self)

German version of Pottery sheet

##### create_sheet_en(self)

English version of Pottery sheet - same as create_sheet

##### create_sheet_fr(self)

French version of Pottery sheet

##### create_sheet_es(self)

Spanish version of Pottery sheet

##### create_sheet_ar(self)

Arabic version of Pottery sheet

##### create_sheet_ca(self)

Catalan version of Pottery sheet

### FOTO_index_pdf_sheet_2

PDF sheet for pottery list WITH thumbnail

**Inherits from**: object

#### Methods

##### __init__(self, data)

*No description available.*
Initializes a `FOTO_index_pdf_sheet_2` instance from a positional data sequence, mapping indexed elements to the instance attributes `sito`, `id_number`, `area`, `us`, `sector`, `anno`, `description`, `foto`, `thumbnail`, `photo`, and `drawing`. The attributes `photo` and `drawing` are conditionally assigned from `data[9]` and `data[10]` respectively, defaulting to an empty string if the sequence does not contain those indices.

##### getTable(self)

*No description available.*
Builds and returns a list of formatted `Paragraph` and `Image` objects representing a single pottery record's fields, intended for use as a row of data within a ReportLab PDF table. Each field — including Pottery ID, Area, SU, Sector, Year, Note, Photo ID, Photo, Drawing, and thumbnail image — is styled using a `getSampleStyleSheet`-derived normal style, with photo and drawing fields using a word-wrap style (`styWrap`) and semicolon-separated values converted to line breaks. The thumbnail image is retrieved from the instance's `thumbnail` attribute, scaled to 0.8 inches in width with proportional height, and center-aligned.

##### makeStyles(self)

*No description available.*
Constructs and returns a `TableStyle` object defining the visual formatting rules for a table. The style applies a black grid border across all cells (from `(0, 0)` to `(-1, -1)`) with a line thickness of `0.0`, and sets the vertical alignment of all cell content to `'TOP'`.

### FOTO_index_pdf_sheet

PDF sheet for pottery list WITHOUT thumbnail

**Inherits from**: object

#### Methods

##### __init__(self, data)

*No description available.*
Initializes a `FOTO_index_pdf_sheet` instance, which represents a PDF sheet for a pottery list without a thumbnail. Assigns instance attributes by unpacking values from the `data` sequence at fixed indices, mapping positional elements to `sito`, `id_number`, `area`, `us`, `sector`, `anno`, `description`, `foto`, `photo`, and `drawing`. The `photo` and `drawing` attributes are conditionally assigned only if `data` contains more than 9 or 10 elements respectively, defaulting to an empty string otherwise.

##### getTable(self)

*No description available.*
Builds and returns a list of `Paragraph` objects representing the fields of a pottery record, formatted for use in a ReportLab table. Each paragraph is styled using a `Normal` stylesheet with defined spacing, font size, and left alignment; photo and drawing fields use a separate word-wrap style (`styWrap`) and have their semicolon-delimited values replaced with line breaks. The method also establishes a database connection to retrieve the thumbnail path, and the returned list contains the following fields in order: Pottery ID, Area, SU, Sector, Year, Note, Photo ID, Photo, and Drawing.

##### makeStyles(self)

*No description available.*
Constructs and returns a `TableStyle` object defining the visual formatting rules for a table. The style applies a black grid border across all cells (from `(0, 0)` to `(-1, -1)`) with a line thickness of `0.0`, and sets the vertical alignment of all cell content to `'TOP'`.

### POTTERY_index_pdf

*No description available.*
A data container and PDF formatting class for pottery artefact index entries. It is initialized with a data sequence from which it extracts three fields — `divelog_id`, `artefact_id`, and `anno` — and provides a `getTable` method that constructs a list of styled `Paragraph` objects representing "Pottery ID", "Note", and "Year" for use in a ReportLab PDF table. The `makeStyles` method returns a `TableStyle` applying a black grid border and top vertical alignment across all cells.

#### Methods

##### __init__(self, data)

*No description available.*
Initializes a `POTTERY_index_pdf` instance by unpacking a sequential data structure into three instance attributes. Assigns `data[0]` to `self.divelog_id`, `data[1]` to `self.artefact_id`, and `data[2]` to `self.anno`.

**Parameters:**
- `data` — An indexable sequence whose first three elements correspond to the dive log identifier, artefact identifier, and year/annotation value respectively.

##### getTable(self)

*No description available.*
Builds and returns a list of `Paragraph` objects representing the fields of a pottery record, formatted for use in a PDF report. Each paragraph is styled using a `Normal` stylesheet entry with predefined font size, spacing, and left alignment, and displays a bold label followed by the corresponding instance value (`id_number`, `note`, and `anno`). The returned list `data1` contains three elements intended to populate a single row of a ReportLab table.

##### makeStyles(self)

*No description available.*
Creates and returns a `TableStyle` object configured with two style directives: a black grid border applied to all cells (`'GRID'` from position `(0,0)` to `(-1,-1)` with a line width of `0.0`), and top vertical alignment (`'VALIGN'`) applied uniformly across all cells. The method takes no parameters beyond `self` and returns the constructed `TableStyle` instance directly.

### generate_POTTERY_pdf

*No description available.*
Generates PDF documents for pottery records within the pyarchinit system, writing output files to the directory specified by `PDF_path`, which is derived from the `PYARCHINIT_HOME` environment variable. The class provides locale-specific sheet-building methods (`build_POTTERY_sheets`, `build_POTTERY_sheets_it`, `build_POTTERY_sheets_de`, `build_POTTERY_sheets_en`, `build_POTTERY_sheets_fr`, `build_POTTERY_sheets_es`, `build_POTTERY_sheets_ar`, `build_POTTERY_sheets_ca`) that iterate over a list of records, render each as a page-broken A4 sheet via `single_pottery_pdf_sheet`, and write the result to a language-specific PDF filename. Additional methods (`build_index_POTTERY`, `build_index_Foto`, `build_index_Foto_2`) produce tabular index PDFs that include a logo, a dated heading, and formatted summary tables for pottery records and associated photographs.

#### Methods

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it as a `DD-MM-YYYY` string via `strftime`. The formatted date string is then returned as the method's output.

##### build_POTTERY_sheets(self, records)

Iterates over a list of records and generates an individual PDF sheet for each entry using `single_pottery_pdf_sheet`, appending a `PageBreak` between sheets. Assembles all elements into a single PDF document named `Pottery.pdf`, written to the path specified by `self.PDF_path`. The document is built using `SimpleDocTemplate` with A4 page size and `NumberedCanvas_USsheet` as the canvas maker.

##### build_POTTERY_sheets_it(self, records)

Italian version

##### build_POTTERY_sheets_de(self, records)

German version

##### build_POTTERY_sheets_en(self, records)

English version

##### build_POTTERY_sheets_fr(self, records)

French version

##### build_POTTERY_sheets_es(self, records)

Spanish version

##### build_POTTERY_sheets_ar(self, records)

Arabic version

##### build_POTTERY_sheets_ca(self, records)

Catalan version

##### build_index_POTTERY(self, records, divelog_id)

Generates a PDF index document for pottery records and saves it as `Pottery_list.pdf` in the configured PDF output folder. It constructs the document by loading a logo image from the database folder, appending a header paragraph with the current date, and building a formatted table from the provided `records` using `POTTERY_index_pdf` instances with predefined column widths. The resulting PDF is rendered in landscape A4 format (`29cm × 21cm`) using `NumberedCanvas_USindex` as the canvas maker.

##### build_index_Foto_2(self, records, sito)

Generates a PDF index document listing photo records associated with pottery finds for a given site. The method builds a formatted A4 PDF containing a logo, a titled header with the site name and current date, and a styled table constructed from the provided `records` using `FOTO_index_pdf_sheet_2`, with ten columns including id number, area, US, sector, year, description, and thumbnail fields. The output file is saved to `self.PDF_path` with a timestamped filename in the format `'List photo thumbnail pottery_<day>_<month>_<year>_<hour>_<minute>_<second>.pdf'`.

##### build_index_Foto(self, records, sito)

*No description available.*
Generates a PDF index document listing photo pottery records for a given archaeological site. The method assembles a styled A4 document containing a logo, a header with the site name and current date, and a formatted table built from the provided `records` using `FOTO_index_pdf_sheet` instances with nine columns (`id_number`, `area`, `us`, `sector`, `anno`, `description`, `foto`, `photo`, `drawing`). The output file is written to `self.PDF_path` with a timestamped filename and rendered using `NumberedCanvas_USsheet`.

