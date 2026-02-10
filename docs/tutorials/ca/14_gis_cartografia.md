# Tutorial 14: GIS i Cartografia

## Introducció

PyArchInit està profundament integrat amb **QGIS**, aprofitant totes les seves funcionalitats GIS per a la gestió espacial de les dades arqueològiques. Aquest tutorial cobreix la integració cartogràfica, les capes predefinides i les funcionalitats avançades com la **segmentació automàtica SAM**.

### Funcionalitats GIS Principals

- Visualització US al mapa
- Capes vectorials predefinides
- Estilització QML personalitzada
- Cotes i mesuraments GIS
- Segmentació automàtica (SAM)
- Exportació cartogràfica

## Capes Predefinides PyArchInit

### Capes Vectorials Principals

| Capa | Geometria | Descripció |
|------|-----------|-------------|
| `pyunitastratigrafiche` | MultiPolygon | US dipòsit |
| `pyunitastratigrafiche_usm` | MultiPolygon | US muràries |
| `pyarchinit_quote` | Point | Punts cota |
| `pyarchinit_siti` | Point | Localització llocs |
| `pyarchinit_ripartizioni_spaziali` | Polygon | Àrees d'excavació |
| `pyarchinit_strutture_ipotesi` | Polygon | Estructures hipotètiques |
| `pyarchinit_documentazione` | Point | Referències documentació |

### Atributs Capa US

| Camp | Tipus | Descripció |
|------|-------|-------------|
| `gid` | Integer | ID únic |
| `scavo_s` | Text | Nom lloc |
| `area_s` | Text | Número àrea |
| `us_s` | Text | Número US |
| `stratigraph_index_us` | Integer | Índex estratigràfic |
| `tipo_us_s` | Text | Tipus US |
| `rilievo_originale` | Text | Aixecament d'origen |
| `disegnatore` | Text | Autor aixecament |
| `data` | Date | Data aixecament |

## Visualització US al Mapa

### Des de la Pestanya "Map" a la Fitxa US

1. Obrir una fitxa US
2. Seleccionar la pestanya **Map**
3. Funcions disponibles:

| Botó | Funció |
|------|--------|
| View US | Visualitza US actual al mapa |
| View All | Visualitza totes les US de l'àrea |
| New Record | Crea nova geometria |
| Pan to | Centra mapa sobre US |

### Visualització des de Cerca

1. Executar una cerca US
2. Botó **"View Record"** → visualitza individual
3. Botó **"View All"** → visualitza tots els resultats

## Estilització de les Capes

### Fitxers QML

PyArchInit inclou estils predefinits en format QML:
```
pyarchinit/styles/
├── pyunitastratigrafiche.qml
├── pyunitastratigrafiche_usm.qml
├── pyarchinit_quote.qml
└── ...
```

### Aplicació Estil

1. Seleccionar la capa a la llegenda
2. Botó dret → **Propietats**
3. Pestanya **Estil**
4. **Carrega estil** → seleccionar QML

### Personalització

Els estils es poden personalitzar per:
- Colors segons el tipus US
- Etiquetes amb número US
- Transparència
- Vores i farciments

## Cotes i Mesuraments

### Capa Cotes

La capa `pyarchinit_quote` emmagatzema:
- Coordenades X, Y
- Cota Z (absoluta)
- Tipus punt cota
- US de referència
- Àrea de referència

### Càlcul Cotes Automàtic

Des de la Fitxa US, les cotes min/max es calculen:
1. Consulta als punts cota associats a l'US
2. Extracció valor mínim i màxim
3. Visualització a l'informe

### Inserció Cotes

1. Capa cotes en edició
2. Dibuixar punt al mapa
3. Emplenar atributs:
   - `sito_q`
   - `area_q`
   - `us_q`
   - `quota`
   - `unita_misura_q`

## Segmentació Automàtica SAM

### Què és SAM?

**SAM (Segment Anything Model)** és un model d'intel·ligència artificial desenvolupat per Meta per a la segmentació automàtica d'imatges. PyArchInit l'integra per:
- Digitalització automàtica de pedres/elements
- Segmentació d'ortofotos
- Acceleració de l'aixecament

### Accés a la Funció

1. **PyArchInit** → **SAM Segmentation**
2. O des de la barra d'eines: icona **SAM**

### Interfície SAM

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
|   Site (sito): [camp automàtic]                  |
|   Area: [input àrea]                             |
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
|   [ComboBox model]                               |
|   API Key: [******]                              |
+--------------------------------------------------+
|        [Start Segmentation]  [Cancel]             |
+--------------------------------------------------+
```

### Modes de Segmentació

#### 1. Mode Automàtic
- Segmenta automàticament tots els objectes visibles
- Ideal per a àrees amb moltes pedres
- Requereix ortofoto de bona qualitat

#### 2. Mode Click
- Fer clic sobre cada objecte a segmentar
- Right-click o Enter per acabar
- Escape per cancel·lar
- Més precís per a objectes específics

#### 3. Mode Box
- Dibuixar rectangle sobre l'àrea
- Segmenta només l'àrea seleccionada
- Útil per a zones delimitades

#### 4. Mode Polygon
- Dibuixar polígon lliure
- Click per afegir vèrtexs
- Right-click per completar
- Per a àrees irregulars

#### 5. Mode From Layer
- Usa polígon existent com a màscara
- Seleccionar capa poligonal
- Segmenta només dins del polígon

### Models Disponibles

| Model | Tipus | Requisits | Qualitat |
|-------|-------|-----------|----------|
| Replicate SAM-2 | Cloud API | API Key | Òptima |
| Roboflow SAM-3 | Cloud API | API Key | Òptima + Text Prompt |
| SAM vit_b | Local | 375MB VRAM | Bona |
| SAM vit_l | Local | 1.2GB VRAM | Molt bona |
| SAM vit_h | Local | 2.5GB VRAM | Excel·lent |
| OpenCV | Local | Cap | Bàsica |

### SAM-3 amb Text Prompt

La versió SAM-3 (Roboflow) suporta **prompts textuals**:
- "stones" - pedres
- "pottery fragments" - fragments ceràmics
- "bones" - ossos
- Qualsevol descripció textual

### Configuració API

#### Replicate API (SAM-2)
1. Registrar-se a [replicate.com](https://replicate.com)
2. Obtenir API key
3. Inserir a la configuració

#### Roboflow API (SAM-3)
1. Registrar-se a [roboflow.com](https://roboflow.com)
2. Obtenir API key
3. Inserir a la configuració

### Instal·lació Local SAM

Per a ús local sense API:
```bash
# Crear entorn virtual
cd ~/pyarchinit/bin
python -m venv sam_venv

# Activar entorn
source sam_venv/bin/activate

# Instal·lar dependències
pip install segment-anything torch torchvision

# Descarregar models (opcional)
# vit_b: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
# vit_l: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth
# vit_h: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
```

### Flux de Treball SAM

1. **Preparació**
   - Carregar ortofoto com a capa ràster
   - Verificar sistema de referència
   - Preparar capa objectiu

2. **Configuració**
   - Seleccionar ràster d'entrada
   - Establir atributs per defecte
   - Escollir mode i model

3. **Execució**
   - Fer clic "Start Segmentation"
   - Esperar elaboració
   - Verificar resultats

4. **Post-elaboració**
   - Controlar polígons generats
   - Assignar números US
   - Corregir eventuals errors

## Integració Cartogràfica

### Exportació Dades GIS

Des de la Fitxa US, pestanya Map:
- **Export GeoPackage**: Capa com GPKG
- **Export Shapefile**: Capa com SHP
- **Export GeoJSON**: Capa com JSON

### Importació Dades GIS

Importar geometries existents:
1. Carregar capa a QGIS
2. Seleccionar feature
3. Usar funció import

### Geoprocessament

Operacions espacials disponibles:
- Buffer
- Intersecció
- Unió
- Diferència
- Centroids

## Bones Pràctiques

### 1. Ortofotos

- Resolució mínima: 1-2 cm/píxel
- Format: GeoTIFF georeferenciat
- Sistema referència: coherent amb projecte

### 2. Digitalització

- Usar snap per a precisió
- Verificar topologia
- Mantenir consistència atributs

### 3. SAM Segmentation

- Ortofoto d'alta qualitat
- Il·luminació uniforme
- Contrast adequat objectes/fons
- Post-verificació sempre necessària

### 4. Organització Capes

- Agrupar per tipologia
- Usar estils consistents
- Mantenir ordre a la llegenda

## Resolució de Problemes

### Capes No Visualitzades

**Causes possibles**:
- Extensió errònia
- Sistema referència diferent
- Filtre actiu

**Solucions**:
- Zoom to Layer
- Verificar CRS
- Eliminar filtres

### SAM No Funciona

**Causes possibles**:
- API key no vàlida
- Ràster no georeferenciat
- Model local no instal·lat

**Solucions**:
- Verificar API key
- Controlar georeferenciació
- Instal·lar model

### Geometries Corruptes

**Causes possibles**:
- Errors de digitalització
- Import problemàtic

**Solucions**:
- Usar "Fix Geometries"
- Redibuixar element

## Referències

### Fitxers Font
- `modules/gis/pyarchinit_pyqgis.py` - Integració GIS
- `tabs/Sam_Segmentation_Dialog.py` - Diàleg SAM
- `modules/gis/sam_map_tools.py` - Tool mapa SAM

### Capes
- `pyunitastratigrafiche` - US dipòsit
- `pyunitastratigrafiche_usm` - US muràries
- `pyarchinit_quote` - Cotes

---

## Vídeo Tutorial

### Integració GIS
`[Placeholder: video_gis_integration.mp4]`

**Continguts**:
- Capes predefinides
- Visualització US
- Estilització i etiquetes
- Exportació cartogràfica

**Durada prevista**: 15-18 minuts

### Segmentació SAM
`[Placeholder: video_sam_segmentation.mp4]`

**Continguts**:
- Configuració SAM
- Modes de segmentació
- Post-elaboració
- Bones pràctiques

**Durada prevista**: 12-15 minuts

---

*Última actualització: Gener 2026*

---

## Animació Interactiva

Explora l'animació interactiva per aprendre més sobre aquest tema.

[Obre Animació Interactiva](../../animations/pyarchinit_image_classification_animation.html)
