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

from datetime import date

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, PageBreak, SimpleDocTemplate, Image
from reportlab.platypus.paragraph import Paragraph

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
        self.setFont("Helvetica", 8)
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

        if os.name == 'posix':
            home = os.environ['HOME']
        elif os.name == 'nt':
            home = os.environ['HOMEPATH']

        home_DB_path = ('%s%s%s') % (home, os.sep, 'pyarchinit_DB_folder')
        alma_path = ('%s%s%s') % (home_DB_path, os.sep, 'alma.jpg')
        alma = Image(alma_path)

        ##		if test_image.drawWidth < 800:

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
            #					('VALIGN',(0,2),(9,2),'TOP'),

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
    if os.name == 'posix':
        HOME = os.environ['HOME']
    elif os.name == 'nt':
        HOME = os.environ['HOMEPATH']

    PDF_path = ('%s%s%s') % (HOME, os.sep, "pyarchinit_PDF_folder")

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
        filename = ('%s%s%s') % (self.PDF_path, os.sep, 'scheda_reperti_lapidei.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_Invlapsheet)
        f.close()

##class Box_labels_Finds_pdf_sheet:

##	def __init__(self, data, sito):
##		self.sito = sito #Sito
##		self.cassa= data[0] #1 - Cassa
##		self.elenco_inv_tip_rep = data[1] #2-  elenco US
##		self.elenco_us = data[2] #3 - elenco Inventari
##		self.luogo_conservazione = data[3]#4 - luogo conservazione
##
##	def datestrfdate(self):
##		now = date.today()
##		today = now.strftime("%d-%m-%Y")
##		return today

##	def create_sheet(self):
##		styleSheet = getSampleStyleSheet()
##		
##		styleSheet.add(ParagraphStyle(name='Cassa Label'))
##		styleSheet.add(ParagraphStyle(name='Sito Label'))
##
##		styCassaLabel = styleSheet['Cassa Label']
##		styCassaLabel.spaceBefore = 0
##		styCassaLabel.spaceAfter = 0
##		styCassaLabel.alignment = 2 #RIGHT
##		styCassaLabel.leading = 25
##		styCassaLabel.fontSize = 30
##
##		stySitoLabel = styleSheet['Sito Label']
##		stySitoLabel.spaceBefore = 0
##		stySitoLabel.spaceAfter = 0
##		stySitoLabel.alignment = 0 #LEFT
##		stySitoLabel.leading = 25
##		stySitoLabel.fontSize = 18
##		stySitoLabel.fontStyle = 'bold'
##
##		styNormal = styleSheet['Normal']
##		styNormal.spaceBefore = 10
##		styNormal.spaceAfter = 10
##		styNormal.alignment = 0 #LEFT
##		styNormal.fontSize = 14
##		styNormal.leading = 15
##
##
##		#format labels
##		if os.name == 'posix':
##			home = os.environ['HOME']
##		elif os.name == 'nt':
##			home = os.environ['HOMEPATH']
##
##		home_DB_path = ('%s%s%s') % (home, os.sep, 'pyarchinit_DB_folder')
##		logo_path = ('%s%s%s') % (home_DB_path, os.sep, 'logo.jpg')
##		logo = Image(logo_path)
##
##		##		if test_image.drawWidth < 800:
##
##		logo.drawHeight = 1.5*inch*logo.drawHeight / logo.drawWidth
##		logo.drawWidth = 1.5*inch
##		
##
##		num_cassa = Paragraph("<b>N. Cassa </b>" + str(self.cassa),styCassaLabel)
##		sito = Paragraph("<b>Sito: </b>" + str(self.sito),stySitoLabel)
##
##		if self.elenco_inv_tip_rep == None:
##			elenco_inv_tip_rep = Paragraph("<b>Elenco N. Inv. / Tipo materiale</b><br/>",styNormal)
##		else:
##			elenco_inv_tip_rep = Paragraph("<b>Elenco N. Inv. / Tipo materiale</b><br/>" + str(self.elenco_inv_tip_rep ),styNormal)
##
##		if self.elenco_us == None:
##			elenco_us = Paragraph("<b>Elenco US/(Struttura)</b>",styNormal)
##		else:
##			elenco_us = Paragraph("<b>Elenco US/(Struttura)</b><br/>" + str(self.elenco_us),styNormal)
##
##		#luogo_conservazione = Paragraph("<b>Luogo di conservazione</b><br/>" + str(self.luogo_conservazione),styNormal)
##
##		#schema
##		cell_schema =	[ #00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
##							[logo, '01', '02', '03', '04','05', num_cassa, '07', '08', '09'],
##							[sito, '01', '02', '03', '04','05', '06', '07', '08', '09'],
##							[elenco_us, '01', '02', '03','04', '05','06', '07', '08', '09'],
##							[elenco_inv_tip_rep, '01', '02','03', '04', '05','06', '07', '08', '09']
##
##						]
##
##
##
##		#table style
##		table_style=[
##
##					('GRID',(0,0),(-1,-1),0,colors.white),#,0.0,colors.black
##					#0 row
##					('SPAN', (0,0),(5,0)),  #elenco US
##					('SPAN', (6,0),(9,0)),  #elenco US
##					('HALIGN',(0,0),(9,0),'LEFT'),
##					('VALIGN',(6,0),(9,0),'TOP'),
##					('HALIGN',(6,0),(9,0),'RIGHT'),
##
##					('SPAN', (0,1),(9,1)),  #elenco US
##					('HALIGN',(0,1),(9,1),'LEFT'),
##
##					('SPAN', (0,2),(9,2)),  #intestazione
##					('VALIGN',(0,2),(9,2),'TOP'), 
##					#1 row
##					('SPAN', (0,3),(9,3)),  #elenco US
##					('VALIGN',(0,3),(9,3),'TOP')
##
##					]
##
##
##		colWidths=None
##		rowHeights=None
##		#colWidths=[80,80,80, 80,80, 80,80,80,80, 80]
##		t=Table(cell_schema,colWidths,rowHeights, style= table_style)
##
##		return t



##class CASSE_index_pdf_sheet:

##	def __init__(self, data):
##		self.cassa= data[0] #1 - Cassa
##		self.elenco_inv_tip_rep = data[1] #2-  elenco US
##		self.elenco_us = data[2] #3 - elenco Inventari
##		self.luogo_conservazione = data[3]#4 - luogo conservazione
##
##	def getTable(self):
##		styleSheet = getSampleStyleSheet()
##		styNormal = styleSheet['Normal']
##		styNormal.spaceBefore = 20
##		styNormal.spaceAfter = 20
##		styNormal.alignment = 0 #LEFT
##		styNormal.fontSize = 10
##
##		#self.unzip_rapporti_stratigrafici()
##
##		num_cassa = Paragraph("<b>Nr.</b><br/>" + str(self.cassa),styNormal)
##
##		if self.elenco_inv_tip_rep == None:
##			elenco_inv_tip_rep = Paragraph("<b>N. Inv./Tipo materiale</b><br/>",styNormal)
##		else:
##			elenco_inv_tip_rep = Paragraph("<b>N. Inv./Tipo materiale</b><br/>" + str(self.elenco_inv_tip_rep ),styNormal)
##
##		if self.elenco_us == None:
##			elenco_us = Paragraph("<b>US(Struttura)</b><br/>",styNormal)
##		else:
##			elenco_us = Paragraph("<b>US(Struttura)</b><br/>" + str(self.elenco_us),styNormal)
##
##		luogo_conservazione = Paragraph("<b>Luogo di conservazione</b><br/>" + str(self.luogo_conservazione),styNormal)
##
##		data = [num_cassa,
##					elenco_inv_tip_rep,
##					elenco_us,
##					luogo_conservazione]
##
##		return data
##
##	def makeStyles(self):
##		styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')])  #finale
##
##		return styles


####class FINDS_index_pdf_sheet:
##
##	def __init__(self, data):
##		self.sito = data[1]							#1 - sito
##		self.num_inventario = data[2]			 #2- numero_inventario
##		self.oggetto = data[3] 				#3 - oggetto
##		self.collocazione = data[4 ]		#4 - collocazione
##		self.tipologia = data[5 ]					#5 - definizione
##		self.area = data[7] 							# 7 - area
##		self.us = data[8] 							#8 - us
##		self.lavato = data[9] 						#9 - lavato
##		self.numero_cassa = data[10] 			#10 - numero cassa
##		self.repertato = data[21]					#22 - repertato
##		self.diagnostico = data[22]				#23 - diagnostico
##
##
##	def getTable(self):
##		styleSheet = getSampleStyleSheet()
##		styNormal = styleSheet['Normal']
##		styNormal.spaceBefore = 20
##		styNormal.spaceAfter = 20
##		styNormal.alignment = 0 #LEFT
##		styNormal.fontSize = 9
##
##		#self.unzip_rapporti_stratigrafici()
##
##		num_inventario = Paragraph("<b>N. Inv.</b><br/>" + str(self.num_inventario),styNormal)
##
##		if self.oggetto == None:
##			oggetto = Paragraph("<b>Tipo reperto</b><br/>",styNormal)
##		else:
##			oggetto = Paragraph("<b>Tipo reperto</b><br/>" + str(self.oggetto),styNormal)
##	
##		if self.collocazione == None:
##			classe_materiale = Paragraph("<b>Classe materiale</b><br/>",styNormal)
##		else:
##			classe_materiale = Paragraph("<b>Classe materiale</b><br/>" + str(self.collocazione),styNormal)
##
##		if self.definizione == None:
##			definizione = Paragraph("<b>Definizione</b><br/>" ,styNormal)
##		else:
##			definizione = Paragraph("<b>Definizione</b><br/>" + str(self.definizione),styNormal)
##
##		if str(self.area) == "None":
##			area = Paragraph("<b>Area</b><br/>",styNormal)
##		else:
##			area = Paragraph("<b>Area</b><br/>" + str(self.area),styNormal)
##
##		if str(self.us) == "None":
##			us = Paragraph("<b>US</b><br/>",styNormal)
##		else:
##			us = Paragraph("<b>US</b><br/>" + str(self.us),styNormal)
##
##		if self.lavato == None:
##			lavato = Paragraph("<b>Lavato</b><br/>",styNormal)
##		else:
##			lavato = Paragraph("<b>Lavato</b><br/>" + str(self.lavato),styNormal)
##
##		if self.repertato == None:
##			repertato = Paragraph("<b>Repertato</b><br/>",styNormal)
##		else:
##			repertato = Paragraph("<b>Repertato</b><br/>" + str(self.repertato),styNormal)
##
##		if self.diagnostico == None:
##			diagnostico = Paragraph("<b>Diagnostico</b><br/>",styNormal)
##		else:
##			diagnostico = Paragraph("<b>Diagnostico</b><br/>" + str(self.diagnostico),styNormal)
##
##		if str(self.numero_cassa) == "None":
##			nr_cassa = Paragraph("<b>Nr. Cassa</b><br/>",styNormal)
##		else:
##			nr_cassa = Paragraph("<b>Nr. Cassa</b><br/>" + str(self.numero_cassa),styNormal)
##
##
##		data = [num_inventario,
##				tipo_reperto,
##				classe_materiale,
##				definizione,
##				area,
##				us,
##				lavato,
##				repertato,
##				diagnostico,
##				nr_cassa]
##
##		return data
##
##	def makeStyles(self):
##		styles =TableStyle([('GRID',(0,0),(-1,-1),0.0,colors.black),('VALIGN', (0,0), (-1,-1), 'TOP')
##		])  #finale
##
##		return styles



##class NumberedCanvas_FINDSindex(canvas.Canvas):
##	def __init__(self, *args, **kwargs):
##		canvas.Canvas.__init__(self, *args, **kwargs)
##		self._saved_page_states = []
##
##	def define_position(self, pos):
##		self.page_position(pos)
##
##	def showPage(self):
##		self._saved_page_states.append(dict(self.__dict__))
##		self._startPage()
##
##	def save(self):
##		"""add page info to each page (page x of y)"""
##		num_pages = len(self._saved_page_states)
##		for state in self._saved_page_states:
##			self.__dict__.update(state)
##			self.draw_page_number(num_pages)
##			canvas.Canvas.showPage(self)
##		canvas.Canvas.save(self)
##
##	def draw_page_number(self, page_count):
##		self.setFont("Helvetica", 8)
##		self.drawRightString(270*mm, 10*mm, "Pag. %d di %d" % (self._pageNumber, page_count)) #scheda us verticale 200mm x 20 mm


##class NumberedCanvas_CASSEindex(canvas.Canvas):
##	def __init__(self, *args, **kwargs):
##		canvas.Canvas.__init__(self, *args, **kwargs)
##		self._saved_page_states = []
##
##	def define_position(self, pos):
##		self.page_position(pos)
##
##	def showPage(self):
##		self._saved_page_states.append(dict(self.__dict__))
##		self._startPage()
##
##	def save(self):
##		"""add page info to each page (page x of y)"""
##		num_pages = len(self._saved_page_states)
##		for state in self._saved_page_states:
##			self.__dict__.update(state)
##			self.draw_page_number(num_pages)
##			canvas.Canvas.showPage(self)
##		canvas.Canvas.save(self)
##
##	def draw_page_number(self, page_count):
##		self.setFont("Helvetica", 8)
##		self.drawRightString(270*mm, 10*mm, "Pag. %d di %d" % (self._pageNumber, page_count)) #scheda us verticale 200mm x 20 mm


##	def build_index_Invmat(self, records, sito):
##		if os.name == 'posix':
##			home = os.environ['HOME']
##		elif os.name == 'nt':
##			home = os.environ['HOMEPATH']
##
##		home_DB_path = ('%s%s%s') % (home, os.sep, 'pyarchinit_DB_folder')
##		logo_path = ('%s%s%s') % (home_DB_path, os.sep, 'logo.jpg')
##
##		logo = Image(logo_path)
##		logo.drawHeight = 1.5*inch*logo.drawHeight / logo.drawWidth
##		logo.drawWidth = 1.5*inch
##		logo.hAlign = "LEFT"
##
##		styleSheet = getSampleStyleSheet()
##		styNormal = styleSheet['Normal']
##		styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
##		styH1 = styleSheet['Heading3']
##
##		data = self.datestrfdate()
##
##		lst = []
##		lst.append(logo)
##		lst.append(Paragraph("<b>ELENCO MATERIALI</b><br/><b>Scavo: %s,  Data: %s</b>" % (sito, data), styH1))
##
##		table_data = []
##		for i in range(len(records)):
##			exp_index = Invmat_index_pdf_sheet(records[i])
##			table_data.append(exp_index.getTable())
##
##		styles = exp_index.makeStyles()
##		colWidths=[70,110,110,110, 35, 35, 60, 60, 60,60]
##
##		table_data_formatted = Table(table_data, colWidths, style=styles)
##		table_data_formatted.hAlign = "LEFT"
##
##		lst.append(table_data_formatted)
##		lst.append(Spacer(0,0))
##
##		filename = ('%s%s%s') % (self.PDF_path, os.sep, 'elenco_materiali.pdf')
##		f = open(filename, "wb")
##
##		doc = SimpleDocTemplate(f, pagesize=(29*cm, 21*cm), showBoundary=0, topMargin = 15, bottomMargin = 40, leftMargin = 30, rightMargin = 30)
##		doc.build(lst, canvasmaker=NumberedCanvas_Invmatindex)
##
##		f.close()
##
##	def build_index_Casse(self, records, sito):
##		if os.name == 'posix':
##			home = os.environ['HOME']
##		elif os.name == 'nt':
##			home = os.environ['HOMEPATH']
##
##		home_DB_path = ('%s%s%s') % (home, os.sep, 'pyarchinit_DB_folder')
##		logo_path = ('%s%s%s') % (home_DB_path, os.sep, 'logo.jpg')
##
##		logo = Image(logo_path)
##		logo.drawHeight = 1.5*inch*logo.drawHeight / logo.drawWidth
##		logo.drawWidth = 1.5*inch
##		logo.hAlign = "LEFT"
##
##		styleSheet = getSampleStyleSheet()
##		styNormal = styleSheet['Normal']
##		styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
##		styH1 = styleSheet['Heading3']
##
##		data = self.datestrfdate()
##		lst = [logo]
##		lst.append(Paragraph("<b>ELENCO CASSE MATERIALI</b><br/><b>Scavo: %s,  Data: %s</b>" % (sito, data), styH1))
##
##		table_data = []
##		for i in range(len(records)):
##			exp_index = CASSE_index_pdf_sheet(records[i])
##			table_data.append(exp_index.getTable())
##
##		styles = exp_index.makeStyles()
##		colWidths=[20,350,250,100]
##
##		table_data_formatted = Table(table_data, colWidths, style=styles)
##		table_data_formatted.hAlign = "LEFT"
##
##		#table_data_formatted.setStyle(styles)
##
##		lst.append(table_data_formatted)
##		lst.append(Spacer(0,0))
##
##		filename = ('%s%s%s') % (self.PDF_path, os.sep, 'elenco_casse.pdf')
##		f = open(filename, "wb")
##
##		doc = SimpleDocTemplate(f, pagesize=(29*cm, 21*cm), showBoundary=0, topMargin = 15, bottomMargin = 40, leftMargin = 30, rightMargin = 30)
##		#doc.build(lst, canvasmaker=NumberedCanvas_Sindex)
##		doc.build(lst)
##
##		f.close()


##	def build_box_labels_Invmat(self, records, sito):
##		elements = []
##		for i in range(len(records)):
##			single_invmat_sheet = Box_labels_Finds_pdf_sheet(records[i], sito)
##			elements.append(single_invmat_sheet.create_sheet())
##			elements.append(PageBreak())
##		filename = ('%s%s%s') % (self.PDF_path, os.sep, 'etichette_casse_materiali.pdf')
##		f = open(filename, "wb")
##		doc = SimpleDocTemplate(f, pagesize=(29*cm, 21*cm), showBoundary=0.0, topMargin = 20, bottomMargin = 20, leftMargin = 20, rightMargin = 20)
##		doc.build(elements)
##		f.close()
