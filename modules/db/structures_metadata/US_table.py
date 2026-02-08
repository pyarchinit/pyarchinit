'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, String, Text, Numeric, UniqueConstraint


# Table representing stratigraphic units (Unità Stratigrafiche - US)
class US_table:
    @classmethod
    def define_table(cls, metadata):
        return Table('us_table', metadata,
                     # Unique identifier for each stratigraphic unit
                     Column('id_us', Integer, primary_key=True),

                     # Archaeological site name
                     Column('sito', Text),

                     # Excavation area within the site
                     Column('area', String(20)),

                     # Stratigraphic unit number
                     Column('us', Integer),

                     # Stratigraphic definition/classification
                     Column('d_stratigrafica', String(255)),

                     # Interpretative definition of the stratigraphic unit
                     Column('d_interpretativa', String(255)),

                     # Detailed description of the stratigraphic unit
                     Column('descrizione', Text),

                     # Archaeological interpretation of the unit
                     Column('interpretazione', Text),

                     # Initial chronological period
                     Column('periodo_iniziale', String(4)),

                     # Initial phase within the period
                     Column('fase_iniziale', String(4)),

                     # Final chronological period
                     Column('periodo_finale', String(4)),

                     # Final phase within the period
                     Column('fase_finale', String(4)),

                     # Indicates if the unit has been excavated (Yes/No)
                     Column('scavato', String(2)),

                     # Activity reference number
                     Column('attivita', String(4)),

                     # Year of excavation
                     Column('anno_scavo', String(4)),

                     # Excavation methodology used
                     Column('metodo_di_scavo', String(20)),

                     # Inclusions found in the stratigraphic unit
                     Column('inclusi', Text),

                     # Samples taken from the unit
                     Column('campioni', Text),

                     # Stratigraphic relationships with other units
                     Column('rapporti', Text),

                     # Date when the form was compiled
                     Column('data_schedatura', String(20)),

                     # Name of the person who compiled the form
                     Column('schedatore', String(25)),

                     # Formation process of the stratigraphic unit
                     Column('formazione', String(20)),

                     # State of preservation
                     Column('stato_di_conservazione', String(20)),

                     # Color of the soil/structure
                     Column('colore', String(20)),

                     # Consistency of the soil/structure
                     Column('consistenza', String(20)),

                     # Type of structure
                     Column('struttura', String(30)),

                     # Periodized context
                     Column('cont_per', String(200)),

                     # Layer order
                     Column('order_layer', Integer),

                     # Associated documentation
                     Column('documentazione', Text),

                     # Type of unit (added for USM - Masonry Stratigraphic Unit)
                     Column('unita_tipo', Text),

                     # Excavation sector
                     Column('settore', Text),

                     # Square/parcel reference
                     Column('quad_par', Text),

                     # Environment/room
                     Column('ambient', Text),

                     # Test pit
                     Column('saggio', Text),

                     # Dating elements
                     Column('elem_datanti', Text),

                     # Static function (for masonry units)
                     Column('funz_statica', Text),

                     # Type of workmanship
                     Column('lavorazione', Text),

                     # Joint thickness
                     Column('spess_giunti', Text),

                     # Laying beds
                     Column('letti_posa', Text),

                     # Module height
                     Column('alt_mod', Text),

                     # Building unit summary
                     Column('un_ed_riass', Text),

                     # Reuse
                     Column('reimp', Text),

                     # Construction technique
                     Column('posa_opera', Text),

                     # Minimum elevation of masonry unit
                     Column('quota_min_usm', Numeric(6, 2)),

                     # Maximum elevation of masonry unit
                     Column('quota_max_usm', Numeric(6, 2)),

                     # Binder consistency
                     Column('cons_legante', Text),

                     # Binder color
                     Column('col_legante', Text),

                     # Binder aggregates
                     Column('aggreg_legante', Text),

                     # Material consistency/texture
                     Column('con_text_mat', Text),

                     # Material color
                     Column('col_materiale', Text),

                     # Inclusions in masonry materials
                     Column('inclusi_materiali_usm', Text),

                     # General catalog number
                     Column('n_catalogo_generale', Text),

                     # Internal catalog number
                     Column('n_catalogo_interno', Text),

                     # International catalog number
                     Column('n_catalogo_internazionale', Text),

                     # Superintendence reference
                     Column('soprintendenza', Text),

                     # Relative elevation
                     Column('quota_relativa', Numeric(6, 2)),

                     # Absolute elevation
                     Column('quota_abs', Numeric(6, 2)),

                     # Tomb reference
                     Column('ref_tm', Text),

                     # Archaeological find reference
                     Column('ref_ra', Text),

                     # Numeric reference
                     Column('ref_n', Text),

                     # Position
                     Column('posizione', Text),

                     # Distinction criteria
                     Column('criteri_distinzione', Text),

                     # Formation mode
                     Column('modo_formazione', Text),

                     # Organic components
                     Column('componenti_organici', Text),

                     # Inorganic components
                     Column('componenti_inorganici', Text),

                     # Maximum length
                     Column('lunghezza_max', Numeric(6, 2)),

                     # Maximum height
                     Column('altezza_max', Numeric(6, 2)),

                     # Minimum height
                     Column('altezza_min', Numeric(6, 2)),

                     # Maximum depth
                     Column('profondita_max', Numeric(6, 2)),

                     # Minimum depth
                     Column('profondita_min', Numeric(6, 2)),

                     # Average width
                     Column('larghezza_media', Numeric(6, 2)),

                     # Maximum absolute elevation
                     Column('quota_max_abs', Numeric(6, 2)),

                     # Maximum relative elevation
                     Column('quota_max_rel', Numeric(6, 2)),

                     # Minimum absolute elevation
                     Column('quota_min_abs', Numeric(6, 2)),

                     # Minimum relative elevation
                     Column('quota_min_rel', Numeric(6, 2)),

                     # General observations
                     Column('osservazioni', Text),

                     # Dating
                     Column('datazione', Text),

                     # Flotation
                     Column('flottazione', Text),

                     # Sieving
                     Column('setacciatura', Text),

                     # Data reliability
                     Column('affidabilita', Text),

                     # Excavation director
                     Column('direttore_us', Text),

                     # Unit supervisor
                     Column('responsabile_us', Text),

                     # Cataloging entity code
                     Column('cod_ente_schedatore', Text),

                     # Survey date
                     Column('data_rilevazione', String(20)),

                     # Reprocessing date
                     Column('data_rielaborazione', String(20)),

                     # Masonry unit length
                     Column('lunghezza_usm', Numeric(6, 2)),

                     # Masonry unit height
                     Column('altezza_usm', Numeric(6, 2)),

                     # Masonry unit thickness
                     Column('spessore_usm', Numeric(6, 2)),

                     # Masonry technique
                     Column('tecnica_muraria_usm', Text),

                     # Masonry unit module
                     Column('modulo_usm', Text),

                     # Mortar samples
                     Column('campioni_malta_usm', Text),

                     # Brick samples
                     Column('campioni_mattone_usm', Text),

                     # Stone samples
                     Column('campioni_pietra_usm', Text),

                     # Materials origin
                     Column('provenienza_materiali_usm', Text),

                     # Masonry unit distinction criteria
                     Column('criteri_distinzione_usm', Text),

                     # Primary use of masonry unit
                     Column('uso_primario_usm', Text),

                     # Work typology
                     Column('tipologia_opera', Text),

                     # Wall section
                     Column('sezione_muraria', Text),

                     # Analyzed surface
                     Column('superficie_analizzata', Text),

                     # Orientation
                     Column('orientamento', Text),

                     # Brick materials
                     Column('materiali_lat', Text),

                     # Brick workmanship
                     Column('lavorazione_lat', Text),

                     # Brick consistency
                     Column('consistenza_lat', Text),

                     # Brick shape
                     Column('forma_lat', Text),

                     # Brick color
                     Column('colore_lat', Text),

                     # Brick mixture
                     Column('impasto_lat', Text),

                     # Stone shape
                     Column('forma_p', Text),

                     # Stone color
                     Column('colore_p', Text),

                     # Stone cut
                     Column('taglio_p', Text),

                     # Stone laying technique
                     Column('posa_opera_p', Text),

                     # Masonry unit aggregates
                     Column('inerti_usm', Text),

                     # Masonry unit binder type
                     Column('tipo_legante_usm', Text),

                     # Masonry unit finishing
                     Column('rifinitura_usm', Text),

                     # Stone material
                     Column('materiale_p', Text),

                     # Stone consistency
                     Column('consistenza_p', Text),

                     # Secondary stratigraphic relationships
                     Column('rapporti2', Text),

                     # USV documentation
                     Column('doc_usv', Text),

                     # StratiGraph persistent identifier (UUID v4)
                     Column('entity_uuid', Text),

                     # Unique constraint ensuring the combination of site, area, stratigraphic unit and unit type is unique
                     UniqueConstraint('sito', 'area', 'us', 'unita_tipo', name='ID_us_unico')
                     )
