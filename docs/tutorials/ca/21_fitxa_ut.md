# Tutorial 21: Fitxa UT - Unitats Topogràfiques

## Introducció

La **Fitxa UT** (Unitats Topogràfiques) és el mòdul de PyArchInit dedicat a la documentació de les prospeccions arqueològiques de superfície (survey). Permet registrar les dades relatives a les concentracions de materials, anomalies del terreny i llocs identificats durant les prospeccions.

### Conceptes Bàsics

**Unitat Topogràfica (UT):**
- Àrea delimitada amb característiques arqueològiques homogènies
- Identificada durant prospecció de superfície
- Definida per concentració de materials o anomalies visibles

**Prospecció (Survey):**
- Prospecció sistemàtica del territori
- Recollida de dades sobre presència antròpica antiga
- Documentació sense excavació

---

## Accés a la Fitxa

### Via Menú
1. Menú **PyArchInit** a la barra de menús de QGIS
2. Seleccionar **Fitxa UT** (o **TU form**)

### Via Barra d'Eines
1. Localitzar la barra d'eines PyArchInit
2. Fer clic a la icona **UT**

---

## Panoràmica de la Interfície

La fitxa és rica en camps per documentar tots els aspectes de la prospecció.

### Àrees Principals

| # | Àrea | Descripció |
|---|------|------------|
| 1 | Toolbar DBMS | Navegació, cerca, desament |
| 2 | Camps Identificatius | Projecte, Nr. UT |
| 3 | Localització | Dades geogràfiques i administratives |
| 4 | Descripció | Definició, descripció, interpretació |
| 5 | Dades Survey | Condicions, metodologia |
| 6 | Cronologia | Períodes i datacions |

---

## Camps Identificatius

### Projecte

**Camp**: `lineEdit_progetto`
**Base de dades**: `progetto`

Nom del projecte de prospecció.

### Número UT

**Camp**: `lineEdit_nr_ut`
**Base de dades**: `nr_ut`

Número progressiu de la Unitat Topogràfica.

### UT Literal

**Camp**: `lineEdit_ut_letterale`
**Base de dades**: `ut_letterale`

Eventual sufix alfabètic (p. ex. UT 15a, 15b).

---

## Camps Localització

### Dades Administratives

| Camp | Base de dades | Descripció |
|------|---------------|------------|
| País | `nazione` | Estat |
| Regió | `regione` | Regió administrativa |
| Província | `provincia` | Província |
| Municipi | `comune` | Municipi |
| Fracció | `frazione` | Fracció/localitat |
| Localitat | `localita` | Topònim local |
| Adreça | `indirizzo` | Via/carretera |
| Nr. | `nr_civico` | Número |

### Dades Cartogràfiques

| Camp | Base de dades | Descripció |
|------|---------------|------------|
| Carta IGM | `carta_topo_igm` | Full IGM |
| Carta CTR | `carta_ctr` | Element CTR |
| Full cadastral | `foglio_catastale` | Referència cadastre |

### Coordenades

| Camp | Base de dades | Descripció |
|------|---------------|------------|
| Coord. geogràfiques | `coord_geografiche` | Lat/Long |
| Coord. planes | `coord_piane` | UTM/Gauss-Boaga |
| Cota | `quota` | Altitud s.n.m. |
| Precisió coord. | `coordinate_precision` | Exactitud GPS |
| Mètode GPS | `gps_method` | Tipus mesurament |

---

## Camps Descriptius

### Definició UT

**Camp**: `comboBox_def_ut`
**Base de dades**: `def_ut`

Classificació tipològica de la UT.

**Valors:**
- Concentració materials
- Àrea de fragments
- Anomalia del terreny
- Estructura aflorant
- Lloc arqueològic

### Descripció UT

**Camp**: `textEdit_descrizione`
**Base de dades**: `descrizione_ut`

Descripció detallada de la Unitat Topogràfica.

**Continguts:**
- Extensió i forma de l'àrea
- Densitat dels materials
- Característiques del terreny
- Visibilitat i condicions

### Interpretació UT

**Camp**: `textEdit_interpretazione`
**Base de dades**: `interpretazione_ut`

Interpretació funcional/històrica.

---

## Dades Ambientals

### Pendent Terreny

**Camp**: `comboBox_terreno`
**Base de dades**: `andamento_terreno_pendenza`

Morfologia i pendent.

**Valors:**
- Pla
- Pendent lleu
- Pendent mitjana
- Pendent fort
- Terrassat

### Ús del Sòl

**Camp**: `comboBox_suolo`
**Base de dades**: `utilizzo_suolo_vegetazione`

Ús del sòl en el moment de la prospecció.

**Valors:**
- Conreu
- Prat/pastura
- Vinya
- Oliverar
- Erm
- Bosc
- Urbà

### Descripció Sòl

**Camp**: `textEdit_suolo`
**Base de dades**: `descrizione_empirica_suolo`

Característiques pedològiques observades.

### Descripció Lloc

**Camp**: `textEdit_luogo`
**Base de dades**: `descrizione_luogo`

Context paisatgístic.

---

## Dades Survey

### Mètode Prospecció

**Camp**: `comboBox_metodo`
**Base de dades**: `metodo_rilievo_e_ricognizione`

Metodologia adoptada.

**Valors:**
- Prospecció sistemàtica
- Prospecció extensiva
- Prospecció dirigida
- Control senyalització

### Tipus Survey

**Camp**: `comboBox_survey_type`
**Base de dades**: `survey_type`

Tipologia de prospecció.

### Visibilitat

**Camp**: `spinBox_visibility`
**Base de dades**: `visibility_percent`

Percentatge de visibilitat del sòl (0-100%).

### Cobertura Vegetació

**Camp**: `comboBox_vegetation`
**Base de dades**: `vegetation_coverage`

Grau de cobertura vegetal.

### Condició Superfície

**Camp**: `comboBox_surface`
**Base de dades**: `surface_condition`

Estat de la superfície.

**Valors:**
- Llaurada de fresc
- Llaurada no fresada
- Herba baixa
- Herba alta
- Rostoll

### Accessibilitat

**Camp**: `comboBox_accessibility`
**Base de dades**: `accessibility`

Facilitat d'accés a l'àrea.

### Data

**Camp**: `dateEdit_data`
**Base de dades**: `data`

Data de la prospecció.

### Hora/Meteo

**Camp**: `lineEdit_meteo`
**Base de dades**: `ora_meteo`

Condicions meteo i hora.

### Responsable

**Camp**: `comboBox_responsabile`
**Base de dades**: `responsabile`

Responsable de la prospecció.

### Equip

**Camp**: `textEdit_team`
**Base de dades**: `team_members`

Components del grup.

---

## Dades Materials

### Dimensions UT

**Camp**: `lineEdit_dimensioni`
**Base de dades**: `dimensioni_ut`

Extensió en m².

### Troballes per m²

**Camp**: `lineEdit_rep_mq`
**Base de dades**: `rep_per_mq`

Densitat materials.

### Troballes Datants

**Camp**: `textEdit_rep_datanti`
**Base de dades**: `rep_datanti`

Descripció materials diagnòstics.

---

## Cronologia

### Període I

| Camp | Base de dades |
|------|---------------|
| Període I | `periodo_I` |
| Datació I | `datazione_I` |
| Interpretació I | `interpretazione_I` |

### Període II

| Camp | Base de dades |
|------|---------------|
| Període II | `periodo_II` |
| Datació II | `datazione_II` |
| Interpretació II | `interpretazione_II` |

---

## Altres Camps

### Geometria

**Camp**: `comboBox_geometria`
**Base de dades**: `geometria`

Forma de la UT.

### Bibliografia

**Camp**: `textEdit_bibliografia`
**Base de dades**: `bibliografia`

Referències bibliogràfiques.

### Documentació

**Camp**: `textEdit_documentazione`
**Base de dades**: `documentazione`

Documentació produïda (fotos, dibuixos).

### Documentació Foto

**Camp**: `textEdit_photo_doc`
**Base de dades**: `photo_documentation`

Llistat documentació fotogràfica.

### Ens Tutela/Vincles

**Camp**: `textEdit_vincoli`
**Base de dades**: `enti_tutela_vincoli`

Vincles i subjectes de tutela.

### Investigacions Preliminars

**Camp**: `textEdit_indagini`
**Base de dades**: `indagini_preliminari`

Eventuals investigacions ja executades.

---

## Flux de Treball Operatiu

### Registre Nova UT

1. **Obertura fitxa**
   - Via menú o barra d'eines

2. **Nou registre**
   - Clic a "New Record"

3. **Dades identificatives**
   ```
   Projecte: Survey Vall del Llobregat 2024
   Nr. UT: 25
   ```

4. **Localització**
   ```
   Regió: Catalunya
   Província: Barcelona
   Municipi: Martorell
   Localitat: Turó Alt
   Coord.: 41.4567 N, 1.9234 E
   Cota: 125 m
   ```

5. **Descripció**
   ```
   Definició: Concentració materials
   Descripció: Àrea el·líptica de ca. 50x30 m
   amb concentració de fragments ceràmics
   i material constructiu sobre vessant
   exposat al sud...
   ```

6. **Dades survey**
   ```
   Mètode: Prospecció sistemàtica
   Visibilitat: 80%
   Condició: Llaurada de fresc
   Data: 15/04/2024
   Responsable: Equip A
   ```

7. **Materials i cronologia**
   ```
   Dimensions: 1500 m²
   Tro/m²: 5-8
   Troballes datants: Ceràmica comuna,
   sigil·lata itàlica, material constructiu

   Període I: Romà
   Datació I: I-II s. d.C.
   Interpretació I: Vil·la rústica
   ```

8. **Desament**
   - Clic a "Save"

---

## Integració GIS

La fitxa UT està estretament integrada amb QGIS:

- **Capa UT**: visualització geometries
- **Atributs connectats**: dades des de la fitxa
- **Selecció des de mapa**: clic sobre geometria obre fitxa

---

## Export PDF

La fitxa suporta l'exportació en PDF per a:
- Fitxes UT individuals
- Llistats per projecte
- Informes de survey

---

## Bones Pràctiques

### Nomenclatura

- Numeració progressiva per projecte
- Usar sufixos per a subdivisions
- Documentar les convencions

### Geolocalització

- Usar GPS diferencial quan sigui possible
- Indicar sempre el mètode i la precisió
- Verificar les coordenades sobre mapa

### Documentació

- Fotografiar cada UT
- Produir esbossos planimètrics
- Registrar condicions de visibilitat

### Materials

- Recollir mostres diagnòstiques
- Estimar densitat per àrea
- Documentar distribució espacial

---

## Resolució de Problemes

### Problema: Coordenades no vàlides

**Causa**: Format erroni o sistema de referència.

**Solució**:
1. Verificar el format (DD o DMS)
2. Controlar el sistema de referència
3. Usar l'eina de conversió QGIS

### Problema: UT no visible al mapa

**Causa**: Geometria no associada.

**Solució**:
1. Verificar que existeixi la capa UT
2. Controlar que el registre tingui geometria
3. Verificar la projecció de la capa

---

## Referències

### Base de Dades

- **Taula**: `ut_table`
- **Classe mapper**: `UT`
- **ID**: `id_ut`

### Fitxers Font

- **UI**: `gui/ui/UT_ui.ui`
- **Controller**: `tabs/UT.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_UTsheet_pdf.py`

---

## Vídeo Tutorial

### Documentació Prospeccions
**Durada**: 15-18 minuts
- Registre UT
- Dades survey
- Geolocalització

[Placeholder vídeo: video_ut_survey.mp4]

### Integració GIS Survey
**Durada**: 10-12 minuts
- Capes i atributs
- Visualització resultats
- Anàlisi espacial

[Placeholder vídeo: video_ut_gis.mp4]

---

*Última actualització: Gener 2026*
*PyArchInit - Sistema de Gestió de Dades Arqueològiques*
