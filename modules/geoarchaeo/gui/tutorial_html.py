# -*- coding: utf-8 -*-
"""Testi HTML del tutorial integrato (italiano e inglese)."""

_STYLE = '''
    <style>
        body { font-family: Arial, sans-serif; max-width: 950px; margin: 0 auto; padding: 20px; line-height: 1.6; color: #333333; background-color: #ffffff; }
        h1 { color: #1976D2; border-bottom: 2px solid #1976D2; padding-bottom: 10px; }
        h2 { color: #388E3C; margin-top: 30px; border-bottom: 1px solid #388E3C; padding-bottom: 5px; }
        h3 { color: #F57C00; }
        h4 { color: #7B1FA2; }
        p, li, td { color: #333333; }
        a { color: #1976D2; }
        code { background-color: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace; color: #c7254e; }
        .tip { background-color: #E3F2FD; border-left: 4px solid #1976D2; padding: 10px; margin: 10px 0; color: #1a237e; }
        .warning { background-color: #FFF3E0; border-left: 4px solid #F57C00; padding: 10px; margin: 10px 0; color: #e65100; }
        .theory { background-color: #F3E5F5; border-left: 4px solid #7B1FA2; padding: 10px; margin: 10px 0; color: #4a148c; }
        table { border-collapse: collapse; width: 100%; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #1976D2; color: white; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .formula { font-family: serif; font-style: italic; background-color: #fff9c4; padding: 5px 10px; display: inline-block; margin: 5px 0; color: #333333; }
    </style>
'''

TUTORIAL_IT = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Tutorial GeoArchaeo - Guida Completa</title>
''' + _STYLE + '''
</head>
<body>
    <h1>Tutorial GeoArchaeo - Guida Completa</h1>
    <p><em>Analisi Geostatistica per la Ricerca Archeologica</em></p>

    <h2>Indice</h2>
    <ol>
        <li><a href="#flusso">Come si usa il pannello</a></li>
        <li><a href="#teoria">Fondamenti Teorici</a></li>
        <li><a href="#variogramma">Il Variogramma</a></li>
        <li><a href="#kriging">Il Kriging e la sua validazione</a></li>
        <li><a href="#ml">Machine Learning</a></li>
        <li><a href="#campionamento">Nuovi punti di campionamento</a></li>
        <li><a href="#esercizi">Esercizi Pratici</a></li>
    </ol>

    <h2 id="flusso">1. Come si usa il pannello</h2>
    <p>In alto nel pannello scegli una volta sola il <strong>layer di punti</strong> e il <strong>campo numerico</strong>
    da analizzare: tutte le schede lavorano su questa selezione. Le schede seguono l'ordine consigliato di lavoro:</p>
    <ol>
        <li><strong>Dati</strong>: statistiche e istogramma per capire la distribuzione dei valori.</li>
        <li><strong>Variogramma</strong>: struttura spaziale (nugget, sill, range) e anisotropia.</li>
        <li><strong>Kriging</strong>: mappa interpolata + mappa dell'incertezza, con cross-validation.</li>
        <li><strong>Pattern (ML)</strong>: gruppi e anomalie.</li>
        <li><strong>Campionamento</strong>: dove campionare/scavare in futuro.</li>
        <li><strong>Report</strong>: un documento HTML con tutto quello che hai calcolato.</li>
    </ol>
    <div class="tip">I risultati di ogni analisi restano visibili nella scheda (riquadro sotto il pulsante) e i
    grafici compaiono nel pannello. Il pulsante "Apri grafico interattivo nel browser" apre la versione Plotly navigabile.</div>

    <h2 id="teoria">2. Fondamenti Teorici</h2>
    <h3>Cos'è la Geostatistica?</h3>
    <p>La geostatistica è una branca della statistica che si occupa di fenomeni spazialmente correlati.
    Il principio fondamentale è la <strong>Prima Legge della Geografia di Tobler</strong>:</p>
    <div class="theory"><em>"Tutto è correlato con tutto, ma le cose vicine sono più correlate delle cose lontane."</em></div>
    <h3>Perché usarla in Archeologia?</h3>
    <ul>
        <li><strong>Distribuzione manufatti</strong>: i frammenti ceramici non sono distribuiti casualmente</li>
        <li><strong>Anomalie geofisiche</strong>: strutture sepolte creano pattern spaziali</li>
        <li><strong>Composizione suoli</strong>: attività antropiche lasciano firme chimiche spazialmente correlate</li>
    </ul>
    <div class="warning"><strong>Coordinate:</strong> usa sempre un CRS proiettato in metri (es. UTM). Con coordinate
    geografiche (gradi) distanze e range non hanno significato fisico e il pannello ti avvisa.</div>

    <h2 id="variogramma">3. Il Variogramma</h2>
    <p>Il variogramma (o semivariogramma) misura come la <strong>variabilità</strong> tra coppie di punti
    cambia al crescere della <strong>distanza</strong>.</p>
    <div class="formula">γ(h) = ½ × E[(Z(x) - Z(x+h))²]</div>
    <h3>Parametri del Variogramma</h3>
    <table>
        <tr><th>Parametro</th><th>Significato</th><th>Interpretazione Archeologica</th></tr>
        <tr><td><strong>Nugget (C₀)</strong></td><td>Variabilità a distanza zero</td><td>Errore di misura + variabilità micro-scala (es. disturbo post-deposizionale)</td></tr>
        <tr><td><strong>Sill (C + C₀)</strong></td><td>Varianza totale asintotica</td><td>Massima variabilità raggiunta</td></tr>
        <tr><td><strong>Range (a)</strong></td><td>Distanza di correlazione</td><td>Dimensione tipica delle "unità funzionali" (es. stanze, aree attività)</td></tr>
    </table>
    <h3>Modelli Teorici</h3>
    <h4>Sferico</h4>
    <p>Il più comune in archeologia: la correlazione diminuisce gradualmente fino al range, oltre il quale i dati sono indipendenti.
    Adatto a distribuzioni ceramiche, densità di manufatti, dati con confini ben definiti.</p>
    <h4>Esponenziale</h4>
    <p>La correlazione cala rapidamente vicino all'origine e poi più lentamente; il range è raggiunto asintoticamente.
    Adatto a diffusione di elementi chimici nel suolo e processi con decadimento continuo.</p>
    <h4>Gaussiano</h4>
    <p>Per fenomeni molto "lisci" (superfici topografiche). Può dare instabilità numerica: usare con cautela.</p>
    <h4>Matérn</h4>
    <p>Modello flessibile (qui con parametro di rugosità ν = 1.5), intermedio tra esponenziale e gaussiano.</p>
    <div class="tip"><strong>Regola pratica:</strong> inizia con il modello <code>sferico</code>; se il fit (RMSE) è scarso prova
    <code>esponenziale</code>. Il pannello propone una distanza massima pari a circa 1/3 della diagonale dell'area (pulsante "Auto").</div>
    <h3>Anisotropia</h3>
    <p>Con la casella "Verifica anisotropia" il plugin calcola i variogrammi nelle direzioni 0°, 45°, 90°, 135° (da Est,
    antiorario). Un rapporto tra range maggiore e minore sopra 2 indica una direzione preferenziale (es. un muro, una strada,
    una pendenza).</p>

    <h2 id="kriging">4. Il Kriging e la sua validazione</h2>
    <p>Il Kriging produce la <strong>Best Linear Unbiased Prediction</strong>: pesa i punti vicini in base al variogramma e
    fornisce, per ogni cella, anche la <strong>deviazione standard</strong> della stima (mappa dell'incertezza).</p>
    <h3>Cross-validation (leave-one-out)</h3>
    <p>Ogni punto viene rimosso e ristimato dagli altri. Le metriche che compaiono dopo il kriging:</p>
    <table>
        <tr><th>Metrica</th><th>Significato</th><th>Valore desiderabile</th></tr>
        <tr><td>RMSE / MAE</td><td>Errore tipico della stima</td><td>Il più basso possibile (confrontalo con la dev. standard dei dati)</td></tr>
        <tr><td>ME</td><td>Errore medio (bias)</td><td>Vicino a 0</td></tr>
        <tr><td>R²</td><td>Quota di variabilità spiegata</td><td>&gt; 0.5 buono, &lt; 0.2 scarso</td></tr>
        <tr><td>MSDR</td><td>Errore quadratico standardizzato</td><td>≈ 1 (l'incertezza stimata è realistica)</td></tr>
    </table>
    <div class="warning"><strong>Risoluzione:</strong> la griglia è limitata a 500 celle per lato. Il pannello mostra in
    anticipo quante celle avrà la griglia; per aree grandi aumenta la dimensione della cella.</div>
    <h3>Co-Kriging e kriging spazio-temporale</h3>
    <p>Sono disponibili nella <strong>Toolbox di Processing</strong> (gruppo GeoArchaeo). Il co-kriging usa variabili
    ausiliarie (es. magnetometria per la ceramica) tramite regressione + kriging dei residui; lo spazio-temporale tratta il
    tempo come terza dimensione.</p>

    <h2 id="ml">5. Machine Learning per Pattern Recognition</h2>
    <h3>K-Means</h3>
    <p>Raggruppa i punti in K gruppi per similarità di posizione e attributi. Scegli K oppure lascia 0 (automatico).
    Adatto a classificare aree funzionali quando sai quanti gruppi aspettarti.</p>
    <h3>DBSCAN</h3>
    <p>Trova gruppi per densità, senza fissare il numero, e segnala i punti isolati (rumore). Adatto a necropoli
    (gruppi familiari) e pattern di forma irregolare.</p>
    <h3>Isolation Forest</h3>
    <p>Individua le <strong>anomalie</strong> (circa il 10% dei punti più "diversi"). Adatto a dati geofisici (muri, fosse,
    forni) e al controllo qualità.</p>
    <h3>Random Forest</h3>
    <p>Classificazione supervisionata: richiede un campo con le etichette note per una parte dei punti. Disponibile in
    Processing → GeoArchaeo → Pattern recognition ML.</p>

    <h2 id="campionamento">6. Nuovi punti di campionamento</h2>
    <table>
        <tr><th>Criterio</th><th>Quando usarlo</th></tr>
        <tr><td>Copertura (maximin)</td><td>Vuoi riempire i vuoti in modo uniforme</td></tr>
        <tr><td>Riduzione incertezza</td><td>Hai già un variogramma e vuoi ridurre l'errore di kriging dove è più alto</td></tr>
        <tr><td>Griglia stratificata</td><td>Vuoi una copertura regolare di un'area definita</td></tr>
        <tr><td>Adattivo</td><td>Vuoi privilegiare le zone meno campionate lasciando una componente casuale</td></tr>
    </table>

    <h2 id="esercizi">7. Esercizi Pratici</h2>
    <h3>Esercizio 1: Distribuzione ceramica (kriging)</h3>
    <ol>
        <li>Carica i dati di esempio (pulsante in alto) → <code>villa_ceramica</code></li>
        <li>In alto: layer <code>villa_ceramica</code>, campo <code>ceramic_count</code></li>
        <li>Scheda Dati → Calcola statistiche</li>
        <li>Scheda Variogramma → distanza "Auto", modello sferico → Calcola</li>
        <li>Scheda Kriging → cella 1 m → Esegui kriging; leggi R² e MSDR</li>
    </ol>
    <h3>Esercizio 2: Anomalie geofisiche (Isolation Forest)</h3>
    <ol>
        <li>Carica <code>geofisica_survey</code></li>
        <li>Scheda Pattern (ML) → seleziona il layer → Isolation Forest → Avvia</li>
        <li>Le anomalie (possibili strutture) sono evidenziate in rosso nel nuovo layer</li>
    </ol>
    <h3>Esercizio 3: Gruppi familiari in necropoli (DBSCAN)</h3>
    <ol>
        <li>Carica <code>necropoli</code></li>
        <li>Scheda Pattern (ML) → DBSCAN → Avvia</li>
        <li>I gruppi rappresentano probabili nuclei familiari; i punti grigi sono isolati</li>
    </ol>
    <h3>Esercizio 4: Dove scavare dopo</h3>
    <ol>
        <li>Layer <code>villa_ceramica</code>, area di studio <code>area_studio</code> (opzionale)</li>
        <li>Scheda Campionamento → 10 punti, criterio "Riduzione incertezza" → Calcola</li>
    </ol>

    <div class="warning">
        <strong>Risoluzione problemi:</strong><br>
        • <strong>Nessun campo numerico?</strong> Il campo è testo: convertilo con il Calcolatore di campi.<br>
        • <strong>Kriging lento?</strong> Aumenta la dimensione della cella.<br>
        • <strong>R² basso?</strong> I dati hanno poca correlazione spaziale: la mappa è solo indicativa.<br>
        • <strong>DBSCAN tutto "isolato"?</strong> Prova K-Means.
    </div>

    <hr>
    <p><strong>Autore:</strong> Enzo Cocca | <strong>Email:</strong> enzo.ccc@gmail.com</p>
    <p><strong>Repository:</strong> <a href="https://github.com/enzococca/GeoArchaeo">github.com/enzococca/GeoArchaeo</a></p>
</body>
</html>'''

TUTORIAL_EN = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>GeoArchaeo Tutorial - Complete Guide</title>
''' + _STYLE + '''
</head>
<body>
    <h1>GeoArchaeo Tutorial - Complete Guide</h1>
    <p><em>Geostatistical Analysis for Archaeological Research</em></p>

    <h2>Table of Contents</h2>
    <ol>
        <li><a href="#workflow">How to use the panel</a></li>
        <li><a href="#theory">Theoretical Foundations</a></li>
        <li><a href="#variogram">The Variogram</a></li>
        <li><a href="#kriging">Kriging and its validation</a></li>
        <li><a href="#ml">Machine Learning</a></li>
        <li><a href="#sampling">New sampling locations</a></li>
        <li><a href="#exercises">Practical Exercises</a></li>
    </ol>

    <h2 id="workflow">1. How to use the panel</h2>
    <p>At the top of the panel choose once the <strong>point layer</strong> and the <strong>numeric field</strong> to
    analyse: every tab works on this selection. The tabs follow the recommended workflow:</p>
    <ol>
        <li><strong>Data</strong>: statistics and histogram to understand the value distribution.</li>
        <li><strong>Variogram</strong>: spatial structure (nugget, sill, range) and anisotropy.</li>
        <li><strong>Kriging</strong>: interpolated map + uncertainty map, with cross-validation.</li>
        <li><strong>Patterns (ML)</strong>: groups and anomalies.</li>
        <li><strong>Sampling</strong>: where to sample/excavate next.</li>
        <li><strong>Report</strong>: an HTML document with everything you computed.</li>
    </ol>
    <div class="tip">The results of each analysis stay visible in the tab (box below the button) and the charts appear in
    the panel. The "Open interactive chart in browser" button opens the navigable Plotly version.</div>

    <h2 id="theory">2. Theoretical Foundations</h2>
    <h3>What is Geostatistics?</h3>
    <p>Geostatistics is a branch of statistics dealing with spatially correlated phenomena. The fundamental principle is
    <strong>Tobler's First Law of Geography</strong>:</p>
    <div class="theory"><em>"Everything is related to everything else, but near things are more related than distant things."</em></div>
    <h3>Why Use It in Archaeology?</h3>
    <ul>
        <li><strong>Artifact distribution</strong>: ceramic fragments are not randomly distributed</li>
        <li><strong>Geophysical anomalies</strong>: buried structures create spatial patterns</li>
        <li><strong>Soil composition</strong>: anthropic activities leave spatially correlated chemical signatures</li>
    </ul>
    <div class="warning"><strong>Coordinates:</strong> always use a projected CRS in metres (e.g. UTM). With geographic
    coordinates (degrees) distances and ranges have no physical meaning and the panel warns you.</div>

    <h2 id="variogram">3. The Variogram</h2>
    <p>The variogram (or semivariogram) measures how <strong>variability</strong> between pairs of points changes as
    <strong>distance</strong> increases.</p>
    <div class="formula">γ(h) = ½ × E[(Z(x) - Z(x+h))²]</div>
    <h3>Variogram Parameters</h3>
    <table>
        <tr><th>Parameter</th><th>Meaning</th><th>Archaeological Interpretation</th></tr>
        <tr><td><strong>Nugget (C₀)</strong></td><td>Variability at zero distance</td><td>Measurement error + micro-scale variability (e.g. post-depositional disturbance)</td></tr>
        <tr><td><strong>Sill (C + C₀)</strong></td><td>Asymptotic total variance</td><td>Maximum variability reached</td></tr>
        <tr><td><strong>Range (a)</strong></td><td>Correlation distance</td><td>Typical size of "functional units" (e.g. rooms, activity areas)</td></tr>
    </table>
    <h3>Theoretical Models</h3>
    <h4>Spherical</h4>
    <p>The most common in archaeology: correlation decreases gradually up to the range, beyond which data are independent.
    Suitable for ceramic distributions, artifact density, data with well-defined boundaries.</p>
    <h4>Exponential</h4>
    <p>Correlation drops quickly near the origin and then more slowly; the range is reached asymptotically. Suitable for
    diffusion of chemical elements in soil and continuously decaying processes.</p>
    <h4>Gaussian</h4>
    <p>For very "smooth" phenomena (topographic surfaces). Can be numerically unstable: use with caution.</p>
    <h4>Matérn</h4>
    <p>Flexible model (here with roughness ν = 1.5), intermediate between exponential and Gaussian.</p>
    <div class="tip"><strong>Rule of thumb:</strong> start with the <code>spherical</code> model; if the fit (RMSE) is poor
    try <code>exponential</code>. The panel proposes a maximum distance of about 1/3 of the area diagonal ("Auto" button).</div>
    <h3>Anisotropy</h3>
    <p>With "Check anisotropy" the plugin computes the variograms along 0°, 45°, 90°, 135° (from East, counter-clockwise).
    A ratio between the largest and smallest range above 2 indicates a preferential direction (e.g. a wall, a road, a slope).</p>

    <h2 id="kriging">4. Kriging and its validation</h2>
    <p>Kriging produces the <strong>Best Linear Unbiased Prediction</strong>: it weights nearby points according to the
    variogram and also provides, for every cell, the <strong>standard deviation</strong> of the estimate (uncertainty map).</p>
    <h3>Cross-validation (leave-one-out)</h3>
    <p>Each point is removed and re-estimated from the others. The metrics shown after kriging:</p>
    <table>
        <tr><th>Metric</th><th>Meaning</th><th>Desirable value</th></tr>
        <tr><td>RMSE / MAE</td><td>Typical estimation error</td><td>As low as possible (compare with the data standard deviation)</td></tr>
        <tr><td>ME</td><td>Mean error (bias)</td><td>Close to 0</td></tr>
        <tr><td>R²</td><td>Share of explained variability</td><td>&gt; 0.5 good, &lt; 0.2 poor</td></tr>
        <tr><td>MSDR</td><td>Mean squared standardized error</td><td>≈ 1 (the estimated uncertainty is realistic)</td></tr>
    </table>
    <div class="warning"><strong>Resolution:</strong> the grid is limited to 500 cells per side. The panel shows in advance
    how many cells the grid will have; for large areas increase the cell size.</div>
    <h3>Co-Kriging and spatio-temporal kriging</h3>
    <p>They are available in the <strong>Processing Toolbox</strong> (GeoArchaeo group). Co-kriging uses auxiliary variables
    (e.g. magnetometry for ceramics) through regression + kriging of the residuals; the spatio-temporal one treats time as a
    third dimension.</p>

    <h2 id="ml">5. Machine Learning for Pattern Recognition</h2>
    <h3>K-Means</h3>
    <p>Groups the points into K groups by similarity of position and attributes. Choose K or leave 0 (automatic).
    Suitable for classifying functional areas when you know how many groups to expect.</p>
    <h3>DBSCAN</h3>
    <p>Finds groups by density, without fixing their number, and flags isolated points (noise). Suitable for necropolises
    (family groups) and irregularly shaped patterns.</p>
    <h3>Isolation Forest</h3>
    <p>Detects <strong>anomalies</strong> (about the 10% most "different" points). Suitable for geophysical data (walls,
    pits, kilns) and quality control.</p>
    <h3>Random Forest</h3>
    <p>Supervised classification: requires a field with known labels for part of the points. Available in
    Processing → GeoArchaeo → ML pattern recognition.</p>

    <h2 id="sampling">6. New sampling locations</h2>
    <table>
        <tr><th>Criterion</th><th>When to use it</th></tr>
        <tr><td>Coverage (maximin)</td><td>You want to fill the gaps uniformly</td></tr>
        <tr><td>Uncertainty reduction</td><td>You already have a variogram and want to reduce the kriging error where it is highest</td></tr>
        <tr><td>Stratified grid</td><td>You want a regular coverage of a defined area</td></tr>
        <tr><td>Adaptive</td><td>You want to favour under-sampled areas while keeping a random component</td></tr>
    </table>

    <h2 id="exercises">7. Practical Exercises</h2>
    <h3>Exercise 1: Ceramic distribution (kriging)</h3>
    <ol>
        <li>Load the example data (button at the top) → <code>villa_ceramica</code></li>
        <li>At the top: layer <code>villa_ceramica</code>, field <code>ceramic_count</code></li>
        <li>Data tab → Calculate statistics</li>
        <li>Variogram tab → distance "Auto", spherical model → Calculate</li>
        <li>Kriging tab → cell 1 m → Run kriging; read R² and MSDR</li>
    </ol>
    <h3>Exercise 2: Geophysical anomalies (Isolation Forest)</h3>
    <ol>
        <li>Load <code>geofisica_survey</code></li>
        <li>Patterns (ML) tab → select the layer → Isolation Forest → Run</li>
        <li>Anomalies (possible structures) are highlighted in red in the new layer</li>
    </ol>
    <h3>Exercise 3: Necropolis family groups (DBSCAN)</h3>
    <ol>
        <li>Load <code>necropoli</code></li>
        <li>Patterns (ML) tab → DBSCAN → Run</li>
        <li>Groups represent probable family units; grey points are isolated</li>
    </ol>
    <h3>Exercise 4: Where to dig next</h3>
    <ol>
        <li>Layer <code>villa_ceramica</code>, study area <code>area_studio</code> (optional)</li>
        <li>Sampling tab → 10 points, "Uncertainty reduction" → Calculate</li>
    </ol>

    <div class="warning">
        <strong>Troubleshooting:</strong><br>
        • <strong>No numeric field?</strong> The field is text: convert it with the Field Calculator.<br>
        • <strong>Kriging slow?</strong> Increase the cell size.<br>
        • <strong>Low R²?</strong> The data have little spatial correlation: the map is only indicative.<br>
        • <strong>DBSCAN all "isolated"?</strong> Try K-Means.
    </div>

    <hr>
    <p><strong>Author:</strong> Enzo Cocca | <strong>Email:</strong> enzo.ccc@gmail.com</p>
    <p><strong>Repository:</strong> <a href="https://github.com/enzococca/GeoArchaeo">github.com/enzococca/GeoArchaeo</a></p>
</body>
</html>'''


def get_tutorial_html(lang='it'):
    return TUTORIAL_EN if lang == 'en' else TUTORIAL_IT
