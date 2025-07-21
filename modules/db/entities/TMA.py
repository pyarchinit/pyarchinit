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
                 ogtm,
                 ldct,
                 ldcn,
                 vecchia_collocazione,
                 cassetta,
                 localita,
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
                 dtzs,
                 cronologie,
                 n_reperti,
                 peso,
                 deso,
                 madi,
                 macc,
                 macl,
                 macp,
                 macd,
                 cronologia_mac,
                 macq,
                 ftap,
                 ftan,
                 drat,
                 dran,
                 draa
                 ):
        self.id_tma = id  # 0
        self.sito = sito  # 1
        self.area = area  # 2
        self.ogtm = ogtm  # 3
        self.ldct = ldct  # 4
        self.ldcn = ldcn  # 5
        self.vecchia_collocazione = vecchia_collocazione  # 6
        self.cassetta = cassetta  # 7
        self.localita = localita  # 8
        self.scan = scan  # 9
        self.saggio = saggio  # 10
        self.vano_locus = vano_locus  # 11
        self.dscd = dscd  # 12
        self.dscu = dscu  # 13
        self.rcgd = rcgd  # 14
        self.rcgz = rcgz  # 15
        self.aint = aint  # 16
        self.aind = aind  # 17
        self.dtzg = dtzg  # 18
        self.dtzs = dtzs  # 19
        self.cronologie = cronologie  # 20
        self.n_reperti = n_reperti  # 21
        self.peso = peso  # 22
        self.deso = deso  # 23
        self.madi = madi  # 24
        self.macc = macc  # 25
        self.macl = macl  # 26
        self.macp = macp  # 27
        self.macd = macd  # 28
        self.cronologia_mac = cronologia_mac  # 29
        self.macq = macq  # 30
        self.ftap = ftap  # 31
        self.ftan = ftan  # 32
        self.drat = drat  # 33
        self.dran = dran  # 34
        self.draa = draa  # 35


    def __repr__(self):
        return "<TMA('%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % (
            self.id_tma,
            self.sito,
            self.area,
            self.ogtm,
            self.ldct,
            self.ldcn,
            self.vecchia_collocazione,
            self.cassetta,
            self.localita,
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
            self.dtzs,
            self.cronologie,
            self.n_reperti,
            self.peso,
            self.deso,
            self.madi,
            self.macc,
            self.macl,
            self.macp,
            self.macd,
            self.cronologia_mac,
            self.macq,
            self.ftap,
            self.ftan,
            self.drat,
            self.dran,
            self.draa
        )