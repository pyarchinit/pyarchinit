# modules/utility/pdf_models/pyarchinit_exp_Findssheet_pdf.py

## Overview

This file contains 21 documented elements.

## Classes

### NumberedCanvas_Findssheet

*No description available.*
A subclass of `canvas.Canvas` that extends the ReportLab canvas with multi-page awareness for finds sheet documents. It defers page rendering by capturing each page's state in `_saved_page_states` during `showPage()`, then replays all states at `save()` time to inject a page number indicator ("Pag. X di Y") in Helvetica 8pt at position 200 mm × 20 mm on each page. The `define_position` method delegates to `self.page_position(pos)` for additional positional configuration.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

*No description available.*
Initializes a `NumberedCanvas_Findssheet` instance by delegating to the parent `canvas.Canvas` constructor with all provided positional and keyword arguments. After the parent initialization, it sets up an instance-level attribute `_saved_page_states` as an empty list, intended to track page state data across the canvas lifecycle.

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
Sets the font to Helvetica at size 8, then draws a right-aligned pagination string at position (200 mm, 20 mm) on the canvas. The string follows the format `"Pag. %d di %d"`, where the first value is the current page number (`self._pageNumber`) and the second is the total page count (`page_count`).

**Parameters:**
- `page_count` (`int`): The total number of pages in the document.

### NumberedCanvas_USindex

*No description available.*
A custom ReportLab `canvas.Canvas` subclass that defers page rendering in order to support total page count in page numbering. It accumulates page states on each `showPage` call and, upon `save`, iterates over all saved states to stamp a right-aligned pagination string ("Pag. X di Y") in Helvetica 8pt at position 270 mm × 10 mm before finalising the document. This pattern allows the total number of pages to be known before any individual page footer is drawn.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

*No description available.*
Initializes a `NumberedCanvas_USindex` instance by delegating to the parent `canvas.Canvas` constructor with all provided positional and keyword arguments. After the parent initialization, it sets up the `_saved_page_states` instance attribute as an empty list.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to `self.page_position(pos)` with the provided argument. This method serves as a named wrapper around `page_position`, accepting a single positional parameter `pos` whose type and valid values are determined by the underlying `page_position` implementation.

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current canvas state to the `_saved_page_states` list. After preserving the state, it initializes a new page by calling `_startPage()`. This method is typically called to mark the end of a page before proceeding to define content on the next one.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Renders a page number string in the format `"Pag. X di Y"` at a fixed position on the current canvas page. The text is drawn right-aligned at coordinates `(270 mm, 10 mm)` using the `"Helvetica"` font at size 8, where `self._pageNumber` represents the current page and `page_count` represents the total number of pages.

**Parameters:**
- `page_count` (`int`): The total number of pages in the document.

### single_Finds_pdf_sheet

*No description available.*
A data container and PDF layout builder for a single archaeological finds inventory record ("Scheda Inventario Reperti"). The constructor accepts a sequence of 18 data elements, assigning them to named instance attributes covering identification, classification, conservation, measurements, technologies, and bibliographic references. The `create_sheet` method formats these attributes into a styled ReportLab `Table` object comprising 14 rows of labeled fields, suitable for direct inclusion in a PDF document.

**Inherits from**: object

#### Methods

##### __init__(self, data)

*No description available.*
Initializes a `single_Finds_pdf_sheet` instance by unpacking a sequential `data` collection into named instance attributes representing the fields of an archaeological find record. The attributes assigned are `id_invmat`, `sito`, `numero_inventario`, `tipo_reperto`, `criterio_schedatura`, `definizione`, `descrizione`, `area`, `us`, `lavato`, `nr_cassa`, `luogo_conservazione`, `stato_conservazione`, `datazione_reperto`, `elementi_reperto`, `misurazioni`, `rif_biblio`, and `tecnologie`, mapped from indices `0` through `17` of `data` respectively. No validation or transformation is applied to the input values during initialization.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, e.g., `"31-12-2024"`). The formatted date string is then returned to the caller.

##### create_sheet(self)

Builds and returns a formatted `Table` object representing an inventory record sheet ("SCHEDA INVENTARIO REPERTI") for an archaeological find. The method constructs styled `Paragraph` elements from instance attributes — including site, area, US, inventory number, find type, conservation state, description, find elements, measurements, technologies, bibliographic references, stratigraphic references, and storage details — and arranges them into a 14-row, 10-column cell schema. A corresponding table style defining grid lines, cell spans, and alignments is applied before the `Table` is returned.

### generate_pdf

*No description available.*
A utility class responsible for generating PDF documents and indexes from archaeological record data. It resolves the output directory from the `PYARCHINIT_HOME` environment variable, writing all generated files to the `pyarchinit_PDF_folder` subdirectory. The class provides methods to build paginated PDF sheets for finds records (`build_Finds_sheets`) and a formatted stratigraphic unit index document (`build_index_US`), both using ReportLab as the underlying PDF generation library.

**Inherits from**: object

#### Methods

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the `"%d-%m-%Y"` pattern (day-month-year). The formatted date string is then returned to the caller.

##### build_Finds_sheets(self, records)

Iterates over a collection of records to generate individual finds sheets by instantiating `single_Finds_pdf_sheet` for each record and appending the resulting sheet along with a `PageBreak` to an elements list. Constructs the output file path using `self.PDF_path` and the fixed filename `scheda_Finds.pdf`, then writes the compiled PDF document to that file using `SimpleDocTemplate` with `NumberedCanvas_Findssheet` as the canvas maker. The output file is closed upon completion of the build process.

##### build_index_US(self, records, sito)

Builds a PDF index document of stratigraphic units ("Unità Stratigrafiche") for a given excavation site. It iterates over the provided `records`, generating a formatted table using `US_index_pdf_sheet` for each record, and composes the document with a styled heading that includes the site name (`sito`) and the current date. The resulting PDF is written to a file named `indice_us.pdf` in the configured `PDF_path` directory, rendered on a landscape A4-sized page using `NumberedCanvas_USindex`.

