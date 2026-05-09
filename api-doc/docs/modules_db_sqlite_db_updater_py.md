# modules/db/sqlite_db_updater.py

## Overview

This file contains 36 documented elements.

## Classes

### SQLiteDBUpdater

Gestisce l'aggiornamento automatico dei database SQLite vecchi

#### Methods

##### __init__(self, db_path, parent)

Initializes a new `SQLiteDBUpdater` instance with the path to the target SQLite database and an optional parent reference. Sets `conn` and `cursor` to `None` in preparation for a database connection, and initializes `updates_made` as an empty list to track applied updates.

##### log_message(self, message, level)

Log message to QGIS if available

##### check_and_update_database(self)

Verifica e aggiorna il database se necessario

##### needs_update(self)

Verifica se il database necessita di aggiornamento

##### backup_database(self)

Crea un backup del database

##### update_database(self)

Esegue l'aggiornamento del database

##### create_or_update_thesaurus_table(self)

Crea o aggiorna la tabella pyarchinit_thesaurus_sigle

##### update_us_table(self)

Aggiorna la tabella us_table

##### update_site_table(self)

Aggiorna la tabella site_table

##### update_ut_table(self)

Aggiorna la tabella ut_table con i nuovi campi survey (v4.9.21+) e analisi (v4.9.67+)

##### update_fauna_table(self)

Crea o aggiorna la tabella fauna_table (v4.9.21+)

##### update_fauna_thesaurus(self)

Installa/aggiorna le voci thesaurus per la tabella fauna_table (v4.9.21+)

##### update_ut_thesaurus(self)

Installa/aggiorna le voci thesaurus per la tabella ut_table in tutte le 7 lingue supportate (v4.9.68+)

##### update_site_management_thesaurus(self)

Seed thesaurus entries for site management (cantiere) tables.
7 codes (14.1-14.7) × 10 languages = ~470 entries.

##### fix_thesaurus_nome_tabella(self)

Fix thesaurus entries that have display names instead of actual table names.

This migration fixes a bug where the Thesaurus form was saving entries with
display names (e.g., 'Fauna') instead of actual table names (e.g., 'fauna_table').
Forms query using actual table names, so entries with display names were not found.

##### update_other_tables(self)

Aggiorna altre tabelle

##### update_struttura_table(self)

Aggiorna la tabella struttura_table con i nuovi campi per scheda AR

##### restore_tables_from_backups(self)

Ripristina tabelle mancanti dai backup se necessario

##### create_pottery_embeddings_metadata_table(self)

Create pottery embeddings metadata table for visual similarity search

##### fix_vector_layer_views(self)

Corregge i tipi di campo nelle view dei layer vettoriali

##### fix_field_types_in_base_tables(self)

Corregge i tipi di campo nelle tabelle base prima di ricreare le view

##### table_exists(self, table_name)

Check if a table exists

##### add_column_if_missing(self, table_name, column_name, column_type)

Add column to table if it doesn't exist

##### update_pottery_thesaurus(self)

Installa/aggiorna le voci thesaurus per la tabella Pottery

##### add_concurrency_columns(self)

Aggiunge le colonne di concurrency per la sincronizzazione con PostgreSQL (v5.0+)

##### create_missing_tables(self)

Crea tabelle mancanti per compatibilità con PostgreSQL (v5.0+)

##### create_performance_indexes(self)

Crea indici di performance per query frequenti

##### update_personale_table(self)

Crea personale_table se non esiste

##### update_presenze_table(self)

Crea presenze_table se non esiste

##### update_attrezzature_table(self)

Crea attrezzature_table se non esiste

##### update_budget_table(self)

Crea budget_table se non esiste

##### update_computo_metrico_table(self)

Crea computo_metrico_table se non esiste

##### update_inventario_lapidei_table(self)

Crea inventario_lapidei_table se non esiste

## Functions

### check_and_update_sqlite_db(db_path, parent)

Funzione helper per verificare e aggiornare un database SQLite

**Parameters:**
- `db_path`
- `parent`

