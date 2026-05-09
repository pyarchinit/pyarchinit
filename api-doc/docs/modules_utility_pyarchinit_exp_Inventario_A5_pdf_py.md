# modules/utility/pyarchinit_exp_Inventario_A5_pdf.py

## Overview

This file contains 20 documented elements.

## Classes

### NumberedCanvas_InventarioA5

*No description available.*
A custom ReportLab `canvas.Canvas` subclass that produces paginated PDF output in landscape A5 format. It buffers page states during rendering and, upon saving, retroactively draws page numbering ("Pag. X di Y") at the bottom-right of each page and optional left and right header titles at the top of each page. The `left_title` and `right_title` values are accepted as keyword arguments at construction time and rendered in bold Helvetica at the appropriate header positions for the A5 landscape dimensions.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

Initializes a `NumberedCanvas_InventarioA5` instance by delegating to the parent `canvas.Canvas.__init__` with all positional and keyword arguments. Sets up an empty list `_saved_page_states` to track page state snapshots, and extracts `left_title` and `right_title` string values from `kwargs`, defaulting each to an empty string if not provided.

##### showPage(self)

*No description available.*
Saves the current page state by appending a copy of the instance's `__dict__` to `_saved_page_states`, then calls `_startPage()` to begin a new page. This deferred approach allows the total page count to be determined at save time, enabling features such as "page X of Y" numbering applied during the `save()` call.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Renders the current page number and total page count onto the canvas using an 8-point Helvetica font. The page indicator is drawn as a right-aligned string in the format `"Pag. X di Y"` — where `X` is the current page number (`self._pageNumber`) and `Y` is the value of `page_count` — positioned at coordinates `(21 cm, 0.3 cm)`.

**Parameters:**
- `page_count` — the total number of pages to display in the pagination string.

##### draw_headers(self)

Draws header titles for a landscape A5 format canvas (24×12 cm). If the instance attribute `left_title` is defined and non-empty, it renders the text left-aligned at position `(3 cm, 11.3 cm)` using **Helvetica-Bold** at size 10. If the instance attribute `right_title` is defined and non-empty, it renders the text right-aligned at position `(21 cm, 11.3 cm)` using the same font and size.

### generate_inventario_pdf_a5

*No description available.*
Generates an A5-format PDF inventory document from a collection of records. The class iterates over the provided records, builds individual inventory sheets using `single_Inventario_pdf_sheet_a5`, and assembles them into a single paginated PDF file with page breaks between records. The output file (`scheda_Inventario_A5.pdf`) is written to the `pyarchinit_PDF_folder` directory using a `SimpleDocTemplate` configured for a 24×12 cm page size with a custom canvas that renders left and right title strings in the page headers.

#### Methods

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, zero-padded and hyphen-separated). The resulting string is returned to the caller.

##### build_Inventario_a5(self, records, sito, left_title, right_title)

Builds an A5-format PDF inventory document from a list of records, generating one `single_Inventario_pdf_sheet_a5` sheet per record and inserting a page break between consecutive sheets. The resulting document is rendered on a 24×12 cm page with 3 cm left/right margins and 0.8/0.2 cm top/bottom margins, using a `CustomCanvas` subclass of `NumberedCanvas_InventarioA5` that carries the provided `left_title` and `right_title` values. The output is written to a file named `scheda_Inventario_A5.pdf` located in `self.PDF_path`.

### single_Inventario_pdf_sheet_a5

*No description available.*
Generates a single A5-format PDF sheet for an individual archaeological find (reperto) inventory record. The class accepts a data array containing up to 29 fields — including inventory number, site, find type, area, stratigraphic unit, conservation state, measurements, ceramic attributes, and storage location — along with optional left and right title strings. It provides methods to parse measurements and find elements from their string-encoded list representations, retrieve the first associated thumbnail image from the database, and assemble the complete sheet layout as a ReportLab `KeepTogether` flowable via `create_sheet()`.

#### Methods

##### __init__(self, data, left_title, right_title)

Initializes an instance of `single_Inventario_pdf_sheet_a5` by assigning the provided `data` sequence and optional title strings to instance attributes. The `data` parameter is stored directly as `self.DATA`, and individual fields are extracted by positional index (indices 1 through 28) into named attributes covering inventory record properties such as `sito`, `numero_inventario`, `tipo_reperto`, `descrizione`, `area`, `us`, `misurazioni`, `tecnologie`, and related archaeological find details. The optional `left_title` and `right_title` parameters default to empty strings and are stored as `self.left_title` and `self.right_title` respectively.

##### parse_measurements(self)

Parse measurements from string representation of list

##### parse_elementi(self)

Parse elementi reperto from string representation

##### get_first_image(self)

Recupera la prima immagine associata al reperto

##### create_sheet(self)

Generates a structured PDF sheet for an inventory item using ReportLab, assembling a series of formatted tables, paragraphs, and an image into a single composed layout. The sheet includes a bordered header box displaying the inventory number, date, stratigraphic unit, area, and quota, followed by sections for object definition, measurements, description, decoration notes, material type, and an associated image with caption. All assembled elements are returned wrapped in a `KeepTogether` flowable to prevent page breaks within the sheet.

##### parse_measurements_inline(self)

Parse measurements for inline display

### CustomCanvas

*No description available.*
`CustomCanvas` is a locally defined subclass of `NumberedCanvas_InventarioA5`, instantiated within the scope of a PDF generation routine for an A5 inventory sheet (`scheda_Inventario_A5.pdf`). It extends its parent class by capturing and storing two additional instance attributes, `left_title` and `right_title`, sourced from the enclosing scope via closure. This class is used as the canvas factory for a `SimpleDocTemplate` configured with a 24×12 cm page size and specific margin settings.

**Inherits from**: NumberedCanvas_InventarioA5

#### Methods

##### __init__(self)

Initializes a `CustomCanvas` instance by delegating to the parent `NumberedCanvas_InventarioA5` constructor via `super().__init__(*args, **kwargs)`. After the parent initialization, it assigns the `left_title` and `right_title` values — captured from the enclosing scope — to the corresponding instance attributes `self.left_title` and `self.right_title`.

## Functions

### safe_str(val)

Converts a value to its string representation, returning an empty string for values that are `None`, or whose string form equals `'None'` or `'[]'`. Otherwise, it returns the result of `str(val)`. This function is used internally to ensure safe, display-ready string formatting when building data structures for output.

**Parameters:**
- `val`

