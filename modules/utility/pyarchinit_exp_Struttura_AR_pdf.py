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

 PDF Export for Struttura with AR (Architettura Rupestre) layout
 Based on D'Amico model scheda AR - 3 pages fully filled
"""

import os
import ast
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, PageBreak, SimpleDocTemplate, Spacer, TableStyle, Image, KeepTogether
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont

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


class NumberedCanvas_Struttura_AR(canvas.Canvas):
    def __init__(self, *args, **kwargs):
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
        self.setFont("Helvetica", 8)
        self.drawRightString(200 * mm, 10 * mm,
                             "Pag. %d di %d" % (self._pageNumber, page_count))


class single_Struttura_AR_pdf_sheet:
    """PDF Sheet for Struttura with AR (Architettura Rupestre) layout - 3 pages"""

    def __init__(self, data):
        # Basic fields
        self.sito = data[0] if len(data) > 0 else ''
        self.sigla_struttura = data[1] if len(data) > 1 else ''
        self.numero_struttura = data[2] if len(data) > 2 else ''
        self.categoria_struttura = data[3] if len(data) > 3 else ''
        self.tipologia_struttura = data[4] if len(data) > 4 else ''
        self.definizione_struttura = data[5] if len(data) > 5 else ''
        self.descrizione = data[6] if len(data) > 6 else ''
        self.interpretazione = data[7] if len(data) > 7 else ''
        self.periodo_iniziale = data[8] if len(data) > 8 else ''
        self.fase_iniziale = data[9] if len(data) > 9 else ''
        self.periodo_finale = data[10] if len(data) > 10 else ''
        self.fase_finale = data[11] if len(data) > 11 else ''
        self.datazione_estesa = data[12] if len(data) > 12 else ''
        self.materiali_impiegati = data[13] if len(data) > 13 else '[]'
        self.elementi_strutturali = data[14] if len(data) > 14 else '[]'
        self.rapporti_struttura = data[15] if len(data) > 15 else '[]'
        self.misure_struttura = data[16] if len(data) > 16 else '[]'
        self.quota_min = data[17] if len(data) > 17 else ''
        self.quota_max = data[18] if len(data) > 18 else ''

        # Extended AR fields
        self.data_compilazione = data[19] if len(data) > 19 else ''
        self.nome_compilatore = data[20] if len(data) > 20 else ''
        self.stato_conservazione = data[21] if len(data) > 21 else '[]'
        self.quota = data[22] if len(data) > 22 else ''
        self.relazione_topografica = data[23] if len(data) > 23 else ''
        self.prospetto_ingresso = data[24] if len(data) > 24 else '[]'
        self.orientamento_ingresso = data[25] if len(data) > 25 else ''
        self.articolazione = data[26] if len(data) > 26 else ''
        self.n_ambienti = data[27] if len(data) > 27 else ''
        self.orientamento_ambienti = data[28] if len(data) > 28 else '[]'
        self.sviluppo_planimetrico = data[29] if len(data) > 29 else ''
        self.elementi_costitutivi = data[30] if len(data) > 30 else '[]'
        self.motivo_decorativo = data[31] if len(data) > 31 else ''
        self.potenzialita_archeologica = data[32] if len(data) > 32 else ''
        self.manufatti = data[33] if len(data) > 33 else '[]'
        self.elementi_datanti = data[34] if len(data) > 34 else ''
        self.fasi_funzionali = data[35] if len(data) > 35 else '[]'

        # id_struttura for image lookup
        self.id_struttura = data[36] if len(data) > 36 else None
        if self.id_struttura is None and hasattr(data, 'id_struttura'):
            self.id_struttura = data.id_struttura

    def datestrfdate(self):
        now = date.today()
        return now.strftime("%d-%m-%Y")

    def safe_str(self, val):
        if val is None or str(val) == 'None' or str(val) == '[]':
            return ''
        return str(val)

    def parse_table_data(self, data_str):
        try:
            if data_str and str(data_str) != 'None' and str(data_str) != '[]':
                return ast.literal_eval(str(data_str))
        except:
            pass
        return []

    def get_first_image(self):
        try:
            conn = Connection()
            thumb_path = conn.thumb_path()
            thumb_resize = conn.thumb_resize()

            search_dict = {
                'entity_type': '"STRUTTURA"',
                'nome_tabella': '"struttura_table"'
            }
            if self.id_struttura:
                search_dict['id_entity'] = int(self.id_struttura)

            DB_MANAGER = Pyarchinit_db_management(conn.conn_str())
            DB_MANAGER.connection()

            u = Utility()
            search_dict = u.remove_empty_items_fr_dict(search_dict)
            mediatoentity_res = DB_MANAGER.query_bool(search_dict, "MEDIATOENTITY")

            if mediatoentity_res:
                first_media = mediatoentity_res[0]
                search_dict_media = {'id_media': '"' + str(first_media.id_media) + '"'}
                media_data = DB_MANAGER.query_bool(search_dict_media, "MEDIA")

                if media_data:
                    thumb_resize_str = thumb_resize + os.sep
                    file_path = thumb_resize_str + str(media_data[0].path_resize)
                    if os.path.exists(file_path):
                        return file_path
        except:
            pass
        return None

    def _create_placeholder_image(self, width=5*cm, height=5*cm):
        placeholder = Table([
            [Paragraph("<i>Immagine<br/>non<br/>disponibile</i>",
                      ParagraphStyle('placeholder', fontSize=9, alignment=TA_CENTER))]
        ], colWidths=[width], rowHeights=[height])
        placeholder.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
        ]))
        return placeholder

    def create_sheet(self):
        return self._create_sheet_layout('it')

    def create_sheet_en(self):
        return self._create_sheet_layout('en')

    def create_sheet_de(self):
        return self._create_sheet_layout('de')

    def _create_sheet_layout(self, lang='it'):
        labels = {
            'it': {
                'title': 'SCHEDA STRUTTURA',
                'site': 'Sito', 'code': 'Sigla/N.', 'category': 'Categoria',
                'typology': 'Tipologia', 'definition': 'Definizione',
                'description': 'Descrizione', 'interpretation': 'Interpretazione',
                'period_start': 'Periodo iniz.', 'phase_start': 'Fase iniz.',
                'period_end': 'Periodo fin.', 'phase_end': 'Fase fin.',
                'extended_dating': 'Datazione estesa', 'materials': 'Materiali impiegati',
                'structural_elem': 'Elementi strutturali', 'relations': 'Rapporti struttura',
                'measurements': 'Misurazioni', 'elevation': 'Quote',
                'elev_min': 'Quota min', 'elev_max': 'Quota max',
                'compiler': 'Compilatore', 'date': 'Data compilazione',
                'conservation': 'Stato conservazione', 'topographic_rel': 'Relazione topografica',
                'entrance_facade': 'Prospetto ingresso', 'entrance_orient': 'Orient. ingresso',
                'articulation': 'Articolazione', 'n_rooms': 'N. ambienti',
                'room_orient': 'Orient. ambienti', 'planimetric_dev': 'Sviluppo planimetrico',
                'constituent_elem': 'Elementi costitutivi', 'decorative_motif': 'Motivo decorativo',
                'arch_potential': 'Potenzialità archeologica', 'artifacts': 'Manufatti',
                'dating_elements': 'Elementi datanti', 'functional_phases': 'Fasi funzionali',
                'periodization': 'PERIODIZZAZIONE', 'initial': 'INIZIALE', 'final': 'FINALE',
                'identification': 'DATI IDENTIFICATIVI', 'classification': 'CLASSIFICAZIONE',
                'spatial_data': 'DATI SPAZIALI', 'chronology': 'CRONOLOGIA',
                'components': 'COMPONENTI E MATERIALI', 'archaeological': 'DATI ARCHEOLOGICI',
            },
            'en': {
                'title': 'STRUCTURE FORM',
                'site': 'Site', 'code': 'Code/Nr.', 'category': 'Category',
                'typology': 'Typology', 'definition': 'Definition',
                'description': 'Description', 'interpretation': 'Interpretation',
                'period_start': 'Start Period', 'phase_start': 'Start Phase',
                'period_end': 'End Period', 'phase_end': 'End Phase',
                'extended_dating': 'Extended Dating', 'materials': 'Materials Used',
                'structural_elem': 'Structural Elements', 'relations': 'Structure Relations',
                'measurements': 'Measurements', 'elevation': 'Elevations',
                'elev_min': 'Min Elev.', 'elev_max': 'Max Elev.',
                'compiler': 'Compiler', 'date': 'Compilation Date',
                'conservation': 'Conservation State', 'topographic_rel': 'Topographic Relation',
                'entrance_facade': 'Entrance Facade', 'entrance_orient': 'Entrance Orient.',
                'articulation': 'Articulation', 'n_rooms': 'Nr. Rooms',
                'room_orient': 'Room Orient.', 'planimetric_dev': 'Planimetric Development',
                'constituent_elem': 'Constituent Elements', 'decorative_motif': 'Decorative Motif',
                'arch_potential': 'Archaeological Potential', 'artifacts': 'Artifacts',
                'dating_elements': 'Dating Elements', 'functional_phases': 'Functional Phases',
                'periodization': 'PERIODIZATION', 'initial': 'STARTING', 'final': 'FINAL',
                'identification': 'IDENTIFICATION DATA', 'classification': 'CLASSIFICATION',
                'spatial_data': 'SPATIAL DATA', 'chronology': 'CHRONOLOGY',
                'components': 'COMPONENTS AND MATERIALS', 'archaeological': 'ARCHAEOLOGICAL DATA',
            },
            'de': {
                'title': 'STRUKTURFORMULAR',
                'site': 'Fundort', 'code': 'Code/Nr.', 'category': 'Kategorie',
                'typology': 'Typologie', 'definition': 'Definition',
                'description': 'Beschreibung', 'interpretation': 'Interpretation',
                'period_start': 'Anfangszeit', 'phase_start': 'Anfangsphase',
                'period_end': 'Endzeit', 'phase_end': 'Endphase',
                'extended_dating': 'Erweiterte Datierung', 'materials': 'Verwendete Materialien',
                'structural_elem': 'Strukturelemente', 'relations': 'Strukturbeziehungen',
                'measurements': 'Messungen', 'elevation': 'Höhen',
                'elev_min': 'Min Höhe', 'elev_max': 'Max Höhe',
                'compiler': 'Bearbeiter', 'date': 'Bearbeitungsdatum',
                'conservation': 'Erhaltungszustand', 'topographic_rel': 'Topographische Beziehung',
                'entrance_facade': 'Eingangsfassade', 'entrance_orient': 'Eingangsausrichtung',
                'articulation': 'Gliederung', 'n_rooms': 'Anzahl Räume',
                'room_orient': 'Raumorientierung', 'planimetric_dev': 'Planimetrische Entwicklung',
                'constituent_elem': 'Bestandteile', 'decorative_motif': 'Dekoratives Motiv',
                'arch_potential': 'Archäologisches Potenzial', 'artifacts': 'Artefakte',
                'dating_elements': 'Datierende Elemente', 'functional_phases': 'Funktionsphasen',
                'periodization': 'PERIODISIERUNG', 'initial': 'ANFANG', 'final': 'ENDE',
                'identification': 'IDENTIFIKATIONSDATEN', 'classification': 'KLASSIFIKATION',
                'spatial_data': 'RÄUMLICHE DATEN', 'chronology': 'CHRONOLOGIE',
                'components': 'KOMPONENTEN UND MATERIALIEN', 'archaeological': 'ARCHÄOLOGISCHE DATEN',
            }
        }

        L = labels.get(lang, labels['it'])

        # Styles
        styTitle = ParagraphStyle('title', fontSize=14, fontName='Helvetica-Bold', alignment=TA_CENTER, leading=16, spaceAfter=6)
        stySection = ParagraphStyle('section', fontSize=10, fontName='Helvetica-Bold', alignment=TA_LEFT, leading=12, spaceBefore=8, spaceAfter=4, backColor=colors.Color(0.85, 0.85, 0.85))
        styLabel = ParagraphStyle('label', fontSize=7, fontName='Helvetica-Bold', alignment=TA_LEFT, leading=9)
        styValue = ParagraphStyle('value', fontSize=8, fontName='Helvetica', alignment=TA_LEFT, wordWrap='CJK', leading=10)
        styDesc = ParagraphStyle('desc', fontSize=8, fontName='Helvetica', alignment=TA_JUSTIFY, wordWrap='CJK', leading=10)

        elements = []

        # Get logo
        home = os.environ['PYARCHINIT_HOME']
        conn = Connection()
        lo_path = conn.logo_path()
        lo_path_str = lo_path['logo']
        home_DB_path = '{}{}{}'.format(home, os.sep, 'pyarchinit_DB_folder')
        logo_path = lo_path_str if bool(lo_path_str) else '{}{}{}'.format(home_DB_path, os.sep, 'logo.jpg')

        logo = None
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path)
                logo.drawHeight = 1.5 * inch * logo.drawHeight / logo.drawWidth
                logo.drawWidth = 1.5 * inch
            except:
                pass

        # =================== PAGE 1 ===================
        # Header
        header_content = [[Paragraph(f"<b>{L['title']}</b>", styTitle), logo if logo else '']]
        header = Table(header_content, colWidths=[14*cm, 4.5*cm])
        header.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.95, 0.95, 0.95)),
        ]))
        elements.append(header)
        elements.append(Spacer(0, 0.4*cm))

        # Section: IDENTIFICATION DATA
        elements.append(Paragraph(f"  {L['identification']}", stySection))
        id_data = [
            [Paragraph(f"<b>{L['site']}</b>", styLabel), Paragraph(self.safe_str(self.sito), styValue),
             Paragraph(f"<b>{L['code']}</b>", styLabel), Paragraph(f"{self.safe_str(self.sigla_struttura)} {self.safe_str(self.numero_struttura)}", styValue)],
            [Paragraph(f"<b>{L['compiler']}</b>", styLabel), Paragraph(self.safe_str(self.nome_compilatore), styValue),
             Paragraph(f"<b>{L['date']}</b>", styLabel), Paragraph(self.safe_str(self.data_compilazione) or self.datestrfdate(), styValue)],
        ]
        id_table = Table(id_data, colWidths=[2.5*cm, 6.5*cm, 2.5*cm, 7*cm], rowHeights=[0.8*cm, 0.8*cm])
        id_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.92, 0.92, 0.92)),
            ('BACKGROUND', (2, 0), (2, -1), colors.Color(0.92, 0.92, 0.92)),
        ]))
        elements.append(id_table)
        elements.append(Spacer(0, 0.4*cm))

        # Section: CLASSIFICATION
        elements.append(Paragraph(f"  {L['classification']}", stySection))
        class_data = [
            [Paragraph(f"<b>{L['category']}</b>", styLabel), Paragraph(self.safe_str(self.categoria_struttura), styValue),
             Paragraph(f"<b>{L['typology']}</b>", styLabel), Paragraph(self.safe_str(self.tipologia_struttura), styValue)],
            [Paragraph(f"<b>{L['definition']}</b>", styLabel), Paragraph(self.safe_str(self.definizione_struttura), styValue), '', ''],
        ]
        class_table = Table(class_data, colWidths=[2.5*cm, 6.5*cm, 2.5*cm, 7*cm], rowHeights=[0.8*cm, 0.8*cm])
        class_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('SPAN', (1, 1), (3, 1)),
            ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.92, 0.92, 0.92)),
            ('BACKGROUND', (2, 0), (2, 0), colors.Color(0.92, 0.92, 0.92)),
        ]))
        elements.append(class_table)
        elements.append(Spacer(0, 0.4*cm))

        # Image and Conservation section
        image_path = self.get_first_image()
        if image_path and os.path.exists(image_path):
            try:
                img = Image(image_path)
                max_h, max_w = 6.5*cm, 6.5*cm
                ratio = min(max_w / img.drawWidth, max_h / img.drawHeight)
                img.drawHeight = img.drawHeight * ratio
                img.drawWidth = img.drawWidth * ratio
                img.hAlign = 'CENTER'
                image_elem = img
            except:
                image_elem = self._create_placeholder_image(6.5*cm, 6.5*cm)
        else:
            image_elem = self._create_placeholder_image(6.5*cm, 6.5*cm)

        # Conservation data
        stato_cons = self.parse_table_data(self.stato_conservazione)
        stato_str = ', '.join([f"{s[0]}: {s[1]}" for s in stato_cons if isinstance(s, (list, tuple)) and len(s) >= 2]) if stato_cons else ''

        left_info = [
            [Paragraph(f"<b>{L['conservation']}</b>", styLabel)],
            [Paragraph(stato_str or '-', styValue)],
            [Spacer(0, 0.2*cm)],
            [Paragraph(f"<b>{L['topographic_rel']}</b>", styLabel)],
            [Paragraph(self.safe_str(self.relazione_topografica) or '-', styValue)],
            [Spacer(0, 0.2*cm)],
            [Paragraph(f"<b>{L['arch_potential']}</b>", styLabel)],
            [Paragraph(self.safe_str(self.potenzialita_archeologica) or '-', styValue)],
        ]
        left_table = Table(left_info, colWidths=[12*cm])
        left_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))

        img_section = Table([[left_table, image_elem]], colWidths=[12*cm, 6.5*cm])
        img_section.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(img_section)
        elements.append(Spacer(0, 0.3*cm))

        # Section: SPATIAL DATA
        elements.append(Paragraph(f"  {L['spatial_data']}", stySection))

        # Prospetto ingresso
        prosp_ing = self.parse_table_data(self.prospetto_ingresso)
        prosp_str = ', '.join([f"{p[0]}: {p[1]}" for p in prosp_ing if isinstance(p, (list, tuple)) and len(p) >= 2]) if prosp_ing else ''

        # Orientamento ambienti
        orient_amb = self.parse_table_data(self.orientamento_ambienti)
        orient_str = ', '.join([f"{o[0]}: {o[1]}" for o in orient_amb if isinstance(o, (list, tuple)) and len(o) >= 2]) if orient_amb else ''

        spatial_data = [
            [Paragraph(f"<b>{L['articulation']}</b>", styLabel), Paragraph(self.safe_str(self.articolazione), styValue),
             Paragraph(f"<b>{L['n_rooms']}</b>", styLabel), Paragraph(self.safe_str(self.n_ambienti), styValue)],
            [Paragraph(f"<b>{L['entrance_orient']}</b>", styLabel), Paragraph(self.safe_str(self.orientamento_ingresso), styValue),
             Paragraph(f"<b>{L['planimetric_dev']}</b>", styLabel), Paragraph(self.safe_str(self.sviluppo_planimetrico), styValue)],
            [Paragraph(f"<b>{L['entrance_facade']}</b>", styLabel), Paragraph(prosp_str or '-', styValue), '', ''],
            [Paragraph(f"<b>{L['room_orient']}</b>", styLabel), Paragraph(orient_str or '-', styValue), '', ''],
        ]
        spatial_table = Table(spatial_data, colWidths=[2.5*cm, 6.5*cm, 2.5*cm, 7*cm], rowHeights=[0.9*cm, 0.9*cm, 0.9*cm, 0.9*cm])
        spatial_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('SPAN', (1, 2), (3, 2)),
            ('SPAN', (1, 3), (3, 3)),
            ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.92, 0.92, 0.92)),
            ('BACKGROUND', (2, 0), (2, 1), colors.Color(0.92, 0.92, 0.92)),
        ]))
        elements.append(spatial_table)
        elements.append(Spacer(0, 0.4*cm))

        # Elementi costitutivi
        elem_cost = self.parse_table_data(self.elementi_costitutivi)
        elem_str = ', '.join([f"{e[0]} ({e[1]})" for e in elem_cost if isinstance(e, (list, tuple)) and len(e) >= 2]) if elem_cost else ''

        const_data = [[Paragraph(f"<b>{L['constituent_elem']}</b>", styLabel), Paragraph(elem_str or '-', styValue)]]
        const_table = Table(const_data, colWidths=[3.5*cm, 15*cm], rowHeights=[1.5*cm])
        const_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, 0), colors.Color(0.92, 0.92, 0.92)),
        ]))
        elements.append(const_table)

        elements.append(PageBreak())

        # =================== PAGE 2 ===================
        # Section: DESCRIPTION
        elements.append(Paragraph(f"  {L['description']}", stySection))
        desc_table = Table([[Paragraph(self.safe_str(self.descrizione) or '-', styDesc)]],
                          colWidths=[18.5*cm], rowHeights=[9*cm])
        desc_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(desc_table)
        elements.append(Spacer(0, 0.4*cm))

        # Section: INTERPRETATION
        elements.append(Paragraph(f"  {L['interpretation']}", stySection))
        interp_table = Table([[Paragraph(self.safe_str(self.interpretazione) or '-', styDesc)]],
                            colWidths=[18.5*cm], rowHeights=[8*cm])
        interp_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(interp_table)
        elements.append(Spacer(0, 0.4*cm))

        # Section: CHRONOLOGY
        elements.append(Paragraph(f"  {L['chronology']}", stySection))
        per_init = self.safe_str(self.periodo_iniziale) if str(self.periodo_iniziale) != 'None' else ''
        fas_init = self.safe_str(self.fase_iniziale) if str(self.fase_iniziale) != 'None' else ''
        per_fin = self.safe_str(self.periodo_finale) if str(self.periodo_finale) != 'None' else ''
        fas_fin = self.safe_str(self.fase_finale) if str(self.fase_finale) != 'None' else ''

        period_data = [
            [Paragraph(f"<b>{L['initial']}</b>", styLabel),
             Paragraph(f"<b>{L['period_start']}</b>", styLabel), Paragraph(per_init or '-', styValue),
             Paragraph(f"<b>{L['phase_start']}</b>", styLabel), Paragraph(fas_init or '-', styValue)],
            [Paragraph(f"<b>{L['final']}</b>", styLabel),
             Paragraph(f"<b>{L['period_end']}</b>", styLabel), Paragraph(per_fin or '-', styValue),
             Paragraph(f"<b>{L['phase_end']}</b>", styLabel), Paragraph(fas_fin or '-', styValue)],
            [Paragraph(f"<b>{L['extended_dating']}</b>", styLabel), Paragraph(self.safe_str(self.datazione_estesa) or '-', styValue), '', '', ''],
        ]
        period_table = Table(period_data, colWidths=[2.5*cm, 2.5*cm, 5*cm, 2.5*cm, 6*cm], rowHeights=[0.9*cm, 0.9*cm, 0.9*cm])
        period_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('SPAN', (1, 2), (4, 2)),
            ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.92, 0.92, 0.92)),
            ('BACKGROUND', (1, 0), (1, 1), colors.Color(0.95, 0.95, 0.95)),
            ('BACKGROUND', (3, 0), (3, 1), colors.Color(0.95, 0.95, 0.95)),
        ]))
        elements.append(period_table)
        elements.append(Spacer(0, 0.4*cm))

        # Section: COMPONENTS AND MATERIALS
        elements.append(Paragraph(f"  {L['components']}", stySection))

        mat_imp = self.parse_table_data(self.materiali_impiegati)
        mat_str = ', '.join([str(m[0]) if isinstance(m, (list, tuple)) else str(m) for m in mat_imp]) if mat_imp else ''

        elem_str_data = self.parse_table_data(self.elementi_strutturali)
        elem_str_str = ', '.join([f"{e[0]}: {e[1]}" for e in elem_str_data if isinstance(e, (list, tuple)) and len(e) >= 2]) if elem_str_data else ''

        comp_data = [
            [Paragraph(f"<b>{L['materials']}</b>", styLabel), Paragraph(mat_str or '-', styValue)],
            [Paragraph(f"<b>{L['structural_elem']}</b>", styLabel), Paragraph(elem_str_str or '-', styValue)],
            [Paragraph(f"<b>{L['decorative_motif']}</b>", styLabel), Paragraph(self.safe_str(self.motivo_decorativo) or '-', styValue)],
        ]
        comp_table = Table(comp_data, colWidths=[3.5*cm, 15*cm], rowHeights=[1.2*cm, 1.2*cm, 1.2*cm])
        comp_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.92, 0.92, 0.92)),
        ]))
        elements.append(comp_table)

        elements.append(PageBreak())

        # =================== PAGE 3 ===================
        # Section: MEASUREMENTS
        elements.append(Paragraph(f"  {L['measurements']}", stySection))

        mis_data = self.parse_table_data(self.misure_struttura)
        if mis_data:
            mis_table_data = [[Paragraph("<b>Tipo misura</b>", styLabel),
                              Paragraph("<b>Unità</b>", styLabel),
                              Paragraph("<b>Valore</b>", styLabel)]]
            for m in mis_data:
                if isinstance(m, (list, tuple)) and len(m) >= 3:
                    mis_table_data.append([
                        Paragraph(str(m[0]), styValue),
                        Paragraph(str(m[1]), styValue),
                        Paragraph(str(m[2]), styValue)
                    ])
            # Add empty rows to fill space if less than 5 measurements
            while len(mis_table_data) < 6:
                mis_table_data.append([Paragraph('', styValue), Paragraph('', styValue), Paragraph('', styValue)])
            mis_table = Table(mis_table_data, colWidths=[6*cm, 4*cm, 8.5*cm], rowHeights=[0.8*cm] * len(mis_table_data))
            mis_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.92, 0.92, 0.92)),
            ]))
            elements.append(mis_table)
        else:
            # Empty table for measurements
            mis_table_data = [[Paragraph("<b>Tipo misura</b>", styLabel),
                              Paragraph("<b>Unità</b>", styLabel),
                              Paragraph("<b>Valore</b>", styLabel)]]
            for _ in range(5):
                mis_table_data.append([Paragraph('', styValue), Paragraph('', styValue), Paragraph('', styValue)])
            mis_table = Table(mis_table_data, colWidths=[6*cm, 4*cm, 8.5*cm], rowHeights=[0.8*cm] * len(mis_table_data))
            mis_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.92, 0.92, 0.92)),
            ]))
            elements.append(mis_table)
        elements.append(Spacer(0, 0.4*cm))

        # Elevations
        elev_data = [
            [Paragraph(f"<b>{L['elevation']}</b>", styLabel),
             Paragraph(f"<b>{L['elev_min']}</b>", styLabel), Paragraph(self.safe_str(self.quota_min) or '-', styValue),
             Paragraph(f"<b>{L['elev_max']}</b>", styLabel), Paragraph(self.safe_str(self.quota_max) or '-', styValue),
             Paragraph("<b>Quota</b>", styLabel), Paragraph(self.safe_str(self.quota) or '-', styValue)]
        ]
        elev_table = Table(elev_data, colWidths=[2*cm, 2*cm, 4*cm, 2*cm, 4*cm, 1.5*cm, 3*cm], rowHeights=[0.9*cm])
        elev_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, 0), colors.Color(0.92, 0.92, 0.92)),
            ('BACKGROUND', (1, 0), (1, 0), colors.Color(0.95, 0.95, 0.95)),
            ('BACKGROUND', (3, 0), (3, 0), colors.Color(0.95, 0.95, 0.95)),
            ('BACKGROUND', (5, 0), (5, 0), colors.Color(0.95, 0.95, 0.95)),
        ]))
        elements.append(elev_table)
        elements.append(Spacer(0, 0.4*cm))

        # Section: ARCHAEOLOGICAL DATA
        elements.append(Paragraph(f"  {L['archaeological']}", stySection))

        # Structure relations
        rapp_str = self.parse_table_data(self.rapporti_struttura)
        rapp_str_str = ', '.join([f"{r[0]}: {r[1]} {r[2]}{r[3]}" for r in rapp_str if isinstance(r, (list, tuple)) and len(r) >= 4]) if rapp_str else ''

        # Artifacts
        manuf = self.parse_table_data(self.manufatti)
        manuf_str = ', '.join([f"{m[0]} ({m[1]})" for m in manuf if isinstance(m, (list, tuple)) and len(m) >= 2]) if manuf else ''

        # Functional phases
        fasi = self.parse_table_data(self.fasi_funzionali)
        fasi_str = ', '.join([f"{f[0]}: {f[1]}" for f in fasi if isinstance(f, (list, tuple)) and len(f) >= 2]) if fasi else ''

        arch_data = [
            [Paragraph(f"<b>{L['relations']}</b>", styLabel), Paragraph(rapp_str_str or '-', styValue)],
            [Paragraph(f"<b>{L['artifacts']}</b>", styLabel), Paragraph(manuf_str or '-', styValue)],
            [Paragraph(f"<b>{L['dating_elements']}</b>", styLabel), Paragraph(self.safe_str(self.elementi_datanti) or '-', styValue)],
            [Paragraph(f"<b>{L['functional_phases']}</b>", styLabel), Paragraph(fasi_str or '-', styValue)],
        ]
        arch_table = Table(arch_data, colWidths=[3.5*cm, 15*cm], rowHeights=[1.5*cm, 1.5*cm, 1.5*cm, 1.5*cm])
        arch_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.92, 0.92, 0.92)),
        ]))
        elements.append(arch_table)
        elements.append(Spacer(0, 0.5*cm))

        # Notes section to fill page
        notes_label = {'it': 'NOTE', 'en': 'NOTES', 'de': 'ANMERKUNGEN'}
        elements.append(Paragraph(f"  {notes_label.get(lang, 'NOTE')}", stySection))
        notes_table = Table([[Paragraph('', styDesc)]], colWidths=[18.5*cm], rowHeights=[5.5*cm])
        notes_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(notes_table)
        elements.append(Spacer(0, 0.3*cm))

        # Footer note
        footer_text = f"Scheda generata da PyArchInit - {self.datestrfdate()}"
        elements.append(Paragraph(f"<i>{footer_text}</i>", ParagraphStyle('footer', fontSize=7, alignment=TA_RIGHT)))

        return elements


class generate_struttura_AR_pdf:
    HOME = os.environ['PYARCHINIT_HOME']
    PDF_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")

    def datestrfdate(self):
        return date.today().strftime("%d-%m-%Y")

    def build_Struttura_AR_sheets(self, records):
        elements = []
        for i in range(len(records)):
            single_sheet = single_Struttura_AR_pdf_sheet(records[i])
            sheet_elements = single_sheet.create_sheet()
            elements.extend(sheet_elements)
            if i < len(records) - 1:
                elements.append(PageBreak())

        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Scheda_Struttura_AR.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f, pagesize=A4,
                               topMargin=0.8*cm, bottomMargin=0.8*cm,
                               leftMargin=1*cm, rightMargin=1*cm)
        doc.build(elements, canvasmaker=NumberedCanvas_Struttura_AR)
        f.close()

    def build_Struttura_AR_sheets_en(self, records):
        elements = []
        for i in range(len(records)):
            single_sheet = single_Struttura_AR_pdf_sheet(records[i])
            sheet_elements = single_sheet.create_sheet_en()
            elements.extend(sheet_elements)
            if i < len(records) - 1:
                elements.append(PageBreak())

        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Structure_Form_AR.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f, pagesize=A4,
                               topMargin=0.8*cm, bottomMargin=0.8*cm,
                               leftMargin=1*cm, rightMargin=1*cm)
        doc.build(elements, canvasmaker=NumberedCanvas_Struttura_AR)
        f.close()

    def build_Struttura_AR_sheets_de(self, records):
        elements = []
        for i in range(len(records)):
            single_sheet = single_Struttura_AR_pdf_sheet(records[i])
            sheet_elements = single_sheet.create_sheet_de()
            elements.extend(sheet_elements)
            if i < len(records) - 1:
                elements.append(PageBreak())

        filename = '{}{}{}'.format(self.PDF_path, os.sep, 'Strukturformular_AR.pdf')
        f = open(filename, "wb")
        doc = SimpleDocTemplate(f, pagesize=A4,
                               topMargin=0.8*cm, bottomMargin=0.8*cm,
                               leftMargin=1*cm, rightMargin=1*cm)
        doc.build(elements, canvasmaker=NumberedCanvas_Struttura_AR)
        f.close()
