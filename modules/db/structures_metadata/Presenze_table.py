'''
Created on 20 feb 2026

@author: Enzo Cocca <enzo.ccc@gmail.com>
'''
from sqlalchemy import Table, Column, Integer, Float, Text, UniqueConstraint


# Table representing personnel attendance/presence records
class Presenze_table:
    @classmethod
    def define_table(cls, metadata):
        return Table('presenze_table', metadata,
                     # Unique identifier for each attendance record
                     Column('id_presenza', Integer, primary_key=True),

                     # Archaeological site name
                     Column('sito', Text),

                     # Reference to personnel ID
                     Column('id_personale', Integer),

                     # Date of attendance
                     Column('data', Text),

                     # Clock-in time
                     Column('ora_ingresso', Text),

                     # Clock-out time
                     Column('ora_uscita', Text),

                     # Regular hours worked
                     Column('ore_ordinarie', Float),

                     # Overtime hours worked
                     Column('ore_straordinario', Float),

                     # Type of day (working, holiday, etc.)
                     Column('tipo_giornata', Text),

                     # Work shift
                     Column('turno', Text),

                     # Work area assignment
                     Column('area_lavoro', Text),

                     # Notes
                     Column('note', Text),

                     # Daily cost
                     Column('costo_giornata', Float),

                     # StratiGraph persistent identifier (UUID v4)
                     Column('entity_uuid', Text),

                     # Unique constraint ensuring one record per person per day per shift
                     UniqueConstraint('sito', 'id_personale', 'data', 'turno', name='ID_presenza_unico')
                     )
