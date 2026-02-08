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
import uuid


class TMA_MATERIALI(object):
    def __init__(self,
                 id,
                 id_tma,
                 madi,
                 macc,
                 macl,
                 macp,
                 macd,
                 cronologia_mac,
                 macq,
                 peso,
                 created_at,
                 updated_at,
                 created_by,
                 updated_by,
                 entity_uuid=None
                 ):
        self.id = id  # 0
        self.id_tma = id_tma  # 1
        self.madi = madi  # 2
        self.macc = macc  # 3
        self.macl = macl  # 4
        self.macp = macp  # 5
        self.macd = macd  # 6
        self.cronologia_mac = cronologia_mac  # 7
        self.macq = macq  # 8
        self.peso = peso  # 9
        self.created_at = created_at  # 10
        self.updated_at = updated_at  # 11
        self.created_by = created_by  # 12
        self.updated_by = updated_by  # 13
        self.entity_uuid = entity_uuid if entity_uuid else str(uuid.uuid4())

    def __repr__(self):
        return "<TMA_MATERIALI('%d','%d','%s','%s','%s','%s','%s','%s','%s','%f')>" % (
            self.id,
            self.id_tma,
            self.madi,
            self.macc,
            self.macl,
            self.macp,
            self.macd,
            self.cronologia_mac,
            self.macq,
            self.peso
        )