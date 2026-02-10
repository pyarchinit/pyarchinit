# Tutorial 14: GIS e Cartografia

## Introduzione

PyArchInit e profondamente integrato con **QGIS**, sfruttandone tutte le funzionalita GIS per la gestione spaziale dei dati archeologici. Questo tutorial copre l'integrazione cartografica, i layer predefiniti e le funzionalita avanzate come la **segmentazione automatica SAM**.

### Funzionalita GIS Principali

- Visualizzazione US su mappa
- Layer vettoriali predefiniti
- Styling QML personalizzato
- Quote e misurazioni GIS
- Segmentazione automatica (SAM)
- Export cartografico

## Layer Predefiniti PyArchInit

### Layer Vettoriali Principali

| Layer | Geometria | Descrizione |
|-------|-----------|-------------|
| `pyunitastratigrafiche` | MultiPolygon | US deposito |
| `pyunitastratigrafiche_usm` | MultiPolygon | US murarie |
| `pyarchinit_quote` | Point | Punti quota |
| `pyarchinit_siti` | Point | Localizzazione siti |
| `pyarchinit_ripartizioni_spaziali` | Polygon | Aree di scavo |
| `pyarchinit_strutture_ipotesi` | Polygon | Strutture ipotizzate |
| `pyarchinit_documentazione` | Point | Riferimenti documentazione |

### Attributi Layer US

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `gid` | Integer | ID univoco |
| `scavo_s` | Text | Nome sito |
| `area_s` | Text | Numero area |
| `us_s` | Text | Numero US |
| `stratigraph_index_us` | Integer | Indice stratigrafico |
| `tipo_us_s` | Text | Tipo US |
| `rilievo_originale` | Text | Rilievo di origine |
| `disegnatore` | Text | Autore rilievo |
| `data` | Date | Data rilievo |

## Visualizzazione US su Mappa

### Dal Tab "Map" nella Scheda US

1. Aprire una scheda US
2. Selezionare il tab **Map**
3. Funzioni disponibili:

| Pulsante | Funzione |
|----------|----------|
| View US | Visualizza US corrente su mappa |
| View All | Visualizza tutte le US dell'area |
| New Record | Crea nuova geometria |
| Pan to | Centra mappa su US |

### Visualizzazione da Ricerca

1. Eseguire una ricerca US
2. Pulsante **"View Record"** → visualizza singola
3. Pulsante **"View All"** → visualizza tutti i risultati

## Styling dei Layer

### File QML

PyArchInit include stili predefiniti in formato QML:
```
pyarchinit/styles/
├── pyunitastratigrafiche.qml
├── pyunitastratigrafiche_usm.qml
├── pyarchinit_quote.qml
└── ...
```

### Applicazione Stile

1. Selezionare il layer in legenda
2. Tasto destro → **Proprieta**
3. Tab **Stile**
4. **Carica stile** → selezionare QML

### Personalizzazione

Gli stili possono essere personalizzati per:
- Colori in base al tipo US
- Etichette con numero US
- Trasparenza
- Bordi e riempimenti

## Quote e Misurazioni

### Layer Quote

Il layer `pyarchinit_quote` memorizza:
- Coordinate X, Y
- Quota Z (assoluta)
- Tipo punto quota
- US di riferimento
- Area di riferimento

### Calcolo Quote Automatico

Dalla Scheda US, le quote min/max vengono calcolate:
1. Query ai punti quota associati all'US
2. Estrazione valore minimo e massimo
3. Visualizzazione nel report

### Inserimento Quote

1. Layer quote in editing
2. Disegnare punto sulla mappa
3. Compilare attributi:
   - `sito_q`
   - `area_q`
   - `us_q`
   - `quota`
   - `unita_misura_q`

## Segmentazione Automatica SAM

### Cos'e SAM?

**SAM (Segment Anything Model)** e un modello di intelligenza artificiale sviluppato da Meta per la segmentazione automatica di immagini. PyArchInit lo integra per:
- Digitalizzazione automatica di pietre/elementi
- Segmentazione di ortofoto
- Velocizzazione del rilievo

### Accesso alla Funzione

1. **PyArchInit** → **SAM Segmentation**
2. Oppure dalla toolbar: icona **SAM**

### Interfaccia SAM

```
+--------------------------------------------------+
|        SAM Stone Segmentation                     |
+--------------------------------------------------+
| Input:                                            |
|   Raster Layer: [ComboBox ortofoto]              |
+--------------------------------------------------+
| Target Layer:                                     |
|   [o] pyunitastratigrafiche                      |
|   [ ] pyunitastratigrafiche_usm                  |
+--------------------------------------------------+
| Default Attributes:                               |
|   Site (sito): [campo automatico]                |
|   Area: [input area]                             |
|   Stratigraphic Index: [1-10]                    |
|   Type US: [pietra|layer|accumulo|taglio]        |
+--------------------------------------------------+
| Segmentation Mode:                                |
|   [o] Automatic (detect all stones)              |
|   [ ] Click mode (click on each stone)           |
|   [ ] Box mode (draw rectangle)                  |
|   [ ] Polygon mode (draw freehand)               |
|   [ ] From layer (use existing polygon)          |
+--------------------------------------------------+
| Model:                                            |
|   [ComboBox modello]                             |
|   API Key: [******]                              |
+--------------------------------------------------+
|        [Start Segmentation]  [Cancel]             |
+--------------------------------------------------+
```

### Modalita di Segmentazione

#### 1. Automatic Mode
- Segmenta automaticamente tutti gli oggetti visibili
- Ideale per aree con molte pietre
- Richiede ortofoto di buona qualita

#### 2. Click Mode
- Cliccare su ogni oggetto da segmentare
- Right-click o Enter per terminare
- Escape per annullare
- Piu preciso per oggetti specifici

#### 3. Box Mode
- Disegnare rettangolo sull'area
- Segmenta solo l'area selezionata
- Utile per zone delimitate

#### 4. Polygon Mode
- Disegnare poligono libero
- Click per aggiungere vertici
- Right-click per completare
- Per aree irregolari

#### 5. From Layer Mode
- Usa poligono esistente come maschera
- Selezionare layer poligonale
- Segmenta solo entro il poligono

### Modelli Disponibili

| Modello | Tipo | Requisiti | Qualita |
|---------|------|-----------|---------|
| Replicate SAM-2 | Cloud API | API Key | Ottima |
| Roboflow SAM-3 | Cloud API | API Key | Ottima + Text Prompt |
| SAM vit_b | Locale | 375MB VRAM | Buona |
| SAM vit_l | Locale | 1.2GB VRAM | Molto buona |
| SAM vit_h | Locale | 2.5GB VRAM | Eccellente |
| OpenCV | Locale | Nessuno | Base |

### SAM-3 con Text Prompt

La versione SAM-3 (Roboflow) supporta **prompt testuali**:
- "stones" - pietre
- "pottery fragments" - frammenti ceramici
- "bones" - ossa
- Qualsiasi descrizione testuale

### Configurazione API

#### Replicate API (SAM-2)
1. Registrarsi su [replicate.com](https://replicate.com)
2. Ottenere API key
3. Inserire nella configurazione

#### Roboflow API (SAM-3)
1. Registrarsi su [roboflow.com](https://roboflow.com)
2. Ottenere API key
3. Inserire nella configurazione

### Installazione Locale SAM

Per utilizzo locale senza API:
```bash
# Creare ambiente virtuale
cd ~/pyarchinit/bin
python -m venv sam_venv

# Attivare ambiente
source sam_venv/bin/activate

# Installare dipendenze
pip install segment-anything torch torchvision

# Scaricare modelli (opzionale)
# vit_b: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
# vit_l: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth
# vit_h: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
```

### Workflow SAM

1. **Preparazione**
   - Caricare ortofoto come layer raster
   - Verificare sistema di riferimento
   - Preparare layer target

2. **Configurazione**
   - Selezionare raster di input
   - Impostare attributi default
   - Scegliere modalita e modello

3. **Esecuzione**
   - Cliccare "Start Segmentation"
   - Attendere elaborazione
   - Verificare risultati

4. **Post-elaborazione**
   - Controllare poligoni generati
   - Assegnare numeri US
   - Correggere eventuali errori

## Integrazione Cartografica

### Export Dati GIS

Dalla Scheda US, tab Map:
- **Export GeoPackage**: Layer come GPKG
- **Export Shapefile**: Layer come SHP
- **Export GeoJSON**: Layer come JSON

### Import Dati GIS

Importare geometrie esistenti:
1. Caricare layer in QGIS
2. Selezionare feature
3. Usare funzione import

### Geoprocessing

Operazioni spaziali disponibili:
- Buffer
- Intersezione
- Unione
- Differenza
- Centroids

## Best Practices

### 1. Ortofoto

- Risoluzione minima: 1-2 cm/pixel
- Formato: GeoTIFF georeferenziato
- Sistema riferimento: coerente con progetto

### 2. Digitalizzazione

- Usare snap per precisione
- Verificare topologia
- Mantenere consistenza attributi

### 3. SAM Segmentation

- Ortofoto di alta qualita
- Illuminazione uniforme
- Contrasto adeguato oggetti/sfondo
- Post-verifica sempre necessaria

### 4. Organizzazione Layer

- Raggruppare per tipologia
- Usare stili consistenti
- Mantenere ordine in legenda

## Risoluzione Problemi

### Layer Non Visualizzati

**Cause possibili**:
- Estensione errata
- Sistema riferimento diverso
- Filtro attivo

**Soluzioni**:
- Zoom to Layer
- Verificare CRS
- Rimuovere filtri

### SAM Non Funziona

**Cause possibili**:
- API key non valida
- Raster non georeferenziato
- Modello locale non installato

**Soluzioni**:
- Verificare API key
- Controllare georeferenziazione
- Installare modello

### Geometrie Corrotte

**Cause possibili**:
- Errori di digitalizzazione
- Import problematico

**Soluzioni**:
- Usare "Fix Geometries"
- Ridisegnare elemento

## Riferimenti

### File Sorgente
- `modules/gis/pyarchinit_pyqgis.py` - Integrazione GIS
- `tabs/Sam_Segmentation_Dialog.py` - Dialogo SAM
- `modules/gis/sam_map_tools.py` - Tool mappa SAM

### Layer
- `pyunitastratigrafiche` - US deposito
- `pyunitastratigrafiche_usm` - US murarie
- `pyarchinit_quote` - Quote

---

## Video Tutorial

### GIS Integration
`[Placeholder: video_gis_integration.mp4]`

**Contenuti**:
- Layer predefiniti
- Visualizzazione US
- Styling e etichette
- Export cartografico

**Durata prevista**: 15-18 minuti

### SAM Segmentation
`[Placeholder: video_sam_segmentation.mp4]`

**Contenuti**:
- Configurazione SAM
- Modalita di segmentazione
- Post-elaborazione
- Best practices

**Durata prevista**: 12-15 minuti

---

*Ultimo aggiornamento: Gennaio 2026*

---

## Animazione Interattiva

Esplora l'animazione interattiva per approfondire questo argomento.

[Apri Animazione Interattiva](../../animations/pyarchinit_image_classification_animation.html)
