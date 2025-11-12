# scripts/sync_tma_thesaurus.py

## Overview

This file contains 30 documented elements.

## Classes

### TMAThesaurusSync

Classe per sincronizzare il thesaurus TMA con le altre tabelle

#### Methods

##### __init__(self)

Inizializza la connessione al database

##### get_tma_areas(self)

Ottiene tutte le aree uniche dal thesaurus TMA

##### get_tma_settori(self)

Ottiene tutti i settori unici dal thesaurus TMA

##### sync_areas_to_tables(self)

Sincronizza le aree del thesaurus TMA con le altre tabelle

##### sync_settori_to_tables(self)

Sincronizza i settori dal us_table e tma al thesaurus TMA

##### sync_material_fields(self)

Sincronizza i campi dei materiali tra tma_materiali_ripetibili e inventario_materiali_table

##### create_sync_trigger(self)

Crea trigger per sincronizzazione automatica (solo per SQLite)

##### run_full_sync(self)

Esegue la sincronizzazione completa

### TMAThesaurusSync

Classe per sincronizzare il thesaurus TMA con le altre tabelle

#### Methods

##### __init__(self)

Inizializza la connessione al database

##### get_tma_areas(self)

Ottiene tutte le aree uniche dal thesaurus TMA

##### get_tma_settori(self)

Ottiene tutti i settori unici dal thesaurus TMA

##### sync_areas_to_tables(self)

Sincronizza le aree del thesaurus TMA con le altre tabelle

##### sync_settori_to_tables(self)

Sincronizza i settori dal us_table e tma al thesaurus TMA

##### sync_material_fields(self)

Sincronizza i campi dei materiali tra tma_materiali_ripetibili e inventario_materiali_table

##### create_sync_trigger(self)

Crea trigger per sincronizzazione automatica (solo per SQLite)

##### run_full_sync(self)

Esegue la sincronizzazione completa

### TMAThesaurusSync

Classe per sincronizzare il thesaurus TMA con le altre tabelle

#### Methods

##### __init__(self)

Inizializza la connessione al database

##### get_tma_areas(self)

Ottiene tutte le aree uniche dal thesaurus TMA

##### get_tma_settori(self)

Ottiene tutti i settori unici dal thesaurus TMA

##### sync_areas_to_tables(self)

Sincronizza le aree del thesaurus TMA con le altre tabelle

##### sync_settori_to_tables(self)

Sincronizza i settori dal us_table e tma al thesaurus TMA

##### sync_material_fields(self)

Sincronizza i campi dei materiali tra tma_materiali_ripetibili e inventario_materiali_table

##### create_sync_trigger(self)

Crea trigger per sincronizzazione automatica (solo per SQLite)

##### run_full_sync(self)

Esegue la sincronizzazione completa

