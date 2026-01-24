#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UT Analysis PDF Report Generator

Generates professional PDF reports for archaeological potential and risk analysis.
Supports 7 languages: IT, EN, DE, ES, FR, AR, CA
Includes descriptive text, factor analysis, and optional heatmap previews.

Created for PyArchInit QGIS Plugin
"""

import os
from datetime import datetime

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm, mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image, KeepTogether, ListFlowable, ListItem
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
INFO_BG = colors.HexColor('#EBF5FB')  # Light blue


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
            'narrative_analysis': 'Detailed Analysis',
            'maps_section': 'Cartographic Visualization',
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
            'very_low': 'Very Low',
            'low': 'Low',
            'medium': 'Medium',
            'high': 'High',
            'very_high': 'Very High',
        },
        'methodology': {
            'potential_intro': 'Archaeological potential is calculated using a weighted scoring system (0-100) based on five key factors:',
            'risk_intro': 'Archaeological risk is assessed by considering threats to archaeological heritage using a weighted scoring system (0-100):',
            'data_quality_note': 'The quality of results depends on the completeness and accuracy of input data.',
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
            'potential_map': 'Archaeological Potential Map',
            'risk_map': 'Archaeological Risk Map',
        },
    }


# Narrative text templates for each language
NARRATIVE_TEMPLATES = {
    'IT': {
        'potential_high': """L'Unità Topografica analizzata presenta un **elevato potenziale archeologico** (punteggio: {score:.1f}/100).

Questo valore indica una significativa probabilità di rinvenimenti archeologici nell'area. I fattori che contribuiscono maggiormente a questo risultato sono:

{factors}

Si raccomanda pertanto di procedere con indagini preliminari approfondite prima di qualsiasi intervento sul territorio.""",

        'potential_medium': """L'Unità Topografica presenta un **potenziale archeologico medio** (punteggio: {score:.1f}/100).

L'area mostra caratteristiche che suggeriscono una moderata possibilità di presenza di depositi archeologici. I principali fattori sono:

{factors}

Si consiglia di mantenere un'attenzione adeguata durante eventuali lavori e di prevedere un monitoraggio archeologico.""",

        'potential_low': """L'Unità Topografica presenta un **basso potenziale archeologico** (punteggio: {score:.1f}/100).

Sulla base dei dati disponibili, l'area mostra una limitata probabilità di rinvenimenti archeologici significativi. I fattori analizzati indicano:

{factors}

Tuttavia, si raccomanda comunque una verifica in fase di progettazione per eventuali interventi.""",

        'risk_high': """L'analisi del **rischio archeologico** evidenzia un livello **elevato** (punteggio: {score:.1f}/100).

Il patrimonio archeologico presente o potenziale nell'area è esposto a significative minacce. I principali fattori di rischio sono:

{factors}

È necessario prevedere misure di mitigazione e protezione urgenti per salvaguardare il patrimonio culturale.""",

        'risk_medium': """Il **rischio archeologico** risulta di livello **medio** (punteggio: {score:.1f}/100).

L'area presenta alcune criticità che potrebbero compromettere l'integrità dei depositi archeologici. I fattori rilevanti sono:

{factors}

Si raccomanda di implementare misure preventive e un monitoraggio periodico dello stato di conservazione.""",

        'risk_low': """Il **rischio archeologico** risulta **basso** (punteggio: {score:.1f}/100).

Le condizioni attuali dell'area non presentano minacce significative per il patrimonio archeologico. I fattori analizzati mostrano:

{factors}

Si consiglia comunque di mantenere un monitoraggio ordinario e di aggiornare periodicamente la valutazione.""",
    },
    'EN': {
        'potential_high': """The analyzed Topographic Unit shows a **high archaeological potential** (score: {score:.1f}/100).

This value indicates a significant probability of archaeological findings in the area. The main contributing factors are:

{factors}

It is therefore recommended to proceed with thorough preliminary investigations before any intervention in the territory.""",

        'potential_medium': """The Topographic Unit shows a **medium archaeological potential** (score: {score:.1f}/100).

The area shows characteristics suggesting a moderate possibility of archaeological deposits. The main factors are:

{factors}

It is advisable to maintain adequate attention during any works and to provide archaeological monitoring.""",

        'potential_low': """The Topographic Unit shows a **low archaeological potential** (score: {score:.1f}/100).

Based on available data, the area shows a limited probability of significant archaeological findings. The analyzed factors indicate:

{factors}

However, verification during the design phase is still recommended for any interventions.""",

        'risk_high': """The **archaeological risk** analysis shows a **high** level (score: {score:.1f}/100).

The existing or potential archaeological heritage in the area is exposed to significant threats. The main risk factors are:

{factors}

Urgent mitigation and protection measures are necessary to safeguard the cultural heritage.""",

        'risk_medium': """The **archaeological risk** is at a **medium** level (score: {score:.1f}/100).

The area presents some critical issues that could compromise the integrity of archaeological deposits. The relevant factors are:

{factors}

It is recommended to implement preventive measures and periodic monitoring of the conservation state.""",

        'risk_low': """The **archaeological risk** is **low** (score: {score:.1f}/100).

The current conditions of the area do not present significant threats to the archaeological heritage. The analyzed factors show:

{factors}

Regular monitoring and periodic reassessment are still advised.""",
    },
    'DE': {
        'potential_high': """Die analysierte Topographische Einheit weist ein **hohes archäologisches Potenzial** auf (Punktzahl: {score:.1f}/100).

Dieser Wert zeigt eine signifikante Wahrscheinlichkeit für archäologische Funde im Gebiet an. Die wichtigsten Faktoren sind:

{factors}

Es wird daher empfohlen, vor jeglichen Eingriffen gründliche Voruntersuchungen durchzuführen.""",

        'potential_medium': """Die Topographische Einheit zeigt ein **mittleres archäologisches Potenzial** (Punktzahl: {score:.1f}/100).

Das Gebiet weist Merkmale auf, die auf eine moderate Möglichkeit archäologischer Ablagerungen hindeuten. Die Hauptfaktoren sind:

{factors}

Es wird empfohlen, bei Arbeiten angemessene Aufmerksamkeit zu wahren und archäologische Überwachung vorzusehen.""",

        'potential_low': """Die Topographische Einheit zeigt ein **niedriges archäologisches Potenzial** (Punktzahl: {score:.1f}/100).

Basierend auf den verfügbaren Daten zeigt das Gebiet eine begrenzte Wahrscheinlichkeit für bedeutende archäologische Funde. Die analysierten Faktoren zeigen:

{factors}

Eine Überprüfung in der Planungsphase wird dennoch empfohlen.""",

        'risk_high': """Die Analyse des **archäologischen Risikos** zeigt ein **hohes** Niveau (Punktzahl: {score:.1f}/100).

Das vorhandene oder potenzielle archäologische Erbe im Gebiet ist erheblichen Bedrohungen ausgesetzt. Die wichtigsten Risikofaktoren sind:

{factors}

Dringende Schutzmaßnahmen sind erforderlich, um das kulturelle Erbe zu schützen.""",

        'risk_medium': """Das **archäologische Risiko** liegt auf **mittlerem** Niveau (Punktzahl: {score:.1f}/100).

Das Gebiet weist einige kritische Punkte auf, die die Integrität archäologischer Ablagerungen gefährden könnten. Die relevanten Faktoren sind:

{factors}

Es wird empfohlen, präventive Maßnahmen und regelmäßige Überwachung des Erhaltungszustands umzusetzen.""",

        'risk_low': """Das **archäologische Risiko** ist **niedrig** (Punktzahl: {score:.1f}/100).

Die aktuellen Bedingungen des Gebiets stellen keine signifikanten Bedrohungen für das archäologische Erbe dar. Die analysierten Faktoren zeigen:

{factors}

Regelmäßige Überwachung und periodische Neubewertung werden empfohlen.""",
    },
    'ES': {
        'potential_high': """La Unidad Topográfica analizada presenta un **alto potencial arqueológico** (puntuación: {score:.1f}/100).

Este valor indica una probabilidad significativa de hallazgos arqueológicos en el área. Los principales factores son:

{factors}

Se recomienda proceder con investigaciones preliminares exhaustivas antes de cualquier intervención.""",

        'potential_medium': """La Unidad Topográfica presenta un **potencial arqueológico medio** (puntuación: {score:.1f}/100).

El área muestra características que sugieren una posibilidad moderada de depósitos arqueológicos. Los principales factores son:

{factors}

Se aconseja mantener una atención adecuada durante los trabajos y prever un seguimiento arqueológico.""",

        'potential_low': """La Unidad Topográfica presenta un **bajo potencial arqueológico** (puntuación: {score:.1f}/100).

Según los datos disponibles, el área muestra una probabilidad limitada de hallazgos arqueológicos significativos. Los factores analizados indican:

{factors}

Sin embargo, se recomienda una verificación durante la fase de diseño.""",

        'risk_high': """El análisis del **riesgo arqueológico** muestra un nivel **alto** (puntuación: {score:.1f}/100).

El patrimonio arqueológico existente o potencial en el área está expuesto a amenazas significativas. Los principales factores de riesgo son:

{factors}

Es necesario prever medidas de mitigación y protección urgentes.""",

        'risk_medium': """El **riesgo arqueológico** es de nivel **medio** (puntuación: {score:.1f}/100).

El área presenta algunas criticidades que podrían comprometer la integridad de los depósitos arqueológicos. Los factores relevantes son:

{factors}

Se recomienda implementar medidas preventivas y un monitoreo periódico.""",

        'risk_low': """El **riesgo arqueológico** es **bajo** (puntuación: {score:.1f}/100).

Las condiciones actuales del área no presentan amenazas significativas para el patrimonio arqueológico. Los factores analizados muestran:

{factors}

Se recomienda mantener un monitoreo ordinario y actualizar periódicamente la evaluación.""",
    },
    'FR': {
        'potential_high': """L'Unité Topographique analysée présente un **potentiel archéologique élevé** (score: {score:.1f}/100).

Cette valeur indique une probabilité significative de découvertes archéologiques dans la zone. Les principaux facteurs sont:

{factors}

Il est donc recommandé de procéder à des investigations préliminaires approfondies avant toute intervention.""",

        'potential_medium': """L'Unité Topographique présente un **potentiel archéologique moyen** (score: {score:.1f}/100).

La zone présente des caractéristiques suggérant une possibilité modérée de dépôts archéologiques. Les principaux facteurs sont:

{factors}

Il est conseillé de maintenir une attention adéquate pendant les travaux et de prévoir un suivi archéologique.""",

        'potential_low': """L'Unité Topographique présente un **faible potentiel archéologique** (score: {score:.1f}/100).

Sur la base des données disponibles, la zone montre une probabilité limitée de découvertes archéologiques significatives. Les facteurs analysés indiquent:

{factors}

Une vérification lors de la phase de conception est néanmoins recommandée.""",

        'risk_high': """L'analyse du **risque archéologique** montre un niveau **élevé** (score: {score:.1f}/100).

Le patrimoine archéologique existant ou potentiel dans la zone est exposé à des menaces significatives. Les principaux facteurs de risque sont:

{factors}

Des mesures d'atténuation et de protection urgentes sont nécessaires.""",

        'risk_medium': """Le **risque archéologique** est de niveau **moyen** (score: {score:.1f}/100).

La zone présente certaines criticités qui pourraient compromettre l'intégrité des dépôts archéologiques. Les facteurs pertinents sont:

{factors}

Il est recommandé de mettre en œuvre des mesures préventives et un suivi périodique.""",

        'risk_low': """Le **risque archéologique** est **faible** (score: {score:.1f}/100).

Les conditions actuelles de la zone ne présentent pas de menaces significatives pour le patrimoine archéologique. Les facteurs analysés montrent:

{factors}

Un suivi régulier et une réévaluation périodique sont conseillés.""",
    },
    'AR': {
        'potential_high': """تُظهر الوحدة الطوبوغرافية المُحللة **إمكانات أثرية عالية** (النتيجة: {score:.1f}/100).

تشير هذه القيمة إلى احتمال كبير للاكتشافات الأثرية في المنطقة. العوامل الرئيسية هي:

{factors}

يُنصح بإجراء تحقيقات أولية شاملة قبل أي تدخل.""",

        'potential_medium': """تُظهر الوحدة الطوبوغرافية **إمكانات أثرية متوسطة** (النتيجة: {score:.1f}/100).

تُظهر المنطقة خصائص تشير إلى احتمال معتدل لوجود رواسب أثرية. العوامل الرئيسية هي:

{factors}

يُنصح بالحفاظ على الاهتمام الكافي أثناء الأعمال وتوفير المراقبة الأثرية.""",

        'potential_low': """تُظهر الوحدة الطوبوغرافية **إمكانات أثرية منخفضة** (النتيجة: {score:.1f}/100).

بناءً على البيانات المتاحة، تُظهر المنطقة احتمالاً محدوداً للاكتشافات الأثرية المهمة. تُشير العوامل المُحللة إلى:

{factors}

يُنصح بالتحقق أثناء مرحلة التصميم.""",

        'risk_high': """يُظهر تحليل **المخاطر الأثرية** مستوى **عالياً** (النتيجة: {score:.1f}/100).

يتعرض التراث الأثري الموجود أو المحتمل في المنطقة لتهديدات كبيرة. عوامل الخطر الرئيسية هي:

{factors}

تدابير التخفيف والحماية العاجلة ضرورية.""",

        'risk_medium': """**المخاطر الأثرية** في مستوى **متوسط** (النتيجة: {score:.1f}/100).

تُقدم المنطقة بعض النقاط الحرجة التي قد تُهدد سلامة الرواسب الأثرية. العوامل ذات الصلة هي:

{factors}

يُنصح بتنفيذ تدابير وقائية ومراقبة دورية.""",

        'risk_low': """**المخاطر الأثرية** **منخفضة** (النتيجة: {score:.1f}/100).

لا تُشكل الظروف الحالية للمنطقة تهديدات كبيرة للتراث الأثري. تُظهر العوامل المُحللة:

{factors}

يُنصح بالمراقبة المنتظمة وإعادة التقييم الدوري.""",
    },
    'CA': {
        'potential_high': """La Unitat Topogràfica analitzada presenta un **alt potencial arqueològic** (puntuació: {score:.1f}/100).

Aquest valor indica una probabilitat significativa de troballes arqueològiques a l'àrea. Els principals factors són:

{factors}

Es recomana procedir amb investigacions preliminars exhaustives abans de qualsevol intervenció.""",

        'potential_medium': """La Unitat Topogràfica presenta un **potencial arqueològic mitjà** (puntuació: {score:.1f}/100).

L'àrea mostra característiques que suggereixen una possibilitat moderada de dipòsits arqueològics. Els principals factors són:

{factors}

S'aconsella mantenir una atenció adequada durant els treballs i preveure un seguiment arqueològic.""",

        'potential_low': """La Unitat Topogràfica presenta un **baix potencial arqueològic** (puntuació: {score:.1f}/100).

Segons les dades disponibles, l'àrea mostra una probabilitat limitada de troballes arqueològiques significatives. Els factors analitzats indiquen:

{factors}

Tanmateix, es recomana una verificació durant la fase de disseny.""",

        'risk_high': """L'anàlisi del **risc arqueològic** mostra un nivell **alt** (puntuació: {score:.1f}/100).

El patrimoni arqueològic existent o potencial a l'àrea està exposat a amenaces significatives. Els principals factors de risc són:

{factors}

Cal preveure mesures de mitigació i protecció urgents.""",

        'risk_medium': """El **risc arqueològic** és de nivell **mitjà** (puntuació: {score:.1f}/100).

L'àrea presenta algunes criticitats que podrien comprometre la integritat dels dipòsits arqueològics. Els factors rellevants són:

{factors}

Es recomana implementar mesures preventives i un monitoratge periòdic.""",

        'risk_low': """El **risc arqueològic** és **baix** (puntuació: {score:.1f}/100).

Les condicions actuals de l'àrea no presenten amenaces significatives per al patrimoni arqueològic. Els factors analitzats mostren:

{factors}

Es recomana mantenir un monitoratge ordinari i actualitzar periòdicament l'avaluació.""",
    },
}


def get_score_level(score, lang='IT'):
    """Get the score level (low/medium/high) based on score value."""
    if score >= 70:
        return 'high'
    elif score >= 40:
        return 'medium'
    else:
        return 'low'


def format_factor_list(contributions, factor_labels, lang='IT'):
    """Format factor contributions as a bulleted list."""
    lines = []
    sorted_factors = sorted(
        contributions.items(),
        key=lambda x: x[1].get('contribution', 0),
        reverse=True
    )

    for factor_key, data in sorted_factors[:3]:  # Top 3 factors
        factor_name = factor_labels.get(factor_key, factor_key.replace('_', ' ').title())
        contribution = data.get('contribution', 0)
        lines.append(f"• {factor_name}: {contribution:.1f} punti")

    return '\n'.join(lines)


def generate_analysis_pdf(file_path, record_data, potential_result, risk_result,
                         lang='IT', potential_map_path=None, risk_map_path=None):
    """
    Generate a professional PDF report for UT analysis.

    Args:
        file_path: Output PDF file path
        record_data: Dictionary with UT record data
        potential_result: Dictionary from UTPotentialCalculator
        risk_result: Dictionary from UTRiskAssessor
        lang: Language code (IT, EN, DE, ES, FR, AR, CA)
        potential_map_path: Optional path to potential heatmap image
        risk_map_path: Optional path to risk heatmap image
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("ReportLab is required for PDF generation")

    # Get labels
    labels = get_labels(lang)
    lang = lang.upper() if lang else 'IT'

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
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        leading=14
    )

    narrative_style = ParagraphStyle(
        'NarrativeText',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        leading=14,
        leftIndent=10,
        rightIndent=10,
        backColor=INFO_BG,
        borderPadding=10
    )

    # Header
    story.append(_create_header(labels, record_data, title_style))
    story.append(Spacer(1, 0.5 * cm))

    # UT Identification
    story.append(_create_identification_section(labels, record_data))
    story.append(Spacer(1, 0.5 * cm))

    # Potential Section with narrative
    story.append(_create_score_section_enhanced(
        labels['headers']['potential_section'],
        potential_result,
        POTENTIAL_COLOR,
        labels,
        'potential',
        section_style,
        body_style,
        narrative_style,
        lang
    ))
    story.append(Spacer(1, 0.3 * cm))

    # Potential Map (if available)
    if potential_map_path and os.path.exists(potential_map_path):
        story.append(_create_map_section(
            labels['pdf'].get('potential_map', 'Archaeological Potential Map'),
            potential_map_path,
            section_style,
            POTENTIAL_COLOR
        ))
        story.append(Spacer(1, 0.5 * cm))

    # Risk Section with narrative
    story.append(_create_score_section_enhanced(
        labels['headers']['risk_section'],
        risk_result,
        RISK_COLOR,
        labels,
        'risk',
        section_style,
        body_style,
        narrative_style,
        lang
    ))
    story.append(Spacer(1, 0.3 * cm))

    # Risk Map (if available)
    if risk_map_path and os.path.exists(risk_map_path):
        story.append(_create_map_section(
            labels['pdf'].get('risk_map', 'Archaeological Risk Map'),
            risk_map_path,
            section_style,
            RISK_COLOR
        ))
        story.append(Spacer(1, 0.5 * cm))

    # Methodology section
    story.append(_create_methodology_section(labels, section_style, body_style))
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

    # Add definition if available
    if record_data.get('def_ut'):
        data.append([
            pdf_labels.get('definition', 'Definition') + ':',
            str(record_data.get('def_ut', '')),
            '', ''
        ])

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
        ('SPAN', (1, -1), (3, -1)) if len(data) > 2 else ('SPAN', (0, 0), (0, 0)),
    ]))

    return table


def _create_score_section_enhanced(title, result, color, labels, score_type,
                                   section_style, body_style, narrative_style, lang):
    """Create an enhanced score section with narrative text."""
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

    # Narrative text
    elements.append(Spacer(1, 0.3 * cm))
    narrative = _generate_narrative(result, labels, score_type, lang)
    if narrative:
        # Convert markdown-style bold to HTML
        narrative = narrative.replace('**', '<b>').replace('<b>', '</b>', 1)
        # Fix alternating bold tags
        import re
        narrative = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', narrative)
        elements.append(Paragraph(narrative, narrative_style))
        elements.append(Spacer(1, 0.3 * cm))

    # Factor breakdown table
    score_labels = labels.get('score_levels', {})
    factor_labels = labels.get(f'{score_type}_factors', {})

    factor_data = [[
        'Fattore' if lang == 'IT' else 'Factor',
        score_labels.get('score', 'Score'),
        score_labels.get('weight', 'Weight'),
        score_labels.get('contribution', 'Contribution')
    ]]

    contributions = result.get('factor_contributions', {})
    for factor_key, data in contributions.items():
        factor_name = factor_labels.get(factor_key, factor_key.replace('_', ' ').title())
        factor_data.append([
            factor_name,
            f"{data.get('score', 0):.0f}",
            f"{data.get('weight', 0)*100:.0f}%",
            f"{data.get('contribution', 0):.1f}"
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

    # Interpretation from result
    interpretation = result.get('interpretation', '')
    if interpretation:
        elements.append(Spacer(1, 0.3 * cm))
        interp_style = ParagraphStyle('Interpretation', fontSize=9, spaceAfter=6, leading=12)
        elements.append(Paragraph(f"<i>{interpretation}</i>", interp_style))

    return KeepTogether(elements)


def _generate_narrative(result, labels, score_type, lang):
    """Generate narrative text based on score and type."""
    total_score = result.get('total_score', 0)
    level = get_score_level(total_score, lang)

    templates = NARRATIVE_TEMPLATES.get(lang, NARRATIVE_TEMPLATES['EN'])
    template_key = f'{score_type}_{level}'
    template = templates.get(template_key, '')

    if not template:
        return ''

    # Format factors list
    factor_labels = labels.get(f'{score_type}_factors', {})
    contributions = result.get('factor_contributions', {})
    factors_text = format_factor_list(contributions, factor_labels, lang)

    return template.format(score=total_score, factors=factors_text)


def _create_score_bar(score, color, labels):
    """Create a visual score bar."""
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


def _create_map_section(title, image_path, section_style, color):
    """Create a section with a map image."""
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

    # Image
    try:
        img = Image(image_path)
        # Scale image to fit width while maintaining aspect ratio
        img_width = USABLE_WIDTH - 20
        aspect = img.imageHeight / img.imageWidth
        img_height = img_width * aspect

        # Limit height
        max_height = 10 * cm
        if img_height > max_height:
            img_height = max_height
            img_width = img_height / aspect

        img.drawWidth = img_width
        img.drawHeight = img_height
        img.hAlign = 'CENTER'

        # Wrap image in a table for border
        img_data = [[img]]
        img_table = Table(img_data, colWidths=[USABLE_WIDTH])
        img_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(img_table)
    except Exception as e:
        error_style = ParagraphStyle('Error', fontSize=9, textColor=colors.red)
        elements.append(Paragraph(f"Error loading image: {str(e)}", error_style))

    return KeepTogether(elements)


def _create_methodology_section(labels, section_style, body_style):
    """Create the methodology section."""
    elements = []

    methodology = labels.get('methodology', {})

    # Section header
    header_data = [[Paragraph(labels['headers'].get('methodology', 'Methodology'), section_style)]]
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

    # Methodology text
    elements.append(Spacer(1, 0.2 * cm))

    potential_intro = methodology.get('potential_intro', '')
    if potential_intro:
        elements.append(Paragraph(f"<b>Potenziale:</b> {potential_intro}", body_style))

    risk_intro = methodology.get('risk_intro', '')
    if risk_intro:
        elements.append(Paragraph(f"<b>Rischio:</b> {risk_intro}", body_style))

    data_note = methodology.get('data_quality_note', '')
    if data_note:
        elements.append(Spacer(1, 0.2 * cm))
        note_style = ParagraphStyle('Note', parent=body_style, fontSize=8, textColor=colors.grey)
        elements.append(Paragraph(f"<i>Nota: {data_note}</i>", note_style))

    return KeepTogether(elements)


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
