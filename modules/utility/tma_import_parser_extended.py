#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Estensione del parser esistente per supportare inventari cassette
"""

import os
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QTableWidget, 
                             QTableWidgetItem, QDialogButtonBox, QGroupBox, 
                             QFormLayout, QMessageBox)
from datetime import datetime

# Import del parser base
from .tma_import_parser import TMAImportManager, TMAFieldMapping, BaseParser

# Import del parser Festos se disponibile
try:
    from .festos_inventory_parser import FestosInventoryParser
    FESTOS_PARSER_AVAILABLE = True
except ImportError:
    FESTOS_PARSER_AVAILABLE = False

# Configurazione logging
logger = logging.getLogger(__name__)


class TMAImportManagerExtended(TMAImportManager):
    """Manager esteso che supporta inventari"""
    
    def __init__(self, db_manager):
        super().__init__(db_manager)
        self.db_manager = db_manager
        
    def import_file(self, file_path: str, custom_mapping: Dict[str, str] = None, 
                   use_festos_parser: bool = False) -> Tuple[int, List[str], List[str]]:
        """
        Override del metodo import_file per gestire inventari DOCX
        """
        # Determina il tipo di file
        _, ext = os.path.splitext(file_path.lower())
        
        # Se è un DOCX, controlla se è un inventario
        if ext == '.docx':
            try:
                from docx import Document
                doc = Document(file_path)
                text_content = '\n'.join([p.text for p in doc.paragraphs[:10]])
                
                # Se sembra un inventario O use_festos_parser è True, usa il parser inventario
                if use_festos_parser or any(word in text_content for word in ['Cassette', 'Magazzino', 'Magazzini']):
                    # Controlla se abbiamo il parser Festos disponibile
                    if FESTOS_PARSER_AVAILABLE:
                        # Usa FestosInventoryParser
                        festos_parser = FestosInventoryParser()
                        records, errors, warnings = festos_parser.parse_file(file_path)
                        
                        # Se ci sono errori di parsing, ritorna subito
                        if errors and not records:
                            return 0, errors, warnings
                    else:
                        # Fallback: usa il parser base con validazione meno restrittiva
                        return super().import_file(file_path, custom_mapping, False)
                    
                    # Applica mapping personalizzato se fornito
                    if custom_mapping:
                        original_mappings = TMAFieldMapping.FIELD_MAPPINGS.copy()
                        TMAFieldMapping.FIELD_MAPPINGS.update(custom_mapping)
                    
                    logger.info(f"Usando parser inventario per: {file_path}")
                    logger.info(f"Record trovati: {len(records)}")
                    
                    # Ripristina mapping originale
                    if custom_mapping:
                        TMAFieldMapping.FIELD_MAPPINGS = original_mappings
                    
                    # Importa i record nel database
                    imported_count = 0
                    import_errors = []
                    
                    for idx, record in enumerate(records):
                        try:
                            # Import usando il metodo del db_manager - nuova struttura con 26 campi
                            tma_id = self.db_manager.max_num_id('TMA', 'id') + 1
                            
                            data = self.db_manager.insert_tma_values(
                                tma_id,
                                record.get('sito', ''),
                                record.get('area', ''),
                                record.get('ogtm', ''),
                                record.get('ldct', ''),
                                record.get('ldcn', ''),
                                record.get('vecchia_collocazione', ''),
                                record.get('cassetta', ''),
                                record.get('localita', ''),
                                record.get('scan', ''),
                                record.get('saggio', ''),
                                record.get('vano_locus', ''),
                                record.get('dscd', ''),
                                record.get('dscu', ''),
                                record.get('rcgd', ''),
                                record.get('rcgz', ''),
                                record.get('aint', ''),
                                record.get('aind', ''),
                                record.get('dtzg', ''),  # Usa solo dtzg, non dtzs
                                record.get('deso', ''),
                                '',  # nsc - campo note storico-critiche
                                record.get('ftap', ''),
                                record.get('ftan', ''),
                                record.get('drat', ''),
                                record.get('dran', ''),
                                record.get('draa', '')
                            )
                            
                            self.db_manager.insert_data_session(data)
                            
                            # Ora salva i materiali separatamente se presenti
                            materials_to_save = []
                            
                            # Se abbiamo dati di materiali, crea record nella tabella materiali
                            if any([record.get('madi'), record.get('macc'), record.get('macl'), 
                                   record.get('macp'), record.get('macd'), record.get('cronologia_mac'), 
                                   record.get('macq'), record.get('peso')]):
                                
                                # Converti peso a float se presente
                                peso = None
                                if record.get('peso'):
                                    try:
                                        peso = float(record.get('peso'))
                                    except (ValueError, TypeError):
                                        peso = None
                                
                                material_data = self.db_manager.insert_tma_materiali_values(
                                    self.db_manager.max_num_id('TMA_MATERIALI', 'id') + 1,
                                    tma_id,
                                    record.get('madi', ''),
                                    record.get('macc', ''),
                                    record.get('macl', ''),
                                    record.get('macp', ''),
                                    record.get('macd', ''),
                                    record.get('cronologia_mac', ''),
                                    record.get('macq', ''),
                                    peso
                                )
                                self.db_manager.insert_data_session(material_data)
                            
                            imported_count += 1
                            
                        except Exception as e:
                            import_errors.append(f"Errore importazione record {idx + 1}: {str(e)}")
                    
                    logger.info(f"Importati {imported_count} record su {len(records)}")
                    
                    # Aggiungi messaggio di successo se necessario
                    if imported_count > 0:
                        warnings.append(f"{imported_count} record importati con successo")
                    
                    return imported_count, import_errors + errors, warnings
                    
            except Exception as e:
                logger.warning(f"Errore controllo inventario: {e}")
        
        # Per tutti gli altri casi, usa il metodo parent
        return super().import_file(file_path, custom_mapping, use_festos_parser)
