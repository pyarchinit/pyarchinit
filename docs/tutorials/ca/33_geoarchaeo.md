# PyArchInit - GeoArchaeo - Analisi Geoestadistica

## Index
1. [Introduccio](#introduccio)
2. [Acces a l'eina](#acces-a-leina)
3. [Interficie d'usuari](#interficie-dusuari)
4. [Pestanya Dades](#pestanya-dades)
5. [Pestanya Variograma](#pestanya-variograma)
6. [Pestanya Kriging](#pestanya-kriging)
7. [Pestanya Machine Learning](#pestanya-machine-learning)
8. [Pestanya Mostreig](#pestanya-mostreig)
9. [Pestanya Informe](#pestanya-informe)
10. [Flux de treball operatiu](#flux-de-treball-operatiu)
11. [Resolucio de problemes](#resolucio-de-problemes)
12. [Notes tecniques](#notes-tecniques)

---

## Introduccio

**GeoArchaeo** es el modul d'analisi geoestadistica integrat a PyArchInit. Proporciona un conjunt complet d'eines per a l'analisi espacial de dades arqueologiques, des de la modelitzacio de variogrames fins a la interpolacio kriging, passant per les prediccions amb aprenentatge automatic i el disseny d'estrategies de mostreig.

<!-- VIDEO: Introduccio a GeoArchaeo -->
> **Video Tutorial**: [Inserir enllac de video introduccio GeoArchaeo]

### Per que l'analisi geoestadistica en arqueologia?

L'analisi geoestadistica permet:

- **Interpolar** valors entre punts de mostreig coneguts, creant superficies continues a partir de dades discretes
- **Quantificar** la correlacio espacial en les dades arqueologiques (p.ex. densitat de troballes, gruix d'estrats)
- **Predir** distribucions espacials en arees encara no excavades
- **Optimitzar** les estrategies de mostreig per a prospeccions futures
- **Generar** informes analitics complets per a la documentacio cientifica

### Visio general del flux de treball

```
1. Carregar dades       2. Variograma          3. Kriging/ML
   (Pestanya Dades)        (Pestanya Variograma)  (Pestanya Kriging/ML)
        |                      |                      |
   Seleccionar capa       Calcular i modelar     Interpolacio o
   i camps                variograma             prediccio espacial
                               |                      |
                          4. Mostreig            5. Informe
                             (Pestanya Mostreig)    (Pestanya Informe)
                                  |                      |
                             Dissenyar            Generar informe
                             estrategia           d'analisi
```

---

## Acces a l'eina

GeoArchaeo es accessible des de la barra d'eines de PyArchInit a traves del boto desplegable d'Eines d'Analisi.

### Des de la barra d'eines

1. Localitzar el boto **Eines d'Analisi** (icona desplegable) a la barra d'eines de PyArchInit
2. Fer clic a la fletxa del menu desplegable
3. Seleccionar **GeoArchaeo** de la llista

<!-- IMAGE: Boto Eines d'Analisi a la barra d'eines -->
> **Fig. 1**: El menu desplegable Eines d'Analisi a la barra d'eines de PyArchInit

El panell GeoArchaeo apareix com un **widget acoblable** a la interficie de QGIS. Es pot arrossegar, redimensionar o desacoblar com qualsevol altre panell de QGIS.

<!-- IMAGE: Panell GeoArchaeo acoblat a QGIS -->
> **Fig. 2**: El panell GeoArchaeo acoblat a la finestra de QGIS

### Selector d'idioma

El panell GeoArchaeo inclou un **selector d'idioma** a la part superior, que permet canviar l'idioma de la interficie sense reiniciar QGIS. Els idiomes suportats inclouen italia, angles, alemany, frances, castella, arab, catala, romanes, portugues i grec.

---

## Interficie d'usuari

El panell GeoArchaeo esta organitzat en **6 pestanyes principals**, cadascuna dedicada a una fase del flux de treball d'analisi geoestadistica.

| Pestanya | Icona | Funcio |
|----------|-------|--------|
| **Dades** | Taula | Carregar i explorar dades espacials des de capes QGIS |
| **Variograma** | Grafic | Calcular i modelar variogrames experimentals |
| **Kriging** | Quadricula | Realitzar interpolacio kriging (ordinari, universal) |
| **ML** | Cervell | Prediccions espacials amb aprenentatge automatic |
| **Mostreig** | Diana | Dissenyar estrategies de mostreig per a prospeccions arqueologiques |
| **Informe** | Document | Generar informes d'analisi |

<!-- IMAGE: Visio general de les 6 pestanyes de GeoArchaeo -->
> **Fig. 3**: Les sis pestanyes del panell GeoArchaeo

### Barra d'eines del panell

A la part superior del panell es troben:

- **Selector d'idioma**: Menu desplegable per canviar l'idioma de la interficie
- **Carregar dades d'exemple**: Boto per carregar un conjunt de dades de prova
- **Ajuda**: Boto per accedir a la documentacio

---

## Pestanya Dades

La pestanya **Dades** es el punt de partida per a qualsevol analisi geoestadistica. Permet carregar i visualitzar les dades espacials disponibles a les capes QGIS.

### Carrega de dades

1. Obrir la pestanya **Dades**
2. Seleccionar una **capa vectorial** del menu desplegable (es llisten totes les capes de punts del projecte QGIS)
3. Seleccionar el **camp d'analisi** (el camp numeric a analitzar)
4. Fer clic a **Carregar dades**

<!-- IMAGE: Pestanya Dades amb capa i camp seleccionats -->
> **Fig. 4**: La pestanya Dades amb una capa i un camp d'analisi seleccionats

### Dades d'exemple

Per familiaritzar-se amb l'eina, es possible carregar un **conjunt de dades d'exemple** fent clic al boto dedicat. El conjunt de dades d'exemple conte dades arqueologiques simulades amb coordenades i valors numerics adequats per a l'analisi geoestadistica.

### Exploracio de dades

Despres de la carrega, la pestanya mostra:

| Informacio | Descripcio |
|------------|------------|
| **Nombre de punts** | Total de punts carregats |
| **Extensio** | Caixa envoltant del conjunt de dades (xmin, ymin, xmax, ymax) |
| **Estadistiques** | Mitjana, mediana, desviacio estandard, min, max |
| **Vista previa** | Taula amb les primeres files del conjunt de dades |

### Requisits de les dades

- La capa ha de ser una **capa vectorial de punts**
- El camp d'analisi ha de contenir **valors numerics**
- Els punts han de tenir **coordenades valides** en el sistema de referencia del projecte
- Es recomanen almenys **30 punts** per a una analisi geoestadistica significativa

---

## Pestanya Variograma

La pestanya **Variograma** permet calcular i modelar variogrames experimentals, que descriuen l'estructura de la correlacio espacial en les dades.

### Que es un variograma?

Un variograma es un grafic que mostra com la **varianca** entre parells de punts canvia en funcio de la **distancia** que els separa. Els parametres clau son:

| Parametre | Descripcio |
|-----------|------------|
| **Nugget** | Varianca a distancia zero (error de mesura + variabilitat a microescala) |
| **Sill** | Varianca maxima assolida (altipla del variograma) |
| **Range** | Distancia mes enlla de la qual no hi ha correlacio espacial |

### Calcul del variograma experimental

1. Assegurar-se d'haver carregat les dades a la pestanya Dades
2. Obrir la pestanya **Variograma**
3. Configurar els parametres:
   - **Nombre de lags**: Nombre d'intervals de distancia (per defecte: 15)
   - **Distancia maxima**: Distancia maxima a considerar (per defecte: auto)
   - **Tolerancia angular**: Per a variogrames direccionals (per defecte: omnidireccional)
4. Fer clic a **Calcular variograma**

<!-- IMAGE: Variograma experimental calculat -->
> **Fig. 5**: Un variograma experimental calculat a partir de dades arqueologiques

### Modelitzacio del variograma

Despres de calcular el variograma experimental, es possible ajustar un **model teoric**:

1. Seleccionar el **tipus de model**:
   - **Esferic**: El model mes comu, arriba al sill a una distancia finita
   - **Exponencial**: Arriba al sill asimptoticament
   - **Gaussia**: Transicio gradual, adequat per a fenomens molt regulars
   - **Lineal**: Variograma sense sill definit
2. Fer clic a **Ajustar model**
3. Verificar els parametres estimats (nugget, sill, range) i la bondat d'ajust

<!-- IMAGE: Model de variograma ajustat -->
> **Fig. 6**: Model esferic ajustat al variograma experimental

### Variogrames direccionals

Per verificar l'**anisotropia** (variacio de l'estructura espacial en diferents direccions):

1. Establir una **tolerancia angular** (p.ex. 22,5 graus)
2. Seleccionar les **direccions** a analitzar (0, 45, 90, 135 graus)
3. Comparar els variogrames en les diferents direccions

---

## Pestanya Kriging

La pestanya **Kriging** permet realitzar la interpolacio kriging, el metode geoestadistic de referencia per a la prediccio espacial optima.

### Tipus de kriging disponibles

| Tipus | Descripcio | Quan usar-lo |
|-------|------------|-------------|
| **Kriging ordinari** | Assumeix una mitjana local constant pero desconeguda | Cas mes comu, dades estacionaries |
| **Kriging universal** | Te en compte una tendencia espacial (deriva) | Quan les dades mostren una tendencia direccional |

### Execucio del kriging

1. Assegurar-se d'haver modelat el variograma a la pestanya Variograma
2. Obrir la pestanya **Kriging**
3. Seleccionar el **tipus de kriging** (ordinari o universal)
4. Configurar els parametres de la quadricula de sortida:
   - **Resolucio**: Mida de les cel.les de la quadricula (en unitats del CRS)
   - **Extensio**: Automatica des del conjunt de dades o personalitzada
5. Configurar els parametres del kriging:
   - **Punts minims**: Nombre minim de punts propers a usar
   - **Punts maxims**: Nombre maxim de punts propers a usar
   - **Radi de cerca**: Distancia maxima per als punts propers
6. Fer clic a **Executar kriging**

<!-- IMAGE: Resultat de la interpolacio kriging -->
> **Fig. 7**: Mapa d'interpolacio kriging amb la quadricula de prediccio

### Resultats del kriging

L'analisi produeix dues capes raster:

- **Prediccio**: Els valors interpolats a la quadricula
- **Varianca de kriging**: La incertesa de la prediccio a cada cel.la

Les capes s'afegeixen automaticament al projecte QGIS i es mostren al mapa.

> **Nota**: L'analisi s'executa en un **fil en segon pla**, de manera que la interficie de QGIS roman utilitzable durant el calcul. Una barra de progres indica l'estat del processament.

---

## Pestanya Machine Learning

La pestanya **ML** ofereix metodes d'aprenentatge automatic per a prediccions espacials, com a alternativa o complement al kriging.

### Algoritmes disponibles

| Algoritme | Descripcio | Avantatges |
|-----------|------------|-----------|
| **Random Forest** | Conjunt d'arbres de decisio | Robust, gestiona relacions no lineals |
| **Gradient Boosting** | Arbres de decisio sequencials | Alta precisio, adequat per a patrons complexos |
| **SVR** | Regressio per vectors de suport | Bo amb poques dades, kernels flexibles |

### Flux de treball ML

1. Obrir la pestanya **ML**
2. Seleccionar l'**algoritme** desitjat
3. Configurar les **variables predictores**:
   - Coordenades (X, Y)
   - Camps addicionals de la capa (p.ex. elevacio, pendent, distancia a un riu)
4. Establir els **parametres** de l'algoritme (o usar els valors per defecte)
5. Seleccionar el metode de **validacio**:
   - Validacio creuada k-fold (per defecte: 5 folds)
   - Hold-out (percentatge de prova)
6. Fer clic a **Entrenar model**

<!-- IMAGE: Configuracio del model ML -->
> **Fig. 8**: Configuracio d'un model Random Forest a la pestanya ML

### Resultats ML

| Resultat | Descripcio |
|----------|------------|
| **Mapa de prediccio** | Capa raster amb els valors predits |
| **Importancia de variables** | Grafic de la importancia relativa de les variables predictores |
| **Metriques de validacio** | R-quadrat, RMSE, MAE de la validacio creuada |
| **Grafic de residus** | Diagrama de dispersio de valors observats vs predits |

### Comparacio Kriging vs ML

Per comparar resultats:

1. Executar tant el kriging com el ML amb les mateixes dades
2. Comparar les metriques de validacio a la pestanya Informe
3. Visualitzar mapes de diferencies

---

## Pestanya Mostreig

La pestanya **Mostreig** permet dissenyar estrategies de mostreig optimes per a prospeccions arqueologiques futures.

### Estrategies de mostreig

| Estrategia | Descripcio | Quan usar-la |
|------------|------------|-------------|
| **Aleatori simple** | Punts distribuits aleatoriament a l'area | Quan no es disposa d'informacio previa |
| **Aleatori estratificat** | Punts aleatoris dins d'estrats definits | Quan l'area te zones amb caracteristiques diferents |
| **Quadricula regular** | Punts en una quadricula regular | Per a cobertura uniforme de l'area |
| **Optimitzat** | Punts posicionats per minimitzar la varianca de kriging | Quan es disposa d'un variograma |

### Disseny del pla de mostreig

1. Obrir la pestanya **Mostreig**
2. Seleccionar l'**estrategia** de mostreig
3. Establir el **nombre de punts** desitjat
4. Definir l'**area d'estudi**:
   - Des de l'extensio de la capa actual
   - Des d'una capa poligonal
   - Dibuixant manualment sobre el mapa
5. Establir possibles **restriccions**:
   - Distancia minima entre punts
   - Arees d'exclusio
6. Fer clic a **Generar mostreig**

<!-- IMAGE: Punts de mostreig generats -->
> **Fig. 9**: Punts de mostreig optimitzat superposats al mapa de l'area d'estudi

### Resultats del mostreig

- Una **capa vectorial de punts** amb els punts de mostreig s'afegeix al projecte QGIS
- Una **taula d'atributs** amb les coordenades i identificadors dels punts
- Un **informe** amb les estadistiques de l'estrategia (cobertura, distancies, etc.)

---

## Pestanya Informe

La pestanya **Informe** permet generar informes complets de l'analisi geoestadistica.

### Contingut de l'informe

L'informe inclou automaticament totes les analisis realitzades durant la sessio:

| Seccio | Contingut |
|--------|-----------|
| **Resum** | Visio general del conjunt de dades i les analisis realitzades |
| **Dades** | Estadistiques descriptives, distribucio, mapa de punts |
| **Variograma** | Variograma experimental, model, parametres |
| **Interpolacio** | Mapa de kriging/ML, metriques de validacio |
| **Mostreig** | Estrategia, mapa de punts, estadistiques |
| **Conclusions** | Interpretacio sintetica dels resultats |

### Generacio de l'informe

1. Obrir la pestanya **Informe**
2. Seleccionar les **seccions** a incloure (totes per defecte)
3. Establir el **format de sortida**:
   - PDF (recomanat per a documentacio)
   - HTML (per a consulta interactiva)
   - Markdown (per a edicio posterior)
4. Introduir possibles **notes addicionals** o comentaris
5. Fer clic a **Generar informe**

<!-- IMAGE: Vista previa de l'informe generat -->
> **Fig. 10**: Vista previa d'un informe d'analisi geoestadistica generat per GeoArchaeo

### Exportacio

L'informe pot guardar-se localment o exportar-se en els formats disponibles. Les imatges (grafics, mapes) s'incorporen directament a l'informe.

---

## Flux de treball operatiu

A continuacio es presenta un flux de treball tipic per a una analisi geoestadistica completa a GeoArchaeo:

### Pas 1: Preparacio de dades

1. Carregar la capa vectorial de punts a QGIS
2. Verificar que el camp numeric a analitzar es present i correcte
3. Comprovar el sistema de referencia de coordenades

### Pas 2: Exploracio de dades

1. Obrir GeoArchaeo des de la barra d'eines
2. A la pestanya **Dades**, seleccionar la capa i el camp
3. Examinar les estadistiques descriptives
4. Verificar la distribucio de les dades (cercar valors atipics o anomals)

### Pas 3: Analisi del variograma

1. A la pestanya **Variograma**, calcular el variograma experimental
2. Provar diferents models (esferic, exponencial, gaussia)
3. Triar el model amb el millor ajust
4. Anotar els parametres (nugget, sill, range)

### Pas 4: Interpolacio

1. A la pestanya **Kriging**, configurar els parametres de la quadricula
2. Executar el kriging ordinari
3. Examinar el mapa de prediccio i la varianca
4. Opcionalment, comparar amb un model ML a la pestanya ML

### Pas 5: Mostreig (opcional)

1. A la pestanya **Mostreig**, dissenyar una estrategia per a prospeccions futures
2. Utilitzar el variograma per al mostreig optimitzat

### Pas 6: Informe

1. A la pestanya **Informe**, generar l'informe final
2. Exportar en PDF per a documentacio

---

## Resolucio de problemes

### Problemes comuns

| Problema | Causa | Solucio |
|----------|-------|---------|
| No hi ha capes disponibles | No hi ha capes de punts al projecte | Afegir una capa vectorial de punts al projecte QGIS |
| No hi ha camps numerics | La capa no te camps numerics | Verificar la taula d'atributs de la capa |
| Variograma pla | Dades sense correlacio espacial | Verificar les dades, augmentar la distancia maxima |
| El kriging falla | Model de variograma no ajustat | Ajustar primer un model a la pestanya Variograma |
| Mals resultats ML | Dades insuficients o variables no informatives | Afegir variables predictores o augmentar les dades |
| Panell no visible | Widget tancat accidentalment | Reobrir des del menu Eines d'Analisi |

### Errors frequents

- **"Dades insuficients"**: Calen almenys 30 punts per a una analisi fiable
- **"Model de variograma no definit"**: Ajustar un model abans d'executar el kriging
- **"CRS incompatible"**: Totes les capes han d'usar el mateix sistema de referencia

### Rendiment

- L'analisi s'executa en un **fil en segon pla**: la interficie de QGIS roman utilitzable
- Per a conjunts de dades molt grans (>10.000 punts), el processament pot trigar mes
- Es possible monitoritzar el progres mitjancant la barra a la part inferior del panell

---

## Notes tecniques

### Dependencies

GeoArchaeo utilitza les seguents biblioteques Python:

| Biblioteca | Us |
|-----------|---|
| **NumPy** | Calculs numerics i matricials |
| **SciPy** | Optimitzacio i ajust de models |
| **scikit-learn** | Algoritmes d'aprenentatge automatic |
| **Matplotlib** | Generacio de grafics |

### Sistemes de referencia

- GeoArchaeo treballa en el sistema de referencia del projecte QGIS actual
- Es recomana un **CRS projectat** (en metres) per a l'analisi geoestadistica
- Els sistemes geografics (en graus) poden produir resultats imprecisos

### Exportacio de resultats

Els resultats poden exportar-se en diversos formats:

- **Capes raster** (GeoTIFF) per a superficies interpolades
- **Capes vectorials** (GeoPackage, Shapefile) per a punts de mostreig
- **Grafics** (PNG, SVG) per a variogrames i diagnostics
- **Informes** (PDF, HTML, Markdown) per a documentacio

### Integracio amb QGIS

- Les capes de sortida s'afegeixen automaticament al panell de **Capes** de QGIS
- L'estil de les capes raster pot personalitzar-se amb les propietats de capa de QGIS
- Els resultats son compatibles amb totes les eines d'analisi espacial de QGIS

---

> **Nota**: GeoArchaeo esta en desenvolupament actiu. Per reportar errors o suggerir millores, utilitzeu el sistema de seguiment d'incidencies del projecte PyArchInit a GitHub.
