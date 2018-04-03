#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             -------------------
    begin                : 2007-12-01
    copyright            : (C) 2008 by Luca Mandolesi
    email                : mandoluca at gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         										   *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from datetime import date

from pyarchinit_OS_utility import *
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, PageBreak, SimpleDocTemplate, TableStyle, Image
from reportlab.platypus.paragraph import Paragraph


class NumberedCanvas_Individuisheet(canvas.Canvas):
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


class NumberedCanvas_Individuiindex(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def define_position(self, pos):
        self.page_position(pos)

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        # add page info to each page (page x of y)
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


class Individui_index_pdf_sheet:
    def __init__(self, data):
        self.area = data[1]
        self.us = data[2]
        self.nr_individuo = data[3]
        self.sesso = data[6]
        self.eta_min = data[7]
        self.eta_max = data[8]
        self.classi_eta = data[9]

    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 9

        # self.unzip_rapporti_stratigrafici()

        individuo = Paragraph("<b>Nr Individuo</b><br/>" + str(self.nr_individuo), styNormal)

        if self.area == None:
            area = Paragraph("<b>Area</b><br/>", styNormal)
        else:
            area = Paragraph("<b>Area</b><br/>" + str(self.area), styNormal)

        if str(self.us) == "None":
            us = Paragraph("<b>US</b><br/>", styNormal)
        else:
            us = Paragraph("<b>US</b><br/>" + str(self.us), styNormal)

        if self.eta_min == "None":
            eta_min = Paragraph("<b>Età min.</b><br/>", styNormal)
        else:
            eta_min = Paragraph("<b>Età min.</b><br/>" + str(self.eta_min), styNormal)

        if self.eta_max == "None":
            eta_max = Paragraph("<b>Età max.</b><br/>", styNormal)
        else:
            eta_max = Paragraph("<b>Età max.</b><br/>" + str(self.eta_max), styNormal)

        if self.classi_eta == None:
            classi_eta = Paragraph("<b>Classi età</b><br/>", styNormal)
        else:
            classi_eta = Paragraph("<b>Classi età</b><br/>" + str(self.classi_eta), styNormal)

        data = [individuo,
                area,
                us,
                eta_min,
                eta_max,
                classi_eta]

        return data

    def makeStyles(self):
        styles = TableStyle([('GRID', (0, 0), (-1, -1), 0.0, colors.black), ('VALIGN', (0, 0), (-1, -1), 'TOP')
                             ])  # finale

        return styles


class single_Individui_pdf_sheet:
    def __init__(self, data):
        self.sito = data[0]
        self.area = data[1]
        self.us = data[2]
        self.nr_individuo = data[3]
        self.data_schedatura = data[4]
        self.schedatore = data[5]
        self.sesso = data[6]
        self.eta_min = data[7]
        self.eta_max = data[8]
        self.classi_eta = data[9]
        self.osservazioni = data[10]

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

        """
        #format labels
        self.id_scheda_ind = data[0]
        self.sito = data[1]
        self.area = data[2]
        self.us = data[3]
        self.nr_individuo = data[4]
        self.data_schedatura = data[5]
        self.schedatore = data[6]
        self.sesso = data[7]
        self.eta_min = data[8]
        self.eta_max =  data[9]
        self.classi_eta = data[10]
        self.osservazioni = data[11]
        """
        # 0 row
        intestazione = Paragraph("<b>SCHEDA INDIVIDUI<br/>" + str(self.datestrfdate()) + "</b>", styNormal)
        # intestazione2 = Paragraph("<b>pyArchInit</b>", styNormal)

        if os.name == 'posix':
            home = os.environ['HOME']
        elif os.name == 'nt':
            home = os.environ['HOMEPATH']

        home_DB_path = ('%s%s%s') % (home, os.sep, 'pyarchinit_DB_folder')
        logo_path = ('%s%s%s') % (home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path)

        ##		if test_image.drawWidth < 800:

        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch

        # 1 row
        sito = Paragraph("<b>Sito</b><br/>" + str(self.sito), styNormal)
        area = Paragraph("<b>Area</b><br/>" + str(self.area), styNormal)
        us = Paragraph("<b>US</b><br/>" + str(self.us), styNormal)
        nr_inventario = Paragraph("<b>Nr. Individuo</b><br/>" + str(self.nr_individuo), styNormal)

        # 2 row
        sesso = Paragraph("<b>Sesso</b><br/>" + self.sesso, styNormal)

        if str(self.eta_min) == "None":
            eta_min = Paragraph("<b>Eta' Minima</b><br/>", styNormal)
        else:
            eta_min = Paragraph("<b>Eta' Minima</b><br/>" + str(self.eta_min), styNormal)

        if str(self.eta_max) == "None":
            eta_max = Paragraph("<b>Eta' massima</b><br/>", styNormal)
        else:
            eta_max = Paragraph("<b>Eta' massima</b><br/>" + str(self.eta_max), styNormal)

            # 3 row
        classi_eta_string = str(self.classi_eta).replace("<", "&lt;")
        # classi_eta = Paragraph(classi_eta_string, styNormal)
        classi_eta = Paragraph("<b>Classi di eta'</b><br/>" + classi_eta_string, styNormal)

        # 4 row
        osservazioni = ''
        try:
            osservazioni = Paragraph("<b>Osservazioni</b><br/>" + str(self.osservazioni), styDescrizione)
        except:
            pass

            # 12 row
        data_schedatura = Paragraph("<b>Data schedatura</b><br/>" + self.data_schedatura, styNormal)
        schedatore = Paragraph("<b>Schedatore</b><br/>" + self.schedatore, styNormal)

        # schema
        cell_schema = [  # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],
            [sito, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 1 row ok
            [area, '01', '02', us, '04', '05', nr_inventario, '07', '08', '09'],  # 2row ok
            [sesso, '01', '02', eta_min, '04', '05', eta_max, '07', '08', '09'],  # 3row ok
            [classi_eta, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 4 row ok
            [osservazioni, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 5 row ok
            [data_schedatura, '01', '02', '03', '04', '05', schedatore, '07', '08', '09']  # 5 row ok
            # ['https://sites.google.com/site/pyarchinit/', '01', '02', '03', '04','05', '06', '07','08', '09'] #6 row
        ]

        # table style
        table_style = [

            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row
            ('SPAN', (0, 0), (6, 0)),  # intestazione
            ('SPAN', (7, 0), (9, 0)),  # intestazione2

            # 1 row
            ('SPAN', (0, 1), (9, 1)),  # sito

            # 2 row
            ('SPAN', (0, 2), (2, 2)),  # area
            ('SPAN', (3, 2), (5, 2)),  # us
            ('SPAN', (6, 2), (9, 2)),  # nr_inventario

            # 2 row
            ('SPAN', (0, 3), (2, 3)),  # sesso
            ('SPAN', (3, 3), (5, 3)),  # eta_min
            ('SPAN', (6, 3), (9, 3)),  # eta_max
            ('VALIGN', (0, 3), (9, 3), 'TOP'),

            # 3 row
            ('SPAN', (0, 4), (9, 4)),  # classi_eta

            # 4 row
            ('SPAN', (0, 5), (9, 5)),  # osservazioni

            # 5 row
            ('SPAN', (0, 6), (5, 6)),  # data_schedatura
            ('SPAN', (6, 6), (9, 6)),  # schedatore

            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]

        t = Table(cell_schema, colWidths=50, rowHeights=None, style=table_style)

        return t


class generate_pdf:
    if os.name == 'posix':
        HOME = os.environ['HOME']
    elif os.name == 'nt':
        HOME = os.environ['HOMEPATH']

    PDF_path = ('%s%s%s') % (HOME, os.sep, "pyarchinit_PDF_folder")

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def build_Individui_sheets(self, records):
        elements = []
        for i in range(len(records)):
            single_individui_sheet = single_Individui_pdf_sheet(records[i])
            elements.append(single_individui_sheet.create_sheet())
            elements.append(PageBreak())
        filename = ('%s%s%s') % (self.PDF_path, os.sep, 'scheda_Individui.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_Individuisheet)
        f.close()

    def build_index_individui(self, records, sito):
        if os.name == 'posix':
            home = os.environ['HOME']
        elif os.name == 'nt':
            home = os.environ['HOMEPATH']

        home_DB_path = ('%s%s%s') % (home, os.sep, 'pyarchinit_DB_folder')
        logo_path = ('%s%s%s') % (home_DB_path, os.sep, 'logo.jpg')

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
        lst.append(Paragraph("<b>ELENCO INDIVIDUI</b><br/><b>Scavo: %s, Data: %s</b>" % (sito, data), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = Individui_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable())

        styles = exp_index.makeStyles()
        colWidths = [60, 60, 60, 60, 60, 250]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        # lst.append(Spacer(0,2))

        filename = ('%s%s%s') % (self.PDF_path, os.sep, 'elenco_individui.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(29 * cm, 21 * cm), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_Individuiindex)

        f.close()
