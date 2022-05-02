
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


class NumberedCanvas_STRUTTURAindex(canvas.Canvas):
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


class NumberedCanvas_STRUTTURAsheet(canvas.Canvas):
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


class Struttura_index_pdf_sheet(object):
    def __init__(self, data):
        self.sigla_struttura = data[1]
        self.numero_struttura = data[2]
        self.categoria_struttura = data[3]
        self.tipologia_struttura = data[4]
        self.definizione_struttura = data[5]
        self.periodo_iniziale = data[8]
        self.fase_iniziale = data[9]
        self.periodo_finale = data[10]
        self.fase_finale = data[11]
        self.datazione_estesa = data[12]

    def getTable(self):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.alignment = 0  # LEFT
        styNormal.fontSize = 7
        styNormal.fontName = 'Cambria'
        

        # self.unzip_rapporti_stratigrafici()

        sigla = Paragraph("<b>Sigla</b><br/>" + str(self.sigla_struttura), styNormal)

        nr_struttura = Paragraph("<b>N° struttura</b><br/>" + str(self.numero_struttura), styNormal)

        categoria_struttura = Paragraph("<b>Categoria</b><br/>" + str(self.categoria_struttura), styNormal)

        tipologia_struttura = Paragraph("<b>Tipologia</b><br/>" + str(self.tipologia_struttura), styNormal)

        definizione_struttura = Paragraph("<b>Definizione</b><br/>" + str(self.definizione_struttura), styNormal)

        periodo_iniziale = Paragraph("<b>Periodo iniziale</b><br/>" + str(self.periodo_iniziale), styNormal)

        fase_iniziale = Paragraph("<b>Fase iniziale</b><br/>" + str(self.fase_iniziale), styNormal)

        periodo_finale = Paragraph("<b>Periodo finale</b><br/>" + str(self.periodo_finale), styNormal)

        fase_finale = Paragraph("<b>Fase finale</b><br/>" + str(self.fase_finale), styNormal)

        datazione_estesa = Paragraph("<b>Datazione estesa</b><br/>" + str(self.datazione_estesa), styNormal)

        data = [sigla,
                nr_struttura,
                categoria_struttura,
                tipologia_struttura,
                definizione_struttura,
                periodo_iniziale,
                fase_iniziale,
                periodo_finale,
                fase_finale,
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

        sigla = Paragraph("<b>Code</b><br/>" + str(self.sigla_struttura), styNormal)

        nr_struttura = Paragraph("<b>N° Struktur</b><br/>" + str(self.numero_struttura), styNormal)

        categoria_struttura = Paragraph("<b>Kategorie</b><br/>" + str(self.categoria_struttura), styNormal)

        tipologia_struttura = Paragraph("<b>Typologie</b><br/>" + str(self.tipologia_struttura), styNormal)

        definizione_struttura = Paragraph("<b>Definition</b><br/>" + str(self.definizione_struttura), styNormal)

        periodo_iniziale = Paragraph("<b>Anfangszeitraum</b><br/>" + str(self.periodo_iniziale), styNormal)

        fase_iniziale = Paragraph("<b>Anfangsphase</b><br/>" + str(self.fase_iniziale), styNormal)

        periodo_finale = Paragraph("<b>Letzte zeitraum</b><br/>" + str(self.periodo_finale), styNormal)

        fase_finale = Paragraph("<b>Letzte phase</b><br/>" + str(self.fase_finale), styNormal)

        datazione_estesa = Paragraph("<b>Erweiterte Datierung</b><br/>" + str(self.datazione_estesa), styNormal)

        data = [sigla,
                nr_struttura,
                categoria_struttura,
                tipologia_struttura,
                definizione_struttura,
                periodo_iniziale,
                fase_iniziale,
                periodo_finale,
                fase_finale,
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

        sigla = Paragraph("<b>Code</b><br/>" + str(self.sigla_struttura), styNormal)

        nr_struttura = Paragraph("<b>Structure Nr.</b><br/>" + str(self.numero_struttura), styNormal)

        categoria_struttura = Paragraph("<b>Categories</b><br/>" + str(self.categoria_struttura), styNormal)

        tipologia_struttura = Paragraph("<b>Typology</b><br/>" + str(self.tipologia_struttura), styNormal)

        definizione_struttura = Paragraph("<b>Definition</b><br/>" + str(self.definizione_struttura), styNormal)

        periodo_iniziale = Paragraph("<b>Starting Period</b><br/>" + str(self.periodo_iniziale), styNormal)

        fase_iniziale = Paragraph("<b>Staring Phase</b><br/>" + str(self.fase_iniziale), styNormal)

        periodo_finale = Paragraph("<b>Final Period</b><br/>" + str(self.periodo_finale), styNormal)

        fase_finale = Paragraph("<b>Final Phase</b><br/>" + str(self.fase_finale), styNormal)

        datazione_estesa = Paragraph("<b>Litteral Datetion</b><br/>" + str(self.datazione_estesa), styNormal)

        data = [sigla,
                nr_struttura,
                categoria_struttura,
                tipologia_struttura,
                definizione_struttura,
                periodo_iniziale,
                fase_iniziale,
                periodo_finale,
                fase_finale,
                datazione_estesa
                ]

        return data 
    def makeStyles(self):
        styles = TableStyle([('GRID', (0, 0), (-1, -1), 0.0, colors.black), ('VALIGN', (0, 0), (-1, -1), 'TOP')
                             ])  # finale

        return styles


class single_Struttura_pdf_sheet(object):
    # rapporti stratigrafici

    materiali_print = ''
    elementi_strutturali_print = ''
    rapporti_struttura_print = ''
    misure_struttura_print = ''

    def __init__(self, data):
        self.sito = data[0]
        self.sigla_struttura = data[1]
        self.numero_struttura = data[2]
        self.categoria_struttura = data[3]
        self.tipologia_struttura = data[4]
        self.definizione_struttura = data[5]
        self.descrizione = data[6]
        self.interpretazione = data[7]
        self.periodo_iniziale = data[8]
        self.fase_iniziale = data[9]
        self.periodo_finale = data[10]
        self.fase_finale = data[11]
        self.datazione_estesa = data[12]
        self.materiali_impiegati = data[13]
        self.elementi_strutturali = data[14]
        self.rapporti_struttura = data[15]
        self.misure_struttura = data[16]
        self.quota_min = data[17]
        self.quota_max = data[18]

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
        intestazione = Paragraph("<b>SCHEDA STRUTTURA<br/></b>", styNormal)
        # intestazione2 = Paragraph("<b>pyArchInit</b><br/>www.pyarchinit.blogspot.com", styNormal)
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
        sigla_struttura = Paragraph(
            "<b>Sigla/N.</b><br/> %s%s" % (str(self.sigla_struttura), str(self.numero_struttura)), styNormal)

        # 2 row
        categoria = Paragraph("<b>Categoria</b><br/>" + self.categoria_struttura, styNormal)
        tipologia = Paragraph("<b>Tipologia</b><br/>" + self.tipologia_struttura, styNormal)
        definizione = Paragraph("<b>Definizione</b><br/>" + self.definizione_struttura, styNormal)

        # 3 row
        descrizione = ''
        try:
            descrizione = Paragraph("<b>Descrizione</b><br/>" + str(self.descrizione), styDescrizione)
        except:
            pass

        interpretazione = ''
        try:
            interpretazione = Paragraph("<b>Interpretazione</b><br/>" + str(self.interpretazione), styDescrizione)
        except:
            pass

            # 4 row
        periodizzazione = Paragraph("<b>PERIODIZZAZIONE</b><br/>", styNormal)

        # 5 row
        iniziale = Paragraph("<b>INIZIALE</b>", styNormal)
        if self.periodo_iniziale == "None":
            periodo_iniziale = Paragraph("<b>Periodo</b><br/>", styNormal)
        else:
            periodo_iniziale = Paragraph("<b>Periodo</b><br/>" + self.periodo_iniziale, styNormal)
        if self.fase_iniziale == "None":
            fase_iniziale = Paragraph("<b>Fase</b><br/>", styNormal)
        else:
            fase_iniziale = Paragraph("<b>Fase</b><br/>" + self.fase_iniziale, styNormal)

        finale = Paragraph("<b>FINALE</b>", styNormal)

        if self.periodo_finale == "None":
            periodo_finale = Paragraph("<b>Periodo</b><br/>", styNormal)
        else:
            periodo_finale = Paragraph("<b>Periodo</b><br/>" + self.periodo_finale, styNormal)
        if self.fase_finale == "None":
            fase_finale = Paragraph("<b>Fase</b><br/>", styNormal)
        else:
            fase_finale = Paragraph("<b>Fase</b><br/>" + self.fase_finale, styNormal)

            # 6 row
        datazione_estesa = Paragraph("<b>DATAZIONE ESTESA</b><br/>" + self.datazione_estesa, styNormal)

        # 7 row
        materiali_impiegati = ''
        if eval(self.materiali_impiegati):
            for i in eval(self.materiali_impiegati):
                if materiali_impiegati == '':
                    try:
                        materiali_impiegati += ("%s") % (str(i[0]))
                    except:
                        pass
                else:
                    try:
                        materiali_impiegati += (", %s") % (str(i[0]))
                    except:
                        pass

        materiali_impiegati = Paragraph("<b>Materiali impiegati</b><br/>" + materiali_impiegati, styNormal)

        # 8 row
        elementi_strutturali = ''
        if eval(self.elementi_strutturali):
            for i in eval(self.elementi_strutturali):
                if elementi_strutturali == '':
                    try:
                        elementi_strutturali += ("Tipologia elemento: %s, quantità: %s") % (str(i[0]), str(i[1]))
                    except:
                        pass
                else:
                    try:
                        elementi_strutturali += ("<br/>Tipologia elemento: %s, quantità: %s") % (str(i[0]), str(i[1]))
                    except:
                        pass

        elementi_strutturali = Paragraph("<b>Elementi strutturali</b><br/>" + elementi_strutturali, styNormal)

        # 9 row
        rapporti_struttura = ''
        if eval(self.rapporti_struttura):
            for i in eval(self.rapporti_struttura):
                if rapporti_struttura == '':
                    try:
                        rapporti_struttura += ("Tipo rapporto: %s, sito: %s, sigla: %s, n.: %s") % (
                        str(i[0]), str(i[1]), str(i[2]), str(i[3]))
                    except:
                        pass
                else:
                    try:
                        rapporti_struttura += ("<br/>Tipo rapporto: %s, sito: %s, sigla: %s, n.: %s") % (
                        str(i[0]), str(i[1]), str(i[2]), str(i[3]))
                    except:
                        pass

        rapporti_struttura = Paragraph("<b>Rapporti struttura</b><br/>" + rapporti_struttura, styNormal)

        # 10 row
        misure_struttura = ''
        if eval(self.misure_struttura):
            for i in eval(self.misure_struttura):
                if misure_struttura == '':
                    try:
                        misure_struttura += ("Tipo di misura: %s = %s %s") % (str(i[0]), str(i[2]), str(i[1]))
                    except:
                        pass
                else:
                    try:
                        misure_struttura += ("<br/>Tipo di misura: %s = %s %s") % (str(i[0]), str(i[2]), str(i[1]))
                    except:
                        pass

        misure_struttura = Paragraph("<b>Misurazioni</b><br/>" + misure_struttura, styNormal)

        # 19 row
        quote_struttura = Paragraph("<b>QUOTE</b><br/>", styNormal)

        # 20 row
        quota_min = Paragraph("<b>Quota min</b><br/>" + str(self.quota_min), styNormal)
        quota_max = Paragraph("<b>Quota max</b><br/>" + str(self.quota_max), styNormal)

        # schema
        cell_schema = [  # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],  # 0 row ok
            [sito, '01', '02', '03', '04', '05', '06', '07', sigla_struttura, '09'],  # 1 row ok
            [categoria, '01', '02', '03', tipologia, '05', '06', '07', definizione, '09'],  # 2 row ok
            [descrizione, '01', '02', '03', '04', interpretazione, '06', '07', '08', '09'],  # 3 row ok
            [periodizzazione, '02', '03', '04', '05', '06', '06', '07', '08', '09'],  # 4 row
            [iniziale, '01', periodo_iniziale, '03', fase_iniziale, finale, '06', periodo_finale, '08', fase_finale],
            # 5 row
            [datazione_estesa, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 6 row
            [rapporti_struttura, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 7 row
            [materiali_impiegati, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 8 row
            [elementi_strutturali, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 9 row
            [misure_struttura, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 10 row
            [quote_struttura, '01', '02', '03', '04', '07', '06', '07', '08', '09'],  # 19 row ok
            [quota_min, '01', '02', '03', quota_max, '06', '07', '08', '09']  # 20 row ok
        ]

        # table style
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row
            ('SPAN', (0, 0), (6, 0)),  # intestazione
            ('SPAN', (7, 0), (9, 0)),  # intestazione

            # 1 row
            ('SPAN', (0, 1), (7, 1)),  # dati identificativi
            ('SPAN', (8, 1), (9, 1)),  # dati identificativi

            # 2 row
            ('SPAN', (0, 2), (3, 2)),  # Definizione - interpretazone
            ('SPAN', (4, 2), (7, 2)),  # definizione - intepretazione
            ('SPAN', (8, 2), (9, 2)),  # definizione - intepretazione

            # 3 row
            ('SPAN', (0, 3), (4, 3)),  # conservazione - consistenza - colore
            ('SPAN', (5, 3), (9, 3)),  # conservazione - consistenza - colore

            # 4 row
            ('SPAN', (0, 4), (9, 4)),  # inclusi - campioni - formazione

            # 5 row
            ('SPAN', (0, 5), (1, 5)),  # iniziale
            ('SPAN', (2, 5), (3, 5)),  # periodo inizlae
            ('SPAN', (5, 5), (6, 5)),  # fase iniziale
            ('SPAN', (7, 5), (8, 5)),  # finale
            ('VALIGN', (0, 5), (0, 5), 'TOP'),
            ('VALIGN', (5, 5), (5, 5), 'TOP'),

            # 6 row
            ('SPAN', (0, 6), (9, 6)),  # Attivita - Struttura - Quota min - Quota max

            # 7 row
            ('SPAN', (0, 7), (9, 7)),  # Attivita - Struttura - Quota min - Quota max

            # 8 row
            ('SPAN', (0, 8), (9, 8)),  # Attivita - Struttura - Quota min - Quota max

            # 9 row
            ('SPAN', (0, 9), (9, 9)),  # Attivita - Struttura - Quota min - Quota max

            # 10 row
            ('SPAN', (0, 10), (9, 10)),  # Attivita - Struttura - Quota min - Quota max

            # 10 row
            ('SPAN', (0, 11), (9, 11)),  # Attivita - Struttura - Quota min - Quota max

            # 10 row
            ('SPAN', (0, 12), (3, 12)),  # conservazione - consistenza - colore
            ('SPAN', (4, 12), (9, 12)),  # conservazione - consistenza - colore

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
        intestazione = Paragraph("<b>FORMULA STRUKTUR<br/>" + str(self.datestrfdate()) + "</b>", styNormal)
        # intestazione2 = Paragraph("<b>pyArchInit</b><br/>www.pyarchinit.blogspot.com", styNormal)
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
        sigla_struttura = Paragraph(
            "<b>Code/Nr.</b><br/> %s%s" % (str(self.sigla_struttura), str(self.numero_struttura)), styNormal)

        # 2 row
        categoria = Paragraph("<b>Categorie</b><br/>" + self.categoria_struttura, styNormal)
        tipologia = Paragraph("<b>Typologie</b><br/>" + self.tipologia_struttura, styNormal)
        definizione = Paragraph("<b>Definition</b><br/>" + self.definizione_struttura, styNormal)

        # 3 row
        descrizione = ''
        try:
            descrizione = Paragraph("<b>Beschreibung</b><br/>" + str(self.descrizione), styDescrizione)
        except:
            pass

        interpretazione = ''
        try:
            interpretazione = Paragraph("<b>Deutung</b><br/>" + str(self.interpretazione), styDescrizione)
        except:
            pass

            # 4 row
        periodizzazione = Paragraph("<b>PERIODISIERUNG</b><br/>", styNormal)

        # 5 row
        iniziale = Paragraph("<b>BEGINNEND</b>", styNormal)
        if self.periodo_iniziale == "None":
            periodo_iniziale = Paragraph("<b>Zeitraum</b><br/>", styNormal)
        else:
            periodo_iniziale = Paragraph("<b>Zeitraum</b><br/>" + self.periodo_iniziale, styNormal)
        if self.fase_iniziale == "None":
            fase_iniziale = Paragraph("<b>Phase</b><br/>", styNormal)
        else:
            fase_iniziale = Paragraph("<b>Phase</b><br/>" + self.fase_iniziale, styNormal)

        finale = Paragraph("<b>ENDE</b>", styNormal)

        if self.periodo_finale == "None":
            periodo_finale = Paragraph("<b>Zeitraum</b><br/>", styNormal)
        else:
            periodo_finale = Paragraph("<b>Zeitraum</b><br/>" + self.periodo_finale, styNormal)
        if self.fase_finale == "None":
            fase_finale = Paragraph("<b>Phase</b><br/>", styNormal)
        else:
            fase_finale = Paragraph("<b>Phase</b><br/>" + self.fase_finale, styNormal)

            # 6 row
        datazione_estesa = Paragraph("<b>ERWEITERTE DATIERUNG</b><br/>" + self.datazione_estesa, styNormal)

        # 7 row
        materiali_impiegati = ''
        if eval(self.materiali_impiegati):
            for i in eval(self.materiali_impiegati):
                if materiali_impiegati == '':
                    try:
                        materiali_impiegati += ("%s") % (str(i[0]))
                    except:
                        pass
                else:
                    try:
                        materiali_impiegati += (", %s") % (str(i[0]))
                    except:
                        pass

        materiali_impiegati = Paragraph("<b>Verwendete Materialien</b><br/>" + materiali_impiegati, styNormal)

        # 8 row
        elementi_strutturali = ''
        if eval(self.elementi_strutturali):
            for i in eval(self.elementi_strutturali):
                if elementi_strutturali == '':
                    try:
                        elementi_strutturali += ("<br/>Funktionsart: %s, Menge: %s") % (str(i[0]), str(i[1]))
                    except:
                        pass
                else:
                    try:
                        elementi_strutturali += ("<br/>Funktionsart: %s, Menge: %s") % (str(i[0]), str(i[1]))
                    except:
                        pass

        elementi_strutturali = Paragraph("<b>Strukturelle Eigenschaften</b><br/>" + elementi_strutturali, styNormal)

        # 9 row
        rapporti_struttura = ''
        if eval(self.rapporti_struttura):
            for i in eval(self.rapporti_struttura):
                if rapporti_struttura == '':
                    try:
                        rapporti_struttura += ("<br/>Relatie type: %s, Ausgrabungsstätte: %s, code: %s, nr.: %s") % (
                        str(i[0]), str(i[1]), str(i[2]), str(i[3]))
                    except:
                        pass
                else:
                    try:
                        rapporti_struttura += ("<br/>Relatie type: %s, Ausgrabungsstätte: %s, code: %s, nr.: %s") % (
                        str(i[0]), str(i[1]), str(i[2]), str(i[3]))
                    except:
                        pass

        rapporti_struttura = Paragraph("<b>Relatie struktur</b><br/>" + rapporti_struttura, styNormal)

        # 10 row
        misure_struttura = ''
        if eval(self.misure_struttura):
            for i in eval(self.misure_struttura):
                if misure_struttura == '':
                    try:
                        misure_struttura += ("<br/>Messart: %s = %s %s") % (str(i[0]), str(i[2]), str(i[1]))
                    except:
                        pass
                else:
                    try:
                        misure_struttura += ("<br/>Messart: %s = %s %s") % (str(i[0]), str(i[2]), str(i[1]))
                    except:
                        pass

        misure_struttura = Paragraph("<b>Messungen</b><br/>" + misure_struttura, styNormal)

        # 19 row
        quote_struttura = Paragraph("<b>HÖHE</b><br/>", styNormal)

        # 20 row
        quota_min = Paragraph("<b>Höhe min</b><br/>" + str(self.quota_min), styNormal)
        quota_max = Paragraph("<b>Höhe max</b><br/>" + str(self.quota_max), styNormal)

        # schema
        cell_schema = [  # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],  # 0 row ok
            [sito, '01', '02', '03', '04', '05', '06', '07', sigla_struttura, '09'],  # 1 row ok
            [categoria, '01', '02', '03', tipologia, '05', '06', '07', definizione, '09'],  # 2 row ok
            [descrizione, '01', '02', '03', '04', interpretazione, '06', '07', '08', '09'],  # 3 row ok
            [periodizzazione, '02', '03', '04', '05', '06', '06', '07', '08', '09'],  # 4 row
            [iniziale, '01', periodo_iniziale, '03', fase_iniziale, finale, '06', periodo_finale, '08', fase_finale],
            # 5 row
            [datazione_estesa, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 6 row
            [rapporti_struttura, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 7 row
            [materiali_impiegati, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 8 row
            [elementi_strutturali, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 9 row
            [misure_struttura, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 10 row
            [quote_struttura, '01', '02', '03', '04', '07', '06', '07', '08', '09'],  # 19 row ok
            [quota_min, '01', '02', '03', quota_max, '06', '07', '08', '09']  # 20 row ok
        ]

        # table style
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row
            ('SPAN', (0, 0), (6, 0)),  # intestazione
            ('SPAN', (7, 0), (9, 0)),  # intestazione

            # 1 row
            ('SPAN', (0, 1), (7, 1)),  # dati identificativi
            ('SPAN', (8, 1), (9, 1)),  # dati identificativi

            # 2 row
            ('SPAN', (0, 2), (3, 2)),  # Definizione - interpretazone
            ('SPAN', (4, 2), (7, 2)),  # definizione - intepretazione
            ('SPAN', (8, 2), (9, 2)),  # definizione - intepretazione

            # 3 row
            ('SPAN', (0, 3), (4, 3)),  # conservazione - consistenza - colore
            ('SPAN', (5, 3), (9, 3)),  # conservazione - consistenza - colore

            # 4 row
            ('SPAN', (0, 4), (9, 4)),  # inclusi - campioni - formazione

            # 5 row
            ('SPAN', (0, 5), (1, 5)),  # iniziale
            ('SPAN', (2, 5), (3, 5)),  # periodo inizlae
            ('SPAN', (5, 5), (6, 5)),  # fase iniziale
            ('SPAN', (7, 5), (8, 5)),  # finale
            ('VALIGN', (0, 5), (0, 5), 'TOP'),
            ('VALIGN', (5, 5), (5, 5), 'TOP'),

            # 6 row
            ('SPAN', (0, 6), (9, 6)),  # Attivita - Struttura - Quota min - Quota max

            # 7 row
            ('SPAN', (0, 7), (9, 7)),  # Attivita - Struttura - Quota min - Quota max

            # 8 row
            ('SPAN', (0, 8), (9, 8)),  # Attivita - Struttura - Quota min - Quota max

            # 9 row
            ('SPAN', (0, 9), (9, 9)),  # Attivita - Struttura - Quota min - Quota max

            # 10 row
            ('SPAN', (0, 10), (9, 10)),  # Attivita - Struttura - Quota min - Quota max

            # 10 row
            ('SPAN', (0, 11), (9, 11)),  # Attivita - Struttura - Quota min - Quota max

            # 10 row
            ('SPAN', (0, 12), (3, 12)),  # conservazione - consistenza - colore
            ('SPAN', (4, 12), (9, 12)),  # conservazione - consistenza - colore

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
        intestazione = Paragraph("<b>STRUCTURE FORM<br/>" + str(self.datestrfdate()) + "</b>", styNormal)
        # intestazione2 = Paragraph("<b>pyArchInit</b><br/>www.pyarchinit.blogspot.com", styNormal)
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
        sigla_struttura = Paragraph(
            "<b>Code/Nr.</b><br/> %s%s" % (str(self.sigla_struttura), str(self.numero_struttura)), styNormal)

        # 2 row
        categoria = Paragraph("<b>Categories</b><br/>" + self.categoria_struttura, styNormal)
        tipologia = Paragraph("<b>Typology</b><br/>" + self.tipologia_struttura, styNormal)
        definizione = Paragraph("<b>Definition</b><br/>" + self.definizione_struttura, styNormal)

        # 3 row
        descrizione = ''
        try:
            descrizione = Paragraph("<b>Description</b><br/>" + str(self.descrizione), styDescrizione)
        except:
            pass

        interpretazione = ''
        try:
            interpretazione = Paragraph("<b>Interpretation</b><br/>" + str(self.interpretazione), styDescrizione)
        except:
            pass

            # 4 row
        periodizzazione = Paragraph("<b>PERIODIZATION</b><br/>", styNormal)

        # 5 row
        iniziale = Paragraph("<b>STARTING</b>", styNormal)
        if self.periodo_iniziale == "None":
            periodo_iniziale = Paragraph("<b>Period</b><br/>", styNormal)
        else:
            periodo_iniziale = Paragraph("<b>Period</b><br/>" + self.periodo_iniziale, styNormal)
        if self.fase_iniziale == "None":
            fase_iniziale = Paragraph("<b>Phase</b><br/>", styNormal)
        else:
            fase_iniziale = Paragraph("<b>Phase</b><br/>" + self.fase_iniziale, styNormal)

        finale = Paragraph("<b>FINAL</b>", styNormal)

        if self.periodo_finale == "None":
            periodo_finale = Paragraph("<b>Period</b><br/>", styNormal)
        else:
            periodo_finale = Paragraph("<b>Period</b><br/>" + self.periodo_finale, styNormal)
        if self.fase_finale == "None":
            fase_finale = Paragraph("<b>Phase</b><br/>", styNormal)
        else:
            fase_finale = Paragraph("<b>Phase</b><br/>" + self.fase_finale, styNormal)

            # 6 row
        datazione_estesa = Paragraph("<b>LETTERAL DATETION</b><br/>" + self.datazione_estesa, styNormal)

        # 7 row
        materiali_impiegati = ''
        if eval(self.materiali_impiegati):
            for i in eval(self.materiali_impiegati):
                if materiali_impiegati == '':
                    try:
                        materiali_impiegati += ("%s") % (str(i[0]))
                    except:
                        pass
                else:
                    try:
                        materiali_impiegati += (", %s") % (str(i[0]))
                    except:
                        pass

        materiali_impiegati = Paragraph("<b>Used material</b><br/>" + materiali_impiegati, styNormal)

        # 8 row
        elementi_strutturali = ''
        if eval(self.elementi_strutturali):
            for i in eval(self.elementi_strutturali):
                if elementi_strutturali == '':
                    try:
                        elementi_strutturali += ("<br/>Element typology: %s, Quantity: %s") % (str(i[0]), str(i[1]))
                    except:
                        pass
                else:
                    try:
                        elementi_strutturali += ("<br/>Element typology: %s, Quantity: %s") % (str(i[0]), str(i[1]))
                    except:
                        pass

        elementi_strutturali = Paragraph("<b>Structural elements</b><br/>" + elementi_strutturali, styNormal)

        # 9 row
        rapporti_struttura = ''
        if eval(self.rapporti_struttura):
            for i in eval(self.rapporti_struttura):
                if rapporti_struttura == '':
                    try:
                        rapporti_struttura += ("<br/>Relation type: %s, site: %s, code: %s, nr.: %s") % (
                        str(i[0]), str(i[1]), str(i[2]), str(i[3]))
                    except:
                        pass
                else:
                    try:
                        rapporti_struttura += ("<br/>Relation type: %s, site: %s, code: %s, nr.: %s") % (
                        str(i[0]), str(i[1]), str(i[2]), str(i[3]))
                    except:
                        pass

        rapporti_struttura = Paragraph("<b>Structure Relationship</b><br/>" + rapporti_struttura, styNormal)

        # 10 row
        misure_struttura = ''
        if eval(self.misure_struttura):
            for i in eval(self.misure_struttura):
                if misure_struttura == '':
                    try:
                        misure_struttura += ("<br/>Measure type: %s = %s %s") % (str(i[0]), str(i[2]), str(i[1]))
                    except:
                        pass
                else:
                    try:
                        misure_struttura += ("<br/>Measure type: %s = %s %s") % (str(i[0]), str(i[2]), str(i[1]))
                    except:
                        pass

        misure_struttura = Paragraph("<b>Measurement</b><br/>" + misure_struttura, styNormal)

        # 19 row
        quote_struttura = Paragraph("<b>ELEVATION</b><br/>", styNormal)

        # 20 row
        quota_min = Paragraph("<b>Elev. min</b><br/>" + str(self.quota_min), styNormal)
        quota_max = Paragraph("<b>Elev. max</b><br/>" + str(self.quota_max), styNormal)

        # schema
        cell_schema = [  # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [intestazione, '01', '02', '03', '04', '05', '06', logo, '08', '09'],  # 0 row ok
            [sito, '01', '02', '03', '04', '05', '06', '07', sigla_struttura, '09'],  # 1 row ok
            [categoria, '01', '02', '03', tipologia, '05', '06', '07', definizione, '09'],  # 2 row ok
            [descrizione, '01', '02', '03', '04', interpretazione, '06', '07', '08', '09'],  # 3 row ok
            [periodizzazione, '02', '03', '04', '05', '06', '06', '07', '08', '09'],  # 4 row
            [iniziale, '01', periodo_iniziale, '03', fase_iniziale, finale, '06', periodo_finale, '08', fase_finale],
            # 5 row
            [datazione_estesa, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 6 row
            [rapporti_struttura, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 7 row
            [materiali_impiegati, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 8 row
            [elementi_strutturali, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 9 row
            [misure_struttura, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 10 row
            [quote_struttura, '01', '02', '03', '04', '07', '06', '07', '08', '09'],  # 19 row ok
            [quota_min, '01', '02', '03', quota_max, '06', '07', '08', '09']  # 20 row ok
        ]

        # table style
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row
            ('SPAN', (0, 0), (6, 0)),  # intestazione
            ('SPAN', (7, 0), (9, 0)),  # intestazione

            # 1 row
            ('SPAN', (0, 1), (7, 1)),  # dati identificativi
            ('SPAN', (8, 1), (9, 1)),  # dati identificativi

            # 2 row
            ('SPAN', (0, 2), (3, 2)),  # Definizione - interpretazone
            ('SPAN', (4, 2), (7, 2)),  # definizione - intepretazione
            ('SPAN', (8, 2), (9, 2)),  # definizione - intepretazione

            # 3 row
            ('SPAN', (0, 3), (4, 3)),  # conservazione - consistenza - colore
            ('SPAN', (5, 3), (9, 3)),  # conservazione - consistenza - colore

            # 4 row
            ('SPAN', (0, 4), (9, 4)),  # inclusi - campioni - formazione

            # 5 row
            ('SPAN', (0, 5), (1, 5)),  # iniziale
            ('SPAN', (2, 5), (3, 5)),  # periodo inizlae
            ('SPAN', (5, 5), (6, 5)),  # fase iniziale
            ('SPAN', (7, 5), (8, 5)),  # finale
            ('VALIGN', (0, 5), (0, 5), 'TOP'),
            ('VALIGN', (5, 5), (5, 5), 'TOP'),

            # 6 row
            ('SPAN', (0, 6), (9, 6)),  # Attivita - Struttura - Quota min - Quota max

            # 7 row
            ('SPAN', (0, 7), (9, 7)),  # Attivita - Struttura - Quota min - Quota max

            # 8 row
            ('SPAN', (0, 8), (9, 8)),  # Attivita - Struttura - Quota min - Quota max

            # 9 row
            ('SPAN', (0, 9), (9, 9)),  # Attivita - Struttura - Quota min - Quota max

            # 10 row
            ('SPAN', (0, 10), (9, 10)),  # Attivita - Struttura - Quota min - Quota max

            # 10 row
            ('SPAN', (0, 11), (9, 11)),  # Attivita - Struttura - Quota min - Quota max

            # 10 row
            ('SPAN', (0, 12), (3, 12)),  # conservazione - consistenza - colore
            ('SPAN', (4, 12), (9, 12)),  # conservazione - consistenza - colore

            ('VALIGN', (0, 0), (-1, -1), 'TOP')

        ]

        t = Table(cell_schema, colWidths=50, rowHeights=None, style=table_style)

        return t    
class generate_struttura_pdf(object):
    HOME = os.environ['PYARCHINIT_HOME']

    PDF_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def build_Struttura_sheets(self, records):
        elements = []
        for i in range(len(records)):
            single_struttura_sheet = single_Struttura_pdf_sheet(records[i])
            elements.append(single_struttura_sheet.create_sheet())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Scheda Struttura.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_STRUTTURAsheet)
        f.close()

    def build_index_Struttura(self, records, sito):
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
        lst.append(Paragraph("<b>ELENCO STRUTTURE</b><br/><b>Scavo: %s</b>" % (sito), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = Struttura_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable())

        styles = exp_index.makeStyles()
        colWidths = [60, 60, 80, 80, 80, 50, 50, 50, 50, 100]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        # lst.append(Spacer(0,2))

        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Elenco Strutture.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(29 * cm, 21 * cm), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_STRUTTURAindex)

        f.close()
    def build_Struttura_sheets_de(self, records):
        elements = []
        for i in range(len(records)):
            single_struttura_sheet = single_Struttura_pdf_sheet(records[i])
            elements.append(single_struttura_sheet.create_sheet_de())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Fromular_strukture.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_STRUTTURAsheet)
        f.close()

    def build_index_Struttura_de(self, records, sito):
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
        lst.append(Paragraph("<b>LISTE STRUKTUR</b><br/><b>Ausgrabungsstätte: %s,  Datum: %s</b>" % (sito, data), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = Struttura_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable_de())

        styles = exp_index.makeStyles()
        colWidths = [60, 60, 80, 80, 80, 50, 50, 50, 50, 100]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        # lst.append(Spacer(0,2))

        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'liste_struktur.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(29 * cm, 21 * cm), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_STRUTTURAindex)

        f.close()
    def build_Struttura_sheets_en(self, records):
        elements = []
        for i in range(len(records)):
            single_struttura_sheet = single_Struttura_pdf_sheet(records[i])
            elements.append(single_struttura_sheet.create_sheet_en())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Structure_form.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_STRUTTURAsheet)
        f.close()

    def build_index_Struttura_en(self, records, sito):
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
        lst.append(Paragraph("<b>STRUCTURE LIST</b><br/><b>Site: %s,  Date: %s</b>" % (sito, data), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = Struttura_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable_en())

        styles = exp_index.makeStyles()
        colWidths = [60, 60, 80, 80, 80, 50, 50, 50, 50, 100]

        table_data_formatted = Table(table_data, colWidths, style=styles)
        table_data_formatted.hAlign = "LEFT"

        lst.append(table_data_formatted)
        # lst.append(Spacer(0,2))

        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'structure_list.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(29 * cm, 21 * cm), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_STRUTTURAindex)

        f.close()

