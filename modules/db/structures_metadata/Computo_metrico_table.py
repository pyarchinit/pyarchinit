'''
Created on 20 feb 2026

@author: Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, Float, Text


# Table representing volumetric/metric computation records for excavation
class Computo_metrico_table:
    @classmethod
    def define_table(cls, metadata):
        return Table('computo_metrico_table', metadata,
                     # Unique identifier for each computation record
                     Column('id_computo', Integer, primary_key=True),

                     # Archaeological site name
                     Column('sito', Text),

                     # Computation name
                     Column('nome_calcolo', Text),

                     # Computation type (volume, area, etc.)
                     Column('tipo_calcolo', Text),

                     # Pre-excavation DEM layer
                     Column('dem_pre', Text),

                     # Post-excavation DEM layer
                     Column('dem_post', Text),

                     # Polygon layer for area calculation
                     Column('layer_poligono', Text),

                     # Area in square meters
                     Column('area_mq', Float),

                     # Volume in cubic meters
                     Column('volume_mc', Float),

                     # Minimum elevation
                     Column('quota_min', Float),

                     # Maximum elevation
                     Column('quota_max', Float),

                     # Computation date
                     Column('data_calcolo', Text),

                     # Excavation phase
                     Column('fase_scavo', Text),

                     # Notes
                     Column('note', Text),

                     # StratiGraph persistent identifier (UUID v4)
                     Column('entity_uuid', Text),
                     )
