
#! /usr/bin/env python
# -*- coding: utf-8 -*-
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

import datetime
from datetime import date
from numpy import *
import io

from builtins import object
from builtins import range
from builtins import str
from reportlab.lib import colors
from reportlab.lib.pagesizes import (A4,A3)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm 
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, PageBreak, SimpleDocTemplate, Spacer, TableStyle, Image
from reportlab.platypus.paragraph import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
# Registered font family
pdfmetrics.registerFont(TTFont('Cambria', 'Cambria.ttc'))
pdfmetrics.registerFont(TTFont('CambriaBd', 'cambriab.ttf'))
pdfmetrics.registerFont(TTFont('CambriaI', 'cambriai.ttf'))
pdfmetrics.registerFont(TTFont('CambriaZ', 'cambriaz.ttf'))
# #Registered fontfamily
registerFontFamily('Cambria',normal='Cambria')



from ..db.pyarchinit_conn_strings import Connection
from .pyarchinit_OS_utility import *
from PIL import Image as giggino
from reportlab.lib.utils import ImageReader
class NumberedCanvas_USsheet(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        
    def define_position(self, pos):
        self.page_position(pos)

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Cambria", 5)
        self.drawRightString(200 * mm, 8 * mm,
                             "Pag. %d di %d" % (self._pageNumber, page_count))  # scheda us verticale 200mm x 20 mm


class NumberedCanvas_USindex(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def define_position(self, pos):
        self.page_position(pos)

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Cambria", 5)
        self.drawRightString(270 * mm, 10 * mm,
                             "Pag. %d di %d" % (self._pageNumber, page_count))  # scheda us verticale 200mm x 20 mm


class single_US_pdf_sheet(object):
    # rapporti stratigrafici
    si_lega_a = ''
    uguale_a = ''
    copre = ''
    coperto_da = ''
    riempie = ''
    riempito_da = ''
    taglia = ''
    tagliato_da = ''
    si_appoggia_a = ''
    gli_si_appoggia = ''

    documentazione_print = ''

    piante_iccd = ""   #sistema per campi scheda iccd italia
    sezioni_iccd = ""  #sistema per campi scheda iccd italia
    prospetti_iccd = ""  #sistema per campi scheda iccd italia
    foto_iccd = ""  #sistema per campi scheda iccd italia

    #Aggiunta campi USM
    inclusi_print = ''

    inclusi__usm_print = ''

    def __init__(self, data):
        self.sito = data[0]
        self.area = data[1]
        self.us = data[2]
        self.d_stratigrafica = data[3]
        self.d_interpretativa = data[4]
        self.descrizione = data[5]
        self.interpretazione = data[6]
        self.periodo_iniziale = data[7]
        self.fase_iniziale = data[8]
        self.periodo_finale = data[9]
        self.fase_finale = data[10]
        self.scavato = data[11]
        self.attivita = data[12]
        self.anno_scavo = data[13]
        self.metodo_di_scavo = data[14]
        self.inclusi = data[15]
        self.campioni = data[16]
        self.rapporti = data[17]
        self.data_schedatura = data[18]
        self.schedatore = data[19]
        self.formazione = data[20]
        self.stato_di_conservazione = data[21]
        self.colore = data[22]
        self.consistenza = data[23]
        self.struttura = data[24]
        self.quota_min = data[25]
        self.quota_max = data[26]
        self.piante = data[27]
        self.documentazione = data[28]
        #campi USM
        self.unita_tipo = data[29]
        self.settore = data[30]
        self.quad_par = data[31]
        self.ambient = data[32]
        self.saggio = data[33]
        self.elem_datanti = data[34]
        self.funz_statica = data[35]
        self.lavorazione = data[36]
        self.spess_giunti = data[37]
        self.letti_posa = data[38]
        self.alt_mod = data[39]
        self.un_ed_riass = data[40]
        self.reimp = data[41]
        self.posa_opera = data[42]
        self.quota_min_usm = data[43]
        self.quota_max_usm = data[44]
        self.cons_legante = data[45]
        self.col_legante = data[46]
        self.aggreg_legante = data[47]
        self.con_text_mat = data[48]
        self.col_materiale = data[49]
        self.inclusi_materiali_usm = data[50]
        #campi aggiunti per Archeo 3.0 e allineamento ICCD
        self.n_catalogo_generale =  data[51]
        self.n_catalogo_interno =  data[52]
        self.n_catalogo_internazionale =  data[53]
        self.soprintendenza =  data[54]
        self.quota_relativa =  data[55]
        self.quota_abs =  data[56]
        self.ref_tm =  data[57]
        self.ref_ra =  data[58]
        self.ref_n =  data[59]
        self.posizione =  data[60]
        self.criteri_distinzione =  data[61]
        self.modo_formazione =  data[62]
        self.componenti_organici =  data[63]
        self.componenti_inorganici =  data[64]
        self.lunghezza_max =  data[65]
        self.altezza_max =  data[66]
        self.altezza_min =  data[67]
        self.profondita_max =  data[68]
        self.profondita_min =  data[69]
        self.larghezza_media =  data[70]
        self.quota_max_abs =  data[71]
        self.quota_max_rel =  data[72]
        self.quota_min_abs =  data[73]
        self.quota_min_rel =  data[74]
        self.osservazioni =  data[75]
        self.datazione =  data[76]
        self.flottazione =  data[77]
        self.setacciatura =  data[78]
        self.affidabilita =  data[79]
        self.direttore_us =  data[80]
        self.responsabile_us =  data[81]
        self.cod_ente_schedatore =  data[82]
        self.data_rilevazione =  data[83]
        self.data_rielaborazione =  data[84]
        self.lunghezza_usm =  data[85]
        self.altezza_usm = data[86]
        self.spessore_usm = data[87]
        self.tecnica_muraria_usm = data[88]
        self.modulo_usm = data[89]
        self.campioni_malta_usm = data[90]
        self.campioni_mattone_usm = data[91]
        self.campioni_pietra_usm = data[92]
        self.provenienza_materiali_usm = data[93]
        self.criteri_distinzione_usm = data[94]
        self.uso_primario_usm = data[95]
        self.tipologia_opera= data[96]
        self.sezione_muraria= data[97]
        self.superficie_analizzata= data[98]
        self.orientamento= data[99]
        self.materiali_lat= data[100]
        self.lavorazione_lat= data[101]
        self.consistenza_lat= data[102]
        self.forma_lat= data[103]
        self.colore_lat= data[104]
        self.impasto_lat= data[105]
        self.forma_p= data[106]
        self.colore_p= data[107]
        self.taglio_p= data[108]
        self.posa_opera_p= data[109]
        self.inerti_usm= data[110]
        self.tipo_legante_usm= data[111]
        self.rifinitura_usm= data[112]
        self.materiale_p= data[113]
        self.consistenza_p= data[113]
    def unzip_componenti(self):
        org = eval(self.componenti_organici)
        inorg = eval(self.componenti_inorganici)
        organici = ''
        inorganici = ''
        if len(org)>0:
            for item in org:
                organici += ""+str(item)[2:len(str(item))-2]+", " #trasforma item da ['Stringa'] a Stringa
            organici = organici[0:len(organici)-2] #tolgo la virgola in più

        if len(inorg) > 0:
            for item in inorg:
                inorganici += "" + str(item)[2:len(str(item)) - 2] + ", "  # trasforma item da ['Stringa'] a Stringa
            inorganici = inorganici[0:len(inorganici) - 2]  # tolgo la virgola in più

         #   if len(org) > 1:
         #       i=1
         #       while i < len(org):
         #           organici += ", "+org[i]
         #           i=i+1

        return organici, inorganici

    def unzip_rapporti_stratigrafici(self):
        rapporti = eval(self.rapporti)
        for rapporto in rapporti:
            if len(rapporto) == 5:
                if rapporto[0] == 'Si lega a' or rapporto[0] == 'si lega a':
                    if self.si_lega_a == '':
                        self.si_lega_a += str(rapporto[1])
                    else:
                        self.si_lega_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Uguale a' or rapporto[0] == 'uguale a':
                    if self.uguale_a == '':
                        self.uguale_a += str(rapporto[1])
                    else:
                        self.uguale_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Copre' or rapporto[0] == 'copre':
                    if self.copre == '':
                        self.copre += str(rapporto[1])
                    else:
                        self.copre += ', ' + str(rapporto[1])

                if rapporto[0] == 'Coperto da' or rapporto[0] == 'coperto da':
                    if self.coperto_da == '':
                        self.coperto_da += str(rapporto[1])
                    else:
                        self.coperto_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Riempie' or rapporto[0] == 'riempie':
                    if self.riempie == '':
                        self.riempie += str(rapporto[1])
                    else:
                        self.riempie += ', ' + str(rapporto[1])

                if rapporto[0] == 'Riempito da' or rapporto[0] == 'riempito da':
                    if self.riempito_da == '':
                        self.riempito_da += str(rapporto[1])
                    else:
                        self.riempito_da += ', ' + str(rapporto[1])
                if rapporto[0] == 'Taglia' or rapporto[0] == 'taglia':
                    if self.taglia == '':
                        self.taglia += str(rapporto[1])
                    else:
                        self.taglia += ', ' + str(rapporto[1])

                if rapporto[0] == 'Tagliato da' or rapporto[0] == 'tagliato da':
                    if self.tagliato_da == '':
                        self.tagliato_da += str(rapporto[1])
                    else:
                        self.tagliato_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Si appoggia a' or rapporto[0] == 'si appoggia a':
                    if self.si_appoggia_a == '':
                        self.si_appoggia_a += str(rapporto[1])
                    else:
                        self.si_appoggia_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Gli si appoggia' or rapporto[0] == 'gli si appoggia':
                    if self.gli_si_appoggia == '':
                        self.gli_si_appoggia += str(rapporto[1])
                    else:
                        self.gli_si_appoggia += ', ' + str(rapporto[1])
            elif len(rapporto) == 4:
                if rapporto[0] == 'Si lega a' or rapporto[0] == 'si lega a':
                    if self.si_lega_a == '':
                        self.si_lega_a += str(rapporto[1])
                    else:
                        self.si_lega_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Uguale a' or rapporto[0] == 'uguale a':
                    if self.uguale_a == '':
                        self.uguale_a += str(rapporto[1])
                    else:
                        self.uguale_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Copre' or rapporto[0] == 'copre':
                    if self.copre == '':
                        self.copre += str(rapporto[1])
                    else:
                        self.copre += ', ' + str(rapporto[1])

                if rapporto[0] == 'Coperto da' or rapporto[0] == 'coperto da':
                    if self.coperto_da == '':
                        self.coperto_da += str(rapporto[1])
                    else:
                        self.coperto_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Riempie' or rapporto[0] == 'riempie':
                    if self.riempie == '':
                        self.riempie += str(rapporto[1])
                    else:
                        self.riempie += ', ' + str(rapporto[1])

                if rapporto[0] == 'Riempito da' or rapporto[0] == 'riempito da':
                    if self.riempito_da == '':
                        self.riempito_da += str(rapporto[1])
                    else:
                        self.riempito_da += ', ' + str(rapporto[1])
                if rapporto[0] == 'Taglia' or rapporto[0] == 'taglia':
                    if self.taglia == '':
                        self.taglia += str(rapporto[1])
                    else:
                        self.taglia += ', ' + str(rapporto[1])

                if rapporto[0] == 'Tagliato da' or rapporto[0] == 'tagliato da':
                    if self.tagliato_da == '':
                        self.tagliato_da += str(rapporto[1])
                    else:
                        self.tagliato_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Si appoggia a' or rapporto[0] == 'si appoggia a':
                    if self.si_appoggia_a == '':
                        self.si_appoggia_a += str(rapporto[1])
                    else:
                        self.si_appoggia_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Gli si appoggia' or rapporto[0] == 'gli si appoggia':
                    if self.gli_si_appoggia == '':
                        self.gli_si_appoggia += str(rapporto[1])
                    else:
                        self.gli_si_appoggia += ', ' + str(rapporto[1])
    
            elif len(rapporto) == 3:
                if rapporto[0] == 'Si lega a' or rapporto[0] == 'si lega a':
                    if self.si_lega_a == '':
                        self.si_lega_a += str(rapporto[1])
                    else:
                        self.si_lega_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Uguale a' or rapporto[0] == 'uguale a':
                    if self.uguale_a == '':
                        self.uguale_a += str(rapporto[1])
                    else:
                        self.uguale_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Copre' or rapporto[0] == 'copre':
                    if self.copre == '':
                        self.copre += str(rapporto[1])
                    else:
                        self.copre += ', ' + str(rapporto[1])

                if rapporto[0] == 'Coperto da' or rapporto[0] == 'coperto da':
                    if self.coperto_da == '':
                        self.coperto_da += str(rapporto[1])
                    else:
                        self.coperto_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Riempie' or rapporto[0] == 'riempie':
                    if self.riempie == '':
                        self.riempie += str(rapporto[1])
                    else:
                        self.riempie += ', ' + str(rapporto[1])

                if rapporto[0] == 'Riempito da' or rapporto[0] == 'riempito da':
                    if self.riempito_da == '':
                        self.riempito_da += str(rapporto[1])
                    else:
                        self.riempito_da += ', ' + str(rapporto[1])
                if rapporto[0] == 'Taglia' or rapporto[0] == 'taglia':
                    if self.taglia == '':
                        self.taglia += str(rapporto[1])
                    else:
                        self.taglia += ', ' + str(rapporto[1])

                if rapporto[0] == 'Tagliato da' or rapporto[0] == 'tagliato da':
                    if self.tagliato_da == '':
                        self.tagliato_da += str(rapporto[1])
                    else:
                        self.tagliato_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Si appoggia a' or rapporto[0] == 'si appoggia a':
                    if self.si_appoggia_a == '':
                        self.si_appoggia_a += str(rapporto[1])
                    else:
                        self.si_appoggia_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Gli si appoggia' or rapporto[0] == 'gli si appoggia':
                    if self.gli_si_appoggia == '':
                        self.gli_si_appoggia += str(rapporto[1])
                    else:
                        self.gli_si_appoggia += ', ' + str(rapporto[1])
    
            elif len(rapporto) == 2:
                if rapporto[0] == 'Si lega a' or rapporto[0] == 'si lega a':
                    if self.si_lega_a == '':
                        self.si_lega_a += str(rapporto[1])
                    else:
                        self.si_lega_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Uguale a' or rapporto[0] == 'uguale a':
                    if self.uguale_a == '':
                        self.uguale_a += str(rapporto[1])
                    else:
                        self.uguale_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Copre' or rapporto[0] == 'copre':
                    if self.copre == '':
                        self.copre += str(rapporto[1])
                    else:
                        self.copre += ', ' + str(rapporto[1])

                if rapporto[0] == 'Coperto da' or rapporto[0] == 'coperto da':
                    if self.coperto_da == '':
                        self.coperto_da += str(rapporto[1])
                    else:
                        self.coperto_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Riempie' or rapporto[0] == 'riempie':
                    if self.riempie == '':
                        self.riempie += str(rapporto[1])
                    else:
                        self.riempie += ', ' + str(rapporto[1])

                if rapporto[0] == 'Riempito da' or rapporto[0] == 'riempito da':
                    if self.riempito_da == '':
                        self.riempito_da += str(rapporto[1])
                    else:
                        self.riempito_da += ', ' + str(rapporto[1])
                if rapporto[0] == 'Taglia' or rapporto[0] == 'taglia':
                    if self.taglia == '':
                        self.taglia += str(rapporto[1])
                    else:
                        self.taglia += ', ' + str(rapporto[1])

                if rapporto[0] == 'Tagliato da' or rapporto[0] == 'tagliato da':
                    if self.tagliato_da == '':
                        self.tagliato_da += str(rapporto[1])
                    else:
                        self.tagliato_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Si appoggia a' or rapporto[0] == 'si appoggia a':
                    if self.si_appoggia_a == '':
                        self.si_appoggia_a += str(rapporto[1])
                    else:
                        self.si_appoggia_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Gli si appoggia' or rapporto[0] == 'gli si appoggia':
                    if self.gli_si_appoggia == '':
                        self.gli_si_appoggia += str(rapporto[1])
                    else:
                        self.gli_si_appoggia += ', ' + str(rapporto[1])
    
    
    
    def unzip_rapporti_stratigrafici_de(self):
        rapporti = eval(self.rapporti)

        rapporti.sort()
        
        for rapporto in rapporti:
            if len(rapporto) == 5:
                if rapporto[0] == 'Bindet an' or rapporto[0] == 'bindet an':
                    if self.si_lega_a == '':
                        self.si_lega_a += str(rapporto[1])
                    else:
                        self.si_lega_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Entspricht' or rapporto[0] == 'entspricht':
                    if self.uguale_a == '':
                        self.uguale_a += str(rapporto[1])
                    else:
                        self.uguale_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Liegt über' or rapporto[0] == 'liegt über':
                    if self.copre == '':
                        self.copre += str(rapporto[1])
                    else:
                        self.copre += ', ' + str(rapporto[1])

                if rapporto[0] == 'Liegt unter' or rapporto[0] == 'liegt unter':
                    if self.coperto_da == '':
                        self.coperto_da += str(rapporto[1])
                    else:
                        self.coperto_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Verfüllt' or rapporto[0] == 'verfüllt':
                    if self.riempie == '':
                        self.riempie += str(rapporto[1])
                    else:
                        self.riempie += ', ' + str(rapporto[1])

                if rapporto[0] == 'Wird verfüllt durch' or rapporto[0] == 'wird verfüllt durch':
                    if self.riempito_da == '':
                        self.riempito_da += str(rapporto[1])
                    else:
                        self.riempito_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Schneidet' or rapporto[0] == 'schneidet':
                    if self.taglia == '':
                        self.taglia += str(rapporto[1])
                    else:
                        self.taglia += ', ' + str(rapporto[1])

                if rapporto[0] == 'Wird geschnitten' or rapporto[0] == 'wird geschnitten':
                    if self.tagliato_da == '':
                        self.tagliato_da += str(rapporto[1])
                    else:
                        self.tagliato_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Stützt sich auf' or rapporto[0] == 'stützt sich auf':
                    if self.si_appoggia_a == '':
                        self.si_appoggia_a += str(rapporto[1])
                    else:
                        self.si_appoggia_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Wird gestüzt von' or rapporto[0] == 'wird gestüzt von':
                    if self.gli_si_appoggia == '':
                        self.gli_si_appoggia += str(rapporto[1])
                    else:
                        self.gli_si_appoggia += ', ' + str(rapporto[1])
    
    def unzip_rapporti_stratigrafici_en(self):
        rapporti = eval(self.rapporti)

        rapporti.sort()
        
        for rapporto in rapporti:
            if len(rapporto) == 5:
                if rapporto[0] == 'Connected to' or rapporto[0] == 'Connected to':
                    if self.si_lega_a == '':
                        self.si_lega_a += str(rapporto[1])
                    else:
                        self.si_lega_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Same as' or rapporto[0] == 'same as':
                    if self.uguale_a == '':
                        self.uguale_a += str(rapporto[1])
                    else:
                        self.uguale_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Covers' or rapporto[0] == 'cover':
                    if self.copre == '':
                        self.copre += str(rapporto[1])
                    else:
                        self.copre += ', ' + str(rapporto[1])

                if rapporto[0] == 'Covered by' or rapporto[0] == 'covered by':
                    if self.coperto_da == '':
                        self.coperto_da += str(rapporto[1])
                    else:
                        self.coperto_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Fills' or rapporto[0] == 'fill':
                    if self.riempie == '':
                        self.riempie += str(rapporto[1])
                    else:
                        self.riempie += ', ' + str(rapporto[1])

                if rapporto[0] == 'Filled by' or rapporto[0] == 'filled by':
                    if self.riempito_da == '':
                        self.riempito_da += str(rapporto[1])
                    else:
                        self.riempito_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Cuts' or rapporto[0] == 'cuts':
                    if self.taglia == '':
                        self.taglia += str(rapporto[1])
                    else:
                        self.taglia += ', ' + str(rapporto[1])

                if rapporto[0] == 'Cutted by' or rapporto[0] == 'cutted by':
                    if self.tagliato_da == '':
                        self.tagliato_da += str(rapporto[1])
                    else:
                        self.tagliato_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Abuts' or rapporto[0] == 'abuts':
                    if self.si_appoggia_a == '':
                        self.si_appoggia_a += str(rapporto[1])
                    else:
                        self.si_appoggia_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Support' or rapporto[0] == 'Support':
                    if self.gli_si_appoggia == '':
                        self.gli_si_appoggia += str(rapporto[1])
                    else:
                        self.gli_si_appoggia += ', ' + str(rapporto[1])
    
            if len(rapporto) == 4:
                if rapporto[0] == 'Connected to' or rapporto[0] == 'Connected to':
                    if self.si_lega_a == '':
                        self.si_lega_a += str(rapporto[1])
                    else:
                        self.si_lega_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Same as' or rapporto[0] == 'same as':
                    if self.uguale_a == '':
                        self.uguale_a += str(rapporto[1])
                    else:
                        self.uguale_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Covers' or rapporto[0] == 'cover':
                    if self.copre == '':
                        self.copre += str(rapporto[1])
                    else:
                        self.copre += ', ' + str(rapporto[1])

                if rapporto[0] == 'Covered by' or rapporto[0] == 'covered by':
                    if self.coperto_da == '':
                        self.coperto_da += str(rapporto[1])
                    else:
                        self.coperto_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Fills' or rapporto[0] == 'fill':
                    if self.riempie == '':
                        self.riempie += str(rapporto[1])
                    else:
                        self.riempie += ', ' + str(rapporto[1])

                if rapporto[0] == 'Filled by' or rapporto[0] == 'filled by':
                    if self.riempito_da == '':
                        self.riempito_da += str(rapporto[1])
                    else:
                        self.riempito_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Cuts' or rapporto[0] == 'cuts':
                    if self.taglia == '':
                        self.taglia += str(rapporto[1])
                    else:
                        self.taglia += ', ' + str(rapporto[1])

                if rapporto[0] == 'Cutted by' or rapporto[0] == 'cutted by':
                    if self.tagliato_da == '':
                        self.tagliato_da += str(rapporto[1])
                    else:
                        self.tagliato_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Abuts' or rapporto[0] == 'abuts':
                    if self.si_appoggia_a == '':
                        self.si_appoggia_a += str(rapporto[1])
                    else:
                        self.si_appoggia_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Support' or rapporto[0] == 'Support':
                    if self.gli_si_appoggia == '':
                        self.gli_si_appoggia += str(rapporto[1])
                    else:
                        self.gli_si_appoggia += ', ' + str(rapporto[1])
            if len(rapporto) == 3:
                if rapporto[0] == 'Connected to' or rapporto[0] == 'Connected to':
                    if self.si_lega_a == '':
                        self.si_lega_a += str(rapporto[1])
                    else:
                        self.si_lega_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Same as' or rapporto[0] == 'same as':
                    if self.uguale_a == '':
                        self.uguale_a += str(rapporto[1])
                    else:
                        self.uguale_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Covers' or rapporto[0] == 'cover':
                    if self.copre == '':
                        self.copre += str(rapporto[1])
                    else:
                        self.copre += ', ' + str(rapporto[1])

                if rapporto[0] == 'Covered by' or rapporto[0] == 'covered by':
                    if self.coperto_da == '':
                        self.coperto_da += str(rapporto[1])
                    else:
                        self.coperto_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Fills' or rapporto[0] == 'fill':
                    if self.riempie == '':
                        self.riempie += str(rapporto[1])
                    else:
                        self.riempie += ', ' + str(rapporto[1])

                if rapporto[0] == 'Filled by' or rapporto[0] == 'filled by':
                    if self.riempito_da == '':
                        self.riempito_da += str(rapporto[1])
                    else:
                        self.riempito_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Cuts' or rapporto[0] == 'cuts':
                    if self.taglia == '':
                        self.taglia += str(rapporto[1])
                    else:
                        self.taglia += ', ' + str(rapporto[1])

                if rapporto[0] == 'Cutted by' or rapporto[0] == 'cutted by':
                    if self.tagliato_da == '':
                        self.tagliato_da += str(rapporto[1])
                    else:
                        self.tagliato_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Abuts' or rapporto[0] == 'abuts':
                    if self.si_appoggia_a == '':
                        self.si_appoggia_a += str(rapporto[1])
                    else:
                        self.si_appoggia_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Support' or rapporto[0] == 'Support':
                    if self.gli_si_appoggia == '':
                        self.gli_si_appoggia += str(rapporto[1])
                    else:
                        self.gli_si_appoggia += ', ' + str(rapporto[1])
    
            if len(rapporto) == 2:
                if rapporto[0] == 'Connected to' or rapporto[0] == 'Connected to':
                    if self.si_lega_a == '':
                        self.si_lega_a += str(rapporto[1])
                    else:
                        self.si_lega_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Same as' or rapporto[0] == 'same as':
                    if self.uguale_a == '':
                        self.uguale_a += str(rapporto[1])
                    else:
                        self.uguale_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Covers' or rapporto[0] == 'cover':
                    if self.copre == '':
                        self.copre += str(rapporto[1])
                    else:
                        self.copre += ', ' + str(rapporto[1])

                if rapporto[0] == 'Covered by' or rapporto[0] == 'covered by':
                    if self.coperto_da == '':
                        self.coperto_da += str(rapporto[1])
                    else:
                        self.coperto_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Fills' or rapporto[0] == 'fill':
                    if self.riempie == '':
                        self.riempie += str(rapporto[1])
                    else:
                        self.riempie += ', ' + str(rapporto[1])

                if rapporto[0] == 'Filled by' or rapporto[0] == 'filled by':
                    if self.riempito_da == '':
                        self.riempito_da += str(rapporto[1])
                    else:
                        self.riempito_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Cuts' or rapporto[0] == 'cuts':
                    if self.taglia == '':
                        self.taglia += str(rapporto[1])
                    else:
                        self.taglia += ', ' + str(rapporto[1])

                if rapporto[0] == 'Cutted by' or rapporto[0] == 'cutted by':
                    if self.tagliato_da == '':
                        self.tagliato_da += str(rapporto[1])
                    else:
                        self.tagliato_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Abuts' or rapporto[0] == 'abuts':
                    if self.si_appoggia_a == '':
                        self.si_appoggia_a += str(rapporto[1])
                    else:
                        self.si_appoggia_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Support' or rapporto[0] == 'Support':
                    if self.gli_si_appoggia == '':
                        self.gli_si_appoggia += str(rapporto[1])
                    else:
                        self.gli_si_appoggia += ', ' + str(rapporto[1])
    def unzip_documentazione(self):  #nuova gestione documentazione per ICCD TEST PUSH

        if self.documentazione == '':
            pass
        else:
            self.documentazione_list = eval(self.documentazione)

            for string_doc in self.documentazione_list:

                if len((string_doc)) == 1:

                    if string_doc[0] == 'ICCD-Piante':
                        self.piante_iccd = 'Si'
                    if string_doc[0] == 'ICCD-Prospetti':
                        self.prospetti_iccd = 'Si'
                    if string_doc[0] == 'ICCD-Sezioni':
                        self.sezioni_iccd = 'Si'
                    if string_doc[0] == 'ICCD-Foto':
                        self.foto_iccd = 'Si'


                if len((string_doc)) == 2 and string_doc[1] == '':

                    if string_doc[0] == 'ICCD-Piante':
                        self.piante_iccd = 'Si'
                    if string_doc[0] == 'ICCD-Prospetti':
                        self.prospetti_iccd = 'Si'
                    if string_doc[0] == 'ICCD-Sezioni':
                        self.sezioni_iccd = 'Si'
                    if string_doc[0] == 'ICCD-Foto':
                        self.foto_iccd = 'Si'

                if len((string_doc)) == 2:
                    #esportazione piante ICCD - Se inserito solo il valore ICCD-Piante il sistema inserisce Si
                    if string_doc[0] == 'ICCD-Piante':
                        if string_doc[1] != '':
                            if self.piante_iccd == '':
                                self.piante_iccd = str(string_doc[1])
                            else:
                                self.piante_iccd += ", " + str(string_doc[1])

                    #esportazione prospetti ICCD - Se inserito solo il valore ICCD-Prospetti il sistema inserisce Si
                    if string_doc[0] == 'ICCD-Prospetti':
                        if string_doc[1] != '':
                            if self.prospetti_iccd == '':
                                self.prospetti_iccd = str(string_doc[1])
                            else:
                                self.prospetti_iccd += ", " + str(string_doc[1])


                    #esportazione sezioni ICCD - Se inserito solo il valore ICCD-Sezioni il sistema inserisce Si
                    if string_doc[0] == 'ICCD-Sezioni':
                        if string_doc[1] != '':
                            if self.sezioni_iccd == '':
                                self.sezioni_iccd = str(string_doc[1])
                            else:
                                self.sezioni_iccd += ", " + str(string_doc[1])

                    #esportazione foto ICCD - Se inserito solo il valore ICCD-Foto il sistema inserisce Si
                    if string_doc[0] == 'ICCD-Foto':
                        if string_doc[1] != '':
                            if self.foto_iccd == '':
                                self.foto_iccd = str(string_doc[1])
                            else:
                                self.foto_iccd += ", " + str(string_doc[1])

    
    def unzip_documentazione_en(self):  #nuova gestione documentazione per ICCD TEST PUSH

        if self.documentazione == '':
            pass
        else:
            self.documentazione_list = eval(self.documentazione)

            for string_doc in self.documentazione_list:

                if len((string_doc)) == 1:

                    if string_doc[0] == 'Maps':
                        self.piante_iccd = 'Yes'
                    if string_doc[0] == 'Elevations':
                        self.prospetti_iccd = 'Yes'
                    if string_doc[0] == 'Sections':
                        self.sezioni_iccd = 'Yes'
                    if string_doc[0] == 'Photo':
                        self.foto_iccd = 'Yes'


                if len((string_doc)) == 2 and string_doc[1] == '':

                    if string_doc[0] == 'Maps':
                        self.piante_iccd = 'Yes'
                    if string_doc[0] == 'Elevations':
                        self.prospetti_iccd = 'Yes'
                    if string_doc[0] == 'Sections':
                        self.sezioni_iccd = 'Yes'
                    if string_doc[0] == 'Photo':
                        self.foto_iccd = 'Yes'

                if len((string_doc)) == 2:
                    #esportazione piante ICCD - Se inserito solo il valore ICCD-Piante il sistema inserisce Si
                    if string_doc[0] == 'Maps':
                        if string_doc[1] != '':
                            if self.piante_iccd == '':
                                self.piante_iccd = str(string_doc[1])
                            else:
                                self.piante_iccd += ", " + str(string_doc[1])

                    #esportazione prospetti ICCD - Se inserito solo il valore ICCD-Prospetti il sistema inserisce Si
                    if string_doc[0] == 'Elevations':
                        if string_doc[1] != '':
                            if self.prospetti_iccd == '':
                                self.prospetti_iccd = str(string_doc[1])
                            else:
                                self.prospetti_iccd += ", " + str(string_doc[1])


                    #esportazione sezioni ICCD - Se inserito solo il valore ICCD-Sezioni il sistema inserisce Si
                    if string_doc[0] == 'Sections':
                        if string_doc[1] != '':
                            if self.sezioni_iccd == '':
                                self.sezioni_iccd = str(string_doc[1])
                            else:
                                self.sezioni_iccd += ", " + str(string_doc[1])

                    #esportazione foto ICCD - Se inserito solo il valore ICCD-Foto il sistema inserisce Si
                    if string_doc[0] == 'Photo':
                        if string_doc[1] != '':
                            if self.foto_iccd == '':
                                self.foto_iccd = str(string_doc[1])
                            else:
                                self.foto_iccd += ", " + str(string_doc[1])
    
    
    
    def unzip_documentazione_de(self):  #nuova gestione documentazione per ICCD TEST PUSH

        if self.documentazione == '':
            pass
        else:
            self.documentazione_list = eval(self.documentazione)

            for string_doc in self.documentazione_list:

                if len((string_doc)) == 1:

                    if string_doc[0] == 'Pflanzen':
                        self.piante_iccd = 'Ja'
                    if string_doc[0] == 'Prospekte':
                        self.prospetti_iccd = 'Ja'
                    if string_doc[0] == 'Sektionen':
                        self.sezioni_iccd = 'Ja'
                    if string_doc[0] == 'Foto':
                        self.foto_iccd = 'Ja'


                if len((string_doc)) == 2 and string_doc[1] == '':

                    if string_doc[0] == 'Pflanzen':
                        self.piante_iccd = 'Ja'
                    if string_doc[0] == 'Prospekte':
                        self.prospetti_iccd = 'Ja'
                    if string_doc[0] == 'Sektionen':
                        self.sezioni_iccd = 'Ja'
                    if string_doc[0] == 'Foto':
                        self.foto_iccd = 'Ja'

                if len((string_doc)) == 2:
                    #esportazione piante ICCD - Se inserito solo il valore ICCD-Piante il sistema inserisce Si
                    if string_doc[0] == 'Pflanzen':
                        if string_doc[1] != '':
                            if self.piante_iccd == '':
                                self.piante_iccd = str(string_doc[1])
                            else:
                                self.piante_iccd += ", " + str(string_doc[1])

                    #esportazione prospetti ICCD - Se inserito solo il valore ICCD-Prospetti il sistema inserisce Si
                    if string_doc[0] == 'Prospekte':
                        if string_doc[1] != '':
                            if self.prospetti_iccd == '':
                                self.prospetti_iccd = str(string_doc[1])
                            else:
                                self.prospetti_iccd += ", " + str(string_doc[1])


                    #esportazione sezioni ICCD - Se inserito solo il valore ICCD-Sezioni il sistema inserisce Si
                    if string_doc[0] == 'Sektionen':
                        if string_doc[1] != '':
                            if self.sezioni_iccd == '':
                                self.sezioni_iccd = str(string_doc[1])
                            else:
                                self.sezioni_iccd += ", " + str(string_doc[1])

                    #esportazione foto ICCD - Se inserito solo il valore ICCD-Foto il sistema inserisce Si
                    if string_doc[0] == 'Foto':
                        if string_doc[1] != '':
                            if self.foto_iccd == '':
                                self.foto_iccd = str(string_doc[1])
                            else:
                                self.foto_iccd += ", " + str(string_doc[1])
    
    
    #Aggiunta campi USM
    #Aggiunta campi USM
    def unzip_inclusi(self):
        if self.inclusi == '':
            pass
        else:
            self.inclusi_print = ""
            for string_inclusi in eval(self.inclusi):
                if len(string_inclusi) == 2:
                    self.inclusi_print += str(string_inclusi[0]) + ": " + str(string_inclusi[1]) + "<br/>"
                if len(string_inclusi) == 1:
                    self.inclusi_print += str(string_inclusi[0]) + "<br/>"

    def unzip_inclusi_usm(self):
        if self.inclusi_usm == '':
            pass
        else:
            self.inclusi_usm_print = ""
            for string_inclusi_usm in eval(self.inclusi_materiali_usm):
                if len(string_inclusi_usm) == 2:
                    self.inclusi_usm_print += str(string_inclusi_usm[0]) + ": " + str(string_inclusi_usm[1]) + "<br/>"
                if len(string_inclusi_usm) == 1:
                    self.inclusi_usm_print += str(string_inclusi_usm[0]) + "<br/>"

    
    def unzip_inerti_usm(self):
       
        inorg = eval(self.aggreg_legante)
        
        inorganici = ''
        

        if len(inorg) > 0:
            for item in inorg:
                inorganici += "" + str(item)[2:len(str(item)) - 2] + ", "  # trasforma item da ['Stringa'] a Stringa
            inorganici = inorganici[0:len(inorganici) - 2]  # tolgo la virgola in più

         #   if len(org) > 1:
         #       i=1
         #       while i < len(org):
         #           organici += ", "+org[i]
         #           i=i+1

        return inorganici
    
    
    def unzip_colore_usm(self):
        inorg = eval(self.col_legante)
        
        inorganici = ''
        

        if len(inorg) > 0:
            for item in inorg:
                inorganici += "" + str(item)[2:len(str(item)) - 2] + ", "  # trasforma item da ['Stringa'] a Stringa
            inorganici = inorganici[0:len(inorganici) - 2]  # tolgo la virgola in più

         #   if len(org) > 1:
         #       i=1
         #       while i < len(org):
         #           organici += ", "+org[i]
         #           i=i+1

        return inorganici
    
    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def create_sheet_archeo3_usm_fields_2(self): #scheda us in stile ICCD Italiano
        self.unzip_rapporti_stratigrafici()
        self.unzip_documentazione()
        self.unzip_colore_usm()
        self.unzip_inerti_usm()
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.fontSize = 7
        styNormal.fontName='Cambria'
        styNormal.alignment = 0  # LEFT

        styleSheet = getSampleStyleSheet()
        styNormal2 = styleSheet['Normal']
        styNormal2.spaceBefore = 20
        styNormal2.spaceAfter = 20
        styNormal2.fontSize = 7
        styNormal2.fontName='Cambria'
        styNormal2.alignment = 0  # LEFT
        
        
        styleSheet = getSampleStyleSheet()
        styL = styleSheet['Normal']
        styL.spaceBefore = 20
        styL.spaceAfter = 20
        styL.fontSize = 2
        styL.fontName='Cambria'
        styL.alignment = 1
        
        
        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.fontSize = 7
        styDescrizione.fontName='Cambria'
        styDescrizione.alignment = 4  # Justified

        styleSheet = getSampleStyleSheet()
        styUnitaTipo = styleSheet['Normal']
        styUnitaTipo.spaceBefore = 20
        styUnitaTipo.spaceAfter = 20
        styUnitaTipo.fontSize = 14
        styUnitaTipo.fontName='Cambria'
        styUnitaTipo.alignment = 1  # CENTER

        styleSheet = getSampleStyleSheet()
        styTitoloComponenti = styleSheet['Normal']
        styTitoloComponenti.spaceBefore = 20
        styTitoloComponenti.spaceAfter = 20
        styTitoloComponenti. rowHeights=0.5
        styTitoloComponenti.fontSize = 7
        styTitoloComponenti.fontName='Cambria'
        styTitoloComponenti.alignment = 1  # CENTER

        styleSheet = getSampleStyleSheet()
        styVerticale = styleSheet['Normal']
        styVerticale.spaceBefore = 10
        styVerticale.spaceAfter = 20
        styVerticale.fontSize = 7
        styVerticale.fontName='Cambria'
        styVerticale.alignment = 1  # CENTER
        styVerticale.leading=8

        #format labels

        #0-1 row Unita tipo, logo, n. catalogo generale, n. catalogo internazionale
        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path)

        logo.drawHeight = 2 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 2 * inch
        logo.hAlign = 'CENTER'
        lst = []
        lst2=[]
        lst.append(logo)
        if str(self.unita_tipo)== 'US':
            unita_tipo = Paragraph(str(self.unita_tipo), styUnitaTipo)
            label_ente_responsabile = Paragraph("<b>ENTE RESPONSABILE</b>", styNormal2)
            #label_catalogo_internazionale = Paragraph("<b>N° CATALOGO INTERNAZIONALE</b>", styNormal)
            ente_responsabile = Paragraph(str(self.n_catalogo_generale), styNormal)
            #catalogo_internazionale = Paragraph(str(self.n_catalogo_internazionale), styNormal)
            sop =  Paragraph("<b>SOPRINTENDENZA MIBACT COMPETENTE PER TUTELA</b><br/>" +str(self.soprintendenza), styNormal2)
            #2-3 row

            sito = Paragraph("<b>LOCALITÀ</b><br/>" + str(self.sito), styNormal)
            #anno_di_scavo = Paragraph("<b>ANNO</b><br/>" + self.anno_scavo, styNormal)
            if self.struttura!='':
            
                area = Paragraph("<b>AREA/EDIFICIO/STRUTTURA</b><br/>" + str(self.area)+'/'+str(self.struttura),styNormal)
            
            else:
                area = Paragraph("<b>AREA/EDIFICIO/STRUTTURA</b><br/>" + str(self.area),styNormal)
            
            saggio = Paragraph("<b>SAGGIO</b><br/>" + self.saggio, styNormal)
            ambiente = Paragraph("<b>AMBIENTE</b><br/>" + self.ambient, styNormal)
            posizione = Paragraph("<b>POS. NELL'AMBIENTE</b><br/>" + self.posizione, styNormal)
            settore = Paragraph("<b>SETTORE/I</b><br/>" + self.settore, styNormal)
            quadrato = Paragraph("<b>QUADRATO/I</b><br/>" + self.quad_par, styNormal)
            quote = Paragraph("<b>QUOTE</b><br/>min: " + self.quota_min + "<br/>max: "+self.quota_max, styNormal)
            label_unita_stratigrafica = Paragraph("<b>NUMERO/CODICE IDENTIFICATIVO DELL’UNITÀ STRATIGRAFICA</b><br/>"+ str(self.us), styNormal2)
            label_sas = Paragraph("<b>NUMERO/CODICE IDENTIFICATIVO DEL SAGGIO STRATIGRAFICO/DELL’EDIFICIO/DELLA STRUTTURA/DELLA DEPOSIZIONE FUNERARIA DI RIFERIMENTO</b><br/>", styNormal2)
            
            if self.formazione == 'Naturale':
                label_NAT = Paragraph("<i>NAT.</i><br/>" + self.formazione, styNormal)
                label_ART = Paragraph("<i>ART.</i>",  styNormal) 
            elif self.formazione == 'Artificiale':
                label_NAT = Paragraph("<i>NAT.</i>", styNormal)
                label_ART = Paragraph("<i>ART.</i><br/>"+ self.formazione, styNormal)
            elif self.formazione !='Naturale' or 'Artificiale':    
                label_NAT = Paragraph("<i>NAT.</i><br/>", styNormal)
                label_ART = Paragraph("<i>ART.</i>",  styNormal) 
            

            piante = Paragraph("<b>PIANTE</b><br/>" + self.piante_iccd, styNormal)
            sezioni = Paragraph("<b>SEZIONI</b><br/>" + self.sezioni_iccd, styNormal)
            prospetti = Paragraph("<b>PROSPETTI</b><br/>"+ self.prospetti_iccd, styNormal)                    #manca valore
            foto = Paragraph("<b>FOTOGRAFIE</b><br/>"+ self.foto_iccd, styNormal)            #manca valore

            tabelle_materiali = Paragraph("<b>RIFERIMENTI TABELLE MATERIALI<br/><br/>RA</b>:"+ self.ref_ra, styNormal)  #manca valore

            #5 row

            d_stratigrafica = Paragraph("<b>DEFINIZIONE E POSIZIONE</b><br/>Definizione stratigrafica: " + self.d_stratigrafica+"<br/>Definizione interpretativa: "+self.d_interpretativa, styNormal)

            #6 row

            criteri_distinzione = Paragraph("<b>CRITERI DI DISTINZIONE</b><br/>" + self.criteri_distinzione, styNormal)

            #7 row

            modo_formazione = Paragraph("<b>MODO FORMAZIONE</b><br/>" + self.modo_formazione, styNormal)

            #8-9 row


            organici, inorganici= self.unzip_componenti()
            inclusi = ''
            for i in eval(self.inclusi):
                if inclusi == '':
                    try:
                        inclusi += str(i[0])
                    except:
                        pass
                else:
                    try:
                        inclusi += ', ' + str(i[0])
                    except:
                        pass

            label_componenti = Paragraph("<b>COMPONENTI<br/></b>",styVerticale)

            label_inorganici = Paragraph("<i>INORGANICI</i>",styTitoloComponenti) #inorganici
            label_organici = Paragraph("<i>ORGANICI</i>", styTitoloComponenti) #organici
            #label_artificiali = Paragraph("<i>INORGANICI</i>", styTitoloComponenti) #inclusi

            comp_organici = Paragraph(organici, styNormal) #organici
            comp_inorganici = Paragraph(inorganici, styNormal)  #geologici
            #inclusi = Paragraph(inclusi, styNormal)  #artificiali

            #10 row

            consistenza = Paragraph("<b>CONSISTENZA</b><br/>" + self.consistenza, styNormal)
            colore = Paragraph("<b>COLORE</b><br/>" + self.colore, styNormal)
            #misure = ''                 # manca valore
            if bool(self.lunghezza_max) and bool(self.larghezza_media) and bool(self.altezza_max):
                misure = Paragraph("<b>MISURE</b><br/>" + 'Lun. '+ self.lunghezza_max + ' x '+ 'Larg. ' + self.larghezza_media + ' x '+ 'Sp. ' + self.altezza_max + 'm', styNormal)
            elif bool(self.lunghezza_max) and bool(self.larghezza_media) and not bool(self.altezza_max):
                misure = Paragraph("<b>MISURE</b><br/>" + 'Lun. ' + self.lunghezza_max + ' x '+ 'Larg. '+ self.larghezza_media + 'm', styNormal)
            
            else:
                misure = Paragraph("<b>MISURE</b><br/>", styNormal)
            #11 row

            stato_conservazione = Paragraph("<b>STATO DI CONSERVAZIONE</b><br/>" + self.stato_di_conservazione, styNormal)

            #12 row

            descrizione = Paragraph("<b>DESCRIZIONE</b><br/>" + self.descrizione, styDescrizione)

            #13-22 row

            si_lega_a = Paragraph("<b>SI LEGA A</b><br/>" + self.si_lega_a, styNormal)
            uguale_a = Paragraph("<b>UGUALE A</b><br/>" + self.uguale_a, styNormal)
            copre = Paragraph("<b>COPRE</b><br/>" + self.copre, styNormal)
            coperto_da = Paragraph("<b>COPERTO DA</b><br/>" + self.coperto_da, styNormal)
            riempie = Paragraph("<b>RIEMPIE</b><br/>" + self.riempie, styNormal)
            riempito_da = Paragraph("<b>RIEMPITO DA</b><br/>" + self.riempito_da, styNormal)
            taglia = Paragraph("<b>TAGLIA</b><br/>" + self.taglia, styNormal)
            tagliato_da = Paragraph("<b>TAGLIATO DA</b><br/>" + self.tagliato_da, styNormal)
            si_appoggia_a = Paragraph("<b>SI APPOGGIA A</b><br/>" + self.si_appoggia_a, styNormal)
            gli_si_appoggia = Paragraph("<b>GLI SI APPOGGIA</b><br/>" + self.gli_si_appoggia, styNormal)

            label_sequenza_stratigrafica = Paragraph("<b>S<br/>E<br/>Q<br/>U<br/>E<br/>N<br/>Z<br/>A<br/><br/>S<br/>T<br/>R<br/>A<br/>T<br/>I<br/>G<br/>R<br/>A<br/>F<br/>I<br/>C<br/>A</b>", styVerticale)

            posteriore_a = Paragraph("<b>POSTERIORE A</b><br/>" + self.copre +"<br/>" + self.riempie +"<br/>"+  self.taglia+ "<br/>" +   self.si_appoggia_a, styNormal)               # manca valore
            anteriore_a = Paragraph("<b>ANTERIORE A</b><br/>"+ self.coperto_da +"<br/>"+  self.riempito_da +"<br/>"+ self.tagliato_da +  "<br/>" + self.gli_si_appoggia, styNormal)                 # manca valore

            #23 row

            osservazioni = Paragraph("<b>OSSERVAZIONI</b><br/>" + self.osservazioni, styDescrizione)

            #24 row

            interpretazione = Paragraph("<b>INTERPRETAZIONE</b><br/>" + self.interpretazione, styDescrizione)

            #25 row

            elementi_datanti = Paragraph("<b>ELEMENTI DATANTI</b><br/>" + self.elem_datanti, styDescrizione)

            #26 row

            datazione_ipotesi = Paragraph("<b>DATAZIONE</b><br/>" + str(self.datazione), styNormal)
            periodo_o_fase = Paragraph("<b>PERIODO O FASE</b><br/>Periodo iniziale: "+self.periodo_iniziale+"<br/>Fase iniziale: "+self.fase_iniziale+"<br/>Periodo finale: "+self.periodo_finale+"<br/>Fase finale: "+self.fase_finale, styNormal)

            #27 row

            dati_quantitativi = Paragraph("<b>DATI QUANTITATIVI DEI REPERTI</b><br/>", styNormal)  # manca valore

            #28 row

            campioni_list = eval(self.campioni)
            campioni = ''
            for i in eval(self.campioni):
                if campioni == '':
                    try:
                        campioni += str(i[0])
                    except:
                        pass
                else:
                    try:
                        campioni += ', ' + str(i[0])
                    except:
                        pass
            campioni = Paragraph("<b>CAMPIONATURE</b><br/>" + campioni, styNormal)
            flottazione = Paragraph("<b>FLOTTAZIONE</b><br/>" + self.flottazione, styNormal)
            setacciatura = Paragraph("<b>SETACCIATURA</b><br/>" + self.setacciatura, styNormal)

            #28 row

            affidabilita = Paragraph("<b>AFFIDABILITÀ STRATIGRAFICA</b><br/>" + self.affidabilita, styNormal)
            direttore = Paragraph("<b>RESPONSABILE SCIENTIFICO DELLE INDAGINI</b><br/>" + self.direttore_us, styNormal)
            responsabile2 = Paragraph("<b>RESPONSABILE COMPILAZIONE SUL CAMPO</b><br/>" + self.schedatore, styNormal)
            responsabile = Paragraph("<b>RESPONSABILE RIELABORAZIONE</b><br/>" + self.responsabile_us, styNormal)
            data_rilievo = Paragraph("<b>DATA RILEVAMENTO SUL CAMPO</b><br/>" + self.data_rilevazione, styNormal)
            data_rielaborazione = Paragraph("<b>DATA RIELABORAZIONE</b><br/>" + self.data_rielaborazione, styNormal)
            attivita = Paragraph("<b>ATTIVITÀ</b><br/>" + self.attivita, styNormal)
            licenza =  Paragraph("<b>MIBACT- ICCD_licenza CC BY-SA 4.0_Creative Commons Attribution-ShareAlike 4.0 International</b>",styL)
            # schema
            cell_schema = [
                
                [unita_tipo, '01' , label_ente_responsabile, '03', '04', '05', '06', '07' , '08', '09', '10', label_unita_stratigrafica, '12', '13', '14', '15', '16', '17'],
                ['00', '01', sop, '03', '04' , '05', '06','07' , '08','09', '10', label_sas, '12', '13', '14', '15', '16', '17'],
                [sito, '01', '02', '03', '04', '05' , '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [area, '01', '02', '03', '04', '05' , '06', '07', '08', '09', '10', saggio, '12', '13', '14', '15', '16', '17'],
                [ambiente, '01', '02', '03', posizione, '04' , '06', settore, '08', quadrato, '10', quote, '12', '13', label_NAT, '15', label_ART, '17'],
                [piante, '01', prospetti, '03', sezioni, '05', '06',foto, '08', '09', '10', tabelle_materiali, '12', '13', '14', '15', '16', '17'],
                [d_stratigrafica, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [criteri_distinzione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [modo_formazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [ label_organici, '01','02', '03', '04', '05', '06', '07', '08', label_inorganici, '10', '11','12' , '13', '14', '15', '16', '17'],
                [label_componenti, comp_organici, '02', '03', '04', '05', '06', '07', '08', comp_inorganici, '10', '11', '12', '13', '14', '15', '16', '17'],
                [consistenza, '01', '02', '03', '04', '05', colore, '07', '08', '09', '10', '11', misure, '13', '14', '15', '16', '17'],
                [stato_conservazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                [uguale_a, '01', '02', '03', '04', '05', si_lega_a, '07', '08', '09', '10', '11', label_sequenza_stratigrafica, posteriore_a, '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [gli_si_appoggia, '01', '02', '03', '04', '05', si_appoggia_a, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [coperto_da, '01', '02', '03', '04', '05', copre, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', anteriore_a , '14', '15', '16', '17'],
                [tagliato_da, '01', '02', '03', '04', '05', taglia, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [riempito_da, '01', '02', '03', '04', '05', riempie, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [osservazioni, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [interpretazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                [datazione_ipotesi, '01', '02', '03', '04', '05', periodo_o_fase, '07', '08', '09', '10', '11', attivita, '13', '14', '15', '16', '17'],
                [elementi_datanti, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [dati_quantitativi, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [campioni, '01', '02', '03', '04', '05', flottazione, '07', '08', '09', '10', '11', setacciatura, '13', '14', '15', '16', '17'],
                [affidabilita, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [direttore, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [data_rilievo, '01', '02', '03', '04', '05', '06', '07', '08', responsabile, '10', '11', '12', '13', '14', '15', '16', '17'],
                [data_rielaborazione, '01', '02', '03', '04', '05', '06', '07', '08', responsabile2, '10', '11', '12', '13', '14', '15', '16', '17'],
                ]

            # table style
            table_style = [
               
                ('GRID', (0, 0), (-1, -1), 0.3, colors.black),
                # 0 row
                ('SPAN', (0, 0), (1, 1)),  # unita tipo
                ('VALIGN', (0, 0), (1, 1), 'MIDDLE'),

                ('SPAN', (2, 0), (10, 0)),  # label n. catalogo generale
                ('SPAN', (11, 0), (17, 0)),  # label n. catalogo internazionale
                ('VALIGN', (2, 0), (12,1), 'TOP'),

                # 1 row
                ('SPAN', (2, 1), (10, 1)),  # n. catalogo generale
                ('SPAN', (11, 1), (17, 1)),  # catalogo internazionale
                ('VALIGN', (2, 0), (17, 1), 'TOP'),

                # 2 row
                ('SPAN', (0, 2), (17, 2)),  # sito
                
                ('VALIGN', (0, 2), (17, 2), 'TOP'),

                # 3 row
                ('SPAN', (0, 3), (10, 3)),  # piante
                ('SPAN', (11, 3), (17, 3)),  # sezioni
                ('VALIGN', (0, 3), (17, 3), 'TOP'),

                # 4 row
                ('SPAN', (0, 4), (3, 4)),  # definizione
                ('SPAN', (4, 4), (6, 4)),  # definizione
                ('SPAN', (7, 4), (8, 4)),  # definizione
                ('SPAN', (9, 4), (10, 4)),  # definizione
                ('SPAN', (11, 4), (13, 4)),  # definizione
                ('SPAN', (14, 4), (15, 4)),  # definizione
                ('SPAN', (16, 4), (17, 4)),  # definizione        
                ('VALIGN', (0, 4), (17, 4), 'TOP'),

                # 5 row
                ('SPAN', (0, 5), (1, 5)),  # definizione
                ('SPAN', (2,5), (3, 5)),  # definizione
                ('SPAN', (4, 5), (6, 5)),  # definizione
                ('SPAN', (7, 5), (10, 5)),  # definizione
                ('SPAN', (11, 5), (17, 5)),  # definizione
                ('VALIGN', (0, 5), (17, 5), 'TOP'),

                # 6 row
                ('SPAN', (0, 6), (17, 6)),  # modo di formazione
                ('VALIGN', (0, 6), (17, 6), 'TOP'),

                # 7 row
                ('SPAN', (0, 7), (17, 7)),  # label componenti
                ('VALIGN', (0, 7), (17, 7), 'TOP'),

                # 8 row
                ('SPAN', (0, 8), (17, 8)),  # consistenza
                ('VALIGN', (0, 8), (17, 8), 'TOP'),
                
                # 9-10 row
                
                ('SPAN', (0, 9), (8, 9)),  # consistenza
                ('SPAN', (9, 9), (17, 9)),  # consistenza
                ('SPAN', (0, 10), (0, 10)),  # consistenza
                ('SPAN', (1, 10), (8, 10)),  # consistenza
                ('SPAN', (9, 10), (17, 10)),  # consistenza
                ('VALIGN', (0, 9), (17, 10), 'TOP'),
                
                
                
                
                # 11 row
                ('SPAN', (0, 11), (5, 11)),  # stato di conservazione
                ('SPAN', (6, 11), (11, 11)),  # stato di conservazione
                ('SPAN', (12, 11), (17, 11)),  # stato di conservazione
                ('VALIGN', (0, 11), (17, 11), 'TOP'),

                # 12 row
                ('SPAN', (0, 12), (17, 12)),  # descrizione
                ('VALIGN', (0, 12), (17, 12), 'TOP'),

                # 13-22 row
                ('SPAN', (0, 13), (5, 14)),    # uguale a
                ('SPAN', (0, 15), (5, 16)),    # gli si appoggia
                ('SPAN', (0, 17), (5, 18)),    # coperto da
                ('SPAN', (0, 19), (5, 20)),    # tagliato da
                ('SPAN', (0, 21), (5, 22)),    # riempito da
                ('SPAN', (6, 13), (11, 14)),   # si lega a
                ('SPAN', (6, 15), (11, 16)),   # si appoggia a
                ('SPAN', (6, 17), (11, 18)),   # copre
                ('SPAN', (6, 19), (11, 20)),   # taglia
                ('SPAN', (6, 21), (11, 22)),   # riempie
                ('SPAN', (12, 13), (12, 22)),  # label sequenza stratigrafica
                ('SPAN', (13, 13), (17, 17)),  # posteriore a
                ('SPAN', (13, 18), (17, 22)),  # uguale a
                ('VALIGN', (0, 13), (17, 22), 'TOP'),

                # 23 row
                ('SPAN', (0, 23), (17, 23)),  # DESCRIZIONE
                ('VALIGN', (0, 23), (17, 23), 'TOP'),

                # 24 row
                ('SPAN', (0, 24), (17, 24)),  # OSSERVAZIONI
                ('VALIGN', (0, 24), (17, 24), 'TOP'),

                # 25 row

                ('SPAN', (0, 25), (17, 25)),  # INTERPRETAZIONI
                ('VALIGN', (0, 25), (17, 25), 'TOP'),

                #26 row

                ('SPAN', (0, 26), (5, 26)),  # datazione
                ('SPAN', (6, 26), (11, 26)),  # periodo o fase
                ('SPAN', (12, 26), (17, 26)),  # ATTIVITA
                ('VALIGN', (0, 26), (17, 26), 'TOP'),

                # #27 row

                ('SPAN', (0, 27), (17, 27)),  # elementi datanti
                ('VALIGN', (0, 27), (17, 27), 'TOP'),

                ('SPAN', (0, 28), (17, 28)),  # elementi datanti
                ('VALIGN', (0, 28), (17, 28), 'TOP'),
                
                #28 row
                ('SPAN', (0, 29), (5, 29)),  # campionature
                ('SPAN', (6, 29), (11, 29)),  # flottazione
                ('SPAN', (12, 29), (17, 29)),  # setacciatura
                ('VALIGN', (0, 29), (17, 29), 'TOP'),

                #29 row
                ('SPAN', (0, 30), (17, 30)),  # affidabilita stratigrafica
                
                ('VALIGN', (0, 30), (17, 30), 'TOP'),

                ('SPAN', (0, 31), (17, 31)),  # affidabilita stratigrafica
                ('VALIGN', (0, 31), (17, 31), 'TOP'),
                
                ('SPAN', (0, 32), (8, 32)),  # affidabilita stratigrafica
                ('SPAN', (9, 32), (17, 32)),  # affidabilita stratigrafica
                ('VALIGN', (0, 32), (17, 32), 'TOP'),
                
                ('SPAN', (0, 33), (8, 33)),  # affidabilita stratigrafica
                ('SPAN', (9, 33), (17, 33)),  # affidabilita stratigrafica
                ('VALIGN', (0, 33), (17, 33), 'TOP'),               
            ]

            colWidths = (15,30,30,30,30,30,30,30,30,30,30,30,20,30,30,30,30,30)
            rowHeights = None
            
            t = Table(cell_schema, colWidths=colWidths, rowHeights=rowHeights, style=table_style)
            lst.append(logo)
            
            return t
        elif str(self.unita_tipo)=='USM':
            unita_tipo = Paragraph(str(self.unita_tipo), styUnitaTipo)
            label_ente_responsabile = Paragraph("<b>ENTE RESPONSABILE</b>", styNormal)
            #label_catalogo_internazionale = Paragraph("<b>N° CATALOGO INTERNAZIONALE</b>", styNormal)
            ente_responsabile = Paragraph(str(self.n_catalogo_generale), styNormal)
            #catalogo_internazionale = Paragraph(str(self.n_catalogo_internazionale), styNormal)
            sop =  Paragraph("<b>SOPRINTENDENZA MIBACT COMPETENTE PER TUTELA</b><br/>" +str(self.soprintendenza), styNormal)
            #2-3 row

            sito = Paragraph("<b>LOCALITÀ</b><br/>" + str(self.sito), styNormal)
            #anno_di_scavo = Paragraph("<b>ANNO</b><br/>" + self.anno_scavo, styNormal)
            if self.struttura!='':
            
                area = Paragraph("<b>AREA/EDIFICIO/STRUTTURA</b><br/>" + str(self.area)+'/'+str(self.struttura),styNormal)
            
            else:
                area = Paragraph("<b>AREA/EDIFICIO/STRUTTURA</b><br/>" + str(self.area),styNormal)
            
            saggio = Paragraph("<b>SAGGIO</b><br/>" + self.saggio, styNormal)
            ambiente = Paragraph("<b>AMBIENTE</b><br/>" + self.ambient, styNormal)
            posizione = Paragraph("<b>POS. NELL'AMBIENTE</b><br/>" + self.posizione, styNormal)
            settore = Paragraph("<b>SETTORE/I</b><br/>" + self.settore, styNormal)
            quadrato = Paragraph("<b>QUADRATO/I</b><br/>" + self.quad_par, styNormal)
            quote = Paragraph("<b>QUOTE</b><br/>min: " + self.quota_min + "<br/>max: "+self.quota_max, styNormal)
            label_unita_stratigrafica = Paragraph("<b>NUMERO/CODICE IDENTIFICATIVO DELL’UNITÀ STRATIGRAFICA</b><br/>"+ str(self.us), styNormal)
            label_sas = Paragraph("<b>NUMERO/CODICE IDENTIFICATIVO DEL SAGGIO STRATIGRAFICO/DELL’EDIFICIO/DELLA STRUTTURA/DELLA DEPOSIZIONE FUNERARIA DI RIFERIMENTO</b><br/>", styNormal)
            
           

            piante = Paragraph("<b>PIANTE</b><br/>" + self.piante_iccd, styNormal)
            sezioni = Paragraph("<b>SEZIONI</b><br/>" + self.sezioni_iccd, styNormal)
            prospetti = Paragraph("<b>PROSPETTI</b><br/>"+ self.prospetti_iccd, styNormal)                    #manca valore
            foto = Paragraph("<b>FOTOGRAFIE</b><br/>"+ self.foto_iccd, styNormal)            #manca valore

           

            t_muraria = Paragraph("<b>TIPOLOGIA DELL'OPERA</b><br/>"+ str(self.tipologia_opera), styNormal)
            t_costruttiva = Paragraph("<b>TECNICA COSTRUTTIVA</b><br/>"+ str(self.tecnica_muraria_usm), styNormal)
            sezione_muraria = Paragraph("<b>SEZIONE MURARIA</b><br/>"+ str(self.sezione_muraria), styNormal)
            
            modulo = Paragraph("<b>MODULO</b><br/>"+ str(self.modulo_usm), styNormal)
            
            
            if bool(self.lunghezza_usm) and bool(self.altezza_usm):
                misure = Paragraph("<b>MISURE</b><br/>" + 'Lun. '+ self.lunghezza_usm + ' x '+ 'Alt. ' + self.altezza_usm + 'm', styNormal)
            elif bool(self.lunghezza_usm) and  not bool(self.altezza_usm):
                misure = Paragraph("<b>MISURE</b><br/>" + 'Lun. ' + self.lunghezza_usm + 'm', styNormal)
            elif bool(self.altezza_usm) and  not bool(self.lunghezza_usm):
                misure = Paragraph("<b>MISURE</b><br/>" + 'Alt. ' + self.altezza_usm + 'm', styNormal)
            else:
                misure = Paragraph("<b>MISURE</b><br/>", styNormal)

            superficie_analizzata = Paragraph("<b>SUPERFICIE ANALIZZATA</b><br/>"+ str(self.superficie_analizzata), styNormal)
            
            d_stratigrafica = Paragraph("<b>DEFINIZIONE E POSIZIONE</b><br/>" + self.d_stratigrafica+"<br/>"+self.d_interpretativa, styNormal)
            

            #6 row

            criteri_distinzione = Paragraph("<b>CRITERI DI DISTINZIONE</b><br/>" + self.criteri_distinzione, styNormal)

            #7 row

            provenienza_materiali = Paragraph("<b>PROVENIENZA MATERIALI</b><br/>"+self.provenienza_materiali_usm,styNormal2)
            
            uso_primario = Paragraph("<b>USO PRIMARIO</b><br/>" + self.uso_primario_usm,styNormal2)
            
            reimpiego = Paragraph("<b>REIMPIEGO</b><br/>"+self.reimp, styNormal2)

            orientamento = Paragraph("<b>ORIENTAMENTO</b><br/>"+self.orientamento, styNormal)
            
            #8-9 row
            stato_conservazione = Paragraph("<b>STATO DI CONSERVAZIONE</b><br/>" + self.stato_di_conservazione, styNormal)
            
            
           
            label_laterizi = Paragraph("<b>LATERIZI<br/></b>", styVerticale)
            materiali = Paragraph("<b>MATERIALI</b><br/>", styNormal2)
            lavorazione = Paragraph("<b>LAVORAZIONE</b><br/>",  styNormal2)
            consistenza = Paragraph("<b>CONSISTENZA</b><br/>", styNormal2)
            forma = Paragraph("<b>FORMA</b><br/>", styNormal2)
            colore = Paragraph("<b>COLORE</b><br/>", styNormal2)
            impasto = Paragraph("<b>IMPASTO</b><br/>", styNormal2)
            posa_opera= Paragraph("<b>POSA IN OPERA</b><br/>", styNormal2)
            
            
            materiali_1 =Paragraph(self.materiali_lat,styNormal)
            lavorazione_1 =Paragraph(self.lavorazione_lat,styNormal)
            consistenza_1 =Paragraph(self.consistenza_lat,styNormal)
            forma_1 =Paragraph(self.forma_lat,styNormal)
            colore_1 =Paragraph(self.colore_lat,styNormal)
            impasto_1 =Paragraph(self.impasto_lat,styNormal)
            posa_opera_1 =Paragraph(self.posa_opera,styNormal)
            #taglio_l = Paragraph(self.taglio_p,styNormal)
            label_pietra = Paragraph("<b>ELEMENTI<br/>LITICI</b>", styVerticale)
            p_1 =Paragraph(self.materiale_p,styNormal)
            p_2 =Paragraph(self.lavorazione,styNormal)
            p_3 =Paragraph(self.consistenza_p,styNormal)
            p_4 =Paragraph(self.forma_p,styNormal)
            p_5 =Paragraph(self.colore_p,styNormal)
            taglio= Paragraph("<b>TAGLIO</b><br/>"+ self.taglio_p, styNormal)
            p_7 =Paragraph(self.posa_opera_p,styNormal)
            
            #12 row
            n=Paragraph('',styNormal)
            
            tipo = Paragraph("<b>TIPO</b><br/>", styNormal)
            consistenza_l = Paragraph("<b>CONSISTENZA</b><br/>",  styNormal)
            colore_l = Paragraph("<b>COLORE</b><br/>", styNormal)
            inerti = Paragraph("<b>INERTI</b><br/>", styNormal)
            spessore = Paragraph("<b>SPESSORE</b><br/>", styNormal)
            rifinitura = Paragraph("<b>RIFINITURA</b><br/>", styNormal)
            
            label_legante= Paragraph("<b>LEGANTE<br/></b>", styVerticale)
            tipo_1 =Paragraph(self.tipo_legante_usm,styNormal)
            consistenza_2 =Paragraph(self.cons_legante,styNormal)
            colore_aaa =self.unzip_colore_usm()
            inerti_aaa =self.unzip_inerti_usm()
            colore_3 =Paragraph(colore_aaa,styNormal)
            inerti_4 =Paragraph(inerti_aaa,styNormal)
            spessore_5 =Paragraph(self.spessore_usm,styNormal)
            rifinitura_6 =Paragraph(self.rifinitura_usm,styNormal)
            
            note_legante = Paragraph("<b>NOTE SPECIFICHE DEL LEGANTE</b><br/>" , styDescrizione)
            note_materiali = Paragraph("<b>NOTE SPECIFICHE SUI MATERIALI</b><br/><br/><br/><br/><br/><br/>" , styDescrizione)
            

            #13-22 row

            si_lega_a = Paragraph("<b>SI LEGA A</b><br/>" + self.si_lega_a, styNormal)
            uguale_a = Paragraph("<b>UGUALE A</b><br/>" + self.uguale_a, styNormal)
            copre = Paragraph("<b>COPRE</b><br/>" + self.copre, styNormal)
            coperto_da = Paragraph("<b>COPERTO DA</b><br/>" + self.coperto_da, styNormal)
            riempie = Paragraph("<b>RIEMPIE</b><br/>" + self.riempie, styNormal)
            riempito_da = Paragraph("<b>RIEMPITO DA</b><br/>" + self.riempito_da, styNormal)
            taglia = Paragraph("<b>TAGLIA</b><br/>" + self.taglia, styNormal)
            tagliato_da = Paragraph("<b>TAGLIATO DA</b><br/>" + self.tagliato_da, styNormal)
            si_appoggia_a = Paragraph("<b>SI APPOGGIA A</b><br/>" + self.si_appoggia_a, styNormal)
            gli_si_appoggia = Paragraph("<b>GLI SI APPOGGIA</b><br/>" + self.gli_si_appoggia, styNormal)

            label_sequenza_stratigrafica = Paragraph("<b>S<br/>E<br/>Q<br/>U<br/>E<br/>N<br/>Z<br/>A<br/><br/>S<br/>T<br/>R<br/>A<br/>T<br/>I<br/>G<br/>R<br/>A<br/>F<br/>I<br/>C<br/>A</b>", styVerticale)

            posteriore_a = Paragraph("<b>POSTERIORE A</b><br/>" + self.copre +"<br/>" + self.riempie +"<br/>"+  self.taglia+ "<br/>" +   self.si_appoggia_a, styNormal)               # manca valore
            anteriore_a = Paragraph("<b>ANTERIORE A</b><br/>"+ self.coperto_da +"<br/>"+  self.riempito_da +"<br/>"+ self.tagliato_da +  "<br/>" + self.gli_si_appoggia, styNormal)                 # manca valore

            descrizione = Paragraph("<b>DESCRIZIONE</b><br/>" + self.descrizione, styDescrizione)

            osservazioni = Paragraph("<b>OSSERVAZIONI</b><br/>" + self.osservazioni, styDescrizione)

            #24 row

            interpretazione = Paragraph("<b>INTERPRETAZIONE</b><br/>" + self.interpretazione, styDescrizione)

            campioni_malta = Paragraph("<b>CAMPIONATURE MALTA</b><br/>"+ str(self.campioni_malta_usm), styNormal)
            campioni_mattone = Paragraph("<b>CAMPIONATURE LATERIZI</b><br/>"+ str(self.campioni_mattone_usm), styNormal)
            campioni_pietra = Paragraph("<b>CAMPIONATURE ELEMENTI LITICI</b><br/>"+ str(self.campioni_pietra_usm), styNormal)

            elementi_datanti = Paragraph("<b>ELEMENTI DATANTI</b><br/>" + self.elem_datanti, styDescrizione)

            #26 row

            datazione_ipotesi = Paragraph("<b>DATAZIONE</b><br/>" + str(self.datazione), styNormal)
            periodo_o_fase = Paragraph("<b>PERIODO O FASE</b><br/>Periodo iniziale: "+self.periodo_iniziale+"<br/>Fase iniziale: "+self.fase_iniziale+"<br/>Periodo finale: "+self.periodo_finale+"<br/>Fase finale: "+self.fase_finale, styNormal)

            affidabilita = Paragraph("<b>AFFIDABILITÀ STRATIGRAFICA</b><br/>" + self.affidabilita, styNormal)
            direttore = Paragraph("<b>RESPONSABILE SCIENTIFICO DELLE INDAGINI</b><br/>" + self.direttore_us, styNormal)
            responsabile2 = Paragraph("<b>RESPONSABILE COMPILAZIONE SUL CAMPO</b><br/>" + self.schedatore, styNormal)
            responsabile = Paragraph("<b>RESPONSABILE RIELABORAZIONE</b><br/>" + self.responsabile_us, styNormal)
            data_rilievo = Paragraph("<b>DATA RILEVAMENTO SUL CAMPO</b><br/>" + self.data_rilevazione, styNormal)
            data_rielaborazione = Paragraph("<b>DATA RIELABORAZIONE</b><br/>" + self.data_rielaborazione, styNormal)
            attivita = Paragraph("<b>ATTIVITÀ</b><br/>" + self.attivita, styNormal)
            licenza =  Paragraph("<b>MIBACT- ICCD_licenza CC BY-SA 4.0_Creative Commons Attribution-ShareAlike 4.0 International</b>",styL)
            # schema

            # schema
            cell_schema = [
                # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
                [unita_tipo, '01' , label_ente_responsabile, '03', '04', '05', '06', '07' , '08', '09', '10', label_unita_stratigrafica, '12', '13', '14', '15', '16', '17'],
                ['00', '01', sop, '03', '04' , '05', '06','07' , '08','09', '10', label_sas, '12', '13', '14', '15', '16', '17'],
                [sito, '01', '02', '03', '04', '05' , '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [area, '01', '02', '03', '04', '05' , '06', '07', '08', '09', '10', saggio, '12', '13', '14', '15', '16', '17'],
                [ambiente, '01', '02', '03', posizione, '04' , '06', settore, '08', quadrato, '10', quote, '12', '13', '14', '15', '16', '17'],
                [piante, '01','02' , '03', prospetti, '05', '06',sezioni, '08', '09', '10', foto, '12', '13', '14', '15', '16', '17'],
                [t_muraria, '01', '02', '03', '04', '05', '06', t_costruttiva, '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [sezione_muraria, '01', '02', '03', '04', '05', '06', modulo, '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [misure, '01', '02', '03', '04', '05', '06', superficie_analizzata, '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [d_stratigrafica, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [criteri_distinzione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                
                
                [provenienza_materiali, '01', '02', '03', '04', '05', '06', orientamento, '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [uso_primario, '01', '02', '03', reimpiego, '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [stato_conservazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                [materiali, '01', '02', lavorazione, '04',  consistenza,'06', '07', forma, '09', colore,'11',  impasto, '13', '14', posa_opera, '16', '17'],
                [label_laterizi,materiali_1, '02', lavorazione_1, '04',  consistenza_1,'06', '07', forma_1, '09', colore_1, '11', impasto_1, '13', '14', posa_opera_1, '16', '17'],
                [label_pietra, p_1, '02', p_2, '04',  p_3,'06', '07', p_4, '09', p_5, '11', taglio, '13', '14', p_7, '16', '17'],
                
                [note_materiali, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                [n, tipo, '02', '03', consistenza_l,'05' , '06',inerti, '08','09' , colore_l, '11', spessore, '13', '14', rifinitura, '16', '17'],
                [label_legante, tipo_1, '02', '03', consistenza_2, '05', '06', inerti_4, '08', '09', colore_3, '11', spessore_5, '13', '14', rifinitura_6, '16', '17'],
                [note_legante, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
				
				[uguale_a, '01', '02', '03', '04', '05', si_lega_a, '07', '08', '09', '10', '11', label_sequenza_stratigrafica, posteriore_a, '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [gli_si_appoggia, '01', '02', '03', '04', '05', si_appoggia_a, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [coperto_da, '01', '02', '03', '04', '05', copre, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', anteriore_a , '14', '15', '16', '17'],
                [tagliato_da, '01', '02', '03', '04', '05', taglia, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [riempito_da, '01', '02', '03', '04', '05', riempie, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
				[descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
				[osservazioni, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [interpretazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                [datazione_ipotesi, '01', '02', '03', '04', '05', periodo_o_fase, '07', '08', '09', '10', '11', attivita, '13', '14', '15', '16', '17'],
                [elementi_datanti, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [campioni_pietra, '01', '02', '03', '04', '05', campioni_mattone, '07', '08', '09', '10', '11', campioni_malta, '13', '14', '15', '16', '17'],
                
                [affidabilita, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [direttore, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [data_rilievo, '01', '02', '03', '04', '05', '06', '07', '08', responsabile, '10', '11', '12', '13', '14', '15', '16', '17'],
                [data_rielaborazione, '01', '02', '03', '04', '05', '06', '07', '08', responsabile2, '10', '11', '12', '13', '14', '15', '16', '17'],
                ]

            # table style
            table_style = [
                ('GRID', (0, 0), (-1, -1), 0.3, colors.black),
                # 0 row
                ('SPAN', (0, 0), (1, 1)),  # unita tipo
                ('VALIGN', (0, 0), (1, 1), 'MIDDLE'),

                ('SPAN', (2, 0), (10, 0)),  # label n. catalogo generale
                ('SPAN', (11, 0), (17, 0)),  # label n. catalogo internazionale
                ('VALIGN', (2, 0), (12,1), 'TOP'),

                # 1 row
                ('SPAN', (2, 1), (10, 1)),  # n. catalogo generale
                ('SPAN', (11, 1), (17, 1)),  # catalogo internazionale
                ('VALIGN', (2, 0), (17, 1), 'TOP'),

                # 2 row
                ('SPAN', (0, 2), (17, 2)),  # sito
                
                ('VALIGN', (0, 2), (17, 2), 'TOP'),

                # 3 row
                ('SPAN', (0, 3), (10, 3)),  # piante
                ('SPAN', (11, 3), (17, 3)),  # sezioni
                ('VALIGN', (0, 3), (17, 3), 'TOP'),

                # 4 row
                ('SPAN', (0, 4), (3, 4)),  # definizione
                ('SPAN', (4, 4), (6, 4)),  # definizione
                ('SPAN', (7, 4), (8, 4)),  # definizione
                ('SPAN', (9, 4), (10, 4)),  # definizione
                ('SPAN', (11, 4), (17, 4)),  # definizione
                ('VALIGN', (0, 4), (17, 4), 'TOP'),

                # 5 row
                ('SPAN', (0, 5), (3, 5)),  # definizione
                ('SPAN', (4,5), (6, 5)),  # definizione
                ('SPAN', (7, 5), (10, 5)),  # definizione
                ('SPAN', (11, 5), (17, 5)),  # definizione
                ('VALIGN', (0, 5), (17, 5), 'TOP'),

                # 5 row
                ('SPAN', (0, 6), (6, 6)),  # definizione
                ('SPAN', (7,6), (17, 6)),  # definizione
                ('VALIGN', (0, 6), (17, 6), 'TOP'),
                
                # 5 row
                ('SPAN', (0, 7), (6, 7)),  # definizione
                ('SPAN', (7,7), (17, 7)),  # definizione
                ('VALIGN', (0, 7), (17, 7), 'TOP'),
                
                # 5 row
                ('SPAN', (0, 8), (6, 8)),  # definizione
                ('SPAN', (7,8), (17, 8)),  # definizione
                ('VALIGN', (0, 8), (17, 8), 'TOP'),
                
                # 6 row
                ('SPAN', (0, 9), (17, 9)),  # modo di formazione
                ('VALIGN', (0, 9), (17, 9), 'TOP'),

                # 7 row
                ('SPAN', (0, 10), (17, 10)),  # label componenti
                ('VALIGN', (0, 10), (17, 10), 'TOP'),

                ('SPAN', (0, 11), (6, 11)),  # label componenti
                ('SPAN', (7, 11), (17, 12)),  # label geologici
                ('SPAN', (0, 12), (3, 12)),  # label organici
                ('SPAN', (4, 12), (6, 12)),  # label artificiali
                ('VALIGN', (0, 11), (17, 12), 'TOP'),
                
                # 7 row
                ('SPAN', (0, 13), (17, 13)),  # label componenti
                ('VALIGN', (0, 13), (17, 13), 'TOP'),
                
                # 10 row
                ('SPAN', (0, 14), (2, 14)),  # label componenti
                ('SPAN', (3, 14), (4, 14)),  # label geologici
                ('SPAN', (5, 14), (7, 14)),  # label organici
                ('SPAN', (8, 14), (9, 14)),  # label artificiali
                ('SPAN', (10, 14), (11, 14)),  #  geologici
                ('SPAN', (12, 14), (14, 14)),  #  organici
                ('SPAN', (15, 14), (17, 14)),  #  artificiali
                ('VALIGN', (0, 14), (17, 14), 'TOP'),

                # 11-12 row
                ('SPAN', (0, 15), (0, 15)),  # label componenti
				('SPAN', (1, 15), (2, 15)),  # label componenti
                ('SPAN', (3, 15), (4, 15)),  # label geologici
                ('SPAN', (5, 15), (7, 15)),  # label organici
                ('SPAN', (8, 15), (9, 15)),  # label artificiali
                ('SPAN', (10, 15), (11, 15)),  #  geologici
                ('SPAN', (12, 15), (14, 15)),  #  organici
                ('SPAN', (15, 15), (17, 15)),  #  artificiali
                ('VALIGN', (0, 15), (17, 15), 'TOP'),

                # 13-14 row
                ('SPAN', (0, 16), (0, 16)),  # label componenti
				('SPAN', (1, 16), (2, 16)),  # label componenti
                ('SPAN', (3, 16), (4, 16)),  # label geologici
                ('SPAN', (5, 16), (7, 16)),  # label organici
                ('SPAN', (8, 16), (9, 16)),  # label artificiali
                ('SPAN', (10, 16), (11, 16)),  #  geologici
                ('SPAN', (12, 16), (14, 16)),  #  organici
                ('SPAN', (15, 16), (17, 16)),  #  artificiali
                ('VALIGN', (0, 16), (17, 16), 'TOP'),
                
                # 17-21 row
                ('SPAN', (0, 17), (17, 17)),  # descrizione
                ('VALIGN', (0, 17), (17, 17), 'TOP'),
                
                # 15 row
                ('SPAN', (0, 18), (0, 18)),  # label componenti
				('SPAN', (1, 18), (3, 18)),  # label componenti
                ('SPAN', (4, 18), (6, 18)),  # label geologici
                ('SPAN', (7, 18), (9, 18)),  # label organici
                ('SPAN', (10, 18), (11, 18)),  # label artificiali
                ('SPAN', (12, 18), (14, 18)),  #  geologici
                ('SPAN', (15, 18), (17, 18)),  #  organici
                ('VALIGN', (0, 18), (17, 18), 'TOP'),
				
				# 16 row
                ('SPAN', (0, 19), (0, 19)),  # label componenti
				('SPAN', (1, 19), (3, 19)),  # label componenti
                ('SPAN', (4, 19), (6, 19)),  # label geologici
                ('SPAN', (7, 19), (9, 19)),  # label organici
                ('SPAN', (10, 19), (11, 19)),  # label artificiali
                ('SPAN', (12, 19), (14, 19)),  #  geologici
                ('SPAN', (15, 19), (17, 19)),  #  organici
                ('VALIGN', (0, 19), (17, 19), 'TOP'),
				
				
				# 17-21 row
                ('SPAN', (0, 20), (17, 20)),  # descrizione
                ('VALIGN', (0, 20), (17, 20), 'TOP'),

                # 22-31 row
                ('SPAN', (0, 21), (5, 22)),    # uguale a
                ('SPAN', (0, 23), (5, 24)),    # gli si appoggia
                ('SPAN', (0, 25), (5, 26)),    # coperto da
                ('SPAN', (0, 27), (5, 28)),    # tagliato da
                ('SPAN', (0, 29), (5, 30)),    # riempito da
                ('SPAN', (6, 21), (11, 22)),   # si lega a
                ('SPAN', (6, 23), (11, 24)),   # si appoggia a
                ('SPAN', (6, 25), (11, 26)),   # copre
                ('SPAN', (6, 27), (11, 28)),   # taglia
                ('SPAN', (6, 29), (11, 30)),   # riempie
                ('SPAN', (12, 21), (12, 30)),  # label sequenza stratigrafica
                ('SPAN', (13, 21), (17, 25)),  # posteriore a
                ('SPAN', (13, 26), (17, 30)),  # uguale a
                ('VALIGN', (0, 21), (17, 30), 'TOP'),



                ('SPAN', (0, 31), (17, 31)),  # descrizione
                ('VALIGN', (0, 31), (17, 31), 'TOP'),
                # 32-34 row
                ('SPAN', (0, 32), (17, 32)),  # osservazioni
                ('VALIGN', (0, 32), (17, 32), 'TOP'),

                # 35-37 row
                ('SPAN', (0, 33), (17, 33)),  # interpretazione
                ('VALIGN', (0, 33), (17, 33), 'TOP'),

                # # 41-42 row
                
                # #29 row
                ('SPAN', (0, 34), (5, 34)),  # affidabilita stratigrafica
                ('SPAN', (6, 34), (11, 34)),  # direttore
                ('SPAN', (12, 34), (17, 34)),  # responsabile
                ('VALIGN', (0, 34), (17, 34), 'TOP'),
                
                
                ('SPAN', (0, 35), (17, 35)),  # elementi datanti
                ('VALIGN', (0, 35), (17, 35), 'TOP'),

                # #35 row
                # #29 row
                ('SPAN', (0, 36), (5, 36)),  # affidabilita stratigrafica
                ('SPAN', (6, 36), (11, 36)),  # direttore
                ('SPAN', (12, 36), (17, 36)),  # responsabile
                ('VALIGN', (0, 36), (17, 36), 'TOP'),
                #29 row
                ('SPAN', (0, 37), (17, 37)),  # affidabilita stratigrafica
                
                ('VALIGN', (0, 37), (17, 37), 'TOP'),

                ('SPAN', (0, 38), (17, 38)),  # affidabilita stratigrafica
                ('VALIGN', (0, 38), (17, 38), 'TOP'),
                
                ('SPAN', (0, 39), (8, 39)),  # affidabilita stratigrafica
                ('SPAN', (9, 39), (17, 39)),  # affidabilita stratigrafica
                ('VALIGN', (0, 39), (17, 39), 'TOP'),
                
                ('SPAN', (0, 40), (8, 40)),  # affidabilita stratigrafica
                ('SPAN', (9, 40), (17, 40)),  # affidabilita stratigrafica
                ('VALIGN', (0, 40), (17, 40), 'TOP'),        

                
            ]

            colWidths = (15,30,30,30,30,30,30,30,30,30,30,30,20,30,30,30,30,30)
            rowHeights = None

            t = Table(cell_schema, colWidths=colWidths, rowHeights=rowHeights, style=table_style)

            return t
        
        
    def create_sheet_en(self): #scheda us in stile ICCD Italiano
        self.unzip_rapporti_stratigrafici_en()
        self.unzip_documentazione_en()

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.fontSize = 7
        styNormal.fontName='Cambria'
        styNormal.alignment = 0  # LEFT

        styleSheet = getSampleStyleSheet()
        styNormal2 = styleSheet['Normal']
        styNormal2.spaceBefore = 20
        styNormal2.spaceAfter = 20
        styNormal2.fontSize = 7
        styNormal2.fontName='Cambria'
        styNormal2.alignment = 0  # LEFT
        
        
        styleSheet = getSampleStyleSheet()
        styL = styleSheet['Normal']
        styL.spaceBefore = 20
        styL.spaceAfter = 20
        styL.fontSize = 2
        styL.fontName='Cambria'
        styL.alignment = 1
        
        
        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.fontSize = 7
        styDescrizione.fontName='Cambria'
        styDescrizione.alignment = 4  # Justified

        styleSheet = getSampleStyleSheet()
        styUnitaTipo = styleSheet['Normal']
        styUnitaTipo.spaceBefore = 20
        styUnitaTipo.spaceAfter = 20
        styUnitaTipo.fontSize = 14
        styUnitaTipo.fontName='Cambria'
        styUnitaTipo.alignment = 1  # CENTER

        styleSheet = getSampleStyleSheet()
        styTitoloComponenti = styleSheet['Normal']
        styTitoloComponenti.spaceBefore = 20
        styTitoloComponenti.spaceAfter = 20
        styTitoloComponenti. rowHeights=0.5
        styTitoloComponenti.fontSize = 7
        styTitoloComponenti.fontName='Cambria'
        styTitoloComponenti.alignment = 1  # CENTER

        styleSheet = getSampleStyleSheet()
        styVerticale = styleSheet['Normal']
        styVerticale.spaceBefore = 20
        styVerticale.spaceAfter = 20
        styVerticale.fontSize = 7
        styVerticale.fontName='Cambria'
        styVerticale.alignment = 1  # CENTER
        styVerticale.leading=8

        #format labels

        #0-1 row Unita tipo, logo, n. catalogo generale, n. catalogo internazionale
        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path)

        logo.drawHeight = 2 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 2 * inch
        logo.hAlign = 'CENTER'
        lst = []
        lst2=[]
        lst.append(logo)
        if str(self.unita_tipo)== 'SU':
            unita_tipo = Paragraph(str(self.unita_tipo), styUnitaTipo)
            label_ente_responsabile = Paragraph("<b>RESPONSIBLE INSTITUTION</b>", styNormal)
            #label_catalogo_internazionale = Paragraph("<b>N° CATALOGO INTERNAZIONALE</b>", styNormal)
            ente_responsabile = Paragraph(str(self.n_catalogo_generale), styNormal)
            #catalogo_internazionale = Paragraph(str(self.n_catalogo_internazionale), styNormal)
            sop =  Paragraph("<b>SUPERINTENDENCE RESPONSIBLE FOR PROTECTION</b><br/>" +str(self.soprintendenza), styNormal)
            #2-3 row

            sito = Paragraph("<b>LOCATION</b><br/>" + str(self.sito), styNormal)
            #anno_di_scavo = Paragraph("<b>ANNO</b><br/>" + self.anno_scavo, styNormal)
            if self.struttura!='':
            
                area = Paragraph("<b>AREA/BUILDING/STRUCTURE</b><br/>" + str(self.area)+'/'+str(self.struttura),styNormal)
            
            else:
                area = Paragraph("<b>AREA/BUILDING/STRUCTURE</b><br/>" + str(self.area),styNormal)
            
            saggio = Paragraph("<b>ESSAY</b><br/>" + self.saggio, styNormal)
            ambiente = Paragraph("<b>PLACE</b><br/>" + self.ambient, styNormal)
            posizione = Paragraph("<b>PLACE POSITION</b><br/>" + self.posizione, styNormal)
            settore = Paragraph("<b>SECTOR</b><br/>" + self.settore, styNormal)
            quadrato = Paragraph("<b>SQUARE</b><br/>" + self.quad_par, styNormal)
            quote = Paragraph("<b>ELEVATION</b><br/>min: " + self.quota_min + "<br/>max: "+self.quota_max, styNormal)
            label_unita_stratigrafica = Paragraph("<b>NUMBER/SU CODE</b><br/>"+ str(self.us), styNormal)
            label_sas = Paragraph("<b>NUMBER/IDENTIFICATION CODE OF THE STRATIGRAPHIC ASSAY/BUILDING/STRUCTURE/FUNERARY DEPOSITION OF REFERENCE</b><br/>", styNormal)
            
            if self.formazione == 'Natural':
                label_NAT = Paragraph("<i>NAT.</i><br/>" + self.formazione, styNormal)
                label_ART = Paragraph("<i>ART.</i>",  styNormal) 
            elif self.formazione == 'Artificial':
                label_NAT = Paragraph("<i>NAT.</i>", styNormal)
                label_ART = Paragraph("<i>ART.</i><br/>"+ self.formazione, styNormal)
            elif self.formazione !='Natural' or 'Artificial':    
                label_NAT = Paragraph("<i>NAT.</i><br/>", styNormal)
                label_ART = Paragraph("<i>ART.</i>",  styNormal) 
            

            piante = Paragraph("<b>MAPS</b><br/>" + self.piante_iccd, styNormal)
            sezioni = Paragraph("<b>SECTION</b><br/>" + self.sezioni_iccd, styNormal)
            prospetti = Paragraph("<b>ELEVATION</b><br/>"+ self.prospetti_iccd, styNormal)                    #manca valore
            foto = Paragraph("<b>PHOTO</b><br/>"+ self.foto_iccd, styNormal)            #manca valore

            tabelle_materiali = Paragraph("<b>ARTEFACT TABLE REFERENCES<br/><br/>RA</b>:"+ self.ref_ra, styNormal)  #manca valore

            #5 row

            d_stratigrafica = Paragraph("<b>DEFINITION AND POSITION</b><br/>Stratigraphic definition: " + self.d_stratigrafica+"<br/>Interpretative definition: "+self.d_interpretativa, styNormal)

            #6 row

            criteri_distinzione = Paragraph("<b>DISTINCTION CRITERIA</b><br/>" + self.criteri_distinzione, styNormal)

            #7 row

            modo_formazione = Paragraph("<b>FORMING MODE</b><br/>" + self.modo_formazione, styNormal)

            #8-9 row


            organici, inorganici= self.unzip_componenti()
            inclusi = ''
            for i in eval(self.inclusi):
                if inclusi == '':
                    try:
                        inclusi += str(i[0])
                    except:
                        pass
                else:
                    try:
                        inclusi += ', ' + str(i[0])
                    except:
                        pass

            label_componenti = Paragraph("<b>COMPONENTS</b>",styVerticale)

            label_inorganici = Paragraph("<i>INORGANICS</i>",styTitoloComponenti) #inorganici
            label_organici = Paragraph("<i>ORGANIC</i>", styTitoloComponenti) #organici
            #label_artificiali = Paragraph("<i>INORGANICI</i>", styTitoloComponenti) #inclusi

            comp_organici = Paragraph(organici, styNormal) #organici
            comp_inorganici = Paragraph(inorganici, styNormal)  #geologici
            #inclusi = Paragraph(inclusi, styNormal)  #artificiali

            #10 row

            consistenza = Paragraph("<b>CONSISTENCY</b><br/>" + self.consistenza, styNormal)
            colore = Paragraph("<b>COLOR</b><br/>" + self.colore, styNormal)
            #misure = ''                 # manca valore
            if bool(self.lunghezza_max) and bool(self.larghezza_media) and bool(self.altezza_max):
                misure = Paragraph("<b>MEASURES</b><br/>" + 'Len. '+ self.lunghezza_max + ' x '+ 'Width ' + self.larghezza_media + ' x '+ 'Thick. ' + self.altezza_max + 'm', styNormal)
            elif bool(self.lunghezza_max) and bool(self.larghezza_media) and not bool(self.altezza_max):
                misure = Paragraph("<b>MEASURES</b><br/>" + 'Len. ' + self.lunghezza_max + ' x '+ 'Width '+ self.larghezza_media + 'm', styNormal)
            
            else:
                misure = Paragraph("<b>MEASURES</b><br/>", styNormal)
            #11 row

            stato_conservazione = Paragraph("<b>STATE OF PRESERVATION</b><br/>" + self.stato_di_conservazione, styNormal)

            #12 row

            descrizione = Paragraph("<b>DESCRIPTION</b><br/>" + self.descrizione, styDescrizione)

            #13-22 row

            si_lega_a = Paragraph("<b>CONNECTED TO</b><br/>" + self.si_lega_a, styNormal)
            uguale_a = Paragraph("<b>SAME AS</b><br/>" + self.uguale_a, styNormal)
            copre = Paragraph("<b>COVERS</b><br/>" + self.copre, styNormal)
            coperto_da = Paragraph("<b>COVERED BY</b><br/>" + self.coperto_da, styNormal)
            riempie = Paragraph("<b>FILLS</b><br/>" + self.riempie, styNormal)
            riempito_da = Paragraph("<b>FILLED BY</b><br/>" + self.riempito_da, styNormal)
            taglia = Paragraph("<b>CUTS</b><br/>" + self.taglia, styNormal)
            tagliato_da = Paragraph("<b>CUTTED BY</b><br/>" + self.tagliato_da, styNormal)
            si_appoggia_a = Paragraph("<b>ABUTS</b><br/>" + self.si_appoggia_a, styNormal)
            gli_si_appoggia = Paragraph("<b>SUPPORT</b><br/>" + self.gli_si_appoggia, styNormal)

            label_sequenza_stratigrafica = Paragraph("<b>S<br/>E<br/>Q<br/>U<br/>E<br/>N<br/>C<br/>E<br/><br/>S<br/>T<br/>R<br/>A<br/>T<br/>I<br/>G<br/>R<br/>A<br/>P<br/>H<br/>I<br/>C</b>", styVerticale)

            posteriore_a = Paragraph("<b>BACK TO</b><br/>" + self.copre +"<br/>" + self.riempie +"<br/>"+  self.taglia+ "<br/>" +   self.si_appoggia_a, styNormal)               # manca valore
            anteriore_a = Paragraph("<b>EARLIER TO</b><br/>"+ self.coperto_da +"<br/>"+  self.riempito_da +"<br/>"+ self.tagliato_da +  "<br/>" + self.gli_si_appoggia, styNormal)                 # manca valore

            #23 row

            osservazioni = Paragraph("<b>NOTE</b><br/>" + self.osservazioni, styDescrizione)

            #24 row

            interpretazione = Paragraph("<b>INTERPRETATION</b><br/>" + self.interpretazione, styDescrizione)

            #25 row

            elementi_datanti = Paragraph("<b>DATING ELEMENTS</b><br/>" + self.elem_datanti, styDescrizione)

            #26 row

            datazione_ipotesi = Paragraph("<b>DATING</b><br/>" + str(self.datazione), styNormal)
            periodo_o_fase = Paragraph("<b>PERIOD OR PHASE</b><br/>Starting period: "+self.periodo_iniziale+"<br/>Starting phase: "+self.fase_iniziale+"<br/>Final Period: "+self.periodo_finale+"<br/>Final phase: "+self.fase_finale, styNormal)

            #27 row

            dati_quantitativi = Paragraph("<b>ARTEFACT QUANTITY</b><br/>", styNormal)  # manca valore

            #28 row

            campioni_list = eval(self.campioni)
            campioni = ''
            for i in eval(self.campioni):
                if campioni == '':
                    try:
                        campioni += str(i[0])
                    except:
                        pass
                else:
                    try:
                        campioni += ', ' + str(i[0])
                    except:
                        pass
            campioni = Paragraph("<b>SAMPLE</b><br/>" + campioni, styNormal)
            flottazione = Paragraph("<b>FLOTTATION</b><br/>" + self.flottazione, styNormal)
            setacciatura = Paragraph("<b>SIEVING</b><br/>" + self.setacciatura, styNormal)

            #28 row

            affidabilita = Paragraph("<b>STRATIGRAPHIC RELIABILITY</b><br/>" + self.affidabilita, styNormal)
            direttore = Paragraph("<b>SCIENTIFIC HEAD OF INVESTIGATIONS</b><br/>" + self.direttore_us, styNormal)
            responsabile2 = Paragraph("<b>FIELD DIRECTOR</b><br/>" + self.schedatore, styNormal)
            responsabile = Paragraph("<b>RESPONSIBLE FOR REVISION</b><br/>" + self.responsabile_us, styNormal)
            data_rilievo = Paragraph("<b>DATE FIELDWORK</b><br/>" + self.data_rilevazione, styNormal)
            data_rielaborazione = Paragraph("<b>PROCESSING DATE</b><br/>" + self.data_rielaborazione, styNormal)
            attivita = Paragraph("<b>ACTIVITIES</b><br/>" + self.attivita, styNormal)
            licenza =  Paragraph("<b>MIBACT- ICCD_licenza CC BY-SA 4.0_Creative Commons Attribution-ShareAlike 4.0 International</b>",styL)
            # schema
            cell_schema = [
                
                [unita_tipo, '01' , label_ente_responsabile, '03', '04', '05', '06', '07' , '08', '09', '10', label_unita_stratigrafica, '12', '13', '14', '15', '16', '17'],
                ['00', '01', sop, '03', '04' , '05', '06','07' , '08','09', '10', label_sas, '12', '13', '14', '15', '16', '17'],
                [sito, '01', '02', '03', '04', '05' , '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [area, '01', '02', '03', '04', '05' , '06', '07', '08', '09', '10', saggio, '12', '13', '14', '15', '16', '17'],
                [ambiente, '01', '02', '03', posizione, '04' , '06', settore, '08', quadrato, '10', quote, '12', '13', label_NAT, '15', label_ART, '17'],
                [piante, '01', prospetti, '03', sezioni, '05', '06',foto, '08', '09', '10', tabelle_materiali, '12', '13', '14', '15', '16', '17'],
                [d_stratigrafica, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [criteri_distinzione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [modo_formazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [ label_organici, '01','02', '03', '04', '05', '06', '07', '08', label_inorganici, '10', '11','12' , '13', '14', '15', '16', '17'],
                [label_componenti, comp_organici, '02', '03', '04', '05', '06', '07', '08', comp_inorganici, '10', '11', '12', '13', '14', '15', '16', '17'],
                [consistenza, '01', '02', '03', '04', '05', colore, '07', '08', '09', '10', '11', misure, '13', '14', '15', '16', '17'],
                [stato_conservazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                [uguale_a, '01', '02', '03', '04', '05', si_lega_a, '07', '08', '09', '10', '11', label_sequenza_stratigrafica, posteriore_a, '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [gli_si_appoggia, '01', '02', '03', '04', '05', si_appoggia_a, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [coperto_da, '01', '02', '03', '04', '05', copre, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', anteriore_a , '14', '15', '16', '17'],
                [tagliato_da, '01', '02', '03', '04', '05', taglia, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [riempito_da, '01', '02', '03', '04', '05', riempie, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [osservazioni, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [interpretazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                [datazione_ipotesi, '01', '02', '03', '04', '05', periodo_o_fase, '07', '08', '09', '10', '11', attivita, '13', '14', '15', '16', '17'],
                [elementi_datanti, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [dati_quantitativi, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [campioni, '01', '02', '03', '04', '05', flottazione, '07', '08', '09', '10', '11', setacciatura, '13', '14', '15', '16', '17'],
                [affidabilita, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [direttore, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [data_rilievo, '01', '02', '03', '04', '05', '06', '07', '08', responsabile, '10', '11', '12', '13', '14', '15', '16', '17'],
                [data_rielaborazione, '01', '02', '03', '04', '05', '06', '07', '08', responsabile2, '10', '11', '12', '13', '14', '15', '16', '17'],
                ]

            # table style
            table_style = [
               
                ('GRID', (0, 0), (-1, -1), 0.3, colors.black),
                # 0 row
                ('SPAN', (0, 0), (1, 1)),  # unita tipo
                ('VALIGN', (0, 0), (1, 1), 'MIDDLE'),

                ('SPAN', (2, 0), (10, 0)),  # label n. catalogo generale
                ('SPAN', (11, 0), (17, 0)),  # label n. catalogo internazionale
                ('VALIGN', (2, 0), (12,1), 'TOP'),

                # 1 row
                ('SPAN', (2, 1), (10, 1)),  # n. catalogo generale
                ('SPAN', (11, 1), (17, 1)),  # catalogo internazionale
                ('VALIGN', (2, 0), (17, 1), 'TOP'),

                # 2 row
                ('SPAN', (0, 2), (17, 2)),  # sito
                
                ('VALIGN', (0, 2), (17, 2), 'TOP'),

                # 3 row
                ('SPAN', (0, 3), (10, 3)),  # piante
                ('SPAN', (11, 3), (17, 3)),  # sezioni
                ('VALIGN', (0, 3), (17, 3), 'TOP'),

                # 4 row
                ('SPAN', (0, 4), (3, 4)),  # definizione
                ('SPAN', (4, 4), (6, 4)),  # definizione
                ('SPAN', (7, 4), (8, 4)),  # definizione
                ('SPAN', (9, 4), (10, 4)),  # definizione
                ('SPAN', (11, 4), (13, 4)),  # definizione
                ('SPAN', (14, 4), (15, 4)),  # definizione
                ('SPAN', (16, 4), (17, 4)),  # definizione        
                ('VALIGN', (0, 4), (17, 4), 'TOP'),

                # 5 row
                ('SPAN', (0, 5), (1, 5)),  # definizione
                ('SPAN', (2,5), (3, 5)),  # definizione
                ('SPAN', (4, 5), (6, 5)),  # definizione
                ('SPAN', (7, 5), (10, 5)),  # definizione
                ('SPAN', (11, 5), (17, 5)),  # definizione
                ('VALIGN', (0, 5), (17, 5), 'TOP'),

                # 6 row
                ('SPAN', (0, 6), (17, 6)),  # modo di formazione
                ('VALIGN', (0, 6), (17, 6), 'TOP'),

                # 7 row
                ('SPAN', (0, 7), (17, 7)),  # label componenti
                ('VALIGN', (0, 7), (17, 7), 'TOP'),

                # 8 row
                ('SPAN', (0, 8), (17, 8)),  # consistenza
                ('VALIGN', (0, 8), (17, 8), 'TOP'),
                
                # 9-10 row
                
                ('SPAN', (0, 9), (8, 9)),  # consistenza
                ('SPAN', (9, 9), (17, 9)),  # consistenza
                ('SPAN', (0, 10), (0, 10)),  # consistenza
                ('SPAN', (1, 10), (8, 10)),  # consistenza
                ('SPAN', (9, 10), (17, 10)),  # consistenza
                ('VALIGN', (0, 9), (17, 10), 'TOP'),
                
                
                
                
                # 11 row
                ('SPAN', (0, 11), (5, 11)),  # stato di conservazione
                ('SPAN', (6, 11), (11, 11)),  # stato di conservazione
                ('SPAN', (12, 11), (17, 11)),  # stato di conservazione
                ('VALIGN', (0, 11), (17, 11), 'TOP'),

                # 12 row
                ('SPAN', (0, 12), (17, 12)),  # descrizione
                ('VALIGN', (0, 12), (17, 12), 'TOP'),

                # 13-22 row
                ('SPAN', (0, 13), (5, 14)),    # uguale a
                ('SPAN', (0, 15), (5, 16)),    # gli si appoggia
                ('SPAN', (0, 17), (5, 18)),    # coperto da
                ('SPAN', (0, 19), (5, 20)),    # tagliato da
                ('SPAN', (0, 21), (5, 22)),    # riempito da
                ('SPAN', (6, 13), (11, 14)),   # si lega a
                ('SPAN', (6, 15), (11, 16)),   # si appoggia a
                ('SPAN', (6, 17), (11, 18)),   # copre
                ('SPAN', (6, 19), (11, 20)),   # taglia
                ('SPAN', (6, 21), (11, 22)),   # riempie
                ('SPAN', (12, 13), (12, 22)),  # label sequenza stratigrafica
                ('SPAN', (13, 13), (17, 17)),  # posteriore a
                ('SPAN', (13, 18), (17, 22)),  # uguale a
                ('VALIGN', (0, 13), (17, 22), 'TOP'),

                # 23 row
                ('SPAN', (0, 23), (17, 23)),  # DESCRIZIONE
                ('VALIGN', (0, 23), (17, 23), 'TOP'),

                # 24 row
                ('SPAN', (0, 24), (17, 24)),  # OSSERVAZIONI
                ('VALIGN', (0, 24), (17, 24), 'TOP'),

                # 25 row

                ('SPAN', (0, 25), (17, 25)),  # INTERPRETAZIONI
                ('VALIGN', (0, 25), (17, 25), 'TOP'),

                #26 row

                ('SPAN', (0, 26), (5, 26)),  # datazione
                ('SPAN', (6, 26), (11, 26)),  # periodo o fase
                ('SPAN', (12, 26), (17, 26)),  # ATTIVITA
                ('VALIGN', (0, 26), (17, 26), 'TOP'),

                # #27 row

                ('SPAN', (0, 27), (17, 27)),  # elementi datanti
                ('VALIGN', (0, 27), (17, 27), 'TOP'),

                ('SPAN', (0, 28), (17, 28)),  # elementi datanti
                ('VALIGN', (0, 28), (17, 28), 'TOP'),
                
                #28 row
                ('SPAN', (0, 29), (5, 29)),  # campionature
                ('SPAN', (6, 29), (11, 29)),  # flottazione
                ('SPAN', (12, 29), (17, 29)),  # setacciatura
                ('VALIGN', (0, 29), (17, 29), 'TOP'),

                #29 row
                ('SPAN', (0, 30), (17, 30)),  # affidabilita stratigrafica
                
                ('VALIGN', (0, 30), (17, 30), 'TOP'),

                ('SPAN', (0, 31), (17, 31)),  # affidabilita stratigrafica
                ('VALIGN', (0, 31), (17, 31), 'TOP'),
                
                ('SPAN', (0, 32), (8, 32)),  # affidabilita stratigrafica
                ('SPAN', (9, 32), (17, 32)),  # affidabilita stratigrafica
                ('VALIGN', (0, 32), (17, 32), 'TOP'),
                
                ('SPAN', (0, 33), (8, 33)),  # affidabilita stratigrafica
                ('SPAN', (9, 33), (17, 33)),  # affidabilita stratigrafica
                ('VALIGN', (0, 33), (17, 33), 'TOP'),               
            ]

            colWidths = (15,30,30,30,30,30,30,30,30,30,30,30,20,30,30,30,30,30)
            rowHeights = None
            
            t = Table(cell_schema, colWidths=colWidths, rowHeights=rowHeights, style=table_style)
            lst.append(logo)
            
            return t
        elif str(self.unita_tipo)=='WSU':
            unita_tipo = Paragraph(str(self.unita_tipo), styUnitaTipo)
            label_ente_responsabile = Paragraph("<b>RESPONSIBLE INSTITUTION</b>", styNormal)
            #label_catalogo_internazionale = Paragraph("<b>N° CATALOGO INTERNAZIONALE</b>", styNormal)
            ente_responsabile = Paragraph(str(self.n_catalogo_generale), styNormal)
            #catalogo_internazionale = Paragraph(str(self.n_catalogo_internazionale), styNormal)
            sop =  Paragraph("<b>SUPERINTENDENCE RESPONSIBLE FOR PROTECTION</b><br/>" +str(self.soprintendenza), styNormal)
            #2-3 row

            sito = Paragraph("<b>LOCATION</b><br/>" + str(self.sito), styNormal)
            #anno_di_scavo = Paragraph("<b>ANNO</b><br/>" + self.anno_scavo, styNormal)
            if self.struttura!='':
            
                area = Paragraph("<b>AREA/BUILDING/STRUCTURE</b><br/>" + str(self.area)+'/'+str(self.struttura),styNormal)
            
            else:
                area = Paragraph("<b>AREA/BUILDING/STRUCTURE</b><br/>" + str(self.area),styNormal)
            
            saggio = Paragraph("<b>ESSAY</b><br/>" + self.saggio, styNormal)
            ambiente = Paragraph("<b>PLACE</b><br/>" + self.ambient, styNormal)
            posizione = Paragraph("<b>PLACE POSITION</b><br/>" + self.posizione, styNormal)
            settore = Paragraph("<b>SECTOR</b><br/>" + self.settore, styNormal)
            quadrato = Paragraph("<b>SQUARE</b><br/>" + self.quad_par, styNormal)
            quote = Paragraph("<b>ELEVATION</b><br/>min: " + self.quota_min + "<br/>max: "+self.quota_max, styNormal)
            label_unita_stratigrafica = Paragraph("<b>NUMBER/SU CODE</b><br/>"+ str(self.us), styNormal)
            label_sas = Paragraph("<b>NUMBER/IDENTIFICATION CODE OF THE STRATIGRAPHIC ASSAY/BUILDING/STRUCTURE/FUNERARY DEPOSITION OF REFERENCE</b><br/>", styNormal)
            
            if self.formazione == 'Natural':
                label_NAT = Paragraph("<i>NAT.</i><br/>" + self.formazione, styNormal)
                label_ART = Paragraph("<i>ART.</i>",  styNormal) 
            elif self.formazione == 'Artificial':
                label_NAT = Paragraph("<i>NAT.</i>", styNormal)
                label_ART = Paragraph("<i>ART.</i><br/>"+ self.formazione, styNormal)
            elif self.formazione !='Natural' or 'Artificial':    
                label_NAT = Paragraph("<i>NAT.</i><br/>", styNormal)
                label_ART = Paragraph("<i>ART.</i>",  styNormal) 
            

            piante = Paragraph("<b>MAPS</b><br/>" + self.piante_iccd, styNormal)
            sezioni = Paragraph("<b>SECTION</b><br/>" + self.sezioni_iccd, styNormal)
            prospetti = Paragraph("<b>ELEVATION</b><br/>"+ self.prospetti_iccd, styNormal)                    #manca valore
            foto = Paragraph("<b>PHOTO</b><br/>"+ self.foto_iccd, styNormal) 

           

            t_muraria = Paragraph("<b>TYPE OF MASONRY</b><br/>"+ str(self.tipologia_opera), styNormal)
            t_costruttiva = Paragraph("<b>CONSTRUCTION TECHNIQUE</b><br/>"+ str(self.tecnica_muraria_usm), styNormal)
            sezione_muraria = Paragraph("<b>CROSS-SECTION</b><br/>"+ str(self.sezione_muraria), styNormal)
            
            modulo = Paragraph("<b>MODULE</b><br/>"+ str(self.modulo_usm), styNormal)
            
            
            if bool(self.lunghezza_usm) and bool(self.altezza_usm):
                misure = Paragraph("<b>MEASURES</b><br/>" + 'Len. '+ self.lunghezza_usm + ' x '+ 'Elev. ' + self.altezza_usm + 'm', styNormal)
            elif bool(self.lunghezza_usm) and  not bool(self.altezza_usm):
                misure = Paragraph("<b>MEASURES</b><br/>" + 'Len. ' + self.lunghezza_usm + 'm', styNormal)
            elif bool(self.altezza_usm) and  not bool(self.lunghezza_usm):
                misure = Paragraph("<b>MEASURES</b><br/>" + 'Elev. ' + self.altezza_usm + 'm', styNormal)
            else:
                misure = Paragraph("<b>MEASURES</b><br/>", styNormal)
            superficie_analizzata = Paragraph("<b>ANALYSED SURFACE</b><br/>"+ str(self.superficie_analizzata), styNormal)
            
            d_stratigrafica = Paragraph("<b>DEFINITION AND POSITION</b><br/>" + self.d_stratigrafica+"<br/>"+self.d_interpretativa, styNormal)
            

            #6 row

            criteri_distinzione = Paragraph("<b>DISTINCTION CRITERIA</b><br/>" + self.criteri_distinzione, styNormal)

            #7 row

            provenienza_materiali = Paragraph("<b>ARTEFACT SOURCE</b><br/>"+self.provenienza_materiali_usm,styNormal2)
            
            uso_primario = Paragraph("<b>PRIMARY USE</b><br/>" + self.uso_primario_usm,styNormal2)
            
            reimpiego = Paragraph("<b>REUSE</b><br/>"+self.reimp, styNormal2)

            orientamento = Paragraph("<b>ORIENTATION</b><br/>"+self.orientamento, styNormal)
            
            #8-9 row
            stato_conservazione = Paragraph("<b>PRESERVATION STATE</b><br/>" + self.stato_di_conservazione, styNormal)
            
            
           
            label_laterizi = Paragraph("<b>LATERIZI</b>", styVerticale)
            materiali = Paragraph("<b>MATERIALS</b><br/>", styNormal)
            lavorazione = Paragraph("<b>PROCESSING</b><br/>",  styNormal)
            consistenza = Paragraph("<b>CONSISTENCY</b><br/>", styNormal)
            forma = Paragraph("<b>SHAPE</b><br/>", styNormal)
            colore = Paragraph("<b>COLOR</b><br/>", styNormal)
            impasto = Paragraph("<b>MIXTURE</b><br/>", styNormal)
            posa_opera= Paragraph("<b>INSTALLATION</b><br/>", styNormal)
            
            
            materiali_1 =Paragraph(self.materiali_lat,styNormal)
            lavorazione_1 =Paragraph(self.lavorazione_lat,styNormal)
            consistenza_1 =Paragraph(self.consistenza_lat,styNormal)
            forma_1 =Paragraph(self.forma_lat,styNormal)
            colore_1 =Paragraph(self.colore_lat,styNormal)
            impasto_1 =Paragraph(self.impasto_lat,styNormal)
            posa_opera_1 =Paragraph(self.posa_opera,styNormal)
            #taglio_l = Paragraph(self.taglio_p,styNormal)
            label_pietra = Paragraph("<b>LITHICS ELEMENTS</b>", styVerticale)
            p_1 =Paragraph(self.materiale_p,styNormal)
            p_2 =Paragraph(self.lavorazione,styNormal)
            p_3 =Paragraph(self.consistenza_p,styNormal)
            p_4 =Paragraph(self.forma_p,styNormal)
            p_5 =Paragraph(self.colore_p,styNormal)
            taglio= Paragraph("<b>CUT</b><br/>"+ self.taglio_p, styNormal)
            p_7 =Paragraph(self.posa_opera_p,styNormal)
            
            #12 row
            n=Paragraph('',styNormal)
            
            tipo = Paragraph("<b>TYPE</b><br/>", styNormal)
            consistenza_l = Paragraph("<b>CONSISTENCY</b><br/>",  styNormal)
            colore_l = Paragraph("<b>COLOR</b><br/>", styNormal)
            inerti = Paragraph("<b>INERTI</b><br/>", styNormal)
            spessore = Paragraph("<b>THICKNESS</b><br/>", styNormal)
            rifinitura = Paragraph("<b>REFINEMENT</b><br/>", styNormal)
            
            label_legante= Paragraph("<b>LEGANTE</b>", styVerticale)
            tipo_1 =Paragraph(self.tipo_legante_usm,styNormal)
            consistenza_2 =Paragraph(self.cons_legante,styNormal)
            colore_3 =Paragraph(self.col_legante,styNormal)
            inerti_4 =Paragraph(self.aggreg_legante,styNormal)
            spessore_5 =Paragraph(self.spessore_usm,styNormal)
            rifinitura_6 =Paragraph(self.rifinitura_usm,styNormal)
            
            note_legante = Paragraph("<b>LEGANTE NOTE</b><br/>" , styDescrizione)
            note_materiali = Paragraph("<b>MATERIALS NOTE</b><br/>" , styDescrizione)
            

            #13-22 row

            si_lega_a = Paragraph("<b>CONNECTED TO</b><br/>" + self.si_lega_a, styNormal)
            uguale_a = Paragraph("<b>SAME AS</b><br/>" + self.uguale_a, styNormal)
            copre = Paragraph("<b>COVERS</b><br/>" + self.copre, styNormal)
            coperto_da = Paragraph("<b>COVERED BY</b><br/>" + self.coperto_da, styNormal)
            riempie = Paragraph("<b>FILLS</b><br/>" + self.riempie, styNormal)
            riempito_da = Paragraph("<b>FILLED BY</b><br/>" + self.riempito_da, styNormal)
            taglia = Paragraph("<b>CUTS</b><br/>" + self.taglia, styNormal)
            tagliato_da = Paragraph("<b>CUTTED BY</b><br/>" + self.tagliato_da, styNormal)
            si_appoggia_a = Paragraph("<b>ABUTS</b><br/>" + self.si_appoggia_a, styNormal)
            gli_si_appoggia = Paragraph("<b>SUPPORT</b><br/>" + self.gli_si_appoggia, styNormal)

            label_sequenza_stratigrafica = Paragraph("<b>S<br/>E<br/>Q<br/>U<br/>E<br/>N<br/>C<br/>E<br/><br/>S<br/>T<br/>R<br/>A<br/>T<br/>I<br/>G<br/>R<br/>A<br/>P<br/>H<br/>I<br/>C</b>", styVerticale)

            posteriore_a = Paragraph("<b>BACK TO</b><br/>" + self.copre +"<br/>" + self.riempie +"<br/>"+  self.taglia+ "<br/>" +   self.si_appoggia_a, styNormal)               # manca valore
            anteriore_a = Paragraph("<b>EARLIER TO</b><br/>"+ self.coperto_da +"<br/>"+  self.riempito_da +"<br/>"+ self.tagliato_da +  "<br/>" + self.gli_si_appoggia, styNormal)                 # manca valore

            descrizione = Paragraph("<b>DESCRIPTION</b><br/>" + self.descrizione, styDescrizione)

            osservazioni = Paragraph("<b>NOTE</b><br/>" + self.osservazioni, styDescrizione)

            #24 row

            interpretazione = Paragraph("<b>INTERPRETATION</b><br/>" + self.interpretazione, styDescrizione)

            campioni_malta = Paragraph("<b>MALTA SAMPLE</b><br/>"+ str(self.campioni_malta_usm), styNormal)
            campioni_mattone = Paragraph("<b>LATERIZI SAMPLE</b><br/>"+ str(self.campioni_mattone_usm), styNormal)
            campioni_pietra = Paragraph("<b>LITHICHS SAMLE</b><br/>"+ str(self.campioni_pietra_usm), styNormal)

            elementi_datanti = Paragraph("<b>DATING ELEMENTS</b><br/>" + self.elem_datanti, styDescrizione)

            #26 row

            datazione_ipotesi = Paragraph("<b>DATING</b><br/>" + str(self.datazione), styNormal)
            periodo_o_fase = Paragraph("<b>PERIOD OR PHASE</b><br/>Starting period: "+self.periodo_iniziale+"<br/>Starting phase: "+self.fase_iniziale+"<br/>Final Period: "+self.periodo_finale+"<br/>Final phase: "+self.fase_finale, styNormal)

            affidabilita = Paragraph("<b>STRATIGRAPHIC RELIABILITY</b><br/>" + self.affidabilita, styNormal)
            direttore = Paragraph("<b>SCIENTIFIC HEAD OF INVESTIGATIONS</b><br/>" + self.direttore_us, styNormal)
            responsabile2 = Paragraph("<b>FIELD DIRECTOR</b><br/>" + self.schedatore, styNormal)
            responsabile = Paragraph("<b>RESPONSIBLE FOR REVISION</b><br/>" + self.responsabile_us, styNormal)
            data_rilievo = Paragraph("<b>DATE FIELDWORK</b><br/>" + self.data_rilevazione, styNormal)
            data_rielaborazione = Paragraph("<b>PROCESSING DATE</b><br/>" + self.data_rielaborazione, styNormal)
            attivita = Paragraph("<b>ACTIVITIES</b><br/>" + self.attivita, styNormal)
            licenza =  Paragraph("<b>MIBACT- ICCD_licenza CC BY-SA 4.0_Creative Commons Attribution-ShareAlike 4.0 International</b>",styL)
            # schema

            # schema
            cell_schema = [
                # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
                [unita_tipo, '01' , label_ente_responsabile, '03', '04', '05', '06', '07' , '08', '09', '10', label_unita_stratigrafica, '12', '13', '14', '15', '16', '17'],
                ['00', '01', sop, '03', '04' , '05', '06','07' , '08','09', '10', label_sas, '12', '13', '14', '15', '16', '17'],
                [sito, '01', '02', '03', '04', '05' , '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [area, '01', '02', '03', '04', '05' , '06', '07', '08', '09', '10', saggio, '12', '13', '14', '15', '16', '17'],
                [ambiente, '01', '02', '03', posizione, '04' , '06', settore, '08', quadrato, '10', quote, '12', '13', '14', '15', '16', '17'],
                [piante, '01','02' , '03', prospetti, '05', '06',sezioni, '08', '09', '10', foto, '12', '13', '14', '15', '16', '17'],
                [t_muraria, '01', '02', '03', '04', '05', '06', t_costruttiva, '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [sezione_muraria, '01', '02', '03', '04', '05', '06', modulo, '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [misure, '01', '02', '03', '04', '05', '06', superficie_analizzata, '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [d_stratigrafica, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [criteri_distinzione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                
                
                [provenienza_materiali, '01', '02', '03', '04', '05', '06', orientamento, '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [uso_primario, '01', '02', '03', reimpiego, '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [stato_conservazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                [materiali, '01', '02', lavorazione, '04',  consistenza,'06', '07', forma, '09', colore,'11',  impasto, '13', '14', posa_opera, '16', '17'],
                [label_laterizi,materiali_1, '02', lavorazione_1, '04',  consistenza_1,'06', '07', forma_1, '09', colore_1, '11', impasto_1, '13', '14', posa_opera_1, '16', '17'],
                [label_pietra, p_1, '02', p_2, '04',  p_3,'06', '07', p_4, '09', p_5, '11', taglio, '13', '14', p_7, '16', '17'],
                
                [note_materiali, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                [n, tipo, '02', '03', consistenza_l,'05' , '06',inerti, '08','09' , colore_l, '11', spessore, '13', '14', rifinitura, '16', '17'],
                [label_legante, tipo_1, '02', '03', consistenza_2, '05', '06', inerti_4, '08', '09', colore_3, '11', spessore_5, '13', '14', rifinitura_6, '16', '17'],
                [note_legante, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
				
				[uguale_a, '01', '02', '03', '04', '05', si_lega_a, '07', '08', '09', '10', '11', label_sequenza_stratigrafica, posteriore_a, '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [gli_si_appoggia, '01', '02', '03', '04', '05', si_appoggia_a, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [coperto_da, '01', '02', '03', '04', '05', copre, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', anteriore_a , '14', '15', '16', '17'],
                [tagliato_da, '01', '02', '03', '04', '05', taglia, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [riempito_da, '01', '02', '03', '04', '05', riempie, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
				[descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
				[osservazioni, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [interpretazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                [datazione_ipotesi, '01', '02', '03', '04', '05', periodo_o_fase, '07', '08', '09', '10', '11', attivita, '13', '14', '15', '16', '17'],
                [elementi_datanti, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [campioni_pietra, '01', '02', '03', '04', '05', campioni_mattone, '07', '08', '09', '10', '11', campioni_malta, '13', '14', '15', '16', '17'],
                
                [affidabilita, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [direttore, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [data_rilievo, '01', '02', '03', '04', '05', '06', '07', '08', responsabile, '10', '11', '12', '13', '14', '15', '16', '17'],
                [data_rielaborazione, '01', '02', '03', '04', '05', '06', '07', '08', responsabile2, '10', '11', '12', '13', '14', '15', '16', '17'],
                ]

            # table style
            table_style = [
                ('GRID', (0, 0), (-1, -1), 0.3, colors.black),
                # 0 row
                ('SPAN', (0, 0), (1, 1)),  # unita tipo
                ('VALIGN', (0, 0), (1, 1), 'MIDDLE'),

                ('SPAN', (2, 0), (10, 0)),  # label n. catalogo generale
                ('SPAN', (11, 0), (17, 0)),  # label n. catalogo internazionale
                ('VALIGN', (2, 0), (12,1), 'TOP'),

                # 1 row
                ('SPAN', (2, 1), (10, 1)),  # n. catalogo generale
                ('SPAN', (11, 1), (17, 1)),  # catalogo internazionale
                ('VALIGN', (2, 0), (17, 1), 'TOP'),

                # 2 row
                ('SPAN', (0, 2), (17, 2)),  # sito
                
                ('VALIGN', (0, 2), (17, 2), 'TOP'),

                # 3 row
                ('SPAN', (0, 3), (10, 3)),  # piante
                ('SPAN', (11, 3), (17, 3)),  # sezioni
                ('VALIGN', (0, 3), (17, 3), 'TOP'),

                # 4 row
                ('SPAN', (0, 4), (3, 4)),  # definizione
                ('SPAN', (4, 4), (6, 4)),  # definizione
                ('SPAN', (7, 4), (8, 4)),  # definizione
                ('SPAN', (9, 4), (10, 4)),  # definizione
                ('SPAN', (11, 4), (17, 4)),  # definizione
                ('VALIGN', (0, 4), (17, 4), 'TOP'),

                # 5 row
                ('SPAN', (0, 5), (3, 5)),  # definizione
                ('SPAN', (4,5), (6, 5)),  # definizione
                ('SPAN', (7, 5), (10, 5)),  # definizione
                ('SPAN', (11, 5), (17, 5)),  # definizione
                ('VALIGN', (0, 5), (17, 5), 'TOP'),

                # 5 row
                ('SPAN', (0, 6), (6, 6)),  # definizione
                ('SPAN', (7,6), (17, 6)),  # definizione
                ('VALIGN', (0, 6), (17, 6), 'TOP'),
                
                # 5 row
                ('SPAN', (0, 7), (6, 7)),  # definizione
                ('SPAN', (7,7), (17, 7)),  # definizione
                ('VALIGN', (0, 7), (17, 7), 'TOP'),
                
                # 5 row
                ('SPAN', (0, 8), (6, 8)),  # definizione
                ('SPAN', (7,8), (17, 8)),  # definizione
                ('VALIGN', (0, 8), (17, 8), 'TOP'),
                
                # 6 row
                ('SPAN', (0, 9), (17, 9)),  # modo di formazione
                ('VALIGN', (0, 9), (17, 9), 'TOP'),

                # 7 row
                ('SPAN', (0, 10), (17, 10)),  # label componenti
                ('VALIGN', (0, 10), (17, 10), 'TOP'),

                ('SPAN', (0, 11), (6, 11)),  # label componenti
                ('SPAN', (7, 11), (17, 12)),  # label geologici
                ('SPAN', (0, 12), (3, 12)),  # label organici
                ('SPAN', (4, 12), (6, 12)),  # label artificiali
                ('VALIGN', (0, 11), (17, 12), 'TOP'),
                
                # 7 row
                ('SPAN', (0, 13), (17, 13)),  # label componenti
                ('VALIGN', (0, 13), (17, 13), 'TOP'),
                
                # 10 row
                ('SPAN', (0, 14), (2, 14)),  # label componenti
                ('SPAN', (3, 14), (4, 14)),  # label geologici
                ('SPAN', (5, 14), (7, 14)),  # label organici
                ('SPAN', (8, 14), (9, 14)),  # label artificiali
                ('SPAN', (10, 14), (11, 14)),  #  geologici
                ('SPAN', (12, 14), (14, 14)),  #  organici
                ('SPAN', (15, 14), (17, 14)),  #  artificiali
                ('VALIGN', (0, 14), (17, 14), 'TOP'),

                # 11-12 row
                ('SPAN', (0, 15), (0, 15)),  # label componenti
				('SPAN', (1, 15), (2, 15)),  # label componenti
                ('SPAN', (3, 15), (4, 15)),  # label geologici
                ('SPAN', (5, 15), (7, 15)),  # label organici
                ('SPAN', (8, 15), (9, 15)),  # label artificiali
                ('SPAN', (10, 15), (11, 15)),  #  geologici
                ('SPAN', (12, 15), (14, 15)),  #  organici
                ('SPAN', (15, 15), (17, 15)),  #  artificiali
                ('VALIGN', (0, 15), (17, 15), 'TOP'),

                # 13-14 row
                ('SPAN', (0, 16), (0, 16)),  # label componenti
				('SPAN', (1, 16), (2, 16)),  # label componenti
                ('SPAN', (3, 16), (4, 16)),  # label geologici
                ('SPAN', (5, 16), (7, 16)),  # label organici
                ('SPAN', (8, 16), (9, 16)),  # label artificiali
                ('SPAN', (10, 16), (11, 16)),  #  geologici
                ('SPAN', (12, 16), (14, 16)),  #  organici
                ('SPAN', (15, 16), (17, 16)),  #  artificiali
                ('VALIGN', (0, 16), (17, 16), 'TOP'),
                
                # 17-21 row
                ('SPAN', (0, 17), (17, 17)),  # descrizione
                ('VALIGN', (0, 17), (17, 17), 'TOP'),
                
                # 15 row
                ('SPAN', (0, 18), (0, 18)),  # label componenti
				('SPAN', (1, 18), (3, 18)),  # label componenti
                ('SPAN', (4, 18), (6, 18)),  # label geologici
                ('SPAN', (7, 18), (9, 18)),  # label organici
                ('SPAN', (10, 18), (11, 18)),  # label artificiali
                ('SPAN', (12, 18), (14, 18)),  #  geologici
                ('SPAN', (15, 18), (17, 18)),  #  organici
                ('VALIGN', (0, 18), (17, 18), 'TOP'),
				
				# 16 row
                ('SPAN', (0, 19), (0, 19)),  # label componenti
				('SPAN', (1, 19), (3, 19)),  # label componenti
                ('SPAN', (4, 19), (6, 19)),  # label geologici
                ('SPAN', (7, 19), (9, 19)),  # label organici
                ('SPAN', (10, 19), (11, 19)),  # label artificiali
                ('SPAN', (12, 19), (14, 19)),  #  geologici
                ('SPAN', (15, 19), (17, 19)),  #  organici
                ('VALIGN', (0, 19), (17, 19), 'TOP'),
				
				
				# 17-21 row
                ('SPAN', (0, 20), (17, 20)),  # descrizione
                ('VALIGN', (0, 20), (17, 20), 'TOP'),

                # 22-31 row
                ('SPAN', (0, 21), (5, 22)),    # uguale a
                ('SPAN', (0, 23), (5, 24)),    # gli si appoggia
                ('SPAN', (0, 25), (5, 26)),    # coperto da
                ('SPAN', (0, 27), (5, 28)),    # tagliato da
                ('SPAN', (0, 29), (5, 30)),    # riempito da
                ('SPAN', (6, 21), (11, 22)),   # si lega a
                ('SPAN', (6, 23), (11, 24)),   # si appoggia a
                ('SPAN', (6, 25), (11, 26)),   # copre
                ('SPAN', (6, 27), (11, 28)),   # taglia
                ('SPAN', (6, 29), (11, 30)),   # riempie
                ('SPAN', (12, 21), (12, 30)),  # label sequenza stratigrafica
                ('SPAN', (13, 21), (17, 25)),  # posteriore a
                ('SPAN', (13, 26), (17, 30)),  # uguale a
                ('VALIGN', (0, 21), (17, 30), 'TOP'),



                ('SPAN', (0, 31), (17, 31)),  # descrizione
                ('VALIGN', (0, 31), (17, 31), 'TOP'),
                # 32-34 row
                ('SPAN', (0, 32), (17, 32)),  # osservazioni
                ('VALIGN', (0, 32), (17, 32), 'TOP'),

                # 35-37 row
                ('SPAN', (0, 33), (17, 33)),  # interpretazione
                ('VALIGN', (0, 33), (17, 33), 'TOP'),

                # # 41-42 row
                
                # #29 row
                ('SPAN', (0, 34), (5, 34)),  # affidabilita stratigrafica
                ('SPAN', (6, 34), (11, 34)),  # direttore
                ('SPAN', (12, 34), (17, 34)),  # responsabile
                ('VALIGN', (0, 34), (17, 34), 'TOP'),
                
                
                ('SPAN', (0, 35), (17, 35)),  # elementi datanti
                ('VALIGN', (0, 35), (17, 35), 'TOP'),

                # #35 row
                # #29 row
                ('SPAN', (0, 36), (5, 36)),  # affidabilita stratigrafica
                ('SPAN', (6, 36), (11, 36)),  # direttore
                ('SPAN', (12, 36), (17, 36)),  # responsabile
                ('VALIGN', (0, 36), (17, 36), 'TOP'),
                #29 row
                ('SPAN', (0, 37), (17, 37)),  # affidabilita stratigrafica
                
                ('VALIGN', (0, 37), (17, 37), 'TOP'),

                ('SPAN', (0, 38), (17, 38)),  # affidabilita stratigrafica
                ('VALIGN', (0, 38), (17, 38), 'TOP'),
                
                ('SPAN', (0, 39), (8, 39)),  # affidabilita stratigrafica
                ('SPAN', (9, 39), (17, 39)),  # affidabilita stratigrafica
                ('VALIGN', (0, 39), (17, 39), 'TOP'),
                
                ('SPAN', (0, 40), (8, 40)),  # affidabilita stratigrafica
                ('SPAN', (9, 40), (17, 40)),  # affidabilita stratigrafica
                ('VALIGN', (0, 40), (17, 40), 'TOP'),        

                
            ]

            colWidths = (15,30,30,30,30,30,30,30,30,30,30,30,20,30,30,30,30,30)
            rowHeights = None

            t = Table(cell_schema, colWidths=colWidths, rowHeights=rowHeights, style=table_style)

            return t    
    
    def create_sheet_de(self): #scheda us in stile ICCD Italiano
        self.unzip_rapporti_stratigrafici_de()
        self.unzip_documentazione_de()

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.fontSize = 7
        styNormal.fontName='Cambria'
        styNormal.alignment = 0  # LEFT

        styleSheet = getSampleStyleSheet()
        styNormal2 = styleSheet['Normal']
        styNormal2.spaceBefore = 20
        styNormal2.spaceAfter = 20
        styNormal2.fontSize = 7
        styNormal2.fontName='Cambria'
        styNormal2.alignment = 0  # LEFT
        
        
        styleSheet = getSampleStyleSheet()
        styL = styleSheet['Normal']
        styL.spaceBefore = 20
        styL.spaceAfter = 20
        styL.fontSize = 2
        styL.fontName='Cambria'
        styL.alignment = 1
        
        
        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.fontSize = 7
        styDescrizione.fontName='Cambria'
        styDescrizione.alignment = 4  # Justified

        styleSheet = getSampleStyleSheet()
        styUnitaTipo = styleSheet['Normal']
        styUnitaTipo.spaceBefore = 20
        styUnitaTipo.spaceAfter = 20
        styUnitaTipo.fontSize = 14
        styUnitaTipo.fontName='Cambria'
        styUnitaTipo.alignment = 1  # CENTER

        styleSheet = getSampleStyleSheet()
        styTitoloComponenti = styleSheet['Normal']
        styTitoloComponenti.spaceBefore = 20
        styTitoloComponenti.spaceAfter = 20
        styTitoloComponenti. rowHeights=0.5
        styTitoloComponenti.fontSize = 7
        styTitoloComponenti.fontName='Cambria'
        styTitoloComponenti.alignment = 1  # CENTER

        styleSheet = getSampleStyleSheet()
        styVerticale = styleSheet['Normal']
        styVerticale.spaceBefore = 20
        styVerticale.spaceAfter = 20
        styVerticale.fontSize = 7
        styVerticale.fontName='Cambria'
        styVerticale.alignment = 1  # CENTER
        styVerticale.leading=8

        #format labels

        #0-1 row Unita tipo, logo, n. catalogo generale, n. catalogo internazionale
        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path)

        logo.drawHeight = 2 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 2 * inch
        logo.hAlign = 'CENTER'
        lst = []
        lst2=[]
        lst.append(logo)
        if str(self.unita_tipo)== 'SE':
            unita_tipo = Paragraph(str(self.unita_tipo), styUnitaTipo)
            label_ente_responsabile = Paragraph("<b>CambriaNTWORTLICHE STELLE</b>", styNormal)
            #label_catalogo_internazionale = Paragraph("<b>N° CATALOGO INTERNAZIONALE</b>", styNormal)
            ente_responsabile = Paragraph(str(self.n_catalogo_generale), styNormal)
            #catalogo_internazionale = Paragraph(str(self.n_catalogo_internazionale), styNormal)
            sop =  Paragraph("<b>ZUSTÄNDIGE AUFSICHTSBEHÖRDE FÜR DEN SCHUTZ</b><br/>" +str(self.soprintendenza), styNormal)
            #2-3 row

            sito = Paragraph("<b>LOKALITÄT</b><br/>" + str(self.sito), styNormal)
            #anno_di_scavo = Paragraph("<b>ANNO</b><br/>" + self.anno_scavo, styNormal)
            if self.struttura!='':
            
                area = Paragraph("<b>FLÄCHE/GEBÄUDE/STRUKTUR</b><br/>" + str(self.area)+'/'+str(self.struttura),styNormal)
            
            else:
                area = Paragraph("<b>FLÄCHE/GEBÄUDE/STRUKTUR</b><br/>" + str(self.area),styNormal)
            
            saggio = Paragraph("<b>AUFSATZ</b><br/>" + self.saggio, styNormal)
            ambiente = Paragraph("<b>UMWELT</b><br/>" + self.ambient, styNormal)
            posizione = Paragraph("<b>POSITION IM UMFELD</b><br/>" + self.posizione, styNormal)
            settore = Paragraph("<b>SECTOR</b><br/>" + self.settore, styNormal)
            quadrato = Paragraph("<b>PLATZ</b><br/>" + self.quad_par, styNormal)
            quote = Paragraph("<b>ELEVATION</b><br/>min: " + self.quota_min + "<br/>max: "+self.quota_max, styNormal)
            label_unita_stratigrafica = Paragraph("<b>NUMMER/IDENTIFIKATIONSCODE DER STRATIGRAPHISCHEN EINHEIT</b><br/>"+ str(self.us), styNormal)
            label_sas = Paragraph("<b>NUMMER/IDENTIFIZIERUNGSCODE DES STRATIGRAPHISCHEN AUFSATZES/GEBÄUDES/DER STRUKTUR/DER FUNERÄREN ABLAGERUNG DER REFERENZ</b><br/>", styNormal)
            
            if self.formazione == 'Natürlich':
                label_NAT = Paragraph("<i>NAT.</i><br/>" + self.formazione, styNormal)
                label_ART = Paragraph("<i>KÜN.</i>",  styNormal) 
            elif self.formazione == 'Künstliche':
                label_NAT = Paragraph("<i>NAT.</i>", styNormal)
                label_ART = Paragraph("<i>KÜN.</i><br/>"+ self.formazione, styNormal)
            elif self.formazione !='Natürlich' or 'Künstliche':    
                label_NAT = Paragraph("<i>NAT.</i><br/>", styNormal)
                label_ART = Paragraph("<i>KÜN.</i>",  styNormal) 
            

            piante = Paragraph("<b>PFLAZEN</b><br/>" + self.piante_iccd, styNormal)
            sezioni = Paragraph("<b>SEKTIONEN</b><br/>" + self.sezioni_iccd, styNormal)
            prospetti = Paragraph("<b>PROSPEKTE</b><br/>"+ self.prospetti_iccd, styNormal)                    #manca valore
            foto = Paragraph("<b>FOTO</b><br/>"+ self.foto_iccd, styNormal)            #manca valore

            tabelle_materiali = Paragraph("<b>REFERENZEN MATERIALTABELLEN<br/><br/>RA</b>:"+ self.ref_ra, styNormal)  #manca valore

            #5 row

            d_stratigrafica = Paragraph("<b>DEFINITION UND POSITION</b><br/>Stratigraphische Definition: " + self.d_stratigrafica+"<br/>Interpretierende Definition: "+self.d_interpretativa, styNormal)

            #6 row

            criteri_distinzione = Paragraph("<b>UNTERSCHEIDUNGSKRITERIEN</b><br/>" + self.criteri_distinzione, styNormal)

            #7 row

            modo_formazione = Paragraph("<b>AUSBILDUNGSMODUS</b><br/>" + self.modo_formazione, styNormal)

            #8-9 row


            organici, inorganici= self.unzip_componenti()
            inclusi = ''
            for i in eval(self.inclusi):
                if inclusi == '':
                    try:
                        inclusi += str(i[0])
                    except:
                        pass
                else:
                    try:
                        inclusi += ', ' + str(i[0])
                    except:
                        pass

            label_componenti = Paragraph("<b>KOMPONENTEN</b>",styVerticale)

            label_inorganici = Paragraph("<i>INORGANIK</i>",styTitoloComponenti) #inorganici
            label_organici = Paragraph("<i>ORGANIK</i>", styTitoloComponenti) #organici
            #label_artificiali = Paragraph("<i>INORGANICI</i>", styTitoloComponenti) #inclusi

            comp_organici = Paragraph(organici, styNormal) #organici
            comp_inorganici = Paragraph(inorganici, styNormal)  #geologici
            #inclusi = Paragraph(inclusi, styNormal)  #artificiali

            #10 row

            consistenza = Paragraph("<b>KONSISTENZ</b><br/>" + self.consistenza, styNormal)
            colore = Paragraph("<b>FARBE</b><br/>" + self.colore, styNormal)
            #misure = ''                 # manca valore
            if bool(self.lunghezza_max) and bool(self.larghezza_media) and bool(self.altezza_max):
                misure = Paragraph("<b>MASSNAHMEN</b><br/>" + 'Länge '+ self.lunghezza_max + ' x '+ 'Breite ' + self.larghezza_media + ' x '+ 'Dicke ' + self.altezza_max + 'm', styNormal)
            elif bool(self.lunghezza_max) and bool(self.larghezza_media) and not bool(self.altezza_max):
                misure = Paragraph("<b>MASSNAHMEN</b><br/>" + 'Länge ' + self.lunghezza_max + ' x '+ 'Breite '+ self.larghezza_media + 'm', styNormal)
            
            else:
                misure = Paragraph("<b>MASSNAHMEN</b><br/>", styNormal)



            #11 row

            stato_conservazione = Paragraph("<b>ERHALTUNGSZUSTAND</b><br/>" + self.stato_di_conservazione, styNormal)

            #12 row

            descrizione = Paragraph("<b>BESCHREIBUNG</b><br/>" + self.descrizione, styDescrizione)

            #13-22 row

            si_lega_a = Paragraph("<b>BINDET AN</b><br/>" + self.si_lega_a, styNormal)
            uguale_a = Paragraph("<b>ENTSPRICHT</b><br/>" + self.uguale_a, styNormal)
            copre = Paragraph("<b>LIEGT ÜBER</b><br/>" + self.copre, styNormal)
            coperto_da = Paragraph("<b>LIEGT UNTER</b><br/>" + self.coperto_da, styNormal)
            riempie = Paragraph("<b>VERFÜLLT</b><br/>" + self.riempie, styNormal)
            riempito_da = Paragraph("<b>WIRD VERFÜLLT DURCH</b><br/>" + self.riempito_da, styNormal)
            taglia = Paragraph("<b>SCHNEIDET</b><br/>" + self.taglia, styNormal)
            tagliato_da = Paragraph("<b>WIRD GESCHNITTEN</b><br/>" + self.tagliato_da, styNormal)
            si_appoggia_a = Paragraph("<b>STÜTZT SICH AUF</b><br/>" + self.si_appoggia_a, styNormal)
            gli_si_appoggia = Paragraph("<b>WIRD GESTÜZT VON</b><br/>" + self.gli_si_appoggia, styNormal)

            label_sequenza_stratigrafica = Paragraph("<b>S<br/>T<br/>R<br/>A<br/>T<br/>I<br/>G<br/>R<br/>A<br/>F<br/>I<br/>S<br/>C<br/>H<br/>E<br/><br/> F<br/>O<br/>L<br/>G<br/>E</b>", styVerticale)

            posteriore_a = Paragraph("<b>REAR</b><br/>" + self.copre +"<br/>" + self.riempie +"<br/>"+  self.taglia+ "<br/>" +   self.si_appoggia_a, styNormal)               # manca valore
            anteriore_a = Paragraph("<b>FRONT</b><br/>"+ self.coperto_da +"<br/>"+  self.riempito_da +"<br/>"+ self.tagliato_da +  "<br/>" + self.gli_si_appoggia, styNormal)                 # manca valore

            #23 row

            osservazioni = Paragraph("<b>BEOBACHTUNGEN</b><br/>" + self.osservazioni, styDescrizione)

            #24 row

            interpretazione = Paragraph("<b>INTERPRETATION</b><br/>" + self.interpretazione, styDescrizione)

            #25 row

            elementi_datanti = Paragraph("<b>ELEMENTEN DATEN</b><br/>" + self.elem_datanti, styDescrizione)

            #26 row

            datazione_ipotesi = Paragraph("<b>DATEN</b><br/>" + str(self.datazione), styNormal)
            periodo_o_fase = Paragraph("<b>PERIODE ODER PHASE</b><br/>Anfangszeit: "+self.periodo_iniziale+"<br/>Anfangsphase: "+self.fase_iniziale+"<br/>Letzte Periode: "+self.periodo_finale+"<br/>Endphase: "+self.fase_finale, styNormal)

            #27 row

            dati_quantitativi = Paragraph("<b>QUANTITATIVE DATEN DER BEFUNDE</b><br/>", styNormal)  # manca valore

            #28 row

            campioni_list = eval(self.campioni)
            campioni = ''
            for i in eval(self.campioni):
                if campioni == '':
                    try:
                        campioni += str(i[0])
                    except:
                        pass
                else:
                    try:
                        campioni += ', ' + str(i[0])
                    except:
                        pass
            campioni = Paragraph("<b>BEISPIEL</b><br/>" + campioni, styNormal)
            flottazione = Paragraph("<b>FLOTATION</b><br/>" + self.flottazione, styNormal)
            setacciatura = Paragraph("<b>SEPARATION</b><br/>" + self.setacciatura, styNormal)

            #28 row

            affidabilita = Paragraph("<b>STRATIGRAPHISCHE SICHERHEIT</b><br/>" + self.affidabilita, styNormal)
            direttore = Paragraph("<b>WISSENSCHAFTLICHER LEITER DER UNTERSUCHUNGEN</b><br/>" + self.direttore_us, styNormal)
            responsabile2 = Paragraph("<b>CambriaNTWORTLICH FÜR DIE ZUSAMMENSTELLUNG IM FELD</b><br/>" + self.schedatore, styNormal)
            responsabile = Paragraph("<b>CambriaNTWORTLICH FÜR DIE NACHARBEIT</b><br/>" + self.responsabile_us, styNormal)
            data_rilievo = Paragraph("<b>DATUM FELDARBEIT</b><br/>" + self.data_rilevazione, styNormal)
            data_rielaborazione = Paragraph("<b>ÜBERARBEITUNGSDATUM</b><br/>" + self.data_rielaborazione, styNormal)
            attivita = Paragraph("<b>AKTIVITÄTEN</b><br/>" + self.attivita, styNormal)
            licenza =  Paragraph("<b>MIBACT- ICCD_licenza CC BY-SA 4.0_Creative Commons Attribution-ShareAlike 4.0 International</b>",styL)
            # schema
            cell_schema = [
                
                [unita_tipo, '01' , label_ente_responsabile, '03', '04', '05', '06', '07' , '08', '09', '10', label_unita_stratigrafica, '12', '13', '14', '15', '16', '17'],
                ['00', '01', sop, '03', '04' , '05', '06','07' , '08','09', '10', label_sas, '12', '13', '14', '15', '16', '17'],
                [sito, '01', '02', '03', '04', '05' , '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [area, '01', '02', '03', '04', '05' , '06', '07', '08', '09', '10', saggio, '12', '13', '14', '15', '16', '17'],
                [ambiente, '01', '02', '03', posizione, '04' , '06', settore, '08', quadrato, '10', quote, '12', '13', label_NAT, '15', label_ART, '17'],
                [piante, '01', prospetti, '03', sezioni, '05', '06',foto, '08', '09', '10', tabelle_materiali, '12', '13', '14', '15', '16', '17'],
                [d_stratigrafica, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [criteri_distinzione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [modo_formazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [ label_organici, '01','02', '03', '04', '05', '06', '07', '08', label_inorganici, '10', '11','12' , '13', '14', '15', '16', '17'],
                [label_componenti, comp_organici, '02', '03', '04', '05', '06', '07', '08', comp_inorganici, '10', '11', '12', '13', '14', '15', '16', '17'],
                [consistenza, '01', '02', '03', '04', '05', colore, '07', '08', '09', '10', '11', misure, '13', '14', '15', '16', '17'],
                [stato_conservazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                [uguale_a, '01', '02', '03', '04', '05', si_lega_a, '07', '08', '09', '10', '11', label_sequenza_stratigrafica, posteriore_a, '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [gli_si_appoggia, '01', '02', '03', '04', '05', si_appoggia_a, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [coperto_da, '01', '02', '03', '04', '05', copre, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', anteriore_a , '14', '15', '16', '17'],
                [tagliato_da, '01', '02', '03', '04', '05', taglia, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [riempito_da, '01', '02', '03', '04', '05', riempie, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [osservazioni, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [interpretazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                [datazione_ipotesi, '01', '02', '03', '04', '05', periodo_o_fase, '07', '08', '09', '10', '11', attivita, '13', '14', '15', '16', '17'],
                [elementi_datanti, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [dati_quantitativi, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [campioni, '01', '02', '03', '04', '05', flottazione, '07', '08', '09', '10', '11', setacciatura, '13', '14', '15', '16', '17'],
                [affidabilita, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [direttore, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [data_rilievo, '01', '02', '03', '04', '05', '06', '07', '08', responsabile, '10', '11', '12', '13', '14', '15', '16', '17'],
                [data_rielaborazione, '01', '02', '03', '04', '05', '06', '07', '08', responsabile2, '10', '11', '12', '13', '14', '15', '16', '17'],
                ]

            # table style
            table_style = [
               
                ('GRID', (0, 0), (-1, -1), 0.3, colors.black),
                # 0 row
                ('SPAN', (0, 0), (1, 1)),  # unita tipo
                ('VALIGN', (0, 0), (1, 1), 'MIDDLE'),

                ('SPAN', (2, 0), (10, 0)),  # label n. catalogo generale
                ('SPAN', (11, 0), (17, 0)),  # label n. catalogo internazionale
                ('VALIGN', (2, 0), (12,1), 'TOP'),

                # 1 row
                ('SPAN', (2, 1), (10, 1)),  # n. catalogo generale
                ('SPAN', (11, 1), (17, 1)),  # catalogo internazionale
                ('VALIGN', (2, 0), (17, 1), 'TOP'),

                # 2 row
                ('SPAN', (0, 2), (17, 2)),  # sito
                
                ('VALIGN', (0, 2), (17, 2), 'TOP'),

                # 3 row
                ('SPAN', (0, 3), (10, 3)),  # piante
                ('SPAN', (11, 3), (17, 3)),  # sezioni
                ('VALIGN', (0, 3), (17, 3), 'TOP'),

                # 4 row
                ('SPAN', (0, 4), (3, 4)),  # definizione
                ('SPAN', (4, 4), (6, 4)),  # definizione
                ('SPAN', (7, 4), (8, 4)),  # definizione
                ('SPAN', (9, 4), (10, 4)),  # definizione
                ('SPAN', (11, 4), (13, 4)),  # definizione
                ('SPAN', (14, 4), (15, 4)),  # definizione
                ('SPAN', (16, 4), (17, 4)),  # definizione        
                ('VALIGN', (0, 4), (17, 4), 'TOP'),

                # 5 row
                ('SPAN', (0, 5), (1, 5)),  # definizione
                ('SPAN', (2,5), (3, 5)),  # definizione
                ('SPAN', (4, 5), (6, 5)),  # definizione
                ('SPAN', (7, 5), (10, 5)),  # definizione
                ('SPAN', (11, 5), (17, 5)),  # definizione
                ('VALIGN', (0, 5), (17, 5), 'TOP'),

                # 6 row
                ('SPAN', (0, 6), (17, 6)),  # modo di formazione
                ('VALIGN', (0, 6), (17, 6), 'TOP'),

                # 7 row
                ('SPAN', (0, 7), (17, 7)),  # label componenti
                ('VALIGN', (0, 7), (17, 7), 'TOP'),

                # 8 row
                ('SPAN', (0, 8), (17, 8)),  # consistenza
                ('VALIGN', (0, 8), (17, 8), 'TOP'),
                
                # 9-10 row
                
                ('SPAN', (0, 9), (8, 9)),  # consistenza
                ('SPAN', (9, 9), (17, 9)),  # consistenza
                ('SPAN', (0, 10), (0, 10)),  # consistenza
                ('SPAN', (1, 10), (8, 10)),  # consistenza
                ('SPAN', (9, 10), (17, 10)),  # consistenza
                ('VALIGN', (0, 9), (17, 10), 'TOP'),
                
                
                
                
                # 11 row
                ('SPAN', (0, 11), (5, 11)),  # stato di conservazione
                ('SPAN', (6, 11), (11, 11)),  # stato di conservazione
                ('SPAN', (12, 11), (17, 11)),  # stato di conservazione
                ('VALIGN', (0, 11), (17, 11), 'TOP'),

                # 12 row
                ('SPAN', (0, 12), (17, 12)),  # descrizione
                ('VALIGN', (0, 12), (17, 12), 'TOP'),

                # 13-22 row
                ('SPAN', (0, 13), (5, 14)),    # uguale a
                ('SPAN', (0, 15), (5, 16)),    # gli si appoggia
                ('SPAN', (0, 17), (5, 18)),    # coperto da
                ('SPAN', (0, 19), (5, 20)),    # tagliato da
                ('SPAN', (0, 21), (5, 22)),    # riempito da
                ('SPAN', (6, 13), (11, 14)),   # si lega a
                ('SPAN', (6, 15), (11, 16)),   # si appoggia a
                ('SPAN', (6, 17), (11, 18)),   # copre
                ('SPAN', (6, 19), (11, 20)),   # taglia
                ('SPAN', (6, 21), (11, 22)),   # riempie
                ('SPAN', (12, 13), (12, 22)),  # label sequenza stratigrafica
                ('SPAN', (13, 13), (17, 17)),  # posteriore a
                ('SPAN', (13, 18), (17, 22)),  # uguale a
                ('VALIGN', (0, 13), (17, 22), 'TOP'),

                # 23 row
                ('SPAN', (0, 23), (17, 23)),  # DESCRIZIONE
                ('VALIGN', (0, 23), (17, 23), 'TOP'),

                # 24 row
                ('SPAN', (0, 24), (17, 24)),  # OSSERVAZIONI
                ('VALIGN', (0, 24), (17, 24), 'TOP'),

                # 25 row

                ('SPAN', (0, 25), (17, 25)),  # INTERPRETAZIONI
                ('VALIGN', (0, 25), (17, 25), 'TOP'),

                #26 row

                ('SPAN', (0, 26), (5, 26)),  # datazione
                ('SPAN', (6, 26), (11, 26)),  # periodo o fase
                ('SPAN', (12, 26), (17, 26)),  # ATTIVITA
                ('VALIGN', (0, 26), (17, 26), 'TOP'),

                # #27 row

                ('SPAN', (0, 27), (17, 27)),  # elementi datanti
                ('VALIGN', (0, 27), (17, 27), 'TOP'),

                ('SPAN', (0, 28), (17, 28)),  # elementi datanti
                ('VALIGN', (0, 28), (17, 28), 'TOP'),
                
                #28 row
                ('SPAN', (0, 29), (5, 29)),  # campionature
                ('SPAN', (6, 29), (11, 29)),  # flottazione
                ('SPAN', (12, 29), (17, 29)),  # setacciatura
                ('VALIGN', (0, 29), (17, 29), 'TOP'),

                #29 row
                ('SPAN', (0, 30), (17, 30)),  # affidabilita stratigrafica
                
                ('VALIGN', (0, 30), (17, 30), 'TOP'),

                ('SPAN', (0, 31), (17, 31)),  # affidabilita stratigrafica
                ('VALIGN', (0, 31), (17, 31), 'TOP'),
                
                ('SPAN', (0, 32), (8, 32)),  # affidabilita stratigrafica
                ('SPAN', (9, 32), (17, 32)),  # affidabilita stratigrafica
                ('VALIGN', (0, 32), (17, 32), 'TOP'),
                
                ('SPAN', (0, 33), (8, 33)),  # affidabilita stratigrafica
                ('SPAN', (9, 33), (17, 33)),  # affidabilita stratigrafica
                ('VALIGN', (0, 33), (17, 33), 'TOP'),               
            ]

            colWidths = (15,30,30,30,30,30,30,30,30,30,30,30,20,30,30,30,30,30)
            rowHeights = None
            
            t = Table(cell_schema, colWidths=colWidths, rowHeights=rowHeights, style=table_style)
            lst.append(logo)
            
            return t
        elif str(self.unita_tipo)=='MSE':
            unita_tipo = Paragraph(str(self.unita_tipo), styUnitaTipo)
            label_ente_responsabile = Paragraph("<b>CambriaNTWORTLICHE STELLE</b>", styNormal)
            #label_catalogo_internazionale = Paragraph("<b>N° CATALOGO INTERNAZIONALE</b>", styNormal)
            ente_responsabile = Paragraph(str(self.n_catalogo_generale), styNormal)
            #catalogo_internazionale = Paragraph(str(self.n_catalogo_internazionale), styNormal)
            sop =  Paragraph("<b>ZUSTÄNDIGE AUFSICHTSBEHÖRDE FÜR DEN SCHUTZ</b><br/>" +str(self.soprintendenza), styNormal)
            #2-3 row

            sito = Paragraph("<b>LOKALITÄT</b><br/>" + str(self.sito), styNormal)
            #anno_di_scavo = Paragraph("<b>ANNO</b><br/>" + self.anno_scavo, styNormal)
            if self.struttura!='':
            
                area = Paragraph("<b>FLÄCHE/GEBÄUDE/STRUKTUR</b><br/>" + str(self.area)+'/'+str(self.struttura),styNormal)
            
            else:
                area = Paragraph("<b>FLÄCHE/GEBÄUDE/STRUKTUR</b><br/>" + str(self.area),styNormal)
            
            saggio = Paragraph("<b>AUFSATZ</b><br/>" + self.saggio, styNormal)
            ambiente = Paragraph("<b>UMWELT</b><br/>" + self.ambient, styNormal)
            posizione = Paragraph("<b>POSITION IM UMFELD</b><br/>" + self.posizione, styNormal)
            settore = Paragraph("<b>SECTOR</b><br/>" + self.settore, styNormal)
            quadrato = Paragraph("<b>PLATZ</b><br/>" + self.quad_par, styNormal)
            quote = Paragraph("<b>ELEVATION</b><br/>min: " + self.quota_min + "<br/>max: "+self.quota_max, styNormal)
            label_unita_stratigrafica = Paragraph("<b>NUMMER/IDENTIFIKATIONSCODE DER STRATIGRAPHISCHEN EINHEIT</b><br/>"+ str(self.us), styNormal)
            label_sas = Paragraph("<b>NUMMER/IDENTIFIZIERUNGSCODE DES STRATIGRAPHISCHEN AUFSATZES/GEBÄUDES/DER STRUKTUR/DER FUNERÄREN ABLAGERUNG DER REFERENZ</b><br/>", styNormal)
            
           

            piante = Paragraph("<b>PFLAZEN</b><br/>" + self.piante_iccd, styNormal)
            sezioni = Paragraph("<b>SEKTIONEN</b><br/>" + self.sezioni_iccd, styNormal)
            prospetti = Paragraph("<b>PROSPEKTE</b><br/>"+ self.prospetti_iccd, styNormal)                    #manca valore
            foto = Paragraph("<b>FOTO</b><br/>"+ self.foto_iccd, styNormal)            #manca valore

           

            t_muraria = Paragraph("<b>TYPOLOGIE DER ARBEIT</b><br/>"+ str(self.tipologia_opera), styNormal)
            t_costruttiva = Paragraph("<b>KONSTRUKTIONSTECHNIK</b><br/>"+ str(self.tecnica_muraria_usm), styNormal)
            sezione_muraria = Paragraph("<b>MAUERWERKSABSCHNITT</b><br/>"+ str(self.sezione_muraria), styNormal)
            
            modulo = Paragraph("<b>MODUL</b><br/>"+ str(self.modulo_usm), styNormal)
            
            
            if bool(self.lunghezza_usm) and bool(self.altezza_usm):
                misure = Paragraph("<b>MASSNAHMEN</b><br/>" + 'Länge '+ self.lunghezza_usm + ' x '+ 'Breite ' + self.altezza_usm + 'm', styNormal)
            elif bool(self.lunghezza_usm) and  not bool(self.altezza_usm):
                misure = Paragraph("<b>MASSNAHMEN</b><br/>" + 'Länge ' + self.lunghezza_usm + 'm', styNormal)
            elif bool(self.altezza_usm) and  not bool(self.lunghezza_usm):
                misure = Paragraph("<b>MASSNAHMEN</b><br/>" + 'Breite ' + self.altezza_usm + 'm', styNormal)
            else:
                misure = Paragraph("<b>MASSNAHMEN</b><br/>", styNormal)

            superficie_analizzata = Paragraph("<b>ANALYSIERTE OBERFLÄCHE</b><br/>"+ str(self.superficie_analizzata), styNormal)
            
            d_stratigrafica = Paragraph("<b>DEFINITION UND POSITION</b><br/>" + self.d_stratigrafica+"<br/>"+self.d_interpretativa, styNormal)
            

            #6 row

            criteri_distinzione = Paragraph("<b>UNTERSCHEIDUNGSKRITERIEN</b><br/>" + self.criteri_distinzione, styNormal)

            #7 row

            provenienza_materiali = Paragraph("<b>HERKUNFT DER MATERIALIEN</b><br/>"+self.provenienza_materiali_usm,styNormal2)
            
            uso_primario = Paragraph("<b>PRIMÄRER GEBRAUCH</b><br/>" + self.uso_primario_usm,styNormal2)
            
            reimpiego = Paragraph("<b>WIEDERVERWENDEN</b><br/>"+self.reimp, styNormal2)

            orientamento = Paragraph("<b>ORIENTIERUNG</b><br/>"+self.orientamento, styNormal)
            
            #8-9 row
            stato_conservazione = Paragraph("<b>ERHALTUNGSZUSTAND</b><br/>" + self.stato_di_conservazione, styNormal)

            
           
            label_laterizi = Paragraph("<b>LATERIZI</b>", styVerticale)
            materiali = Paragraph("<b>MATERIALIEN</b><br/>", styNormal)
            lavorazione = Paragraph("<b>CambriaRBEITUNG</b><br/>",  styNormal)
            consistenza = Paragraph("<b>KONSISTENZ</b><br/>", styNormal)
            forma = Paragraph("<b>FORM</b><br/>", styNormal)
            colore = Paragraph("<b>FARBE</b><br/>", styNormal)
            impasto = Paragraph("<b>PAST</b><br/>", styNormal)
            posa_opera= Paragraph("<b>INSTALLIERUNG</b><br/>", styNormal)
            
            
            materiali_1 =Paragraph(self.materiali_lat,styNormal)
            lavorazione_1 =Paragraph(self.lavorazione_lat,styNormal)
            consistenza_1 =Paragraph(self.consistenza_lat,styNormal)
            forma_1 =Paragraph(self.forma_lat,styNormal)
            colore_1 =Paragraph(self.colore_lat,styNormal)
            impasto_1 =Paragraph(self.impasto_lat,styNormal)
            posa_opera_1 =Paragraph(self.posa_opera,styNormal)
            #taglio_l = Paragraph(self.taglio_p,styNormal)
            label_pietra = Paragraph("<b>LITHIK</b>", styVerticale)
            p_1 =Paragraph(self.materiale_p,styNormal)
            p_2 =Paragraph(self.lavorazione,styNormal)
            p_3 =Paragraph(self.consistenza_p,styNormal)
            p_4 =Paragraph(self.forma_p,styNormal)
            p_5 =Paragraph(self.colore_p,styNormal)
            taglio= Paragraph("<b>SCHNITT</b><br/>"+ self.taglio_p, styNormal)
            p_7 =Paragraph(self.posa_opera_p,styNormal)
            
            #12 row
            n=Paragraph('',styNormal)
            
            tipo = Paragraph("<b>TYP</b><br/>", styNormal)
            consistenza_l = Paragraph("<b>CKONSISTENZ</b><br/>",  styNormal)
            colore_l = Paragraph("<b>FARBE</b><br/>", styNormal)
            inerti = Paragraph("<b>INERTS</b><br/>", styNormal)
            spessore = Paragraph("<b>DICHTE</b><br/>", styNormal)
            rifinitura = Paragraph("<b>ENDE</b><br/>", styNormal)
            
            label_legante= Paragraph("<b>HINWEISE</b>", styVerticale)
            tipo_1 =Paragraph(self.tipo_legante_usm,styNormal)
            consistenza_2 =Paragraph(self.cons_legante,styNormal)
            colore_3 =Paragraph(self.col_legante,styNormal)
            inerti_4 =Paragraph(self.aggreg_legante,styNormal)
            spessore_5 =Paragraph(self.spessore_usm,styNormal)
            rifinitura_6 =Paragraph(self.rifinitura_usm,styNormal)
            
            note_legante = Paragraph("<b>BINDERSPEZIFISCHE HINWEISE</b><br/>" , styDescrizione)
            note_materiali = Paragraph("<b>BESONDERE HINWEISE ZU WERKSTOFFEN</b><br/>" , styDescrizione)
            

            #13-22 row

            si_lega_a = Paragraph("<b>BINDET AN</b><br/>" + self.si_lega_a, styNormal)
            uguale_a = Paragraph("<b>ENTSPRICHT</b><br/>" + self.uguale_a, styNormal)
            copre = Paragraph("<b>LIEGT ÜBER</b><br/>" + self.copre, styNormal)
            coperto_da = Paragraph("<b>LIEGT UNTER</b><br/>" + self.coperto_da, styNormal)
            riempie = Paragraph("<b>VERFÜLLT</b><br/>" + self.riempie, styNormal)
            riempito_da = Paragraph("<b>WIRD VERFÜLLT DURCH</b><br/>" + self.riempito_da, styNormal)
            taglia = Paragraph("<b>SCHNEIDET</b><br/>" + self.taglia, styNormal)
            tagliato_da = Paragraph("<b>WIRD GESCHNITTEN</b><br/>" + self.tagliato_da, styNormal)
            si_appoggia_a = Paragraph("<b>STÜTZT SICH AUF</b><br/>" + self.si_appoggia_a, styNormal)
            gli_si_appoggia = Paragraph("<b>WIRD GESTÜZT VON</b><br/>" + self.gli_si_appoggia, styNormal)

            label_sequenza_stratigrafica = Paragraph("<b>S<br/>T<br/>R<br/>A<br/>T<br/>I<br/>G<br/>R<br/>A<br/>F<br/>I<br/>S<br/>C<br/>H<br/>E<br/><br/> F<br/>O<br/>L<br/>G<br/>E</b>", styVerticale)

            posteriore_a = Paragraph("<b>REAR</b><br/>" + self.copre +"<br/>" + self.riempie +"<br/>"+  self.taglia+ "<br/>" +   self.si_appoggia_a, styNormal)               # manca valore
            anteriore_a = Paragraph("<b>FRONT</b><br/>"+ self.coperto_da +"<br/>"+  self.riempito_da +"<br/>"+ self.tagliato_da +  "<br/>" + self.gli_si_appoggia, styNormal)                 # manca valore

            descrizione = Paragraph("<b>DESCRIPTION</b><br/>" + self.descrizione, styDescrizione)

            osservazioni = Paragraph("<b>BEOBACHTUNGEN</b><br/>" + self.osservazioni, styDescrizione)

            #24 row

            interpretazione = Paragraph("<b>INTERPRETATION</b><br/>" + self.interpretazione, styDescrizione)

            campioni_malta = Paragraph("<b>MEISTER MALTA</b><br/>"+ str(self.campioni_malta_usm), styNormal)
            campioni_mattone = Paragraph("<b>MEISTER LATERIZI</b><br/>"+ str(self.campioni_mattone_usm), styNormal)
            campioni_pietra = Paragraph("<b>MEISTER LITHIK</b><br/>"+ str(self.campioni_pietra_usm), styNormal)

            elementi_datanti = Paragraph("<b>ELEMENTEN DATEN</b><br/>" + self.elem_datanti, styDescrizione)

            #26 row

            datazione_ipotesi = Paragraph("<b>DATEN</b><br/>" + str(self.datazione), styNormal)
            periodo_o_fase = Paragraph("<b>PERIODE ODER PHASE</b><br/>Anfangszeit: "+self.periodo_iniziale+"<br/>Anfangsphase: "+self.fase_iniziale+"<br/>Letzte Periode: "+self.periodo_finale+"<br/>Endphase: "+self.fase_finale, styNormal)

            affidabilita = Paragraph("<b>STRATIGRAPHISCHE SICHERHEIT</b><br/>" + self.affidabilita, styNormal)
            direttore = Paragraph("<b>WISSENSCHAFTLICHER LEITER DER UNTERSUCHUNGEN</b><br/>" + self.direttore_us, styNormal)
            responsabile2 = Paragraph("<b>CambriaNTWORTLICH FÜR DIE ZUSAMMENSTELLUNG IM FELD</b><br/>" + self.schedatore, styNormal)
            responsabile = Paragraph("<b>CambriaNTWORTLICH FÜR DIE NACHARBEIT</b><br/>" + self.responsabile_us, styNormal)
            data_rilievo = Paragraph("<b>DATUM FELDARBEIT</b><br/>" + self.data_rilevazione, styNormal)
            data_rielaborazione = Paragraph("<b>ÜBERARBEITUNGSDATUM</b><br/>" + self.data_rielaborazione, styNormal)
            attivita = Paragraph("<b>AKTIVITÄTEN</b><br/>" + self.attivita, styNormal)
            licenza =  Paragraph("<b>MIBACT- ICCD_licenza CC BY-SA 4.0_Creative Commons Attribution-ShareAlike 4.0 International</b>",styL)
            # schema

            # schema
            cell_schema = [
                # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
                [unita_tipo, '01' , label_ente_responsabile, '03', '04', '05', '06', '07' , '08', '09', '10', label_unita_stratigrafica, '12', '13', '14', '15', '16', '17'],
                ['00', '01', sop, '03', '04' , '05', '06','07' , '08','09', '10', label_sas, '12', '13', '14', '15', '16', '17'],
                [sito, '01', '02', '03', '04', '05' , '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [area, '01', '02', '03', '04', '05' , '06', '07', '08', '09', '10', saggio, '12', '13', '14', '15', '16', '17'],
                [ambiente, '01', '02', '03', posizione, '04' , '06', settore, '08', quadrato, '10', quote, '12', '13', '14', '15', '16', '17'],
                [piante, '01','02' , '03', prospetti, '05', '06',sezioni, '08', '09', '10', foto, '12', '13', '14', '15', '16', '17'],
                [t_muraria, '01', '02', '03', '04', '05', '06', t_costruttiva, '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [sezione_muraria, '01', '02', '03', '04', '05', '06', modulo, '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [misure, '01', '02', '03', '04', '05', '06', superficie_analizzata, '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [d_stratigrafica, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [criteri_distinzione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                
                
                [provenienza_materiali, '01', '02', '03', '04', '05', '06', orientamento, '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [uso_primario, '01', '02', '03', reimpiego, '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [stato_conservazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                [materiali, '01', '02', lavorazione, '04',  consistenza,'06', '07', forma, '09', colore,'11',  impasto, '13', '14', posa_opera, '16', '17'],
                [label_laterizi,materiali_1, '02', lavorazione_1, '04',  consistenza_1,'06', '07', forma_1, '09', colore_1, '11', impasto_1, '13', '14', posa_opera_1, '16', '17'],
                [label_pietra, p_1, '02', p_2, '04',  p_3,'06', '07', p_4, '09', p_5, '11', taglio, '13', '14', p_7, '16', '17'],
                
                [note_materiali, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                [n, tipo, '02', '03', consistenza_l,'05' , '06',inerti, '08','09' , colore_l, '11', spessore, '13', '14', rifinitura, '16', '17'],
                [label_legante, tipo_1, '02', '03', consistenza_2, '05', '06', inerti_4, '08', '09', colore_3, '11', spessore_5, '13', '14', rifinitura_6, '16', '17'],
                [note_legante, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
				
				[uguale_a, '01', '02', '03', '04', '05', si_lega_a, '07', '08', '09', '10', '11', label_sequenza_stratigrafica, posteriore_a, '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [gli_si_appoggia, '01', '02', '03', '04', '05', si_appoggia_a, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [coperto_da, '01', '02', '03', '04', '05', copre, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', anteriore_a , '14', '15', '16', '17'],
                [tagliato_da, '01', '02', '03', '04', '05', taglia, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [riempito_da, '01', '02', '03', '04', '05', riempie, '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
				[descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
				[osservazioni, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [interpretazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                
                [datazione_ipotesi, '01', '02', '03', '04', '05', periodo_o_fase, '07', '08', '09', '10', '11', attivita, '13', '14', '15', '16', '17'],
                [elementi_datanti, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [campioni_pietra, '01', '02', '03', '04', '05', campioni_mattone, '07', '08', '09', '10', '11', campioni_malta, '13', '14', '15', '16', '17'],
                
                [affidabilita, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [direttore, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
                [data_rilievo, '01', '02', '03', '04', '05', '06', '07', '08', responsabile, '10', '11', '12', '13', '14', '15', '16', '17'],
                [data_rielaborazione, '01', '02', '03', '04', '05', '06', '07', '08', responsabile2, '10', '11', '12', '13', '14', '15', '16', '17'],
                ]

            # table style
            table_style = [
                ('GRID', (0, 0), (-1, -1), 0.3, colors.black),
                # 0 row
                ('SPAN', (0, 0), (1, 1)),  # unita tipo
                ('VALIGN', (0, 0), (1, 1), 'MIDDLE'),

                ('SPAN', (2, 0), (10, 0)),  # label n. catalogo generale
                ('SPAN', (11, 0), (17, 0)),  # label n. catalogo internazionale
                ('VALIGN', (2, 0), (12,1), 'TOP'),

                # 1 row
                ('SPAN', (2, 1), (10, 1)),  # n. catalogo generale
                ('SPAN', (11, 1), (17, 1)),  # catalogo internazionale
                ('VALIGN', (2, 0), (17, 1), 'TOP'),

                # 2 row
                ('SPAN', (0, 2), (17, 2)),  # sito
                
                ('VALIGN', (0, 2), (17, 2), 'TOP'),

                # 3 row
                ('SPAN', (0, 3), (10, 3)),  # piante
                ('SPAN', (11, 3), (17, 3)),  # sezioni
                ('VALIGN', (0, 3), (17, 3), 'TOP'),

                # 4 row
                ('SPAN', (0, 4), (3, 4)),  # definizione
                ('SPAN', (4, 4), (6, 4)),  # definizione
                ('SPAN', (7, 4), (8, 4)),  # definizione
                ('SPAN', (9, 4), (10, 4)),  # definizione
                ('SPAN', (11, 4), (17, 4)),  # definizione
                ('VALIGN', (0, 4), (17, 4), 'TOP'),

                # 5 row
                ('SPAN', (0, 5), (3, 5)),  # definizione
                ('SPAN', (4,5), (6, 5)),  # definizione
                ('SPAN', (7, 5), (10, 5)),  # definizione
                ('SPAN', (11, 5), (17, 5)),  # definizione
                ('VALIGN', (0, 5), (17, 5), 'TOP'),

                # 5 row
                ('SPAN', (0, 6), (6, 6)),  # definizione
                ('SPAN', (7,6), (17, 6)),  # definizione
                ('VALIGN', (0, 6), (17, 6), 'TOP'),
                
                # 5 row
                ('SPAN', (0, 7), (6, 7)),  # definizione
                ('SPAN', (7,7), (17, 7)),  # definizione
                ('VALIGN', (0, 7), (17, 7), 'TOP'),
                
                # 5 row
                ('SPAN', (0, 8), (6, 8)),  # definizione
                ('SPAN', (7,8), (17, 8)),  # definizione
                ('VALIGN', (0, 8), (17, 8), 'TOP'),
                
                # 6 row
                ('SPAN', (0, 9), (17, 9)),  # modo di formazione
                ('VALIGN', (0, 9), (17, 9), 'TOP'),

                # 7 row
                ('SPAN', (0, 10), (17, 10)),  # label componenti
                ('VALIGN', (0, 10), (17, 10), 'TOP'),

                ('SPAN', (0, 11), (6, 11)),  # label componenti
                ('SPAN', (7, 11), (17, 12)),  # label geologici
                ('SPAN', (0, 12), (3, 12)),  # label organici
                ('SPAN', (4, 12), (6, 12)),  # label artificiali
                ('VALIGN', (0, 11), (17, 12), 'TOP'),
                
                # 7 row
                ('SPAN', (0, 13), (17, 13)),  # label componenti
                ('VALIGN', (0, 13), (17, 13), 'TOP'),
                
                # 10 row
                ('SPAN', (0, 14), (2, 14)),  # label componenti
                ('SPAN', (3, 14), (4, 14)),  # label geologici
                ('SPAN', (5, 14), (7, 14)),  # label organici
                ('SPAN', (8, 14), (9, 14)),  # label artificiali
                ('SPAN', (10, 14), (11, 14)),  #  geologici
                ('SPAN', (12, 14), (14, 14)),  #  organici
                ('SPAN', (15, 14), (17, 14)),  #  artificiali
                ('VALIGN', (0, 14), (17, 14), 'TOP'),

                # 11-12 row
                ('SPAN', (0, 15), (0, 15)),  # label componenti
				('SPAN', (1, 15), (2, 15)),  # label componenti
                ('SPAN', (3, 15), (4, 15)),  # label geologici
                ('SPAN', (5, 15), (7, 15)),  # label organici
                ('SPAN', (8, 15), (9, 15)),  # label artificiali
                ('SPAN', (10, 15), (11, 15)),  #  geologici
                ('SPAN', (12, 15), (14, 15)),  #  organici
                ('SPAN', (15, 15), (17, 15)),  #  artificiali
                ('VALIGN', (0, 15), (17, 15), 'TOP'),

                # 13-14 row
                ('SPAN', (0, 16), (0, 16)),  # label componenti
				('SPAN', (1, 16), (2, 16)),  # label componenti
                ('SPAN', (3, 16), (4, 16)),  # label geologici
                ('SPAN', (5, 16), (7, 16)),  # label organici
                ('SPAN', (8, 16), (9, 16)),  # label artificiali
                ('SPAN', (10, 16), (11, 16)),  #  geologici
                ('SPAN', (12, 16), (14, 16)),  #  organici
                ('SPAN', (15, 16), (17, 16)),  #  artificiali
                ('VALIGN', (0, 16), (17, 16), 'TOP'),
                
                # 17-21 row
                ('SPAN', (0, 17), (17, 17)),  # descrizione
                ('VALIGN', (0, 17), (17, 17), 'TOP'),
                
                # 15 row
                ('SPAN', (0, 18), (0, 18)),  # label componenti
				('SPAN', (1, 18), (3, 18)),  # label componenti
                ('SPAN', (4, 18), (6, 18)),  # label geologici
                ('SPAN', (7, 18), (9, 18)),  # label organici
                ('SPAN', (10, 18), (11, 18)),  # label artificiali
                ('SPAN', (12, 18), (14, 18)),  #  geologici
                ('SPAN', (15, 18), (17, 18)),  #  organici
                ('VALIGN', (0, 18), (17, 18), 'TOP'),
				
				# 16 row
                ('SPAN', (0, 19), (0, 19)),  # label componenti
				('SPAN', (1, 19), (3, 19)),  # label componenti
                ('SPAN', (4, 19), (6, 19)),  # label geologici
                ('SPAN', (7, 19), (9, 19)),  # label organici
                ('SPAN', (10, 19), (11, 19)),  # label artificiali
                ('SPAN', (12, 19), (14, 19)),  #  geologici
                ('SPAN', (15, 19), (17, 19)),  #  organici
                ('VALIGN', (0, 19), (17, 19), 'TOP'),
				
				
				# 17-21 row
                ('SPAN', (0, 20), (17, 20)),  # descrizione
                ('VALIGN', (0, 20), (17, 20), 'TOP'),

                # 22-31 row
                ('SPAN', (0, 21), (5, 22)),    # uguale a
                ('SPAN', (0, 23), (5, 24)),    # gli si appoggia
                ('SPAN', (0, 25), (5, 26)),    # coperto da
                ('SPAN', (0, 27), (5, 28)),    # tagliato da
                ('SPAN', (0, 29), (5, 30)),    # riempito da
                ('SPAN', (6, 21), (11, 22)),   # si lega a
                ('SPAN', (6, 23), (11, 24)),   # si appoggia a
                ('SPAN', (6, 25), (11, 26)),   # copre
                ('SPAN', (6, 27), (11, 28)),   # taglia
                ('SPAN', (6, 29), (11, 30)),   # riempie
                ('SPAN', (12, 21), (12, 30)),  # label sequenza stratigrafica
                ('SPAN', (13, 21), (17, 25)),  # posteriore a
                ('SPAN', (13, 26), (17, 30)),  # uguale a
                ('VALIGN', (0, 21), (17, 30), 'TOP'),



                ('SPAN', (0, 31), (17, 31)),  # descrizione
                ('VALIGN', (0, 31), (17, 31), 'TOP'),
                # 32-34 row
                ('SPAN', (0, 32), (17, 32)),  # osservazioni
                ('VALIGN', (0, 32), (17, 32), 'TOP'),

                # 35-37 row
                ('SPAN', (0, 33), (17, 33)),  # interpretazione
                ('VALIGN', (0, 33), (17, 33), 'TOP'),

                # # 41-42 row
                
                # #29 row
                ('SPAN', (0, 34), (5, 34)),  # affidabilita stratigrafica
                ('SPAN', (6, 34), (11, 34)),  # direttore
                ('SPAN', (12, 34), (17, 34)),  # responsabile
                ('VALIGN', (0, 34), (17, 34), 'TOP'),
                
                
                ('SPAN', (0, 35), (17, 35)),  # elementi datanti
                ('VALIGN', (0, 35), (17, 35), 'TOP'),

                # #35 row
                # #29 row
                ('SPAN', (0, 36), (5, 36)),  # affidabilita stratigrafica
                ('SPAN', (6, 36), (11, 36)),  # direttore
                ('SPAN', (12, 36), (17, 36)),  # responsabile
                ('VALIGN', (0, 36), (17, 36), 'TOP'),
                #29 row
                ('SPAN', (0, 37), (17, 37)),  # affidabilita stratigrafica
                
                ('VALIGN', (0, 37), (17, 37), 'TOP'),

                ('SPAN', (0, 38), (17, 38)),  # affidabilita stratigrafica
                ('VALIGN', (0, 38), (17, 38), 'TOP'),
                
                ('SPAN', (0, 39), (8, 39)),  # affidabilita stratigrafica
                ('SPAN', (9, 39), (17, 39)),  # affidabilita stratigrafica
                ('VALIGN', (0, 39), (17, 39), 'TOP'),
                
                ('SPAN', (0, 40), (8, 40)),  # affidabilita stratigrafica
                ('SPAN', (9, 40), (17, 40)),  # affidabilita stratigrafica
                ('VALIGN', (0, 40), (17, 40), 'TOP'),        

                
            ]

            colWidths = (15,30,30,30,30,30,30,30,30,30,30,30,20,30,30,30,30,30)
            rowHeights = None

            t = Table(cell_schema, colWidths=colWidths, rowHeights=rowHeights, style=table_style)

            return t
    
    
class US_index_pdf_sheet(object):
    si_lega_a = ''
    uguale_a = ''
    copre = ''
    coperto_da = ''
    riempie = ''
    riempito_da = ''
    taglia = ''
    tagliato_da = ''
    si_appoggia_a = ''
    gli_si_appoggia = ''

    def __init__(self, data):
        self.sito = data[0]
        self.area = data[1]
        self.us = data[2]
        self.d_stratigrafica = data[3]
        self.rapporti = data[17]

    def unzip_rapporti_stratigrafici(self):
        rapporti = eval(self.rapporti)
        for rapporto in rapporti:
            if len(rapporto) == 5:
                if rapporto[0] == 'Si lega a' or rapporto[0] == 'si lega a':
                    if self.si_lega_a == '':
                        self.si_lega_a += str(rapporto[1])
                    else:
                        self.si_lega_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Uguale a' or rapporto[0] == 'uguale a':
                    if self.uguale_a == '':
                        self.uguale_a += str(rapporto[1])
                    else:
                        self.uguale_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Copre' or rapporto[0] == 'copre':
                    if self.copre == '':
                        self.copre += str(rapporto[1])
                    else:
                        self.copre += ', ' + str(rapporto[1])

                if rapporto[0] == 'Coperto da' or rapporto[0] == 'coperto da':
                    if self.coperto_da == '':
                        self.coperto_da += str(rapporto[1])
                    else:
                        self.coperto_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Riempie' or rapporto[0] == 'riempie':
                    if self.riempie == '':
                        self.riempie += str(rapporto[1])
                    else:
                        self.riempie += ', ' + str(rapporto[1])

                if rapporto[0] == 'Riempito da' or rapporto[0] == 'riempito da':
                    if self.riempito_da == '':
                        self.riempito_da += str(rapporto[1])
                    else:
                        self.riempito_da += ', ' + str(rapporto[1])
                if rapporto[0] == 'Taglia' or rapporto[0] == 'taglia':
                    if self.taglia == '':
                        self.taglia += str(rapporto[1])
                    else:
                        self.taglia += ', ' + str(rapporto[1])

                if rapporto[0] == 'Tagliato da' or rapporto[0] == 'tagliato da':
                    if self.tagliato_da == '':
                        self.tagliato_da += str(rapporto[1])
                    else:
                        self.tagliato_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Si appoggia a' or rapporto[0] == 'si appoggia a':
                    if self.si_appoggia_a == '':
                        self.si_appoggia_a += str(rapporto[1])
                    else:
                        self.si_appoggia_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Gli si appoggia' or rapporto[0] == 'gli si appoggia':
                    if self.gli_si_appoggia == '':
                        self.gli_si_appoggia += str(rapporto[1])
                    else:
                        self.gli_si_appoggia += ', ' + str(rapporto[1])
            elif len(rapporto) == 4:
                if rapporto[0] == 'Si lega a' or rapporto[0] == 'si lega a':
                    if self.si_lega_a == '':
                        self.si_lega_a += str(rapporto[1])
                    else:
                        self.si_lega_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Uguale a' or rapporto[0] == 'uguale a':
                    if self.uguale_a == '':
                        self.uguale_a += str(rapporto[1])
                    else:
                        self.uguale_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Copre' or rapporto[0] == 'copre':
                    if self.copre == '':
                        self.copre += str(rapporto[1])
                    else:
                        self.copre += ', ' + str(rapporto[1])

                if rapporto[0] == 'Coperto da' or rapporto[0] == 'coperto da':
                    if self.coperto_da == '':
                        self.coperto_da += str(rapporto[1])
                    else:
                        self.coperto_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Riempie' or rapporto[0] == 'riempie':
                    if self.riempie == '':
                        self.riempie += str(rapporto[1])
                    else:
                        self.riempie += ', ' + str(rapporto[1])

                if rapporto[0] == 'Riempito da' or rapporto[0] == 'riempito da':
                    if self.riempito_da == '':
                        self.riempito_da += str(rapporto[1])
                    else:
                        self.riempito_da += ', ' + str(rapporto[1])
                if rapporto[0] == 'Taglia' or rapporto[0] == 'taglia':
                    if self.taglia == '':
                        self.taglia += str(rapporto[1])
                    else:
                        self.taglia += ', ' + str(rapporto[1])

                if rapporto[0] == 'Tagliato da' or rapporto[0] == 'tagliato da':
                    if self.tagliato_da == '':
                        self.tagliato_da += str(rapporto[1])
                    else:
                        self.tagliato_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Si appoggia a' or rapporto[0] == 'si appoggia a':
                    if self.si_appoggia_a == '':
                        self.si_appoggia_a += str(rapporto[1])
                    else:
                        self.si_appoggia_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Gli si appoggia' or rapporto[0] == 'gli si appoggia':
                    if self.gli_si_appoggia == '':
                        self.gli_si_appoggia += str(rapporto[1])
                    else:
                        self.gli_si_appoggia += ', ' + str(rapporto[1])
    
            elif len(rapporto) == 3:
                if rapporto[0] == 'Si lega a' or rapporto[0] == 'si lega a':
                    if self.si_lega_a == '':
                        self.si_lega_a += str(rapporto[1])
                    else:
                        self.si_lega_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Uguale a' or rapporto[0] == 'uguale a':
                    if self.uguale_a == '':
                        self.uguale_a += str(rapporto[1])
                    else:
                        self.uguale_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Copre' or rapporto[0] == 'copre':
                    if self.copre == '':
                        self.copre += str(rapporto[1])
                    else:
                        self.copre += ', ' + str(rapporto[1])

                if rapporto[0] == 'Coperto da' or rapporto[0] == 'coperto da':
                    if self.coperto_da == '':
                        self.coperto_da += str(rapporto[1])
                    else:
                        self.coperto_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Riempie' or rapporto[0] == 'riempie':
                    if self.riempie == '':
                        self.riempie += str(rapporto[1])
                    else:
                        self.riempie += ', ' + str(rapporto[1])

                if rapporto[0] == 'Riempito da' or rapporto[0] == 'riempito da':
                    if self.riempito_da == '':
                        self.riempito_da += str(rapporto[1])
                    else:
                        self.riempito_da += ', ' + str(rapporto[1])
                if rapporto[0] == 'Taglia' or rapporto[0] == 'taglia':
                    if self.taglia == '':
                        self.taglia += str(rapporto[1])
                    else:
                        self.taglia += ', ' + str(rapporto[1])

                if rapporto[0] == 'Tagliato da' or rapporto[0] == 'tagliato da':
                    if self.tagliato_da == '':
                        self.tagliato_da += str(rapporto[1])
                    else:
                        self.tagliato_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Si appoggia a' or rapporto[0] == 'si appoggia a':
                    if self.si_appoggia_a == '':
                        self.si_appoggia_a += str(rapporto[1])
                    else:
                        self.si_appoggia_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Gli si appoggia' or rapporto[0] == 'gli si appoggia':
                    if self.gli_si_appoggia == '':
                        self.gli_si_appoggia += str(rapporto[1])
                    else:
                        self.gli_si_appoggia += ', ' + str(rapporto[1])
    
            elif len(rapporto) == 2:
                if rapporto[0] == 'Si lega a' or rapporto[0] == 'si lega a':
                    if self.si_lega_a == '':
                        self.si_lega_a += str(rapporto[1])
                    else:
                        self.si_lega_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Uguale a' or rapporto[0] == 'uguale a':
                    if self.uguale_a == '':
                        self.uguale_a += str(rapporto[1])
                    else:
                        self.uguale_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Copre' or rapporto[0] == 'copre':
                    if self.copre == '':
                        self.copre += str(rapporto[1])
                    else:
                        self.copre += ', ' + str(rapporto[1])

                if rapporto[0] == 'Coperto da' or rapporto[0] == 'coperto da':
                    if self.coperto_da == '':
                        self.coperto_da += str(rapporto[1])
                    else:
                        self.coperto_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Riempie' or rapporto[0] == 'riempie':
                    if self.riempie == '':
                        self.riempie += str(rapporto[1])
                    else:
                        self.riempie += ', ' + str(rapporto[1])

                if rapporto[0] == 'Riempito da' or rapporto[0] == 'riempito da':
                    if self.riempito_da == '':
                        self.riempito_da += str(rapporto[1])
                    else:
                        self.riempito_da += ', ' + str(rapporto[1])
                if rapporto[0] == 'Taglia' or rapporto[0] == 'taglia':
                    if self.taglia == '':
                        self.taglia += str(rapporto[1])
                    else:
                        self.taglia += ', ' + str(rapporto[1])

                if rapporto[0] == 'Tagliato da' or rapporto[0] == 'tagliato da':
                    if self.tagliato_da == '':
                        self.tagliato_da += str(rapporto[1])
                    else:
                        self.tagliato_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Si appoggia a' or rapporto[0] == 'si appoggia a':
                    if self.si_appoggia_a == '':
                        self.si_appoggia_a += str(rapporto[1])
                    else:
                        self.si_appoggia_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Gli si appoggia' or rapporto[0] == 'gli si appoggia':
                    if self.gli_si_appoggia == '':
                        self.gli_si_appoggia += str(rapporto[1])
                    else:
                        self.gli_si_appoggia += ', ' + str(rapporto[1])



    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 10
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 6
        styNormal.fontName = 'Cambria'
        self.unzip_rapporti_stratigrafici()

        area = Paragraph("<b>Area</b><br/>" + str(self.area), styNormal)
        us = Paragraph("<b>US</b><br/>" + str(self.us), styNormal)
        d_stratigrafica = Paragraph("<b>Definizione stratigrafica</b><br/>" + str(self.d_stratigrafica), styNormal)
        copre = Paragraph("<b>Copre</b><br/>" + str(self.copre), styNormal)
        coperto_da = Paragraph("<b>Coperto da</b><br/>" + str(self.coperto_da), styNormal)
        taglia = Paragraph("<b>Taglia</b><br/>" + str(self.taglia), styNormal)
        tagliato_da = Paragraph("<b>Tagliato da</b><br/>" + str(self.tagliato_da), styNormal)
        riempie = Paragraph("<b>Riempie</b><br/>" + str(self.riempie), styNormal)
        riempito_da = Paragraph("<b>Riempito da</b><br/>" + str(self.riempito_da), styNormal)
        si_appoggia_a = Paragraph("<b>Si appoggia a</b><br/>" + str(self.si_appoggia_a), styNormal)
        gli_si_appoggia = Paragraph("<b>Gli si appoggia</b><br/>" + str(self.gli_si_appoggia), styNormal)
        uguale_a = Paragraph("<b>Uguale a</b><br/>" + str(self.uguale_a), styNormal)
        si_lega_a = Paragraph("<b>Si lega a</b><br/>" + str(self.si_lega_a), styNormal)

        data = [area,
                us,
                d_stratigrafica,
                copre,
                coperto_da,
                taglia,
                tagliato_da,
                riempie,
                riempito_da,
                si_appoggia_a,
                gli_si_appoggia,
                uguale_a,
                si_lega_a]

        """
        for i in range(20):
            data.append([area = Paragraph("<b>Area</b><br/>" + str(area),styNormal),
                        us = Paragraph("<b>US</b><br/>" + str(us),styNormal),
                        copre = Paragraph("<b>Copre</b><br/>" + str(copre),styNormal),
                        coperto_da = Paragraph("<b>Coperto da</b><br/>" + str(coperto_da),styNormal),
                        taglia = Paragraph("<b>Taglia</b><br/>" + str(taglia),styNormal),
                        tagliato_da = Paragraph("<b>Tagliato da</b><br/>" + str(tagliato_da),styNormal),
                        riempie = Paragraph("<b>Riempie</b><br/>" + str(riempie),styNormal),
                        riempito_da = Paragraph("<b>Riempito da</b><br/>" + str(riempito_da),styNormal),
                        si_appoggia_a = Paragraph("<b>Si appoggia a</b><br/>" + str(si_appoggia_a),styNormal),
                        gli_si_appoggia = Paragraph("<b>Gli si appoggia</b><br/>" + str(gli_si_appoggi),styNormal),
                        uguale_a = Paragraph("<b>Uguale a</b><br/>" + str(uguale_a),styNormal),
                        si_lega_a = Paragraph("<b>Si lega a</b><br/>" + str(si_lega_a),styNormal)])
        """
        # t = Table(data,  colWidths=55.5)

        return data
    
    
    def unzip_rapporti_stratigrafici_en(self):
        rapporti = eval(self.rapporti)

        rapporti.sort()
        
        for rapporto in rapporti:
            if len(rapporto) == 5:
                if rapporto[0] == 'Connected to' or rapporto[0] == 'Connected to':
                    if self.si_lega_a == '':
                        self.si_lega_a += str(rapporto[1])
                    else:
                        self.si_lega_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Same as' or rapporto[0] == 'same as':
                    if self.uguale_a == '':
                        self.uguale_a += str(rapporto[1])
                    else:
                        self.uguale_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Covers' or rapporto[0] == 'cover':
                    if self.copre == '':
                        self.copre += str(rapporto[1])
                    else:
                        self.copre += ', ' + str(rapporto[1])

                if rapporto[0] == 'Covered by' or rapporto[0] == 'covered by':
                    if self.coperto_da == '':
                        self.coperto_da += str(rapporto[1])
                    else:
                        self.coperto_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Fills' or rapporto[0] == 'fill':
                    if self.riempie == '':
                        self.riempie += str(rapporto[1])
                    else:
                        self.riempie += ', ' + str(rapporto[1])

                if rapporto[0] == 'Filled by' or rapporto[0] == 'filled by':
                    if self.riempito_da == '':
                        self.riempito_da += str(rapporto[1])
                    else:
                        self.riempito_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Cuts' or rapporto[0] == 'cuts':
                    if self.taglia == '':
                        self.taglia += str(rapporto[1])
                    else:
                        self.taglia += ', ' + str(rapporto[1])

                if rapporto[0] == 'Cutted by' or rapporto[0] == 'cutted by':
                    if self.tagliato_da == '':
                        self.tagliato_da += str(rapporto[1])
                    else:
                        self.tagliato_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Abuts' or rapporto[0] == 'abuts':
                    if self.si_appoggia_a == '':
                        self.si_appoggia_a += str(rapporto[1])
                    else:
                        self.si_appoggia_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Support' or rapporto[0] == 'Support':
                    if self.gli_si_appoggia == '':
                        self.gli_si_appoggia += str(rapporto[1])
                    else:
                        self.gli_si_appoggia += ', ' + str(rapporto[1])
    
            elif len(rapporto) == 4:
                if rapporto[0] == 'Connected to' or rapporto[0] == 'Connected to':
                    if self.si_lega_a == '':
                        self.si_lega_a += str(rapporto[1])
                    else:
                        self.si_lega_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Same as' or rapporto[0] == 'same as':
                    if self.uguale_a == '':
                        self.uguale_a += str(rapporto[1])
                    else:
                        self.uguale_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Covers' or rapporto[0] == 'cover':
                    if self.copre == '':
                        self.copre += str(rapporto[1])
                    else:
                        self.copre += ', ' + str(rapporto[1])

                if rapporto[0] == 'Covered by' or rapporto[0] == 'covered by':
                    if self.coperto_da == '':
                        self.coperto_da += str(rapporto[1])
                    else:
                        self.coperto_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Fills' or rapporto[0] == 'fill':
                    if self.riempie == '':
                        self.riempie += str(rapporto[1])
                    else:
                        self.riempie += ', ' + str(rapporto[1])

                if rapporto[0] == 'Filled by' or rapporto[0] == 'filled by':
                    if self.riempito_da == '':
                        self.riempito_da += str(rapporto[1])
                    else:
                        self.riempito_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Cuts' or rapporto[0] == 'cuts':
                    if self.taglia == '':
                        self.taglia += str(rapporto[1])
                    else:
                        self.taglia += ', ' + str(rapporto[1])

                if rapporto[0] == 'Cutted by' or rapporto[0] == 'cutted by':
                    if self.tagliato_da == '':
                        self.tagliato_da += str(rapporto[1])
                    else:
                        self.tagliato_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Abuts' or rapporto[0] == 'abuts':
                    if self.si_appoggia_a == '':
                        self.si_appoggia_a += str(rapporto[1])
                    else:
                        self.si_appoggia_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Support' or rapporto[0] == 'Support':
                    if self.gli_si_appoggia == '':
                        self.gli_si_appoggia += str(rapporto[1])
                    else:
                        self.gli_si_appoggia += ', ' + str(rapporto[1])
                        
            elif len(rapporto) == 3:
                if rapporto[0] == 'Connected to' or rapporto[0] == 'Connected to':
                    if self.si_lega_a == '':
                        self.si_lega_a += str(rapporto[1])
                    else:
                        self.si_lega_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Same as' or rapporto[0] == 'same as':
                    if self.uguale_a == '':
                        self.uguale_a += str(rapporto[1])
                    else:
                        self.uguale_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Covers' or rapporto[0] == 'cover':
                    if self.copre == '':
                        self.copre += str(rapporto[1])
                    else:
                        self.copre += ', ' + str(rapporto[1])

                if rapporto[0] == 'Covered by' or rapporto[0] == 'covered by':
                    if self.coperto_da == '':
                        self.coperto_da += str(rapporto[1])
                    else:
                        self.coperto_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Fills' or rapporto[0] == 'fill':
                    if self.riempie == '':
                        self.riempie += str(rapporto[1])
                    else:
                        self.riempie += ', ' + str(rapporto[1])

                if rapporto[0] == 'Filled by' or rapporto[0] == 'filled by':
                    if self.riempito_da == '':
                        self.riempito_da += str(rapporto[1])
                    else:
                        self.riempito_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Cuts' or rapporto[0] == 'cuts':
                    if self.taglia == '':
                        self.taglia += str(rapporto[1])
                    else:
                        self.taglia += ', ' + str(rapporto[1])

                if rapporto[0] == 'Cutted by' or rapporto[0] == 'cutted by':
                    if self.tagliato_da == '':
                        self.tagliato_da += str(rapporto[1])
                    else:
                        self.tagliato_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Abuts' or rapporto[0] == 'abuts':
                    if self.si_appoggia_a == '':
                        self.si_appoggia_a += str(rapporto[1])
                    else:
                        self.si_appoggia_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Support' or rapporto[0] == 'Support':
                    if self.gli_si_appoggia == '':
                        self.gli_si_appoggia += str(rapporto[1])
                    else:
                        self.gli_si_appoggia += ', ' + str(rapporto[1])     
                        
            elif len(rapporto) == 2:
                if rapporto[0] == 'Connected to' or rapporto[0] == 'Connected to':
                    if self.si_lega_a == '':
                        self.si_lega_a += str(rapporto[1])
                    else:
                        self.si_lega_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Same as' or rapporto[0] == 'same as':
                    if self.uguale_a == '':
                        self.uguale_a += str(rapporto[1])
                    else:
                        self.uguale_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Covers' or rapporto[0] == 'cover':
                    if self.copre == '':
                        self.copre += str(rapporto[1])
                    else:
                        self.copre += ', ' + str(rapporto[1])

                if rapporto[0] == 'Covered by' or rapporto[0] == 'covered by':
                    if self.coperto_da == '':
                        self.coperto_da += str(rapporto[1])
                    else:
                        self.coperto_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Fills' or rapporto[0] == 'fill':
                    if self.riempie == '':
                        self.riempie += str(rapporto[1])
                    else:
                        self.riempie += ', ' + str(rapporto[1])

                if rapporto[0] == 'Filled by' or rapporto[0] == 'filled by':
                    if self.riempito_da == '':
                        self.riempito_da += str(rapporto[1])
                    else:
                        self.riempito_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Cuts' or rapporto[0] == 'cuts':
                    if self.taglia == '':
                        self.taglia += str(rapporto[1])
                    else:
                        self.taglia += ', ' + str(rapporto[1])

                if rapporto[0] == 'Cutted by' or rapporto[0] == 'cutted by':
                    if self.tagliato_da == '':
                        self.tagliato_da += str(rapporto[1])
                    else:
                        self.tagliato_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Abuts' or rapporto[0] == 'abuts':
                    if self.si_appoggia_a == '':
                        self.si_appoggia_a += str(rapporto[1])
                    else:
                        self.si_appoggia_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Support' or rapporto[0] == 'Support':
                    if self.gli_si_appoggia == '':
                        self.gli_si_appoggia += str(rapporto[1])
                    else:
                        self.gli_si_appoggia += ', ' + str(rapporto[1])            
    def getTable_en(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7
        styNormal.fontName = 'Cambria'
        self.unzip_rapporti_stratigrafici_en()

        area = Paragraph("<b>Area</b><br/>" + str(self.area), styNormal)
        us = Paragraph("<b>SU</b><br/>" + str(self.us), styNormal)
        d_stratigrafica = Paragraph("<b>SU Definition</b><br/>" + str(self.d_stratigrafica), styNormal)
        copre = Paragraph("<b>Covers</b><br/>" + str(self.copre), styNormal)
        coperto_da = Paragraph("<b>Covered by</b><br/>" + str(self.coperto_da), styNormal)
        taglia = Paragraph("<b>Cuts</b><br/>" + str(self.taglia), styNormal)
        tagliato_da = Paragraph("<b>Cutted by</b><br/>" + str(self.tagliato_da), styNormal)
        riempie = Paragraph("<b>Fills</b><br/>" + str(self.riempie), styNormal)
        riempito_da = Paragraph("<b>Filled by</b><br/>" + str(self.riempito_da), styNormal)
        si_appoggia_a = Paragraph("<b>Abuts</b><br/>" + str(self.si_appoggia_a), styNormal)
        gli_si_appoggia = Paragraph("<b>Support</b><br/>" + str(self.gli_si_appoggia), styNormal)
        uguale_a = Paragraph("<b>Same as</b><br/>" + str(self.uguale_a), styNormal)
        si_lega_a = Paragraph("<b>Connected to</b><br/>" + str(self.si_lega_a), styNormal)

        data = [area,
                us,
                d_stratigrafica,
                copre,
                coperto_da,
                taglia,
                tagliato_da,
                riempie,
                riempito_da,
                si_appoggia_a,
                gli_si_appoggia,
                uguale_a,
                si_lega_a]

        """
        for i in range(20):
            data.append([area = Paragraph("<b>Area</b><br/>" + str(area),styNormal),
                        us = Paragraph("<b>US</b><br/>" + str(us),styNormal),
                        copre = Paragraph("<b>Copre</b><br/>" + str(copre),styNormal),
                        coperto_da = Paragraph("<b>Coperto da</b><br/>" + str(coperto_da),styNormal),
                        taglia = Paragraph("<b>Taglia</b><br/>" + str(taglia),styNormal),
                        tagliato_da = Paragraph("<b>Tagliato da</b><br/>" + str(tagliato_da),styNormal),
                        riempie = Paragraph("<b>Riempie</b><br/>" + str(riempie),styNormal),
                        riempito_da = Paragraph("<b>Riempito da</b><br/>" + str(riempito_da),styNormal),
                        si_appoggia_a = Paragraph("<b>Si appoggia a</b><br/>" + str(si_appoggia_a),styNormal),
                        gli_si_appoggia = Paragraph("<b>Gli si appoggia</b><br/>" + str(gli_si_appoggi),styNormal),
                        uguale_a = Paragraph("<b>Uguale a</b><br/>" + str(uguale_a),styNormal),
                        si_lega_a = Paragraph("<b>Si lega a</b><br/>" + str(si_lega_a),styNormal)])
        """
        # t = Table(data,  colWidths=55.5)

        return data
    
    def unzip_rapporti_stratigrafici_de(self):
        rapporti = eval(self.rapporti)

        rapporti.sort()
        
        for rapporto in rapporti:
            if len(rapporto) == 5:
                if rapporto[0] == 'Bindet an' or rapporto[0] == 'bindet an':
                    if self.si_lega_a == '':
                        self.si_lega_a += str(rapporto[1])
                    else:
                        self.si_lega_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Entspricht' or rapporto[0] == 'entspricht':
                    if self.uguale_a == '':
                        self.uguale_a += str(rapporto[1])
                    else:
                        self.uguale_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Liegt über' or rapporto[0] == 'liegt über':
                    if self.copre == '':
                        self.copre += str(rapporto[1])
                    else:
                        self.copre += ', ' + str(rapporto[1])

                if rapporto[0] == 'Liegt unter' or rapporto[0] == 'liegt unter':
                    if self.coperto_da == '':
                        self.coperto_da += str(rapporto[1])
                    else:
                        self.coperto_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Verfüllt' or rapporto[0] == 'verfüllt':
                    if self.riempie == '':
                        self.riempie += str(rapporto[1])
                    else:
                        self.riempie += ', ' + str(rapporto[1])

                if rapporto[0] == 'Wird verfüllt durch' or rapporto[0] == 'wird verfüllt durch':
                    if self.riempito_da == '':
                        self.riempito_da += str(rapporto[1])
                    else:
                        self.riempito_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Schneidet' or rapporto[0] == 'schneidet':
                    if self.taglia == '':
                        self.taglia += str(rapporto[1])
                    else:
                        self.taglia += ', ' + str(rapporto[1])

                if rapporto[0] == 'Wird geschnitten' or rapporto[0] == 'wird geschnitten':
                    if self.tagliato_da == '':
                        self.tagliato_da += str(rapporto[1])
                    else:
                        self.tagliato_da += ', ' + str(rapporto[1])

                if rapporto[0] == 'Stützt sich auf' or rapporto[0] == 'stützt sich auf':
                    if self.si_appoggia_a == '':
                        self.si_appoggia_a += str(rapporto[1])
                    else:
                        self.si_appoggia_a += ', ' + str(rapporto[1])

                if rapporto[0] == 'Wird gestüzt von' or rapporto[0] == 'wird gestüzt von':
                    if self.gli_si_appoggia == '':
                        self.gli_si_appoggia += str(rapporto[1])
                    else:
                        self.gli_si_appoggia += ', ' + str(rapporto[1])
    
    def getTable_de(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7
        styNormal.fontName = 'Cambria'
        self.unzip_rapporti_stratigrafici_de()

        area = Paragraph("<b>Bereich</b><br/>" + str(self.area), styNormal)
        us = Paragraph("<b>SE</b><br/>" + str(self.us), styNormal)
        d_stratigrafica = Paragraph("<b>Stratigrafische Definitie</b><br/>" + str(self.d_stratigrafica), styNormal)
        copre = Paragraph("<b>Liegt über</b><br/>" + str(self.copre), styNormal)
        coperto_da = Paragraph("<b>Liegt unter</b><br/>" + str(self.coperto_da), styNormal)
        taglia = Paragraph("<b>Schneidet</b><br/>" + str(self.taglia), styNormal)
        tagliato_da = Paragraph("<b>Wird geschnitten</b><br/>" + str(self.tagliato_da), styNormal)
        riempie = Paragraph("<b>Verfüllt</b><br/>" + str(self.riempie), styNormal)
        riempito_da = Paragraph("<b>Wird verfüllt durch</b><br/>" + str(self.riempito_da), styNormal)
        si_appoggia_a = Paragraph("<b>Stützt sich auf</b><br/>" + str(self.si_appoggia_a), styNormal)
        gli_si_appoggia = Paragraph("<b>Wird gestüzt von</b><br/>" + str(self.gli_si_appoggia), styNormal)
        uguale_a = Paragraph("<b>Entspricht</b><br/>" + str(self.uguale_a), styNormal)
        si_lega_a = Paragraph("<b>Bindet an</b><br/>" + str(self.si_lega_a), styNormal)

        data = [area,
                us,
                d_stratigrafica,
                copre,
                coperto_da,
                taglia,
                tagliato_da,
                riempie,
                riempito_da,
                si_appoggia_a,
                gli_si_appoggia,
                uguale_a,
                si_lega_a]

        """
        for i in range(20):
            data.append([area = Paragraph("<b>Area</b><br/>" + str(area),styNormal),
                        us = Paragraph("<b>US</b><br/>" + str(us),styNormal),
                        copre = Paragraph("<b>Copre</b><br/>" + str(copre),styNormal),
                        coperto_da = Paragraph("<b>Coperto da</b><br/>" + str(coperto_da),styNormal),
                        taglia = Paragraph("<b>Taglia</b><br/>" + str(taglia),styNormal),
                        tagliato_da = Paragraph("<b>Tagliato da</b><br/>" + str(tagliato_da),styNormal),
                        riempie = Paragraph("<b>Riempie</b><br/>" + str(riempie),styNormal),
                        riempito_da = Paragraph("<b>Riempito da</b><br/>" + str(riempito_da),styNormal),
                        si_appoggia_a = Paragraph("<b>Si appoggia a</b><br/>" + str(si_appoggia_a),styNormal),
                        gli_si_appoggia = Paragraph("<b>Gli si appoggia</b><br/>" + str(gli_si_appoggi),styNormal),
                        uguale_a = Paragraph("<b>Uguale a</b><br/>" + str(uguale_a),styNormal),
                        si_lega_a = Paragraph("<b>Si lega a</b><br/>" + str(si_lega_a),styNormal)])
        """
        # t = Table(data,  colWidths=55.5)

        return data 
    def makeStyles(self):
        styles = TableStyle([('GRID', (0, 0), (-1, -1), 0.0, colors.black), ('VALIGN', (0, 0), (-1, -1), 'TOP')
                             ])  # finale

        return styles

class FOTO_index_pdf_sheet(object):
    

    def __init__(self, data):
        
        self.sito= data[0]
        self.foto = data[5]
        self.thumbnail = data[6]
        self.us = data[2]
        self.area = data[1]
        self.d_stratigrafica= data[4]
        self.unita_tipo =data[3]
    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7
        styNormal.fontName = 'Cambria'
        

        conn = Connection()
    
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        
        
        area = Paragraph("<b>Area</b><br/>" + str(self.area), styNormal)
        if self.unita_tipo == 'US':
            us = Paragraph("<b>US</b><br/>" + str(self.us), styNormal)
        else:
            us = Paragraph("<b>USM</b><br/>" + str(self.us), styNormal)
        foto = Paragraph("<b>Foto ID</b><br/>" + str(self.foto), styNormal)
        d_stratigrafica = Paragraph("<b>Descrizione</b><br/>" + str(self.d_stratigrafica), styNormal)
        us_presenti = Paragraph("<b>US-USM presenti</b><br/>", styNormal)
        
        logo= Image(self.thumbnail)
        logo.drawHeight = 1 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1 * inch
        logo.hAlign = "CENTER"
        
        thumbnail= logo
        data = [
                foto,
                thumbnail,
                us,
                area,
                d_stratigrafica
                ]

        return data
    
    def getTable_en(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7
        styNormal.fontName = 'Cambria'
        

        conn = Connection()
    
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        area = Paragraph("<b>Area</b><br/>" + str(self.area), styNormal)
        if self.unita_tipo == 'SU':
            us = Paragraph("<b>SU</b><br/>" + str(self.us), styNormal)
        else:
            us = Paragraph("<b>WSU</b><br/>" + str(self.us), styNormal)
        foto = Paragraph("<b>ID</b><br/>" + str(self.foto), styNormal)
        d_stratigrafica = Paragraph("<b>Description</b><br/>" + str(self.d_stratigrafica), styNormal)
        us_presenti = Paragraph("<b>SU-WSU in list</b><br/>", styNormal)
        
        logo= Image(self.thumbnail)
        logo.drawHeight = 1 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1 * inch
        logo.hAlign = "CENTER"
        
        thumbnail= logo
        data = [
                foto,
                thumbnail,
                us,
                area,
                d_stratigrafica
                ]

        return data
    
    def getTable_de(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7
        styNormal.fontName = 'Cambria'
        

        conn = Connection()
    
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        area = Paragraph("<b>Area</b><br/>" + str(self.area), styNormal)
        if self.unita_tipo == 'SE':
            us = Paragraph("<b>SE</b><br/>" + str(self.us), styNormal)
        else:
            us = Paragraph("<b>MSE</b><br/>" + str(self.us), styNormal)
        foto = Paragraph("<b>Foto ID</b><br/>" + str(self.foto), styNormal)
        d_stratigrafica = Paragraph("<b>Beschreibung</b><br/>" + str(self.d_stratigrafica), styNormal)
        us_presenti = Paragraph("<b>SE-MSE in Liste</b><br/>", styNormal)
        
        logo= Image(self.thumbnail)
        logo.drawHeight = 1 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1 * inch
        logo.hAlign = "CENTER"
        
        thumbnail= logo
        data = [
                foto,
                thumbnail,
                us,
                area,
                d_stratigrafica
                ]

        return data
    
    def makeStyles(self):
        styles = TableStyle([('GRID', (0, 0), (-1, -1), 0.0, colors.black), ('VALIGN', (0, 0), (-1, -1), 'TOP')
                             ])  # finale

        return styles
class FOTO_index_pdf_sheet_2(object):
    

    def __init__(self, data):
        
        self.sito= data[0]
        self.foto = data[5]
        #self.thumbnail = data[6]
        self.us = data[2]
        self.area = data[1]
        self.d_stratigrafica= data[4]
        self.unita_tipo =data[3]
    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7
        styNormal.fontName = 'Cambria'
        

        conn = Connection()
    
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        area = Paragraph("<b>Area</b><br/>" + str(self.area), styNormal)
        if self.unita_tipo == 'US':
            us = Paragraph("<b>US</b><br/>" + str(self.us), styNormal)
        else:
            us = Paragraph("<b>USM</b><br/>" + str(self.us), styNormal)
        foto = Paragraph("<b>Foto ID</b><br/>" + str(self.foto), styNormal)
        d_stratigrafica = Paragraph("<b>Descrizione</b><br/>" + str(self.d_stratigrafica), styNormal)
        us_presenti = Paragraph("<b>US-USM presenti</b><br/>", styNormal)
        
        # logo= Image(self.thumbnail)
        # logo.drawHeight = 1 * inch * logo.drawHeight / logo.drawWidth
        # logo.drawWidth = 1 * inch
        # logo.hAlign = "CENTER"
        
        #thumbnail= logo
        data = [
                foto,
                #thumbnail,
                us,
                area,
                d_stratigrafica
                ]

        return data
    
    def getTable_en(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7

        

        conn = Connection()
    
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        area = Paragraph("<b>Area</b><br/>" + str(self.area), styNormal)
        if self.unita_tipo == 'SU':
            us = Paragraph("<b>SU</b><br/>" + str(self.us), styNormal)
        else:
            us = Paragraph("<b>WSU</b><br/>" + str(self.us), styNormal)
        foto = Paragraph("<b>ID</b><br/>" + str(self.foto), styNormal)
        d_stratigrafica = Paragraph("<b>Description</b><br/>" + str(self.d_stratigrafica), styNormal)
        us_presenti = Paragraph("<b>SU-WSU in list</b><br/>", styNormal)
        
        # logo= Image(self.thumbnail)
        # logo.drawHeight = 1 * inch * logo.drawHeight / logo.drawWidth
        # logo.drawWidth = 1 * inch
        # logo.hAlign = "CENTER"
        
        #thumbnail= logo
        data = [
                foto,
                #thumbnail,
                us,
                area,
                d_stratigrafica
                ]

        return data
    def getTable_de(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7

        

        conn = Connection()
    
        thumb_path = conn.thumb_path()
        thumb_path_str = thumb_path['thumb_path']
        area = Paragraph("<b>Area</b><br/>" + str(self.area), styNormal)
        if self.unita_tipo == 'SE':
            us = Paragraph("<b>SE</b><br/>" + str(self.us), styNormal)
        else:
            us = Paragraph("<b>MSE</b><br/>" + str(self.us), styNormal)
        foto = Paragraph("<b>Foto ID</b><br/>" + str(self.foto), styNormal)
        d_stratigrafica = Paragraph("<b>Beschreibung</b><br/>" + str(self.d_stratigrafica), styNormal)
        us_presenti = Paragraph("<b>SE-MSE in Liste</b><br/>", styNormal)
        
        # logo= Image(self.thumbnail)
        # logo.drawHeight = 1 * inch * logo.drawHeight / logo.drawWidth
        # logo.drawWidth = 1 * inch
        # logo.hAlign = "CENTER"
        
        #thumbnail= logo
        data = [
                foto,
                #thumbnail,
                us,
                area,
                d_stratigrafica
                ]

        return data
    
    def makeStyles(self):
        styles = TableStyle([('GRID', (0, 0), (-1, -1), 0.0, colors.black), ('VALIGN', (0, 0), (-1, -1), 'TOP')
                             ])  # finale

        return styles    
        
class generate_US_pdf(object):
    HOME = os.environ['PYARCHINIT_HOME']

    PDF_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def build_US_sheets(self, records):
        home = os.environ['PYARCHINIT_HOME']
        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        if not bool(lo_path_str):
            logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        else:
            logo_path=lo_path_str
        logo_path2 = '{}{}{}'.format(home_DB_path, os.sep, 'logo_2.png')
        logo = Image(logo_path)
        logo.drawHeight = 2.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 2.5 * inch
        logo.hAlign = "CENTER"
        
        elements_us_iccd = []
        for i in range(len(records)):
            single_us_sheet = single_US_pdf_sheet(records[i])
            elements_us_iccd.append(logo)
            elements_us_iccd.append(Spacer(4, 6))
            elements_us_iccd.append(single_us_sheet.create_sheet_archeo3_usm_fields_2()) 
            
            elements_us_iccd.append(PageBreak())
            
            
            #terza versione scheda US SENZA CAMPI US formato Ministeriale ICCD
            
            
        dt = datetime.datetime.now()
        
        
        
        #us
        # filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        # self.PDF_path, os.sep, 'scheda_US', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        # f = open(filename, "wb")

        # doc = SimpleDocTemplate(f, pagesize=A4)
        # doc.build(elements_us_pyarchinit, canvasmaker=NumberedCanvas_USsheet)

        # f.close()

        # #ususm
        # filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        # self.PDF_path, os.sep, 'scheda_USUSM', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        # f = open(filename, "wb")

        # doc = SimpleDocTemplate(f, pagesize=A4)
        # doc.build(elements_ususm_pyarchinit, canvasmaker=NumberedCanvas_USsheet)

        # f.close()

        #usICCD
        filename = ('%s%s%s') % (
        self.PDF_path, os.sep, 'Scheda USICCD.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(21 * cm, 29 * cm),  topMargin=10, bottomMargin=20,
                                leftMargin=10, rightMargin=10)
        doc.build(elements_us_iccd, canvasmaker=NumberedCanvas_USsheet)

        f.close()

    
    def build_US_sheets_en(self, records):
        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        
        if not bool(lo_path_str):
            logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        else:
            logo_path=lo_path_str
        logo_path2 = '{}{}{}'.format(home_DB_path, os.sep, 'logo_2.png')
        logo = Image(logo_path)
        logo.drawHeight = 2.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 2.5 * inch
        logo.hAlign = "CENTER"
        
        elements_us_iccd = []
        for i in range(len(records)):
            single_us_sheet = single_US_pdf_sheet(records[i])
            elements_us_iccd.append(logo)
            elements_us_iccd.append(Spacer(4, 6))
            elements_us_iccd.append(single_us_sheet.create_sheet_en()) 
            
            elements_us_iccd.append(PageBreak())
            
            
            #terza versione scheda US SENZA CAMPI US formato Ministeriale ICCD
            
            
        dt = datetime.datetime.now()
        
        
        
        #us
        # filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        # self.PDF_path, os.sep, 'scheda_US', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        # f = open(filename, "wb")

        # doc = SimpleDocTemplate(f, pagesize=A4)
        # doc.build(elements_us_pyarchinit, canvasmaker=NumberedCanvas_USsheet)

        # f.close()

        # #ususm
        # filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        # self.PDF_path, os.sep, 'scheda_USUSM', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        # f = open(filename, "wb")

        # doc = SimpleDocTemplate(f, pagesize=A4)
        # doc.build(elements_ususm_pyarchinit, canvasmaker=NumberedCanvas_USsheet)

        # f.close()

        #usICCD
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        self.PDF_path, os.sep, 'Form SU', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(21 * cm, 29 * cm),  topMargin=10, bottomMargin=20,
                                leftMargin=10, rightMargin=10)
        doc.build(elements_us_iccd, canvasmaker=NumberedCanvas_USsheet)

        f.close()
    
    
    
    def build_US_sheets_de(self, records):
        home = os.environ['PYARCHINIT_HOME']

        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        if not bool(lo_path_str):
            logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        else:
            logo_path=lo_path_str
        logo_path2 = '{}{}{}'.format(home_DB_path, os.sep, 'logo_2.png')
        logo = Image(logo_path)
        logo.drawHeight = 2.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 2.5 * inch
        logo.hAlign = "CENTER"
        
        elements_us_iccd = []
        for i in range(len(records)):
            single_us_sheet = single_US_pdf_sheet(records[i])
            elements_us_iccd.append(logo)
            elements_us_iccd.append(Spacer(4, 6))
            elements_us_iccd.append(single_us_sheet.create_sheet_de()) 
            
            elements_us_iccd.append(PageBreak())
            
            
            #terza versione scheda US SENZA CAMPI US formato Ministeriale ICCD
            
            
        dt = datetime.datetime.now()
        
        
        
        #us
        # filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        # self.PDF_path, os.sep, 'scheda_US', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        # f = open(filename, "wb")

        # doc = SimpleDocTemplate(f, pagesize=A4)
        # doc.build(elements_us_pyarchinit, canvasmaker=NumberedCanvas_USsheet)

        # f.close()

        # #ususm
        # filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        # self.PDF_path, os.sep, 'scheda_USUSM', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        # f = open(filename, "wb")

        # doc = SimpleDocTemplate(f, pagesize=A4)
        # doc.build(elements_ususm_pyarchinit, canvasmaker=NumberedCanvas_USsheet)

        # f.close()

        #usICCD
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        self.PDF_path, os.sep, 'Form SE', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(21 * cm, 29 * cm),  topMargin=10, bottomMargin=20,
                                leftMargin=10, rightMargin=10)
        doc.build(elements_us_iccd, canvasmaker=NumberedCanvas_USsheet)

        f.close()
    
    
    
    def build_index_US(self, records, sito):
        home = os.environ['PYARCHINIT_HOME']

        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        if not bool(lo_path_str):
            logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        else:
            logo_path=lo_path_str

        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch
        logo.hAlign = "LEFT"

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.fontName='Cambria'
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        styH1 = styleSheet['Heading3']
        styH1.fontName='Cambria'
        data = self.datestrfdate()

        lst = []
        lst.append(logo)
        lst.append(
            Paragraph("<b>ELENCO UNITA' STRATIGRAFICHE</b><br/><b>Scavo: %s</b>" % (sito), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = US_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable())

        styles = exp_index.makeStyles()
        colWidths = [30, 28, 118, 45, 58, 45, 58, 55, 64, 64, 52, 52, 52]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        lst.append(Spacer(0, 2))

        dt = datetime.datetime.now()
        filename = ('%s%s%s') % (
        self.PDF_path, os.sep, 'Elenco US.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(A3), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_USindex)

        f.close()
        
    def build_index_Foto(self, records, sito):
        home = os.environ['PYARCHINIT_HOME']

        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        if not bool(lo_path_str):
            logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        else:
            logo_path=lo_path_str
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch
        logo.hAlign = "LEFT"

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        styH1 = styleSheet['Heading3']
        styH1.fontName='Cambria'
        data = self.datestrfdate()

        lst = []
        lst.append(logo)
        lst.append(
            Paragraph("<b>ELENCO FOTO STRATIGRAFICHE</b><br/><b> Scavo: %s</b>" % (sito), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = FOTO_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable())

        styles = exp_index.makeStyles()
        colWidths = [100, 105, 30, 30, 200]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        lst.append(Spacer(0, 2))

        dt = datetime.datetime.now()
        filename = ('%s%s%s') % (
        self.PDF_path, os.sep, 'Elenco Foto.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(lst, canvasmaker=NumberedCanvas_USsheet)

        f.close()
    def build_index_Foto_2(self, records, sito):
        home = os.environ['PYARCHINIT_HOME']

        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        if not bool(lo_path_str):
            logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        else:
            logo_path=lo_path_str
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch
        logo.hAlign = "LEFT"

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        styH1 = styleSheet['Heading3']
        styH1.fontName='Cambria'
        data = self.datestrfdate()

        lst = []
        lst.append(logo)
        lst.append(
            Paragraph("<b>ELENCO FOTO STRATIGRAFICHE</b><br/><b> Scavo: %s</b>" % (sito), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = FOTO_index_pdf_sheet_2(records[i])
            table_data.append(exp_index.getTable())

        styles = exp_index.makeStyles()
        colWidths = [100, 50, 50, 200]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        lst.append(Spacer(0, 2))

        dt = datetime.datetime.now()
        filename = ('%s%s%s') % (
        self.PDF_path, os.sep, 'Elenco Foto.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(lst, canvasmaker=NumberedCanvas_USsheet)

        f.close()
        
    def build_index_US_de(self, records, sito):
        home = os.environ['PYARCHINIT_HOME']

        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        if not bool(lo_path_str):
            logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        else:
            logo_path=lo_path_str
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch
        logo.hAlign = "LEFT"

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        styH1 = styleSheet['Heading3']

        data = self.datestrfdate()

        lst = []
        lst.append(logo)
        lst.append(
            Paragraph("<b>LISTE DER STRATIGRAPHISCHEN EINHEITEN</b><br/><b>Ausgrabung: %s,  Datum: %s</b>" % (sito, data), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = US_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable_de())

        styles = exp_index.makeStyles()
        colWidths = [28, 28, 120, 45, 58, 45, 58, 55, 64, 64, 52, 52, 52]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        lst.append(Spacer(0, 2))

        dt = datetime.datetime.now()
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        self.PDF_path, os.sep, 'LISTE SE', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(A3), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_USindex)

        f.close()
        
    def build_index_Foto_de(self, records, sito):
        home = os.environ['PYARCHINIT_HOME']

        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        if not bool(lo_path_str):
            logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        else:
            logo_path=lo_path_str
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch
        logo.hAlign = "LEFT"

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        styH1 = styleSheet['Heading3']

        data = self.datestrfdate()

        lst = []
        lst.append(logo)
        lst.append(
            Paragraph("<b>LISTE DER STRATIGRAPHISCHEN FOTOS</b><br/><b> Ausgrabung: %s,  Datum: %s</b>" % (sito, data), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = FOTO_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable_de())

        styles = exp_index.makeStyles()
        colWidths = [100, 105, 30, 30, 200]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        lst.append(Spacer(0, 2))

        dt = datetime.datetime.now()
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        self.PDF_path, os.sep, 'Liste foto', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(lst, canvasmaker=NumberedCanvas_USsheet)

        f.close()
    def build_index_Foto_2_de(self, records, sito):
        home = os.environ['PYARCHINIT_HOME']

        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        if not bool(lo_path_str):
            logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        else:
            logo_path=lo_path_str
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch
        logo.hAlign = "LEFT"

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        styH1 = styleSheet['Heading3']

        data = self.datestrfdate()

        lst = []
        lst.append(logo)
        lst.append(
            Paragraph("<b>LISTE DER STRATIGRAPHISCHEN FOTOS</b><br/><b> Ausgrabung: %s,  Datum: %s</b>" % (sito, data), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = FOTO_index_pdf_sheet_2(records[i])
            table_data.append(exp_index.getTable_de())

        styles = exp_index.makeStyles()
        colWidths = [100, 50, 50, 200]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        lst.append(Spacer(0, 2))

        dt = datetime.datetime.now()
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        self.PDF_path, os.sep, 'Liste foto', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(lst, canvasmaker=NumberedCanvas_USsheet)

        f.close()
    
    
    
    def build_index_US_en(self, records, sito):
        home = os.environ['PYARCHINIT_HOME']

        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        if not bool(lo_path_str):
            logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        else:
            logo_path=lo_path_str
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch
        logo.hAlign = "LEFT"

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        styH1 = styleSheet['Heading3']

        data = self.datestrfdate()

        lst = []
        lst.append(logo)
        lst.append(
            Paragraph("<b>LIST OF STRATIGRAPHIC UNITS</b><br/><b>Site: %s,  Date: %s</b>" % (sito, data), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = US_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable_en())

        styles = exp_index.makeStyles()
        colWidths = [28, 28, 120, 45, 58, 45, 58, 55, 64, 64, 52, 52, 52]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        lst.append(Spacer(0, 2))

        dt = datetime.datetime.now()
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        self.PDF_path, os.sep, 'List SU', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(A3), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_USindex)

        f.close()
        
    def build_index_Foto_en(self, records, sito):
        home = os.environ['PYARCHINIT_HOME']

        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        if not bool(lo_path_str):
            logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        else:
            logo_path=lo_path_str
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch
        logo.hAlign = "LEFT"

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        styH1 = styleSheet['Heading3']

        data = self.datestrfdate()

        lst = []
        lst.append(logo)
        lst.append(
            Paragraph("<b>LIST OF STRATIGRAPHIC PHOTOS</b><br/><b> Site: %s,  Date: %s</b>" % (sito, data), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = FOTO_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable_en())

        styles = exp_index.makeStyles()
        colWidths = [100, 105, 30, 30, 200]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        lst.append(Spacer(0, 2))

        dt = datetime.datetime.now()
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        self.PDF_path, os.sep, 'List Photo', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(lst, canvasmaker=NumberedCanvas_USsheet)

        f.close()
    def build_index_Foto_2_en(self, records, sito):
        home = os.environ['PYARCHINIT_HOME']

        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        if not bool(lo_path_str):
            logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        else:
            logo_path=lo_path_str
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch
        logo.hAlign = "LEFT"

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        styH1 = styleSheet['Heading3']

        data = self.datestrfdate()

        lst = []
        lst.append(logo)
        lst.append(
            Paragraph("<b>LIST OF STRATIGRAPHIC PHOTOS</b><br/><b> Site: %s,  Date: %s</b>" % (sito, data), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = FOTO_index_pdf_sheet_2(records[i])
            table_data.append(exp_index.getTable_en())

        styles = exp_index.makeStyles()
        colWidths = [100, 50, 50, 200]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        lst.append(Spacer(0, 2))

        dt = datetime.datetime.now()
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        self.PDF_path, os.sep, 'List Photo', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(lst, canvasmaker=NumberedCanvas_USsheet)

        f.close()
    
    

   