#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per sincronizzare il thesaurus TMA con le altre tabelle del database.
Sincronizza:
1. Le aree dal thesaurus TMA alle tabelle us_table, inventario_materiali_table, tomba_table, individui_table
2. I campi dei materiali tra tma_materiali_ripetibili e inventario_materiali_table
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.db.pyarchinit_conn_strings import Connection
from modules.db.pyarchinit_db_manager import Pyarchinit_db_management
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


class TMAThesaurusSync:
    """Classe per sincronizzare il thesaurus TMA con le altre tabelle"""
    
    def __init__(self):
        """Inizializza la connessione al database"""
        self.conn = Connection()
        self.engine = create_engine(self.conn.conn_str())
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
    def get_tma_areas(self):
        """Ottiene tutte le aree uniche dal thesaurus TMA"""
        try:
            query = text("""
                SELECT DISTINCT thesaurus_sigle 
                FROM pyarchinit_thesaurus 
                WHERE nome_tabella = 'TMA materiali archeologici' 
                AND tipologia_sigla = 'area'
                AND thesaurus_sigle IS NOT NULL
                ORDER BY thesaurus_sigle
            """)
            result = self.session.execute(query)
            areas = [row[0] for row in result if row[0]]
            print(f"Trovate {len(areas)} aree nel thesaurus TMA: {areas}")
            return areas
        except Exception as e:
            print(f"Errore nel recupero delle aree: {e}")
            return []
            
    def get_tma_settori(self):
        """Ottiene tutti i settori unici dal thesaurus TMA"""
        try:
            query = text("""
                SELECT DISTINCT sigla 
                FROM pyarchinit_thesaurus_sigle 
                WHERE nome_tabella = 'TMA materiali archeologici' 
                AND tipologia_sigla = 'settore'
                AND sigla IS NOT NULL
                ORDER BY sigla
            """)
            result = self.session.execute(query)
            settori = [row[0] for row in result if row[0]]
            print(f"Trovati {len(settori)} settori nel thesaurus TMA: {settori}")
            return settori
        except Exception as e:
            print(f"Errore nel recupero dei settori: {e}")
            return []
    
    def sync_areas_to_tables(self):
        """Sincronizza le aree del thesaurus TMA con le altre tabelle"""
        areas = self.get_tma_areas()
        if not areas:
            print("Nessuna area trovata nel thesaurus TMA")
            return
            
        # Tabelle da aggiornare con il campo area
        tables_to_update = [
            ('us_table', 'area'),
            ('inventario_materiali_table', 'area'),
            ('tomba_table', 'area'),
            ('individui_table', 'area'),
            ('tma_materiali_archeologici', 'area')
        ]
        
        for table_name, field_name in tables_to_update:
            try:
                # Prima verifica le aree esistenti
                query = text(f"SELECT DISTINCT {field_name} FROM {table_name} WHERE {field_name} IS NOT NULL")
                result = self.session.execute(query)
                existing_areas = set(row[0] for row in result if row[0])
                
                # Trova aree mancanti nel thesaurus per questa tabella
                missing_in_thesaurus = existing_areas - set(areas)
                
                if missing_in_thesaurus:
                    print(f"\nTabella {table_name}: aree presenti nei dati ma mancanti nel thesaurus TMA:")
                    for area in sorted(missing_in_thesaurus):
                        print(f"  - {area}")
                        
                        # Aggiungi al thesaurus
                        insert_query = text("""
                            INSERT OR IGNORE INTO pyarchinit_thesaurus 
                            (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
                            VALUES (:nome_tabella, :tipologia_sigla, :sigla_estesa, :thesaurus_sigle, :lingua, :order_layer)
                        """)
                        
                        self.session.execute(insert_query, {
                            'nome_tabella': 'TMA materiali archeologici',
                            'tipologia_sigla': 'area',
                            'sigla_estesa': f'Area {area}',
                            'thesaurus_sigle': area,
                            'lingua': 'it',
                            'order_layer': 2
                        })
                        print(f"    Aggiunta al thesaurus TMA: {area}")
                        
                self.session.commit()
                print(f"✓ Sincronizzazione aree completata per {table_name}")
                
            except Exception as e:
                print(f"✗ Errore nella sincronizzazione di {table_name}: {e}")
                self.session.rollback()
                
    def sync_settori_to_tables(self):
        """Sincronizza i settori dal us_table e tma al thesaurus TMA"""
        
        # Tabelle che hanno il campo settore
        tables_with_settore = [
            ('us_table', 'settore'),
            ('tma_materiali_archeologici', 'settore')
        ]
        
        print("\n=== Sincronizzazione settori ===")
        
        for table_name, field_name in tables_with_settore:
            try:
                # Ottieni settori esistenti nella tabella
                query = text(f"SELECT DISTINCT {field_name} FROM {table_name} WHERE {field_name} IS NOT NULL AND {field_name} != ''")
                result = self.session.execute(query)
                existing_settori = set(row[0] for row in result if row[0])
                
                if existing_settori:
                    print(f"\nTabella {table_name}: trovati {len(existing_settori)} settori")
                    
                    for settore in sorted(existing_settori):
                        # Aggiungi al thesaurus
                        insert_query = text("""
                            INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle 
                            (nome_tabella, tipologia_sigla, sigla_estesa, sigla, lingua, order_layer)
                            VALUES (:nome_tabella, :tipologia_sigla, :sigla_estesa, :sigla, :lingua, :order_layer)
                        """)
                        
                        self.session.execute(insert_query, {
                            'nome_tabella': 'TMA materiali archeologici',
                            'tipologia_sigla': 'settore',
                            'sigla_estesa': f'Settore {settore}',
                            'sigla': settore,
                            'lingua': 'it',
                            'order_layer': 2
                        })
                        print(f"    + Settore {settore}")
                        
                self.session.commit()
                print(f"✓ Sincronizzazione settori completata per {table_name}")
                
            except Exception as e:
                print(f"✗ Errore nella sincronizzazione settori di {table_name}: {e}")
                self.session.rollback()
                
    def sync_material_fields(self):
        """Sincronizza i campi dei materiali tra tma_materiali_ripetibili e inventario_materiali_table"""
        
        # Mapping dei campi thesaurus -> inventario
        field_mapping = {
            'Categoria': 'tipo_reperto',          # macc -> tipo_reperto
            'Classe': 'classe_materiale',         # macl -> classe_materiale  
            'Precisazione tipologica': 'tipo',    # macp -> tipologia (nel DB è 'tipo')
            'Definizione': 'definizione'          # macd -> definizione_reperto (nel DB è 'definizione')
        }
        
        print("\n=== Sincronizzazione campi materiali ===")
        
        for thesaurus_type, inv_field in field_mapping.items():
            try:
                # Ottieni valori dal thesaurus TMA materiali
                query = text("""
                    SELECT DISTINCT thesaurus_sigle 
                    FROM pyarchinit_thesaurus 
                    WHERE nome_tabella = 'TMA materiali archeologici' 
                    AND tipologia_sigla = :tipo
                    AND thesaurus_sigle IS NOT NULL
                    ORDER BY thesaurus_sigle
                """)
                
                result = self.session.execute(query, {'tipo': thesaurus_type})
                thesaurus_values = set(row[0] for row in result if row[0])
                
                print(f"\n{thesaurus_type}: trovati {len(thesaurus_values)} valori nel thesaurus")
                
                # Ottieni valori dall'inventario materiali
                inv_query = text(f"""
                    SELECT DISTINCT {inv_field} 
                    FROM inventario_materiali_table 
                    WHERE {inv_field} IS NOT NULL AND {inv_field} != ''
                """)
                
                inv_result = self.session.execute(inv_query)
                inventory_values = set(row[0] for row in inv_result if row[0])
                
                # Trova valori mancanti nel thesaurus
                missing_in_thesaurus = inventory_values - thesaurus_values
                
                if missing_in_thesaurus:
                    print(f"  Valori da aggiungere al thesaurus da inventario_materiali_table:")
                    for value in sorted(missing_in_thesaurus):
                        # Aggiungi al thesaurus
                        insert_query = text("""
                            INSERT OR IGNORE INTO pyarchinit_thesaurus 
                            (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
                            VALUES (:nome_tabella, :tipologia_sigla, :sigla_estesa, :thesaurus_sigle, :lingua, :order_layer)
                        """)
                        
                        self.session.execute(insert_query, {
                            'nome_tabella': 'TMA materiali archeologici',
                            'tipologia_sigla': thesaurus_type,
                            'sigla_estesa': value,
                            'thesaurus_sigle': value,
                            'lingua': 'it',
                            'order_layer': 3
                        })
                        print(f"    + {value}")
                        
                self.session.commit()
                print(f"  ✓ Sincronizzazione completata per {thesaurus_type}")
                
            except Exception as e:
                print(f"  ✗ Errore nella sincronizzazione di {thesaurus_type}: {e}")
                self.session.rollback()
                
    def create_sync_trigger(self):
        """Crea trigger per sincronizzazione automatica (solo per SQLite)"""
        if 'sqlite' in self.conn.conn_str():
            try:
                conn = sqlite3.connect(self.conn.conn_str().replace('sqlite:///', ''))
                cursor = conn.cursor()
                
                # Trigger per sincronizzare quando si inserisce in inventario_materiali_table
                trigger_sql = """
                CREATE TRIGGER IF NOT EXISTS sync_inventory_to_thesaurus
                AFTER INSERT ON inventario_materiali_table
                BEGIN
                    -- Sync tipo_reperto to Categoria
                    INSERT OR IGNORE INTO pyarchinit_thesaurus 
                    (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
                    SELECT 'TMA materiali archeologici', 'Categoria', NEW.tipo_reperto, NEW.tipo_reperto, 'it', 3
                    WHERE NEW.tipo_reperto IS NOT NULL AND NEW.tipo_reperto != '';
                    
                    -- Sync classe_materiale to Classe
                    INSERT OR IGNORE INTO pyarchinit_thesaurus 
                    (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
                    SELECT 'TMA materiali archeologici', 'Classe', NEW.classe_materiale, NEW.classe_materiale, 'it', 3
                    WHERE NEW.classe_materiale IS NOT NULL AND NEW.classe_materiale != '';
                    
                    -- Sync tipo to Precisazione tipologica
                    INSERT OR IGNORE INTO pyarchinit_thesaurus 
                    (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
                    SELECT 'TMA materiali archeologici', 'Precisazione tipologica', NEW.tipo, NEW.tipo, 'it', 3
                    WHERE NEW.tipo IS NOT NULL AND NEW.tipo != '';
                    
                    -- Sync definizione to Definizione
                    INSERT OR IGNORE INTO pyarchinit_thesaurus 
                    (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
                    SELECT 'TMA materiali archeologici', 'Definizione', NEW.definizione, NEW.definizione, 'it', 3
                    WHERE NEW.definizione IS NOT NULL AND NEW.definizione != '';
                    
                    -- Sync area
                    INSERT OR IGNORE INTO pyarchinit_thesaurus 
                    (nome_tabella, tipologia_sigla, sigla_estesa, thesaurus_sigle, lingua, order_layer)
                    SELECT 'TMA materiali archeologici', 'area', 'Area ' || NEW.area, NEW.area, 'it', 2
                    WHERE NEW.area IS NOT NULL AND NEW.area != '';
                END;
                """
                
                cursor.execute(trigger_sql)
                conn.commit()
                conn.close()
                print("\n✓ Trigger di sincronizzazione creato con successo")
                
            except Exception as e:
                print(f"\n✗ Errore nella creazione del trigger: {e}")
                
    def run_full_sync(self):
        """Esegue la sincronizzazione completa"""
        print("=== SINCRONIZZAZIONE THESAURUS TMA ===")
        print(f"Database: {self.conn.conn_str()}")
        print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # Sincronizza aree
        print("\n1. Sincronizzazione aree...")
        self.sync_areas_to_tables()
        
        # Sincronizza settori
        print("\n2. Sincronizzazione settori...")
        self.sync_settori_to_tables()
        
        # Sincronizza campi materiali
        print("\n3. Sincronizzazione campi materiali...")
        self.sync_material_fields()
        
        # Crea trigger per sincronizzazione automatica futura
        print("\n4. Creazione trigger per sincronizzazione automatica...")
        self.create_sync_trigger()
        
        self.session.close()
        print("\n=== SINCRONIZZAZIONE COMPLETATA ===")


if __name__ == "__main__":
    sync = TMAThesaurusSync()
    sync.run_full_sync()