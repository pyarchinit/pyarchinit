
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
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
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

# Page dimensions and margins for A4
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_LEFT = 1.5 * cm
MARGIN_RIGHT = 1.5 * cm
MARGIN_TOP = 1.5 * cm
MARGIN_BOTTOM = 2 * cm
USABLE_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

# Colors for professional look
HEADER_BG = colors.HexColor('#2C3E50')  # Dark blue-gray
SECTION_BG = colors.HexColor('#3498DB')  # Blue
SUBSECTION_BG = colors.HexColor('#ECF0F1')  # Light gray
LABEL_BG = colors.HexColor('#F8F9FA')  # Very light gray
BORDER_COLOR = colors.HexColor('#BDC3C7')  # Medium gray


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
    Professional full-page layout with organized sections.
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

    def _get_styles(self):
        """Create professional styles for the PDF"""
        styles = {}

        # Title style - large, centered, white on dark background
        styles['title'] = ParagraphStyle(
            'Title',
            fontName='Cambria',
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
            textColor=colors.white,
            spaceAfter=0,
            spaceBefore=0
        )

        # Section header style - medium, white on blue
        styles['section'] = ParagraphStyle(
            'Section',
            fontName='Cambria',
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
            textColor=colors.white,
            spaceAfter=0,
            spaceBefore=0,
            leftIndent=3
        )

        # Label style - bold, small
        styles['label'] = ParagraphStyle(
            'Label',
            fontName='Cambria',
            fontSize=7,
            leading=9,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=1,
            spaceBefore=1
        )

        # Value style - normal text
        styles['value'] = ParagraphStyle(
            'Value',
            fontName='Cambria',
            fontSize=8,
            leading=10,
            alignment=TA_LEFT,
            textColor=colors.black,
            spaceAfter=2,
            spaceBefore=0
        )

        # Long text style - justified
        styles['longtext'] = ParagraphStyle(
            'LongText',
            fontName='Cambria',
            fontSize=8,
            leading=10,
            alignment=TA_JUSTIFY,
            textColor=colors.black,
            spaceAfter=2,
            spaceBefore=0
        )

        return styles

    def _get_logo(self):
        """Get the logo image"""
        home = os.environ['PYARCHINIT_HOME']
        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        if not bool(lo_path_str):
            logo_path = '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')
        else:
            logo_path = lo_path_str

        if os.path.exists(logo_path):
            logo = Image(logo_path)
            logo.drawHeight = 1.2 * inch * logo.drawHeight / logo.drawWidth
            logo.drawWidth = 1.2 * inch
            logo.hAlign = 'CENTER'
            return logo
        return None

    def _make_field(self, label, value, styles, long=False):
        """Create a field paragraph with label and value"""
        style = styles['longtext'] if long else styles['value']
        val_str = str(value) if value else '-'
        return Paragraph(f"<b>{label}:</b> {val_str}", style)

    def _parse_specie_psi(self, specie_psi_str):
        """Parse specie_psi JSON into list of [species, skeletal_part] rows"""
        if not specie_psi_str or specie_psi_str == '-':
            return []
        try:
            import json
            import ast
            # Try JSON first, then ast.literal_eval
            try:
                data = json.loads(specie_psi_str)
            except:
                data = ast.literal_eval(specie_psi_str)

            if not data or not isinstance(data, list):
                return []

            rows = []
            for item in data:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    species = str(item[0]) if item[0] else '-'
                    part = str(item[1]) if item[1] else '-'
                    rows.append([species, part])
            return rows
        except:
            return []

    def _parse_misure_ossa(self, misure_str):
        """Parse misure_ossa JSON into list of [elemento, specie, GL, GB, Bp, Bd] rows"""
        if not misure_str or misure_str == '-':
            return []
        try:
            import json
            import ast
            # Try JSON first, then ast.literal_eval
            try:
                data = json.loads(misure_str)
            except:
                data = ast.literal_eval(misure_str)

            if not data or not isinstance(data, list):
                return []

            rows = []
            for item in data:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    elemento = str(item[0]) if item[0] else '-'
                    specie = str(item[1]) if len(item) > 1 and item[1] else '-'
                    gl = str(item[2]) if len(item) > 2 and item[2] else '-'
                    gb = str(item[3]) if len(item) > 3 and item[3] else '-'
                    bp = str(item[4]) if len(item) > 4 and item[4] else '-'
                    bd = str(item[5]) if len(item) > 5 and item[5] else '-'
                    rows.append([elemento, specie, gl, gb, bp, bd])
            return rows
        except:
            return []

    def _format_specie_psi(self, specie_psi_str):
        """Format specie_psi JSON into readable text for species and skeletal parts (legacy)"""
        rows = self._parse_specie_psi(specie_psi_str)
        if not rows:
            return '-', '-'
        species = [r[0] for r in rows if r[0] != '-']
        parts = [r[1] for r in rows if r[1] != '-']
        species_str = ', '.join(species) if species else '-'
        parts_str = ', '.join(parts) if parts else '-'
        return species_str, parts_str

    def _format_misure_ossa(self, misure_str):
        """Format misure_ossa JSON into readable text with measurement labels (legacy)"""
        rows = self._parse_misure_ossa(misure_str)
        if not rows:
            return '-'
        formatted_parts = []
        for row in rows:
            elemento, specie, gl, gb, bp, bd = row
            measures = []
            if gl != '-':
                measures.append(f"GL={gl}")
            if gb != '-':
                measures.append(f"GB={gb}")
            if bp != '-':
                measures.append(f"Bp={bp}")
            if bd != '-':
                measures.append(f"Bd={bd}")
            if elemento != '-' or specie != '-':
                header = elemento if elemento != '-' else ''
                if specie != '-':
                    header = f"{header} ({specie})" if header else specie
                if measures:
                    formatted_parts.append(f"{header}: {', '.join(measures)}")
                else:
                    formatted_parts.append(header)
        return '; '.join(formatted_parts) if formatted_parts else '-'

    def _create_specie_psi_table(self, specie_psi_str, labels, styles):
        """Create a proper table for specie_psi data with columns"""
        rows = self._parse_specie_psi(specie_psi_str)

        # Also check legacy fields
        if not rows and self.specie:
            # Create single row from legacy data
            rows = [[self.specie, self.parti_scheletriche or '-']]

        if not rows:
            return None

        # Table header
        header_style = ParagraphStyle('TableHeader', fontName='Cambria', fontSize=7,
                                      leading=9, alignment=TA_CENTER,
                                      textColor=colors.white)
        value_style = ParagraphStyle('TableValue', fontName='Cambria', fontSize=7,
                                     leading=9, alignment=TA_LEFT,
                                     textColor=colors.black)

        table_data = [
            [Paragraph(f"<b>{labels['species']}</b>", header_style),
             Paragraph(f"<b>{labels['skeletal_parts']}</b>", header_style)]
        ]

        for row in rows:
            table_data.append([
                Paragraph(row[0], value_style),
                Paragraph(row[1], value_style)
            ])

        col_widths = [USABLE_WIDTH * 0.4, USABLE_WIDTH * 0.6]
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), SECTION_BG),
            ('BACKGROUND', (0, 1), (-1, -1), LABEL_BG),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ]))
        return table

    def _create_misure_table(self, misure_str, labels, styles):
        """Create a proper table for bone measurements with columns"""
        rows = self._parse_misure_ossa(misure_str)

        if not rows:
            return None

        # Table header
        header_style = ParagraphStyle('TableHeader', fontName='Cambria', fontSize=7,
                                      leading=9, alignment=TA_CENTER,
                                      textColor=colors.white)
        value_style = ParagraphStyle('TableValue', fontName='Cambria', fontSize=7,
                                     leading=9, alignment=TA_CENTER,
                                     textColor=colors.black)

        table_data = [
            [Paragraph(f"<b>{labels.get('element', 'Elemento')}</b>", header_style),
             Paragraph(f"<b>{labels['species']}</b>", header_style),
             Paragraph("<b>GL</b>", header_style),
             Paragraph("<b>GB</b>", header_style),
             Paragraph("<b>Bp</b>", header_style),
             Paragraph("<b>Bd</b>", header_style)]
        ]

        for row in rows:
            table_data.append([
                Paragraph(row[0], value_style),
                Paragraph(row[1], value_style),
                Paragraph(row[2], value_style),
                Paragraph(row[3], value_style),
                Paragraph(row[4], value_style),
                Paragraph(row[5], value_style)
            ])

        # Column widths: Elemento and Specie wider, measurements narrower
        col_widths = [USABLE_WIDTH * 0.25, USABLE_WIDTH * 0.25,
                      USABLE_WIDTH * 0.125, USABLE_WIDTH * 0.125,
                      USABLE_WIDTH * 0.125, USABLE_WIDTH * 0.125]
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), SECTION_BG),
            ('BACKGROUND', (0, 1), (-1, -1), LABEL_BG),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ]))
        return table

    def _create_professional_sheet(self, labels):
        """
        Create a professional full-page layout.
        labels: dictionary with all field labels in the target language
        """
        styles = self._get_styles()
        logo = self._get_logo()

        # Calculate column widths for full page (4 columns)
        col_width = USABLE_WIDTH / 4
        full_width = USABLE_WIDTH
        half_width = USABLE_WIDTH / 2
        third_width = USABLE_WIDTH / 3

        elements = []

        # ==================== HEADER ====================
        header_data = [
            [Paragraph(f"<b>{labels['title']}</b>", styles['title']),
             '', '',
             logo if logo else '']
        ]
        header_table = Table(header_data, colWidths=[col_width*3, 0, 0, col_width])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (2, 0), HEADER_BG),
            ('BACKGROUND', (3, 0), (3, 0), colors.white),
            ('SPAN', (0, 0), (2, 0)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (3, 0), (3, 0), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 3*mm))

        # ==================== RECORD INFO ====================
        record_header = [[Paragraph(f"<b>{labels['section_record']}</b>", styles['section'])]]
        record_header_table = Table(record_header, colWidths=[full_width])
        record_header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), SECTION_BG),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(record_header_table)

        record_data = [
            [self._make_field(labels['id'], self.id_fauna, styles),
             self._make_field(labels['site'], self.sito, styles),
             self._make_field(labels['area'], self.area, styles),
             self._make_field(labels['trench'], self.saggio, styles)],
            [self._make_field(labels['su'], self.us, styles),
             self._make_field(labels['su_dating'], self.datazione_us, styles),
             self._make_field(labels['recorder'], self.responsabile_scheda, styles),
             self._make_field(labels['date'], self.data_compilazione, styles)]
        ]
        record_table = Table(record_data, colWidths=[col_width]*4)
        record_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LABEL_BG),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(record_table)
        elements.append(Spacer(1, 3*mm))

        # ==================== CONTEXT & METHODOLOGY ====================
        context_header = [[Paragraph(f"<b>{labels['section_context']}</b>", styles['section'])]]
        context_header_table = Table(context_header, colWidths=[full_width])
        context_header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), SECTION_BG),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(context_header_table)

        context_data = [
            [self._make_field(labels['recovery_method'], self.metodologia_recupero, styles),
             self._make_field(labels['context'], self.contesto, styles),
             self._make_field(labels['photo_doc'], self.documentazione_fotografica, styles),
             ''],
            [Paragraph(f"<b>{labels['context_desc']}:</b> {self.descrizione_contesto or '-'}", styles['longtext']), '', '', '']
        ]
        context_table = Table(context_data, colWidths=[col_width]*4)
        context_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LABEL_BG),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('SPAN', (0, 1), (3, 1)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(context_table)
        elements.append(Spacer(1, 3*mm))

        # ==================== DEPOSIT CHARACTERISTICS ====================
        deposit_header = [[Paragraph(f"<b>{labels['section_deposit']}</b>", styles['section'])]]
        deposit_header_table = Table(deposit_header, colWidths=[full_width])
        deposit_header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), SECTION_BG),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(deposit_header_table)

        deposit_data = [
            [self._make_field(labels['anatomical_conn'], self.resti_connessione_anatomica, styles),
             self._make_field(labels['accumulation_type'], self.tipologia_accumulo, styles),
             self._make_field(labels['deposition'], self.deposizione, styles),
             ''],
            [self._make_field(labels['estimated_number'], self.numero_stimato_resti, styles),
             self._make_field(labels['mni'], self.numero_minimo_individui, styles),
             self._make_field(labels['reliability'], self.affidabilita_stratigrafica, styles),
             '']
        ]
        deposit_table = Table(deposit_data, colWidths=[col_width]*4)
        deposit_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LABEL_BG),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(deposit_table)
        elements.append(Spacer(1, 3*mm))

        # ==================== TAXONOMIC DATA ====================
        taxo_header = [[Paragraph(f"<b>{labels['section_taxonomy']}</b>", styles['section'])]]
        taxo_header_table = Table(taxo_header, colWidths=[full_width])
        taxo_header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), SECTION_BG),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(taxo_header_table)

        # Create Species/Skeletal Parts table
        specie_psi_table = self._create_specie_psi_table(self.specie_psi, labels, styles)
        if specie_psi_table:
            # Sub-header for species table
            specie_subheader = [[Paragraph(f"<b>{labels['species']} / {labels['skeletal_parts']}</b>", styles['label'])]]
            specie_subheader_table = Table(specie_subheader, colWidths=[full_width])
            specie_subheader_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), SUBSECTION_BG),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(specie_subheader_table)
            elements.append(specie_psi_table)
        else:
            # Fallback: show as text if no data
            specie_formatted, parti_formatted = self._format_specie_psi(self.specie_psi)
            if specie_formatted == '-' and self.specie:
                specie_formatted = self.specie
            if parti_formatted == '-' and self.parti_scheletriche:
                parti_formatted = self.parti_scheletriche
            fallback_data = [[Paragraph(f"<b>{labels['species']}:</b> {specie_formatted} | <b>{labels['skeletal_parts']}:</b> {parti_formatted}", styles['value'])]]
            fallback_table = Table(fallback_data, colWidths=[full_width])
            fallback_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), LABEL_BG),
                ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(fallback_table)

        elements.append(Spacer(1, 2*mm))

        # Create Bone Measurements table
        misure_table = self._create_misure_table(self.misure_ossa, labels, styles)
        if misure_table:
            # Sub-header for measurements table
            misure_subheader = [[Paragraph(f"<b>{labels['bone_measurements']}</b>", styles['label'])]]
            misure_subheader_table = Table(misure_subheader, colWidths=[full_width])
            misure_subheader_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), SUBSECTION_BG),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(misure_subheader_table)
            elements.append(misure_table)
        else:
            # Fallback: show as text if no data
            misure_formatted = self._format_misure_ossa(self.misure_ossa)
            fallback_data = [[Paragraph(f"<b>{labels['bone_measurements']}:</b> {misure_formatted}", styles['value'])]]
            fallback_table = Table(fallback_data, colWidths=[full_width])
            fallback_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), LABEL_BG),
                ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(fallback_table)

        elements.append(Spacer(1, 3*mm))

        # ==================== TAPHONOMY & PRESERVATION ====================
        tafo_header = [[Paragraph(f"<b>{labels['section_taphonomy']}</b>", styles['section'])]]
        tafo_header_table = Table(tafo_header, colWidths=[full_width])
        tafo_header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), SECTION_BG),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(tafo_header_table)

        combustion_other = labels['yes'] if self.combustione_altri_materiali_us else labels['no']
        tafo_data = [
            [self._make_field(labels['fragmentation'], self.stato_frammentazione, styles),
             self._make_field(labels['preservation'], self.stato_conservazione, styles),
             self._make_field(labels['alterations'], self.alterazioni_morfologiche, styles),
             ''],
            [self._make_field(labels['burning_traces'], self.tracce_combustione, styles),
             self._make_field(labels['burning_type'], self.tipo_combustione, styles),
             self._make_field(labels['other_burned'], combustion_other, styles),
             ''],
            [self._make_field(labels['taphonomic_signs'], self.segni_tafonomici_evidenti, styles),
             Paragraph(f"<b>{labels['taphonomic_char']}:</b> {self.caratterizzazione_segni_tafonomici or '-'}", styles['longtext']),
             '', '']
        ]
        tafo_table = Table(tafo_data, colWidths=[col_width]*4)
        tafo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LABEL_BG),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('SPAN', (1, 2), (3, 2)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(tafo_table)
        elements.append(Spacer(1, 3*mm))

        # ==================== NOTES & INTERPRETATION ====================
        notes_header = [[Paragraph(f"<b>{labels['section_notes']}</b>", styles['section'])]]
        notes_header_table = Table(notes_header, colWidths=[full_width])
        notes_header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), SECTION_BG),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(notes_header_table)

        notes_data = [
            [Paragraph(f"<b>{labels['position_notes']}:</b> {self.note_terreno_giacitura or '-'}", styles['longtext'])],
            [Paragraph(f"<b>{labels['sampling']}:</b> {self.campionature_effettuate or '-'}", styles['value'])],
            [Paragraph(f"<b>{labels['associated_finds']}:</b> {self.classi_reperti_associazione or '-'}", styles['longtext'])],
            [Paragraph(f"<b>{labels['observations']}:</b> {self.osservazioni or '-'}", styles['longtext'])],
            [Paragraph(f"<b>{labels['interpretation']}:</b> {self.interpretazione or '-'}", styles['longtext'])]
        ]
        notes_table = Table(notes_data, colWidths=[full_width])
        notes_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LABEL_BG),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(notes_table)

        # ==================== FOOTER ====================
        elements.append(Spacer(1, 5*mm))
        footer_style = ParagraphStyle('Footer', fontName='Cambria', fontSize=7,
                                       alignment=TA_RIGHT, textColor=colors.gray)
        footer = Paragraph(f"{labels['generated']} {self.datestrfdate()} - PyArchInit", footer_style)
        elements.append(footer)

        # Create main table containing all elements
        main_data = [[e] for e in elements]
        main_table = Table(main_data, colWidths=[full_width])
        main_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))

        return main_table

    def create_sheet(self):
        """Italian version of the sheet"""
        labels = {
            'title': 'SCHEDA FAUNA ARCHEOLOGICA',
            'section_record': 'DATI IDENTIFICATIVI',
            'section_context': 'CONTESTO E METODOLOGIA',
            'section_deposit': 'CARATTERISTICHE DEL DEPOSITO',
            'section_taxonomy': 'DATI TASSONOMICI',
            'section_taphonomy': 'TAFONOMIA E CONSERVAZIONE',
            'section_notes': 'NOTE E INTERPRETAZIONE',
            'id': 'ID Scheda',
            'site': 'Sito',
            'area': 'Area',
            'trench': 'Saggio',
            'su': 'US',
            'su_dating': 'Datazione US',
            'recorder': 'Responsabile',
            'date': 'Data Compilazione',
            'recovery_method': 'Metodologia Recupero',
            'context': 'Contesto',
            'context_desc': 'Descrizione Contesto',
            'photo_doc': 'Doc. Fotografica',
            'anatomical_conn': 'Connessione Anatomica',
            'accumulation_type': 'Tipologia Accumulo',
            'deposition': 'Deposizione',
            'estimated_number': 'N. Stimato Resti',
            'mni': 'NMI',
            'reliability': 'Affidabilit\u00e0 Strat.',
            'species': 'Specie',
            'skeletal_parts': 'Parti Scheletriche',
            'species_psi': 'Specie PSI',
            'element': 'Elemento',
            'bone_measurements': 'Misure Ossa',
            'fragmentation': 'Frammentazione',
            'preservation': 'Stato Conservazione',
            'alterations': 'Alterazioni Morf.',
            'burning_traces': 'Tracce Combustione',
            'burning_type': 'Tipo Combustione',
            'other_burned': 'Altri Mat. Combusti',
            'taphonomic_signs': 'Segni Tafonomici',
            'taphonomic_char': 'Caratterizzazione Tafonomica',
            'position_notes': 'Note Terreno/Giacitura',
            'sampling': 'Campionature Effettuate',
            'associated_finds': 'Classi Reperti Associati',
            'observations': 'Osservazioni',
            'interpretation': 'Interpretazione',
            'generated': 'Generato il',
            'yes': 'S\u00ec',
            'no': 'No'
        }
        return self._create_professional_sheet(labels)

    def create_sheet_de(self):
        """German version of the sheet"""
        labels = {
            'title': 'ARCH\u00c4OLOGISCHES FAUNA FORMULAR',
            'section_record': 'IDENTIFIKATIONSDATEN',
            'section_context': 'KONTEXT UND METHODIK',
            'section_deposit': 'ABLAGERUNGSEIGENSCHAFTEN',
            'section_taxonomy': 'TAXONOMISCHE DATEN',
            'section_taphonomy': 'TAPHONOMIE UND ERHALTUNG',
            'section_notes': 'ANMERKUNGEN UND INTERPRETATION',
            'id': 'Formular-ID',
            'site': 'Fundstelle',
            'area': 'Bereich',
            'trench': 'Schnitt',
            'su': 'SE',
            'su_dating': 'Datierung SE',
            'recorder': 'Bearbeiter',
            'date': 'Erstellungsdatum',
            'recovery_method': 'Bergungsmethode',
            'context': 'Kontext',
            'context_desc': 'Kontextbeschreibung',
            'photo_doc': 'Foto-Dok.',
            'anatomical_conn': 'Anatomischer Verbund',
            'accumulation_type': 'Akkumulationstyp',
            'deposition': 'Ablagerung',
            'estimated_number': 'Gesch\u00e4tzte Anzahl',
            'mni': 'MNI',
            'reliability': 'Strat. Zuverl\u00e4ssigkeit',
            'species': 'Spezies',
            'skeletal_parts': 'Skelettelemente',
            'species_psi': 'Spezies PSI',
            'element': 'Element',
            'bone_measurements': 'Knochenma\u00dfe',
            'fragmentation': 'Fragmentierung',
            'preservation': 'Erhaltungszustand',
            'alterations': 'Morph. Ver\u00e4nderungen',
            'burning_traces': 'Brandspuren',
            'burning_type': 'Brandtyp',
            'other_burned': 'Andere verbr. Mat.',
            'taphonomic_signs': 'Taphonomische Zeichen',
            'taphonomic_char': 'Taphonomische Charakterisierung',
            'position_notes': 'Anmerkungen zur Lage',
            'sampling': 'Probenahmen',
            'associated_finds': 'Assoziierte Funde',
            'observations': 'Beobachtungen',
            'interpretation': 'Interpretation',
            'generated': 'Erstellt am',
            'yes': 'Ja',
            'no': 'Nein'
        }
        return self._create_professional_sheet(labels)

    def create_sheet_en(self):
        """English version of the sheet"""
        labels = {
            'title': 'ARCHAEOLOGICAL FAUNA RECORD',
            'section_record': 'IDENTIFICATION DATA',
            'section_context': 'CONTEXT AND METHODOLOGY',
            'section_deposit': 'DEPOSIT CHARACTERISTICS',
            'section_taxonomy': 'TAXONOMIC DATA',
            'section_taphonomy': 'TAPHONOMY AND PRESERVATION',
            'section_notes': 'NOTES AND INTERPRETATION',
            'id': 'Record ID',
            'site': 'Site',
            'area': 'Area',
            'trench': 'Trench',
            'su': 'SU',
            'su_dating': 'SU Dating',
            'recorder': 'Recorder',
            'date': 'Recording Date',
            'recovery_method': 'Recovery Method',
            'context': 'Context',
            'context_desc': 'Context Description',
            'photo_doc': 'Photo Doc.',
            'anatomical_conn': 'Anatomical Connection',
            'accumulation_type': 'Accumulation Type',
            'deposition': 'Deposition',
            'estimated_number': 'Estimated Number',
            'mni': 'MNI',
            'reliability': 'Strat. Reliability',
            'species': 'Species',
            'skeletal_parts': 'Skeletal Elements',
            'species_psi': 'Species PSI',
            'element': 'Element',
            'bone_measurements': 'Bone Measurements',
            'fragmentation': 'Fragmentation',
            'preservation': 'Preservation State',
            'alterations': 'Morph. Alterations',
            'burning_traces': 'Burning Traces',
            'burning_type': 'Burning Type',
            'other_burned': 'Other Burned Mat.',
            'taphonomic_signs': 'Taphonomic Signs',
            'taphonomic_char': 'Taphonomic Characterization',
            'position_notes': 'Notes on Position',
            'sampling': 'Sampling',
            'associated_finds': 'Associated Finds',
            'observations': 'Observations',
            'interpretation': 'Interpretation',
            'generated': 'Generated on',
            'yes': 'Yes',
            'no': 'No'
        }
        return self._create_professional_sheet(labels)

    def create_sheet_fr(self):
        """French version of the sheet"""
        labels = {
            'title': 'FICHE FAUNE ARCH\u00c9OLOGIQUE',
            'section_record': 'DONN\u00c9ES D\'IDENTIFICATION',
            'section_context': 'CONTEXTE ET M\u00c9THODOLOGIE',
            'section_deposit': 'CARACT\u00c9RISTIQUES DU D\u00c9P\u00d4T',
            'section_taxonomy': 'DONN\u00c9ES TAXONOMIQUES',
            'section_taphonomy': 'TAPHONOMIE ET CONSERVATION',
            'section_notes': 'NOTES ET INTERPR\u00c9TATION',
            'id': 'ID Fiche',
            'site': 'Site',
            'area': 'Zone',
            'trench': 'Sondage',
            'su': 'US',
            'su_dating': 'Datation US',
            'recorder': 'Responsable',
            'date': 'Date de Compilation',
            'recovery_method': 'M\u00e9thode de R\u00e9cup\u00e9ration',
            'context': 'Contexte',
            'context_desc': 'Description du Contexte',
            'photo_doc': 'Doc. Photo',
            'anatomical_conn': 'Connexion Anatomique',
            'accumulation_type': 'Type d\'Accumulation',
            'deposition': 'D\u00e9position',
            'estimated_number': 'Nombre Estim\u00e9',
            'mni': 'NMI',
            'reliability': 'Fiabilit\u00e9 Strat.',
            'species': 'Esp\u00e8ce',
            'skeletal_parts': '\u00c9l\u00e9ments Squelettiques',
            'species_psi': 'Esp\u00e8ce PSI',
            'element': '\u00c9l\u00e9ment',
            'bone_measurements': 'Mesures Osseuses',
            'fragmentation': 'Fragmentation',
            'preservation': '\u00c9tat de Conservation',
            'alterations': 'Alt\u00e9rations Morph.',
            'burning_traces': 'Traces de Combustion',
            'burning_type': 'Type de Combustion',
            'other_burned': 'Autres Mat. Br\u00fbl\u00e9s',
            'taphonomic_signs': 'Signes Taphonomiques',
            'taphonomic_char': 'Caract\u00e9risation Taphonomique',
            'position_notes': 'Notes sur la Position',
            'sampling': '\u00c9chantillonnages',
            'associated_finds': 'Mobilier Associ\u00e9',
            'observations': 'Observations',
            'interpretation': 'Interpr\u00e9tation',
            'generated': 'G\u00e9n\u00e9r\u00e9 le',
            'yes': 'Oui',
            'no': 'Non'
        }
        return self._create_professional_sheet(labels)

    def create_sheet_es(self):
        """Spanish version of the sheet"""
        labels = {
            'title': 'FICHA DE FAUNA ARQUEOL\u00d3GICA',
            'section_record': 'DATOS DE IDENTIFICACI\u00d3N',
            'section_context': 'CONTEXTO Y METODOLOG\u00cdA',
            'section_deposit': 'CARACTER\u00cdSTICAS DEL DEP\u00d3SITO',
            'section_taxonomy': 'DATOS TAXON\u00d3MICOS',
            'section_taphonomy': 'TAFONOMÍA Y CONSERVACI\u00d3N',
            'section_notes': 'NOTAS E INTERPRETACI\u00d3N',
            'id': 'ID Ficha',
            'site': 'Sitio',
            'area': '\u00c1rea',
            'trench': 'Sondeo',
            'su': 'UE',
            'su_dating': 'Dataci\u00f3n UE',
            'recorder': 'Responsable',
            'date': 'Fecha Compilaci\u00f3n',
            'recovery_method': 'M\u00e9todo Recuperaci\u00f3n',
            'context': 'Contexto',
            'context_desc': 'Descripci\u00f3n Contexto',
            'photo_doc': 'Doc. Fotogr\u00e1fica',
            'anatomical_conn': 'Conexi\u00f3n Anat\u00f3mica',
            'accumulation_type': 'Tipo Acumulaci\u00f3n',
            'deposition': 'Deposici\u00f3n',
            'estimated_number': 'N\u00famero Estimado',
            'mni': 'NMI',
            'reliability': 'Fiabilidad Estrat.',
            'species': 'Especie',
            'skeletal_parts': 'Elementos Esquel\u00e9ticos',
            'species_psi': 'Especie PSI',
            'element': 'Elemento',
            'bone_measurements': 'Medidas \u00d3seas',
            'fragmentation': 'Fragmentaci\u00f3n',
            'preservation': 'Estado Conservaci\u00f3n',
            'alterations': 'Alteraciones Morf.',
            'burning_traces': 'Trazas Combusti\u00f3n',
            'burning_type': 'Tipo Combusti\u00f3n',
            'other_burned': 'Otros Mat. Quemados',
            'taphonomic_signs': 'Se\u00f1ales Tafon\u00f3micas',
            'taphonomic_char': 'Caracterizaci\u00f3n Tafon\u00f3mica',
            'position_notes': 'Notas Posici\u00f3n',
            'sampling': 'Muestreos',
            'associated_finds': 'Materiales Asociados',
            'observations': 'Observaciones',
            'interpretation': 'Interpretaci\u00f3n',
            'generated': 'Generado el',
            'yes': 'S\u00ed',
            'no': 'No'
        }
        return self._create_professional_sheet(labels)

    def create_sheet_ar(self):
        """Arabic version of the sheet"""
        labels = {
            'title': '\u0628\u0637\u0627\u0642\u0629 \u0627\u0644\u062d\u064a\u0648\u0627\u0646\u0627\u062a \u0627\u0644\u0623\u062b\u0631\u064a\u0629',
            'section_record': '\u0628\u064a\u0627\u0646\u0627\u062a \u0627\u0644\u062a\u0639\u0631\u064a\u0641',
            'section_context': '\u0627\u0644\u0633\u064a\u0627\u0642 \u0648\u0627\u0644\u0645\u0646\u0647\u062c\u064a\u0629',
            'section_deposit': '\u062e\u0635\u0627\u0626\u0635 \u0627\u0644\u0631\u0648\u0627\u0633\u0628',
            'section_taxonomy': '\u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a \u0627\u0644\u062a\u0635\u0646\u064a\u0641\u064a\u0629',
            'section_taphonomy': '\u0627\u0644\u062a\u0627\u0641\u0648\u0646\u0648\u0645\u064a\u0627 \u0648\u0627\u0644\u062d\u0641\u0638',
            'section_notes': '\u0627\u0644\u0645\u0644\u0627\u062d\u0638\u0627\u062a \u0648\u0627\u0644\u062a\u0641\u0633\u064a\u0631',
            'id': '\u0631\u0642\u0645 \u0627\u0644\u0628\u0637\u0627\u0642\u0629',
            'site': '\u0627\u0644\u0645\u0648\u0642\u0639',
            'area': '\u0627\u0644\u0645\u0646\u0637\u0642\u0629',
            'trench': '\u0627\u0644\u0645\u062c\u0633',
            'su': '\u0648.\u0637',
            'su_dating': '\u062a\u0623\u0631\u064a\u062e \u0648.\u0637',
            'recorder': '\u0627\u0644\u0645\u0633\u0624\u0648\u0644',
            'date': '\u062a\u0627\u0631\u064a\u062e \u0627\u0644\u062a\u062c\u0645\u064a\u0639',
            'recovery_method': '\u0637\u0631\u064a\u0642\u0629 \u0627\u0644\u0627\u0633\u062a\u0631\u062f\u0627\u062f',
            'context': '\u0627\u0644\u0633\u064a\u0627\u0642',
            'context_desc': '\u0648\u0635\u0641 \u0627\u0644\u0633\u064a\u0627\u0642',
            'photo_doc': '\u0627\u0644\u062a\u0648\u062b\u064a\u0642 \u0627\u0644\u0641\u0648\u062a\u0648\u063a\u0631\u0627\u0641\u064a',
            'anatomical_conn': '\u0627\u0644\u0627\u062a\u0635\u0627\u0644 \u0627\u0644\u062a\u0634\u0631\u064a\u062d\u064a',
            'accumulation_type': '\u0646\u0648\u0639 \u0627\u0644\u062a\u0631\u0627\u0643\u0645',
            'deposition': '\u0627\u0644\u062a\u0631\u0633\u064a\u0628',
            'estimated_number': '\u0627\u0644\u0639\u062f\u062f \u0627\u0644\u0645\u0642\u062f\u0631',
            'mni': '\u0627\u0644\u062d\u062f \u0627\u0644\u0623\u062f\u0646\u0649',
            'reliability': '\u0627\u0644\u0645\u0648\u062b\u0648\u0642\u064a\u0629 \u0627\u0644\u0637\u0628\u0642\u064a\u0629',
            'species': '\u0627\u0644\u0623\u0646\u0648\u0627\u0639',
            'skeletal_parts': '\u0639\u0646\u0627\u0635\u0631 \u0627\u0644\u0647\u064a\u0643\u0644 \u0627\u0644\u0639\u0638\u0645\u064a',
            'species_psi': '\u0623\u0646\u0648\u0627\u0639 PSI',
            'element': '\u0627\u0644\u0639\u0646\u0635\u0631',
            'bone_measurements': '\u0642\u064a\u0627\u0633\u0627\u062a \u0627\u0644\u0639\u0638\u0627\u0645',
            'fragmentation': '\u0627\u0644\u062a\u062c\u0632\u0626\u0629',
            'preservation': '\u062d\u0627\u0644\u0629 \u0627\u0644\u062d\u0641\u0638',
            'alterations': '\u0627\u0644\u062a\u063a\u064a\u0631\u0627\u062a \u0627\u0644\u0645\u0648\u0631\u0641\u0648\u0644\u0648\u062c\u064a\u0629',
            'burning_traces': '\u0622\u062b\u0627\u0631 \u0627\u0644\u0627\u062d\u062a\u0631\u0627\u0642',
            'burning_type': '\u0646\u0648\u0639 \u0627\u0644\u0627\u062d\u062a\u0631\u0627\u0642',
            'other_burned': '\u0645\u0648\u0627\u062f \u0645\u062d\u062a\u0631\u0642\u0629 \u0623\u062e\u0631\u0649',
            'taphonomic_signs': '\u0639\u0644\u0627\u0645\u0627\u062a \u0627\u0644\u062a\u0627\u0641\u0648\u0646\u0648\u0645\u064a\u0629',
            'taphonomic_char': '\u0648\u0635\u0641 \u0627\u0644\u062a\u0627\u0641\u0648\u0646\u0648\u0645\u064a\u0629',
            'position_notes': '\u0645\u0644\u0627\u062d\u0638\u0627\u062a \u0627\u0644\u0645\u0648\u0642\u0639',
            'sampling': '\u0623\u062e\u0630 \u0627\u0644\u0639\u064a\u0646\u0627\u062a',
            'associated_finds': '\u0627\u0644\u0644\u0642\u0649 \u0627\u0644\u0645\u0631\u062a\u0628\u0637\u0629',
            'observations': '\u0627\u0644\u0645\u0644\u0627\u062d\u0638\u0627\u062a',
            'interpretation': '\u0627\u0644\u062a\u0641\u0633\u064a\u0631',
            'generated': '\u062a\u0645 \u0625\u0646\u0634\u0627\u0624\u0647 \u0641\u064a',
            'yes': '\u0646\u0639\u0645',
            'no': '\u0644\u0627'
        }
        return self._create_professional_sheet(labels)

    def create_sheet_ca(self):
        """Catalan version of the sheet"""
        labels = {
            'title': 'FITXA DE FAUNA ARQUEOL\u00d2GICA',
            'section_record': 'DADES D\'IDENTIFICACI\u00d3',
            'section_context': 'CONTEXT I METODOLOGIA',
            'section_deposit': 'CARACTER\u00cdSTIQUES DEL DIP\u00d2SIT',
            'section_taxonomy': 'DADES TAXON\u00d2MIQUES',
            'section_taphonomy': 'TAFONOMIA I CONSERVACI\u00d3',
            'section_notes': 'NOTES I INTERPRETACI\u00d3',
            'id': 'ID Fitxa',
            'site': 'Jaciment',
            'area': '\u00c0rea',
            'trench': 'Sondeig',
            'su': 'UE',
            'su_dating': 'Dataci\u00f3 UE',
            'recorder': 'Responsable',
            'date': 'Data Compilaci\u00f3',
            'recovery_method': 'M\u00e8tode Recuperaci\u00f3',
            'context': 'Context',
            'context_desc': 'Descripci\u00f3 Context',
            'photo_doc': 'Doc. Fotogr\u00e0fica',
            'anatomical_conn': 'Connexi\u00f3 Anat\u00f2mica',
            'accumulation_type': 'Tipus Acumulaci\u00f3',
            'deposition': 'Deposici\u00f3',
            'estimated_number': 'Nombre Estimat',
            'mni': 'NMI',
            'reliability': 'Fiabilitat Estrat.',
            'species': 'Esp\u00e8cie',
            'skeletal_parts': 'Elements Esquel\u00e8tics',
            'species_psi': 'Esp\u00e8cie PSI',
            'element': 'Element',
            'bone_measurements': 'Mesures \u00d2ssies',
            'fragmentation': 'Fragmentaci\u00f3',
            'preservation': 'Estat Conservaci\u00f3',
            'alterations': 'Alteracions Morf.',
            'burning_traces': 'Traces de Combusti\u00f3',
            'burning_type': 'Tipus Combusti\u00f3',
            'other_burned': 'Altres Mat. Cremats',
            'taphonomic_signs': 'Senyals Tafon\u00f2miques',
            'taphonomic_char': 'Caracteritzaci\u00f3 Tafon\u00f2mica',
            'position_notes': 'Notes Posici\u00f3',
            'sampling': 'Mostreigs',
            'associated_finds': 'Materials Associats',
            'observations': 'Observacions',
            'interpretation': 'Interpretaci\u00f3',
            'generated': 'Generat el',
            'yes': 'S\u00ed',
            'no': 'No'
        }
        return self._create_professional_sheet(labels)


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
        doc = SimpleDocTemplate(f, pagesize=A4,
                                leftMargin=MARGIN_LEFT, rightMargin=MARGIN_RIGHT,
                                topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM)

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
        doc = SimpleDocTemplate(f, pagesize=A4,
                                leftMargin=MARGIN_LEFT, rightMargin=MARGIN_RIGHT,
                                topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM)

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
        doc = SimpleDocTemplate(f, pagesize=A4,
                                leftMargin=MARGIN_LEFT, rightMargin=MARGIN_RIGHT,
                                topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM)

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
        doc = SimpleDocTemplate(f, pagesize=A4,
                                leftMargin=MARGIN_LEFT, rightMargin=MARGIN_RIGHT,
                                topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM)

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
        doc = SimpleDocTemplate(f, pagesize=A4,
                                leftMargin=MARGIN_LEFT, rightMargin=MARGIN_RIGHT,
                                topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM)

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
        doc = SimpleDocTemplate(f, pagesize=A4,
                                leftMargin=MARGIN_LEFT, rightMargin=MARGIN_RIGHT,
                                topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM)

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
        doc = SimpleDocTemplate(f, pagesize=A4,
                                leftMargin=MARGIN_LEFT, rightMargin=MARGIN_RIGHT,
                                topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM)

        story = []
        for i in range(len(records)):
            single_fauna_sheet = single_Fauna_pdf_sheet(records[i])
            story.append(single_fauna_sheet.create_sheet_ca())
            story.append(PageBreak())

        doc.build(story, canvasmaker=NumberedCanvas_Faunasheet)
        f.close()
