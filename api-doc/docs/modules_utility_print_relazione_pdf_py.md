# modules/utility/print_relazione_pdf.py

## Overview

This file contains 15 documented elements.

## Classes

### NumberedCanvas_Relazione

*No description available.*
A subclass of `canvas.Canvas` (ReportLab) that extends the standard canvas with multi-page awareness and automatic page numbering for report generation. It accumulates page states during rendering via an overridden `showPage` method, then replays them on `save` to inject a total page count into each page. On all pages after the first, `draw_page_number` renders a logo image, two horizontal border lines, a right-aligned page number (`pag. X`), and two centred footer strings identifying "adArte srl Archeologia, Restauro, ICT".

**Inherits from**: canvas.Canvas

#### Methods

##### __init__(self)

## `__init__` Method

Initializes a `NumberedCanvas_Relazione` instance by delegating to the parent `canvas.Canvas` constructor with all provided positional and keyword arguments. After the parent initialization, it sets up an instance-level attribute `_saved_page_states` as an empty list, which is used to track page states across the canvas lifecycle.

##### define_position(self, pos)

*No description available.*
Sets the page position by delegating directly to the `page_position` method with the provided `pos` argument. This method serves as a named wrapper, offering a semantically distinct interface for specifying position on the canvas.

**Parameters:**
- `pos` — The position value passed to `page_position`. See implementation for accepted types and format.

##### showPage(self)

*No description available.*
Finalizes the current page by saving its state to the `_saved_page_states` list as a copy of the current instance dictionary. After preserving the page state, it initializes a new page by calling `_startPage()`. This method is typically called to mark the end of a page before beginning content on a new one.

##### save(self)

add page info to each page (page x of y)

##### draw_page_number(self, page_count)

*No description available.*
Renders page decoration elements onto the current canvas page, skipping all rendering on the first page. For all subsequent pages, it draws an inline logo image, two horizontal lines, and footer text including a right-aligned page number (formatted as `"pag. %d"` using `self._pageNumber - 1`), a centred company name, and a centred address string. The `page_count` parameter is accepted but not used within the method body.

### exp_rel_pdf

*No description available.*
A PDF report generator for archaeological site data, scoped to a single site identified by the `SITO` parameter supplied at construction. On instantiation, the class establishes a database connection via `Pyarchinit_db_management` and exposes methods to query, sort, and load records for use in report generation. The primary method, `export_rel_pdf`, assembles a multi-section ReportLab PDF document — including site description, chronological periodization, structural data, an image catalogue, and appendix sections — and writes the output to a file named `relazione.pdf` within the configured `pyarchinit_PDF_folder` directory.

**Inherits from**: object

#### Methods

##### __init__(self, sito)

*No description available.*
Initializes a new instance of the class by assigning the provided `sito` argument to the instance attribute `self.SITO`. Immediately invokes `self.connection_db()` to establish a database connection upon instantiation.

##### connection_db(self)

*No description available.*
Establishes a database connection by instantiating a `Connection` object and retrieving its connection string via `conn_str()`. It uses the resulting string to initialize a `Pyarchinit_db_management` instance, stored as `self.DB_MANAGER`, and invokes its `connection()` method. If any exception occurs during this process, a warning dialog is displayed to the user with the message `"La connessione e' fallita"`.

##### search_records(self, f, v, m)

*No description available.*
Queries the database for records matching a specified field-value pair within a given mapper table class. Constructs a search dictionary using the provided field name `f` and value `v`, then delegates the query to `DB_MANAGER.query_bool()` using the mapper class `m`. Prints the result to standard output and returns the query result.

##### extract_id_list(self, rec, idf)

*No description available.*
Iterates over a list of records (`rec`) and dynamically retrieves the value of a specified field (`idf`) from each record using `eval`. The extracted field values are collected into a list, which is returned to the caller.

**Parameters:**
- `rec` — a list of record objects to iterate over.
- `idf` — a string representing the field name whose value is to be extracted from each record.

**Returns:** A list containing the value of the specified field from each record in `rec`.

##### load_data_sorted(self, id_list, sort_fields_list, sort_mode, mapper_table_class, id_table)

*No description available.*
Loads a sorted set of database records into the instance's `DATA_LIST` by delegating the query to `DB_MANAGER.query_sort` using the provided identifiers, sort fields, sort mode, mapper table class, and ID table. The method first assigns all parameters to their corresponding instance attributes, then appends each record returned by the sorted query to `DATA_LIST`.

**Parameters:**
- `id_list` — list of record identifiers to query.
- `sort_fields_list` — list of fields by which the results are sorted.
- `sort_mode` — the sort direction or mode applied to the query.
- `mapper_table_class` — the ORM mapper class representing the target table.
- `id_table` — the identifier of the table to query against.

##### myFirstPage(self, canvas, doc)

*No description available.*
Renders the first page template for a PDF export by loading a logo image from the `pyarchinit_DB_folder` directory and scaling it to 1.5 inches in width while preserving the aspect ratio for height. It saves the canvas state, draws the site name (`self.SITO`) centered near the top of the page in 16-point Times-Bold font (with underscores replaced by spaces), and renders a page information string in 9-point Cambria font at the bottom-left corner. The canvas state is restored after all drawing operations are complete.

##### export_rel_pdf(self)

Generates a multi-section PDF report ("relazione.pdf") saved to `self.PDF_path`, assembling a `ReportLab` `Story` list that includes a logo, header information, site description, excavation periodization, structural data, a image catalogue section, and appendix placeholders. It queries the database via `self.DB_MANAGER` for site, periodization, and structure records filtered by `self.SITO`, formatting each section with appropriate headings, paragraphs, and page breaks. The document is built using `SimpleDocTemplate` with A4 page size and rendered with the `NumberedCanvas_Relazione` canvas maker, with `self.myFirstPage` applied to the first page.

