# modules/utility/pyarchinit_tma_thesaurus_sync.py

## Overview

This file contains 52 documented elements.

## Classes

### TMAThesaurusSync

Classe per sincronizzare il thesaurus TMA con le altre tabelle.
Può essere usata sia come script standalone che integrata nell'applicazione.

#### Methods

##### __init__(self, db_manager)

Inizializza con il db_manager di PyArchInit

Args:
    db_manager: istanza di Pyarchinit_db_management

##### sync_settore_to_thesaurus(self, settore, sito, source_table)

Aggiunge un settore al thesaurus TMA se non esiste

Args:
    settore: nome del settore da aggiungere
    sito: nome del sito (opzionale)
    source_table: tabella di origine per tracking

##### sync_area_to_thesaurus(self, area, sito, source_table)

Aggiunge un'area al thesaurus TMA se non esiste

Args:
    area: nome dell'area da aggiungere
    sito: nome del sito (opzionale)
    source_table: tabella di origine per tracking

##### sync_material_value_to_thesaurus(self, value, field_type)

Aggiunge un valore di materiale al thesaurus TMA se non esiste

Args:
    value: valore da aggiungere
    field_type: tipo di campo ('Categoria', 'Classe', 'Precisazione tipologica', 'Definizione')

##### sync_from_inventory_materials(self, inventory_record)

Sincronizza i valori da un record di inventario_materiali_table al thesaurus TMA

Args:
    inventory_record: record dell'inventario materiali

##### get_thesaurus_values(self, field_type, sito, area)

Ottiene i valori del thesaurus per un determinato tipo di campo

Args:
    field_type: tipo di campo thesaurus
    sito: filtra per sito (opzionale)
    area: filtra per area (opzionale)
    
Returns:
    lista di valori del thesaurus

##### sync_tma_thesaurus_to_other_tables(self)

Sincronizza le aree predefinite del thesaurus TMA verso le altre tabelle
Copia le aree da TMA (10.7) verso US, Inventario Materiali, Tombe e Individui

##### sync_tma_materials_to_inventory(self)

Sincronizza i valori dei materiali dal thesaurus TMA verso inventario materiali

##### sync_all_areas_to_thesaurus(self)

Sincronizza tutte le aree da tutte le tabelle al thesaurus TMA

##### sync_all_settori_to_thesaurus(self)

Sincronizza tutti i settori da us_table e tma al thesaurus TMA

##### sync_all_inventory_to_thesaurus(self)

Sincronizza tutti i valori dall'inventario materiali al thesaurus TMA

### TMAThesaurusSync

Classe per sincronizzare il thesaurus TMA con le altre tabelle.
Può essere usata sia come script standalone che integrata nell'applicazione.

#### Methods

##### __init__(self, db_manager)

Inizializza con il db_manager di PyArchInit

Args:
    db_manager: istanza di Pyarchinit_db_management

##### sync_settore_to_thesaurus(self, settore, sito, source_table)

Aggiunge un settore al thesaurus TMA se non esiste

Args:
    settore: nome del settore da aggiungere
    sito: nome del sito (opzionale)
    source_table: tabella di origine per tracking

##### sync_area_to_thesaurus(self, area, sito, source_table)

Aggiunge un'area al thesaurus TMA se non esiste

Args:
    area: nome dell'area da aggiungere
    sito: nome del sito (opzionale)
    source_table: tabella di origine per tracking

##### sync_material_value_to_thesaurus(self, value, field_type)

Aggiunge un valore di materiale al thesaurus TMA se non esiste

Args:
    value: valore da aggiungere
    field_type: tipo di campo ('Categoria', 'Classe', 'Precisazione tipologica', 'Definizione')

##### sync_from_inventory_materials(self, inventory_record)

Sincronizza i valori da un record di inventario_materiali_table al thesaurus TMA

Args:
    inventory_record: record dell'inventario materiali

##### get_thesaurus_values(self, field_type, sito, area)

Ottiene i valori del thesaurus per un determinato tipo di campo

Args:
    field_type: tipo di campo thesaurus
    sito: filtra per sito (opzionale)
    area: filtra per area (opzionale)
    
Returns:
    lista di valori del thesaurus

##### sync_tma_thesaurus_to_other_tables(self)

Sincronizza le aree predefinite del thesaurus TMA verso le altre tabelle
Copia le aree da TMA (10.7) verso US, Inventario Materiali, Tombe e Individui

##### sync_tma_materials_to_inventory(self)

Sincronizza i valori dei materiali dal thesaurus TMA verso inventario materiali

##### sync_all_areas_to_thesaurus(self)

Sincronizza tutte le aree da tutte le tabelle al thesaurus TMA

##### sync_all_settori_to_thesaurus(self)

Sincronizza tutti i settori da us_table e tma al thesaurus TMA

##### sync_all_inventory_to_thesaurus(self)

Sincronizza tutti i valori dall'inventario materiali al thesaurus TMA

### TMAThesaurusSync

Classe per sincronizzare il thesaurus TMA con le altre tabelle.
Può essere usata sia come script standalone che integrata nell'applicazione.

#### Methods

##### __init__(self, db_manager)

Inizializza con il db_manager di PyArchInit

Args:
    db_manager: istanza di Pyarchinit_db_management

##### sync_settore_to_thesaurus(self, settore, sito, source_table)

Aggiunge un settore al thesaurus TMA se non esiste

Args:
    settore: nome del settore da aggiungere
    sito: nome del sito (opzionale)
    source_table: tabella di origine per tracking

##### sync_area_to_thesaurus(self, area, sito, source_table)

Aggiunge un'area al thesaurus TMA se non esiste

Args:
    area: nome dell'area da aggiungere
    sito: nome del sito (opzionale)
    source_table: tabella di origine per tracking

##### sync_material_value_to_thesaurus(self, value, field_type)

Aggiunge un valore di materiale al thesaurus TMA se non esiste

Args:
    value: valore da aggiungere
    field_type: tipo di campo ('Categoria', 'Classe', 'Precisazione tipologica', 'Definizione')

##### sync_from_inventory_materials(self, inventory_record)

Sincronizza i valori da un record di inventario_materiali_table al thesaurus TMA

Args:
    inventory_record: record dell'inventario materiali

##### get_thesaurus_values(self, field_type, sito, area)

Ottiene i valori del thesaurus per un determinato tipo di campo

Args:
    field_type: tipo di campo thesaurus
    sito: filtra per sito (opzionale)
    area: filtra per area (opzionale)
    
Returns:
    lista di valori del thesaurus

##### sync_tma_thesaurus_to_other_tables(self)

Sincronizza le aree predefinite del thesaurus TMA verso le altre tabelle
Copia le aree da TMA (10.7) verso US, Inventario Materiali, Tombe e Individui

##### sync_tma_materials_to_inventory(self)

Sincronizza i valori dei materiali dal thesaurus TMA verso inventario materiali

##### sync_all_areas_to_thesaurus(self)

Sincronizza tutte le aree da tutte le tabelle al thesaurus TMA

##### sync_all_settori_to_thesaurus(self)

Sincronizza tutti i settori da us_table e tma al thesaurus TMA

##### sync_all_inventory_to_thesaurus(self)

Sincronizza tutti i valori dall'inventario materiali al thesaurus TMA

### TMAThesaurusSync

Classe per sincronizzare il thesaurus TMA con le altre tabelle.
Può essere usata sia come script standalone che integrata nell'applicazione.

#### Methods

##### __init__(self, db_manager)

Inizializza con il db_manager di PyArchInit

Args:
    db_manager: istanza di Pyarchinit_db_management

##### sync_settore_to_thesaurus(self, settore, sito, source_table)

Aggiunge un settore al thesaurus TMA se non esiste

Args:
    settore: nome del settore da aggiungere
    sito: nome del sito (opzionale)
    source_table: tabella di origine per tracking

##### sync_area_to_thesaurus(self, area, sito, source_table)

Aggiunge un'area al thesaurus TMA se non esiste

Args:
    area: nome dell'area da aggiungere
    sito: nome del sito (opzionale)
    source_table: tabella di origine per tracking

##### sync_material_value_to_thesaurus(self, value, field_type)

Aggiunge un valore di materiale al thesaurus TMA se non esiste

Args:
    value: valore da aggiungere
    field_type: tipo di campo ('Categoria', 'Classe', 'Precisazione tipologica', 'Definizione')

##### sync_from_inventory_materials(self, inventory_record)

Sincronizza i valori da un record di inventario_materiali_table al thesaurus TMA

Args:
    inventory_record: record dell'inventario materiali

##### get_thesaurus_values(self, field_type, sito, area)

Ottiene i valori del thesaurus per un determinato tipo di campo

Args:
    field_type: tipo di campo thesaurus
    sito: filtra per sito (opzionale)
    area: filtra per area (opzionale)
    
Returns:
    lista di valori del thesaurus

##### sync_tma_thesaurus_to_other_tables(self)

Sincronizza le aree predefinite del thesaurus TMA verso le altre tabelle
Copia le aree da TMA (10.7) verso US, Inventario Materiali, Tombe e Individui

##### sync_tma_materials_to_inventory(self)

Sincronizza i valori dei materiali dal thesaurus TMA verso inventario materiali

##### sync_all_areas_to_thesaurus(self)

Sincronizza tutte le aree da tutte le tabelle al thesaurus TMA

##### sync_all_settori_to_thesaurus(self)

Sincronizza tutti i settori da us_table e tma al thesaurus TMA

##### sync_all_inventory_to_thesaurus(self)

Sincronizza tutti i valori dall'inventario materiali al thesaurus TMA

