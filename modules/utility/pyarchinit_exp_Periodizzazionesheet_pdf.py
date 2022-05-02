
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
from ..db.pyarchinit_conn_strings import Connection
from .pyarchinit_OS_utility import *


class NumberedCanvas_Periodizzazioneindex(canvas.Canvas):
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


class NumberedCanvas_Periodizzazionesheet(canvas.Canvas):
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
        self.drawRightString(200 * mm, 20 * mm,
                             "Pag. %d di %d" % (self._pageNumber, page_count))  # scheda us verticale 200mm x 20 mm


class Periodizzazione_index_pdf_sheet(object):
    def __init__(self, data):
        self.periodo = data[1]  # 1 - periodo
        self.fase = data[2]  # 2 - fase
        self.cron_iniziale = data[3]  # 3 - cron_iniziale
        self.cron_finale = data[4]  # 4 - cron_finale
        self.datazione_estesa = data[5]  # 5 - datazione_estesa

    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7
        styNormal.fontName = 'Cambria'
        

        # self.unzip_rapporti_stratigrafici()

        periodo = Paragraph("<b>Periodo</b><br/>" + str(self.periodo), styNormal)

        fase = Paragraph("<b>Fase</b><br/>" + str(self.fase), styNormal)

        if str(self.cron_iniziale) == 'None':
            cron_iniziale = Paragraph("<b>Cronologia iniziale</b><br/>" , styNormal)
        else:
            cron_iniziale = Paragraph("<b>Cronologia iniziale</b><br/>" +str(self.cron_iniziale), styNormal)

        if str(self.cron_finale) == 'None':
            cron_finale = Paragraph("<b>Cronologia finale</b><br/>" , styNormal)
        else:
            cron_finale = Paragraph("<b>Cronologia finale</b><br/>" + str(self.cron_finale), styNormal)

        datazione_estesa = Paragraph("<b>Datazione estesa</b><br/>" + str(self.datazione_estesa), styNormal)

        data = [periodo,
                fase,
                cron_iniziale,
                cron_finale,
                datazione_estesa
                ]

        return data
    def getTable_de(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7

        # self.unzip_rapporti_stratigrafici()

        periodo = Paragraph("<b>Period</b><br/>" + str(self.periodo), styNormal)

        fase = Paragraph("<b>Phase</b><br/>" + str(self.fase), styNormal)

        if str(self.cron_iniziale) == "None":
            cron_iniziale = Paragraph("<b>Anfangschronologie</b><br/>" + str(self.cron_iniziale), styNormal)
        else:
            cron_iniziale = Paragraph("<b>Anfangschronologie</b><br/>", styNormal)

        if str(self.cron_finale) == "None":
            cron_finale = Paragraph("<b>Letzte Chronologie</b><br/>" + str(self.cron_finale), styNormal)
        else:
            cron_finale = Paragraph("<b>Letzte Chronologie</b><br/>", styNormal)

        datazione_estesa = Paragraph("<b>Erweiterte Datierung</b><br/>" + str(self.datazione_estesa), styNormal)

        data = [periodo,
                fase,
                cron_iniziale,
                cron_finale,
                datazione_estesa
                ]

        return data
    def getTable_en(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7

        # self.unzip_rapporti_stratigrafici()

        periodo = Paragraph("<b>Period</b><br/>" + str(self.periodo), styNormal)

        fase = Paragraph("<b>Phase</b><br/>" + str(self.fase), styNormal)

        if str(self.cron_iniziale) == "None":
            cron_iniziale = Paragraph("<bStart chronology</b><br/>" + str(self.cron_iniziale), styNormal)
        else:
            cron_iniziale = Paragraph("<b>Start chronology</b><br/>", styNormal)

        if str(self.cron_finale) == "None":
            cron_finale = Paragraph("<b>Final chronology</b><br/>" + str(self.cron_finale), styNormal)
        else:
            cron_finale = Paragraph("<b>Final chronology</b><br/>", styNormal)

        datazione_estesa = Paragraph("<b>Letteral datation</b><br/>" + str(self.datazione_estesa), styNormal)

        data = [periodo,
                fase,
                cron_iniziale,
                cron_finale,
                datazione_estesa
                ]

        return data 
    def makeStyles(self):
        styles = TableStyle([('GRID', (0, 0), (-1, -1), 0.0, colors.black), ('VALIGN', (0, 0), (-1, -1), 'TOP')
                             ])  # finale

        return styles


class single_Periodizzazione_pdf_sheet(object):
    def __init__(self, data):
        self.sito = data[0]
        self.periodo = data[1]
        self.fase = data[2]
        self.cron_iniziale = data[3]
        self.cron_finale = data[4]
        self.datazione_estesa = data[5]
        self.descrizione = data[6]

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
        styNormal.fontSize = 7
        styNormal.fontName = 'Cambria'
        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.alignment = 4  # Justified
        styDescrizione.fontSize = 7
        styDescrizione.fontName = 'Cambria'

        # format labels

        # 0 row
        intestazione = Paragraph("<b>SCHEDA PERIODIZZAZIONE</b>", styNormal)

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
        sito = Paragraph("<b>Sito</b><br/>" + str(self.sito), styNormal)
        periodo = Paragraph("<b>Periodo</b><br/>" + str(self.periodo), styNormal)
        fase = Paragraph("<b>Fase</b><br/>" + str(self.fase), styNormal)

        # 2 row
        cronologia = Paragraph("<b>CRONOLOGIA</b><br/>", styNormal)

        # 3 row
        cronologia_iniziale = Paragraph("<b>Cronologia iniziale</b><br/>" + str(self.cron_iniziale), styNormal)
        cronologia_finale = Paragraph("<b>Cronologia finale</b><br/>" + str(self.cron_finale), styNormal)
        datazione_ext = Paragraph("<b>Cronologia testuale</b><br/>" + str(self.datazione_estesa), styNormal)

        # 4 row
        descrizione = ''
        try:
            descrizione = Paragraph("<b>Descrizione</b><br/>" + str(self.descrizione), styDescrizione)
        except:
            pass

            # schema
        cell_schema = [  # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],  # 0 row ok
            [sito, '01', '02', '03', '04', '05', '06', '07', periodo, fase],  # 1 row ok
            [cronologia, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 2 row ok
            [cronologia_iniziale, '01', cronologia_finale, '03', datazione_ext, '05', '06', '07', '08', '09'],
            # 3 row
            [descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09']]  # 4row ok

        # table style
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row
            ('SPAN', (0, 0), (6, 0)),  # intestazione
            ('SPAN', (7, 0), (9, 0)),  # intestazione

            # 1 row
            ('SPAN', (0, 1), (7, 1)),  # Sito
            ('SPAN', (8, 1), (8, 1)),  # periodo
            ('SPAN', (9, 1), (9, 1)),  # fase

            # 2 row
            ('SPAN', (0, 2), (9, 2)),  # intestazione cronologia

            # 3 row
            ('SPAN', (0, 3), (1, 3)),  # cron iniziale
            ('SPAN', (2, 3), (3, 3)),  # cron finale
            ('SPAN', (4, 3), (9, 3)),  # datazione estesa

            # 4
            ('SPAN', (0, 4), (9, 4)),  # datazione estesa
            ('VALIGN', (0, 4), (9, 4), 'TOP'),
            # ('VALIGN',(5,3),(5,3),'TOP'),

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
        styNormal.fontSize = 7
        styNormal.fontName = 'Cambria'
        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.alignment = 4  # Justified
        styDescrizione.fontSize = 7
        styDescrizione.fontName = 'Cambria'

        # format labels

        # 0 row
        intestazione = Paragraph("<b>FORMULAR PERIOD<br/>" + str(self.datestrfdate()) + "</b>", styNormal)

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
        sito = Paragraph("<b>Ausgrabungsstätte</b><br/>" + str(self.sito), styNormal)
        periodo = Paragraph("<b>Period</b><br/>" + str(self.periodo), styNormal)
        fase = Paragraph("<b>Phase</b><br/>" + str(self.fase), styNormal)

        # 2 row
        cronologia = Paragraph("<b>CHRONOLOGIE</b><br/>", styNormal)

        # 3 row
        cronologia_iniziale = Paragraph("<b>Anfangschronologie</b><br/>" + str(self.cron_iniziale), styNormal)
        cronologia_finale = Paragraph("<b>Letzte Chronologie</b><br/>" + str(self.cron_finale), styNormal)
        datazione_ext = Paragraph("<b>Erweiterte Datierung</b><br/>" + str(self.datazione_estesa), styNormal)

        # 4 row
        descrizione = ''
        try:
            descrizione = Paragraph("<b>Beschreibung</b><br/>" + str(self.descrizione), styDescrizione)
        except:
            pass

            # schema
        cell_schema = [  # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],  # 0 row ok
            [sito, '01', '02', '03', '04', '05', '06', '07', periodo, fase],  # 1 row ok
            [cronologia, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 2 row ok
            [cronologia_iniziale, '01', cronologia_finale, '03', datazione_ext, '05', '06', '07', '08', '09'],
            # 3 row
            [descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09']]  # 4row ok

        # table style
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row
            ('SPAN', (0, 0), (6, 0)),  # intestazione
            ('SPAN', (7, 0), (9, 0)),  # intestazione

            # 1 row
            ('SPAN', (0, 1), (7, 1)),  # Sito
            ('SPAN', (8, 1), (8, 1)),  # periodo
            ('SPAN', (9, 1), (9, 1)),  # fase

            # 2 row
            ('SPAN', (0, 2), (9, 2)),  # intestazione cronologia

            # 3 row
            ('SPAN', (0, 3), (1, 3)),  # cron iniziale
            ('SPAN', (2, 3), (3, 3)),  # cron finale
            ('SPAN', (4, 3), (9, 3)),  # datazione estesa

            # 4
            ('SPAN', (0, 4), (9, 4)),  # datazione estesa
            ('VALIGN', (0, 4), (9, 4), 'TOP'),
            # ('VALIGN',(5,3),(5,3),'TOP'),

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
        intestazione = Paragraph("<b>PERIODIZATION FORM<br/>" + str(self.datestrfdate()) + "</b>", styNormal)

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
        sito = Paragraph("<b>Site</b><br/>" + str(self.sito), styNormal)
        periodo = Paragraph("<b>Period</b><br/>" + str(self.periodo), styNormal)
        fase = Paragraph("<b>Phase</b><br/>" + str(self.fase), styNormal)

        # 2 row
        cronologia = Paragraph("<b>CHRONOLOGY</b><br/>", styNormal)

        # 3 row
        cronologia_iniziale = Paragraph("<b>Start chronology</b><br/>" + str(self.cron_iniziale), styNormal)
        cronologia_finale = Paragraph("<b>Final chronology</b><br/>" + str(self.cron_finale), styNormal)
        datazione_ext = Paragraph("<b>Letteral datation</b><br/>" + str(self.datazione_estesa), styNormal)

        # 4 row
        descrizione = ''
        try:
            descrizione = Paragraph("<b>Description</b><br/>" + str(self.descrizione), styDescrizione)
        except:
            pass

            # schema
        cell_schema = [  # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],  # 0 row ok
            [sito, '01', '02', '03', '04', '05', '06', '07', periodo, fase],  # 1 row ok
            [cronologia, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 2 row ok
            [cronologia_iniziale, '01', cronologia_finale, '03', datazione_ext, '05', '06', '07', '08', '09'],
            # 3 row
            [descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09']]  # 4row ok

        # table style
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row
            ('SPAN', (0, 0), (6, 0)),  # intestazione
            ('SPAN', (7, 0), (9, 0)),  # intestazione

            # 1 row
            ('SPAN', (0, 1), (7, 1)),  # Sito
            ('SPAN', (8, 1), (8, 1)),  # periodo
            ('SPAN', (9, 1), (9, 1)),  # fase

            # 2 row
            ('SPAN', (0, 2), (9, 2)),  # intestazione cronologia

            # 3 row
            ('SPAN', (0, 3), (1, 3)),  # cron iniziale
            ('SPAN', (2, 3), (3, 3)),  # cron finale
            ('SPAN', (4, 3), (9, 3)),  # datazione estesa

            # 4
            ('SPAN', (0, 4), (9, 4)),  # datazione estesa
            ('VALIGN', (0, 4), (9, 4), 'TOP'),
            # ('VALIGN',(5,3),(5,3),'TOP'),

            ('VALIGN', (0, 0), (-1, -1), 'TOP')

        ]

        t = Table(cell_schema, colWidths=50, rowHeights=None, style=table_style)

        return t
class generate_Periodizzazione_pdf(object):
    HOME = os.environ['PYARCHINIT_HOME']

    PDF_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def build_Periodizzazione_sheets(self, records):
        elements = []
        for i in range(len(records)):
            single_periodizzazione_sheet = single_Periodizzazione_pdf_sheet(records[i])
            elements.append(single_periodizzazione_sheet.create_sheet())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Scheda Periodizzazione.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_Periodizzazionesheet)
        f.close()
    def build_Periodizzazione_sheets_de(self, records):
        elements = []
        for i in range(len(records)):
            single_periodizzazione_sheet = single_Periodizzazione_pdf_sheet(records[i])
            elements.append(single_periodizzazione_sheet.create_sheet_de())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'formular_period.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_Periodizzazionesheet)
        f.close()
    def build_Periodizzazione_sheets_en(self, records):
        elements = []
        for i in range(len(records)):
            single_periodizzazione_sheet = single_Periodizzazione_pdf_sheet(records[i])
            elements.append(single_periodizzazione_sheet.create_sheet_en())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'form_Periodization.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_Periodizzazionesheet)
        f.close()   
    def build_index_Periodizzazione(self, records, sito):
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
        lst.append(Paragraph("<b>ELENCO PERIODIZZAZIONI</b><br/><b>Scavo: %s</b>" % (sito), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = Periodizzazione_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable())

        styles = exp_index.makeStyles()
        colWidths = [60, 60, 150, 150, 300]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        # lst.append(Spacer(0,2))

        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Elenco Periodizzazione.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(29 * cm, 21 * cm), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_Periodizzazioneindex)

        f.close()
    def build_index_Periodizzazione_de(self, records, sito):
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
        lst.append(Paragraph("<b>LISTE PERIOD</b><br/><b>Ausgrabungsstätte: %s,  Datum: %s</b>" % (sito, data), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = Periodizzazione_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable_de())

        styles = exp_index.makeStyles()
        colWidths = [60, 60, 150, 150, 300]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        # lst.append(Spacer(0,2))

        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Liste_period.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(29 * cm, 21 * cm), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_Periodizzazioneindex)

        f.close()
    def build_index_Periodizzazione_en(self, records, sito):
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
        lst.append(Paragraph("<b>LIST PERIODIZATION</b><br/><b>Site: %s,  Date: %s</b>" % (sito, data), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = Periodizzazione_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable_en())

        styles = exp_index.makeStyles()
        colWidths = [60, 60, 150, 150, 300]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        # lst.append(Spacer(0,2))

        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'list_periodization.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(29 * cm, 21 * cm), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_Periodizzazioneindex)

        f.close()   
