# scripts/update_old_sqlite_db.py

## Overview

This file contains 20 documented elements.

## Classes

### PyArchInitDBUpdater

Classe per aggiornare database SQLite vecchi di PyArchInit

#### Methods

##### __init__(self, db_path)

Initializes a new `PyArchInitDBUpdater` instance with the specified database path. Sets `db_path` to the provided `db_path` argument and initializes `conn`, `cursor`, and `updates_made` to `None`, `None`, and an empty list, respectively. The database connection is not established at construction time; use `connect()` to open it.

##### connect(self)

Connette al database

##### check_column_exists(self, table_name, column_name)

Verifica se una colonna esiste in una tabella

##### check_table_exists(self, table_name)

Verifica se una tabella esiste

##### add_column(self, table_name, column_name, column_type, default_value)

Aggiunge una colonna a una tabella se non esiste

##### update_pyarchinit_thesaurus_sigle(self)

Aggiorna la tabella pyarchinit_thesaurus_sigle

##### update_us_table(self)

Aggiorna la tabella us_table

##### update_site_table(self)

Aggiorna la tabella site_table

##### update_inventario_materiali(self)

Aggiorna la tabella inventario_materiali_table

##### update_pottery_table(self)

Aggiorna la tabella pottery_table

##### update_struttura_table(self)

Aggiorna la tabella struttura_table

##### update_periodizzazione_table(self)

Aggiorna la tabella periodizzazione_table

##### fix_vector_layer_views(self)

Corregge i tipi di campo nelle view dei layer vettoriali

##### create_missing_tables(self)

Crea tabelle che potrebbero mancare completamente

##### create_triggers(self)

Crea i trigger necessari per il database

##### backup_database(self)

Crea un backup del database prima delle modifiche

##### update_database(self)

Esegue tutti gli aggiornamenti necessari

## Functions

### main()

Funzione principale

