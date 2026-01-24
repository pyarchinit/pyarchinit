#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UT Analysis Labels - 7-language support for archaeological potential and risk analysis.

Supported languages:
- IT: Italian
- EN: English
- DE: German
- ES: Spanish
- FR: French
- AR: Arabic
- CA: Catalan

Created for PyArchInit QGIS Plugin
"""


class UTAnalysisLabels:
    """Centralized labels for UT analysis in 7 languages."""

    # =========================================================================
    # MAIN SECTION HEADERS
    # =========================================================================
    HEADERS = {
        'IT': {
            'title': 'Analisi del Potenziale e Rischio Archeologico',
            'potential_section': 'Potenziale Archeologico',
            'risk_section': 'Rischio Archeologico',
            'heatmap_section': 'Generazione Mappe di Calore',
            'methodology': 'Metodologia',
            'results': 'Risultati',
            'recommendations': 'Raccomandazioni',
            'factors_breakdown': 'Dettaglio Fattori',
            'data_sources': 'Fonti Dati',
            'export_options': 'Opzioni di Esportazione',
        },
        'EN': {
            'title': 'Archaeological Potential and Risk Analysis',
            'potential_section': 'Archaeological Potential',
            'risk_section': 'Archaeological Risk',
            'heatmap_section': 'Heatmap Generation',
            'methodology': 'Methodology',
            'results': 'Results',
            'recommendations': 'Recommendations',
            'factors_breakdown': 'Factor Breakdown',
            'data_sources': 'Data Sources',
            'export_options': 'Export Options',
        },
        'DE': {
            'title': 'Archäologische Potenzial- und Risikoanalyse',
            'potential_section': 'Archäologisches Potenzial',
            'risk_section': 'Archäologisches Risiko',
            'heatmap_section': 'Heatmap-Generierung',
            'methodology': 'Methodik',
            'results': 'Ergebnisse',
            'recommendations': 'Empfehlungen',
            'factors_breakdown': 'Faktorenaufschlüsselung',
            'data_sources': 'Datenquellen',
            'export_options': 'Exportoptionen',
        },
        'ES': {
            'title': 'Análisis de Potencial y Riesgo Arqueológico',
            'potential_section': 'Potencial Arqueológico',
            'risk_section': 'Riesgo Arqueológico',
            'heatmap_section': 'Generación de Mapas de Calor',
            'methodology': 'Metodología',
            'results': 'Resultados',
            'recommendations': 'Recomendaciones',
            'factors_breakdown': 'Desglose de Factores',
            'data_sources': 'Fuentes de Datos',
            'export_options': 'Opciones de Exportación',
        },
        'FR': {
            'title': 'Analyse du Potentiel et du Risque Archéologique',
            'potential_section': 'Potentiel Archéologique',
            'risk_section': 'Risque Archéologique',
            'heatmap_section': 'Génération de Cartes de Chaleur',
            'methodology': 'Méthodologie',
            'results': 'Résultats',
            'recommendations': 'Recommandations',
            'factors_breakdown': 'Détail des Facteurs',
            'data_sources': 'Sources de Données',
            'export_options': 'Options d\'Exportation',
        },
        'AR': {
            'title': 'تحليل الإمكانات والمخاطر الأثرية',
            'potential_section': 'الإمكانات الأثرية',
            'risk_section': 'المخاطر الأثرية',
            'heatmap_section': 'إنشاء خرائط الحرارة',
            'methodology': 'المنهجية',
            'results': 'النتائج',
            'recommendations': 'التوصيات',
            'factors_breakdown': 'تفصيل العوامل',
            'data_sources': 'مصادر البيانات',
            'export_options': 'خيارات التصدير',
        },
        'CA': {
            'title': 'Anàlisi del Potencial i Risc Arqueològic',
            'potential_section': 'Potencial Arqueològic',
            'risk_section': 'Risc Arqueològic',
            'heatmap_section': 'Generació de Mapes de Calor',
            'methodology': 'Metodologia',
            'results': 'Resultats',
            'recommendations': 'Recomanacions',
            'factors_breakdown': 'Desglossament de Factors',
            'data_sources': 'Fonts de Dades',
            'export_options': 'Opcions d\'Exportació',
        },
    }

    # =========================================================================
    # POTENTIAL FACTORS
    # =========================================================================
    POTENTIAL_FACTORS = {
        'IT': {
            'site_proximity': 'Prossimità a siti noti',
            'site_proximity_desc': 'Distanza dai siti archeologici conosciuti nella zona',
            'find_density': 'Densità reperti',
            'find_density_desc': 'Numero di reperti per metro quadro e concentrazioni',
            'environmental': 'Fattori ambientali',
            'environmental_desc': 'Pendenza del terreno, visibilità, uso del suolo',
            'chronology': 'Cronologia/Periodi',
            'chronology_desc': 'Affidabilità della datazione e fasi cronologiche',
            'structure_presence': 'Presenza strutture',
            'structure_presence_desc': 'Ubicazione di strutture archeologiche nelle vicinanze',
        },
        'EN': {
            'site_proximity': 'Proximity to known sites',
            'site_proximity_desc': 'Distance from known archaeological sites in the area',
            'find_density': 'Find density',
            'find_density_desc': 'Number of finds per square meter and concentrations',
            'environmental': 'Environmental factors',
            'environmental_desc': 'Terrain slope, visibility, land use',
            'chronology': 'Chronology/Periods',
            'chronology_desc': 'Dating reliability and chronological phases',
            'structure_presence': 'Structure presence',
            'structure_presence_desc': 'Location of archaeological structures nearby',
        },
        'DE': {
            'site_proximity': 'Nähe zu bekannten Fundstellen',
            'site_proximity_desc': 'Entfernung zu bekannten archäologischen Fundstellen',
            'find_density': 'Funddichte',
            'find_density_desc': 'Anzahl der Funde pro Quadratmeter und Konzentrationen',
            'environmental': 'Umweltfaktoren',
            'environmental_desc': 'Geländeneigung, Sichtbarkeit, Landnutzung',
            'chronology': 'Chronologie/Perioden',
            'chronology_desc': 'Datierungszuverlässigkeit und chronologische Phasen',
            'structure_presence': 'Strukturpräsenz',
            'structure_presence_desc': 'Lage archäologischer Strukturen in der Nähe',
        },
        'ES': {
            'site_proximity': 'Proximidad a sitios conocidos',
            'site_proximity_desc': 'Distancia de sitios arqueológicos conocidos en la zona',
            'find_density': 'Densidad de hallazgos',
            'find_density_desc': 'Número de hallazgos por metro cuadrado y concentraciones',
            'environmental': 'Factores ambientales',
            'environmental_desc': 'Pendiente del terreno, visibilidad, uso del suelo',
            'chronology': 'Cronología/Períodos',
            'chronology_desc': 'Fiabilidad de la datación y fases cronológicas',
            'structure_presence': 'Presencia de estructuras',
            'structure_presence_desc': 'Ubicación de estructuras arqueológicas cercanas',
        },
        'FR': {
            'site_proximity': 'Proximité des sites connus',
            'site_proximity_desc': 'Distance des sites archéologiques connus dans la zone',
            'find_density': 'Densité des trouvailles',
            'find_density_desc': 'Nombre de trouvailles par mètre carré et concentrations',
            'environmental': 'Facteurs environnementaux',
            'environmental_desc': 'Pente du terrain, visibilité, utilisation du sol',
            'chronology': 'Chronologie/Périodes',
            'chronology_desc': 'Fiabilité de la datation et phases chronologiques',
            'structure_presence': 'Présence de structures',
            'structure_presence_desc': 'Emplacement des structures archéologiques à proximité',
        },
        'AR': {
            'site_proximity': 'القرب من المواقع المعروفة',
            'site_proximity_desc': 'المسافة من المواقع الأثرية المعروفة في المنطقة',
            'find_density': 'كثافة اللقى',
            'find_density_desc': 'عدد اللقى لكل متر مربع والتركيزات',
            'environmental': 'العوامل البيئية',
            'environmental_desc': 'انحدار التضاريس، الرؤية، استخدام الأرض',
            'chronology': 'التسلسل الزمني/الفترات',
            'chronology_desc': 'موثوقية التأريخ والمراحل الزمنية',
            'structure_presence': 'وجود الهياكل',
            'structure_presence_desc': 'موقع الهياكل الأثرية القريبة',
        },
        'CA': {
            'site_proximity': 'Proximitat a llocs coneguts',
            'site_proximity_desc': 'Distància dels llocs arqueològics coneguts a la zona',
            'find_density': 'Densitat de troballes',
            'find_density_desc': 'Nombre de troballes per metre quadrat i concentracions',
            'environmental': 'Factors ambientals',
            'environmental_desc': 'Pendent del terreny, visibilitat, ús del sòl',
            'chronology': 'Cronologia/Períodes',
            'chronology_desc': 'Fiabilitat de la datació i fases cronològiques',
            'structure_presence': 'Presència d\'estructures',
            'structure_presence_desc': 'Ubicació d\'estructures arqueològiques properes',
        },
    }

    # =========================================================================
    # RISK FACTORS
    # =========================================================================
    RISK_FACTORS = {
        'IT': {
            'urban_development': 'Sviluppo urbanistico',
            'urban_development_desc': 'Prossimità a zone urbanizzate e progetti edilizi',
            'natural_erosion': 'Erosione naturale',
            'natural_erosion_desc': 'Rischio di erosione da pendenza, drenaggio, agenti atmosferici',
            'agricultural_activity': 'Attività agricola',
            'agricultural_activity_desc': 'Intensità delle lavorazioni agricole e arature profonde',
            'conservation_state': 'Stato di conservazione',
            'conservation_state_desc': 'Condizione attuale dei depositi archeologici',
            'discovery_probability': 'Probabilità di scoperta',
            'discovery_probability_desc': 'Probabilità di rinvenire ulteriori resti archeologici',
        },
        'EN': {
            'urban_development': 'Urban development',
            'urban_development_desc': 'Proximity to urbanized areas and construction projects',
            'natural_erosion': 'Natural erosion',
            'natural_erosion_desc': 'Erosion risk from slope, drainage, weathering',
            'agricultural_activity': 'Agricultural activity',
            'agricultural_activity_desc': 'Intensity of agricultural works and deep plowing',
            'conservation_state': 'Conservation state',
            'conservation_state_desc': 'Current condition of archaeological deposits',
            'discovery_probability': 'Discovery probability',
            'discovery_probability_desc': 'Probability of finding additional archaeological remains',
        },
        'DE': {
            'urban_development': 'Stadtentwicklung',
            'urban_development_desc': 'Nähe zu urbanisierten Gebieten und Bauprojekten',
            'natural_erosion': 'Natürliche Erosion',
            'natural_erosion_desc': 'Erosionsrisiko durch Hangneigung, Entwässerung, Verwitterung',
            'agricultural_activity': 'Landwirtschaftliche Tätigkeit',
            'agricultural_activity_desc': 'Intensität der landwirtschaftlichen Arbeiten und Tiefpflügen',
            'conservation_state': 'Erhaltungszustand',
            'conservation_state_desc': 'Aktueller Zustand der archäologischen Ablagerungen',
            'discovery_probability': 'Entdeckungswahrscheinlichkeit',
            'discovery_probability_desc': 'Wahrscheinlichkeit, weitere archäologische Überreste zu finden',
        },
        'ES': {
            'urban_development': 'Desarrollo urbanístico',
            'urban_development_desc': 'Proximidad a zonas urbanizadas y proyectos de construcción',
            'natural_erosion': 'Erosión natural',
            'natural_erosion_desc': 'Riesgo de erosión por pendiente, drenaje, meteorización',
            'agricultural_activity': 'Actividad agrícola',
            'agricultural_activity_desc': 'Intensidad de trabajos agrícolas y arado profundo',
            'conservation_state': 'Estado de conservación',
            'conservation_state_desc': 'Condición actual de los depósitos arqueológicos',
            'discovery_probability': 'Probabilidad de descubrimiento',
            'discovery_probability_desc': 'Probabilidad de encontrar restos arqueológicos adicionales',
        },
        'FR': {
            'urban_development': 'Développement urbain',
            'urban_development_desc': 'Proximité des zones urbanisées et des projets de construction',
            'natural_erosion': 'Érosion naturelle',
            'natural_erosion_desc': 'Risque d\'érosion par la pente, le drainage, l\'altération',
            'agricultural_activity': 'Activité agricole',
            'agricultural_activity_desc': 'Intensité des travaux agricoles et labour profond',
            'conservation_state': 'État de conservation',
            'conservation_state_desc': 'État actuel des dépôts archéologiques',
            'discovery_probability': 'Probabilité de découverte',
            'discovery_probability_desc': 'Probabilité de trouver des vestiges archéologiques supplémentaires',
        },
        'AR': {
            'urban_development': 'التطوير العمراني',
            'urban_development_desc': 'القرب من المناطق الحضرية ومشاريع البناء',
            'natural_erosion': 'التآكل الطبيعي',
            'natural_erosion_desc': 'خطر التآكل من الانحدار والصرف والتجوية',
            'agricultural_activity': 'النشاط الزراعي',
            'agricultural_activity_desc': 'كثافة الأعمال الزراعية والحرث العميق',
            'conservation_state': 'حالة الحفظ',
            'conservation_state_desc': 'الحالة الراهنة للرواسب الأثرية',
            'discovery_probability': 'احتمال الاكتشاف',
            'discovery_probability_desc': 'احتمال العثور على بقايا أثرية إضافية',
        },
        'CA': {
            'urban_development': 'Desenvolupament urbanístic',
            'urban_development_desc': 'Proximitat a zones urbanitzades i projectes de construcció',
            'natural_erosion': 'Erosió natural',
            'natural_erosion_desc': 'Risc d\'erosió per pendent, drenatge, meteorització',
            'agricultural_activity': 'Activitat agrícola',
            'agricultural_activity_desc': 'Intensitat dels treballs agrícoles i llaurada profunda',
            'conservation_state': 'Estat de conservació',
            'conservation_state_desc': 'Condició actual dels dipòsits arqueològics',
            'discovery_probability': 'Probabilitat de descobriment',
            'discovery_probability_desc': 'Probabilitat de trobar restes arqueològiques addicionals',
        },
    }

    # =========================================================================
    # HEATMAP METHODS
    # =========================================================================
    HEATMAP_METHODS = {
        'IT': {
            'kde': 'Stima della Densità del Kernel (KDE)',
            'kde_desc': 'Crea una superficie continua liscia basata sulla densità dei punti',
            'idw': 'Ponderazione Inversa della Distanza (IDW)',
            'idw_desc': 'Interpola valori usando una media ponderata basata sulla distanza',
            'grid': 'Aggregazione a Griglia',
            'grid_desc': 'Divide l\'area in celle e aggrega i valori per cella',
            'cell_size': 'Dimensione cella (m)',
            'bandwidth': 'Larghezza di banda',
            'power': 'Potenza',
            'search_radius': 'Raggio di ricerca (m)',
        },
        'EN': {
            'kde': 'Kernel Density Estimation (KDE)',
            'kde_desc': 'Creates a smooth continuous surface based on point density',
            'idw': 'Inverse Distance Weighting (IDW)',
            'idw_desc': 'Interpolates values using a distance-weighted average',
            'grid': 'Grid-Based Aggregation',
            'grid_desc': 'Divides area into cells and aggregates values per cell',
            'cell_size': 'Cell size (m)',
            'bandwidth': 'Bandwidth',
            'power': 'Power',
            'search_radius': 'Search radius (m)',
        },
        'DE': {
            'kde': 'Kerndichteschätzung (KDE)',
            'kde_desc': 'Erstellt eine glatte kontinuierliche Oberfläche basierend auf Punktdichte',
            'idw': 'Inverse Distanzgewichtung (IDW)',
            'idw_desc': 'Interpoliert Werte mit einem entfernungsgewichteten Durchschnitt',
            'grid': 'Gitterbasierte Aggregation',
            'grid_desc': 'Teilt das Gebiet in Zellen und aggregiert Werte pro Zelle',
            'cell_size': 'Zellengröße (m)',
            'bandwidth': 'Bandbreite',
            'power': 'Potenz',
            'search_radius': 'Suchradius (m)',
        },
        'ES': {
            'kde': 'Estimación de Densidad del Kernel (KDE)',
            'kde_desc': 'Crea una superficie continua suave basada en la densidad de puntos',
            'idw': 'Ponderación Inversa de la Distancia (IDW)',
            'idw_desc': 'Interpola valores usando un promedio ponderado por distancia',
            'grid': 'Agregación Basada en Cuadrícula',
            'grid_desc': 'Divide el área en celdas y agrega valores por celda',
            'cell_size': 'Tamaño de celda (m)',
            'bandwidth': 'Ancho de banda',
            'power': 'Potencia',
            'search_radius': 'Radio de búsqueda (m)',
        },
        'FR': {
            'kde': 'Estimation de la Densité du Noyau (KDE)',
            'kde_desc': 'Crée une surface continue lisse basée sur la densité des points',
            'idw': 'Pondération Inverse de la Distance (IDW)',
            'idw_desc': 'Interpole les valeurs en utilisant une moyenne pondérée par la distance',
            'grid': 'Agrégation Basée sur une Grille',
            'grid_desc': 'Divise la zone en cellules et agrège les valeurs par cellule',
            'cell_size': 'Taille de cellule (m)',
            'bandwidth': 'Largeur de bande',
            'power': 'Puissance',
            'search_radius': 'Rayon de recherche (m)',
        },
        'AR': {
            'kde': 'تقدير كثافة النواة (KDE)',
            'kde_desc': 'ينشئ سطحًا مستمرًا سلسًا بناءً على كثافة النقاط',
            'idw': 'الترجيح العكسي للمسافة (IDW)',
            'idw_desc': 'يقحم القيم باستخدام متوسط مرجح بالمسافة',
            'grid': 'التجميع القائم على الشبكة',
            'grid_desc': 'يقسم المنطقة إلى خلايا ويجمع القيم لكل خلية',
            'cell_size': 'حجم الخلية (م)',
            'bandwidth': 'عرض النطاق',
            'power': 'القوة',
            'search_radius': 'نصف قطر البحث (م)',
        },
        'CA': {
            'kde': 'Estimació de la Densitat del Kernel (KDE)',
            'kde_desc': 'Crea una superfície contínua suau basada en la densitat de punts',
            'idw': 'Ponderació Inversa de la Distància (IDW)',
            'idw_desc': 'Interpola valors usant una mitjana ponderada per distància',
            'grid': 'Agregació Basada en Quadrícula',
            'grid_desc': 'Divideix l\'àrea en cel·les i agrega valors per cel·la',
            'cell_size': 'Mida de cel·la (m)',
            'bandwidth': 'Amplada de banda',
            'power': 'Potència',
            'search_radius': 'Radi de cerca (m)',
        },
    }

    # =========================================================================
    # SCORE LEVELS
    # =========================================================================
    SCORE_LEVELS = {
        'IT': {
            'very_low': 'Molto Basso',
            'low': 'Basso',
            'medium': 'Medio',
            'high': 'Alto',
            'very_high': 'Molto Alto',
            'score': 'Punteggio',
            'weight': 'Peso',
            'contribution': 'Contributo',
            'total': 'Totale',
        },
        'EN': {
            'very_low': 'Very Low',
            'low': 'Low',
            'medium': 'Medium',
            'high': 'High',
            'very_high': 'Very High',
            'score': 'Score',
            'weight': 'Weight',
            'contribution': 'Contribution',
            'total': 'Total',
        },
        'DE': {
            'very_low': 'Sehr Niedrig',
            'low': 'Niedrig',
            'medium': 'Mittel',
            'high': 'Hoch',
            'very_high': 'Sehr Hoch',
            'score': 'Punktzahl',
            'weight': 'Gewicht',
            'contribution': 'Beitrag',
            'total': 'Gesamt',
        },
        'ES': {
            'very_low': 'Muy Bajo',
            'low': 'Bajo',
            'medium': 'Medio',
            'high': 'Alto',
            'very_high': 'Muy Alto',
            'score': 'Puntuación',
            'weight': 'Peso',
            'contribution': 'Contribución',
            'total': 'Total',
        },
        'FR': {
            'very_low': 'Très Bas',
            'low': 'Bas',
            'medium': 'Moyen',
            'high': 'Haut',
            'very_high': 'Très Haut',
            'score': 'Score',
            'weight': 'Poids',
            'contribution': 'Contribution',
            'total': 'Total',
        },
        'AR': {
            'very_low': 'منخفض جداً',
            'low': 'منخفض',
            'medium': 'متوسط',
            'high': 'عالي',
            'very_high': 'عالي جداً',
            'score': 'النتيجة',
            'weight': 'الوزن',
            'contribution': 'المساهمة',
            'total': 'المجموع',
        },
        'CA': {
            'very_low': 'Molt Baix',
            'low': 'Baix',
            'medium': 'Mitjà',
            'high': 'Alt',
            'very_high': 'Molt Alt',
            'score': 'Puntuació',
            'weight': 'Pes',
            'contribution': 'Contribució',
            'total': 'Total',
        },
    }

    # =========================================================================
    # UI LABELS
    # =========================================================================
    UI_LABELS = {
        'IT': {
            'calculate_analysis': 'Calcola Analisi',
            'calculating': 'Calcolo in corso...',
            'generate_heatmap': 'Genera Mappa di Calore',
            'generating': 'Generazione in corso...',
            'export_pdf': 'Esporta Report PDF',
            'export_raster': 'Esporta Raster',
            'preview': 'Anteprima',
            'select_method': 'Seleziona Metodo',
            'analysis_date': 'Data Analisi',
            'analysis_method': 'Metodo Analisi',
            'no_data': 'Nessun dato disponibile',
            'error': 'Errore',
            'success': 'Successo',
            'warning': 'Avviso',
            'save_results': 'Salva Risultati',
            'load_results': 'Carica Risultati',
            'reset': 'Reimposta',
            'close': 'Chiudi',
            'apply': 'Applica',
            'cancel': 'Annulla',
        },
        'EN': {
            'calculate_analysis': 'Calculate Analysis',
            'calculating': 'Calculating...',
            'generate_heatmap': 'Generate Heatmap',
            'generating': 'Generating...',
            'export_pdf': 'Export PDF Report',
            'export_raster': 'Export Raster',
            'preview': 'Preview',
            'select_method': 'Select Method',
            'analysis_date': 'Analysis Date',
            'analysis_method': 'Analysis Method',
            'no_data': 'No data available',
            'error': 'Error',
            'success': 'Success',
            'warning': 'Warning',
            'save_results': 'Save Results',
            'load_results': 'Load Results',
            'reset': 'Reset',
            'close': 'Close',
            'apply': 'Apply',
            'cancel': 'Cancel',
        },
        'DE': {
            'calculate_analysis': 'Analyse Berechnen',
            'calculating': 'Berechnung läuft...',
            'generate_heatmap': 'Heatmap Generieren',
            'generating': 'Generierung läuft...',
            'export_pdf': 'PDF-Bericht Exportieren',
            'export_raster': 'Raster Exportieren',
            'preview': 'Vorschau',
            'select_method': 'Methode Auswählen',
            'analysis_date': 'Analysedatum',
            'analysis_method': 'Analysemethode',
            'no_data': 'Keine Daten verfügbar',
            'error': 'Fehler',
            'success': 'Erfolg',
            'warning': 'Warnung',
            'save_results': 'Ergebnisse Speichern',
            'load_results': 'Ergebnisse Laden',
            'reset': 'Zurücksetzen',
            'close': 'Schließen',
            'apply': 'Anwenden',
            'cancel': 'Abbrechen',
        },
        'ES': {
            'calculate_analysis': 'Calcular Análisis',
            'calculating': 'Calculando...',
            'generate_heatmap': 'Generar Mapa de Calor',
            'generating': 'Generando...',
            'export_pdf': 'Exportar Informe PDF',
            'export_raster': 'Exportar Ráster',
            'preview': 'Vista Previa',
            'select_method': 'Seleccionar Método',
            'analysis_date': 'Fecha de Análisis',
            'analysis_method': 'Método de Análisis',
            'no_data': 'Sin datos disponibles',
            'error': 'Error',
            'success': 'Éxito',
            'warning': 'Advertencia',
            'save_results': 'Guardar Resultados',
            'load_results': 'Cargar Resultados',
            'reset': 'Restablecer',
            'close': 'Cerrar',
            'apply': 'Aplicar',
            'cancel': 'Cancelar',
        },
        'FR': {
            'calculate_analysis': 'Calculer l\'Analyse',
            'calculating': 'Calcul en cours...',
            'generate_heatmap': 'Générer la Carte de Chaleur',
            'generating': 'Génération en cours...',
            'export_pdf': 'Exporter le Rapport PDF',
            'export_raster': 'Exporter le Raster',
            'preview': 'Aperçu',
            'select_method': 'Sélectionner la Méthode',
            'analysis_date': 'Date d\'Analyse',
            'analysis_method': 'Méthode d\'Analyse',
            'no_data': 'Aucune donnée disponible',
            'error': 'Erreur',
            'success': 'Succès',
            'warning': 'Avertissement',
            'save_results': 'Enregistrer les Résultats',
            'load_results': 'Charger les Résultats',
            'reset': 'Réinitialiser',
            'close': 'Fermer',
            'apply': 'Appliquer',
            'cancel': 'Annuler',
        },
        'AR': {
            'calculate_analysis': 'حساب التحليل',
            'calculating': 'جاري الحساب...',
            'generate_heatmap': 'إنشاء خريطة الحرارة',
            'generating': 'جاري الإنشاء...',
            'export_pdf': 'تصدير تقرير PDF',
            'export_raster': 'تصدير الراستر',
            'preview': 'معاينة',
            'select_method': 'اختر الطريقة',
            'analysis_date': 'تاريخ التحليل',
            'analysis_method': 'طريقة التحليل',
            'no_data': 'لا توجد بيانات متاحة',
            'error': 'خطأ',
            'success': 'نجاح',
            'warning': 'تحذير',
            'save_results': 'حفظ النتائج',
            'load_results': 'تحميل النتائج',
            'reset': 'إعادة تعيين',
            'close': 'إغلاق',
            'apply': 'تطبيق',
            'cancel': 'إلغاء',
        },
        'CA': {
            'calculate_analysis': 'Calcular Anàlisi',
            'calculating': 'Calculant...',
            'generate_heatmap': 'Generar Mapa de Calor',
            'generating': 'Generant...',
            'export_pdf': 'Exportar Informe PDF',
            'export_raster': 'Exportar Ràster',
            'preview': 'Vista Prèvia',
            'select_method': 'Seleccionar Mètode',
            'analysis_date': 'Data d\'Anàlisi',
            'analysis_method': 'Mètode d\'Anàlisi',
            'no_data': 'Sense dades disponibles',
            'error': 'Error',
            'success': 'Èxit',
            'warning': 'Advertiment',
            'save_results': 'Desar Resultats',
            'load_results': 'Carregar Resultats',
            'reset': 'Restablir',
            'close': 'Tancar',
            'apply': 'Aplicar',
            'cancel': 'Cancel·lar',
        },
    }

    # =========================================================================
    # METHODOLOGY DESCRIPTIONS
    # =========================================================================
    METHODOLOGY = {
        'IT': {
            'potential_intro': 'Il potenziale archeologico è calcolato utilizzando un sistema di punteggio ponderato (0-100) basato su cinque fattori chiave:',
            'risk_intro': 'Il rischio archeologico è valutato considerando le minacce al patrimonio archeologico utilizzando un sistema di punteggio ponderato (0-100):',
            'kde_methodology': 'La Stima della Densità del Kernel (KDE) utilizza una funzione gaussiana per creare una superficie di densità continua dai punti campione. Questo metodo è ideale per visualizzare la distribuzione spaziale dei rinvenimenti.',
            'idw_methodology': 'La Ponderazione Inversa della Distanza (IDW) interpola i valori assumendo che i punti più vicini abbiano maggiore influenza sul valore predetto. È particolarmente utile per l\'interpolazione di valori noti.',
            'grid_methodology': 'L\'Aggregazione a Griglia divide l\'area di studio in celle regolari e calcola statistiche aggregate (media, somma, conteggio) per ciascuna cella. È il metodo più semplice e intuitivo.',
            'data_quality_note': 'La qualità dei risultati dipende dalla completezza e accuratezza dei dati di input. Si raccomanda di verificare i dati prima dell\'analisi.',
        },
        'EN': {
            'potential_intro': 'Archaeological potential is calculated using a weighted scoring system (0-100) based on five key factors:',
            'risk_intro': 'Archaeological risk is assessed by considering threats to archaeological heritage using a weighted scoring system (0-100):',
            'kde_methodology': 'Kernel Density Estimation (KDE) uses a Gaussian function to create a continuous density surface from sample points. This method is ideal for visualizing spatial distribution of finds.',
            'idw_methodology': 'Inverse Distance Weighting (IDW) interpolates values assuming that closer points have greater influence on the predicted value. It is particularly useful for interpolating known values.',
            'grid_methodology': 'Grid-Based Aggregation divides the study area into regular cells and calculates aggregate statistics (mean, sum, count) for each cell. It is the simplest and most intuitive method.',
            'data_quality_note': 'The quality of results depends on the completeness and accuracy of input data. It is recommended to verify data before analysis.',
        },
        'DE': {
            'potential_intro': 'Das archäologische Potenzial wird anhand eines gewichteten Bewertungssystems (0-100) auf Basis von fünf Schlüsselfaktoren berechnet:',
            'risk_intro': 'Das archäologische Risiko wird durch Berücksichtigung von Bedrohungen des archäologischen Erbes anhand eines gewichteten Bewertungssystems (0-100) bewertet:',
            'kde_methodology': 'Die Kerndichteschätzung (KDE) verwendet eine Gauß-Funktion, um eine kontinuierliche Dichteoberfläche aus Stichprobenpunkten zu erstellen. Diese Methode ist ideal zur Visualisierung der räumlichen Verteilung von Funden.',
            'idw_methodology': 'Die Inverse Distanzgewichtung (IDW) interpoliert Werte unter der Annahme, dass nähere Punkte einen größeren Einfluss auf den vorhergesagten Wert haben. Sie ist besonders nützlich für die Interpolation bekannter Werte.',
            'grid_methodology': 'Die gitterbasierte Aggregation teilt das Untersuchungsgebiet in regelmäßige Zellen und berechnet aggregierte Statistiken (Mittelwert, Summe, Anzahl) für jede Zelle. Es ist die einfachste und intuitivste Methode.',
            'data_quality_note': 'Die Qualität der Ergebnisse hängt von der Vollständigkeit und Genauigkeit der Eingabedaten ab. Es wird empfohlen, die Daten vor der Analyse zu überprüfen.',
        },
        'ES': {
            'potential_intro': 'El potencial arqueológico se calcula utilizando un sistema de puntuación ponderado (0-100) basado en cinco factores clave:',
            'risk_intro': 'El riesgo arqueológico se evalúa considerando las amenazas al patrimonio arqueológico utilizando un sistema de puntuación ponderado (0-100):',
            'kde_methodology': 'La Estimación de Densidad del Kernel (KDE) utiliza una función gaussiana para crear una superficie de densidad continua a partir de puntos de muestra. Este método es ideal para visualizar la distribución espacial de los hallazgos.',
            'idw_methodology': 'La Ponderación Inversa de la Distancia (IDW) interpola valores asumiendo que los puntos más cercanos tienen mayor influencia en el valor predicho. Es particularmente útil para interpolar valores conocidos.',
            'grid_methodology': 'La Agregación Basada en Cuadrícula divide el área de estudio en celdas regulares y calcula estadísticas agregadas (media, suma, conteo) para cada celda. Es el método más simple e intuitivo.',
            'data_quality_note': 'La calidad de los resultados depende de la integridad y precisión de los datos de entrada. Se recomienda verificar los datos antes del análisis.',
        },
        'FR': {
            'potential_intro': 'Le potentiel archéologique est calculé en utilisant un système de notation pondéré (0-100) basé sur cinq facteurs clés:',
            'risk_intro': 'Le risque archéologique est évalué en considérant les menaces pour le patrimoine archéologique en utilisant un système de notation pondéré (0-100):',
            'kde_methodology': 'L\'Estimation de la Densité du Noyau (KDE) utilise une fonction gaussienne pour créer une surface de densité continue à partir de points d\'échantillonnage. Cette méthode est idéale pour visualiser la distribution spatiale des trouvailles.',
            'idw_methodology': 'La Pondération Inverse de la Distance (IDW) interpole les valeurs en supposant que les points plus proches ont une plus grande influence sur la valeur prédite. Elle est particulièrement utile pour interpoler des valeurs connues.',
            'grid_methodology': 'L\'Agrégation Basée sur une Grille divise la zone d\'étude en cellules régulières et calcule des statistiques agrégées (moyenne, somme, compte) pour chaque cellule. C\'est la méthode la plus simple et la plus intuitive.',
            'data_quality_note': 'La qualité des résultats dépend de l\'exhaustivité et de l\'exactitude des données d\'entrée. Il est recommandé de vérifier les données avant l\'analyse.',
        },
        'AR': {
            'potential_intro': 'يتم حساب الإمكانات الأثرية باستخدام نظام تسجيل مرجح (0-100) بناءً على خمسة عوامل رئيسية:',
            'risk_intro': 'يتم تقييم المخاطر الأثرية من خلال النظر في التهديدات للتراث الأثري باستخدام نظام تسجيل مرجح (0-100):',
            'kde_methodology': 'يستخدم تقدير كثافة النواة (KDE) دالة غاوسية لإنشاء سطح كثافة مستمر من نقاط العينة. هذه الطريقة مثالية لتصور التوزيع المكاني للنتائج.',
            'idw_methodology': 'يقوم الترجيح العكسي للمسافة (IDW) بتقحيم القيم على افتراض أن النقاط الأقرب لها تأثير أكبر على القيمة المتوقعة. وهي مفيدة بشكل خاص لتقحيم القيم المعروفة.',
            'grid_methodology': 'يقسم التجميع القائم على الشبكة منطقة الدراسة إلى خلايا منتظمة ويحسب الإحصائيات المجمعة (المتوسط، المجموع، العدد) لكل خلية. إنها الطريقة الأبسط والأكثر بديهية.',
            'data_quality_note': 'تعتمد جودة النتائج على اكتمال ودقة بيانات الإدخال. يوصى بالتحقق من البيانات قبل التحليل.',
        },
        'CA': {
            'potential_intro': 'El potencial arqueològic es calcula utilitzant un sistema de puntuació ponderat (0-100) basat en cinc factors clau:',
            'risk_intro': 'El risc arqueològic s\'avalua considerant les amenaces al patrimoni arqueològic utilitzant un sistema de puntuació ponderat (0-100):',
            'kde_methodology': 'L\'Estimació de la Densitat del Kernel (KDE) utilitza una funció gaussiana per crear una superfície de densitat contínua a partir de punts de mostra. Aquest mètode és ideal per visualitzar la distribució espacial de les troballes.',
            'idw_methodology': 'La Ponderació Inversa de la Distància (IDW) interpola valors assumint que els punts més propers tenen major influència en el valor predit. És particularment útil per interpolar valors coneguts.',
            'grid_methodology': 'L\'Agregació Basada en Quadrícula divideix l\'àrea d\'estudi en cel·les regulars i calcula estadístiques agregades (mitjana, suma, recompte) per a cada cel·la. És el mètode més simple i intuïtiu.',
            'data_quality_note': 'La qualitat dels resultats depèn de la completesa i precisió de les dades d\'entrada. Es recomana verificar les dades abans de l\'anàlisi.',
        },
    }

    # =========================================================================
    # PDF REPORT LABELS
    # =========================================================================
    PDF_LABELS = {
        'IT': {
            'report_title': 'Report di Analisi Archeologica',
            'ut_identification': 'Identificazione UT',
            'project': 'Progetto',
            'ut_number': 'N. UT',
            'definition': 'Definizione',
            'location': 'Localizzazione',
            'generated_on': 'Generato il',
            'page': 'Pagina',
            'of': 'di',
            'interpretation': 'Interpretazione',
            'notes': 'Note',
            'legend': 'Legenda',
            'scale': 'Scala',
        },
        'EN': {
            'report_title': 'Archaeological Analysis Report',
            'ut_identification': 'UT Identification',
            'project': 'Project',
            'ut_number': 'UT No.',
            'definition': 'Definition',
            'location': 'Location',
            'generated_on': 'Generated on',
            'page': 'Page',
            'of': 'of',
            'interpretation': 'Interpretation',
            'notes': 'Notes',
            'legend': 'Legend',
            'scale': 'Scale',
        },
        'DE': {
            'report_title': 'Archäologischer Analysebericht',
            'ut_identification': 'UT-Identifikation',
            'project': 'Projekt',
            'ut_number': 'UT-Nr.',
            'definition': 'Definition',
            'location': 'Standort',
            'generated_on': 'Erstellt am',
            'page': 'Seite',
            'of': 'von',
            'interpretation': 'Interpretation',
            'notes': 'Anmerkungen',
            'legend': 'Legende',
            'scale': 'Maßstab',
        },
        'ES': {
            'report_title': 'Informe de Análisis Arqueológico',
            'ut_identification': 'Identificación UT',
            'project': 'Proyecto',
            'ut_number': 'N. UT',
            'definition': 'Definición',
            'location': 'Ubicación',
            'generated_on': 'Generado el',
            'page': 'Página',
            'of': 'de',
            'interpretation': 'Interpretación',
            'notes': 'Notas',
            'legend': 'Leyenda',
            'scale': 'Escala',
        },
        'FR': {
            'report_title': 'Rapport d\'Analyse Archéologique',
            'ut_identification': 'Identification UT',
            'project': 'Projet',
            'ut_number': 'N. UT',
            'definition': 'Définition',
            'location': 'Localisation',
            'generated_on': 'Généré le',
            'page': 'Page',
            'of': 'de',
            'interpretation': 'Interprétation',
            'notes': 'Notes',
            'legend': 'Légende',
            'scale': 'Échelle',
        },
        'AR': {
            'report_title': 'تقرير التحليل الأثري',
            'ut_identification': 'تعريف الوحدة الطوبوغرافية',
            'project': 'المشروع',
            'ut_number': 'رقم الوحدة',
            'definition': 'التعريف',
            'location': 'الموقع',
            'generated_on': 'تم إنشاؤه في',
            'page': 'صفحة',
            'of': 'من',
            'interpretation': 'التفسير',
            'notes': 'ملاحظات',
            'legend': 'وسيلة الإيضاح',
            'scale': 'المقياس',
        },
        'CA': {
            'report_title': 'Informe d\'Anàlisi Arqueològica',
            'ut_identification': 'Identificació UT',
            'project': 'Projecte',
            'ut_number': 'N. UT',
            'definition': 'Definició',
            'location': 'Localització',
            'generated_on': 'Generat el',
            'page': 'Pàgina',
            'of': 'de',
            'interpretation': 'Interpretació',
            'notes': 'Notes',
            'legend': 'Llegenda',
            'scale': 'Escala',
        },
    }

    @classmethod
    def get_labels(cls, lang='IT'):
        """
        Get all labels for a specific language.

        Args:
            lang: Language code (IT, EN, DE, ES, FR, AR, CA)

        Returns:
            Dictionary containing all label categories for the language
        """
        lang = lang.upper() if lang else 'IT'
        if lang not in ['IT', 'EN', 'DE', 'ES', 'FR', 'AR', 'CA']:
            lang = 'EN'  # Default to English for unknown languages

        return {
            'headers': cls.HEADERS.get(lang, cls.HEADERS['EN']),
            'potential_factors': cls.POTENTIAL_FACTORS.get(lang, cls.POTENTIAL_FACTORS['EN']),
            'risk_factors': cls.RISK_FACTORS.get(lang, cls.RISK_FACTORS['EN']),
            'heatmap_methods': cls.HEATMAP_METHODS.get(lang, cls.HEATMAP_METHODS['EN']),
            'score_levels': cls.SCORE_LEVELS.get(lang, cls.SCORE_LEVELS['EN']),
            'ui': cls.UI_LABELS.get(lang, cls.UI_LABELS['EN']),
            'methodology': cls.METHODOLOGY.get(lang, cls.METHODOLOGY['EN']),
            'pdf': cls.PDF_LABELS.get(lang, cls.PDF_LABELS['EN']),
        }

    @classmethod
    def get_score_level(cls, score, lang='IT'):
        """
        Get the score level label based on the numeric score.

        Args:
            score: Numeric score (0-100)
            lang: Language code

        Returns:
            Localized score level string
        """
        lang = lang.upper() if lang else 'IT'
        levels = cls.SCORE_LEVELS.get(lang, cls.SCORE_LEVELS['EN'])

        if score is None:
            return levels.get('very_low', 'Very Low')
        elif score < 20:
            return levels['very_low']
        elif score < 40:
            return levels['low']
        elif score < 60:
            return levels['medium']
        elif score < 80:
            return levels['high']
        else:
            return levels['very_high']
