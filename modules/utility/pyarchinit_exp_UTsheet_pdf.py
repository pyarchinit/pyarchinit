
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

from ..db.pyarchinit_conn_strings import Connection
from .pyarchinit_OS_utility import *
from PIL import Image as giggino
from reportlab.lib.utils import ImageReader

class NumberedCanvas_UTsheet(canvas.Canvas):
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
        self.setFont("Cambria", 6)
        self.drawRightString(200 * mm, 20 * mm,
                             "Pag. %d di %d" % (self._pageNumber, page_count))  # scheda us verticale 200mm x 20 mm


class NumberedCanvas_UTindex(canvas.Canvas):
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


class single_UT_pdf_sheet(object):
    def __init__(self, data):
        self.progetto = data[0]  # 1
        self.nr_ut = data[1]  # 2
        #self.ut_letterale = data[2]  # 3
        self.def_ut = data[3]  # 4
        self.descrizione_ut = data[4]  # 5
        self.interpretazione_ut = data[5]  # 6
        self.nazione = data[6]  # 7
        self.regione = data[7]  # 8
        self.provincia = data[8]  # 9
        self.comune = data[9]  # 10
        self.frazione = data[10]  # 11
        self.localita = data[11]  # 12
        self.indirizzo = data[12]  # 13
        self.nr_civico = data[13]  # 14
        self.carta_topo_igm = data[14]  # 15
        self.carta_ctr = data[15]  # 16
        self.coord_geografiche = data[16]  # 17
        self.coord_piane = data[17]  # 18
        self.quota = data[18]  # 19
        self.andamento_terreno_pendenza = data[19]  # 20
        self.utilizzo_suolo_vegetazione = data[20]  # 21
        self.descrizione_empirica_suolo = data[21]  # 22
        self.descrizione_luogo = data[22]  # 23
        self.metodo_rilievo_e_ricognizione = data[23]  # 24
        self.geometria = data[24]  # 25
        self.bibliografia = data[25]  # 26
        self.data = data[26]  # 27
        self.ora_meteo = data[27]  # 28
        self.responsabile = data[28]  # 29
        self.dimensioni_ut = data[29]  # 30
        self.rep_per_mq = data[30]  # 31
        self.rep_datanti = data[31]  # 32
        self.periodo_I = data[32]  # 33
        self.datazione_I = data[33]  # 34
        self.interpretazione_I = data[34]  # 35
        self.periodo_II = data[35]  # 36
        self.datazione_II = data[36]  # 37
        self.interpretazione_II = data[37]  # 38
        self.documentazione = data[38]  # 39
        self.enti_tutela_vincoli = data[39]  # 40
        self.indagini_preliminari = data[40]
        # New survey fields (v4.9.21+)
        self.visibility_percent = str(data[41]) if len(data) > 41 and data[41] is not None else ''
        self.vegetation_coverage = str(data[42]) if len(data) > 42 and data[42] else ''
        self.gps_method = str(data[43]) if len(data) > 43 and data[43] else ''
        self.coordinate_precision = str(data[44]) if len(data) > 44 and data[44] is not None else ''
        self.survey_type = str(data[45]) if len(data) > 45 and data[45] else ''
        self.surface_condition = str(data[46]) if len(data) > 46 and data[46] else ''
        self.accessibility = str(data[47]) if len(data) > 47 and data[47] else ''
        self.photo_documentation = 'Sì' if len(data) > 48 and data[48] else 'No'
        self.weather_conditions = str(data[49]) if len(data) > 49 and data[49] else ''
        self.team_members = str(data[50]) if len(data) > 50 and data[50] else ''
        self.foglio_catastale = str(data[51]) if len(data) > 51 and data[51] else ''

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def create_sheet(self):

        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.fontSize = 5
        styNormal.fontName='Cambria'
        styNormal.alignment = 0  # LEFT

        styleSheet = getSampleStyleSheet()
        styNormal2 = styleSheet['Normal']
        styNormal2.spaceBefore = 20
        styNormal2.spaceAfter = 20
        styNormal2.fontSize = 5
        styNormal2.fontName='Cambria'
        styNormal2.alignment = 1  # LEFT
        
        
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
        styDescrizione.fontSize = 5
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
        styTitoloComponenti.fontSize = 5
        styTitoloComponenti.fontName='Cambria'
        styTitoloComponenti.alignment = 1  # CENTER

        styleSheet = getSampleStyleSheet()
        styVerticale = styleSheet['Normal']
        styVerticale.spaceBefore = 20
        styVerticale.spaceAfter = 20
        styVerticale.fontSize = 5
        styVerticale.fontName='Cambria'
        styVerticale.alignment = 1  # CENTER
        styVerticale.leading=8

        # format labels

        # 0 row
        intestazione = Paragraph("<b>SCHEDA DI UNIT&Agrave; TOPOGRAFICA<br/>" + str(self.datestrfdate()) + "</b>",
                                 styNormal)
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

        logo.drawHeight = 2 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 2 * inch
        logo.hAlign = 'CENTER'
        lst = []
        lst2=[]
        lst.append(logo)
        # intestazione2 = Paragraph("<b>pyArchInit</b><br/>www.pyarchinit.blogspot.com", styNormal)

        # 1 row
        progetto = Paragraph("<b>PROGETTO</b><br/>" + str(self.progetto), styNormal)
        UT = Paragraph("<b>N° UT</b><br/>" + str(self.nr_ut), styNormal)
        #UTletterale = Paragraph("<b>UT letterale</b><br/>" + str(self.ut_letterale), styNormal)

        # 2 row
        descrizione_ut = Paragraph("<b>DESCRIZIONE UT</b><br/>" + self.descrizione_ut, styNormal)
        interpretazione_ut = Paragraph("<b>INTEPRETAZIONE UT</b><br/>" + self.interpretazione_ut, styNormal)

        # 3 row
        nazione = Paragraph("<b>NAZIONE</b><br/>" + self.nazione, styNormal)
        regione = Paragraph("<b>REGIONE</b><br/>" + self.regione, styNormal)
        provincia = Paragraph("<b>PROVINCIA</b><br/>" + self.provincia, styNormal)
        comune = Paragraph("<b>COMUNE</b><br/>" + self.comune, styNormal)
        frazione = Paragraph("<b>FRAZIONE</b><br/>" + self.frazione, styNormal)
        localita = Paragraph("<b>LOCALIZZAZIONE</b><br/>" + self.localita, styNormal)
        indirizzo = Paragraph("<b>INDIRIZZO</b><br/>" + self.indirizzo, styNormal)
        nr_civico = Paragraph("<b>NR CIVICO</b><br/>" + self.nr_civico, styNormal)
        carta_topo_igm = Paragraph("<b>IGM</b><br/>" + self.carta_topo_igm, styNormal)
        carta_ctr = Paragraph("<b>CTR</b><br/>" + self.carta_ctr, styNormal)
        coord_geografiche = Paragraph("<b>COORDINATE GEOGRAFICHE</b><br/>" + self.coord_geografiche, styNormal)
        coord_piane = Paragraph("<b>COORDINATE PIANE</b><br/>" + self.coord_piane, styNormal)
        quota = Paragraph("<b>QUOTA</b><br/>" + self.quota, styNormal)
        andamento_terreno_pendenza = Paragraph("<b>PENDENZA</b><br/>" + self.andamento_terreno_pendenza, styNormal)
        utilizzo_suolo_vegetazione = Paragraph("<b>UTILIZZO SUOLO</b><br/>" + self.utilizzo_suolo_vegetazione,
                                               styNormal)
        descrizione_empirica_suolo = Paragraph(
            "<b>DESCRIZIONE EMPIRICA SUOLO</b><br/>" + self.descrizione_empirica_suolo, styNormal)
        descrizione_luogo = Paragraph("<b>DESCRIZIONE SUOLO</b><br/>" + self.descrizione_luogo, styNormal)
        metodo_rilievo_e_ricognizione = Paragraph("<b>TIPO RICOGNIZIONE</b><br/>" + self.metodo_rilievo_e_ricognizione,
                                                  styNormal)
        geometria = Paragraph("<b>GEOMETRIA</b><br/>" + self.geometria, styNormal)
        bibliografia = Paragraph("<b>BIBLIOGRAFIA</b><br/>" + self.bibliografia, styNormal)
        data = Paragraph("<b>DATA</b><br/>" + self.data, styNormal)
        ora_meteo = Paragraph("<b>ORA E METEO</b><br/>" + self.ora_meteo, styNormal)
        responsabile = Paragraph("<b>RESPONSABILE</b><br/>" + self.responsabile, styNormal)
        dimensioni_ut = Paragraph("<b>DIMENSIONI UT</b><br/>" + self.dimensioni_ut, styNormal)
        rep_per_mq = Paragraph("<b>Q.T&Agrave; PER MQ </b><br/>" + self.rep_per_mq, styNormal)
        rep_datanti = Paragraph("<b>Q.T&Agrave; DATANTI</b><br/>" + self.rep_datanti, styNormal)
        periodo_I = Paragraph("<b>DATAZIONE</b><br/>" + self.periodo_I, styNormal)
        datazione_I = Paragraph("<b>Datazione I</b><br/>" + self.datazione_I, styNormal)
        interpretazione_I = Paragraph("<b>Interpretazione I</b><br/>" + self.interpretazione_I, styNormal)
        periodo_II = Paragraph("<b>Periodo II</b><br/>" + self.periodo_II, styNormal)
        datazione_II = Paragraph("<b>Datazione II</b><br/>" + self.datazione_II, styNormal)
        interpretazione_II = Paragraph("<b>Interpretazione II</b><br/>" + self.interpretazione_II, styNormal)
        documentazione = Paragraph("<b>Documentazione</b><br/>" + self.documentazione, styNormal)
        enti_tutela_vincoli = Paragraph("<b>Enti tutela e vincoli</b><br/>" + self.enti_tutela_vincoli, styNormal)
        indagini_preliminari = Paragraph("<b>Indagini preliminari</b><br/>" + self.indagini_preliminari, styNormal)

        # New survey fields (v4.9.21+)
        visibility_percent = Paragraph("<b>VISIBILIT&Agrave; (%)</b><br/>" + self.visibility_percent, styNormal)
        vegetation_coverage = Paragraph("<b>COPERTURA VEGETALE</b><br/>" + self.vegetation_coverage, styNormal)
        gps_method = Paragraph("<b>METODO GPS</b><br/>" + self.gps_method, styNormal)
        coordinate_precision = Paragraph("<b>PRECISIONE GPS (m)</b><br/>" + self.coordinate_precision, styNormal)
        survey_type = Paragraph("<b>TIPO SURVEY</b><br/>" + self.survey_type, styNormal)
        surface_condition = Paragraph("<b>CONDIZIONE SUPERFICIE</b><br/>" + self.surface_condition, styNormal)
        accessibility = Paragraph("<b>ACCESSIBILIT&Agrave;</b><br/>" + self.accessibility, styNormal)
        photo_documentation = Paragraph("<b>DOC. FOTOGRAFICA</b><br/>" + self.photo_documentation, styNormal)
        weather_conditions = Paragraph("<b>CONDIZIONI METEO</b><br/>" + self.weather_conditions, styNormal)
        team_members = Paragraph("<b>TEAM SURVEY</b><br/>" + self.team_members, styNormal)
        foglio_catastale = Paragraph("<b>FOGLIO CATASTALE</b><br/>" + self.foglio_catastale, styNormal)

        # schema
        cell_schema = [  # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09','10','11','12','13','14','15','16','17'],  # 0 row
            [progetto, '01', '02', '03', '04', UT, '06', '07','08', '09','10','11','12','13','14','15','16','17'],  # 1 row
            [descrizione_ut, '01', '02', '03', '04','04', '05', '06', '07','08', '09','10','11','12','13','14','15','16','17'],  # 2 row
            [interpretazione_ut, '01', '02', '03', '04', '05', '06', '07', '08', '09','10','11','12','13','14','15','16','17'],  # 3 row
            [nazione, '01', provincia, '03', regione,'05', '06', comune, '08', '9', '10','11','12','13','14','15','16','17'],  # 4 row
            [frazione, '01', localita, '03', indirizzo, '05', nr_civico,'07', '08', '09', '10','11','12','13','14','15','16','17'],  # 5 row
            [carta_topo_igm, '01', carta_ctr, '03', coord_geografiche, '05', coord_piane,'07', '08', '09', '10','11','12','13','14','15','16','17'],  # 6 row
            [foglio_catastale, '01', gps_method, '03', coordinate_precision, '05', '06', '07','08', '09', '10','11','12','13','14','15','16','17'],  # 7 row NEW
            [quota, '01', andamento_terreno_pendenza, '03', utilizzo_suolo_vegetazione, '05',descrizione_empirica_suolo, '07','08', '09', '10','11','12','13','14','15','16','17'],  # 8 row
            [descrizione_luogo, '01', metodo_rilievo_e_ricognizione, '03', geometria, '05', bibliografia, '07','08', '09', '10','11','12','13','14','15','16','17'],  # 9 row
            [data, '01', ora_meteo, '03', responsabile, '05', dimensioni_ut, '07','08', '09', '10','11','12','13','14','15','16','17'],  # 10 row
            [survey_type, '01', visibility_percent, '03', weather_conditions, '05', team_members,'07', '08', '09', '10','11','12','13','14','15','16','17'],  # 11 row NEW
            [vegetation_coverage, '01', surface_condition, '03', accessibility, '05', photo_documentation,'07', '08', '09', '10','11','12','13','14','15','16','17'],  # 12 row NEW
            [rep_per_mq, '01', rep_datanti, '03', periodo_I, '05', datazione_I,'07', '08', '09', '10','11','12','13','14','15','16','17'],  # 13 row
            [interpretazione_I, '01', periodo_II, '03', datazione_II, '05', interpretazione_II, '07','08', '09', '10','11','12','13','14','15','16','17'],  # 14 row
            [documentazione, '01', '02', enti_tutela_vincoli,  '04', indagini_preliminari,'06', '07', '08','09', '10','11','12','13','14','15','16','17']  # 15 row
        ]

        # table style
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row - intestazione
            ('SPAN', (0, 0), (6, 0)),
            ('SPAN', (7, 0), (9, 0)),
            # 1 row - progetto, UT
            ('SPAN', (0, 1), (4, 1)),
            ('SPAN', (5, 1), (7, 1)),
            ('SPAN', (8, 1), (9, 1)),
            # 2-3 rows - descrizione, interpretazione
            ('SPAN', (0, 2), (9, 2)),
            ('SPAN', (0, 3), (9, 3)),
            # 4 row - nazione, provincia, regione, comune
            ('SPAN', (0, 4), (1, 4)),
            ('SPAN', (2, 4), (3, 4)),
            ('SPAN', (4, 4), (5, 4)),
            ('SPAN', (6, 4), (9, 4)),
            # 5 row - frazione, localita, indirizzo, nr_civico
            ('SPAN', (0, 5), (1, 5)),
            ('SPAN', (2, 5), (3, 5)),
            ('SPAN', (4, 5), (5, 5)),
            ('SPAN', (6, 5), (9, 5)),
            # 6 row - carte, coordinate
            ('SPAN', (0, 6), (1, 6)),
            ('SPAN', (2, 6), (3, 6)),
            ('SPAN', (4, 6), (5, 6)),
            ('SPAN', (6, 6), (9, 6)),
            # 7 row NEW - foglio_catastale, gps_method, coordinate_precision
            ('SPAN', (0, 7), (1, 7)),
            ('SPAN', (2, 7), (3, 7)),
            ('SPAN', (4, 7), (9, 7)),
            # 8 row - quota, pendenza, utilizzo_suolo, desc_empirica
            ('SPAN', (0, 8), (1, 8)),
            ('SPAN', (2, 8), (3, 8)),
            ('SPAN', (4, 8), (5, 8)),
            ('SPAN', (6, 8), (9, 8)),
            # 9 row - desc_luogo, metodo, geometria, biblio
            ('SPAN', (0, 9), (1, 9)),
            ('SPAN', (2, 9), (3, 9)),
            ('SPAN', (4, 9), (5, 9)),
            ('SPAN', (6, 9), (9, 9)),
            # 10 row - data, ora_meteo, responsabile, dimensioni
            ('SPAN', (0, 10), (1, 10)),
            ('SPAN', (2, 10), (3, 10)),
            ('SPAN', (4, 10), (5, 10)),
            ('SPAN', (6, 10), (9, 10)),
            # 11 row NEW - survey_type, visibility, weather, team
            ('SPAN', (0, 11), (1, 11)),
            ('SPAN', (2, 11), (3, 11)),
            ('SPAN', (4, 11), (5, 11)),
            ('SPAN', (6, 11), (9, 11)),
            # 12 row NEW - vegetation, surface, accessibility, photo_doc
            ('SPAN', (0, 12), (1, 12)),
            ('SPAN', (2, 12), (3, 12)),
            ('SPAN', (4, 12), (5, 12)),
            ('SPAN', (6, 12), (9, 12)),
            # 13 row - rep_per_mq, rep_datanti, periodo_I, datazione_I
            ('SPAN', (0, 13), (1, 13)),
            ('SPAN', (2, 13), (3, 13)),
            ('SPAN', (4, 13), (5, 13)),
            ('SPAN', (6, 13), (9, 13)),
            # 14 row - interpretazione_I, periodo_II, datazione_II, interp_II
            ('SPAN', (0, 14), (1, 14)),
            ('SPAN', (2, 14), (3, 14)),
            ('SPAN', (4, 14), (5, 14)),
            ('SPAN', (6, 14), (9, 14)),
            # 15 row - documentazione, enti_tutela, indagini_preliminari
            ('SPAN', (0, 15), (2, 15)),
            ('SPAN', (3, 15), (5, 15)),
            ('SPAN', (6, 15), (9, 15)),

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
        intestazione = Paragraph("<b>FORMULAR TE<br/>" + str(self.datestrfdate()) + "</b>",
                                 styNormal)
        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo_de.jpg')
        logo = Image(logo_path)

        ##      if test_image.drawWidth < 800:

        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch

        # intestazione2 = Paragraph("<b>pyArchInit</b><br/>www.pyarchinit.blogspot.com", styNormal)

        # 1 row
        progetto = Paragraph("<b>Project</b><br/>" + str(self.progetto), styNormal)
        UT = Paragraph("<b>N° TE</b><br/>" + str(self.nr_ut), styNormal)
        UTletterale = Paragraph("<b>TE<br/>" + str(self.ut_letterale), styNormal)

        # 2 row
        descrizione_ut = Paragraph("<b>Beschreibung TE</b><br/>" + self.descrizione_ut, styNormal)
        interpretazione_ut = Paragraph("<b>Deutung TE</b><br/>" + self.interpretazione_ut, styNormal)

        # 3 row
        nazione = Paragraph("<b>Nation</b><br/>" + self.nazione, styNormal)
        regione = Paragraph("<b>Region</b><br/>" + self.regione, styNormal)
        provincia = Paragraph("<b>Provinz</b><br/>" + self.provincia, styNormal)
        comune = Paragraph("<b>Stadt</b><br/>" + self.comune, styNormal)
        frazione = Paragraph("<b>Landkreis</b><br/>" + self.frazione, styNormal)
        localita = Paragraph("<b>Ort</b><br/>" + self.localita, styNormal)
        indirizzo = Paragraph("<b>Adress</b><br/>" + self.indirizzo, styNormal)
        nr_civico = Paragraph("<b>Hausnummer</b><br/>" + self.nr_civico, styNormal)
        carta_topo_igm = Paragraph("<b>Topographische Karte</b><br/>" + self.carta_topo_igm, styNormal)
        carta_ctr = Paragraph("<b>CTR</b><br/>" + self.carta_ctr, styNormal)
        coord_geografiche = Paragraph("<b>Geographische Koordinaten</b><br/>" + self.coord_geografiche, styNormal)
        coord_piane = Paragraph("<b>Planum-Koordinaten</b><br/>" + self.coord_piane, styNormal)
        quota = Paragraph("<b>Nivellement</b><br/>" + self.quota, styNormal)
        andamento_terreno_pendenza = Paragraph("<b>Hang-Trend</b><br/>" + self.andamento_terreno_pendenza, styNormal)
        utilizzo_suolo_vegetazione = Paragraph("<b>Verwendung Boden</b><br/>" + self.utilizzo_suolo_vegetazione,
                                               styNormal)
        descrizione_empirica_suolo = Paragraph(
            "<b>Empirische Beschreibung des Bodens</b><br/>" + self.descrizione_empirica_suolo, styNormal)
        descrizione_luogo = Paragraph("<b>Ortsbeschreibung</b><br/>" + self.descrizione_luogo, styNormal)
        metodo_rilievo_e_ricognizione = Paragraph("<b>Survey u. Oberflächenbegehung</b><br/>" + self.metodo_rilievo_e_ricognizione,
                                                  styNormal)
        geometria = Paragraph("<b>Geometrie</b><br/>" + self.geometria, styNormal)
        bibliografia = Paragraph("<bBibliographie</b><br/>" + self.bibliografia, styNormal)
        data = Paragraph("<b>Datum</b><br/>" + self.data, styNormal)
        ora_meteo = Paragraph("<b>Zeit / Wetter</b><br/>" + self.ora_meteo, styNormal)
        responsabile = Paragraph("<b>Verantwortlich</b><br/>" + self.responsabile, styNormal)
        dimensioni_ut = Paragraph("<b>TE-Größe (MQ)</b><br/>" + self.dimensioni_ut, styNormal)
        rep_per_mq = Paragraph("<b>Findet für MQ</b><br/>" + self.rep_per_mq, styNormal)
        rep_datanti = Paragraph("<b>Findet</b><br/>" + self.rep_datanti, styNormal)
        periodo_I = Paragraph("<b>Zeitraum I</b><br/>" + self.periodo_I, styNormal)
        datazione_I = Paragraph("<b>Dating I</b><br/>" + self.frazione, styNormal)
        interpretazione_I = Paragraph("<b>Interpretation I</b><br/>" + self.interpretazione_I, styNormal)
        periodo_II = Paragraph("<b>Zeitraum II</b><br/>" + self.periodo_II, styNormal)
        datazione_II = Paragraph("<b>Dating II</b><br/>" + self.datazione_II, styNormal)
        interpretazione_II = Paragraph("<b>Interpretation II</b><br/>" + self.interpretazione_II, styNormal)
        documentazione = Paragraph("<b>Dokumentation</b><br/>" + self.documentazione, styNormal)
        enti_tutela_vincoli = Paragraph("<b>Entitäten Schutz und Einschränkungen</b><br/>" + self.enti_tutela_vincoli, styNormal)
        indagini_preliminari = Paragraph("<b>Voruntersuchungen</b><br/>" + self.indagini_preliminari, styNormal)

        # New survey fields (v4.9.21+)
        foglio_catastale = Paragraph("<b>KATASTERBLATT</b><br/>" + self.foglio_catastale, styNormal)
        visibility_percent = Paragraph("<b>SICHTBARKEIT (%)</b><br/>" + self.visibility_percent, styNormal)
        vegetation_coverage = Paragraph("<b>VEGETATIONSBEDECKUNG</b><br/>" + self.vegetation_coverage, styNormal)
        gps_method = Paragraph("<b>GPS-METHODE</b><br/>" + self.gps_method, styNormal)
        coordinate_precision = Paragraph("<b>KOORDINATENGENAUIGKEIT (m)</b><br/>" + self.coordinate_precision, styNormal)
        survey_type = Paragraph("<b>SURVEY-TYP</b><br/>" + self.survey_type, styNormal)
        surface_condition = Paragraph("<b>OBERFLÄCHENZUSTAND</b><br/>" + self.surface_condition, styNormal)
        accessibility = Paragraph("<b>ZUGÄNGLICHKEIT</b><br/>" + self.accessibility, styNormal)
        photo_documentation = Paragraph("<b>FOTODOKUMENTATION</b><br/>" + self.photo_documentation, styNormal)
        weather_conditions = Paragraph("<b>WETTERBEDINGUNGEN</b><br/>" + self.weather_conditions, styNormal)
        team_members = Paragraph("<b>TEAMMITGLIEDER</b><br/>" + self.team_members, styNormal)

        # schema
        cell_schema = [  # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],  # 0 row ok
            [progetto, '01', '02', '03', '04', UT, '06', '07', UTletterale, '09'],  # 1 row ok
            [descrizione_ut, '01', '02', '03', '04'],
            [interpretazione_ut, '01', '02', '03', '04', '05', '06', '07', '08'],  # 2 row ok
            [nazione, '01', provincia, '03', regione, '06', comune, '9'],  # 3
            [frazione, '01', localita, '03', indirizzo, '05', nr_civico, '08', '09'],  # 4
            [carta_topo_igm, '01', carta_ctr, '03', coord_geografiche, '05', coord_piane, '08', '09'],  # 5
            # row 7 - survey fields
            [foglio_catastale, '01', gps_method, '03', coordinate_precision, '05', survey_type, '08', '09'],
            [quota, '01', andamento_terreno_pendenza, '03', utilizzo_suolo_vegetazione, '05',
             descrizione_empirica_suolo, '08', '09'],
            # 6
            [descrizione_luogo, '01', metodo_rilievo_e_ricognizione, '03', geometria, '05', bibliografia, '08', '09'],
            [data, '01', ora_meteo, '03', responsabile, '05', dimensioni_ut, '08', '09'],  # 7
            # row 11 - survey conditions
            [visibility_percent, '01', vegetation_coverage, '03', surface_condition, '05', accessibility, '08', '09'],
            # row 12 - survey documentation
            [weather_conditions, '01', team_members, '03', photo_documentation, '05', '06', '07', '08', '09'],
            [rep_per_mq, '01', rep_datanti, '03', periodo_I, '05', datazione_I, '08', '09'],  # 8
            [interpretazione_I, '01', periodo_II, '03', datazione_II, '05', interpretazione_II, '08', '09'],
            # 9
            [documentazione, '01', '02', enti_tutela_vincoli, '03', '04', indagini_preliminari, '09']
            # 10 row ok
        ]

        # table style
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row
            ('SPAN', (0, 0), (6, 0)),  # intestazione
            ('SPAN', (7, 0), (9, 0)),  # intestazione

            # 1 row
            ('SPAN', (0, 1), (4, 1)),  # dati identificativi
            ('SPAN', (5, 1), (7, 1)),  # dati identificativi
            ('SPAN', (8, 1), (9, 1)),  # dati identificativi

            # 2 row
            ('SPAN', (0, 2), (9, 2)),  # Definizione - interpretazone
            ('SPAN', (0, 3), (9, 3)),  # definizione - intepretazione

            # 4 row
            ('SPAN', (0, 4), (1, 4)),
            ('SPAN', (2, 4), (3, 4)),
            ('SPAN', (4, 4), (5, 4)),
            ('SPAN', (6, 4), (9, 4)),

            # 5 row
            ('SPAN', (0, 5), (1, 5)),
            ('SPAN', (2, 5), (3, 5)),
            ('SPAN', (4, 5), (5, 5)),
            ('SPAN', (6, 5), (9, 5)),

            # 6 row
            ('SPAN', (0, 6), (1, 6)),
            ('SPAN', (2, 6), (3, 6)),
            ('SPAN', (4, 6), (5, 6)),
            ('SPAN', (6, 6), (9, 6)),

            # 7 row - survey fields
            ('SPAN', (0, 7), (1, 7)),
            ('SPAN', (2, 7), (3, 7)),
            ('SPAN', (4, 7), (5, 7)),
            ('SPAN', (6, 7), (9, 7)),

            # 8 row
            ('SPAN', (0, 8), (1, 8)),
            ('SPAN', (2, 8), (3, 8)),
            ('SPAN', (4, 8), (5, 8)),
            ('SPAN', (6, 8), (9, 8)),

            # 9 row
            ('SPAN', (0, 9), (1, 9)),
            ('SPAN', (2, 9), (3, 9)),
            ('SPAN', (4, 9), (5, 9)),
            ('SPAN', (6, 9), (9, 9)),

            # 10 row
            ('SPAN', (0, 10), (1, 10)),
            ('SPAN', (2, 10), (3, 10)),
            ('SPAN', (4, 10), (5, 10)),
            ('SPAN', (6, 10), (9, 10)),

            # 11 row - survey conditions
            ('SPAN', (0, 11), (1, 11)),
            ('SPAN', (2, 11), (3, 11)),
            ('SPAN', (4, 11), (5, 11)),
            ('SPAN', (6, 11), (9, 11)),

            # 12 row - survey documentation
            ('SPAN', (0, 12), (1, 12)),
            ('SPAN', (2, 12), (3, 12)),
            ('SPAN', (4, 12), (9, 12)),

            # 13 row
            ('SPAN', (0, 13), (1, 13)),
            ('SPAN', (2, 13), (3, 13)),
            ('SPAN', (4, 13), (5, 13)),
            ('SPAN', (6, 13), (9, 13)),

            # 14 row
            ('SPAN', (0, 14), (1, 14)),
            ('SPAN', (2, 14), (3, 14)),
            ('SPAN', (4, 14), (5, 14)),
            ('SPAN', (6, 14), (9, 14)),

            # 15 row
            ('SPAN', (0, 15), (2, 15)),
            ('SPAN', (3, 15), (5, 15)),
            ('SPAN', (6, 15), (9, 15)),

            ('VALIGN', (0, 0), (-1, -1), 'TOP')

        ]

        # 4 row


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
        intestazione = Paragraph("<b>TOPOGRAPHIC FORM<br/>" + str(self.datestrfdate()) + "</b>",
                                 styNormal)
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

        # intestazione2 = Paragraph("<b>pyArchInit</b><br/>www.pyarchinit.blogspot.com", styNormal)

        # 1 row
        progetto = Paragraph("<b>Project</b><br/>" + str(self.progetto), styNormal)
        UT = Paragraph("<b>N° TU</b><br/>" + str(self.nr_ut), styNormal)
        UTletterale = Paragraph("<b>TU</b><br/>" + str(self.ut_letterale), styNormal)

        # 2 row
        descrizione_ut = Paragraph("<b>TU description</b><br/>" + self.descrizione_ut, styNormal)
        interpretazione_ut = Paragraph("<b>TU interpretation</b><br/>" + self.interpretazione_ut, styNormal)

        # 3 row
        nazione = Paragraph("<b>Nation</b><br/>" + self.nazione, styNormal)
        regione = Paragraph("<b>Region</b><br/>" + self.regione, styNormal)
        provincia = Paragraph("<b>Province</b><br/>" + self.provincia, styNormal)
        comune = Paragraph("<b>Town</b><br/>" + self.comune, styNormal)
        frazione = Paragraph("<b>Hamlet</b><br/>" + self.frazione, styNormal)
        localita = Paragraph("<b>Location</b><br/>" + self.localita, styNormal)
        indirizzo = Paragraph("<b>Adress</b><br/>" + self.indirizzo, styNormal)
        nr_civico = Paragraph("<b>Nr civic</b><br/>" + self.nr_civico, styNormal)
        carta_topo_igm = Paragraph("<b>IGM</b><br/>" + self.carta_topo_igm, styNormal)
        carta_ctr = Paragraph("<b>CTR</b><br/>" + self.carta_ctr, styNormal)
        coord_geografiche = Paragraph("<b>Coord. geographic</b><br/>" + self.coord_geografiche, styNormal)
        coord_piane = Paragraph("<b>Coord. plane</b><br/>" + self.coord_piane, styNormal)
        quota = Paragraph("<b>Elevation</b><br/>" + self.quota, styNormal)
        andamento_terreno_pendenza = Paragraph("<b>Slope</b><br/>" + self.andamento_terreno_pendenza, styNormal)
        utilizzo_suolo_vegetazione = Paragraph("<b>Soil reuse</b><br/>" + self.utilizzo_suolo_vegetazione,
                                               styNormal)
        descrizione_empirica_suolo = Paragraph(
            "<b>Description soil</b><br/>" + self.descrizione_empirica_suolo, styNormal)
        descrizione_luogo = Paragraph("<b>Description place</b><br/>" + self.descrizione_luogo, styNormal)
        metodo_rilievo_e_ricognizione = Paragraph("<b>Survey</b><br/>" + self.metodo_rilievo_e_ricognizione,
                                                  styNormal)
        geometria = Paragraph("<b>Geometry</b><br/>" + self.geometria, styNormal)
        bibliografia = Paragraph("<b>Bibliography</b><br/>" + self.bibliografia, styNormal)
        data = Paragraph("<b>Date</b><br/>" + self.data, styNormal)
        ora_meteo = Paragraph("<b>Time and meteo</b><br/>" + self.ora_meteo, styNormal)
        responsabile = Paragraph("<b>Responsable</b><br/>" + self.responsabile, styNormal)
        dimensioni_ut = Paragraph("<b>Dimension TU</b><br/>" + self.dimensioni_ut, styNormal)
        rep_per_mq = Paragraph("<b>Finds for square meter</b><br/>" + self.rep_per_mq, styNormal)
        rep_datanti = Paragraph("<b>Finds</b><br/>" + self.rep_datanti, styNormal)
        periodo_I = Paragraph("<b>Period I</b><br/>" + self.periodo_I, styNormal)
        datazione_I = Paragraph("<b>Datation I</b><br/>" + self.frazione, styNormal)
        interpretazione_I = Paragraph("<b>Interpretation I</b><br/>" + self.interpretazione_I, styNormal)
        periodo_II = Paragraph("<b>Period II</b><br/>" + self.periodo_II, styNormal)
        datazione_II = Paragraph("<b>Datation II</b><br/>" + self.datazione_II, styNormal)
        interpretazione_II = Paragraph("<b>Interpretation II</b><br/>" + self.interpretazione_II, styNormal)
        documentazione = Paragraph("<b>Documentation</b><br/>" + self.documentazione, styNormal)
        enti_tutela_vincoli = Paragraph("<b>Company constraints</b><br/>" + self.enti_tutela_vincoli, styNormal)
        indagini_preliminari = Paragraph("<b>Preliminary investigation</b><br/>" + self.indagini_preliminari, styNormal)

        # New survey fields (v4.9.21+)
        foglio_catastale = Paragraph("<b>CADASTRAL SHEET</b><br/>" + self.foglio_catastale, styNormal)
        visibility_percent = Paragraph("<b>VISIBILITY (%)</b><br/>" + self.visibility_percent, styNormal)
        vegetation_coverage = Paragraph("<b>VEGETATION COVERAGE</b><br/>" + self.vegetation_coverage, styNormal)
        gps_method = Paragraph("<b>GPS METHOD</b><br/>" + self.gps_method, styNormal)
        coordinate_precision = Paragraph("<b>COORDINATE PRECISION (m)</b><br/>" + self.coordinate_precision, styNormal)
        survey_type = Paragraph("<b>SURVEY TYPE</b><br/>" + self.survey_type, styNormal)
        surface_condition = Paragraph("<b>SURFACE CONDITION</b><br/>" + self.surface_condition, styNormal)
        accessibility = Paragraph("<b>ACCESSIBILITY</b><br/>" + self.accessibility, styNormal)
        photo_documentation = Paragraph("<b>PHOTO DOCUMENTATION</b><br/>" + self.photo_documentation, styNormal)
        weather_conditions = Paragraph("<b>WEATHER CONDITIONS</b><br/>" + self.weather_conditions, styNormal)
        team_members = Paragraph("<b>TEAM MEMBERS</b><br/>" + self.team_members, styNormal)

        # schema
        cell_schema = [  # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],  # 0 row ok
            [progetto, '01', '02', '03', '04', UT, '06', '07', UTletterale, '09'],  # 1 row ok
            [descrizione_ut, '01', '02', '03', '04'],
            [interpretazione_ut, '01', '02', '03', '04', '05', '06', '07', '08'],  # 2 row ok
            [nazione, '01', provincia, '03', regione, '06', comune, '9'],  # 3
            [frazione, '01', localita, '03', indirizzo, '05', nr_civico, '08', '09'],  # 4
            [carta_topo_igm, '01', carta_ctr, '03', coord_geografiche, '05', coord_piane, '08', '09'],  # 5
            # row 7 - survey fields
            [foglio_catastale, '01', gps_method, '03', coordinate_precision, '05', survey_type, '08', '09'],
            [quota, '01', andamento_terreno_pendenza, '03', utilizzo_suolo_vegetazione, '05',
             descrizione_empirica_suolo, '08', '09'],
            # 6
            [descrizione_luogo, '01', metodo_rilievo_e_ricognizione, '03', geometria, '05', bibliografia, '08', '09'],
            [data, '01', ora_meteo, '03', responsabile, '05', dimensioni_ut, '08', '09'],  # 7
            # row 11 - survey conditions
            [visibility_percent, '01', vegetation_coverage, '03', surface_condition, '05', accessibility, '08', '09'],
            # row 12 - survey documentation
            [weather_conditions, '01', team_members, '03', photo_documentation, '05', '06', '07', '08', '09'],
            [rep_per_mq, '01', rep_datanti, '03', periodo_I, '05', datazione_I, '08', '09'],  # 8
            [interpretazione_I, '01', periodo_II, '03', datazione_II, '05', interpretazione_II, '08', '09'],
            # 9
            [documentazione, '01', '02', enti_tutela_vincoli, '03', '04', indagini_preliminari, '09']
            # 10 row ok
        ]

        # table style
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row
            ('SPAN', (0, 0), (6, 0)),  # intestazione
            ('SPAN', (7, 0), (9, 0)),  # intestazione

            # 1 row
            ('SPAN', (0, 1), (4, 1)),  # dati identificativi
            ('SPAN', (5, 1), (7, 1)),  # dati identificativi
            ('SPAN', (8, 1), (9, 1)),  # dati identificativi

            # 2 row
            ('SPAN', (0, 2), (9, 2)),  # Definizione - interpretazone
            ('SPAN', (0, 3), (9, 3)),  # definizione - intepretazione

            # 4 row
            ('SPAN', (0, 4), (1, 4)),
            ('SPAN', (2, 4), (3, 4)),
            ('SPAN', (4, 4), (5, 4)),
            ('SPAN', (6, 4), (9, 4)),

            # 5 row
            ('SPAN', (0, 5), (1, 5)),
            ('SPAN', (2, 5), (3, 5)),
            ('SPAN', (4, 5), (5, 5)),
            ('SPAN', (6, 5), (9, 5)),

            # 6 row
            ('SPAN', (0, 6), (1, 6)),
            ('SPAN', (2, 6), (3, 6)),
            ('SPAN', (4, 6), (5, 6)),
            ('SPAN', (6, 6), (9, 6)),

            # 7 row - survey fields
            ('SPAN', (0, 7), (1, 7)),
            ('SPAN', (2, 7), (3, 7)),
            ('SPAN', (4, 7), (5, 7)),
            ('SPAN', (6, 7), (9, 7)),

            # 8 row
            ('SPAN', (0, 8), (1, 8)),
            ('SPAN', (2, 8), (3, 8)),
            ('SPAN', (4, 8), (5, 8)),
            ('SPAN', (6, 8), (9, 8)),

            # 9 row
            ('SPAN', (0, 9), (1, 9)),
            ('SPAN', (2, 9), (3, 9)),
            ('SPAN', (4, 9), (5, 9)),
            ('SPAN', (6, 9), (9, 9)),

            # 10 row
            ('SPAN', (0, 10), (1, 10)),
            ('SPAN', (2, 10), (3, 10)),
            ('SPAN', (4, 10), (5, 10)),
            ('SPAN', (6, 10), (9, 10)),

            # 11 row - survey conditions
            ('SPAN', (0, 11), (1, 11)),
            ('SPAN', (2, 11), (3, 11)),
            ('SPAN', (4, 11), (5, 11)),
            ('SPAN', (6, 11), (9, 11)),

            # 12 row - survey documentation
            ('SPAN', (0, 12), (1, 12)),
            ('SPAN', (2, 12), (3, 12)),
            ('SPAN', (4, 12), (9, 12)),

            # 13 row
            ('SPAN', (0, 13), (1, 13)),
            ('SPAN', (2, 13), (3, 13)),
            ('SPAN', (4, 13), (5, 13)),
            ('SPAN', (6, 13), (9, 13)),

            # 14 row
            ('SPAN', (0, 14), (1, 14)),
            ('SPAN', (2, 14), (3, 14)),
            ('SPAN', (4, 14), (5, 14)),
            ('SPAN', (6, 14), (9, 14)),

            # 15 row
            ('SPAN', (0, 15), (2, 15)),
            ('SPAN', (3, 15), (5, 15)),
            ('SPAN', (6, 15), (9, 15)),

            ('VALIGN', (0, 0), (-1, -1), 'TOP')

        ]

        # 4 row


        t = Table(cell_schema, colWidths=50, rowHeights=None, style=table_style)

        return t

    def create_sheet_fr(self):
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

        # 0 row
        intestazione = Paragraph("<b>FICHE UT<br/>" + str(self.datestrfdate()) + "</b>", styNormal)
        home = os.environ['PYARCHINIT_HOME']
        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        if not bool(lo_path_str):
            logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        else:
            logo_path = lo_path_str
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch

        # 1 row
        progetto = Paragraph("<b>Projet</b><br/>" + str(self.progetto), styNormal)
        UT = Paragraph("<b>N° UT</b><br/>" + str(self.nr_ut), styNormal)
        UTletterale = Paragraph("<b>UT</b><br/>" + str(self.ut_letterale), styNormal)

        # 2 row
        descrizione_ut = Paragraph("<b>Description UT</b><br/>" + self.descrizione_ut, styNormal)
        interpretazione_ut = Paragraph("<b>Interprétation UT</b><br/>" + self.interpretazione_ut, styNormal)

        # Location fields
        nazione = Paragraph("<b>Pays</b><br/>" + self.nazione, styNormal)
        regione = Paragraph("<b>Région</b><br/>" + self.regione, styNormal)
        provincia = Paragraph("<b>Province</b><br/>" + self.provincia, styNormal)
        comune = Paragraph("<b>Commune</b><br/>" + self.comune, styNormal)
        frazione = Paragraph("<b>Quartier</b><br/>" + self.frazione, styNormal)
        localita = Paragraph("<b>Localité</b><br/>" + self.localita, styNormal)
        indirizzo = Paragraph("<b>Adresse</b><br/>" + self.indirizzo, styNormal)
        nr_civico = Paragraph("<b>N° civique</b><br/>" + self.nr_civico, styNormal)
        carta_topo_igm = Paragraph("<b>Carte IGM</b><br/>" + self.carta_topo_igm, styNormal)
        carta_ctr = Paragraph("<b>CTR</b><br/>" + self.carta_ctr, styNormal)
        coord_geografiche = Paragraph("<b>Coord. géographiques</b><br/>" + self.coord_geografiche, styNormal)
        coord_piane = Paragraph("<b>Coord. planes</b><br/>" + self.coord_piane, styNormal)
        quota = Paragraph("<b>Altitude</b><br/>" + self.quota, styNormal)
        andamento_terreno_pendenza = Paragraph("<b>Pente</b><br/>" + self.andamento_terreno_pendenza, styNormal)
        utilizzo_suolo_vegetazione = Paragraph("<b>Utilisation sol</b><br/>" + self.utilizzo_suolo_vegetazione, styNormal)
        descrizione_empirica_suolo = Paragraph("<b>Description sol</b><br/>" + self.descrizione_empirica_suolo, styNormal)
        descrizione_luogo = Paragraph("<b>Description lieu</b><br/>" + self.descrizione_luogo, styNormal)
        metodo_rilievo_e_ricognizione = Paragraph("<b>Prospection</b><br/>" + self.metodo_rilievo_e_ricognizione, styNormal)
        geometria = Paragraph("<b>Géométrie</b><br/>" + self.geometria, styNormal)
        bibliografia = Paragraph("<b>Bibliographie</b><br/>" + self.bibliografia, styNormal)
        data = Paragraph("<b>Date</b><br/>" + self.data, styNormal)
        ora_meteo = Paragraph("<b>Heure et météo</b><br/>" + self.ora_meteo, styNormal)
        responsabile = Paragraph("<b>Responsable</b><br/>" + self.responsabile, styNormal)
        dimensioni_ut = Paragraph("<b>Dimensions UT</b><br/>" + self.dimensioni_ut, styNormal)
        rep_per_mq = Paragraph("<b>Trouvailles par m²</b><br/>" + self.rep_per_mq, styNormal)
        rep_datanti = Paragraph("<b>Trouvailles</b><br/>" + self.rep_datanti, styNormal)
        periodo_I = Paragraph("<b>Période I</b><br/>" + self.periodo_I, styNormal)
        datazione_I = Paragraph("<b>Datation I</b><br/>" + self.datazione_I, styNormal)
        interpretazione_I = Paragraph("<b>Interprétation I</b><br/>" + self.interpretazione_I, styNormal)
        periodo_II = Paragraph("<b>Période II</b><br/>" + self.periodo_II, styNormal)
        datazione_II = Paragraph("<b>Datation II</b><br/>" + self.datazione_II, styNormal)
        interpretazione_II = Paragraph("<b>Interprétation II</b><br/>" + self.interpretazione_II, styNormal)
        documentazione = Paragraph("<b>Documentation</b><br/>" + self.documentazione, styNormal)
        enti_tutela_vincoli = Paragraph("<b>Contraintes</b><br/>" + self.enti_tutela_vincoli, styNormal)
        indagini_preliminari = Paragraph("<b>Enquêtes préliminaires</b><br/>" + self.indagini_preliminari, styNormal)

        # New survey fields
        foglio_catastale = Paragraph("<b>FEUILLE CADASTRALE</b><br/>" + self.foglio_catastale, styNormal)
        visibility_percent = Paragraph("<b>VISIBILITÉ (%)</b><br/>" + self.visibility_percent, styNormal)
        vegetation_coverage = Paragraph("<b>COUVERTURE VÉGÉTALE</b><br/>" + self.vegetation_coverage, styNormal)
        gps_method = Paragraph("<b>MÉTHODE GPS</b><br/>" + self.gps_method, styNormal)
        coordinate_precision = Paragraph("<b>PRÉCISION COORD. (m)</b><br/>" + self.coordinate_precision, styNormal)
        survey_type = Paragraph("<b>TYPE PROSPECTION</b><br/>" + self.survey_type, styNormal)
        surface_condition = Paragraph("<b>ÉTAT SURFACE</b><br/>" + self.surface_condition, styNormal)
        accessibility = Paragraph("<b>ACCESSIBILITÉ</b><br/>" + self.accessibility, styNormal)
        photo_documentation = Paragraph("<b>DOC. PHOTO</b><br/>" + self.photo_documentation, styNormal)
        weather_conditions = Paragraph("<b>CONDITIONS MÉTÉO</b><br/>" + self.weather_conditions, styNormal)
        team_members = Paragraph("<b>MEMBRES ÉQUIPE</b><br/>" + self.team_members, styNormal)

        # schema
        cell_schema = [
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],
            [progetto, '01', '02', '03', '04', UT, '06', '07', UTletterale, '09'],
            [descrizione_ut, '01', '02', '03', '04'],
            [interpretazione_ut, '01', '02', '03', '04', '05', '06', '07', '08'],
            [nazione, '01', provincia, '03', regione, '06', comune, '9'],
            [frazione, '01', localita, '03', indirizzo, '05', nr_civico, '08', '09'],
            [carta_topo_igm, '01', carta_ctr, '03', coord_geografiche, '05', coord_piane, '08', '09'],
            [foglio_catastale, '01', gps_method, '03', coordinate_precision, '05', survey_type, '08', '09'],
            [quota, '01', andamento_terreno_pendenza, '03', utilizzo_suolo_vegetazione, '05', descrizione_empirica_suolo, '08', '09'],
            [descrizione_luogo, '01', metodo_rilievo_e_ricognizione, '03', geometria, '05', bibliografia, '08', '09'],
            [data, '01', ora_meteo, '03', responsabile, '05', dimensioni_ut, '08', '09'],
            [visibility_percent, '01', vegetation_coverage, '03', surface_condition, '05', accessibility, '08', '09'],
            [weather_conditions, '01', team_members, '03', photo_documentation, '05', '06', '07', '08', '09'],
            [rep_per_mq, '01', rep_datanti, '03', periodo_I, '05', datazione_I, '08', '09'],
            [interpretazione_I, '01', periodo_II, '03', datazione_II, '05', interpretazione_II, '08', '09'],
            [documentazione, '01', '02', enti_tutela_vincoli, '03', '04', indagini_preliminari, '09']
        ]

        # table style
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('SPAN', (0, 0), (6, 0)), ('SPAN', (7, 0), (9, 0)),
            ('SPAN', (0, 1), (4, 1)), ('SPAN', (5, 1), (7, 1)), ('SPAN', (8, 1), (9, 1)),
            ('SPAN', (0, 2), (9, 2)), ('SPAN', (0, 3), (9, 3)),
            ('SPAN', (0, 4), (1, 4)), ('SPAN', (2, 4), (3, 4)), ('SPAN', (4, 4), (5, 4)), ('SPAN', (6, 4), (9, 4)),
            ('SPAN', (0, 5), (1, 5)), ('SPAN', (2, 5), (3, 5)), ('SPAN', (4, 5), (5, 5)), ('SPAN', (6, 5), (9, 5)),
            ('SPAN', (0, 6), (1, 6)), ('SPAN', (2, 6), (3, 6)), ('SPAN', (4, 6), (5, 6)), ('SPAN', (6, 6), (9, 6)),
            ('SPAN', (0, 7), (1, 7)), ('SPAN', (2, 7), (3, 7)), ('SPAN', (4, 7), (5, 7)), ('SPAN', (6, 7), (9, 7)),
            ('SPAN', (0, 8), (1, 8)), ('SPAN', (2, 8), (3, 8)), ('SPAN', (4, 8), (5, 8)), ('SPAN', (6, 8), (9, 8)),
            ('SPAN', (0, 9), (1, 9)), ('SPAN', (2, 9), (3, 9)), ('SPAN', (4, 9), (5, 9)), ('SPAN', (6, 9), (9, 9)),
            ('SPAN', (0, 10), (1, 10)), ('SPAN', (2, 10), (3, 10)), ('SPAN', (4, 10), (5, 10)), ('SPAN', (6, 10), (9, 10)),
            ('SPAN', (0, 11), (1, 11)), ('SPAN', (2, 11), (3, 11)), ('SPAN', (4, 11), (5, 11)), ('SPAN', (6, 11), (9, 11)),
            ('SPAN', (0, 12), (1, 12)), ('SPAN', (2, 12), (3, 12)), ('SPAN', (4, 12), (9, 12)),
            ('SPAN', (0, 13), (1, 13)), ('SPAN', (2, 13), (3, 13)), ('SPAN', (4, 13), (5, 13)), ('SPAN', (6, 13), (9, 13)),
            ('SPAN', (0, 14), (1, 14)), ('SPAN', (2, 14), (3, 14)), ('SPAN', (4, 14), (5, 14)), ('SPAN', (6, 14), (9, 14)),
            ('SPAN', (0, 15), (2, 15)), ('SPAN', (3, 15), (5, 15)), ('SPAN', (6, 15), (9, 15)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]

        t = Table(cell_schema, colWidths=50, rowHeights=None, style=table_style)
        return t

    def create_sheet_es(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0

        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.alignment = 4

        # 0 row
        intestazione = Paragraph("<b>FICHA UT<br/>" + str(self.datestrfdate()) + "</b>", styNormal)
        home = os.environ['PYARCHINIT_HOME']
        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        if not bool(lo_path_str):
            logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        else:
            logo_path = lo_path_str
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch

        progetto = Paragraph("<b>Proyecto</b><br/>" + str(self.progetto), styNormal)
        UT = Paragraph("<b>N° UT</b><br/>" + str(self.nr_ut), styNormal)
        UTletterale = Paragraph("<b>UT</b><br/>" + str(self.ut_letterale), styNormal)
        descrizione_ut = Paragraph("<b>Descripción UT</b><br/>" + self.descrizione_ut, styNormal)
        interpretazione_ut = Paragraph("<b>Interpretación UT</b><br/>" + self.interpretazione_ut, styNormal)
        nazione = Paragraph("<b>País</b><br/>" + self.nazione, styNormal)
        regione = Paragraph("<b>Región</b><br/>" + self.regione, styNormal)
        provincia = Paragraph("<b>Provincia</b><br/>" + self.provincia, styNormal)
        comune = Paragraph("<b>Municipio</b><br/>" + self.comune, styNormal)
        frazione = Paragraph("<b>Barrio</b><br/>" + self.frazione, styNormal)
        localita = Paragraph("<b>Localidad</b><br/>" + self.localita, styNormal)
        indirizzo = Paragraph("<b>Dirección</b><br/>" + self.indirizzo, styNormal)
        nr_civico = Paragraph("<b>N° cívico</b><br/>" + self.nr_civico, styNormal)
        carta_topo_igm = Paragraph("<b>Carta IGM</b><br/>" + self.carta_topo_igm, styNormal)
        carta_ctr = Paragraph("<b>CTR</b><br/>" + self.carta_ctr, styNormal)
        coord_geografiche = Paragraph("<b>Coord. geográficas</b><br/>" + self.coord_geografiche, styNormal)
        coord_piane = Paragraph("<b>Coord. planas</b><br/>" + self.coord_piane, styNormal)
        quota = Paragraph("<b>Cota</b><br/>" + self.quota, styNormal)
        andamento_terreno_pendenza = Paragraph("<b>Pendiente</b><br/>" + self.andamento_terreno_pendenza, styNormal)
        utilizzo_suolo_vegetazione = Paragraph("<b>Uso suelo</b><br/>" + self.utilizzo_suolo_vegetazione, styNormal)
        descrizione_empirica_suolo = Paragraph("<b>Descripción suelo</b><br/>" + self.descrizione_empirica_suolo, styNormal)
        descrizione_luogo = Paragraph("<b>Descripción lugar</b><br/>" + self.descrizione_luogo, styNormal)
        metodo_rilievo_e_ricognizione = Paragraph("<b>Prospección</b><br/>" + self.metodo_rilievo_e_ricognizione, styNormal)
        geometria = Paragraph("<b>Geometría</b><br/>" + self.geometria, styNormal)
        bibliografia = Paragraph("<b>Bibliografía</b><br/>" + self.bibliografia, styNormal)
        data = Paragraph("<b>Fecha</b><br/>" + self.data, styNormal)
        ora_meteo = Paragraph("<b>Hora y clima</b><br/>" + self.ora_meteo, styNormal)
        responsabile = Paragraph("<b>Responsable</b><br/>" + self.responsabile, styNormal)
        dimensioni_ut = Paragraph("<b>Dimensiones UT</b><br/>" + self.dimensioni_ut, styNormal)
        rep_per_mq = Paragraph("<b>Hallazgos por m²</b><br/>" + self.rep_per_mq, styNormal)
        rep_datanti = Paragraph("<b>Hallazgos</b><br/>" + self.rep_datanti, styNormal)
        periodo_I = Paragraph("<b>Período I</b><br/>" + self.periodo_I, styNormal)
        datazione_I = Paragraph("<b>Datación I</b><br/>" + self.datazione_I, styNormal)
        interpretazione_I = Paragraph("<b>Interpretación I</b><br/>" + self.interpretazione_I, styNormal)
        periodo_II = Paragraph("<b>Período II</b><br/>" + self.periodo_II, styNormal)
        datazione_II = Paragraph("<b>Datación II</b><br/>" + self.datazione_II, styNormal)
        interpretazione_II = Paragraph("<b>Interpretación II</b><br/>" + self.interpretazione_II, styNormal)
        documentazione = Paragraph("<b>Documentación</b><br/>" + self.documentazione, styNormal)
        enti_tutela_vincoli = Paragraph("<b>Restricciones</b><br/>" + self.enti_tutela_vincoli, styNormal)
        indagini_preliminari = Paragraph("<b>Investigaciones preliminares</b><br/>" + self.indagini_preliminari, styNormal)

        # New survey fields
        foglio_catastale = Paragraph("<b>HOJA CATASTRAL</b><br/>" + self.foglio_catastale, styNormal)
        visibility_percent = Paragraph("<b>VISIBILIDAD (%)</b><br/>" + self.visibility_percent, styNormal)
        vegetation_coverage = Paragraph("<b>COBERTURA VEGETAL</b><br/>" + self.vegetation_coverage, styNormal)
        gps_method = Paragraph("<b>MÉTODO GPS</b><br/>" + self.gps_method, styNormal)
        coordinate_precision = Paragraph("<b>PRECISIÓN COORD. (m)</b><br/>" + self.coordinate_precision, styNormal)
        survey_type = Paragraph("<b>TIPO PROSPECCIÓN</b><br/>" + self.survey_type, styNormal)
        surface_condition = Paragraph("<b>ESTADO SUPERFICIE</b><br/>" + self.surface_condition, styNormal)
        accessibility = Paragraph("<b>ACCESIBILIDAD</b><br/>" + self.accessibility, styNormal)
        photo_documentation = Paragraph("<b>DOC. FOTOGRÁFICA</b><br/>" + self.photo_documentation, styNormal)
        weather_conditions = Paragraph("<b>CONDICIONES CLIMÁTICAS</b><br/>" + self.weather_conditions, styNormal)
        team_members = Paragraph("<b>MIEMBROS EQUIPO</b><br/>" + self.team_members, styNormal)

        cell_schema = [
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],
            [progetto, '01', '02', '03', '04', UT, '06', '07', UTletterale, '09'],
            [descrizione_ut, '01', '02', '03', '04'],
            [interpretazione_ut, '01', '02', '03', '04', '05', '06', '07', '08'],
            [nazione, '01', provincia, '03', regione, '06', comune, '9'],
            [frazione, '01', localita, '03', indirizzo, '05', nr_civico, '08', '09'],
            [carta_topo_igm, '01', carta_ctr, '03', coord_geografiche, '05', coord_piane, '08', '09'],
            [foglio_catastale, '01', gps_method, '03', coordinate_precision, '05', survey_type, '08', '09'],
            [quota, '01', andamento_terreno_pendenza, '03', utilizzo_suolo_vegetazione, '05', descrizione_empirica_suolo, '08', '09'],
            [descrizione_luogo, '01', metodo_rilievo_e_ricognizione, '03', geometria, '05', bibliografia, '08', '09'],
            [data, '01', ora_meteo, '03', responsabile, '05', dimensioni_ut, '08', '09'],
            [visibility_percent, '01', vegetation_coverage, '03', surface_condition, '05', accessibility, '08', '09'],
            [weather_conditions, '01', team_members, '03', photo_documentation, '05', '06', '07', '08', '09'],
            [rep_per_mq, '01', rep_datanti, '03', periodo_I, '05', datazione_I, '08', '09'],
            [interpretazione_I, '01', periodo_II, '03', datazione_II, '05', interpretazione_II, '08', '09'],
            [documentazione, '01', '02', enti_tutela_vincoli, '03', '04', indagini_preliminari, '09']
        ]

        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('SPAN', (0, 0), (6, 0)), ('SPAN', (7, 0), (9, 0)),
            ('SPAN', (0, 1), (4, 1)), ('SPAN', (5, 1), (7, 1)), ('SPAN', (8, 1), (9, 1)),
            ('SPAN', (0, 2), (9, 2)), ('SPAN', (0, 3), (9, 3)),
            ('SPAN', (0, 4), (1, 4)), ('SPAN', (2, 4), (3, 4)), ('SPAN', (4, 4), (5, 4)), ('SPAN', (6, 4), (9, 4)),
            ('SPAN', (0, 5), (1, 5)), ('SPAN', (2, 5), (3, 5)), ('SPAN', (4, 5), (5, 5)), ('SPAN', (6, 5), (9, 5)),
            ('SPAN', (0, 6), (1, 6)), ('SPAN', (2, 6), (3, 6)), ('SPAN', (4, 6), (5, 6)), ('SPAN', (6, 6), (9, 6)),
            ('SPAN', (0, 7), (1, 7)), ('SPAN', (2, 7), (3, 7)), ('SPAN', (4, 7), (5, 7)), ('SPAN', (6, 7), (9, 7)),
            ('SPAN', (0, 8), (1, 8)), ('SPAN', (2, 8), (3, 8)), ('SPAN', (4, 8), (5, 8)), ('SPAN', (6, 8), (9, 8)),
            ('SPAN', (0, 9), (1, 9)), ('SPAN', (2, 9), (3, 9)), ('SPAN', (4, 9), (5, 9)), ('SPAN', (6, 9), (9, 9)),
            ('SPAN', (0, 10), (1, 10)), ('SPAN', (2, 10), (3, 10)), ('SPAN', (4, 10), (5, 10)), ('SPAN', (6, 10), (9, 10)),
            ('SPAN', (0, 11), (1, 11)), ('SPAN', (2, 11), (3, 11)), ('SPAN', (4, 11), (5, 11)), ('SPAN', (6, 11), (9, 11)),
            ('SPAN', (0, 12), (1, 12)), ('SPAN', (2, 12), (3, 12)), ('SPAN', (4, 12), (9, 12)),
            ('SPAN', (0, 13), (1, 13)), ('SPAN', (2, 13), (3, 13)), ('SPAN', (4, 13), (5, 13)), ('SPAN', (6, 13), (9, 13)),
            ('SPAN', (0, 14), (1, 14)), ('SPAN', (2, 14), (3, 14)), ('SPAN', (4, 14), (5, 14)), ('SPAN', (6, 14), (9, 14)),
            ('SPAN', (0, 15), (2, 15)), ('SPAN', (3, 15), (5, 15)), ('SPAN', (6, 15), (9, 15)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]

        t = Table(cell_schema, colWidths=50, rowHeights=None, style=table_style)
        return t

    def create_sheet_ar(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0

        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.alignment = 4

        # 0 row
        intestazione = Paragraph("<b>بطاقة UT<br/>" + str(self.datestrfdate()) + "</b>", styNormal)
        home = os.environ['PYARCHINIT_HOME']
        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        if not bool(lo_path_str):
            logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        else:
            logo_path = lo_path_str
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch

        progetto = Paragraph("<b>المشروع</b><br/>" + str(self.progetto), styNormal)
        UT = Paragraph("<b>رقم UT</b><br/>" + str(self.nr_ut), styNormal)
        UTletterale = Paragraph("<b>UT</b><br/>" + str(self.ut_letterale), styNormal)
        descrizione_ut = Paragraph("<b>وصف UT</b><br/>" + self.descrizione_ut, styNormal)
        interpretazione_ut = Paragraph("<b>تفسير UT</b><br/>" + self.interpretazione_ut, styNormal)
        nazione = Paragraph("<b>البلد</b><br/>" + self.nazione, styNormal)
        regione = Paragraph("<b>المنطقة</b><br/>" + self.regione, styNormal)
        provincia = Paragraph("<b>المحافظة</b><br/>" + self.provincia, styNormal)
        comune = Paragraph("<b>البلدية</b><br/>" + self.comune, styNormal)
        frazione = Paragraph("<b>الحي</b><br/>" + self.frazione, styNormal)
        localita = Paragraph("<b>الموقع</b><br/>" + self.localita, styNormal)
        indirizzo = Paragraph("<b>العنوان</b><br/>" + self.indirizzo, styNormal)
        nr_civico = Paragraph("<b>الرقم</b><br/>" + self.nr_civico, styNormal)
        carta_topo_igm = Paragraph("<b>خريطة IGM</b><br/>" + self.carta_topo_igm, styNormal)
        carta_ctr = Paragraph("<b>CTR</b><br/>" + self.carta_ctr, styNormal)
        coord_geografiche = Paragraph("<b>الإحداثيات الجغرافية</b><br/>" + self.coord_geografiche, styNormal)
        coord_piane = Paragraph("<b>الإحداثيات المستوية</b><br/>" + self.coord_piane, styNormal)
        quota = Paragraph("<b>الارتفاع</b><br/>" + self.quota, styNormal)
        andamento_terreno_pendenza = Paragraph("<b>الميل</b><br/>" + self.andamento_terreno_pendenza, styNormal)
        utilizzo_suolo_vegetazione = Paragraph("<b>استخدام الأرض</b><br/>" + self.utilizzo_suolo_vegetazione, styNormal)
        descrizione_empirica_suolo = Paragraph("<b>وصف التربة</b><br/>" + self.descrizione_empirica_suolo, styNormal)
        descrizione_luogo = Paragraph("<b>وصف المكان</b><br/>" + self.descrizione_luogo, styNormal)
        metodo_rilievo_e_ricognizione = Paragraph("<b>المسح</b><br/>" + self.metodo_rilievo_e_ricognizione, styNormal)
        geometria = Paragraph("<b>الهندسة</b><br/>" + self.geometria, styNormal)
        bibliografia = Paragraph("<b>المراجع</b><br/>" + self.bibliografia, styNormal)
        data = Paragraph("<b>التاريخ</b><br/>" + self.data, styNormal)
        ora_meteo = Paragraph("<b>الوقت والطقس</b><br/>" + self.ora_meteo, styNormal)
        responsabile = Paragraph("<b>المسؤول</b><br/>" + self.responsabile, styNormal)
        dimensioni_ut = Paragraph("<b>أبعاد UT</b><br/>" + self.dimensioni_ut, styNormal)
        rep_per_mq = Paragraph("<b>اللقى لكل م²</b><br/>" + self.rep_per_mq, styNormal)
        rep_datanti = Paragraph("<b>اللقى</b><br/>" + self.rep_datanti, styNormal)
        periodo_I = Paragraph("<b>الفترة I</b><br/>" + self.periodo_I, styNormal)
        datazione_I = Paragraph("<b>التأريخ I</b><br/>" + self.datazione_I, styNormal)
        interpretazione_I = Paragraph("<b>التفسير I</b><br/>" + self.interpretazione_I, styNormal)
        periodo_II = Paragraph("<b>الفترة II</b><br/>" + self.periodo_II, styNormal)
        datazione_II = Paragraph("<b>التأريخ II</b><br/>" + self.datazione_II, styNormal)
        interpretazione_II = Paragraph("<b>التفسير II</b><br/>" + self.interpretazione_II, styNormal)
        documentazione = Paragraph("<b>التوثيق</b><br/>" + self.documentazione, styNormal)
        enti_tutela_vincoli = Paragraph("<b>القيود</b><br/>" + self.enti_tutela_vincoli, styNormal)
        indagini_preliminari = Paragraph("<b>التحقيقات الأولية</b><br/>" + self.indagini_preliminari, styNormal)

        # New survey fields
        foglio_catastale = Paragraph("<b>صحيفة المساحة</b><br/>" + self.foglio_catastale, styNormal)
        visibility_percent = Paragraph("<b>الرؤية (%)</b><br/>" + self.visibility_percent, styNormal)
        vegetation_coverage = Paragraph("<b>الغطاء النباتي</b><br/>" + self.vegetation_coverage, styNormal)
        gps_method = Paragraph("<b>طريقة GPS</b><br/>" + self.gps_method, styNormal)
        coordinate_precision = Paragraph("<b>دقة الإحداثيات (م)</b><br/>" + self.coordinate_precision, styNormal)
        survey_type = Paragraph("<b>نوع المسح</b><br/>" + self.survey_type, styNormal)
        surface_condition = Paragraph("<b>حالة السطح</b><br/>" + self.surface_condition, styNormal)
        accessibility = Paragraph("<b>إمكانية الوصول</b><br/>" + self.accessibility, styNormal)
        photo_documentation = Paragraph("<b>التوثيق الفوتوغرافي</b><br/>" + self.photo_documentation, styNormal)
        weather_conditions = Paragraph("<b>الظروف الجوية</b><br/>" + self.weather_conditions, styNormal)
        team_members = Paragraph("<b>أعضاء الفريق</b><br/>" + self.team_members, styNormal)

        cell_schema = [
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],
            [progetto, '01', '02', '03', '04', UT, '06', '07', UTletterale, '09'],
            [descrizione_ut, '01', '02', '03', '04'],
            [interpretazione_ut, '01', '02', '03', '04', '05', '06', '07', '08'],
            [nazione, '01', provincia, '03', regione, '06', comune, '9'],
            [frazione, '01', localita, '03', indirizzo, '05', nr_civico, '08', '09'],
            [carta_topo_igm, '01', carta_ctr, '03', coord_geografiche, '05', coord_piane, '08', '09'],
            [foglio_catastale, '01', gps_method, '03', coordinate_precision, '05', survey_type, '08', '09'],
            [quota, '01', andamento_terreno_pendenza, '03', utilizzo_suolo_vegetazione, '05', descrizione_empirica_suolo, '08', '09'],
            [descrizione_luogo, '01', metodo_rilievo_e_ricognizione, '03', geometria, '05', bibliografia, '08', '09'],
            [data, '01', ora_meteo, '03', responsabile, '05', dimensioni_ut, '08', '09'],
            [visibility_percent, '01', vegetation_coverage, '03', surface_condition, '05', accessibility, '08', '09'],
            [weather_conditions, '01', team_members, '03', photo_documentation, '05', '06', '07', '08', '09'],
            [rep_per_mq, '01', rep_datanti, '03', periodo_I, '05', datazione_I, '08', '09'],
            [interpretazione_I, '01', periodo_II, '03', datazione_II, '05', interpretazione_II, '08', '09'],
            [documentazione, '01', '02', enti_tutela_vincoli, '03', '04', indagini_preliminari, '09']
        ]

        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('SPAN', (0, 0), (6, 0)), ('SPAN', (7, 0), (9, 0)),
            ('SPAN', (0, 1), (4, 1)), ('SPAN', (5, 1), (7, 1)), ('SPAN', (8, 1), (9, 1)),
            ('SPAN', (0, 2), (9, 2)), ('SPAN', (0, 3), (9, 3)),
            ('SPAN', (0, 4), (1, 4)), ('SPAN', (2, 4), (3, 4)), ('SPAN', (4, 4), (5, 4)), ('SPAN', (6, 4), (9, 4)),
            ('SPAN', (0, 5), (1, 5)), ('SPAN', (2, 5), (3, 5)), ('SPAN', (4, 5), (5, 5)), ('SPAN', (6, 5), (9, 5)),
            ('SPAN', (0, 6), (1, 6)), ('SPAN', (2, 6), (3, 6)), ('SPAN', (4, 6), (5, 6)), ('SPAN', (6, 6), (9, 6)),
            ('SPAN', (0, 7), (1, 7)), ('SPAN', (2, 7), (3, 7)), ('SPAN', (4, 7), (5, 7)), ('SPAN', (6, 7), (9, 7)),
            ('SPAN', (0, 8), (1, 8)), ('SPAN', (2, 8), (3, 8)), ('SPAN', (4, 8), (5, 8)), ('SPAN', (6, 8), (9, 8)),
            ('SPAN', (0, 9), (1, 9)), ('SPAN', (2, 9), (3, 9)), ('SPAN', (4, 9), (5, 9)), ('SPAN', (6, 9), (9, 9)),
            ('SPAN', (0, 10), (1, 10)), ('SPAN', (2, 10), (3, 10)), ('SPAN', (4, 10), (5, 10)), ('SPAN', (6, 10), (9, 10)),
            ('SPAN', (0, 11), (1, 11)), ('SPAN', (2, 11), (3, 11)), ('SPAN', (4, 11), (5, 11)), ('SPAN', (6, 11), (9, 11)),
            ('SPAN', (0, 12), (1, 12)), ('SPAN', (2, 12), (3, 12)), ('SPAN', (4, 12), (9, 12)),
            ('SPAN', (0, 13), (1, 13)), ('SPAN', (2, 13), (3, 13)), ('SPAN', (4, 13), (5, 13)), ('SPAN', (6, 13), (9, 13)),
            ('SPAN', (0, 14), (1, 14)), ('SPAN', (2, 14), (3, 14)), ('SPAN', (4, 14), (5, 14)), ('SPAN', (6, 14), (9, 14)),
            ('SPAN', (0, 15), (2, 15)), ('SPAN', (3, 15), (5, 15)), ('SPAN', (6, 15), (9, 15)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]

        t = Table(cell_schema, colWidths=50, rowHeights=None, style=table_style)
        return t

    def create_sheet_ca(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0

        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.alignment = 4

        # 0 row
        intestazione = Paragraph("<b>FITXA UT<br/>" + str(self.datestrfdate()) + "</b>", styNormal)
        home = os.environ['PYARCHINIT_HOME']
        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        if not bool(lo_path_str):
            logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        else:
            logo_path = lo_path_str
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch

        progetto = Paragraph("<b>Projecte</b><br/>" + str(self.progetto), styNormal)
        UT = Paragraph("<b>N° UT</b><br/>" + str(self.nr_ut), styNormal)
        UTletterale = Paragraph("<b>UT</b><br/>" + str(self.ut_letterale), styNormal)
        descrizione_ut = Paragraph("<b>Descripció UT</b><br/>" + self.descrizione_ut, styNormal)
        interpretazione_ut = Paragraph("<b>Interpretació UT</b><br/>" + self.interpretazione_ut, styNormal)
        nazione = Paragraph("<b>País</b><br/>" + self.nazione, styNormal)
        regione = Paragraph("<b>Regió</b><br/>" + self.regione, styNormal)
        provincia = Paragraph("<b>Província</b><br/>" + self.provincia, styNormal)
        comune = Paragraph("<b>Municipi</b><br/>" + self.comune, styNormal)
        frazione = Paragraph("<b>Barri</b><br/>" + self.frazione, styNormal)
        localita = Paragraph("<b>Localitat</b><br/>" + self.localita, styNormal)
        indirizzo = Paragraph("<b>Adreça</b><br/>" + self.indirizzo, styNormal)
        nr_civico = Paragraph("<b>N° cívic</b><br/>" + self.nr_civico, styNormal)
        carta_topo_igm = Paragraph("<b>Carta IGM</b><br/>" + self.carta_topo_igm, styNormal)
        carta_ctr = Paragraph("<b>CTR</b><br/>" + self.carta_ctr, styNormal)
        coord_geografiche = Paragraph("<b>Coord. geogràfiques</b><br/>" + self.coord_geografiche, styNormal)
        coord_piane = Paragraph("<b>Coord. planes</b><br/>" + self.coord_piane, styNormal)
        quota = Paragraph("<b>Cota</b><br/>" + self.quota, styNormal)
        andamento_terreno_pendenza = Paragraph("<b>Pendent</b><br/>" + self.andamento_terreno_pendenza, styNormal)
        utilizzo_suolo_vegetazione = Paragraph("<b>Ús del sòl</b><br/>" + self.utilizzo_suolo_vegetazione, styNormal)
        descrizione_empirica_suolo = Paragraph("<b>Descripció sòl</b><br/>" + self.descrizione_empirica_suolo, styNormal)
        descrizione_luogo = Paragraph("<b>Descripció lloc</b><br/>" + self.descrizione_luogo, styNormal)
        metodo_rilievo_e_ricognizione = Paragraph("<b>Prospecció</b><br/>" + self.metodo_rilievo_e_ricognizione, styNormal)
        geometria = Paragraph("<b>Geometria</b><br/>" + self.geometria, styNormal)
        bibliografia = Paragraph("<b>Bibliografia</b><br/>" + self.bibliografia, styNormal)
        data = Paragraph("<b>Data</b><br/>" + self.data, styNormal)
        ora_meteo = Paragraph("<b>Hora i clima</b><br/>" + self.ora_meteo, styNormal)
        responsabile = Paragraph("<b>Responsable</b><br/>" + self.responsabile, styNormal)
        dimensioni_ut = Paragraph("<b>Dimensions UT</b><br/>" + self.dimensioni_ut, styNormal)
        rep_per_mq = Paragraph("<b>Troballes per m²</b><br/>" + self.rep_per_mq, styNormal)
        rep_datanti = Paragraph("<b>Troballes</b><br/>" + self.rep_datanti, styNormal)
        periodo_I = Paragraph("<b>Període I</b><br/>" + self.periodo_I, styNormal)
        datazione_I = Paragraph("<b>Datació I</b><br/>" + self.datazione_I, styNormal)
        interpretazione_I = Paragraph("<b>Interpretació I</b><br/>" + self.interpretazione_I, styNormal)
        periodo_II = Paragraph("<b>Període II</b><br/>" + self.periodo_II, styNormal)
        datazione_II = Paragraph("<b>Datació II</b><br/>" + self.datazione_II, styNormal)
        interpretazione_II = Paragraph("<b>Interpretació II</b><br/>" + self.interpretazione_II, styNormal)
        documentazione = Paragraph("<b>Documentació</b><br/>" + self.documentazione, styNormal)
        enti_tutela_vincoli = Paragraph("<b>Restriccions</b><br/>" + self.enti_tutela_vincoli, styNormal)
        indagini_preliminari = Paragraph("<b>Investigacions preliminars</b><br/>" + self.indagini_preliminari, styNormal)

        # New survey fields
        foglio_catastale = Paragraph("<b>FULL CADASTRAL</b><br/>" + self.foglio_catastale, styNormal)
        visibility_percent = Paragraph("<b>VISIBILITAT (%)</b><br/>" + self.visibility_percent, styNormal)
        vegetation_coverage = Paragraph("<b>COBERTURA VEGETAL</b><br/>" + self.vegetation_coverage, styNormal)
        gps_method = Paragraph("<b>MÈTODE GPS</b><br/>" + self.gps_method, styNormal)
        coordinate_precision = Paragraph("<b>PRECISIÓ COORD. (m)</b><br/>" + self.coordinate_precision, styNormal)
        survey_type = Paragraph("<b>TIPUS PROSPECCIÓ</b><br/>" + self.survey_type, styNormal)
        surface_condition = Paragraph("<b>ESTAT SUPERFÍCIE</b><br/>" + self.surface_condition, styNormal)
        accessibility = Paragraph("<b>ACCESSIBILITAT</b><br/>" + self.accessibility, styNormal)
        photo_documentation = Paragraph("<b>DOC. FOTOGRÀFICA</b><br/>" + self.photo_documentation, styNormal)
        weather_conditions = Paragraph("<b>CONDICIONS CLIMÀTIQUES</b><br/>" + self.weather_conditions, styNormal)
        team_members = Paragraph("<b>MEMBRES EQUIP</b><br/>" + self.team_members, styNormal)

        cell_schema = [
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],
            [progetto, '01', '02', '03', '04', UT, '06', '07', UTletterale, '09'],
            [descrizione_ut, '01', '02', '03', '04'],
            [interpretazione_ut, '01', '02', '03', '04', '05', '06', '07', '08'],
            [nazione, '01', provincia, '03', regione, '06', comune, '9'],
            [frazione, '01', localita, '03', indirizzo, '05', nr_civico, '08', '09'],
            [carta_topo_igm, '01', carta_ctr, '03', coord_geografiche, '05', coord_piane, '08', '09'],
            [foglio_catastale, '01', gps_method, '03', coordinate_precision, '05', survey_type, '08', '09'],
            [quota, '01', andamento_terreno_pendenza, '03', utilizzo_suolo_vegetazione, '05', descrizione_empirica_suolo, '08', '09'],
            [descrizione_luogo, '01', metodo_rilievo_e_ricognizione, '03', geometria, '05', bibliografia, '08', '09'],
            [data, '01', ora_meteo, '03', responsabile, '05', dimensioni_ut, '08', '09'],
            [visibility_percent, '01', vegetation_coverage, '03', surface_condition, '05', accessibility, '08', '09'],
            [weather_conditions, '01', team_members, '03', photo_documentation, '05', '06', '07', '08', '09'],
            [rep_per_mq, '01', rep_datanti, '03', periodo_I, '05', datazione_I, '08', '09'],
            [interpretazione_I, '01', periodo_II, '03', datazione_II, '05', interpretazione_II, '08', '09'],
            [documentazione, '01', '02', enti_tutela_vincoli, '03', '04', indagini_preliminari, '09']
        ]

        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('SPAN', (0, 0), (6, 0)), ('SPAN', (7, 0), (9, 0)),
            ('SPAN', (0, 1), (4, 1)), ('SPAN', (5, 1), (7, 1)), ('SPAN', (8, 1), (9, 1)),
            ('SPAN', (0, 2), (9, 2)), ('SPAN', (0, 3), (9, 3)),
            ('SPAN', (0, 4), (1, 4)), ('SPAN', (2, 4), (3, 4)), ('SPAN', (4, 4), (5, 4)), ('SPAN', (6, 4), (9, 4)),
            ('SPAN', (0, 5), (1, 5)), ('SPAN', (2, 5), (3, 5)), ('SPAN', (4, 5), (5, 5)), ('SPAN', (6, 5), (9, 5)),
            ('SPAN', (0, 6), (1, 6)), ('SPAN', (2, 6), (3, 6)), ('SPAN', (4, 6), (5, 6)), ('SPAN', (6, 6), (9, 6)),
            ('SPAN', (0, 7), (1, 7)), ('SPAN', (2, 7), (3, 7)), ('SPAN', (4, 7), (5, 7)), ('SPAN', (6, 7), (9, 7)),
            ('SPAN', (0, 8), (1, 8)), ('SPAN', (2, 8), (3, 8)), ('SPAN', (4, 8), (5, 8)), ('SPAN', (6, 8), (9, 8)),
            ('SPAN', (0, 9), (1, 9)), ('SPAN', (2, 9), (3, 9)), ('SPAN', (4, 9), (5, 9)), ('SPAN', (6, 9), (9, 9)),
            ('SPAN', (0, 10), (1, 10)), ('SPAN', (2, 10), (3, 10)), ('SPAN', (4, 10), (5, 10)), ('SPAN', (6, 10), (9, 10)),
            ('SPAN', (0, 11), (1, 11)), ('SPAN', (2, 11), (3, 11)), ('SPAN', (4, 11), (5, 11)), ('SPAN', (6, 11), (9, 11)),
            ('SPAN', (0, 12), (1, 12)), ('SPAN', (2, 12), (3, 12)), ('SPAN', (4, 12), (9, 12)),
            ('SPAN', (0, 13), (1, 13)), ('SPAN', (2, 13), (3, 13)), ('SPAN', (4, 13), (5, 13)), ('SPAN', (6, 13), (9, 13)),
            ('SPAN', (0, 14), (1, 14)), ('SPAN', (2, 14), (3, 14)), ('SPAN', (4, 14), (5, 14)), ('SPAN', (6, 14), (9, 14)),
            ('SPAN', (0, 15), (2, 15)), ('SPAN', (3, 15), (5, 15)), ('SPAN', (6, 15), (9, 15)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]

        t = Table(cell_schema, colWidths=50, rowHeights=None, style=table_style)
        return t

    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7

    def makeStyles(self):
        styles = TableStyle([('GRID', (0, 0), (-1, -1), 0.0, colors.black), ('VALIGN', (0, 0), (-1, -1), 'TOP')
                             ])  # finale

        return styles


class generate_pdf(object):
    HOME = os.environ['PYARCHINIT_HOME']

    PDF_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def build_UT_sheets(self, records):
        elements = []
        for i in range(len(records)):
            single_us_sheet = single_UT_pdf_sheet(records[i])
            elements.append(single_us_sheet.create_sheet())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'scheda_UT.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_UTsheet)
        f.close()
    def build_UT_sheets_de(self, records):
        elements = []
        for i in range(len(records)):
            single_us_sheet = single_UT_pdf_sheet(records[i])
            elements.append(single_us_sheet.create_sheet_de())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Formular_TE.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_UTsheet)
        f.close()
    def build_UT_sheets_en(self, records):
        elements = []
        for i in range(len(records)):
            single_us_sheet = single_UT_pdf_sheet(records[i])
            elements.append(single_us_sheet.create_sheet_en())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Form_UT.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_UTsheet)
        f.close()

    def build_UT_sheets_fr(self, records):
        elements = []
        for i in range(len(records)):
            single_us_sheet = single_UT_pdf_sheet(records[i])
            elements.append(single_us_sheet.create_sheet_fr())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Fiche_UT.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_UTsheet)
        f.close()

    def build_UT_sheets_es(self, records):
        elements = []
        for i in range(len(records)):
            single_us_sheet = single_UT_pdf_sheet(records[i])
            elements.append(single_us_sheet.create_sheet_es())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Ficha_UT.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_UTsheet)
        f.close()

    def build_UT_sheets_ar(self, records):
        elements = []
        for i in range(len(records)):
            single_us_sheet = single_UT_pdf_sheet(records[i])
            elements.append(single_us_sheet.create_sheet_ar())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Bitaqa_UT.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_UTsheet)
        f.close()

    def build_UT_sheets_ca(self, records):
        elements = []
        for i in range(len(records)):
            single_us_sheet = single_UT_pdf_sheet(records[i])
            elements.append(single_us_sheet.create_sheet_ca())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Fitxa_UT.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_UTsheet)
        f.close()

