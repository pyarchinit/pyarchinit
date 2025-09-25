#!/usr/bin/env python
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
"""
import os
import ast
from datetime import date
from reportlab.lib.pagesizes import A5, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, PageBreak, SimpleDocTemplate, Spacer, TableStyle, Image, KeepTogether, Flowable
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from qgis.PyQt.QtWidgets import QMessageBox

# Register fonts
try:
    pdfmetrics.registerFont(TTFont('Cambria', 'Cambria.ttc'))
    pdfmetrics.registerFont(TTFont('cambriab', 'cambriab.ttf'))
except:
    pass

from ..db.pyarchinit_conn_strings import Connection
from ..db.pyarchinit_db_manager import Pyarchinit_db_management
from ..db.pyarchinit_utility import Utility
from .pyarchinit_OS_utility import *


class NumberedCanvas_InventarioA5(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self.left_title = kwargs.get('left_title', '')
        self.right_title = kwargs.get('right_title', '')

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            self.draw_headers()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 8)
        self.drawRightString(21 * cm, 0.3 * cm,
                             "Pag. %d di %d" % (self._pageNumber, page_count))

    def draw_headers(self):
        # Draw header titles for landscape A5 format (24x12 cm)
        if hasattr(self, 'left_title') and self.left_title:
            self.setFont("Helvetica-Bold", 10)
            self.drawString(3 * cm, 11.3 * cm, self.left_title)

        if hasattr(self, 'right_title') and self.right_title:
            self.setFont("Helvetica-Bold", 10)
            self.drawRightString(21 * cm, 11.3 * cm, self.right_title)


class generate_inventario_pdf_a5:
    HOME = os.environ['PYARCHINIT_HOME']
    PDF_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")

    def datestrfdate(self):
        oggi = date.today()
        oggi_str = oggi.strftime("%d-%m-%Y")
        return oggi_str

    def build_Inventario_a5(self, records, sito, left_title='', right_title=''):
        elements = []
        for i in range(len(records)):
            single_inventario_sheet = single_Inventario_pdf_sheet_a5(records[i], left_title, right_title)
            sheet_elements = single_inventario_sheet.create_sheet()
            elements.append(sheet_elements)
            if i < len(records) - 1:  # Don't add page break after last record
                elements.append(PageBreak())

        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'scheda_Inventario_A5.pdf')
        f = open(filename, "wb")

        class CustomCanvas(NumberedCanvas_InventarioA5):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.left_title = left_title
                self.right_title = right_title

        # Page size: 24x12 cm with content area 18x11 cm
        # This means 3cm margins on width and 0.5cm margins on height
        doc = SimpleDocTemplate(f, pagesize=(24*cm, 12*cm), showBoundary=0,
                              topMargin=0.8*cm, bottomMargin=0.2*cm,
                              leftMargin=3*cm, rightMargin=3*cm)
        doc.build(elements, canvasmaker=CustomCanvas)
        f.close()


class single_Inventario_pdf_sheet_a5:
    DATA = []

    def __init__(self, data, left_title='', right_title=''):
        self.DATA = data
        self.left_title = left_title
        self.right_title = right_title
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
        self.forme_minime = data[18]
        self.forme_massime = data[19]
        self.totale_frammenti = data[20]
        self.corpo_ceramico = data[21]
        self.rivestimento = data[22]
        self.diametro_orlo = data[23]
        self.peso = data[24]
        self.tipo = data[25]
        self.eve_orlo = data[26]
        self.repertato = data[27]
        self.diagnostico = data[28]

    def parse_measurements(self):
        """Parse measurements from string representation of list"""
        try:
            if self.misurazioni and str(self.misurazioni) != 'None':
                # Convert string representation to actual list
                measurements = ast.literal_eval(str(self.misurazioni))
                result = []
                for m in measurements:
                    if isinstance(m, (list, tuple)) and len(m) >= 3:
                        tipo = str(m[0]) if m[0] else ''
                        valore = str(m[1]) if m[1] else ''
                        unita = str(m[2]) if m[2] else ''
                        result.append(f"{tipo}: {valore} {unita}")
                return ', '.join(result) if result else ''
        except:
            pass
        return str(self.misurazioni) if self.misurazioni and str(self.misurazioni) != 'None' else ''

    def parse_elementi(self):
        """Parse elementi reperto from string representation"""
        try:
            if self.elementi_reperto and str(self.elementi_reperto) != 'None':
                elementi = ast.literal_eval(str(self.elementi_reperto))
                result = []
                for e in elementi:
                    if isinstance(e, (list, tuple)) and len(e) >= 2:
                        elem = str(e[0]) if e[0] else ''
                        quant = str(e[1]) if e[1] else ''
                        result.append(f"{elem} ({quant})")
                return ', '.join(result) if result else ''
        except:
            pass
        return str(self.elementi_reperto) if self.elementi_reperto and str(self.elementi_reperto) != 'None' else ''

    def get_first_image(self):
        """Recupera la prima immagine associata al reperto"""
        try:
            conn = Connection()
            thumb_path = conn.thumb_path()
            thumb_resize = conn.thumb_resize()

            # Query per trovare le immagini associate
            search_dict = {
                'id_entity': int(self.numero_inventario),
                'entity_type': '"REPERTO"',
                'nome_tabella': '"inventario_materiali_table"'
            }

            DB_MANAGER = Pyarchinit_db_management(conn.conn_str())
            DB_MANAGER.connection()

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)

            mediatoentity_res = DB_MANAGER.query_bool(search_dict, "MEDIATOENTITY")

            if mediatoentity_res:
                # Prendi solo la prima immagine
                first_media = mediatoentity_res[0]

                # Query per ottenere i dettagli del media
                search_dict_media = {'id_media': '"' + str(first_media.id_media) + '"'}
                media_data = DB_MANAGER.query_bool(search_dict_media, "MEDIA")

                if media_data:
                    thumb_resize_str = thumb_resize + os.sep
                    file_path = thumb_resize_str + str(media_data[0].path_resize)

                    if os.path.exists(file_path):
                        return file_path

        except Exception as e:
            pass

        return None

    def create_sheet(self):
        from reportlab.platypus import KeepTogether
        from reportlab.lib.utils import ImageReader
        from datetime import datetime

        # Define styles matching template exactly
        styleSheet = getSampleStyleSheet()

        # Normal style for labels (bold)
        styLabel = ParagraphStyle('label')
        styLabel.fontSize = 7
        styLabel.fontName = 'Helvetica-Bold'
        styLabel.alignment = TA_LEFT
        styLabel.leading = 8

        # Normal style for values (regular)
        styValue = ParagraphStyle('value')
        styValue.fontSize = 7
        styValue.fontName = 'Helvetica'
        styValue.alignment = TA_LEFT
        styValue.wordWrap = 'CJK'
        styValue.leading = 8

        # Small style for image caption
        stySmall = ParagraphStyle('small')
        stySmall.fontSize = 6
        stySmall.fontName = 'Helvetica'
        stySmall.alignment = TA_LEFT
        stySmall.leading = 7

        # Data list
        data_list = []

        # Format values safely
        def safe_str(val):
            if val is None or str(val) == 'None' or str(val) == '[]':
                return ''
            return str(val)

        # Create the bordered box with main data
        # Left column of the box
        left_box_data = []
        left_box_data.append([Paragraph(f"<b>N° {safe_str(self.numero_inventario)}</b>",
                                      ParagraphStyle('bignum', fontSize=11, fontName='Helvetica-Bold', alignment=TA_CENTER, leading=12))])

        # Right column of the box - split into multiple rows
        right_box_content = []

        # DATA row - use current date for cataloging date
        data_str = datetime.now().strftime("%d/%m/%Y")
        right_box_content.append([Paragraph("<b>DATA</b>", styLabel), Paragraph(data_str, styValue)])

        # Strato row
        strato_str = f"US {safe_str(self.us)}" if self.us else ""
        right_box_content.append([Paragraph("<b>Strato</b>", styLabel), Paragraph(strato_str, styValue)])
        right_box_content.append([Paragraph("<b>o Punto riuv.</b>", styLabel), Paragraph("", styValue)])

        # Vano o area
        right_box_content.append([Paragraph("<b>Vano o area</b>", styLabel), Paragraph(safe_str(self.area), styValue)])

        # Quota
        quota_str = f"interfaccia tra US {safe_str(self.us)}" if self.us else ""
        right_box_content.append([Paragraph("<b>Quota:</b>", styLabel), Paragraph(quota_str, styValue)])

        right_table = Table(right_box_content, colWidths=[2.5*cm, 12.5*cm])
        right_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ]))

        # Main bordered box - adjusted for 18cm content width
        box_table = Table([
            [left_box_data[0][0], right_table]
        ], colWidths=[3*cm, 15*cm], rowHeights=[2*cm])

        box_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (0, 0), 1, colors.black),
            ('LINEAFTER', (0, 0), (0, 0), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ]))

        data_list.append(box_table)
        data_list.append(Spacer(0, 0.15 * cm))

        # OGGETTO section with image on right
        oggetto_content = []

        # OGGETTO and related fields
        oggetto_line = []
        oggetto_line.append(Paragraph("<b>OGGETTO:</b>", styLabel))
        oggetto_line.append(Paragraph(safe_str(self.definizione), styValue))
        oggetto_table = Table([oggetto_line], colWidths=[1.8*cm, 7.2*cm])
        oggetto_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ]))
        oggetto_content.append(oggetto_table)

        # Misure on same line if exists
        measurements_str = self.parse_measurements_inline()
        if measurements_str:
            misure_line = []
            misure_line.append(Paragraph("<b>Misure:</b>", styLabel))
            misure_line.append(Paragraph(measurements_str, styValue))
            misure_table = Table([misure_line], colWidths=[1.2*cm, 7.8*cm])
            misure_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ]))
            oggetto_content.append(misure_table)

        oggetto_content.append(Spacer(0, 0.1 * cm))

        # Get or create image
        image_path = self.get_first_image()
        image_elem = None

        if image_path and os.path.exists(image_path):
            try:
                img = Image(image_path)
                # Set image size (matching template)
                img.drawHeight = 3.5 * cm
                img.drawWidth = 3.5 * cm
                img.hAlign = 'CENTER'
                image_elem = img
            except:
                image_elem = self._create_placeholder_image()
        else:
            image_elem = self._create_placeholder_image()

        # Left side with object info AND description
        left_content = []
        for item in oggetto_content:
            left_content.append([item])

        # Add Descrizione to left content
        if self.descrizione and safe_str(self.descrizione):
            left_content.append([Spacer(0, 0.15*cm)])
            desc_header = Paragraph("<b>Descrizione:</b>", styLabel)
            desc_text = Paragraph(safe_str(self.descrizione), styValue)
            left_content.append([desc_header])
            left_content.append([desc_text])

        # Add DECORAZIONE section to left content
        decorazione_parts = []
        if safe_str(self.datazione_reperto):
            decorazione_parts.append(f"Cronologia: {safe_str(self.datazione_reperto)}")
        if safe_str(self.stato_conservazione):
            decorazione_parts.append(f"Fabbrica: {safe_str(self.stato_conservazione)}")

        if decorazione_parts:
            left_content.append([Spacer(0, 0.1*cm)])
            left_content.append([Paragraph("<i>DECORAZIONE:</i>", styLabel)])
            for part in decorazione_parts:
                left_content.append([Paragraph(part, styValue)])

        left_content_table = Table(left_content, colWidths=[9*cm])
        left_content_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        # Right side with Materiale and image
        right_content = []
        # Materiale label and value
        materiale_table = Table([
            [Paragraph("<b>Materiale:</b>", styLabel), Paragraph(safe_str(self.tipo_reperto), styValue)]
        ], colWidths=[1.8*cm, 7.2*cm])
        materiale_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        right_content.append([materiale_table])
        right_content.append([Spacer(0, 0.1*cm)])
        right_content.append([image_elem])

        # Add proper image caption
        caption_parts = []
        # Photo name (using numero_inventario as reference)
        caption_parts.append(f"Foto: DSC_{safe_str(self.numero_inventario).zfill(4)}")
        # Disegnatore if available
        if safe_str(self.repertato):
            caption_parts.append(f"Dis.: {safe_str(self.repertato)}")
        # Collocazione (location and box)
        if safe_str(self.nr_cassa) or safe_str(self.luogo_conservazione):
            loc = safe_str(self.luogo_conservazione) if self.luogo_conservazione else "Mag. 5"
            box = safe_str(self.nr_cassa) if self.nr_cassa else "66"
            caption_parts.append(f"Coll.: {loc} – cass. {box}")

        if caption_parts:
            right_content.append([Paragraph('<br/>'.join(caption_parts), stySmall)])

        right_content_table = Table(right_content, colWidths=[9*cm])
        right_content_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 2), (0, 2), 'CENTER'),
        ]))

        main_content = Table([
            [left_content_table, right_content_table]
        ], colWidths=[9*cm, 9*cm])

        main_content.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        data_list.append(main_content)

        # Return elements wrapped in KeepTogether
        return KeepTogether(data_list)

    def parse_measurements_inline(self):
        """Parse measurements for inline display"""
        try:
            if self.misurazioni and str(self.misurazioni) != 'None':
                # Convert string representation to actual list
                measurements = ast.literal_eval(str(self.misurazioni))
                result = []
                for m in measurements:
                    if isinstance(m, (list, tuple)) and len(m) >= 3:
                        tipo = str(m[0]) if m[0] else ''
                        valore = str(m[1]) if m[1] else ''
                        unita = str(m[2]) if m[2] else ''
                        # Format like in template: "Diam. cm 1,5; spess. max 0,6"
                        if tipo and valore:
                            formatted = f"{tipo} {unita} {valore}" if unita else f"{tipo} {valore}"
                            result.append(formatted)
                return '; '.join(result) if result else ''
        except:
            pass
        return str(self.misurazioni) if self.misurazioni and str(self.misurazioni) != 'None' else ''

    def _create_placeholder_image(self):
        """Create placeholder for missing image"""
        placeholder = Table([
            [Paragraph("<i>Immagine<br/>non<br/>disponibile</i>",
                      ParagraphStyle('placeholder', fontSize=8, alignment=TA_CENTER))]
        ], colWidths=[3.5*cm], rowHeights=[3.5*cm])
        placeholder.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ]))
        return placeholder