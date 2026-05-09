# scripts/generate_thesaurus_html.py

## Overview

This file contains 7 documented elements.

## Functions

### get_html_template()

Restituisce il template HTML base.

### generate_nav_links(tables_data, lang)

Genera i link di navigazione.

**Parameters:**
- `tables_data`
- `lang`

### generate_table_section(table_id, table_data, labels)

Genera una sezione per una tabella.

**Parameters:**
- `table_id`
- `table_data`
- `labels`

### load_thesaurus_data(db_path)

Carica i dati del thesaurus dal database.

**Parameters:**
- `db_path`

### generate_html_for_language(lang, thesaurus_data, output_dir)

Genera il file HTML per una lingua specifica.

**Parameters:**
- `lang`
- `thesaurus_data`
- `output_dir`

### main()

Funzione principale.

