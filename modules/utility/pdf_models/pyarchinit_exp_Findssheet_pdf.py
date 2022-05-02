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
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, PageBreak, SimpleDocTemplate, Spacer
from reportlab.platypus.paragraph import Paragraph

from ..pyarchinit_OS_utility import *


class NumberedCanvas_Findssheet(canvas.Canvas):
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


class NumberedCanvas_USindex(canvas.Canvas):
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


class single_Finds_pdf_sheet(object):
    def __init__(self, data):
        self.id_invmat = data[0]
        self.sito = data[1]
        self.numero_inventario = data[2]
        self.tipo_reperto = data[3]
        self.criterio_schedatura = data[4]
        self.definizione = data[5]
        self.descrizione = data[6]
        self.area = data[7]
        self.us = data[8]
        self.lavato = data[9]
        self.nr_cassa = data[10]
        self.luogo_conservazione = data[11]
        self.stato_conservazione = data[12]
        self.datazione_reperto = data[13]
        self.elementi_reperto = data[14]
        self.misurazioni = data[15]
        self.rif_biblio = data[16]
        self.tecnologie = data[17]

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
        intestazione = Paragraph("<b>SCHEDA INVENTARIO REPERTI<br/>" + str(self.datestrfdate()) + "</b>", styNormal)
        intestazione2 = Paragraph("<b>pyArchInit</b>", styNormal)

        # 1 row
        sito = Paragraph("<b>Sito</b><br/>" + str(self.sito), styNormal)
        area = Paragraph("<b>Tomba</b><br/>" + str(self.area), styNormal)
        us = Paragraph("<b>US</b><br/>" + str(self.us), styNormal)
        nr_inventario = Paragraph("<b>N° Inventario</b><br/>" + str(self.numero_inventario), styNormal)

        # 2 row
        criterio_schedatura = Paragraph("<b>Classe</b><br/>" + self.criterio_schedatura, styNormal)
        tipo_reperto = Paragraph("<b>Tipo reperto</b><br/>" + self.tipo_reperto, styNormal)
        definizione = Paragraph("<b>Forma</b><br/>" + self.definizione, styNormal)

        # 3 row
        stato_conservazione = Paragraph("<b>Stato Conservazione</b><br/>" + self.stato_conservazione, styNormal)
        datazione = Paragraph("<b>Datazione</b><br/>" + self.datazione_reperto, styNormal)

        # 4 row
        descrizione = ''
        try:
            descrizione = Paragraph("<b>Descrizione</b><br/>" + str(self.descrizione), styDescrizione)
        except:
            pass

            # 5 row
        elementi_reperto = ''
        if ast.literal_eval(self.elementi_reperto) > 0:
            for i in ast.literal_eval(self.elementi_reperto):
                if elementi_reperto == '':
                    try:
                        elementi_reperto += ("%s: %s %s") % (str(i[0]), str(i[2]), str(i[1]))
                    except:
                        pass
                else:
                    try:
                        elementi_reperto += ("<br/>%s: %s %s") % (str(i[0]), str(i[2]), str(i[1]))
                    except:
                        pass

        elementi_reperto = Paragraph("<b>Elementi reperto</b><br/>" + elementi_reperto, styNormal)

        # 6 row
        misurazioni = ''
        if eval(self.misurazioni) > 0:
            for i in eval(self.misurazioni):
                if misurazioni == '':
                    try:
                        misurazioni += ("%s: %s %s") % (str(i[0]), str(i[1]), str(i[2]))
                    except:
                        pass
                else:
                    try:
                        misurazioni += ("<br/>%s: %s %s") % (str(i[0]), str(i[1]), str(i[2]))
                    except:
                        pass
        misurazioni = Paragraph("<b>Misurazioni</b><br/>" + misurazioni, styNormal)

        # 7 row
        tecnologie = ''
        if eval(self.tecnologie) > 0:
            for i in eval(self.tecnologie):
                if tecnologie == '':
                    try:
                        tecnologie += ("%s %s: %s %s") % (str(i[0]), str(i[1]), str(i[4]), str(i[3]))
                    except:
                        pass
                else:
                    try:
                        tecnologie += ("<br/>%s %s: %s %s") % (str(i[0]), str(i[1]), str(i[4]), str(i[3]))
                    except:
                        pass
        tecnologie = Paragraph("<b>Tecnologie</b><br/>" + tecnologie, styNormal)

        # 8 row
        rif_biblio = ''
        if eval(self.rif_biblio) > 0:
            for i in eval(self.rif_biblio):  # gigi
                if rif_biblio == '':
                    try:
                        rif_biblio += ("<b>Autore: %s, Anno: %s, Titolo: %s, Pag.: %s, Fig.: %s") % (
                        str(i[0]), str(i[1]), str(i[2]), str(i[3]), str(i[4]))
                    except:
                        pass
                else:
                    try:
                        rif_biblio += ("<br/><b>Autore: %s, Anno: %s, Titolo: %s, Pag.: %s, Fig.: %s") % (
                        str(i[0]), str(i[1]), str(i[2]), str(i[3]), str(i[4]))
                    except:
                        pass

        rif_biblio = Paragraph("<b>Riferimenti bibliografici</b><br/>" + rif_biblio, styNormal)

        # 9 row
        riferimenti_stratigrafici = Paragraph("<b>Riferimenti stratigrafici</b>", styNormal)

        # 10 row
        area = Paragraph("<b>Tomba</b><br/>" + self.area, styNormal)
        us = Paragraph("<b>US</b><br/>" + self.us, styNormal)

        # 11 row
        riferimenti_magazzino = Paragraph("<b>Riferimenti magazzino</b>", styNormal)

        # 12 row
        lavato = Paragraph("<b>Lavato</b><br/>" + self.lavato, styNormal)
        nr_cassa = Paragraph("<b>N° Cassa</b><br/>" + self.nr_cassa, styNormal)
        luogo_conservazione = Paragraph("<b>Luogo di conservazione</b><br/>" + self.luogo_conservazione, styNormal)

        # 13 row
        ##		intestazione_immagine  = Paragraph("<b>Immagine</b><br/>", styNormal)
        ##		test_image = Image("/Users/Windows/pyarchinit_PDF_folder/catalogo_immagini/inv120.png")
        ##		test_image.drawHeight = 2*inch*test_image.drawHeight / test_image.drawWidth
        ##		test_image.drawWidth = 2*inch

        # Paragraph('<para autoLeading="off" fontSize=12>This &lt;img/&gt;<img src="/Users/pyarchinit/pyarchinit_PDF_folder/test_immagini/kelebe.jpg" valign="bottom"/> is aligned<b>bottom</b></para>', styNormal)
        # schema
        cell_schema = [  # 00, 01, 02, 03, 04, 05, 06, 07, 08, 09 rows
            [intestazione, '01', '02', '03', '04', '05', '06', '07', intestazione2, '09'],
            [sito, '01', '02', area, '04', us, '06', '07', nr_inventario, '09'],  # 1 row ok
            [tipo_reperto, '01', '02', criterio_schedatura, '04', '05', definizione, '07', '08', '09'],
            # 2 row ok
            [datazione, '01', '02', '03', '04', stato_conservazione, '06', '07', '08', '09'],  # 3 row ok
            [descrizione, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 4 row ok
            [elementi_reperto, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 5 row ok
            [misurazioni, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 6 row ok
            [tecnologie, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 7 row ok
            [rif_biblio, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 8 row ok
            [riferimenti_stratigrafici, '02', '03', '04', '05', '06', '07', '08', '09'],  # 9 row ok
            [area, '01', '02', us, '04', '05', '06', '07', '08', '09'],  # 10 row ok
            [riferimenti_magazzino, '01', '02', '03', '04', '05', '06', '07', '08', '09'],  # 11 row ok
            [lavato, '01', '02', nr_cassa, '04', '05', luogo_conservazione, '07', '08', '09'],  # 12 row ok
            ['', '02', '03', '04', '05', '06', '07', '08', '09']  # 13 row
            # ["https://sites.google.com/site/pyarchinit/", '01', '02', '03', '04', '05', '06', '07', '08', '09' ] #13 row

        ]

        # table style
        table_style = [

            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # 0 row
            ('SPAN', (0, 0), (7, 0)),  # intestazione
            ('SPAN', (8, 0), (9, 0)),  # intestazione

            # 1 row
            ('SPAN', (0, 1), (2, 1)),  # dati identificativi
            ('SPAN', (3, 1), (4, 1)),  # dati identificativi
            ('SPAN', (5, 1), (7, 1)),  # dati identificativi
            ('SPAN', (8, 1), (9, 1)),  # dati identificativi

            # 2 row
            ('SPAN', (0, 2), (2, 2)),  # definizione
            ('SPAN', (3, 2), (5, 2)),  # definizione
            ('SPAN', (6, 2), (9, 2)),  # definizione
            ('VALIGN', (0, 2), (9, 2), 'TOP'),

            # 3 row
            ('SPAN', (0, 3), (4, 3)),  # datazione
            ('SPAN', (5, 3), (9, 3)),  # conservazione

            # 4 row
            ('SPAN', (0, 4), (9, 4)),  # descrizione

            # 5 row
            ('SPAN', (0, 5), (9, 5)),  # elementi_reperto

            # 6 row
            ('SPAN', (0, 6), (9, 6)),  # misurazioni

            # 7 row
            ('SPAN', (0, 7), (9, 7)),  # tecnologie

            # 8 row
            ('SPAN', (0, 8), (9, 8)),  # bibliografia

            # 9 row
            ('SPAN', (0, 9), (9, 9)),  # Riferimenti stratigrafici - Titolo

            # 10 row
            ('SPAN', (0, 10), (2, 10)),  # Riferimenti stratigrafici - area
            ('SPAN', (3, 10), (9, 10)),  # Riferimenti stratigrafici - us

            # 11 row
            ('SPAN', (0, 11), (9, 11)),  # Riferimenti magazzino - Titolo

            # 12 row
            ('SPAN', (0, 12), (2, 12)),  # Riferimenti magazzino - lavato
            ('SPAN', (3, 12), (5, 12)),  # Riferimenti magazzino - nr_cassa
            ('SPAN', (6, 12), (9, 12)),  # Riferimenti magazzino - luogo conservazione

            # 13 row
            ('SPAN', (0, 13), (9, 13)),  # pie' di pagina
            ('ALIGN', (0, 13), (9, 13), 'CENTER')

        ]

        t = Table(cell_schema, colWidths=50, rowHeights=None, style=table_style)

        return t


class generate_pdf(object):
    HOME = os.environ['PYARCHINIT_HOME']

    PDF_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")

    def datestrfdate(self):
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def build_Finds_sheets(self, records):
        elements = []
        for i in range(len(records)):
            single_finds_sheet = single_Finds_pdf_sheet(records[i])
            elements.append(single_finds_sheet.create_sheet())
            elements.append(PageBreak())
        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'scheda_Finds.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f)
        doc.build(elements, canvasmaker=NumberedCanvas_Findssheet)
        f.close()

    def build_index_US(self, records, sito):
        styleSheet = getSampleStyleSheet()
        styNormal = styleSheet['Normal']
        styBackground = ParagraphStyle('background', parent=styNormal, backColor=colors.pink)
        styH1 = styleSheet['Heading3']
        data = self.datestrfdate()
        lst = []
        lst.append(Paragraph(
            "<b>ELENCO UNITA' STRATIGRAFICHE</b><br/><b>Scavo: %s <br/>Data: %s <br/>Ditta esecutrice: adArte snc, Rimini</b>" % (
            sito, data), styH1))

        table_data = []
        for i in range(len(records)):
            exp_index = US_index_pdf_sheet(records[i])
            table_data.append(exp_index.getTable())

        styles = exp_index.makeStyles()
        table_data_formatted = Table(table_data, colWidths=55.5)
        table_data_formatted.setStyle(styles)

        lst.append(table_data_formatted)
        lst.append(Spacer(0, 12))

        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'indice_us.pdf')
        f = open(filename, "wb")

        doc = SimpleDocTemplate(f, pagesize=(29 * cm, 21 * cm), showBoundary=0)
        doc.build(lst, canvasmaker=NumberedCanvas_USindex)

        f.close()
