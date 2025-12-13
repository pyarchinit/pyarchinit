'''
Created on 05 dic 2022

@author:  Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, Numeric, Text,  UniqueConstraint


# Table representing pottery finds and their characteristics
class PotteryTable:
    @classmethod
    def define_table(cls, metadata):
        return Table('pottery_table', metadata,
                     # Unique identifier for each pottery record
                     Column('id_rep', Integer, primary_key=True),

                     # Identification number
                     Column('id_number', Integer),

                     # Archaeological site name
                     Column('sito', Text),

                     # Excavation area
                     Column('area', Text),

                     # Stratigraphic unit number
                     Column('us', Integer),

                     # Storage box number
                     Column('box', Integer),

                     # Reference to photograph
                     Column('photo', Text),

                     # Reference to technical drawing
                     Column('drawing', Text),

                     # Year of discovery
                     Column('anno', Integer),

                     # Fabric/paste composition
                     Column('fabric', Text),

                     # Percentage of preservation
                     Column('percent', Text),

                     # Material type
                     Column('material', Text),

                     # General form classification
                     Column('form', Text),

                     # Specific form classification
                     Column('specific_form', Text),

                     # Ware type
                     Column('ware', Text),

                     # Munsell color code
                     Column('munsell', Text),

                     # Surface treatment
                     Column('surf_trat', Text),

                     # External decoration
                     Column('exdeco', Text),

                     # Internal decoration
                     Column('intdeco', Text),

                     # Wheel-made indicator
                     Column('wheel_made', Text),

                     # Description of external decoration
                     Column('descrip_ex_deco', Text),

                     # Description of internal decoration
                     Column('descrip_in_deco', Text),

                     # Additional notes
                     Column('note', Text),

                     # Maximum diameter
                     Column('diametro_max', Numeric(7, 3)),

                     # Quantity of fragments
                     Column('qty', Integer),

                     # Rim diameter
                     Column('diametro_rim', Numeric(7, 3)),

                     # Bottom diameter
                     Column('diametro_bottom', Numeric(7, 3)),

                     # Height
                     Column('diametro_height', Numeric(7, 3)),

                     # Preserved diameter
                     Column('diametro_preserved', Numeric(7, 3)),

                     # Specific shape description
                     Column('specific_shape', Text),

                     # Bag number
                     Column('bag', Integer),

                     # Excavation sector
                     Column('sector', Text),

                     Column('decoration_type', Text),

                     Column('decoration_motif', Text),

                     Column('decoration_position', Text),

                     # Unique constraint ensuring the combination of site and ID number is unique
                     UniqueConstraint('sito', 'id_number', name='ID_rep_unico')
                     )


