# -*- coding: utf-8 -*-
"""
GeoArchaeo - Internationalization (i18n) module
Supports Italian (it) and English (en)
"""

# Current language setting
_current_language = 'it'

# Translation dictionary
TRANSLATIONS = {
    # Tab names
    'tab_data': {
        'it': 'Dati',
        'en': 'Data'
    },
    'tab_variogram': {
        'it': 'Variogramma',
        'en': 'Variogram'
    },
    'tab_kriging': {
        'it': 'Kriging',
        'en': 'Kriging'
    },
    'tab_ml': {
        'it': 'ML',
        'en': 'ML'
    },
    'tab_sampling': {
        'it': 'Campionamento',
        'en': 'Sampling'
    },
    'tab_report': {
        'it': 'Report',
        'en': 'Report'
    },

    # Data tab
    'data_title': {
        'it': '<b>Analisi Esplorativa Dati</b>',
        'en': '<b>Exploratory Data Analysis</b>'
    },
    'data_desc': {
        'it': 'Carica un layer di punti e seleziona il campo numerico da analizzare.<br>'
              'Otterrai statistiche descrittive per capire la distribuzione dei tuoi dati.',
        'en': 'Load a point layer and select the numeric field to analyze.<br>'
              'You will get descriptive statistics to understand your data distribution.'
    },
    'data_selection': {
        'it': 'Selezione Dati',
        'en': 'Data Selection'
    },
    'point_layer': {
        'it': 'Layer punti:',
        'en': 'Point layer:'
    },
    'value_field': {
        'it': 'Campo valore (numerico):',
        'en': 'Value field (numeric):'
    },
    'statistics': {
        'it': 'Statistiche:',
        'en': 'Statistics:'
    },
    'calc_statistics': {
        'it': 'Calcola Statistiche',
        'en': 'Calculate Statistics'
    },

    # Variogram tab
    'variogram_title': {
        'it': '<b>Analisi Variogramma</b>',
        'en': '<b>Variogram Analysis</b>'
    },
    'variogram_desc': {
        'it': 'Il variogramma misura come varia la correlazione spaziale al variare della distanza.<br>'
              'È essenziale per capire la struttura spaziale dei tuoi dati prima del kriging.',
        'en': 'The variogram measures how spatial correlation varies with distance.<br>'
              'It is essential to understand the spatial structure of your data before kriging.'
    },
    'variogram_params': {
        'it': 'Parametri Variogramma',
        'en': 'Variogram Parameters'
    },
    'max_distance': {
        'it': 'Distanza massima (m):',
        'en': 'Maximum distance (m):'
    },
    'theoretical_model': {
        'it': 'Modello teorico:',
        'en': 'Theoretical model:'
    },
    'advanced_params': {
        'it': 'Parametri Avanzati (opzionale)',
        'en': 'Advanced Parameters (optional)'
    },
    'nugget': {
        'it': 'Nugget (effetto pepita):',
        'en': 'Nugget (nugget effect):'
    },
    'calc_variogram': {
        'it': 'Calcola Variogramma',
        'en': 'Calculate Variogram'
    },

    # Kriging tab
    'kriging_title': {
        'it': '<b>Interpolazione Kriging</b>',
        'en': '<b>Kriging Interpolation</b>'
    },
    'kriging_desc': {
        'it': 'Il Kriging è un metodo di interpolazione geostatistica che produce stime ottimali.<br>'
              'Fornisce anche una mappa dell\'incertezza per valutare l\'affidabilità delle stime.',
        'en': 'Kriging is a geostatistical interpolation method that produces optimal estimates.<br>'
              'It also provides an uncertainty map to evaluate the reliability of estimates.'
    },
    'kriging_params': {
        'it': 'Parametri Kriging',
        'en': 'Kriging Parameters'
    },
    'kriging_type': {
        'it': 'Tipo Kriging:',
        'en': 'Kriging type:'
    },
    'grid_resolution': {
        'it': 'Risoluzione griglia (m):',
        'en': 'Grid resolution (m):'
    },
    'use_variogram': {
        'it': 'Usa variogramma calcolato',
        'en': 'Use calculated variogram'
    },
    'run_kriging': {
        'it': 'Esegui Kriging',
        'en': 'Run Kriging'
    },

    # ML tab
    'ml_title': {
        'it': '<b>Pattern Recognition (ML)</b>',
        'en': '<b>Pattern Recognition (ML)</b>'
    },
    'ml_desc': {
        'it': 'Usa algoritmi di Machine Learning per identificare pattern nascosti nei dati.<br>'
              'Utile per clustering, rilevamento anomalie e classificazione automatica.',
        'en': 'Use Machine Learning algorithms to identify hidden patterns in data.<br>'
              'Useful for clustering, anomaly detection, and automatic classification.'
    },
    'ml_method': {
        'it': 'Metodo:',
        'en': 'Method:'
    },
    'run_ml': {
        'it': 'Avvia Pattern Recognition',
        'en': 'Run Pattern Recognition'
    },

    # Sampling tab
    'sampling_title': {
        'it': '<b>Design Campionamento Ottimale</b>',
        'en': '<b>Optimal Sampling Design</b>'
    },
    'sampling_desc': {
        'it': 'Pianifica dove effettuare nuovi campionamenti per massimizzare l\'informazione.<br>'
              'Basato su criteri geostatistici per ottimizzare la copertura spaziale.',
        'en': 'Plan where to take new samples to maximize information.<br>'
              'Based on geostatistical criteria to optimize spatial coverage.'
    },
    'sampling_params': {
        'it': 'Parametri Campionamento',
        'en': 'Sampling Parameters'
    },
    'existing_points': {
        'it': 'Punti esistenti:',
        'en': 'Existing points:'
    },
    'new_points': {
        'it': 'Nuovi punti da aggiungere:',
        'en': 'New points to add:'
    },
    'sampling_method': {
        'it': 'Metodo:',
        'en': 'Method:'
    },
    'calc_optimal': {
        'it': 'Calcola Punti Ottimali',
        'en': 'Calculate Optimal Points'
    },

    # Report tab
    'report_title': {
        'it': '<b>Generazione Report</b>',
        'en': '<b>Report Generation</b>'
    },
    'report_desc': {
        'it': 'Genera un report completo delle analisi effettuate in formato HTML.<br>'
              'Include grafici, statistiche e interpretazioni dei risultati.',
        'en': 'Generate a complete report of the analyses in HTML format.<br>'
              'Includes graphs, statistics, and result interpretations.'
    },
    'report_sections': {
        'it': 'Sezioni da includere:',
        'en': 'Sections to include:'
    },
    'generate_report': {
        'it': 'Genera Report HTML',
        'en': 'Generate HTML Report'
    },

    # Example data
    'load_examples': {
        'it': 'Carica Dati di Esempio',
        'en': 'Load Example Data'
    },
    'examples_title': {
        'it': 'Dati di Esempio GeoArchaeo',
        'en': 'GeoArchaeo Example Data'
    },
    'examples_desc': {
        'it': 'Seleziona i dataset di esempio da caricare:',
        'en': 'Select example datasets to load:'
    },
    'villa_ceramica': {
        'it': 'Villa Ceramica (500 punti - distribuzione ceramica)',
        'en': 'Villa Ceramica (500 points - ceramic distribution)'
    },
    'geofisica': {
        'it': 'Survey Geofisico (4800 punti - GPR + Magnetometria)',
        'en': 'Geophysical Survey (4800 points - GPR + Magnetometry)'
    },
    'soil_samples': {
        'it': 'Campioni Suolo (80 punti - analisi composizionali)',
        'en': 'Soil Samples (80 points - compositional analysis)'
    },
    'necropoli': {
        'it': 'Necropoli (120 tombe - clustering)',
        'en': 'Necropolis (120 tombs - clustering)'
    },

    # Tutorial
    'show_tutorial': {
        'it': 'Mostra Tutorial',
        'en': 'Show Tutorial'
    },

    # Messages
    'warning': {
        'it': 'Attenzione',
        'en': 'Warning'
    },
    'error': {
        'it': 'Errore',
        'en': 'Error'
    },
    'completed': {
        'it': 'Completato',
        'en': 'Completed'
    },
    'select_layer_field': {
        'it': 'Seleziona layer e campo',
        'en': 'Select layer and field'
    },
    'min_points': {
        'it': 'Servono almeno 5 punti validi',
        'en': 'At least 5 valid points required'
    },
    'large_grid_warning': {
        'it': 'La griglia avrà {nx}x{ny} = {total} celle.\n'
              'Con {points} punti, il calcolo potrebbe richiedere molto tempo.\n\n'
              'Suggerimento: aumenta la risoluzione (es. 2.0m invece di 1.0m).\n\n'
              'Vuoi continuare comunque?',
        'en': 'The grid will have {nx}x{ny} = {total} cells.\n'
              'With {points} points, the calculation may take a long time.\n\n'
              'Suggestion: increase resolution (e.g., 2.0m instead of 1.0m).\n\n'
              'Do you want to continue anyway?'
    },
    'large_grid_title': {
        'it': 'Griglia grande',
        'en': 'Large grid'
    },
    'kriging_complete': {
        'it': 'Kriging completato con successo!\n\n',
        'en': 'Kriging completed successfully!\n\n'
    },
    'cv_metrics': {
        'it': 'Metriche Cross-Validation:\n',
        'en': 'Cross-Validation Metrics:\n'
    },
    'graph_opened': {
        'it': 'Il grafico è stato aperto nel browser.\nUn raster è stato aggiunto alla mappa.',
        'en': 'The graph has been opened in the browser.\nA raster has been added to the map.'
    },

    # Language
    'language': {
        'it': 'Lingua',
        'en': 'Language'
    },
    'italian': {
        'it': 'Italiano',
        'en': 'Italian'
    },
    'english': {
        'it': 'Inglese',
        'en': 'English'
    },

    # Layer names
    'ml_clusters_layer': {
        'it': 'Cluster_ML',
        'en': 'ML_Clusters'
    },
    'kriging_result_layer': {
        'it': 'Risultato_Kriging',
        'en': 'Kriging_Result'
    },
    'sampling_points_layer': {
        'it': 'Punti_Campionamento',
        'en': 'Sampling_Points'
    },

    # Cluster labels
    'cluster_label': {
        'it': 'Gruppo {letter}',
        'en': 'Group {letter}'
    },
    'cluster_with_count': {
        'it': 'Gruppo {letter} (n={count})',
        'en': 'Group {letter} (n={count})'
    },
    'anomaly_normal': {
        'it': 'Normale',
        'en': 'Normal'
    },
    'anomaly_outlier': {
        'it': 'Anomalia',
        'en': 'Anomaly'
    },
    'noise_points': {
        'it': 'Rumore/Isolati',
        'en': 'Noise/Isolated'
    },

    # ML attribute fields
    'cluster_name': {
        'it': 'nome_cluster',
        'en': 'cluster_name'
    },
    'cluster_size': {
        'it': 'dimensione',
        'en': 'size'
    },
    'cluster_description': {
        'it': 'descrizione',
        'en': 'description'
    },

    # Kriging legend
    'kriging_legend_title': {
        'it': 'Valore Interpolato',
        'en': 'Interpolated Value'
    },
    'kriging_low': {
        'it': 'Basso',
        'en': 'Low'
    },
    'kriging_high': {
        'it': 'Alto',
        'en': 'High'
    },

    # Error messages
    'error': {
        'it': 'Errore',
        'en': 'Error'
    },
    'error_visualization': {
        'it': 'Errore nella visualizzazione:\n{msg}',
        'en': 'Visualization error:\n{msg}'
    },
    'error_analysis': {
        'it': 'Errore durante l\'analisi:\n{msg}',
        'en': 'Analysis error:\n{msg}'
    },
    'raster_created': {
        'it': 'Raster kriging creato con successo',
        'en': 'Kriging raster created successfully'
    },
    'layer_created': {
        'it': 'Layer creato con successo',
        'en': 'Layer created successfully'
    },

    # ML method descriptions
    'kmeans_desc': {
        'it': 'Clustering K-Means: raggruppa per similarità',
        'en': 'K-Means Clustering: groups by similarity'
    },
    'dbscan_desc': {
        'it': 'DBSCAN: raggruppa per densità spaziale',
        'en': 'DBSCAN: groups by spatial density'
    },
    'isolation_desc': {
        'it': 'Isolation Forest: rileva anomalie',
        'en': 'Isolation Forest: detects anomalies'
    },
    'rf_desc': {
        'it': 'Random Forest: classificazione supervisionata',
        'en': 'Random Forest: supervised classification'
    },

    # Cluster characteristics
    'high_values': {
        'it': 'valori alti',
        'en': 'high values'
    },
    'medium_values': {
        'it': 'valori medi',
        'en': 'medium values'
    },
    'low_values': {
        'it': 'valori bassi',
        'en': 'low values'
    },

    # Additional variogram labels
    'sill': {
        'it': 'Sill (varianza totale):',
        'en': 'Sill (total variance):'
    },
    'range': {
        'it': 'Range (distanza correlazione):',
        'en': 'Range (correlation distance):'
    },
    'anisotropy_check': {
        'it': 'Verifica anisotropia (direzionale)',
        'en': 'Check anisotropy (directional)'
    },

    # Kriging labels
    'ordinary_kriging': {
        'it': 'Kriging Ordinario',
        'en': 'Ordinary Kriging'
    },
    'universal_kriging': {
        'it': 'Kriging Universale',
        'en': 'Universal Kriging'
    },

    # ML labels
    'ml_algorithm': {
        'it': 'Algoritmo:',
        'en': 'Algorithm:'
    },
    'ml_layers_select': {
        'it': 'Layer da analizzare:',
        'en': 'Layers to analyze:'
    },

    # Sampling labels
    'n_new_points': {
        'it': 'Numero nuovi punti:',
        'en': 'Number of new points:'
    },
    'sampling_strategy': {
        'it': 'Strategia:',
        'en': 'Strategy:'
    },
    'variance_reduction': {
        'it': 'Riduzione Varianza',
        'en': 'Variance Reduction'
    },
    'max_entropy': {
        'it': 'Massima Entropia',
        'en': 'Maximum Entropy'
    },
    'regular_grid': {
        'it': 'Griglia Regolare',
        'en': 'Regular Grid'
    },

    # Report labels
    'include_stats': {
        'it': 'Includi statistiche descrittive',
        'en': 'Include descriptive statistics'
    },
    'include_variogram': {
        'it': 'Includi analisi variogramma',
        'en': 'Include variogram analysis'
    },
    'include_kriging': {
        'it': 'Includi risultati kriging',
        'en': 'Include kriging results'
    },
    'include_ml': {
        'it': 'Includi risultati ML',
        'en': 'Include ML results'
    },

    # Messages
    'select_layer_first': {
        'it': 'Seleziona un layer prima',
        'en': 'Select a layer first'
    },
    'analysis_running': {
        'it': 'Analisi in corso...',
        'en': 'Analysis running...'
    },
    'analysis_complete': {
        'it': 'Analisi completata',
        'en': 'Analysis complete'
    },

    # Additional messages
    'no_values_found': {
        'it': 'Nessun valore trovato',
        'en': 'No values found'
    },
    'select_at_least_one_layer': {
        'it': 'Seleziona almeno un layer',
        'en': 'Select at least one layer'
    },
    'no_valid_data': {
        'it': 'Nessun dato valido trovato',
        'en': 'No valid data found'
    },
    'select_existing_points': {
        'it': 'Seleziona layer punti esistenti',
        'en': 'Select existing points layer'
    },
    'no_points_in_layer': {
        'it': 'Nessun punto trovato nel layer',
        'en': 'No points found in layer'
    },
    'report_saved': {
        'it': 'Report salvato in {path}',
        'en': 'Report saved to {path}'
    },
    'variogram_complete': {
        'it': 'Variogramma calcolato!',
        'en': 'Variogram calculated!'
    },
}


def get_language():
    """Get current language"""
    return _current_language


def set_language(lang):
    """Set current language (it or en)"""
    global _current_language
    if lang in ['it', 'en']:
        _current_language = lang


def tr(key):
    """Translate a key to the current language"""
    if key in TRANSLATIONS:
        return TRANSLATIONS[key].get(_current_language, TRANSLATIONS[key].get('en', key))
    return key


def tr_format(key, **kwargs):
    """Translate a key and format with kwargs"""
    text = tr(key)
    try:
        return text.format(**kwargs)
    except KeyError:
        return text
