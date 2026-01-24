# Tutorial 21: Fitxa UT - Unitats Topogràfiques

## Introducció

La **Fitxa UT** (Unitats Topogràfiques) és el mòdul de PyArchInit dedicat a la documentació de les prospeccions arqueològiques de superfície (survey). Permet registrar les dades relatives a les concentracions de materials, anomalies del terreny i jaciments identificats durant les prospeccions.

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

La fitxa està organitzada en diverses pestanyes per documentar tots els aspectes de la prospecció.

### Pestanyes Principals

| # | Pestanya | Descripció |
|---|----------|------------|
| 1 | Identificació | Projecte, Nr. UT, Localització |
| 2 | Descripció | Definició, descripció, interpretació |
| 3 | Dades UT | Condicions, metodologia, dates |
| 4 | Anàlisi | Potencial i risc arqueològic |

### Barra d'Eines Principal

| Botó | Funció |
|------|--------|
| ⏮ Primer | Anar al primer registre |
| ◀ Anterior | Registre anterior |
| ▶ Següent | Registre següent |
| ⏭ Últim | Anar a l'últim registre |
| 🔍 Cerca | Cerca avançada |
| 💾 Desar | Desar registre |
| 🗑 Eliminar | Eliminar registre |
| 📄 PDF | Exportar fitxa PDF |
| 📋 **Llista PDF** | Exportar llistat d'UT en PDF |
| 📦 **Export GNA** | Exportar en format GNA |
| 🗺 Mostrar Capa | Visualitzar capa al mapa |

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
| Coord. geogràfiques | `coord_geografiche` | Lat/Long (format: lat, lon) |
| Coord. planes | `coord_piane` | UTM/Gauss-Boaga (format: x, y) |
| Cota | `quota` | Altitud s.n.m. |
| Precisió coord. | `coordinate_precision` | Exactitud GPS en metres |

**IMPORTANT**: Les coordenades s'utilitzen per a la generació dels mapes de calor. Almenys un entre `coord_geografiche` i `coord_piane` ha d'estar emplenat per a cada UT.

---

## Camps Descriptius

### Definició UT

**Camp**: `comboBox_def_ut`
**Base de dades**: `def_ut`
**Tesaurus**: Codi 12.7

Classificació tipològica de la UT. Els valors es carreguen del tesaurus i es tradueixen automàticament a l'idioma actual.

**Valors estàndard:**
| Codi | Català | Anglès |
|------|--------|--------|
| scatter | Dispersió de materials | Material scatter |
| site | Jaciment arqueològic | Archaeological site |
| anomaly | Anomalia del terreny | Terrain anomaly |
| structure | Estructura aflorant | Outcropping structure |
| concentration | Concentració de troballes | Finds concentration |
| traces | Traces antròpiques | Anthropic traces |
| findspot | Troballa esporàdica | Sporadic find |
| negative | Resultat negatiu | Negative result |

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

## Camps Survey amb Tesaurus

Els camps següents utilitzen el sistema de tesaurus per garantir terminologia estandarditzada i traduïda a 7 idiomes (IT, EN, DE, ES, FR, AR, CA).

### Tipus de Survey (12.1)

**Camp**: `comboBox_survey_type`
**Base de dades**: `survey_type`

| Codi | Català | Descripció |
|------|--------|------------|
| intensive | Prospecció intensiva | Prospecció sistemàtica intensiva |
| extensive | Prospecció extensiva | Prospecció per mostreig |
| targeted | Prospecció dirigida | Investigació d'àrees específiques |
| random | Mostreig aleatori | Metodologia aleatòria |

### Cobertura Vegetal (12.2)

**Camp**: `comboBox_vegetation_coverage`
**Base de dades**: `vegetation_coverage`

| Codi | Català | Descripció |
|------|--------|------------|
| none | Absent | Sòl nu |
| sparse | Escassa | Cobertura < 25% |
| moderate | Moderada | Cobertura 25-50% |
| dense | Densa | Cobertura 50-75% |
| very_dense | Molt densa | Cobertura > 75% |

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
| ploughed | Llaurada | Camp llaurada recentment |
| stubble | Rostoll | Presència de rostoll |
| pasture | Pastura | Terreny de pastura/prat |
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
| restricted | Accés restringit | Només amb autorització |

### Condicions Meteorològiques (12.6)

**Camp**: `comboBox_weather_conditions`
**Base de dades**: `weather_conditions`

| Codi | Català | Descripció |
|------|--------|------------|
| sunny | Assolellat | Temps clar |
| cloudy | Ennuvolat | Condicions nuvoloses |
| rainy | Plujós | Pluja durant prospecció |
| windy | Ventós | Vent fort |

---

## Dades Ambientals

### Percentatge de Visibilitat

**Camp**: `spinBox_visibility_percent`
**Base de dades**: `visibility_percent`

Percentatge de visibilitat del sòl (0-100%). Valor numèric important per al càlcul del potencial arqueològic.

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

Extensió en m2.

### Troballes per m2

**Camp**: `lineEdit_rep_per_mq`
**Base de dades**: `rep_per_mq`

Densitat de materials per metre quadrat. Valor crític per al càlcul del potencial.

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

## Pestanya Anàlisi - Potencial i Risc Arqueològic

La pestanya **Anàlisi** proporciona eines avançades per al càlcul automàtic del potencial i risc arqueològic.

### Potencial Arqueològic

El sistema calcula una puntuació de 0 a 100 basant-se en diversos factors ponderats:

| Factor | Pes | Descripció | Com es calcula |
|--------|-----|------------|----------------|
| Definició UT | 30% | Tipus d'evidència arqueològica | "site" = 100, "structure" = 90, "concentration" = 80, "scatter" = 60, etc. |
| Període històric | 25% | Cronologia dels materials | Períodes antics pesen més (Prehistòric = 90, Romà = 85, Medieval = 70, etc.) |
| Densitat troballes | 20% | Materials per m2 | >10/m2 = 100, 5-10 = 80, 2-5 = 60, <2 = 40 |
| Condició superfície | 15% | Visibilitat i accessibilitat | "ploughed" = 90, "stubble" = 70, "pasture" = 50, "woodland" = 30 |
| Documentació | 10% | Qualitat de la documentació | Presència fotos = +20, bibliografia = +30, investigacions = +50 |

**Classificació de la puntuació:**

| Puntuació | Nivell | Color | Significat |
|-----------|--------|-------|------------|
| 80-100 | Alt | Verd | Elevada probabilitat de dipòsits significatius |
| 60-79 | Mitjà-Alt | Groc-Verd | Bona probabilitat, verificació recomanada |
| 40-59 | Mitjà | Taronja | Probabilitat moderada |
| 20-39 | Baix | Vermell | Baixa probabilitat |
| 0-19 | No avaluable | Gris | Dades insuficients |

### Risc Arqueològic

Avalua el risc d'impacte/pèrdua del patrimoni:

| Factor | Pes | Descripció | Com es calcula |
|--------|-----|------------|----------------|
| Accessibilitat | 25% | Facilitat d'accés a l'àrea | "easy" = 80, "moderate" = 50, "difficult" = 30, "restricted" = 10 |
| Ús del sòl | 25% | Activitats agrícoles/constructives | "urban" = 90, "ploughed" = 70, "pasture" = 40, "woodland" = 20 |
| Restriccions existents | 20% | Proteccions legals | Absència restriccions = 80, restricció paisatgística = 40, restricció arqueològica = 10 |
| Investigacions prèvies | 15% | Estat del coneixement | Cap investigació = 60, prospecció = 40, excavació = 20 |
| Potencial | 15% | Inversament proporcional al potencial | Alt potencial = alt risc de pèrdua |

**Classificació del risc:**

| Puntuació | Nivell | Color | Acció recomanada |
|-----------|--------|-------|------------------|
| 75-100 | Alt | Vermell | Intervenció urgent, mesures de tutela immediates |
| 50-74 | Mitjà | Taronja | Monitoratge actiu, valorar protecció |
| 25-49 | Baix | Groc | Monitoratge periòdic |
| 0-24 | Nul | Verd | Cap intervenció immediata necessària |

### Camps Base de Dades per a l'Anàlisi

| Camp | Base de dades | Descripció |
|------|---------------|------------|
| Puntuació Potencial | `potential_score` | Valor 0-100 calculat |
| Puntuació Risc | `risk_score` | Valor 0-100 calculat |
| Factors Potencial | `potential_factors` | JSON amb detall factors |
| Factors Risc | `risk_factors` | JSON amb detall factors |
| Data Anàlisi | `analysis_date` | Timestamp del càlcul |
| Mètode Anàlisi | `analysis_method` | Algorisme utilitzat |

---

## Capes Geomètriques UT

PyArchInit gestiona tres tipus de geometries per a les Unitats Topogràfiques:

### Taules Geomètriques

| Capa | Taula | Tipus Geometria | Ús |
|------|-------|-----------------|-----|
| UT Punts | `pyarchinit_ut_point` | Point | Localització puntual |
| UT Línies | `pyarchinit_ut_line` | LineString | Traçats, recorreguts |
| UT Polígons | `pyarchinit_ut_polygon` | Polygon | Àrees de dispersió |

### Creació de Capes UT

1. **Via QGIS Browser:**
   - Obrir la base de dades al Browser
   - Localitzar la taula `pyarchinit_ut_point/line/polygon`
   - Arrossegar sobre el mapa

2. **Via Menú PyArchInit:**
   - Menú **PyArchInit** > **GIS Tools** > **Load UT Layers**
   - Seleccionar el tipus de geometria

### Connexió UT-Geometria

Cada registre geomètric està connectat a la fitxa UT mitjançant:

| Camp | Descripció |
|------|------------|
| `progetto` | Nom projecte (ha de correspondre) |
| `nr_ut` | Número UT (ha de correspondre) |

### Flux de Treball Creació Geometries

1. **Activar edició** a la capa UT desitjada
2. **Dibuixar** la geometria al mapa
3. **Emplenar** els atributs `progetto` i `nr_ut`
4. **Desar** la capa
5. **Verificar** la connexió des de la fitxa UT

---

## Generació de Mapes de Calor

El mòdul de generació de mapes de calor permet visualitzar la distribució espacial del potencial i del risc arqueològic.

### Requisits Mínims

- **Almenys 2 UT** amb coordenades vàlides (`coord_geografiche` O `coord_piane`)
- **Puntuacions calculades** per a potencial i/o risc
- **CRS definit** al projecte QGIS

### Mètodes d'Interpolació

| Mètode | Descripció | Quan utilitzar-lo |
|--------|------------|-------------------|
| **KDE** (Kernel Density) | Estimació densitat kernel gaussiana | Distribució contínua, molts punts |
| **IDW** (Inverse Distance) | Pes invers de la distància | Dades disperses, valors puntuals importants |
| **Grid** | Interpolació sobre graella regular | Anàlisis sistemàtiques |

### Paràmetres Mapa de Calor

| Paràmetre | Valor Per Defecte | Descripció |
|-----------|-------------------|------------|
| Cell Size | 50 m | Resolució de la graella |
| Bandwidth (KDE) | Auto | Radi d'influència |
| Power (IDW) | 2 | Exponent de ponderació |

### Procediment de Generació

1. **Des de la fitxa UT:**
   - Anar a la pestanya **Anàlisi**
   - Verificar que les puntuacions estiguin calculades
   - Fer clic a **Generar Mapa de Calor**

2. **Selecció de paràmetres:**
   - Tipus: Potencial o Risc
   - Mètode: KDE, IDW, o Grid
   - Cell size: típicament 25-100 m

3. **Sortida:**
   - Capa ràster afegida a QGIS
   - Desada a `pyarchinit_Raster_folder`
   - Simbologia aplicada automàticament

### Mapa de Calor amb Màscara Poligonal (GNA)

Per generar mapes de calor **dins d'una àrea de projecte** (p. ex. perímetre d'estudi):

1. **Preparar el polígon** de l'àrea de projecte
2. **Utilitzar GNA Export** (veure secció següent)
3. El sistema **emmascara** automàticament el mapa de calor al polígon

---

## Export GNA - Geoportal Nacional d'Arqueologia

### Què és el GNA?

El **Geoportale Nazionale per l'Archeologia** (GNA) és el sistema informatiu del Ministeri de Cultura italià per a la gestió de dades arqueològiques territorials. PyArchInit suporta l'exportació en format GeoPackage estàndard GNA.

### Estructura GeoPackage GNA

| Capa | Tipus | Descripció |
|------|-------|------------|
| **MOPR** | Polygon | Àrea/Perímetre de projecte |
| **MOSI** | Point/Polygon | Jaciments arqueològics (UT) |
| **VRP** | MultiPolygon | Carta del Potencial Arqueològic |
| **VRD** | MultiPolygon | Carta del Risc Arqueològic |

### Mapping Camps UT → MOSI GNA

| Camp GNA | Camp UT PyArchInit | Notes |
|----------|---------------------|-------|
| ID | `{progetto}_{nr_ut}` | Identificatiu compost |
| AMA | `def_ut` | Vocabulari controlat GNA |
| OGD | `interpretazione_ut` | Definició objecte |
| OGT | `geometria` | Tipus geometria |
| DES | `descrizione_ut` | Descripció (màx 10000 char) |
| OGM | `metodo_rilievo_e_ricognizione` | Modalitat identificació |
| DTSI | `periodo_I` → data | Data inici (negatiu per a.C.) |
| DTSF | `periodo_II` → data | Data fi |
| PRVN | `nazione` | País |
| PVCR | `regione` | Regió |
| PVCP | `provincia` | Província |
| PVCC | `comune` | Municipi |
| LCDQ | `quota` | Cota s.n.m. |

### Classificació VRP (Potencial)

| Rang | Codi GNA | Etiqueta | Color |
|------|----------|----------|-------|
| 0-20 | NV | No avaluable | Gris |
| 20-40 | NU | Nul | Verd |
| 40-60 | BA | Baix | Groc |
| 60-80 | ME | Mitjà | Taronja |
| 80-100 | AL | Alt | Vermell |

### Classificació VRD (Risc)

| Rang | Codi GNA | Etiqueta | Color |
|------|----------|----------|-------|
| 0-25 | NU | Nul | Verd |
| 25-50 | BA | Baix | Groc |
| 50-75 | ME | Mitjà | Taronja |
| 75-100 | AL | Alt | Vermell |

### Procediment Export GNA

1. **Preparació dades:**
   - Verificar que totes les UT tinguin coordenades
   - Calcular les puntuacions potencial/risc
   - Preparar el polígon de l'àrea de projecte (MOPR)

2. **Inici export:**
   - Des de la fitxa UT, fer clic a **GNA Export**
   - O menú **PyArchInit** > **GNA** > **Export**

3. **Configuració:**
   ```
   Projecte: [seleccionar projecte]
   Àrea de projecte: [seleccionar capa polígon MOPR]
   Sortida: [camí fitxer .gpkg]

   ☑ Exportar MOSI (jaciments)
   ☑ Generar VRP (potencial)
   ☑ Generar VRD (risc)

   Mètode heatmap: KDE
   Cell size: 50 m
   ```

4. **Execució:**
   - Fer clic a **Exportar**
   - Esperar generació (pot requerir alguns minuts)
   - El GeoPackage es desa al camí especificat

5. **Verificació sortida:**
   - Obrir el GeoPackage a QGIS
   - Verificar les capes MOPR, MOSI, VRP, VRD
   - Comprovar que les geometries VRP/VRD estiguin retallades al MOPR

### Validació GNA

Per validar la sortida contra les especificacions GNA:

1. Carregar el GeoPackage al **template GNA oficial**
2. Verificar que les capes siguin reconegudes
3. Comprovar els vocabularis controlats
4. Verificar les relacions geomètriques (MOSI dins MOPR)

---

## Export PDF

### Fitxa UT Individual

Exporta la fitxa UT completa en format PDF professional.

**Contingut:**
- Capçalera amb projecte i número UT
- Secció Identificació
- Secció Localització
- Secció Terreny
- Secció Dades Survey
- Secció Cronologia
- Secció Anàlisi (potencial/risc amb barres acolorides)
- Secció Documentació

**Procediment:**
1. Seleccionar el registre UT
2. Fer clic al botó **PDF** a la barra d'eines
3. El PDF es desa a `pyarchinit_PDF_folder`

### Llistat UT (Llista PDF)

Exporta un llistat tabular de totes les UT en format horitzontal.

**Columnes:**
- UT, Projecte, Definició, Interpretació
- Municipi, Coordenades, Període I, Període II
- Tro/m2, Visibilitat, Potencial, Risc

**Procediment:**
1. Carregar les UT a exportar (cerca o visualitza tot)
2. Fer clic al botó **Llista PDF** a la barra d'eines
3. El PDF es desa com a `Llistat_UT.pdf`

### Informe d'Anàlisi UT

Genera un informe detallat de l'anàlisi potencial/risc.

**Contingut:**
1. Dades identificatives de la UT
2. Secció Potencial Arqueològic
   - Puntuació amb indicador gràfic
   - Text narratiu descriptiu
   - Taula factors amb contribucions
3. Secció Risc Arqueològic
   - Puntuació amb indicador gràfic
   - Text narratiu amb recomanacions
   - Taula factors amb contribucions
4. Secció Metodologia

---

## Flux de Treball Operatiu Complet

### Fase 1: Configuració Projecte

1. **Crear nou projecte** a PyArchInit o utilitzar-ne un d'existent
2. **Definir l'àrea d'estudi** (polígon MOPR)
3. **Configurar el CRS** del projecte QGIS

### Fase 2: Registre UT al Camp

1. **Obertura fitxa UT**
2. **Nou registre** (clic "New Record")
3. **Emplenar dades identificatives:**
   ```
   Projecte: Survey Vall del Llobregat 2024
   Nr. UT: 25
   ```

4. **Emplenar localització:**
   ```
   Regió: Catalunya
   Província: Barcelona
   Municipi: Martorell
   Localitat: Turó Alt
   Coord. geogràfiques: 41.4567, 1.9234
   Cota: 125 m
   Precisió GPS: 3 m
   ```

5. **Emplenar descripció** (utilitzant tesaurus):
   ```
   Definició: Concentració de troballes
   Descripció: Àrea el·líptica de ca. 50x30 m
   amb concentració de fragments ceràmics
   i laterici sobre vessant de turó...
   ```

6. **Emplenar dades survey** (utilitzant tesaurus):
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

7. **Emplenar materials i cronologia:**
   ```
   Dimensions: 1500 m2
   Tro/m2: 5-8
   Troballes datants: Ceràmica comuna,
   sigil·lata itàlica, laterici

   Període I: Romà
   Datació I: I-II s. d.C.
   Interpretació I: Vil·la rústica
   ```

8. **Desar** (clic "Save")

### Fase 3: Creació Geometries

1. **Carregar capa** `pyarchinit_ut_polygon`
2. **Activar edició**
3. **Dibuixar** el perímetre de la UT al mapa
4. **Emplenar atributs**: progetto, nr_ut
5. **Desar** la capa

### Fase 4: Anàlisi

1. **Obrir pestanya Anàlisi** a la fitxa UT
2. **Verificar** les puntuacions calculades automàticament
3. **Generar mapa de calor** si és necessari
4. **Exportar informe PDF** de l'anàlisi

### Fase 5: Export GNA (si es requereix)

1. **Verificar completesa dades** per a totes les UT
2. **Preparar polígon MOPR** de l'àrea de projecte
3. **Executar GNA Export**
4. **Validar sortida** contra especificacions GNA

---

## Consells i Trucs

### Optimització del Flux de Treball

1. **Preemplenar els tesaurus** abans d'iniciar les prospeccions
2. **Utilitzar plantilles de projecte** amb dades comunes preconfigurades
3. **Sincronitzar coordenades** del GPS al camp `coord_geografiche`
4. **Desar freqüentment** durant l'emplenat

### Millorar la Qualitat de les Dades

1. **Emplenar TOTS els camps** rellevants per a cada UT
2. **Utilitzar sempre els tesaurus** en lloc de text lliure
3. **Verificar les coordenades** al mapa abans de desar
4. **Documentar fotogràficament** cada UT

### Optimització Mapa de Calor

1. **Cell size apropiat**: utilitzar 25-50m per àrees petites, 100-200m per àrees extenses
2. **Mètode KDE** per distribucions contínues i homogènies
3. **Mètode IDW** quan els valors puntuals són crítics
4. **Verificar sempre** que les coordenades siguin correctes abans de generar

### Export GNA Eficient

1. **Preparar el polígon MOPR** amb antelació com a capa separada
2. **Verificar que totes les UT** tinguin coordenades vàlides
3. **Calcular les puntuacions** abans de l'export
4. **Utilitzar noms de fitxer** descriptius per als GeoPackage

### Gestió Multi-Usuari

1. **Definir convencions** de numeració UT compartides
2. **Utilitzar base de dades PostgreSQL** per accés concurrent
3. **Sincronitzar periòdicament** les dades
4. **Documentar les modificacions** als camps de notes

---

## Resolució de Problemes

### Problema: Combobox Tesaurus Buits

**Símptomes:** Els menús desplegables per survey_type, vegetation, etc. estan buits.

**Causes:**
- Entrades tesaurus no presents a la base de dades
- Codi d'idioma erroni
- Taula tesaurus no actualitzada

**Solucions:**
1. Menú **PyArchInit** > **Database** > **Actualitzar base de dades**
2. Verificar taula `pyarchinit_thesaurus_sigle` per a entrades `ut_table`
3. Comprovar configuració d'idioma
4. Si és necessari, reimportar els tesaurus des de la plantilla

### Problema: Coordenades No Vàlides

**Símptomes:** Error en desar o coordenades visualitzades en posició errònia.

**Causes:**
- Format erroni (coma vs punt decimal)
- Sistema de referència no corresponent
- Ordre lat/lon invertit

**Solucions:**
1. Format correcte `coord_geografiche`: `42.1234, 12.5678` (lat, lon)
2. Format correcte `coord_piane`: `1234567.89, 4567890.12` (x, y)
3. Utilitzar sempre el punt com a separador decimal
4. Verificar CRS del projecte QGIS

### Problema: UT No Visible al Mapa

**Símptomes:** Després de desar, la UT no apareix al mapa.

**Causes:**
- Geometria no creada a la capa
- Atributs `progetto`/`nr_ut` no corresponents
- Capa no carregada o oculta
- CRS diferent entre capa i projecte

**Solucions:**
1. Verificar que existeixi la capa `pyarchinit_ut_point/polygon`
2. Comprovar que els atributs estiguin emplenats correctament
3. Activar la visibilitat de la capa al panell Capes
4. Utilitzar "Zoom to Layer" per verificar l'extensió

### Problema: Mapa de Calor No Generat

**Símptomes:** Error "Calen almenys 2 punts amb coordenades vàlides".

**Causes:**
- Menys de 2 UT amb coordenades
- Coordenades en format erroni
- Camps de coordenades buits

**Solucions:**
1. Verificar que almenys 2 UT tinguin `coord_geografiche` O `coord_piane` emplenats
2. Comprovar el format de les coordenades (punt decimal, ordre correcte)
3. Recalcular les puntuacions abans de generar el mapa de calor
4. Verificar que els camps no continguin caràcters especials

### Problema: Puntuació Potencial/Risc No Calculada

**Símptomes:** Els camps potenziale_score i risk_score estan buits o a zero.

**Causes:**
- Camps obligatoris no emplenats
- Valors tesaurus no reconeguts
- Error en el càlcul

**Solucions:**
1. Emplenar almenys: `def_ut`, `periodo_I`, `visibility_percent`
2. Utilitzar valors del tesaurus (no text lliure)
3. Desar el registre i reobrir-lo
4. Verificar als logs de QGIS possibles errors

### Problema: Export GNA Fallit

**Símptomes:** El GeoPackage no es crea o està incomplet.

**Causes:**
- Mòdul GNA no disponible
- Dades UT incompletes
- Polígon MOPR no vàlid
- Permisos d'escriptura insuficients

**Solucions:**
1. Verificar que el mòdul `modules/gna` estigui instal·lat
2. Comprovar que totes les UT tinguin coordenades vàlides
3. Verificar que el polígon MOPR sigui vàlid (sense auto-interseccions)
4. Comprovar permisos a la carpeta de sortida
5. Verificar espai de disc suficient

### Problema: PDF Export amb Camps Mancants

**Símptomes:** El PDF generat no mostra alguns camps o mostra valors erronis.

**Causes:**
- Camps base de dades no actualitzats
- Versió esquema base de dades obsoleta
- Dades no desades abans de l'export

**Solucions:**
1. Desar el registre abans d'exportar
2. Actualitzar la base de dades si és necessari
3. Verificar que els nous camps (v4.9.67+) existeixin a la taula

### Problema: Error Qt6/QGIS 4.x

**Símptomes:** El plugin no carrega a QGIS 4.x amb error `AllDockWidgetFeatures`.

**Causes:**
- Incompatibilitat Qt5/Qt6
- Fitxer UI no actualitzat

**Solucions:**
1. Actualitzar PyArchInit a l'última versió
2. El fitxer `UT_ui.ui` ha d'utilitzar flags explícits en lloc de `AllDockWidgetFeatures`

---

## Referències

### Base de Dades

- **Taula**: `ut_table`
- **Classe mapper**: `UT`
- **ID**: `id_ut`

### Taules Geomètriques

- **Punts**: `pyarchinit_ut_point`
- **Línies**: `pyarchinit_ut_line`
- **Polígons**: `pyarchinit_ut_polygon`

### Fitxers Font

| Fitxer | Descripció |
|--------|------------|
| `gui/ui/UT_ui.ui` | Interfície d'usuari Qt |
| `tabs/UT.py` | Controlador principal |
| `modules/utility/pyarchinit_exp_UTsheet_pdf.py` | Export PDF fitxes |
| `modules/utility/pyarchinit_exp_UT_analysis_pdf.py` | Export PDF anàlisi |
| `modules/analysis/ut_potential.py` | Càlcul potencial |
| `modules/analysis/ut_risk.py` | Càlcul risc |
| `modules/analysis/ut_heatmap_generator.py` | Generació mapa de calor |
| `modules/gna/gna_exporter.py` | Export GNA |
| `modules/gna/gna_vocabulary_mapper.py` | Mapping vocabularis GNA |

### Codis Tesaurus UT

| Codi | Camp | Descripció |
|------|------|------------|
| 12.1 | survey_type | Tipus de prospecció |
| 12.2 | vegetation_coverage | Cobertura vegetal |
| 12.3 | gps_method | Mètode GPS |
| 12.4 | surface_condition | Condició superfície |
| 12.5 | accessibility | Accessibilitat |
| 12.6 | weather_conditions | Condicions meteo |
| 12.7 | def_ut | Definició UT |

---

## Vídeo Tutorial

### Documentació Prospeccions
**Durada**: 15-18 minuts
- Registre UT
- Dades survey amb tesaurus
- Geolocalització

### Anàlisi Potencial i Risc
**Durada**: 10-12 minuts
- Càlcul automàtic puntuacions
- Interpretació resultats
- Generació mapa de calor

### Export GNA
**Durada**: 12-15 minuts
- Preparació dades
- Configuració export
- Validació sortida

### Export Informe PDF
**Durada**: 8-10 minuts
- Fitxa UT estàndard
- Llistat UT
- Informe d'anàlisi amb mapes

---

*Última actualització: Gener 2026*
*PyArchInit v4.9.68 - Sistema de Gestió de Dades Arqueològiques*
