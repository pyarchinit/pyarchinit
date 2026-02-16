# PyArchInit - MoveCost - Analiza Rutelor cu Cel Mai Mic Cost

## Cuprins

1. [Introducere](#introducere)
2. [Accesarea instrumentului](#accesarea-instrumentului)
3. [Cerinte preliminare](#cerinte-preliminare)
4. [Interfata utilizator](#interfata-utilizator)
5. [Fila Algoritmi](#fila-algoritmi)
6. [Fila Rezultate](#fila-rezultate)
7. [Fila Export](#fila-export)
8. [Fila Setari](#fila-setari)
9. [Flux de lucru operational](#flux-de-lucru-operational)
10. [Depanare](#depanare)
11. [Note tehnice](#note-tehnice)

---

## Introducere

**MoveCost** este un instrument autonom din PyArchInit pentru analiza rutelor cu cel mai mic cost (Least-Cost Path Analysis, LCPA) bazat pe scripturi R. Analiza rutelor cu cel mai mic cost este o metodologie fundamentala in arheologia peisajului care permite modelarea celor mai probabile trasee intre locatii, tinand cont de topografia terenului si de costul energetic al deplasarii.

### Istoric

Anterior, functionalitatea MoveCost era integrata direct in formularul de Sit (Site form) din PyArchInit. Incepand cu versiunea actuala, MoveCost a fost extras ca **instrument de analiza independent**, accesibil printr-un QDialog dedicat. Aceasta separare ofera mai multe avantaje:

- **Interfata dedicata**: Un dialog cu 4 file organizate pe functii
- **Organizare mai buna**: Algoritmi, rezultate, export si setari clar separate
- **Acces rapid**: Disponibil din bara de instrumente fara a deschide formularul de Sit
- **Extensibilitate**: Structura modulara care faciliteaza adaugarea de noi algoritmi

### Ce este analiza rutelor cu cel mai mic cost?

Analiza rutelor cu cel mai mic cost calculeaza traseul optim intre doua sau mai multe puncte pe o suprafata de cost derivata dintr-un model digital al terenului (MDT). Costul deplasarii depinde de panta terenului si este calculat folosind functii de cost anizotrope care tin cont de directia miscarii (urcus vs coboras).

<!-- IMAGE: Exemplu de ruta cu cel mai mic cost pe MDT -->
> **Fig. 1**: Exemplu de ruta cu cel mai mic cost calculata pe un model digital al terenului

---

## Accesarea instrumentului

### Din bara de instrumente

1. Localizati butonul derulant **Instrumente de Analiza** (Analysis Tools) in bara de instrumente PyArchInit -- are o pictograma de grafic/analiza
2. Faceti clic pe sageata meniului derulant
3. Selectati **MoveCost** din meniu

<!-- IMAGE: Butonul Instrumente de Analiza in bara de instrumente -->
> **Fig. 2**: Butonul Instrumente de Analiza din bara de instrumente PyArchInit cu meniul derulant deschis

### Fereastra de dialog

La clic, se deschide un **QDialog modal** cu patru file:

```
+-----------------------------------------------------------+
|  MoveCost - Analiza Rutelor cu Cel Mai Mic Cost            |
+-----------------------------------------------------------+
| [Algoritmi] | [Rezultate] | [Export] | [Setari]           |
+-----------------------------------------------------------+
|                                                           |
|              (Continutul filei active)                      |
|                                                           |
+-----------------------------------------------------------+
|                              [Inchide]                     |
+-----------------------------------------------------------+
```

---

## Cerinte preliminare

Inainte de a utiliza MoveCost, verificati ca urmatoarele componente sunt instalate si configurate:

### 1. R (Limbaj statistic)

| Cerinta | Detaliu |
|---------|---------|
| **Software** | R (versiunea >= 4.0 recomandata) |
| **Descarcare** | [https://cran.r-project.org/](https://cran.r-project.org/) |
| **Verificare** | Deschideti un terminal si tastati `R --version` |

### 2. Pachetul R `movecost`

Instalati pachetul din interiorul R:

```r
install.packages("movecost")
```

Dependentele principale sunt instalate automat: `terra`, `gdistance`, `sp`.

### 3. QGIS Processing R Provider

| Cerinta | Detaliu |
|---------|---------|
| **Plugin** | Processing R Provider |
| **Instalare** | QGIS > Plugin-uri > Gestioneaza si instaleaza plugin-uri > Cautati "Processing R Provider" |
| **Configurare** | Setari de procesare > Furnizori > R > Calea folderului R |

### 4. Date de intrare

- **MDT/MDE**: Un raster al modelului digital al terenului pentru zona de studiu
- **Strat de puncte**: Puncte de origine si destinatie pentru analiza
- **Strat de poligoane**: (Optional) Pentru variantele "by polygon" ale algoritmilor

### Lista de verificare rapida

```
+-------------------------------------------+
| Lista de verificare a cerintelor           |
+-------------------------------------------+
| [x] R instalat si in PATH                |
| [x] Pachetul movecost instalat in R      |
| [x] Processing R Provider activ in QGIS  |
| [x] MDT incarcat in proiectul QGIS        |
| [x] Strat de puncte cu origini/destinatii |
+-------------------------------------------+
```

---

## Interfata utilizator

Dialogul MoveCost este organizat in **4 file**, fiecare cu o functie specifica.

### Prezentarea generala a filelor

| Fila | Pictograma | Functie |
|------|------------|---------|
| **Algoritmi** | Roata dintata | Selectarea si rularea celor 14 algoritmi de analiza |
| **Rezultate** | Grafic | Vizualizarea statisticilor de cost si a graficelor R |
| **Export** | Disc | Exportarea rezultatelor in CSV, PDF sau HTML |
| **Setari** | Cheie | Configurarea scripturilor R, limba, organizarea straturilor |

<!-- IMAGE: Prezentarea generala a dialogului MoveCost cu 4 file -->
> **Fig. 3**: Dialogul MoveCost cu cele patru file vizibile

---

## Fila Algoritmi

Fila **Algoritmi** este inima instrumentului MoveCost. Contine **14 algoritmi** bazati pe scripturi R, organizati in **3 grupuri functionale**.

### Grupul 1: Suprafata de cost si trasee

Algoritmi pentru calculul suprafetelor de cost acumulate si al traseelor cu cel mai mic cost.

| Algoritm | Descriere |
|----------|-----------|
| **movecost** | Calculeaza suprafata de cost acumulata anizotropa dependenta de panta si traseele cu cel mai mic cost de la un punct de origine |
| **movecost by polygon** | La fel, dar folosind o zona poligonala pentru a defini extinderea MDT |
| **movebound** | Calculeaza limitele de cost de deplasare dependente de panta in jurul locatiilor punctuale |
| **movebound by polygon** | La fel, dar folosind un poligon |

### Grupul 2: Analiza de coridoare si retele

Algoritmi pentru analiza coridoarelor de cost si a retelelor de trasee optime.

| Algoritm | Descriere |
|----------|-----------|
| **movecorr** | Calculeaza coridorul cu cel mai mic cost intre locatii punctuale |
| **movecorr by polygon** | La fel, dar folosind un poligon |
| **movealloc** | Calculeaza alocarea costului de deplasare dependenta de panta catre origini |
| **movealloc by polygon** | La fel, dar folosind un poligon |
| **movenetw** | Calculeaza reteaua de trasee cu cel mai mic cost intre puncte multiple |
| **movenetw by polygon** | La fel, dar folosind un poligon |

### Grupul 3: Comparatie si clasificare

Algoritmi pentru compararea functiilor de cost si clasificarea destinatiilor.

| Algoritm | Descriere |
|----------|-----------|
| **movecomp** | Compara traseele cu cel mai mic cost generate folosind diferite functii de cost |
| **movecomp by polygon** | La fel, dar folosind un poligon |
| **moverank** | Clasifica destinatiile dupa costul de deplasare de la o origine |
| **moverank by polygon** | La fel, dar folosind un poligon |

### Cum se ruleaza un algoritm

1. Selectati algoritmul dorit din lista
2. Interfata de procesare QGIS se deschide cu parametrii specifici algoritmului
3. Configurati parametrii de intrare:
   - **MDT/MDE**: Selectati rasterul terenului
   - **Punct(e) de origine**: Selectati stratul de puncte
   - **Poligon** (daca este varianta "by polygon"): Selectati zona de studiu
   - **Functia de cost**: Alegeti dintre functiile disponibile (Tobler, Minetti, etc.)
4. Faceti clic pe **Ruleaza**
5. Rezultatele sunt adaugate automat in proiectul QGIS

<!-- IMAGE: Fila Algoritmi cu 3 grupuri -->
> **Fig. 4**: Fila Algoritmi cu cele trei grupuri de algoritmi evidentiate

<!-- IMAGE: Interfata de procesare pentru un algoritm movecost -->
> **Fig. 5**: Interfata de procesare QGIS pentru algoritmul movecost cu parametrii configurati

### Variantele "by polygon"

Variantele "by polygon" ale fiecarui algoritm permit:
- **Limitarea zonei de analiza** la o regiune specifica
- **Reducerea timpului de calcul** prin lucrul pe un MDT decupat
- **Focalizarea analizei** pe o zona de interes arheologic

---

## Fila Rezultate

Fila **Rezultate** permite vizualizarea rezultatelor analizelor executate.

### Rezumatul costurilor (Cost Summary)

O zona de text (QTextEdit) afiseaza statisticile sumare ale straturilor de cost generate:

| Statistica | Descriere |
|------------|-----------|
| **Minim** | Valoarea minima de cost in suprafata |
| **Maxim** | Valoarea maxima de cost in suprafata |
| **Medie** | Valoarea medie de cost |
| **Dev. Standard** | Deviatia standard a valorilor de cost |

```
+---------------------------------------------------+
| Rezumatul costurilor                               |
+---------------------------------------------------+
| Strat: movecost_accumulated_cost                   |
| Minim: 0.00                                        |
| Maxim: 15234.56                                    |
| Medie: 4521.89                                     |
| Dev. Standard: 2103.45                             |
|                                                    |
| Strat: movecost_back_link                          |
| Minim: 0.00                                        |
| Maxim: 8.00                                        |
| Medie: 4.12                                        |
+---------------------------------------------------+
```

### Vizualizatorul de grafice R (R Plot Viewer)

Vizualizatorul de grafice R afiseaza ultimul grafic generat de scripturile R:

| Functie | Descriere |
|---------|-----------|
| **Afisare automata** | Afiseaza ultimul grafic R din directorul temporar |
| **Reimprospatare** | Reincarca ultimul grafic disponibil |
| **Salvare** | Salveaza graficul curent intr-un fisier imagine (PNG, JPG) |
| **Selectare manuala** | Permite deschiderea unui grafic R specific din orice locatie |

<!-- IMAGE: Fila Rezultate cu rezumatul costurilor si grafic R -->
> **Fig. 6**: Fila Rezultate afisand statisticile de cost si un grafic R

### Locatiile graficelor R

Graficele R sunt salvate in directoarele temporare ale QGIS/R. Vizualizatorul cauta automat in urmatoarele locatii:

- Directorul temporar al QGIS Processing
- Directorul temporar al R (`tempdir()`)
- Folderul de iesire specificat de utilizator

---

## Fila Export

Fila **Export** ofera trei optiuni pentru exportarea rezultatelor analizei.

### Exportare tabel de costuri (CSV)

Exporta statisticile straturilor de cost intr-un fisier CSV:

1. Faceti clic pe **Exportare tabel de costuri**
2. Selectati locatia si numele fisierului
3. Fisierul CSV contine: numele stratului, minim, maxim, medie, deviatie standard

| Coloana | Descriere |
|---------|-----------|
| `layer_name` | Numele stratului de cost |
| `min_value` | Valoarea minima |
| `max_value` | Valoarea maxima |
| `mean_value` | Valoarea medie |
| `std_dev` | Deviatia standard |

### Exportare raport (PDF)

> **Nota**: Aceasta functionalitate este in prezent in curs de dezvoltare (stub). Va fi disponibila intr-o versiune viitoare.

### Exportare raport (HTML)

Genereaza un raport HTML complet si stilizat care include:

- **Antet** cu titlul proiectului si data
- **Parametrii analizei** utilizati
- **Statisticile straturilor** in format tabelar
- **Grafice R** incorporate ca imagini
- **Stil CSS integrat** pentru o prezentare profesionala

1. Faceti clic pe **Exportare raport (HTML)**
2. Selectati locatia si numele fisierului
3. Raportul se deschide automat in browserul implicit

<!-- IMAGE: Exemplu de raport HTML exportat -->
> **Fig. 7**: Un exemplu de raport HTML generat de MoveCost cu statistici si grafice

---

## Fila Setari

Fila **Setari** permite configurarea instrumentului MoveCost.

### Instalare scripturi R

| Functie | Descriere |
|---------|-----------|
| **Instalare scripturi R** | Copiaza scripturile R movecost in directorul de procesare al QGIS |

Aceasta operatiune este necesara la **prima configurare** sau dupa o actualizare a plugin-ului. Scripturile sunt copiate in folderul de scripturi R al Processing:

```
{QGIS_HOME}/processing/rscripts/
```

### Selectarea limbii

MoveCost suporta **5 limbi** pentru interfata:

| Limba | Cod |
|-------|-----|
| English | en |
| Italiano | it |
| Francais | fr |
| Espanol | es |
| Deutsch | de |

Limba selectata se aplica la:
- Etichetele interfetei dialogului
- Mesajele de stare si eroare
- Antetele tabelelor de rezultate

### Organizarea straturilor

| Functie | Descriere |
|---------|-----------|
| **Organizeaza straturi** | Organizare si stilizare automata a straturilor de iesire movecost |

Aceasta functie:
1. Grupeaza straturile de iesire in grupuri logice in panoul Straturi al QGIS
2. Aplica stiluri de culoare predefinite (rampe de culoare pentru suprafetele de cost)
3. Redenumeste straturile cu nume descriptive

### Documentatie

| Functie | Descriere |
|---------|-----------|
| **Ajutor** | Deschide documentatia incorporata a instrumentului |

<!-- IMAGE: Fila Setari cu toate optiunile -->
> **Fig. 8**: Fila Setari a MoveCost cu optiunile de configurare

---

## Flux de lucru operational

### Exemplu pas cu pas: Calculul unei rute cu cel mai mic cost

Acest exemplu arata cum se calculeaza o ruta cu cel mai mic cost intre o asezare si o sursa de apa.

### Pasul 1: Pregatirea datelor

```
1. Incarcati MDT-ul zonei de studiu in proiectul QGIS
2. Creati un strat de puncte cu:
   - Punct de origine (asezare)
   - Punct(e) de destinatie (sursa de apa)
3. Verificati ca sistemul de referinta al coordonatelor este consistent
```

### Pasul 2: Verificarea cerintelor

```
1. Deschideti MoveCost din bara de instrumente
2. Mergeti la fila Setari
3. Faceti clic pe "Instalare scripturi R" (daca este prima data)
4. Verificati ca nu sunt raportate erori
```

### Pasul 3: Executarea analizei

```
1. Comutati la fila Algoritmi
2. Selectati "movecost" din Grupul 1
3. In fereastra de procesare:
   - MDT: selectati rasterul terenului
   - Origine: selectati punctul asezarii
   - Destinatie: selectati punctul sursei de apa
   - Functia de cost: Tobler (recomandata implicit)
4. Faceti clic pe Ruleaza
5. Asteptati finalizarea procesarii
```

### Pasul 4: Analiza rezultatelor

```
1. Comutati la fila Rezultate
2. Consultati Rezumatul costurilor pentru statistici
3. Examinati graficul R pentru vizualizare
4. In canvasul QGIS, observati:
   - Suprafata de cost acumulata (raster colorat)
   - Ruta cu cel mai mic cost (linie vectoriala)
```

### Pasul 5: Export

```
1. Comutati la fila Export
2. Exportati tabelul de costuri in CSV pentru analize suplimentare
3. Generati raportul HTML pentru documentatie
4. Salvati graficul R din fila Rezultate
```

### Pasul 6: Organizare

```
1. Reveniti la fila Setari
2. Faceti clic pe "Organizeaza straturi" pentru a sorta rezultatele
3. Straturile sunt grupate si stilizate automat
```

<!-- IMAGE: Fluxul de lucru complet cu capturi de ecran adnotate -->
> **Fig. 9**: Fluxul de lucru complet de la pregatirea datelor la rezultatele finale

---

## Depanare

### R nu este gasit

**Simptom**: Mesaj de eroare "R nu este gasit" sau "R is not installed"

**Solutii**:
1. Verificati ca R este instalat: deschideti un terminal si tastati `R --version`
2. Verificati calea R in setarile de Processing:
   - **QGIS** > **Setari** > **Optiuni** > **Procesare** > **Furnizori** > **R**
   - Setati **calea folderului R** corect
3. Pe macOS, R poate fi localizat la `/Library/Frameworks/R.framework/Resources/`
4. Pe Windows, de obicei la `C:\Program Files\R\R-4.x.x\`
5. Pe Linux, verificati cu `which R`

### Scripturi R lipsa

**Simptom**: Algoritmii nu apar in caseta de instrumente de procesare

**Solutii**:
1. Deschideti MoveCost > Setari > faceti clic pe **Instalare scripturi R**
2. Reporniti QGIS dupa instalarea scripturilor
3. Verificati ca Processing R Provider este activ:
   - **QGIS** > **Plugin-uri** > **Gestioneaza si instaleaza plugin-uri** > Verificati "Processing R Provider"
4. Verificati folderul de scripturi R: `{QGIS_HOME}/processing/rscripts/`

### Graficele R nu se afiseaza

**Simptom**: Fila Rezultate nu afiseaza niciun grafic

**Solutii**:
1. Faceti clic pe **Reimprospatare** in fila Rezultate
2. Utilizati **Selectare manuala** pentru a naviga la folderul graficelor
3. Verificati ca analiza s-a finalizat cu succes
4. Verificati directoarele temporare:
   - macOS/Linux: `/tmp/` sau `$TMPDIR`
   - Windows: `%TEMP%`
5. Unii algoritmi pot sa nu genereze grafice

### Pachetul movecost nu este instalat in R

**Simptom**: Eroare "there is no package called 'movecost'"

**Solutii**:
1. Deschideti R sau RStudio
2. Rulati: `install.packages("movecost")`
3. Verificati: `library(movecost)` -- nu trebuie sa produca erori
4. Daca exista probleme de dependente: `install.packages("movecost", dependencies = TRUE)`

### Analiza foarte lenta

**Simptom**: Procesarea dureaza foarte mult

**Solutii**:
1. Utilizati variantele **"by polygon"** pentru a limita zona de calcul
2. Reduceti rezolutia MDT (reeantionare)
3. Verificati dimensiunile MDT:
   - MDT-urile foarte mari (>10000x10000 pixeli) necesita timp considerabil
   - Decupati MDT-ul la zona de interes inainte de analiza
4. Inchideti alte aplicatii pentru a elibera RAM

### Eroare de proiectie / CRS

**Simptom**: Rezultate inconsistente sau eroare de sistem de referinta al coordonatelor

**Solutii**:
1. Verificati ca MDT-ul si straturile de puncte au **acelasi CRS**
2. Utilizati un **CRS proiectat** (metric), nu geografic
3. CRS recomandate: UTM (de ex. EPSG:32632 pentru Italia centrala)
4. Reproiectati straturile daca este necesar inainte de analiza

---

## Note tehnice

### Arhitectura instrumentului

MoveCost este implementat ca un **QDialog** autonom (`MoveCostDialog`) care:
- Se interfateaza cu QGIS Processing Framework pentru executia algoritmilor R
- Citeste rezultatele din straturile incarcate in proiect
- Gestioneaza vizualizarea graficelor R prin QLabel/QPixmap
- Genereaza rapoarte HTML folosind sabloane predefinite

### Fisiere sursa

| Fisier | Descriere |
|--------|-----------|
| `tabs/MoveCost.py` | Dialogul principal si logica interfetei |
| `gui/ui/MoveCost.ui` | Aspectul interfetei Qt Designer |
| `resources/r_scripts/` | Scripturi R pentru algoritmii movecost |

### Functii de cost suportate

Pachetul R `movecost` suporta mai multe functii de cost anizotrope:

| Functie | Autor | Descriere |
|---------|-------|-----------|
| **Tobler** | Tobler (1993) | Functia clasica de cost al mersului |
| **Minetti** | Minetti et al. (2002) | Bazata pe costul metabolic |
| **Herzog** | Herzog (2010) | Varianta modificata |
| **Llobera-Sluckin** | Llobera & Sluckin (2007) | Model energetic |
| **Altele** | Diversi | Consultati documentatia pachetului R |

### Referinte bibliografice

- Alberti, G. (2019). `movecost`: An R package for calculating accumulated slope-dependent anisotropic cost-surfaces and least-cost paths. *SoftwareX*, 10, 100601.
- Tobler, W. (1993). Three presentations on geographical analysis and modeling. *NCGIA Technical Report*, 93-1.
- Minetti, A.E. et al. (2002). Energy cost of walking and running at extreme uphill and downhill slopes. *Journal of Applied Physiology*, 93(3), 1039-1046.

### Compatibilitate

| Component | Versiune minima |
|-----------|----------------|
| PyArchInit | 5.0.x |
| QGIS | 3.22+ |
| R | 4.0+ |
| Pachetul movecost (R) | 1.0+ |
| Processing R Provider | 2.0+ |

---

## Tutorial video

### MoveCost - Analiza Rutelor cu Cel Mai Mic Cost
`[Marcaj: video_movecost.mp4]`

**Continut**:
- Configurarea R si a pachetului movecost
- Instalarea scripturilor R in QGIS
- Rularea algoritmului movecost de baza
- Vizualizarea rezultatelor si a graficelor R
- Exportarea rapoartelor

**Durata estimata**: 20-25 minute

---

*Documentatie PyArchInit - MoveCost*
*Versiunea: 5.0.x*
*Ultima actualizare: Februarie 2026*
