# -*- coding: utf-8 -*-
"""
GeoArchaeo - Internationalization (i18n) module
Supports Italian (it) and English (en).

La lingua viene letta/salvata nelle impostazioni di QGIS
(chiave "GeoArchaeo/language"); in mancanza si usa la locale di QGIS.
"""

SUPPORTED_LANGUAGES = ('it', 'en')
_SETTINGS_KEY = 'GeoArchaeo/language'


def _detect_language():
    try:
        from qgis.PyQt.QtCore import QSettings
        settings = QSettings()
        saved = settings.value(_SETTINGS_KEY, '', type=str)
        if saved in SUPPORTED_LANGUAGES:
            return saved
        locale = settings.value('locale/userLocale', '', type=str) or ''
        return 'it' if locale.lower().startswith('it') else 'en'
    except (ImportError, TypeError):
        return 'en'


# Current language setting
_current_language = _detect_language()

# Translation dictionary
TRANSLATIONS = {
    # ------------------------------------------------------------ tabs
    'tab_data': {'it': 'Dati', 'en': 'Data'},
    'tab_variogram': {'it': 'Variogramma', 'en': 'Variogram'},
    'tab_kriging': {'it': 'Kriging', 'en': 'Kriging'},
    'tab_ml': {'it': 'Pattern (ML)', 'en': 'Patterns (ML)'},
    'tab_sampling': {'it': 'Campionamento', 'en': 'Sampling'},
    'tab_report': {'it': 'Report', 'en': 'Report'},

    # ------------------------------------------------------------ header
    'load_examples': {'it': 'Carica dati di esempio', 'en': 'Load example data'},
    'show_tutorial': {'it': 'Tutorial', 'en': 'Tutorial'},
    'language': {'it': 'Lingua', 'en': 'Language'},
    'input_data': {'it': 'Dati di input (usati da tutte le schede)', 'en': 'Input data (used by all tabs)'},
    'point_layer': {'it': 'Layer punti:', 'en': 'Point layer:'},
    'value_field': {'it': 'Campo valore (numerico):', 'en': 'Value field (numeric):'},
    'no_layer_selected': {'it': 'Nessun layer di punti nel progetto: caricane uno o usa i dati di esempio.',
                          'en': 'No point layer in the project: load one or use the example data.'},
    'no_numeric_field': {'it': 'Il layer non ha campi numerici. Converti il campo da analizzare in numero '
                               '(es. con il Calcolatore di campi).',
                         'en': 'The layer has no numeric fields. Convert the field to analyse to a number '
                               '(e.g. with the Field Calculator).'},
    'layer_summary': {'it': '{n} punti validi su {total} · CRS {crs} · estensione {w} × {h} {unit}',
                      'en': '{n} valid points of {total} · CRS {crs} · extent {w} × {h} {unit}'},
    'geographic_crs_warning': {'it': 'Attenzione: CRS geografico (gradi). Per distanze in metri riproietta il layer '
                                     'in un CRS proiettato (es. UTM).',
                               'en': 'Warning: geographic CRS (degrees). For distances in metres reproject the layer '
                                     'to a projected CRS (e.g. UTM).'},
    'unit_m': {'it': 'm', 'en': 'm'},
    'unit_deg': {'it': 'gradi', 'en': 'degrees'},
    'unit_generic': {'it': 'unità', 'en': 'units'},

    # ------------------------------------------------------------ data tab
    'data_title': {'it': '<b>1. Analisi esplorativa</b>', 'en': '<b>1. Exploratory analysis</b>'},
    'data_desc': {'it': 'Scegli layer e campo in alto, poi calcola le statistiche per capire la distribuzione '
                        'dei valori prima di interpolare.',
                  'en': 'Choose the layer and field above, then compute the statistics to understand the '
                        'value distribution before interpolating.'},
    'calc_statistics': {'it': 'Calcola statistiche', 'en': 'Calculate statistics'},
    'statistics': {'it': 'Statistiche', 'en': 'Statistics'},
    'stat_n': {'it': 'Numero valori', 'en': 'Number of values'},
    'stat_min': {'it': 'Minimo', 'en': 'Minimum'},
    'stat_max': {'it': 'Massimo', 'en': 'Maximum'},
    'stat_mean': {'it': 'Media', 'en': 'Mean'},
    'stat_median': {'it': 'Mediana', 'en': 'Median'},
    'stat_std': {'it': 'Dev. standard', 'en': 'Std. deviation'},
    'stat_cv': {'it': 'Coeff. di variazione', 'en': 'Coeff. of variation'},
    'stat_q1': {'it': 'Primo quartile (Q1)', 'en': 'First quartile (Q1)'},
    'stat_q3': {'it': 'Terzo quartile (Q3)', 'en': 'Third quartile (Q3)'},
    'stat_skew': {'it': 'Asimmetria (skewness)', 'en': 'Skewness'},
    'stat_kurt': {'it': 'Curtosi', 'en': 'Kurtosis'},
    'stat_nulls': {'it': 'Valori mancanti', 'en': 'Missing values'},
    'interp_skew_right': {'it': 'Distribuzione asimmetrica a destra (pochi valori molto alti): '
                                'valuta una trasformazione logaritmica prima del kriging.',
                          'en': 'Right-skewed distribution (few very high values): consider a log '
                                'transform before kriging.'},
    'interp_skew_left': {'it': 'Distribuzione asimmetrica a sinistra (pochi valori molto bassi).',
                         'en': 'Left-skewed distribution (few very low values).'},
    'interp_symmetric': {'it': 'Distribuzione circa simmetrica: adatta al kriging.',
                         'en': 'Roughly symmetric distribution: suitable for kriging.'},
    'interp_outliers': {'it': '{n} possibili valori anomali oltre 3 deviazioni standard.',
                        'en': '{n} possible outliers beyond 3 standard deviations.'},
    'next_variogram': {'it': 'Prossimo passo: Variogramma →', 'en': 'Next step: Variogram →'},

    # ------------------------------------------------------------ variogram tab
    'variogram_title': {'it': '<b>2. Variogramma</b>', 'en': '<b>2. Variogram</b>'},
    'variogram_desc': {'it': 'Misura come la differenza tra i valori cresce con la distanza. '
                             'Serve a capire la struttura spaziale dei dati e guida il kriging.',
                       'en': 'Measures how the difference between values grows with distance. '
                             'It describes the spatial structure of the data and drives the kriging.'},
    'variogram_params': {'it': 'Parametri', 'en': 'Parameters'},
    'max_distance': {'it': 'Distanza massima:', 'en': 'Maximum distance:'},
    'auto': {'it': 'Auto', 'en': 'Auto'},
    'max_distance_tip': {'it': 'Distanza massima tra coppie di punti considerate. Consigliato circa 1/3 '
                               'della diagonale dell\'area ("Auto").',
                         'en': 'Maximum distance between point pairs. About 1/3 of the area diagonal is '
                               'recommended ("Auto").'},
    'theoretical_model': {'it': 'Modello teorico:', 'en': 'Theoretical model:'},
    'model_spherical': {'it': 'Sferico (consigliato)', 'en': 'Spherical (recommended)'},
    'model_exponential': {'it': 'Esponenziale', 'en': 'Exponential'},
    'model_gaussian': {'it': 'Gaussiano', 'en': 'Gaussian'},
    'model_matern': {'it': 'Matérn', 'en': 'Matérn'},
    'manual_params': {'it': 'Parametri manuali (opzionale)', 'en': 'Manual parameters (optional)'},
    'manual_params_tip': {'it': 'Se attivo, i valori diversi da zero sostituiscono quelli stimati automaticamente.',
                          'en': 'When enabled, non-zero values override the automatically fitted ones.'},
    'nugget': {'it': 'Nugget (effetto pepita):', 'en': 'Nugget:'},
    'sill': {'it': 'Sill (varianza totale):', 'en': 'Sill (total variance):'},
    'range': {'it': 'Range (distanza di correlazione):', 'en': 'Range (correlation distance):'},
    'anisotropy_check': {'it': 'Verifica anisotropia (variogrammi direzionali)',
                         'en': 'Check anisotropy (directional variograms)'},
    'calc_variogram': {'it': 'Calcola variogramma', 'en': 'Calculate variogram'},
    'variogram_results': {'it': '<b>Modello {model}</b> · Nugget {nugget} · Sill {sill} · Range {range} {unit} '
                                '· RMSE fit {rmse}',
                          'en': '<b>{model} model</b> · Nugget {nugget} · Sill {sill} · Range {range} {unit} '
                                '· fit RMSE {rmse}'},
    'variogram_pairs': {'it': '{pairs} coppie di punti in {lags} classi di distanza',
                        'en': '{pairs} point pairs in {lags} distance classes'},
    'variogram_subsampled': {'it': ' (sottocampione di {used} punti su {n})',
                             'en': ' (subsample of {used} points out of {n})'},
    'interp_range': {'it': 'I valori sono spazialmente correlati fino a circa {range} {unit}: oltre questa '
                           'distanza i punti non si influenzano.',
                     'en': 'Values are spatially correlated up to about {range} {unit}: beyond this '
                           'distance points do not influence each other.'},
    'interp_nugget_low': {'it': 'Nugget {pct}% del sill: forte continuità spaziale a piccola scala.',
                          'en': 'Nugget {pct}% of sill: strong small-scale spatial continuity.'},
    'interp_nugget_mid': {'it': 'Nugget {pct}% del sill: continuità spaziale moderata.',
                          'en': 'Nugget {pct}% of sill: moderate spatial continuity.'},
    'interp_nugget_high': {'it': 'Nugget {pct}% del sill: molta variabilità a piccola scala o errore di misura; '
                                 'il kriging sarà poco informativo.',
                           'en': 'Nugget {pct}% of sill: high small-scale variability or measurement error; '
                                 'kriging will be weakly informative.'},
    'anisotropy_result': {'it': 'Anisotropia: rapporto {ratio} tra i range, direzione maggiore {dir}° (da Est, antiorario).',
                          'en': 'Anisotropy: range ratio {ratio}, major direction {dir}° (from East, counter-clockwise).'},
    'anisotropy_none': {'it': 'Nessuna anisotropia rilevante (rapporto tra i range {ratio}).',
                        'en': 'No relevant anisotropy (range ratio {ratio}).'},
    'anisotropy_insufficient': {'it': 'Coppie insufficienti per i variogrammi direzionali.',
                                'en': 'Not enough pairs for directional variograms.'},
    'next_kriging': {'it': 'Prossimo passo: Kriging →', 'en': 'Next step: Kriging →'},

    # ------------------------------------------------------------ kriging tab
    'kriging_title': {'it': '<b>3. Kriging ordinario</b>', 'en': '<b>3. Ordinary kriging</b>'},
    'kriging_desc': {'it': 'Interpola i valori su una griglia regolare usando il variogramma e produce '
                           'anche una mappa dell\'incertezza. I raster vengono aggiunti al progetto.',
                     'en': 'Interpolates the values on a regular grid using the variogram and also '
                           'produces an uncertainty map. The rasters are added to the project.'},
    'kriging_params': {'it': 'Parametri', 'en': 'Parameters'},
    'grid_resolution': {'it': 'Risoluzione cella:', 'en': 'Cell size:'},
    'grid_info': {'it': 'Griglia: {nx} × {ny} = {cells} celle', 'en': 'Grid: {nx} × {ny} = {cells} cells'},
    'grid_capped': {'it': ' · risoluzione minima {ps} (max {side} celle per lato)',
                    'en': ' · minimum cell size {ps} (max {side} cells per side)'},
    'grid_large_question': {'it': 'La griglia avrà {cells} celle: il calcolo può richiedere alcuni minuti.\n'
                                  'Suggerimento: aumenta la dimensione della cella.\n\nContinuare?',
                            'en': 'The grid will have {cells} cells: the computation may take a few minutes.\n'
                                  'Tip: increase the cell size.\n\nContinue?'},
    'use_variogram': {'it': 'Usa il variogramma calcolato', 'en': 'Use the calculated variogram'},
    'create_uncertainty': {'it': 'Crea anche il raster dell\'incertezza (dev. standard)',
                           'en': 'Also create the uncertainty raster (std. deviation)'},
    'variogram_status_ok': {'it': 'Variogramma disponibile: {model}, range {range} {unit} ✓',
                            'en': 'Variogram available: {model}, range {range} {unit} ✓'},
    'variogram_status_none': {'it': 'Nessun variogramma calcolato: verrà stimato automaticamente (modello sferico).',
                              'en': 'No variogram calculated: it will be estimated automatically (spherical model).'},
    'variogram_status_stale': {'it': 'Il variogramma è stato calcolato su un altro layer/campo: verrà ricalcolato.',
                               'en': 'The variogram was calculated on another layer/field: it will be recalculated.'},
    'goto_variogram': {'it': '← Vai al Variogramma', 'en': '← Go to Variogram'},
    'run_kriging': {'it': 'Esegui kriging', 'en': 'Run kriging'},
    'cancel': {'it': 'Annulla', 'en': 'Cancel'},
    'kriging_results': {'it': '<b>Kriging completato</b> · {n} punti · griglia {nx} × {ny} ({ps} {unit}/cella) '
                              '· {model}, range {range} {unit}',
                        'en': '<b>Kriging completed</b> · {n} points · grid {nx} × {ny} ({ps} {unit}/cell) '
                              '· {model}, range {range} {unit}'},
    'cv_title': {'it': 'Cross-validation leave-one-out ({n} punti)', 'en': 'Leave-one-out cross-validation ({n} points)'},
    'cv_rmse': {'it': 'RMSE (errore quadratico medio)', 'en': 'RMSE (root mean squared error)'},
    'cv_mae': {'it': 'MAE (errore assoluto medio)', 'en': 'MAE (mean absolute error)'},
    'cv_me': {'it': 'ME (errore medio, bias)', 'en': 'ME (mean error, bias)'},
    'cv_r2': {'it': 'R² (quota di varianza spiegata)', 'en': 'R² (explained variance)'},
    'cv_msdr': {'it': 'MSDR (errore standardizzato, ideale ≈ 1)', 'en': 'MSDR (standardized error, ideal ≈ 1)'},
    'cv_none': {'it': 'Cross-validation non disponibile.', 'en': 'Cross-validation not available.'},
    'interp_r2_good': {'it': 'Buona capacità predittiva: la struttura spaziale spiega gran parte della variabilità.',
                       'en': 'Good predictive skill: the spatial structure explains most of the variability.'},
    'interp_r2_mid': {'it': 'Capacità predittiva moderata: la mappa è indicativa, considera l\'incertezza.',
                      'en': 'Moderate predictive skill: the map is indicative, consider the uncertainty.'},
    'interp_r2_low': {'it': 'Bassa capacità predittiva: i dati hanno poca correlazione spaziale o troppo rumore.',
                      'en': 'Low predictive skill: the data have little spatial correlation or too much noise.'},
    'interp_msdr_over': {'it': 'MSDR > 1.5: l\'incertezza stimata è sottostimata.',
                         'en': 'MSDR > 1.5: the estimated uncertainty is underestimated.'},
    'interp_msdr_under': {'it': 'MSDR < 0.5: l\'incertezza stimata è sovrastimata.',
                          'en': 'MSDR < 0.5: the estimated uncertainty is overestimated.'},
    'kriging_layers_added': {'it': 'Layer aggiunti alla mappa: {names}', 'en': 'Layers added to the map: {names}'},
    'next_report': {'it': 'Prossimo passo: Report →', 'en': 'Next step: Report →'},

    # ------------------------------------------------------------ ML tab
    'ml_title': {'it': '<b>4. Pattern recognition (machine learning)</b>',
                 'en': '<b>4. Pattern recognition (machine learning)</b>'},
    'ml_desc': {'it': 'Raggruppa i punti per posizione e attributi numerici o individua anomalie. '
                      'Viene creato un layer con l\'etichetta di ogni punto.',
                'en': 'Groups points by position and numeric attributes or detects anomalies. '
                      'A layer with each point\'s label is created.'},
    'ml_data': {'it': 'Dati e metodo', 'en': 'Data and method'},
    'ml_layers_select': {'it': 'Layer di punti da analizzare (uno o più):', 'en': 'Point layers to analyse (one or more):'},
    'ml_method': {'it': 'Metodo:', 'en': 'Method:'},
    'ml_kmeans': {'it': 'K-Means – gruppi per similarità', 'en': 'K-Means – groups by similarity'},
    'ml_dbscan': {'it': 'DBSCAN – gruppi per densità (trova anche punti isolati)',
                  'en': 'DBSCAN – groups by density (also finds isolated points)'},
    'ml_isolation': {'it': 'Isolation Forest – rilevamento anomalie', 'en': 'Isolation Forest – anomaly detection'},
    'ml_n_clusters': {'it': 'Numero di gruppi (0 = automatico):', 'en': 'Number of groups (0 = automatic):'},
    'ml_rf_hint': {'it': 'Classificazione supervisionata (Random Forest con campo etichetta): '
                         'Processing → GeoArchaeo → Pattern recognition ML.',
                   'en': 'Supervised classification (Random Forest with a label field): '
                         'Processing → GeoArchaeo → ML pattern recognition.'},
    'run_ml': {'it': 'Avvia pattern recognition', 'en': 'Run pattern recognition'},
    'ml_results': {'it': '<b>{method}</b>: {n} gruppi su {points} punti', 'en': '<b>{method}</b>: {n} groups over {points} points'},
    'ml_group_line': {'it': '{name}: {count} punti', 'en': '{name}: {count} points'},
    'select_at_least_one_layer': {'it': 'Seleziona almeno un layer', 'en': 'Select at least one layer'},

    # ------------------------------------------------------------ sampling tab
    'sampling_title': {'it': '<b>5. Nuovi punti di campionamento</b>', 'en': '<b>5. New sampling locations</b>'},
    'sampling_desc': {'it': 'Suggerisce dove campionare/scavare in futuro partendo dai punti esistenti '
                            '(layer scelto in alto). Viene creato un layer con i punti proposti.',
                      'en': 'Suggests where to sample/excavate next based on the existing points '
                            '(layer chosen above). A layer with the proposed points is created.'},
    'sampling_params': {'it': 'Parametri', 'en': 'Parameters'},
    'existing_points': {'it': 'Punti esistenti: <b>{layer}</b>', 'en': 'Existing points: <b>{layer}</b>'},
    'study_area': {'it': 'Area di studio (poligono, opzionale):', 'en': 'Study area (polygon, optional):'},
    'new_points': {'it': 'Nuovi punti da proporre:', 'en': 'New points to propose:'},
    'sampling_method': {'it': 'Criterio:', 'en': 'Criterion:'},
    'sampling_maximin': {'it': 'Copertura (maximin)', 'en': 'Coverage (maximin)'},
    'sampling_variance': {'it': 'Riduzione incertezza (varianza di kriging)', 'en': 'Uncertainty reduction (kriging variance)'},
    'sampling_stratified': {'it': 'Griglia stratificata', 'en': 'Stratified grid'},
    'sampling_adaptive': {'it': 'Adattivo (zone meno dense)', 'en': 'Adaptive (sparser areas)'},
    'sampling_maximin_desc': {'it': 'Ogni nuovo punto è il più lontano possibile da tutti gli altri: copertura uniforme.',
                              'en': 'Each new point is as far as possible from all others: uniform coverage.'},
    'sampling_variance_desc': {'it': 'Ogni nuovo punto va dove la varianza di kriging è massima (usa il variogramma '
                                     'calcolato, se disponibile).',
                               'en': 'Each new point goes where the kriging variance is highest (uses the '
                                     'calculated variogram, if available).'},
    'sampling_stratified_desc': {'it': 'Una posizione per cella di una griglia regolare, con leggera perturbazione casuale.',
                                 'en': 'One location per cell of a regular grid, with a slight random jitter.'},
    'sampling_adaptive_desc': {'it': 'Estrazione casuale con probabilità maggiore nelle zone con pochi punti esistenti.',
                               'en': 'Random draw with higher probability where few existing points are present.'},
    'calc_optimal': {'it': 'Calcola nuovi punti', 'en': 'Calculate new points'},
    'sampling_results': {'it': '<b>{n} nuovi punti proposti</b> ({method})', 'en': '<b>{n} new points proposed</b> ({method})'},
    'suggested_points': {'it': 'Coordinate dei punti proposti:', 'en': 'Coordinates of the proposed points:'},
    'select_existing_points': {'it': 'Seleziona il layer dei punti esistenti (in alto)', 'en': 'Select the existing points layer (above)'},
    'no_points_in_layer': {'it': 'Nessun punto trovato nel layer', 'en': 'No points found in the layer'},

    # ------------------------------------------------------------ report tab
    'report_title': {'it': '<b>6. Report</b>', 'en': '<b>6. Report</b>'},
    'report_desc': {'it': 'Riunisce in un unico documento le analisi eseguite in questa sessione '
                          '(statistiche, grafici interattivi, parametri e validazione).',
                    'en': 'Collects the analyses run in this session into a single document '
                          '(statistics, interactive charts, parameters and validation).'},
    'report_sections': {'it': 'Sezioni da includere', 'en': 'Sections to include'},
    'section_stats': {'it': 'Statistiche descrittive', 'en': 'Descriptive statistics'},
    'section_variogram': {'it': 'Variogramma', 'en': 'Variogram'},
    'section_kriging': {'it': 'Kriging e cross-validation', 'en': 'Kriging and cross-validation'},
    'section_ml': {'it': 'Pattern recognition', 'en': 'Pattern recognition'},
    'section_sampling': {'it': 'Nuovi punti di campionamento', 'en': 'New sampling locations'},
    'available': {'it': 'disponibile', 'en': 'available'},
    'not_available': {'it': 'non ancora calcolato', 'en': 'not yet calculated'},
    'generate_report': {'it': 'Salva report HTML', 'en': 'Save HTML report'},
    'generate_pdf': {'it': 'Salva report PDF', 'en': 'Save PDF report'},
    'save_report_html': {'it': 'Salva report HTML', 'en': 'Save HTML report'},
    'save_report_pdf': {'it': 'Salva report PDF', 'en': 'Save PDF report'},
    'report_saved': {'it': 'Report salvato in {path}', 'en': 'Report saved to {path}'},
    'report_no_sections': {'it': 'Seleziona almeno una sezione', 'en': 'Select at least one section'},
    'report_nothing': {'it': 'Nessuna analisi disponibile: esegui prima almeno un\'analisi.',
                       'en': 'No analysis available: run at least one analysis first.'},
    'report_generated': {'it': 'Generato il', 'en': 'Generated on'},
    'report_layer': {'it': 'Layer', 'en': 'Layer'},
    'report_field': {'it': 'Campo', 'en': 'Field'},
    'report_parameter': {'it': 'Parametro', 'en': 'Parameter'},
    'report_value': {'it': 'Valore', 'en': 'Value'},
    'report_method': {'it': 'Metodo', 'en': 'Method'},
    'report_pdf_error': {'it': 'Impossibile creare il PDF.\nSalva il report HTML e stampalo dal browser.\nErrore: {msg}',
                         'en': 'Cannot create the PDF.\nSave the HTML report and print it from the browser.\nError: {msg}'},
    'report_preview_hint': {'it': 'Anteprima: i grafici interattivi sono inclusi nel file HTML salvato.',
                            'en': 'Preview: the interactive charts are included in the saved HTML file.'},

    # ------------------------------------------------------------ examples
    'examples_title': {'it': 'Dati di esempio GeoArchaeo', 'en': 'GeoArchaeo example data'},
    'examples_desc': {'it': 'Seleziona i dataset da aggiungere al progetto:', 'en': 'Select the datasets to add to the project:'},
    'examples_path': {'it': 'Cartella:', 'en': 'Folder:'},
    'examples_none': {'it': 'Nessun dataset trovato in {path}', 'en': 'No dataset found in {path}'},
    'examples_loaded': {'it': '{n} layer caricati', 'en': '{n} layers loaded'},
    'examples_errors': {'it': 'Errori:\n{errors}', 'en': 'Errors:\n{errors}'},
    'browse': {'it': 'Sfoglia…', 'en': 'Browse…'},
    'select_examples_dir': {'it': 'Scegli la cartella dei dati di esempio', 'en': 'Choose the example data folder'},
    'villa_ceramica': {'it': 'Villa Ceramica (500 punti – distribuzione ceramica)', 'en': 'Villa Ceramica (500 points – ceramic distribution)'},
    'geofisica_survey': {'it': 'Survey geofisico (4800 punti – GPR + magnetometria)', 'en': 'Geophysical survey (4800 points – GPR + magnetometry)'},
    'soil_samples': {'it': 'Campioni di suolo (80 punti – composizione)', 'en': 'Soil samples (80 points – composition)'},
    'necropoli': {'it': 'Necropoli (120 tombe – clustering)', 'en': 'Necropolis (120 tombs – clustering)'},
    'magnetometria_grid': {'it': 'Griglia magnetometrica (2500 punti – anomalie)', 'en': 'Magnetometry grid (2500 points – anomalies)'},
    'ricognizione_survey': {'it': 'Ricognizione (100 punti – densità)', 'en': 'Field survey (100 points – density)'},
    'unita_scavo_ceramica': {'it': 'Unità di scavo (50 punti – ceramica)', 'en': 'Excavation units (50 points – ceramics)'},
    'area_studio': {'it': 'Area di studio (poligono per il campionamento)', 'en': 'Study area (polygon for sampling)'},

    # ------------------------------------------------------------ messages
    'warning': {'it': 'Attenzione', 'en': 'Warning'},
    'error': {'it': 'Errore', 'en': 'Error'},
    'completed': {'it': 'Completato', 'en': 'Completed'},
    'select_layer_field': {'it': 'Seleziona un layer di punti e un campo numerico (in alto nel pannello)',
                           'en': 'Select a point layer and a numeric field (at the top of the panel)'},
    'min_points': {'it': 'Servono almeno {n} punti con valore valido (trovati {found})',
                   'en': 'At least {n} points with a valid value are required (found {found})'},
    'analysis_running': {'it': 'Un\'analisi è già in corso: attendi che finisca o annullala.',
                         'en': 'An analysis is already running: wait for it to finish or cancel it.'},
    'analysis_cancelled': {'it': 'Analisi annullata', 'en': 'Analysis cancelled'},
    'running': {'it': 'Calcolo in corso…', 'en': 'Computing…'},
    'error_visualization': {'it': 'Errore nella visualizzazione:\n{msg}', 'en': 'Visualization error:\n{msg}'},
    'error_analysis': {'it': 'Errore durante l\'analisi:\n{msg}', 'en': 'Analysis error:\n{msg}'},
    'raster_created': {'it': 'Raster kriging creato', 'en': 'Kriging raster created'},
    'layer_created': {'it': 'Layer creato: {name}', 'en': 'Layer created: {name}'},
    'open_in_browser': {'it': 'Apri grafico interattivo nel browser', 'en': 'Open interactive chart in browser'},
    'plot_waiting': {'it': 'Il grafico apparirà qui dopo il calcolo.', 'en': 'The chart will appear here after the computation.'},
    'plot_static_hint': {'it': 'Anteprima statica (QtWebEngine non disponibile in questa installazione di QGIS).',
                         'en': 'Static preview (QtWebEngine not available in this QGIS installation).'},
    'no_values_found': {'it': 'Nessun valore numerico valido nel campo selezionato', 'en': 'No valid numeric value in the selected field'},
    'no_valid_data': {'it': 'Nessun dato valido trovato', 'en': 'No valid data found'},
    'geographic_crs_question': {'it': 'Il layer usa un CRS geografico: le distanze saranno in gradi e i risultati '
                                      'poco significativi.\nMeglio riproiettare in un CRS proiettato (es. UTM).\n\n'
                                      'Continuare comunque?',
                                'en': 'The layer uses a geographic CRS: distances will be in degrees and the results '
                                      'hardly meaningful.\nReproject to a projected CRS (e.g. UTM) first.\n\n'
                                      'Continue anyway?'},
    'language_changed': {'it': 'Lingua impostata su Italiano', 'en': 'Language set to English'},

    # ------------------------------------------------------------ layer names
    'kriging_result_layer': {'it': 'Kriging_{field}', 'en': 'Kriging_{field}'},
    'kriging_std_layer': {'it': 'Kriging_{field}_incertezza', 'en': 'Kriging_{field}_uncertainty'},
    'ml_clusters_layer': {'it': 'Gruppi_ML', 'en': 'ML_groups'},
    'ml_anomalies_layer': {'it': 'Anomalie_ML', 'en': 'ML_anomalies'},
    'sampling_points_layer': {'it': 'Nuovi_punti_campionamento', 'en': 'New_sampling_points'},

    # ------------------------------------------------------------ cluster labels
    'cluster_label': {'it': 'Gruppo {letter}', 'en': 'Group {letter}'},
    'cluster_with_count': {'it': 'Gruppo {letter} (n={count})', 'en': 'Group {letter} (n={count})'},
    'anomaly_normal': {'it': 'Normale', 'en': 'Normal'},
    'anomaly_outlier': {'it': 'Anomalia', 'en': 'Anomaly'},
    'noise_points': {'it': 'Isolati / rumore', 'en': 'Isolated / noise'},
    'kmeans_desc': {'it': 'K-Means: gruppi per similarità di posizione e attributi', 'en': 'K-Means: groups by similarity of position and attributes'},
    'dbscan_desc': {'it': 'DBSCAN: gruppi per densità spaziale', 'en': 'DBSCAN: groups by spatial density'},
    'isolation_desc': {'it': 'Isolation Forest: rilevamento anomalie', 'en': 'Isolation Forest: anomaly detection'},
    'rf_desc': {'it': 'Random Forest: classificazione supervisionata', 'en': 'Random Forest: supervised classification'},

    # ------------------------------------------------------------ plugin toolbar / menu
    'toolbar_panel': {'it': 'Pannello GeoArchaeo', 'en': 'GeoArchaeo panel'},
    'toolbar_variogram': {'it': 'Variogramma', 'en': 'Variogram'},
    'toolbar_kriging': {'it': 'Kriging', 'en': 'Kriging'},
    'toolbar_ml': {'it': 'Pattern recognition', 'en': 'Pattern recognition'},
    'toolbar_report': {'it': 'Report', 'en': 'Report'},
    'toolbar_help': {'it': 'Guida GeoArchaeo', 'en': 'GeoArchaeo help'},
    'toolbar_examples': {'it': 'Carica dati di esempio', 'en': 'Load example data'},
}


def get_language():
    """Get current language"""
    return _current_language


def set_language(lang, persist=True):
    """Set current language (it or en) and optionally persist it in QGIS settings"""
    global _current_language
    if lang not in SUPPORTED_LANGUAGES:
        return
    _current_language = lang
    if persist:
        try:
            from qgis.PyQt.QtCore import QSettings
        except ImportError:      # fuori da QGIS (test del motore)
            return
        QSettings().setValue(_SETTINGS_KEY, lang)


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
    except (KeyError, IndexError, ValueError):
        return text


def tr2(it, en):
    """Scelta diretta tra due testi (per stringhe lunghe usate una sola volta)"""
    return it if _current_language == 'it' else en
