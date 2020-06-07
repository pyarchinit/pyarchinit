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

import datetime
from datetime import date
from numpy import *
import io

from builtins import object
from builtins import range
from builtins import str
from reportlab.lib import colors
from reportlab.lib.pagesizes import (A4)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm 
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, PageBreak, SimpleDocTemplate, Spacer, TableStyle, Image
from reportlab.platypus.paragraph import Paragraph
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
        self.setFont("Helvetica", 8)
        self.drawRightString(200 * mm, 20 * mm,
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
        self.setFont("Helvetica", 8)
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
        # self.foto=data[96]
        # self.unitatipo = data[97]
        # self.thumbanil = data[98]
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
            if len(rapporto) == 2:
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
            if len(rapporto) == 2:
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

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def create_sheet(self):  #scheda in stile pyarchini per l'US
        self.unzip_rapporti_stratigrafici()
        self.unzip_documentazione()

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT

        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.alignment = 4  # Justified

        # format labels

        # 0 row
        intestazione = Paragraph("<b>SCHEDA DI UNITA' STRATIGRAFICA<br/>" + str(self.datestrfdate()) + "</b>",
                                 styNormal)

        # intestazione2 = Paragraph("<b>Pyarchinit</b><br/>https://sites.google.com/site/pyarchinit/", styNormal)

        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path)

        ##      if test_image.drawWidth < 800:

        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch

        # 1 row
        sito = Paragraph("<b>Sito</b><br/>" + str(self.sito), styNormal)
        area = Paragraph("<b>Area</b><br/>" + str(self.area), styNormal)

        # 2 row
        unita_tipo_label = "<b>" + str(self.unita_tipo) + "</b><br/>"
        us = Paragraph(unita_tipo_label + str(self.us), styNormal)

        # 3 row
        d_stratigrafica = Paragraph("<b>Definizione stratigrafica</b><br/>" + self.d_stratigrafica, styNormal)
        d_interpretativa = Paragraph("<b>Definizione Interpretativa</b><br/>" + self.d_interpretativa, styNormal)

        # 4 row
        stato_conservazione = Paragraph("<b>Stato di conservazione</b><br/>" + self.stato_di_conservazione, styNormal)
        consistenza = Paragraph("<b>Consistenza</b><br/>" + self.consistenza, styNormal)
        colore = Paragraph("<b>Colore</b><br/>" + self.colore, styNormal)

        # 5 row
        #inclusi_list = eval(self.inclusi) #da cancellare?
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
        inclusi = Paragraph("<b>Inclusi</b><br/>" + inclusi, styNormal)

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
        campioni = Paragraph("<b>Campioni</b><br/>" + campioni, styNormal)
        formazione = Paragraph("<b>Formazione</b><br/>" + self.formazione, styNormal)

        # 6 row
        descrizione = ''
        try:
            descrizione = Paragraph("<b>Descrizione</b><br/>" + self.descrizione, styDescrizione)
        except:
            pass

        # 7 row
        interpretazione = ''
        try:
            interpretazione = Paragraph("<b>Interpretazione</b><br/>" + self.interpretazione, styDescrizione)
        except:
            pass

        # 8 row
        attivita = Paragraph("<b>Attivita'</b><br/>" + self.attivita, styNormal)
        struttura = Paragraph("<b>Struttura</b><br/>" + self.struttura, styNormal)
        quota_min = Paragraph("<b>Quota Min:</b><br/>" + self.quota_min, styNormal)
        quota_max = Paragraph("<b>Quota Max:</b><br/>" + self.quota_max, styNormal)

        # 9 row
        usm_section = Paragraph("<b>DATI USM</b>", styNormal)

        # 10 row
        settore = Paragraph("<b>Settore</b><br/>" + self.settore, styNormal)
        quadrato = Paragraph("<b>Quadrato/Parete</b><br/>" + self.quad_par, styNormal)
        ambiente = Paragraph("<b>Ambiente</b><br/>" + self.ambient, styNormal)
        saggio = Paragraph("<b>Saggio</b><br/>" + self.saggio, styNormal)

        # 11 row
        elem_datanti = Paragraph("<b>Elementi datanti</b><br/>" + self.elem_datanti, styNormal)
        funz_statica = Paragraph("<b>Funz. Statica</b><br/>" + self.funz_statica, styNormal)
        lavorazione = Paragraph("<b>Lavorazione</b><br/>" + self.lavorazione, styNormal)
        spess_giunti = Paragraph("<b>Spessore giunti</b><br/>" + self.spess_giunti, styNormal)

        # 12 row
        letti_posa = Paragraph("<b>Letti posa</b><br/>" + self.letti_posa, styNormal)
        alt_modulo = Paragraph("<b>Alt. modulo</b><br/>" + self.alt_mod, styNormal)
        un_ed_riass = Paragraph("<b>Unita Ed. Riass</b><br/>" + self.un_ed_riass, styNormal)
        reimp = Paragraph("<b>Reimpiego</b><br/>" + self.reimp, styNormal)

        # 13 row
        posa_opera = Paragraph("<b>Posa in opera</b><br/>" + self.posa_opera, styNormal)
        quota_min_usm = Paragraph("<b>Quota Min. USM:</b><br/>" + self.quota_min_usm, styNormal)
        quota_max_usm = Paragraph("<b>Quota Max. USM:</b><br/>" + self.quota_max_usm, styNormal)

        # 14 row
        modulo_usm = Paragraph("<b>Modulo usm</b><br/>" + self.modulo_usm, styNormal)
        col_legante = Paragraph("<b>Colore legante</b><br/>" + self.col_legante, styNormal)
        aggreg_legante = Paragraph("<b>Aggreganti legante:</b><br/>" + self.aggreg_legante, styNormal)
        con_text_mat = Paragraph("<b>Texture Materiali</b><br/>" + self.con_text_mat, styNormal)
        col_mat = Paragraph("<b>Colore materiale</b><br/>" + self.col_materiale, styNormal)

        # 15row
        inclusi_materiali_usm_list = eval(self.inclusi_materiali_usm)
        inclusi_materiali_usm = ''
        for i in eval(self.inclusi_materiali_usm):
            if inclusi_materiali_usm == '':
                try:
                    inclusi_materiali_usm += str(i[0])
                except:
                    pass
            else:
                try:
                    inclusi_materiali_usm += ', ' + str(i[0])
                except:
                    pass
        inclusi_mat_usm = Paragraph("<b>Inclusi mat. usm</b><br/>" + inclusi_materiali_usm, styNormal)

        # 16 row
        periodizzazione = Paragraph("<b>PERIODIZZAZIONE</b>", styNormal)

        # 17 row
        iniziale = Paragraph("<b>INIZIALE</b>", styNormal)
        periodo_iniziale = Paragraph("<b>Periodo</b><br/>" + self.periodo_iniziale, styNormal)
        fase_iniziale = Paragraph("<b>Fase</b><br/>" + self.fase_iniziale, styNormal)
        finale = Paragraph("<b>FINALE</b>", styNormal)
        periodo_finale = Paragraph("<b>Periodo</b><br/>" + self.periodo_finale, styNormal)
        fase_finale = Paragraph("<b>Fase</b><br/>" + self.fase_finale, styNormal)

        # 18 row
        rapporti_stratigrafici = Paragraph("<b>RAPPORTI STRATIGRAFICI</b>", styNormal)
        piante = Paragraph("<b>Planimetrie</b><br/>" + self.piante, styNormal)

        # 19 row
        si_lega_a = Paragraph("<b>Si lega a</b><br/>" + self.si_lega_a, styNormal)
        uguale_a = Paragraph("<b>Uguale a</b><br/>" + self.uguale_a, styNormal)

        # 20 row
        copre = Paragraph("<b>Copre</b><br/>" + self.copre, styNormal)
        coperto_da = Paragraph("<b>Coperto da</b><br/>" + self.coperto_da, styNormal)

        # 21 row
        riempie = Paragraph("<b>Riempie</b><br/>" + self.riempie, styNormal)
        riempito_da = Paragraph("<b>Riempito da</b><br/>" + self.riempito_da, styNormal)

        # 22 row
        taglia = Paragraph("<b>Taglia</b><br/>" + self.taglia, styNormal)
        tagliato_da = Paragraph("<b>Tagliato da</b><br/>" + self.tagliato_da, styNormal)

        # 23 row
        si_appoggia_a = Paragraph("<b>Si appoggia a</b><br/>" + self.si_appoggia_a, styNormal)
        gli_si_appoggia = Paragraph("<b>Gli si appoggia</b><br/>" + self.gli_si_appoggia, styNormal)

        # 24 row
        scavato = Paragraph("<b>Scavato</b><br/>" + self.scavato, styNormal)
        anno_di_scavo = Paragraph("<b>Anno di scavo</b><br/>" + self.anno_scavo, styNormal)
        metodo_di_scavo = Paragraph("<b>Metodo di scavo</b><br/>" + self.metodo_di_scavo, styNormal)
        data_schedatura = Paragraph("<b>Data schedatura</b><br/>" + self.data_schedatura, styNormal)
        schedatore = Paragraph("<b>Schedatore</b><br/>" + self.schedatore, styNormal)

        # 25 row
        sing_doc = self.documentazione_print
        self.documentazione_print = Paragraph("<b>Documentazione</b><br/>" + sing_doc, styNormal)

        # schema
        cell_schema = [
            # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],  # 0 row ok
            [sito, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 1 row ok
            [area, '01', '02', '03', '04', us, '06', '07', '08', '09'],  # 2 row ok
            [d_stratigrafica, '01', '02', '03', '04', d_interpretativa, '06', '07', '08', '09'],  # 3 row ok
            [stato_conservazione, '01', '02', consistenza, '04', '05', colore, '07', '08', '09'],  # 4 row ok
            [inclusi, '01', '02', '03', campioni, '05', '06', '07', formazione, '09'],  # 5 row ok
            [descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 6row ok
            [interpretazione, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 7 row ok
            [attivita, '01', '02', struttura, '04', '05', quota_min, '07', quota_max, '09'],  # 8 row
            [usm_section, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 9 row
            [settore, '01', '02', quadrato, '04', '05', ambiente, '07', saggio, '09'],  # 10 row
            [elem_datanti, '01', '02', funz_statica, '04', '05', lavorazione, '07', spess_giunti, '09'],  # 11 row
            [letti_posa, '01', '02', alt_modulo, '04', '05', un_ed_riass, '07', reimp, '09'],  # 12 row
            [posa_opera, '01', '02', quota_min_usm, '04', '05', quota_max_usm, '07', '08', '09'],  # 13 row
            [col_legante, '01', '02', aggreg_legante, '04', '05', con_text_mat, '07', col_mat, '09'],  # 14 row
            [inclusi_mat_usm, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 15 row
            [periodizzazione, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 16row
            [iniziale, '01', periodo_iniziale, '03', fase_iniziale, finale, '06', periodo_finale, '08', fase_finale],
            # 17 row
            [rapporti_stratigrafici, '01', '02', '03', '04', piante, '06', '07', '08', '09'],  # 18 row
            [si_lega_a, '01', '02', '03', '04', uguale_a, '06', '07', '08', '09'],  # 19 row
            [copre, '01', '02', '03', '04', coperto_da, '06', '07', '08', '09'],  # 20 row
            [riempie, '01', '02', '03', '04', riempito_da, '06', '07', '08', '09'],  # 21 row
            [taglia, '01', '02', '03', '04', tagliato_da, '06', '07', '08', '09'],  # 22 row
            [si_appoggia_a, '01', '02', '03', '04', gli_si_appoggia, '06', '07', '08', '09'],  # 23 row
            [self.documentazione_print, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 24 row
            [scavato, anno_di_scavo, '02', metodo_di_scavo, '04', data_schedatura, '06', schedatore, '08', '09']
            # 25row
        ]

        # table style
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row
            ('SPAN', (0, 0), (6, 0)),  # intestazione
            ('SPAN', (7, 0), (9, 0)),  # intestazione

            # 1 row
            ('SPAN', (0, 1), (9, 1)),  # dati identificativi

            # 2 row
            ('SPAN', (0, 2), (4, 2)),  # dati identificativi
            ('SPAN', (5, 2), (9, 2)),  # dati identificativi

            # 3 row
            ('SPAN', (0, 3), (4, 3)),  # Definizione - interpretazone
            ('SPAN', (5, 3), (9, 3)),  # definizione - intepretazione

            # 3 row
            ('SPAN', (0, 4), (2, 4)),  # conservazione - consistenza - colore
            ('SPAN', (3, 4), (5, 4)),  # conservazione - consistenza - colore
            ('SPAN', (6, 4), (9, 4)),  # conservazione - consistenza - colore

            # 4 row
            ('SPAN', (0, 5), (3, 5)),  # inclusi - campioni - formazione
            ('SPAN', (4, 5), (7, 5)),  # inclusi - campioni - formazione
            ('SPAN', (8, 5), (9, 5)),  # inclusi - campioni - formazione

            # 6 row
            ('SPAN', (0, 6), (9, 6)),  # descrizione

            # 7 row
            ('SPAN', (0, 7), (9, 7)),  # interpretazione #6 row
            ('VALIGN', (0, 6), (9, 6), 'TOP'),

            # 8 row
            ('SPAN', (0, 8), (2, 8)),  # Attivita - Struttura - Quota min - Quota max
            ('SPAN', (3, 8), (5, 8)),  # Attivita - Struttura - Quota min - Quota max
            ('SPAN', (6, 8), (7, 8)),  # Attivita - Struttura - Quota min - Quota max
            ('SPAN', (8, 8), (9, 8)),  # Attivita - Struttura - Quota min - Quota max

            ('SPAN', (0, 9), (9, 9)),  # USM

            # 10 row
            ('SPAN', (0, 10), (2, 10)),
            ('SPAN', (3, 10), (5, 10)),
            ('SPAN', (6, 10), (7, 10)),
            ('SPAN', (8, 10), (9, 10)),

            # 11 row
            ('SPAN', (0, 11), (2, 11)),
            ('SPAN', (3, 11), (5, 11)),
            ('SPAN', (6, 11), (7, 11)),
            ('SPAN', (8, 11), (9, 11)),

            # 12 row
            ('SPAN', (0, 12), (2, 12)),
            ('SPAN', (3, 12), (5, 12)),
            ('SPAN', (6, 12), (7, 12)),
            ('SPAN', (8, 12), (9, 12)),

            # 13row
            ('SPAN', (0, 13), (2, 13)),
            ('SPAN', (3, 13), (5, 13)),
            ('SPAN', (6, 13), (9, 13)),

            # 14 row
            ('SPAN', (0, 14), (2, 14)),
            ('SPAN', (3, 14), (5, 14)),
            ('SPAN', (6, 14), (7, 14)),
            ('SPAN', (8, 14), (9, 14)),

            # 15 row

            ('SPAN', (0, 15), (9, 15)),  # Periodizzazione - Titolo

            # 16 row
            ('SPAN', (0, 16), (9, 16)),  # Periodizzazione - Titolo

            # 17 row
            ('SPAN', (0, 17), (1, 17)),  # iniziale
            ('SPAN', (2, 17), (3, 17)),  # periodo inizlae
            ('SPAN', (5, 17), (6, 17)),  # fase iniziale
            ('SPAN', (7, 17), (8, 17)),  # finale
            ('VALIGN', (0, 17), (0, 17), 'TOP'),
            ('VALIGN', (5, 17), (5, 17), 'TOP'),

            # 18row
            ('SPAN', (0, 18), (4, 18)),  # Rapporti stratigrafici - Titolo
            ('SPAN', (5, 18), (9, 18)),  # Piante - Titolo

            # 19 row
            ('SPAN', (0, 19), (4, 19)),  # Rapporti stratigrafici - Si lega a - Uguale a
            ('SPAN', (5, 19), (9, 19)),  # Rapporti stratigrafici - Si lega a - Uguale a

            # 20 row
            ('SPAN', (0, 20), (4, 20)),  # Rapporti stratigrafici - Copre - Coperto da
            ('SPAN', (5, 20), (9, 20)),  # Rapporti stratigrafici - Copre - Coperto da

            # 21 row
            ('SPAN', (0, 21), (4, 21)),  # Rapporti stratigrafici - Riempie - Riempito da
            ('SPAN', (5, 21), (9, 21)),  # Rapporti stratigrafici - Riempie - Riempito da

            # 22 row
            ('SPAN', (0, 22), (4, 22)),  # Rapporti stratigrafici - Taglia - Tagliato da
            ('SPAN', (5, 22), (9, 22)),  # Rapporti stratigrafici - Taglia - Tagliato da

            # 23 row
            ('SPAN', (0, 23), (4, 23)),  # Rapporti stratigrafici - Si appoggia a - Gli si appoggia
            ('SPAN', (5, 23), (9, 23)),  # Rapporti stratigrafici - Si appoggia a - Gli si appoggia

            ('VALIGN', (0, 0), (-1, -1), 'TOP'),

            # 24 row
            ('SPAN', (0, 24), (9, 24)),  # pie' di pagina
            ('ALIGN', (0, 24), (9, 24), 'CENTER'),

            # 25 row
            ('SPAN', (1, 25), (2, 25)),  # scavato anno_di_scavo - metodo_di_scavo, data_schedatura
            ('SPAN', (3, 25), (4, 25)),  # scavato anno_di_scavo - metodo_di_scavo, data_schedatura
            ('SPAN', (5, 25), (6, 25)),  # scavato anno_di_scavo - metodo_di_scavo, data_schedatura
            ('SPAN', (7, 25), (9, 25)),  # scavato anno_di_scavo - metodo_di_scavo, data_schedatura
        ]

        t = Table(cell_schema, colWidths=55, rowHeights=None, style=table_style)

        return t


    def create_sheet_archeo3_usm_fields(self):  #scheda USM in stile pyArchInit
        self.unzip_rapporti_stratigrafici()
        self.unzip_documentazione()

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT

        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.alignment = 4  # Justified

        #format labels

        #0 row Intestazione + logo
        intestazione = Paragraph("<b>SCHEDA DI UNITA' STRATIGRAFICA<br/>" + str(self.datestrfdate()) + "</b>",
                                 styNormal)
        # intestazione2 = Paragraph("<b>Pyarchinit</b><br/>https://sites.google.com/site/pyarchinit/", styNormal)

        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path)

        ##if test_image.drawWidth < 800:

        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch

        #1 row Nome del sito (si consiglia di lasciarlo così a se stante per la lunghezza dei nomi in alcuni casi
        sito = Paragraph("<b>Sito</b><br/>" + str(self.sito), styNormal)

        area = "<b>Area: </b>" + str(self.area)
        unita_tipo_label = "<br/><b>" + str(self.unita_tipo) + ": </b>"
        us = Paragraph(area + unita_tipo_label + str(self.us), styNormal)

        #2 row Soprintenza - nr catalogo generale - nr catalogo interno n cataologo internazione
        sabap_data  = Paragraph("<b>Soprintendenza</b><br/>" + str(self.soprintendenza) +
                                "<b>N. Catalogo generale</b><br/>" + str(self.n_catalogo_generale) +
                                "<b>N. Catalogo interno</b><br/>" + str(self.n_catalogo_interno) +
                                "<b>N. Catalogo internazionale</b><br/>" + str(self.n_catalogo_internazionale),
                                styNormal)

        #3 row
        d_stratigrafica = Paragraph("<b>Definizione stratigrafica</b><br/>" + self.d_stratigrafica, styNormal)
        d_interpretativa = Paragraph("<b>Definizione Interpretativa</b><br/>" + self.d_interpretativa, styNormal)

        # 4 row
        settore = Paragraph("<b>Settore</b><br/>" + self.settore, styNormal)
        quadrato = Paragraph("<b>Quadrato/Parete</b><br/>" + self.quad_par, styNormal)
        ambiente = Paragraph("<b>Ambiente</b><br/>" + self.ambient, styNormal)
        saggio = Paragraph("<b>Saggio</b><br/>" + self.saggio, styNormal)

        # 5 row
        stato_conservazione = Paragraph("<b>Conservazione</b><br/>" + self.stato_di_conservazione, styNormal)
        consistenza = Paragraph("<b>Consistenza</b><br/>" + self.consistenza, styNormal)
        colore = Paragraph("<b>Colore</b><br/>" + self.colore, styNormal)
        formazione = Paragraph("<b>Formazione</b><br/>" + self.formazione, styNormal)
        modo_formazione = Paragraph("<b>Modo formazione</b><br/>" + self.modo_formazione, styNormal)


        # 6 row
        posizione = Paragraph("<b>Posizione</b>" + self.posizione, styNormal)
        criteri_distinzione = Paragraph("<b>Criteri distinzione</b><br/>" + self.criteri_distinzione, styNormal)
        flottazione = Paragraph("<b>Flottazione</b><br/>" + self.flottazione, styNormal)
        setacciatura = Paragraph("<b>Setacciatura</b><br/>" + self.setacciatura, styNormal)
        affidabilita = Paragraph("<b>Affidabilita</b><br/>" + self.affidabilita, styNormal)


        # 7 row
        comp_organici = Paragraph("<b>Comp. organici</b><br/>" + self.componenti_organici, styNormal)
        comp_inorganici = Paragraph("<b>Comp. inorganici</b><br/>" + self.componenti_inorganici, styNormal)
        inclusi_list = eval(self.inclusi)
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
        inclusi = Paragraph("<b>Inclusi</b><br/>" + inclusi, styNormal)

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
        campioni = Paragraph("<b>Campioni</b><br/>" + campioni, styNormal)

        # 8 row
        descrizione = ''
        try:
            descrizione = Paragraph("<b>Descrizione</b><br/>" + self.descrizione, styDescrizione)
        except:
            pass

        # 9 row
        interpretazione = ''
        try:
            interpretazione = Paragraph("<b>Interpretazione</b><br/>" + self.interpretazione, styDescrizione)
        except:
            pass

        # 10 row
        elementi_datanti = ''
        try:
            elementi_datanti = Paragraph("<b>Elementi datanti</b><br/>" + self.elem_datanti, styDescrizione)
        except:
            pass

        # 11 row
        osservazioni = ''
        try:
            osservazioni = Paragraph("<b>Osservazioni</b><br/>" + self.osservazioni, styDescrizione)
        except:
            pass

        # 12 row
        attivita = Paragraph("<b>Attivita'</b><br/>" + self.attivita, styNormal)
        struttura = Paragraph("<b>Struttura</b><br/>" + self.struttura, styNormal)
        quota_min = Paragraph("<b>Quota Min:</b><br/>" + self.quota_min, styNormal)
        quota_max = Paragraph("<b>Quota Max:</b><br/>" + self.quota_max, styNormal)

        # 13 row
        usm_section = Paragraph("<b>DATI USM</b>", styNormal)

        # 14 row
        funz_statica = Paragraph("<b>Funz. Statica</b><br/>" + self.funz_statica, styNormal)
        lavorazione = Paragraph("<b>Lavorazione</b><br/>" + self.lavorazione, styNormal)
        spess_giunti = Paragraph("<b>Spessore giunti</b><br/>" + self.spess_giunti, styNormal)
        letti_posa = Paragraph("<b>Letti posa</b><br/>" + self.letti_posa, styNormal)
        alt_modulo = Paragraph("<b>Alt. modulo</b><br/>" + self.alt_mod, styNormal)

        #15 row
        un_ed_riass = Paragraph("<b>Unita Ed. Riass</b><br/>" + self.un_ed_riass, styNormal)
        uso_primario = Paragraph("<b>Uso primario</b><br/>" + self.uso_primario_usm, styNormal)
        reimp = Paragraph("<b>Reimpiego</b><br/>" + self.reimp, styNormal)
        posa_opera = Paragraph("<b>Posa in opera</b><br/>" + self.posa_opera, styNormal)
        tecnica_muraria = Paragraph("<b>Tecnica</b><br/>" + self.tecnica_muraria_usm, styNormal)

        # 16 row
        col_legante_usm = ''
        for i in eval(self.col_legante):
            if col_legante_usm == '':
                try:
                    col_legante_usm += str(i[0])
                except:
                    pass
            else:
                try:
                    col_legante_usm += ', ' + str(i[0])
                except:
                    pass
        col_legante_usm = Paragraph("<b>Colore legante usm</b><br/>" + col_legante_usm, styNormal)

        cons_legante = Paragraph("<b>Cons. legante:</b><br/>" + self.cons_legante, styNormal)


        #block
        con_text_mat_usm = ''
        for i in eval(self.con_text_mat):
            if con_text_mat_usm == '':
                try:
                    con_text_mat_usm += str(i[0])
                except:
                    pass
            else:
                try:
                    con_text_mat_usm += ', ' + str(i[0])
                except:
                    pass
        con_text_mat_usm = Paragraph("<b>Consiste/texture materiale usm</b><br/>" + con_text_mat_usm, styNormal)
        #/block

        #block
        col_mat_usm = ''
        for i in eval(self.col_materiale):
            if col_mat_usm == '':
                try:
                    col_mat_usm += str(i[0])
                except:
                    pass
            else:
                try:
                    col_mat_usm += ', ' + str(i[0])
                except:
                    pass
        col_mat_usm = Paragraph("<b>Colore materiale</b><br/>" + col_mat_usm, styNormal)
        #/block

        # 17 row
        inclusi_materiali_usm_list = eval(self.inclusi_materiali_usm)
        inclusi_materiali_usm = ''
        for i in eval(self.inclusi_materiali_usm):
            if inclusi_materiali_usm == '':
                try:
                    inclusi_materiali_usm += str(i[0])
                except:
                    pass
            else:
                try:
                    inclusi_materiali_usm += ', ' + str(i[0])
                except:
                    pass
        inclusi_mat_usm = Paragraph("<b>Inclusi materiale usm</b><br/>" + inclusi_materiali_usm, styNormal)

        # 18 row
        aggreg_legante_usm_list = eval(self.aggreg_legante)
        aggreg_legante_usm = ''
        for i in eval(self.aggreg_legante):
            if aggreg_legante_usm == '':
                try:
                    aggreg_legante_usm += str(i[0])
                except:
                    pass
            else:
                try:
                    aggreg_legante_usm += ', ' + str(i[0])
                except:
                    pass
        aggreg_legante_usm = Paragraph("<b>Inclusi aggreganti legante usm</b><br/>" + aggreg_legante_usm, styNormal)

        # 19 row
        campioni_malta = Paragraph("<b>Campioni malta</b><br/>" + self.campioni_malta_usm, styNormal)
        campioni_pietra = Paragraph("<b>Campioni pietra</b><br/>" + self.campioni_pietra_usm, styNormal)
        campioni_mattone = Paragraph("<b>Campioni mattone</b><br/>" + self.campioni_mattone_usm, styNormal)

        # 20 row
        quota_min_usm = Paragraph("<b>Quota Min.</b><br/>" + self.quota_min_usm, styNormal)
        quota_max_usm = Paragraph("<b>Quota Max.</b><br/>" + self.quota_max_usm, styNormal)
        spessore_usm = Paragraph("<b>Spessore</b><br/>" + self.spessore_usm, styNormal)
        lunghezza_usm =  Paragraph("<b>Lunghezza usm</b><br/>" + self.lunghezza_usm, styNormal)
        altezza_usm = Paragraph("<b>Altezza usm</b><br/>" + self.altezza_usm, styNormal)

        # 21 row
        periodizzazione = Paragraph("<b>PERIODIZZAZIONE</b>", styNormal)
        datazione_ipotesi = Paragraph("<b>datazione ipotesi</b><br/>" + str(self.datazione), styNormal)

        # 22 row
        iniziale = Paragraph("<b>INIZIALE</b>", styNormal)
        periodo_iniziale = Paragraph("<b>Periodo</b><br/>" + self.periodo_iniziale, styNormal)
        fase_iniziale = Paragraph("<b>Fase</b><br/>" + self.fase_iniziale, styNormal)
        finale = Paragraph("<b>FINALE</b>", styNormal)
        periodo_finale = Paragraph("<b>Periodo</b><br/>" + self.periodo_finale, styNormal)
        fase_finale = Paragraph("<b>Fase</b><br/>" + self.fase_finale, styNormal)

        # 23 row
        rapporti_stratigrafici = Paragraph("<b>RAPPORTI STRATIGRAFICI</b>", styNormal)
        piante = Paragraph("<b>Tipo pianta</b><br/>" + self.piante, styNormal)

        # 24 row
        si_lega_a = Paragraph("<b>Si lega a</b><br/>" + self.si_lega_a, styNormal)
        uguale_a = Paragraph("<b>Uguale a</b><br/>" + self.uguale_a, styNormal)

        # 25 row
        copre = Paragraph("<b>Copre</b><br/>" + self.copre, styNormal)
        coperto_da = Paragraph("<b>Coperto da</b><br/>" + self.coperto_da, styNormal)

        # 26 row
        riempie = Paragraph("<b>Riempie</b><br/>" + self.riempie, styNormal)
        riempito_da = Paragraph("<b>Riempito da</b><br/>" + self.riempito_da, styNormal)

        # 27 row
        taglia = Paragraph("<b>Taglia</b><br/>" + self.taglia, styNormal)
        tagliato_da = Paragraph("<b>Tagliato da</b><br/>" + self.tagliato_da, styNormal)

        # 28 row
        si_appoggia_a = Paragraph("<b>Si appoggia a</b><br/>" + self.si_appoggia_a, styNormal)
        gli_si_appoggia = Paragraph("<b>Gli si appoggia</b><br/>" + self.gli_si_appoggia, styNormal)

        # 29 row
        sing_doc = self.documentazione_print
        self.documentazione_print = Paragraph("<b>Documentazione</b><br/>" + str(sing_doc), styNormal)

        # 30 row
        scavato = Paragraph("<b>Scavato</b><br/>" + self.scavato, styNormal)
        anno_di_scavo = Paragraph("<b>Anno di scavo</b><br/>" + self.anno_scavo, styNormal)
        metodo_di_scavo = Paragraph("<b>Metodo di scavo</b><br/>" + self.metodo_di_scavo, styNormal)
        data_schedatura = Paragraph("<b>Data schedatura</b><br/>" + self.data_schedatura, styNormal)
        schedatore = Paragraph("<b>Schedatore</b><br/>" + self.schedatore, styNormal)

        # 31 row
        data_rilevazione = Paragraph("<b>Rilevazione</b><br/>" + self.data_rilevazione, styNormal)
        data_rielaborazione = Paragraph("<b>Rielaborazione</b><br/>" + self.data_rielaborazione, styNormal)
        direttore_us     = Paragraph("<b>Direttore us</b><br/>" + self.direttore_us, styNormal)
        responsabile_us = Paragraph("<b>Responsabile us</b><br/>" + self.responsabile_us, styNormal)
        cod_ente_schedatore = Paragraph("<b>Cod. Ente Schedatore</b><br/>" + self.cod_ente_schedatore, styNormal)

        # 32 row
        ref_tm = Paragraph("<b>Scavato</b><br/>" + self.scavato, styNormal)
        ref_n = Paragraph("<b>Anno di scavo</b><br/>" + self.anno_scavo, styNormal)
        ref_ra = Paragraph("<b>Metodo di scavo</b><br/>" + self.metodo_di_scavo, styNormal)


        # schema
        cell_schema = [
            # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],                                       # 0 row ok intestazione e logo archeo 3
            [sito, '01', '02', '03', '04', '05', '06', '07', '08', us],                                                 # 1 row ok sito e numero di us archeo 3
            [sabap_data, '01', '02', '03', '04', '05', '06', '07', '08', '09'],                                         # 2 row ok dati sabap ok archeo 3
            [d_stratigrafica, '01', '02', '03', '04', d_interpretativa, '06', '07', '08', '09'],                        # 3 row def stratigrafiche e interpretate
            [settore, '01', quadrato, '03', ambiente, '05', saggio, '07', '08', '09'],                                  # 4 row ok settore quadrato ambiente saggio archeo 3
            [stato_conservazione, '01', consistenza, '03', colore, '05',formazione , '07', modo_formazione, '09'],      # 5 row ok  stato_conservazione, consistenza, colore, formazione, modo_formazione
            [posizione, '01', criteri_distinzione, '03', flottazione, '05',setacciatura , '07', affidabilita, '09'],    # 6 row ok  posizione, criteri_distinzione, flottazione, setacciatura, affidabilita
            [comp_organici, '01', comp_inorganici, '03', inclusi, '05', '06', campioni,'08', '09'],                     # 7 row ok  comp_organici, comp_inorganici, inclusi, campioni
            [descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09'],                                        # 8 row ok  descrizione
            [interpretazione, '01', '02', '03', '04', '05', '06', '07', '08', '09'],                                    # 9 row ok  interpretazione
            [elementi_datanti, '01', '02', '03', '04', '05', '06', '07', '08', '09'],                                   # 10 row ok  elementi datanti
            [osservazioni, '01', '02', '03', '04', '05', '06', '07', '08', '09'],                                       # 11 row ok  osservazioni
            [attivita, '01', '02', struttura, '04', '05', quota_min, '07', quota_max, '09'],                            # 12 row ok attivita struttura quota min quota max
            [usm_section, '01', '02', '03', '04', '05', '06', '07', '08', '09'],                                        # 13 row ok USM section intestazione
            [funz_statica, '01', lavorazione, '03', spess_giunti, '05', letti_posa, '07', alt_modulo, '09'],            # 14 row ok funz statica, lavorazione, spess_giunti, letti_posa, alt_modulo
            [un_ed_riass, '01', uso_primario, '03', reimp, '05', posa_opera, '07', tecnica_muraria, '09'],              # 15 row ok un_ed_riass, uso_primario, reimpiego, posa_opera, tec_muraria
            [col_legante_usm, '01', '02', cons_legante, '04', '05', con_text_mat_usm, '07', col_mat_usm, '09'],         # 16 row ok col legante, cons_legante, cont text mat, col mat
            [inclusi_mat_usm, '01', '02', '03', '04', '05', '06', '07', '08', '09'],                                    # 17 row ok inclusi_materiale
            [aggreg_legante_usm, '01', '02', '03', '04', '05', '06', '07', '08', '09'],                                 # 18 row ok aggreg_legante_usm
            [campioni_malta, '01', '02', campioni_pietra, '04', '05', campioni_mattone, '07', '08', '09'],              # 19 row ok campioni pietra, campioni malta, campioni mattone
            [quota_min_usm, '01', quota_max_usm, '03', spessore_usm, '05', lunghezza_usm, '07', altezza_usm, '09' ],    # 20 row quota min usm, quota max usm, spessore, lugnhezza, altezza
            [periodizzazione, '01', '02', '03', '04', '05', datazione_ipotesi, '07', '08', '09' ],                      # 21 row periodizzazione, ipotesi datazione
            [iniziale, '01', periodo_iniziale, '03', fase_iniziale, finale, '06', periodo_finale, '08', fase_finale],   # 22 row periodi
            [rapporti_stratigrafici, '01', '02', '03', '04', piante, '06', '07', '08', '09'],                           # 23 row
            [si_lega_a, '01', '02', '03', '04', uguale_a, '06', '07', '08', '09'],                                      # 24 row
            [copre, '01', '02', '03', '04', coperto_da, '06', '07', '08', '09'],                                        # 25 row
            [riempie, '01', '02', '03', '04', riempito_da, '06', '07', '08', '09'],                                     # 26 row
            [taglia, '01', '02', '03', '04', tagliato_da, '06', '07', '08', '09'],                                      # 27 row
            [si_appoggia_a, '01', '02', '03', '04', gli_si_appoggia, '06', '07', '08', '09'],                           # 28 row
            [self.documentazione_print, '01', '02', '03', '04', '05', '06', '07', '08', '09'],                          # 29 row
            [scavato, anno_di_scavo, '02', metodo_di_scavo, '04', data_schedatura, '06', schedatore, '08', '09'],       # 30 row scavato, anno scavo, metodo scavo, data schedatura, schedatore
            [data_rilevazione, '01', data_rielaborazione, '03', direttore_us, '05', responsabile_us, '07', cod_ente_schedatore, '09'],  # 31 row data_rilevazione, '01', data_rielaborazione, '03', direttore_us, '05', responsabile_us, '07', cod_ente_schedatore, '09']
            [ref_tm, '01', ref_n, '03', ref_ra, '05', '06', '07', '08', '09']                                           # 31 row ref tm, ref n, ref ra
            ]

        # table style
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row OK archeo 3
            ('SPAN', (0, 0), (6, 0)),  # intestazione
            ('SPAN', (7, 0), (9, 0)),  # intestazione

            # 1 row   ok archeo 3
            ('SPAN', (0, 1), (8, 1)),  # dati identificativi
            ('SPAN', (9, 1), (9, 1)),  # dati identificativi

            # 2 row ok archeo 3
            ('SPAN', (0, 2), (9, 2)),  # dati identificativi

            # 3 row ok archeo 3
            ('SPAN', (0, 3), (4, 3)),  # Definizione - interpretazone
            ('SPAN', (5, 3), (9, 3)),  # definizione - intepretazione

            # 4 row  ok archeo 3 settore quadrato ambiente saggio
            ('SPAN', (0, 4), (1, 4)),  #
            ('SPAN', (2, 4), (3, 4)),  #
            ('SPAN', (4, 4), (5, 4)),  #
            ('SPAN', (6, 4), (9, 4)),  #

            # 5 row ok archeo 3 stato di conservazione consistenza colore formazione modo formazione
            ('SPAN', (0, 5), (1, 5)),  #
            ('SPAN', (2, 5), (3, 5)),  #
            ('SPAN', (4, 5), (5, 5)),  #
            ('SPAN', (6, 5), (7, 5)),  #
            ('SPAN', (8, 5), (9, 5)),  #

            # 6 row ok archeo 3 posizione, criteri_distinzione, flottazione, setacciatura, affidabilita
            ('SPAN', (0, 6), (1, 6)),  #
            ('SPAN', (2, 6), (3, 6)),  #
            ('SPAN', (4, 6), (5, 6)),  #
            ('SPAN', (6, 6), (7, 6)),  #
            ('SPAN', (8, 6), (9, 6)),  #


            # 7 row  ok archeo 3  [comp_organici, '01', comp_inorganici, '03', inclusi, '05', '06', campioni, '08', '09'],
            ('SPAN', (0, 7), (1, 7)),  #
            ('SPAN', (2, 7), (3, 7)),  #
            ('SPAN', (4, 7), (6, 7)),  #
            ('SPAN', (7, 7), (9, 7)),  #

            # 8 row ok archeo 3
            ('SPAN', (0, 8), (9, 8)),  # descrizione
            ('VALIGN', (0, 8), (9, 8), 'TOP'),

            # 9 row ok archeo 3
            ('SPAN', (0, 9), (9, 9)),  # interpretazione
            ('VALIGN', (0, 9), (9, 9), 'TOP'),

            # 10 row ok archeo 3
            ('SPAN', (0, 10), (9, 10)),  # elementi datanti
            ('VALIGN', (0, 10), (9, 10), 'TOP'),

            # 11 row ok archeo 3
            ('SPAN', (0, 11), (9, 11)),  # osservazioni
            ('VALIGN', (0, 11), (9, 11), 'TOP'),

            # 12 row archeo 3  # Attivita - Struttura - Quota min - Quota max
            ('SPAN', (0, 12), (2, 12)),
            ('SPAN', (3, 12), (5, 12)),
            ('SPAN', (6, 12), (7, 12)),
            ('SPAN', (8, 12), (9, 12)),

            # 13 row archeo 3  # Aintestazione USM
            ('SPAN', (0, 13), (9, 13)),

            # 14 row ok archeo 3 funz_statica, lavorazione, spess_giunti, letti_posa, alt_modulo
            ('SPAN', (0, 14), (1, 14)),  #
            ('SPAN', (2, 14), (3, 14)),  #
            ('SPAN', (4, 14), (5, 14)),  #
            ('SPAN', (6, 14), (7, 14)),  #
            ('SPAN', (8, 14), (9, 14)),  #

            # 15 row ok archeo 3 un_ed_riass, uso_primario, reimpiego, posa_opera, tec_muraria
            ('SPAN', (0, 15), (1, 15)),  #
            ('SPAN', (2, 15), (3, 15)),  #
            ('SPAN', (4, 15), (5, 15)),  #
            ('SPAN', (6, 15), (7, 15)),  #
            ('SPAN', (8, 15), (9, 15)),  #

            #16 row ok col legante, cons_legante, cont text mat, col mat
            ('SPAN', (0, 16), (2, 16)),
            ('SPAN', (3, 16), (5, 16)),
            ('SPAN', (6, 16), (7, 16)),
            ('SPAN', (8, 16), (9, 16)),

            # 17 row ok archeo 3 inclusi materiale
            ('SPAN', (0, 17), (9, 17)),

            # 18 row ok archeo 3 inclusi aggreg legante
            ('SPAN', (0, 18), (9, 18)),

            # 19 row ok archeo 3 campioni pietra, campioni malta, campioni mattone
            ('SPAN', (0, 19), (2, 19)),
            ('SPAN', (3, 19), (5, 19)),
            ('SPAN', (6, 19), (9, 19)),

            #20 row quota min usm, quota max usm, spessore, lugnhezza, altezza
            ('SPAN', (0, 20), (1, 20)),  #
            ('SPAN', (2, 20), (3, 20)),  #
            ('SPAN', (4, 20), (5, 20)),  #
            ('SPAN', (6, 20), (7, 20)),  #
            ('SPAN', (8, 20), (9, 20)),  #

            # 21 row ok archeo 3 periodizzazione ipotesi_datazione
            ('SPAN', (0, 21), (5, 21)),  #
            ('SPAN', (6, 21), (9, 21)),  #

            # 22 row ok archeo e periodi iniziale e finale
            ('SPAN', (0, 22), (1, 22)),  # iniziale
            ('SPAN', (2, 22), (3, 22)),  # periodo inizlae
            ('SPAN', (4, 22), (4, 22)),  # periodo inizlae
            ('SPAN', (5, 22), (6, 22)),  # fase iniziale
            ('SPAN', (7, 22), (8, 22)),  # finale
            ('SPAN', (9, 22), (9, 22)),  # finale
            ('VALIGN', (0, 22), (0, 22), 'TOP'),
            ('VALIGN', (5, 22), (5, 22), 'TOP'),

            # 23 row ok archeo 3
            ('SPAN', (0, 23), (4, 23)),  # Rapporti stratigrafici - Titolo
            ('SPAN', (5, 23), (9, 23)),  # Piante - Titolo

            # 24 row ok archeo 3
            ('SPAN', (0, 24), (4, 24)),  # Rapporti stratigrafici - Si lega a - Uguale a
            ('SPAN', (5, 24), (9, 24)),  # Rapporti stratigrafici - Si lega a - Uguale a

            # 25 row ok archeo 3
            ('SPAN', (0, 25), (4, 25)),  # Rapporti stratigrafici - Copre - Coperto da
            ('SPAN', (5, 25), (9, 25)),  # Rapporti stratigrafici - Copre - Coperto da

            # 26 row ok archeo 3
            ('SPAN', (0, 26), (4, 26)),  # Rapporti stratigrafici - Riempie - Riempito da
            ('SPAN', (5, 26), (9, 26)),  # Rapporti stratigrafici - Riempie - Riempito da

            # 27 row ok archeo 3
            ('SPAN', (0, 27), (4, 27)),  # Rapporti stratigrafici - Taglia - Tagliato da
            ('SPAN', (5, 27), (9, 27)),  # Rapporti stratigrafici - Taglia - Tagliato da

            # 28 row
            ('SPAN', (0, 28), (4, 28)),  # Rapporti stratigrafici - Si appoggia a - Gli si appoggia
            ('SPAN', (5, 28), (9, 28)),  # Rapporti stratigrafici - Si appoggia a - Gli si appoggia

            ('VALIGN', (0, 0), (-1, -1), 'TOP'),

            # 29 row Documentazione
            ('SPAN', (0, 29), (9, 29)),  # pie' di pagina
            ('ALIGN', (0, 29), (9, 29), 'CENTER'),

            # 30 row ok archeo 3 scavato, anno scavo, metodo scavo, data schedatura, schedatore
            ('SPAN', (0, 30), (0, 30)),
            ('SPAN', (1, 30), (2, 30)),
            ('SPAN', (3, 30), (4, 30)),
            ('SPAN', (5, 30), (6, 30)),
            ('SPAN', (7, 30), (9, 30)),


            # 31 row ok archeo 3 data_rilevazione, '01', data_rielaborazione, '03', direttore_us, '05', responsabile_us, cod_ente_schedatore, '09'
            ('SPAN', (0, 31), (1, 31)),
            ('SPAN', (2, 31), (3, 31)),
            ('SPAN', (4, 31), (5, 31)),
            ('SPAN', (6, 31), (7, 31)),
            ('SPAN', (8, 31), (9, 31)),


            # 32 row ok archeo 3 ref_tm, '01', ref_n, '03', ref_ra,
            ('SPAN', (0, 32), (1, 32)),
            ('SPAN', (2, 32), (3, 32)),
            ('SPAN', (4, 32), (9, 32))
        ]

        t = Table(cell_schema, colWidths=55, rowHeights=None, style=table_style)

        return t

    #SCHEDA US TIPO ICCD
    def create_sheet_archeo3_usm_fields_2(self): #scheda us in stile ICCD Italiano
        self.unzip_rapporti_stratigrafici()
        self.unzip_documentazione()

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.fontSize = 6
        styNormal.alignment = 0  # LEFT


        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.fontSize = 6
        styDescrizione.alignment = 4  # Justified

        styleSheet = getSampleStyleSheet()
        styUnitaTipo = styleSheet['Normal']
        styUnitaTipo.spaceBefore = 20
        styUnitaTipo.spaceAfter = 20
        styUnitaTipo.fontSize = 14
        styUnitaTipo.alignment = 1  # CENTER

        styleSheet = getSampleStyleSheet()
        styTitoloComponenti = styleSheet['Normal']
        styTitoloComponenti.spaceBefore = 20
        styTitoloComponenti.spaceAfter = 20
        styTitoloComponenti.fontSize = 6
        styTitoloComponenti.alignment = 1  # CENTER

        styleSheet = getSampleStyleSheet()
        styVerticale = styleSheet['Normal']
        styVerticale.spaceBefore = 20
        styVerticale.spaceAfter = 20
        styVerticale.fontSize = 6
        styVerticale.alignment = 1  # CENTER
        styVerticale.leading=8

        #format labels

        #0-1 row Unita tipo, logo, n. catalogo generale, n. catalogo internazionale
        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path)

        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch

        unita_tipo = Paragraph(str(self.unita_tipo), styUnitaTipo)
        label_catalogo_generale = Paragraph("<b>N. CATALOGO GENERALE</b>", styNormal)
        label_catalogo_internazionale = Paragraph("<b>N. CATALOGO INTERNAZIONALE</b>", styNormal)
        catalogo_generale = Paragraph(str(self.n_catalogo_generale), styNormal)
        catalogo_internazionale = Paragraph(str(self.n_catalogo_internazionale), styNormal)
        sop =  Paragraph("<b></b><br/>" +str(self.soprintendenza), styNormal)
        #2-3 row

        sito = Paragraph("<b>LOCALITÀ</b><br/>" + str(self.sito), styNormal)
        anno_di_scavo = Paragraph("<b>ANNO</b><br/>" + self.anno_scavo, styNormal)
        area = Paragraph("<b>AREA</b><br/>" + str(self.area),styNormal)
        settore = Paragraph("<b>SETTORE/I</b><br/>" + self.settore, styNormal)
        quadrato = Paragraph("<b>QUADRATO/I</b><br/>" + self.quad_par, styNormal)
        quote = Paragraph("<b>QUOTE</b><br/>min: " + self.quota_min + "<br/>max: "+self.quota_max, styNormal)
        label_unita_stratigrafica = Paragraph("<b>UNITÀ STRATIGRAFICA</b><br/>"+ str(self.us), styNormal)
        
        
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
        foto = Paragraph("<b>FOTO</b><br/>"+ self.foto_iccd, styNormal)            #manca valore

        tabelle_materiali = Paragraph("<b>TABELLE MATERIALI<br/><br/>RA</b>:"+ self.ref_ra, styNormal)  #manca valore

        #5 row

        d_stratigrafica = Paragraph("<b>DEFINIZIONE</b><br/>Definizione stratigrafica: " + self.d_stratigrafica+"<br/>Definizione interpretativa: "+self.d_interpretativa, styNormal)

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

        label_componenti = Paragraph("<b>COMPONENTI</b>",styVerticale)

        label_geologici = Paragraph("<i>GEOLOGICI</i>",styTitoloComponenti) #inorganici
        label_organici = Paragraph("<i>ORGANICI</i>", styTitoloComponenti) #organici
        label_artificiali = Paragraph("<i>ARTIFICIALI</i>", styTitoloComponenti) #inclusi

        comp_organici = Paragraph(organici, styNormal) #organici
        comp_inorganici = Paragraph(inorganici, styNormal)  #geologici
        inclusi = Paragraph(inclusi, styNormal)  #artificiali

        #10 row

        consistenza = Paragraph("<b>CONSISTENZA</b><br/>" + self.consistenza, styNormal)
        colore = Paragraph("<b>COLORE</b><br/>" + self.colore, styNormal)
        misure = Paragraph("<b>MISURE</b><br/>", styNormal)                 # manca valore

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

        affidabilita = Paragraph("<b>AFFIDABILITÀ</b><br/>" + self.affidabilita, styNormal)
        direttore = Paragraph("<b>DIRETTORE</b><br/>" + self.direttore_us, styNormal)
        responsabile = Paragraph("<b>RESPONSABILE</b><br/>" + self.responsabile_us, styNormal)

        # schema
        cell_schema = [
            # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [unita_tipo, '01' , label_catalogo_generale, '03', '04', '05', '06', label_catalogo_internazionale , '08', '09', '10', '11', '12', logo , '14', '15', '16', '17'],
            ['00', '01', catalogo_generale, '03', '04' , '05', '06', catalogo_internazionale , '08', '09', '10', '11', '12', sop, '14', '15', '16', '17'],
            [sito, '01', '02', '03', '04', anno_di_scavo , area, settore, '08', quadrato, '10', quote, '12', '13', label_unita_stratigrafica, '15', '16', '17'],
            ['00', '01', '02', '03', '04', '05','06' , '07', '08', '09', '10', '11', '12', '13', label_NAT, '15', label_ART, '17'],    #
            [piante, '01', '02', sezioni, '04', '05', prospetti, '07', '08', foto, '10', '11', '12', '13', tabelle_materiali, '15', '16', '17'],
            [d_stratigrafica, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [criteri_distinzione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [modo_formazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [label_componenti, label_geologici, '02', '03', '04', '05', label_organici, '07', '08', '09', '10', '11', label_artificiali, '13', '14', '15', '16', '17'],
            ['00', comp_inorganici, '02', '03', '04', '05', comp_organici, '07', '08', '09', '10', '11', inclusi, '13', '14', '15', '16', '17'],
            [consistenza, '01', '02', '03', '04', '05', colore, '07', '08', '09', '10', '11', misure, '13', '14', '15', '16', '17'],
            [stato_conservazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
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
            [osservazioni, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [interpretazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [elementi_datanti, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [datazione_ipotesi, '01', '02', '03', '04', '05', '06', '07', '08', periodo_o_fase, '10', '11', '12', '13', '14', '15', '16', '17'],
            [dati_quantitativi, '01', '02', '03', '04', '05', '06', '07', '08', periodo_o_fase, '10', '11', '12', '13', '14', '15', '16', '17'],
            [campioni, '01', '02', '03', '04', '05', flottazione, '07', '08', '09', '10', '11', setacciatura, '13', '14', '15', '16', '17'],
            [affidabilita, '01', '02', '03', '04', '05', direttore, '07', '08', '09', '10', '11', responsabile, '13', '14', '15', '16', '17'],
            ]

        # table style
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row

            ('SPAN', (0, 0), (1, 1)),  # unita tipo
            ('VALIGN', (0, 0), (1, 1), 'MIDDLE'),

            ('SPAN', (2, 0), (6, 1)),  # label n. catalogo generale
            ('SPAN', (7, 0), (12, 1)),  # label n. catalogo internazionale
            ('VALIGN', (2, 0), (12,1), 'MIDDLE'),

            # 1 row
            ('SPAN', (2, 1), (6, 1)),  # n. catalogo generale
            ('SPAN', (7, 1), (12, 1)),  # catalogo internazionale
            ('SPAN', (13, 1), (17, 1)),
            ('SPAN', (13, 0), (17, 0)),  # logo
            ('ALIGN', (13, 0), (17, 0), 'CENTER'),
            ('VALIGN', (13, 0), (17, 0), 'MIDDLE'),

            # 2-3 row
            ('SPAN', (0, 2), (4, 3)),  # sito
            ('SPAN', (5, 2), (5, 3)),  # anno di scavo
            ('SPAN', (6, 2), (6, 3)),  # area
            ('SPAN', (7, 2), (8, 3)),  # settore
            ('SPAN', (9, 2), (10, 3)),  # quadrato
            ('SPAN', (11, 2), (13, 3)),  # quote
            ('SPAN', (14, 2), (17, 2)),  # label unita stratigrafica
            ('SPAN', (14, 3), (15, 3)),  # label NAT
            ('SPAN', (16, 3), (17, 3)),  # label ART
            #('VALIGN', (0, 2), (17, 3), 'TOP'),

            # 4 row
            ('SPAN', (0, 4), (2, 4)),  # piante
            ('SPAN', (3, 4), (5, 4)),  # sezioni
            ('SPAN', (6, 4), (8, 4)),  # prospetti
            ('SPAN', (9, 4), (13, 4)),  # foto
            ('SPAN', (14, 4), (17, 4)),  # tabelle materiali
            #('VALIGN', (0, 4), (17, 4), 'TOP'),

            # 5 row
            ('SPAN', (0, 5), (17, 5)),  # definizione
            #('VALIGN', (0, 5), (17, 5), 'TOP'),

            # 6 row
            ('SPAN', (0, 6), (17, 6)),  # criteri di distinzione
            #('VALIGN', (0, 6), (17, 6), 'TOP'),

            # 7 row
            ('SPAN', (0, 7), (17, 7)),  # modo di formazione
            #('VALIGN', (0, 7), (17, 7), 'TOP'),

            # 8-9 row
            ('SPAN', (0, 8), (0, 9)),  # label componenti
            ('SPAN', (1, 8), (5, 9)),  # label geologici
            ('SPAN', (6, 8), (11, 9)),  # label organici
            ('SPAN', (12, 8), (17, 9)),  # label artificiali
            ('SPAN', (1, 9), (5, 9)),  #  geologici
            ('SPAN', (6, 9), (11, 9)),  #  organici
            ('SPAN', (12, 9), (17, 9)),  #  artificiali
            #('VALIGN', (0, 8), (17, 9), 'TOP'),

            # 10 row
            ('SPAN', (0, 10), (5, 10)),  # consistenza
            ('SPAN', (6, 10), (11, 10)),  # colore
            ('SPAN', (12, 10), (17, 10)),  # misure
            #('VALIGN', (0, 10), (17, 10), 'TOP'),

            # 11 row
            ('SPAN', (0, 11), (17, 11)),  # stato di conservazione
            #('VALIGN', (0, 11), (17, 11), 'TOP'),

            # 12 row
            ('SPAN', (0, 12), (17, 12)),  # descrizione
            #('VALIGN', (0, 12), (17, 12), 'TOP'),

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
            #('VALIGN', (0, 13), (17, 22), 'TOP'),

            # 23 row
            ('SPAN', (0, 23), (17, 23)),  # osservazioni
            #('VALIGN', (0, 23), (17, 23), 'TOP'),

            # 24 row
            ('SPAN', (0, 24), (17, 24)),  # interpretazione
            #('VALIGN', (0, 24), (17, 24), 'TOP'),

            # 25 row

            ('SPAN', (0, 25), (17, 25)),  # elementi datanti
            #('VALIGN', (0, 25), (17, 25), 'TOP'),

            #26 row

            ('SPAN', (0, 26), (8, 26)),  # datazione
            ('SPAN', (9, 26), (17, 26)),  # periodo o fase
            #('VALIGN', (0, 26), (17, 26), 'TOP'),

            #27 row

            ('SPAN', (0, 27), (17, 27)),  # dati quantitativi dei reperti
            #('VALIGN', (0, 27), (17, 27), 'TOP'),

            #28 row
            ('SPAN', (0, 28), (5, 28)),  # campionature
            ('SPAN', (6, 28), (11, 28)),  # flottazione
            ('SPAN', (12, 28), (17, 28)),  # setacciatura
            #('VALIGN', (0, 28), (17, 28), 'TOP'),

            #29 row
            ('SPAN', (0, 29), (5, 29)),  # affidabilita stratigrafica
            ('SPAN', (6, 29), (11, 29)),  # direttore
            ('SPAN', (12, 29), (17, 29)),  # responsabile
            #('VALIGN', (0, 29), (17, 29), 'TOP'),

            ('VALIGN', (0, 2), (17, 29), 'TOP'),
        ]

        colWidths = (15,30,30,30,30,30,30,30,30,30,30,30,20,30,30,30,30,30)
        rowHeights = None

        t = Table(cell_schema, colWidths=colWidths, rowHeights=rowHeights, style=table_style)

        return t

        
        
        
    def create_sheet_en(self):
        self.unzip_rapporti_stratigrafici_en()
        self.unzip_documentazione()

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.fontSize = 6
        styNormal.alignment = 0  # LEFT


        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.fontSize = 6
        styDescrizione.alignment = 4  # Justified

        styleSheet = getSampleStyleSheet()
        styUnitaTipo = styleSheet['Normal']
        styUnitaTipo.spaceBefore = 20
        styUnitaTipo.spaceAfter = 20
        styUnitaTipo.fontSize = 14
        styUnitaTipo.alignment = 1  # CENTER

        styleSheet = getSampleStyleSheet()
        styTitoloComponenti = styleSheet['Normal']
        styTitoloComponenti.spaceBefore = 20
        styTitoloComponenti.spaceAfter = 20
        styTitoloComponenti.fontSize = 6
        styTitoloComponenti.alignment = 1  # CENTER

        styleSheet = getSampleStyleSheet()
        styVerticale = styleSheet['Normal']
        styVerticale.spaceBefore = 20
        styVerticale.spaceAfter = 20
        styVerticale.fontSize = 6
        styVerticale.alignment = 1  # CENTER
        styVerticale.leading=8

        #format labels

        #0-1 row Unita tipo, logo, n. catalogo generale, n. catalogo internazionale
        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path)

        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch

        unita_tipo = Paragraph(str(self.unita_tipo), styUnitaTipo)
        label_catalogo_generale = Paragraph("<b>N. GENERAL CATALOG</b>", styNormal)
        label_catalogo_internazionale = Paragraph("<b>N. INTERNATIONAL CATALOG</b>", styNormal)
        catalogo_generale = Paragraph(str(self.n_catalogo_generale), styNormal)
        catalogo_internazionale = Paragraph(str(self.n_catalogo_internazionale), styNormal)
        sop =  Paragraph("<b></b><br/>" +str(self.soprintendenza), styNormal)
        #2-3 row

        sito = Paragraph("<b>SITE</b><br/>" + str(self.sito), styNormal)
        anno_di_scavo = Paragraph("<b>YEAR</b><br/>" + self.anno_scavo, styNormal)
        area = Paragraph("<b>AREA</b><br/>" + str(self.area),styNormal)
        settore = Paragraph("<b>SECTORS</b><br/>" + self.settore, styNormal)
        quadrato = Paragraph("<b>SQUARE</b><br/>" + self.quad_par, styNormal)
        quote = Paragraph("<b>ELEVATION</b><br/>min: " + self.quota_min + "<br/>max: "+self.quota_max, styNormal)
        label_unita_stratigrafica = Paragraph("<b>STRATIGRAPHIC UNIT</b><br/>"+ str(self.us), styNormal)
        
        if self.formazione== 'Natural':
            label_NAT = Paragraph("<i>NAT.</i><br/>" + self.formazione, styNormal)
            label_ART = Paragraph("<i>ART.</i>",  styNormal) 
        elif self.formazione== 'Artificial':
            label_NAT = Paragraph("<i>NAT.</i>", styNormal)
            label_ART = Paragraph("<i>ART.</i><br/>"+ self.formazione, styNormal)
        elif self.formazione !='Natural' or 'Artificial':    
            label_NAT = Paragraph("<i>NAT.</i><br/>", styNormal)
            label_ART = Paragraph("<i>ART.</i>",  styNormal) 
        #4 row

        piante = Paragraph("<b>MAP</b><br/>" + self.piante, styNormal)
        sezioni = Paragraph("<b>SECTION</b><br/>", styNormal)                 #manca valore
        prospetti = Paragraph("<b>PROFILE</b><br/>", styNormal)             #manca valore
        foto = Paragraph("<b>PHOTO</b><br/>B/W:<br/>Digital:", styNormal)     #manca valore
        tabelle_materiali = Paragraph("<b>ARTEFACT TABLE<br/><br/>RA</b>:", styNormal)  #manca valore

        #5 row

        d_stratigrafica = Paragraph("<b>DEFINITION</b><br/>STRATIGRAPHIC DEFINITION: " + self.d_stratigrafica+"<br/>INTERPRETATION: "+self.d_interpretativa, styNormal)

        #6 row

        criteri_distinzione = Paragraph("<b>CRITERIA FOR DISTINCTION</b><br/>" + self.criteri_distinzione, styNormal)

        #7 row

        modo_formazione = Paragraph("<b>FORMATION MODE</b><br/>" + self.modo_formazione, styNormal)

        #8-9 row

        organici, inorganici= self.unzip_componenti()

        label_componenti = Paragraph("<b>COMPONENTS</b>",styVerticale)
        label_geologici = Paragraph("<i>GEOLOGIC</i>",styTitoloComponenti)
        label_organici = Paragraph("<i>ORGANIC</i>", styTitoloComponenti)
        label_artificiali = Paragraph("<i>ARTIFICIAL</i>", styTitoloComponenti)
        comp_organici = Paragraph(organici, styNormal)
        comp_inorganici = Paragraph(inorganici, styNormal)  #geologici? artificiali?

        #10 row

        consistenza = Paragraph("<b>TEXTURE</b><br/>" + self.consistenza, styNormal)
        colore = Paragraph("<b>COLOR</b><br/>" + self.colore, styNormal)
        misure = Paragraph("<b>MEASURES</b><br/>", styNormal)                 # manca valore

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

        posteriore_a = Paragraph("<b>POSTERIOR TO</b><br/>"+ self.copre +"<br/>" + self.riempie +"<br/>"+  self.taglia+ "<br/>" +   self.si_appoggia_a, styNormal)               # manca valore
        anteriore_a = Paragraph("<b>ANTERIOR TO</b><br/>"+ self.coperto_da +"<br/>"+  self.riempito_da +"<br/>"+ self.tagliato_da +  "<br/>" + self.gli_si_appoggia, styNormal)                 # manca valore

        #23 row

        osservazioni = Paragraph("<b>OBSERVATION</b><br/>" + self.osservazioni, styDescrizione)

        #24 row

        interpretazione = Paragraph("<b>INTERACTION</b><br/>" + self.interpretazione, styDescrizione)

        #25 row

        elementi_datanti = Paragraph("<b>DATA ELEMNTS</b><br/>" + self.elem_datanti, styDescrizione)

        #26 row

        datazione_ipotesi = Paragraph("<b>DATATION</b><br/>" + str(self.datazione), styNormal)
        periodo_o_fase = Paragraph("<b>PERIOD OR PHASE</b><br/>Beginning Period: "+self.periodo_iniziale+"<br/>Beginning Phase: "+self.fase_iniziale+"<br/>Final Period: "+self.periodo_finale+"<br/>Finale Phase: "+self.fase_finale, styNormal)

        #27 row

        dati_quantitativi = Paragraph("<b>QUANTITATIVE DATA OF THE ARTIFACTS</b><br/>", styNormal)  # manca valore

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
        campioni = Paragraph("<b>SAMPLES</b><br/>" + campioni, styNormal)
        flottazione = Paragraph("<b>FLOTATION</b><br/>" + self.flottazione, styNormal)
        setacciatura = Paragraph("<b>SETTED</b><br/>" + self.setacciatura, styNormal)

        #28 row

        affidabilita = Paragraph("<b>RELIABILITY</b><br/>" + self.affidabilita, styNormal)
        direttore = Paragraph("<b>DIRECTOR</b><br/>" + self.direttore_us, styNormal)
        responsabile = Paragraph("<b>RESPONSIBLE</b><br/>" + self.responsabile_us, styNormal)

        # schema
        cell_schema = [
            # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [unita_tipo, '01' , label_catalogo_generale, '03', '04', '05', '06', label_catalogo_internazionale , '08', '09', '10', '11', '12', logo , '14', '15', '16', '17'],
            ['00', '01', catalogo_generale, '03', '04' , '05', '06', catalogo_internazionale , '08', '09', '10', '11', '12', sop, '14', '15', '16', '17'],
            [sito, '01', '02', '03', '04', anno_di_scavo , area, settore, '08', quadrato, '10', quote, '12', '13', label_unita_stratigrafica, '15', '16', '17'],
            #['00', '01', '02', '03', '04', '05','06' , '07', '08', '09', '10', '11', '12', '13', label_NAT, '15', label_ART, '17'],    #
            [piante, '01', '02', sezioni, '04', '05', prospetti, '07', '08', foto, '10', '11', '12', '13', tabelle_materiali, '15', '16', '17'],
            [d_stratigrafica, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [criteri_distinzione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [modo_formazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [label_componenti, label_geologici, '02', '03', '04', '05', label_organici, '07', '08', '09', '10', '11', label_artificiali, '13', '14', '15', '16', '17'],
            ['00', comp_inorganici, '02', '03', '04', '05', comp_organici, '07', '08', '09', '10', '11', comp_inorganici, '13', '14', '15', '16', '17'],
            [consistenza, '01', '02', '03', '04', '05', colore, '07', '08', '09', '10', '11', misure, '13', '14', '15', '16', '17'],
            [stato_conservazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
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
            [osservazioni, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [interpretazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [elementi_datanti, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [datazione_ipotesi, '01', '02', '03', '04', '05', '06', '07', '08', periodo_o_fase, '10', '11', '12', '13', '14', '15', '16', '17'],
            [dati_quantitativi, '01', '02', '03', '04', '05', '06', '07', '08', periodo_o_fase, '10', '11', '12', '13', '14', '15', '16', '17'],
            [campioni, '01', '02', '03', '04', '05', flottazione, '07', '08', '09', '10', '11', setacciatura, '13', '14', '15', '16', '17'],
            [affidabilita, '01', '02', '03', '04', '05', direttore, '07', '08', '09', '10', '11', responsabile, '13', '14', '15', '16', '17'],
            ]

        # table style
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row

            ('SPAN', (0, 0), (1, 1)),  # unita tipo
            ('VALIGN', (0, 0), (1, 1), 'MIDDLE'),

            ('SPAN', (2, 0), (6, 1)),  # label n. catalogo generale
            ('SPAN', (7, 0), (12, 1)),  # label n. catalogo internazionale
            ('VALIGN', (2, 0), (12,1), 'MIDDLE'),

            # 1 row
            ('SPAN', (2, 1), (6, 1)),  # n. catalogo generale
            ('SPAN', (7, 1), (12, 1)),  # catalogo internazionale
            ('SPAN', (13, 1), (17, 1)),
            ('SPAN', (13, 0), (17, 0)),  # logo
            ('ALIGN', (13, 0), (17, 0), 'CENTER'),
            ('VALIGN', (13, 0), (17, 0), 'MIDDLE'),

            # 2-3 row
            ('SPAN', (0, 2), (4, 3)),  # sito
            ('SPAN', (5, 2), (5, 3)),  # anno di scavo
            ('SPAN', (6, 2), (6, 3)),  # area
            ('SPAN', (7, 2), (8, 3)),  # settore
            ('SPAN', (9, 2), (10, 3)),  # quadrato
            ('SPAN', (11, 2), (13, 3)),  # quote
            ('SPAN', (14, 2), (17, 2)),  # label unita stratigrafica
            ('SPAN', (14, 3), (15, 3)),  # label NAT
            ('SPAN', (16, 3), (17, 3)),  # label ART
            #('VALIGN', (0, 2), (17, 3), 'TOP'),

            # 4 row
            ('SPAN', (0, 4), (2, 4)),  # piante
            ('SPAN', (3, 4), (5, 4)),  # sezioni
            ('SPAN', (6, 4), (8, 4)),  # prospetti
            ('SPAN', (9, 4), (13, 4)),  # foto
            ('SPAN', (14, 4), (17, 4)),  # tabelle materiali
            #('VALIGN', (0, 4), (17, 4), 'TOP'),

            # 5 row
            ('SPAN', (0, 5), (17, 5)),  # definizione
            #('VALIGN', (0, 5), (17, 5), 'TOP'),

            # 6 row
            ('SPAN', (0, 6), (17, 6)),  # criteri di distinzione
            #('VALIGN', (0, 6), (17, 6), 'TOP'),

            # 7 row
            ('SPAN', (0, 7), (17, 7)),  # modo di formazione
            #('VALIGN', (0, 7), (17, 7), 'TOP'),

            # 8-9 row
            ('SPAN', (0, 8), (0, 9)),  # label componenti
            ('SPAN', (1, 8), (5, 9)),  # label geologici
            ('SPAN', (6, 8), (11, 9)),  # label organici
            ('SPAN', (12, 8), (17, 9)),  # label artificiali
            ('SPAN', (1, 9), (5, 9)),  #  geologici
            ('SPAN', (6, 9), (11, 9)),  #  organici
            ('SPAN', (12, 9), (17, 9)),  #  artificiali
            #('VALIGN', (0, 8), (17, 9), 'TOP'),

            # 10 row
            ('SPAN', (0, 10), (5, 10)),  # consistenza
            ('SPAN', (6, 10), (11, 10)),  # colore
            ('SPAN', (12, 10), (17, 10)),  # misure
            #('VALIGN', (0, 10), (17, 10), 'TOP'),

            # 11 row
            ('SPAN', (0, 11), (17, 11)),  # stato di conservazione
            #('VALIGN', (0, 11), (17, 11), 'TOP'),

            # 12 row
            ('SPAN', (0, 12), (17, 12)),  # descrizione
            #('VALIGN', (0, 12), (17, 12), 'TOP'),

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
            #('VALIGN', (0, 13), (17, 22), 'TOP'),

            # 23 row
            ('SPAN', (0, 23), (17, 23)),  # osservazioni
            #('VALIGN', (0, 23), (17, 23), 'TOP'),

            # 24 row
            ('SPAN', (0, 24), (17, 24)),  # interpretazione
            #('VALIGN', (0, 24), (17, 24), 'TOP'),

            # 25 row

            ('SPAN', (0, 25), (17, 25)),  # elementi datanti
            #('VALIGN', (0, 25), (17, 25), 'TOP'),

            #26 row

            ('SPAN', (0, 26), (8, 26)),  # datazione
            ('SPAN', (9, 26), (17, 26)),  # periodo o fase
            #('VALIGN', (0, 26), (17, 26), 'TOP'),

            #27 row

            ('SPAN', (0, 27), (17, 27)),  # dati quantitativi dei reperti
            #('VALIGN', (0, 27), (17, 27), 'TOP'),

            #28 row
            ('SPAN', (0, 28), (5, 28)),  # campionature
            ('SPAN', (6, 28), (11, 28)),  # flottazione
            ('SPAN', (12, 28), (17, 28)),  # setacciatura
            #('VALIGN', (0, 28), (17, 28), 'TOP'),

            #29 row
            ('SPAN', (0, 29), (5, 29)),  # affidabilita stratigrafica
            ('SPAN', (6, 29), (11, 29)),  # direttore
            ('SPAN', (12, 29), (17, 29)),  # responsabile
            #('VALIGN', (0, 29), (17, 29), 'TOP'),

            ('VALIGN', (0, 2), (17, 29), 'TOP'),
        ]

        colWidths = (15,30,30,30,30,30,30,30,30,30,30,30,20,30,30,30,30,30)
        rowHeights = None

        t = Table(cell_schema, colWidths=colWidths, rowHeights=rowHeights, style=table_style)

        return t
        
    def create_sheet_de(self):
        self.unzip_rapporti_stratigrafici_de()
        self.unzip_documentazione()

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.fontSize = 6
        styNormal.alignment = 0  # LEFT


        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.fontSize = 6
        styDescrizione.alignment = 4  # Justified

        styleSheet = getSampleStyleSheet()
        styUnitaTipo = styleSheet['Normal']
        styUnitaTipo.spaceBefore = 20
        styUnitaTipo.spaceAfter = 20
        styUnitaTipo.fontSize = 14
        styUnitaTipo.alignment = 1  # CENTER

        styleSheet = getSampleStyleSheet()
        styTitoloComponenti = styleSheet['Normal']
        styTitoloComponenti.spaceBefore = 20
        styTitoloComponenti.spaceAfter = 20
        styTitoloComponenti.fontSize = 6
        styTitoloComponenti.alignment = 1  # CENTER

        styleSheet = getSampleStyleSheet()
        styVerticale = styleSheet['Normal']
        styVerticale.spaceBefore = 20
        styVerticale.spaceAfter = 20
        styVerticale.fontSize = 6
        styVerticale.alignment = 1  # CENTER
        styVerticale.leading=8

        #format labels

        #0-1 row Unita tipo, logo, n. catalogo generale, n. catalogo internazionale
        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo_de.jpg')
        logo = Image(logo_path)

        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch

        unita_tipo = Paragraph(str(self.unita_tipo), styUnitaTipo)
        label_catalogo_generale = Paragraph("<b>ALLGEMEINE KATALOGNUMMER</b>", styNormal)
        label_catalogo_internazionale = Paragraph("<b>INTERNATIONALE KATALOGNUMMER</b>", styNormal)
        catalogo_generale = Paragraph(str(self.n_catalogo_generale), styNormal)
        catalogo_internazionale = Paragraph(str(self.n_catalogo_internazionale), styNormal)
        sop = Paragraph(str(self.sopreintendenza), styNormal)
        #2-3 row

        sito = Paragraph("<b>ORT</b><br/>" + str(self.sito), styNormal)
        anno_di_scavo = Paragraph("<b>JAHR</b><br/>" + self.anno_scavo, styNormal)
        area = Paragraph("<b>AREAL</b><br/>" + str(self.area),styNormal)
        settore = Paragraph("<b>SEKTOR</b><br/>" + self.settore, styNormal)
        quadrato = Paragraph("<b>QUADRAT</b><br/>" + self.quad_par, styNormal)
        quote = Paragraph("<b>NIVELLEMENTS</b><br/>min: " + self.quota_min + "<br/>max: "+self.quota_max, styNormal)
        label_unita_stratigrafica = Paragraph("<b>STRATIGRAFISCHE EINHEIT</b><br/>"+ str(self.us), styNormal)
        label_NAT = Paragraph("<i>NAT.</i>", styNormal)                       #manca valore
        label_ART = Paragraph("<i>KUN.</i>", styNormal)                       #manca valore

        #4 row

        piante = Paragraph("<b>PLANA</b><br/>" + self.piante, styNormal)
        sezioni = Paragraph("<b>PROFILE</b><br/>", styNormal)                 #manca valore
        prospetti = Paragraph("<b>ANSICHT</b><br/>", styNormal)             #manca valore
        foto = Paragraph("<b>FOTOS</b><br/>B/N:<br/>Digital:", styNormal)     #manca valore
        tabelle_materiali = Paragraph("<b>MATERIALTABELLEN<br/><br/>RA</b>:", styNormal)  #manca valore

        #5 row

        d_stratigrafica = Paragraph("<b>DEFINITION</b><br/>Stratigrafiche Definition: " + self.d_stratigrafica+"<br/>Interpretative Definition: "+self.d_interpretativa, styNormal)

        #6 row

        criteri_distinzione = Paragraph("<b>UNTERSCHEIDUNGSKRITERIEN</b><br/>" + self.criteri_distinzione, styNormal)

        #7 row

        modo_formazione = Paragraph("<b>AUSBILDUNGSMODUS</b><br/>" + self.modo_formazione, styNormal)

        #8-9 row

        organici, inorganici= self.unzip_componenti()

        label_componenti = Paragraph("<b>KOMPONENTEN</b>",styVerticale)
        label_geologici = Paragraph("<i>GEOLOGISCHE</i>",styTitoloComponenti)
        label_organici = Paragraph("<i>ORGANISCHE</i>", styTitoloComponenti)
        label_artificiali = Paragraph("<i>ANTHROPOGENE</i>", styTitoloComponenti)
        comp_organici = Paragraph(organici, styNormal)
        comp_inorganici = Paragraph(inorganici, styNormal)  #geologici? artificiali?

        #10 row

        consistenza = Paragraph("<b>KONSISTENZ</b><br/>" + self.consistenza, styNormal)
        colore = Paragraph("<b>FARBE</b><br/>" + self.colore, styNormal)
        misure = Paragraph("<b>MESSUNGEN</b><br/>", styNormal)                 # manca valore

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

        
        
        
        label_sequenza_stratigrafica = Paragraph("<b>S<br/>T<br/>R<br/>A<br/>T<br/>I<br/>G<br/>R<br/>A<br/>F<br/>I<br/>S<br/>C<br/>H<br/>E<br/><br/<br/S<br/>E<br/>Q<br/>U<br/>E<br/>N<br/>C<br/>E</b>", styVerticale)

        posteriore_a = Paragraph("<b>VORZEITIG ZU</b><br/>"+ self.copre +"<br/>" + self.riempie +"<br/>"+  self.taglia+ "<br/>" +   self.si_appoggia_a, styNormal)               # manca valore
        anteriore_a = Paragraph("<b>NACHZEITIG ZU</b><br/>"+ self.coperto_da +"<br/>"+  self.riempito_da +"<br/>"+ self.tagliato_da +  "<br/>" + self.gli_si_appoggia, styNormal)                 # manca valore

        #23 row

        osservazioni = Paragraph("<b>BEOBACHTUNGEN</b><br/>" + self.osservazioni, styDescrizione)

        #24 row

        interpretazione = Paragraph("<b>INTERPRETATION</b><br/>" + self.interpretazione, styDescrizione)

        #25 row

        elementi_datanti = Paragraph("<b>DATIERENDE ELEMENTE</b><br/>" + self.elem_datanti, styDescrizione)

        #26 row

        datazione_ipotesi = Paragraph("<b>DATIERUNG</b><br/>" + str(self.datazione), styNormal)
        periodo_o_fase = Paragraph("<b>ZEITSTELLUNG ODER PHASE</b><br/>Anfangszeitstellung: "+self.periodo_iniziale+"<br/>Endzeitstellung: "+self.periodo_finale+"<br/>Anfangsphase:   "+self.fase_iniziale+"<br/>Endphase: "+self.fase_finale, styNormal)

        #27 row

        dati_quantitativi = Paragraph("<b>QUANTITATIVE DATEN DER FUNDE</b><br/>", styNormal)  # manca valore

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
        campioni = Paragraph("<b>PROBEN</b><br/>" + campioni, styNormal)
        flottazione = Paragraph("<b>FLOTATION</b><br/>" + self.flottazione, styNormal)
        setacciatura = Paragraph("<b>GESIEBT</b><br/>" + self.setacciatura, styNormal)

        #28 row

        affidabilita = Paragraph("<b>RELIABILITÄT</b><br/>" + self.affidabilita, styNormal)
        direttore = Paragraph("<b>PROJEKTLEITER</b><br/>" + self.direttore_us, styNormal)
        responsabile = Paragraph("<b>GRABUNGSLEITER</b><br/>" + self.responsabile_us, styNormal)

        # schema
        cell_schema = [
            # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [unita_tipo, '01' , label_catalogo_generale, '03', '04', '05', '06', label_catalogo_internazionale , '08', '09', '10', '11', '12', logo , '14', '15', '16', '17'],
            ['00', '01', catalogo_generale, '03', '04' , '05', '06', catalogo_internazionale , '08', '09', '10', '11', '12', sop, '14', '15', '16', '17'],
            [sito, '01', '02', '03', '04', anno_di_scavo , area, settore, '08', quadrato, '10', quote, '12', '13', label_unita_stratigrafica, '15', '16', '17'],
            ['00', '01', '02', '03', '04', '05','06' , '07', '08', '09', '10', '11', '12', '13', label_NAT, '15', label_ART, '17'],    #
            [piante, '01', '02', sezioni, '04', '05', prospetti, '07', '08', foto, '10', '11', '12', '13', tabelle_materiali, '15', '16', '17'],
            [d_stratigrafica, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [criteri_distinzione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [modo_formazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [label_componenti, label_geologici, '02', '03', '04', '05', label_organici, '07', '08', '09', '10', '11', label_artificiali, '13', '14', '15', '16', '17'],
            ['00', comp_inorganici, '02', '03', '04', '05', comp_organici, '07', '08', '09', '10', '11', comp_inorganici, '13', '14', '15', '16', '17'],
            [consistenza, '01', '02', '03', '04', '05', colore, '07', '08', '09', '10', '11', misure, '13', '14', '15', '16', '17'],
            [stato_conservazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
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
            [osservazioni, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [interpretazione, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [elementi_datanti, '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17'],
            [datazione_ipotesi, '01', '02', '03', '04', '05', '06', '07', '08', periodo_o_fase, '10', '11', '12', '13', '14', '15', '16', '17'],
            [dati_quantitativi, '01', '02', '03', '04', '05', '06', '07', '08', periodo_o_fase, '10', '11', '12', '13', '14', '15', '16', '17'],
            [campioni, '01', '02', '03', '04', '05', flottazione, '07', '08', '09', '10', '11', setacciatura, '13', '14', '15', '16', '17'],
            [affidabilita, '01', '02', '03', '04', '05', direttore, '07', '08', '09', '10', '11', responsabile, '13', '14', '15', '16', '17'],
            ]

        # table style
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row

            ('SPAN', (0, 0), (1, 1)),  # unita tipo
            ('VALIGN', (0, 0), (1, 1), 'MIDDLE'),

            ('SPAN', (2, 0), (6, 1)),  # label n. catalogo generale
            ('SPAN', (7, 0), (12, 1)),  # label n. catalogo internazionale
            ('VALIGN', (2, 0), (12,1), 'MIDDLE'),

            # 1 row
            ('SPAN', (2, 1), (6, 1)),  # n. catalogo generale
            ('SPAN', (7, 1), (12, 1)),  # catalogo internazionale
            ('SPAN', (13, 1), (17, 1)),
            ('SPAN', (13, 0), (17, 0)),  # logo
            ('ALIGN', (13, 0), (17, 0), 'CENTER'),
            ('VALIGN', (13, 0), (17, 0), 'MIDDLE'),

            # 2-3 row
            ('SPAN', (0, 2), (4, 3)),  # sito
            ('SPAN', (5, 2), (5, 3)),  # anno di scavo
            ('SPAN', (6, 2), (6, 3)),  # area
            ('SPAN', (7, 2), (8, 3)),  # settore
            ('SPAN', (9, 2), (10, 3)),  # quadrato
            ('SPAN', (11, 2), (13, 3)),  # quote
            ('SPAN', (14, 2), (17, 2)),  # label unita stratigrafica
            ('SPAN', (14, 3), (15, 3)),  # label NAT
            ('SPAN', (16, 3), (17, 3)),  # label ART
            #('VALIGN', (0, 2), (17, 3), 'TOP'),

            # 4 row
            ('SPAN', (0, 4), (2, 4)),  # piante
            ('SPAN', (3, 4), (5, 4)),  # sezioni
            ('SPAN', (6, 4), (8, 4)),  # prospetti
            ('SPAN', (9, 4), (13, 4)),  # foto
            ('SPAN', (14, 4), (17, 4)),  # tabelle materiali
            #('VALIGN', (0, 4), (17, 4), 'TOP'),

            # 5 row
            ('SPAN', (0, 5), (17, 5)),  # definizione
            #('VALIGN', (0, 5), (17, 5), 'TOP'),

            # 6 row
            ('SPAN', (0, 6), (17, 6)),  # criteri di distinzione
            #('VALIGN', (0, 6), (17, 6), 'TOP'),

            # 7 row
            ('SPAN', (0, 7), (17, 7)),  # modo di formazione
            #('VALIGN', (0, 7), (17, 7), 'TOP'),

            # 8-9 row
            ('SPAN', (0, 8), (0, 9)),  # label componenti
            ('SPAN', (1, 8), (5, 9)),  # label geologici
            ('SPAN', (6, 8), (11, 9)),  # label organici
            ('SPAN', (12, 8), (17, 9)),  # label artificiali
            ('SPAN', (1, 9), (5, 9)),  #  geologici
            ('SPAN', (6, 9), (11, 9)),  #  organici
            ('SPAN', (12, 9), (17, 9)),  #  artificiali
            #('VALIGN', (0, 8), (17, 9), 'TOP'),

            # 10 row
            ('SPAN', (0, 10), (5, 10)),  # consistenza
            ('SPAN', (6, 10), (11, 10)),  # colore
            ('SPAN', (12, 10), (17, 10)),  # misure
            #('VALIGN', (0, 10), (17, 10), 'TOP'),

            # 11 row
            ('SPAN', (0, 11), (17, 11)),  # stato di conservazione
            #('VALIGN', (0, 11), (17, 11), 'TOP'),

            # 12 row
            ('SPAN', (0, 12), (17, 12)),  # descrizione
            #('VALIGN', (0, 12), (17, 12), 'TOP'),

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
            #('VALIGN', (0, 13), (17, 22), 'TOP'),

            # 23 row
            ('SPAN', (0, 23), (17, 23)),  # osservazioni
            #('VALIGN', (0, 23), (17, 23), 'TOP'),

            # 24 row
            ('SPAN', (0, 24), (17, 24)),  # interpretazione
            #('VALIGN', (0, 24), (17, 24), 'TOP'),

            # 25 row

            ('SPAN', (0, 25), (17, 25)),  # elementi datanti
            #('VALIGN', (0, 25), (17, 25), 'TOP'),

            #26 row

            ('SPAN', (0, 26), (8, 26)),  # datazione
            ('SPAN', (9, 26), (17, 26)),  # periodo o fase
            #('VALIGN', (0, 26), (17, 26), 'TOP'),

            #27 row

            ('SPAN', (0, 27), (17, 27)),  # dati quantitativi dei reperti
            #('VALIGN', (0, 27), (17, 27), 'TOP'),

            #28 row
            ('SPAN', (0, 28), (5, 28)),  # campionature
            ('SPAN', (6, 28), (11, 28)),  # flottazione
            ('SPAN', (12, 28), (17, 28)),  # setacciatura
            #('VALIGN', (0, 28), (17, 28), 'TOP'),

            #29 row
            ('SPAN', (0, 29), (5, 29)),  # affidabilita stratigrafica
            ('SPAN', (6, 29), (11, 29)),  # direttore
            ('SPAN', (12, 29), (17, 29)),  # responsabile
            #('VALIGN', (0, 29), (17, 29), 'TOP'),

            ('VALIGN', (0, 2), (17, 29), 'TOP'),
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

        rapporti.sort()
        
        for rapporto in rapporti:
            if len(rapporto) == 2:
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

                if rapporto[0] == 'Gli si appoggia' or rapporto[0] == 'gli si appoggia a':
                    if self.gli_si_appoggia == '':
                        self.gli_si_appoggia += str(rapporto[1])
                    else:
                        self.gli_si_appoggia += ', ' + str(rapporto[1])



    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 6

        self.unzip_rapporti_stratigrafici()

        area = Paragraph("<b>Area</b><br/>" + str(self.area), styNormal)
        us = Paragraph("<b>US</b><br/>" + str(self.us), styNormal)
        d_stratigrafica = Paragraph("<b>Def. Stratigr.</b><br/>" + str(self.d_stratigrafica), styNormal)
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
    
    
    def getTable_en(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 6

        self.unzip_rapporti_stratigrafici_en()

        area = Paragraph("<b>Area</b><br/>" + str(self.area), styNormal)
        us = Paragraph("<b>SU</b><br/>" + str(self.us), styNormal)
        d_stratigrafica = Paragraph("<b>Def. Stratigr.</b><br/>" + str(self.d_stratigrafica), styNormal)
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
            if len(rapporto) == 2:
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
        styNormal.fontSize = 6

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
        styNormal.fontSize = 6

        

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
        styNormal.fontSize = 6

        

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

        elements_us_pyarchinit = []
        for i in range(len(records)):
            single_us_sheet = single_US_pdf_sheet(records[i])
            elements_us_pyarchinit.append(single_us_sheet.create_sheet())                       #prima versione scheda US
            elements_us_pyarchinit.append(PageBreak())                                          #prima versione scheda US

        elements_ususm_pyarchinit = []
        for i in range(len(records)):
            single_us_sheet = single_US_pdf_sheet(records[i])
            elements_ususm_pyarchinit.append(single_us_sheet.create_sheet_archeo3_usm_fields()) #seconda versione scheda US con USM
            elements_ususm_pyarchinit.append(PageBreak())                                       #seconda versione scheda US con USM

        elements_us_iccd = []
        for i in range(len(records)):
            single_us_sheet = single_US_pdf_sheet(records[i])
            elements_us_iccd.append(single_us_sheet.create_sheet_archeo3_usm_fields_2())        #terza versione scheda US SENZA CAMPI US formato Ministeriale ICCD
            elements_us_iccd.append(PageBreak())                                                #terza versione scheda US SENZA CAMPI US formato Ministeriale ICCD

        dt = datetime.datetime.now()

        #us
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        self.PDF_path, os.sep, 'scheda_US', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(elements_us_pyarchinit, canvasmaker=NumberedCanvas_USsheet)

        f.close()

        #ususm
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        self.PDF_path, os.sep, 'scheda_USUSM', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(elements_ususm_pyarchinit, canvasmaker=NumberedCanvas_USsheet)

        f.close()

        #usICCD
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        self.PDF_path, os.sep, 'scheda_USICCD', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(elements_us_iccd, canvasmaker=NumberedCanvas_USsheet)

        f.close()

    
    
    def build_US_sheets_en(self, records):

        elements = []
        for i in range(len(records)):
            single_us_sheet = single_US_pdf_sheet(records[i])
            #elements.append(single_us_sheet.create_sheet())
            #elements.append(PageBreak())
            #elements.append(single_us_sheet.create_sheet_archeo3_usm_fields())
            #elements.append(PageBreak())
            elements.append(single_us_sheet.create_sheet_en())
            elements.append(PageBreak())

        dt = datetime.datetime.now()
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        self.PDF_path, os.sep, 'SU_form', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(elements, canvasmaker=NumberedCanvas_USsheet)

        f.close()
    
    
    def build_US_sheets_de(self, records):

        elements = []
        for i in range(len(records)):
            single_us_sheet = single_US_pdf_sheet(records[i])
            #elements.append(single_us_sheet.create_sheet())
            #elements.append(PageBreak())
            #elements.append(single_us_sheet.create_sheet_archeo3_usm_fields())
            #elements.append(PageBreak())
            elements.append(single_us_sheet.create_sheet_de())
            elements.append(PageBreak())

        dt = datetime.datetime.now()
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        self.PDF_path, os.sep, 'SE_formular', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(elements, canvasmaker=NumberedCanvas_USsheet)

        f.close()
    
    def build_index_US(self, records, sito):
        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')

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
            Paragraph("<b>ELENCO UNITA' STRATIGRAFICHE</b><br/><b>Scavo: %s,  Data: %s</b>" % (sito, data), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = US_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable())

        styles = exp_index.makeStyles()
        colWidths = [28, 28, 120, 45, 58, 45, 58, 55, 64, 64, 52, 52, 52]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        lst.append(Spacer(0, 2))

        dt = datetime.datetime.now()
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        self.PDF_path, os.sep, 'elenco_us', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(29 * cm, 21 * cm), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_USindex)

        f.close()
        
    def build_index_Foto(self, records, sito):
        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        
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
            Paragraph("<b>ELENCO FOTO STRATIGRAFICHE</b><br/><b> Scavo: %s,  Data: %s</b>" % (sito, data), styH1))

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
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        self.PDF_path, os.sep, 'Elenco_foto', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(lst, canvasmaker=NumberedCanvas_USsheet)

        f.close()
    def build_index_Foto_2(self, records, sito):
        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        
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
            Paragraph("<b>ELENCO FOTO STRATIGRAFICHE</b><br/><b> Scavo: %s,  Data: %s</b>" % (sito, data), styH1))

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
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        self.PDF_path, os.sep, 'Elenco_foto', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.build(lst, canvasmaker=NumberedCanvas_USsheet)

        f.close()
        
    def build_index_US_en(self, records, sito):
        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')

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
            Paragraph("<b>LIST STRATIGRAPHIC UNIT</b><br/><b>Site: %s,  Data: %s</b>" % (sito, data), styH1))

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
        self.PDF_path, os.sep, 'SU_list', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(29 * cm, 21 * cm), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_USindex)

        f.close()
        
    def build_index_US_de(self, records, sito):
        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo_de.jpg')

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
            Paragraph("<b>LISTE STRATIGRAPHISCHE EINHEID</b><br/><b>Ausgrabungsstätte: %s,  Datum: %s</b>" % (sito, data), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = US_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable_de())

        styles = exp_index.makeStyles()
        colWidths = [35, 24, 120, 45, 58, 45, 58, 55, 64, 64, 52, 52, 52]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        lst.append(Spacer(0, 2))

        dt = datetime.datetime.now()
        filename = ('%s%s%s_%s_%s_%s_%s_%s_%s%s') % (
        self.PDF_path, os.sep, 'liste_SE', dt.day, dt.month, dt.year, dt.hour, dt.minute, dt.second, ".pdf")
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(29 * cm, 21 * cm), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_USindex)

        f.close()   
