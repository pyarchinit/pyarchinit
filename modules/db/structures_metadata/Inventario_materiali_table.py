'''
Created on 15 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''

from sqlalchemy import Table, Column, Integer, String, Text, Numeric, UniqueConstraint


# Table representing archaeological materials inventory
class Inventario_materiali_table:
    @classmethod
    def define_table(cls, metadata):
        return Table('inventario_materiali_table', metadata,
                     # Unique identifier for each material record
                     Column('id_invmat', Integer, primary_key=True),

                     # Archaeological site name
                     Column('sito', Text),

                     # Inventory number
                     Column('numero_inventario', Integer),

                     # Type of find/artifact
                     Column('tipo_reperto', Text),

                     # Cataloging criteria used
                     Column('criterio_schedatura', Text),

                     # Definition/classification of the artifact
                     Column('definizione', Text),

                     # Detailed description of the artifact
                     Column('descrizione', Text),

                     # Excavation area number
                     Column('area', Text),

                     # Stratigraphic unit number
                     Column('us', Text),

                     # Indicates if the artifact has been washed (Yes/No)
                     Column('lavato', String(3)),

                     # Storage box number
                     Column('nr_cassa', Text),

                     # Storage location
                     Column('luogo_conservazione', Text),

                     # State of preservation
                     Column('stato_conservazione', String(200)),

                     # Dating of the artifact
                     Column('datazione_reperto', String(200)),

                     # Distinctive elements of the artifact
                     Column('elementi_reperto', Text),

                     # Measurements
                     Column('misurazioni', Text),

                     # Bibliographic references
                     Column('rif_biblio', Text),

                     # Technologies used in creation
                     Column('tecnologie', Text),

                     # Minimum number of forms
                     Column('forme_minime', Integer),

                     # Maximum number of forms
                     Column('forme_massime', Integer),

                     # Total number of fragments
                     Column('totale_frammenti', Integer),

                     # Ceramic body characteristics
                     Column('corpo_ceramico', String(200)),

                     # Surface treatment/coating
                     Column('rivestimento', String(200)),

                     # Rim diameter
                     Column('diametro_orlo', Numeric(7, 3)),

                     # Weight
                     Column('peso', Numeric(9, 3)),

                     # Type classification
                     Column('tipo', String(200)),

                     # EVE (Estimated Vessel Equivalent) of rim
                     Column('eve_orlo', Numeric(7, 3)),

                     # Indicates if the artifact is inventoried (Yes/No)
                     Column('repertato', String(3)),

                     # Indicates if the artifact is diagnostic (Yes/No)
                     Column('diagnostico', String(3)),

                     # Find number
                     Column('n_reperto', Integer),

                     # Container type
                     Column('tipo_contenitore', String(200)),

                     # Associated structure
                     Column('struttura', String(200)),

                     # Year of discovery/excavation
                     Column('years', Integer),

                     # Cataloger/compiler name
                     Column('schedatore', Text),

                     # Date of cataloging
                     Column('date_scheda', Text),

                     # Find point/location
                     Column('punto_rinv', Text),

                     # Negative photo references
                     Column('negativo_photo', Text),

                     # Slide/transparency references
                     Column('diapositiva', Text),

                     # Elevation/quota in meters
                     Column('quota_usm', Numeric(10, 3)),

                     # Unit of measurement for quota
                     Column('unita_misura_quota', String(20)),

                     # Photo IDs - auto-populated with associated photo names (not starting with D_)
                     Column('photo_id', Text),

                     # Drawing IDs - auto-populated with associated drawing names (starting with D_)
                     Column('drawing_id', Text),

                     # Unique constraint ensuring the combination of site and inventory number is unique
                     UniqueConstraint('sito', 'numero_inventario', name='ID_invmat_unico')
                     )
