# modules/utility/pyarchinit_exp_Faunasheet_pdf.py

## Overview

This file contains 32 documented elements.

## Classes

### NumberedCanvas_Faunasheet

*No description available.*
A subclass of `canvas.Canvas` that extends PDF canvas functionality with multi-page awareness and automatic page numbering. It accumulates page states during document generation via `showPage`, then on `save` iterates over all saved states to render a "Pag. X di Y" label (in 6pt Cambria font, right-aligned at 200mm × 20mm) on each page before finalising the document. A `define_position` method is also provided to delegate positioning to `page_position`.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

*No description available.*
Initializes a `NumberedCanvas_Faunasheet` instance by delegating to the parent `canvas.Canvas` constructor with all provided positional and keyword arguments. After the parent initialization, it sets up an instance-level `_saved_page_states` attribute as an empty list.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to `self.page_position(pos)` with the provided argument. This method serves as a named wrapper around `page_position`, accepting a single positional parameter `pos` whose type and valid values are determined by the underlying `page_position` implementation.

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current canvas state to the `_saved_page_states` list. After preserving the state, it initializes a new page by calling `_startPage()`.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Sets the font to "Cambria" at size 6, then draws a right-aligned page number string at the position `(200 mm, 20 mm)` on the current canvas page. The string is formatted as `"Pag. %d di %d"`, where the first value is the current page number (`self._pageNumber`) and the second is the total page count (`page_count`).

### NumberedCanvas_Faunaindex

*No description available.*
A subclass of `canvas.Canvas` that extends the ReportLab canvas to support total page count in page numbering for Fauna index documents. It defers page rendering by saving each page's state during `showPage()`, then iterates over all saved states at `save()` time to inject the final page count before committing. Page numbers are drawn in Helvetica 8pt at position `(270 mm, 10 mm)` using the format `"Pag. %d di %d"`.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

Initializes a `NumberedCanvas_Faunaindex` instance by delegating to the parent `canvas.Canvas.__init__` method, passing through all positional and keyword arguments unchanged. After the parent initialization, it sets up an instance attribute `_saved_page_states` as an empty list.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to the `page_position` method with the provided `pos` argument. This method serves as a named wrapper, offering a semantically distinct interface for specifying position on the current page.

**Parameters:**
- `pos` — The position value passed to `page_position`. See implementation for accepted types and format.

##### showPage(self)

*No description available.*
Finalizes the current page by saving its state to the `_saved_page_states` list as a copy of the current instance dictionary. After preserving the page state, it initializes a new page by calling `_startPage()`.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

Renders the current page number and total page count as a right-aligned string in the footer area of the PDF canvas.

The text is formatted as `"Pag. %d di %d"` using the current page number (`self._pageNumber`) and the provided `page_count` argument, rendered in Helvetica 8-point font at position `(270 mm, 10 mm)` from the bottom-left origin.

### single_Fauna_pdf_sheet

Single Fauna record PDF sheet generator.
Supports multiple languages: IT, DE, EN, FR, ES, AR, CA
Professional full-page layout with organized sections.

**Inherits from**: object

#### Methods

##### __init__(self, data)

*No description available.*
Initializes a fauna record instance by unpacking a sequential data structure into 36 named instance attributes. Each attribute corresponds to a positional index in the `data` argument, mapping fields such as `id_fauna`, `id_us`, `sito`, `area`, `saggio`, `us`, and a range of archaeozoological properties including species identification, skeletal parts, taphonomic signs, combustion traces, fragmentation state, conservation status, and stratigraphic reliability. The `data` parameter must be an ordered, index-accessible sequence containing exactly the expected values at positions `0` through `35`.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, e.g., `"31-12-2024"`). The formatted date string is then returned as the result.

##### create_sheet(self)

Italian version of the sheet

##### create_sheet_de(self)

German version of the sheet

##### create_sheet_en(self)

English version of the sheet

##### create_sheet_fr(self)

French version of the sheet

##### create_sheet_es(self)

Spanish version of the sheet

##### create_sheet_ar(self)

Arabic version of the sheet

##### create_sheet_ca(self)

Catalan version of the sheet

### generate_fauna_pdf

Main PDF generator class for Fauna records.
Generates both individual sheets and index lists.

**Inherits from**: object

#### Methods

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the `"%d-%m-%Y"` pattern (day-month-year, e.g., `"31-12-2024"`). No parameters are accepted beyond the implicit `self` reference.

##### build_Fauna_sheets(self, records)

Build PDF sheets in Italian

##### build_Fauna_sheets_de(self, records)

Build PDF sheets in German

##### build_Fauna_sheets_en(self, records)

Build PDF sheets in English

##### build_Fauna_sheets_fr(self, records)

Build PDF sheets in French

##### build_Fauna_sheets_es(self, records)

Build PDF sheets in Spanish

##### build_Fauna_sheets_ar(self, records)

Build PDF sheets in Arabic

##### build_Fauna_sheets_ca(self, records)

Build PDF sheets in Catalan

