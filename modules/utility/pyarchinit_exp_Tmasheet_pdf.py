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
        self.thumbnail = data[2] if len(data) > 2 else ''  # Thumbnail path
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
        elements.append(Spacer(1, 12))
        
        # Section OG - OGGETTO
        elements.append(self._create_section_og())
        elements.append(Spacer(1, 12))
        
        # Section LC - LOCALIZZAZIONE
        elements.append(self._create_section_lc())
        elements.append(Spacer(1, 12))
        
        # Section LA - ALTRE LOCALIZZAZIONI
        elements.append(self._create_section_la())
        elements.append(Spacer(1, 12))
        
        # Section UB - DATI PATRIMONIALI
        elements.append(self._create_section_ub())
        elements.append(Spacer(1, 12))
        
        # Section RE - MODALITA' DI REPERIMENTO
        elements.append(self._create_section_re())
        elements.append(Spacer(1, 12))
        
        # Section DT - CRONOLOGIA
        elements.append(self._create_section_dt())
        elements.append(Spacer(1, 12))
        
        # Section DO - FONTI E DOCUMENTI
        do_section = self._create_section_do()
        if isinstance(do_section, list):
            elements.extend(do_section)
        else:
            elements.append(do_section)
        elements.append(Spacer(1, 12))
        
        # Section CO - CONSERVAZIONE
        elements.append(self._create_section_co())
        elements.append(Spacer(1, 12))
        
        # Section TU - CONDIZIONE GIURIDICA
        elements.append(self._create_section_tu())
        elements.append(Spacer(1, 12))
        
        # Section AD - ACCESSO AI DATI
        elements.append(self._create_section_ad())
        elements.append(Spacer(1, 12))
        
        # Section CM - COMPILAZIONE
        elements.append(self._create_section_cm())
        
        # Add page break before materials
        elements.append(PageBreak())
        
        # Section MA - MATERIALI
        ma_elements = self._create_section_ma()
        if isinstance(ma_elements, list):
            elements.extend(ma_elements)
        else:
            elements.append(ma_elements)
        
        # Build PDF
        doc = SimpleDocTemplate(self.file_path, pagesize=A4,
                                topMargin=20*mm, bottomMargin=30*mm,
                                leftMargin=20*mm, rightMargin=20*mm)
        
        doc.build(elements, canvasmaker=NumberedCanvas_TMAsheet)
        
    def _create_header(self):
        """Create header with title and optional image"""
        elements = []
        
        # Title row
        title_data = [[Paragraph("<b>SCHEDA TMA</b>", self.styles['Bold_large'])]]
        
        # Use thumbnail path if provided (following Inv_Materiali logic)
        if self.thumbnail and os.path.exists(self.thumbnail):
            try:
                img = Image(self.thumbnail)
                img.drawHeight = 2.5 * inch * img.drawHeight / img.drawWidth
                img.drawWidth = 2.5 * inch
                img.hAlign = "CENTER"
                title_data.append([img])
                image_found = True
            except Exception as e:
                print(f"Error loading thumbnail: {e}")
                title_data.append([Paragraph("[Immagine non disponibile]", self.styles['Normal'])])
        else:
            # If no thumbnail provided, show placeholder
            title_data.append([Paragraph("[Immagine non disponibile]", self.styles['Normal'])])
            
            # Try to find images by naming convention
            image_found = False
            media_path = os.path.join(self.HOME, "pyarchinit_db_folder", "media", "media_thumb")
            if os.path.exists(media_path):
                # Look for images with TMA naming pattern
                for file in os.listdir(media_path):
                    if file.startswith(f"TMA_{self.record.sito}_cassetta_{self.record.cassetta}_") and \
                       file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        img_path = os.path.join(media_path, file)
                        try:
                            img = Image(img_path, width=160*mm, height=100*mm, kind='proportional')
                            title_data.append([img])
                            image_found = True
                            break
                        except:
                            pass
        
        # If still no image and FTAN is available, try that
        if 'image_found' not in locals():
            image_found = False
        if not image_found and hasattr(self.record, 'ftan') and self.record.ftan:
            media_path = os.path.join(self.HOME, "pyarchinit_db_folder", "media", "media_thumb")
            img_name = f"{self.record.ftan}.jpg"
            img_path = os.path.join(media_path, img_name)
            if os.path.exists(img_path):
                try:
                    img = Image(img_path, width=160*mm, height=100*mm, kind='proportional')
                    title_data.append([img])
                    image_found = True
                except:
                    pass
        
        # Add placeholder if no image found
        if not image_found:
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
        """Create CD section with blue header"""
        data = [
            [Paragraph("<font color='white'><b>CD - CODICI</b></font>", self.styles['Normal'])],
        ]
        
        # Create the section header
        header_table = Table(data, colWidths=[170*mm])
        header_table.setStyle(self.table_style_blue_header)
        
        # Detail data without codes
        detail_data = [
            ["TSK - Tipo scheda", "TMA"],
            ["NCT - Codice univoco", f"TMA_{self.record.sito}_{self.record.cassetta}_{self.record.id}"],
            ["ESC - Ente schedatore", ""],
            ["ECP - Ente competente", ""],
            ["Sito", str(self.record.sito)],
            ["Area", str(self.record.area)],
            ["US", str(self.record.dscu) if self.record.dscu else ""],
            ["Numero Cassetta", str(self.record.cassetta)],
        ]
        
        detail_table = Table(detail_data, colWidths=[85*mm, 85*mm])
        detail_table.setStyle(self.table_style)
        
        return Table([[header_table], [detail_table]], colWidths=[170*mm])
    
        
    def _create_section_og(self):
        """Create OG - OGGETTO section"""
        data = [
            [Paragraph("<font color='white'><b>OG - OGGETTO</b></font>", self.styles['Normal'])],
        ]
        
        detail_data = [
            ["Definizione", "materiale proveniente da Unità Stratigrafica/cassetta"],
            ["Materiale componente", str(self.record.ogtm) if self.record.ogtm else ""],
        ]
        
        header_table = Table(data, colWidths=[170*mm])
        header_table.setStyle(self.table_style_blue_header)
        
        detail_table = Table(detail_data, colWidths=[85*mm, 85*mm])
        detail_table.setStyle(self.table_style)
        
        return Table([[header_table], [detail_table]], colWidths=[170*mm])
        
    def _create_section_lc(self):
        """Create LC - LOCALIZZAZIONE section"""
        data = [
            [Paragraph("<font color='white'><b>LC - LOCALIZZAZIONE</b></font>", 
                      self.styles['Normal'])],
        ]
        
        detail_data = []
        
        # Add location type and denomination if present
        if self.record.ldct:
            detail_data.append(["Tipologia", str(self.record.ldct)])
        if self.record.ldcn:
            detail_data.append(["Denominazione attuale", str(self.record.ldcn)])
        if self.record.vecchia_collocazione:
            detail_data.append(["Vecchia collocazione", str(self.record.vecchia_collocazione)])
        
        header_table = Table(data, colWidths=[170*mm])
        header_table.setStyle(self.table_style_blue_header)
        
        if detail_data:
            detail_table = Table(detail_data, colWidths=[85*mm, 85*mm])
            detail_table.setStyle(self.table_style)
            return Table([[header_table], [detail_table]], colWidths=[170*mm])
        else:
            return header_table
        
    def _create_section_la(self):
        """Create LA - ALTRE LOCALIZZAZIONI section"""
        data = [
            [Paragraph("<font color='white'><b>LA - ALTRE LOCALIZZAZIONI GEOGRAFICO-AMMINISTRATIVE</b></font>", 
                      self.styles['Normal'])],
        ]
        
        detail_data = [
            ["Tipo di localizzazione", "luogo di reperimento"],
            ["Stato", "ITALIA"],
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
        
        detail_data = [
            ["CDG - Condizione giuridica", "proprietà Stato"],
            ["ACQ - Tipo acquisizione", "scavo"]
        ]
        
        header_table = Table(data, colWidths=[170*mm])
        header_table.setStyle(self.table_style_blue_header)
        
        detail_table = Table(detail_data, colWidths=[85*mm, 85*mm])
        detail_table.setStyle(self.table_style)
        
        return Table([[header_table], [detail_table]], colWidths=[170*mm])
        
    def _create_section_re(self):
        """Create RE - MODALITA' DI REPERIMENTO section"""
        data = [
            [Paragraph("<font color='white'><b>RE - MODALITA' DI REPERIMENTO</b></font>", self.styles['Normal'])],
        ]
        
        detail_data = []
        
        # Add all reperimento fields
        detail_data.append(["Tipo di reperimento", "scavo archeologico"])
        
        if self.record.scan:
            detail_data.append(["Nome scavo", str(self.record.scan)])
        if self.record.saggio:
            detail_data.append(["Saggio", str(self.record.saggio)])
        if self.record.vano_locus:
            detail_data.append(["Vano/Locus", str(self.record.vano_locus)])
        if self.record.dscd:
            detail_data.append(["Data scavo", str(self.record.dscd)])
        
        # Add NSC (numero scheda correlata) if present
        if self.record.nsc:
            detail_data.append(["Numero scheda correlata", str(self.record.nsc)])
            
        # Add acquisition data 
        detail_data.append(["Tipo acquisizione", str(self.record.aint) if self.record.aint else "scavo"])
        if self.record.aind:
            detail_data.append(["Data acquisizione", str(self.record.aind)])
        
        header_table = Table(data, colWidths=[170*mm])
        header_table.setStyle(self.table_style_blue_header)
        
        if detail_data:
            detail_table = Table(detail_data, colWidths=[85*mm, 85*mm])
            detail_table.setStyle(self.table_style)
            return Table([[header_table], [detail_table]], colWidths=[170*mm])
        else:
            return header_table
        
    def _create_section_dt(self):
        """Create DT - CRONOLOGIA section"""
        data = [
            [Paragraph("<font color='white'><b>DT - CRONOLOGIA</b></font>", self.styles['Normal'])],
        ]
        
        detail_data = []
        
        detail_data.append(["DTR - Riferimento cronologico", ""])
        if self.record.dtzg:
            detail_data.append(["Fascia cronologica", str(self.record.dtzg)])
        detail_data.append(["Motivazione cronologia", "analisi tipologica"])
        detail_data.append(["DTS - Specifiche cronologiche", ""])
        
        header_table = Table(data, colWidths=[170*mm])
        header_table.setStyle(self.table_style_blue_header)
        
        detail_table = Table(detail_data, colWidths=[85*mm, 85*mm])
        detail_table.setStyle(self.table_style)
        
        return Table([[header_table], [detail_table]], colWidths=[170*mm])
        
    def _create_section_ma(self):
        """Create MA - MATERIALE section with all materials grouped by definition"""
        elements = []
        
        # Section header
        data = [
            [Paragraph("<font color='white'><b>MA - MATERIALE</b></font>", self.styles['Normal'])],
        ]
        header_table = Table(data, colWidths=[170*mm])
        header_table.setStyle(self.table_style_blue_header)
        elements.append(header_table)
        
        if not self.materials:
            elements.append(Paragraph("Nessun materiale registrato", self.styles['Normal']))
            return elements
        
        # Group materials by definition (madi field)
        materials_by_definition = {}
        for material in self.materials:
            definition = str(material.madi) if material.madi else 'Non specificato'
            if definition not in materials_by_definition:
                materials_by_definition[definition] = []
            materials_by_definition[definition].append(material)
        
        # Sort definitions alphabetically
        sorted_definitions = sorted(materials_by_definition.keys())
        
        for definition in sorted_definitions:
            # Add definition header with gray background
            def_header_data = [[Paragraph(f"<b>Definizione: {definition}</b>", self.styles['Normal'])]]
            def_header_table = Table(def_header_data, colWidths=[170*mm])
            def_header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#E0E0E0")),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(def_header_table)
            
            # Create table for materials in this definition group
            material_headers = [
                'Materiale', 'Categoria', 'Classe', 'Prec. tipologica', 'Quantità', 'Peso'
            ]
            
            material_data = [material_headers]
            
            # Aggregate materials with same characteristics
            materials_aggregated = {}
            for material in materials_by_definition[definition]:
                key = (material.macc, material.macl, material.macd, material.macp)
                if key not in materials_aggregated:
                    materials_aggregated[key] = {'qty': 0, 'weight': 0}
                
                # Add quantity
                qty = int(material.macq) if material.macq and str(material.macq).isdigit() else 0
                materials_aggregated[key]['qty'] += qty
                
                # Add weight
                weight = float(material.peso) if material.peso and str(material.peso).replace('.','').isdigit() else 0
                materials_aggregated[key]['weight'] += weight
            
            # Add aggregated materials to table
            for (macc, macl, macd, macp), totals in materials_aggregated.items():
                row = [
                    str(macc) if macc else '',
                    str(macl) if macl else '',
                    str(macd) if macd else '',
                    str(macp) if macp else '',
                    str(totals['qty']),
                    f"{totals['weight']:.2f} g" if totals['weight'] > 0 else ''
                ]
                material_data.append(row)
            
            # Create materials table
            materials_table = Table(material_data, colWidths=[28*mm, 28*mm, 28*mm, 28*mm, 28*mm, 30*mm])
            materials_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#CCCCCC")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            elements.append(materials_table)
            elements.append(Spacer(1, 8))
        
        # Add description if present
        if self.record.deso:
            elements.append(Spacer(1, 12))
            desc_data = [
                ["Indicazione oggetti", str(self.record.deso)],
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
            ["Data compilazione", self.datestrfdate()],
            ["Nome compilatore", str(self.record.created_by) if self.record.created_by else ""],
            ["FUR - Funzionario responsabile", ""],
            ["RVM - TRASCRIZIONE PER INFORMATIZZAZIONE", ""],
            ["Data trascrizione", str(self.record.created_at) if self.record.created_at else ""],
            ["Nome trascrittore", str(self.record.created_by) if self.record.created_by else ""],
            ["AGG - AGGIORNAMENTO", ""],
            ["Data aggiornamento", str(self.record.updated_at) if self.record.updated_at else ""],
            ["Nome aggiornamento", str(self.record.updated_by) if self.record.updated_by else ""],
        ]
        
        header_table = Table(data, colWidths=[170*mm])
        header_table.setStyle(self.table_style_blue_header)
        
        detail_table = Table(detail_data, colWidths=[85*mm, 85*mm])
        detail_table.setStyle(self.table_style)
        
        return Table([[header_table], [detail_table]], colWidths=[170*mm])
        
    def _create_section_co(self):
        """Create CO - CONSERVAZIONE section"""
        data = [
            [Paragraph("<font color='white'><b>CO - CONSERVAZIONE</b></font>", self.styles['Normal'])],
        ]
        
        detail_data = [
            ["Stato di conservazione", "buono"],
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
            ["Indicazione generica", "proprietà Stato"],
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
            ["Profilo di accesso", "1"],
            ["Motivazione", "scheda contenente dati liberamente accessibili"],
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