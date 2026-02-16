# PyArchInit - GeoArchaeo - Analiza Geostatistica

## Cuprins
1. [Introducere](#introducere)
2. [Accesarea instrumentului](#accesarea-instrumentului)
3. [Interfata utilizatorului](#interfata-utilizatorului)
4. [Fila Date](#fila-date)
5. [Fila Variograma](#fila-variograma)
6. [Fila Kriging](#fila-kriging)
7. [Fila Machine Learning](#fila-machine-learning)
8. [Fila Esantionare](#fila-esantionare)
9. [Fila Raport](#fila-raport)
10. [Fluxul de lucru operational](#fluxul-de-lucru-operational)
11. [Depanare](#depanare)
12. [Note tehnice](#note-tehnice)

---

## Introducere

**GeoArchaeo** este modulul de analiza geostatistica integrat in PyArchInit. Ofera un set complet de instrumente pentru analiza spatiala a datelor arheologice, de la modelarea variogramelor la interpolarea kriging, predictii cu invatare automata si proiectarea strategiilor de esantionare.

<!-- VIDEO: Introducere in GeoArchaeo -->
> **Tutorial video**: [Inserati link video introducere GeoArchaeo]

### De ce analiza geostatistica in arheologie?

Analiza geostatistica permite:

- **Interpolarea** valorilor intre punctele de esantionare cunoscute, creand suprafete continue din date discrete
- **Cuantificarea** corelatiei spatiale in datele arheologice (de ex. densitatea descoperirilor, grosimea straturilor)
- **Predictia** distributiilor spatiale in zonele inca neexcavate
- **Optimizarea** strategiilor de esantionare pentru prospectiuni viitoare
- **Generarea** de rapoarte analitice complete pentru documentatia stiintifica

### Prezentare generala a fluxului de lucru

```
1. Incarca date          2. Variograma          3. Kriging/ML
   (Fila Date)              (Fila Variograma)      (Fila Kriging/ML)
        |                      |                      |
   Selecteaza strat       Calculeaza si          Interpolare sau
   si campuri             modeleaza variograma   predictie spatiala
                               |                      |
                          4. Esantionare         5. Raport
                             (Fila Esantionare)     (Fila Raport)
                                  |                      |
                             Proiecteaza          Genereaza raport
                             strategia            de analiza
```

---

## Accesarea instrumentului

GeoArchaeo este accesibil din bara de instrumente PyArchInit prin butonul derulant Instrumente de Analiza.

### Din bara de instrumente

1. Localizati butonul **Instrumente de Analiza** (pictograma derulanta) in bara de instrumente PyArchInit
2. Faceti clic pe sageata meniului derulant
3. Selectati **GeoArchaeo** din lista

<!-- IMAGE: Butonul Instrumente de Analiza in bara de instrumente -->
> **Fig. 1**: Meniul derulant Instrumente de Analiza din bara de instrumente PyArchInit

Panoul GeoArchaeo apare ca un **widget andocabil** in interfata QGIS. Poate fi tras, redimensionat sau detasat ca orice alt panou QGIS.

<!-- IMAGE: Panoul GeoArchaeo andocat in QGIS -->
> **Fig. 2**: Panoul GeoArchaeo andocat in fereastra QGIS

### Selectorul de limba

Panoul GeoArchaeo include un **selector de limba** in partea de sus, care permite schimbarea limbii interfetei fara a reporni QGIS. Limbile acceptate includ italiana, engleza, germana, franceza, spaniola, araba, catalana, romana, portugheza si greaca.

---

## Interfata utilizatorului

Panoul GeoArchaeo este organizat in **6 file principale**, fiecare dedicata unei faze a fluxului de lucru de analiza geostatistica.

| Fila | Pictograma | Functie |
|------|-----------|---------|
| **Date** | Tabel | Incarcarea si explorarea datelor spatiale din straturile QGIS |
| **Variograma** | Grafic | Calcularea si modelarea variogramelor experimentale |
| **Kriging** | Grila | Efectuarea interpolarii kriging (ordinar, universal) |
| **ML** | Creier | Predictii spatiale cu invatare automata |
| **Esantionare** | Tinta | Proiectarea strategiilor de esantionare pentru prospectiuni arheologice |
| **Raport** | Document | Generarea rapoartelor de analiza |

<!-- IMAGE: Prezentare generala a celor 6 file GeoArchaeo -->
> **Fig. 3**: Cele sase file ale panoului GeoArchaeo

### Bara de instrumente a panoului

In partea de sus a panoului veti gasi:

- **Selector de limba**: Meniu derulant pentru schimbarea limbii interfetei
- **Incarca date exemplu**: Buton pentru incarcarea unui set de date de test
- **Ajutor**: Buton pentru accesarea documentatiei

---

## Fila Date

Fila **Date** este punctul de pornire pentru orice analiza geostatistica. Permite incarcarea si vizualizarea datelor spatiale disponibile in straturile QGIS.

### Incarcarea datelor

1. Deschideti fila **Date**
2. Selectati un **strat vectorial** din meniul derulant (sunt listate toate straturile de puncte din proiectul QGIS)
3. Selectati **campul de analiza** (campul numeric de analizat)
4. Faceti clic pe **Incarca date**

<!-- IMAGE: Fila Date cu strat si camp selectate -->
> **Fig. 4**: Fila Date cu un strat si un camp de analiza selectate

### Date exemplu

Pentru a va familiariza cu instrumentul, puteti incarca un **set de date exemplu** facand clic pe butonul dedicat. Setul de date exemplu contine date arheologice simulate cu coordonate si valori numerice adecvate pentru analiza geostatistica.

### Explorarea datelor

Dupa incarcare, fila afiseaza:

| Informatie | Descriere |
|------------|-----------|
| **Numar de puncte** | Totalul punctelor incarcate |
| **Extensie** | Caseta de incadrare a setului de date (xmin, ymin, xmax, ymax) |
| **Statistici** | Medie, mediana, deviatie standard, min, max |
| **Previzualizare** | Tabel cu primele randuri ale setului de date |

### Cerinte privind datele

- Stratul trebuie sa fie un **strat vectorial de puncte**
- Campul de analiza trebuie sa contina **valori numerice**
- Punctele trebuie sa aiba **coordonate valide** in sistemul de referinta al proiectului
- Se recomanda cel putin **30 de puncte** pentru o analiza geostatistica semnificativa

---

## Fila Variograma

Fila **Variograma** permite calcularea si modelarea variogramelor experimentale, care descriu structura corelatiei spatiale in date.

### Ce este o variograma?

O variograma este un grafic care arata cum **varianta** intre perechi de puncte se schimba in functie de **distanta** dintre ele. Parametrii cheie sunt:

| Parametru | Descriere |
|-----------|-----------|
| **Nugget** | Varianta la distanta zero (eroare de masurare + variabilitate la microscara) |
| **Sill** | Varianta maxima atinsa (platoul variogramei) |
| **Range** | Distanta dincolo de care nu mai exista corelatie spatiala |

### Calcularea variogramei experimentale

1. Asigurati-va ca ati incarcat datele in fila Date
2. Deschideti fila **Variograma**
3. Setati parametrii:
   - **Numar de lag-uri**: Numarul intervalelor de distanta (implicit: 15)
   - **Distanta maxima**: Distanta maxima de luat in considerare (implicit: auto)
   - **Toleranta unghiulara**: Pentru variograme directionale (implicit: omnidirectional)
4. Faceti clic pe **Calculeaza variograma**

<!-- IMAGE: Variograma experimentala calculata -->
> **Fig. 5**: O variograma experimentala calculata din date arheologice

### Modelarea variogramei

Dupa calcularea variogramei experimentale, puteti ajusta un **model teoretic**:

1. Selectati **tipul de model**:
   - **Sferic**: Cel mai comun model, atinge sill-ul la o distanta finita
   - **Exponential**: Atinge sill-ul asimptotic
   - **Gaussian**: Tranzitie graduala, potrivit pentru fenomene foarte regulate
   - **Linear**: Variograma fara sill definit
2. Faceti clic pe **Ajusteaza model**
3. Verificati parametrii estimati (nugget, sill, range) si calitatea ajustarii

<!-- IMAGE: Model de variograma ajustat -->
> **Fig. 6**: Model sferic ajustat la variograma experimentala

### Variograme directionale

Pentru a verifica **anizotropia** (variatia structurii spatiale in directii diferite):

1. Setati o **toleranta unghiulara** (de ex. 22,5 grade)
2. Selectati **directiile** de analizat (0, 45, 90, 135 grade)
3. Comparati variogramele in directii diferite

---

## Fila Kriging

Fila **Kriging** permite efectuarea interpolarii kriging, metoda geostatistica de referinta pentru predictia spatiala optima.

### Tipuri de kriging disponibile

| Tip | Descriere | Cand se utilizeaza |
|-----|-----------|-------------------|
| **Kriging ordinar** | Presupune o medie locala constanta dar necunoscuta | Cazul cel mai comun, date stationare |
| **Kriging universal** | Tine cont de o tendinta spatiala (deriva) | Cand datele prezinta o tendinta directionala |

### Executarea kriging-ului

1. Asigurati-va ca ati modelat variograma in fila Variograma
2. Deschideti fila **Kriging**
3. Selectati **tipul de kriging** (ordinar sau universal)
4. Setati parametrii grilei de iesire:
   - **Rezolutie**: Dimensiunea celulelor grilei (in unitati CRS)
   - **Extensie**: Automata din setul de date sau personalizata
5. Setati parametrii kriging-ului:
   - **Puncte minime**: Numarul minim de puncte vecine de utilizat
   - **Puncte maxime**: Numarul maxim de puncte vecine de utilizat
   - **Raza de cautare**: Distanta maxima pentru punctele vecine
6. Faceti clic pe **Executa kriging**

<!-- IMAGE: Rezultatul interpolarii kriging -->
> **Fig. 7**: Harta de interpolare kriging cu grila de predictie

### Rezultatele kriging-ului

Analiza produce doua straturi raster:

- **Predictie**: Valorile interpolate pe grila
- **Varianta kriging**: Incertitudinea predictiei in fiecare celula

Straturile sunt adaugate automat in proiectul QGIS si afisate pe harta.

> **Nota**: Analiza ruleaza intr-un **fir de executie in fundal**, astfel incat interfata QGIS ramane utilizabila in timpul calculului. O bara de progres indica starea procesarii.

---

## Fila Machine Learning

Fila **ML** ofera metode de invatare automata pentru predictii spatiale, ca alternativa sau complement la kriging.

### Algoritmi disponibili

| Algoritm | Descriere | Avantaje |
|----------|-----------|----------|
| **Random Forest** | Ansamblu de arbori de decizie | Robust, gestioneaza relatii neliniare |
| **Gradient Boosting** | Arbori de decizie secventiali | Precizie ridicata, potrivit pentru tipare complexe |
| **SVR** | Regresie cu vectori suport | Bun cu putine date, nuclee flexibile |

### Fluxul de lucru ML

1. Deschideti fila **ML**
2. Selectati **algoritmul** dorit
3. Configurati **variabilele predictoare**:
   - Coordonate (X, Y)
   - Campuri suplimentare din strat (de ex. altitudine, panta, distanta fata de un rau)
4. Setati **parametrii** algoritmului (sau utilizati valorile implicite)
5. Selectati metoda de **validare**:
   - Validare incrucisata k-fold (implicit: 5 fold-uri)
   - Hold-out (procentaj de test)
6. Faceti clic pe **Antreneaza model**

<!-- IMAGE: Configurarea modelului ML -->
> **Fig. 8**: Configurarea unui model Random Forest in fila ML

### Rezultate ML

| Rezultat | Descriere |
|----------|-----------|
| **Harta de predictie** | Strat raster cu valorile prezise |
| **Importanta variabilelor** | Grafic al importantei relative a variabilelor predictoare |
| **Metrici de validare** | R-patrat, RMSE, MAE din validarea incrucisata |
| **Grafic rezidual** | Diagrama de dispersie a valorilor observate vs prezise |

### Comparatie Kriging vs ML

Pentru a compara rezultatele:

1. Executati atat kriging-ul cat si ML pe aceleasi date
2. Comparati metricile de validare in fila Raport
3. Vizualizati harti de diferente

---

## Fila Esantionare

Fila **Esantionare** permite proiectarea strategiilor optime de esantionare pentru prospectiuni arheologice viitoare.

### Strategii de esantionare

| Strategie | Descriere | Cand se utilizeaza |
|-----------|-----------|-------------------|
| **Aleatorie simpla** | Puncte distribuite aleatoriu in zona | Cand nu exista informatii prealabile |
| **Aleatorie stratificata** | Puncte aleatorii in straturi definite | Cand zona are sectoare cu caracteristici diferite |
| **Grila regulata** | Puncte pe o grila regulata | Pentru acoperire uniforma a zonei |
| **Optimizata** | Puncte pozitionate pentru minimizarea variantei kriging | Cand se dispune de o variograma |

### Proiectarea planului de esantionare

1. Deschideti fila **Esantionare**
2. Selectati **strategia** de esantionare
3. Setati **numarul de puncte** dorit
4. Definiti **zona de studiu**:
   - Din extensia stratului curent
   - Dintr-un strat poligonal
   - Desenand manual pe harta
5. Setati eventuale **constrangeri**:
   - Distanta minima intre puncte
   - Zone de excludere
6. Faceti clic pe **Genereaza esantionare**

<!-- IMAGE: Puncte de esantionare generate -->
> **Fig. 9**: Puncte de esantionare optimizata suprapuse pe harta zonei de studiu

### Rezultatele esantionarii

- Un **strat vectorial de puncte** cu punctele de esantionare este adaugat in proiectul QGIS
- Un **tabel de atribute** cu coordonatele si identificatorii punctelor
- Un **raport** cu statisticile strategiei (acoperire, distante, etc.)

---

## Fila Raport

Fila **Raport** permite generarea de rapoarte complete ale analizei geostatistice.

### Continutul raportului

Raportul include automat toate analizele efectuate in timpul sesiunii:

| Sectiune | Continut |
|----------|---------|
| **Rezumat** | Prezentare generala a setului de date si analizelor efectuate |
| **Date** | Statistici descriptive, distributie, harta punctelor |
| **Variograma** | Variograma experimentala, model, parametri |
| **Interpolare** | Harta kriging/ML, metrici de validare |
| **Esantionare** | Strategie, harta punctelor, statistici |
| **Concluzii** | Interpretarea sintetica a rezultatelor |

### Generarea raportului

1. Deschideti fila **Raport**
2. Selectati **sectiunile** de inclus (toate implicit)
3. Setati **formatul de iesire**:
   - PDF (recomandat pentru documentatie)
   - HTML (pentru consultare interactiva)
   - Markdown (pentru editare ulterioara)
4. Introduceti eventuale **note suplimentare** sau comentarii
5. Faceti clic pe **Genereaza raport**

<!-- IMAGE: Previzualizare raport generat -->
> **Fig. 10**: Previzualizare a unui raport de analiza geostatistica generat de GeoArchaeo

### Export

Raportul poate fi salvat local sau exportat in formatele disponibile. Imaginile (grafice, harti) sunt incorporate direct in raport.

---

## Fluxul de lucru operational

Iata un flux de lucru tipic pentru o analiza geostatistica completa in GeoArchaeo:

### Pasul 1: Pregatirea datelor

1. Incarcati stratul vectorial de puncte in QGIS
2. Verificati ca campul numeric de analizat este prezent si corect
3. Verificati sistemul de referinta al coordonatelor

### Pasul 2: Explorarea datelor

1. Deschideti GeoArchaeo din bara de instrumente
2. In fila **Date**, selectati stratul si campul
3. Examinati statisticile descriptive
4. Verificati distributia datelor (cautati valori aberante sau anomale)

### Pasul 3: Analiza variogramei

1. In fila **Variograma**, calculati variograma experimentala
2. Incercati diferite modele (sferic, exponential, gaussian)
3. Alegeti modelul cu cel mai bun ajustaj
4. Notati parametrii (nugget, sill, range)

### Pasul 4: Interpolarea

1. In fila **Kriging**, setati parametrii grilei
2. Executati kriging-ul ordinar
3. Examinati harta de predictie si varianta
4. Optional, comparati cu un model ML in fila ML

### Pasul 5: Esantionare (optional)

1. In fila **Esantionare**, proiectati o strategie pentru prospectiuni viitoare
2. Utilizati variograma pentru esantionarea optimizata

### Pasul 6: Raport

1. In fila **Raport**, generati raportul final
2. Exportati in PDF pentru documentatie

---

## Depanare

### Probleme comune

| Problema | Cauza | Solutie |
|----------|-------|---------|
| Nu sunt straturi disponibile | Nu exista straturi de puncte in proiect | Adaugati un strat vectorial de puncte in proiectul QGIS |
| Nu sunt campuri numerice | Stratul nu are campuri numerice | Verificati tabelul de atribute al stratului |
| Variograma plata | Date fara corelatie spatiala | Verificati datele, cresteti distanta maxima |
| Kriging-ul esueaza | Modelul variogramei nu este ajustat | Ajustati mai intai un model in fila Variograma |
| Rezultate ML slabe | Date insuficiente sau variabile neinformative | Adaugati variabile predictoare sau cresteti datele |
| Panoul nu este vizibil | Widget inchis accidental | Redeschideti din meniul Instrumente de Analiza |

### Erori frecvente

- **"Date insuficiente"**: Sunt necesare cel putin 30 de puncte pentru o analiza fiabila
- **"Modelul variogramei nu este definit"**: Ajustati un model inainte de a executa kriging-ul
- **"CRS incompatibil"**: Toate straturile trebuie sa utilizeze acelasi sistem de referinta

### Performanta

- Analiza ruleaza intr-un **fir de executie in fundal**: interfata QGIS ramane utilizabila
- Pentru seturi de date foarte mari (>10.000 de puncte), procesarea poate dura mai mult
- Progresul poate fi monitorizat prin bara din partea de jos a panoului

---

## Note tehnice

### Dependente

GeoArchaeo utilizeaza urmatoarele biblioteci Python:

| Biblioteca | Utilizare |
|-----------|----------|
| **NumPy** | Calcule numerice si matriciale |
| **SciPy** | Optimizare si ajustarea modelelor |
| **scikit-learn** | Algoritmi de invatare automata |
| **Matplotlib** | Generarea graficelor |

### Sisteme de referinta

- GeoArchaeo lucreaza in sistemul de referinta al proiectului QGIS curent
- Se recomanda un **CRS proiectat** (in metri) pentru analiza geostatistica
- Sistemele geografice (in grade) pot produce rezultate imprecise

### Exportul rezultatelor

Rezultatele pot fi exportate in diverse formate:

- **Straturi raster** (GeoTIFF) pentru suprafete interpolate
- **Straturi vectoriale** (GeoPackage, Shapefile) pentru puncte de esantionare
- **Grafice** (PNG, SVG) pentru variograme si diagnostice
- **Rapoarte** (PDF, HTML, Markdown) pentru documentatie

### Integrarea cu QGIS

- Straturile de iesire sunt adaugate automat in panoul **Straturi** al QGIS
- Stilul straturilor raster poate fi personalizat prin proprietatile de strat QGIS
- Rezultatele sunt compatibile cu toate instrumentele de analiza spatiala QGIS

---

> **Nota**: GeoArchaeo este in dezvoltare activa. Pentru a raporta erori sau a sugera imbunatatiri, utilizati sistemul de urmarire a problemelor al proiectului PyArchInit pe GitHub.
