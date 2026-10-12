# PyArchInit - GeoArchaeo - Anàlisi Geoestadística

## Índex
1. [Introducció](#introducció)
2. [Accés a l'eina](#accés-a-leina)
3. [Interfície d'usuari](#interfície-dusuari)
4. [Pestanya Dades](#pestanya-dades)
5. [Pestanya Variograma](#pestanya-variograma)
6. [Pestanya Kriging](#pestanya-kriging)
7. [Pestanya Patrons (ML)](#pestanya-patrons-ml)
8. [Pestanya Mostreig](#pestanya-mostreig)
9. [Pestanya Informe](#pestanya-informe)
10. [Flux de treball operatiu](#flux-de-treball-operatiu)
11. [Resolució de problemes](#resolució-de-problemes)
12. [Notes tècniques](#notes-tècniques)

---

## Introducció

**GeoArchaeo** és el mòdul d'anàlisi geoestadística integrat a PyArchInit i correspon a la versió **1.3.1** del connector GeoArchaeo. Treballa amb qualsevol capa de punts del projecte QGIS que tingui un camp numèric (nombre de fragments, mesures geofísiques, anàlisis de sòl, mesures de les tombes…) i acompanya l'anàlisi des de les estadístiques descriptives fins al variograma, la interpolació amb kriging ordinari i la seva incertesa, la cerca de grups i anomalies amb aprenentatge automàtic, la proposta de nous punts de mostreig i, finalment, un informe.

La interfície de GeoArchaeo només existeix en italià i en anglès. En aquest tutorial les etiquetes es tradueixen i entre parèntesis s'indica l'etiqueta anglesa que apareix al panell. Els paràmetres del variograma es designen amb els termes habituals en geoestadística: nugget (efecte pepita), sill (variància total) i range (abast).

<!-- VIDEO: Introduccio a GeoArchaeo -->
> **Video Tutorial**: [Inserir enllac de video introduccio GeoArchaeo]

### Per què l'anàlisi geoestadística en arqueologia?

L'anàlisi geoestadística permet:

- **Descriure** la distribució dels valors mesurats (mitjana, dispersió, asimetria, valors atípics)
- **Quantificar** la correlació espacial, és a dir, fins a quina distància s'assemblen els valors (variograma)
- **Interpolar** els valors entre els punts coneguts i obtenir una superfície contínua acompanyada de la seva incertesa (kriging)
- **Reconèixer** grups de punts semblants i anomalies (aprenentatge automàtic)
- **Planificar** on mostrejar o excavar en les properes campanyes
- **Documentar** les anàlisis en un informe

### Visió general del flux de treball

```
Dades d'entrada: capa de punts + camp numèric (triats a dalt, una sola vegada)
  │
  ├─ 1 Dades ............ estadístiques descriptives, histograma
  ├─ 2 Variograma ....... nugget, sill, range, anisotropia
  ├─ 3 Kriging .......... ràsters de l'estimació i de la incertesa, validació creuada
  ├─ 4 Patrons (ML) ..... grups i anomalies (capa de punts)
  ├─ 5 Mostreig ......... nous punts proposats (capa de punts)
  └─ 6 Informe .......... document HTML amb gràfics interactius, o PDF
```

### Novetats de la versió 1.3.1

- La capa i el camp es trien **una sola vegada** a dalt i valen per a totes les pestanyes; cada pestanya conserva els seus resultats
- Els gràfics apareixen al panell fins i tot sense QtWebEngine (previsualització estàtica i botó per obrir-los al navegador)
- El kriging produeix també el **ràster d'incertesa**, aplica la rampa de colors i calcula una veritable **validació creuada leave-one-out**
- L'anisotropia es comprova amb veritables **variogrames direccionals**; nugget, sill i range es poden fixar a mà
- El variograma i el kriging són molt més ràpids (cerca de veïns amb KD-tree): quadrícules de fins a **500 × 500 cel·les**
- Els valors NULL ja no bloquegen les estadístiques ni el kriging; l'informe conté els gràfics; les dades d'exemple provenen de la carpeta del mòdul
- L'idioma del panell es desa a la configuració de QGIS

---

## Accés a l'eina

GeoArchaeo forma part del grup d'eines d'anàlisi de PyArchInit.

### Des de la barra d'eines

1. A la barra d'eines de PyArchInit, localitzar el botó desplegable de les **eines d'anàlisi** (el mateix grup que conté, entre d'altres, SAM, Pottery Tools i MoveCost)
2. Fer clic a la fletxa del costat del botó: la icona visible pot ser la d'una altra eina del grup
3. Triar **GeoArchaeo - Geostatistical Analysis** (etiqueta de l'acció a PyArchInit quan QGIS està en català)

<!-- IMAGE: Boto desplegable de les eines d'analisi a la barra d'eines -->
> **Fig. 1**: El menú desplegable de les eines d'anàlisi a la barra d'eines de PyArchInit

La mateixa entrada es troba al menú **pyArchInit** de la barra de menús de QGIS i al menú de complements, a **pyArchInit - Archaeological GIS Tools**.

El panell GeoArchaeo s'obre com a **panell acoblable** al costat dret de la finestra de QGIS: es pot moure, redimensionar o desacoblar com qualsevol panell de QGIS. Si es tanca, la mateixa entrada el torna a obrir amb els resultats de la sessió encara presents.

<!-- IMAGE: Panell GeoArchaeo acoblat a la dreta de QGIS -->
> **Fig. 2**: El panell GeoArchaeo acoblat al costat dret de la finestra de QGIS

### Selector d'idioma

A dalt a la dreta, la llista **«Idioma:»** (*Language:*) ofereix **Italiano** i **English**, els dos únics idiomes de la interfície de GeoArchaeo. El canvi és immediat, sense reiniciar QGIS, i l'elecció es desa a la configuració de QGIS. Mentre no se'n triï cap, el panell segueix l'idioma de QGIS: italià si QGIS està en italià, anglès en tots els altres casos, i per tant també amb QGIS en català.

---

## Interfície d'usuari

De dalt a baix, el panell conté: la capçalera amb els botons, el grup **«Dades d'entrada (utilitzades per totes les pestanyes)»** (*Input data (used by all tabs)*), les **6 pestanyes** de l'anàlisi i, durant els càlculs, la barra de progrés amb el botó **«Cancel·la»** (*Cancel*).

### Capçalera

| Element | Funció |
|---------|--------|
| **«Carrega dades d'exemple»** (*Load example data*) | Obre la llista dels conjunts de dades de prova inclosos al mòdul (vegeu la pestanya Dades) |
| **«Tutorial»** (*Tutorial*) | Obre la guia integrada de GeoArchaeo, en italià o en anglès, que també es pot obrir al navegador |
| **«Idioma:»** (*Language:*) | Llista Italiano / English |

### Dades d'entrada

Al grup **«Dades d'entrada (utilitzades per totes les pestanyes)»** (*Input data (used by all tabs)*) es tria una sola vegada:

- **«Capa de punts:»** (*Point layer:*): una capa vectorial de punts del projecte
- **«Camp de valor (numèric):»** (*Value field (numeric):*): el camp que s'analitzarà (la llista només mostra camps numèrics)

A sota apareix un resum amb els punts vàlids sobre el total, el SRC i l'extensió de la capa, per exemple «500 punts vàlids de 500 · SRC EPSG:32633 · …» (*500 valid points of 500 · CRS EPSG:32633 · …*). Els punts sense valor (NULL o text no numèric) no es compten com a vàlids. El resum també avisa quan el projecte no té capes de punts, quan la capa no té camps numèrics o quan el SRC és geogràfic (graus).

Quan es canvia de capa, el panell proposa també la distància màxima del variograma i la mida de cel·la del kriging, i preselecciona la capa a la pestanya Patrons (ML) si encara no n'hi ha cap de seleccionada.

### Les sis pestanyes

| Pestanya | Funció | Resultat |
|----------|--------|----------|
| **Dades** (*Data*) | Estadístiques descriptives del camp | Taula d'estadístiques, histograma amb diagrama de caixa |
| **Variograma** (*Variogram*) | Estructura espacial dels valors | Nugget, sill, range, anisotropia, gràfic |
| **Kriging** (*Kriging*) | Interpolació sobre una quadrícula regular | Ràsters de l'estimació i de la incertesa, validació creuada |
| **Patrons (ML)** (*Patterns (ML)*) | Grups i anomalies amb aprenentatge automàtic | Capa de punts amb l'etiqueta del grup |
| **Mostreig** (*Sampling*) | Proposta de nous punts de mostreig | Capa de punts i taula de coordenades |
| **Informe** (*Report*) | Recull de les anàlisis de la sessió | Fitxer HTML amb gràfics interactius, o PDF |

<!-- IMAGE: Capcalera, grup Dades d'entrada i les sis pestanyes de GeoArchaeo -->
> **Fig. 3**: La capçalera, el grup «Dades d'entrada» i les sis pestanyes del panell GeoArchaeo

### Resultats i gràfics

Cada pestanya mostra els resultats en un **requadre** sota el botó de càlcul, que continua visible fins que es repeteix l'anàlisi, i el **gràfic** al panell:

- si QGIS disposa de QtWebEngine, el gràfic Plotly és interactiu directament al panell (zoom, valors en passar-hi el ratolí)
- si no, apareix una **previsualització estàtica** amb la nota «Previsualització estàtica (QtWebEngine no disponible en aquesta instal·lació de QGIS).» (*Static preview (QtWebEngine not available in this QGIS installation).*)
- en tots dos casos, el botó **«Obre el gràfic interactiu al navegador»** (*Open interactive chart in browser*) obre la versió interactiva al navegador web

Les pestanyes Dades, Variograma i Kriging acaben amb un enllaç al pas següent, per exemple **«Pas següent: Variograma →»** (*Next step: Variogram →*).

### Anàlisis en curs

El variograma, el kriging, el reconeixement de patrons i el mostreig es calculen en un **fil d'execució separat**: QGIS continua sent utilitzable i a la part inferior del panell apareixen la **barra de progrés** (en percentatge per al kriging) i el botó **«Cancel·la»** (*Cancel*). S'executa una anàlisi cada vegada: si se n'inicia una altra apareix «Ja hi ha una anàlisi en curs: espera que acabi o cancel·la-la.» (*An analysis is already running: wait for it to finish or cancel it.*)

---

## Pestanya Dades

La pestanya **Dades** (*Data*, «1. Anàlisi exploratòria» / *1. Exploratory analysis*) descriu la distribució dels valors abans d'interpolar-los.

### Càlcul de les estadístiques

1. Al grup «Dades d'entrada», triar la capa de punts i el camp numèric
2. Obrir la pestanya **Dades**
3. Fer clic a **«Calcula estadístiques»** (*Calculate statistics*)

<!-- IMAGE: Pestanya Dades amb estadistiques i histograma -->
> **Fig. 4**: La pestanya Dades amb la taula d'estadístiques i l'histograma del camp triat

### Estadístiques i interpretació

| Estadística | Descripció |
|-------------|------------|
| **Nombre de valors** (*Number of values*), **Valors absents** (*Missing values*) | Punts amb un valor vàlid i punts exclosos (NULL o text no numèric) |
| **Mínim**, **Màxim**, **Mitjana** (*Mean*), **Mediana** (*Median*) | Interval i posició dels valors |
| **Desv. estàndard** (*Std. deviation*), **Coef. de variació** (*Coeff. of variation*) | Dispersió absoluta i relativa |
| **Primer quartil (Q1)**, **Tercer quartil (Q3)** (*First/Third quartile*) | Límits del 50 % central dels valors |
| **Asimetria** (*Skewness*), **Curtosi** (*Kurtosis*) | Forma de la distribució |

Sota la taula, el panell hi afegeix una lectura en paraules:

- asimetria superior a 1: distribució asimètrica a la dreta (pocs valors molt alts); convé valorar una transformació logarítmica abans del kriging, per exemple creant un camp nou amb la calculadora de camps
- asimetria inferior a -1: distribució asimètrica a l'esquerra (pocs valors molt baixos)
- en els altres casos: distribució aproximadament simètrica, adequada per al kriging
- el nombre de possibles valors atípics, és a dir, més enllà de 3 desviacions estàndard de la mitjana

El gràfic mostra l'**histograma** dels valors amb un **diagrama de caixa** (a la previsualització estàtica, només l'histograma).

### Dades d'exemple

El botó **«Carrega dades d'exemple»** (*Load example data*) obre la finestra «Dades d'exemple de GeoArchaeo» (*GeoArchaeo example data*) amb els conjunts de dades de la carpeta `test_layers` del mòdul; el camí s'indica a **«Carpeta:»** (*Folder:*) i es pot canviar amb **«Navega…»** (*Browse…*). Els GeoPackage i els GeoJSON ja estan marcats. Els CSV només apareixen si no existeix un GeoPackage o un GeoJSON amb el mateix nom; s'han de marcar a mà i es carreguen com a text delimitat (camps `x` i `y`, EPSG:32633). Amb **OK** les capes s'afegeixen al projecte i la primera capa de punts carregada esdevé la capa d'entrada del panell.

| Conjunt de dades | Punts | Camps numèrics principals | Ús recomanat |
|------------------|-------|---------------------------|--------------|
| `villa_ceramica` (GeoPackage) | 500 | `ceramic_count`, `weight_g`, `depth_cm` | Estadístiques, variograma, kriging |
| `geoarchaeo_test_complete` (GeoPackage) | 500 | Els mateixos que `villa_ceramica` | Prova de totes les pestanyes |
| `geofisica_survey` (GeoPackage) | 4800 | `gpr_amplitude`, `mag_nt` | Isolation Forest, prova amb un conjunt gran |
| `necropoli` (GeoPackage) | 120 tombes | `length_cm`, `width_cm`, `depth_cm`, `n_grave_goods` | DBSCAN o K-Means |
| `soil_samples` (GeoPackage) | 80 | `sand_pct`, `silt_pct`, `clay_pct`, `ph`, `p_ppm`, `organic_pct` | Kriging de propietats del sòl |
| `ricognizione_survey` (GeoJSON) | 100 | `densita_mq`, `visibilita`, `pendenza`, `distanza_acqua` | Kriging de la densitat, mostreig |
| `unita_scavo_ceramica` (GeoJSON) | 50 | `ceramica_tot`, `ceramica_fine`, `ceramica_comune` | Variograma i kriging amb pocs punts |
| `area_studio` (GeoJSON) | 1 polígon | — | Àrea d'estudi per al mostreig |

Entre els CSV, `magnetometria_grid` (2500 punts, camp `mag_nT`) conté anomalies magnètiques simulades (dos murs, una fossa, un forn). Totes les dades són simulades i estan en EPSG:32633 (UTM 33N, metres). El polígon `area_studio` cobreix la zona de `ricognizione_survey`, `unita_scavo_ceramica` i `magnetometria_grid`, no la dels altres conjunts de dades.

### Requisits de les dades

- La capa ha de ser una capa vectorial de **punts** (en els multipunts s'utilitza el primer punt)
- El camp ha de ser **numèric**: un camp de text que contingui nombres s'ha de convertir amb la calculadora de camps
- Els valors NULL o no numèrics s'exclouen automàticament i es compten com a absents
- Calen almenys **5 punts** amb un valor vàlid per al variograma i el kriging (1 per a les estadístiques); un variograma fiable sol requerir unes quantes desenes de punts
- Es recomana un **SRC projectat** en metres (per exemple UTM): amb un SRC geogràfic el resum avisa i el variograma i el kriging demanen confirmació

---

## Pestanya Variograma

La pestanya **Variograma** (*Variogram*, «2. Variograma» / *2. Variogram*) mesura com creix la diferència entre els valors amb la distància: descriu l'estructura espacial de les dades i guia el kriging.

### Què és un variograma?

El variograma relaciona la **semivariància** dels parells de punts amb la **distància** que els separa. Els paràmetres del model són:

| Paràmetre | Descripció |
|-----------|------------|
| **Nugget** (efecte pepita) | Variabilitat a distància gairebé nul·la: error de mesura i variabilitat a petita escala |
| **Sill** (variància total) | Variància total que assoleix el model (el "replà") |
| **Range** (abast) | Distància a partir de la qual els valors deixen d'estar correlacionats; a GeoArchaeo és l'abast pràctic (95 % del sill) |

### Càlcul del variograma

1. Obrir la pestanya **Variograma**
2. Al grup **«Paràmetres»** (*Parameters*), revisar **«Distància màxima:»** (*Maximum distance:*): el botó **«Auto»** proposa aproximadament 1/3 de la diagonal de l'àrea que ocupen els punts (el mateix valor es proposa quan es canvia de capa)
3. Triar el **«Model teòric:»** (*Theoretical model:*)
4. Si cal, marcar **«Comprova l'anisotropia (variogrames direccionals)»** (*Check anisotropy (directional variograms)*)
5. Fer clic a **«Calcula el variograma»** (*Calculate variogram*)

Els parells de punts s'agrupen en **15 classes de distància** (lags) entre zero i la distància màxima; el nombre de classes no es pot canviar des del panell. Per sobre de **3000 punts**, el variograma es calcula sobre una submostra aleatòria de 3000 punts, perquè el nombre de parells creix amb el quadrat del nombre de punts. El model s'ajusta per mínims quadrats ponderats pel nombre de parells de cada classe.

<!-- IMAGE: Pestanya Variograma amb parametres i resultats -->
> **Fig. 5**: La pestanya Variograma amb els paràmetres, el model teòric i el requadre de resultats

### Models teòrics

| Model | Comportament | Quan utilitzar-lo |
|-------|--------------|-------------------|
| **«Esfèric (recomanat)»** (*Spherical (recommended)*) | Creix fins al range i després es manté constant | El més utilitzat: densitats de materials, distribucions amb límits nets |
| **«Exponencial»** (*Exponential*) | Creix ràpidament prop de l'origen i assoleix el sill de manera gradual | Fenòmens de decaïment continu, per exemple elements químics al sòl |
| **«Gaussià»** (*Gaussian*) | Molt regular prop de l'origen | Fenòmens molt "suaus" (superfícies); s'ha d'utilitzar amb prudència |
| **«Matérn»** (*Matérn*) | Intermedi entre l'exponencial i el gaussià (ν = 1,5) | Alternativa flexible |

Regla pràctica: començar pel model esfèric i comparar el RMSE del seu ajust amb el dels altres models. El kriging utilitza l'**últim** variograma calculat: després de les comparacions, cal tornar a calcular el model triat.

### Paràmetres manuals

El grup **«Paràmetres manuals (opcional)»** (*Manual parameters (optional)*), desactivat per defecte, permet fixar **«Nugget:»** (*Nugget:*), **«Sill (variància total):»** (*Sill (total variance):*) i **«Range (distància de correlació):»** (*Range (correlation distance):*). Amb el grup actiu, els valors diferents de zero queden fixos i els que es deixen en «Auto» (zero) s'estimen.

### Lectura dels resultats

El requadre de resultats indica:

- el model amb el **nugget**, el **sill**, el **range** (en unitats del SRC) i el **RMSE** de l'ajust
- el nombre de parells de punts i de classes de distància, amb la submostra utilitzada si n'hi ha
- una lectura del range: fins a aquesta distància els valors estan correlacionats espacialment; més enllà no s'influeixen
- la relació nugget/sill: per sota del 25 % forta continuïtat a petita escala, fins al 60 % continuïtat moderada, per sobre del 60 % molta variabilitat a petita escala o error de mesura (el kriging serà poc informatiu)

El gràfic mostra els punts del variograma experimental (més grans on hi ha més parells), la corba del model i les línies del nugget, el sill i el range.

<!-- IMAGE: Variograma experimental amb el model ajustat -->
> **Fig. 6**: Variograma experimental i model esfèric amb les línies del nugget, el sill i el range

### Variogrames direccionals (anisotropia)

Amb **«Comprova l'anisotropia (variogrames direccionals)»** marcada, GeoArchaeo calcula també els variogrames en les direccions **0°, 45°, 90° i 135°** (angles mesurats des de l'est en sentit antihorari, tolerància ±22,5°). El nugget i el sill són els del variograma global; per a cada direcció s'estima el range.

- Si la relació entre el range més gran i el més petit supera **2**, el requadre assenyala l'anisotropia i la direcció principal (per exemple al llarg d'un mur, un camí o un pendent)
- Si no, indica «Cap anisotropia rellevant» (*No relevant anisotropy*) amb la relació calculada
- Amb massa pocs parells per direcció apareix «No hi ha prou parells per als variogrames direccionals.» (*Not enough pairs for directional variograms.*)

Al gràfic interactiu, els variogrames direccionals són entrades de la llegenda amagades al principi: cal fer clic a 0°, 45°, 90° o 135° per mostrar-los (a la previsualització estàtica sempre es dibuixen). El kriging del panell utilitza el model omnidireccional: l'anisotropia serveix per a la interpretació.

---

## Pestanya Kriging

La pestanya **Kriging** (*Kriging*, «3. Kriging ordinari» / *3. Ordinary kriging*) interpola els valors sobre una quadrícula regular amb el variograma, produeix també el mapa d'incertesa i afegeix els ràsters al projecte.

### El kriging ordinari

El panell executa **kriging ordinari** (mitjana local constant però desconeguda), adequat per a la majoria de les dades arqueològiques. Per a cada cel·la utilitza els **20 punts més propers**, trobats amb un KD-tree; aquest nombre no es pot canviar des del panell. El cokriging, el kriging espaciotemporal i el kriging per blocs per a conjunts de dades molt grans només existeixen com a algorismes de Processing del connector GeoArchaeo independent i no estan disponibles a PyArchInit.

### Execució del kriging

1. Obrir la pestanya **Kriging** i llegir la línia d'estat del variograma (vegeu més avall); el botó **«← Vés al variograma»** (*← Go to Variogram*) torna a la pestanya anterior
2. Ajustar **«Mida de cel·la:»** (*Cell size:*), és a dir, la mida d'una cel·la en unitats del SRC: el panell proposa unes 100 cel·les al costat més llarg de la capa i mostra a sota la quadrícula resultant («Quadrícula: … × … = … cel·les» / *Grid: … × … = … cells*)
3. Deixar marcada **«Utilitza el variograma calculat»** (*Use the calculated variogram*) per utilitzar el variograma de la pestanya anterior; si no està marcada, el variograma s'estima automàticament
4. Deixar marcada **«Crea també el ràster d'incertesa (desv. estàndard)»** (*Also create the uncertainty raster (std. deviation)*) si cal el mapa d'incertesa
5. Fer clic a **«Executa el kriging»** (*Run kriging*): la barra de progrés mostra el percentatge i **«Cancel·la»** (*Cancel*) interromp el càlcul

La línia d'estat pot indicar:

- «Variograma disponible: …, range … ✓» (*Variogram available: …, range … ✓*): s'utilitza el variograma calculat amb la mateixa capa i el mateix camp
- «Cap variograma calculat: s'estimarà automàticament (model esfèric).» (*No variogram calculated: it will be estimated automatically (spherical model).*)
- «El variograma es va calcular amb una altra capa o un altre camp: es tornarà a calcular.» (*The variogram was calculated on another layer/field: it will be recalculated.*), també en aquest cas amb una estimació automàtica

> **Quadrícula**: la quadrícula cobreix l'extensió de la capa de punts i està limitada a **500 cel·les per costat**. Si la mida de cel·la triada és massa fina, s'augmenta automàticament i la línia de la quadrícula ho indica («mida de cel·la mínima … (màx. 500 cel·les per costat)» / *minimum cell size … (max 500 cells per side)*). Per sobre de **40.000 cel·les** la línia es torna taronja i, en iniciar, el panell demana confirmació perquè el càlcul pot trigar uns quants minuts.

<!-- IMAGE: Rasters del kriging i metriques de validacio creuada -->
> **Fig. 7**: Els ràsters de l'estimació i de la incertesa al mapa, amb el requadre de resultats i la validació creuada

### Resultats del kriging

El kriging afegeix al projecte dos ràsters GeoTIFF en el SRC de la capa de punts:

| Capa | Contingut | Estil |
|------|-----------|-------|
| `Kriging_<camp>` | Valor estimat a cada cel·la | Rampa de colors del blau al vermell passant pel groc; visible |
| `Kriging_<camp>_uncertainty` | Desviació estàndard de l'estimació (incertesa) | Rampa del groc clar al vermell; afegida a dalt de la llista de capes, però amagada |

Amb el panell en italià, el segon ràster s'anomena `Kriging_<camp>_incertezza`. Els fitxers s'escriuen en una **carpeta temporal**: per conservar-los, cal exportar-los des del menú contextual de la capa (**Exporta**).

El requadre de resultats resumeix els punts utilitzats, la mida de la quadrícula, la mida de cel·la, el model i el range; el gràfic mostra el mapa dels valors estimats i el de la incertesa, amb els punts de mostra superposats.

### Validació creuada leave-one-out

Després del kriging, GeoArchaeo fa una **validació creuada leave-one-out**: cada punt s'elimina i es torna a estimar a partir dels altres (sobre un màxim de 200 punts triats a l'atzar en els conjunts grans). Les mètriques apareixen al requadre de resultats:

| Mètrica | Significat | Valor desitjable |
|---------|------------|------------------|
| **RMSE** (*root mean squared error*) | Error típic de l'estimació | El més baix possible, comparat amb la desviació estàndard de les dades |
| **MAE** (*mean absolute error*) | Error mitjà en valor absolut | El més baix possible |
| **ME** (*mean error, bias*) | Sobreestimació o subestimació sistemàtica | Proper a 0 |
| **R²** (*explained variance*) | Capacitat predictiva | A partir de 0,5 bona, per sota de 0,2 baixa |
| **MSDR** (*standardized error*) | Realisme de la incertesa estimada | Al voltant d'1; per sobre d'1,5 incertesa subestimada, per sota de 0,5 sobreestimada |

El panell hi afegeix un judici en paraules sobre la capacitat predictiva (bona, moderada o baixa) i, quan escau, sobre el MSDR.

> **Nota**: el kriging s'executa en un **fil d'execució en segon pla**, de manera que la interfície de QGIS continua sent utilitzable durant el càlcul; la barra de progrés indica l'estat del processament.

---

## Pestanya Patrons (ML)

La pestanya **Patrons (ML)** (*Patterns (ML)*, «4. Reconeixement de patrons (aprenentatge automàtic)» / *4. Pattern recognition (machine learning)*) agrupa els punts per posició i atributs numèrics, o detecta anomalies, i crea una capa amb l'etiqueta de cada punt.

### Mètodes disponibles

| Mètode (entrada de la llista) | Què fa | Paràmetres |
|-------------------------------|--------|------------|
| **«K-Means – grups per similitud»** (*K-Means – groups by similarity*) | Divideix els punts en K grups semblants per posició i atributs | **«Nombre de grups (0 = automàtic):»** (*Number of groups (0 = automatic):*); amb 0 el nombre es tria segons la quantitat de punts (de 2 a 5) |
| **«DBSCAN – grups per densitat (també troba punts aïllats)»** (*DBSCAN – groups by density (also finds isolated points)*) | Troba grups per densitat sense fixar-ne el nombre; els punts aïllats formen el grup «Aïllats / soroll» (*Isolated / noise*) | Automàtics |
| **«Isolation Forest – detecció d'anomalies»** (*Isolation Forest – anomaly detection*) | Marca com a «Anomalia» (*Anomaly*) aproximadament el 10 % dels punts més diferents dels altres; la resta són «Normal» (*Normal*) | Automàtics |

### Execució

1. Obrir la pestanya **Patrons (ML)**
2. A la llista **«Capes de punts per analitzar (una o més):»** (*Point layers to analyse (one or more):*), seleccionar una o més capes de punts (si no hi ha res seleccionat, es preselecciona la capa d'entrada)
3. Triar el **«Mètode:»** (*Method:*)
4. Només per a K-Means, ajustar **«Nombre de grups (0 = automàtic):»**
5. Fer clic a **«Inicia el reconeixement de patrons»** (*Run pattern recognition*)

Les variables analitzades són les **coordenades X i Y** i **tots els camps numèrics** de les capes seleccionades, estandarditzats; els valors absents se substitueixen per la mitjana del camp. Per tant, no s'utilitza només el camp de valor triat a dalt: hi entren tots els camps numèrics, inclosos identificadors i números correlatius, i si distorsionen els grups convé analitzar una còpia de la capa només amb els camps útils. Si s'analitzen diverses capes juntes, convé que tinguin els mateixos camps numèrics en el mateix ordre i el mateix SRC (la capa creada utilitza el SRC de la primera capa seleccionada).

<!-- IMAGE: Pestanya Patrons (ML) amb la capa de grups -->
> **Fig. 8**: La pestanya Patrons (ML) amb el gràfic dels grups i la capa `ML_groups` al mapa

### Resultats

- El requadre de resultats indica el mètode, el nombre de grups i quants punts cauen en cadascun (per exemple «Grup A (n=42)» / *Group A (n=42)*)
- El gràfic mostra els punts en el pla de les dues primeres components principals (PC1, PC2) de les variables, acolorits per grup
- Es crea una capa de punts temporal, `ML_groups` (K-Means, DBSCAN) o `ML_anomalies` (Isolation Forest), amb una llegenda per categories: gris per als punts aïllats, vermell i més gran per a les anomalies; amb el panell en italià els noms són `Gruppi_ML` i `Anomalie_ML`

| Camp | Contingut |
|------|-----------|
| `cluster_id` | Número del grup (-1 = aïllats amb DBSCAN; 1 = anomalia i 0 = normal amb Isolation Forest) |
| `cluster_name` | Nom llegible, per exemple «Group A (n=42)», «Isolated / noise (n=5)», «Anomaly (n=12)» |
| `cluster_size` | Nombre de punts del grup |
| `method` | Mètode utilitzat |
| `x_coord`, `y_coord` | Coordenades del punt |

### Classificació supervisada

Sota el mètode, el panell recorda que la classificació supervisada (Random Forest amb un camp d'etiquetes) es troba a **Processing → GeoArchaeo**. Aquest algorisme pertany al connector GeoArchaeo independent: a PyArchInit el proveïdor de Processing de GeoArchaeo no es registra, de manera que Random Forest no està disponible. Per utilitzar-lo cal el connector GeoArchaeo separat.

---

## Pestanya Mostreig

La pestanya **Mostreig** (*Sampling*, «5. Nous punts de mostreig» / *5. New sampling locations*) suggereix on mostrejar o excavar en el futur a partir dels punts existents i crea una capa amb els punts proposats.

### Criteris de mostreig

| Criteri (entrada de la llista) | Com tria els punts | Quan utilitzar-lo |
|--------------------------------|--------------------|-------------------|
| **«Cobertura (maximin)»** (*Coverage (maximin)*) | Cada punt nou és el més lluny possible de tots els altres | Omplir els buits de manera uniforme |
| **«Reducció de la incertesa (variància de kriging)»** (*Uncertainty reduction (kriging variance)*) | Cada punt nou va on la variància de kriging és màxima | Reduir l'error del kriging on és més gran |
| **«Quadrícula estratificada»** (*Stratified grid*) | Una posició per cel·la d'una quadrícula regular, amb una lleugera pertorbació aleatòria | Cobertura regular d'una àrea definida |
| **«Adaptatiu (zones menys denses)»** (*Adaptive (sparser areas)*) | Extracció aleatòria amb més probabilitat on hi ha pocs punts | Afavorir les zones menys mostrejades mantenint un component aleatori |

El criteri «Reducció de la incertesa» utilitza el variograma calculat si correspon a la mateixa capa i al mateix camp i si a la pestanya Kriging està marcada «Utilitza el variograma calculat»; si no, utilitza un model genèric basat en la distància típica entre els punts.

### Disseny del mostreig

1. Comprovar **«Punts existents:»** (*Existing points:*): és la capa triada a dalt al grup «Dades d'entrada» (per al mostreig no cal el camp numèric)
2. Opcional: triar a **«Àrea d'estudi (polígon, opcional):»** (*Study area (polygon, optional):*) una capa de polígons; tots els seus polígons s'uneixen i es reprojecten al SRC dels punts, encara que la capa estigui en un altre SRC
3. Ajustar **«Nous punts per proposar:»** (*New points to propose:*) (d'1 a 500, 10 per defecte)
4. Triar el **«Criteri:»** (*Criterion:*): sota la llista apareix la seva descripció
5. Fer clic a **«Calcula nous punts»** (*Calculate new points*)

Sense àrea d'estudi, els punts es cerquen al rectangle que conté els punts existents, ampliat un 20 % per cada costat.

<!-- IMAGE: Nous punts de mostreig proposats -->
> **Fig. 9**: Els nous punts de mostreig (estrelles grogues) proposats dins de l'àrea d'estudi

### Resultats del mostreig

- El requadre de resultats indica quants punts s'han proposat i amb quin criteri; a sota, la taula «Coordenades dels punts proposats:» (*Coordinates of the proposed points:*) enumera el número, X i Y
- Es crea la capa de punts temporal `New_sampling_points` (`Nuovi_punti_campionamento` amb el panell en italià), amb símbol d'estrella groga i els camps `point_id`, `x_coord`, `y_coord` i `type` (valor `suggested`)

---

## Pestanya Informe

La pestanya **Informe** (*Report*, «6. Informe» / *6. Report*) reuneix en un sol document les anàlisis fetes durant la sessió: estadístiques, gràfics interactius, paràmetres i validació.

### Contingut de l'informe

Al grup **«Seccions per incloure»** (*Sections to include*), cada secció es marca com a «disponible» (*available*) o «encara no calculat» (*not yet calculated*); les seccions no calculades no es poden triar.

| Secció | Contingut |
|--------|-----------|
| **Estadístiques descriptives** (*Descriptive statistics*) | Capa i camp, taula d'estadístiques amb la lectura en paraules, histograma |
| **Variograma** (*Variogram*) | Model, nugget, sill, range, RMSE, distància màxima, interpretació, gràfic |
| **Kriging i validació creuada** (*Kriging and cross-validation*) | Mètode, mida de cel·la, dimensions de la quadrícula, mètriques de validació creuada, gràfic |
| **Reconeixement de patrons** (*Pattern recognition*) | Capes analitzades, grups amb el seu nombre de punts, gràfic |
| **Nous punts de mostreig** (*New sampling locations*) | Criteri, capa, taula de coordenades |

Cada secció conté l'**última** anàlisi del seu tipus feta durant la sessió.

### Generació de l'informe

1. Fer les anàlisis desitjades a les altres pestanyes
2. Obrir la pestanya **Informe** i deixar marcades les seccions que s'hi vulguin incloure (estan marcades per defecte)
3. Fer clic a **«Desa l'informe HTML»** (*Save HTML report*) o a **«Desa l'informe PDF»** (*Save PDF report*) i triar el nom del fitxer

En desar, el panell mostra també una previsualització de l'informe sense gràfics; la nota «Previsualització: els gràfics interactius s'inclouen al fitxer HTML desat.» (*Preview: the interactive charts are included in the saved HTML file.*) recorda on són.

<!-- IMAGE: Informe HTML de GeoArchaeo obert al navegador -->
> **Fig. 10**: Un informe HTML de GeoArchaeo amb gràfics interactius, obert al navegador

### Exportació

| Format | Contingut | Notes |
|--------|-----------|-------|
| **HTML** (`geoarchaeo_report.html`) | Text, taules i **gràfics interactius** | El fitxer és autònom (la biblioteca de gràfics hi és inclosa i funciona també sense connexió) i s'obre de seguida al navegador |
| **PDF** (`geoarchaeo_report.pdf`) | Text i taules, **sense gràfics** | Si no es pot crear el PDF, desar l'informe HTML i imprimir-lo en PDF des del navegador |

Si no s'ha fet cap anàlisi apareix «Cap anàlisi disponible: executa primer almenys una anàlisi.» (*No analysis available: run at least one analysis first.*); si no hi ha cap secció marcada, «Selecciona almenys una secció» (*Select at least one section*).

---

## Flux de treball operatiu

Un exemple complet amb les dades d'exemple incloses al mòdul (panell en anglès).

### Pas 1: Preparació de les dades

1. Obrir GeoArchaeo des de la barra d'eines de PyArchInit
2. Fer clic a **«Carrega dades d'exemple»** (*Load example data*) i confirmar amb **OK** (es carreguen els GeoPackage i els GeoJSON)
3. Al grup «Dades d'entrada», triar la capa `villa_ceramica` i el camp `ceramic_count`
4. Comprovar el resum: 500 punts vàlids de 500, SRC EPSG:32633

### Pas 2: Exploració de les dades

1. Pestanya **Dades** → **«Calcula estadístiques»** (*Calculate statistics*)
2. Llegir l'asimetria i els valors atípics; amb una forta asimetria a la dreta, valorar una transformació logarítmica

### Pas 3: Anàlisi del variograma

1. Pestanya **Variograma** → **«Auto»** per a la distància màxima, model **«Esfèric (recomanat)»** (*Spherical (recommended)*) → **«Calcula el variograma»** (*Calculate variogram*)
2. Repetir amb **«Exponencial»** (*Exponential*) i comparar el RMSE de l'ajust
3. Opcional: tornar a calcular amb **«Comprova l'anisotropia (variogrames direccionals)»**
4. Calcular en darrer lloc el model triat i anotar el nugget, el sill i el range

### Pas 4: Interpolació

1. Pestanya **Kriging**: comprovar la línia «Variograma disponible … ✓» (*Variogram available … ✓*)
2. Mantenir la mida de cel·la proposada o indicar 1 (metre)
3. **«Executa el kriging»** (*Run kriging*)
4. Examinar els ràsters `Kriging_ceramic_count` i `Kriging_ceramic_count_uncertainty` i els valors de R² i MSDR

### Pas 5: Patrons i mostreig (opcionals)

1. Pestanya **Patrons (ML)**: deixar seleccionada a la llista només `necropoli`, mètode DBSCAN → **«Inicia el reconeixement de patrons»** (*Run pattern recognition*); la capa `ML_groups` mostra els grups de tombes i els punts aïllats
2. A dalt, triar la capa `ricognizione_survey` (camp `densita_mq`); pestanya **Mostreig**: àrea d'estudi `area_studio`, 10 punts, criteri «Cobertura (maximin)» (*Coverage (maximin)*) → **«Calcula nous punts»** (*Calculate new points*)

### Pas 6: Informe

1. Pestanya **Informe**: deixar marcades les seccions disponibles
2. **«Desa l'informe HTML»** (*Save HTML report*): l'informe s'obre al navegador amb els gràfics interactius
3. Exportar els ràsters i les capes temporals que es vulguin conservar

---

## Resolució de problemes

### Problemes comuns

| Problema | Causa | Solució |
|----------|-------|---------|
| «No hi ha cap capa de punts al projecte…» (*No point layer in the project: load one or use the example data.*) | El projecte no té capes de punts | Afegir una capa de punts o utilitzar **«Carrega dades d'exemple»** |
| «La capa no té camps numèrics…» (*The layer has no numeric fields…*) | El camp que s'ha d'analitzar és de text | Convertir-lo en nombre amb la calculadora de camps |
| «Calen almenys 5 punts amb un valor vàlid…» (*At least 5 points with a valid value are required (found …)*) | Massa valors NULL o no numèrics | Revisar la taula d'atributs o triar un altre camp |
| Avís «SRC geogràfic (graus)» (*geographic CRS (degrees)*) | La capa no està en un SRC projectat | Reprojectar la capa, per exemple a UTM, i repetir l'anàlisi |
| Error «No point pairs within the maximum distance…» | Distància màxima del variograma massa petita | Augmentar **«Distància màxima:»** o utilitzar **«Auto»** |
| «No hi ha prou parells per als variogrames direccionals.» (*Not enough pairs for directional variograms.*) | Massa pocs parells per direcció | Augmentar la distància màxima o renunciar a la comprovació de l'anisotropia |
| Kriging lent, petició de confirmació o «Memòria insuficient: augmenta la mida de cel·la.» (*Out of memory: increase the cell size.*) | Quadrícula amb massa cel·les | Augmentar **«Mida de cel·la:»** |
| R² baix a la validació creuada | Poca correlació espacial o massa soroll | Considerar el mapa només orientatiu i consultar el ràster d'incertesa |
| DBSCAN posa gairebé tots els punts a «Aïllats / soroll» (*Isolated / noise*) | Densitat uniforme o massa variables | Provar K-Means o reduir els camps numèrics |
| «Machine Learning features not available. Please install scikit-learn.» | Falta scikit-learn | Instal·lar scikit-learn a l'entorn Python de QGIS |
| «Plotly visualization not available. Please install plotly.» | Falta Plotly | Instal·lar plotly a l'entorn Python de QGIS |
| Gràfic només com a imatge estàtica | QtWebEngine no disponible | Utilitzar **«Obre el gràfic interactiu al navegador»** (*Open interactive chart in browser*) |
| «No es pot crear el PDF…» (*Cannot create the PDF…*) | Error en imprimir el PDF | Desar l'informe HTML i imprimir-lo des del navegador |
| Panell no visible | Panell tancat | Tornar-lo a obrir des de la barra d'eines o el menú pyArchInit: els resultats de la sessió continuen allà |

### Errors freqüents

- **«Ja hi ha una anàlisi en curs…»** (*An analysis is already running: wait for it to finish or cancel it.*): esperar que acabi el càlcul o prémer «Cancel·la»
- **«Anàlisi cancel·lada»** (*Analysis cancelled*): l'anàlisi es va interrompre amb «Cancel·la» i no ha produït resultats
- **«Selecciona almenys una capa»** (*Select at least one layer*, pestanya Patrons): seleccionar almenys una capa a la llista
- **«Selecciona la capa dels punts existents (a dalt)»** (*Select the existing points layer (above)*, pestanya Mostreig): triar la capa al grup «Dades d'entrada»
- **«Selecciona una capa de punts i un camp numèric (a la part superior del panell)»** (*Select a point layer and a numeric field (at the top of the panel)*): completar l'elecció al grup «Dades d'entrada»

### Rendiment

- Les anàlisis s'executen en un **fil d'execució en segon pla**: QGIS continua sent utilitzable i el càlcul es pot cancel·lar
- El variograma utilitza com a màxim 3000 punts (submostra aleatòria) i la validació creuada com a màxim 200
- El kriging utilitza els 20 punts més propers a cada cel·la: el temps depèn sobretot del nombre de cel·les
- La quadrícula està limitada a 500 × 500 cel·les; per sobre de 40.000 cel·les el panell demana confirmació
- Amb conjunts de dades grans (per exemple els 4800 punts de `geofisica_survey`), augmentar la mida de cel·la

---

## Notes tècniques

### Versió i origen

- El mòdul `modules/geoarchaeo/` està alineat amb **GeoArchaeo 1.3.1**, el connector independent d'Enzo Cocca (github.com/enzococca/GeoArchaeo)
- A PyArchInit només hi ha integrat el panell: el proveïdor de Processing de GeoArchaeo (cokriging, kriging espaciotemporal, kriging per blocs, anàlisi composicional, Random Forest) **no** es registra
- El mòdul és compatible amb QGIS 3 (Qt5) i QGIS 4 (Qt6)

### Dependències

| Biblioteca | Ús |
|------------|----|
| **NumPy** | Càlculs numèrics |
| **SciPy** | Ajust dels models de variograma, cerca de veïns (KD-tree), estadístiques |
| **scikit-learn** | K-Means, DBSCAN, Isolation Forest, components principals (necessària per a la pestanya Patrons) |
| **Plotly** | Gràfics interactius al panell i a l'informe HTML |
| **Matplotlib** | Previsualitzacions estàtiques dels gràfics quan falta QtWebEngine |
| **QtWebEngine** (opcional) | Gràfics interactius directament al panell |
| **threadpoolctl** (opcional) | Limita els fils de càlcul durant les anàlisis en segon pla |
| **GDAL** | Escriptura dels ràsters GeoTIFF (inclòs a QGIS) |

### Sistemes de referència

- Les distàncies (distància màxima, range, mida de cel·la) s'expressen en les **unitats del SRC de la capa de punts**
- Cal utilitzar un **SRC projectat** en metres: amb un SRC geogràfic el resum avisa i el variograma i el kriging demanen confirmació
- Els ràsters del kriging i les capes creades utilitzen el SRC de la capa de punts (a la pestanya Patrons, el de la primera capa seleccionada)
- L'àrea d'estudi es reprojecta automàticament al SRC dels punts

### Capes i fitxers generats

| Producte | Tipus | Ubicació |
|----------|-------|----------|
| `Kriging_<camp>`, `Kriging_<camp>_uncertainty` | Ràster GeoTIFF (compressió LZW) | Carpeta temporal del sistema |
| `ML_groups` / `ML_anomalies` | Capa de punts temporal (en memòria) | Només al projecte obert |
| `New_sampling_points` | Capa de punts temporal (en memòria) | Només al projecte obert |
| Informe | HTML o PDF | Camí triat en desar |

Els ràsters i les capes temporals s'han d'exportar (menú contextual de la capa → **Exporta**) per no perdre'ls en tancar el projecte. Els noms de les capes segueixen l'idioma del panell en el moment del càlcul.

### Configuració

- L'idioma del panell es desa a la configuració de QGIS (clau `GeoArchaeo/language`)
- Els resultats es mantenen en memòria mentre QGIS està obert: tancar el panell no els esborra

---

> **Nota**: GeoArchaeo està en desenvolupament continu. Per informar d'errors o suggerir millores, utilitzeu el sistema de seguiment d'incidències (issues) del projecte PyArchInit a GitHub.
