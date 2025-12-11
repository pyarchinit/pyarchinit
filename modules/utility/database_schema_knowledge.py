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
            "description": "Archaeological excavation database system with GIS support",
            "tables": {
                # ==================== MAIN DATA TABLES ====================
                "site_table": {
                    "description": "Archaeological sites registry",
                    "primary_key": "id_sito",
                    "has_geometry": False,
                    "fields": {
                        "id_sito": "Primary key ID",
                        "sito": "Site name (unique identifier used across all tables)",
                        "nazione": "Country/Nation",
                        "regione": "Region",
                        "comune": "Municipality/Town",
                        "provincia": "Province",
                        "descrizione": "Site description",
                        "definizione_sito": "Site type definition",
                        "sito_path": "Path to site files",
                        "find_check": "Find check flag"
                    }
                },
                "us_table": {
                    "description": "Stratigraphic Units (US) - main excavation data",
                    "primary_key": "id_us",
                    "has_geometry": False,
                    "fields": {
                        "id_us": "Primary key ID",
                        "sito": "Site name (FK to site_table)",
                        "area": "Excavation area",
                        "us": "Stratigraphic unit number",
                        "d_stratigrafica": "Stratigraphic definition",
                        "d_interpretativa": "Interpretative definition",
                        "descrizione": "Description",
                        "interpretazione": "Interpretation",
                        "periodo_iniziale": "Initial period number",
                        "fase_iniziale": "Initial phase number",
                        "periodo_finale": "Final period number",
                        "fase_finale": "Final phase number",
                        "scavato": "Excavated status (Si/No)",
                        "attivita": "Activity type",
                        "anno_scavo": "Excavation year",
                        "metodo_di_scavo": "Excavation method",
                        "inclusi": "Inclusions",
                        "campioni": "Samples",
                        "rapporti": "Stratigraphic relationships (JSON array)",
                        "data_schedatura": "Recording date",
                        "schedatore": "Recorder name",
                        "formazione": "Formation process",
                        "stato_di_conservazione": "Conservation state",
                        "colore": "Color",
                        "consistenza": "Consistency",
                        "struttura": "Associated structure",
                        "cont_per": "Period container",
                        "order_layer": "Layer order for Harris Matrix",
                        "documentazione": "Documentation references",
                        "unita_tipo": "Unit type (US/USM)",
                        "settore": "Sector",
                        "quad_par": "Square/Parcel",
                        "ambient": "Environment/Room",
                        "saggio": "Test trench",
                        "elem_datanti": "Dating elements",
                        "osservazioni": "Observations/Notes",
                        "datazione": "Dating",
                        "quota_min_abs": "Minimum absolute elevation",
                        "quota_max_abs": "Maximum absolute elevation",
                        "quota_min_rel": "Minimum relative elevation",
                        "quota_max_rel": "Maximum relative elevation",
                        "lunghezza_max": "Maximum length",
                        "altezza_max": "Maximum height",
                        "altezza_min": "Minimum height",
                        "profondita_max": "Maximum depth",
                        "profondita_min": "Minimum depth",
                        "larghezza_media": "Average width",
                        "quota_min_usm": "USM minimum elevation",
                        "quota_max_usm": "USM maximum elevation",
                        "lunghezza_usm": "USM length",
                        "altezza_usm": "USM height",
                        "spessore_usm": "USM thickness",
                        "tecnica_muraria_usm": "USM wall technique",
                        "modulo_usm": "USM module"
                    },
                    "relationships": {
                        "site_table": "sito -> site_table.sito",
                        "inventario_materiali_table": "One-to-many via sito/area/us",
                        "pottery_table": "One-to-many via sito/area/us",
                        "tma_table": "One-to-many via sito/area/us",
                        "periodizzazione_table": "periodo/fase links",
                        "pyus_table": "Geometry in pyarchinit_us_view"
                    }
                },
                "inventario_materiali_table": {
                    "description": "Material finds inventory - general archaeological finds",
                    "primary_key": "id_invmat",
                    "has_geometry": False,
                    "fields": {
                        "id_invmat": "Primary key ID",
                        "sito": "Site name",
                        "numero_inventario": "Inventory number",
                        "tipo_reperto": "Find type (ceramica, metallo, osso, vetro, etc.)",
                        "criterio_schedatura": "Recording criteria",
                        "definizione": "Definition/Classification",
                        "descrizione": "Description",
                        "area": "Excavation area",
                        "us": "Stratigraphic unit number",
                        "lavato": "Washed status (Si/No)",
                        "nr_cassa": "Box/Crate number",
                        "luogo_conservazione": "Storage location",
                        "stato_conservazione": "Conservation state",
                        "datazione_reperto": "Find dating",
                        "elementi_reperto": "Find elements (JSON)",
                        "misurazioni": "Measurements (JSON)",
                        "rif_biblio": "Bibliographic references",
                        "tecnologie": "Technologies",
                        "forme_minime": "Minimum forms (MNI)",
                        "forme_massime": "Maximum forms",
                        "totale_frammenti": "Total fragments count",
                        "corpo_ceramico": "Ceramic body type",
                        "rivestimento": "Coating/Slip",
                        "diametro_orlo": "Rim diameter",
                        "peso": "Weight in grams",
                        "tipo": "Type classification",
                        "eve_orlo": "EVE rim percentage",
                        "repertato": "Catalogued status (Si/No)",
                        "diagnostico": "Diagnostic piece (Si/No)",
                        "n_reperto": "Find number",
                        "tipo_contenitore": "Container type",
                        "struttura": "Associated structure",
                        "years": "Year of excavation"
                    }
                },
                "pottery_table": {
                    "description": "Pottery catalog - detailed ceramics database",
                    "primary_key": "id_rep",
                    "has_geometry": False,
                    "fields": {
                        "id_rep": "Primary key ID",
                        "id_number": "Pottery ID number",
                        "sito": "Site name",
                        "area": "Excavation area",
                        "us": "Stratigraphic unit number",
                        "box": "Storage box number",
                        "photo": "Photo reference",
                        "drawing": "Drawing reference",
                        "anno": "Year of excavation/discovery - USE THIS FOR YEAR QUERIES",
                        "fabric": "Fabric type/clay composition",
                        "percent": "Percentage of vessel preserved",
                        "material": "Material type",
                        "form": "General vessel form (bowl, jar, plate, amphora, etc.)",
                        "specific_form": "Specific form variant",
                        "specific_shape": "Detailed shape description - USE FOR SHAPE QUERIES",
                        "ware": "Ware type (coarse ware, fine ware, cooking ware, etc.)",
                        "munsell": "Munsell color code",
                        "surf_trat": "Surface treatment",
                        "exdeco": "External decoration type",
                        "intdeco": "Internal decoration type",
                        "wheel_made": "Wheel made (yes/no)",
                        "descrip_ex_deco": "External decoration description",
                        "descrip_in_deco": "Internal decoration description",
                        "note": "Notes",
                        "diametro_max": "Maximum diameter (cm)",
                        "qty": "Quantity of sherds",
                        "diametro_rim": "Rim diameter (cm)",
                        "diametro_bottom": "Bottom diameter (cm)",
                        "diametro_height": "Height (cm)",
                        "diametro_preserved": "Preserved height (cm)",
                        "bag": "Bag number",
                        "sector": "Excavation sector"
                    },
                    "query_hints": {
                        "year_filter": "Use 'anno' field for year-based queries",
                        "form_filter": "Use 'form', 'specific_form', or 'specific_shape' for form queries",
                        "us_filter": "Use 'us' field for stratigraphic unit queries",
                        "ware_filter": "Use 'ware' field for ware type queries"
                    }
                },
                "tma_table": {
                    "description": "TMA - Tipologia Materiali Archeologici (Archaeological Materials Typology)",
                    "primary_key": "id",
                    "has_geometry": False,
                    "fields": {
                        "id": "Primary key ID (also called id_tma)",
                        "sito": "Site name",
                        "area": "Excavation area",
                        "localita": "Locality",
                        "settore": "Sector",
                        "inventario": "Inventory reference",
                        "ogtm": "Material object type (OGTM code)",
                        "ldct": "Category (LDCT)",
                        "ldcn": "Denomination (LDCN)",
                        "vecchia_collocazione": "Previous location",
                        "cassetta": "Box/Crate number",
                        "scan": "Scan reference",
                        "saggio": "Test trench",
                        "vano_locus": "Room/Locus",
                        "dscd": "Description date",
                        "dscu": "Description unit",
                        "rcgd": "Recovery date",
                        "rcgz": "Recovery zone",
                        "aint": "Internal analysis",
                        "aind": "Individual analysis",
                        "dtzg": "General dating",
                        "deso": "Object description",
                        "nsc": "NSC code",
                        "ftap": "Photo type",
                        "ftan": "Photo number",
                        "drat": "Drawing type",
                        "dran": "Drawing number",
                        "draa": "Drawing author",
                        "quantita": "Quantity"
                    }
                },
                "struttura_table": {
                    "description": "Archaeological structures",
                    "primary_key": "id_struttura",
                    "has_geometry": False,
                    "fields": {
                        "id_struttura": "Primary key ID",
                        "sito": "Site name",
                        "sigla_struttura": "Structure abbreviation (e.g., STR, MR)",
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
                        "datazione_estesa": "Extended dating text",
                        "materiali_impiegati": "Materials used",
                        "elementi_strutturali": "Structural elements",
                        "rapporti_struttura": "Structure relationships",
                        "misure_struttura": "Structure measurements"
                    }
                },
                "tomba_table": {
                    "description": "Burials/Tombs database - funerary contexts",
                    "primary_key": "id_tomba",
                    "has_geometry": False,
                    "fields": {
                        "id_tomba": "Primary key ID",
                        "sito": "Site name",
                        "area": "Excavation area",
                        "nr_scheda_taf": "Taphonomic sheet number",
                        "sigla_struttura": "Structure abbreviation",
                        "nr_struttura": "Structure number",
                        "nr_individuo": "Individual number",
                        "rito": "Burial rite (inumazione, cremazione, etc.)",
                        "descrizione_taf": "Taphonomic description",
                        "interpretazione_taf": "Taphonomic interpretation",
                        "segnacoli": "Grave markers",
                        "canale_libatorio_si_no": "Libation channel (Si/No)",
                        "oggetti_rinvenuti_esterno": "Objects found outside tomb",
                        "stato_di_conservazione": "Conservation state",
                        "copertura_tipo": "Cover type",
                        "tipo_contenitore_resti": "Remains container type",
                        "tipo_deposizione": "Deposition type (primaria, secondaria)",
                        "tipo_sepoltura": "Burial type (fossa, cassa, etc.)",
                        "orientamento_asse": "Axis orientation (N-S, E-W, etc.)",
                        "orientamento_azimut": "Azimuth orientation in degrees",
                        "corredo_presenza": "Grave goods presence (Si/No)",
                        "corredo_tipo": "Grave goods type",
                        "corredo_descrizione": "Grave goods description",
                        "lunghezza_scheletro": "Skeleton length",
                        "posizione_scheletro": "Skeleton position (supino, prono, etc.)",
                        "posizione_cranio": "Skull position",
                        "posizione_arti_superiori": "Upper limbs position",
                        "posizione_arti_inferiori": "Lower limbs position",
                        "completo_si_no": "Complete (Si/No)",
                        "disturbato_si_no": "Disturbed (Si/No)",
                        "in_connessione_si_no": "In connection (Si/No)",
                        "caratteristiche": "Characteristics",
                        "periodo_iniziale": "Initial period",
                        "fase_iniziale": "Initial phase",
                        "periodo_finale": "Final period",
                        "fase_finale": "Final phase",
                        "datazione_estesa": "Extended dating",
                        "misure_tomba": "Tomb measurements"
                    }
                },
                "periodizzazione_table": {
                    "description": "Periodization - chronological phases definition",
                    "primary_key": "id_perfas",
                    "has_geometry": False,
                    "fields": {
                        "id_perfas": "Primary key ID",
                        "sito": "Site name",
                        "periodo": "Period number",
                        "fase": "Phase number",
                        "cron_iniziale": "Initial chronology (year, negative for BC)",
                        "cron_finale": "Final chronology (year, negative for BC)",
                        "descrizione": "Period/Phase description",
                        "datazione_estesa": "Extended dating text (e.g., 'II sec. a.C.')",
                        "cont_per": "Period container/grouping"
                    }
                },
                "campioni_table": {
                    "description": "Samples database - scientific samples",
                    "primary_key": "id_campione",
                    "has_geometry": False,
                    "fields": {
                        "id_campione": "Primary key ID",
                        "sito": "Site name",
                        "nr_campione": "Sample number",
                        "tipo_campione": "Sample type (C14, polline, carbone, terra, etc.)",
                        "descrizione": "Description",
                        "area": "Excavation area",
                        "us": "Stratigraphic unit number",
                        "numero_inventario_materiale": "Material inventory number",
                        "nr_cassa": "Box/Crate number",
                        "luogo_conservazione": "Storage location"
                    }
                },
                "documentazione_table": {
                    "description": "Documentation records - photos, drawings, plans",
                    "primary_key": "id_documentazione",
                    "has_geometry": False,
                    "fields": {
                        "id_documentazione": "Primary key ID",
                        "sito": "Site name",
                        "nome_doc": "Document name/number",
                        "data": "Date",
                        "tipo_documentazione": "Documentation type (foto, pianta, sezione, prospetto)",
                        "sorgente": "Source (digitale, analogico)",
                        "scala": "Scale (1:20, 1:50, etc.)",
                        "disegnatore": "Drawer/Author",
                        "note": "Notes"
                    }
                },
                "schedaind_table": {
                    "description": "Individual sheets - anthropological/osteological data",
                    "primary_key": "id_scheda_ind",
                    "has_geometry": False,
                    "fields": {
                        "id_scheda_ind": "Primary key ID",
                        "sito": "Site name",
                        "area": "Excavation area",
                        "us": "Stratigraphic unit number",
                        "nr_individuo": "Individual number",
                        "data_schedatura": "Recording date",
                        "schedatore": "Recorder name",
                        "sesso": "Sex (M/F/Indeterminato)",
                        "eta_min": "Minimum estimated age",
                        "eta_max": "Maximum estimated age",
                        "classi_eta": "Age class (infans, juvenis, adulto, senile)",
                        "osservazioni": "Observations",
                        "sigla_struttura": "Structure abbreviation",
                        "nr_struttura": "Structure number",
                        "completo_si_no": "Complete (Si/No)",
                        "disturbato_si_no": "Disturbed (Si/No)",
                        "in_connessione_si_no": "In anatomical connection (Si/No)",
                        "lunghezza_scheletro": "Skeleton length",
                        "posizione_scheletro": "Skeleton position",
                        "posizione_cranio": "Skull position",
                        "posizione_arti_superiori": "Upper limbs position",
                        "posizione_arti_inferiori": "Lower limbs position",
                        "orientamento_asse": "Axis orientation",
                        "orientamento_azimut": "Azimuth orientation"
                    }
                },
                "archeozoology_table": {
                    "description": "Archaeozoology - faunal remains analysis",
                    "primary_key": "id_archzoo",
                    "has_geometry": False,
                    "fields": {
                        "id_archzoo": "Primary key ID",
                        "sito": "Site name",
                        "area": "Excavation area",
                        "us": "Stratigraphic unit number",
                        "quadrato": "Square/grid reference",
                        "coord_x": "X coordinate",
                        "coord_y": "Y coordinate",
                        "coord_z": "Z coordinate (depth)",
                        "bos_bison": "Bos/Bison count",
                        "calcinati": "Calcined bones count",
                        "camoscio": "Chamois count",
                        "capriolo": "Roe deer count",
                        "cervo": "Red deer count",
                        "combusto": "Burnt bones count",
                        "coni": "Rabbit count",
                        "pdi": "Identifiable pieces count",
                        "stambecco": "Ibex count",
                        "strie": "Cut marks count",
                        "canidi": "Canids count",
                        "ursidi": "Bears count",
                        "megacero": "Giant deer count"
                    }
                },
                "ut_table": {
                    "description": "UT - Unità Topografiche (Topographic Units) for survey",
                    "primary_key": "id_ut",
                    "has_geometry": False,
                    "fields": {
                        "id_ut": "Primary key ID",
                        "progetto": "Project name",
                        "nr_ut": "UT number",
                        "ut_letterale": "UT literal name",
                        "def_ut": "UT definition",
                        "descrizione_ut": "UT description",
                        "interpretazione_ut": "UT interpretation",
                        "nazione": "Country",
                        "regione": "Region",
                        "provincia": "Province",
                        "comune": "Municipality",
                        "frazione": "Hamlet",
                        "localita": "Locality",
                        "indirizzo": "Address",
                        "nr_civico": "Street number",
                        "carta_topo_igm": "IGM topographic map",
                        "carta_ctr": "CTR map reference",
                        "coord_geografiche": "Geographic coordinates",
                        "coord_piane": "Planar coordinates",
                        "quota": "Elevation",
                        "andamento_terreno_pendenza": "Terrain slope",
                        "utilizzo_suolo_vegetazione": "Land use/vegetation",
                        "descrizione_empirica_suolo": "Soil description",
                        "descrizione_luogo": "Place description",
                        "metodo_rilievo_e_ricognizione": "Survey method",
                        "geometria": "Geometry type",
                        "bibliografia": "Bibliography",
                        "data": "Date",
                        "ora_meteo": "Time and weather",
                        "responsabile": "Responsible person",
                        "dimensioni_ut": "UT dimensions",
                        "rep_per_mq": "Finds per square meter",
                        "rep_datanti": "Dating finds",
                        "periodo_I": "Period I",
                        "datazione_I": "Dating I",
                        "interpretazione_I": "Interpretation I",
                        "periodo_II": "Period II",
                        "datazione_II": "Dating II",
                        "interpretazione_II": "Interpretation II",
                        "documentazione": "Documentation",
                        "enti_tutela_vincoli": "Protection authorities/constraints",
                        "indagini_preliminari": "Preliminary investigations"
                    }
                },

                # ==================== MEDIA TABLES ====================
                "media_table": {
                    "description": "Media files registry - images and documents",
                    "primary_key": "id_media",
                    "has_geometry": False,
                    "fields": {
                        "id_media": "Primary key ID",
                        "mediatype": "Media type (image, video, document)",
                        "filename": "File name",
                        "filetype": "File type/extension",
                        "filepath": "Full file path",
                        "descrizione": "Description",
                        "tags": "Tags for search"
                    }
                },
                "mediatoentity_table": {
                    "description": "Links media to database entities",
                    "has_geometry": False,
                    "fields": {
                        "id_mediaToEntity": "Primary key ID",
                        "id_entity": "Entity ID",
                        "entity_type": "Entity type (US, CERAMICA, REPERTO, TOMBA, etc.)",
                        "id_media": "Media ID (FK to media_table)"
                    }
                },
                "media_thumb_table": {
                    "description": "Media thumbnails",
                    "primary_key": "id_media_thumb",
                    "has_geometry": False,
                    "fields": {
                        "id_media_thumb": "Primary key ID",
                        "id_media": "Media ID (FK)",
                        "mediatype": "Media type",
                        "media_filename": "Original filename",
                        "media_thumb_filename": "Thumbnail filename",
                        "filetype": "File type",
                        "filepath": "Thumbnail file path"
                    }
                },

                # ==================== GEOMETRY TABLES (GIS) ====================
                "pyus_table": {
                    "description": "US Geometry - polygons for stratigraphic units (pyarchinit_us_view)",
                    "primary_key": "gid",
                    "has_geometry": True,
                    "geometry_type": "Polygon/MultiPolygon",
                    "fields": {
                        "gid": "Primary key ID",
                        "area_s": "Area code",
                        "scavo_s": "Excavation/Site name",
                        "us_s": "US number",
                        "stratigraph_index_us": "Stratigraphic index",
                        "tipo_us_s": "US type",
                        "rilievo_originale": "Original survey",
                        "disegnatore": "Drawer",
                        "data": "Date",
                        "tipo_doc": "Document type",
                        "nome_doc": "Document name",
                        "coord": "Coordinates",
                        "unita_tipo_s": "Unit type (US/USM)",
                        "the_geom": "Geometry column (PostGIS/Sketches)"
                    }
                },
                "pyquote_table": {
                    "description": "Elevation points - spot heights (pyarchinit_quote_view)",
                    "primary_key": "id",
                    "has_geometry": True,
                    "geometry_type": "Point",
                    "fields": {
                        "id": "Primary key ID",
                        "sito_q": "Site name",
                        "area_q": "Area code",
                        "us_q": "US number",
                        "unita_misu_q": "Measurement unit (m slm, m)",
                        "quota_q": "Elevation value",
                        "data": "Date",
                        "disegnatore": "Surveyor",
                        "rilievo_originale": "Original survey",
                        "unita_tipo_q": "Unit type",
                        "the_geom": "Point geometry"
                    }
                },
                "pyreperti_table": {
                    "description": "Finds geometry - point locations of artifacts",
                    "primary_key": "id",
                    "has_geometry": True,
                    "geometry_type": "Point",
                    "fields": {
                        "id": "Primary key ID",
                        "id_rep": "Find ID/inventory number",
                        "siti": "Site name",
                        "link": "Link to find record",
                        "the_geom": "Point geometry"
                    }
                },
                "pystrutture_table": {
                    "description": "Structure geometry - polygons for structures",
                    "primary_key": "id",
                    "has_geometry": True,
                    "geometry_type": "Polygon",
                    "fields": {
                        "id": "Primary key ID",
                        "sito": "Site name",
                        "id_strutt": "Structure ID",
                        "per_iniz": "Initial period",
                        "per_fin": "Final period",
                        "dataz_ext": "Extended dating",
                        "fase_iniz": "Initial phase",
                        "fase_fin": "Final phase",
                        "descrizione": "Description",
                        "sigla_strut": "Structure abbreviation",
                        "nr_strut": "Structure number",
                        "the_geom": "Polygon geometry"
                    }
                },
                "pytomba_table": {
                    "description": "Tomb geometry - polygons for burials",
                    "primary_key": "id",
                    "has_geometry": True,
                    "geometry_type": "Polygon",
                    "fields": {
                        "id": "Primary key ID",
                        "sito": "Site name",
                        "nr_scheda": "Sheet number",
                        "the_geom": "Polygon geometry"
                    }
                },
                "pysito_point_table": {
                    "description": "Site points - point locations of sites",
                    "primary_key": "gid",
                    "has_geometry": True,
                    "geometry_type": "Point",
                    "fields": {
                        "gid": "Primary key ID",
                        "sito_nome": "Site name",
                        "the_geom": "Point geometry"
                    }
                },
                "pysito_polygon_table": {
                    "description": "Site polygons - area extent of sites",
                    "primary_key": "gid",
                    "has_geometry": True,
                    "geometry_type": "Polygon",
                    "fields": {
                        "gid": "Primary key ID",
                        "sito_nome": "Site name",
                        "the_geom": "Polygon geometry"
                    }
                },
                "pysezioni_table": {
                    "description": "Sections - line geometry for section drawings",
                    "primary_key": "gid",
                    "has_geometry": True,
                    "geometry_type": "LineString",
                    "fields": {
                        "gid": "Primary key ID",
                        "id_sezione": "Section ID",
                        "sito": "Site name",
                        "area": "Area",
                        "descr": "Description",
                        "the_geom": "Line geometry"
                    }
                },
                "pylineeriferimento_table": {
                    "description": "Reference lines - baseline and reference geometry",
                    "primary_key": "gid",
                    "has_geometry": True,
                    "geometry_type": "LineString",
                    "fields": {
                        "gid": "Primary key ID",
                        "sito": "Site name",
                        "descr": "Description",
                        "the_geom": "Line geometry"
                    }
                },
                "pyripartizioni_spaziali_table": {
                    "description": "Spatial partitions - excavation grid and areas",
                    "primary_key": "gid",
                    "has_geometry": True,
                    "geometry_type": "Polygon",
                    "fields": {
                        "gid": "Primary key ID",
                        "id_ripartizione": "Partition ID",
                        "sito": "Site name",
                        "descr": "Description",
                        "the_geom": "Polygon geometry"
                    }
                },
                "pycampioni_table": {
                    "description": "Sample points - locations of scientific samples",
                    "primary_key": "gid",
                    "has_geometry": True,
                    "geometry_type": "Point",
                    "fields": {
                        "gid": "Primary key ID",
                        "id_campione": "Sample ID",
                        "sito": "Site name",
                        "tipo_campione": "Sample type",
                        "the_geom": "Point geometry"
                    }
                },
                "pydocumentazione_table": {
                    "description": "Documentation points - locations of photos/drawings",
                    "primary_key": "gid",
                    "has_geometry": True,
                    "geometry_type": "Point",
                    "fields": {
                        "gid": "Primary key ID",
                        "id_doc": "Document ID",
                        "sito": "Site name",
                        "nome_doc": "Document name",
                        "tipo_doc": "Document type",
                        "the_geom": "Point geometry"
                    }
                },
                "pyindividui_table": {
                    "description": "Individual points - locations of skeletal remains",
                    "primary_key": "gid",
                    "has_geometry": True,
                    "geometry_type": "Point",
                    "fields": {
                        "gid": "Primary key ID",
                        "id_individuo": "Individual ID",
                        "sito": "Site name",
                        "the_geom": "Point geometry"
                    }
                }
            }
        }

    @staticmethod
    def get_schema_prompt():
        """
        Returns a text prompt describing the database schema for AI context
        """
        schema = DatabaseSchemaKnowledge.get_full_schema()

        prompt = f"""
=== DATABASE SCHEMA: {schema['database_name']} ===
{schema['description']}

"""
        # Group tables by type
        main_tables = []
        geo_tables = []
        media_tables = []

        for table_name, table_info in schema['tables'].items():
            if table_info.get('has_geometry'):
                geo_tables.append((table_name, table_info))
            elif 'media' in table_name.lower():
                media_tables.append((table_name, table_info))
            else:
                main_tables.append((table_name, table_info))

        # Main data tables
        prompt += "=== TABELLE DATI PRINCIPALI ===\n"
        for table_name, table_info in main_tables:
            prompt += f"\n### {table_name.upper()}\n"
            prompt += f"Descrizione: {table_info['description']}\n"
            if 'primary_key' in table_info:
                prompt += f"Chiave primaria: {table_info['primary_key']}\n"
            prompt += "Campi:\n"
            for field_name, field_desc in list(table_info.get('fields', {}).items())[:15]:  # Limit fields shown
                prompt += f"  - {field_name}: {field_desc}\n"
            if len(table_info.get('fields', {})) > 15:
                prompt += f"  ... e altri {len(table_info['fields']) - 15} campi\n"
            if 'query_hints' in table_info:
                prompt += "Query hints:\n"
                for hint_name, hint_desc in table_info['query_hints'].items():
                    prompt += f"  - {hint_desc}\n"

        # Geometry tables summary
        prompt += "\n=== TABELLE GEOMETRICHE (GIS) ===\n"
        for table_name, table_info in geo_tables:
            prompt += f"- {table_name}: {table_info['description']} ({table_info.get('geometry_type', 'geometry')})\n"

        # Media tables summary
        prompt += "\n=== TABELLE MEDIA ===\n"
        for table_name, table_info in media_tables:
            prompt += f"- {table_name}: {table_info['description']}\n"

        prompt += """

=== NOTE IMPORTANTI ===
1. Tutte le tabelle usano 'sito' come chiave esterna principale
2. Le US sono collegate ai materiali tramite la combinazione sito/area/us
3. Per query su pottery/ceramica: usa 'anno' per l'anno, 'form'/'specific_form'/'specific_shape' per le forme
4. Per query sui materiali: usa 'tipo_reperto' per il tipo, 'definizione' per la classificazione
5. Le tabelle PY* contengono le geometrie GIS collegate alle tabelle dati
6. I media sono collegati alle entità tramite mediatoentity_table con entity_type (US, CERAMICA, REPERTO, etc.)
"""
        return prompt

    @staticmethod
    def get_table_list():
        """Returns list of all table names"""
        return list(DatabaseSchemaKnowledge.get_full_schema()['tables'].keys())

    @staticmethod
    def get_table_fields(table_name):
        """Returns fields for a specific table"""
        schema = DatabaseSchemaKnowledge.get_full_schema()
        # Try exact match first
        if table_name in schema['tables']:
            return schema['tables'][table_name].get('fields', {})
        # Try with _table suffix
        table_key = table_name.lower() + '_table' if not table_name.endswith('_table') else table_name.lower()
        if table_key in schema['tables']:
            return schema['tables'][table_key].get('fields', {})
        return {}

    @staticmethod
    def get_geometry_tables():
        """Returns list of tables with geometry"""
        schema = DatabaseSchemaKnowledge.get_full_schema()
        return [name for name, info in schema['tables'].items() if info.get('has_geometry')]
