#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UT Analysis PDF Report Generator

Generates professional PDF reports for archaeological potential and risk analysis.
Supports 7 languages: IT, EN, DE, ES, FR, AR, CA

Created for PyArchInit QGIS Plugin
"""

import os
from datetime import datetime

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm, mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image, KeepTogether
    )
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Import labels
try:
    from ..analysis.ut_labels import UTAnalysisLabels
    LABELS_AVAILABLE = True
except ImportError:
    LABELS_AVAILABLE = False

# Page constants
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_LEFT = 1.5 * cm
MARGIN_RIGHT = 1.5 * cm
MARGIN_TOP = 1.5 * cm
MARGIN_BOTTOM = 2 * cm
USABLE_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

# Colors
HEADER_BG = colors.HexColor('#2C3E50')  # Dark blue-gray
POTENTIAL_COLOR = colors.HexColor('#27AE60')  # Green
RISK_COLOR = colors.HexColor('#E74C3C')  # Red
SECTION_BG = colors.HexColor('#3498DB')  # Blue
LABEL_BG = colors.HexColor('#F8F9FA')  # Very light gray
BORDER_COLOR = colors.HexColor('#BDC3C7')  # Medium gray


def get_labels(lang='IT'):
    """Get labels for the specified language."""
    if LABELS_AVAILABLE:
        return UTAnalysisLabels.get_labels(lang)

    # Fallback labels
    return {
        'headers': {
            'title': 'Archaeological Analysis Report',
            'potential_section': 'Archaeological Potential',
            'risk_section': 'Archaeological Risk',
            'methodology': 'Methodology',
            'recommendations': 'Recommendations',
            'factors_breakdown': 'Factor Breakdown',
        },
        'potential_factors': {
            'site_proximity': 'Site Proximity',
            'find_density': 'Find Density',
            'environmental': 'Environmental',
            'chronology': 'Chronology',
            'structure_presence': 'Structure Presence',
        },
        'risk_factors': {
            'urban_development': 'Urban Development',
            'natural_erosion': 'Natural Erosion',
            'agricultural_activity': 'Agricultural Activity',
            'conservation_state': 'Conservation State',
            'discovery_probability': 'Discovery Probability',
        },
        'score_levels': {
            'score': 'Score',
            'weight': 'Weight',
            'contribution': 'Contribution',
            'total': 'Total',
        },
        'pdf': {
            'report_title': 'Archaeological Analysis Report',
            'ut_identification': 'UT Identification',
            'project': 'Project',
            'ut_number': 'UT No.',
            'generated_on': 'Generated on',
            'page': 'Page',
            'of': 'of',
            'interpretation': 'Interpretation',
        },
    }


def generate_analysis_pdf(file_path, record_data, potential_result, risk_result, lang='IT'):
    """
    Generate a professional PDF report for UT analysis.

    Args:
        file_path: Output PDF file path
        record_data: Dictionary with UT record data
        potential_result: Dictionary from UTPotentialCalculator
        risk_result: Dictionary from UTRiskAssessor
        lang: Language code (IT, EN, DE, ES, FR, AR, CA)
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("ReportLab is required for PDF generation")

    # Get labels
    labels = get_labels(lang)

    # Create document
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        leftMargin=MARGIN_LEFT,
        rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM
    )

    # Build story
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.white,
        spaceAfter=0,
        alignment=TA_CENTER
    )

    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.white,
        spaceAfter=0,
        spaceBefore=0,
        alignment=TA_LEFT
    )

    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )

    # Header
    story.append(_create_header(labels, record_data, title_style))
    story.append(Spacer(1, 0.5 * cm))

    # UT Identification
    story.append(_create_identification_section(labels, record_data))
    story.append(Spacer(1, 0.5 * cm))

    # Potential Section
    story.append(_create_score_section(
        labels['headers']['potential_section'],
        potential_result,
        POTENTIAL_COLOR,
        labels,
        'potential',
        section_style
    ))
    story.append(Spacer(1, 0.5 * cm))

    # Risk Section
    story.append(_create_score_section(
        labels['headers']['risk_section'],
        risk_result,
        RISK_COLOR,
        labels,
        'risk',
        section_style
    ))
    story.append(Spacer(1, 0.5 * cm))

    # Recommendations
    if risk_result.get('recommendations'):
        story.append(_create_recommendations_section(labels, risk_result['recommendations'], section_style))
        story.append(Spacer(1, 0.5 * cm))

    # Footer with generation info
    story.append(_create_footer(labels))

    # Build PDF
    doc.build(story)


def _create_header(labels, record_data, title_style):
    """Create the report header."""
    header_data = [[
        Paragraph(labels['pdf'].get('report_title', 'Archaeological Analysis Report'), title_style)
    ]]

    header_table = Table(header_data, colWidths=[USABLE_WIDTH])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HEADER_BG),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))

    return header_table


def _create_identification_section(labels, record_data):
    """Create the UT identification section."""
    pdf_labels = labels.get('pdf', {})

    data = [
        [pdf_labels.get('project', 'Project') + ':', str(record_data.get('progetto', 'N/A')),
         pdf_labels.get('ut_number', 'UT No.') + ':', str(record_data.get('nr_ut', 'N/A'))],
        ['Comune:', str(record_data.get('comune', 'N/A')),
         'Provincia:', str(record_data.get('provincia', 'N/A'))],
    ]

    col_widths = [USABLE_WIDTH * 0.15, USABLE_WIDTH * 0.35, USABLE_WIDTH * 0.15, USABLE_WIDTH * 0.35]
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), LABEL_BG),
        ('BACKGROUND', (2, 0), (2, -1), LABEL_BG),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))

    return table


def _create_score_section(title, result, color, labels, score_type, section_style):
    """Create a score section (potential or risk)."""
    elements = []

    # Section header
    header_data = [[Paragraph(title, section_style)]]
    header_table = Table(header_data, colWidths=[USABLE_WIDTH])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(header_table)

    # Score bar
    total_score = result.get('total_score', 0)
    score_bar = _create_score_bar(total_score, color, labels)
    elements.append(score_bar)

    # Factor breakdown table
    score_labels = labels.get('score_levels', {})
    factor_labels = labels.get(f'{score_type}_factors', {})

    factor_data = [[
        score_labels.get('Factor', 'Factor'),
        score_labels.get('score', 'Score'),
        score_labels.get('weight', 'Weight'),
        score_labels.get('contribution', 'Contribution')
    ]]

    contributions = result.get('factor_contributions', {})
    for factor_key, data in contributions.items():
        factor_name = factor_labels.get(factor_key, factor_key.replace('_', ' ').title())
        factor_data.append([
            factor_name,
            f"{data['score']:.0f}",
            f"{data['weight']*100:.0f}%",
            f"{data['contribution']:.1f}"
        ])

    # Total row
    factor_data.append([
        score_labels.get('total', 'Total'),
        '',
        '',
        f"{total_score:.1f}"
    ])

    col_widths = [USABLE_WIDTH * 0.40, USABLE_WIDTH * 0.20, USABLE_WIDTH * 0.20, USABLE_WIDTH * 0.20]
    factor_table = Table(factor_data, colWidths=col_widths)
    factor_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LABEL_BG),
        ('BACKGROUND', (0, -1), (-1, -1), LABEL_BG),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(factor_table)

    # Interpretation
    interpretation = result.get('interpretation', '')
    if interpretation:
        elements.append(Spacer(1, 0.3 * cm))
        interp_style = ParagraphStyle('Interpretation', fontSize=9, spaceAfter=6, leading=12)
        elements.append(Paragraph(f"<i>{interpretation}</i>", interp_style))

    return KeepTogether(elements)


def _create_score_bar(score, color, labels):
    """Create a visual score bar."""
    bar_width = USABLE_WIDTH * 0.7
    filled_width = bar_width * (score / 100.0)

    # Create bar representation using table
    bar_data = [[
        f"{score:.1f}/100"
    ]]

    bar_table = Table(bar_data, colWidths=[USABLE_WIDTH])
    bar_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, -1), color),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))

    return bar_table


def _create_recommendations_section(labels, recommendations, section_style):
    """Create the recommendations section."""
    elements = []

    # Section header
    header_data = [[Paragraph(labels['headers'].get('recommendations', 'Recommendations'), section_style)]]
    header_table = Table(header_data, colWidths=[USABLE_WIDTH])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SECTION_BG),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(header_table)

    # Recommendations list
    rec_style = ParagraphStyle('Recommendation', fontSize=9, spaceAfter=4, leftIndent=10)
    for rec in recommendations:
        elements.append(Paragraph(f"<bullet>&bull;</bullet> {rec}", rec_style))

    return KeepTogether(elements)


def _create_footer(labels):
    """Create the report footer."""
    pdf_labels = labels.get('pdf', {})
    generated_text = f"{pdf_labels.get('generated_on', 'Generated on')}: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    footer_data = [[generated_text, 'PyArchInit - UT Analysis Module']]

    footer_table = Table(footer_data, colWidths=[USABLE_WIDTH * 0.5, USABLE_WIDTH * 0.5])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))

    return footer_table
