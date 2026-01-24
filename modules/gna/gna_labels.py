# -*- coding: utf-8 -*-
"""
GNA Labels - Multilingual UI Labels

Provides translated labels for GNA export interface in 7 languages:
- Italian (it)
- English (en)
- German (de)
- Spanish (es)
- French (fr)
- Arabic (ar)
- Catalan (ca)
"""

GNA_LABELS = {
    # Dialog titles and main UI
    'dialog_title': {
        'it': 'Esporta in GNA GeoPackage',
        'en': 'Export to GNA GeoPackage',
        'de': 'In GNA GeoPackage exportieren',
        'es': 'Exportar a GNA GeoPackage',
        'fr': 'Exporter vers GNA GeoPackage',
        'ar': 'تصدير إلى GNA GeoPackage',
        'ca': 'Exporta a GNA GeoPackage',
    },

    # Section headers
    'section_project': {
        'it': 'Progetto',
        'en': 'Project',
        'de': 'Projekt',
        'es': 'Proyecto',
        'fr': 'Projet',
        'ar': 'المشروع',
        'ca': 'Projecte',
    },
    'section_area': {
        'it': 'Area di Progetto (MOPR)',
        'en': 'Project Area (MOPR)',
        'de': 'Projektgebiet (MOPR)',
        'es': 'Área del Proyecto (MOPR)',
        'fr': 'Zone du Projet (MOPR)',
        'ar': 'منطقة المشروع (MOPR)',
        'ca': 'Àrea del Projecte (MOPR)',
    },
    'section_layers': {
        'it': 'Layer da Esportare',
        'en': 'Layers to Export',
        'de': 'Zu exportierende Layer',
        'es': 'Capas a Exportar',
        'fr': 'Couches à Exporter',
        'ar': 'الطبقات للتصدير',
        'ca': 'Capes a Exportar',
    },
    'section_options': {
        'it': 'Opzioni Heatmap',
        'en': 'Heatmap Options',
        'de': 'Heatmap-Optionen',
        'es': 'Opciones de Mapa de Calor',
        'fr': 'Options Carte de Chaleur',
        'ar': 'خيارات الخريطة الحرارية',
        'ca': 'Opcions del Mapa de Calor',
    },
    'section_output': {
        'it': 'Output',
        'en': 'Output',
        'de': 'Ausgabe',
        'es': 'Salida',
        'fr': 'Sortie',
        'ar': 'المخرجات',
        'ca': 'Sortida',
    },

    # Field labels
    'label_project_code': {
        'it': 'Codice Progetto:',
        'en': 'Project Code:',
        'de': 'Projektcode:',
        'es': 'Código de Proyecto:',
        'fr': 'Code Projet:',
        'ar': 'رمز المشروع:',
        'ca': 'Codi del Projecte:',
    },
    'label_project_title': {
        'it': 'Titolo:',
        'en': 'Title:',
        'de': 'Titel:',
        'es': 'Título:',
        'fr': 'Titre:',
        'ar': 'العنوان:',
        'ca': 'Títol:',
    },
    'label_responsible': {
        'it': 'Responsabile:',
        'en': 'Responsible:',
        'de': 'Verantwortlich:',
        'es': 'Responsable:',
        'fr': 'Responsable:',
        'ar': 'المسؤول:',
        'ca': 'Responsable:',
    },
    'label_select_polygon': {
        'it': 'Seleziona Poligono:',
        'en': 'Select Polygon:',
        'de': 'Polygon auswählen:',
        'es': 'Seleccionar Polígono:',
        'fr': 'Sélectionner Polygone:',
        'ar': 'اختر المضلع:',
        'ca': 'Selecciona Polígon:',
    },
    'label_from_layer': {
        'it': 'Da Layer:',
        'en': 'From Layer:',
        'de': 'Von Layer:',
        'es': 'Desde Capa:',
        'fr': 'Depuis Couche:',
        'ar': 'من الطبقة:',
        'ca': 'Des de Capa:',
    },
    'label_draw_polygon': {
        'it': 'Disegna Poligono',
        'en': 'Draw Polygon',
        'de': 'Polygon zeichnen',
        'es': 'Dibujar Polígono',
        'fr': 'Dessiner Polygone',
        'ar': 'ارسم مضلع',
        'ca': 'Dibuixa Polígon',
    },

    # Layer checkboxes
    'layer_mosi': {
        'it': 'MOSI - Siti Archeologici',
        'en': 'MOSI - Archaeological Sites',
        'de': 'MOSI - Archäologische Stätten',
        'es': 'MOSI - Sitios Arqueológicos',
        'fr': 'MOSI - Sites Archéologiques',
        'ar': 'MOSI - المواقع الأثرية',
        'ca': 'MOSI - Jaciments Arqueològics',
    },
    'layer_vrp': {
        'it': 'VRP - Potenziale Archeologico',
        'en': 'VRP - Archaeological Potential',
        'de': 'VRP - Archäologisches Potential',
        'es': 'VRP - Potencial Arqueológico',
        'fr': 'VRP - Potentiel Archéologique',
        'ar': 'VRP - الإمكانات الأثرية',
        'ca': 'VRP - Potencial Arqueològic',
    },
    'layer_vrd': {
        'it': 'VRD - Rischio Archeologico',
        'en': 'VRD - Archaeological Risk',
        'de': 'VRD - Archäologisches Risiko',
        'es': 'VRD - Riesgo Arqueológico',
        'fr': 'VRD - Risque Archéologique',
        'ar': 'VRD - المخاطر الأثرية',
        'ca': 'VRD - Risc Arqueològic',
    },

    # Heatmap options
    'label_method': {
        'it': 'Metodo Interpolazione:',
        'en': 'Interpolation Method:',
        'de': 'Interpolationsmethode:',
        'es': 'Método de Interpolación:',
        'fr': 'Méthode d\'Interpolation:',
        'ar': 'طريقة الاستيفاء:',
        'ca': 'Mètode d\'Interpolació:',
    },
    'label_cell_size': {
        'it': 'Dimensione Cella (m):',
        'en': 'Cell Size (m):',
        'de': 'Zellgröße (m):',
        'es': 'Tamaño de Celda (m):',
        'fr': 'Taille de Cellule (m):',
        'ar': 'حجم الخلية (م):',
        'ca': 'Mida de Cel·la (m):',
    },
    'method_kde': {
        'it': 'KDE (Kernel Density)',
        'en': 'KDE (Kernel Density)',
        'de': 'KDE (Kernel Density)',
        'es': 'KDE (Densidad de Kernel)',
        'fr': 'KDE (Densité de Noyau)',
        'ar': 'KDE (كثافة النواة)',
        'ca': 'KDE (Densitat de Kernel)',
    },
    'method_idw': {
        'it': 'IDW (Inverse Distance)',
        'en': 'IDW (Inverse Distance)',
        'de': 'IDW (Inverse Distanz)',
        'es': 'IDW (Distancia Inversa)',
        'fr': 'IDW (Distance Inverse)',
        'ar': 'IDW (المسافة العكسية)',
        'ca': 'IDW (Distància Inversa)',
    },
    'method_grid': {
        'it': 'Griglia',
        'en': 'Grid',
        'de': 'Gitter',
        'es': 'Cuadrícula',
        'fr': 'Grille',
        'ar': 'شبكة',
        'ca': 'Quadrícula',
    },

    # Output options
    'label_output_path': {
        'it': 'Percorso Output:',
        'en': 'Output Path:',
        'de': 'Ausgabepfad:',
        'es': 'Ruta de Salida:',
        'fr': 'Chemin de Sortie:',
        'ar': 'مسار المخرجات:',
        'ca': 'Camí de Sortida:',
    },
    'label_load_layers': {
        'it': 'Carica layer in QGIS',
        'en': 'Load layers in QGIS',
        'de': 'Layer in QGIS laden',
        'es': 'Cargar capas en QGIS',
        'fr': 'Charger les couches dans QGIS',
        'ar': 'تحميل الطبقات في QGIS',
        'ca': 'Carrega capes a QGIS',
    },
    'browse': {
        'it': 'Sfoglia...',
        'en': 'Browse...',
        'de': 'Durchsuchen...',
        'es': 'Examinar...',
        'fr': 'Parcourir...',
        'ar': 'تصفح...',
        'ca': 'Navega...',
    },

    # Buttons
    'btn_export': {
        'it': 'Esporta',
        'en': 'Export',
        'de': 'Exportieren',
        'es': 'Exportar',
        'fr': 'Exporter',
        'ar': 'تصدير',
        'ca': 'Exporta',
    },
    'btn_cancel': {
        'it': 'Annulla',
        'en': 'Cancel',
        'de': 'Abbrechen',
        'es': 'Cancelar',
        'fr': 'Annuler',
        'ar': 'إلغاء',
        'ca': 'Cancel·la',
    },
    'btn_preview': {
        'it': 'Anteprima',
        'en': 'Preview',
        'de': 'Vorschau',
        'es': 'Vista Previa',
        'fr': 'Aperçu',
        'ar': 'معاينة',
        'ca': 'Previsualitza',
    },

    # Status messages
    'status_exporting': {
        'it': 'Esportazione in corso...',
        'en': 'Exporting...',
        'de': 'Exportiere...',
        'es': 'Exportando...',
        'fr': 'Exportation en cours...',
        'ar': 'جارٍ التصدير...',
        'ca': 'Exportant...',
    },
    'status_creating_mopr': {
        'it': 'Creazione layer MOPR...',
        'en': 'Creating MOPR layer...',
        'de': 'Erstelle MOPR-Layer...',
        'es': 'Creando capa MOPR...',
        'fr': 'Création de la couche MOPR...',
        'ar': 'إنشاء طبقة MOPR...',
        'ca': 'Creant capa MOPR...',
    },
    'status_creating_mosi': {
        'it': 'Creazione layer MOSI...',
        'en': 'Creating MOSI layer...',
        'de': 'Erstelle MOSI-Layer...',
        'es': 'Creando capa MOSI...',
        'fr': 'Création de la couche MOSI...',
        'ar': 'إنشاء طبقة MOSI...',
        'ca': 'Creant capa MOSI...',
    },
    'status_generating_vrp': {
        'it': 'Generazione mappa VRP...',
        'en': 'Generating VRP map...',
        'de': 'Generiere VRP-Karte...',
        'es': 'Generando mapa VRP...',
        'fr': 'Génération de la carte VRP...',
        'ar': 'توليد خريطة VRP...',
        'ca': 'Generant mapa VRP...',
    },
    'status_generating_vrd': {
        'it': 'Generazione mappa VRD...',
        'en': 'Generating VRD map...',
        'de': 'Generiere VRD-Karte...',
        'es': 'Generando mapa VRD...',
        'fr': 'Génération de la carte VRD...',
        'ar': 'توليد خريطة VRD...',
        'ca': 'Generant mapa VRD...',
    },
    'status_complete': {
        'it': 'Esportazione completata!',
        'en': 'Export complete!',
        'de': 'Export abgeschlossen!',
        'es': '¡Exportación completada!',
        'fr': 'Exportation terminée!',
        'ar': 'اكتمل التصدير!',
        'ca': 'Exportació completada!',
    },

    # Error messages
    'error_no_polygon': {
        'it': 'Selezionare un poligono per l\'area di progetto',
        'en': 'Select a polygon for the project area',
        'de': 'Wählen Sie ein Polygon für das Projektgebiet',
        'es': 'Seleccione un polígono para el área del proyecto',
        'fr': 'Sélectionnez un polygone pour la zone du projet',
        'ar': 'اختر مضلعًا لمنطقة المشروع',
        'ca': 'Seleccioneu un polígon per a l\'àrea del projecte',
    },
    'error_no_records': {
        'it': 'Nessun record UT da esportare',
        'en': 'No UT records to export',
        'de': 'Keine UT-Datensätze zum Exportieren',
        'es': 'No hay registros UT para exportar',
        'fr': 'Aucun enregistrement UT à exporter',
        'ar': 'لا توجد سجلات UT للتصدير',
        'ca': 'No hi ha registres UT per exportar',
    },
    'error_invalid_polygon': {
        'it': 'Geometria del poligono non valida',
        'en': 'Invalid polygon geometry',
        'de': 'Ungültige Polygongeometrie',
        'es': 'Geometría de polígono no válida',
        'fr': 'Géométrie du polygone invalide',
        'ar': 'هندسة المضلع غير صالحة',
        'ca': 'Geometria del polígon no vàlida',
    },
    'error_export_failed': {
        'it': 'Errore durante l\'esportazione: {0}',
        'en': 'Export failed: {0}',
        'de': 'Export fehlgeschlagen: {0}',
        'es': 'Error de exportación: {0}',
        'fr': 'Échec de l\'exportation: {0}',
        'ar': 'فشل التصدير: {0}',
        'ca': 'Error d\'exportació: {0}',
    },
    'error_no_scores': {
        'it': 'Calcolare prima i punteggi di potenziale/rischio',
        'en': 'Calculate potential/risk scores first',
        'de': 'Berechnen Sie zuerst die Potential-/Risiko-Werte',
        'es': 'Calcule primero las puntuaciones de potencial/riesgo',
        'fr': 'Calculez d\'abord les scores de potentiel/risque',
        'ar': 'احسب درجات الإمكانات/المخاطر أولاً',
        'ca': 'Calculeu primer les puntuacions de potencial/risc',
    },

    # Success messages
    'success_export': {
        'it': 'GeoPackage GNA creato con successo:\n{0}\n\nLayer: {1}\nRecord: {2}',
        'en': 'GNA GeoPackage created successfully:\n{0}\n\nLayers: {1}\nRecords: {2}',
        'de': 'GNA GeoPackage erfolgreich erstellt:\n{0}\n\nLayer: {1}\nDatensätze: {2}',
        'es': 'GNA GeoPackage creado con éxito:\n{0}\n\nCapas: {1}\nRegistros: {2}',
        'fr': 'GNA GeoPackage créé avec succès:\n{0}\n\nCouches: {1}\nEnregistrements: {2}',
        'ar': 'تم إنشاء GNA GeoPackage بنجاح:\n{0}\n\nالطبقات: {1}\nالسجلات: {2}',
        'ca': 'GNA GeoPackage creat amb èxit:\n{0}\n\nCapes: {1}\nRegistres: {2}',
    },

    # VRP Classification labels
    'vrp_nv': {
        'it': 'Non valutabile',
        'en': 'Not assessable',
        'de': 'Nicht bewertbar',
        'es': 'No evaluable',
        'fr': 'Non évaluable',
        'ar': 'غير قابل للتقييم',
        'ca': 'No avaluable',
    },
    'vrp_nu': {
        'it': 'Nullo',
        'en': 'Null',
        'de': 'Null',
        'es': 'Nulo',
        'fr': 'Nul',
        'ar': 'منعدم',
        'ca': 'Nul',
    },
    'vrp_ba': {
        'it': 'Basso',
        'en': 'Low',
        'de': 'Niedrig',
        'es': 'Bajo',
        'fr': 'Faible',
        'ar': 'منخفض',
        'ca': 'Baix',
    },
    'vrp_me': {
        'it': 'Medio',
        'en': 'Medium',
        'de': 'Mittel',
        'es': 'Medio',
        'fr': 'Moyen',
        'ar': 'متوسط',
        'ca': 'Mitjà',
    },
    'vrp_al': {
        'it': 'Alto',
        'en': 'High',
        'de': 'Hoch',
        'es': 'Alto',
        'fr': 'Élevé',
        'ar': 'مرتفع',
        'ca': 'Alt',
    },

    # Tooltips
    'tooltip_mopr': {
        'it': 'MOPR: Perimetro del progetto - Delimita l\'area di studio',
        'en': 'MOPR: Project perimeter - Delimits the study area',
        'de': 'MOPR: Projektperimeter - Begrenzt das Untersuchungsgebiet',
        'es': 'MOPR: Perímetro del proyecto - Delimita el área de estudio',
        'fr': 'MOPR: Périmètre du projet - Délimite la zone d\'étude',
        'ar': 'MOPR: محيط المشروع - يحدد منطقة الدراسة',
        'ca': 'MOPR: Perímetre del projecte - Delimita l\'àrea d\'estudi',
    },
    'tooltip_mosi': {
        'it': 'MOSI: Monumenti e Siti - I record UT esportati',
        'en': 'MOSI: Monuments and Sites - The exported UT records',
        'de': 'MOSI: Monumente und Stätten - Die exportierten UT-Datensätze',
        'es': 'MOSI: Monumentos y Sitios - Los registros UT exportados',
        'fr': 'MOSI: Monuments et Sites - Les enregistrements UT exportés',
        'ar': 'MOSI: المعالم والمواقع - سجلات UT المصدرة',
        'ca': 'MOSI: Monuments i Jaciments - Els registres UT exportats',
    },
    'tooltip_vrp': {
        'it': 'VRP: Valutazione Rischio Potenziale - Mappa del potenziale archeologico classificata in 5 livelli',
        'en': 'VRP: Potential Risk Assessment - Archaeological potential map classified in 5 levels',
        'de': 'VRP: Potentialrisikobewertung - Archäologische Potentialkarte in 5 Stufen klassifiziert',
        'es': 'VRP: Evaluación de Riesgo Potencial - Mapa de potencial arqueológico clasificado en 5 niveles',
        'fr': 'VRP: Évaluation du Risque Potentiel - Carte du potentiel archéologique classée en 5 niveaux',
        'ar': 'VRP: تقييم المخاطر المحتملة - خريطة الإمكانات الأثرية مصنفة في 5 مستويات',
        'ca': 'VRP: Avaluació del Risc Potencial - Mapa del potencial arqueològic classificat en 5 nivells',
    },
    'tooltip_vrd': {
        'it': 'VRD: Valutazione Rischio Diretto - Mappa del rischio archeologico classificata in 4 livelli',
        'en': 'VRD: Direct Risk Assessment - Archaeological risk map classified in 4 levels',
        'de': 'VRD: Direkte Risikobewertung - Archäologische Risikokarte in 4 Stufen klassifiziert',
        'es': 'VRD: Evaluación de Riesgo Directo - Mapa de riesgo arqueológico clasificado en 4 niveles',
        'fr': 'VRD: Évaluation du Risque Direct - Carte du risque archéologique classée en 4 niveaux',
        'ar': 'VRD: تقييم المخاطر المباشرة - خريطة المخاطر الأثرية مصنفة في 4 مستويات',
        'ca': 'VRD: Avaluació del Risc Directe - Mapa del risc arqueològic classificat en 4 nivells',
    },
}


def get_label(key, language='it'):
    """
    Get a translated label.

    Args:
        key: Label key from GNA_LABELS
        language: Language code (it, en, de, es, fr, ar, ca)

    Returns:
        Translated string or key if not found
    """
    if key not in GNA_LABELS:
        return key

    labels = GNA_LABELS[key]

    # Try exact language
    if language in labels:
        return labels[language]

    # Fallback to Italian
    if 'it' in labels:
        return labels['it']

    # Return first available
    return next(iter(labels.values()), key)


def get_all_labels(language='it'):
    """
    Get all labels for a language.

    Args:
        language: Language code

    Returns:
        dict with all labels in the specified language
    """
    result = {}
    for key in GNA_LABELS:
        result[key] = get_label(key, language)
    return result
