# modules/db/media_migration_mapper.py

## Overview

This file contains 10 documented elements.

## Classes

### MediaMigrationMapper

Classe per gestire il mapping degli ID durante la migrazione dei dati.
Mantiene la relazione tra vecchi e nuovi ID per aggiornare correttamente
i riferimenti nella tabella media_to_entity.

#### Methods

##### __init__(self)

Inizializza i dizionari di mapping per ogni tabella che ha relazioni con i media

##### add_id_mapping(self, table_name, old_id, new_id)

Aggiunge un mapping tra vecchio e nuovo ID per una tabella specifica

Args:
    table_name: Nome della tabella (es. 'US', 'INVENTARIO_MATERIALI')
    old_id: ID originale del record
    new_id: Nuovo ID assegnato durante la migrazione

##### get_new_id(self, table_name, old_id)

Ottiene il nuovo ID corrispondente a un vecchio ID

Args:
    table_name: Nome della tabella
    old_id: ID originale
    
Returns:
    Il nuovo ID se trovato, altrimenti None

##### get_new_entity_id(self, entity_type, old_id)

Ottiene il nuovo ID per un entity_type specifico

Args:
    entity_type: Tipo di entità (es. 'US', 'REPERTO')
    old_id: ID originale dell'entità
    
Returns:
    Il nuovo ID se trovato, altrimenti l'ID originale

##### get_new_media_id(self, old_media_id)

Ottiene il nuovo ID media corrispondente

Args:
    old_media_id: ID originale del media
    
Returns:
    Il nuovo ID media se trovato, altrimenti l'ID originale

##### update_mediatoentity_record(self, record)

Aggiorna un record MEDIATOENTITY con i nuovi ID

Args:
    record: Record originale da aggiornare
    
Returns:
    Dizionario con i valori aggiornati

##### get_mapping_summary(self)

Ottiene un riepilogo dei mapping creati

Returns:
    Dizionario con statistiche sui mapping

##### clear_mappings(self)

Pulisce tutti i mapping memorizzati

