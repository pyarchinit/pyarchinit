# modules/utility/festos_inventory_parser.py

## Overview

This file contains 4 documented elements.

## Classes

### FestosInventoryParser

Parser specifico per file inventario cassette archeologiche formato Festos

#### Methods

##### __init__(self)

Initializes a new `FestosInventoryParser` instance by setting up a dictionary of default field values used when parsing archaeological box inventory files in the Festos format. The `default_values` dictionary pre-populates fields such as material type (`ogtm`), location (`ldct`), status (`stato`), category (`macc`), and chronological range (`dtzg`) with predefined fallback strings. Two empty lists, `errors` and `warnings`, are also initialized to collect any issues encountered during subsequent parsing operations.

##### parse_file(self, file_path, sito)

Parsa un file docx con inventario cassette e restituisce i record
invece di salvarli direttamente nel database

Args:
    file_path: Path del file docx
    sito: Nome del sito (se non specificato, cerca nel testo)
    
Returns:
    Tuple con (lista record, lista errori, lista warning)

