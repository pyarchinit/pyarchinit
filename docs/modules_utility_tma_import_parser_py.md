# modules/utility/tma_import_parser.py

## Overview

This file contains 100 documented elements.

## Classes

### TMAFieldMapping

Mappatura dei campi tra vari formati e il database TMA

#### Methods

##### find_field_mapping(cls, field_name)

Trova il campo del database corrispondente a un nome di campo del file

##### validate_field_value(cls, field, value)

Valida il valore di un campo specifico

### BaseParser

Classe base astratta per i parser

**Inherits from**: ABC

#### Methods

##### __init__(self, file_path)

##### parse(self)

Metodo astratto per il parsing del file

##### validate_required_fields(self, record)

Valida i campi obbligatori

##### clean_value(self, value)

Pulisce e normalizza i valori

### ExcelParser

Parser per file Excel

**Inherits from**: BaseParser

#### Methods

##### parse(self)

Parsing di file Excel

### CSVParser

Parser per file CSV

**Inherits from**: BaseParser

#### Methods

##### __init__(self, file_path, delimiter, encoding)

##### parse(self)

Parsing di file CSV

### JSONParser

Parser per file JSON

**Inherits from**: BaseParser

#### Methods

##### parse(self)

Parsing di file JSON

### XMLParser

Parser per file XML

**Inherits from**: BaseParser

#### Methods

##### parse(self)

Parsing di file XML

### DOCXParser

Parser per file DOCX

**Inherits from**: BaseParser

#### Methods

##### __init__(self, file_path, use_festos_parser, db_session)

##### parse(self)

Parsing di file DOCX

### TMAImportManager

Manager principale per l'importazione dei dati TMA

#### Methods

##### __init__(self, db_manager)

##### import_file(self, file_path, custom_mapping, use_festos_parser)

Importa un file nel database TMA

Args:
    file_path: percorso del file da importare
    custom_mapping: mapping personalizzato dei campi (opzionale)
    use_festos_parser: usa il parser specifico per Festos (per file DOCX)

Returns:
    Tuple con (numero record importati, lista errori, lista warning)

##### import_batch(self, file_paths)

Importa multipli file in batch

### TMAFieldMapping

Mappatura dei campi tra vari formati e il database TMA

#### Methods

##### find_field_mapping(cls, field_name)

Trova il campo del database corrispondente a un nome di campo del file

##### validate_field_value(cls, field, value)

Valida il valore di un campo specifico

### BaseParser

Classe base astratta per i parser

**Inherits from**: ABC

#### Methods

##### __init__(self, file_path)

##### parse(self)

Metodo astratto per il parsing del file

##### validate_required_fields(self, record)

Valida i campi obbligatori

##### clean_value(self, value)

Pulisce e normalizza i valori

### ExcelParser

Parser per file Excel

**Inherits from**: BaseParser

#### Methods

##### parse(self)

Parsing di file Excel

### CSVParser

Parser per file CSV

**Inherits from**: BaseParser

#### Methods

##### __init__(self, file_path, delimiter, encoding)

##### parse(self)

Parsing di file CSV

### JSONParser

Parser per file JSON

**Inherits from**: BaseParser

#### Methods

##### parse(self)

Parsing di file JSON

### XMLParser

Parser per file XML

**Inherits from**: BaseParser

#### Methods

##### parse(self)

Parsing di file XML

### DOCXParser

Parser per file DOCX

**Inherits from**: BaseParser

#### Methods

##### __init__(self, file_path, use_festos_parser, db_session)

##### parse(self)

Parsing di file DOCX

### TMAImportManager

Manager principale per l'importazione dei dati TMA

#### Methods

##### __init__(self, db_manager)

##### import_file(self, file_path, custom_mapping, use_festos_parser)

Importa un file nel database TMA

Args:
    file_path: percorso del file da importare
    custom_mapping: mapping personalizzato dei campi (opzionale)
    use_festos_parser: usa il parser specifico per Festos (per file DOCX)

Returns:
    Tuple con (numero record importati, lista errori, lista warning)

##### import_batch(self, file_paths)

Importa multipli file in batch

### TMAFieldMapping

Mappatura dei campi tra vari formati e il database TMA

#### Methods

##### find_field_mapping(cls, field_name)

Trova il campo del database corrispondente a un nome di campo del file

##### validate_field_value(cls, field, value)

Valida il valore di un campo specifico

### BaseParser

Classe base astratta per i parser

**Inherits from**: ABC

#### Methods

##### __init__(self, file_path)

##### parse(self)

Metodo astratto per il parsing del file

##### validate_required_fields(self, record)

Valida i campi obbligatori

##### clean_value(self, value)

Pulisce e normalizza i valori

### ExcelParser

Parser per file Excel

**Inherits from**: BaseParser

#### Methods

##### parse(self)

Parsing di file Excel

### CSVParser

Parser per file CSV

**Inherits from**: BaseParser

#### Methods

##### __init__(self, file_path, delimiter, encoding)

##### parse(self)

Parsing di file CSV

### JSONParser

Parser per file JSON

**Inherits from**: BaseParser

#### Methods

##### parse(self)

Parsing di file JSON

### XMLParser

Parser per file XML

**Inherits from**: BaseParser

#### Methods

##### parse(self)

Parsing di file XML

### DOCXParser

Parser per file DOCX

**Inherits from**: BaseParser

#### Methods

##### __init__(self, file_path, use_festos_parser, db_session)

##### parse(self)

Parsing di file DOCX

### TMAImportManager

Manager principale per l'importazione dei dati TMA

#### Methods

##### __init__(self, db_manager)

##### import_file(self, file_path, custom_mapping, use_festos_parser)

Importa un file nel database TMA

Args:
    file_path: percorso del file da importare
    custom_mapping: mapping personalizzato dei campi (opzionale)
    use_festos_parser: usa il parser specifico per Festos (per file DOCX)

Returns:
    Tuple con (numero record importati, lista errori, lista warning)

##### import_batch(self, file_paths)

Importa multipli file in batch

### TMAFieldMapping

Mappatura dei campi tra vari formati e il database TMA

#### Methods

##### find_field_mapping(cls, field_name)

Trova il campo del database corrispondente a un nome di campo del file

##### validate_field_value(cls, field, value)

Valida il valore di un campo specifico

### BaseParser

Classe base astratta per i parser

**Inherits from**: ABC

#### Methods

##### __init__(self, file_path)

##### parse(self)

Metodo astratto per il parsing del file

##### validate_required_fields(self, record)

Valida i campi obbligatori

##### clean_value(self, value)

Pulisce e normalizza i valori

### ExcelParser

Parser per file Excel

**Inherits from**: BaseParser

#### Methods

##### parse(self)

Parsing di file Excel

### CSVParser

Parser per file CSV

**Inherits from**: BaseParser

#### Methods

##### __init__(self, file_path, delimiter, encoding)

##### parse(self)

Parsing di file CSV

### JSONParser

Parser per file JSON

**Inherits from**: BaseParser

#### Methods

##### parse(self)

Parsing di file JSON

### XMLParser

Parser per file XML

**Inherits from**: BaseParser

#### Methods

##### parse(self)

Parsing di file XML

### DOCXParser

Parser per file DOCX

**Inherits from**: BaseParser

#### Methods

##### __init__(self, file_path, use_festos_parser, db_session)

##### parse(self)

Parsing di file DOCX

### TMAImportManager

Manager principale per l'importazione dei dati TMA

#### Methods

##### __init__(self, db_manager)

##### import_file(self, file_path, custom_mapping, use_festos_parser)

Importa un file nel database TMA

Args:
    file_path: percorso del file da importare
    custom_mapping: mapping personalizzato dei campi (opzionale)
    use_festos_parser: usa il parser specifico per Festos (per file DOCX)

Returns:
    Tuple con (numero record importati, lista errori, lista warning)

##### import_batch(self, file_paths)

Importa multipli file in batch

