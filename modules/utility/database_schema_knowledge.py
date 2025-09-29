#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Database Schema Knowledge for AI
This module provides comprehensive database schema information that can be used
by AI systems to understand the PyArchInit database structure.
"""

class DatabaseSchemaKnowledge:
    """
    Contains complete database schema information for AI context
    """

    @staticmethod
    def get_full_schema():
        """
        Returns the complete database schema as a structured dictionary
        that can be used by AI for understanding relationships
        """
        return {
            "database_name": "pyarchinit",
            "description": "Archaeological excavation database system",
            "tables": {
                "site_table": {
                    "description": "Archaeological sites",
                    "primary_key": "id_sito",
                    "fields": {
                        "sito": "Site name",
                        "nazione": "Country",
                        "regione": "Region",
                        "comune": "Municipality",
                        "descrizione": "Description",
                        "provincia": "Province"
                    }
                },
                "us_table": {
                    "description": "Stratigraphic units",
                    "primary_key": "id_us",
                    "fields": {
                        "sito": "Site name (FK to site_table)",
                        "area": "Excavation area",
                        "us": "Unit number",
                        "d_stratigrafica": "Stratigraphic definition",
                        "d_interpretativa": "Interpretative definition",
                        "descrizione": "Description",
                        "interpretazione": "Interpretation",
                        "periodo_iniziale": "Initial period",
                        "fase_iniziale": "Initial phase",
                        "periodo_finale": "Final period",
                        "fase_finale": "Final phase",
                        "scavato": "Excavated (yes/no)",
                        "attivita": "Activity",
                        "anno_scavo": "Excavation year",
                        "metodo_di_scavo": "Excavation method",
                        "inclusi": "Inclusions",
                        "campioni": "Samples",
                        "rapporti": "Relationships",
                        "organici": "Organic materials",
                        "inorganici": "Inorganic materials"
                    },
                    "relationships": {
                        "site_table": "sito -> site_table.sito",
                        "inventario_materiali_table": "One-to-many via sito/area/us",
                        "pottery_table": "One-to-many via sito/area/us"
                    }
                },
                "inventario_materiali_table": {
                    "description": "Material finds inventory",
                    "primary_key": "id_invmat",
                    "fields": {
                        "sito": "Site name",
                        "numero_inventario": "Inventory number",
                        "tipo_reperto": "Find type",
                        "criterio_schedatura": "Recording criteria",
                        "definizione": "Definition",
                        "descrizione": "Description",
                        "area": "Area",
                        "us": "Stratigraphic unit",
                        "lavato": "Washed",
                        "nr_cassa": "Box number",
                        "luogo_conservazione": "Storage location",
                        "stato_conservazione": "Conservation state",
                        "datazione_reperto": "Dating",
                        "elementi_reperto": "Find elements",
                        "misurazioni": "Measurements",
                        "rif_biblio": "Bibliographic references",
                        "tecnologie": "Technologies"
                    },
                    "relationships": {
                        "us_table": "sito/area/us -> us_table"
                    }
                },
                "pottery_table": {
                    "description": "Pottery catalog",
                    "primary_key": "id_pottery",
                    "fields": {
                        "sito": "Site name",
                        "area": "Area",
                        "us": "Stratigraphic unit",
                        "inv_number": "Inventory number",
                        "typology": "Typology",
                        "fabric": "Fabric",
                        "specific_form": "Specific form",
                        "specific_part": "Specific part",
                        "ware": "Ware",
                        "exterior_decoration": "Exterior decoration",
                        "interior_decoration": "Interior decoration",
                        "wheel_made": "Wheel made",
                        "description": "Description",
                        "diameter_max": "Maximum diameter",
                        "diameter_rim": "Rim diameter",
                        "diameter_bottom": "Bottom diameter",
                        "total_height": "Total height",
                        "preserved_height": "Preserved height",
                        "diameter_border": "Border diameter"
                    },
                    "relationships": {
                        "us_table": "sito/area/us -> us_table"
                    }
                },
                "tma_materiali_archeologici": {
                    "description": "Archaeological materials typology (TMA)",
                    "primary_key": "id_tma",
                    "fields": {
                        "sito": "Site name",
                        "area": "Area",
                        "us": "Stratigraphic unit",
                        "localita": "Locality",
                        "settore": "Sector",
                        "inventario": "Inventory",
                        "ogtm": "Material object type",
                        "ldct": "Category",
                        "ldcn": "Denomination",
                        "cassetta": "Box number",
                        "stato_conservazione": "Conservation state",
                        "stato_reperto": "Find state",
                        "descrizione": "Description",
                        "materiale": "Material",
                        "note": "Notes",
                        "misure": "Measurements",
                        "cronologia": "Chronology",
                        "riferimenti_bibliografici": "Bibliographic references",
                        "quantita": "Quantity",
                        "unita_misura": "Unit of measurement"
                    },
                    "relationships": {
                        "us_table": "sito/area/us -> us_table",
                        "tma_materiali_ripetibili": "One-to-many via id_tma"
                    }
                },
                "tma_materiali_ripetibili": {
                    "description": "Repeatable materials linked to TMA",
                    "primary_key": "id",
                    "foreign_key": "id_tma",
                    "fields": {
                        "id_tma": "Foreign key to tma_materiali_archeologici",
                        "reperto": "Find",
                        "descrizione": "Description",
                        "quantita": "Quantity",
                        "misure": "Measurements",
                        "note": "Notes"
                    },
                    "relationships": {
                        "tma_materiali_archeologici": "id_tma -> tma_materiali_archeologici.id_tma"
                    }
                },
                "tomba_table": {
                    "description": "Burial records",
                    "primary_key": "id_tomba",
                    "fields": {
                        "sito": "Site name",
                        "nr_scheda_taf": "TAF form number",
                        "sigla_struttura": "Structure abbreviation",
                        "nr_struttura": "Structure number",
                        "nr_individuo": "Individual number",
                        "rito": "Rite",
                        "descrizione_taf": "TAF description",
                        "interpretazione_taf": "TAF interpretation",
                        "segnacoli": "Grave markers",
                        "canale_libatorio_si_no": "Libation channel yes/no",
                        "oggetti_rinvenuti_esterno": "Objects found outside",
                        "stato_di_conservazione": "Conservation state",
                        "copertura_tipo": "Cover type",
                        "tipo_contenitore_resti": "Type of remains container",
                        "orientamento_asse": "Axis orientation",
                        "orientamento_azimut": "Azimuth orientation",
                        "corredo_presenza": "Grave goods presence"
                    }
                },
                "periodizzazione_table": {
                    "description": "Periodization and phasing",
                    "primary_key": "id_perfas",
                    "fields": {
                        "sito": "Site name",
                        "periodo": "Period",
                        "fase": "Phase",
                        "cron_iniziale": "Initial chronology",
                        "cron_finale": "Final chronology",
                        "descrizione": "Description",
                        "datazione_estesa": "Extended dating"
                    }
                },
                "struttura_table": {
                    "description": "Architectural structures",
                    "primary_key": "id_struttura",
                    "fields": {
                        "sito": "Site name",
                        "sigla_struttura": "Structure abbreviation",
                        "numero_struttura": "Structure number",
                        "categoria_struttura": "Structure category",
                        "tipologia_struttura": "Structure typology",
                        "definizione_struttura": "Structure definition",
                        "descrizione": "Description",
                        "interpretazione": "Interpretation",
                        "periodo_iniziale": "Initial period",
                        "fase_iniziale": "Initial phase",
                        "periodo_finale": "Final period",
                        "fase_finale": "Final phase",
                        "datazione_estesa": "Extended dating"
                    }
                }
            },
            "relationships_summary": {
                "hierarchical": [
                    "site_table -> us_table (one-to-many)",
                    "us_table -> inventario_materiali_table (one-to-many)",
                    "us_table -> pottery_table (one-to-many)",
                    "us_table -> tma_materiali_archeologici (one-to-many)",
                    "tma_materiali_archeologici -> tma_materiali_ripetibili (one-to-many)"
                ],
                "referential": [
                    "periodizzazione_table references site_table",
                    "struttura_table references site_table",
                    "tomba_table references site_table"
                ]
            },
            "key_concepts": {
                "stratigraphic_relationships": "US tables contain stratigraphic relationships between units",
                "material_culture": "Materials are cataloged in inventario_materiali, pottery, and TMA tables",
                "chronology": "Periodization table defines chronological phases",
                "spatial_organization": "Areas and sectors organize excavation spatially",
                "conservation": "Multiple tables track conservation status of finds"
            }
        }

    @staticmethod
    def get_schema_prompt():
        """
        Returns a natural language description of the schema for AI prompts
        """
        return """
COMPLETE DATABASE SCHEMA KNOWLEDGE:

The PyArchInit database is an archaeological excavation management system with the following structure:

CORE TABLES:
1. **site_table**: Master site registry
   - Primary key: id_sito
   - Contains: site name, location (country, region, municipality), description

2. **us_table**: Stratigraphic Units (core archaeological data)
   - Primary key: id_us
   - Links to: site_table via 'sito' field
   - Contains: area, unit number, descriptions, interpretations, dating, excavation details
   - Relationships: rapporti field contains stratigraphic relationships between units

3. **inventario_materiali_table**: General finds inventory
   - Primary key: id_invmat
   - Links to: us_table via sito/area/us combination
   - Contains: inventory numbers, find types, descriptions, conservation, storage

4. **pottery_table**: Specialized pottery catalog
   - Primary key: id_pottery
   - Links to: us_table via sito/area/us
   - Contains: typology, fabric, forms, decorations, measurements

5. **tma_materiali_archeologici**: Archaeological materials typology
   - Primary key: id_tma
   - Links to: us_table via sito/area/us
   - Contains: material types (ogtm), categories (ldct), denominations (ldcn)
   - Has child table: tma_materiali_ripetibili

6. **tma_materiali_ripetibili**: Repeatable materials for TMA
   - Foreign key: id_tma links to tma_materiali_archeologici
   - Contains: individual find details, quantities, measurements
   - Multiple records can exist for one TMA entry

7. **tomba_table**: Burial records
   - Links to: site_table
   - Contains: burial rites, orientation, grave goods, conservation

8. **periodizzazione_table**: Chronological periods and phases
   - Links to: site_table
   - Defines: temporal framework for the site

9. **struttura_table**: Architectural structures
   - Links to: site_table
   - Contains: structure types, categories, interpretations

KEY RELATIONSHIPS:
- Site → US → Materials (hierarchical)
- TMA → TMA_Ripetibili (parent-child, one-to-many)
- US units have stratigraphic relationships stored in 'rapporti' field
- All material finds link back to their stratigraphic context

IMPORTANT FIELDS FOR QUERIES:
- sito: Site identifier (present in all tables)
- area: Excavation area
- us: Stratigraphic unit number
- periodo/fase: Chronological markers
- stato_conservazione: Conservation status
- cassetta/nr_cassa: Storage box numbers

When querying this database:
1. Always join tables through their relationships
2. TMA data requires joining both tma_materiali_archeologici and tma_materiali_ripetibili
3. Material culture includes inventario_materiali, pottery, and TMA tables
4. Chronology is defined in periodizzazione_table and referenced in us_table and struttura_table
"""

    @staticmethod
    def get_table_mapping():
        """
        Returns the mapping between UI names and database table names
        """
        return {
            'us_table': 'US',  # Maps to US entity
            'materials': 'INVENTARIO_MATERIALI',
            'pottery': 'POTTERY',
            'tma_table': 'TMA',  # Maps to tma_materiali_archeologici
            'tma_materials': 'TMA_MATERIALI',  # Maps to tma_materiali_ripetibili
            'site': 'SITE',
            'period': 'PERIODIZZAZIONE',
            'structure': 'STRUTTURA',
            'tomb': 'TOMBA'
        }

    @staticmethod
    def get_query_examples():
        """
        Returns example queries that demonstrate the schema relationships
        """
        return {
            "find_materials_by_us": """
                SELECT im.* FROM inventario_materiali_table im
                WHERE im.sito = ? AND im.area = ? AND im.us = ?
            """,
            "get_tma_with_materials": """
                SELECT t.*, tm.*
                FROM tma_materiali_archeologici t
                LEFT JOIN tma_materiali_ripetibili tm ON t.id_tma = tm.id_tma
                WHERE t.sito = ?
            """,
            "stratigraphic_sequence": """
                SELECT u1.us as unit, u1.rapporti, u2.us as related_unit
                FROM us_table u1
                LEFT JOIN us_table u2 ON u1.sito = u2.sito AND u1.area = u2.area
                WHERE u1.sito = ? AND u1.area = ?
            """,
            "materials_by_period": """
                SELECT p.periodo, p.fase, COUNT(im.id_invmat) as material_count
                FROM periodizzazione_table p
                JOIN us_table u ON p.sito = u.sito
                    AND p.periodo = u.periodo_iniziale
                    AND p.fase = u.fase_iniziale
                LEFT JOIN inventario_materiali_table im ON u.sito = im.sito
                    AND u.area = im.area
                    AND u.us = im.us
                WHERE p.sito = ?
                GROUP BY p.periodo, p.fase
            """
        }

    @classmethod
    def enhance_ai_prompt_with_schema(cls, base_prompt):
        """
        Enhances an AI prompt with schema knowledge

        Args:
            base_prompt: The original prompt

        Returns:
            Enhanced prompt with schema context
        """
        schema_context = cls.get_schema_prompt()

        enhanced = f"""
{schema_context}

CURRENT TASK:
{base_prompt}

Remember to:
1. Use the correct table and field names from the schema
2. Consider relationships between tables
3. For TMA data, always check both tma_materiali_archeologici and tma_materiali_ripetibili
4. Use appropriate joins when data spans multiple tables
"""
        return enhanced