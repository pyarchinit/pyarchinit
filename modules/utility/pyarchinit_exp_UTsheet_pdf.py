#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyArchInit UT PDF Sheet Generator - Modern Layout

Generates professional PDF sheets for Unità Topografica (UT) records.
Supports 7 languages: IT, EN, DE, ES, FR, AR, CA

Features:
- Modern full-page layout
- All fields including survey and analysis data
- Individual sheets and list export
- Color-coded sections
"""

import os
from datetime import date, datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# Try to register fonts
try:
    pdfmetrics.registerFont(TTFont('Cambria', 'Cambria.ttc'))
    pdfmetrics.registerFont(TTFont('CambriaBold', 'cambriab.ttf'))
    registerFontFamily('Cambria', normal='Cambria', bold='CambriaBold')
    DEFAULT_FONT = 'Cambria'
except:
    DEFAULT_FONT = 'Helvetica'

from ..db.pyarchinit_conn_strings import Connection
from .pyarchinit_OS_utility import *

# Page dimensions
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 1.2 * cm
USABLE_WIDTH = PAGE_WIDTH - 2 * MARGIN

# Modern color scheme
COLORS = {
    'header_bg': colors.HexColor('#2C3E50'),      # Dark blue-gray
    'header_text': colors.white,
    'section_bg': colors.HexColor('#3498DB'),     # Blue
    'section_text': colors.white,
    'subsection_bg': colors.HexColor('#ECF0F1'),  # Light gray
    'label_bg': colors.HexColor('#F8F9FA'),       # Very light gray
    'value_bg': colors.white,
    'border': colors.HexColor('#BDC3C7'),         # Medium gray
    'potential_high': colors.HexColor('#27AE60'), # Green
    'potential_med': colors.HexColor('#F39C12'),  # Orange
    'potential_low': colors.HexColor('#95A5A6'),  # Gray
    'risk_high': colors.HexColor('#E74C3C'),      # Red
    'risk_med': colors.HexColor('#F39C12'),       # Orange
    'risk_low': colors.HexColor('#27AE60'),       # Green
}

# Labels for multiple languages
LABELS = {
    'IT': {
        'title': 'SCHEDA UNITÀ TOPOGRAFICA',
        'list_title': 'ELENCO UNITÀ TOPOGRAFICHE',
        'section_id': 'IDENTIFICAZIONE',
        'section_location': 'LOCALIZZAZIONE',
        'section_terrain': 'CARATTERISTICHE DEL TERRENO',
        'section_survey': 'DATI RICOGNIZIONE',
        'section_chronology': 'CRONOLOGIA E INTERPRETAZIONE',
        'section_analysis': 'ANALISI POTENZIALE/RISCHIO',
        'section_docs': 'DOCUMENTAZIONE',
        'project': 'Progetto',
        'ut_number': 'N° UT',
        'ut_literal': 'UT Letterale',
        'definition': 'Definizione',
        'description': 'Descrizione',
        'interpretation': 'Interpretazione',
        'nation': 'Nazione',
        'region': 'Regione',
        'province': 'Provincia',
        'municipality': 'Comune',
        'hamlet': 'Frazione',
        'locality': 'Località',
        'address': 'Indirizzo',
        'civic_number': 'N° Civico',
        'igm_map': 'Carta IGM',
        'ctr_map': 'Carta CTR',
        'cadastral_sheet': 'Foglio Catastale',
        'geo_coords': 'Coordinate Geografiche',
        'plane_coords': 'Coordinate Piane',
        'altitude': 'Quota (m)',
        'slope': 'Pendenza',
        'land_use': 'Uso del Suolo',
        'soil_desc': 'Descrizione Suolo',
        'place_desc': 'Descrizione Luogo',
        'survey_method': 'Metodo Ricognizione',
        'geometry': 'Geometria',
        'dimensions': 'Dimensioni',
        'date': 'Data',
        'time_weather': 'Ora e Meteo',
        'responsible': 'Responsabile',
        'visibility': 'Visibilità (%)',
        'vegetation': 'Copertura Vegetale',
        'gps_method': 'Metodo GPS',
        'gps_precision': 'Precisione GPS (m)',
        'survey_type': 'Tipo Survey',
        'surface_cond': 'Condizione Superficie',
        'accessibility': 'Accessibilità',
        'photo_doc': 'Doc. Fotografica',
        'weather': 'Condizioni Meteo',
        'team': 'Team Survey',
        'finds_sqm': 'Reperti per m²',
        'dating_finds': 'Reperti Datanti',
        'period_1': 'Periodo I',
        'dating_1': 'Datazione I',
        'interp_1': 'Interpretazione I',
        'period_2': 'Periodo II',
        'dating_2': 'Datazione II',
        'interp_2': 'Interpretazione II',
        'potential_score': 'Potenziale Archeologico',
        'risk_score': 'Rischio Archeologico',
        'analysis_date': 'Data Analisi',
        'analysis_method': 'Metodo Analisi',
        'bibliography': 'Bibliografia',
        'documentation': 'Documentazione',
        'protection': 'Vincoli e Tutela',
        'prelim_surveys': 'Indagini Preliminari',
        'page': 'Pag.',
        'of': 'di',
        'generated': 'Generato il',
        'yes': 'Sì',
        'no': 'No',
    },
    'EN': {
        'title': 'TOPOGRAPHIC UNIT SHEET',
        'list_title': 'TOPOGRAPHIC UNITS LIST',
        'section_id': 'IDENTIFICATION',
        'section_location': 'LOCATION',
        'section_terrain': 'TERRAIN CHARACTERISTICS',
        'section_survey': 'SURVEY DATA',
        'section_chronology': 'CHRONOLOGY AND INTERPRETATION',
        'section_analysis': 'POTENTIAL/RISK ANALYSIS',
        'section_docs': 'DOCUMENTATION',
        'project': 'Project',
        'ut_number': 'UT No.',
        'ut_literal': 'UT Literal',
        'definition': 'Definition',
        'description': 'Description',
        'interpretation': 'Interpretation',
        'nation': 'Nation',
        'region': 'Region',
        'province': 'Province',
        'municipality': 'Municipality',
        'hamlet': 'Hamlet',
        'locality': 'Locality',
        'address': 'Address',
        'civic_number': 'Civic No.',
        'igm_map': 'IGM Map',
        'ctr_map': 'CTR Map',
        'cadastral_sheet': 'Cadastral Sheet',
        'geo_coords': 'Geographic Coordinates',
        'plane_coords': 'Plane Coordinates',
        'altitude': 'Altitude (m)',
        'slope': 'Slope',
        'land_use': 'Land Use',
        'soil_desc': 'Soil Description',
        'place_desc': 'Place Description',
        'survey_method': 'Survey Method',
        'geometry': 'Geometry',
        'dimensions': 'Dimensions',
        'date': 'Date',
        'time_weather': 'Time & Weather',
        'responsible': 'Responsible',
        'visibility': 'Visibility (%)',
        'vegetation': 'Vegetation Cover',
        'gps_method': 'GPS Method',
        'gps_precision': 'GPS Precision (m)',
        'survey_type': 'Survey Type',
        'surface_cond': 'Surface Condition',
        'accessibility': 'Accessibility',
        'photo_doc': 'Photo Documentation',
        'weather': 'Weather Conditions',
        'team': 'Survey Team',
        'finds_sqm': 'Finds per m²',
        'dating_finds': 'Dating Finds',
        'period_1': 'Period I',
        'dating_1': 'Dating I',
        'interp_1': 'Interpretation I',
        'period_2': 'Period II',
        'dating_2': 'Dating II',
        'interp_2': 'Interpretation II',
        'potential_score': 'Archaeological Potential',
        'risk_score': 'Archaeological Risk',
        'analysis_date': 'Analysis Date',
        'analysis_method': 'Analysis Method',
        'bibliography': 'Bibliography',
        'documentation': 'Documentation',
        'protection': 'Protection & Constraints',
        'prelim_surveys': 'Preliminary Surveys',
        'page': 'Page',
        'of': 'of',
        'generated': 'Generated on',
        'yes': 'Yes',
        'no': 'No',
    },
    'DE': {
        'title': 'TOPOGRAFISCHE EINHEIT FORMULAR',
        'list_title': 'TOPOGRAFISCHE EINHEITEN LISTE',
        'section_id': 'IDENTIFIKATION',
        'section_location': 'LOKALISIERUNG',
        'section_terrain': 'GELÄNDEMERKMALE',
        'section_survey': 'SURVEY-DATEN',
        'section_chronology': 'CHRONOLOGIE UND INTERPRETATION',
        'section_analysis': 'POTENTIAL/RISIKO ANALYSE',
        'section_docs': 'DOKUMENTATION',
        'project': 'Projekt',
        'ut_number': 'TE Nr.',
        'definition': 'Definition',
        'description': 'Beschreibung',
        'interpretation': 'Interpretation',
        'nation': 'Nation',
        'region': 'Region',
        'province': 'Provinz',
        'municipality': 'Gemeinde',
        'page': 'Seite',
        'of': 'von',
        'generated': 'Erstellt am',
        'yes': 'Ja',
        'no': 'Nein',
    }
}

# Add missing keys with Italian fallback
for lang in ['DE', 'ES', 'FR', 'AR', 'CA']:
    if lang not in LABELS:
        LABELS[lang] = LABELS['IT'].copy()
    else:
        for key in LABELS['IT']:
            if key not in LABELS[lang]:
                LABELS[lang][key] = LABELS['IT'][key]


def get_label(key, lang='IT'):
    """Get label for key in specified language."""
    return LABELS.get(lang, LABELS['IT']).get(key, LABELS['IT'].get(key, key))


class NumberedCanvas(canvas.Canvas):
    """Canvas with page numbers."""

    def __init__(self, *args, **kwargs):
        self.lang = kwargs.pop('lang', 'IT')
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont(DEFAULT_FONT, 8)
        page_label = get_label('page', self.lang)
        of_label = get_label('of', self.lang)
        self.drawRightString(
            PAGE_WIDTH - MARGIN, MARGIN / 2,
            f"{page_label} {self._pageNumber} {of_label} {page_count}"
        )


class single_UT_pdf_sheet:
    """Generates a single UT PDF sheet with modern layout."""

    def __init__(self, data):
        """Initialize with data tuple from database."""
        self.progetto = str(data[0]) if data[0] else ''
        self.nr_ut = str(data[1]) if data[1] else ''
        self.ut_letterale = str(data[2]) if len(data) > 2 and data[2] else ''
        self.def_ut = str(data[3]) if len(data) > 3 and data[3] else ''
        self.descrizione_ut = str(data[4]) if len(data) > 4 and data[4] else ''
        self.interpretazione_ut = str(data[5]) if len(data) > 5 and data[5] else ''
        self.nazione = str(data[6]) if len(data) > 6 and data[6] else ''
        self.regione = str(data[7]) if len(data) > 7 and data[7] else ''
        self.provincia = str(data[8]) if len(data) > 8 and data[8] else ''
        self.comune = str(data[9]) if len(data) > 9 and data[9] else ''
        self.frazione = str(data[10]) if len(data) > 10 and data[10] else ''
        self.localita = str(data[11]) if len(data) > 11 and data[11] else ''
        self.indirizzo = str(data[12]) if len(data) > 12 and data[12] else ''
        self.nr_civico = str(data[13]) if len(data) > 13 and data[13] else ''
        self.carta_topo_igm = str(data[14]) if len(data) > 14 and data[14] else ''
        self.carta_ctr = str(data[15]) if len(data) > 15 and data[15] else ''
        self.coord_geografiche = str(data[16]) if len(data) > 16 and data[16] else ''
        self.coord_piane = str(data[17]) if len(data) > 17 and data[17] else ''
        self.quota = str(data[18]) if len(data) > 18 and data[18] is not None else ''
        self.andamento_terreno_pendenza = str(data[19]) if len(data) > 19 and data[19] else ''
        self.utilizzo_suolo_vegetazione = str(data[20]) if len(data) > 20 and data[20] else ''
        self.descrizione_empirica_suolo = str(data[21]) if len(data) > 21 and data[21] else ''
        self.descrizione_luogo = str(data[22]) if len(data) > 22 and data[22] else ''
        self.metodo_rilievo_e_ricognizione = str(data[23]) if len(data) > 23 and data[23] else ''
        self.geometria = str(data[24]) if len(data) > 24 and data[24] else ''
        self.bibliografia = str(data[25]) if len(data) > 25 and data[25] else ''
        self.data = str(data[26]) if len(data) > 26 and data[26] else ''
        self.ora_meteo = str(data[27]) if len(data) > 27 and data[27] else ''
        self.responsabile = str(data[28]) if len(data) > 28 and data[28] else ''
        self.dimensioni_ut = str(data[29]) if len(data) > 29 and data[29] else ''
        self.rep_per_mq = str(data[30]) if len(data) > 30 and data[30] else ''
        self.rep_datanti = str(data[31]) if len(data) > 31 and data[31] else ''
        self.periodo_I = str(data[32]) if len(data) > 32 and data[32] else ''
        self.datazione_I = str(data[33]) if len(data) > 33 and data[33] else ''
        self.interpretazione_I = str(data[34]) if len(data) > 34 and data[34] else ''
        self.periodo_II = str(data[35]) if len(data) > 35 and data[35] else ''
        self.datazione_II = str(data[36]) if len(data) > 36 and data[36] else ''
        self.interpretazione_II = str(data[37]) if len(data) > 37 and data[37] else ''
        self.documentazione = str(data[38]) if len(data) > 38 and data[38] else ''
        self.enti_tutela_vincoli = str(data[39]) if len(data) > 39 and data[39] else ''
        self.indagini_preliminari = str(data[40]) if len(data) > 40 and data[40] else ''

        # Survey fields (v4.9.21+)
        self.visibility_percent = str(data[41]) if len(data) > 41 and data[41] is not None else ''
        self.vegetation_coverage = str(data[42]) if len(data) > 42 and data[42] else ''
        self.gps_method = str(data[43]) if len(data) > 43 and data[43] else ''
        self.coordinate_precision = str(data[44]) if len(data) > 44 and data[44] is not None else ''
        self.survey_type = str(data[45]) if len(data) > 45 and data[45] else ''
        self.surface_condition = str(data[46]) if len(data) > 46 and data[46] else ''
        self.accessibility = str(data[47]) if len(data) > 47 and data[47] else ''
        self.photo_documentation = str(data[48]) if len(data) > 48 and data[48] is not None else ''
        self.weather_conditions = str(data[49]) if len(data) > 49 and data[49] else ''
        self.team_members = str(data[50]) if len(data) > 50 and data[50] else ''
        self.foglio_catastale = str(data[51]) if len(data) > 51 and data[51] else ''

        # Analysis fields (v4.9.67+)
        self.potential_score = str(data[52]) if len(data) > 52 and data[52] is not None else ''
        self.risk_score = str(data[53]) if len(data) > 53 and data[53] is not None else ''
        self.potential_factors = str(data[54]) if len(data) > 54 and data[54] else ''
        self.risk_factors = str(data[55]) if len(data) > 55 and data[55] else ''
        self.analysis_date = str(data[56]) if len(data) > 56 and data[56] else ''
        self.analysis_method = str(data[57]) if len(data) > 57 and data[57] else ''

    def create_sheet(self, lang='IT'):
        """Create the PDF sheet elements."""
        elements = []

        # Styles
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'Title', parent=styles['Normal'],
            fontName=DEFAULT_FONT, fontSize=14, alignment=TA_CENTER,
            textColor=colors.white, spaceAfter=0
        )

        section_style = ParagraphStyle(
            'Section', parent=styles['Normal'],
            fontName=DEFAULT_FONT, fontSize=9, alignment=TA_LEFT,
            textColor=colors.white, spaceBefore=0, spaceAfter=0
        )

        label_style = ParagraphStyle(
            'Label', parent=styles['Normal'],
            fontName=DEFAULT_FONT, fontSize=7, alignment=TA_LEFT,
            textColor=colors.HexColor('#2C3E50'), spaceBefore=1, spaceAfter=1
        )

        value_style = ParagraphStyle(
            'Value', parent=styles['Normal'],
            fontName=DEFAULT_FONT, fontSize=8, alignment=TA_LEFT,
            spaceBefore=1, spaceAfter=1
        )

        desc_style = ParagraphStyle(
            'Description', parent=styles['Normal'],
            fontName=DEFAULT_FONT, fontSize=8, alignment=TA_JUSTIFY,
            spaceBefore=2, spaceAfter=2
        )

        # Helper functions
        def make_header():
            """Create header with logo and title."""
            home = os.environ.get('PYARCHINIT_HOME', '')
            conn = Connection()
            lo_path = conn.logo_path()
            lo_path_str = lo_path.get('logo', '')

            if lo_path_str and os.path.exists(lo_path_str):
                logo_path = lo_path_str
            else:
                logo_path = os.path.join(home, 'pyarchinit_DB_folder', 'logo.jpg')

            logo_cell = ''
            if os.path.exists(logo_path):
                try:
                    logo = Image(logo_path)
                    logo.drawHeight = 1.5 * cm
                    logo.drawWidth = 1.5 * cm * logo.drawWidth / logo.drawHeight
                    logo_cell = logo
                except:
                    logo_cell = ''

            title_text = get_label('title', lang)
            today = date.today().strftime("%d/%m/%Y")

            header_data = [[
                logo_cell,
                Paragraph(f"<b>{title_text}</b>", title_style),
                Paragraph(f"<b>UT {self.nr_ut}</b><br/>{today}", title_style)
            ]]

            header_table = Table(header_data, colWidths=[2*cm, USABLE_WIDTH - 5*cm, 3*cm])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), COLORS['header_bg']),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            return header_table

        def make_section_header(text):
            """Create a section header."""
            data = [[Paragraph(f"<b>{text}</b>", section_style)]]
            table = Table(data, colWidths=[USABLE_WIDTH])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), COLORS['section_bg']),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ]))
            return table

        def make_field_row(fields, widths=None):
            """Create a row with label-value pairs."""
            if widths is None:
                col_width = USABLE_WIDTH / len(fields)
                widths = [col_width] * len(fields)

            row_data = []
            for label, value in fields:
                cell_content = Paragraph(
                    f"<b>{label}</b><br/>{value if value else '-'}",
                    label_style
                )
                row_data.append(cell_content)

            table = Table([row_data], colWidths=widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), COLORS['label_bg']),
                ('BOX', (0, 0), (-1, -1), 0.5, COLORS['border']),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            return table

        def make_text_field(label, value):
            """Create a text field spanning full width."""
            data = [[Paragraph(f"<b>{label}</b>", label_style)],
                    [Paragraph(value if value else '-', desc_style)]]
            table = Table(data, colWidths=[USABLE_WIDTH])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), COLORS['subsection_bg']),
                ('BACKGROUND', (0, 1), (0, 1), COLORS['value_bg']),
                ('BOX', (0, 0), (-1, -1), 0.5, COLORS['border']),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ]))
            return table

        def make_score_display(label, score, score_type='potential'):
            """Create a colored score display."""
            try:
                score_val = float(score) if score else 0
            except:
                score_val = 0

            if score_type == 'potential':
                if score_val >= 70:
                    bg_color = COLORS['potential_high']
                elif score_val >= 40:
                    bg_color = COLORS['potential_med']
                else:
                    bg_color = COLORS['potential_low']
            else:  # risk
                if score_val >= 70:
                    bg_color = COLORS['risk_high']
                elif score_val >= 40:
                    bg_color = COLORS['risk_med']
                else:
                    bg_color = COLORS['risk_low']

            score_text = f"{score_val:.1f}/100" if score else "-"
            data = [[
                Paragraph(f"<b>{label}</b>", label_style),
                Paragraph(f"<b>{score_text}</b>",
                         ParagraphStyle('Score', fontSize=12, alignment=TA_CENTER, textColor=colors.white))
            ]]
            table = Table(data, colWidths=[USABLE_WIDTH * 0.6, USABLE_WIDTH * 0.4])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), COLORS['label_bg']),
                ('BACKGROUND', (1, 0), (1, 0), bg_color),
                ('BOX', (0, 0), (-1, -1), 0.5, COLORS['border']),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            return table

        # Build the sheet
        elements.append(make_header())
        elements.append(Spacer(1, 0.3 * cm))

        # SECTION 1: Identification
        elements.append(make_section_header(get_label('section_id', lang)))
        elements.append(make_field_row([
            (get_label('project', lang), self.progetto),
            (get_label('ut_number', lang), self.nr_ut),
            (get_label('definition', lang), self.def_ut),
            (get_label('geometry', lang), self.geometria),
        ]))
        elements.append(make_text_field(get_label('description', lang), self.descrizione_ut))
        elements.append(make_text_field(get_label('interpretation', lang), self.interpretazione_ut))
        elements.append(Spacer(1, 0.2 * cm))

        # SECTION 2: Location
        elements.append(make_section_header(get_label('section_location', lang)))
        elements.append(make_field_row([
            (get_label('nation', lang), self.nazione),
            (get_label('region', lang), self.regione),
            (get_label('province', lang), self.provincia),
            (get_label('municipality', lang), self.comune),
        ]))
        elements.append(make_field_row([
            (get_label('hamlet', lang), self.frazione),
            (get_label('locality', lang), self.localita),
            (get_label('address', lang), self.indirizzo),
            (get_label('civic_number', lang), self.nr_civico),
        ]))
        elements.append(make_field_row([
            (get_label('igm_map', lang), self.carta_topo_igm),
            (get_label('ctr_map', lang), self.carta_ctr),
            (get_label('cadastral_sheet', lang), self.foglio_catastale),
            (get_label('altitude', lang), self.quota),
        ]))
        elements.append(make_field_row([
            (get_label('geo_coords', lang), self.coord_geografiche),
            (get_label('plane_coords', lang), self.coord_piane),
        ], [USABLE_WIDTH * 0.5, USABLE_WIDTH * 0.5]))
        elements.append(Spacer(1, 0.2 * cm))

        # SECTION 3: Terrain
        elements.append(make_section_header(get_label('section_terrain', lang)))
        elements.append(make_field_row([
            (get_label('slope', lang), self.andamento_terreno_pendenza),
            (get_label('land_use', lang), self.utilizzo_suolo_vegetazione),
            (get_label('dimensions', lang), self.dimensioni_ut),
        ]))
        elements.append(make_text_field(get_label('soil_desc', lang), self.descrizione_empirica_suolo))
        elements.append(make_text_field(get_label('place_desc', lang), self.descrizione_luogo))
        elements.append(Spacer(1, 0.2 * cm))

        # SECTION 4: Survey Data
        elements.append(make_section_header(get_label('section_survey', lang)))
        elements.append(make_field_row([
            (get_label('date', lang), self.data),
            (get_label('responsible', lang), self.responsabile),
            (get_label('survey_method', lang), self.metodo_rilievo_e_ricognizione),
            (get_label('survey_type', lang), self.survey_type),
        ]))
        elements.append(make_field_row([
            (get_label('visibility', lang), self.visibility_percent),
            (get_label('vegetation', lang), self.vegetation_coverage),
            (get_label('surface_cond', lang), self.surface_condition),
            (get_label('accessibility', lang), self.accessibility),
        ]))
        elements.append(make_field_row([
            (get_label('gps_method', lang), self.gps_method),
            (get_label('gps_precision', lang), self.coordinate_precision),
            (get_label('weather', lang), self.weather_conditions),
            (get_label('photo_doc', lang), get_label('yes', lang) if self.photo_documentation else get_label('no', lang)),
        ]))
        elements.append(make_field_row([
            (get_label('team', lang), self.team_members),
            (get_label('time_weather', lang), self.ora_meteo),
        ], [USABLE_WIDTH * 0.5, USABLE_WIDTH * 0.5]))
        elements.append(Spacer(1, 0.2 * cm))

        # SECTION 5: Chronology
        elements.append(make_section_header(get_label('section_chronology', lang)))
        elements.append(make_field_row([
            (get_label('finds_sqm', lang), self.rep_per_mq),
            (get_label('dating_finds', lang), self.rep_datanti),
        ], [USABLE_WIDTH * 0.5, USABLE_WIDTH * 0.5]))
        elements.append(make_field_row([
            (get_label('period_1', lang), self.periodo_I),
            (get_label('dating_1', lang), self.datazione_I),
            (get_label('interp_1', lang), self.interpretazione_I),
        ]))
        elements.append(make_field_row([
            (get_label('period_2', lang), self.periodo_II),
            (get_label('dating_2', lang), self.datazione_II),
            (get_label('interp_2', lang), self.interpretazione_II),
        ]))
        elements.append(Spacer(1, 0.2 * cm))

        # SECTION 6: Analysis (if available)
        if self.potential_score or self.risk_score:
            elements.append(make_section_header(get_label('section_analysis', lang)))

            analysis_data = [[
                make_score_display(get_label('potential_score', lang), self.potential_score, 'potential'),
                make_score_display(get_label('risk_score', lang), self.risk_score, 'risk'),
            ]]
            analysis_table = Table(analysis_data, colWidths=[USABLE_WIDTH * 0.5, USABLE_WIDTH * 0.5])
            analysis_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(analysis_table)

            if self.analysis_date or self.analysis_method:
                elements.append(make_field_row([
                    (get_label('analysis_date', lang), self.analysis_date),
                    (get_label('analysis_method', lang), self.analysis_method),
                ], [USABLE_WIDTH * 0.5, USABLE_WIDTH * 0.5]))
            elements.append(Spacer(1, 0.2 * cm))

        # SECTION 7: Documentation
        elements.append(make_section_header(get_label('section_docs', lang)))
        elements.append(make_text_field(get_label('bibliography', lang), self.bibliografia))
        elements.append(make_text_field(get_label('documentation', lang), self.documentazione))
        elements.append(make_field_row([
            (get_label('protection', lang), self.enti_tutela_vincoli),
            (get_label('prelim_surveys', lang), self.indagini_preliminari),
        ], [USABLE_WIDTH * 0.5, USABLE_WIDTH * 0.5]))

        return elements


class generate_pdf:
    """Main PDF generator class."""

    HOME = os.environ.get('PYARCHINIT_HOME', '')
    PDF_path = os.path.join(HOME, 'pyarchinit_PDF_folder')

    def __init__(self):
        if not os.path.exists(self.PDF_path):
            os.makedirs(self.PDF_path)

    def build_UT_sheets(self, records, lang='IT'):
        """Build PDF sheets for multiple UT records."""
        # Use language-appropriate filename
        filenames = {
            'IT': 'scheda_UT.pdf',
            'EN': 'Form_UT.pdf',
            'DE': 'Formular_TE.pdf',
            'FR': 'Fiche_UT.pdf',
            'ES': 'Ficha_UT.pdf',
            'AR': 'Bitaqa_UT.pdf',
            'CA': 'Fitxa_UT.pdf',
        }
        filename = filenames.get(lang, 'scheda_UT.pdf')
        self._build_sheets(records, filename, lang)

    def build_UT_sheets_en(self, records):
        """Build PDF sheets for multiple UT records (English)."""
        self._build_sheets(records, 'Form_UT.pdf', 'EN')

    def build_UT_sheets_de(self, records):
        """Build PDF sheets for multiple UT records (German)."""
        self._build_sheets(records, 'Formular_TE.pdf', 'DE')

    def build_UT_sheets_fr(self, records):
        """Build PDF sheets for multiple UT records (French)."""
        self._build_sheets(records, 'Fiche_UT.pdf', 'FR')

    def build_UT_sheets_es(self, records):
        """Build PDF sheets for multiple UT records (Spanish)."""
        self._build_sheets(records, 'Ficha_UT.pdf', 'ES')

    def build_UT_sheets_ar(self, records):
        """Build PDF sheets for multiple UT records (Arabic)."""
        self._build_sheets(records, 'Bitaqa_UT.pdf', 'AR')

    def build_UT_sheets_ca(self, records):
        """Build PDF sheets for multiple UT records (Catalan)."""
        self._build_sheets(records, 'Fitxa_UT.pdf', 'CA')

    def _build_sheets(self, records, filename, lang='IT'):
        """Build PDF sheets for records."""
        filepath = os.path.join(self.PDF_path, filename)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN * 1.5
        )

        elements = []
        for i, record in enumerate(records):
            sheet = single_UT_pdf_sheet(record)
            elements.extend(sheet.create_sheet(lang))
            if i < len(records) - 1:
                elements.append(PageBreak())

        doc.build(elements, canvasmaker=lambda *args, **kwargs: NumberedCanvas(*args, lang=kwargs.pop('lang', lang), **kwargs))

    def build_UT_list(self, records, lang='IT'):
        """Build a list/index of all UT records."""
        filename = 'Elenco_UT.pdf' if lang == 'IT' else 'UT_List.pdf'
        filepath = os.path.join(self.PDF_path, filename)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=landscape(A4),
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN * 1.5
        )

        elements = []

        # Title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title', parent=styles['Heading1'],
            fontName=DEFAULT_FONT, fontSize=16, alignment=TA_CENTER,
            spaceAfter=0.5 * cm
        )

        title = get_label('list_title', lang)
        today = date.today().strftime("%d/%m/%Y")
        elements.append(Paragraph(f"<b>{title}</b><br/><font size='10'>{today}</font>", title_style))
        elements.append(Spacer(1, 0.5 * cm))

        # Table header
        header_style = ParagraphStyle(
            'Header', fontName=DEFAULT_FONT, fontSize=7, alignment=TA_CENTER,
            textColor=colors.white
        )
        cell_style = ParagraphStyle(
            'Cell', fontName=DEFAULT_FONT, fontSize=7, alignment=TA_LEFT
        )

        # Column definitions
        page_width = landscape(A4)[0] - 2 * MARGIN
        col_widths = [
            page_width * 0.04,  # UT
            page_width * 0.10,  # Progetto
            page_width * 0.08,  # Definizione
            page_width * 0.18,  # Interpretazione
            page_width * 0.08,  # Comune
            page_width * 0.10,  # Coordinate
            page_width * 0.08,  # Periodo I
            page_width * 0.08,  # Periodo II
            page_width * 0.08,  # Rep/m²
            page_width * 0.06,  # Visib.
            page_width * 0.06,  # Potenz.
            page_width * 0.06,  # Rischio
        ]

        headers = [
            Paragraph('<b>UT</b>', header_style),
            Paragraph(f'<b>{get_label("project", lang)}</b>', header_style),
            Paragraph(f'<b>{get_label("definition", lang)}</b>', header_style),
            Paragraph(f'<b>{get_label("interpretation", lang)}</b>', header_style),
            Paragraph(f'<b>{get_label("municipality", lang)}</b>', header_style),
            Paragraph(f'<b>{get_label("geo_coords", lang)}</b>', header_style),
            Paragraph(f'<b>{get_label("period_1", lang)}</b>', header_style),
            Paragraph(f'<b>{get_label("period_2", lang)}</b>', header_style),
            Paragraph(f'<b>{get_label("finds_sqm", lang)}</b>', header_style),
            Paragraph(f'<b>{get_label("visibility", lang)[:5]}.</b>', header_style),
            Paragraph(f'<b>Pot.</b>', header_style),
            Paragraph(f'<b>Risk</b>', header_style),
        ]

        table_data = [headers]

        for record in records:
            row = [
                Paragraph(str(record[1]) if record[1] else '', cell_style),  # nr_ut
                Paragraph(str(record[0])[:15] if record[0] else '', cell_style),  # progetto
                Paragraph(str(record[3])[:12] if len(record) > 3 and record[3] else '', cell_style),  # def_ut
                Paragraph(str(record[5])[:25] if len(record) > 5 and record[5] else '', cell_style),  # interpretazione
                Paragraph(str(record[9])[:12] if len(record) > 9 and record[9] else '', cell_style),  # comune
                Paragraph(str(record[16])[:15] if len(record) > 16 and record[16] else '', cell_style),  # coord_geo
                Paragraph(str(record[32])[:10] if len(record) > 32 and record[32] else '', cell_style),  # periodo_I
                Paragraph(str(record[35])[:10] if len(record) > 35 and record[35] else '', cell_style),  # periodo_II
                Paragraph(str(record[30]) if len(record) > 30 and record[30] else '', cell_style),  # rep_per_mq
                Paragraph(str(record[41]) if len(record) > 41 and record[41] is not None else '', cell_style),  # visibility
                Paragraph(f"{float(record[52]):.0f}" if len(record) > 52 and record[52] is not None else '', cell_style),  # potential
                Paragraph(f"{float(record[53]):.0f}" if len(record) > 53 and record[53] is not None else '', cell_style),  # risk
            ]
            table_data.append(row)

        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['header_bg']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLORS['label_bg']]),
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
            # Alignment
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # UT column centered
            ('ALIGN', (-2, 0), (-1, -1), 'CENTER'),  # Scores centered
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ]))

        elements.append(table)

        # Footer with count
        elements.append(Spacer(1, 0.5 * cm))
        count_text = f"Totale: {len(records)} UT" if lang == 'IT' else f"Total: {len(records)} TU"
        elements.append(Paragraph(count_text, cell_style))

        doc.build(elements, canvasmaker=lambda *args, **kwargs: NumberedCanvas(*args, lang=kwargs.pop('lang', lang), **kwargs))

        return filepath
