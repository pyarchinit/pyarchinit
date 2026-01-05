
#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
/***************************************************************************
        pyArchInit Plugin  - A QGIS plugin to manage archaeological dataset
                             stored in Postgres
                             -------------------
    begin                : 2024
    copyright            : (C) 2024 by Enzo Cocca <enzo.ccc@gmail.com>
    email                : enzo.ccc@gmail.com
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
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import (A4, A3)
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
registerFontFamily('Cambria', normal='Cambria')

from ..db.pyarchinit_conn_strings import Connection
from .pyarchinit_OS_utility import *


class NumberedCanvas_Faunasheet(canvas.Canvas):
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
                             "Pag. %d di %d" % (self._pageNumber, page_count))


class NumberedCanvas_Faunaindex(canvas.Canvas):
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
                             "Pag. %d di %d" % (self._pageNumber, page_count))


class single_Fauna_pdf_sheet(object):
    """
    Single Fauna record PDF sheet generator.
    Supports multiple languages: IT, DE, EN, FR, ES, AR, CA
    """

    def __init__(self, data):
        self.id_fauna = data[0]
        self.id_us = data[1]
        self.sito = data[2]
        self.area = data[3]
        self.saggio = data[4]
        self.us = data[5]
        self.datazione_us = data[6]
        self.responsabile_scheda = data[7]
        self.data_compilazione = data[8]
        self.documentazione_fotografica = data[9]
        self.metodologia_recupero = data[10]
        self.contesto = data[11]
        self.descrizione_contesto = data[12]
        self.resti_connessione_anatomica = data[13]
        self.tipologia_accumulo = data[14]
        self.deposizione = data[15]
        self.numero_stimato_resti = data[16]
        self.numero_minimo_individui = data[17]
        self.specie = data[18]
        self.parti_scheletriche = data[19]
        self.specie_psi = data[20]
        self.misure_ossa = data[21]
        self.stato_frammentazione = data[22]
        self.tracce_combustione = data[23]
        self.combustione_altri_materiali_us = data[24]
        self.tipo_combustione = data[25]
        self.segni_tafonomici_evidenti = data[26]
        self.caratterizzazione_segni_tafonomici = data[27]
        self.stato_conservazione = data[28]
        self.alterazioni_morfologiche = data[29]
        self.note_terreno_giacitura = data[30]
        self.campionature_effettuate = data[31]
        self.affidabilita_stratigrafica = data[32]
        self.classi_reperti_associazione = data[33]
        self.osservazioni = data[34]
        self.interpretazione = data[35]

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def create_sheet(self):
        """Italian version of the sheet"""
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.fontSize = 5
        styNormal.fontName = 'Cambria'
        styNormal.alignment = 0  # LEFT

        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.fontSize = 5
        styDescrizione.fontName = 'Cambria'
        styDescrizione.alignment = 4  # Justified

        # Header
        intestazione = Paragraph("<b>SCHEDA FAUNA ARCHEOLOGICA<br/>" + str(self.datestrfdate()) + "</b>", styNormal)

        # Logo
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
        logo.hAlign = 'CENTER'

        # Labels
        id_fauna = Paragraph("<b>ID SCHEDA</b><br/>" + str(self.id_fauna), styNormal)
        sito = Paragraph("<b>SITO</b><br/>" + str(self.sito), styNormal)
        area = Paragraph("<b>AREA</b><br/>" + str(self.area), styNormal)
        saggio = Paragraph("<b>SAGGIO</b><br/>" + str(self.saggio), styNormal)
        us = Paragraph("<b>US</b><br/>" + str(self.us), styNormal)
        datazione_us = Paragraph("<b>DATAZIONE US</b><br/>" + str(self.datazione_us), styNormal)
        responsabile_scheda = Paragraph("<b>RESPONSABILE</b><br/>" + str(self.responsabile_scheda), styNormal)
        data_compilazione = Paragraph("<b>DATA COMPILAZIONE</b><br/>" + str(self.data_compilazione), styNormal)
        documentazione_fotografica = Paragraph("<b>DOC. FOTOGRAFICA</b><br/>" + str(self.documentazione_fotografica), styNormal)
        metodologia_recupero = Paragraph("<b>METODOLOGIA RECUPERO</b><br/>" + str(self.metodologia_recupero), styNormal)
        contesto = Paragraph("<b>CONTESTO</b><br/>" + str(self.contesto), styNormal)
        descrizione_contesto = Paragraph("<b>DESCRIZIONE CONTESTO</b><br/>" + str(self.descrizione_contesto), styDescrizione)
        resti_connessione = Paragraph("<b>RESTI IN CONNESSIONE</b><br/>" + str(self.resti_connessione_anatomica), styNormal)
        tipologia_accumulo = Paragraph("<b>TIPOLOGIA ACCUMULO</b><br/>" + str(self.tipologia_accumulo), styNormal)
        deposizione = Paragraph("<b>DEPOSIZIONE</b><br/>" + str(self.deposizione), styNormal)
        numero_stimato = Paragraph("<b>N. STIMATO RESTI</b><br/>" + str(self.numero_stimato_resti), styNormal)
        nmi = Paragraph("<b>NMI</b><br/>" + str(self.numero_minimo_individui), styNormal)
        specie = Paragraph("<b>SPECIE</b><br/>" + str(self.specie), styDescrizione)
        parti_scheletriche = Paragraph("<b>PARTI SCHELETRICHE</b><br/>" + str(self.parti_scheletriche), styDescrizione)
        specie_psi = Paragraph("<b>SPECIE PSI</b><br/>" + str(self.specie_psi), styNormal)
        misure_ossa = Paragraph("<b>MISURE OSSA</b><br/>" + str(self.misure_ossa), styNormal)
        stato_frammentazione = Paragraph("<b>STATO FRAMMENTAZIONE</b><br/>" + str(self.stato_frammentazione), styNormal)
        tracce_combustione = Paragraph("<b>TRACCE COMBUSTIONE</b><br/>" + str(self.tracce_combustione), styNormal)
        combustione_altri = Paragraph("<b>COMBUSTIONE ALTRI MAT.</b><br/>" + ("Si" if self.combustione_altri_materiali_us else "No"), styNormal)
        tipo_combustione = Paragraph("<b>TIPO COMBUSTIONE</b><br/>" + str(self.tipo_combustione), styNormal)
        segni_tafonomici = Paragraph("<b>SEGNI TAFONOMICI</b><br/>" + str(self.segni_tafonomici_evidenti), styNormal)
        caratterizzazione_tafo = Paragraph("<b>CARATTERIZZAZIONE SEGNI</b><br/>" + str(self.caratterizzazione_segni_tafonomici), styDescrizione)
        stato_conservazione = Paragraph("<b>STATO CONSERVAZIONE</b><br/>" + str(self.stato_conservazione), styNormal)
        alterazioni = Paragraph("<b>ALTERAZIONI MORFOLOGICHE</b><br/>" + str(self.alterazioni_morfologiche), styNormal)
        note_terreno = Paragraph("<b>NOTE TERRENO/GIACITURA</b><br/>" + str(self.note_terreno_giacitura), styDescrizione)
        campionature = Paragraph("<b>CAMPIONATURE</b><br/>" + str(self.campionature_effettuate), styNormal)
        affidabilita = Paragraph("<b>AFFIDABILIT&Agrave; STRAT.</b><br/>" + str(self.affidabilita_stratigrafica), styNormal)
        classi_reperti = Paragraph("<b>CLASSI REPERTI ASSOC.</b><br/>" + str(self.classi_reperti_associazione), styDescrizione)
        osservazioni = Paragraph("<b>OSSERVAZIONI</b><br/>" + str(self.osservazioni), styDescrizione)
        interpretazione = Paragraph("<b>INTERPRETAZIONE</b><br/>" + str(self.interpretazione), styDescrizione)

        # Schema table
        cell_schema = [
            [intestazione, '', '', '', '', '', logo, '', ''],
            [sito, '', area, saggio, us, '', datazione_us, '', ''],
            [responsabile_scheda, '', '', data_compilazione, '', documentazione_fotografica, '', '', ''],
            [metodologia_recupero, '', contesto, '', '', descrizione_contesto, '', '', ''],
            [resti_connessione, '', tipologia_accumulo, '', deposizione, '', '', '', ''],
            [numero_stimato, '', nmi, '', specie, '', '', '', ''],
            [parti_scheletriche, '', '', '', '', '', '', '', ''],
            [specie_psi, '', misure_ossa, '', stato_frammentazione, '', '', '', ''],
            [tracce_combustione, '', combustione_altri, '', tipo_combustione, '', '', '', ''],
            [segni_tafonomici, '', caratterizzazione_tafo, '', '', '', '', '', ''],
            [stato_conservazione, '', alterazioni, '', '', '', '', '', ''],
            [note_terreno, '', '', '', '', '', '', '', ''],
            [campionature, '', '', affidabilita, '', '', '', '', ''],
            [classi_reperti, '', '', '', '', '', '', '', ''],
            [osservazioni, '', '', '', '', '', '', '', ''],
            [interpretazione, '', '', '', '', '', '', '', '']
        ]

        # Table style
        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # Row 0 - header
            ('SPAN', (0, 0), (5, 0)),
            ('SPAN', (6, 0), (8, 0)),
            # Row 1 - sito, area, saggio, us, datazione
            ('SPAN', (0, 1), (1, 1)),
            ('SPAN', (4, 1), (5, 1)),
            ('SPAN', (6, 1), (8, 1)),
            # Row 2 - responsabile, data, doc foto
            ('SPAN', (0, 2), (2, 2)),
            ('SPAN', (3, 2), (4, 2)),
            ('SPAN', (5, 2), (8, 2)),
            # Row 3 - metodologia, contesto, descrizione
            ('SPAN', (0, 3), (1, 3)),
            ('SPAN', (2, 3), (4, 3)),
            ('SPAN', (5, 3), (8, 3)),
            # Row 4 - resti, tipologia, deposizione
            ('SPAN', (0, 4), (1, 4)),
            ('SPAN', (2, 4), (3, 4)),
            ('SPAN', (4, 4), (8, 4)),
            # Row 5 - numero stimato, nmi, specie
            ('SPAN', (0, 5), (1, 5)),
            ('SPAN', (2, 5), (3, 5)),
            ('SPAN', (4, 5), (8, 5)),
            # Row 6 - parti scheletriche
            ('SPAN', (0, 6), (8, 6)),
            # Row 7 - specie_psi, misure, frammentazione
            ('SPAN', (0, 7), (1, 7)),
            ('SPAN', (2, 7), (3, 7)),
            ('SPAN', (4, 7), (8, 7)),
            # Row 8 - tracce combustione
            ('SPAN', (0, 8), (1, 8)),
            ('SPAN', (2, 8), (3, 8)),
            ('SPAN', (4, 8), (8, 8)),
            # Row 9 - segni tafonomici
            ('SPAN', (0, 9), (1, 9)),
            ('SPAN', (2, 9), (8, 9)),
            # Row 10 - stato conservazione, alterazioni
            ('SPAN', (0, 10), (1, 10)),
            ('SPAN', (2, 10), (8, 10)),
            # Row 11 - note terreno
            ('SPAN', (0, 11), (8, 11)),
            # Row 12 - campionature, affidabilita
            ('SPAN', (0, 12), (2, 12)),
            ('SPAN', (3, 12), (8, 12)),
            # Row 13 - classi reperti
            ('SPAN', (0, 13), (8, 13)),
            # Row 14 - osservazioni
            ('SPAN', (0, 14), (8, 14)),
            # Row 15 - interpretazione
            ('SPAN', (0, 15), (8, 15)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]

        t = Table(cell_schema, colWidths=55, rowHeights=None, style=table_style)
        return t

    def create_sheet_de(self):
        """German version of the sheet"""
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.fontSize = 5
        styNormal.fontName = 'Cambria'
        styNormal.alignment = 0

        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.fontSize = 5
        styDescrizione.fontName = 'Cambria'
        styDescrizione.alignment = 4

        intestazione = Paragraph("<b>ARCH&Auml;OLOGISCHE FAUNA FORMULAR<br/>" + str(self.datestrfdate()) + "</b>", styNormal)

        home = os.environ['PYARCHINIT_HOME']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo_de.jpg')
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch

        id_fauna = Paragraph("<b>FORMULAR-ID</b><br/>" + str(self.id_fauna), styNormal)
        sito = Paragraph("<b>FUNDSTELLE</b><br/>" + str(self.sito), styNormal)
        area = Paragraph("<b>BEREICH</b><br/>" + str(self.area), styNormal)
        saggio = Paragraph("<b>SCHNITT</b><br/>" + str(self.saggio), styNormal)
        us = Paragraph("<b>SE</b><br/>" + str(self.us), styNormal)
        datazione_us = Paragraph("<b>DATIERUNG SE</b><br/>" + str(self.datazione_us), styNormal)
        responsabile_scheda = Paragraph("<b>BEARBEITER</b><br/>" + str(self.responsabile_scheda), styNormal)
        data_compilazione = Paragraph("<b>ERSTELLUNGSDATUM</b><br/>" + str(self.data_compilazione), styNormal)
        documentazione_fotografica = Paragraph("<b>FOTO-DOK.</b><br/>" + str(self.documentazione_fotografica), styNormal)
        metodologia_recupero = Paragraph("<b>BERGUNGSMETHODE</b><br/>" + str(self.metodologia_recupero), styNormal)
        contesto = Paragraph("<b>KONTEXT</b><br/>" + str(self.contesto), styNormal)
        descrizione_contesto = Paragraph("<b>KONTEXTBESCHREIBUNG</b><br/>" + str(self.descrizione_contesto), styDescrizione)
        resti_connessione = Paragraph("<b>VERBUNDENE RESTE</b><br/>" + str(self.resti_connessione_anatomica), styNormal)
        tipologia_accumulo = Paragraph("<b>AKKUMULATIONSTYP</b><br/>" + str(self.tipologia_accumulo), styNormal)
        deposizione = Paragraph("<b>ABLAGERUNG</b><br/>" + str(self.deposizione), styNormal)
        numero_stimato = Paragraph("<b>GESCH&Auml;TZTE ANZAHL</b><br/>" + str(self.numero_stimato_resti), styNormal)
        nmi = Paragraph("<b>MNI</b><br/>" + str(self.numero_minimo_individui), styNormal)
        specie = Paragraph("<b>SPEZIES</b><br/>" + str(self.specie), styDescrizione)
        parti_scheletriche = Paragraph("<b>SKELETTELEMENTE</b><br/>" + str(self.parti_scheletriche), styDescrizione)
        specie_psi = Paragraph("<b>SPEZIES PSI</b><br/>" + str(self.specie_psi), styNormal)
        misure_ossa = Paragraph("<b>KNOCHENMASSE</b><br/>" + str(self.misure_ossa), styNormal)
        stato_frammentazione = Paragraph("<b>FRAGMENTIERUNG</b><br/>" + str(self.stato_frammentazione), styNormal)
        tracce_combustione = Paragraph("<b>BRANDSPUREN</b><br/>" + str(self.tracce_combustione), styNormal)
        combustione_altri = Paragraph("<b>BRAND ANDERER MAT.</b><br/>" + ("Ja" if self.combustione_altri_materiali_us else "Nein"), styNormal)
        tipo_combustione = Paragraph("<b>BRANDTYP</b><br/>" + str(self.tipo_combustione), styNormal)
        segni_tafonomici = Paragraph("<b>TAPHONOMISCHE ZEICHEN</b><br/>" + str(self.segni_tafonomici_evidenti), styNormal)
        caratterizzazione_tafo = Paragraph("<b>TAPH. CHARAKTERISIERUNG</b><br/>" + str(self.caratterizzazione_segni_tafonomici), styDescrizione)
        stato_conservazione = Paragraph("<b>ERHALTUNGSZUSTAND</b><br/>" + str(self.stato_conservazione), styNormal)
        alterazioni = Paragraph("<b>MORPH. VER&Auml;NDERUNGEN</b><br/>" + str(self.alterazioni_morfologiche), styNormal)
        note_terreno = Paragraph("<b>ANMERKUNGEN LAGE</b><br/>" + str(self.note_terreno_giacitura), styDescrizione)
        campionature = Paragraph("<b>PROBENAHMEN</b><br/>" + str(self.campionature_effettuate), styNormal)
        affidabilita = Paragraph("<b>STRAT. ZUVERL&Auml;SSIGKEIT</b><br/>" + str(self.affidabilita_stratigrafica), styNormal)
        classi_reperti = Paragraph("<b>ASSOZIIERTE FUNDE</b><br/>" + str(self.classi_reperti_associazione), styDescrizione)
        osservazioni = Paragraph("<b>BEOBACHTUNGEN</b><br/>" + str(self.osservazioni), styDescrizione)
        interpretazione = Paragraph("<b>INTERPRETATION</b><br/>" + str(self.interpretazione), styDescrizione)

        cell_schema = [
            [intestazione, '', '', '', '', '', logo, '', ''],
            [sito, '', area, saggio, us, '', datazione_us, '', ''],
            [responsabile_scheda, '', '', data_compilazione, '', documentazione_fotografica, '', '', ''],
            [metodologia_recupero, '', contesto, '', '', descrizione_contesto, '', '', ''],
            [resti_connessione, '', tipologia_accumulo, '', deposizione, '', '', '', ''],
            [numero_stimato, '', nmi, '', specie, '', '', '', ''],
            [parti_scheletriche, '', '', '', '', '', '', '', ''],
            [specie_psi, '', misure_ossa, '', stato_frammentazione, '', '', '', ''],
            [tracce_combustione, '', combustione_altri, '', tipo_combustione, '', '', '', ''],
            [segni_tafonomici, '', caratterizzazione_tafo, '', '', '', '', '', ''],
            [stato_conservazione, '', alterazioni, '', '', '', '', '', ''],
            [note_terreno, '', '', '', '', '', '', '', ''],
            [campionature, '', '', affidabilita, '', '', '', '', ''],
            [classi_reperti, '', '', '', '', '', '', '', ''],
            [osservazioni, '', '', '', '', '', '', '', ''],
            [interpretazione, '', '', '', '', '', '', '', '']
        ]

        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('SPAN', (0, 0), (5, 0)), ('SPAN', (6, 0), (8, 0)),
            ('SPAN', (0, 1), (1, 1)), ('SPAN', (4, 1), (5, 1)), ('SPAN', (6, 1), (8, 1)),
            ('SPAN', (0, 2), (2, 2)), ('SPAN', (3, 2), (4, 2)), ('SPAN', (5, 2), (8, 2)),
            ('SPAN', (0, 3), (1, 3)), ('SPAN', (2, 3), (4, 3)), ('SPAN', (5, 3), (8, 3)),
            ('SPAN', (0, 4), (1, 4)), ('SPAN', (2, 4), (3, 4)), ('SPAN', (4, 4), (8, 4)),
            ('SPAN', (0, 5), (1, 5)), ('SPAN', (2, 5), (3, 5)), ('SPAN', (4, 5), (8, 5)),
            ('SPAN', (0, 6), (8, 6)),
            ('SPAN', (0, 7), (1, 7)), ('SPAN', (2, 7), (3, 7)), ('SPAN', (4, 7), (8, 7)),
            ('SPAN', (0, 8), (1, 8)), ('SPAN', (2, 8), (3, 8)), ('SPAN', (4, 8), (8, 8)),
            ('SPAN', (0, 9), (1, 9)), ('SPAN', (2, 9), (8, 9)),
            ('SPAN', (0, 10), (1, 10)), ('SPAN', (2, 10), (8, 10)),
            ('SPAN', (0, 11), (8, 11)),
            ('SPAN', (0, 12), (2, 12)), ('SPAN', (3, 12), (8, 12)),
            ('SPAN', (0, 13), (8, 13)),
            ('SPAN', (0, 14), (8, 14)),
            ('SPAN', (0, 15), (8, 15)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]

        t = Table(cell_schema, colWidths=55, rowHeights=None, style=table_style)
        return t

    def create_sheet_en(self):
        """English version of the sheet"""
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.fontSize = 5
        styNormal.fontName = 'Cambria'
        styNormal.alignment = 0

        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.fontSize = 5
        styDescrizione.fontName = 'Cambria'
        styDescrizione.alignment = 4

        intestazione = Paragraph("<b>ARCHAEOLOGICAL FAUNA RECORD<br/>" + str(self.datestrfdate()) + "</b>", styNormal)

        home = os.environ['PYARCHINIT_HOME']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch

        id_fauna = Paragraph("<b>RECORD ID</b><br/>" + str(self.id_fauna), styNormal)
        sito = Paragraph("<b>SITE</b><br/>" + str(self.sito), styNormal)
        area = Paragraph("<b>AREA</b><br/>" + str(self.area), styNormal)
        saggio = Paragraph("<b>TRENCH</b><br/>" + str(self.saggio), styNormal)
        us = Paragraph("<b>SU</b><br/>" + str(self.us), styNormal)
        datazione_us = Paragraph("<b>SU DATING</b><br/>" + str(self.datazione_us), styNormal)
        responsabile_scheda = Paragraph("<b>RECORDER</b><br/>" + str(self.responsabile_scheda), styNormal)
        data_compilazione = Paragraph("<b>RECORDING DATE</b><br/>" + str(self.data_compilazione), styNormal)
        documentazione_fotografica = Paragraph("<b>PHOTO DOC.</b><br/>" + str(self.documentazione_fotografica), styNormal)
        metodologia_recupero = Paragraph("<b>RECOVERY METHOD</b><br/>" + str(self.metodologia_recupero), styNormal)
        contesto = Paragraph("<b>CONTEXT</b><br/>" + str(self.contesto), styNormal)
        descrizione_contesto = Paragraph("<b>CONTEXT DESCRIPTION</b><br/>" + str(self.descrizione_contesto), styDescrizione)
        resti_connessione = Paragraph("<b>ANATOMICAL CONNECTION</b><br/>" + str(self.resti_connessione_anatomica), styNormal)
        tipologia_accumulo = Paragraph("<b>ACCUMULATION TYPE</b><br/>" + str(self.tipologia_accumulo), styNormal)
        deposizione = Paragraph("<b>DEPOSITION</b><br/>" + str(self.deposizione), styNormal)
        numero_stimato = Paragraph("<b>ESTIMATED NUMBER</b><br/>" + str(self.numero_stimato_resti), styNormal)
        nmi = Paragraph("<b>MNI</b><br/>" + str(self.numero_minimo_individui), styNormal)
        specie = Paragraph("<b>SPECIES</b><br/>" + str(self.specie), styDescrizione)
        parti_scheletriche = Paragraph("<b>SKELETAL ELEMENTS</b><br/>" + str(self.parti_scheletriche), styDescrizione)
        specie_psi = Paragraph("<b>SPECIES PSI</b><br/>" + str(self.specie_psi), styNormal)
        misure_ossa = Paragraph("<b>BONE MEASUREMENTS</b><br/>" + str(self.misure_ossa), styNormal)
        stato_frammentazione = Paragraph("<b>FRAGMENTATION</b><br/>" + str(self.stato_frammentazione), styNormal)
        tracce_combustione = Paragraph("<b>BURNING TRACES</b><br/>" + str(self.tracce_combustione), styNormal)
        combustione_altri = Paragraph("<b>OTHER BURNED MAT.</b><br/>" + ("Yes" if self.combustione_altri_materiali_us else "No"), styNormal)
        tipo_combustione = Paragraph("<b>BURNING TYPE</b><br/>" + str(self.tipo_combustione), styNormal)
        segni_tafonomici = Paragraph("<b>TAPHONOMIC SIGNS</b><br/>" + str(self.segni_tafonomici_evidenti), styNormal)
        caratterizzazione_tafo = Paragraph("<b>TAPH. CHARACTERIZATION</b><br/>" + str(self.caratterizzazione_segni_tafonomici), styDescrizione)
        stato_conservazione = Paragraph("<b>PRESERVATION STATE</b><br/>" + str(self.stato_conservazione), styNormal)
        alterazioni = Paragraph("<b>MORPH. ALTERATIONS</b><br/>" + str(self.alterazioni_morfologiche), styNormal)
        note_terreno = Paragraph("<b>NOTES ON POSITION</b><br/>" + str(self.note_terreno_giacitura), styDescrizione)
        campionature = Paragraph("<b>SAMPLING</b><br/>" + str(self.campionature_effettuate), styNormal)
        affidabilita = Paragraph("<b>STRAT. RELIABILITY</b><br/>" + str(self.affidabilita_stratigrafica), styNormal)
        classi_reperti = Paragraph("<b>ASSOCIATED FINDS</b><br/>" + str(self.classi_reperti_associazione), styDescrizione)
        osservazioni = Paragraph("<b>OBSERVATIONS</b><br/>" + str(self.osservazioni), styDescrizione)
        interpretazione = Paragraph("<b>INTERPRETATION</b><br/>" + str(self.interpretazione), styDescrizione)

        cell_schema = [
            [intestazione, '', '', '', '', '', logo, '', ''],
            [sito, '', area, saggio, us, '', datazione_us, '', ''],
            [responsabile_scheda, '', '', data_compilazione, '', documentazione_fotografica, '', '', ''],
            [metodologia_recupero, '', contesto, '', '', descrizione_contesto, '', '', ''],
            [resti_connessione, '', tipologia_accumulo, '', deposizione, '', '', '', ''],
            [numero_stimato, '', nmi, '', specie, '', '', '', ''],
            [parti_scheletriche, '', '', '', '', '', '', '', ''],
            [specie_psi, '', misure_ossa, '', stato_frammentazione, '', '', '', ''],
            [tracce_combustione, '', combustione_altri, '', tipo_combustione, '', '', '', ''],
            [segni_tafonomici, '', caratterizzazione_tafo, '', '', '', '', '', ''],
            [stato_conservazione, '', alterazioni, '', '', '', '', '', ''],
            [note_terreno, '', '', '', '', '', '', '', ''],
            [campionature, '', '', affidabilita, '', '', '', '', ''],
            [classi_reperti, '', '', '', '', '', '', '', ''],
            [osservazioni, '', '', '', '', '', '', '', ''],
            [interpretazione, '', '', '', '', '', '', '', '']
        ]

        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('SPAN', (0, 0), (5, 0)), ('SPAN', (6, 0), (8, 0)),
            ('SPAN', (0, 1), (1, 1)), ('SPAN', (4, 1), (5, 1)), ('SPAN', (6, 1), (8, 1)),
            ('SPAN', (0, 2), (2, 2)), ('SPAN', (3, 2), (4, 2)), ('SPAN', (5, 2), (8, 2)),
            ('SPAN', (0, 3), (1, 3)), ('SPAN', (2, 3), (4, 3)), ('SPAN', (5, 3), (8, 3)),
            ('SPAN', (0, 4), (1, 4)), ('SPAN', (2, 4), (3, 4)), ('SPAN', (4, 4), (8, 4)),
            ('SPAN', (0, 5), (1, 5)), ('SPAN', (2, 5), (3, 5)), ('SPAN', (4, 5), (8, 5)),
            ('SPAN', (0, 6), (8, 6)),
            ('SPAN', (0, 7), (1, 7)), ('SPAN', (2, 7), (3, 7)), ('SPAN', (4, 7), (8, 7)),
            ('SPAN', (0, 8), (1, 8)), ('SPAN', (2, 8), (3, 8)), ('SPAN', (4, 8), (8, 8)),
            ('SPAN', (0, 9), (1, 9)), ('SPAN', (2, 9), (8, 9)),
            ('SPAN', (0, 10), (1, 10)), ('SPAN', (2, 10), (8, 10)),
            ('SPAN', (0, 11), (8, 11)),
            ('SPAN', (0, 12), (2, 12)), ('SPAN', (3, 12), (8, 12)),
            ('SPAN', (0, 13), (8, 13)),
            ('SPAN', (0, 14), (8, 14)),
            ('SPAN', (0, 15), (8, 15)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]

        t = Table(cell_schema, colWidths=55, rowHeights=None, style=table_style)
        return t

    def create_sheet_fr(self):
        """French version of the sheet"""
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.fontSize = 5
        styNormal.fontName = 'Cambria'
        styNormal.alignment = 0

        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.fontSize = 5
        styDescrizione.fontName = 'Cambria'
        styDescrizione.alignment = 4

        intestazione = Paragraph("<b>FICHE FAUNE ARCH&Eacute;OLOGIQUE<br/>" + str(self.datestrfdate()) + "</b>", styNormal)

        home = os.environ['PYARCHINIT_HOME']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch

        sito = Paragraph("<b>SITE</b><br/>" + str(self.sito), styNormal)
        area = Paragraph("<b>ZONE</b><br/>" + str(self.area), styNormal)
        saggio = Paragraph("<b>SONDAGE</b><br/>" + str(self.saggio), styNormal)
        us = Paragraph("<b>US</b><br/>" + str(self.us), styNormal)
        datazione_us = Paragraph("<b>DATATION US</b><br/>" + str(self.datazione_us), styNormal)
        responsabile_scheda = Paragraph("<b>RESPONSABLE</b><br/>" + str(self.responsabile_scheda), styNormal)
        data_compilazione = Paragraph("<b>DATE DE COMPILATION</b><br/>" + str(self.data_compilazione), styNormal)
        documentazione_fotografica = Paragraph("<b>DOC. PHOTO</b><br/>" + str(self.documentazione_fotografica), styNormal)
        metodologia_recupero = Paragraph("<b>M&Eacute;THODE DE R&Eacute;CUP.</b><br/>" + str(self.metodologia_recupero), styNormal)
        contesto = Paragraph("<b>CONTEXTE</b><br/>" + str(self.contesto), styNormal)
        descrizione_contesto = Paragraph("<b>DESCRIPTION CONTEXTE</b><br/>" + str(self.descrizione_contesto), styDescrizione)
        resti_connessione = Paragraph("<b>CONNEXION ANATOMIQUE</b><br/>" + str(self.resti_connessione_anatomica), styNormal)
        tipologia_accumulo = Paragraph("<b>TYPE D'ACCUMULATION</b><br/>" + str(self.tipologia_accumulo), styNormal)
        deposizione = Paragraph("<b>D&Eacute;POSITION</b><br/>" + str(self.deposizione), styNormal)
        numero_stimato = Paragraph("<b>NOMBRE ESTIM&Eacute;</b><br/>" + str(self.numero_stimato_resti), styNormal)
        nmi = Paragraph("<b>NMI</b><br/>" + str(self.numero_minimo_individui), styNormal)
        specie = Paragraph("<b>ESP&Egrave;CE</b><br/>" + str(self.specie), styDescrizione)
        parti_scheletriche = Paragraph("<b>&Eacute;L&Eacute;MENTS SQUELETTIQUES</b><br/>" + str(self.parti_scheletriche), styDescrizione)
        specie_psi = Paragraph("<b>ESP&Egrave;CE PSI</b><br/>" + str(self.specie_psi), styNormal)
        misure_ossa = Paragraph("<b>MESURES OSSEUSES</b><br/>" + str(self.misure_ossa), styNormal)
        stato_frammentazione = Paragraph("<b>FRAGMENTATION</b><br/>" + str(self.stato_frammentazione), styNormal)
        tracce_combustione = Paragraph("<b>TRACES DE COMBUSTION</b><br/>" + str(self.tracce_combustione), styNormal)
        combustione_altri = Paragraph("<b>AUTRES MAT. BR&Ucirc;L&Eacute;S</b><br/>" + ("Oui" if self.combustione_altri_materiali_us else "Non"), styNormal)
        tipo_combustione = Paragraph("<b>TYPE DE COMBUSTION</b><br/>" + str(self.tipo_combustione), styNormal)
        segni_tafonomici = Paragraph("<b>SIGNES TAPHONOMIQUES</b><br/>" + str(self.segni_tafonomici_evidenti), styNormal)
        caratterizzazione_tafo = Paragraph("<b>CARACT. TAPHONOMIQUE</b><br/>" + str(self.caratterizzazione_segni_tafonomici), styDescrizione)
        stato_conservazione = Paragraph("<b>&Eacute;TAT DE CONSERVATION</b><br/>" + str(self.stato_conservazione), styNormal)
        alterazioni = Paragraph("<b>ALT&Eacute;RATIONS MORPH.</b><br/>" + str(self.alterazioni_morfologiche), styNormal)
        note_terreno = Paragraph("<b>NOTES SUR LA POSITION</b><br/>" + str(self.note_terreno_giacitura), styDescrizione)
        campionature = Paragraph("<b>&Eacute;CHANTILLONNAGES</b><br/>" + str(self.campionature_effettuate), styNormal)
        affidabilita = Paragraph("<b>FIABILIT&Eacute; STRAT.</b><br/>" + str(self.affidabilita_stratigrafica), styNormal)
        classi_reperti = Paragraph("<b>MOBILIER ASSOCI&Eacute;</b><br/>" + str(self.classi_reperti_associazione), styDescrizione)
        osservazioni = Paragraph("<b>OBSERVATIONS</b><br/>" + str(self.osservazioni), styDescrizione)
        interpretazione = Paragraph("<b>INTERPR&Eacute;TATION</b><br/>" + str(self.interpretazione), styDescrizione)

        cell_schema = [
            [intestazione, '', '', '', '', '', logo, '', ''],
            [sito, '', area, saggio, us, '', datazione_us, '', ''],
            [responsabile_scheda, '', '', data_compilazione, '', documentazione_fotografica, '', '', ''],
            [metodologia_recupero, '', contesto, '', '', descrizione_contesto, '', '', ''],
            [resti_connessione, '', tipologia_accumulo, '', deposizione, '', '', '', ''],
            [numero_stimato, '', nmi, '', specie, '', '', '', ''],
            [parti_scheletriche, '', '', '', '', '', '', '', ''],
            [specie_psi, '', misure_ossa, '', stato_frammentazione, '', '', '', ''],
            [tracce_combustione, '', combustione_altri, '', tipo_combustione, '', '', '', ''],
            [segni_tafonomici, '', caratterizzazione_tafo, '', '', '', '', '', ''],
            [stato_conservazione, '', alterazioni, '', '', '', '', '', ''],
            [note_terreno, '', '', '', '', '', '', '', ''],
            [campionature, '', '', affidabilita, '', '', '', '', ''],
            [classi_reperti, '', '', '', '', '', '', '', ''],
            [osservazioni, '', '', '', '', '', '', '', ''],
            [interpretazione, '', '', '', '', '', '', '', '']
        ]

        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('SPAN', (0, 0), (5, 0)), ('SPAN', (6, 0), (8, 0)),
            ('SPAN', (0, 1), (1, 1)), ('SPAN', (4, 1), (5, 1)), ('SPAN', (6, 1), (8, 1)),
            ('SPAN', (0, 2), (2, 2)), ('SPAN', (3, 2), (4, 2)), ('SPAN', (5, 2), (8, 2)),
            ('SPAN', (0, 3), (1, 3)), ('SPAN', (2, 3), (4, 3)), ('SPAN', (5, 3), (8, 3)),
            ('SPAN', (0, 4), (1, 4)), ('SPAN', (2, 4), (3, 4)), ('SPAN', (4, 4), (8, 4)),
            ('SPAN', (0, 5), (1, 5)), ('SPAN', (2, 5), (3, 5)), ('SPAN', (4, 5), (8, 5)),
            ('SPAN', (0, 6), (8, 6)),
            ('SPAN', (0, 7), (1, 7)), ('SPAN', (2, 7), (3, 7)), ('SPAN', (4, 7), (8, 7)),
            ('SPAN', (0, 8), (1, 8)), ('SPAN', (2, 8), (3, 8)), ('SPAN', (4, 8), (8, 8)),
            ('SPAN', (0, 9), (1, 9)), ('SPAN', (2, 9), (8, 9)),
            ('SPAN', (0, 10), (1, 10)), ('SPAN', (2, 10), (8, 10)),
            ('SPAN', (0, 11), (8, 11)),
            ('SPAN', (0, 12), (2, 12)), ('SPAN', (3, 12), (8, 12)),
            ('SPAN', (0, 13), (8, 13)),
            ('SPAN', (0, 14), (8, 14)),
            ('SPAN', (0, 15), (8, 15)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]

        t = Table(cell_schema, colWidths=55, rowHeights=None, style=table_style)
        return t

    def create_sheet_es(self):
        """Spanish version of the sheet"""
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.fontSize = 5
        styNormal.fontName = 'Cambria'
        styNormal.alignment = 0

        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.fontSize = 5
        styDescrizione.fontName = 'Cambria'
        styDescrizione.alignment = 4

        intestazione = Paragraph("<b>FICHA DE FAUNA ARQUEOL&Oacute;GICA<br/>" + str(self.datestrfdate()) + "</b>", styNormal)

        home = os.environ['PYARCHINIT_HOME']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch

        sito = Paragraph("<b>SITIO</b><br/>" + str(self.sito), styNormal)
        area = Paragraph("<b>&Aacute;REA</b><br/>" + str(self.area), styNormal)
        saggio = Paragraph("<b>SONDEO</b><br/>" + str(self.saggio), styNormal)
        us = Paragraph("<b>UE</b><br/>" + str(self.us), styNormal)
        datazione_us = Paragraph("<b>DATACI&Oacute;N UE</b><br/>" + str(self.datazione_us), styNormal)
        responsabile_scheda = Paragraph("<b>RESPONSABLE</b><br/>" + str(self.responsabile_scheda), styNormal)
        data_compilazione = Paragraph("<b>FECHA COMPILACI&Oacute;N</b><br/>" + str(self.data_compilazione), styNormal)
        documentazione_fotografica = Paragraph("<b>DOC. FOTOGR&Aacute;FICA</b><br/>" + str(self.documentazione_fotografica), styNormal)
        metodologia_recupero = Paragraph("<b>M&Eacute;TODO RECUPERACI&Oacute;N</b><br/>" + str(self.metodologia_recupero), styNormal)
        contesto = Paragraph("<b>CONTEXTO</b><br/>" + str(self.contesto), styNormal)
        descrizione_contesto = Paragraph("<b>DESCRIPCI&Oacute;N CONTEXTO</b><br/>" + str(self.descrizione_contesto), styDescrizione)
        resti_connessione = Paragraph("<b>CONEXI&Oacute;N ANAT&Oacute;MICA</b><br/>" + str(self.resti_connessione_anatomica), styNormal)
        tipologia_accumulo = Paragraph("<b>TIPO ACUMULACI&Oacute;N</b><br/>" + str(self.tipologia_accumulo), styNormal)
        deposizione = Paragraph("<b>DEPOSICI&Oacute;N</b><br/>" + str(self.deposizione), styNormal)
        numero_stimato = Paragraph("<b>N&Uacute;MERO ESTIMADO</b><br/>" + str(self.numero_stimato_resti), styNormal)
        nmi = Paragraph("<b>NMI</b><br/>" + str(self.numero_minimo_individui), styNormal)
        specie = Paragraph("<b>ESPECIE</b><br/>" + str(self.specie), styDescrizione)
        parti_scheletriche = Paragraph("<b>ELEMENTOS ESQUEL&Eacute;TICOS</b><br/>" + str(self.parti_scheletriche), styDescrizione)
        specie_psi = Paragraph("<b>ESPECIE PSI</b><br/>" + str(self.specie_psi), styNormal)
        misure_ossa = Paragraph("<b>MEDIDAS &Oacute;SEAS</b><br/>" + str(self.misure_ossa), styNormal)
        stato_frammentazione = Paragraph("<b>FRAGMENTACI&Oacute;N</b><br/>" + str(self.stato_frammentazione), styNormal)
        tracce_combustione = Paragraph("<b>TRAZAS COMBUSTI&Oacute;N</b><br/>" + str(self.tracce_combustione), styNormal)
        combustione_altri = Paragraph("<b>OTROS MAT. QUEMADOS</b><br/>" + ("S&iacute;" if self.combustione_altri_materiali_us else "No"), styNormal)
        tipo_combustione = Paragraph("<b>TIPO COMBUSTI&Oacute;N</b><br/>" + str(self.tipo_combustione), styNormal)
        segni_tafonomici = Paragraph("<b>SE&Ntilde;ALES TAFON&Oacute;MICAS</b><br/>" + str(self.segni_tafonomici_evidenti), styNormal)
        caratterizzazione_tafo = Paragraph("<b>CARACT. TAFON&Oacute;MICA</b><br/>" + str(self.caratterizzazione_segni_tafonomici), styDescrizione)
        stato_conservazione = Paragraph("<b>ESTADO CONSERVACI&Oacute;N</b><br/>" + str(self.stato_conservazione), styNormal)
        alterazioni = Paragraph("<b>ALTERACIONES MORF.</b><br/>" + str(self.alterazioni_morfologiche), styNormal)
        note_terreno = Paragraph("<b>NOTAS POSICI&Oacute;N</b><br/>" + str(self.note_terreno_giacitura), styDescrizione)
        campionature = Paragraph("<b>MUESTREOS</b><br/>" + str(self.campionature_effettuate), styNormal)
        affidabilita = Paragraph("<b>FIABILIDAD ESTRAT.</b><br/>" + str(self.affidabilita_stratigrafica), styNormal)
        classi_reperti = Paragraph("<b>MATERIALES ASOCIADOS</b><br/>" + str(self.classi_reperti_associazione), styDescrizione)
        osservazioni = Paragraph("<b>OBSERVACIONES</b><br/>" + str(self.osservazioni), styDescrizione)
        interpretazione = Paragraph("<b>INTERPRETACI&Oacute;N</b><br/>" + str(self.interpretazione), styDescrizione)

        cell_schema = [
            [intestazione, '', '', '', '', '', logo, '', ''],
            [sito, '', area, saggio, us, '', datazione_us, '', ''],
            [responsabile_scheda, '', '', data_compilazione, '', documentazione_fotografica, '', '', ''],
            [metodologia_recupero, '', contesto, '', '', descrizione_contesto, '', '', ''],
            [resti_connessione, '', tipologia_accumulo, '', deposizione, '', '', '', ''],
            [numero_stimato, '', nmi, '', specie, '', '', '', ''],
            [parti_scheletriche, '', '', '', '', '', '', '', ''],
            [specie_psi, '', misure_ossa, '', stato_frammentazione, '', '', '', ''],
            [tracce_combustione, '', combustione_altri, '', tipo_combustione, '', '', '', ''],
            [segni_tafonomici, '', caratterizzazione_tafo, '', '', '', '', '', ''],
            [stato_conservazione, '', alterazioni, '', '', '', '', '', ''],
            [note_terreno, '', '', '', '', '', '', '', ''],
            [campionature, '', '', affidabilita, '', '', '', '', ''],
            [classi_reperti, '', '', '', '', '', '', '', ''],
            [osservazioni, '', '', '', '', '', '', '', ''],
            [interpretazione, '', '', '', '', '', '', '', '']
        ]

        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('SPAN', (0, 0), (5, 0)), ('SPAN', (6, 0), (8, 0)),
            ('SPAN', (0, 1), (1, 1)), ('SPAN', (4, 1), (5, 1)), ('SPAN', (6, 1), (8, 1)),
            ('SPAN', (0, 2), (2, 2)), ('SPAN', (3, 2), (4, 2)), ('SPAN', (5, 2), (8, 2)),
            ('SPAN', (0, 3), (1, 3)), ('SPAN', (2, 3), (4, 3)), ('SPAN', (5, 3), (8, 3)),
            ('SPAN', (0, 4), (1, 4)), ('SPAN', (2, 4), (3, 4)), ('SPAN', (4, 4), (8, 4)),
            ('SPAN', (0, 5), (1, 5)), ('SPAN', (2, 5), (3, 5)), ('SPAN', (4, 5), (8, 5)),
            ('SPAN', (0, 6), (8, 6)),
            ('SPAN', (0, 7), (1, 7)), ('SPAN', (2, 7), (3, 7)), ('SPAN', (4, 7), (8, 7)),
            ('SPAN', (0, 8), (1, 8)), ('SPAN', (2, 8), (3, 8)), ('SPAN', (4, 8), (8, 8)),
            ('SPAN', (0, 9), (1, 9)), ('SPAN', (2, 9), (8, 9)),
            ('SPAN', (0, 10), (1, 10)), ('SPAN', (2, 10), (8, 10)),
            ('SPAN', (0, 11), (8, 11)),
            ('SPAN', (0, 12), (2, 12)), ('SPAN', (3, 12), (8, 12)),
            ('SPAN', (0, 13), (8, 13)),
            ('SPAN', (0, 14), (8, 14)),
            ('SPAN', (0, 15), (8, 15)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]

        t = Table(cell_schema, colWidths=55, rowHeights=None, style=table_style)
        return t

    def create_sheet_ar(self):
        """Arabic version of the sheet"""
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.fontSize = 5
        styNormal.fontName = 'Cambria'
        styNormal.alignment = 2  # RIGHT for Arabic

        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.fontSize = 5
        styDescrizione.fontName = 'Cambria'
        styDescrizione.alignment = 2

        intestazione = Paragraph("<b>بطاقة الحيوانات الأثرية<br/>" + str(self.datestrfdate()) + "</b>", styNormal)

        home = os.environ['PYARCHINIT_HOME']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch

        sito = Paragraph("<b>الموقع</b><br/>" + str(self.sito), styNormal)
        area = Paragraph("<b>المنطقة</b><br/>" + str(self.area), styNormal)
        saggio = Paragraph("<b>المجس</b><br/>" + str(self.saggio), styNormal)
        us = Paragraph("<b>و.ط</b><br/>" + str(self.us), styNormal)
        datazione_us = Paragraph("<b>تأريخ و.ط</b><br/>" + str(self.datazione_us), styNormal)
        responsabile_scheda = Paragraph("<b>المسؤول</b><br/>" + str(self.responsabile_scheda), styNormal)
        data_compilazione = Paragraph("<b>تاريخ التجميع</b><br/>" + str(self.data_compilazione), styNormal)
        documentazione_fotografica = Paragraph("<b>التوثيق الفوتوغرافي</b><br/>" + str(self.documentazione_fotografica), styNormal)
        metodologia_recupero = Paragraph("<b>طريقة الاسترداد</b><br/>" + str(self.metodologia_recupero), styNormal)
        contesto = Paragraph("<b>السياق</b><br/>" + str(self.contesto), styNormal)
        descrizione_contesto = Paragraph("<b>وصف السياق</b><br/>" + str(self.descrizione_contesto), styDescrizione)
        resti_connessione = Paragraph("<b>الاتصال التشريحي</b><br/>" + str(self.resti_connessione_anatomica), styNormal)
        tipologia_accumulo = Paragraph("<b>نوع التراكم</b><br/>" + str(self.tipologia_accumulo), styNormal)
        deposizione = Paragraph("<b>الترسيب</b><br/>" + str(self.deposizione), styNormal)
        numero_stimato = Paragraph("<b>العدد المقدر</b><br/>" + str(self.numero_stimato_resti), styNormal)
        nmi = Paragraph("<b>الحد الأدنى للأفراد</b><br/>" + str(self.numero_minimo_individui), styNormal)
        specie = Paragraph("<b>الأنواع</b><br/>" + str(self.specie), styDescrizione)
        parti_scheletriche = Paragraph("<b>عناصر الهيكل العظمي</b><br/>" + str(self.parti_scheletriche), styDescrizione)
        specie_psi = Paragraph("<b>أنواع PSI</b><br/>" + str(self.specie_psi), styNormal)
        misure_ossa = Paragraph("<b>قياسات العظام</b><br/>" + str(self.misure_ossa), styNormal)
        stato_frammentazione = Paragraph("<b>التجزئة</b><br/>" + str(self.stato_frammentazione), styNormal)
        tracce_combustione = Paragraph("<b>آثار الاحتراق</b><br/>" + str(self.tracce_combustione), styNormal)
        combustione_altri = Paragraph("<b>مواد محترقة أخرى</b><br/>" + ("نعم" if self.combustione_altri_materiali_us else "لا"), styNormal)
        tipo_combustione = Paragraph("<b>نوع الاحتراق</b><br/>" + str(self.tipo_combustione), styNormal)
        segni_tafonomici = Paragraph("<b>علامات التافونومية</b><br/>" + str(self.segni_tafonomici_evidenti), styNormal)
        caratterizzazione_tafo = Paragraph("<b>وصف التافونومية</b><br/>" + str(self.caratterizzazione_segni_tafonomici), styDescrizione)
        stato_conservazione = Paragraph("<b>حالة الحفظ</b><br/>" + str(self.stato_conservazione), styNormal)
        alterazioni = Paragraph("<b>التغيرات المورفولوجية</b><br/>" + str(self.alterazioni_morfologiche), styNormal)
        note_terreno = Paragraph("<b>ملاحظات الموقع</b><br/>" + str(self.note_terreno_giacitura), styDescrizione)
        campionature = Paragraph("<b>أخذ العينات</b><br/>" + str(self.campionature_effettuate), styNormal)
        affidabilita = Paragraph("<b>الموثوقية الطبقية</b><br/>" + str(self.affidabilita_stratigrafica), styNormal)
        classi_reperti = Paragraph("<b>اللقى المرتبطة</b><br/>" + str(self.classi_reperti_associazione), styDescrizione)
        osservazioni = Paragraph("<b>الملاحظات</b><br/>" + str(self.osservazioni), styDescrizione)
        interpretazione = Paragraph("<b>التفسير</b><br/>" + str(self.interpretazione), styDescrizione)

        cell_schema = [
            [intestazione, '', '', '', '', '', logo, '', ''],
            [sito, '', area, saggio, us, '', datazione_us, '', ''],
            [responsabile_scheda, '', '', data_compilazione, '', documentazione_fotografica, '', '', ''],
            [metodologia_recupero, '', contesto, '', '', descrizione_contesto, '', '', ''],
            [resti_connessione, '', tipologia_accumulo, '', deposizione, '', '', '', ''],
            [numero_stimato, '', nmi, '', specie, '', '', '', ''],
            [parti_scheletriche, '', '', '', '', '', '', '', ''],
            [specie_psi, '', misure_ossa, '', stato_frammentazione, '', '', '', ''],
            [tracce_combustione, '', combustione_altri, '', tipo_combustione, '', '', '', ''],
            [segni_tafonomici, '', caratterizzazione_tafo, '', '', '', '', '', ''],
            [stato_conservazione, '', alterazioni, '', '', '', '', '', ''],
            [note_terreno, '', '', '', '', '', '', '', ''],
            [campionature, '', '', affidabilita, '', '', '', '', ''],
            [classi_reperti, '', '', '', '', '', '', '', ''],
            [osservazioni, '', '', '', '', '', '', '', ''],
            [interpretazione, '', '', '', '', '', '', '', '']
        ]

        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('SPAN', (0, 0), (5, 0)), ('SPAN', (6, 0), (8, 0)),
            ('SPAN', (0, 1), (1, 1)), ('SPAN', (4, 1), (5, 1)), ('SPAN', (6, 1), (8, 1)),
            ('SPAN', (0, 2), (2, 2)), ('SPAN', (3, 2), (4, 2)), ('SPAN', (5, 2), (8, 2)),
            ('SPAN', (0, 3), (1, 3)), ('SPAN', (2, 3), (4, 3)), ('SPAN', (5, 3), (8, 3)),
            ('SPAN', (0, 4), (1, 4)), ('SPAN', (2, 4), (3, 4)), ('SPAN', (4, 4), (8, 4)),
            ('SPAN', (0, 5), (1, 5)), ('SPAN', (2, 5), (3, 5)), ('SPAN', (4, 5), (8, 5)),
            ('SPAN', (0, 6), (8, 6)),
            ('SPAN', (0, 7), (1, 7)), ('SPAN', (2, 7), (3, 7)), ('SPAN', (4, 7), (8, 7)),
            ('SPAN', (0, 8), (1, 8)), ('SPAN', (2, 8), (3, 8)), ('SPAN', (4, 8), (8, 8)),
            ('SPAN', (0, 9), (1, 9)), ('SPAN', (2, 9), (8, 9)),
            ('SPAN', (0, 10), (1, 10)), ('SPAN', (2, 10), (8, 10)),
            ('SPAN', (0, 11), (8, 11)),
            ('SPAN', (0, 12), (2, 12)), ('SPAN', (3, 12), (8, 12)),
            ('SPAN', (0, 13), (8, 13)),
            ('SPAN', (0, 14), (8, 14)),
            ('SPAN', (0, 15), (8, 15)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]

        t = Table(cell_schema, colWidths=55, rowHeights=None, style=table_style)
        return t

    def create_sheet_ca(self):
        """Catalan version of the sheet"""
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styNormal.spaceBefore = 20
        styNormal.spaceAfter = 20
        styNormal.fontSize = 5
        styNormal.fontName = 'Cambria'
        styNormal.alignment = 0

        styleSheet = getSampleStyleSheet()
        styDescrizione = styleSheet['Normal']
        styDescrizione.spaceBefore = 20
        styDescrizione.spaceAfter = 20
        styDescrizione.fontSize = 5
        styDescrizione.fontName = 'Cambria'
        styDescrizione.alignment = 4

        intestazione = Paragraph("<b>FITXA DE FAUNA ARQUEOL&Ograve;GICA<br/>" + str(self.datestrfdate()) + "</b>", styNormal)

        home = os.environ['PYARCHINIT_HOME']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path)
        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch

        sito = Paragraph("<b>JACIMENT</b><br/>" + str(self.sito), styNormal)
        area = Paragraph("<b>&Agrave;REA</b><br/>" + str(self.area), styNormal)
        saggio = Paragraph("<b>SONDEIG</b><br/>" + str(self.saggio), styNormal)
        us = Paragraph("<b>UE</b><br/>" + str(self.us), styNormal)
        datazione_us = Paragraph("<b>DATACI&Oacute; UE</b><br/>" + str(self.datazione_us), styNormal)
        responsabile_scheda = Paragraph("<b>RESPONSABLE</b><br/>" + str(self.responsabile_scheda), styNormal)
        data_compilazione = Paragraph("<b>DATA COMPILACI&Oacute;</b><br/>" + str(self.data_compilazione), styNormal)
        documentazione_fotografica = Paragraph("<b>DOC. FOTOGR&Agrave;FICA</b><br/>" + str(self.documentazione_fotografica), styNormal)
        metodologia_recupero = Paragraph("<b>M&Egrave;TODE RECUPERACI&Oacute;</b><br/>" + str(self.metodologia_recupero), styNormal)
        contesto = Paragraph("<b>CONTEXT</b><br/>" + str(self.contesto), styNormal)
        descrizione_contesto = Paragraph("<b>DESCRIPCI&Oacute; CONTEXT</b><br/>" + str(self.descrizione_contesto), styDescrizione)
        resti_connessione = Paragraph("<b>CONNEXI&Oacute; ANAT&Ograve;MICA</b><br/>" + str(self.resti_connessione_anatomica), styNormal)
        tipologia_accumulo = Paragraph("<b>TIPUS ACUMULACI&Oacute;</b><br/>" + str(self.tipologia_accumulo), styNormal)
        deposizione = Paragraph("<b>DEPOSICI&Oacute;</b><br/>" + str(self.deposizione), styNormal)
        numero_stimato = Paragraph("<b>NOMBRE ESTIMAT</b><br/>" + str(self.numero_stimato_resti), styNormal)
        nmi = Paragraph("<b>NMI</b><br/>" + str(self.numero_minimo_individui), styNormal)
        specie = Paragraph("<b>ESP&Egrave;CIE</b><br/>" + str(self.specie), styDescrizione)
        parti_scheletriche = Paragraph("<b>ELEMENTS ESQUEL&Egrave;TICS</b><br/>" + str(self.parti_scheletriche), styDescrizione)
        specie_psi = Paragraph("<b>ESP&Egrave;CIE PSI</b><br/>" + str(self.specie_psi), styNormal)
        misure_ossa = Paragraph("<b>MESURES &Ograve;SSIES</b><br/>" + str(self.misure_ossa), styNormal)
        stato_frammentazione = Paragraph("<b>FRAGMENTACI&Oacute;</b><br/>" + str(self.stato_frammentazione), styNormal)
        tracce_combustione = Paragraph("<b>TRACES DE COMBUSTI&Oacute;</b><br/>" + str(self.tracce_combustione), styNormal)
        combustione_altri = Paragraph("<b>ALTRES MAT. CREMATS</b><br/>" + ("S&iacute;" if self.combustione_altri_materiali_us else "No"), styNormal)
        tipo_combustione = Paragraph("<b>TIPUS COMBUSTI&Oacute;</b><br/>" + str(self.tipo_combustione), styNormal)
        segni_tafonomici = Paragraph("<b>SENYALS TAFON&Ograve;MIQUES</b><br/>" + str(self.segni_tafonomici_evidenti), styNormal)
        caratterizzazione_tafo = Paragraph("<b>CARACT. TAFON&Ograve;MICA</b><br/>" + str(self.caratterizzazione_segni_tafonomici), styDescrizione)
        stato_conservazione = Paragraph("<b>ESTAT CONSERVACI&Oacute;</b><br/>" + str(self.stato_conservazione), styNormal)
        alterazioni = Paragraph("<b>ALTERACIONS MORF.</b><br/>" + str(self.alterazioni_morfologiche), styNormal)
        note_terreno = Paragraph("<b>NOTES POSICI&Oacute;</b><br/>" + str(self.note_terreno_giacitura), styDescrizione)
        campionature = Paragraph("<b>MOSTREIGS</b><br/>" + str(self.campionature_effettuate), styNormal)
        affidabilita = Paragraph("<b>FIABILITAT ESTRAT.</b><br/>" + str(self.affidabilita_stratigrafica), styNormal)
        classi_reperti = Paragraph("<b>MATERIALS ASSOCIATS</b><br/>" + str(self.classi_reperti_associazione), styDescrizione)
        osservazioni = Paragraph("<b>OBSERVACIONS</b><br/>" + str(self.osservazioni), styDescrizione)
        interpretazione = Paragraph("<b>INTERPRETACI&Oacute;</b><br/>" + str(self.interpretazione), styDescrizione)

        cell_schema = [
            [intestazione, '', '', '', '', '', logo, '', ''],
            [sito, '', area, saggio, us, '', datazione_us, '', ''],
            [responsabile_scheda, '', '', data_compilazione, '', documentazione_fotografica, '', '', ''],
            [metodologia_recupero, '', contesto, '', '', descrizione_contesto, '', '', ''],
            [resti_connessione, '', tipologia_accumulo, '', deposizione, '', '', '', ''],
            [numero_stimato, '', nmi, '', specie, '', '', '', ''],
            [parti_scheletriche, '', '', '', '', '', '', '', ''],
            [specie_psi, '', misure_ossa, '', stato_frammentazione, '', '', '', ''],
            [tracce_combustione, '', combustione_altri, '', tipo_combustione, '', '', '', ''],
            [segni_tafonomici, '', caratterizzazione_tafo, '', '', '', '', '', ''],
            [stato_conservazione, '', alterazioni, '', '', '', '', '', ''],
            [note_terreno, '', '', '', '', '', '', '', ''],
            [campionature, '', '', affidabilita, '', '', '', '', ''],
            [classi_reperti, '', '', '', '', '', '', '', ''],
            [osservazioni, '', '', '', '', '', '', '', ''],
            [interpretazione, '', '', '', '', '', '', '', '']
        ]

        table_style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('SPAN', (0, 0), (5, 0)), ('SPAN', (6, 0), (8, 0)),
            ('SPAN', (0, 1), (1, 1)), ('SPAN', (4, 1), (5, 1)), ('SPAN', (6, 1), (8, 1)),
            ('SPAN', (0, 2), (2, 2)), ('SPAN', (3, 2), (4, 2)), ('SPAN', (5, 2), (8, 2)),
            ('SPAN', (0, 3), (1, 3)), ('SPAN', (2, 3), (4, 3)), ('SPAN', (5, 3), (8, 3)),
            ('SPAN', (0, 4), (1, 4)), ('SPAN', (2, 4), (3, 4)), ('SPAN', (4, 4), (8, 4)),
            ('SPAN', (0, 5), (1, 5)), ('SPAN', (2, 5), (3, 5)), ('SPAN', (4, 5), (8, 5)),
            ('SPAN', (0, 6), (8, 6)),
            ('SPAN', (0, 7), (1, 7)), ('SPAN', (2, 7), (3, 7)), ('SPAN', (4, 7), (8, 7)),
            ('SPAN', (0, 8), (1, 8)), ('SPAN', (2, 8), (3, 8)), ('SPAN', (4, 8), (8, 8)),
            ('SPAN', (0, 9), (1, 9)), ('SPAN', (2, 9), (8, 9)),
            ('SPAN', (0, 10), (1, 10)), ('SPAN', (2, 10), (8, 10)),
            ('SPAN', (0, 11), (8, 11)),
            ('SPAN', (0, 12), (2, 12)), ('SPAN', (3, 12), (8, 12)),
            ('SPAN', (0, 13), (8, 13)),
            ('SPAN', (0, 14), (8, 14)),
            ('SPAN', (0, 15), (8, 15)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]

        t = Table(cell_schema, colWidths=55, rowHeights=None, style=table_style)
        return t


class generate_fauna_pdf(object):
    """
    Main PDF generator class for Fauna records.
    Generates both individual sheets and index lists.
    """

    HOME = os.environ['PYARCHINIT_HOME']

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def build_Fauna_sheets(self, records):
        """Build PDF sheets in Italian"""
        home = self.HOME
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_PDF_folder')
        filename = '{}{}{}'.format(home_DB_path, os.sep, 'scheda_Fauna.pdf')

        f = open(filename, "wb")
        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.pagesize = A4

        story = []
        for i in range(len(records)):
            single_fauna_sheet = single_Fauna_pdf_sheet(records[i])
            story.append(single_fauna_sheet.create_sheet())
            story.append(PageBreak())

        doc.build(story, canvasmaker=NumberedCanvas_Faunasheet)
        f.close()

    def build_Fauna_sheets_de(self, records):
        """Build PDF sheets in German"""
        home = self.HOME
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_PDF_folder')
        filename = '{}{}{}'.format(home_DB_path, os.sep, 'Fauna_formular.pdf')

        f = open(filename, "wb")
        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.pagesize = A4

        story = []
        for i in range(len(records)):
            single_fauna_sheet = single_Fauna_pdf_sheet(records[i])
            story.append(single_fauna_sheet.create_sheet_de())
            story.append(PageBreak())

        doc.build(story, canvasmaker=NumberedCanvas_Faunasheet)
        f.close()

    def build_Fauna_sheets_en(self, records):
        """Build PDF sheets in English"""
        home = self.HOME
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_PDF_folder')
        filename = '{}{}{}'.format(home_DB_path, os.sep, 'Fauna_record.pdf')

        f = open(filename, "wb")
        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.pagesize = A4

        story = []
        for i in range(len(records)):
            single_fauna_sheet = single_Fauna_pdf_sheet(records[i])
            story.append(single_fauna_sheet.create_sheet_en())
            story.append(PageBreak())

        doc.build(story, canvasmaker=NumberedCanvas_Faunasheet)
        f.close()

    def build_Fauna_sheets_fr(self, records):
        """Build PDF sheets in French"""
        home = self.HOME
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_PDF_folder')
        filename = '{}{}{}'.format(home_DB_path, os.sep, 'fiche_Faune.pdf')

        f = open(filename, "wb")
        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.pagesize = A4

        story = []
        for i in range(len(records)):
            single_fauna_sheet = single_Fauna_pdf_sheet(records[i])
            story.append(single_fauna_sheet.create_sheet_fr())
            story.append(PageBreak())

        doc.build(story, canvasmaker=NumberedCanvas_Faunasheet)
        f.close()

    def build_Fauna_sheets_es(self, records):
        """Build PDF sheets in Spanish"""
        home = self.HOME
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_PDF_folder')
        filename = '{}{}{}'.format(home_DB_path, os.sep, 'ficha_Fauna.pdf')

        f = open(filename, "wb")
        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.pagesize = A4

        story = []
        for i in range(len(records)):
            single_fauna_sheet = single_Fauna_pdf_sheet(records[i])
            story.append(single_fauna_sheet.create_sheet_es())
            story.append(PageBreak())

        doc.build(story, canvasmaker=NumberedCanvas_Faunasheet)
        f.close()

    def build_Fauna_sheets_ar(self, records):
        """Build PDF sheets in Arabic"""
        home = self.HOME
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_PDF_folder')
        filename = '{}{}{}'.format(home_DB_path, os.sep, 'fauna_bitaqa.pdf')

        f = open(filename, "wb")
        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.pagesize = A4

        story = []
        for i in range(len(records)):
            single_fauna_sheet = single_Fauna_pdf_sheet(records[i])
            story.append(single_fauna_sheet.create_sheet_ar())
            story.append(PageBreak())

        doc.build(story, canvasmaker=NumberedCanvas_Faunasheet)
        f.close()

    def build_Fauna_sheets_ca(self, records):
        """Build PDF sheets in Catalan"""
        home = self.HOME
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_PDF_folder')
        filename = '{}{}{}'.format(home_DB_path, os.sep, 'fitxa_Fauna.pdf')

        f = open(filename, "wb")
        doc = SimpleDocTemplate(f, pagesize=A4)
        doc.pagesize = A4

        story = []
        for i in range(len(records)):
            single_fauna_sheet = single_Fauna_pdf_sheet(records[i])
            story.append(single_fauna_sheet.create_sheet_ca())
            story.append(PageBreak())

        doc.build(story, canvasmaker=NumberedCanvas_Faunasheet)
        f.close()
