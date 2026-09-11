# Tutorial 14: GIS și Cartografie

## Introducere

PyArchInit este integrat profund cu **QGIS**, valorificând toate funcționalitățile GIS pentru gestionarea spațială a datelor arheologice. Acest tutorial acoperă integrarea cartografică, straturile predefinite și funcții avansate precum **segmentarea automată SAM**.

### Funcții GIS Principale

- Vizualizarea US pe hartă
- Straturi vectoriale predefinite
- Stilizare QML personalizată
- Cote și măsurători GIS
- Segmentare automată (SAM)
- Export cartografic

## Straturi Predefinite PyArchInit

### Straturi Vectoriale Principale

| Strat | Geometrie | Descriere |
|-------|-----------|-----------|
| `pyunitastratigrafiche` | MultiPolygon | US depozit |
| `pyunitastratigrafiche_usm` | MultiPolygon | US zidărie |
| `pyarchinit_quote` | Point | Puncte de cotă |
| `pyarchinit_siti` | Point | Locații situri |
| `pyarchinit_ripartizioni_spaziali` | Polygon | Zone de săpătură |
| `pyarchinit_strutture_ipotesi` | Polygon | Structuri ipotetice |
| `pyarchinit_documentazione` | Point | Referințe documentație |

### Atributele Stratului US

| Câmp | Tip | Descriere |
|------|-----|-----------|
| `gid` | Integer | ID unic |
| `scavo_s` | Text | Numele sitului |
| `area_s` | Text | Numărul zonei |
| `us_s` | Text | Numărul US |
| `stratigraph_index_us` | Integer | Index stratigrafic |
| `tipo_us_s` | Text | Tipul US |
| `rilievo_originale` | Text | Releveu original |
| `disegnatore` | Text | Autorul releveului |
| `data` | Date | Data releveului |

## Vizualizarea US pe Hartă

### Din Tab-ul „Hartă" în Fișa US

1. Deschideți o fișă US
2. Selectați tab-ul **Hartă**
3. Funcții disponibile:

| Buton | Funcție |
|-------|---------|
| Vizualizare US | Afișează US curentă pe hartă |
| Vizualizare Toate | Afișează toate US-urile din zonă |
| Înregistrare Nouă | Creează o geometrie nouă |
| Centrare pe | Centrează harta pe US |

### Vizualizare din Căutare

1. Executați o căutare US
2. Butonul **„Vizualizare Înregistrare"** → afișare individuală
3. Butonul **„Vizualizare Toate"** → afișare toate rezultatele

### Alegerea Stilului (US și USM)

Când US sau US de zidărie (USM) din rezultatele căutării sunt încărcate pe hartă, apare fereastra **Style Choice** („How do you want to manage the layer style?"). Butoanele sunt afișate în engleză:

| Buton | Efect |
|-------|-------|
| **Save new style** | Creează stilul pe baza câmpului ales și îl salvează în baza de date cu un nume |
| **Load existing style** | Aplică un stil deja salvat în baza de date (dacă sunt mai multe, se alege unul); dacă nu există niciunul, funcționează ca **Use temporary style** |
| **Use temporary style** | Creează stilul pe baza câmpului ales fără a-l salva în baza de date |
| **Single symbol (outline only)** | Desenează doar conturul geometriilor, fără umplere |

Cu **Save new style** și **Use temporary style** se alege apoi câmpul de categorizare (fereastra **Select Categorization Field**, în engleză): **Stratigraphic Definition** (definiție stratigrafică), **SU Type** (tip US) sau **Interpretive Definition** (definiție interpretativă); fiecare valoare a câmpului primește o culoare proprie. Apar doar câmpurile prezente în strat.

Începând cu 5.13.18-alpha, stilul ales (și câmpul de categorizare) este respectat și cu bazele de date SQLite, atât pentru US, cât și pentru USM; înainte harta apărea întotdeauna cu o culoare pentru fiecare US.

## Stilizarea Straturilor

### Fișiere QML

PyArchInit include stiluri predefinite în format QML:
```
pyarchinit/styles/
├── pyunitastratigrafiche.qml
├── pyunitastratigrafiche_usm.qml
├── pyarchinit_quote.qml
└── ...
```

### Aplicarea Stilului

1. Selectați stratul în legendă
2. Clic dreapta → **Proprietăți**
3. Tab-ul **Stil**
4. **Încarcă stil** → selectați QML

### Personalizare

Stilurile pot fi personalizate pentru:
- Culori bazate pe tipul US
- Etichete cu numărul US
- Transparență
- Margini și umpleri

## Cote și Măsurători

### Stratul de Cote

Stratul `pyarchinit_quote` stochează:
- Coordonate X, Y
- Cota Z (absolută)
- Tipul punctului de cotă
- US de referință
- Zona de referință

### Calculul Automat al Cotelor

Din Fișa US, cotele min/max sunt calculate:
1. Interogare puncte de cotă asociate US-ului
2. Extragerea valorii minime și maxime
3. Afișare în raport

### Introducerea Cotelor

1. Stratul de cote în mod editare
2. Desenați un punct pe hartă
3. Completați atributele:
   - `sito_q`
   - `area_q`
   - `us_q`
   - `quota`
   - `unita_misura_q`

## Segmentarea Automată SAM

### Ce este SAM?

**SAM (Segment Anything Model)** este un model de inteligență artificială dezvoltat de Meta pentru segmentarea automată a imaginilor. PyArchInit îl integrează pentru:
- Digitizarea automată a pietrelor/elementelor
- Segmentarea ortofotografiilor
- Accelerarea releveelor

### Accesarea Funcției

1. **PyArchInit** → **Segmentare SAM**
2. Sau din bara de instrumente: pictograma **SAM**

### Interfața SAM

```
+--------------------------------------------------+
|        Segmentare Pietre SAM                      |
+--------------------------------------------------+
| Intrare:                                          |
|   Strat Raster: [ComboBox ortofoto]              |
+--------------------------------------------------+
| Strat Țintă:                                     |
|   [o] pyunitastratigrafiche                      |
|   [ ] pyunitastratigrafiche_usm                  |
+--------------------------------------------------+
| Atribute Implicite:                               |
|   Sit (sito): [câmp automat]                     |
|   Zonă: [intrare zonă]                           |
|   Index Stratigrafic: [1-10]                     |
|   Tip US: [piatră|strat|acumulare|tăietură]     |
+--------------------------------------------------+
| Mod Segmentare:                                   |
|   [o] Automat (detectează toate pietrele)        |
|   [ ] Mod clic (clic pe fiecare piatră)         |
|   [ ] Mod casetă (desenează dreptunghi)          |
|   [ ] Mod poligon (desenează liber)              |
|   [ ] Din strat (folosește poligon existent)     |
+--------------------------------------------------+
| Model:                                            |
|   [ComboBox model]                               |
|   Cheie API: [******]                            |
+--------------------------------------------------+
|        [Start Segmentare]  [Anulare]              |
+--------------------------------------------------+
```

### Moduri de Segmentare

#### 1. Mod Automat
- Segmentează automat toate obiectele vizibile
- Ideal pentru zone cu multe pietre
- Necesită ortofotografie de bună calitate

#### 2. Mod Clic
- Clic pe fiecare obiect de segmentat
- Clic dreapta sau Enter pentru finalizare
- Escape pentru anulare
- Mai precis pentru obiecte specifice

#### 3. Mod Casetă
- Desenați un dreptunghi pe zonă
- Segmentează doar zona selectată
- Util pentru zone delimitate

#### 4. Mod Poligon
- Desenați un poligon liber
- Clic pentru adăugare vârfuri
- Clic dreapta pentru finalizare
- Pentru zone neregulate

#### 5. Mod Din Strat
- Folosiți un poligon existent ca mască
- Selectați stratul de poligon
- Segmentează doar în interiorul poligonului

### Modele Disponibile

| Model | Tip | Cerințe | Calitate |
|-------|-----|---------|----------|
| Replicate SAM-2 | Cloud API | Cheie API | Excelentă |
| Roboflow SAM-3 | Cloud API | Cheie API | Excelentă + Prompt Text |
| SAM vit_b | Local | 375MB VRAM | Bună |
| SAM vit_l | Local | 1.2GB VRAM | Foarte bună |
| SAM vit_h | Local | 2.5GB VRAM | Excelentă |
| OpenCV | Local | Niciunul | De bază |

### SAM-3 cu Prompt Text

Versiunea SAM-3 (Roboflow) suportă **prompturi text**:
- „stones" - pietre
- „pottery fragments" - fragmente de ceramică
- „bones" - oase
- Orice descriere text

### Configurarea API

#### API Replicate (SAM-2)
1. Înregistrare la [replicate.com](https://replicate.com)
2. Obținerea cheii API
3. Introducerea în configurare

#### API Roboflow (SAM-3)
1. Înregistrare la [roboflow.com](https://roboflow.com)
2. Obținerea cheii API
3. Introducerea în configurare

### Instalarea SAM Local

Pentru utilizare locală fără API:
```bash
# Crearea mediului virtual
cd ~/pyarchinit/bin
python -m venv sam_venv

# Activarea mediului
source sam_venv/bin/activate

# Instalarea dependențelor
pip install segment-anything torch torchvision

# Descărcarea modelelor (opțional)
# vit_b: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
# vit_l: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth
# vit_h: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
```

### Flux de Lucru SAM

1. **Pregătire**
   - Încărcați ortofotografia ca strat raster
   - Verificați sistemul de referință al coordonatelor
   - Pregătiți stratul țintă

2. **Configurare**
   - Selectați rasterul de intrare
   - Setați atributele implicite
   - Alegeți modul și modelul

3. **Execuție**
   - Faceți clic pe „Start Segmentare"
   - Așteptați procesarea
   - Verificați rezultatele

4. **Post-procesare**
   - Verificați poligoanele generate
   - Atribuiți numerele US
   - Corectați eventualele erori

## Integrare Cartografică

### Export Date GIS

Din Fișa US, tab-ul Hartă:
- **Export GeoPackage**: Strat ca GPKG
- **Export Shapefile**: Strat ca SHP
- **Export GeoJSON**: Strat ca JSON

### Import Date GIS

Import geometrii existente:
1. Încărcați stratul în QGIS
2. Selectați entitățile
3. Folosiți funcția de import

### Geoprocesare

Operații spațiale disponibile:
- Buffer
- Intersecție
- Uniune
- Diferență
- Centroizi

## Bune Practici

### 1. Ortofotografii

- Rezoluție minimă: 1-2 cm/pixel
- Format: GeoTIFF georeferențiat
- Sistem de referință: consistent cu proiectul

### 2. Digitizare

- Folosiți snap pentru precizie
- Verificați topologia
- Mențineți consistența atributelor

### 3. Segmentare SAM

- Ortofotografie de înaltă calitate
- Iluminare uniformă
- Contrast adecvat obiect/fundal
- Post-verificarea este întotdeauna necesară

### 4. Organizarea Straturilor

- Grupare pe tip
- Folosiți stiluri consistente
- Mențineți ordinea în legendă

## Depanare

### Straturile Nu Sunt Afișate

**Cauze posibile**:
- Extindere greșită
- Sistem de referință diferit
- Filtru activ

**Soluții**:
- Zoom la Strat
- Verificați CRS
- Eliminați filtrele

### SAM Nu Funcționează

**Cauze posibile**:
- Cheie API invalidă
- Raster negeoreferențiat
- Modelul local neinstalat

**Soluții**:
- Verificați cheia API
- Verificați georeferențierea
- Instalați modelul

### Geometrii Corupte

**Cauze posibile**:
- Erori de digitizare
- Import problematic

**Soluții**:
- Folosiți „Reparare Geometrii"
- Redesenați elementul

### Strat încărcat, dar geometrii invizibile (SQLite)

**Simptom**:
- Un strat pyArchInit dintr-o bază de date SQLite/SpatiaLite (ex. US `pyunitastratigrafiche`, USM, materiale, US negative) se încarcă și tabelul de atribute afișează înregistrările, dar pe hartă nu se desenează nimic, iar „Zoom la Strat" nu funcționează

**Cauză**:
- Indexul spațial (R*Tree) al stratului nu a fost întreținut: triggerele sale s-au pierdut când un tabel a fost recreat (ex. de scripturi vechi de actualizare a schemei) sau datele au fost importate ocolindu-le
- QGIS alege entitățile de desenat prin acest index, deci ele rămân invizibile
- Au fost afectate și bazele de date create din șablonul SQLite între octombrie 2025 și septembrie 2026

**Soluție (automată)**:
- La conectarea la o bază de date SQLite, pyArchInit verifică toți indecșii spațiali (câteva clipe; nu se scrie nimic dacă baza de date este intactă) și îi reconstruiește automat pe cei deteriorați
- Începând cu versiunea 5.13.16-alpha, aceeași verificare repară și **vederile spațiale** (`pyarchinit_us_view`, `pyarchinit_quote_view`, structuri, materiale, vederile UT etc.):
  - fiecare vedere este legată de ROWID-ul tabelului său de geometrie
  - înregistrările vederilor care nu mai există sunt eliminate
  - vederile standard lipsă sunt recreate
  - vederile UT sunt înregistrate ca vederi spațiale
  - tabelele de geometrie fără index spațial primesc unul: necesar când GDAL-ul inclus în QGIS nu are funcțiile SpatiaLite (ex. QGIS pe macOS), unde fără index acele straturi nu desenau nimic
- Înainte de a modifica ceva, salvează O SINGURĂ copie de siguranță lângă baza de date: `<baza_de_date>.sqlite.pre_spatial_index_repair_<data-ora UTC>`
- Rezultatul este scris în panoul de mesaje jurnal al QGIS (View → Panels → Log Messages), fila „PyArchInit"

**Ce trebuie făcut**:
- Nimic de pornit manual: verificarea rulează automat la PRIMA conectare la fiecare bază de date în fiecare sesiune QGIS (deci după actualizarea pluginului sau după repornirea QGIS)
- Dacă straturile erau deja încărcate, eliminați-le și adăugați-le din nou (sau redeschideți proiectul) după reparare
- Dacă jurnalul „PyArchInit" raportează că un index NU a putut fi reparat (ex. SpatiaLite nu poate fi încărcat), remediați cauza și reporniți QGIS: verificarea se repetă doar într-o sesiune nouă
- Fișierul de siguranță poate fi șters după verificarea straturilor
- Pentru a repeta verificarea (ex. după restaurarea unei copii de siguranță), reporniți QGIS
- Notă: în `inventario_materiali_view` punctul șantierului este repetat pentru fiecare material, deci „Identify" pe acel punct afișează unul dintre materiale

## Referințe

### Fișiere Sursă
- `modules/gis/pyarchinit_pyqgis.py` - Integrare GIS
- `tabs/Sam_Segmentation_Dialog.py` - Dialog SAM
- `modules/gis/sam_map_tools.py` - Instrumente hartă SAM

### Straturi
- `pyunitastratigrafiche` - US depozit
- `pyunitastratigrafiche_usm` - US zidărie
- `pyarchinit_quote` - Cote

---

## Tutorial Video

### Integrare GIS
`[Substituent: video_gis_integration.mp4]`

**Conținut**:
- Straturi predefinite
- Vizualizarea US
- Stilizare și etichete
- Export cartografic

**Durată estimată**: 15-18 minute

### Segmentare SAM
`[Substituent: video_sam_segmentation.mp4]`

**Conținut**:
- Configurarea SAM
- Moduri de segmentare
- Post-procesare
- Bune practici

**Durată estimată**: 12-15 minute

---

*Ultima actualizare: ianuarie 2026*

---

## Animație Interactivă

Explorați animația interactivă pentru a afla mai multe despre acest subiect.

[Deschideți Animația Interactivă](../../animations/pyarchinit_image_classification_animation.html)
