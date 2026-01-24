# Tutorial 21: Fitxa UT - Unitats Topogràfiques

## Introducció

La **Fitxa UT** (Unitats Topogràfiques) és el mòdul de PyArchInit dedicat a la documentació de les prospeccions arqueològiques de superfície. Permet registrar les dades relatives a les concentracions de materials, anomalies del terreny i llocs identificats durant les prospeccions.

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
2. Seleccionar **Fitxa UT**

### Via Barra d'Eines
1. Localitzar la barra d'eines PyArchInit
2. Fer clic a la icona **UT**

---

## Panoràmica de la Interfície

La fitxa està organitzada en diverses pestanyes per documentar tots els aspectes de la prospecció.

### Pestanyes Principals

| # | Pestanya | Descripció |
|---|----------|------------|
| 1 | Identificació | Projecte, Nr. UT, Localització |
| 2 | Descripció | Definició, descripció, interpretació |
| 3 | Dades UT | Condicions, metodologia, dates |
| 4 | Anàlisi | Potencial i risc arqueològic |

---

## Camps Identificatius

### Projecte

**Camp**: `comboBox_progetto`
**Base de dades**: `progetto`

Nom del projecte de prospecció.

### Número UT

**Camp**: `comboBox_nr_ut`
**Base de dades**: `nr_ut`

Número progressiu de la Unitat Topogràfica.

### UT Literal

**Camp**: `lineEdit_ut_letterale`
**Base de dades**: `ut_letterale`

Sufix alfabètic opcional (p. ex. UT 15a, 15b).

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

---

## Camps Descriptius

### Definició UT ⭐ NOU

**Camp**: `comboBox_def_ut`
**Base de dades**: `def_ut`
**Tesaurus**: Codi 12.7

Classificació tipològica de la UT. Els valors es carreguen del tesaurus i es tradueixen automàticament a l'idioma actual.

**Valors estàndard:**
| Codi | Català | Italià |
|------|--------|--------|
| scatter | Dispersió de materials | Area di dispersione materiali |
| site | Jaciment arqueològic | Sito archeologico |
| anomaly | Anomalia del terreny | Anomalia del terreno |
| structure | Estructura aflorant | Struttura affiorante |
| concentration | Concentració de troballes | Concentrazione reperti |
| traces | Traces antròpiques | Tracce antropiche |
| findspot | Troballa esporàdica | Rinvenimento sporadico |
| negative | Resultat negatiu | Esito negativo |

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

## Camps Tesaurus Survey ⭐ NOU

Els camps següents utilitzen el sistema de tesaurus per garantir terminologia estandarditzada traduïda a 7 idiomes (IT, EN, DE, ES, FR, AR, CA).

### Tipus de Survey (12.1)

**Camp**: `comboBox_survey_type`
**Base de dades**: `survey_type`

| Codi | Català | Descripció |
|------|--------|------------|
| intensive | Prospecció intensiva | Batuda sistemàtica intensiva |
| extensive | Prospecció extensiva | Reconeixement extensiu |
| targeted | Prospecció dirigida | Investigació d'àrees específiques |
| random | Mostreig aleatori | Metodologia de mostreig aleatori |

### Cobertura Vegetal (12.2)

**Camp**: `comboBox_vegetation_coverage`
**Base de dades**: `vegetation_coverage`

| Codi | Català | Descripció |
|------|--------|------------|
| none | Sense vegetació | Sòl nu |
| sparse | Vegetació escassa | Cobertura < 25% |
| moderate | Vegetació moderada | Cobertura 25-50% |
| dense | Vegetació densa | Cobertura 50-75% |
| very_dense | Vegetació molt densa | Cobertura > 75% |

### Mètode GPS (12.3)

**Camp**: `comboBox_gps_method`
**Base de dades**: `gps_method`

| Codi | Català | Descripció |
|------|--------|------------|
| handheld | GPS de mà | Dispositiu GPS portàtil |
| dgps | GPS diferencial | DGPS amb estació base |
| rtk | GPS RTK | Cinemàtic en temps real |
| total_station | Estació total | Aixecament amb estació total |

### Condició de Superfície (12.4)

**Camp**: `comboBox_surface_condition`
**Base de dades**: `surface_condition`

| Codi | Català | Descripció |
|------|--------|------------|
| ploughed | Llaurada | Camp recentment llaurada |
| stubble | Rostoll | Presència de rostoll |
| pasture | Pastura | Prat/pastura |
| woodland | Bosc | Àrea boscosa |
| urban | Urbà | Àrea urbana/edificada |

### Accessibilitat (12.5)

**Camp**: `comboBox_accessibility`
**Base de dades**: `accessibility`

| Codi | Català | Descripció |
|------|--------|------------|
| easy | Accés fàcil | Sense restriccions |
| moderate_access | Accés moderat | Algunes dificultats |
| difficult | Accés difícil | Problemes significatius |
| restricted | Accés restringit | Només amb permís |

### Condicions Meteorològiques (12.6)

**Camp**: `comboBox_weather_conditions`
**Base de dades**: `weather_conditions`

| Codi | Català | Descripció |
|------|--------|------------|
| sunny | Assolellat | Clar i assolellat |
| cloudy | Ennuvolat | Condicions nuvoloses |
| rainy | Plujós | Pluja durant prospecció |
| windy | Ventós | Vents forts |

---

## Dades Ambientals

### Percentatge de Visibilitat

**Camp**: `spinBox_visibility_percent`
**Base de dades**: `visibility_percent`

Percentatge de visibilitat del sòl (0-100%). Valor numèric.

### Pendent del Terreny

**Camp**: `lineEdit_andamento_terreno_pendenza`
**Base de dades**: `andamento_terreno_pendenza`

Morfologia i pendent del terreny.

### Ús del Sòl

**Camp**: `lineEdit_utilizzo_suolo_vegetazione`
**Base de dades**: `utilizzo_suolo_vegetazione`

Ús del sòl en el moment de la prospecció.

---

## Dades Materials

### Dimensions UT

**Camp**: `lineEdit_dimensioni_ut`
**Base de dades**: `dimensioni_ut`

Extensió de l'àrea en m².

### Troballes per m²

**Camp**: `lineEdit_rep_per_mq`
**Base de dades**: `rep_per_mq`

Densitat de materials per metre quadrat.

### Troballes Datants

**Camp**: `lineEdit_rep_datanti`
**Base de dades**: `rep_datanti`

Descripció de materials diagnòstics.

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

## Pestanya Anàlisi ⭐ NOU

La pestanya **Anàlisi** proporciona eines avançades per al càlcul automàtic del potencial i risc arqueològic.

### Potencial Arqueològic

El sistema calcula una puntuació de 0 a 100 basant-se en:

| Factor | Pes | Descripció |
|--------|-----|------------|
| Definició UT | 30% | Tipus d'evidència arqueològica |
| Període històric | 25% | Cronologia dels materials |
| Densitat de troballes | 20% | Materials per m² |
| Condició superfície | 15% | Visibilitat i accessibilitat |
| Documentació | 10% | Qualitat de la documentació |

**Visualització:**
- Barra de progrés acolorida (verd = alt, groc = mitjà, vermell = baix)
- Taula detallada de factors amb puntuacions individuals
- Text narratiu automàtic amb interpretació

### Risc Arqueològic

Avalua el risc d'impacte/pèrdua del patrimoni:

| Factor | Pes | Descripció |
|--------|-----|------------|
| Accessibilitat | 25% | Facilitat d'accés a l'àrea |
| Ús del sòl | 25% | Activitats agrícoles/constructives |
| Restriccions existents | 20% | Proteccions legals |
| Investigacions prèvies | 15% | Estat del coneixement |
| Visibilitat | 15% | Exposició del lloc |

### Generació de Mapa de Calor

El botó **Generar Mapa de Calor** crea capes ràster que mostren:
- **Mapa de Potencial**: distribució espacial del potencial arqueològic
- **Mapa de Risc**: mapa de risc d'impacte

**Mètodes disponibles:**
- Estimació de Densitat Kernel (KDE)
- Ponderació per Distància Inversa (IDW)
- Veí Natural

---

## Exportació PDF ⭐ MILLORAT

### Fitxa UT Estàndard

Exporta la fitxa UT completa amb tots els camps emplenats.

### Informe d'Anàlisi UT

Genera un informe PDF que inclou:

1. **Dades d'identificació UT**
2. **Secció Potencial Arqueològic**
   - Puntuació amb indicador gràfic
   - Text narratiu descriptiu
   - Taula de factors amb contribucions
   - Imatge del mapa de potencial (si s'ha generat)
3. **Secció Risc Arqueològic**
   - Puntuació amb indicador gràfic
   - Text narratiu amb recomanacions
   - Taula de factors amb contribucions
   - Imatge del mapa de risc (si s'ha generat)
4. **Secció Metodologia**
   - Descripció dels algorismes utilitzats
   - Notes sobre ponderació dels factors

L'informe està disponible en els 7 idiomes suportats.

---

## Flux de Treball Operatiu

### Registre de Nova UT

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

5. **Descripció** (usant tesaurus)
   ```
   Definició: Concentració de troballes (del tesaurus)
   Descripció: Àrea el·líptica de ca. 50x30 m
   amb concentració de fragments ceràmics
   i material constructiu sobre vessant
   exposat al sud...
   ```

6. **Dades survey** (usant tesaurus)
   ```
   Tipus Survey: Prospecció intensiva
   Cobertura Vegetal: Escassa
   Mètode GPS: GPS diferencial
   Condició Superfície: Llaurada
   Accessibilitat: Accés fàcil
   Condicions Meteo: Assolellat
   Visibilitat: 80%
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

8. **Anàlisi** (pestanya Anàlisi)
   - Verificar puntuació Potencial
   - Verificar puntuació Risc
   - Generar Mapa de Calor si cal

9. **Desament**
   - Clic a "Save"

---

## Integració GIS

La fitxa UT està estretament integrada amb QGIS:

- **Capa UT**: visualització de geometries
- **Atributs connectats**: dades des de la fitxa
- **Selecció des de mapa**: clic sobre geometria obre fitxa
- **Mapa de calor com a capa**: els mapes generats es desen com a capes ràster

---

## Bones Pràctiques

### Ús del Tesaurus

- Preferir sempre valors del tesaurus per coherència
- Els valors es tradueixen automàticament a l'idioma de l'usuari
- Per a nous valors, afegir-los primer al tesaurus

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

### Anàlisi

- Verificar sempre les puntuacions calculades
- Generar mapes de calor per a projectes complets
- Exportar informes per a documentació

---

## Codis Tesaurus UT

| Codi | Camp | Descripció |
|------|------|------------|
| 12.1 | survey_type | Tipus de survey |
| 12.2 | vegetation_coverage | Cobertura vegetal |
| 12.3 | gps_method | Mètode GPS |
| 12.4 | surface_condition | Condició de superfície |
| 12.5 | accessibility | Accessibilitat |
| 12.6 | weather_conditions | Condicions meteorològiques |
| 12.7 | def_ut | Definició UT |

---

## Resolució de Problemes

### Problema: Comboboxes buits

**Causa**: Entrades del tesaurus no presents a la base de dades.

**Solució**:
1. Actualitzar base de dades via "Update database"
2. Verificar que la taula `pyarchinit_thesaurus_sigle` contingui entrades per a `ut_table`
3. Comprovar codi d'idioma a la configuració

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

### Problema: Mapa de calor no generat

**Causa**: Dades insuficients o error de càlcul.

**Solució**:
1. Verificar que existeixin almenys 3 UTs amb dades completes
2. Comprovar que les geometries siguin vàlides
3. Verificar espai de disc disponible

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
- **PDF Anàlisi**: `modules/utility/pyarchinit_exp_UT_analysis_pdf.py`
- **Calculador Potencial**: `modules/analysis/ut_potential.py`
- **Calculador Risc**: `modules/analysis/ut_risk.py`
- **Generador Mapa Calor**: `modules/analysis/ut_heatmap_generator.py`

---

## Vídeo Tutorial

### Documentació Prospeccions
**Durada**: 15-18 minuts
- Registre UT
- Dades survey amb tesaurus
- Geolocalització

[Placeholder vídeo: video_ut_survey.mp4]

### Anàlisi de Potencial i Risc
**Durada**: 10-12 minuts
- Càlcul automàtic de puntuacions
- Interpretació de resultats
- Generació de mapa de calor

[Placeholder vídeo: video_ut_analysis.mp4]

### Exportació d'Informes PDF
**Durada**: 8-10 minuts
- Fitxa UT estàndard
- Informe d'anàlisi amb mapes
- Personalització de sortida

[Placeholder vídeo: video_ut_pdf.mp4]

---

*Última actualització: Gener 2026*
*PyArchInit v4.9.68 - Sistema de Gestió de Dades Arqueològiques*
