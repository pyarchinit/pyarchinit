# modules/db/postgres_db_updater.py

## Overview

This file contains 36 documented elements.

## Classes

### PostgresDbUpdater

`PostgresDbUpdater` manages schema migrations and database maintenance for a PostgreSQL backend used by the PyArchInit QGIS plugin. It provides methods to create missing tables, add missing columns to existing tables, recreate or update database views, seed thesaurus entries for multiple archaeological data domains and languages, install PostgreSQL functions and event triggers for automatic GRANT synchronization, and create performance indexes. Migrations are split into lightweight essential operations executed on every connection and heavier optional operations intended for explicit user-initiated updates.

#### Methods

##### __init__(self, db_manager, parent)

Inizializza l'updater per PostgreSQL

Args:
    db_manager: istanza di Pyarchinit_db_management
    parent: widget parent per i messaggi (opzionale)

##### log_message(self, message, level)

Log dei messaggi tramite QgsMessageLog

##### run_essential_migrations(self)

Esegue migrazioni essenziali (leggere) necessarie per evitare errori.
Questa funzione è pensata per essere veloce e sicura da eseguire ad ogni connessione.

##### check_and_update_database(self)

Controlla e aggiorna il database PostgreSQL

##### column_exists(self, table_name, column_name)

Verifica se una colonna esiste nella tabella

##### add_column_if_missing(self, table_name, column_name, column_type, default_value)

Aggiunge una colonna se non esiste

##### get_column_position(self, table_name, column_name)

Restituisce la posizione ordinale di una colonna

##### reorder_pottery_datazione_column(self)

Riordina la colonna datazione nella pottery_table se si trova dopo i campi audit.
La colonna datazione deve essere in posizione 36 (dopo decoration_position e prima di editing_by).

##### update_thesaurus_table(self)

Aggiorna la tabella pyarchinit_thesaurus_sigle

##### update_reperti_table(self)

Aggiorna la tabella pyarchinit_reperti

##### update_us_view(self)

Crea o aggiorna la view pyarchinit_us_view - gestisce colonne mancanti

##### update_usm_view(self)

Crea o aggiorna la view pyarchinit_usm_view - gestisce colonne mancanti

##### update_activity_triggers(self)

Installa/aggiorna i trigger per il tracking delle attività

##### update_pottery_table(self)

Aggiorna la tabella pottery_table con i nuovi campi decorazione

##### update_pottery_thesaurus(self)

Installa/aggiorna le voci thesaurus per la tabella Pottery

##### install_grant_sync_functions(self)

Installa le funzioni e l'event trigger per la sincronizzazione automatica dei GRANT.
Quando una tabella viene ricreata (DROP + CREATE), i permessi GRANT vengono
automaticamente ripristinati dalla tabella pyarchinit_permissions.

##### update_inventario_materiali_table(self)

Aggiorna la tabella inventario_materiali_table con colonne mancanti

##### update_struttura_table(self)

Aggiorna la tabella struttura_table con i nuovi campi Architettura Rupestre (AR)

##### update_ut_table(self)

Aggiorna la tabella ut_table con i nuovi campi analisi (v4.9.67+)

##### update_strutture_view(self)

Aggiorna/ricrea la view pyarchinit_strutture_view con i nuovi campi AR

##### table_exists(self, table_name)

Verifica se una tabella esiste nel database

##### update_fauna_table(self)

Crea fauna_table se non esiste (v4.9.21+)

##### update_fauna_thesaurus(self)

Installa/aggiorna le voci thesaurus per la tabella fauna_table (v4.9.21+)

##### update_ut_thesaurus(self)

Installa/aggiorna le voci thesaurus per la tabella ut_table in tutte le 7 lingue supportate (v4.9.68+)

##### update_site_management_thesaurus(self)

Seed thesaurus entries for site management (cantiere) tables.
7 codes (14.1-14.7) × 10 languages.

##### fix_thesaurus_nome_tabella(self)

Fix thesaurus entries that have display names instead of actual table names.

This migration fixes a bug where the Thesaurus form was saving entries with
display names (e.g., 'Fauna') instead of actual table names (e.g., 'fauna_table').
Forms query using actual table names, so entries with display names were not found.

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

Crea inventario_lapidei_table se non esiste (richiesta dai SQL di concorrenza)

## Functions

### check_and_update_postgres_db(db_manager, parent)

Funzione di utilità per controllare e aggiornare un database PostgreSQL

Args:
    db_manager: istanza di Pyarchinit_db_management
    parent: widget parent per i messaggi (opzionale)

Returns:
    bool: True se l'aggiornamento è riuscito, False altrimenti

**Parameters:**
- `db_manager`
- `parent`

