"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi; Enzo Cocca <enzo.ccc@gmail.com>
    email                : mandoluca at gmail.com
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

from sqlalchemy import Table, Column, Integer, String, MetaData, create_engine

from modules.db.pyarchinit_conn_strings import Connection


class Tma_table:
    """TMA (Tabella Materiali Archeologici) table structure"""

    # connection string postgres"
    internal_connection = Connection()

    # create engine and metadata

    engine = create_engine(internal_connection.conn_str(), echo=False, convert_unicode=True)
    metadata = MetaData(engine)
        
    tma_table = Table('tma_materiali_archeologici', metadata,
                     Column('id', Integer, primary_key=True),

                     # Basic identification
                     Column('sito', String(100)),
                     Column('area', String(100)),

                     # Object data (OG)
                     Column('ogtm', String(100), nullable=False),  # Material type (required)

                     # Location data (LC)
                     Column('ldct', String(50)),                    # Location type
                     Column('ldcn', String(50), nullable=False),    # Location denomination (required)
                     Column('vecchia_collocazione', String(100)),   # Old location
                     Column('cassetta', String(15), nullable=False), # Box (required)

                     # Excavation data (RE - DSC)
                     Column('localita', String(50), nullable=False), # Locality (required)
                     Column('scan', String(50)),                     # Excavation name
                     Column('saggio', String(50)),                   # Test pit
                     Column('vano_locus', String(100)),              # Room/Locus
                     Column('dscd', String(20)),                     # Excavation date
                     Column('dscu', String(100), nullable=False),    # Stratigraphic Unit (required)

                     # Survey data (RE - RCG)
                     Column('rcgd', String(20)),                     # Survey date
                     Column('rcgz', String(100)),                    # Survey specifications

                     # Other acquisition (RE - AIN)
                     Column('aint', String(100)),                    # Acquisition type
                     Column('aind', String(50)),                     # Acquisition date

                     # Dating (DT)
                     Column('dtzg', String(50), nullable=False),     # Chronological range (required)
                     Column('dtzs', String(20)),                     # Chronological fraction
                     Column('cronologie', String(50)),               # Chronologies
                     Column('n_reperti', String(30)),                # Number of finds
                     Column('peso', String(20)),                     # Weight

                     # Analytical data (DA)
                     Column('deso', String(500)),                    # Object indications

                     # Technical data (MA)
                     Column('madi', String(50)),                     # Inventory
                     Column('macc', String(30), nullable=False),     # Category (required)
                     Column('macl', String(30)),                     # Class
                     Column('macp', String(30)),                     # Typological specification
                     Column('macd', String(30)),                     # Definition
                     Column('cronologia_mac', String(50)),           # MAC chronology
                     Column('macq', String(20)),                     # Quantity

                     # Documentation (DO)
                     Column('ftap', String(50)),                     # Photo type
                     Column('ftan', String(100)),                    # Photo identification code
                     Column('drat', String(50)),                     # Drawing type
                     Column('dran', String(100)),                    # Drawing identification code
                     Column('draa', String(50)),                     # Drawing author

                     # System fields
                     Column('created_at', String(50)),
                     Column('updated_at', String(50)),
                     Column('created_by', String(100)),
                     Column('updated_by', String(100)),


                     )




    metadata.create_all(engine)