#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Database migrations for PyArchInit
Handles automatic creation of new tables and thesaurus entries
"""

from sqlalchemy import text, inspect
from sqlalchemy.orm import sessionmaker


class DatabaseMigrations:
    """Handle database migrations for PyArchInit"""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.engine = db_manager.engine

    def check_and_migrate(self):
        """Run all necessary migrations"""
        migrations_run = []

        # Check and create fauna_table
        if self.migrate_fauna_table():
            migrations_run.append('fauna_table')

        # Add fauna thesaurus entries
        if self.migrate_fauna_thesaurus():
            migrations_run.append('fauna_thesaurus')

        return migrations_run

    def table_exists(self, table_name):
        """Check if a table exists in the database"""
        inspector = inspect(self.engine)
        return table_name in inspector.get_table_names()

    def migrate_fauna_table(self):
        """Create fauna_table if it doesn't exist"""
        if self.table_exists('fauna_table'):
            return False

        # Determine database type
        dialect = self.engine.dialect.name

        if dialect == 'postgresql':
            create_sql = """
            CREATE TABLE IF NOT EXISTS fauna_table (
                id_fauna BIGSERIAL PRIMARY KEY,
                id_us BIGINT,
                sito TEXT,
                area TEXT,
                saggio TEXT,
                us TEXT,
                datazione_us TEXT,
                responsabile_scheda TEXT,
                data_compilazione DATE,
                documentazione_fotografica TEXT,
                metodologia_recupero TEXT,
                contesto TEXT,
                descrizione_contesto TEXT,
                resti_connessione_anatomica TEXT,
                tipologia_accumulo TEXT,
                deposizione TEXT,
                numero_stimato_resti TEXT,
                numero_minimo_individui INTEGER,
                specie TEXT,
                parti_scheletriche TEXT,
                specie_psi TEXT,
                misure_ossa TEXT,
                stato_frammentazione TEXT,
                tracce_combustione TEXT,
                combustione_altri_materiali_us BOOLEAN,
                tipo_combustione TEXT,
                segni_tafonomici_evidenti TEXT,
                caratterizzazione_segni_tafonomici TEXT,
                stato_conservazione TEXT,
                alterazioni_morfologiche TEXT,
                note_terreno_giacitura TEXT,
                campionature_effettuate TEXT,
                affidabilita_stratigrafica TEXT,
                classi_reperti_associazione TEXT,
                osservazioni TEXT,
                interpretazione TEXT,
                UNIQUE (sito, area, us, id_fauna)
            );
            """
        else:  # SQLite
            create_sql = """
            CREATE TABLE IF NOT EXISTS fauna_table (
                id_fauna INTEGER PRIMARY KEY AUTOINCREMENT,
                id_us INTEGER,
                sito TEXT,
                area TEXT,
                saggio TEXT,
                us TEXT,
                datazione_us TEXT,
                responsabile_scheda TEXT,
                data_compilazione DATE,
                documentazione_fotografica TEXT,
                metodologia_recupero TEXT,
                contesto TEXT,
                descrizione_contesto TEXT,
                resti_connessione_anatomica TEXT,
                tipologia_accumulo TEXT,
                deposizione TEXT,
                numero_stimato_resti TEXT,
                numero_minimo_individui INTEGER,
                specie TEXT,
                parti_scheletriche TEXT,
                specie_psi TEXT,
                misure_ossa TEXT,
                stato_frammentazione TEXT,
                tracce_combustione TEXT,
                combustione_altri_materiali_us INTEGER,
                tipo_combustione TEXT,
                segni_tafonomici_evidenti TEXT,
                caratterizzazione_segni_tafonomici TEXT,
                stato_conservazione TEXT,
                alterazioni_morfologiche TEXT,
                note_terreno_giacitura TEXT,
                campionature_effettuate TEXT,
                affidabilita_stratigrafica TEXT,
                classi_reperti_associazione TEXT,
                osservazioni TEXT,
                interpretazione TEXT,
                UNIQUE (sito, area, us, id_fauna)
            );
            """

        try:
            with self.engine.connect() as conn:
                conn.execute(text(create_sql))
                conn.commit()
            return True
        except Exception as e:
            print(f"[PyArchInit] Error creating fauna_table: {e}")
            return False

    def migrate_fauna_thesaurus(self):
        """Add fauna thesaurus entries if they don't exist"""
        # Check if fauna_table entries already exist
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT COUNT(*) FROM pyarchinit_thesaurus_sigle WHERE nome_tabella = 'fauna_table'"
                ))
                count = result.scalar()
                if count and count > 0:
                    return False
        except Exception as e:
            print(f"[PyArchInit] Error checking fauna thesaurus: {e}")
            return False

        # Thesaurus entries to add
        entries = self._get_fauna_thesaurus_entries()

        dialect = self.engine.dialect.name

        try:
            Session = sessionmaker(bind=self.engine)
            session = Session()

            for entry in entries:
                if dialect == 'postgresql':
                    insert_sql = text("""
                        INSERT INTO pyarchinit_thesaurus_sigle
                        (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
                        VALUES (:nome_tabella, :sigla, :sigla_estesa, :descrizione, :tipologia_sigla, :lingua)
                        ON CONFLICT DO NOTHING
                    """)
                else:  # SQLite
                    insert_sql = text("""
                        INSERT OR IGNORE INTO pyarchinit_thesaurus_sigle
                        (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla, lingua)
                        VALUES (:nome_tabella, :sigla, :sigla_estesa, :descrizione, :tipologia_sigla, :lingua)
                    """)

                session.execute(insert_sql, entry)

            session.commit()
            session.close()
            return True
        except Exception as e:
            print(f"[PyArchInit] Error adding fauna thesaurus: {e}")
            return False

    def _get_fauna_thesaurus_entries(self):
        """Return list of fauna thesaurus entries"""
        entries = []

        # 13.1 - Contesto
        for sigla, sigla_estesa, desc in [
            ('DOMESTICO', 'Contesto domestico', 'Contesto residenziale/abitativo'),
            ('RITUALE', 'Contesto rituale', 'Contesto cerimoniale/rituale'),
            ('FUNERARIO', 'Contesto funerario', 'Contesto sepolcrale/funerario'),
            ('PRODUTTIVO', 'Contesto produttivo', 'Contesto artigianale/industriale'),
            ('RIFIUTI', 'Deposito rifiuti', 'Scarico/deposito di rifiuti'),
        ]:
            entries.append({
                'nome_tabella': 'fauna_table', 'sigla': sigla, 'sigla_estesa': sigla_estesa,
                'descrizione': desc, 'tipologia_sigla': '13.1', 'lingua': 'IT'
            })

        # 13.2 - Metodologia Recupero
        for sigla, sigla_estesa, desc in [
            ('MANUALE', 'Raccolta manuale', 'Recupero manuale durante lo scavo'),
            ('SETACCIO', 'Setacciatura', 'Recupero mediante setacciatura'),
            ('FLOTTAZIONE', 'Flottazione', 'Recupero mediante flottazione'),
        ]:
            entries.append({
                'nome_tabella': 'fauna_table', 'sigla': sigla, 'sigla_estesa': sigla_estesa,
                'descrizione': desc, 'tipologia_sigla': '13.2', 'lingua': 'IT'
            })

        # 13.3 - Tipologia Accumulo
        for sigla, sigla_estesa, desc in [
            ('NATURALE', 'Accumulo naturale', 'Accumulo per cause naturali'),
            ('ANTROPICO', 'Accumulo antropico', 'Accumulo per attività umana'),
            ('MISTO', 'Accumulo misto', 'Accumulo di origine mista'),
        ]:
            entries.append({
                'nome_tabella': 'fauna_table', 'sigla': sigla, 'sigla_estesa': sigla_estesa,
                'descrizione': desc, 'tipologia_sigla': '13.3', 'lingua': 'IT'
            })

        # 13.4 - Deposizione
        for sigla, sigla_estesa, desc in [
            ('PRIMARIA', 'Deposizione primaria', 'Deposizione in situ'),
            ('SECONDARIA', 'Deposizione secondaria', 'Deposizione dopo spostamento'),
            ('RIMANEGGIATA', 'Deposizione rimaneggiata', 'Deposizione disturbata'),
        ]:
            entries.append({
                'nome_tabella': 'fauna_table', 'sigla': sigla, 'sigla_estesa': sigla_estesa,
                'descrizione': desc, 'tipologia_sigla': '13.4', 'lingua': 'IT'
            })

        # 13.5 - Stato Frammentazione
        for sigla, sigla_estesa, desc in [
            ('INTEGRO', 'Integro', 'Osso completo'),
            ('FRAMMENTATO', 'Frammentato', 'Osso frammentato'),
            ('PARZIALE', 'Parziale', 'Osso parzialmente conservato'),
        ]:
            entries.append({
                'nome_tabella': 'fauna_table', 'sigla': sigla, 'sigla_estesa': sigla_estesa,
                'descrizione': desc, 'tipologia_sigla': '13.5', 'lingua': 'IT'
            })

        # 13.6 - Stato Conservazione
        for sigla, sigla_estesa, desc in [
            ('BUONO', 'Buono', 'Buono stato di conservazione'),
            ('MEDIOCRE', 'Mediocre', 'Stato di conservazione mediocre'),
            ('CATTIVO', 'Cattivo', 'Cattivo stato di conservazione'),
        ]:
            entries.append({
                'nome_tabella': 'fauna_table', 'sigla': sigla, 'sigla_estesa': sigla_estesa,
                'descrizione': desc, 'tipologia_sigla': '13.6', 'lingua': 'IT'
            })

        # 13.7 - Affidabilità Stratigrafica
        for sigla, sigla_estesa, desc in [
            ('ALTA', 'Alta affidabilità', 'Alta affidabilità stratigrafica'),
            ('MEDIA', 'Media affidabilità', 'Media affidabilità stratigrafica'),
            ('BASSA', 'Bassa affidabilità', 'Bassa affidabilità stratigrafica'),
        ]:
            entries.append({
                'nome_tabella': 'fauna_table', 'sigla': sigla, 'sigla_estesa': sigla_estesa,
                'descrizione': desc, 'tipologia_sigla': '13.7', 'lingua': 'IT'
            })

        # 13.8 - Tracce Combustione
        for sigla, sigla_estesa, desc in [
            ('ASSENTI', 'Assenti', 'Nessuna traccia di combustione'),
            ('PRESENTI', 'Presenti', 'Tracce di combustione presenti'),
            ('DIFFUSE', 'Diffuse', 'Tracce di combustione diffuse'),
        ]:
            entries.append({
                'nome_tabella': 'fauna_table', 'sigla': sigla, 'sigla_estesa': sigla_estesa,
                'descrizione': desc, 'tipologia_sigla': '13.8', 'lingua': 'IT'
            })

        # 13.9 - Tipo Combustione
        for sigla, sigla_estesa, desc in [
            ('CARBONIZZAZIONE', 'Carbonizzazione', 'Combustione con carbonizzazione'),
            ('CALCINAZIONE', 'Calcinazione', 'Combustione con calcinazione'),
            ('PARZIALE', 'Parziale', 'Combustione parziale'),
        ]:
            entries.append({
                'nome_tabella': 'fauna_table', 'sigla': sigla, 'sigla_estesa': sigla_estesa,
                'descrizione': desc, 'tipologia_sigla': '13.9', 'lingua': 'IT'
            })

        # 13.10 - Connessione Anatomica
        for sigla, sigla_estesa, desc in [
            ('SI', 'In connessione', 'Ossa in connessione anatomica'),
            ('NO', 'Non in connessione', 'Ossa disarticolate'),
            ('PARZIALE', 'Parziale', 'Connessione anatomica parziale'),
        ]:
            entries.append({
                'nome_tabella': 'fauna_table', 'sigla': sigla, 'sigla_estesa': sigla_estesa,
                'descrizione': desc, 'tipologia_sigla': '13.10', 'lingua': 'IT'
            })

        # 13.11 - Specie
        for sigla, sigla_estesa, desc in [
            ('BOS_TAURUS', 'Bos taurus', 'Bovino domestico'),
            ('OVIS_ARIES', 'Ovis aries', 'Pecora domestica'),
            ('CAPRA_HIRCUS', 'Capra hircus', 'Capra domestica'),
            ('SUS_DOMESTICUS', 'Sus domesticus', 'Maiale domestico'),
            ('OVIS_CAPRA', 'Ovis/Capra', 'Ovicaprino indeterminato'),
            ('CERVUS_ELAPHUS', 'Cervus elaphus', 'Cervo'),
            ('EQUUS_CABALLUS', 'Equus caballus', 'Cavallo'),
            ('CANIS_FAMILIARIS', 'Canis familiaris', 'Cane domestico'),
            ('INDET', 'Indeterminato', 'Specie indeterminata'),
        ]:
            entries.append({
                'nome_tabella': 'fauna_table', 'sigla': sigla, 'sigla_estesa': sigla_estesa,
                'descrizione': desc, 'tipologia_sigla': '13.11', 'lingua': 'IT'
            })

        # 13.12 - Parti Scheletriche (PSI)
        for sigla, sigla_estesa, desc in [
            ('CRANIO', 'Cranio', 'Cranio/elementi craniali'),
            ('MANDIBOLA', 'Mandibola', 'Mandibola/mascella'),
            ('VERTEBRE', 'Vertebre', 'Elementi vertebrali'),
            ('COSTE', 'Coste', 'Costole'),
            ('SCAPOLA', 'Scapola', 'Scapola'),
            ('OMERO', 'Omero', 'Omero'),
            ('RADIO', 'Radio', 'Radio'),
            ('ULNA', 'Ulna', 'Ulna'),
            ('PELVI', 'Pelvi', 'Bacino'),
            ('FEMORE', 'Femore', 'Femore'),
            ('TIBIA', 'Tibia', 'Tibia'),
            ('METAPODIO', 'Metapodio', 'Metacarpo/Metatarso'),
            ('FALANGI', 'Falangi', 'Falangi'),
        ]:
            entries.append({
                'nome_tabella': 'fauna_table', 'sigla': sigla, 'sigla_estesa': sigla_estesa,
                'descrizione': desc, 'tipologia_sigla': '13.12', 'lingua': 'IT'
            })

        # 13.13 - Elemento Anatomico
        for sigla, sigla_estesa, desc in [
            ('HUM', 'Humerus', 'Omero'),
            ('RAD', 'Radius', 'Radio'),
            ('FEM', 'Femur', 'Femore'),
            ('TIB', 'Tibia', 'Tibia'),
            ('MTC', 'Metacarpus', 'Metacarpo'),
            ('MTT', 'Metatarsus', 'Metatarso'),
            ('AST', 'Astragalus', 'Astragalo'),
            ('CAL', 'Calcaneus', 'Calcagno'),
            ('PHI', 'Phalanx I', 'Prima falange'),
            ('PHII', 'Phalanx II', 'Seconda falange'),
            ('PHIII', 'Phalanx III', 'Terza falange'),
        ]:
            entries.append({
                'nome_tabella': 'fauna_table', 'sigla': sigla, 'sigla_estesa': sigla_estesa,
                'descrizione': desc, 'tipologia_sigla': '13.13', 'lingua': 'IT'
            })

        return entries


def run_migrations(db_manager):
    """Run all database migrations"""
    try:
        migrations = DatabaseMigrations(db_manager)
        result = migrations.check_and_migrate()
        if result:
            print(f"[PyArchInit] Database migrations completed: {', '.join(result)}")
        return result
    except Exception as e:
        print(f"[PyArchInit] Error running migrations: {e}")
        return []
