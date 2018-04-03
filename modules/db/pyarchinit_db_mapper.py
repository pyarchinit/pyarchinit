#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
        					 stored in Postgres
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi
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
from sqlalchemy.orm import mapper

from modules.db.entities.ARCHEOZOOLOGY import ARCHEOZOOLOGY
from modules.db.entities.CAMPIONI import CAMPIONI
from modules.db.entities.DETETA import DETETA
from modules.db.entities.DETSESSO import DETSESSO
from modules.db.entities.INVENTARIO_LAPIDEI import INVENTARIO_LAPIDEI
from modules.db.entities.INVENTARIO_MATERIALI_TOIMP import INVENTARIO_MATERIALI_TOIMP
from modules.db.entities.MEDIA import MEDIA
from modules.db.entities.MEDIATOENTITY import MEDIATOENTITY
from modules.db.entities.MEDIA_THUMB import MEDIA_THUMB
from modules.db.entities.PDF_ADMINISTRATOR import PDF_ADMINISTRATOR
from modules.db.entities.PERIODIZZAZIONE import PERIODIZZAZIONE
from modules.db.entities.PYARCHINIT_THESAURUS_SIGLE import PYARCHINIT_THESAURUS_SIGLE
from modules.db.entities.SCHEDAIND import SCHEDAIND
from modules.db.entities.SITE import SITE
from modules.db.entities.STRUTTURA import STRUTTURA
from modules.db.entities.TAFONOMIA import TAFONOMIA
from modules.db.entities.US import US
from modules.db.entities.US_TOIMP import US_TOIMP
from modules.db.entities.UT import UT
from modules.db.structures.Archeozoology_table import Archeozoology_table
from modules.db.structures.Campioni_table import Campioni_table
from modules.db.structures.DETETA_table import DETETA_table
from modules.db.structures.DETSESSO_table import DETSESSO_table
from modules.db.structures.Inventario_Lapidei_table import Inventario_Lapidei_table
from modules.db.structures.Inventario_materiali_table import Inventario_materiali_table_toimp
from modules.db.structures.Media_table import Media_table
from modules.db.structures.Media_thumb_table import Media_thumb_table
from modules.db.structures.Media_to_Entity_table import Media_to_Entity_table
from modules.db.structures.PDF_administrator_table import PDF_administrator_table
from modules.db.structures.Periodizzazione_table import Periodizzazione_table
from modules.db.structures.Pyarchinit_thesaurus_sigle import Pyarchinit_thesaurus_sigle
from modules.db.structures.SCHEDAIND_table import SCHEDAIND_table
from modules.db.structures.Site_table import Site_table
from modules.db.structures.Struttura_table import Struttura_table
from modules.db.structures.Tafonomia_table import Tafonomia_table
from modules.db.structures.US_table import US_table
from modules.db.structures.US_table_toimp import US_table_toimp
from modules.db.structures.UT_table import UT_table

try:
    # mapper
    mapper(ARCHEOZOOLOGY, Archeozoology_table.archeozoology_table)

    # mapper
    mapper(CAMPIONI, Campioni_table.campioni_table)

    # mapper
    mapper(DETETA, DETETA_table.deteta_table)

    # mapper
    mapper(DETSESSO, DETSESSO_table.detsesso_table)

    # mapper
    # mapper(DOCUMENTAZIONE, Documentazione_table.documentazione_table)

    # mapper
    mapper(INVENTARIO_LAPIDEI, Inventario_Lapidei_table.inventario_lapidei_table)

    # mapper
    mapper(INVENTARIO_MATERIALI_TOIMP, Inventario_materiali_table_toimp.inventario_materiali_table_toimp)

    # mapper
    # mapper(INVENTARIO_MATERIALI, Inventario_materiali_table.inventario_materiali_table)

    # mapper
    mapper(US, US_table.us_table)

    # mapper
    mapper(UT, UT_table.ut_table)

    # mapper
    mapper(US_TOIMP, US_table_toimp.us_table_toimp)

    # mapper
    mapper(STRUTTURA, Struttura_table.struttura_table)

    # mapper
    mapper(MEDIA, Media_table.media_table)

    # mapper
    mapper(MEDIA_THUMB, Media_thumb_table.media_thumb_table)

    # mapper
    mapper(MEDIATOENTITY, Media_to_Entity_table.media_to_entity_table)

    # mapper
    mapper(PERIODIZZAZIONE, Periodizzazione_table.periodizzazione_table)

    # mapper
    mapper(PDF_ADMINISTRATOR, PDF_administrator_table.pdf_administrator_table)

    # mapper
    mapper(PYARCHINIT_THESAURUS_SIGLE, Pyarchinit_thesaurus_sigle.pyarchinit_thesaurus_sigle)

    # mapper
    mapper(SCHEDAIND, SCHEDAIND_table.individui_table)

    # mapper
    mapper(SITE, Site_table.site_table)

    # mapper
    mapper(TAFONOMIA, Tafonomia_table.tafonomia_table)

except:
    pass
