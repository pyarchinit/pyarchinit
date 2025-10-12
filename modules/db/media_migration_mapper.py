#!/usr/bin/env python3
"""
Media Migration Mapper
Gestisce il mapping degli ID durante la migrazione dei dati per mantenere i collegamenti media
"""

class MediaMigrationMapper:
    """
    Classe per gestire il mapping degli ID durante la migrazione dei dati.
    Mantiene la relazione tra vecchi e nuovi ID per aggiornare correttamente
    i riferimenti nella tabella media_to_entity.
    """
    
    def __init__(self):
        """
        Inizializza i dizionari di mapping per ogni tabella che ha relazioni con i media
        """
        self.id_mappings = {
            'US': {},  # {old_id_us: new_id_us}
            'INVENTARIO_MATERIALI': {},  # {old_id_invmat: new_id_invmat}
            'STRUTTURA': {},  # {old_id_struttura: new_id_struttura}
            'POTTERY': {},  # {old_id_pottery: new_id_pottery}
            'TOMBA': {},  # {old_id_tomba: new_id_tomba}
            'TMA': {},  # {old_id: new_id}
            'MEDIA': {},  # {old_id_media: new_id_media}
        }
        
        # Mapping tra entity_type e nome tabella per la conversione
        self.entity_type_to_table = {
            'US': 'US',
            'REPERTO': 'INVENTARIO_MATERIALI',
            'STRUTTURA': 'STRUTTURA',
            'POTTERY': 'POTTERY',
            'TOMBA': 'TOMBA',
            'TMA': 'TMA'
        }
        
        # Mapping inverso per ottenere entity_type dal nome tabella
        self.table_to_entity_type = {
            'US': 'US',
            'INVENTARIO_MATERIALI': 'REPERTO',
            'STRUTTURA': 'STRUTTURA',
            'POTTERY': 'POTTERY',
            'TOMBA': 'TOMBA',
            'TMA': 'TMA'
        }
    
    def add_id_mapping(self, table_name, old_id, new_id):
        """
        Aggiunge un mapping tra vecchio e nuovo ID per una tabella specifica
        
        Args:
            table_name: Nome della tabella (es. 'US', 'INVENTARIO_MATERIALI')
            old_id: ID originale del record
            new_id: Nuovo ID assegnato durante la migrazione
        """
        if table_name in self.id_mappings:
            self.id_mappings[table_name][old_id] = new_id
    
    def get_new_id(self, table_name, old_id):
        """
        Ottiene il nuovo ID corrispondente a un vecchio ID
        
        Args:
            table_name: Nome della tabella
            old_id: ID originale
            
        Returns:
            Il nuovo ID se trovato, altrimenti None
        """
        return self.id_mappings.get(table_name, {}).get(old_id)
    
    def get_new_entity_id(self, entity_type, old_id):
        """
        Ottiene il nuovo ID per un entity_type specifico
        
        Args:
            entity_type: Tipo di entità (es. 'US', 'REPERTO')
            old_id: ID originale dell'entità
            
        Returns:
            Il nuovo ID se trovato, altrimenti l'ID originale
        """
        table_name = self.entity_type_to_table.get(entity_type, entity_type)
        new_id = self.get_new_id(table_name, old_id)
        return new_id if new_id is not None else old_id
    
    def get_new_media_id(self, old_media_id):
        """
        Ottiene il nuovo ID media corrispondente
        
        Args:
            old_media_id: ID originale del media
            
        Returns:
            Il nuovo ID media se trovato, altrimenti l'ID originale
        """
        new_id = self.get_new_id('MEDIA', old_media_id)
        return new_id if new_id is not None else old_media_id
    
    def update_mediatoentity_record(self, record):
        """
        Aggiorna un record MEDIATOENTITY con i nuovi ID
        
        Args:
            record: Record originale da aggiornare
            
        Returns:
            Dizionario con i valori aggiornati
        """
        # Ottieni il nuovo id_entity basato su entity_type
        new_id_entity = self.get_new_entity_id(record.entity_type, record.id_entity)
        
        # Ottieni il nuovo id_media
        new_id_media = self.get_new_media_id(record.id_media)
        
        # Ritorna i valori aggiornati
        return {
            'id_entity': new_id_entity,
            'entity_type': record.entity_type,
            'table_name': record.table_name,
            'id_media': new_id_media,
            'filepath': record.filepath,
            'media_name': record.media_name
        }
    
    def get_mapping_summary(self):
        """
        Ottiene un riepilogo dei mapping creati
        
        Returns:
            Dizionario con statistiche sui mapping
        """
        summary = {}
        for table, mappings in self.id_mappings.items():
            if mappings:
                summary[table] = {
                    'count': len(mappings),
                    'old_ids': list(mappings.keys()),
                    'new_ids': list(mappings.values())
                }
        return summary
    
    def clear_mappings(self):
        """
        Pulisce tutti i mapping memorizzati
        """
        for table in self.id_mappings:
            self.id_mappings[table].clear()