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

from sqlalchemy import Table, Column, Integer, String, MetaData, create_engine, Text

from modules.db.pyarchinit_conn_strings import Connection


class Tma_table:
    """TMA (Tabella Materiali Archeologici) table structure"""


    metadata = MetaData()
        
    tma_table = Table('tma_materiali_archeologici', metadata,
                      Column('id', Integer, primary_key=True),

                      # Basic identification
                      Column('sito', Text),
                      Column('area', Text),
                      Column('localita', Text),
                      Column('settore', Text),
                      Column('inventario', Text),

                      # Object data (OG)
                      Column('ogtm', Text),  # Material type (required)

                      # Location data (LC)
                      Column('ldct', Text),                    # Location type
                      Column('ldcn', Text),    # Location denomination (required)
                      Column('vecchia_collocazione', Text),   # Old location
                      Column('cassetta', Text), # Box (required)

                      # Excavation data (RE - DSC)
                      Column('scan', Text),                     # Excavation name
                      Column('saggio', Text),                   # Test pit
                      Column('vano_locus', Text),              # Room/Locus
                      Column('dscd', Text),                     # Excavation date
                      Column('dscu', Text),    # Stratigraphic Unit (required)

                      # Survey data (RE - RCG)
                      Column('rcgd', Text),                     # Survey date
                      Column('rcgz', Text),                    # Survey specifications

                      # Other acquisition (RE - AIN)
                      Column('aint', Text),                    # Acquisition type
                      Column('aind', Text),                     # Acquisition date

                      # Dating (DT) - Simplified to single chronological field
                      Column('dtzg', Text),     # Chronological range (required)

                      # Analytical data (DA)
                      Column('deso', Text),                    # Object indications

                      # Historical-critical notes (NSC)
                      Column('nsc', Text),                     # Historical-critical notes

                      # Documentation (DO)
                      Column('ftap', Text),                     # Photo type
                      Column('ftan', Text),                    # Photo identification code
                      Column('drat', Text),                     # Drawing type
                      Column('dran', Text),                    # Drawing identification code
                      Column('draa', Text),                     # Drawing author

                      # System fields
                      Column('created_at', Text),
                      Column('updated_at', Text),
                      Column('created_by', Text),
                      Column('updated_by', Text),
                      Column('entity_uuid', Text),


                     )




    # DO NOT create tables at module import time!





    # metadata.create_all(engine)  # This line was causing connection errors