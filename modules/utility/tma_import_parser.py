#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TMA Import Parser
Parser modulare per importare dati da vari formati nel database TMA
"""

import os
import csv
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import re
from abc import ABC, abstractmethod
import openpyxl
import xml.etree.ElementTree as ET
from docx import Document
import PyPDF2
import logging

# Import del parser Festos se disponibile
try:
    from modules.utility.festos_inventory_parser import FestosInventoryParser
    FESTOS_PARSER_AVAILABLE = True
except ImportError:
    FESTOS_PARSER_AVAILABLE = False

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TMAFieldMapping:
    """Mappatura dei campi tra vari formati e il database TMA"""

    # Mapping generico dei campi - può essere personalizzato per ogni formato
    FIELD_MAPPINGS = {
        # Campi base
        'sito': ['sito', 'site', 'scavo', 'excavation', 'cantiere', 'dslgt'],
        'area': ['area', 'settore', 'sector', 'zona'],
        'dscu': ['us', 'unita_stratigrafica', 'stratigraphic_unit', 'su', 'dscu'],

        # Materiale
        'ogtm': ['materiale', 'material', 'tipo_materiale', 'material_type', 'ogtm', 'categoria_materiale'],

        # Collocazione
        'ldct': ['tipo_collocazione', 'location_type', 'tipologia_collocazione', 'ldct'],
        'ldcn': ['denominazione_collocazione', 'location_name', 'collocazione', 'ldcn'],
        'vecchia_collocazione': ['vecchia_collocazione', 'old_location', 'collocazione_precedente'],
        'cassetta': ['cassetta', 'box', 'contenitore', 'cassa'],
        'num_cassetta': ['num_cassetta', 'numero_cassetta', 'n_cassetta', 'cassette'],
        'magazzino': ['magazzino', 'magazine', 'deposito', 'storage'],
        'settore': ['settore', 'sector', 'area_scavo', 'prefisso'],

        # Localizzazione
        'localita': ['localita', 'locality', 'luogo', 'comune'],
        'scan': ['denominazione_scavo', 'excavation_name', 'nome_scavo', 'scan'],
        'saggio': ['saggio', 'trench', 'trincea'],
        'vano_locus': ['vano', 'locus', 'ambiente', 'room'],
        'dscd': ['data_scavo', 'excavation_date', 'data_rinvenimento', 'dscd'],

        # Ricognizione
        'rcgd': ['data_ricognizione', 'survey_date', 'rcgd'],
        'rcgz': ['specifiche_ricognizione', 'survey_notes', 'note_ricognizione', 'rcgz'],
        'aint': ['tipo_acquisizione', 'acquisition_type', 'modalita_acquisizione', 'aint'],
        'aind': ['data_acquisizione', 'acquisition_date', 'aind'],

        # Datazione
        'dtzg': ['fascia_cronologica', 'chronological_period', 'periodo', 'cronologia', 'dtzg'],
        'dtzs': ['frazione_cronologica', 'chronological_fraction', 'sottofase', 'dtzs'],
        'cronologie': ['cronologie', 'chronologies', 'datazione'],
        'anni_scavo': ['anni_scavo', 'anno_scavo', 'anno', 'year', 'campagna'],

        # Quantità
        'n_reperti': ['numero_reperti', 'number_finds', 'quantita', 'n_frammenti'],
        'peso': ['peso', 'weight', 'peso_gr', 'peso_kg'],

        # Descrizione
        'deso': ['descrizione', 'description', 'indicazione_oggetti', 'deso'],
        'dsogt': ['descrizione_oggetto', 'object_description', 'descrizione_materiale', 'dsogt'],

        # Inventario
        'madi': ['inventario', 'inventory', 'numero_inventario', 'madi'],
        'macc': ['categoria', 'category', 'classe_materiale', 'macc'],
        'macl': ['classe', 'class', 'sottoclasse', 'macl'],
        'macp': ['precisazione_tipologica', 'typological_precision', 'tipo', 'macp'],
        'macd': ['definizione', 'definition', 'forma', 'macd'],
        'cronologia_mac': ['cronologia_mac', 'mac_chronology', 'datazione_mac'],
        'macq': ['quantita_mac', 'mac_quantity', 'macq'],

        # Documentazione
        'ftap': ['tipo_foto', 'photo_type', 'tipologia_foto', 'ftap'],
        'ftan': ['codice_foto', 'photo_code', 'numero_foto', 'ftan'],
        'drat': ['tipo_disegno', 'drawing_type', 'tipologia_disegno', 'drat'],
        'dran': ['codice_disegno', 'drawing_code', 'numero_disegno', 'dran'],
        'draa': ['autore_disegno', 'drawing_author', 'disegnatore', 'draa'],
        
        # Altri campi
        'riferimenti': ['riferimenti', 'references', 'note', 'notes'],
        'data_schedatura': ['data_schedatura', 'cataloging_date', 'data_catalogazione']
    }

    # Valori validi per campi con vocabolario controllato
    VALID_VALUES = {
        'ogtm': ['CERAMICA', 'INDUSTRIA LITICA', 'LITICA', 'METALLO'],
        'ldct': ['Magazzino', 'Materiali all\'aperto', 'Museo']
    }

    @classmethod
    def find_field_mapping(cls, field_name: str) -> Optional[str]:
        """Trova il campo del database corrispondente a un nome di campo del file"""
        field_name_lower = field_name.lower().strip()

        for db_field, aliases in cls.FIELD_MAPPINGS.items():
            if field_name_lower in [alias.lower() for alias in aliases]:
                return db_field

        return None

    @classmethod
    def validate_field_value(cls, field: str, value: Any) -> Tuple[bool, Optional[str]]:
        """Valida il valore di un campo specifico"""
        if field in cls.VALID_VALUES:
            if value and value.upper() not in cls.VALID_VALUES[field]:
                return False, f"Valore '{value}' non valido per campo {field}. Valori accettati: {', '.join(cls.VALID_VALUES[field])}"

        # Validazioni specifiche per tipo di campo
        if field in ['dscd', 'rcgd', 'aind']:  # Campi data
            # Qui si potrebbe aggiungere validazione formato data
            pass

        if field in ['n_reperti', 'peso', 'macq']:  # Campi numerici
            if value and not str(value).replace('.', '').replace(',', '').isdigit():
                return False, f"Il campo {field} deve contenere un valore numerico"

        return True, None


class BaseParser(ABC):
    """Classe base astratta per i parser"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.errors = []
        self.warnings = []
        self.data = []

    @abstractmethod
    def parse(self) -> List[Dict[str, Any]]:
        """Metodo astratto per il parsing del file"""
        pass

    def validate_required_fields(self, record: Dict[str, Any]) -> bool:
        """Valida i campi obbligatori"""
        required_fields = ['sito', 'area', 'dscu', 'ogtm', 'ldcn', 'cassetta', 'localita', 'dtzg', 'macc']

        for field in required_fields:
            if field not in record or not record[field]:
                self.errors.append(f"Campo obbligatorio mancante: {field}")
                return False

        return True

    def clean_value(self, value: Any) -> str:
        """Pulisce e normalizza i valori"""
        if value is None:
            return ''

        # Converti in stringa e rimuovi spazi
        value_str = str(value).strip()

        # Rimuovi caratteri speciali problematici
        value_str = value_str.replace('\n', ' ').replace('\r', ' ')
        value_str = re.sub(r'\s+', ' ', value_str)

        return value_str


class ExcelParser(BaseParser):
    """Parser per file Excel"""

    def parse(self) -> List[Dict[str, Any]]:
        """Parsing di file Excel"""
        try:
            # Leggi il file Excel
            df = pd.read_excel(self.file_path)
            logger.info(f"Letto file Excel con {len(df)} righe")

            # Mappa le colonne
            column_mapping = {}
            for col in df.columns:
                db_field = TMAFieldMapping.find_field_mapping(col)
                if db_field:
                    column_mapping[col] = db_field
                else:
                    self.warnings.append(f"Colonna '{col}' non mappata")

            # Converti ogni riga
            for idx, row in df.iterrows():
                record = {}

                for excel_col, db_field in column_mapping.items():
                    value = self.clean_value(row.get(excel_col))

                    # Valida il valore
                    is_valid, error_msg = TMAFieldMapping.validate_field_value(db_field, value)
                    if not is_valid:
                        self.warnings.append(f"Riga {idx + 2}: {error_msg}")

                    record[db_field] = value

                # Aggiungi campi mancanti come vuoti
                for field in TMAFieldMapping.FIELD_MAPPINGS.keys():
                    if field not in record:
                        record[field] = ''

                # Valida campi obbligatori
                if self.validate_required_fields(record):
                    self.data.append(record)
                else:
                    self.errors.append(f"Riga {idx + 2} scartata per campi obbligatori mancanti")

            return self.data

        except Exception as e:
            self.errors.append(f"Errore parsing Excel: {str(e)}")
            return []


class CSVParser(BaseParser):
    """Parser per file CSV"""

    def __init__(self, file_path: str, delimiter: str = ',', encoding: str = 'utf-8'):
        super().__init__(file_path)
        self.delimiter = delimiter
        self.encoding = encoding

    def parse(self) -> List[Dict[str, Any]]:
        """Parsing di file CSV"""
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as file:
                # Prova a rilevare il dialetto CSV
                sample = file.read(1024)
                file.seek(0)

                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample)

                reader = csv.DictReader(file, delimiter=self.delimiter or dialect.delimiter)

                # Mappa le colonne
                column_mapping = {}
                for col in reader.fieldnames:
                    db_field = TMAFieldMapping.find_field_mapping(col)
                    if db_field:
                        column_mapping[col] = db_field
                    else:
                        self.warnings.append(f"Colonna '{col}' non mappata")

                # Converti ogni riga
                for idx, row in enumerate(reader):
                    record = {}

                    for csv_col, db_field in column_mapping.items():
                        value = self.clean_value(row.get(csv_col))

                        # Valida il valore
                        is_valid, error_msg = TMAFieldMapping.validate_field_value(db_field, value)
                        if not is_valid:
                            self.warnings.append(f"Riga {idx + 2}: {error_msg}")

                        record[db_field] = value

                    # Aggiungi campi mancanti come vuoti
                    for field in TMAFieldMapping.FIELD_MAPPINGS.keys():
                        if field not in record:
                            record[field] = ''

                    # Valida campi obbligatori
                    if self.validate_required_fields(record):
                        self.data.append(record)
                    else:
                        self.errors.append(f"Riga {idx + 2} scartata per campi obbligatori mancanti")

                return self.data

        except Exception as e:
            self.errors.append(f"Errore parsing CSV: {str(e)}")
            return []


class JSONParser(BaseParser):
    """Parser per file JSON"""

    def parse(self) -> List[Dict[str, Any]]:
        """Parsing di file JSON"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)

            # Gestisci sia array che oggetto singolo
            if isinstance(json_data, dict):
                json_data = [json_data]
            elif not isinstance(json_data, list):
                self.errors.append("Formato JSON non valido: deve essere un oggetto o un array")
                return []

            # Processa ogni record
            for idx, item in enumerate(json_data):
                record = {}

                for json_field, value in item.items():
                    db_field = TMAFieldMapping.find_field_mapping(json_field)
                    if db_field:
                        clean_value = self.clean_value(value)

                        # Valida il valore
                        is_valid, error_msg = TMAFieldMapping.validate_field_value(db_field, clean_value)
                        if not is_valid:
                            self.warnings.append(f"Record {idx + 1}: {error_msg}")

                        record[db_field] = clean_value
                    else:
                        self.warnings.append(f"Campo JSON '{json_field}' non mappato")

                # Aggiungi campi mancanti come vuoti
                for field in TMAFieldMapping.FIELD_MAPPINGS.keys():
                    if field not in record:
                        record[field] = ''

                # Valida campi obbligatori
                if self.validate_required_fields(record):
                    self.data.append(record)
                else:
                    self.errors.append(f"Record {idx + 1} scartato per campi obbligatori mancanti")

            return self.data

        except Exception as e:
            self.errors.append(f"Errore parsing JSON: {str(e)}")
            return []


class XMLParser(BaseParser):
    """Parser per file XML"""

    def parse(self) -> List[Dict[str, Any]]:
        """Parsing di file XML"""
        try:
            tree = ET.parse(self.file_path)
            root = tree.getroot()

            # Trova tutti gli elementi record (potrebbero avere nomi diversi)
            records = root.findall('.//record') or root.findall('.//scheda') or root.findall('.//item')

            if not records and root.tag in ['record', 'scheda', 'item']:
                records = [root]

            # Processa ogni record
            for idx, record_elem in enumerate(records):
                record = {}

                # Estrai tutti i campi dal record
                for elem in record_elem:
                    db_field = TMAFieldMapping.find_field_mapping(elem.tag)
                    if db_field:
                        value = self.clean_value(elem.text)

                        # Valida il valore
                        is_valid, error_msg = TMAFieldMapping.validate_field_value(db_field, value)
                        if not is_valid:
                            self.warnings.append(f"Record {idx + 1}: {error_msg}")

                        record[db_field] = value
                    else:
                        self.warnings.append(f"Tag XML '{elem.tag}' non mappato")

                # Controlla anche gli attributi
                for attr_name, attr_value in record_elem.attrib.items():
                    db_field = TMAFieldMapping.find_field_mapping(attr_name)
                    if db_field and db_field not in record:
                        record[db_field] = self.clean_value(attr_value)

                # Aggiungi campi mancanti come vuoti
                for field in TMAFieldMapping.FIELD_MAPPINGS.keys():
                    if field not in record:
                        record[field] = ''

                # Valida campi obbligatori
                if self.validate_required_fields(record):
                    self.data.append(record)
                else:
                    self.errors.append(f"Record {idx + 1} scartato per campi obbligatori mancanti")

            return self.data

        except Exception as e:
            self.errors.append(f"Errore parsing XML: {str(e)}")
            return []


class DOCXParser(BaseParser):
    """Parser per file DOCX"""

    def __init__(self, file_path: str, use_festos_parser: bool = False, db_session=None):
        super().__init__(file_path)
        self.use_festos_parser = use_festos_parser
        self.db_session = db_session

    def parse(self) -> List[Dict[str, Any]]:
        """Parsing di file DOCX"""
        # Se è un file Festos e abbiamo il parser specifico
        if self.use_festos_parser and FESTOS_PARSER_AVAILABLE and self.db_session:
            try:
                parser = FestosInventoryParser(self.db_session)
                success_count, errors, warnings = parser.parse_file(self.file_path)
                
                self.errors = errors
                self.warnings = warnings
                
                # Il FestosInventoryParser salva direttamente nel DB,
                # quindi ritorniamo una lista vuota
                return []
                
            except Exception as e:
                self.errors.append(f"Errore usando FestosInventoryParser: {str(e)}")
                # Fallback al parser generico
        
        # Parser generico per DOCX
        try:
            doc = Document(self.file_path)
            
            # Cerca tabelle nel documento
            all_data = []
            
            for table in doc.tables:
                # Assumi che la prima riga sia l'header
                if len(table.rows) < 2:
                    continue
                    
                headers = [cell.text.strip() for cell in table.rows[0].cells]
                
                # Mappa le colonne
                column_mapping = {}
                for col in headers:
                    db_field = TMAFieldMapping.find_field_mapping(col)
                    if db_field:
                        column_mapping[col] = db_field
                    else:
                        self.warnings.append(f"Colonna '{col}' non mappata")
                
                # Processa le righe
                for row_idx, row in enumerate(table.rows[1:], start=2):
                    record = {}
                    
                    for col_idx, cell in enumerate(row.cells):
                        if col_idx < len(headers):
                            header = headers[col_idx]
                            if header in column_mapping:
                                value = self.clean_value(cell.text)
                                db_field = column_mapping[header]
                                
                                # Valida il valore
                                is_valid, error_msg = TMAFieldMapping.validate_field_value(db_field, value)
                                if not is_valid:
                                    self.warnings.append(f"Tabella {len(all_data)+1}, Riga {row_idx}: {error_msg}")
                                
                                record[db_field] = value
                    
                    # Aggiungi campi mancanti come vuoti
                    for field in TMAFieldMapping.FIELD_MAPPINGS.keys():
                        if field not in record:
                            record[field] = ''
                    
                    # Valida campi obbligatori
                    if self.validate_required_fields(record):
                        all_data.append(record)
                    else:
                        self.errors.append(f"Tabella {len(all_data)+1}, Riga {row_idx} scartata per campi obbligatori mancanti")
            
            self.data = all_data
            return self.data
            
        except Exception as e:
            self.errors.append(f"Errore parsing DOCX: {str(e)}")
            return []


class TMAImportManager:
    """Manager principale per l'importazione dei dati TMA"""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.parsers = {
            '.xlsx': ExcelParser,
            '.xls': ExcelParser,
            '.csv': CSVParser,
            '.json': JSONParser,
            '.xml': XMLParser,
            '.docx': DOCXParser
        }

    def import_file(self, file_path: str, custom_mapping: Dict[str, str] = None, 
                   use_festos_parser: bool = False) -> Tuple[int, List[str], List[str]]:
        """
        Importa un file nel database TMA
        
        Args:
            file_path: percorso del file da importare
            custom_mapping: mapping personalizzato dei campi (opzionale)
            use_festos_parser: usa il parser specifico per Festos (per file DOCX)
        
        Returns:
            Tuple con (numero record importati, lista errori, lista warning)
        """
        # Determina il tipo di file
        _, ext = os.path.splitext(file_path.lower())

        if ext not in self.parsers:
            return 0, [f"Formato file {ext} non supportato"], []

        # Crea il parser appropriato
        parser_class = self.parsers[ext]
        
        # Per file DOCX, passa i parametri aggiuntivi se necessario
        if ext == '.docx' and use_festos_parser:
            parser = parser_class(file_path, use_festos_parser=True, 
                                db_session=getattr(self.db_manager, 'session', None))
        else:
            parser = parser_class(file_path)

        # Applica mapping personalizzato se fornito
        if custom_mapping:
            # Crea una copia per non modificare il mapping globale
            original_mappings = TMAFieldMapping.FIELD_MAPPINGS.copy()
            TMAFieldMapping.FIELD_MAPPINGS.update(custom_mapping)

        # Esegui il parsing
        logger.info(f"Inizio parsing file: {file_path}")
        records = parser.parse()

        # Ripristina mapping originale se era stato modificato
        if custom_mapping:
            TMAFieldMapping.FIELD_MAPPINGS = original_mappings

        if parser.errors:
            logger.error(f"Errori durante il parsing: {parser.errors}")
            return 0, parser.errors, parser.warnings

        # Se il parser Festos ha già salvato i dati, ritorna il conteggio
        if ext == '.docx' and use_festos_parser and not records:
            # Estrai il numero di record importati dai messaggi
            imported_count = 0
            for warning in parser.warnings:
                if "importati con successo" in warning:
                    match = re.search(r'(\d+) record', warning)
                    if match:
                        imported_count = int(match.group(1))
            return imported_count, parser.errors, parser.warnings

        # Importa i record nel database
        imported_count = 0
        import_errors = []

        for idx, record in enumerate(records):
            try:
                # Prepara i dati per l'inserimento - nuova struttura con 26 campi
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
                    record.get('dscu', ''),  # dscu = US
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

        return imported_count, import_errors + parser.errors, parser.warnings

    def import_batch(self, file_paths: List[str]) -> Dict[str, Any]:
        """Importa multipli file in batch"""
        results = {
            'total_imported': 0,
            'file_results': {}
        }

        for file_path in file_paths:
            imported, errors, warnings = self.import_file(file_path)

            results['total_imported'] += imported
            results['file_results'][file_path] = {
                'imported': imported,
                'errors': errors,
                'warnings': warnings
            }

        return results


# Esempio di utilizzo
if __name__ == "__main__":
    # Test del sistema di mapping
    test_fields = ['Materiale', 'US', 'numero_inventario', 'PESO_GR']

    for field in test_fields:
        mapped = TMAFieldMapping.find_field_mapping(field)
        print(f"{field} -> {mapped}")
