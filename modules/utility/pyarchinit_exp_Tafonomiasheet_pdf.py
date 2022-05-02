
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

from datetime import date

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
pdfmetrics.registerFont(TTFont('cambriab', 'cambriab.ttf'))
pdfmetrics.registerFont(TTFont('VeraIt', 'VeraIt.ttf'))
pdfmetrics.registerFont(TTFont('VeraBI', 'VeraBI.ttf'))
# Registered fontfamily
registerFontFamily('Cambria',normal='Cambria')
from qgis.core import QgsSettings
from .pyarchinit_OS_utility import *
from ..db.pyarchinit_utility import Utility
from ..db.pyarchinit_conn_strings import Connection

class NumberedCanvas_TOMBAsheet(canvas.Canvas):
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


class NumberedCanvas_TOMBAindex(canvas.Canvas):
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


class Tomba_index_pdf_sheet(object):
    L=QgsSettings().value("locale/userLocale")[0:2]
    def __init__(self, data):
        self.nr_scheda_taf = data[1]
        self.sigla_struttura = data[2]
        self.nr_struttura = data[3]
        self.nr_individuo = data[4]
        self.rito = data[5]
        self.tipo_contenitore_resti = data[13]
        self.orientamento_asse = data[14]
        self.orientamento_azimut = data[15]
        self.corredo_presenza = data[16]
        self.completo_si_no = data[24]
        self.disturbato_si_no = data[25]
        self.in_connessione_si_no = data[26]
        self.periodo_iniziale = data[28]
        self.fase_iniziale = data[29]
        self.periodo_finale = data[30]
        self.fase_finale = data[31]
        self.datazione_estesa = data[32]

    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7
        styNormal.fontName='Cambria'
        # self.unzip_rapporti_stratigrafici()

        num_scheda = Paragraph("<b>N° Scheda</b><br/>" + str(self.nr_scheda_taf), styNormal)

        sigla_struttura = Paragraph("<b>Sigla Struttura</b><br/>" + str(self.sigla_struttura), styNormal)

        numero_struttura = Paragraph("<b>N° Struttura</b><br/>" + str(self.nr_struttura), styNormal)

        numero_individuo = Paragraph("<b>N° Individuo</b><br/>" + str(self.nr_individuo), styNormal)

        if self.rito == None:
            rito = Paragraph("<b>Rito</b><br/>", styNormal)
        else:
            rito = Paragraph("<b>Rito</b><br/>" + str(self.rito), styNormal)

        if self.tipo_contenitore_resti == None:
            tipo_contenitore_resti = Paragraph("<b>Tipo contenitore resti</b><br/>", styNormal)
        else:
            tipo_contenitore_resti = Paragraph("<b>Tipo contenitore resti</b><br/>" + str(self.tipo_contenitore_resti),
                                               styNormal)

        if self.orientamento_asse == None:
            orientamento_asse = Paragraph("<b>Orientamento asse</b><br/>", styNormal)
        else:
            orientamento_asse = Paragraph("<b>Orientamento asse</b><br/>" + str(self.orientamento_asse), styNormal)

        if self.orientamento_azimut == None:
            orientamento_azimut = Paragraph("<b>Azimut</b><br/>", styNormal)
        else:
            orientamento_azimut = Paragraph("<b>Azimut</b><br/>" + str(self.orientamento_azimut), styNormal)

        if self.corredo_presenza == None:
            corredo_presenza = Paragraph("<b>Corredo</b><br/>", styNormal)
        else:
            corredo_presenza = Paragraph("<b>Corredo</b><br/>" + self.corredo_presenza, styNormal)

        if self.completo_si_no == None:
            completo_si_no = Paragraph("<b>Completo</b><br/>", styNormal)
        else:
            completo_si_no = Paragraph("<b>Completo</b><br/>" + self.completo_si_no, styNormal)

        if self.disturbato_si_no == None:
            disturbato_si_no = Paragraph("<b>Disturbato</b><br/>", styNormal)
        else:
            disturbato_si_no = Paragraph("<b>Disturbato</b><br/>" + self.disturbato_si_no, styNormal)

        if self.in_connessione_si_no == None:
            connessione_si_no = Paragraph("<b>Connessione</b><br/>", styNormal)
        else:
            connessione_si_no = Paragraph("<b>Connessione</b><br/>" + self.in_connessione_si_no, styNormal)

        if self.periodo_iniziale == None:
            periodo_iniziale = Paragraph("<b>Periodo iniziale</b><br/>", styNormal)
        else:
            periodo_iniziale = Paragraph("<b>Periodo iniziale</b><br/>" + self.periodo_iniziale, styNormal)

        if self.fase_iniziale == None:
            fase_iniziale = Paragraph("<b>Fase inziale</b><br/>", styNormal)
        else:
            fase_iniziale = Paragraph("<b>Fase iniziale</b><br/>" + self.fase_iniziale, styNormal)

        if self.periodo_finale == None:
            periodo_finale = Paragraph("<b>Periodo finale</b><br/>", styNormal)
        else:
            periodo_finale = Paragraph("<b>Periodo finale</b><br/>" + self.periodo_finale, styNormal)

        if self.fase_finale == None:
            fase_finale = Paragraph("<b>Fase finale</b><br/>", styNormal)
        else:
            fase_finale = Paragraph("<b>Fase finale</b><br/>" + self.fase_finale, styNormal)

        if self.datazione_estesa == None:
            datazione_estesa = Paragraph("<b>Datazione</b><br/>", styNormal)
        else:
            datazione_estesa = Paragraph("<b>Datazione estesa</b><br/>" + self.datazione_estesa, styNormal)

        data = [num_scheda,
                sigla_struttura,
                numero_struttura,
                numero_individuo,
                rito,
                corredo_presenza,
                completo_si_no,
                periodo_iniziale,
                fase_iniziale,
                periodo_finale,
                fase_finale]

        return data
    def getTable_de(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7

        # self.unzip_rapporti_stratigrafici()

        num_scheda = Paragraph("<b>N° Feld</b><br/>" + str(self.nr_scheda_taf), styNormal)

        sigla_struttura = Paragraph("<b>Strukturcode</b><br/>" + str(self.sigla_struttura), styNormal)

        numero_struttura = Paragraph("<b>Nr struktur</b><br/>" + str(self.nr_struttura), styNormal)

        numero_individuo = Paragraph("<b>Nr Individuel</b><br/>" + str(self.nr_individuo), styNormal)

        if self.rito == None:
            rito = Paragraph("<b>Ritus</b><br/>", styNormal)
        else:
            rito = Paragraph("<b>Ritus</b><br/>" + str(self.rito), styNormal)

        if self.tipo_contenitore_resti == None:
            tipo_contenitore_resti = Paragraph("<b>Funeralbehältnisses</b><br/>", styNormal)
        else:
            tipo_contenitore_resti = Paragraph("<b>Funeralbehältnisses</b><br/>" + str(self.tipo_contenitore_resti),
                                               styNormal)

        if self.orientamento_asse == None:
            orientamento_asse = Paragraph("<b>Orientierung Achse</b><br/>", styNormal)
        else:
            orientamento_asse = Paragraph("<b>Orientierung Achse</b><br/>" + str(self.orientamento_asse), styNormal)

        if self.orientamento_azimut == None:
            orientamento_azimut = Paragraph("<b>Azimut</b><br/>", styNormal)
        else:
            orientamento_azimut = Paragraph("<b>Azimut</b><br/>" + str(self.orientamento_azimut), styNormal)

        if self.corredo_presenza == None:
            corredo_presenza = Paragraph("<b>Grabbeigabe</b><br/>", styNormal)
        else:
            corredo_presenza = Paragraph("<b>Grabbeigabe</b><br/>" + self.corredo_presenza, styNormal)

        if self.completo_si_no == None:
            completo_si_no = Paragraph("<b>Voll</b><br/>", styNormal)
        else:
            completo_si_no = Paragraph("<b>Voll</b><br/>" + self.completo_si_no, styNormal)

        if self.disturbato_si_no == None:
            disturbato_si_no = Paragraph("<b>Gestört</b><br/>", styNormal)
        else:
            disturbato_si_no = Paragraph("<b>Gestört</b><br/>" + self.disturbato_si_no, styNormal)

        if self.in_connessione_si_no == None:
            connessione_si_no = Paragraph("<b>In Verbindung</b><br/>", styNormal)
        else:
            connessione_si_no = Paragraph("<b>In Verbindung</b><br/>" + self.in_connessione_si_no, styNormal)

        if self.periodo_iniziale == None:
            periodo_iniziale = Paragraph("<b>Anfangszeitraum</b><br/>", styNormal)
        else:
            periodo_iniziale = Paragraph("<b>Anfangszeitraum</b><br/>" + self.periodo_iniziale, styNormal)

        if self.fase_iniziale == None:
            fase_iniziale = Paragraph("<b>Anfangsphase</b><br/>", styNormal)
        else:
            fase_iniziale = Paragraph("<b>Anfangsphase</b><br/>" + self.fase_iniziale, styNormal)

        if self.periodo_finale == None:
            periodo_finale = Paragraph("<b>Letzte zeitraum</b><br/>", styNormal)
        else:
            periodo_finale = Paragraph("<b>Letzte zeitraum</b><br/>" + self.periodo_finale, styNormal)

        if self.fase_finale == None:
            fase_finale = Paragraph("<b>Letzte phase</b><br/>", styNormal)
        else:
            fase_finale = Paragraph("<b>Letzte phase</b><br/>" + self.fase_finale, styNormal)

        if self.datazione_estesa == None:
            datazione_estesa = Paragraph("<b>Erweiterte Datierung</b><br/>", styNormal)
        else:
            datazione_estesa = Paragraph("<b>Erweiterte Datierung</b><br/>" + self.datazione_estesa, styNormal)

        data = [num_scheda,
                sigla_struttura,
                numero_struttura,
                numero_individuo,
                rito,
                corredo_presenza,
                completo_si_no,
                periodo_iniziale,
                fase_iniziale,
                periodo_finale,
                fase_finale]

        return data
    def getTable_en(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7

        # self.unzip_rapporti_stratigrafici()

        num_scheda = Paragraph("<b>Field Nr.</b><br/>" + str(self.nr_scheda_taf), styNormal)

        sigla_struttura = Paragraph("<b>Structure code</b><br/>" + str(self.sigla_struttura), styNormal)

        numero_struttura = Paragraph("<b>Structure Nr.</b><br/>" + str(self.nr_struttura), styNormal)

        numero_individuo = Paragraph("<b>Individual Nr.</b><br/>" + str(self.nr_individuo), styNormal)

        if self.rito == None:
            rito = Paragraph("<b>Rite</b><br/>", styNormal)
        else:
            rito = Paragraph("<b>Rite</b><br/>" + str(self.rito), styNormal)

        if self.tipo_contenitore_resti == None:
            tipo_contenitore_resti = Paragraph("<b>Container type</b><br/>", styNormal)
        else:
            tipo_contenitore_resti = Paragraph("<b>Container type</b><br/>" + str(self.tipo_contenitore_resti),
                                               styNormal)

        if self.orientamento_asse == None:
            orientamento_asse = Paragraph("<b>Axes orientation</b><br/>", styNormal)
        else:
            orientamento_asse = Paragraph("<b>Axes orientation</b><br/>" + str(self.orientamento_asse), styNormal)

        if self.orientamento_azimut == None:
            orientamento_azimut = Paragraph("<b>Azimut</b><br/>", styNormal)
        else:
            orientamento_azimut = Paragraph("<b>Azimut</b><br/>" + str(self.orientamento_azimut), styNormal)

        if self.corredo_presenza == None:
            corredo_presenza = Paragraph("<b>Trousseau</b><br/>", styNormal)
        else:
            corredo_presenza = Paragraph("<b>Trousseau</b><br/>" + self.corredo_presenza, styNormal)

        if self.completo_si_no == None:
            completo_si_no = Paragraph("<b>Complete</b><br/>", styNormal)
        else:
            completo_si_no = Paragraph("<b>Complete</b><br/>" + self.completo_si_no, styNormal)

        if self.disturbato_si_no == None:
            disturbato_si_no = Paragraph("<b>Hampered</b><br/>", styNormal)
        else:
            disturbato_si_no = Paragraph("<b>Hampered</b><br/>" + self.disturbato_si_no, styNormal)

        if self.in_connessione_si_no == None:
            connessione_si_no = Paragraph("<b>In connection</b><br/>", styNormal)
        else:
            connessione_si_no = Paragraph("<b>In connection</b><br/>" + self.in_connessione_si_no, styNormal)

        if self.periodo_iniziale == None:
            periodo_iniziale = Paragraph("<b>Start period</b><br/>", styNormal)
        else:
            periodo_iniziale = Paragraph("<b>Start period</b><br/>" + self.periodo_iniziale, styNormal)

        if self.fase_iniziale == None:
            fase_iniziale = Paragraph("<b>Start phase</b><br/>", styNormal)
        else:
            fase_iniziale = Paragraph("<b>Start phase</b><br/>" + self.fase_iniziale, styNormal)

        if self.periodo_finale == None:
            periodo_finale = Paragraph("<b>Final period</b><br/>", styNormal)
        else:
            periodo_finale = Paragraph("<b>Final period</b><br/>" + self.periodo_finale, styNormal)

        if self.fase_finale == None:
            fase_finale = Paragraph("<b>Final phase</b><br/>", styNormal)
        else:
            fase_finale = Paragraph("<b>Final phase</b><br/>" + self.fase_finale, styNormal)

        if self.datazione_estesa == None:
            datazione_estesa = Paragraph("<b>Litteral datation</b><br/>", styNormal)
        else:
            datazione_estesa = Paragraph("<b>Litteral datation</b><br/>" + self.datazione_estesa, styNormal)

        data = [num_scheda,
                sigla_struttura,
                numero_struttura,
                numero_individuo,
                rito,
                corredo_presenza,
                completo_si_no,
                periodo_iniziale,
                fase_iniziale,
                periodo_finale,
                fase_finale]

        return data
    
    
    def makeStyles(self):
        styles = TableStyle([('GRID', (0, 0), (-1, -1), 0.0, colors.black), ('VALIGN', (0, 0), (-1, -1), 'TOP')
                             ])  # finale

        return styles


class Tomba_index_II_pdf_sheet(object):
    L=QgsSettings().value("locale/userLocale")[0:2]
    PU = Utility()
    # this model includes str.n., area/sett, descrizione, rito
    # corredo,orient., UUSS/UUSSMM, quotemax, misure, datazione

    us_ind_print = ''
    us_str_print = ''
    us_ind_list = ''
    us_str_list = ''

    def __init__(self, data):
        self.nr_scheda_taf = data[1]
        self.sigla_struttura = data[2]
        self.nr_struttura = data[3]
        self.nr_individuo = data[4]
        self.rito = data[5]
        self.corredo_presenza = data[16]
        self.orientamento_asse = data[14]
        self.orientamento_azimut = data[15]

        try:
            self.us_ind_list = data[38]
            self.us_str_list = data[39]
        except:
            pass

        self.quota_min_strutt = data[36]
        self.quota_max_strutt = data[37]
        self.misure_tomba = data[33]
        self.datazione_estesa = data[32]

    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7

        # self.unzip_rapporti_stratigrafici()

        num_scheda = Paragraph("<b>N°Scheda</b><br/>" + str(self.nr_scheda_taf), styNormal)

        sigla_num_struttura = Paragraph("<b>Sigla Str.</b><br/>" + str(self.sigla_struttura) + str(self.nr_struttura),
                                        styNormal)

        numero_individuo = Paragraph("<b>N°Ind</b><br/>" + str(self.nr_individuo), styNormal)

        if self.rito == None:
            rito = Paragraph("<b>Rito</b><br/>", styNormal)
        else:
            rito = Paragraph("<b>Rito</b><br/>" + str(self.rito), styNormal)

        if self.corredo_presenza == None:
            corredo_presenza = Paragraph("<b>Corredo</b><br/>", styNormal)
        else:
            corredo_presenza = Paragraph("<b>Corredo</b><br/>" + str(self.corredo_presenza), styNormal)

        if self.orientamento_asse == None:
            orientamento_asse = Paragraph("<b>Asse</b><br/>", styNormal)
        else:
            orientamento_asse = Paragraph("<b>Asse</b><br/>" + str(self.orientamento_asse), styNormal)

        if str(self.orientamento_azimut) == "None":
            orientamento_azimut = Paragraph("<b>Azimut</b><br/>", styNormal)
        else:
            orientamento_azimut_conv = self.PU.conversione_numeri(self.orientamento_azimut)
            orientamento_azimut = Paragraph("<b>Azimut</b><br/>" + orientamento_azimut_conv + "°", styNormal)

        if self.us_ind_list:
            us_ind_temp = ""
            for us_ind in self.us_ind_list:
                if us_ind_temp == '':
                    us_ind_temp = '%s/%s' % (us_ind[1], us_ind[2])
                else:
                    us_ind_temp += ',<br/>' + '%s/%s' % (us_ind[1], us_ind[2])

            self.us_ind_print = Paragraph("<b>US Ind.<br/>(Area/US)</b><br/>" + str(us_ind_temp) + "<br/>", styNormal)
        else:
            self.us_ind_print = Paragraph("<b>US Ind.<br/>(Area/US)</b><br/>", styNormal)

        if self.us_str_list:
            us_str_temp = ""
            for us_str in self.us_str_list:
                if us_str_temp == '':
                    us_str_temp = '%s/%s' % (us_str[1], us_str[2])
                else:
                    us_str_temp += ',<br/>' + '%s/%s' % (us_str[1], us_str[2])

            self.us_str_print = Paragraph("<b>US Str<br/>(Area/US)</b><br/>" + str(us_str_temp) + "<br/>", styNormal)
        else:
            self.us_str_print = Paragraph("<b>US Str<br/>(Area/US)</b><br/>", styNormal)

        quota_min_max = Paragraph("<b>Quota Min-max:</b><br/>" + self.quota_min_strutt + "-" + self.quota_max_strutt,
                                  styNormal)

        if self.datazione_estesa == None:
            datazione_estesa = Paragraph("<b>Datazione</b><br/>", styNormal)
        else:
            datazione_estesa = Paragraph("<b>Datazione estesa</b><br/>" + str(self.datazione_estesa), styNormal)

        data = [num_scheda,
                sigla_num_struttura,
                numero_individuo,
                rito,
                corredo_presenza,
                orientamento_asse,
                orientamento_azimut,
                self.us_ind_print,
                self.us_str_print,
                quota_min_max,
                datazione_estesa]

        return data
    def getTable_de(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7

        # self.unzip_rapporti_stratigrafici()

        num_scheda = Paragraph("<b>N° Feld</b><br/>" + str(self.nr_scheda_taf), styNormal)

        sigla_num_struttura = Paragraph("<b>Strukturcode</b><br/>" + str(self.sigla_struttura) + str(self.nr_struttura),
                                        styNormal)

        numero_individuo = Paragraph("<b>Nr Individuel</b><br/>" + str(self.nr_individuo), styNormal)

        if self.rito == None:
            rito = Paragraph("<b>Ritus</b><br/>", styNormal)
        else:
            rito = Paragraph("<b>Ritus</b><br/>" + str(self.rito), styNormal)

        if self.corredo_presenza == None:
            corredo_presenza = Paragraph("<b>Grabbeigabe</b><br/>", styNormal)
        else:
            corredo_presenza = Paragraph("<b>Grabbeigabe</b><br/>" + str(self.corredo_presenza), styNormal)

        if self.orientamento_asse == None:
            orientamento_asse = Paragraph("<b>Achse</b><br/>", styNormal)
        else:
            orientamento_asse = Paragraph("<b>Achse</b><br/>" + str(self.orientamento_asse), styNormal)

        if str(self.orientamento_azimut) == "None":
            orientamento_azimut = Paragraph("<b>Azimut</b><br/>", styNormal)
        else:
            orientamento_azimut_conv = self.PU.conversione_numeri(self.orientamento_azimut)
            orientamento_azimut = Paragraph("<b>Azimut</b><br/>" + orientamento_azimut_conv + "°", styNormal)

        if self.us_ind_list:
            us_ind_temp = ""
            for us_ind in self.us_ind_list:
                if us_ind_temp == '':
                    us_ind_temp = '%s/%s' % (us_ind[1], us_ind[2])
                else:
                    us_ind_temp += ',<br/>' + '%s/%s' % (us_ind[1], us_ind[2])

            self.us_ind_print = Paragraph("<b>SE Ind.<br/>(Areal/SE)</b><br/>" + str(us_ind_temp) + "<br/>", styNormal)
        else:
            self.us_ind_print = Paragraph("<b>SE Ind.<br/>(Areal/SE)</b><br/>", styNormal)

        if self.us_str_list:
            us_str_temp = ""
            for us_str in self.us_str_list:
                if us_str_temp == '':
                    us_str_temp = '%s/%s' % (us_str[1], us_str[2])
                else:
                    us_str_temp += ',<br/>' + '%s/%s' % (us_str[1], us_str[2])

            self.us_str_print = Paragraph("<b>SE Str<br/>(Areal/SE)</b><br/>" + str(us_str_temp) + "<br/>", styNormal)
        else:
            self.us_str_print = Paragraph("<b>SE Str<br/>(Areal/SE)</b><br/>", styNormal)

        quota_min_max = Paragraph("<b>Höhe Min-max:</b><br/>" + self.quota_min_strutt + "-" + self.quota_max_strutt,
                                  styNormal)

        if self.datazione_estesa == None:
            datazione_estesa = Paragraph("<b>Erweiterte Datierung</b><br/>", styNormal)
        else:
            datazione_estesa = Paragraph("<b>Erweiterte Datierung</b><br/>" + str(self.datazione_estesa), styNormal)

        data = [num_scheda,
                sigla_num_struttura,
                numero_individuo,
                rito,
                corredo_presenza,
                orientamento_asse,
                orientamento_azimut,
                self.us_ind_print,
                self.us_str_print,
                quota_min_max,
                datazione_estesa]

        return data
    
    def getTable_en(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7

        # self.unzip_rapporti_stratigrafici()

        num_scheda = Paragraph("<b>Field Nr.</b><br/>" + str(self.nr_scheda_taf), styNormal)

        sigla_num_struttura = Paragraph("<b>Structure code</b><br/>" + str(self.sigla_struttura) + str(self.nr_struttura),
                                        styNormal)

        numero_individuo = Paragraph("<b>Individual Nr.</b><br/>" + str(self.nr_individuo), styNormal)

        if self.rito == None:
            rito = Paragraph("<b>Rite</b><br/>", styNormal)
        else:
            rito = Paragraph("<b>Rite</b><br/>" + str(self.rito), styNormal)

        if self.corredo_presenza == None:
            corredo_presenza = Paragraph("<b>Trousseau</b><br/>", styNormal)
        else:
            corredo_presenza = Paragraph("<b>Trousseau</b><br/>" + str(self.corredo_presenza), styNormal)

        if self.orientamento_asse == None:
            orientamento_asse = Paragraph("<b>Axes</b><br/>", styNormal)
        else:
            orientamento_asse = Paragraph("<b>Axes</b><br/>" + str(self.orientamento_asse), styNormal)

        if str(self.orientamento_azimut) == "None":
            orientamento_azimut = Paragraph("<b>Azimut</b><br/>", styNormal)
        else:
            orientamento_azimut_conv = self.PU.conversione_numeri(self.orientamento_azimut)
            orientamento_azimut = Paragraph("<b>Azimut</b><br/>" + orientamento_azimut_conv + "°", styNormal)

        if self.us_ind_list:
            us_ind_temp = ""
            for us_ind in self.us_ind_list:
                if us_ind_temp == '':
                    us_ind_temp = '%s/%s' % (us_ind[1], us_ind[2])
                else:
                    us_ind_temp += ',<br/>' + '%s/%s' % (us_ind[1], us_ind[2])

            self.us_ind_print = Paragraph("<b>SU Ind.<br/>(Area/SU)</b><br/>" + str(us_ind_temp) + "<br/>", styNormal)
        else:
            self.us_ind_print = Paragraph("<b>US Ind.<br/>(Area/US)</b><br/>", styNormal)

        if self.us_str_list:
            us_str_temp = ""
            for us_str in self.us_str_list:
                if us_str_temp == '':
                    us_str_temp = '%s/%s' % (us_str[1], us_str[2])
                else:
                    us_str_temp += ',<br/>' + '%s/%s' % (us_str[1], us_str[2])

            self.us_str_print = Paragraph("<b>SU Str<br/>(Area/SU)</b><br/>" + str(us_str_temp) + "<br/>", styNormal)
        else:
            self.us_str_print = Paragraph("<b>SU Str<br/>(Area/US)</b><br/>", styNormal)

        quota_min_max = Paragraph("<b>Elev. Min-max:</b><br/>" + self.quota_min_strutt + "-" + self.quota_max_strutt,
                                  styNormal)

        if self.datazione_estesa == None:
            datazione_estesa = Paragraph("<b>Letteral datation</b><br/>", styNormal)
        else:
            datazione_estesa = Paragraph("<b>Letteral datation</b><br/>" + str(self.datazione_estesa), styNormal)

        data = [num_scheda,
                sigla_num_struttura,
                numero_individuo,
                rito,
                corredo_presenza,
                orientamento_asse,
                orientamento_azimut,
                self.us_ind_print,
                self.us_str_print,
                quota_min_max,
                datazione_estesa]

        return data
    
    def makeStyles(self):
        styles = TableStyle([('GRID', (0, 0), (-1, -1), 0.0, colors.black), ('VALIGN', (0, 0), (-1, -1), 'TOP')
                             ])  # finale

        return styles


class single_Tomba_pdf_sheet(object):
    L=QgsSettings().value("locale/userLocale")[0:2]
    PU = Utility()

    # rapporti stratigrafici

    def __init__(self, data):
        self.sito = data[0]
        self.nr_scheda_taf = data[1]
        self.sigla_struttura = data[2]
        self.nr_struttura = data[3]
        self.nr_individuo = data[4]
        self.rito = data[5]
        self.descrizione_taf = data[6]
        self.interpretazione_taf = data[7]
        self.segnacoli = data[8]
        self.canale_libatorio_si_no = data[9]
        self.oggetti_rinvenuti_esterno = data[10]
        self.stato_di_conservazione = data[11]
        self.copertura_tipo = data[12]
        self.tipo_contenitore_resti = data[13]
        self.orientamento_asse = data[14]
        self.orientamento_azimut = data[15]
        self.corredo_presenza = data[16]
        self.corredo_tipo = data[17]
        self.corredo_descrizione = data[18]
        self.lunghezza_scheletro = data[19]
        self.posizione_cranio = data[20]
        self.posizione_scheletro = data[21]
        self.posizione_arti_superiori = data[22]
        self.posizione_arti_inferiori = data[23]
        self.completo_si_no = data[24]
        self.disturbato_si_no = data[25]
        self.in_connessione_si_no = data[26]
        self.caratteristiche = data[27]
        self.periodo_iniziale = data[28]
        self.fase_iniziale = data[29]
        self.periodo_finale = data[30]
        self.fase_finale = data[31]
        self.datazione_estesa = data[32]
        self.misure_tomba = data[33]
        self.quota_min_ind = data[34]
        self.quota_max_ind = data[35]
        self.quota_min_strutt = data[36]
        self.quota_max_strutt = data[37]

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def create_sheet(self):
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
        intestazione = Paragraph("<b>SCHEDA TAFONOMICA<br/>" + str(self.datestrfdate()) + "</b>", styNormal)

        # intestazione2 = Paragraph("<b>pyArchInit</b><br/>pyarchinit", styNormal)

        # intestazione2  = Paragraph("<b>Ditta esecutrice</b><br/>", styNormal)
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

        ##      if test_image.drawWidth < 800:

        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch

        # 1 row
        sito = Paragraph("<b>Sito</b><br/>" + str(self.sito), styNormal)
        sigla_struttura = Paragraph("<b>Sigla struttura</b><br/>" + str(self.sigla_struttura) + str(self.nr_struttura),
                                    styNormal)
        nr_individuo = Paragraph("<b>N° Individuo</b><br/>" + str(self.nr_individuo), styNormal)
        nr_scheda = Paragraph("<b>N° Scheda</b><br/>" + str(self.nr_scheda_taf), styNormal)

        # 2 row
        periodizzazione = Paragraph("<b>PERIODIZZAZIONE DEL RITO DI SEPOLTURA</b><br/>", styNormal)

        # 3 row
        if str(self.periodo_iniziale) == "None":
            periodo_iniziale = Paragraph("<b>Periodo iniziale</b><br/>", styNormal)
        else:
            periodo_iniziale = Paragraph("<b>Periodo iniziale</b><br/>" + str(self.periodo_iniziale), styNormal)

        if str(self.fase_iniziale) == "None":
            fase_iniziale = Paragraph("<b>Fase iniziale</b><br/>", styNormal)
        else:
            fase_iniziale = Paragraph("<b>Fase iniziale</b><br/>" + str(self.fase_iniziale), styNormal)

        if str(self.periodo_finale) == "None":
            periodo_finale = Paragraph("<b>Periodo finale</b><br/>", styNormal)
        else:
            periodo_finale = Paragraph("<b>Periodo finale</b><br/>" + str(self.periodo_finale), styNormal)

        if str(self.fase_finale) == "None":
            fase_finale = Paragraph("<b>Fase finale</b><br/>", styNormal)
        else:
            fase_finale = Paragraph("<b>Fase finale</b><br/>" + str(self.fase_finale), styNormal)

        # 4 row
        if str(self.datazione_estesa) == "None":
            datazione_estesa = Paragraph("<b>Datazione estesa</b><br/>", styNormal)
        else:
            datazione_estesa = Paragraph("<b>Datazione estesa</b><br/>" + self.datazione_estesa, styNormal)

        # 5 row
        elementi_strutturali = Paragraph("<b>ELEMENTI STRUTTURALI</b><br/>", styNormal)

        # 6row
        tipo_contenitore_resti = Paragraph("<b>Tipo contenitore resti</b><br/>" + self.tipo_contenitore_resti,
                                           styNormal)
        tipo_copertura = Paragraph("<b>Tipo copertura</b><br/>" + self.copertura_tipo, styNormal)
        segnacoli = Paragraph("<b>Segnacoli</b><br/>" + self.segnacoli, styNormal)
        canale_libatorio = Paragraph("<b>Canale libatorio</b><br/>" + self.canale_libatorio_si_no, styNormal)

        # 7 row
        dati_deposizionali = Paragraph("<b>DATI DEPOSIZIONALI INUMATO</b><br/>", styNormal)

        # 8 row
        rito = Paragraph("<b>Rito</b><br/>" + self.rito, styNormal)
        orientamento_asse = Paragraph("<b>Orientamento asse</b><br/>" + str(self.orientamento_asse), styNormal)
        if str(self.orientamento_azimut) == "None":
            orientamento_azimut = Paragraph("<b>Azimut</b><br/>", styNormal)
        else:
            orientamento_azimut_conv = self.PU.conversione_numeri(self.orientamento_azimut)
            orientamento_azimut = Paragraph("<b>Azimut</b><br/>" + orientamento_azimut_conv + "°", styNormal)
        posizione_cranio = Paragraph("<b>Posizione cranio</b><br/>" + str(self.posizione_cranio), styNormal)

        # 9 row
        posizione_scheletro = Paragraph("<b>Posizione scheletro</b><br/>" + str(self.posizione_scheletro), styNormal)
        if str(self.lunghezza_scheletro) == "None":
            lunghezza_scheletro = Paragraph("<b>Lunghezza scheletro</b><br/>", styNormal)
        else:
            lunghezza_scheletro_conv = self.PU.conversione_numeri(self.lunghezza_scheletro)
            lunghezza_scheletro = Paragraph("<b>Lunghezza scheletro</b><br/>" + lunghezza_scheletro_conv + " m",
                                            styNormal)
        posizione_arti_superiori = Paragraph(
            "<b>Posizione arti superiori</b><br/>" + str(self.posizione_arti_superiori), styNormal)
        posizione_arti_inferiori = Paragraph(
            "<b>Posizione arti inferiori</b><br/>" + str(self.posizione_arti_inferiori), styNormal)

        # 10 row
        dati_postdeposizionali = Paragraph("<b>DATI POSTDEPOSIZIONALI</b><br/>", styNormal)

        # 11 row
        stato_conservazione = Paragraph("<b>Stato di conservazione</b><br/>" + str(self.stato_di_conservazione),
                                        styNormal)
        disturbato = Paragraph("<b>Disturbato</b><br/>" + str(self.disturbato_si_no), styNormal)
        completo = Paragraph("<b>Completo</b><br/>" + str(self.completo_si_no), styNormal)
        in_connessione = Paragraph("<b>In connessione</b><br/>" + str(self.in_connessione_si_no), styNormal)

        # 12 row
        caratteristiche_tafonomiche = ''
        caratteristiche_list = eval(self.caratteristiche)
        if len(caratteristiche_list) > 0:
            for i in caratteristiche_list:
                if caratteristiche_tafonomiche == '':
                    caratteristiche_tafonomiche = ("Tipo caratteristica: %s, posizione: %s") % (str(i[0]), str(i[1]))
                else:
                    caratteristiche_tafonomiche += ("<br/>Tipo caratteristica: %s, posizione: %s") % (
                    str(i[0]), str(i[1]))

        caratteristiche_tafonomiche_txt = Paragraph(
            "<b>CARATTERISTICHE TAFONOMICHE</b><br/>" + caratteristiche_tafonomiche, styNormal)

        # 13 row
        descrizione = ''
        try:
            descrizione = Paragraph("<b>Descrizione</b><br/>" + self.descrizione_taf, styDescrizione)
        except:
            pass

        interpretazione = ''
        try:
            interpretazione = Paragraph("<b>Interpretazione</b><br/>" + self.interpretazione_taf, styDescrizione)
        except:
            pass

        # 14 row
        corredo = Paragraph("<b>CORREDO</b><br/>", styNormal)

        # 15 row
        corredo_presente = Paragraph("<b>Presenza</b><br/>" + self.corredo_presenza, styDescrizione)

        # 16 row
        corredo_descrizione = Paragraph("<b>Descrizione</b><br/>" + self.corredo_descrizione, styDescrizione)

        # 17 row
        corredo_tipo = ''
        if len(self.corredo_tipo) > 0:
            for i in eval(self.corredo_tipo):
                if corredo_tipo == '':
                    try:
                        corredo_tipo += ("N° reperto %s, tipo corredo: %s, descrizione: %s") % (
                        str(i[0]), str(i[1]), str(i[2]))
                    except:
                        pass
                else:
                    try:
                        corredo_tipo += ("<br/>N° reperto %s, tipo corredo: %s, descrizione: %s") % (
                        str(i[0]), str(i[1]), str(i[2]))
                    except:
                        pass

        corredo_tipo_txt = Paragraph("<b>Singoli oggetti di corredo</b><br/>" + corredo_tipo, styNormal)

        # 18 row
        misure_tomba = ''
        if len(self.misure_tomba) > 0:
            for i in eval(self.misure_tomba):
                if misure_tomba == '':
                    try:
                        misure_tomba += ("%s: %s %s") % (str(i[0]), str(i[2]), str(i[1]))
                    except:
                        pass
                else:
                    try:
                        misure_tomba += ("<br/>%s: %s %s") % (str(i[0]), str(i[2]), str(i[1]))
                    except:
                        pass

        misure_tomba_txt = Paragraph("<b>Misurazioni</b><br/>" + misure_tomba, styNormal)

        # 19 row
        quote_tomba = Paragraph("<b>QUOTE INDIVIDUO E STRUTTURA</b><br/>", styNormal)

        # 20 row
        quota_min_ind = Paragraph("<b>Quota min individuo</b><br/>" + str(self.quota_min_ind), styNormal)
        quota_max_ind = Paragraph("<b>Quota max individuo</b><br/>" + str(self.quota_max_ind), styNormal)
        quota_min_strutt = Paragraph("<b>Quota min struttura</b><br/>" + str(self.quota_min_strutt), styNormal)
        quota_max_strutt = Paragraph("<b>Quota max struttura</b><br/>" + str(self.quota_max_strutt), styNormal)

        # schema
        cell_schema = [  # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],  # 0 row  ok
            [sito, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 1 row ok
            [sigla_struttura, '01', '02', '03', '04', nr_individuo, '06', '07', nr_scheda, '09'],  # 1 row ok
            [periodizzazione, '01', '02', '03', '04', '07', '06', '07', '08', '09'],  # 2 row ok
            [periodo_iniziale, '01', '02', fase_iniziale, '04', periodo_finale, '06', fase_finale, '08', '09'],
            # 3 row ok
            [datazione_estesa, '01', '02', '03', '04', '07', '06', '07', '08', '09'],  # 4 row ok
            [elementi_strutturali, '01', '02', '03', '04', '07', '06', '07', '08', '09'],  # 5 row ok
            [tipo_contenitore_resti, '01', '02', tipo_copertura, '04', segnacoli, '06', canale_libatorio, '08'],
            # 6 row ok
            [dati_deposizionali, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 7 row ok
            [rito, '01', '02', orientamento_asse, '04', orientamento_azimut, '06', posizione_cranio, '08', '09'],
            # 8 row ok
            [posizione_scheletro, '01', lunghezza_scheletro, '03', posizione_arti_superiori, '05', '06',
             posizione_arti_inferiori, '08', '09'],  # 9 row ok
            [dati_postdeposizionali, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 10 row ok
            [stato_conservazione, '01', '02', disturbato, '04', completo, '06', in_connessione, '08'],  # 11 row ok
            [caratteristiche_tafonomiche_txt, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 12 row ok
            [descrizione, '01', '02', '03', '04', interpretazione, '06', '07', '08', '09'],  # 13 row ok
            [corredo, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 14 row ok
            [corredo_presente, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 15 ow
            [corredo_descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 16 row
            [corredo_tipo_txt, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 17 row
            [misure_tomba_txt, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 18 row
            [quote_tomba, '01', '02', '03', '04', '07', '06', '07', '08', '09'],  # 19 row ok
            [quota_min_ind, '01', '02', quota_max_ind, '04', quota_min_strutt, '06', quota_max_strutt, '08', '09']
            # 20 row ok
        ]

        # table style
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row
            ('SPAN', (0, 0), (6, 0)),  # intestazione
            ('SPAN', (7, 0), (9, 0)),  # intestazione

            # 1 row
            ('SPAN', (0, 1), (9, 1)),  # sito

            # 2
            ('SPAN', (0, 2), (4, 2)),  # dati identificativi
            ('SPAN', (5, 2), (7, 2)),  # dati identificativi
            ('SPAN', (8, 2), (9, 2)),  # dati identificativi

            # 2 row
            ('SPAN', (0, 3), (9, 3)),  # Periodizzazione

            # 3 row
            ('SPAN', (0, 4), (2, 4)),  #
            ('SPAN', (3, 4), (4, 4)),  #
            ('SPAN', (5, 4), (6, 4)),  #
            ('SPAN', (7, 4), (9, 4)),  #

            # 4 row
            ('SPAN', (0, 5), (9, 5)),  # datazione estesa
            ##################################
            # 5 row
            ('SPAN', (0, 6), (9, 6)),  # Elementi strutturali

            # 6 row
            ('SPAN', (0, 7), (2, 7)),  #
            ('SPAN', (3, 7), (4, 7)),  #
            ('SPAN', (5, 7), (6, 7)),  #
            ('SPAN', (7, 7), (9, 7)),  #

            # 7 row
            ('SPAN', (0, 8), (9, 8)),  #

            # 8 row
            ('SPAN', (0, 9), (2, 9)),  #
            ('SPAN', (3, 9), (4, 9)),  #
            ('SPAN', (5, 9), (6, 9)),  #
            ('SPAN', (7, 9), (9, 9)),  #

            # 9 row
            ('SPAN', (0, 10), (1, 10)),  #
            ('SPAN', (2, 10), (3, 10)),  #
            ('SPAN', (4, 10), (6, 10)),  #
            ('SPAN', (7, 10), (9, 10)),  #

            # 10 row
            ('SPAN', (0, 11), (9, 11)),  #

            # 11 row
            ('SPAN', (0, 12), (2, 12)),  #
            ('SPAN', (3, 12), (4, 12)),  #
            ('SPAN', (5, 12), (6, 12)),  #
            ('SPAN', (7, 12), (9, 12)),  #

            # 12 row
            ('SPAN', (0, 13), (9, 13)),  #

            # 13 row
            ('SPAN', (0, 14), (4, 14)),  #
            ('SPAN', (5, 14), (9, 14)),  #

            # 14 row
            ('SPAN', (0, 15), (9, 15)),  #

            # 15 row
            ('SPAN', (0, 16), (9, 16)),  #

            # 16 row
            ('SPAN', (0, 17), (9, 17)),

            # 17 row
            ('SPAN', (0, 18), (9, 18)),  #

            # 18 row
            ('SPAN', (0, 19), (9, 19)),  #

            ('SPAN', (0, 20), (9, 20)),  # Periodizzazione

            # 3 row
            ('SPAN', (0, 21), (2, 21)),  #
            ('SPAN', (3, 21), (4, 21)),  #
            ('SPAN', (5, 21), (6, 21)),  #
            ('SPAN', (7, 21), (9, 21)),  #

            ('VALIGN', (0, 0), (-1, -1), 'TOP')

        ]

        t = Table(cell_schema, colWidths=50, rowHeights=None, style=table_style)

        return t

    def create_sheet_de(self):
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
        intestazione = Paragraph("<b>FELD THAPHONOMIE<br/>" + str(self.datestrfdate()) + "</b>", styNormal)

        # intestazione2 = Paragraph("<b>pyArchInit</b><br/>pyarchinit", styNormal)

        # intestazione2  = Paragraph("<b>Ditta esecutrice</b><br/>", styNormal)
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

        ##      if test_image.drawWidth < 800:

        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch

        # 1 row
        sito = Paragraph("<b>Ausgrabungsstätte</b><br/>" + str(self.sito), styNormal)
        sigla_struttura = Paragraph("<b>Nr struktur</b><br/>" + str(self.sigla_struttura) + str(self.nr_struttura),
                                    styNormal)
        nr_individuo = Paragraph("<b>Nr Individuel</b><br/>" + str(self.nr_individuo), styNormal)
        nr_scheda = Paragraph("<b>N° Feld</b><br/>" + str(self.nr_scheda_taf), styNormal)

        # 2 row
        periodizzazione = Paragraph("<b>PERIODISIERUNG BESTATTUNGEN</b><br/>", styNormal)

        # 3 row
        if str(self.periodo_iniziale) == "None":
            periodo_iniziale = Paragraph("<b>Anfangszeitraum</b><br/>", styNormal)
        else:
            periodo_iniziale = Paragraph("<b>Anfangszeitraum</b><br/>" + str(self.periodo_iniziale), styNormal)

        if str(self.fase_iniziale) == "None":
            fase_iniziale = Paragraph("<b>Anfangsphase</b><br/>", styNormal)
        else:
            fase_iniziale = Paragraph("<b>Anfangsphase</b><br/>" + str(self.fase_iniziale), styNormal)

        if str(self.periodo_finale) == "None":
            periodo_finale = Paragraph("<b>Letzte zeitraum</b><br/>", styNormal)
        else:
            periodo_finale = Paragraph("<b>Letzte zeitraum</b><br/>" + str(self.periodo_finale), styNormal)

        if str(self.fase_finale) == "None":
            fase_finale = Paragraph("<b>Letzte phase</b><br/>", styNormal)
        else:
            fase_finale = Paragraph("<b>Letzte phase</b><br/>" + str(self.fase_finale), styNormal)

        # 4 row
        if str(self.datazione_estesa) == "None":
            datazione_estesa = Paragraph("<b>Erweiterte Datierung</b><br/>", styNormal)
        else:
            datazione_estesa = Paragraph("<b>Erweiterte Datierung</b><br/>" + self.datazione_estesa, styNormal)

        # 5 row
        elementi_strutturali = Paragraph("<b>STRUKTURELLE EIGENSCHAFTEN</b><br/>", styNormal)

        # 6row
        tipo_contenitore_resti = Paragraph("<b>Funeralbehältnisses</b><br/>" + self.tipo_contenitore_resti,
                                           styNormal)
        tipo_copertura = Paragraph("<b>Abdeckung</b><br/>" + self.copertura_tipo, styNormal)
        segnacoli = Paragraph("<b>Markierung</b><br/>" + self.segnacoli, styNormal)
        canale_libatorio = Paragraph("<b>Kanaal Libatorio</b><br/>" + self.canale_libatorio_si_no, styNormal)

        # 7 row
        dati_deposizionali = Paragraph("<b>INHUMIERTE DEPOSITIONSDATEN</b><br/>", styNormal)

        # 8 row
        rito = Paragraph("<b>Ritus</b><br/>" + self.rito, styNormal)
        orientamento_asse = Paragraph("<b>Orientierung Achse</b><br/>" + str(self.orientamento_asse), styNormal)
        if str(self.orientamento_azimut) == "None":
            orientamento_azimut = Paragraph("<b>Azimut</b><br/>", styNormal)
        else:
            orientamento_azimut_conv = self.PU.conversione_numeri(self.orientamento_azimut)
            orientamento_azimut = Paragraph("<b>Azimut</b><br/>" + orientamento_azimut_conv + "°", styNormal)
        posizione_cranio = Paragraph("<b>Schädelposition</b><br/>" + str(self.posizione_cranio), styNormal)

        # 9 row
        posizione_scheletro = Paragraph("<b>Skelettposition</b><br/>" + str(self.posizione_scheletro), styNormal)
        if str(self.lunghezza_scheletro) == "None":
            lunghezza_scheletro = Paragraph("<b>Skelettlänge</b><br/>", styNormal)
        else:
            lunghezza_scheletro_conv = self.PU.conversione_numeri(self.lunghezza_scheletro)
            lunghezza_scheletro = Paragraph("<b>Skelettlänge</b><br/>" + lunghezza_scheletro_conv + " m",
                                            styNormal)
        posizione_arti_superiori = Paragraph(
            "<b>Position der oberen Gliedmaße</b><br/>" + str(self.posizione_arti_superiori), styNormal)
        posizione_arti_inferiori = Paragraph(
            "<b>Position der unteren Gliedmaße</b><br/>" + str(self.posizione_arti_inferiori), styNormal)

        # 10 row
        dati_postdeposizionali = Paragraph("<b>POSTDEPOSITIONALE DATEN</b><br/>", styNormal)

        # 11 row
        stato_conservazione = Paragraph("<b>Erhaltungszustand</b><br/>" + str(self.stato_di_conservazione),
                                        styNormal)
        disturbato = Paragraph("<b>Gestört</b><br/>" + str(self.disturbato_si_no), styNormal)
        completo = Paragraph("<b>Voll</b><br/>" + str(self.completo_si_no), styNormal)
        in_connessione = Paragraph("<b>In Verbindung</b><br/>" + str(self.in_connessione_si_no), styNormal)

        # 12 row
        caratteristiche_tafonomiche = ''
        caratteristiche_list = eval(self.caratteristiche)
        if len(caratteristiche_list) > 0:
            for i in caratteristiche_list:
                if caratteristiche_tafonomiche == '':
                    caratteristiche_tafonomiche = ("Eigenschaftentyp: %s, position: %s") % (str(i[0]), str(i[1]))
                else:
                    caratteristiche_tafonomiche += ("<br/>Eigenschaftentyp: %s, position: %s") % (
                    str(i[0]), str(i[1]))

        caratteristiche_tafonomiche_txt = Paragraph(
            "<b>TAFONOMISCHE EIGENSCHAFTEN</b><br/>" + caratteristiche_tafonomiche, styNormal)

        # 13 row
        descrizione = ''
        try:
            descrizione = Paragraph("<b>Beschreibung</b><br/>" + self.descrizione_taf, styDescrizione)
        except:
            pass

        interpretazione = ''
        try:
            interpretazione = Paragraph("<b>Deutung</b><br/>" + self.interpretazione_taf, styDescrizione)
        except:
            pass

        # 14 row
        corredo = Paragraph("<b>Grabbeigabe</b><br/>", styNormal)

        # 15 row
        corredo_presente = Paragraph("<b>Präsenz</b><br/>" + self.corredo_presenza, styDescrizione)

        # 16 row
        corredo_descrizione = Paragraph("<b>Beschreibung</b><br/>" + self.corredo_descrizione, styDescrizione)

        # 17 row
        corredo_tipo = ''
        if len(self.corredo_tipo) > 0:
            for i in eval(self.corredo_tipo):
                if corredo_tipo == '':
                    try:
                        corredo_tipo += ("<br/>N° finden %s, Grabbeigabetyp: %s, Beschreibung: %s") % (
                        str(i[0]), str(i[1]), str(i[2]))
                    except:
                        pass
                else:
                    try:
                        corredo_tipo += ("<br/>N° finden %s, Grabbeigabetyp: %s, Beschreibung: %s") % (
                        str(i[0]), str(i[1]), str(i[2]))
                    except:
                        pass

        corredo_tipo_txt = Paragraph("<b>Einzelne Geräte</b><br/>" + corredo_tipo, styNormal)

        # 18 row
        misure_tomba = ''
        if len(self.misure_tomba) > 0:
            for i in eval(self.misure_tomba):
                if misure_tomba == '':
                    try:
                        misure_tomba += ("%s: %s %s") % (str(i[0]), str(i[2]), str(i[1]))
                    except:
                        pass
                else:
                    try:
                        misure_tomba += ("<br/>%s: %s %s") % (str(i[0]), str(i[2]), str(i[1]))
                    except:
                        pass

        misure_tomba_txt = Paragraph("<b>Messungen</b><br/>" + misure_tomba, styNormal)

        # 19 row
        quote_tomba = Paragraph("<b>INDIVIDUELLES Höhe UND STRUKTUR</b><br/>", styNormal)

        # 20 row
        quota_min_ind = Paragraph("<b>Höhe min ind.</b><br/>" + str(self.quota_min_ind), styNormal)
        quota_max_ind = Paragraph("<b>Höhe max ind.</b><br/>" + str(self.quota_max_ind), styNormal)
        quota_min_strutt = Paragraph("<b>Höhe min str.</b><br/>" + str(self.quota_min_strutt), styNormal)
        quota_max_strutt = Paragraph("<b>Höhe max str.</b><br/>" + str(self.quota_max_strutt), styNormal)

        # schema
        cell_schema = [  # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],  # 0 row  ok
            [sito, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 1 row ok
            [sigla_struttura, '01', '02', '03', '04', nr_individuo, '06', '07', nr_scheda, '09'],  # 1 row ok
            [periodizzazione, '01', '02', '03', '04', '07', '06', '07', '08', '09'],  # 2 row ok
            [periodo_iniziale, '01', '02', fase_iniziale, '04', periodo_finale, '06', fase_finale, '08', '09'],
            # 3 row ok
            [datazione_estesa, '01', '02', '03', '04', '07', '06', '07', '08', '09'],  # 4 row ok
            [elementi_strutturali, '01', '02', '03', '04', '07', '06', '07', '08', '09'],  # 5 row ok
            [tipo_contenitore_resti, '01', '02', tipo_copertura, '04', segnacoli, '06', canale_libatorio, '08'],
            # 6 row ok
            [dati_deposizionali, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 7 row ok
            [rito, '01', '02', orientamento_asse, '04', orientamento_azimut, '06', posizione_cranio, '08', '09'],
            # 8 row ok
            [posizione_scheletro, '01', lunghezza_scheletro, '03', posizione_arti_superiori, '05', '06',
             posizione_arti_inferiori, '08', '09'],  # 9 row ok
            [dati_postdeposizionali, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 10 row ok
            [stato_conservazione, '01', '02', disturbato, '04', completo, '06', in_connessione, '08'],  # 11 row ok
            [caratteristiche_tafonomiche_txt, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 12 row ok
            [descrizione, '01', '02', '03', '04', interpretazione, '06', '07', '08', '09'],  # 13 row ok
            [corredo, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 14 row ok
            [corredo_presente, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 15 ow
            [corredo_descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 16 row
            [corredo_tipo_txt, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 17 row
            [misure_tomba_txt, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 18 row
            [quote_tomba, '01', '02', '03', '04', '07', '06', '07', '08', '09'],  # 19 row ok
            [quota_min_ind, '01', '02', quota_max_ind, '04', quota_min_strutt, '06', quota_max_strutt, '08', '09']
            # 20 row ok
        ]

        # table style
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row
            ('SPAN', (0, 0), (6, 0)),  # intestazione
            ('SPAN', (7, 0), (9, 0)),  # intestazione

            # 1 row
            ('SPAN', (0, 1), (9, 1)),  # sito

            # 2
            ('SPAN', (0, 2), (4, 2)),  # dati identificativi
            ('SPAN', (5, 2), (7, 2)),  # dati identificativi
            ('SPAN', (8, 2), (9, 2)),  # dati identificativi

            # 2 row
            ('SPAN', (0, 3), (9, 3)),  # Periodizzazione

            # 3 row
            ('SPAN', (0, 4), (2, 4)),  #
            ('SPAN', (3, 4), (4, 4)),  #
            ('SPAN', (5, 4), (6, 4)),  #
            ('SPAN', (7, 4), (9, 4)),  #

            # 4 row
            ('SPAN', (0, 5), (9, 5)),  # datazione estesa
            ##################################
            # 5 row
            ('SPAN', (0, 6), (9, 6)),  # Elementi strutturali

            # 6 row
            ('SPAN', (0, 7), (2, 7)),  #
            ('SPAN', (3, 7), (4, 7)),  #
            ('SPAN', (5, 7), (6, 7)),  #
            ('SPAN', (7, 7), (9, 7)),  #

            # 7 row
            ('SPAN', (0, 8), (9, 8)),  #

            # 8 row
            ('SPAN', (0, 9), (2, 9)),  #
            ('SPAN', (3, 9), (4, 9)),  #
            ('SPAN', (5, 9), (6, 9)),  #
            ('SPAN', (7, 9), (9, 9)),  #

            # 9 row
            ('SPAN', (0, 10), (1, 10)),  #
            ('SPAN', (2, 10), (3, 10)),  #
            ('SPAN', (4, 10), (6, 10)),  #
            ('SPAN', (7, 10), (9, 10)),  #

            # 10 row
            ('SPAN', (0, 11), (9, 11)),  #

            # 11 row
            ('SPAN', (0, 12), (2, 12)),  #
            ('SPAN', (3, 12), (4, 12)),  #
            ('SPAN', (5, 12), (6, 12)),  #
            ('SPAN', (7, 12), (9, 12)),  #

            # 12 row
            ('SPAN', (0, 13), (9, 13)),  #

            # 13 row
            ('SPAN', (0, 14), (4, 14)),  #
            ('SPAN', (5, 14), (9, 14)),  #

            # 14 row
            ('SPAN', (0, 15), (9, 15)),  #

            # 15 row
            ('SPAN', (0, 16), (9, 16)),  #

            # 16 row
            ('SPAN', (0, 17), (9, 17)),

            # 17 row
            ('SPAN', (0, 18), (9, 18)),  #

            # 18 row
            ('SPAN', (0, 19), (9, 19)),  #

            ('SPAN', (0, 20), (9, 20)),  # Periodizzazione

            # 3 row
            ('SPAN', (0, 21), (2, 21)),  #
            ('SPAN', (3, 21), (4, 21)),  #
            ('SPAN', (5, 21), (6, 21)),  #
            ('SPAN', (7, 21), (9, 21)),  #

            ('VALIGN', (0, 0), (-1, -1), 'TOP')

        ]

        t = Table(cell_schema, colWidths=50, rowHeights=None, style=table_style)

        return t
        
    def create_sheet_en(self):
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
        intestazione = Paragraph("<b>TAPHONOMY FORM<br/>" + str(self.datestrfdate()) + "</b>", styNormal)

        # intestazione2 = Paragraph("<b>pyArchInit</b><br/>pyarchinit", styNormal)

        # intestazione2  = Paragraph("<b>Ditta esecutrice</b><br/>", styNormal)
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

        ##      if test_image.drawWidth < 800:

        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch

        # 1 row
        sito = Paragraph("<b>Site</b><br/>" + str(self.sito), styNormal)
        sigla_struttura = Paragraph("<b>Structure code</b><br/>" + str(self.sigla_struttura) + str(self.nr_struttura),
                                    styNormal)
        nr_individuo = Paragraph("<b>Individual Nr.</b><br/>" + str(self.nr_individuo), styNormal)
        nr_scheda = Paragraph("<b>Form Nr.</b><br/>" + str(self.nr_scheda_taf), styNormal)

        # 2 row
        periodizzazione = Paragraph("<b>PERIODIZATION OF RITUAL GRAVE</b><br/>", styNormal)

        # 3 row
        if str(self.periodo_iniziale) == "None":
            periodo_iniziale = Paragraph("<b>Starting Period</b><br/>", styNormal)
        else:
            periodo_iniziale = Paragraph("<b>Starting Period</b><br/>" + str(self.periodo_iniziale), styNormal)

        if str(self.fase_iniziale) == "None":
            fase_iniziale = Paragraph("<b>Starting Phase</b><br/>", styNormal)
        else:
            fase_iniziale = Paragraph("<b>Starting Phase</b><br/>" + str(self.fase_iniziale), styNormal)

        if str(self.periodo_finale) == "None":
            periodo_finale = Paragraph("<b>Final Period</b><br/>", styNormal)
        else:
            periodo_finale = Paragraph("<b>Final Period</b><br/>" + str(self.periodo_finale), styNormal)

        if str(self.fase_finale) == "None":
            fase_finale = Paragraph("<b>Final Phase</b><br/>", styNormal)
        else:
            fase_finale = Paragraph("<b>Final Phase</b><br/>" + str(self.fase_finale), styNormal)

        # 4 row
        if str(self.datazione_estesa) == "None":
            datazione_estesa = Paragraph("<b>Letteral datation</b><br/>", styNormal)
        else:
            datazione_estesa = Paragraph("<b>Letteral datation</b><br/>" + self.datazione_estesa, styNormal)

        # 5 row
        elementi_strutturali = Paragraph("<b>STRUCTURAL ELEMENTS</b><br/>", styNormal)

        # 6row
        tipo_contenitore_resti = Paragraph("<b>Container type</b><br/>" + self.tipo_contenitore_resti,
                                           styNormal)
        tipo_copertura = Paragraph("<b>Covering type</b><br/>" + self.copertura_tipo, styNormal)
        segnacoli = Paragraph("<b>Marker</b><br/>" + self.segnacoli, styNormal)
        canale_libatorio = Paragraph("<b>Canal libatorio</b><br/>" + self.canale_libatorio_si_no, styNormal)

        # 7 row
        dati_deposizionali = Paragraph("<b>INHUMED DEPOSITIONAL DATA</b><br/>", styNormal)

        # 8 row
        rito = Paragraph("<b>Rite</b><br/>" + self.rito, styNormal)
        orientamento_asse = Paragraph("<b>Axes orientation</b><br/>" + str(self.orientamento_asse), styNormal)
        if str(self.orientamento_azimut) == "None":
            orientamento_azimut = Paragraph("<b>Azimut</b><br/>", styNormal)
        else:
            orientamento_azimut_conv = self.PU.conversione_numeri(self.orientamento_azimut)
            orientamento_azimut = Paragraph("<b>Azimut</b><br/>" + orientamento_azimut_conv + "°", styNormal)
        posizione_cranio = Paragraph("<b>Skull position</b><br/>" + str(self.posizione_cranio), styNormal)

        # 9 row
        posizione_scheletro = Paragraph("<b>Skeleton position</b><br/>" + str(self.posizione_scheletro), styNormal)
        if str(self.lunghezza_scheletro) == "None":
            lunghezza_scheletro = Paragraph("<b>Skeleton length</b><br/>", styNormal)
        else:
            lunghezza_scheletro_conv = self.PU.conversione_numeri(self.lunghezza_scheletro)
            lunghezza_scheletro = Paragraph("<b>Skeleton length</b><br/>" + lunghezza_scheletro_conv + " m",
                                            styNormal)
        posizione_arti_superiori = Paragraph(
            "<b>Upper limb position</b><br/>" + str(self.posizione_arti_superiori), styNormal)
        posizione_arti_inferiori = Paragraph(
            "<b>Lower limb position</b><br/>" + str(self.posizione_arti_inferiori), styNormal)

        # 10 row
        dati_postdeposizionali = Paragraph("<b>POSTDEPOSITIONAL DATA</b><br/>", styNormal)

        # 11 row
        stato_conservazione = Paragraph("<b>Status of conservation</b><br/>" + str(self.stato_di_conservazione),
                                        styNormal)
        disturbato = Paragraph("<b>Hampered</b><br/>" + str(self.disturbato_si_no), styNormal)
        completo = Paragraph("<b>Complete</b><br/>" + str(self.completo_si_no), styNormal)
        in_connessione = Paragraph("<b>In connection</b><br/>" + str(self.in_connessione_si_no), styNormal)

        # 12 row
        caratteristiche_tafonomiche = ''
        caratteristiche_list = eval(self.caratteristiche)
        if len(caratteristiche_list) > 0:
            for i in caratteristiche_list:
                if caratteristiche_tafonomiche == '':
                    caratteristiche_tafonomiche = ("<br/>Features: %s, position: %s") % (str(i[0]), str(i[1]))
                else:
                    caratteristiche_tafonomiche += ("<br/><br/>Features: %s, position: %s") % (
                    str(i[0]), str(i[1]))

        caratteristiche_tafonomiche_txt = Paragraph(
            "<b>TAPHONOMIC FEATURES</b><br/>" + caratteristiche_tafonomiche, styNormal)

        # 13 row
        descrizione = ''
        try:
            descrizione = Paragraph("<b>Description</b><br/>" + self.descrizione_taf, styDescrizione)
        except:
            pass

        interpretazione = ''
        try:
            interpretazione = Paragraph("<b>Interpretation</b><br/>" + self.interpretazione_taf, styDescrizione)
        except:
            pass

        # 14 row
        corredo = Paragraph("<b>TROUSSEAU</b><br/>", styNormal)

        # 15 row
        corredo_presente = Paragraph("<b>Presenze</b><br/>" + self.corredo_presenza, styDescrizione)

        # 16 row
        corredo_descrizione = Paragraph("<b>Description</b><br/>" + self.corredo_descrizione, styDescrizione)

        # 17 row
        corredo_tipo = ''
        if len(self.corredo_tipo) > 0:
            for i in eval(self.corredo_tipo):
                if corredo_tipo == '':
                    try:
                        corredo_tipo += ("<br/>Artefact N° %s, Trousseau type: %s, Description: %s") % (
                        str(i[0]), str(i[1]), str(i[2]))
                    except:
                        pass
                else:
                    try:
                        corredo_tipo += ("<br/>Artefact N° %s, Trousseau type: %s, Description: %s") % (
                        str(i[0]), str(i[1]), str(i[2]))
                    except:
                        pass

        corredo_tipo_txt = Paragraph("<b>Single items of trousseau</b><br/>" + corredo_tipo, styNormal)

        # 18 row
        misure_tomba = ''
        if len(self.misure_tomba) > 0:
            for i in eval(self.misure_tomba):
                if misure_tomba == '':
                    try:
                        misure_tomba += ("%s: %s %s") % (str(i[0]), str(i[2]), str(i[1]))
                    except:
                        pass
                else:
                    try:
                        misure_tomba += ("<br/>%s: %s %s") % (str(i[0]), str(i[2]), str(i[1]))
                    except:
                        pass

        misure_tomba_txt = Paragraph("<b>Measurement</b><br/>" + misure_tomba, styNormal)

        # 19 row
        quote_tomba = Paragraph("<b>INDIVIDUAL AND STRUCTURE ELEVATION </b><br/>", styNormal)

        # 20 row
        quota_min_ind = Paragraph("<b>Elev. min ind.</b><br/>" + str(self.quota_min_ind), styNormal)
        quota_max_ind = Paragraph("<b>Elev. max ind.</b><br/>" + str(self.quota_max_ind), styNormal)
        quota_min_strutt = Paragraph("<b>Elev. min str.</b><br/>" + str(self.quota_min_strutt), styNormal)
        quota_max_strutt = Paragraph("<b>Elev. max str.</b><br/>" + str(self.quota_max_strutt), styNormal)

        # schema
        cell_schema = [  # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],  # 0 row  ok
            [sito, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 1 row ok
            [sigla_struttura, '01', '02', '03', '04', nr_individuo, '06', '07', nr_scheda, '09'],  # 1 row ok
            [periodizzazione, '01', '02', '03', '04', '07', '06', '07', '08', '09'],  # 2 row ok
            [periodo_iniziale, '01', '02', fase_iniziale, '04', periodo_finale, '06', fase_finale, '08', '09'],
            # 3 row ok
            [datazione_estesa, '01', '02', '03', '04', '07', '06', '07', '08', '09'],  # 4 row ok
            [elementi_strutturali, '01', '02', '03', '04', '07', '06', '07', '08', '09'],  # 5 row ok
            [tipo_contenitore_resti, '01', '02', tipo_copertura, '04', segnacoli, '06', canale_libatorio, '08'],
            # 6 row ok
            [dati_deposizionali, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 7 row ok
            [rito, '01', '02', orientamento_asse, '04', orientamento_azimut, '06', posizione_cranio, '08', '09'],
            # 8 row ok
            [posizione_scheletro, '01', lunghezza_scheletro, '03', posizione_arti_superiori, '05', '06',
             posizione_arti_inferiori, '08', '09'],  # 9 row ok
            [dati_postdeposizionali, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 10 row ok
            [stato_conservazione, '01', '02', disturbato, '04', completo, '06', in_connessione, '08'],  # 11 row ok
            [caratteristiche_tafonomiche_txt, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 12 row ok
            [descrizione, '01', '02', '03', '04', interpretazione, '06', '07', '08', '09'],  # 13 row ok
            [corredo, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 14 row ok
            [corredo_presente, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 15 ow
            [corredo_descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 16 row
            [corredo_tipo_txt, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 17 row
            [misure_tomba_txt, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 18 row
            [quote_tomba, '01', '02', '03', '04', '07', '06', '07', '08', '09'],  # 19 row ok
            [quota_min_ind, '01', '02', quota_max_ind, '04', quota_min_strutt, '06', quota_max_strutt, '08', '09']
            # 20 row ok
        ]

        # table style
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row
            ('SPAN', (0, 0), (6, 0)),  # intestazione
            ('SPAN', (7, 0), (9, 0)),  # intestazione

            # 1 row
            ('SPAN', (0, 1), (9, 1)),  # sito

            # 2
            ('SPAN', (0, 2), (4, 2)),  # dati identificativi
            ('SPAN', (5, 2), (7, 2)),  # dati identificativi
            ('SPAN', (8, 2), (9, 2)),  # dati identificativi

            # 2 row
            ('SPAN', (0, 3), (9, 3)),  # Periodizzazione

            # 3 row
            ('SPAN', (0, 4), (2, 4)),  #
            ('SPAN', (3, 4), (4, 4)),  #
            ('SPAN', (5, 4), (6, 4)),  #
            ('SPAN', (7, 4), (9, 4)),  #

            # 4 row
            ('SPAN', (0, 5), (9, 5)),  # datazione estesa
            ##################################
            # 5 row
            ('SPAN', (0, 6), (9, 6)),  # Elementi strutturali

            # 6 row
            ('SPAN', (0, 7), (2, 7)),  #
            ('SPAN', (3, 7), (4, 7)),  #
            ('SPAN', (5, 7), (6, 7)),  #
            ('SPAN', (7, 7), (9, 7)),  #

            # 7 row
            ('SPAN', (0, 8), (9, 8)),  #

            # 8 row
            ('SPAN', (0, 9), (2, 9)),  #
            ('SPAN', (3, 9), (4, 9)),  #
            ('SPAN', (5, 9), (6, 9)),  #
            ('SPAN', (7, 9), (9, 9)),  #

            # 9 row
            ('SPAN', (0, 10), (1, 10)),  #
            ('SPAN', (2, 10), (3, 10)),  #
            ('SPAN', (4, 10), (6, 10)),  #
            ('SPAN', (7, 10), (9, 10)),  #

            # 10 row
            ('SPAN', (0, 11), (9, 11)),  #

            # 11 row
            ('SPAN', (0, 12), (2, 12)),  #
            ('SPAN', (3, 12), (4, 12)),  #
            ('SPAN', (5, 12), (6, 12)),  #
            ('SPAN', (7, 12), (9, 12)),  #

            # 12 row
            ('SPAN', (0, 13), (9, 13)),  #

            # 13 row
            ('SPAN', (0, 14), (4, 14)),  #
            ('SPAN', (5, 14), (9, 14)),  #

            # 14 row
            ('SPAN', (0, 15), (9, 15)),  #

            # 15 row
            ('SPAN', (0, 16), (9, 16)),  #

            # 16 row
            ('SPAN', (0, 17), (9, 17)),

            # 17 row
            ('SPAN', (0, 18), (9, 18)),  #

            # 18 row
            ('SPAN', (0, 19), (9, 19)),  #

            ('SPAN', (0, 20), (9, 20)),  # Periodizzazione

            # 3 row
            ('SPAN', (0, 21), (2, 21)),  #
            ('SPAN', (3, 21), (4, 21)),  #
            ('SPAN', (5, 21), (6, 21)),  #
            ('SPAN', (7, 21), (9, 21)),  #

            ('VALIGN', (0, 0), (-1, -1), 'TOP')

        ]

        t = Table(cell_schema, colWidths=50, rowHeights=None, style=table_style)

        return t    
class generate_tomba_pdf(object):
    L=QgsSettings().value("locale/userLocale")[0:2]
    HOME = os.environ['PYARCHINIT_HOME']

    PDF_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def build_Tomba_sheets(self, records):
        elements = []
        for i in range(len(records)):
            single_tomba_sheet = single_Tomba_pdf_sheet(records[i])
            elements.append(single_tomba_sheet.create_sheet())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'scheda_Tafonomica.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_TOMBAsheet)
        f.close()
    def build_Tomba_sheets_de(self, records):
        elements = []
        for i in range(len(records)):
            single_tomba_sheet = single_Tomba_pdf_sheet(records[i])
            elements.append(single_tomba_sheet.create_sheet_de())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Formular_taphonomie.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_TOMBAsheet)
        f.close()
    def build_Tomba_sheets_en(self, records):
        elements = []
        for i in range(len(records)):
            single_tomba_sheet = single_Tomba_pdf_sheet(records[i])
            elements.append(single_tomba_sheet.create_sheet_en())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Taphonomic_form.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_TOMBAsheet)
        f.close()   
    def build_index_Tomba(self, records, sito):

        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        
        if self.L=='de':
            logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo_de.jpg')
        else:
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
        styNormal.fontSize = 7
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        styH1 = styleSheet['Heading3']

        data = self.datestrfdate()

        ###################### ELENCO SCHEDE TAFONOMICHE ###########

        lst = []
        lst.append(logo)
        if self.L=='it':
        
            lst.append(Paragraph("<b>ELENCO SCHEDE TAFONOMICHE</b><br/><b>Scavo: %s,  Data: %s</b>" % (sito, data), styH1))
        elif self.L=='de':
        
            lst.append(Paragraph("<b>LISTE FORMULAR TAPHOMIE</b><br/><b>Ausgrabungsstätte: %s,  Datum: %s</b>" % (sito, data), styH1))
            
        else:
        
            lst.append(Paragraph("<b>LIST TAPHONOMIC FORM</b><br/><b>Site: %s,  Date: %s</b>" % (sito, data), styH1)) 
        
        table_data = []
        
        if self.L=='it':
            for i in range(len(records)):
                exp_index = Tomba_index_pdf_sheet(records[i])
                table_data.append(exp_index.getTable())
        elif self.L=='de':
            for i in range(len(records)):
                exp_index = Tomba_index_pdf_sheet(records[i])
                table_data.append(exp_index.getTable_de())
        else:
            for i in range(len(records)):
                exp_index = Tomba_index_pdf_sheet(records[i])
                table_data.append(exp_index.getTable_en())      
                
        styles = exp_index.makeStyles()
        colWidths = [50, 80, 80, 80, 100, 60, 50, 60, 60, 60, 60, 150]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        # lst.append(Spacer(0,2))

        if self.L=='it':
            filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Elenco_tomba.pdf')
        elif self.L=='it':
            filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Listen_thaphonomie.pdf')
        else:
            filename = '{}{}{}'.format(self.PDF_path, os.sep, 'List_taphonomic.pdf')    
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(29 * cm, 21 * cm), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_TOMBAindex)

        f.close()

        ###################### ELENCO SCHEDE STRUTTURE TAFONOMICHE ###########

        lst = []
        lst.append(logo)

        if self.L=='it':
        
            lst.append(Paragraph("<b>ELENCO SCHEDE TAFONOMICHE</b><br/><b>Scavo: %s,  Data: %s</b>" % (sito, data), styH1))
        elif self.L=='de':
        
            lst.append(Paragraph("<b>LISTEN FORMULAR TAPHONOMIE</b><br/><b>Ausgrabungsstätte: %s,  Datum: %s</b>" % (sito, data), styH1))
            
        else:
        
            lst.append(Paragraph("<b>LIST TAPHONOMIC FORM</b><br/><b>Site: %s,  Date: %s</b>" % (sito, data), styH1))   

        table_data = []
        if self.L=='it':
            for i in range(len(records)):
                exp_index = Tomba_index_II_pdf_sheet(records[i])
                table_data.append(exp_index.getTable())
        elif self.L=='de':
            for i in range(len(records)):
                exp_index = Tomba_index_II_pdf_sheet(records[i])
                table_data.append(exp_index.getTable_de())
                
        else:
            for i in range(len(records)):
                exp_index = Tomba_index_II_pdf_sheet(records[i])
                table_data.append(exp_index.getTable_en())

                
        styles = exp_index.makeStyles()
        colWidths = [50, 50, 40, 100, 60, 50, 50, 60, 60, 60, 80]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        # lst.append(Spacer(0,2))
        if self.L=='it':
            filename = '{}{}{}'.format(self.PDF_path, os.sep, 'elenco_strutture_tomba.pdf')
        elif self.L=='it':
            filename = '{}{}{}'.format(self.PDF_path, os.sep, 'listen_thaphonomie_struktur.pdf')
        else:
            filename = '{}{}{}'.format(self.PDF_path, os.sep, 'List taphonomic structure.pdf')  
        
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(29 * cm, 21 * cm), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_TOMBAindex)

        f.close()

