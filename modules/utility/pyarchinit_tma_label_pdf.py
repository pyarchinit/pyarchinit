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
import sys
import tempfile
from datetime import datetime
import traceback

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm, inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.platypus import Image as PlatypusImage

try:
    import qrcode
    from PIL import Image as PILImage
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
    
    def get_color_for_site(self, site_name):
        """Get a consistent color for a site name."""
        if not site_name:
            return "#000000"
        
        site_lower = site_name.lower().strip()
        
        # Predefined colors for common localities (dark colors for QR readability)
        predefined_colors = {
            'roma': '#8B0000',  # Dark red
            'milano': '#00008B',  # Dark blue
            'napoli': '#006400',  # Dark green
            'torino': '#483D8B',  # Dark slate blue
            'firenze': '#8B4513',  # Saddle brown
            'venezia': '#2F4F4F',  # Dark slate gray
            'bologna': '#B8860B',  # Dark goldenrod
            'palermo': '#8B008B',  # Dark magenta
            'genova': '#008B8B',  # Dark cyan
            'bari': '#696969',  # Dim gray
            'catania': '#4B0082',  # Indigo
            'verona': '#800080',  # Purple
            'padova': '#708090',  # Slate gray
            'trieste': '#191970',  # Midnight blue
            'brescia': '#8B4500',  # Dark orange
        }
        
        # Check if we have a predefined color
        for key, color in predefined_colors.items():
            if key in site_lower:
                return color
        
        # Otherwise generate a consistent color based on hash
        hash_val = abs(hash(site_name.upper()))
        # Use modulo to select from a set of predefined dark colors
        backup_colors = [
            '#000080',  # Navy
            '#800000',  # Maroon
            '#008000',  # Green
            '#808000',  # Olive
            '#800080',  # Purple
            '#008080',  # Teal
            '#4B0000',  # Dark red
            '#00004B',  # Dark blue
            '#004B00',  # Dark green
            '#4B4B00',  # Dark yellow
        ]
        
        return backup_colors[hash_val % len(backup_colors)]
    
    def draw_area_symbol(self, c, center_x, center_y, area, size=10):
        """Draw a distinctive symbol based on area code."""
        if not area:
            return
            
        # Convert area to string
        area_str = str(area).strip().upper()
        if not area_str:
            return
        
        # Create white background circle
        c.setFillColor(colors.white)
        c.circle(center_x, center_y, size * 0.7, fill=1)
        
        # Set colors for symbol
        c.setFillColor(colors.black)
        c.setStrokeColor(colors.black)
        c.setLineWidth(1.5)
        
        # Map areas to specific symbols (consistent mapping)
        symbol_map = {
            'A': 'house',      # Casa
            'B': 'tower',      # Torre
            'C': 'temple',     # Tempio
            'D': 'wall',       # Muro
            'E': 'arch',       # Arco
            'F': 'column',     # Colonna
            'G': 'amphora',    # Anfora
            'H': 'coin',       # Moneta
            'I': 'key',        # Chiave
            'L': 'lamp',       # Lucerna
            'M': 'mill',       # Macina
            'N': 'necropolis', # Necropoli
            'O': 'oven',       # Forno
            'P': 'plaza',      # Piazza
            'Q': 'quarry',     # Cava
            'R': 'road',       # Strada
            'S': 'storage',    # Magazzino
            'T': 'tomb',       # Tomba
            'U': 'urban',      # Urbano
            'V': 'villa',      # Villa
            'W': 'water',      # Acqua/Pozzo
            'X': 'cross',      # Croce
            'Y': 'yard',       # Cortile
            'Z': 'zone',       # Zona
        }
        
        # For numeric areas, use geometric shapes
        if area_str[0].isdigit():
            try:
                num = int(area_str[0])
                if num == 1:
                    symbol_type = 'circle'
                elif num == 2:
                    symbol_type = 'square'
                elif num == 3:
                    symbol_type = 'triangle'
                elif num == 4:
                    symbol_type = 'diamond'
                elif num == 5:
                    symbol_type = 'pentagon'
                elif num == 6:
                    symbol_type = 'hexagon'
                elif num == 7:
                    symbol_type = 'star'
                elif num == 8:
                    symbol_type = 'octagon'
                elif num == 9:
                    symbol_type = 'cross'
                else:
                    symbol_type = 'circle'
            except:
                symbol_type = 'circle'
        else:
            # For letter areas, use mapped symbols
            symbol_type = symbol_map.get(area_str[0], 'circle')
        
        # Draw the symbol
        symbol_size = size * 0.4
        
        if symbol_type == 'circle':
            c.circle(center_x, center_y, symbol_size * 0.8, fill=0, stroke=1)
        
        elif symbol_type == 'square':
            c.rect(center_x - symbol_size * 0.7, center_y - symbol_size * 0.7,
                   symbol_size * 1.4, symbol_size * 1.4, fill=0, stroke=1)
        
        elif symbol_type == 'triangle':
            c.beginPath()
            c.moveTo(center_x, center_y - symbol_size)
            c.lineTo(center_x - symbol_size * 0.9, center_y + symbol_size * 0.5)
            c.lineTo(center_x + symbol_size * 0.9, center_y + symbol_size * 0.5)
            c.closePath()
            c.stroke()
        
        elif symbol_type == 'diamond':
            c.beginPath()
            c.moveTo(center_x, center_y - symbol_size)
            c.lineTo(center_x + symbol_size * 0.7, center_y)
            c.lineTo(center_x, center_y + symbol_size)
            c.lineTo(center_x - symbol_size * 0.7, center_y)
            c.closePath()
            c.stroke()
        
        elif symbol_type == 'house':
            # Draw a simple house shape
            # Roof
            c.beginPath()
            c.moveTo(center_x - symbol_size, center_y)
            c.lineTo(center_x, center_y - symbol_size)
            c.lineTo(center_x + symbol_size, center_y)
            c.closePath()
            c.stroke()
            # Walls
            c.rect(center_x - symbol_size * 0.8, center_y,
                   symbol_size * 1.6, symbol_size * 0.8, fill=0, stroke=1)
        
        elif symbol_type == 'tower':
            # Draw a tower
            c.rect(center_x - symbol_size * 0.5, center_y - symbol_size,
                   symbol_size, symbol_size * 1.8, fill=0, stroke=1)
            # Battlements
            for i in range(3):
                x = center_x - symbol_size * 0.5 + i * symbol_size * 0.33
                c.rect(x, center_y - symbol_size * 1.2, 
                       symbol_size * 0.2, symbol_size * 0.2, fill=0, stroke=1)
        
        elif symbol_type == 'temple':
            # Draw temple with columns
            # Roof
            c.beginPath()
            c.moveTo(center_x - symbol_size * 1.1, center_y - symbol_size * 0.5)
            c.lineTo(center_x, center_y - symbol_size)
            c.lineTo(center_x + symbol_size * 1.1, center_y - symbol_size * 0.5)
            c.closePath()
            c.stroke()
            # Columns
            for i in range(3):
                x = center_x - symbol_size * 0.8 + i * symbol_size * 0.8
                c.line(x, center_y - symbol_size * 0.5, x, center_y + symbol_size * 0.8)
        
        elif symbol_type == 'amphora':
            # Draw simplified amphora
            c.beginPath()
            c.arc(center_x - symbol_size * 0.3, center_y - symbol_size * 0.3,
                  symbol_size * 0.3, 90, 180)
            c.arc(center_x + symbol_size * 0.3, center_y - symbol_size * 0.3,
                  symbol_size * 0.3, 0, 90)
            c.lineTo(center_x + symbol_size * 0.5, center_y + symbol_size * 0.5)
            c.lineTo(center_x - symbol_size * 0.5, center_y + symbol_size * 0.5)
            c.closePath()
            c.stroke()
        
        elif symbol_type == 'star':
            # Draw 5-pointed star
            import math
            c.beginPath()
            for i in range(10):
                angle = (i * 36 - 90) * math.pi / 180
                radius = symbol_size if i % 2 == 0 else symbol_size * 0.5
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                if i == 0:
                    c.moveTo(x, y)
                else:
                    c.lineTo(x, y)
            c.closePath()
            c.stroke()
        
        elif symbol_type == 'cross':
            # Draw cross
            cross_size = symbol_size * 0.8
            c.line(center_x, center_y - cross_size, center_x, center_y + cross_size)
            c.line(center_x - cross_size, center_y, center_x + cross_size, center_y)
        
        else:
            # Default: circle with area letter
            c.circle(center_x, center_y, symbol_size * 0.8, fill=0, stroke=1)
        
        # Add area text below the symbol
        c.setFont("Helvetica-Bold", int(size/4))
        text_width = c.stringWidth(area_str, "Helvetica-Bold", int(size/4))
        c.drawString(center_x - text_width/2, center_y + size * 0.5, area_str)
    
    def generate_qr_code(self, data, size=20, color=None):
        """Generate QR code image."""
        if not HAS_QRCODE:
            return None
        
        try:
            qr = qrcode.QRCode(
                version=None,  # Allow automatic version selection
                error_correction=qrcode.constants.ERROR_CORRECT_M,  # Medium error correction for better reliability
                box_size=5,  # Larger boxes for better readability
                border=2,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Use custom color if provided, otherwise black
            fill_color = color if color else "black"
            img = qr.make_image(fill_color=fill_color, back_color="white")
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png', mode='wb')
            temp_file.close()  # Close the file handle first
            
            # Save the image
            img.save(temp_file.name, format='PNG')
            
            # Verify file was created
            if os.path.exists(temp_file.name) and os.path.getsize(temp_file.name) > 0:
                return temp_file.name
            else:
                return None
                
        except Exception as e:
            # Silently fail and return None
            return None
    
    def format_tma_data(self, tma_record):
        """Format TMA record data for label."""
        # Extract year from dscd field if present
        anno_scavo = ''
        if tma_record.dscd:
            # Try to extract year from date string
            date_str = str(tma_record.dscd)
            # Common date formats: YYYY, YYYY-MM-DD, DD/MM/YYYY, etc.
            import re
            year_match = re.search(r'(\d{4})', date_str)
            if year_match:
                anno_scavo = year_match.group(1)
        
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
            'anno_scavo': anno_scavo,
        }
        
        # Create QR code data as formatted text (readable by iPhone camera)
        qr_text_parts = []
        qr_text_parts.append("SCHEDA TMA")
        qr_text_parts.append(f"Cassetta: {data['cassetta']}")
        if data['sito']:
            qr_text_parts.append(f"Sito: {data['sito']}")
        if data['localita']:
            qr_text_parts.append(f"Località: {data['localita']}")
        if data['area']:
            qr_text_parts.append(f"Area: {data['area']}")
        if data['settore']:
            qr_text_parts.append(f"Settore: {data['settore']}")
        if data['us']:
            qr_text_parts.append(f"US: {data['us']}")
        if data['inventario']:
            qr_text_parts.append(f"Inventario: {data['inventario']}")
        if data['saggio']:
            qr_text_parts.append(f"Saggio: {data['saggio']}")
        if data['vano_locus']:
            qr_text_parts.append(f"Vano/Locus: {data['vano_locus']}")
        if data['anno_scavo']:
            qr_text_parts.append(f"Anno scavo: {data['anno_scavo']}")
        if data['ogtm']:
            qr_text_parts.append(f"Materiale: {data['ogtm']}")
        if data['dtzg']:
            qr_text_parts.append(f"Cronologia: {data['dtzg']}")
        
        # Format as plain text with line breaks (iPhone readable)
        qr_data = "\n".join(qr_text_parts)
        
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
            c.setFont("Helvetica-Bold", 8)
            c.drawString(content_x, current_y - line_height, f"Sito: {tma_data['sito']}")
            current_y -= line_height * 0.9
            
            c.setFont("Helvetica", 7)
            c.drawString(content_x, current_y - line_height, f"Località: {tma_data['localita']}")
            current_y -= line_height * 0.8
            
            if tma_data['anno_scavo']:
                c.drawString(content_x, current_y - line_height, f"Anno di scavo: {tma_data['anno_scavo']}")
                current_y -= line_height * 0.8
            
            # Show US (US contained in the box)
            c.drawString(content_x, current_y - line_height, f"US: {tma_data['us']}")
            current_y -= line_height * 0.8
            
            c.drawString(content_x, current_y - line_height, f"Area: {tma_data['area']}")
            current_y -= line_height * 0.8
            
            c.drawString(content_x, current_y - line_height, f"Settore: {tma_data['settore']}")
            current_y -= line_height * 0.8
            
            c.drawString(content_x, current_y - line_height, f"Saggio: {tma_data['saggio']}")
            current_y -= line_height * 0.8
            
            if tma_data['vano_locus']:
                c.drawString(content_x, current_y - line_height, f"Vano/Locus: {tma_data['vano_locus']}")
                current_y -= line_height * 0.8
            
            c.setFont("Helvetica-Bold", 8)
            c.drawString(content_x, current_y - line_height, f"Cassetta: {tma_data['cassetta']}")
            current_y -= line_height * 0.8
            
            c.setFont("Helvetica", 7)
            if tma_data['ogtm']:
                c.drawString(content_x, current_y - line_height, f"Materiale: {tma_data['ogtm']}")
        
        elif label_style == 'qr_minimal':
            # QR code with minimal info style
            # Always calculate positions first
            qr_size = min(label_height - (2 * margin), label_width * 0.4)
            qr_x = content_x
            qr_y = y + (label_height - qr_size) / 2
            text_x = qr_x + qr_size + margin
            text_y = y + label_height / 2
            
            if HAS_QRCODE:
                # Get color based on locality
                qr_color = self.get_color_for_site(tma_data['localita'])
                
                # Generate larger QR code for this style
                qr_file = self.generate_qr_code(qr_data, color=qr_color)
                if qr_file and os.path.exists(qr_file):
                    try:
                        # Draw QR code
                        c.drawImage(qr_file, qr_x, qr_y, qr_size, qr_size, preserveAspectRatio=True)
                        
                        # Draw area symbol in the center of QR code
                        qr_center_x = qr_x + qr_size / 2
                        qr_center_y = qr_y + qr_size / 2
                        self.draw_area_symbol(c, qr_center_x, qr_center_y, tma_data['area'], qr_size / 5)
                        
                        # Draw cassetta number (large)
                        c.setFont("Helvetica-Bold", 12)
                        c.drawString(text_x, text_y + 6, f"Cassetta: {tma_data['cassetta']}")
                        
                        # Draw località (smaller)
                        c.setFont("Helvetica", 10)
                        c.drawString(text_x, text_y - 6, f"Località: {tma_data['localita']}")
                        
                        # Clean up temp file
                        try:
                            os.unlink(qr_file)
                        except:
                            pass
                    except Exception as e:
                        # Fallback - still position text on the right
                        # Draw placeholder for QR code
                        c.setStrokeColor(colors.lightgrey)
                        c.rect(qr_x, qr_y, qr_size, qr_size)
                        c.setFont("Helvetica", 8)
                        c.drawString(qr_x + 5, qr_y + qr_size/2, "[QR Error]")
                        
                        # Text on the right
                        c.setFont("Helvetica-Bold", 12)
                        c.drawString(text_x, text_y + 6, f"Cassetta: {tma_data['cassetta']}")
                        c.setFont("Helvetica", 10)
                        c.drawString(text_x, text_y - 6, f"Località: {tma_data['localita']}")
                else:
                    # Fallback if QR generation fails
                    # Draw placeholder rectangle
                    c.setStrokeColor(colors.lightgrey)
                    c.rect(qr_x, qr_y, qr_size, qr_size)
                    c.setFont("Helvetica", 8)
                    c.drawString(qr_x + 5, qr_y + qr_size/2, "[No QR]")
                    
                    # Text on the right
                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(text_x, text_y + 6, f"Cassetta: {tma_data['cassetta']}")
                    c.setFont("Helvetica", 10)
                    c.drawString(text_x, text_y - 6, f"Località: {tma_data['localita']}")
            else:
                # No QR code library available
                # Draw placeholder rectangle with message
                c.setStrokeColor(colors.lightgrey)
                c.setFillColor(colors.lightgrey)
                c.rect(qr_x, qr_y, qr_size, qr_size, fill=0)
                
                # Add notice in the rectangle
                c.setFillColor(colors.black)
                c.setFont("Helvetica", 7)
                notice_lines = ["QR code", "richiede", "modulo", "'qrcode'"]
                line_y = qr_y + qr_size - 10
                for line in notice_lines:
                    text_width = c.stringWidth(line, "Helvetica", 7)
                    c.drawString(qr_x + (qr_size - text_width)/2, line_y, line)
                    line_y -= 10
                
                # Text on the right - always same position
                c.setFont("Helvetica-Bold", 12)
                c.drawString(text_x, text_y + 6, f"Cassetta: {tma_data['cassetta']}")
                c.setFont("Helvetica", 10)
                c.drawString(text_x, text_y - 6, f"Località: {tma_data['localita']}")
    
    def extract_box_number(self, cassetta):
        """Extract numeric portion from cassetta field."""
        import re
        if not cassetta:
            return None
        # Extract the numeric part (e.g., "1" from "1a", "55" from "55b")
        match = re.match(r'^(\d+)', str(cassetta).strip())
        return match.group(1) if match else None
    
    def group_records_by_box(self, tma_records):
        """Group TMA records by box numeric portion."""
        from collections import defaultdict
        grouped = defaultdict(list)
        
        for record in tma_records:
            box_num = self.extract_box_number(record.cassetta)
            if box_num:
                grouped[box_num].append(record)
            else:
                # Records without numeric portion go as individual labels
                grouped[f"_individual_{record.cassetta}"].append(record)
        
        return grouped
    
    def generate_labels(self, tma_records, output_path, label_style='standard', group_by_box=True):
        """
        Generate PDF with labels for TMA records.
        
        Args:
            tma_records: List of TMA record objects
            output_path: Path for output PDF file
            label_style: Style of labels ('standard', 'minimal', 'detailed')
            group_by_box: Whether to group records by box number
        """
        c = canvas.Canvas(output_path, pagesize=self.page_size)
        
        positions = self.calculate_label_positions()
        labels_per_page = len(positions)
        
        if group_by_box and label_style == 'detailed':
            # Group records by box number for detailed labels
            grouped_records = self.group_records_by_box(tma_records)
            
            label_index = 0
            for box_num, records in sorted(grouped_records.items()):
                if label_index > 0 and label_index % labels_per_page == 0:
                    c.showPage()
                
                position_index = label_index % labels_per_page
                x, y = positions[position_index]
                
                # For grouped records, combine US information
                if len(records) > 1 and not box_num.startswith('_individual_'):
                    # Combine data from all records in the group
                    combined_record = records[0]  # Use first record as base
                    us_list = []
                    for rec in records:
                        if rec.dscu:
                            us_list.append(str(rec.dscu))
                    combined_us = ', '.join(sorted(set(us_list)))  # Remove duplicates and sort
                    
                    # Create modified data with combined US
                    tma_data, qr_data = self.format_tma_data(combined_record)
                    tma_data['us'] = combined_us
                    tma_data['cassetta'] = box_num  # Show just the numeric portion
                    
                    self.draw_label(c, x, y, tma_data, qr_data, label_style)
                else:
                    # Single record, process normally
                    tma_data, qr_data = self.format_tma_data(records[0])
                    self.draw_label(c, x, y, tma_data, qr_data, label_style)
                
                label_index += 1
        else:
            # Original behavior for non-grouped labels
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