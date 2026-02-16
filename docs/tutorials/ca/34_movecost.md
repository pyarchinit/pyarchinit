# PyArchInit - MoveCost - Analisi de Camins de Menor Cost

## Index

1. [Introduccio](#introduccio)
2. [Acces a l'eina](#acces-a-leina)
3. [Prerequisits](#prerequisits)
4. [Interficie d'usuari](#interficie-dusuari)
5. [Pestanya Algorismes](#pestanya-algorismes)
6. [Pestanya Resultats](#pestanya-resultats)
7. [Pestanya Exportacio](#pestanya-exportacio)
8. [Pestanya Configuracio](#pestanya-configuracio)
9. [Flux de treball operatiu](#flux-de-treball-operatiu)
10. [Resolucio de problemes](#resolucio-de-problemes)
11. [Notes tecniques](#notes-tecniques)

---

## Introduccio

**MoveCost** es una eina autonoma de PyArchInit per a l'analisi de camins de menor cost (Least-Cost Path Analysis, LCPA) basada en scripts R. L'analisi de camins de menor cost es una metodologia fonamental en arqueologia del paisatge que permet modelar les rutes mes probables entre localitzacions, tenint en compte la topografia del terreny i el cost energetic del moviment.

### Historia

Anteriorment, la funcionalitat MoveCost estava integrada directament al formulari de Jaciment (Site form) de PyArchInit. A partir de la versio actual, MoveCost s'ha extret com a **eina d'analisi independent**, accessible a traves d'un QDialog dedicat. Aquesta separacio ofereix diversos avantatges:

- **Interficie dedicada**: Un dialeg amb 4 pestanyes organitzades per funcio
- **Millor organitzacio**: Algorismes, resultats, exportacio i configuracio clarament separats
- **Acces rapid**: Disponible des de la barra d'eines sense obrir el formulari de Jaciment
- **Extensibilitat**: Estructura modular que facilita l'addicio de nous algorismes

### Que es l'analisi de camins de menor cost?

L'analisi de camins de menor cost calcula el cami optim entre dos o mes punts sobre una superficie de cost derivada d'un model digital del terreny (MDT). El cost del moviment depen del pendent del terreny i es calcula utilitzant funcions de cost anisotropiques que tenen en compte la direccio del moviment (pujada vs baixada).

<!-- IMAGE: Exemple de cami de menor cost sobre MDT -->
> **Fig. 1**: Exemple de cami de menor cost calculat sobre un model digital del terreny

---

## Acces a l'eina

### Des de la barra d'eines

1. Localitzar el boto desplegable **Eines d'Analisi** (Analysis Tools) a la barra d'eines de PyArchInit -- te una icona de grafic/analisi
2. Fer clic a la fletxa del menu desplegable
3. Seleccionar **MoveCost** del menu

<!-- IMAGE: Boto Eines d'Analisi a la barra d'eines -->
> **Fig. 2**: El boto Eines d'Analisi a la barra d'eines de PyArchInit amb el menu desplegable obert

### Finestra de dialeg

En fer clic, s'obre un **QDialog modal** amb quatre pestanyes:

```
+-----------------------------------------------------------+
|  MoveCost - Analisi de Camins de Menor Cost                |
+-----------------------------------------------------------+
| [Algorismes] | [Resultats] | [Exportacio] | [Configuracio]|
+-----------------------------------------------------------+
|                                                           |
|              (Contingut de la pestanya activa)              |
|                                                           |
+-----------------------------------------------------------+
|                              [Tancar]                      |
+-----------------------------------------------------------+
```

---

## Prerequisits

Abans d'utilitzar MoveCost, verificar que els seguents components estan instal.lats i configurats:

### 1. R (Llenguatge estadistic)

| Prerequisit | Detall |
|-------------|--------|
| **Programari** | R (versio >= 4.0 recomanada) |
| **Descarrega** | [https://cran.r-project.org/](https://cran.r-project.org/) |
| **Verificacio** | Obrir un terminal i escriure `R --version` |

### 2. Paquet R `movecost`

Instal.lar el paquet des de R:

```r
install.packages("movecost")
```

Dependencies principals instal.lades automaticament: `terra`, `gdistance`, `sp`.

### 3. QGIS Processing R Provider

| Prerequisit | Detall |
|-------------|--------|
| **Complement** | Processing R Provider |
| **Instal.lacio** | QGIS > Complements > Gestiona i instal.la complements > Cercar "Processing R Provider" |
| **Configuracio** | Opcions de processament > Proveidor > R > Cami de la carpeta R |

### 4. Dades d'entrada

- **MDT/MDE**: Un raster del model digital del terreny per a l'area d'estudi
- **Capa de punts**: Punts d'origen i destinacio per a l'analisi
- **Capa de poligons**: (Opcional) Per a les variants "by polygon" dels algorismes

### Llista de verificacio rapida

```
+-------------------------------------------+
| Llista de verificacio de prerequisits      |
+-------------------------------------------+
| [x] R instal.lat i al PATH               |
| [x] Paquet movecost instal.lat a R       |
| [x] Processing R Provider actiu a QGIS   |
| [x] MDT carregat al projecte QGIS         |
| [x] Capa de punts amb origens/destinac.   |
+-------------------------------------------+
```

---

## Interficie d'usuari

El dialeg MoveCost esta organitzat en **4 pestanyes**, cadascuna amb una funcio especifica.

### Vista general de les pestanyes

| Pestanya | Icona | Funcio |
|----------|-------|--------|
| **Algorismes** | Engranatge | Seleccionar i executar els 14 algorismes d'analisi |
| **Resultats** | Grafic | Visualitzar estadistiques de cost i grafics R |
| **Exportacio** | Disc | Exportar resultats a CSV, PDF o HTML |
| **Configuracio** | Clau anglesa | Configurar scripts R, idioma, organitzacio de capes |

<!-- IMAGE: Vista general del dialeg MoveCost amb 4 pestanyes -->
> **Fig. 3**: El dialeg MoveCost amb les quatre pestanyes visibles

---

## Pestanya Algorismes

La pestanya **Algorismes** es el nucli de l'eina MoveCost. Conte **14 algorismes** basats en scripts R, organitzats en **3 grups funcionals**.

### Grup 1: Superficie de cost i camins

Algorismes per al calcul de superficies de cost acumulades i camins de menor cost.

| Algorisme | Descripcio |
|-----------|------------|
| **movecost** | Calcula la superficie de cost acumulada anisotropica depenent del pendent i els camins de menor cost des d'un punt d'origen |
| **movecost by polygon** | El mateix, pero utilitzant una area poligonal per definir l'extensio del MDT |
| **movebound** | Calcula els limits de cost de desplacament depenents del pendent al voltant de localitzacions puntuals |
| **movebound by polygon** | El mateix, pero utilitzant un poligon |

### Grup 2: Analisi de corredors i xarxes

Algorismes per a l'analisi de corredors de cost i xarxes de camins optims.

| Algorisme | Descripcio |
|-----------|------------|
| **movecorr** | Calcula el corredor de menor cost entre localitzacions puntuals |
| **movecorr by polygon** | El mateix, pero utilitzant un poligon |
| **movealloc** | Calcula l'assignacio de cost de desplacament depenent del pendent als origens |
| **movealloc by polygon** | El mateix, pero utilitzant un poligon |
| **movenetw** | Calcula la xarxa de camins de menor cost entre multiples punts |
| **movenetw by polygon** | El mateix, pero utilitzant un poligon |

### Grup 3: Comparacio i classificacio

Algorismes per comparar funcions de cost i classificar destinacions.

| Algorisme | Descripcio |
|-----------|------------|
| **movecomp** | Compara camins de menor cost generats utilitzant diferents funcions de cost |
| **movecomp by polygon** | El mateix, pero utilitzant un poligon |
| **moverank** | Classifica les destinacions per cost de desplacament des d'un origen |
| **moverank by polygon** | El mateix, pero utilitzant un poligon |

### Com executar un algorisme

1. Seleccionar l'algorisme desitjat de la llista
2. La interficie de processament de QGIS s'obre amb els parametres especifics de l'algorisme
3. Configurar els parametres d'entrada:
   - **MDT/MDE**: Seleccionar el raster del terreny
   - **Punt/s d'origen**: Seleccionar la capa de punts
   - **Poligon** (si es variant "by polygon"): Seleccionar l'area d'estudi
   - **Funcio de cost**: Triar entre les funcions disponibles (Tobler, Minetti, etc.)
4. Fer clic a **Executa**
5. Els resultats s'afegeixen automaticament al projecte QGIS

<!-- IMAGE: Pestanya Algorismes amb 3 grups -->
> **Fig. 4**: La pestanya Algorismes amb els tres grups d'algorismes destacats

<!-- IMAGE: Interficie de processament per a un algorisme movecost -->
> **Fig. 5**: La interficie de processament de QGIS per a l'algorisme movecost amb els parametres configurats

### Variants "by polygon"

Les variants "by polygon" de cada algorisme permeten:
- **Limitar l'area d'analisi** a una regio especifica
- **Reduir el temps de calcul** treballant amb un MDT retallat
- **Focalitzar l'analisi** en una area d'interes arqueologic

---

## Pestanya Resultats

La pestanya **Resultats** permet visualitzar els resultats de les analisis executades.

### Resum de costos (Cost Summary)

Una area de text (QTextEdit) mostra les estadistiques resumides de les capes de cost generades:

| Estadistica | Descripcio |
|-------------|------------|
| **Minim** | Valor minim de cost a la superficie |
| **Maxim** | Valor maxim de cost a la superficie |
| **Mitjana** | Valor mitja de cost |
| **Desv. Estandard** | Desviacio estandard dels valors de cost |

```
+---------------------------------------------------+
| Resum de costos                                    |
+---------------------------------------------------+
| Capa: movecost_accumulated_cost                    |
| Minim: 0.00                                        |
| Maxim: 15234.56                                    |
| Mitjana: 4521.89                                   |
| Desv. Estandard: 2103.45                           |
|                                                    |
| Capa: movecost_back_link                           |
| Minim: 0.00                                        |
| Maxim: 8.00                                        |
| Mitjana: 4.12                                      |
+---------------------------------------------------+
```

### Visualitzador de grafics R (R Plot Viewer)

El visualitzador de grafics R mostra l'ultim grafic generat pels scripts R:

| Funcio | Descripcio |
|--------|------------|
| **Visualitzacio automatica** | Mostra l'ultim grafic R del directori temporal |
| **Actualitzar** | Recarrega l'ultim grafic disponible |
| **Desar** | Desa el grafic actual en un fitxer d'imatge (PNG, JPG) |
| **Seleccio manual** | Permet obrir un grafic R especific des de qualsevol ubicacio |

<!-- IMAGE: Pestanya Resultats amb resum de costos i grafic R -->
> **Fig. 6**: La pestanya Resultats mostrant les estadistiques de cost i un grafic R

### Ubicacions dels grafics R

Els grafics R es desen als directoris temporals de QGIS/R. El visualitzador cerca automaticament a les seguents ubicacions:

- Directori temporal de QGIS Processing
- Directori temporal de R (`tempdir()`)
- Carpeta de sortida especificada per l'usuari

---

## Pestanya Exportacio

La pestanya **Exportacio** ofereix tres opcions per exportar els resultats de l'analisi.

### Exportar taula de costos (CSV)

Exporta les estadistiques de les capes de cost a un fitxer CSV:

1. Fer clic a **Exportar taula de costos**
2. Seleccionar la ubicacio i el nom del fitxer
3. El fitxer CSV conte: nom de capa, minim, maxim, mitjana, desviacio estandard

| Columna | Descripcio |
|---------|------------|
| `layer_name` | Nom de la capa de cost |
| `min_value` | Valor minim |
| `max_value` | Valor maxim |
| `mean_value` | Valor mitja |
| `std_dev` | Desviacio estandard |

### Exportar informe (PDF)

> **Nota**: Aquesta funcionalitat esta actualment en fase de desenvolupament (stub). Estara disponible en una versio futura.

### Exportar informe (HTML)

Genera un informe HTML complet i estilitzat que inclou:

- **Capcalera** amb titol del projecte i data
- **Parametres de l'analisi** utilitzats
- **Estadistiques de les capes** en format tabular
- **Grafics R** incrustats com a imatges
- **Estil CSS integrat** per a una presentacio professional

1. Fer clic a **Exportar informe (HTML)**
2. Seleccionar la ubicacio i el nom del fitxer
3. L'informe s'obre automaticament al navegador predeterminat

<!-- IMAGE: Exemple d'informe HTML exportat -->
> **Fig. 7**: Un exemple d'informe HTML generat per MoveCost amb estadistiques i grafics

---

## Pestanya Configuracio

La pestanya **Configuracio** permet configurar l'eina MoveCost.

### Instal.lar scripts R

| Funcio | Descripcio |
|--------|------------|
| **Instal.lar scripts R** | Copia els scripts R de movecost al directori de processament de QGIS |

Aquesta operacio es necessaria a la **primera configuracio** o despres d'una actualitzacio del complement. Els scripts es copien a la carpeta d'scripts R del Processing:

```
{QGIS_HOME}/processing/rscripts/
```

### Seleccio d'idioma

MoveCost admet **5 idiomes** per a la interficie:

| Idioma | Codi |
|--------|------|
| English | en |
| Italiano | it |
| Francais | fr |
| Espanol | es |
| Deutsch | de |

L'idioma seleccionat s'aplica a:
- Etiquetes de la interficie del dialeg
- Missatges d'estat i error
- Capcaleres de les taules de resultats

### Organitzacio de capes

| Funcio | Descripcio |
|--------|------------|
| **Organitzar capes** | Organitzacio i estilitzacio automatica de les capes de sortida de movecost |

Aquesta funcio:
1. Agrupa les capes de sortida en grups logics al panell de Capes de QGIS
2. Aplica estils de color predefinits (rampes de color per a superficies de cost)
3. Reanomena les capes amb noms descriptius

### Documentacio

| Funcio | Descripcio |
|--------|------------|
| **Ajuda** | Obre la documentacio en linia de l'eina |

<!-- IMAGE: Pestanya Configuracio amb totes les opcions -->
> **Fig. 8**: La pestanya Configuracio de MoveCost amb les opcions de configuracio

---

## Flux de treball operatiu

### Exemple pas a pas: Calcul d'un cami de menor cost

Aquest exemple mostra com calcular un cami de menor cost entre un assentament i una font d'aigua.

### Pas 1: Preparacio de dades

```
1. Carregar el MDT de l'area d'estudi al projecte QGIS
2. Crear una capa de punts amb:
   - Punt d'origen (assentament)
   - Punt/s de destinacio (font d'aigua)
3. Verificar que el sistema de referencia de coordenades es consistent
```

### Pas 2: Verificacio de prerequisits

```
1. Obrir MoveCost des de la barra d'eines
2. Anar a la pestanya Configuracio
3. Fer clic a "Instal.lar scripts R" (si es la primera vegada)
4. Verificar que no es reporten errors
```

### Pas 3: Execucio de l'analisi

```
1. Canviar a la pestanya Algorismes
2. Seleccionar "movecost" del Grup 1
3. A la finestra de processament:
   - MDT: seleccionar el raster del terreny
   - Origen: seleccionar el punt de l'assentament
   - Destinacio: seleccionar el punt de la font d'aigua
   - Funcio de cost: Tobler (recomanada per defecte)
4. Fer clic a Executa
5. Esperar que es completi el processament
```

### Pas 4: Analisi dels resultats

```
1. Canviar a la pestanya Resultats
2. Revisar el Resum de costos per a les estadistiques
3. Examinar el grafic R per a la visualitzacio
4. Al llenC de QGIS, observar:
   - La superficie de cost acumulada (raster acolorit)
   - El cami de menor cost (linia vectorial)
```

### Pas 5: Exportacio

```
1. Canviar a la pestanya Exportacio
2. Exportar la taula de costos a CSV per a analisis addicionals
3. Generar l'informe HTML per a la documentacio
4. Desar el grafic R des de la pestanya Resultats
```

### Pas 6: Organitzacio

```
1. Tornar a la pestanya Configuracio
2. Fer clic a "Organitzar capes" per ordenar els resultats
3. Les capes s'agrupen i estilitzen automaticament
```

<!-- IMAGE: Flux de treball complet amb captures de pantalla anotades -->
> **Fig. 9**: El flux de treball complet des de la preparacio de dades fins als resultats finals

---

## Resolucio de problemes

### R no trobat

**Simptoma**: Missatge d'error "R no trobat" o "R is not installed"

**Solucions**:
1. Verificar que R esta instal.lat: obrir un terminal i escriure `R --version`
2. Comprovar el cami de R a la configuracio de Processing:
   - **QGIS** > **Configuracio** > **Opcions** > **Processament** > **Proveidor** > **R**
   - Establir el **cami de la carpeta R** correctament
3. A macOS, R pot trobar-se a `/Library/Frameworks/R.framework/Resources/`
4. A Windows, normalment a `C:\Program Files\R\R-4.x.x\`
5. A Linux, verificar amb `which R`

### Scripts R absents

**Simptoma**: Els algorismes no apareixen a la caixa d'eines de processament

**Solucions**:
1. Obrir MoveCost > Configuracio > fer clic a **Instal.lar scripts R**
2. Reiniciar QGIS despres d'instal.lar els scripts
3. Verificar que el Processing R Provider esta actiu:
   - **QGIS** > **Complements** > **Gestiona i instal.la complements** > Verificar "Processing R Provider"
4. Comprovar la carpeta d'scripts R: `{QGIS_HOME}/processing/rscripts/`

### Grafics R no es mostren

**Simptoma**: La pestanya Resultats no mostra cap grafic

**Solucions**:
1. Fer clic a **Actualitzar** a la pestanya Resultats
2. Utilitzar **Seleccio manual** per navegar a la carpeta de grafics
3. Verificar que l'analisi s'ha completat amb exit
4. Comprovar els directoris temporals:
   - macOS/Linux: `/tmp/` o `$TMPDIR`
   - Windows: `%TEMP%`
5. Alguns algorismes poden no generar grafics

### Paquet movecost no instal.lat a R

**Simptoma**: Error "there is no package called 'movecost'"

**Solucions**:
1. Obrir R o RStudio
2. Executar: `install.packages("movecost")`
3. Verificar: `library(movecost)` -- no ha de produir errors
4. Si hi ha problemes de dependencies: `install.packages("movecost", dependencies = TRUE)`

### Analisi molt lenta

**Simptoma**: El processament triga molt de temps

**Solucions**:
1. Utilitzar les variants **"by polygon"** per limitar l'area de calcul
2. Reduir la resolucio del MDT (remostreig)
3. Comprovar les dimensions del MDT:
   - MDT molt grans (>10000x10000 pixels) requereixen temps considerable
   - Retallar el MDT a l'area d'interes abans de l'analisi
4. Tancar altres aplicacions per alliberar RAM

### Error de projeccio / SRC

**Simptoma**: Resultats inconsistents o error de sistema de referencia de coordenades

**Solucions**:
1. Verificar que el MDT i les capes de punts tenen el **mateix SRC**
2. Utilitzar un **SRC projectat** (metric), no geografic
3. SRC recomanats: UTM (p.ex. EPSG:32632 per a Italia central)
4. Reprojectar les capes si es necessari abans de l'analisi

---

## Notes tecniques

### Arquitectura de l'eina

MoveCost esta implementat com un **QDialog** autonom (`MoveCostDialog`) que:
- S'interfasa amb el QGIS Processing Framework per a l'execucio d'algorismes R
- Llegeix els resultats de les capes carregades al projecte
- Gestiona la visualitzacio de grafics R mitjancant QLabel/QPixmap
- Genera informes HTML utilitzant plantilles predefinides

### Fitxers font

| Fitxer | Descripcio |
|--------|------------|
| `tabs/MoveCost.py` | Dialeg principal i logica de la interficie |
| `gui/ui/MoveCost.ui` | Disseny de la interficie Qt Designer |
| `resources/r_scripts/` | Scripts R per als algorismes movecost |

### Funcions de cost suportades

El paquet R `movecost` suporta diverses funcions de cost anisotropiques:

| Funcio | Autor | Descripcio |
|--------|-------|------------|
| **Tobler** | Tobler (1993) | Funcio de cost de marxa classica |
| **Minetti** | Minetti et al. (2002) | Basada en el cost metabolic |
| **Herzog** | Herzog (2010) | Variant modificada |
| **Llobera-Sluckin** | Llobera & Sluckin (2007) | Model energetic |
| **Altres** | Diversos | Consulteu la documentacio del paquet R |

### Referencias bibliografiques

- Alberti, G. (2019). `movecost`: An R package for calculating accumulated slope-dependent anisotropic cost-surfaces and least-cost paths. *SoftwareX*, 10, 100601.
- Tobler, W. (1993). Three presentations on geographical analysis and modeling. *NCGIA Technical Report*, 93-1.
- Minetti, A.E. et al. (2002). Energy cost of walking and running at extreme uphill and downhill slopes. *Journal of Applied Physiology*, 93(3), 1039-1046.

### Compatibilitat

| Component | Versio minima |
|-----------|--------------|
| PyArchInit | 5.0.x |
| QGIS | 3.22+ |
| R | 4.0+ |
| Paquet movecost (R) | 1.0+ |
| Processing R Provider | 2.0+ |

---

## Tutorial en video

### MoveCost - Analisi de Camins de Menor Cost
`[Marcador: video_movecost.mp4]`

**Contingut**:
- Configuracio de R i el paquet movecost
- Instal.lacio dels scripts R a QGIS
- Execucio de l'algorisme movecost basic
- Visualitzacio de resultats i grafics R
- Exportacio d'informes

**Durada estimada**: 20-25 minuts

---

*Documentacio PyArchInit - MoveCost*
*Versio: 5.0.x*
*Ultima actualitzacio: Febrer 2026*
