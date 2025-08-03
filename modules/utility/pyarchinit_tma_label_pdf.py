#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TMA Label PDF Export Module

This module provides functionality to export TMA records as printable labels.
Supports various label formats including single labels and label sheets.

Created on: 2025-07-31
Author: Enzo Cocca <enzo.ccc@gmail.com>
"""

import os
import tempfile
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm, inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False


class TMALabelPDF:
    """Class to generate printable labels for TMA records."""
    
    # Standard label sheet formats (width x height in mm)
    LABEL_FORMATS = {
        'single_70x37': {'width': 70, 'height': 37, 'per_row': 3, 'per_col': 8, 'margin': 2},
        'single_105x57': {'width': 105, 'height': 57, 'per_row': 2, 'per_col': 5, 'margin': 3},
        'single_210x297': {'width': 210, 'height': 297, 'per_row': 1, 'per_col': 1, 'margin': 10},
        'avery_l7163': {'width': 99.1, 'height': 38.1, 'per_row': 2, 'per_col': 7, 'margin': 2.5},
        'avery_l7160': {'width': 63.5, 'height': 38.1, 'per_row': 3, 'per_col': 7, 'margin': 2.5},
    }
    
    def __init__(self, label_format='single_70x37', page_size=A4):
        """
        Initialize the label PDF generator.
        
        Args:
            label_format: One of the predefined label formats
            page_size: Page size (default A4)
        """
        self.label_format = self.LABEL_FORMATS.get(label_format, self.LABEL_FORMATS['single_70x37'])
        self.page_size = page_size
        self.page_width = page_size[0] / mm
        self.page_height = page_size[1] / mm
        
    def calculate_label_positions(self):
        """Calculate label positions on page."""
        label_width = self.label_format['width']
        label_height = self.label_format['height']
        per_row = self.label_format['per_row']
        per_col = self.label_format['per_col']
        
        # Calculate margins to center labels on page
        total_width = per_row * label_width
        total_height = per_col * label_height
        
        left_margin = (self.page_width - total_width) / 2
        top_margin = (self.page_height - total_height) / 2
        
        positions = []
        for col in range(per_col):
            for row in range(per_row):
                x = left_margin + (row * label_width)
                y = self.page_height - top_margin - ((col + 1) * label_height)
                positions.append((x * mm, y * mm))
                
        return positions
    
    def generate_qr_code(self, data, size=20):
        """Generate QR code image."""
        if not HAS_QRCODE:
            return None
            
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=2,
            border=1,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(temp_file.name)
        temp_file.close()
        
        return temp_file.name
    
    def format_tma_data(self, tma_record):
        """Format TMA record data for label."""
        data = {
            'id': str(tma_record.id_tma) if hasattr(tma_record, 'id_tma') else '',
            'sito': tma_record.sito or '',
            'area': tma_record.area or '',
            'us': tma_record.dscu or '',
            'cassetta': tma_record.cassetta or '',
            'inventario': tma_record.inventario or '',
            'localita': tma_record.localita or '',
            'settore': tma_record.settore or '',
            'saggio': tma_record.saggio or '',
            'vano_locus': tma_record.vano_locus or '',
            'ogtm': tma_record.ogtm or '',
            'dtzg': tma_record.dtzg or '',
        }
        
        # Create QR code data
        qr_data = f"TMA:{data['id']}|{data['sito']}|{data['cassetta']}|{data['inventario']}"
        
        return data, qr_data
    
    def draw_label(self, c, x, y, tma_data, qr_data, label_style='standard'):
        """Draw a single label on the canvas."""
        label_width = self.label_format['width'] * mm
        label_height = self.label_format['height'] * mm
        margin = self.label_format['margin'] * mm
        
        # Draw border (optional)
        c.setStrokeColor(colors.lightgrey)
        c.rect(x, y, label_width, label_height)
        
        # Set font
        c.setFont("Helvetica-Bold", 10)
        
        # Calculate content area
        content_x = x + margin
        content_y = y + label_height - margin
        content_width = label_width - (2 * margin)
        
        # Line height
        line_height = 4 * mm
        current_y = content_y
        
        if label_style == 'standard':
            # Title
            c.drawString(content_x, current_y - line_height, f"TMA {tma_data['inventario']}")
            current_y -= line_height * 1.5
            
            # Site and area info
            c.setFont("Helvetica", 8)
            c.drawString(content_x, current_y - line_height, f"Sito: {tma_data['sito']}")
            current_y -= line_height
            
            c.drawString(content_x, current_y - line_height, f"Area: {tma_data['area']} | US: {tma_data['us']}")
            current_y -= line_height
            
            c.drawString(content_x, current_y - line_height, f"Cassetta: {tma_data['cassetta']}")
            current_y -= line_height
            
            # Material type
            if tma_data['ogtm']:
                c.drawString(content_x, current_y - line_height, f"Materiale: {tma_data['ogtm']}")
                current_y -= line_height
            
            # QR Code (if available and space permits)
            if HAS_QRCODE and label_height > 50 * mm:
                qr_file = self.generate_qr_code(qr_data)
                if qr_file:
                    qr_size = 15 * mm
                    qr_x = x + label_width - qr_size - margin
                    qr_y = y + margin
                    c.drawImage(qr_file, qr_x, qr_y, qr_size, qr_size)
                    os.unlink(qr_file)
                    
        elif label_style == 'minimal':
            # Minimal style - just essential info
            c.drawString(content_x, current_y - line_height, f"{tma_data['inventario']}")
            current_y -= line_height
            
            c.setFont("Helvetica", 7)
            c.drawString(content_x, current_y - line_height, f"{tma_data['sito']} - {tma_data['cassetta']}")
            
        elif label_style == 'detailed':
            # Detailed style with more information
            c.setFont("Helvetica-Bold", 9)
            c.drawString(content_x, current_y - line_height, f"Inv: {tma_data['inventario']}")
            current_y -= line_height * 1.2
            
            c.setFont("Helvetica", 7)
            c.drawString(content_x, current_y - line_height, f"Sito: {tma_data['sito']} | Località: {tma_data['localita']}")
            current_y -= line_height * 0.9
            
            c.drawString(content_x, current_y - line_height, f"Area: {tma_data['area']} | Settore: {tma_data['settore']}")
            current_y -= line_height * 0.9
            
            c.drawString(content_x, current_y - line_height, f"US: {tma_data['us']} | Saggio: {tma_data['saggio']}")
            current_y -= line_height * 0.9
            
            c.drawString(content_x, current_y - line_height, f"Cassetta: {tma_data['cassetta']}")
            current_y -= line_height * 0.9
            
            if tma_data['ogtm']:
                c.drawString(content_x, current_y - line_height, f"Mat: {tma_data['ogtm']}")
                current_y -= line_height * 0.9
                
            if tma_data['dtzg']:
                c.drawString(content_x, current_y - line_height, f"Cron: {tma_data['dtzg']}")
    
    def generate_labels(self, tma_records, output_path, label_style='standard'):
        """
        Generate PDF with labels for TMA records.
        
        Args:
            tma_records: List of TMA record objects
            output_path: Path for output PDF file
            label_style: Style of labels ('standard', 'minimal', 'detailed')
        """
        c = canvas.Canvas(output_path, pagesize=self.page_size)
        
        positions = self.calculate_label_positions()
        labels_per_page = len(positions)
        
        for i, record in enumerate(tma_records):
            if i > 0 and i % labels_per_page == 0:
                c.showPage()
                
            position_index = i % labels_per_page
            x, y = positions[position_index]
            
            tma_data, qr_data = self.format_tma_data(record)
            self.draw_label(c, x, y, tma_data, qr_data, label_style)
        
        c.save()
        return output_path
    
    def generate_single_label(self, tma_record, output_path, label_style='standard'):
        """Generate a single label PDF."""
        return self.generate_labels([tma_record], output_path, label_style)