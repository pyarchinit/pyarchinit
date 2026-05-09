# modules/utility/pyarchinit_exp_pdf_experimental.py

## Overview

This file contains 14 documented elements.

## Classes

### NumberedCanvas_Individuisheet

*No description available.*
A subclass of `canvas.Canvas` that extends ReportLab's canvas with multi-page awareness, enabling each page to display a "Pag. X di Y" page numbering footer. It defers the rendering of individual pages by capturing page states in `_saved_page_states` during `showPage()`, then iterates over all collected states at `save()` time to apply the total page count before finalizing the document. Page numbers are drawn right-aligned at position `(200 mm, 20 mm)` using the Cambria font at size 5.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

Initializes a `NumberedCanvas_Individuisheet` instance by delegating to the parent `canvas.Canvas.__init__` method, passing through all positional and keyword arguments. After the parent class is initialized, it sets up an instance-level attribute `_saved_page_states` as an empty list.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to `self.page_position(pos)`. This method serves as a named wrapper around `page_position`, accepting a single positional argument `pos` and forwarding it without modification.

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current instance state to the `_saved_page_states` list. After preserving the state, it calls `_startPage()` to initialize a new page for subsequent content.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Sets the font to "Cambria" at size 5, then renders a right-aligned pagination string in the format `"Pag. <current_page> di <total_pages>"` at the position `(200 mm, 20 mm)` on the current canvas page. The `page_count` parameter represents the total number of pages, while the current page number is retrieved from the instance attribute `self._pageNumber`.

### single_pdf_sheet

*No description available.*
Represents a single PDF sheet layout built from a flat data list. The class stores the provided data in `DATA` and exposes two methods: `datestrfdate`, which returns the current date formatted as `"%d-%m-%Y"`, and `create_sheet`, which constructs and returns a `Table` object composed of styled `Paragraph` elements derived from the data entries. The table is rendered with a fixed column width of 50 units and a predefined cell-spanning style that organises fields such as site, area, US, individual number, sex, age, age class, observations, and scheduling metadata across a seven-row grid.

#### Methods

##### __init__(self, data)

*No description available.*
Initializes a new instance of the `single_pdf_sheet` class. Accepts a single `data` parameter and assigns it to the instance attribute `DATA`, overriding the class-level default empty string.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year). The formatted date string is returned as the method's result.

##### create_sheet(self)

*No description available.*
Builds and returns a formatted `Table` object representing a single record sheet for an individual entry. The method defines two paragraph styles (`styNormal` and `styDescrizione`) using ReportLab's `getSampleStyleSheet`, maps the instance's `DATA` list into bold `Paragraph` objects, and arranges them into a predefined 7-row by 10-column cell schema with explicit span and alignment directives. The resulting `Table` is constructed with a column width of 50 units and a grid border style, and is returned for inclusion in a PDF document.

### generate_pdf

*No description available.*
A utility class responsible for generating PDF documents from archaeological record data. It resolves the output directory from the `PYARCHINIT_HOME` environment variable, targeting a subdirectory named `pyarchinit_PDF_folder`, and provides a method (`build_Individui_sheets`) that iterates over a collection of records, constructs individual PDF sheets via `single_pdf_sheet`, and writes the compiled output to a file named `Scheda Individui.pdf` using a `SimpleDocTemplate` with a custom canvas (`NumberedCanvas_Individuisheet`). A helper method (`datestrfdate`) returns the current date formatted as `DD-MM-YYYY`.

#### Methods

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. It retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, e.g., `"31-12-2024"`). The formatted date string is then returned to the caller.

##### build_Individui_sheets(self, records)

Builds a multi-page PDF document containing individual record sheets from the provided `records` collection. For each record, it instantiates a `single_pdf_sheet` object, generates its sheet content, and appends a `PageBreak` after each sheet. The resulting document is written to a file named `'Scheda Individui.pdf'` located at `self.PDF_path`, using `SimpleDocTemplate` and `NumberedCanvas_Individuisheet` as the canvas maker.

