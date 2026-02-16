# Test Layers per GeoArchaeo Plugin

Questa cartella contiene layer di test per il plugin GeoArchaeo. I dati sono simulati ma realistici per testare le funzionalità geostatistiche.

## Layer Disponibili

### 1. Unità di Scavo (unita_scavo_ceramica)
- **Formato**: CSV + GeoJSON
- **Punti**: 50
- **CRS**: EPSG:32633 (UTM 33N)
- **Campi principali**:
  - `ceramica_tot`: Totale frammenti ceramici
  - `ceramica_fine`: Ceramica fine
  - `ceramica_comune`: Ceramica comune  
  - `fase`: Fase cronologica (Medievale, Romano Imperiale, Romano Repubblicano)
  - `profondita`: Profondità in cm
  - `area_mq`: Area scavata in mq

**Uso consigliato**:
- Variogramma su campo `ceramica_tot`
- Co-Kriging usando `ceramica_fine` e `ceramica_comune`
- Analisi per fasi cronologiche

### 2. Ricognizione (ricognizione_survey)
- **Formato**: CSV + GeoJSON
- **Punti**: 100 (griglia 10x10)
- **CRS**: EPSG:32633 (UTM 33N)
- **Campi principali**:
  - `densita_mq`: Frammenti per metro quadrato
  - `visibilita`: Scala 1-5
  - `uso_suolo`: Tipo di terreno
  - `pendenza`: Inclinazione in gradi
  - `distanza_acqua`: Distanza dalla fonte d'acqua più vicina

**Uso consigliato**:
- Kriging su `densita_mq` con filtro visibilità
- Machine Learning per identificare pattern
- Correlazione con variabili ambientali

### 3. Magnetometria (magnetometria_grid)
- **Formato**: CSV
- **Punti**: 2500 (griglia 50x50)
- **CRS**: EPSG:32633 (UTM 33N)
- **Campi principali**:
  - `mag_nT`: Valore magnetometrico in nanoTesla
  - `x_local`, `y_local`: Coordinate locali griglia

**Caratteristiche simulate**:
- 2 muri perpendicolari (anomalie positive ~50 nT)
- 1 fossa circolare (anomalia negativa ~-30 nT)
- 1 fornace (anomalia positiva forte ~100 nT)

**Uso consigliato**:
- Kriging per interpolazione superficie
- Isolation Forest per rilevare anomalie
- Visualizzazione con scala colori divergente

## Caricamento in QGIS

### Metodo 1: File CSV
1. Menu `Layer → Aggiungi Layer → Aggiungi layer testo delimitato`
2. Seleziona il file CSV
3. Imposta:
   - Campo X: `x`
   - Campo Y: `y`
   - CRS: EPSG:32633
4. Clicca "Aggiungi"

### Metodo 2: File GeoJSON
1. Trascina il file .geojson direttamente nella mappa QGIS
2. O usa `Layer → Aggiungi Layer → Aggiungi layer vettoriale`

## Test Workflow Completo

### Test 1: Analisi Ceramica Scavo
1. Carica `unita_scavo_ceramica`
2. Apri pannello GeoArchaeo
3. Tab Variogramma:
   - Layer: unita_scavo_ceramica
   - Campo: ceramica_tot
   - Calcola variogramma
4. Tab Kriging:
   - Usa parametri dal variogramma
   - Risoluzione: 5m
   - Esegui interpolazione

### Test 2: Pattern Recognition Survey
1. Carica `ricognizione_survey`
2. Tab Machine Learning:
   - Algoritmo: DBSCAN
   - Features: densita_mq, visibilita
   - Identifica clusters

### Test 3: Anomalie Magnetometriche
1. Carica `magnetometria_grid`
2. Tab Kriging:
   - Campo: mag_nT
   - Modello: Gaussiano
   - Risoluzione: 0.5m
3. Tab Machine Learning:
   - Algoritmo: Isolation Forest
   - Rileva anomalie

## Note Tecniche

- Tutti i dati sono simulati con pattern realistici
- Le coordinate sono in metri (UTM 33N)
- I valori seguono distribuzioni tipiche per dati archeologici
- Presenza di rumore gaussiano per simulare misurazioni reali

## Troubleshooting

Se i layer non si caricano correttamente:
1. Verifica che il CRS sia impostato su EPSG:32633
2. Controlla che i campi X e Y siano riconosciuti
3. Per i CSV, assicurati che il separatore sia la virgola