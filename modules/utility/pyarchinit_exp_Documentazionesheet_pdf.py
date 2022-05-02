
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

import os
from datetime import date

from .pyarchinit_OS_utility import *
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

class NumberedCanvas_Documentazionesheet(canvas.Canvas):
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


class NumberedCanvas_Documentazioneindex(canvas.Canvas):
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


'''
class NumberedCanvas_CASSEindex(canvas.Canvas):
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
        self.setFont("Cambria", 8)
        self.drawRightString(270*mm, 10*mm, "Pag. %d di %d" % (self._pageNumber, page_count)) #scheda us verticale 200mm x 20 mm

'''


class single_Documentazione_pdf_sheet:
    def __init__(self, data):
        self.sito = data[0]  # 1 - Sito
        self.nome_doc = data[1]  # 2 - Numero campione
        self.data = data[2]  # 3 - Tipo campione
        self.tipo_documentazione = data[3]  # 4 - Descrizione
        self.sorgente = data[4]  # 5 - Area
        self.scala = data[5]  # 6 - us
        self.disegnatore = data[6]  # 7 - numero inventario materiale
        self.note = data[7]  # 8 - luogo_conservazione

    #       self.nr_cassa = data[8]                                 #9 - nr cassa

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
        intestazione = Paragraph("<b>SCHEDA DOCUMENTAZIONE<br/></b>", styNormal)

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
        nome_doc = Paragraph("<b>Nome documentazione</b><br/>" + str(self.nome_doc), styNormal)
        data = Paragraph("<b>Data</b><br/>" + str(self.data), styNormal)

        # 2 row
        tipo_documentazione = Paragraph("<b>Tipo documentazione</b><br/>" + str(self.tipo_documentazione), styNormal)
        sorgente = Paragraph("<b>Sorgente</b><br/>" + str(self.sorgente), styNormal)
        scala = Paragraph("<b>Scala</b><br/>" + str(self.scala), styNormal)

        # 4 row
        disegnatore = Paragraph("<b>Disegnatore</b><br/>" + str(self.disegnatore), styNormal)

        # 4 row
        note = Paragraph("<b>Note</b><br/>" + str(self.note), styDescrizione)
        #       nr_cassa = Paragraph("<b>N° Cassa</b><br/>" + unicode(self.nr_cassa), styNormal)

        # schema
        cell_schema = [  # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],  # 0 row ok
            [sito, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 1 row ok
            [tipo_documentazione, '01', '02', nome_doc, '04', '05', '06', scala, '08', '09'],  # 2 row ok
            [note, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 3 row ok
            [data, '01', '02', '03', '04', disegnatore, '06', '07', '08', '09']  # 4 row ok
        ]

        # table style
        table_style = [

            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row
            ('SPAN', (0, 0), (6, 0)),  # intestazione
            ('SPAN', (7, 0), (9, 0)),  # logo

            # 1 row
            ('SPAN', (0, 1), (9, 1)),  # sito
            #                   ('SPAN', (7,1),(9,1)),   #data

            # 2 row
            ('SPAN', (0, 2), (2, 2)),  # tipo_documentazione
            ('SPAN', (3, 2), (6, 2)),  # nome_doc
            ('SPAN', (7, 2), (9, 2)),  # scala
            #                   ('VALIGN',(0,2),(9,2),'TOP'),

            # 3 row
            ('SPAN', (0, 3), (9, 3)),  # note
            ('VALIGN', (0, 3), (9, 3), 'TOP'),

            # 5 row
            ('SPAN', (0, 4), (4, 4)),  # data
            ('SPAN', (5, 4), (9, 4)),  # disegnatore

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
        intestazione = Paragraph("<b>FORMULAR DOCUMENTATION<br/>" + str(self.datestrfdate()) + "</b>", styNormal)

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
        nome_doc = Paragraph("<b>Nomen documentation</b><br/>" + str(self.nome_doc), styNormal)
        data = Paragraph("<b>Datum</b><br/>" + str(self.data), styNormal)

        # 2 row
        tipo_documentazione = Paragraph("<b>Documentationtyp</b><br/>" + str(self.tipo_documentazione), styNormal)
        sorgente = Paragraph("<b>Quelle</b><br/>" + str(self.sorgente), styNormal)
        scala = Paragraph("<b>Maßstab</b><br/>" + str(self.scala), styNormal)

        # 4 row
        disegnatore = Paragraph("<bZeichner</b><br/>" + str(self.disegnatore), styNormal)

        # 4 row
        note = Paragraph("<b>Notes</b><br/>" + str(self.note), styDescrizione)
        #       nr_cassa = Paragraph("<b>N° Cassa</b><br/>" + unicode(self.nr_cassa), styNormal)

        # schema
        cell_schema = [  # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],  # 0 row ok
            [sito, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 1 row ok
            [tipo_documentazione, '01', '02', nome_doc, '04', '05', '06', scala, '08', '09'],  # 2 row ok
            [note, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 3 row ok
            [data, '01', '02', '03', '04', disegnatore, '06', '07', '08', '09']  # 4 row ok
        ]

        # table style
        table_style = [

            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row
            ('SPAN', (0, 0), (6, 0)),  # intestazione
            ('SPAN', (7, 0), (9, 0)),  # logo

            # 1 row
            ('SPAN', (0, 1), (9, 1)),  # sito
            #                   ('SPAN', (7,1),(9,1)),   #data

            # 2 row
            ('SPAN', (0, 2), (2, 2)),  # tipo_documentazione
            ('SPAN', (3, 2), (6, 2)),  # nome_doc
            ('SPAN', (7, 2), (9, 2)),  # scala
            #                   ('VALIGN',(0,2),(9,2),'TOP'),

            # 3 row
            ('SPAN', (0, 3), (9, 3)),  # note
            ('VALIGN', (0, 3), (9, 3), 'TOP'),

            # 5 row
            ('SPAN', (0, 4), (4, 4)),  # data
            ('SPAN', (5, 4), (9, 4)),  # disegnatore

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
        intestazione = Paragraph("<b>DOCUMENTATION FORM<br/>" + str(self.datestrfdate()) + "</b>", styNormal)

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
        nome_doc = Paragraph("<b>Documentation name</b><br/>" + str(self.nome_doc), styNormal)
        data = Paragraph("<b>Date</b><br/>" + str(self.data), styNormal)

        # 2 row
        tipo_documentazione = Paragraph("<b>Documentation type</b><br/>" + str(self.tipo_documentazione), styNormal)
        sorgente = Paragraph("<b>Source</b><br/>" + str(self.sorgente), styNormal)
        scala = Paragraph("<b>Scale</b><br/>" + str(self.scala), styNormal)

        # 4 row
        disegnatore = Paragraph("<b>Draftman</b><br/>" + str(self.disegnatore), styNormal)

        # 4 row
        note = Paragraph("<b>Note</b><br/>" + str(self.note), styDescrizione)
        #       nr_cassa = Paragraph("<b>N° Cassa</b><br/>" + unicode(self.nr_cassa), styNormal)

        # schema
        cell_schema = [  # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],  # 0 row ok
            [sito, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 1 row ok
            [tipo_documentazione, '01', '02', nome_doc, '04', '05', '06', scala, '08', '09'],  # 2 row ok
            [note, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 3 row ok
            [data, '01', '02', '03', '04', disegnatore, '06', '07', '08', '09']  # 4 row ok
        ]

        # table style
        table_style = [

            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row
            ('SPAN', (0, 0), (6, 0)),  # intestazione
            ('SPAN', (7, 0), (9, 0)),  # logo

            # 1 row
            ('SPAN', (0, 1), (9, 1)),  # sito
            #                   ('SPAN', (7,1),(9,1)),   #data

            # 2 row
            ('SPAN', (0, 2), (2, 2)),  # tipo_documentazione
            ('SPAN', (3, 2), (6, 2)),  # nome_doc
            ('SPAN', (7, 2), (9, 2)),  # scala
            #                   ('VALIGN',(0,2),(9,2),'TOP'),

            # 3 row
            ('SPAN', (0, 3), (9, 3)),  # note
            ('VALIGN', (0, 3), (9, 3), 'TOP'),

            # 5 row
            ('SPAN', (0, 4), (4, 4)),  # data
            ('SPAN', (5, 4), (9, 4)),  # disegnatore

            ('VALIGN', (0, 0), (-1, -1), 'TOP')

        ]

        t = Table(cell_schema, colWidths=50, rowHeights=None, style=table_style)

        return t    
'''

class Box_labels_Campioni_pdf_sheet:

    def __init__(self, data, sito):
        self.sito = sito #Sito
        self.cassa= data[0] #1 - Cassa
        self.elenco_inv_tip_rep = data[1] #2-  elenco US
        self.elenco_us = data[2] #3 - elenco Inventari
        self.luogo_conservazione = data[3]#4 - luogo conservazione

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def create_sheet(self):
        styleSheet = getSampleStyleSheet()
        
        styleSheet.add(ParagraphStyle(name='Cassa Label'))
        styleSheet.add(ParagraphStyle(name='Sito Label'))

        styCassaLabel = styleSheet['Cassa Label']
        styCassaLabel.spaceBefore = 0
        styCassaLabel.spaceAfter = 0
        styCassaLabel.alignment = 2 #RIGHT
        styCassaLabel.leading = 25
        styCassaLabel.fontSize = 30

        stySitoLabel = styleSheet['Sito Label']
        stySitoLabel.spaceBefore = 0
        stySitoLabel.spaceAfter = 0
        stySitoLabel.alignment = 0 #LEFT
        stySitoLabel.leading = 25
        stySitoLabel.fontSize = 18
        stySitoLabel.fontStyle = 'bold'

        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 10
        styNormal.spaceAfter = 10
        styNormal.alignment = 0 #LEFT
        styNormal.fontSize = 14
        styNormal.leading = 15


        #format labels
        if os.name == 'posix':
            home = os.environ['HOME']
        elif os.name == 'nt':
            home = os.environ['HOMEPATH']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path)

        ##      if test_image.drawWidth < 800:

        logo.drawHeight = 1.5*inch*logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5*inch
        

        num_cassa = Paragraph("<b>N° Cassa </b>" + str(self.cassa),styCassaLabel)
        sito = Paragraph("<b>Sito: </b>" + str(self.sito),stySitoLabel)

        if self.elenco_inv_tip_rep == None:
            elenco_inv_tip_rep = Paragraph("<b>Elenco N° Inv. / Tipo campione</b><br/>",styNormal)
        else:
            elenco_inv_tip_rep = Paragraph("<b>Elenco N° Inv. / Tipo campione</b><br/>" + str(self.elenco_inv_tip_rep ),styNormal)

        if self.elenco_us == None:
            elenco_us = Paragraph("<b>Elenco US/(Struttura)</b>",styNormal)
        else:
            elenco_us = Paragraph("<b>Elenco US/(Struttura)</b><br/>" + str(self.elenco_us),styNormal)

        #luogo_conservazione = Paragraph("<b>Luogo di conservazione</b><br/>" + str(self.luogo_conservazione),styNormal)

        #schema
        cell_schema =   [ #00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
                            [logo, '01', '02', '03', '04','05', num_cassa, '07', '08', '09'],
                            [sito, '01', '02', '03', '04','05', '06', '07', '08', '09'],
                            [elenco_us, '01', '02', '03','04', '05','06', '07', '08', '09'],
                            [elenco_inv_tip_rep, '01', '02','03', '04', '05','06', '07', '08', '09']

                        ]



        #table style
        table_style=[

                    ('GRID',(0,0),(-1,-1),0,colors.white),#,0.0,colors.black
                    #0 row
                    ('SPAN', (0,0),(5,0)),  #elenco US
                    ('SPAN', (6,0),(9,0)),  #elenco US
                    ('HALIGN',(0,0),(9,0),'LEFT'),
                    ('VALIGN',(6,0),(9,0),'TOP'),
                    ('HALIGN',(6,0),(9,0),'RIGHT'),

                    ('SPAN', (0,1),(9,1)),  #elenco US
                    ('HALIGN',(0,1),(9,1),'LEFT'),

                    ('SPAN', (0,2),(9,2)),  #intestazione
                    ('VALIGN',(0,2),(9,2),'TOP'), 
                    #1 row
                    ('SPAN', (0,3),(9,3)),  #elenco US
                    ('VALIGN',(0,3),(9,3),'TOP')

                    ]


        colWidths=None
        rowHeights=None
        #colWidths=[80,80,80, 80,80, 80,80,80,80, 80]
        t=Table(cell_schema,colWidths,rowHeights, style= table_style)

        return t
'''
'''
class CASSE_index_pdf_sheet:

    def __init__(self, data):
        self.tipo_documentazione= data[0] #1 - Tipo documentazione
        self.nome_doc = data[1] #2-  Nome documentazione
        self.data = data[2] #3 - Data
        self.scala = data[3]#4 - Scala
        self.disegnatore = data[3]#4 - Disegnatore

    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0 #LEFT
        styNormal.fontSize = 10

        #self.unzip_rapporti_stratigrafici()

        num_cassa = Paragraph("<b>Nr.</b><br/>" + str(self.cassa),styNormal)

        if self.elenco_inv_tip_camp == None:
            elenco_inv_tip_camp = Paragraph("<b>N° Inv./Tipo campione</b><br/>",styNormal)
        else:
            elenco_inv_tip_camp = Paragraph("<b>N° Inv./Tipo campione</b><br/>" + str(self.elenco_inv_tip_camp ),styNormal)

        if self.elenco_us == None:
            elenco_us = Paragraph("<b>US(Struttura)</b><br/>",styNormal)
        else:
            elenco_us = Paragraph("<b>US(Struttura)</b><br/>" + str(self.elenco_us),styNormal)

        luogo_conservazione = Paragraph("<b>Luogo di conservazione</b><br/>" + str(self.luogo_conservazione),styNormal)

        data = [num_cassa,
                    elenco_inv_tip_camp,
                    elenco_us,
                    luogo_conservazione]

        return data

    def makeStyles(self):
        styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')])  #finale

        return styles

'''


class Documentazione_index_pdf_sheet:
    def __init__(self, data):
        self.sito = data[0]  # 1 - Sito
        self.nome_doc = data[1]  # 2 - Nome documentazione
        self.data = data[2]  # 3 - Data
        self.tipo_documentazione = data[3]  # 4 - Tipo documentazione
        self.sorgente = data[4]  # 5 - Sorgente
        self.scala = data[5]  # 6 - Scala
        self.disegnatore = data[6]  # 7 - Disegnatore
        self.us = data[8]  # 8 - Note

    #       self.nr_cassa = data[8]                                 #9 - nr cassa

    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7
        styNormal.fontName = 'Cambria'
        # self.unzip_rapporti_stratigrafici()

        #       num_campione = Paragraph("<b>N° Camp.</b><br/>" + str(self.numero_campione),styNormal)


        if self.tipo_documentazione == "":
            tipo_documentazione = Paragraph("<b>Tipo</b><br/>", styNormal)
        else:
            tipo_documentazione = Paragraph("<b>Tipo</b><br/>" + str(self.tipo_documentazione), styNormal)

        if self.nome_doc == "":
            nome_doc = Paragraph("<b>Nome documentazione</b><br/>", styNormal)
        else:
            nome_doc = Paragraph("<b>Nome documentazione</b><br/>" + str(self.nome_doc), styNormal)

        if self.scala == "":
            scala = Paragraph("<b>Scala</b><br/>", styNormal)
        else:
            scala = Paragraph("<b>Scala</b><br/>" + str(self.scala), styNormal)

        if self.sorgente == "":
            sorgente = Paragraph("<b>Sorgente</b><br/>", styNormal)
        else:
            sorgente = Paragraph("<b>Sorgente</b><br/>" + str(self.sorgente), styNormal)

        if self.data == "":
            data = Paragraph("<b>Data</b><br/>", styNormal)
        else:
            data = Paragraph("<b>Data</b><br/>" + str(self.data), styNormal)

        if self.disegnatore == "":
            disegnatore = Paragraph("<b>Disegnatore</b><br/>", styNormal)
        else:
            disegnatore = Paragraph("<b>Disegnatore</b><br/>" + str(self.disegnatore), styNormal)

        if self.us == "":
            us = Paragraph("<b>Note</b><br/>", styNormal)
        else:
            us = Paragraph("<b>Note</b><br/>" + str(self.us), styNormal)

        data = [tipo_documentazione,
                nome_doc,
                scala,
                sorgente,
                data,
                disegnatore,
                us]

        return data
    def getTable_de(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7

        # self.unzip_rapporti_stratigrafici()

        #       num_campione = Paragraph("<b>N° Camp.</b><br/>" + str(self.numero_campione),styNormal)


        if self.tipo_documentazione == "":
            tipo_documentazione = Paragraph("<b>Typ</b><br/>", styNormal)
        else:
            tipo_documentazione = Paragraph("<b>Typ</b><br/>" + str(self.tipo_documentazione), styNormal)

        if self.nome_doc == "":
            nome_doc = Paragraph("<b>Nomen documentation</b><br/>", styNormal)
        else:
            nome_doc = Paragraph("<b>Nomen documentation</b><br/>" + str(self.nome_doc), styNormal)

        if self.scala == "":
            scala = Paragraph("<b>Maßstab</b><br/>", styNormal)
        else:
            scala = Paragraph("<b>Maßstab</b><br/>" + str(self.scala), styNormal)

        if self.sorgente == "":
            sorgente = Paragraph("<b>Quelle</b><br/>", styNormal)
        else:
            sorgente = Paragraph("<b>Quelle</b><br/>" + str(self.sorgente), styNormal)

        if self.data == "":
            data = Paragraph("<b>Datum</b><br/>", styNormal)
        else:
            data = Paragraph("<b>Datum</b><br/>" + str(self.data), styNormal)

        if self.disegnatore == "":
            disegnatore = Paragraph("<b>Zeichner</b><br/>", styNormal)
        else:
            disegnatore = Paragraph("<b>Zeichner</b><br/>" + str(self.disegnatore), styNormal)

        if self.us == "":
            us = Paragraph("<b>Notes</b><br/>", styNormal)
        else:
            us = Paragraph("<b>Notes</b><br/>" + str(self.us), styNormal)

        data = [tipo_documentazione,
                nome_doc,
                scala,
                sorgente,
                data,
                disegnatore,
                us]

        return data
        
    def getTable_en(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7

        # self.unzip_rapporti_stratigrafici()

        #       num_campione = Paragraph("<b>N° Camp.</b><br/>" + str(self.numero_campione),styNormal)


        if self.tipo_documentazione == "":
            tipo_documentazione = Paragraph("<b>Type</b><br/>", styNormal)
        else:
            tipo_documentazione = Paragraph("<b>Type</b><br/>" + str(self.tipo_documentazione), styNormal)

        if self.nome_doc == "":
            nome_doc = Paragraph("<b>Documentation name</b><br/>", styNormal)
        else:
            nome_doc = Paragraph("<b>Documentation name</b><br/>" + str(self.nome_doc), styNormal)

        if self.scala == "":
            scala = Paragraph("<b>Scale</b><br/>", styNormal)
        else:
            scala = Paragraph("<b>Scale</b><br/>" + str(self.scala), styNormal)

        if self.sorgente == "":
            sorgente = Paragraph("<b>Source</b><br/>", styNormal)
        else:
            sorgente = Paragraph("<b>Source</b><br/>" + str(self.sorgente), styNormal)

        if self.data == "":
            data = Paragraph("<b>Date</b><br/>", styNormal)
        else:
            data = Paragraph("<b>Date</b><br/>" + str(self.data), styNormal)

        if self.disegnatore == "":
            disegnatore = Paragraph("<b>Draftman</b><br/>", styNormal)
        else:
            disegnatore = Paragraph("<b>Draftman</b><br/>" + str(self.disegnatore), styNormal)

        if self.us == "":
            us = Paragraph("<b>Note</b><br/>", styNormal)
        else:
            us = Paragraph("<b>Note</b><br/>" + str(self.us), styNormal)

        data = [tipo_documentazione,
                nome_doc,
                scala,
                sorgente,
                data,
                disegnatore,
                us]

        return data 
    def makeStyles(self):
        styles = TableStyle([('GRID', (0, 0), (-1, -1), 0.0, colors.black), ('VALIGN', (0, 0), (-1, -1), 'TOP')
                             ])  # finale

        return styles


class generate_documentazione_pdf:
    HOME = os.environ['PYARCHINIT_HOME']

    PDF_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def build_Documentazione_sheets(self, records):
        elements = []
        for i in range(len(records)):
            single_Documentazione_sheet = single_Documentazione_pdf_sheet(records[i])
            elements.append(single_Documentazione_sheet.create_sheet())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Scheda Documentazione.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_Documentazionesheet)
        f.close()
    def build_Documentazione_sheets_de(self, records):
        elements = []
        for i in range(len(records)):
            single_Documentazione_sheet = single_Documentazione_pdf_sheet(records[i])
            elements.append(single_Documentazione_sheet.create_sheet())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Dodumentation_formular.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_Documentazionesheet)
        f.close()
    def build_Documentazione_sheets_en(self, records):
        elements = []
        for i in range(len(records)):
            single_Documentazione_sheet = single_Documentazione_pdf_sheet(records[i])
            elements.append(single_Documentazione_sheet.create_sheet())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Documentation_form.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_Documentazionesheet)
        f.close()   
    def build_index_Documentazione(self, records, sito):
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
        lst.append(Paragraph("<b>ELENCO DOCUMENTAZIONE</b><br/><b>Scavo: %s</b>" % (sito), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = Documentazione_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable())

        styles = exp_index.makeStyles()
        colWidths = [100, 100, 60, 60, 60, 150]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        # lst.append(Spacer(0,2))

        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Elenco Documentazione.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(29 * cm, 21 * cm), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_Documentazioneindex)

        f.close()
    def build_index_Documentazione_de(self, records, sito):
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
        lst.append(Paragraph("<b>LISTE DOCUMENTATION</b><br/><b>Ausgrabungsstätte: %s,  Datum: %s</b>" % (sito, data), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = Documentazione_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable())

        styles = exp_index.makeStyles()
        colWidths = [100, 100, 60, 60, 60, 150]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        # lst.append(Spacer(0,2))

        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'liste_documentation.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(29 * cm, 21 * cm), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_Documentazioneindex)

        f.close()
    def build_index_Documentazione_en(self, records, sito):
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
        lst.append(Paragraph("<b>DOCUMENTATION LIST</b><br/><b>Site: %s,  Date: %s</b>" % (sito, data), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = Documentazione_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable())

        styles = exp_index.makeStyles()
        colWidths = [100, 100, 60, 60, 60, 150]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        # lst.append(Spacer(0,2))

        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'documentation_list.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(29 * cm, 21 * cm), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_Documentazioneindex)

        f.close()

