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

from sqlalchemy import Table, Column, Integer, String, Float, ForeignKey, MetaData, create_engine

from modules.db.pyarchinit_conn_strings import Connection


class Tma_materiali_table:
    """TMA Materiali - Table for repetitive material data"""

    # connection string postgres
    internal_connection = Connection()

    # create engine and metadata
    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    metadata = MetaData(engine)
        
    tma_materiali_table = Table('tma_materiali_ripetibili', metadata,
                     Column('id', Integer, primary_key=True),
                     
                     # Foreign key to main TMA record
                     Column('id_tma', Integer, ForeignKey('tma_materiali_archeologici.id'), nullable=False),
                     
                     # Material description data (MAD)
                     Column('madi', String(50)),                     # Inventory
                     
                     # Material component data (MAC) - all repetitive
                     Column('macc', String(30), nullable=False),     # Category (required)
                     Column('macl', String(30)),                     # Class
                     Column('macp', String(30)),                     # Typological specification
                     Column('macd', String(30)),                     # Definition
                     Column('cronologia_mac', String(50)),           # MAC chronology
                     Column('macq', String(20)),                     # Quantity
                     Column('peso', Float),                          # Weight (now float)

                     # System fields
                     Column('created_at', String(50)),
                     Column('updated_at', String(50)),
                     Column('created_by', String(100)),
                     Column('updated_by', String(100)),
                     )

    try:
        metadata.create_all(engine)
    except:
        pass  # Table already exists or geometry type not supported