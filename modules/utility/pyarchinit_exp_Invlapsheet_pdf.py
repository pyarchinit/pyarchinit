
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


class NumberedCanvas_Invlapsheet(canvas.Canvas):
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


class single_Invlap_pdf_sheet:
    def __init__(self, data):
        self.id_invlap = data[0]
        self.sito = data[1]
        self.scheda_numero = data[2]
        self.collocazione = data[3]
        self.oggetto = data[4]
        self.tipologia = data[5]
        self.materiale = data[6]
        self.d_letto_posa = data[7]
        self.d_letto_attesa = data[8]
        self.toro = data[9]
        self.spessore = data[10]
        self.larghezza = data[11]
        self.lunghezza = data[12]
        self.h = data[13]
        self.descrizione = data[14]
        self.lavorazione_e_stato_di_conservazione = data[15]
        self.confronti = data[16]
        self.cronologia = data[17]
        self.bibliografia = data[18]
        self.compilatore = data[19]

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
        intestazione = Paragraph("<b>SCHEDA REPERTI LAPIDEI<br/>" + str(self.datestrfdate()) + "</b>", styNormal)
        # intestazione2 = Paragraph("<b>pyArchInit</b>", styNormal)

        home = os.environ['PYARCHINIT_HOME']

        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = lo_path_str# '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        alma = Image(logo_path)

        ##      if test_image.drawWidth < 800:

        alma.drawHeight = 1.5 * inch * alma.drawHeight / alma.drawWidth
        alma.drawWidth = 1.5 * inch

        # 1 row
        sito = Paragraph("<b>Contesto/Provenienza</b><br/>" + str(self.sito), styNormal)
        scheda_numero = Paragraph("<b>Scheda Numero</b><br/>" + str(self.scheda_numero), styNormal)

        # 2 row
        collocazione = Paragraph("<b>Collocazione</b><br/>" + str(self.collocazione), styNormal)

        # 3 row
        materiale = Paragraph("<b>Materiale</b><br/>" + self.materiale, styNormal)

        # 4 row
        oggetto = Paragraph("<b>Oggetto</b><br/>" + str(self.oggetto), styNormal)

        # 5 row
        tipologia = Paragraph("<b>Tipologia</b><br/>" + self.tipologia, styNormal)

        # 6 row
        d_letto_posa = Paragraph("<b>D (letto posa)</b><br/>" + self.d_letto_posa, styNormal)

        # 7 row
        d_letto_attesa = Paragraph("<b>D (letto attesa)</b><br/>" + self.d_letto_attesa, styNormal)

        # 8 row
        toro = Paragraph("<b>Toro</b><br/>" + self.toro, styNormal)

        # 9 row
        spessore = Paragraph("<b>Spessore</b><br/>" + self.spessore, styNormal)

        # 10 row
        lunghezza = Paragraph("<b>Lunghezza</b><br/>" + self.lunghezza, styNormal)

        # 11 row
        larghezza = Paragraph("<b>Larghezza</b><br/>" + self.larghezza, styNormal)

        # 12 row
        h = Paragraph("<b>h</b><br/>" + self.h, styNormal)

        # 13row
        lavorazione_e_stato_di_conservazione = Paragraph(
            "<b>Lavorazione e stato di conservazione</b><br/>" + self.lavorazione_e_stato_di_conservazione, styNormal)

        # 14 row
        confronti = Paragraph("<b>Confronti</b><br/>" + self.confronti, styNormal)

        # 15 row
        cronologia = Paragraph("<b>Cronologia</b><br/>" + self.cronologia, styNormal)

        # 16 row
        compilatore = Paragraph("<b>Autore scheda</b><br/>" + self.compilatore, styNormal)

        # 17 row
        descrizione = ''
        try:
            descrizione = Paragraph("<b>Descrizione</b><br/>" + self.descrizione, styDescrizione)
        except:
            pass

            # 18 row
        bibliografia = ''
        if len(eval(self.bibliografia)) > 0:
            for i in eval(self.bibliografia):  # gigi
                if bibliografia == '':
                    try:
                        bibliografia += ("<b>Autore: %s, Anno: %s, Titolo: %s, Pag.: %s, Fig.: %s") % (
                        str(i[0]), str(i[1]), str(i[2]), str(i[3]), str(i[4]))
                    except:
                        pass
                else:
                    try:
                        bibliografia += ("<b>Autore: %s, Anno: %s, Titolo: %s, Pag.: %s, Fig.: %s") % (
                        str(i[0]), str(i[1]), str(i[2]), str(i[3]), str(i[4]))
                    except:
                        pass

        bibliografia = Paragraph("<b>Bibliografia</b><br/>" + bibliografia, styNormal)

        # schema
        cell_schema = [  # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [alma, '01', '02', '03', '04', '05', '06', intestazione, '08', '09'],  # 0 row ok
            [sito, '01', '02', '03', '04', '05', '06', '07', scheda_numero, '09'],  # 1 row ok
            [collocazione, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 2 row ok
            [materiale, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 3 row ok
            [oggetto, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 4 row ok
            [tipologia, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 5 row ok
            [d_letto_posa, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 6 row ok
            [d_letto_attesa, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 7 row ok
            [toro, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 8 row ok
            [spessore, '02', '03', '04', '05', '06', '07', '08', '09'],  # 9 row ok
            [larghezza, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 10 row ok
            [lunghezza, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 11 row ok
            [h, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 12 row ok
            [descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 13 row ok
            [lavorazione_e_stato_di_conservazione, '01', '02', '03', '04', '05', '06', '07', '08', '09'],
            # 14 row ok
            [confronti, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 15 row ok
            [cronologia, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 16 row ok
            [bibliografia, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 17 row ok
            [compilatore, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 18 row ok
        ]

        # table style
        table_style = [

            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row
            ('SPAN', (0, 0), (6, 0)),  # intestazione
            ('SPAN', (7, 0), (9, 0)),  # logo

            # 1 row
            ('SPAN', (0, 1), (7, 1)),  # sito
            ('SPAN', (8, 1), (9, 1)),  # scheda numero

            # 2 row
            ('SPAN', (0, 2), (9, 2)),  # collocazione
            #                   ('VALIGN',(0,2),(9,2),'TOP'),

            # 3 row
            ('SPAN', (0, 3), (9, 3)),  # materiale

            # 4 row
            ('SPAN', (0, 4), (9, 4)),  # oggetto

            # 5row
            ('SPAN', (0, 5), (9, 5)),  # tipologia

            # 6 row
            ('SPAN', (0, 6), (9, 6)),  # d_letto_posa

            # 7 row
            ('SPAN', (0, 7), (9, 7)),  # d_letto_attesa

            # 8 row
            ('SPAN', (0, 8), (9, 8)),  # toro

            # 9 row
            ('SPAN', (0, 9), (9, 9)),  # spessore

            # 10 row
            ('SPAN', (0, 10), (9, 10)),  # larghezza

            # 11 row
            ('SPAN', (0, 11), (9, 11)),  # lunghezza

            # 12row
            ('SPAN', (0, 12), (9, 12)),  # h

            # 13 row
            ('SPAN', (0, 13), (9, 13)),  # descrizione

            # 14 row
            ('SPAN', (0, 14), (9, 14)),  # lavorazione

            # 15 row
            ('SPAN', (0, 15), (9, 15)),  # confronti

            # 16 row
            ('SPAN', (0, 16), (9, 16)),  # cronologia

            # 17 row
            ('SPAN', (0, 17), (9, 17)),  # bibliografia

            # 18 row
            ('SPAN', (0, 18), (9, 18)),  # autore scheda
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
        intestazione = Paragraph("<b>STEINARTEFAKTFORMULAR<br/>" + str(self.datestrfdate()) + "</b>", styNormal)
        # intestazione2 = Paragraph("<b>pyArchInit</b>", styNormal)

        home = os.environ['PYARCHINIT_HOME']

        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = lo_path_str# '{}{}{}'.format(home_DB_path, os.sep, 'logo_de.jpg')
        alma = Image(logo_path)

        ##      if test_image.drawWidth < 800:

        alma.drawHeight = 1.5 * inch * alma.drawHeight / alma.drawWidth
        alma.drawWidth = 1.5 * inch

        # 1 row
        sito = Paragraph("<b>Kontext-Herkunft</b><br/>" + str(self.sito), styNormal)
        scheda_numero = Paragraph("<b>N° Feld</b><br/>" + str(self.scheda_numero), styNormal)

        # 2 row
        collocazione = Paragraph("<b>Lage</b><br/>" + str(self.collocazione), styNormal)

        # 3 row
        materiale = Paragraph("<b>Material</b><br/>" + self.materiale, styNormal)

        # 4 row
        oggetto = Paragraph("<b>Thema</b><br/>" + str(self.oggetto), styNormal)

        # 5 row
        tipologia = Paragraph("<b>Typologie</b><br/>" + self.tipologia, styNormal)

        # 6 row
        d_letto_posa = Paragraph("<b>D (bett)</b><br/>" + self.d_letto_posa, styNormal)

        # 7 row
        d_letto_attesa = Paragraph("<b>D (Wartebett)</b><br/>" + self.d_letto_attesa, styNormal)

        # 8 row
        toro = Paragraph("<b>Wulst</b><br/>" + self.toro, styNormal)

        # 9 row
        spessore = Paragraph("<b>Dicke</b><br/>" + self.spessore, styNormal)

        # 10 row
        lunghezza = Paragraph("<b>Breite</b><br/>" + self.lunghezza, styNormal)

        # 11 row
        larghezza = Paragraph("<b>Länge</b><br/>" + self.larghezza, styNormal)

        # 12 row
        h = Paragraph("<b>h</b><br/>" + self.h, styNormal)

        # 13row
        lavorazione_e_stato_di_conservazione = Paragraph(
            "<b>Verarbeitung und Erhaltungszustand</b><br/>" + self.lavorazione_e_stato_di_conservazione, styNormal)

        # 14 row
        confronti = Paragraph("<b>Vergleiche</b><br/>" + self.confronti, styNormal)

        # 15 row
        cronologia = Paragraph("<b>Chronologie</b><br/>" + self.cronologia, styNormal)

        # 16 row
        compilatore = Paragraph("<b>Verfasser</b><br/>" + self.compilatore, styNormal)

        # 17 row
        descrizione = ''
        try:
            descrizione = Paragraph("<b>Beschreibung</b><br/>" + self.descrizione, styDescrizione)
        except:
            pass

            # 18 row
        bibliografia = ''
        if len(eval(self.bibliografia)) > 0:
            for i in eval(self.bibliografia):  # gigi
                if bibliografia == '':
                    try:
                        bibliografia += ("<b>Verfasser: %s, Jahr: %s, Titel: %s, Seite: %s, Bild: %s") % (
                        str(i[0]), str(i[1]), str(i[2]), str(i[3]), str(i[4]))
                    except:
                        pass
                else:
                    try:
                        bibliografia += ("<b>Verfasser: %s, Jahr: %s, Titel: %s, Seite: %s, Bild: %s") % (
                        str(i[0]), str(i[1]), str(i[2]), str(i[3]), str(i[4]))
                    except:
                        pass

        bibliografia = Paragraph("<b>Bibliographie</b><br/>" + bibliografia, styNormal)

        # schema
        cell_schema = [  # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [alma, '01', '02', '03', '04', '05', '06', intestazione, '08', '09'],  # 0 row ok
            [sito, '01', '02', '03', '04', '05', '06', '07', scheda_numero, '09'],  # 1 row ok
            [collocazione, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 2 row ok
            [materiale, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 3 row ok
            [oggetto, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 4 row ok
            [tipologia, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 5 row ok
            [d_letto_posa, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 6 row ok
            [d_letto_attesa, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 7 row ok
            [toro, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 8 row ok
            [spessore, '02', '03', '04', '05', '06', '07', '08', '09'],  # 9 row ok
            [larghezza, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 10 row ok
            [lunghezza, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 11 row ok
            [h, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 12 row ok
            [descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 13 row ok
            [lavorazione_e_stato_di_conservazione, '01', '02', '03', '04', '05', '06', '07', '08', '09'],
            # 14 row ok
            [confronti, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 15 row ok
            [cronologia, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 16 row ok
            [bibliografia, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 17 row ok
            [compilatore, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 18 row ok
        ]

        # table style
        table_style = [

            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row
            ('SPAN', (0, 0), (6, 0)),  # intestazione
            ('SPAN', (7, 0), (9, 0)),  # logo

            # 1 row
            ('SPAN', (0, 1), (7, 1)),  # sito
            ('SPAN', (8, 1), (9, 1)),  # scheda numero

            # 2 row
            ('SPAN', (0, 2), (9, 2)),  # collocazione
            #                   ('VALIGN',(0,2),(9,2),'TOP'),

            # 3 row
            ('SPAN', (0, 3), (9, 3)),  # materiale

            # 4 row
            ('SPAN', (0, 4), (9, 4)),  # oggetto

            # 5row
            ('SPAN', (0, 5), (9, 5)),  # tipologia

            # 6 row
            ('SPAN', (0, 6), (9, 6)),  # d_letto_posa

            # 7 row
            ('SPAN', (0, 7), (9, 7)),  # d_letto_attesa

            # 8 row
            ('SPAN', (0, 8), (9, 8)),  # toro

            # 9 row
            ('SPAN', (0, 9), (9, 9)),  # spessore

            # 10 row
            ('SPAN', (0, 10), (9, 10)),  # larghezza

            # 11 row
            ('SPAN', (0, 11), (9, 11)),  # lunghezza

            # 12row
            ('SPAN', (0, 12), (9, 12)),  # h

            # 13 row
            ('SPAN', (0, 13), (9, 13)),  # descrizione

            # 14 row
            ('SPAN', (0, 14), (9, 14)),  # lavorazione

            # 15 row
            ('SPAN', (0, 15), (9, 15)),  # confronti

            # 16 row
            ('SPAN', (0, 16), (9, 16)),  # cronologia

            # 17 row
            ('SPAN', (0, 17), (9, 17)),  # bibliografia

            # 18 row
            ('SPAN', (0, 18), (9, 18)),  # autore scheda
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
        intestazione = Paragraph("<b>STONE FORM<br/>" + str(self.datestrfdate()) + "</b>", styNormal)
        # intestazione2 = Paragraph("<b>pyArchInit</b>", styNormal)

        home = os.environ['PYARCHINIT_HOME']

        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = lo_path_str# '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        alma = Image(logo_path)

        ##      if test_image.drawWidth < 800:

        alma.drawHeight = 1.5 * inch * alma.drawHeight / alma.drawWidth
        alma.drawWidth = 1.5 * inch

        # 1 row
        sito = Paragraph("<b>Context</b><br/>" + str(self.sito), styNormal)
        scheda_numero = Paragraph("<b>N° Form</b><br/>" + str(self.scheda_numero), styNormal)

        # 2 row
        collocazione = Paragraph("<b>Place</b><br/>" + str(self.collocazione), styNormal)

        # 3 row
        materiale = Paragraph("<b>Material</b><br/>" + self.materiale, styNormal)

        # 4 row
        oggetto = Paragraph("<b>Object</b><br/>" + str(self.oggetto), styNormal)

        # 5 row
        tipologia = Paragraph("<b>Typology</b><br/>" + self.tipologia, styNormal)

        # 6 row
        d_letto_posa = Paragraph("<b>D (bed pose)</b><br/>" + self.d_letto_posa, styNormal)

        # 7 row
        d_letto_attesa = Paragraph("<b>D (waiting bed)</b><br/>" + self.d_letto_attesa, styNormal)

        # 8 row
        toro = Paragraph("<b>Toro</b><br/>" + self.toro, styNormal)

        # 9 row
        spessore = Paragraph("<b>Thikness</b><br/>" + self.spessore, styNormal)

        # 10 row
        lunghezza = Paragraph("<b>Weight</b><br/>" + self.lunghezza, styNormal)

        # 11 row
        larghezza = Paragraph("<b>Lenght</b><br/>" + self.larghezza, styNormal)

        # 12 row
        h = Paragraph("<b>h</b><br/>" + self.h, styNormal)

        # 13row
        lavorazione_e_stato_di_conservazione = Paragraph(
            "<b>Lavorazione e stato di conservazione</b><br/>" + self.lavorazione_e_stato_di_conservazione, styNormal)

        # 14 row
        confronti = Paragraph("<b>Comparision</b><br/>" + self.confronti, styNormal)

        # 15 row
        cronologia = Paragraph("<b>Chronology</b><br/>" + self.cronologia, styNormal)

        # 16 row
        compilatore = Paragraph("<b>Filler</b><br/>" + self.compilatore, styNormal)

        # 17 row
        descrizione = ''
        try:
            descrizione = Paragraph("<b>Description</b><br/>" + self.descrizione, styDescrizione)
        except:
            pass

            # 18 row
        bibliografia = ''
        if len(eval(self.bibliografia)) > 0:
            for i in eval(self.bibliografia):  # gigi
                if bibliografia == '':
                    try:
                        bibliografia += ("<b>Autor: %s, Year: %s, Title: %s, Pag.: %s, Fig.: %s") % (
                        str(i[0]), str(i[1]), str(i[2]), str(i[3]), str(i[4]))
                    except:
                        pass
                else:
                    try:
                        bibliografia += ("<b>Autor: %s, Year: %s, Title: %s, Pag.: %s, Fig.: %s") % (
                        str(i[0]), str(i[1]), str(i[2]), str(i[3]), str(i[4]))
                    except:
                        pass

        bibliografia = Paragraph("<b>Bibliography</b><br/>" + bibliografia, styNormal)

        # schema
        cell_schema = [  # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [alma, '01', '02', '03', '04', '05', '06', intestazione, '08', '09'],  # 0 row ok
            [sito, '01', '02', '03', '04', '05', '06', '07', scheda_numero, '09'],  # 1 row ok
            [collocazione, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 2 row ok
            [materiale, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 3 row ok
            [oggetto, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 4 row ok
            [tipologia, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 5 row ok
            [d_letto_posa, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 6 row ok
            [d_letto_attesa, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 7 row ok
            [toro, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 8 row ok
            [spessore, '02', '03', '04', '05', '06', '07', '08', '09'],  # 9 row ok
            [larghezza, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 10 row ok
            [lunghezza, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 11 row ok
            [h, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 12 row ok
            [descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 13 row ok
            [lavorazione_e_stato_di_conservazione, '01', '02', '03', '04', '05', '06', '07', '08', '09'],
            # 14 row ok
            [confronti, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 15 row ok
            [cronologia, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 16 row ok
            [bibliografia, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 17 row ok
            [compilatore, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 18 row ok
        ]

        # table style
        table_style = [

            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row
            ('SPAN', (0, 0), (6, 0)),  # intestazione
            ('SPAN', (7, 0), (9, 0)),  # logo

            # 1 row
            ('SPAN', (0, 1), (7, 1)),  # sito
            ('SPAN', (8, 1), (9, 1)),  # scheda numero

            # 2 row
            ('SPAN', (0, 2), (9, 2)),  # collocazione
            #                   ('VALIGN',(0,2),(9,2),'TOP'),

            # 3 row
            ('SPAN', (0, 3), (9, 3)),  # materiale

            # 4 row
            ('SPAN', (0, 4), (9, 4)),  # oggetto

            # 5row
            ('SPAN', (0, 5), (9, 5)),  # tipologia

            # 6 row
            ('SPAN', (0, 6), (9, 6)),  # d_letto_posa

            # 7 row
            ('SPAN', (0, 7), (9, 7)),  # d_letto_attesa

            # 8 row
            ('SPAN', (0, 8), (9, 8)),  # toro

            # 9 row
            ('SPAN', (0, 9), (9, 9)),  # spessore

            # 10 row
            ('SPAN', (0, 10), (9, 10)),  # larghezza

            # 11 row
            ('SPAN', (0, 11), (9, 11)),  # lunghezza

            # 12row
            ('SPAN', (0, 12), (9, 12)),  # h

            # 13 row
            ('SPAN', (0, 13), (9, 13)),  # descrizione

            # 14 row
            ('SPAN', (0, 14), (9, 14)),  # lavorazione

            # 15 row
            ('SPAN', (0, 15), (9, 15)),  # confronti

            # 16 row
            ('SPAN', (0, 16), (9, 16)),  # cronologia

            # 17 row
            ('SPAN', (0, 17), (9, 17)),  # bibliografia

            # 18 row
            ('SPAN', (0, 18), (9, 18)),  # autore scheda
            ('VALIGN', (0, 0), (-1, -1), 'TOP')

        ]

        t = Table(cell_schema, colWidths=50, rowHeights=None, style=table_style)

        return t
class generate_reperti_pdf:
    HOME = os.environ['PYARCHINIT_HOME']

    PDF_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def build_Invlap_sheets(self, records):
        elements = []
        for i in range(len(records)):
            single_invlap_sheet = single_Invlap_pdf_sheet(records[i])
            elements.append(single_invlap_sheet.create_sheet())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'scheda_reperti_lapidei.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_Invlapsheet)
        f.close()

    def build_Invlap_sheets_de(self, records):
        elements = []
        for i in range(len(records)):
            single_invlap_sheet = single_Invlap_pdf_sheet(records[i])
            elements.append(single_invlap_sheet.create_sheet_de())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Stoneformular.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_Invlapsheet)
        f.close()
    def build_Invlap_sheets_en(self, records):
        elements = []
        for i in range(len(records)):
            single_invlap_sheet = single_Invlap_pdf_sheet(records[i])
            elements.append(single_invlap_sheet.create_sheet_en())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Stone_form.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_Invlapsheet)
        f.close()   

