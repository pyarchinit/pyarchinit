"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
                             -------------------
    begin                : 2025-01-25
    copyright            : (C) 2025 by Enzo Cocca <enzo.ccc@gmail.com>
    email                : enzo.ccc@gmail.com
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

from sqlalchemy import Table, Column, Integer, String, ForeignKey, Float, Text


class Tma_materiali_table:
    """TMA Materiali - Table for repetitive material data"""

    @classmethod
    def define_table(cls, metadata):
        
        return Table('tma_materiali_ripetibili', metadata,
                     Column('id', Integer, primary_key=True),
                     
                     # Foreign key to main TMA record
                     Column('id_tma', Integer, ForeignKey('tma_materiali_archeologici.id'), nullable=False),
                     
                     # Material description data (MAD)
                     Column('madi', Text),                     # Inventory
                     
                     # Material component data (MAC) - all repetitive
                     Column('macc', Text, nullable=False),     # Category (required)
                     Column('macl', Text),                     # Class
                     Column('macp', Text),                     # Typological specification
                     Column('macd', Text),                     # Definition
                     Column('cronologia_mac', Text),           # MAC chronology
                     Column('macq', Text),                     # Quantity
                     Column('peso', Float),                          # Weight (now float)

                     # System fields
                     Column('created_at', Text),
                     Column('updated_at', Text),
                     Column('created_by', Text),
                     Column('updated_by', Text),
                     )

   # Table already exists or geometry type not supported