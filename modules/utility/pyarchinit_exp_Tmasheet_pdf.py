#!/usr/bin/env python3
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
import os
import datetime
from datetime import date
from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from builtins import object
from builtins import range
from builtins import str
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (Table, PageBreak, SimpleDocTemplate, Spacer, 
                                TableStyle, Image, Frame, PageTemplate, BaseDocTemplate,
                                KeepTogether)
from reportlab.platypus.paragraph import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont

# Registered font family
try:
    pdfmetrics.registerFont(TTFont('Cambria', 'Cambria.ttc'))
    pdfmetrics.registerFont(TTFont('cambriab', 'cambriab.ttf'))
    pdfmetrics.registerFont(TTFont('VeraIt', 'VeraIt.ttf'))
    pdfmetrics.registerFont(TTFont('VeraBI', 'VeraBI.ttf'))
    registerFontFamily('Cambria', normal='Cambria')
except:
    pass

from ..db.pyarchinit_conn_strings import Connection
from .pyarchinit_OS_utility import *


class NumberedCanvas_TMAsheet(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

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
        self.drawCentredString(A4[0]/2, 20 * mm,
                             "Pagina %d di %d" % (self._pageNumber, page_count))


class generate_tma_pdf:
    HOME = os.environ['PYARCHINIT_HOME']
    PDF_path = '{}{}{}'.format(HOME, os.sep, "pyarchinit_PDF_folder")

    def __init__(self, data):
        self.record = data[0]  # TMA record
        self.materials = data[1] if len(data) > 1 else []  # List of materials
        self.file_name = "Scheda_TMA_" + str(self.record.sito) + "_cassetta_" + str(self.record.cassetta) + ".pdf"
        self.file_path = os.path.join(self.PDF_path, self.file_name)
        
        # Create standard styles
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='Center', alignment=1))  # Center align
        self.styles.add(ParagraphStyle(name='Normal_small', parent=self.styles['Normal'], fontSize=8))
        self.styles.add(ParagraphStyle(name='Bold', parent=self.styles['Normal'], fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(name='Bold_large', parent=self.styles['Normal'], fontName='Helvetica-Bold', fontSize=14))
        
        # Table styles
        self.table_style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ])
        
        self.table_style_blue_header = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#000080")),  # Navy blue
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ])

    def datestrfdate(self):
        """Convert date for display"""
        now = date.today()
        today = now.strftime("%d-%m-%Y")
        return today

    def create_sheet(self):
        """Main method to create the PDF"""
        elements = []
        
        # Add header with photo if available
        elements.append(self._create_header())
        elements.append(Spacer(1, 12))
        
        # Section CD - CODICI
        elements.append(self._create_section_cd())
        
        # Section OG - OGGETTO
        elements.append(self._create_section_og())
        
        # Section LC - LOCALIZZAZIONE
        elements.append(self._create_section_lc())
        
        # Section LA - ALTRE LOCALIZZAZIONI
        elements.append(self._create_section_la())
        
        # Section UB - DATI PATRIMONIALI
        elements.append(self._create_section_ub())
        
        # Section RE - MODALITA' DI REPERIMENTO
        elements.append(self._create_section_re())
        
        # Section DT - CRONOLOGIA
        elements.append(self._create_section_dt())
        
        # Add page break before materials
        elements.append(PageBreak())
        
        # Section MA - MATERIALI
        ma_elements = self._create_section_ma()
        if isinstance(ma_elements, list):
            elements.extend(ma_elements)
        else:
            elements.append(ma_elements)
        
        # Section CO - CONSERVAZIONE
        elements.append(self._create_section_co())
        
        # Section TU - CONDIZIONE GIURIDICA
        elements.append(self._create_section_tu())
        
        # Section DO - FONTI E DOCUMENTI
        do_elements = self._create_section_do()
        if isinstance(do_elements, list):
            elements.extend(do_elements)
        else:
            elements.append(do_elements)
        
        # Section AD - ACCESSO AI DATI
        elements.append(self._create_section_ad())
        
        # Section CM - COMPILAZIONE
        elements.append(self._create_section_cm())
        
        # Build PDF
        doc = SimpleDocTemplate(self.file_path, pagesize=A4,
                                topMargin=20*mm, bottomMargin=30*mm,
                                leftMargin=20*mm, rightMargin=20*mm)
        
        doc.build(elements, canvasmaker=NumberedCanvas_TMAsheet)
        
    def _create_header(self):
        """Create header with title and optional image"""
        elements = []
        
        # Title row
        title_data = [[Paragraph("<b>Scheda</b>", self.styles['Bold_large'])]]
        
        # Check for TMA media images
        media_path = os.path.join(self.HOME, "pyarchinit_db_folder", "media", "media_thumb")
        image_found = False
        
        # Try to find images for this TMA
        if os.path.exists(media_path):
            for file in os.listdir(media_path):
                if file.startswith(f"TMA_{self.record.sito}_cassetta_{self.record.cassetta}_") and \
                   file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    img_path = os.path.join(media_path, file)
                    try:
                        # Add image with max width/height
                        img = Image(img_path, width=160*mm, height=100*mm, kind='proportional')
                        title_data.append([img])
                        image_found = True
                        break
                    except:
                        pass
        
        # If no image found, add placeholder text
        if not image_found:
            # Try to get the first image from FTAX if available
            if self.record.ftan:
                img_name = f"{self.record.ftan}.jpg"
                img_path = os.path.join(media_path, img_name)
                if os.path.exists(img_path):
                    try:
                        img = Image(img_path, width=160*mm, height=100*mm, kind='proportional')
                        title_data.append([img])
                    except:
                        title_data.append([Paragraph("[Immagine non disponibile]", self.styles['Normal'])])
                else:
                    title_data.append([Paragraph("[Immagine non disponibile]", self.styles['Normal'])])
        
        table = Table(title_data, colWidths=[170*mm])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (0, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        return table
        
    def _create_section_cd(self):
        """Create CD - CODICI section"""
        data = [
            [Paragraph("<font color='white'><b>CD - CODICI</b></font>", self.styles['Normal'])],
        ]
        
        detail_data = [
            ["TSK - Tipo Scheda", "TMA"],
            ["LIR - Livello ricerca", "I"],
            ["NCT - CODICE UNIVOCO", ""],
            ["    NCTR - Codice regione", str(getattr(self.record, 'nctr', '07'))],
            ["    NCTN - Numero catalogo generale", str(getattr(self.record, 'nctn', ''))],
            ["ESC - Ente schedatore", str(getattr(self.record, 'esc', 'S19'))],
            ["ECP - Ente competente", str(getattr(self.record, 'ecp', 'S19'))],
        ]
        
        # Create the section header
        header_table = Table(data, colWidths=[170*mm])
        header_table.setStyle(self.table_style_blue_header)
        
        # Create the details table
        detail_table = Table(detail_data, colWidths=[85*mm, 85*mm])
        detail_table.setStyle(self.table_style)
        
        return Table([[header_table], [detail_table]], colWidths=[170*mm])
        
    def _create_section_og(self):
        """Create OG - OGGETTO section"""
        data = [
            [Paragraph("<font color='white'><b>OG - OGGETTO</b></font>", self.styles['Normal'])],
        ]
        
        detail_data = [
            ["OGT - OGGETTO", ""],
            ["    OGTD - Definizione", "materiale proveniente da Unità Stratigrafica/ cassetta"],
            ["    OGTM - Definizione materiale componente", str(self.record.ogtm) if self.record.ogtm else ""],
        ]
        
        header_table = Table(data, colWidths=[170*mm])
        header_table.setStyle(self.table_style_blue_header)
        
        detail_table = Table(detail_data, colWidths=[85*mm, 85*mm])
        detail_table.setStyle(self.table_style)
        
        return Table([[header_table], [detail_table]], colWidths=[170*mm])
        
    def _create_section_lc(self):
        """Create LC - LOCALIZZAZIONE section"""
        data = [
            [Paragraph("<font color='white'><b>LC - LOCALIZZAZIONE GEOGRAFICO-AMMINISTRATIVA</b></font>", 
                      self.styles['Normal'])],
        ]
        
        detail_data = [
            ["PVC - LOCALIZZAZIONE GEOGRAFICO-AMMINISTRATIVA ATTUALE", ""],
            ["    PVCS - Stato", "ITALIA"],
            ["    PVCR - Regione", str(getattr(self.record, 'pvcr', ''))],
            ["    PVCP - Provincia", str(getattr(self.record, 'pvcp', ''))],
            ["    PVCC - Comune", str(getattr(self.record, 'pvcc', self.record.sito if self.record.sito else ''))],
            ["LDC - COLLOCAZIONE SPECIFICA", ""],
            ["    LDCT - Tipologia", str(self.record.ldct) if self.record.ldct else ""],
            ["    LDCN - Denominazione attuale", str(self.record.ldcn) if self.record.ldcn else ""],
            ["    LDCU - Indirizzo", str(getattr(self.record, 'ldcu', ''))],
            ["    LDCS - Specifiche e note", 
             f"Cassetta {self.record.cassetta}, {self.record.vecchia_collocazione if self.record.vecchia_collocazione else ''}"],
        ]
        
        header_table = Table(data, colWidths=[170*mm])
        header_table.setStyle(self.table_style_blue_header)
        
        detail_table = Table(detail_data, colWidths=[85*mm, 85*mm])
        detail_table.setStyle(self.table_style)
        
        return Table([[header_table], [detail_table]], colWidths=[170*mm])
        
    def _create_section_la(self):
        """Create LA - ALTRE LOCALIZZAZIONI section"""
        data = [
            [Paragraph("<font color='white'><b>LA - ALTRE LOCALIZZAZIONI GEOGRAFICO-AMMINISTRATIVE</b></font>", 
                      self.styles['Normal'])],
        ]
        
        detail_data = [
            ["TCL - Tipo di localizzazione", "luogo di reperimento"],
            ["PRV - LOCALIZZAZIONE GEOGRAFICO-AMMINISTRATIVA", ""],
            ["    PRVS - Stato", "ITALIA"],
            ["    PRVR - Regione", str(getattr(self.record, 'prvr', ''))],
            ["    PRVP - Provincia", str(getattr(self.record, 'prvp', ''))],
            ["    PRVC - Comune", str(getattr(self.record, 'prvc', ''))],
            ["    PRVL - Località", str(getattr(self.record, 'prvl', ''))],
        ]
        
        header_table = Table(data, colWidths=[170*mm])
        header_table.setStyle(self.table_style_blue_header)
        
        detail_table = Table(detail_data, colWidths=[85*mm, 85*mm])
        detail_table.setStyle(self.table_style)
        
        return Table([[header_table], [detail_table]], colWidths=[170*mm])
        
    def _create_section_ub(self):
        """Create UB - DATI PATRIMONIALI section"""
        data = [
            [Paragraph("<font color='white'><b>UB - DATI PATRIMONIALI</b></font>", self.styles['Normal'])],
        ]
        
        detail_data = []
        
        # Add inventory data if present
        invn = getattr(self.record, 'invn', None)
        invd = getattr(self.record, 'invd', None)
        if invn or invd:
            detail_data.extend([
                ["INV - INVENTARIO", ""],
                ["    INVN - Numero", str(invn) if invn else ""],
                ["    INVD - Data", str(invd) if invd else ""],
            ])
            
        # Add estimation data if present
        stis = getattr(self.record, 'stis', None)
        stid = getattr(self.record, 'stid', None)
        stim = getattr(self.record, 'stim', None)
        if stis or stid:
            detail_data.extend([
                ["STI - STIMA", ""],
                ["    STIS - Stima", str(stis) if stis else ""],
                ["    STID - Data stima", str(stid) if stid else ""],
                ["    STIM - Motivo della stima", str(stim) if stim else "valutazione all'atto della compilazione dell'inventario generale"],
            ])
        
        if detail_data:
            header_table = Table(data, colWidths=[170*mm])
            header_table.setStyle(self.table_style_blue_header)
            
            detail_table = Table(detail_data, colWidths=[85*mm, 85*mm])
            detail_table.setStyle(self.table_style)
            
            return Table([[header_table], [detail_table]], colWidths=[170*mm])
        else:
            return Spacer(1, 1)  # Return empty spacer if no data
        
    def _create_section_re(self):
        """Create RE - MODALITA' DI REPERIMENTO section"""
        data = [
            [Paragraph("<font color='white'><b>RE - MODALITA' DI REPERIMENTO</b></font>", self.styles['Normal'])],
        ]
        
        detail_data = [
            ["DSC - DATI DI SCAVO", ""],
            ["    SCAN - Denominazione dello scavo", str(self.record.scan) if self.record.scan else ""],
            ["    DSCF - Ente responsabile", ""],
            ["    DSCA - Responsabile scientifico", ""],
            ["    DSCT - Motivo", "ricerca scientifica"],
            ["    DSCM - Metodo", "per saggi stratigrafici"],
            ["    DSCD - Data", str(self.record.dscd) if self.record.dscd else ""],
            ["    DSCU - Unità Stratigrafica", str(self.record.dscu) if self.record.dscu else ""],
            ["    DSCZ - Bibliografia specifica", ""],
        ]
        
        # Add survey data if present
        if self.record.rcgd or self.record.rcgz:
            detail_data.extend([
                ["RCG - DATI DI RICOGNIZIONE", ""],
                ["    RCGD - Data", str(self.record.rcgd) if self.record.rcgd else ""],
                ["    RCGZ - Specifiche", str(self.record.rcgz) if self.record.rcgz else ""],
            ])
            
        # Add acquisition data if present
        if self.record.aint or self.record.aind:
            detail_data.extend([
                ["AIN - ALTRE ACQUISIZIONI", ""],
                ["    AINT - Tipo", str(self.record.aint) if self.record.aint else ""],
                ["    AIND - Data", str(self.record.aind) if self.record.aind else ""],
            ])
        
        header_table = Table(data, colWidths=[170*mm])
        header_table.setStyle(self.table_style_blue_header)
        
        detail_table = Table(detail_data, colWidths=[85*mm, 85*mm])
        detail_table.setStyle(self.table_style)
        
        return Table([[header_table], [detail_table]], colWidths=[170*mm])
        
    def _create_section_dt(self):
        """Create DT - CRONOLOGIA section"""
        data = [
            [Paragraph("<font color='white'><b>DT - CRONOLOGIA</b></font>", self.styles['Normal'])],
        ]
        
        detail_data = [
            ["DTZ - CRONOLOGIA GENERICA", ""],
            ["    DTZG - Fascia cronologica di riferimento", str(self.record.dtzg) if self.record.dtzg else ""],
            ["    DTM - Motivazione cronologia", "analisi tipologica"],
        ]
        
        header_table = Table(data, colWidths=[170*mm])
        header_table.setStyle(self.table_style_blue_header)
        
        detail_table = Table(detail_data, colWidths=[85*mm, 85*mm])
        detail_table.setStyle(self.table_style)
        
        return Table([[header_table], [detail_table]], colWidths=[170*mm])
        
    def _create_section_ma(self):
        """Create MA - MATERIALE section with all materials"""
        elements = []
        
        # Section header
        data = [
            [Paragraph("<font color='white'><b>MA - MATERIALE</b></font>", self.styles['Normal'])],
        ]
        header_table = Table(data, colWidths=[170*mm])
        header_table.setStyle(self.table_style_blue_header)
        elements.append(header_table)
        
        # Group materials by type for better organization
        materials_by_type = {}
        for material in self.materials:
            key = (material.macc, material.macl, material.macd, material.macp)
            if key not in materials_by_type:
                materials_by_type[key] = []
            materials_by_type[key].append(material)
        
        # Add materials from the materials table
        for idx, (key, materials_group) in enumerate(materials_by_type.items()):
            # Aggregate quantities for same type
            total_qty = sum(int(m.macq) if m.macq and str(m.macq).isdigit() else 0 for m in materials_group)
            
            material_data = []
            
            # MAC - MATERIALE COMPONENTE
            material_data.append(["MAC - MATERIALE COMPONENTE", ""])
            material_data.append(["    MACC - Categoria", str(key[0]) if key[0] else ""])
            material_data.append(["    MACL - Classe", str(key[1]) if key[1] else ""])
            material_data.append(["    MACD - Definizione", str(key[2]) if key[2] else ""])
            if key[3]:
                material_data.append(["    MACP - Precisazione tipologica", str(key[3])])
            material_data.append(["    MACQ - Quantità", str(total_qty)])
            
            # Add descriptions for each material in the group
            for mat_idx, material in enumerate(materials_group):
                # Since we don't have separate MAD fields in the database,
                # we'll just add the inventory number if present
                if material.madi:
                    material_data.append(["    MADI - Inventario", str(material.madi)])
            
            detail_table = Table(material_data, colWidths=[85*mm, 85*mm])
            detail_table.setStyle(self.table_style)
            elements.append(detail_table)
            
            # Add spacing between material groups
            if idx < len(materials_by_type) - 1:
                elements.append(Spacer(1, 12))
        
        # If there's additional object description
        if self.record.deso:
            elements.append(Spacer(1, 12))
            desc_data = [
                ["DA - DESCRIZIONE", ""],
                ["    DESO - Indicazione oggetti", str(self.record.deso)],
            ]
            desc_table = Table(desc_data, colWidths=[85*mm, 85*mm])
            desc_table.setStyle(self.table_style)
            elements.append(desc_table)
        
        return elements
        
    def _create_section_do(self):
        """Create DO - FONTI E DOCUMENTI section"""
        elements = []
        
        data = [
            [Paragraph("<font color='white'><b>DO - FONTI E DOCUMENTI DI RIFERIMENTO</b></font>", 
                      self.styles['Normal'])],
        ]
        header_table = Table(data, colWidths=[170*mm])
        header_table.setStyle(self.table_style_blue_header)
        elements.append(header_table)
        
        detail_data = []
        
        # Add photo documentation if present
        if self.record.ftap or self.record.ftan:
            detail_data.append(["FTA - DOCUMENTAZIONE FOTOGRAFICA", ""])
            detail_data.append(["    FTAX - Genere", "documentazione allegata"])
            detail_data.append(["    FTAP - Tipo", str(self.record.ftap) if self.record.ftap else ""])
            detail_data.append(["    FTAN - Codice identificativo", str(self.record.ftan) if self.record.ftan else ""])
            
        # Add drawing documentation if present
        if self.record.drat or self.record.dran:
            detail_data.append(["DRA - DOCUMENTAZIONE GRAFICA", ""])
            detail_data.append(["    DRAT - Tipo", str(self.record.drat) if self.record.drat else ""])
            detail_data.append(["    DRAN - Codice identificativo", str(self.record.dran) if self.record.dran else ""])
            if self.record.draa:
                detail_data.append(["    DRAA - Autore", str(self.record.draa)])
        
        if detail_data:
            detail_table = Table(detail_data, colWidths=[85*mm, 85*mm])
            detail_table.setStyle(self.table_style)
            elements.append(detail_table)
        
        return elements
        
    def _create_section_cm(self):
        """Create CM - COMPILAZIONE section"""
        data = [
            [Paragraph("<font color='white'><b>CM - COMPILAZIONE</b></font>", self.styles['Normal'])],
        ]
        
        detail_data = [
            ["CMP - COMPILAZIONE", ""],
            ["    CMPD - Data", self.datestrfdate()],
            ["    CMPN - Nome", ""],
            ["FUR - Funzionario responsabile", ""],
        ]
        
        header_table = Table(data, colWidths=[170*mm])
        header_table.setStyle(self.table_style_blue_header)
        
        detail_table = Table(detail_data, colWidths=[85*mm, 85*mm])
        detail_table.setStyle(self.table_style)
        
        return Table([[header_table], [detail_table]], colWidths=[170*mm])
        
    def _create_section_co(self):
        """Create CO - CONSERVAZIONE section"""
        stcc = getattr(self.record, 'stcc', None)
        if not stcc:
            return Spacer(1, 1)
            
        data = [
            [Paragraph("<font color='white'><b>CO - CONSERVAZIONE</b></font>", self.styles['Normal'])],
        ]
        
        detail_data = [
            ["STC - STATO DI CONSERVAZIONE", ""],
            ["    STCC - Stato di conservazione", str(stcc) if stcc else "buono"],
        ]
        
        header_table = Table(data, colWidths=[170*mm])
        header_table.setStyle(self.table_style_blue_header)
        
        detail_table = Table(detail_data, colWidths=[85*mm, 85*mm])
        detail_table.setStyle(self.table_style)
        
        return Table([[header_table], [detail_table]], colWidths=[170*mm])
        
    def _create_section_tu(self):
        """Create TU - CONDIZIONE GIURIDICA section"""
        data = [
            [Paragraph("<font color='white'><b>TU - CONDIZIONE GIURIDICA E VINCOLI</b></font>", self.styles['Normal'])],
        ]
        
        detail_data = [
            ["ACQ - ACQUISIZIONE", ""],
            ["    ACQT - Tipo acquisizione", str(getattr(self.record, 'acqt', 'scavo'))],
            ["CDG - CONDIZIONE GIURIDICA", ""],
            ["    CDGG - Indicazione generica", str(getattr(self.record, 'cdgg', 'proprietà Stato'))],
        ]
        
        header_table = Table(data, colWidths=[170*mm])
        header_table.setStyle(self.table_style_blue_header)
        
        detail_table = Table(detail_data, colWidths=[85*mm, 85*mm])
        detail_table.setStyle(self.table_style)
        
        return Table([[header_table], [detail_table]], colWidths=[170*mm])
        
    def _create_section_ad(self):
        """Create AD - ACCESSO AI DATI section"""
        data = [
            [Paragraph("<font color='white'><b>AD - ACCESSO AI DATI</b></font>", self.styles['Normal'])],
        ]
        
        detail_data = [
            ["ADS - SPECIFICHE DI ACCESSO AI DATI", ""],
            ["    ADSP - Profilo di accesso", str(getattr(self.record, 'adsp', '1'))],
            ["    ADSM - Motivazione", str(getattr(self.record, 'adsm', 'scheda contenente dati liberamente accessibili'))],
        ]
        
        header_table = Table(data, colWidths=[170*mm])
        header_table.setStyle(self.table_style_blue_header)
        
        detail_table = Table(detail_data, colWidths=[85*mm, 85*mm])
        detail_table.setStyle(self.table_style)
        
        return Table([[header_table], [detail_table]], colWidths=[170*mm])


def single_TMA_pdf(data):
    """Function to generate a single TMA PDF"""
    tma_pdf = generate_tma_pdf(data)
    tma_pdf.create_sheet()
    return tma_pdf.file_path