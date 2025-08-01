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


'''
Created on 19 feb 2018

@author: Serena Sensini; Enzo Cocca <enzo.ccc@gmail.com>
'''


class TMA(object):
    def __init__(self,
                 id,
                 sito,
                 area,
                 localita,
                 settore,
                 ogtm,
                 ldct,
                 ldcn,
                 vecchia_collocazione,
                 cassetta,
                 scan,
                 saggio,
                 vano_locus,
                 dscd,
                 dscu,
                 rcgd,
                 rcgz,
                 aint,
                 aind,
                 dtzg,
                 deso,
                 nsc,
                 ftap,
                 ftan,
                 drat,
                 dran,
                 draa,
                 created_at,
                 updated_at,
                 created_by,
                 updated_by
                 ):
        self.id = id  # 0
        self.sito = sito  # 1
        self.area = area  # 2
        self.localita = localita  # 3
        self.settore = settore  # 4
        self.ogtm = ogtm  # 5
        self.ldct = ldct  # 6
        self.ldcn = ldcn  # 7
        self.vecchia_collocazione = vecchia_collocazione  # 8
        self.cassetta = cassetta  # 9
        self.scan = scan  # 10
        self.saggio = saggio  # 11
        self.vano_locus = vano_locus  # 12
        self.dscd = dscd  # 13
        self.dscu = dscu  # 14
        self.rcgd = rcgd  # 15
        self.rcgz = rcgz  # 16
        self.aint = aint  # 17
        self.aind = aind  # 18
        self.dtzg = dtzg  # 19
        self.deso = deso  # 20
        self.nsc = nsc  # 21
        self.ftap = ftap  # 22
        self.ftan = ftan  # 23
        self.drat = drat  # 24
        self.dran = dran  # 25
        self.draa = draa  # 26
        self.created_at = created_at  # 27
        self.updated_at = updated_at  # 28
        self.created_by = created_by  # 29
        self.updated_by = updated_by  # 30

    def __repr__(self):
        return "<TMA('%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % (
            self.id,
            self.sito,
            self.area,
            self.localita,
            self.settore,
            self.ogtm,
            self.ldct,
            self.ldcn,
            self.vecchia_collocazione,
            self.cassetta,
            self.scan,
            self.saggio,
            self.vano_locus,
            self.dscd,
            self.dscu,
            self.rcgd,
            self.rcgz,
            self.aint,
            self.aind,
            self.dtzg,
            self.deso,
            self.nsc,
            self.ftap,
            self.ftan,
            self.drat,
            self.dran,
            self.draa,
            self.created_at,
            self.updated_at,
            self.created_by,
            self.updated_by
        )