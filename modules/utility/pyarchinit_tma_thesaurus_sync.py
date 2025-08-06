#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi; Enzo Cocca <enzo.ccc@gmail.com>
    email                : mandoluca at gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from sqlalchemy import text
from qgis.core import QgsMessageLog, Qgis


class TMAThesaurusSync:
    """
    Classe per sincronizzare il thesaurus TMA con le altre tabelle.
    Può essere usata sia come script standalone che integrata nell'applicazione.
    """
    
    def __init__(self, db_manager):
        """
        Inizializza con il db_manager di PyArchInit
        
        Args:
            db_manager: istanza di Pyarchinit_db_management
        """
        self.db_manager = db_manager
        self.engine = db_manager.engine
        
    def sync_settore_to_thesaurus(self, settore, sito=None, source_table=None):
        """
        Aggiunge un settore al thesaurus TMA se non esiste
        
        Args:
            settore: nome del settore da aggiungere
            sito: nome del sito (opzionale)
            source_table: tabella di origine per tracking
        """
        if not settore:
            return
            
        try:
            session = self.engine.connect()
            
            # Determina il codice tipologia_sigla e nome_tabella corretti in base alla tabella di origine
            table_config = {
                'us_table': {
                    'tipologia_sigla': '2.21',
                    'nome_tabella': 'US'
                },
                'tma_materiali_archeologici': {
                    'tipologia_sigla': '10.15',
                    'nome_tabella': 'TMA materiali archeologici'
                }
            }
            
            # Ottieni configurazione per questa tabella
            config = table_config.get(source_table, {
                'tipologia_sigla': '10.15',
                'nome_tabella': 'TMA materiali archeologici'
            })
            
            tipologia_sigla = config['tipologia_sigla']
            nome_tabella = config['nome_tabella']
            
            # Verifica se il settore esiste già nel thesaurus confrontando sigla, sigla_estesa e descrizione
            check_query = text("""
                SELECT id_thesaurus_sigle, sigla, sigla_estesa, descrizione 
                FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = :nome_tabella
                AND tipologia_sigla = :tipologia
                AND sigla = :settore
            """)
            
            result = session.execute(check_query, {
                "nome_tabella": nome_tabella,
                "tipologia": tipologia_sigla,
                "settore": str(settore)
            })
            existing = result.fetchone()
            
            if not existing:
                # Aggiungi il settore al thesaurus
                sigla_estesa = f"Settore {settore}"
                if sito:
                    sigla_estesa = f"{sito} - Settore {settore}"
                    
                # Prepara descrizione con source tracking
                descrizione = ""
                if source_table:
                    descrizione = f"Sincronizzato da {source_table}"
                    
                insert_query = text("""
                    INSERT INTO pyarchinit_thesaurus_sigle 
                    (nome_tabella, tipologia_sigla, sigla_estesa, sigla, descrizione, lingua, order_layer)
                    VALUES (:nome_tabella, :tipologia_sigla, :sigla_estesa, :sigla, :descrizione, :lingua, :order_layer)
                """)
                
                session.execute(insert_query, {
                    'nome_tabella': nome_tabella,
                    'tipologia_sigla': tipologia_sigla,
                    'sigla_estesa': sigla_estesa,
                    'sigla': str(settore),
                    'descrizione': descrizione,
                    'lingua': 'IT',
                    'order_layer': 2
                })
                
                QgsMessageLog.logMessage(f"Settore '{settore}' aggiunto al thesaurus TMA da {source_table}", "PyArchInit", Qgis.Info)
            else:
                # Se esiste già, aggiorna la descrizione se necessario
                if source_table and (not existing[3] or source_table not in existing[3]):
                    new_desc = existing[3] if existing[3] else ""
                    if new_desc:
                        new_desc += f"; Sincronizzato anche da {source_table}"
                    else:
                        new_desc = f"Sincronizzato da {source_table}"
                        
                    update_query = text("""
                        UPDATE pyarchinit_thesaurus_sigle 
                        SET descrizione = :descrizione
                        WHERE id_thesaurus_sigle = :id
                    """)
                    
                    session.execute(update_query, {
                        'descrizione': new_desc,
                        'id': existing[0]
                    })
                
            session.close()
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Errore sync settore to thesaurus: {str(e)}", "PyArchInit", Qgis.Warning)
    
    def sync_area_to_thesaurus(self, area, sito=None, source_table=None):
        """
        Aggiunge un'area al thesaurus TMA se non esiste
        
        Args:
            area: nome dell'area da aggiungere
            sito: nome del sito (opzionale)
            source_table: tabella di origine per tracking
        """
        if not area:
            return
            
        try:
            session = self.engine.connect()
            
            # Determina il codice tipologia_sigla e nome_tabella corretti in base alla tabella di origine
            table_config = {
                'us_table': {
                    'tipologia_sigla': '2.43',
                    'nome_tabella': 'US'
                },
                'inventario_materiali_table': {
                    'tipologia_sigla': '3.11',  # Area per Inventario Materiali
                    'nome_tabella': 'Inventario Materiali'
                },
                'tomba_table': {
                    'tipologia_sigla': '7.8',  # Area per Tombe
                    'nome_tabella': 'Tomba'
                },
                'individui_table': {
                    'tipologia_sigla': '8.6',  # Area per Individui
                    'nome_tabella': 'Individui'
                },
                'tma_materiali_archeologici': {
                    'tipologia_sigla': '10.7',
                    'nome_tabella': 'TMA materiali archeologici'
                }
            }
            
            # Ottieni configurazione per questa tabella
            config = table_config.get(source_table, {
                'tipologia_sigla': '10.7',
                'nome_tabella': 'TMA materiali archeologici'
            })
            
            tipologia_sigla = config['tipologia_sigla']
            nome_tabella = config['nome_tabella']
            
            # Verifica se l'area esiste già nel thesaurus confrontando sigla, sigla_estesa e descrizione
            check_query = text("""
                SELECT id_thesaurus_sigle, sigla, sigla_estesa, descrizione 
                FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = :nome_tabella
                AND tipologia_sigla = :tipologia
                AND sigla = :area
            """)
            
            result = session.execute(check_query, {
                "nome_tabella": nome_tabella,
                "tipologia": tipologia_sigla, 
                "area": str(area)
            })
            existing = result.fetchone()
            
            if not existing:
                # Aggiungi l'area al thesaurus
                sigla_estesa = f"Area {area}"
                if sito:
                    sigla_estesa = f"{sito} - Area {area}"
                    
                # Prepara descrizione con source tracking
                descrizione = ""
                if source_table:
                    descrizione = f"Sincronizzato da {source_table}"
                    
                insert_query = text("""
                    INSERT INTO pyarchinit_thesaurus_sigle 
                    (nome_tabella, tipologia_sigla, sigla_estesa, sigla, descrizione, lingua, order_layer)
                    VALUES (:nome_tabella, :tipologia_sigla, :sigla_estesa, :sigla, :descrizione, :lingua, :order_layer)
                """)
                
                session.execute(insert_query, {
                    'nome_tabella': nome_tabella,
                    'tipologia_sigla': tipologia_sigla,
                    'sigla_estesa': sigla_estesa,
                    'sigla': str(area),
                    'descrizione': descrizione,
                    'lingua': 'IT',
                    'order_layer': 2
                })
                
                QgsMessageLog.logMessage(f"Area '{area}' aggiunta al thesaurus TMA da {source_table}", "PyArchInit", Qgis.Info)
            else:
                # Se esiste già, aggiorna la descrizione se necessario
                if source_table and (not existing[3] or source_table not in existing[3]):
                    new_desc = existing[3] if existing[3] else ""
                    if new_desc:
                        new_desc += f"; Sincronizzato anche da {source_table}"
                    else:
                        new_desc = f"Sincronizzato da {source_table}"
                        
                    update_query = text("""
                        UPDATE pyarchinit_thesaurus_sigle 
                        SET descrizione = :descrizione
                        WHERE id_thesaurus_sigle = :id
                    """)
                    
                    session.execute(update_query, {
                        'descrizione': new_desc,
                        'id': existing[0]
                    })
                
            session.close()
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Errore sync area to thesaurus: {str(e)}", "PyArchInit", Qgis.Warning)
            
    def sync_material_value_to_thesaurus(self, value, field_type):
        """
        Aggiunge un valore di materiale al thesaurus TMA se non esiste
        
        Args:
            value: valore da aggiungere
            field_type: tipo di campo ('Categoria', 'Classe', 'Precisazione tipologica', 'Definizione')
        """
        if not value or not field_type:
            return
            
        try:
            session = self.engine.connect()
            
            # Verifica se il valore esiste già nel thesaurus
            check_query = text("""
                SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = 'TMA materiali archeologici' 
                AND tipologia_sigla = :tipo
                AND sigla = :valore
            """)
            
            result = session.execute(check_query, {"tipo": field_type, "valore": value})
            count = result.scalar()
            
            if count == 0:
                # Aggiungi il valore al thesaurus
                insert_query = text("""
                    INSERT INTO pyarchinit_thesaurus_sigle 
                    (nome_tabella, tipologia_sigla, sigla_estesa, sigla, lingua, order_layer)
                    VALUES (:nome_tabella, :tipologia_sigla, :sigla_estesa, :sigla, :lingua, :order_layer)
                """)
                
                session.execute(insert_query, {
                    'nome_tabella': 'TMA materiali archeologici',
                    'tipologia_sigla': field_type,
                    'sigla_estesa': value,
                    'sigla': value,
                    'lingua': 'IT',
                    'order_layer': 3
                })
                
                QgsMessageLog.logMessage(f"{field_type} '{value}' aggiunto al thesaurus TMA", "PyArchInit", Qgis.Info)
                
            session.close()
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Errore sync material value to thesaurus: {str(e)}", "PyArchInit", Qgis.Warning)
            
    def sync_from_inventory_materials(self, inventory_record):
        """
        Sincronizza i valori da un record di inventario_materiali_table al thesaurus TMA
        
        Args:
            inventory_record: record dell'inventario materiali
        """
        # Mapping dei campi
        field_mapping = {
            'tipo_reperto': 'Categoria',
            'corpo_ceramico': 'Classe',  # Cambiato da classe_materiale che non esiste
            'tipo': 'Precisazione tipologica',
            'definizione': 'Definizione'
        }
        
        # Sincronizza area se presente
        if hasattr(inventory_record, 'area') and inventory_record.area:
            sito = inventory_record.sito if hasattr(inventory_record, 'sito') else None
            self.sync_area_to_thesaurus(inventory_record.area, sito, 'inventario_materiali_table')
            
        # Sincronizza settore se presente (anche se non è comune nell'inventario)
        if hasattr(inventory_record, 'settore') and inventory_record.settore:
            sito = inventory_record.sito if hasattr(inventory_record, 'sito') else None
            self.sync_settore_to_thesaurus(inventory_record.settore, sito, 'inventario_materiali_table')
            
        # Sincronizza campi materiali
        for inv_field, thes_type in field_mapping.items():
            if hasattr(inventory_record, inv_field):
                value = getattr(inventory_record, inv_field)
                if value:
                    self.sync_material_value_to_thesaurus(value, thes_type)
                    
    def get_thesaurus_values(self, field_type, sito=None, area=None):
        """
        Ottiene i valori del thesaurus per un determinato tipo di campo
        
        Args:
            field_type: tipo di campo thesaurus
            sito: filtra per sito (opzionale)
            area: filtra per area (opzionale)
            
        Returns:
            lista di valori del thesaurus
        """
        try:
            session = self.engine.connect()
            
            query = text("""
                SELECT DISTINCT sigla 
                FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = 'TMA materiali archeologici' 
                AND tipologia_sigla = :tipo
                AND sigla IS NOT NULL
                ORDER BY sigla
            """)
            
            result = session.execute(query, {"tipo": field_type})
            values = [row[0] for row in result if row[0]]
            
            session.close()
            return values
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Errore get thesaurus values: {str(e)}", "PyArchInit", Qgis.Warning)
            return []
            
    def sync_tma_thesaurus_to_other_tables(self):
        """
        Sincronizza le aree predefinite del thesaurus TMA verso le altre tabelle
        Copia le aree da TMA (10.7) verso US, Inventario Materiali, Tombe e Individui
        """
        areas_synced = 0
        try:
            session = self.engine.connect()
            
            # 1. Ottieni tutte le aree predefinite TMA dal thesaurus
            query = text("""
                SELECT DISTINCT sigla, sigla_estesa 
                FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = 'TMA materiali archeologici' 
                AND tipologia_sigla = '10.7'
                ORDER BY sigla
            """)
            
            result = session.execute(query)
            tma_areas = []
            for row in result:
                if row[0]:
                    tma_areas.append({
                        'sigla': row[0],
                        'sigla_estesa': row[1] if row[1] else f"Area {row[0]}"
                    })
            
            QgsMessageLog.logMessage(f"Trovate {len(tma_areas)} aree TMA nel thesaurus da sincronizzare", "PyArchInit", Qgis.Info)
            
            # 2. Definisci le tabelle target con i loro codici
            target_tables = [
                {'nome': 'US', 'codice': '2.43'},
                {'nome': 'Inventario Materiali', 'codice': '3.11'},
                {'nome': 'Tomba', 'codice': '7.8'},
                {'nome': 'Individui', 'codice': '8.6'}
            ]
            
            # 3. Sincronizza verso ogni tabella
            for target in target_tables:
                table_synced = 0
                for area in tma_areas:
                    # Verifica se esiste già
                    check_query = text("""
                        SELECT COUNT(*) 
                        FROM pyarchinit_thesaurus_sigle 
                        WHERE nome_tabella = :nome_tabella
                        AND tipologia_sigla = :tipologia
                        AND sigla = :sigla
                    """)
                    
                    exists = session.execute(check_query, {
                        'nome_tabella': target['nome'],
                        'tipologia': target['codice'],
                        'sigla': area['sigla']
                    }).scalar()
                    
                    if not exists:
                        # Inserisci
                        insert_query = text("""
                            INSERT INTO pyarchinit_thesaurus_sigle 
                            (nome_tabella, tipologia_sigla, sigla_estesa, sigla, descrizione, lingua, order_layer)
                            VALUES (:nome_tabella, :tipologia_sigla, :sigla_estesa, :sigla, :descrizione, :lingua, :order_layer)
                        """)
                        
                        session.execute(insert_query, {
                            'nome_tabella': target['nome'],
                            'tipologia_sigla': target['codice'],
                            'sigla_estesa': area['sigla_estesa'],
                            'sigla': area['sigla'],
                            'descrizione': 'Sincronizzato da thesaurus TMA',
                            'lingua': 'IT',
                            'order_layer': 2
                        })
                        table_synced += 1
                        areas_synced += 1
                
                if table_synced > 0:
                    QgsMessageLog.logMessage(f"Sincronizzate {table_synced} aree verso {target['nome']}", "PyArchInit", Qgis.Info)
            
            session.close()
            QgsMessageLog.logMessage(f"Sincronizzate {areas_synced} aree totali da TMA verso altre tabelle", "PyArchInit", Qgis.Info)
            return areas_synced
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Errore sync TMA to other tables: {str(e)}", "PyArchInit", Qgis.Warning)
            return 0
    
    def sync_tma_materials_to_inventory(self):
        """
        Sincronizza i valori dei materiali dal thesaurus TMA verso inventario materiali
        """
        materials_synced = 0
        try:
            session = self.engine.connect()
            
            # Mapping TMA -> Inventario con i codici corretti
            field_mapping = [
                ('10.10', '3.1'),  # Categoria -> TIPO REPERTO
                ('10.11', '3.2'),  # Classe -> CLASSE MATERIALE
                ('10.13', '3.3') , # Definizione -> DEFINIZIONE REPERTO
                ('10.12', '3.12') # tipologia

            ]
            
            for tma_code, inv_code in field_mapping:
                # Ottieni valori TMA
                query = text("""
                    SELECT DISTINCT sigla, sigla_estesa 
                    FROM pyarchinit_thesaurus_sigle 
                    WHERE nome_tabella = 'TMA Materiali Ripetibili' 
                    AND tipologia_sigla = :tipo
                    ORDER BY sigla
                """)
                
                result = session.execute(query, {'tipo': tma_code})
                
                for row in result:
                    if row[0]:
                        # Verifica se esiste in inventario
                        check_query = text("""
                            SELECT COUNT(*) 
                            FROM pyarchinit_thesaurus_sigle 
                            WHERE nome_tabella = 'Inventario Materiali'
                            AND tipologia_sigla = :tipo
                            AND sigla = :sigla
                        """)
                        
                        exists = session.execute(check_query, {
                            'tipo': inv_code,
                            'sigla': row[0]
                        }).scalar()
                        
                        if not exists:
                            # Inserisci
                            insert_query = text("""
                                INSERT INTO pyarchinit_thesaurus_sigle 
                                (nome_tabella, tipologia_sigla, sigla_estesa, sigla, descrizione, lingua, order_layer)
                                VALUES (:nome_tabella, :tipologia_sigla, :sigla_estesa, :sigla, :descrizione, :lingua, :order_layer)
                            """)
                            
                            session.execute(insert_query, {
                                'nome_tabella': 'Inventario Materiali',
                                'tipologia_sigla': inv_code,
                                'sigla_estesa': row[1] if row[1] else row[0],
                                'sigla': row[0],
                                'descrizione': 'Sincronizzato da TMA',
                                'lingua': 'IT',
                                'order_layer': 3
                            })
                            materials_synced += 1
            
            session.close()
            QgsMessageLog.logMessage(f"Sincronizzati {materials_synced} valori materiali da TMA verso Inventario", "PyArchInit", Qgis.Info)
            return materials_synced
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Errore sync TMA materials: {str(e)}", "PyArchInit", Qgis.Warning)
            return 0
    
    def sync_all_areas_to_thesaurus(self):
        """
        Sincronizza tutte le aree da tutte le tabelle al thesaurus TMA
        """
        areas_found = 0
        try:
            session = self.engine.connect()
            
            # Tabelle da cui estrarre le aree
            tables = [
                ('us_table', 'area', 'us_table'),
                ('inventario_materiali_table', 'area', 'inventario_materiali_table'),
                ('tomba_table', 'area', 'tomba_table'),
                ('individui_table', 'area', 'individui_table'),
                ('tma_materiali_archeologici', 'area', 'tma_materiali_archeologici')
            ]
            
            for table_name, field_name, source_name in tables:
                try:
                    # Ottieni tutte le aree distinte da questa tabella
                    query = text(f"""
                        SELECT DISTINCT {field_name}, sito 
                        FROM {table_name} 
                        WHERE {field_name} IS NOT NULL 
                        AND {field_name} != ''
                        ORDER BY {field_name}
                    """)
                    
                    result = session.execute(query)
                    table_areas = []
                    
                    for row in result:
                        if row[0]:
                            area = str(row[0])
                            sito = row[1] if len(row) > 1 else None
                            table_areas.append((area, sito))
                            
                    if table_areas:
                        QgsMessageLog.logMessage(f"Trovate {len(table_areas)} aree in {table_name}", "PyArchInit", Qgis.Info)
                        
                        for area, sito in table_areas:
                            self.sync_area_to_thesaurus(area, sito, source_name)
                            areas_found += 1
                            
                except Exception as e:
                    QgsMessageLog.logMessage(f"Errore lettura aree da {table_name}: {str(e)}", "PyArchInit", Qgis.Warning)
                    
            session.close()
            QgsMessageLog.logMessage(f"Sincronizzate {areas_found} aree totali al thesaurus TMA", "PyArchInit", Qgis.Info)
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Errore sync all areas: {str(e)}", "PyArchInit", Qgis.Warning)
            
    def sync_all_settori_to_thesaurus(self):
        """
        Sincronizza tutti i settori da us_table e tma al thesaurus TMA
        """
        settori_found = 0
        try:
            session = self.engine.connect()
            
            # Tabelle da cui estrarre i settori
            tables = [
                ('us_table', 'settore', 'us_table'),
                ('tma_materiali_archeologici', 'settore', 'tma_materiali_archeologici')
            ]
            
            for table_name, field_name, source_name in tables:
                try:
                    # Ottieni tutti i settori distinti da questa tabella
                    query = text(f"""
                        SELECT DISTINCT {field_name}, sito 
                        FROM {table_name} 
                        WHERE {field_name} IS NOT NULL 
                        AND {field_name} != ''
                        ORDER BY {field_name}
                    """)
                    
                    result = session.execute(query)
                    table_settori = []
                    
                    for row in result:
                        if row[0]:
                            settore = str(row[0])
                            sito = row[1] if len(row) > 1 else None
                            table_settori.append((settore, sito))
                            
                    if table_settori:
                        QgsMessageLog.logMessage(f"Trovati {len(table_settori)} settori in {table_name}", "PyArchInit", Qgis.Info)
                        
                        for settore, sito in table_settori:
                            self.sync_settore_to_thesaurus(settore, sito, source_name)
                            settori_found += 1
                            
                except Exception as e:
                    QgsMessageLog.logMessage(f"Errore lettura settori da {table_name}: {str(e)}", "PyArchInit", Qgis.Warning)
                    
            session.close()
            QgsMessageLog.logMessage(f"Sincronizzati {settori_found} settori totali al thesaurus TMA", "PyArchInit", Qgis.Info)
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Errore sync all settori: {str(e)}", "PyArchInit", Qgis.Warning)
    
    def sync_all_inventory_to_thesaurus(self):
        """
        Sincronizza tutti i valori dall'inventario materiali al thesaurus TMA
        """
        try:
            # Use direct SQL to get inventory materials data
            session = self.engine.connect()
            
            # Get distinct tipo_reperto values (-> Categoria)
            query = text("SELECT DISTINCT tipo_reperto FROM inventario_materiali_table WHERE tipo_reperto IS NOT NULL AND tipo_reperto != ''")
            result = session.execute(query)
            for row in result:
                if row[0]:
                    self.sync_material_value_to_thesaurus(row[0], 'Categoria')
                    
            # Get distinct corpo_ceramico values (-> Classe) 
            # Non c'è un campo classe_materiale, uso corpo_ceramico come alternativa
            query = text("SELECT DISTINCT corpo_ceramico FROM inventario_materiali_table WHERE corpo_ceramico IS NOT NULL AND corpo_ceramico != ''")
            result = session.execute(query)
            for row in result:
                if row[0]:
                    self.sync_material_value_to_thesaurus(row[0], 'Classe')
                    
            # Get distinct tipo values (-> Precisazione tipologica)
            query = text("SELECT DISTINCT tipo FROM inventario_materiali_table WHERE tipo IS NOT NULL AND tipo != ''")
            result = session.execute(query)
            for row in result:
                if row[0]:
                    self.sync_material_value_to_thesaurus(row[0], 'Precisazione tipologica')
                    
            # Get distinct definizione values (-> Definizione)
            query = text("SELECT DISTINCT definizione FROM inventario_materiali_table WHERE definizione IS NOT NULL AND definizione != ''")
            result = session.execute(query)
            for row in result:
                if row[0]:
                    self.sync_material_value_to_thesaurus(row[0], 'Definizione')
                    
            session.close()
            
            QgsMessageLog.logMessage("Sincronizzazione inventario->thesaurus completata", "PyArchInit", Qgis.Info)
            
        except Exception as e:
            QgsMessageLog.logMessage(f"Errore sync all inventory: {str(e)}", "PyArchInit", Qgis.Warning)