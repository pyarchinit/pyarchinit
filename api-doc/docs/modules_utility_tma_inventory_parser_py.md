# modules/utility/tma_inventory_parser.py

## Overview

This file contains 6 documented elements.

## Classes

### TMAInventoryParser

Parser specifico per file inventario cassette archeologiche

#### Methods

##### __init__(self)

Initializes a new `TMAInventoryParser` instance by setting up the `default_values` dictionary, which contains predefined fallback values used during inventory parsing. The dictionary defines five fields: `ogtm` (material type, defaulting to `'CERAMICA'`), `ldct` (localization, defaulting to `'MAGAZZINO'`), `stato` (defaulting to `'COMPLETO'`), `determinazione` (defaulting to `'ND'`), and `dsstcc` (conservation status, defaulting to `'A'`).

##### parse_docx_inventory(self, file_path, sito)

Parsa un file docx con inventario cassette

Args:
    file_path: Path del file docx
    sito: Nome del sito (se non specificato, cerca nel testo)
    
Returns:
    Lista di dizionari con i record da importare

### TMAInventoryImportDialog

Dialog per completare i dati mancanti durante l'import

#### Methods

##### __init__(self, parent)

Initializes a new instance of `TMAInventoryImportDialog`, a dialog used to complete missing data during an import operation. Sets the `parent` reference to the provided argument, and initializes `site_default` to `None` and `material_defaults` to an empty dictionary.

##### get_completion_data(self, records)

Mostra un dialog per completare i dati mancanti

Returns:
    Tuple di (records aggiornati, conferma import)

