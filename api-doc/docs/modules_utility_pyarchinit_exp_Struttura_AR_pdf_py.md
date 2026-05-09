# modules/utility/pyarchinit_exp_Struttura_AR_pdf.py

## Overview

This file contains 20 documented elements.

## Classes

### NumberedCanvas_Struttura_AR

*No description available.*
A custom ReportLab canvas subclass that extends `canvas.Canvas` to support total page count numbering across a multi-page PDF document. It defers page rendering by saving each page's state in `_saved_page_states`, then replays all states at save time to inject the final page count before committing. A page number label in the format `"Pag. X di Y"` is drawn in Helvetica 8pt at the bottom-right of each page using `draw_page_number`.

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

Initializes a `NumberedCanvas_Struttura_AR` instance by delegating to the parent `canvas.Canvas.__init__` method with all provided positional and keyword arguments. After the parent class is initialized, it sets up an empty list `_saved_page_states` as an instance attribute, which is used to store page state snapshots across the document's pages.

##### showPage(self)

Finalizes the current page by saving a snapshot of the current canvas state dictionary to the `_saved_page_states` list. After preserving the state, it calls `_startPage()` to initialize a new page for subsequent drawing operations.

##### save(self)

*No description available.*
Finalizes the document by iterating over all saved page states and restoring each one before rendering the page number and committing the page via `canvas.Canvas.showPage`. The total page count, derived from the length of `_saved_page_states`, is passed to `draw_page_number` on each page to enable "page X of Y" numbering. Once all pages have been processed, `canvas.Canvas.save` is called to complete and write the document.

##### draw_page_number(self, page_count)

Renders the page number indicator at a fixed position on the current page canvas. Sets the font to Helvetica at 8 points and draws a right-aligned string at coordinates (200 mm, 10 mm) formatted as `"Pag. %d di %d"`, displaying the current page number (`self._pageNumber`) and the total page count (`page_count`).

### single_Struttura_AR_pdf_sheet

PDF Sheet for Struttura with AR (Architettura Rupestre) layout - 3 pages

#### Methods

##### __init__(self, data)

Initializes a `single_Struttura_AR_pdf_sheet` instance by populating its attributes from a positional `data` sequence of up to 37 elements. Basic structural fields (indices 0–18) cover site identification, categorization, chronology, and measurements, while extended AR fields (indices 19–35) capture compilation metadata, topographic relations, architectural articulation, and functional phases; all attributes default to an empty string or `'[]'` if the corresponding index is absent from `data`. The final attribute, `id_struttura`, is read from index 36 or, if not present, falls back to a same-named attribute on `data` if one exists, otherwise defaults to `None`.

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method retrieves today's date using `date.today()` and formats it according to the pattern `"%d-%m-%Y"`, producing a string in `DD-MM-YYYY` format. This method takes no parameters and always reflects the date at the time of invocation.

##### safe_str(self, val)

*No description available.*
Converts a value to its string representation, guarding against empty or null-like values. If `val` is `None`, or its string representation equals `'None'` or `'[]'`, the method returns an empty string. Otherwise, it returns `str(val)`.

##### parse_table_data(self, data_str)

*No description available.*
Attempts to parse a string representation of table data into a Python object using `ast.literal_eval`. If `data_str` is `None`, the string `'None'`, the string `'[]'`, or if evaluation raises any exception, the method returns an empty list. On success, returns the evaluated Python object produced from the input string.

##### get_first_image(self)

Retrieves the file path of the first thumbnail image associated with the current `STRUTTURA` entity by querying the database for linked media records via `MEDIATOENTITY` and `MEDIA` tables. It constructs the resized thumbnail path using the connection's configured thumbnail directory and verifies the file exists on disk before returning it. Returns the file path string if a valid image is found, or `None` if no associated media exists, the file is absent, or any error occurs.

##### create_sheet(self)

*No description available.*
Creates a sheet layout using Italian (`'it'`) as the target language by delegating to the internal `_create_sheet_layout` method. Returns the result produced by `_create_sheet_layout('it')`.

##### create_sheet_en(self)

Creates a sheet layout using English as the target language by delegating to the internal `_create_sheet_layout` method with the language code `'en'`. Returns the result produced by `_create_sheet_layout('en')`.

##### create_sheet_de(self)

Creates and returns a sheet layout configured for the German language by delegating to `_create_sheet_layout` with the language code `'de'`. This method serves as a language-specific convenience wrapper, passing the fixed argument `'de'` to the underlying layout generation logic.

### generate_struttura_AR_pdf

*No description available.*
Generates multi-page PDF reports for Struttura AR (Archaeological Structure) records by assembling individual sheets produced by `single_Struttura_AR_pdf_sheet`. The class provides three locale-specific build methods — `build_Struttura_AR_sheets` (Italian), `build_Struttura_AR_sheets_en` (English), and `build_Struttura_AR_sheets_de` (German) — each iterating over a list of records, inserting page breaks between sheets, and writing the result to a fixed-name PDF file in the `pyarchinit_PDF_folder` directory. All output documents are formatted as A4 pages using `SimpleDocTemplate` with `NumberedCanvas_Struttura_AR` as the canvas maker.

#### Methods

##### datestrfdate(self)

*No description available.*
Returns the current date as a formatted string. The method calls `date.today()` and formats the result using the `strftime` directive `"%d-%m-%Y"`, producing a string in `DD-MM-YYYY` format. It takes no parameters beyond `self` and returns a `str`.

##### build_Struttura_AR_sheets(self, records)

Iterates over a list of records and generates a single-page PDF sheet for each record using `single_Struttura_AR_pdf_sheet`, inserting a `PageBreak` between consecutive sheets. Assembles all resulting elements into an A4 `SimpleDocTemplate` with fixed margins (top/bottom: 0.8 cm, left/right: 1 cm) and builds the document using `NumberedCanvas_Struttura_AR`. The output is written to a file named `Scheda_Struttura_AR.pdf` located in the directory specified by `self.PDF_path`.

##### build_Struttura_AR_sheets_en(self, records)

Builds an English-language PDF document containing one or more "Structure AR" form sheets from the provided `records` collection. Each record is processed by `single_Struttura_AR_pdf_sheet` to generate its sheet elements via `create_sheet_en()`, with a `PageBreak` inserted between consecutive sheets. The resulting document is written to `Structure_Form_AR.pdf` in the configured PDF output path, formatted as an A4 page using `SimpleDocTemplate` with `NumberedCanvas_Struttura_AR` as the canvas maker.

##### build_Struttura_AR_sheets_de(self, records)

Builds a multi-page German-language PDF document named `Strukturformular_AR.pdf` from a collection of records. For each record, it instantiates a `single_Struttura_AR_pdf_sheet` object, generates its German sheet elements via `create_sheet_de()`, and appends a `PageBreak` between consecutive sheets. The resulting document is written to the path defined by `self.PDF_path` using A4 page size with fixed margins, rendered via `NumberedCanvas_Struttura_AR`.

