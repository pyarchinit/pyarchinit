#! /usr/bin/env python
# -*- coding: utf 8 -*-
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
 *                                                                          *
 *   This program is free software; you can redistribute it and/or modify   *
 *   it under the terms of the GNU General Public License as published by   *
 *   the Free Software Foundation; either version 2 of the License, or      *
 *   (at your option) any later version.                                    *                                                                       *
 ***************************************************************************/
"""

from builtins import str
from builtins import range
from builtins import object
import time
import os

from ..db.pyarchinit_conn_strings import Connection
from ..db.pyarchinit_db_manager import Pyarchinit_db_management
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, PageBreak, SimpleDocTemplate, Spacer, TableStyle, Image
from reportlab.platypus.paragraph import Paragraph

from .pyarchinit_OS_utility import *
from reportlab.rl_config import defaultPageSize


##############################################################
#####MODELLO RELAZIONE
##### PROBLEMATICA AREE DIFFERENTI
#####Sezione 1 - COPERTINA
####    In altro al centro il logo
####    Titolo
####    Immagine che definisce lo scavo
####    in fondo mese anno
##
###Sezione 2 - SITO
####Dati del sito: nome,comune, provincia, regione, nazione
##
###Sezione 3 - PERIODI
####Dati dei periodi
######Elenco periodi Periodo - Fase - Datazione estesa
######Singoli periodi con descrizione
###Sezione 4 - Strutture
####Dati delle strutture
######Elenco Strutture - Sigla - Numero - Periodo - Fase
######Singolie strutture con descrizione
###Sezione 5 - DATI DI CANTIERE
####Dati di cantiere
######Elenco periodi Periodo - Fase - Datazione estesa
###Sezione 6 - ALLEGATO 1 - schede US
####Dati dei periodi
######Elenco periodi Periodo - Fase - Datazione estesa

class NumberedCanvas_Relazione(canvas.Canvas):
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
        for state in range(len(self._saved_page_states)):
            self.__dict__.update(self._saved_page_states[state])
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        if self._pageNumber == 1:
            pass
        else:
            logo = os.path.join(os.path.dirname(__file__), "..", "..", "iconadarte.png")
            self.drawInlineImage(logo, 250, 780, width=120, height=40)
            self.line(35, 775, 550, 775)
            self.line(35, 40, 550, 40)
            self.setFont("Helvetica", 8)
            self.drawRightString(548, 45, "pag. %d" % (self._pageNumber - 1))  # scheda us verticale 200mm x 20 mm
            self.drawCentredString(300, 20, "adArte srl Archeologia, Restauro, ICT")
            self.drawCentredString(300, 10, "Piazzetta Plebiscito 7, 47921 Rimini (RN)")


class exp_rel_pdf(object):
    DB_MANAGER = ""
    DATA_LIST = []
    SITO = ""

    HOME = os.environ['PYARCHINIT_HOME']

    PDF_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")
    Title = ""
    pageinfo = "adArte srl"

    PAGE_HEIGHT = defaultPageSize[1]
    PAGE_WIDTH = defaultPageSize[0]
    styles = getSampleStyleSheet()

    def __init__(self, sito):
        self.SITO = sito
        self.connection_db()

    def connection_db(self):
        conn = Connection()
        conn_str = conn.conn_str()
        try:
            self.DB_MANAGER = Pyarchinit_db_management(conn_str)
            self.DB_MANAGER.connection()
        except Exception as e:
            QMessageBox.warning(self, "Alert", "La connessione e' fallita", QMessageBox.Ok)

    def search_records(self, f, v, m):
        self.field = f
        self.value = v
        self.mapper_table_class = m
        search_dict = {self.field: "'" + str(self.value) + "'"}
        res = self.DB_MANAGER.query_bool(search_dict, self.mapper_table_class)
        print(res)
        return res

    def extract_id_list(self, rec, idf):
        self.rec = rec
        self.id_field = idf
        id_list = []
        for sing_rec in range(len(self.rec)):
            text_cmd = ("self.rec[sing_rec].%s") % (self.id_field)
            id_list.append(eval(text_cmd))

        return id_list

    def load_data_sorted(self, id_list, sort_fields_list, sort_mode, mapper_table_class, id_table):
        self.id_list = id_list
        self.sort_fields_list = sort_fields_list
        self.sort_mode = sort_mode
        self.mapper_table_class = mapper_table_class
        self.id_table = id_table

        temp_data_list = self.DB_MANAGER.query_sort(self.id_list, self.sort_fields_list, self.sort_mode,
                                                    self.mapper_table_class, self.id_table)

        for i in temp_data_list:
            self.DATA_LIST.append(i)

        ############################
        ######Sezione di esportazione PDF#####
        ############################

    def myFirstPage(self, canvas, doc):
       
        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path, 100, 100 )

        ##      if test_image.drawWidth < 800:

        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch
        
        canvas.saveState()
        canvas.setFont('Times-Bold', 16)
        canvas.drawCentredString(self.PAGE_WIDTH / 2.0, self.PAGE_HEIGHT - 108, str(self.SITO).replace("_",' '))
        canvas.setFont('Cambria', 9)
        canvas.drawString(inch, 0.75 * inch, "First Page / %s" % self.pageinfo)
        canvas.restoreState()

    def export_rel_pdf(self):
        Story = []
        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path)

        ##      if test_image.drawWidth < 800:

        logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
        logo.drawWidth = 1.5 * inch
        magName = "Pythonista"
        subPrice = "99.00"
        limitedDate = "03/05/2010"
        freeGift = "tin foil hat"

        # DATI INTESTAZIONE
        formatted_time = time.ctime()
        full_name = "Responsabile: Luca Mandolesi"
        address_parts = ["Sito: Via Cavour 60, Ravenna", "Indirizzo: Via Cavour 60", "Comune: Ravenna"]

        Story.append(PageBreak())
        #im = Image(logo)
        Story.append(logo)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, bulletText='-'))

        ptext = '<font size=12>%s</font>' % formatted_time
        Story.append(Paragraph(ptext, styles["Normal"]))
        Story.append(Spacer(1, 12))

        # Create return address
        ptext = '<font size=12>%s</font>' % full_name
        Story.append(Paragraph(ptext, styles["Normal"]))

        for part in address_parts:
            ptext = '<font size=12>%s</font>' % part.strip()
            Story.append(Paragraph(ptext, styles["Normal"]))
        Story.append(Spacer(1, 12))
        ptext = '<font size=12>Dear %s:</font>' % full_name.split()[0].strip()
        Story.append(Paragraph(ptext, styles["Normal"]))
        Story.append(Spacer(1, 12))

        Story.append(PageBreak())

        ###Sezione 2 - SITO
        # Titolo descrizione sito

        # funzioni di ricerca
        search_dict = {'sito': "'" + str(self.SITO) + "'"}
        self.DATA_LIST = self.DB_MANAGER.query_bool(search_dict, "SITE")

        # formattazione del testo
        ptext = '<font size=14><b>Sito: %s</b></font>' % self.DATA_LIST[0].sito

        Story.append(Paragraph(ptext, styles["Normal"]))
        Story.append(Spacer(1, 12))
        # Descrizione sito
        ptext = '<font size=12> <b>Descrizione del sito </b><br/> %s </font>'% self.DATA_LIST[0].descrizione
        Story.append(Paragraph(ptext, styles["Justify"]))
        Story.append(Spacer(1, 12))

        # Titolo descrizione periodo
        # cerca se e' presente una scansione cronologica del sito
        self.DATA_LIST = []
        periodizzazione_records = self.search_records('sito', self.SITO, 'PERIODIZZAZIONE')
        if bool(periodizzazione_records):
            Story.append(PageBreak())
            # crea l'intestazione della Periodizzazione
            ptext = '<font size=16 ><b>Periodizzazione di scavo</b><br/><br/></font>'
            Story.append(Paragraph(ptext, styles["Normal"]))
            Story.append(Spacer(1, 12))
            # estrae gli id dai record
            id_list_periodo = self.extract_id_list(periodizzazione_records, 'id_perfas')
            # carica i record di periodo ordinati in base al codice di periodo
            self.load_data_sorted(id_list_periodo, ['cont_per'], 'asc', 'PERIODIZZAZIONE', 'id_perfas')

            for sing_rec in range(len(self.DATA_LIST)):
                ptext = '<font size=12 ><b>Periodo: %s - Fase %s - Datazione estesa: %s</b></font><br/>' % (
                self.DATA_LIST[sing_rec].periodo, self.DATA_LIST[sing_rec].fase,
                self.DATA_LIST[sing_rec].datazione_estesa)
                Story.append(Paragraph(ptext, styles["Normal"]))
                Story.append(Spacer(1, 12))

            Story.append(PageBreak())

            for sing_rec in range(len(self.DATA_LIST)):
                ptext = '<font size=12 ><b>Periodo: %s - Fase %s </b></font><br/>' % (
                self.DATA_LIST[sing_rec].periodo, self.DATA_LIST[sing_rec].fase)
                Story.append(Paragraph(ptext, styles["Normal"]))
                Story.append(Spacer(1, 12))

                # Descrizione periodo
                ptext = '<font size=12> %s </font><br/><br/>' % (self.DATA_LIST[sing_rec].descrizione)
                Story.append(Paragraph(ptext, styles["Justify"]))
                Story.append(Spacer(1, 12))

                # Titolo descrizione struttura
                # cerca se sono presenti strutture
        self.DATA_LIST = []
        strutture_records = self.search_records('sito', self.SITO, 'STRUTTURA')
        if bool(strutture_records):
            Story.append(PageBreak())
            # crea l'intestazione delle Strutture
            ptext = '<font size=16 ><b>Strutture di scavo</b><br/><br/></font>'
            Story.append(Paragraph(ptext, styles["Normal"]))
            Story.append(Spacer(1, 12))
            # estrae gli id dai record
            id_list_strutture = self.extract_id_list(strutture_records, 'id_struttura')

            # carica i record di struttura ordinati in base alla sigla struttura e il suo numero
            self.load_data_sorted(id_list_strutture, ['sigla_struttura', 'numero_struttura'], 'asc', 'STRUTTURA',
                                  'id_struttura')

            # crea l'intestazione dell'elenco delle sigle struttura presenti nel DB
            ptext = '<font size=16 >Elenco Strutture<br/></font>'
            Story.append(Paragraph(ptext, styles["Normal"]))
            Story.append(Spacer(1, 12))

            # Viene stampata la prima sigla di struttura
            rec_sigla_struttura = self.search_records('sigla', self.DATA_LIST[0].sigla_struttura,
                                                      'PYARCHINIT_THESAURUS_SIGLE')
            sigla_temp = self.DATA_LIST[0].sigla_struttura
            ptext = '<font size=14 ><b>Sigla: %s - Tipologia: %s</b><br/></font>' % (
            sigla_temp, rec_sigla_struttura[0].sigla_estesa)
            Story.append(Paragraph(ptext, styles["Normal"]))
            Story.append(Spacer(1, 12))
            #ptext = '<bullet>'
            #Story.append(Paragraph(ptext, styles["Normal"],bulletText='-'))

            # crea l'elenco delle sigle struttura presenti nel DB
            for rec in range(len(self.DATA_LIST)):
                if sigla_temp == self.DATA_LIST[rec].sigla_struttura:
                    rec_sigla_struttura = self.search_records('sigla', self.DATA_LIST[rec].sigla_struttura,
                                                              'PYARCHINIT_THESAURUS_SIGLE')
                    ptext = '<font size=12 ><b> Sigla: %s%s - Tipologia: %s </b></font>' % (
                    self.DATA_LIST[rec].sigla_struttura, str(self.DATA_LIST[rec].numero_struttura),
                    rec_sigla_struttura[0].sigla_estesa)
                    Story.append(Paragraph(ptext, styles["Normal"], bulletText='-'))
                    Story.append(Spacer(1, 12))
                    ptext = '<font size=12 > - Periodo: %s - Fase: %s<br/><br/></font>' % (
                    str(self.DATA_LIST[rec].periodo_iniziale), str(self.DATA_LIST[rec].fase_iniziale))
                    Story.append(Paragraph(ptext, styles["Normal"], bulletText='   '))
                    Story.append(Spacer(1, 12))
                else:
                    #ptext = '<bullet>'
                    #Story.append(Paragraph(ptext, styles["Normal"], bulletText='-'))
                    rec_sigla_struttura = self.search_records('sigla', self.DATA_LIST[rec].sigla_struttura,
                                                              'PYARCHINIT_THESAURUS_SIGLE')
                    sigla_temp = self.DATA_LIST[rec].sigla_struttura
                    ptext = '<font size=14 ><b>Sigla: %s - Tipologia: %s</b><br/></font>' % (
                    sigla_temp, rec_sigla_struttura[0].sigla_estesa)
                    Story.append(Paragraph(ptext, styles["Normal"]))
                    Story.append(Spacer(1, 12))
                    ptext = '<bullet>'
                    Story.append(Paragraph(ptext, styles["Normal"]))
                    ptext = '<font size=12 ><b>Sigla: %s - Tipologia: %s </b></font>' % (
                    self.DATA_LIST[rec].sigla_struttura, str(self.DATA_LIST[rec].numero_struttura),
                    rec_sigla_struttura[0].sigla_estesa)
                    Story.append(Paragraph(ptext, styles["Normal"], bulletText='-'))
                    Story.append(Spacer(1, 12))
                    ptext = '<font size=12 > - Periodo: %s - Fase: %s<br/><br/></font>' % (
                    str(self.DATA_LIST[rec].periodo_iniziale), str(self.DATA_LIST[rec].fase_iniziale))
                    Story.append(Paragraph(ptext, styles["Normal"], bulletText='   '))
                    Story.append(Spacer(1, 12))
            #ptext = '</bullet>'
            #Story.append(Paragraph(ptext, styles["Normal"]))

            # crea la descrizione e interpretazione delle singole strutture presenti nel DB
            ptext = '<font size=16 ><b>Descrizione singole strutture</b><br/></font>'
            Story.append(Paragraph(ptext, styles["Normal"]))
            Story.append(Spacer(1, 12))
            for rec in range(len(self.DATA_LIST)):
                rec_sigla_struttura = self.search_records('sigla', self.DATA_LIST[rec].sigla_struttura,
                                                          'PYARCHINIT_THESAURUS_SIGLE')
                ptext = '<font size=14 ><b>Sigla: %s%s - Tipologia: %s </b><br/><br/></font>' % (
                self.DATA_LIST[rec].sigla_struttura, str(self.DATA_LIST[rec].numero_struttura),
                rec_sigla_struttura[0].sigla_estesa)
                Story.append(Paragraph(ptext, styles["Normal"]))
                ptext = '<font size=12 ><b>Descrizione</b><br/>%s<br/><b>Intepretazione</b><br/>%s<br/></font>' % (
                str(self.DATA_LIST[rec].descrizione), str(self.DATA_LIST[rec].interpretazione))
                Story.append(Paragraph(ptext, styles["Normal"]))
                Story.append(Spacer(1, 12))
        Story.append(PageBreak())

        # Titolo dati di cantiere
        ptext = '<font size=14 ><b>Dati Cantiere</b></font>'

        Story.append(Paragraph(ptext, styles["Normal"]))
        Story.append(Spacer(1, 12))

        # Descrizione dati di scavo
        ptext = """<font size=12>Direttore Cantiere: Fox Molder</font>"""  # % (magName, issueNum,subPrice,limitedDate,freeGift)
        Story.append(Paragraph(ptext, styles["Justify"]))
        Story.append(Spacer(1, 12))
        Story.append(PageBreak())

        # Titolo Catalogo Immagini 1
        styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
        ptext = '<font size=36><b>Catalogo Immagini</b></font>'

        Story.append(Paragraph(ptext, styles["Center"]))
        Story.append(Spacer(1, 20))
        Story.append(PageBreak())

        # Immagini
        home = os.environ['PYARCHINIT_HOME']

        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        logo = Image(logo_path)
        #logo = os.path.join(os.path.dirname(__file__), "..", "..", "iconadarte.png")
        #im = Image(logo)
        Story.append(logo)
        # Didascalia
        ptext = '<font size=10><b>Figura 1 - Esempio di foto</b></font>'

        Story.append(Paragraph(ptext, styles["Normal"]))
        Story.append(Spacer(1, 200))

        #logo = os.path.join(os.path.dirname(__file__), "..", "..", "iconadarte.png")
        #im = Image(logo)
        Story.append(logo)
        # Didascalia
        ptext = '<font size=10><b>Figura 2 - Esempio di foto</b></font>'

        Story.append(Paragraph(ptext, styles["Normal"]))
        Story.append(Spacer(1, 12))
        Story.append(PageBreak())

        # Titolo Allegato 1
        ptext = '<font size=36><b>Allegato 1</b></font>'

        Story.append(Paragraph(ptext, styles["Center"]))
        Story.append(Spacer(1, 20))

        # Titolo Allegato 1
        ptext = '<font size=36><b>Schede US</b></font>'

        Story.append(Paragraph(ptext, styles["Center"]))
        Story.append(Spacer(1, 50))

        # Chiusura del documento
       
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'relazione.pdf')
        f = open(filename, "wb")
        # doc = SimpleDocTemplate(f)
        # doc.build(elements, canvasmaker=NumberedCanvas_Periodizzazionesheet)


        doc = SimpleDocTemplate(f, pagesize=A4,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=40)
        doc.build(Story, canvasmaker=NumberedCanvas_Relazione, onFirstPage=self.myFirstPage)
        f.close()
