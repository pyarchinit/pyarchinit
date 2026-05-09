# modules/utility/tma_import_parser_extended.py

## Overview

This file contains 4 documented elements.

## Classes

### TMAImportManagerExtended

Manager esteso che supporta inventari

**Inherits from**: TMAImportManager

#### Methods

##### __init__(self, db_manager)

Initializes a `TMAImportManagerExtended` instance by delegating to the parent class `TMAImportManager` constructor via `super().__init__(db_manager)`. Stores the provided `db_manager` reference as an instance attribute for later use by the extended class.

##### import_file(self, file_path, custom_mapping, use_festos_parser)

Override del metodo import_file per gestire inventari DOCX

