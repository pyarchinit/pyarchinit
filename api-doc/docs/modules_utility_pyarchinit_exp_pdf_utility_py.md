# modules/utility/pyarchinit_exp_pdf_utility.py

## Overview

This file contains 14 documented elements.

## Classes

### NumberedCanvas_Individuisheet

*No description available.*
A subclass of `canvas.Canvas` that extends ReportLab's canvas with multi-page awareness, enabling "page X of Y" numbering across a document. It defers page rendering by capturing each page's state in `_saved_page_states` during `showPage`, then iterates over all saved states at `save` time to draw the final page count on each page. Page numbers are rendered in Cambria 5pt font, right-aligned at position `(200mm, 20mm)`, formatted as `"Pag. %d di %d"`.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

Initializes a `NumberedCanvas_Individuisheet` instance by delegating to the parent `canvas.Canvas.__init__` method, passing through all positional and keyword arguments. After the parent class is initialized, it sets up an instance-level attribute `_saved_page_states` as an empty list.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to `self.page_position(pos)`. This method serves as a named wrapper around `page_position`, accepting a single positional argument `pos` that is passed through unchanged. See the implementation of `page_position` for details on how the position value is applied.

##### showPage(self)

*No description available.*
Finalizes the current page by saving a snapshot of the current canvas state to the `_saved_page_states` list. After preserving the state, it initializes a new page by calling `_startPage()`. This method is typically called to mark the end of a page before proceeding to define content on the next one.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Sets the font to "Cambria" at size 5, then renders a right-aligned pagination string in the format `"Pag. <current_page> di <total_pages>"` at the position `(200 mm, 20 mm)` on the current canvas page. The `page_count` parameter represents the total number of pages, while the current page number is retrieved from the instance attribute `self._pageNumber`.

### single_pdf_sheet

*No description available.*
Represents a single PDF sheet layout built from a provided data sequence. The class stores the input data in the `DATA` class-level attribute and exposes two methods: `datestrfdate`, which returns the current date formatted as `"%d-%m-%Y"`, and `create_sheet`, which constructs and returns a `Table` object composed of bold `Paragraph` elements derived from the data entries, arranged in a predefined seven-row, ten-column grid schema with associated cell spanning and styling rules.

#### Methods

##### __init__(self, data)

*No description available.*
Initializes a new instance of the `single_pdf_sheet` class. Accepts a single `data` parameter and assigns it to the instance attribute `DATA`, overriding the class-level default empty string.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the `"%d-%m-%Y"` pattern (day-month-year, e.g., `"31-12-2024"`). The formatted date string is returned as the method's output.

##### create_sheet(self)

*No description available.*
Builds and returns a formatted `Table` object representing a structured data sheet for individual records. The method configures two paragraph styles (`styNormal` and `styDescrizione`) using ReportLab's `getSampleStyleSheet`, maps entries from `self.DATA` into a dictionary, and converts each entry into a bold `Paragraph` element. These paragraphs are arranged into a predefined 7-row by 10-column cell schema with corresponding span and alignment table styles applied before the `Table` is constructed and returned.

### generate_pdf

*No description available.*
A utility class responsible for generating PDF documents from archaeological record data. It resolves the output directory from the `PYARCHINIT_HOME` environment variable, targeting a subdirectory named `pyarchinit_PDF_folder`, and provides a method (`build_Individui_sheets`) that iterates over a collection of records, constructs individual PDF sheets via `single_pdf_sheet`, and writes the compiled output to a file named `Scheda Individui.pdf` using ReportLab's `SimpleDocTemplate`. A helper method (`datestrfdate`) returns the current date formatted as `DD-MM-YYYY`.

#### Methods

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"` (day-month-year, e.g., `"31-12-2024"`). The formatted date string is then returned to the caller.

##### build_Individui_sheets(self, records)

Builds a multi-page PDF document containing individual record sheets from the provided `records` collection. For each record, it instantiates a `single_pdf_sheet` object, generates its sheet content, and appends a `PageBreak` after each sheet. The resulting document is written to a file named `'Scheda Individui.pdf'` located at `self.PDF_path`, using `SimpleDocTemplate` and `NumberedCanvas_Individuisheet` as the canvas maker.

