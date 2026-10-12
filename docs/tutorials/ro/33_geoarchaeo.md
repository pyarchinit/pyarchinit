# PyArchInit - GeoArchaeo - Analiză Geostatistică

## Cuprins
1. [Introducere](#introducere)
2. [Accesarea instrumentului](#accesarea-instrumentului)
3. [Interfața utilizatorului](#interfața-utilizatorului)
4. [Fila Date](#fila-date)
5. [Fila Variogramă](#fila-variogramă)
6. [Fila Kriging](#fila-kriging)
7. [Fila Tipare (ML)](#fila-tipare-ml)
8. [Fila Eșantionare](#fila-eșantionare)
9. [Fila Raport](#fila-raport)
10. [Fluxul de lucru operațional](#fluxul-de-lucru-operațional)
11. [Depanare](#depanare)
12. [Note tehnice](#note-tehnice)

---

## Introducere

**GeoArchaeo** este modulul de analiză geostatistică integrat în PyArchInit și corespunde versiunii **1.3.1** a pluginului GeoArchaeo. Lucrează cu orice strat de puncte din proiectul QGIS care are un câmp numeric (număr de fragmente, măsurători geofizice, analize de sol, dimensiuni ale mormintelor…) și însoțește analiza de la statisticile descriptive la variogramă, la interpolarea prin kriging ordinar împreună cu incertitudinea sa, la căutarea grupurilor și a anomaliilor prin învățare automată, la propunerea de noi puncte de eșantionare și, în final, la un raport.

Interfața GeoArchaeo există doar în italiană și în engleză. În acest tutorial etichetele sunt traduse, iar între paranteze este indicată eticheta în engleză care apare în panou. Parametrii variogramei sunt numiți cu termenii consacrați în geostatistică: nugget (efect de pepită), sill (pragul, varianța totală) și range (raza de corelație).

<!-- VIDEO: Introducere in GeoArchaeo -->
> **Tutorial video**: [Inserati link video introducere GeoArchaeo]

### De ce analiza geostatistică în arheologie?

Analiza geostatistică permite:

- **Descrierea** distribuției valorilor măsurate (medie, dispersie, asimetrie, valori aberante)
- **Cuantificarea** corelației spațiale, adică până la ce distanță valorile se aseamănă (variograma)
- **Interpolarea** valorilor între punctele cunoscute, obținând o suprafață continuă împreună cu incertitudinea ei (kriging)
- **Recunoașterea** grupurilor de puncte asemănătoare și a anomaliilor (învățare automată)
- **Planificarea** locurilor de eșantionat sau de săpat în campaniile următoare
- **Documentarea** analizelor într-un raport

### Prezentarea generală a fluxului de lucru

```
Date de intrare: strat de puncte + câmp numeric (alese sus, o singură dată)
  │
  ├─ 1 Date .............. statistici descriptive, histogramă
  ├─ 2 Variogramă ........ nugget, sill, range, anizotropie
  ├─ 3 Kriging ........... rastere ale estimării și ale incertitudinii, validare încrucișată
  ├─ 4 Tipare (ML) ....... grupuri și anomalii (strat de puncte)
  ├─ 5 Eșantionare ....... puncte noi propuse (strat de puncte)
  └─ 6 Raport ............ document HTML cu grafice interactive, sau PDF
```

### Noutățile versiunii 1.3.1

- Stratul și câmpul se aleg **o singură dată** sus și sunt valabile pentru toate filele; fiecare filă își păstrează propriile rezultate
- Graficele apar în panou chiar și fără QtWebEngine (previzualizare statică și buton pentru deschiderea lor în browser)
- Kriging-ul produce și **rasterul de incertitudine**, aplică rampa de culori și calculează o adevărată **validare încrucișată leave-one-out**
- Anizotropia se verifică cu **variograme direcționale** reale; nugget, sill și range pot fi fixate manual
- Variograma și kriging-ul sunt mult mai rapide (căutarea vecinilor cu KD-tree): grile de până la **500 × 500 de celule**
- Valorile NULL nu mai blochează statisticile și kriging-ul; raportul conține graficele; datele de exemplu provin din dosarul modulului
- Limba panoului este salvată în setările QGIS

---

## Accesarea instrumentului

GeoArchaeo face parte din grupul instrumentelor de analiză ale PyArchInit.

### Din bara de instrumente

1. În bara de instrumente PyArchInit, identificați butonul derulant al **instrumentelor de analiză** (același grup care conține, printre altele, SAM, Pottery Tools și MoveCost)
2. Faceți clic pe săgeata de lângă buton: pictograma vizibilă poate fi a altui instrument din grup
3. Alegeți **GeoArchaeo - Geostatistical Analysis** (eticheta acțiunii în PyArchInit când QGIS este în română)

<!-- IMAGE: Butonul derulant al instrumentelor de analiza din bara de instrumente -->
> **Fig. 1**: Meniul derulant al instrumentelor de analiză din bara de instrumente PyArchInit

Aceeași intrare se găsește în meniul **pyArchInit** din bara de meniuri QGIS și în meniul de pluginuri, la **pyArchInit - Archaeological GIS Tools**.

Panoul GeoArchaeo se deschide ca **panou andocabil** în partea dreaptă a ferestrei QGIS: poate fi mutat, redimensionat sau detașat ca orice panou QGIS. Dacă este închis, aceeași intrare îl redeschide cu rezultatele sesiunii încă prezente.

<!-- IMAGE: Panoul GeoArchaeo andocat in dreapta in QGIS -->
> **Fig. 2**: Panoul GeoArchaeo andocat în partea dreaptă a ferestrei QGIS

### Selectorul de limbă

În dreapta sus, lista **«Limbă:»** (*Language:*) oferă **Italiano** și **English**, singurele două limbi ale interfeței GeoArchaeo. Schimbarea este imediată, fără repornirea QGIS, iar alegerea este salvată în setările QGIS. Până la prima alegere, panoul urmează limba QGIS: italiană dacă QGIS este în italiană, engleză în toate celelalte cazuri, deci și cu QGIS în română.

---

## Interfața utilizatorului

De sus în jos, panoul conține: antetul cu butoanele, grupul **«Date de intrare (folosite de toate filele)»** (*Input data (used by all tabs)*), cele **6 file** ale analizei și, în timpul calculelor, bara de progres cu butonul **«Anulează»** (*Cancel*).

### Antetul

| Element | Funcție |
|---------|---------|
| **«Încarcă date de exemplu»** (*Load example data*) | Deschide lista seturilor de date de test incluse în modul (vezi fila Date) |
| **«Tutorial»** (*Tutorial*) | Deschide ghidul integrat GeoArchaeo, în italiană sau engleză, care poate fi deschis și în browser |
| **«Limbă:»** (*Language:*) | Listă Italiano / English |

### Datele de intrare

În grupul **«Date de intrare (folosite de toate filele)»** (*Input data (used by all tabs)*) se aleg o singură dată:

- **«Strat de puncte:»** (*Point layer:*): un strat vectorial de puncte din proiect
- **«Câmp de valori (numeric):»** (*Value field (numeric):*): câmpul de analizat (lista afișează doar câmpurile numerice)

Dedesubt apare un rezumat cu punctele valide din total, SRC-ul și extinderea stratului, de exemplu «500 de puncte valide din 500 · SRC EPSG:32633 · …» (*500 valid points of 500 · CRS EPSG:32633 · …*). Punctele fără valoare (NULL sau text nenumeric) nu sunt numărate ca valide. Rezumatul avertizează și atunci când proiectul nu are straturi de puncte, când stratul nu are câmpuri numerice sau când SRC-ul este geografic (grade).

La schimbarea stratului, panoul propune și distanța maximă a variogramei și dimensiunea celulei pentru kriging și preselectează stratul în fila Tipare (ML), dacă acolo nu este încă nimic selectat.

### Cele șase file

| Filă | Funcție | Rezultat |
|------|---------|----------|
| **Date** (*Data*) | Statisticile descriptive ale câmpului | Tabel de statistici, histogramă cu diagramă cutie |
| **Variogramă** (*Variogram*) | Structura spațială a valorilor | Nugget, sill, range, anizotropie, grafic |
| **Kriging** (*Kriging*) | Interpolare pe o grilă regulată | Rastere ale estimării și ale incertitudinii, validare încrucișată |
| **Tipare (ML)** (*Patterns (ML)*) | Grupuri și anomalii prin învățare automată | Strat de puncte cu eticheta grupului |
| **Eșantionare** (*Sampling*) | Propunerea de noi puncte de eșantionare | Strat de puncte și tabel de coordonate |
| **Raport** (*Report*) | Reunirea analizelor din sesiune | Fișier HTML cu grafice interactive, sau PDF |

<!-- IMAGE: Antetul, grupul Date de intrare si cele sase file GeoArchaeo -->
> **Fig. 3**: Antetul, grupul «Date de intrare» și cele șase file ale panoului GeoArchaeo

### Rezultate și grafice

Fiecare filă afișează rezultatele într-un **chenar** sub butonul de calcul, care rămâne vizibil până la repetarea analizei, precum și **graficul** în panou:

- dacă QGIS dispune de QtWebEngine, graficul Plotly este interactiv direct în panou (zoom, valori la trecerea mouse-ului)
- altfel apare o **previzualizare statică** cu nota «Previzualizare statică (QtWebEngine nu este disponibil în această instalare QGIS).» (*Static preview (QtWebEngine not available in this QGIS installation).*)
- în ambele cazuri, butonul **«Deschide graficul interactiv în browser»** (*Open interactive chart in browser*) deschide versiunea interactivă în browserul web

Filele Date, Variogramă și Kriging se încheie cu o legătură către pasul următor, de exemplu **«Pasul următor: Variogramă →»** (*Next step: Variogram →*).

### Analize în curs

Variograma, kriging-ul, recunoașterea tiparelor și eșantionarea sunt calculate într-un **fir de execuție separat**: QGIS rămâne utilizabil, iar în partea de jos a panoului apar **bara de progres** (în procente pentru kriging) și butonul **«Anulează»** (*Cancel*). Se rulează o singură analiză odată: la pornirea alteia apare «O analiză este deja în curs: așteptați să se termine sau anulați-o.» (*An analysis is already running: wait for it to finish or cancel it.*)

---

## Fila Date

Fila **Date** (*Data*, «1. Analiză exploratorie» / *1. Exploratory analysis*) descrie distribuția valorilor înainte de interpolarea lor.

### Calculul statisticilor

1. În grupul «Date de intrare», alegeți stratul de puncte și câmpul numeric
2. Deschideți fila **Date**
3. Faceți clic pe **«Calculează statisticile»** (*Calculate statistics*)

<!-- IMAGE: Fila Date cu statistici si histograma -->
> **Fig. 4**: Fila Date cu tabelul statisticilor și histograma câmpului ales

### Statistici și interpretare

| Statistică | Descriere |
|------------|-----------|
| **Număr de valori** (*Number of values*), **Valori lipsă** (*Missing values*) | Puncte cu valoare validă și puncte excluse (NULL sau text nenumeric) |
| **Minim**, **Maxim**, **Medie** (*Mean*), **Mediană** (*Median*) | Intervalul și poziția valorilor |
| **Abatere standard** (*Std. deviation*), **Coeficient de variație** (*Coeff. of variation*) | Dispersia absolută și relativă |
| **Prima cuartilă (Q1)**, **A treia cuartilă (Q3)** (*First/Third quartile*) | Limitele celor 50 % valori centrale |
| **Asimetrie** (*Skewness*), **Kurtosis** (*Kurtosis*) | Forma distribuției |

Sub tabel, panoul adaugă o interpretare în cuvinte:

- asimetrie mai mare de 1: distribuție asimetrică la dreapta (puține valori foarte mari); merită luată în calcul o transformare logaritmică înainte de kriging, de exemplu creând un câmp nou cu calculatorul de câmpuri
- asimetrie mai mică de -1: distribuție asimetrică la stânga (puține valori foarte mici)
- în celelalte cazuri: distribuție aproximativ simetrică, potrivită pentru kriging
- numărul posibilelor valori aberante, adică dincolo de 3 abateri standard de la medie

Graficul arată **histograma** valorilor cu o **diagramă cutie** (în previzualizarea statică doar histograma).

### Date de exemplu

Butonul **«Încarcă date de exemplu»** (*Load example data*) deschide fereastra «Date de exemplu GeoArchaeo» (*GeoArchaeo example data*) cu seturile de date din dosarul `test_layers` al modulului; calea este indicată la **«Dosar:»** (*Folder:*) și poate fi schimbată cu **«Răsfoiește…»** (*Browse…*). Fișierele GeoPackage și GeoJSON sunt deja bifate. Fișierele CSV apar doar dacă nu există un GeoPackage sau un GeoJSON cu același nume; trebuie bifate manual și se încarcă drept text delimitat (câmpurile `x` și `y`, EPSG:32633). Cu **OK**, straturile sunt adăugate în proiect, iar primul strat de puncte încărcat devine stratul de intrare al panoului.

| Set de date | Puncte | Câmpuri numerice principale | Utilizare recomandată |
|-------------|--------|-----------------------------|-----------------------|
| `villa_ceramica` (GeoPackage) | 500 | `ceramic_count`, `weight_g`, `depth_cm` | Statistici, variogramă, kriging |
| `geoarchaeo_test_complete` (GeoPackage) | 500 | Aceleași ca `villa_ceramica` | Încercarea tuturor filelor |
| `geofisica_survey` (GeoPackage) | 4800 | `gpr_amplitude`, `mag_nt` | Isolation Forest, test pe un set de date mare |
| `necropoli` (GeoPackage) | 120 de morminte | `length_cm`, `width_cm`, `depth_cm`, `n_grave_goods` | DBSCAN sau K-Means |
| `soil_samples` (GeoPackage) | 80 | `sand_pct`, `silt_pct`, `clay_pct`, `ph`, `p_ppm`, `organic_pct` | Kriging al proprietăților solului |
| `ricognizione_survey` (GeoJSON) | 100 | `densita_mq`, `visibilita`, `pendenza`, `distanza_acqua` | Kriging al densității, eșantionare |
| `unita_scavo_ceramica` (GeoJSON) | 50 | `ceramica_tot`, `ceramica_fine`, `ceramica_comune` | Variogramă și kriging cu puține puncte |
| `area_studio` (GeoJSON) | 1 poligon | — | Zona de studiu pentru eșantionare |

Dintre fișierele CSV, `magnetometria_grid` (2500 de puncte, câmpul `mag_nT`) conține anomalii magnetice simulate (două ziduri, o groapă, un cuptor). Toate datele sunt simulate și în EPSG:32633 (UTM 33N, metri). Poligonul `area_studio` acoperă zona `ricognizione_survey`, `unita_scavo_ceramica` și `magnetometria_grid`, nu și pe cea a celorlalte seturi de date.

### Cerințe pentru date

- Stratul trebuie să fie un strat vectorial de **puncte** (pentru multipuncte se folosește primul punct)
- Câmpul trebuie să fie **numeric**: un câmp text care conține numere trebuie convertit cu calculatorul de câmpuri
- Valorile NULL sau nenumerice sunt excluse automat și numărate ca lipsă
- Pentru variogramă și kriging sunt necesare cel puțin **5 puncte** cu valoare validă (1 pentru statistici); o variogramă fiabilă necesită de regulă câteva zeci de puncte
- Se recomandă un **SRC proiectat** în metri (de exemplu UTM): cu un SRC geografic rezumatul avertizează, iar variograma și kriging-ul cer confirmare

---

## Fila Variogramă

Fila **Variogramă** (*Variogram*, «2. Variogramă» / *2. Variogram*) măsoară cum crește diferența dintre valori odată cu distanța: descrie structura spațială a datelor și ghidează kriging-ul.

### Ce este o variogramă?

Variograma pune în relație **semivarianța** perechilor de puncte cu **distanța** care le separă. Parametrii modelului sunt:

| Parametru | Descriere |
|-----------|-----------|
| **Nugget** (efect de pepită) | Variabilitatea la distanță aproape nulă: eroare de măsurare și variabilitate la scară mică |
| **Sill** (pragul) | Varianța totală atinsă de model ("platoul") |
| **Range** (raza de corelație) | Distanța dincolo de care valorile nu mai sunt corelate; în GeoArchaeo este raza practică (95 % din sill) |

### Calculul variogramei

1. Deschideți fila **Variogramă**
2. În grupul **«Parametri»** (*Parameters*), verificați **«Distanța maximă:»** (*Maximum distance:*): butonul **«Auto»** propune aproximativ 1/3 din diagonala zonei ocupate de puncte (aceeași valoare este propusă la schimbarea stratului)
3. Alegeți **«Model teoretic:»** (*Theoretical model:*)
4. Dacă este nevoie, bifați **«Verifică anizotropia (variograme direcționale)»** (*Check anisotropy (directional variograms)*)
5. Faceți clic pe **«Calculează variograma»** (*Calculate variogram*)

Perechile de puncte sunt grupate în **15 clase de distanță** (lag-uri) între zero și distanța maximă; numărul de clase nu poate fi schimbat din panou. Peste **3000 de puncte**, variograma este calculată pe un subeșantion aleator de 3000 de puncte, deoarece numărul de perechi crește cu pătratul numărului de puncte. Modelul este ajustat prin metoda celor mai mici pătrate, ponderată cu numărul de perechi din fiecare clasă.

<!-- IMAGE: Fila Variograma cu parametri si rezultate -->
> **Fig. 5**: Fila Variogramă cu parametrii, modelul teoretic și chenarul rezultatelor

### Modele teoretice

| Model | Comportament | Când se folosește |
|-------|--------------|-------------------|
| **«Sferic (recomandat)»** (*Spherical (recommended)*) | Crește până la range, apoi rămâne constant | Cel mai folosit: densități de materiale, distribuții cu limite nete |
| **«Exponențial»** (*Exponential*) | Crește rapid lângă origine și atinge sill-ul treptat | Fenomene cu descreștere continuă, de exemplu elemente chimice în sol |
| **«Gaussian»** (*Gaussian*) | Foarte regulat lângă origine | Fenomene foarte "netede" (suprafețe); de folosit cu prudență |
| **«Matérn»** (*Matérn*) | Intermediar între exponențial și gaussian (ν = 1,5) | Alternativă flexibilă |

Regulă practică: începeți cu modelul sferic și comparați RMSE-ul ajustării cu cel al celorlalte modele. Kriging-ul folosește **ultima** variogramă calculată: după comparații, recalculați modelul ales.

### Parametri manuali

Grupul **«Parametri manuali (opțional)»** (*Manual parameters (optional)*), dezactivat implicit, permite fixarea valorilor **«Nugget:»** (*Nugget:*), **«Sill (varianța totală):»** (*Sill (total variance):*) și **«Range (distanța de corelație):»** (*Range (correlation distance):*). Cu grupul activ, valorile diferite de zero rămân fixe, iar cele lăsate pe «Auto» (zero) sunt estimate.

### Citirea rezultatelor

Chenarul rezultatelor indică:

- modelul cu **nugget**, **sill**, **range** (în unitățile SRC-ului) și **RMSE**-ul ajustării
- numărul de perechi de puncte și de clase de distanță, cu subeșantionul folosit, dacă există
- o interpretare a range-ului: până la această distanță valorile sunt corelate spațial, dincolo de ea nu se influențează
- raportul nugget/sill: sub 25 % continuitate puternică la scară mică, până la 60 % continuitate moderată, peste 60 % variabilitate mare la scară mică sau eroare de măsurare (kriging-ul va fi puțin informativ)

Graficul arată punctele variogramei experimentale (mai mari acolo unde perechile sunt mai numeroase), curba modelului și liniile pentru nugget, sill și range.

<!-- IMAGE: Variograma experimentala cu modelul ajustat -->
> **Fig. 6**: Variograma experimentală și modelul sferic cu liniile pentru nugget, sill și range

### Variograme direcționale (anizotropie)

Cu **«Verifică anizotropia (variograme direcționale)»** bifată, GeoArchaeo calculează și variogramele pe direcțiile **0°, 45°, 90° și 135°** (unghiuri măsurate de la est, în sens trigonometric, toleranță ±22,5°). Nugget-ul și sill-ul rămân cele ale variogramei globale; pentru fiecare direcție se estimează range-ul.

- Dacă raportul dintre cel mai mare și cel mai mic range depășește **2**, chenarul semnalează anizotropia și direcția principală (de exemplu de-a lungul unui zid, al unui drum sau al unei pante)
- Altfel indică «Nicio anizotropie relevantă» (*No relevant anisotropy*) împreună cu raportul calculat
- Cu prea puține perechi pe direcție apare «Perechi insuficiente pentru variogramele direcționale.» (*Not enough pairs for directional variograms.*)

În graficul interactiv, variogramele direcționale sunt intrări ale legendei ascunse la început: faceți clic pe 0°, 45°, 90° sau 135° pentru a le afișa (în previzualizarea statică sunt desenate mereu). Kriging-ul din panou folosește modelul omnidirecțional: anizotropia servește interpretării.

---

## Fila Kriging

Fila **Kriging** (*Kriging*, «3. Kriging ordinar» / *3. Ordinary kriging*) interpolează valorile pe o grilă regulată folosind variograma, produce și harta incertitudinii și adaugă rasterele în proiect.

### Kriging-ul ordinar

Panoul execută **kriging ordinar** (medie locală constantă, dar necunoscută), potrivit pentru majoritatea datelor arheologice. Pentru fiecare celulă folosește cele mai apropiate **20 de puncte**, găsite cu un KD-tree; acest număr nu poate fi schimbat din panou. Co-kriging-ul, kriging-ul spațio-temporal și kriging-ul pe blocuri pentru seturi de date foarte mari există doar ca algoritmi Processing ai pluginului GeoArchaeo independent și nu sunt disponibile în PyArchInit.

### Rularea kriging-ului

1. Deschideți fila **Kriging** și citiți linia de stare a variogramei (vezi mai jos); butonul **«← Mergi la variogramă»** (*← Go to Variogram*) duce înapoi la fila anterioară
2. Setați **«Dimensiunea celulei:»** (*Cell size:*), adică latura unei celule în unitățile SRC-ului: panoul propune aproximativ 100 de celule pe latura cea mai lungă a stratului și afișează dedesubt grila rezultată («Grilă: … × … = … celule» / *Grid: … × … = … cells*)
3. Lăsați bifată opțiunea **«Folosește variograma calculată»** (*Use the calculated variogram*) pentru a folosi variograma din fila anterioară; dacă este debifată, variograma este estimată automat
4. Lăsați bifată opțiunea **«Creează și rasterul de incertitudine (abatere standard)»** (*Also create the uncertainty raster (std. deviation)*) dacă aveți nevoie de harta incertitudinii
5. Faceți clic pe **«Rulează kriging»** (*Run kriging*): bara de progres arată procentul, iar **«Anulează»** (*Cancel*) întrerupe calculul

Linia de stare poate indica:

- «Variogramă disponibilă: …, range … ✓» (*Variogram available: …, range … ✓*): se folosește variograma calculată pe același strat și același câmp
- «Nicio variogramă calculată: va fi estimată automat (model sferic).» (*No variogram calculated: it will be estimated automatically (spherical model).*)
- «Variograma a fost calculată pe alt strat/câmp: va fi recalculată.» (*The variogram was calculated on another layer/field: it will be recalculated.*), tot cu o estimare automată

> **Grila**: grila acoperă extinderea stratului de puncte și este limitată la **500 de celule pe latură**. Dacă dimensiunea aleasă a celulei este prea fină, ea este mărită automat, iar linia grilei semnalează acest lucru («dimensiune minimă a celulei … (max. 500 de celule pe latură)» / *minimum cell size … (max 500 cells per side)*). Peste **40.000 de celule**, linia devine portocalie și, la pornire, panoul cere confirmare, deoarece calculul poate dura câteva minute.

<!-- IMAGE: Rasterele kriging si metricile validarii incrucisate -->
> **Fig. 7**: Rasterele estimării și incertitudinii pe hartă, cu chenarul rezultatelor și validarea încrucișată

### Rezultatele kriging-ului

Kriging-ul adaugă în proiect două rastere GeoTIFF, în SRC-ul stratului de puncte:

| Strat | Conținut | Stil |
|-------|----------|------|
| `Kriging_<câmp>` | Valoarea estimată în fiecare celulă | Rampă de culori de la albastru la roșu, trecând prin galben; vizibil |
| `Kriging_<câmp>_uncertainty` | Abaterea standard a estimării (incertitudinea) | Rampă de la galben deschis la roșu; adăugat în partea de sus a listei de straturi, dar ascuns |

Cu panoul în italiană, al doilea raster se numește `Kriging_<câmp>_incertezza`. Fișierele sunt scrise într-un **dosar temporar**: pentru a le păstra, exportați-le din meniul contextual al stratului (**Export**).

Chenarul rezultatelor rezumă punctele folosite, dimensiunile grilei, dimensiunea celulei, modelul și range-ul; graficul arată harta valorilor estimate și harta incertitudinii, cu punctele de eșantion suprapuse.

### Validarea încrucișată leave-one-out

După kriging, GeoArchaeo efectuează o **validare încrucișată leave-one-out**: fiecare punct este eliminat și reestimat din celelalte (pe cel mult 200 de puncte alese aleatoriu în seturile mari). Metricile apar în chenarul rezultatelor:

| Metrică | Semnificație | Valoare dorită |
|---------|--------------|----------------|
| **RMSE** (*root mean squared error*) | Eroarea tipică a estimării | Cât mai mică, comparată cu abaterea standard a datelor |
| **MAE** (*mean absolute error*) | Eroarea medie în valoare absolută | Cât mai mică |
| **ME** (*mean error, bias*) | Supraestimare sau subestimare sistematică | Apropiată de 0 |
| **R²** (*explained variance*) | Capacitatea predictivă | De la 0,5 în sus bună, sub 0,2 slabă |
| **MSDR** (*standardized error*) | Realismul incertitudinii estimate | În jur de 1; peste 1,5 incertitudine subestimată, sub 0,5 supraestimată |

Panoul adaugă o apreciere în cuvinte a capacității predictive (bună, moderată sau slabă) și, când este cazul, a MSDR.

> **Notă**: kriging-ul rulează într-un **fir de execuție în fundal**, astfel încât interfața QGIS rămâne utilizabilă în timpul calculului; bara de progres indică starea procesării.

---

## Fila Tipare (ML)

Fila **Tipare (ML)** (*Patterns (ML)*, «4. Recunoașterea tiparelor (învățare automată)» / *4. Pattern recognition (machine learning)*) grupează punctele după poziție și atribute numerice sau detectează anomaliile și creează un strat cu eticheta fiecărui punct.

### Metode disponibile

| Metodă (intrare din listă) | Ce face | Parametri |
|----------------------------|---------|-----------|
| **«K-Means – grupuri după similaritate»** (*K-Means – groups by similarity*) | Împarte punctele în K grupuri asemănătoare ca poziție și atribute | **«Număr de grupuri (0 = automat):»** (*Number of groups (0 = automatic):*); cu 0, numărul este ales după câte puncte există (de la 2 la 5) |
| **«DBSCAN – grupuri după densitate (găsește și punctele izolate)»** (*DBSCAN – groups by density (also finds isolated points)*) | Găsește grupuri după densitate fără a le fixa numărul; punctele izolate formează grupul «Izolate / zgomot» (*Isolated / noise*) | Automați |
| **«Isolation Forest – detectarea anomaliilor»** (*Isolation Forest – anomaly detection*) | Marchează drept «Anomalie» (*Anomaly*) aproximativ 10 % dintre punctele cele mai diferite de celelalte; restul sunt «Normal» (*Normal*) | Automați |

### Rulare

1. Deschideți fila **Tipare (ML)**
2. În lista **«Straturi de puncte de analizat (unul sau mai multe):»** (*Point layers to analyse (one or more):*), selectați unul sau mai multe straturi de puncte (dacă nu este selectat nimic, se preselectează stratul de intrare)
3. Alegeți **«Metodă:»** (*Method:*)
4. Doar pentru K-Means, setați **«Număr de grupuri (0 = automat):»**
5. Faceți clic pe **«Pornește recunoașterea tiparelor»** (*Run pattern recognition*)

Variabilele analizate sunt **coordonatele X și Y** și **toate câmpurile numerice** ale straturilor selectate, standardizate; valorile lipsă sunt înlocuite cu media câmpului. Prin urmare, nu se folosește doar câmpul de valori ales sus: intră toate câmpurile numerice, inclusiv identificatorii și numerele de ordine, iar dacă acestea distorsionează grupurile este mai bine să analizați o copie a stratului doar cu câmpurile utile. Dacă analizați mai multe straturi împreună, ele trebuie să aibă aceleași câmpuri numerice, în aceeași ordine, și același SRC (stratul creat folosește SRC-ul primului strat selectat).

<!-- IMAGE: Fila Tipare (ML) cu stratul grupurilor -->
> **Fig. 8**: Fila Tipare (ML) cu graficul grupurilor și stratul `ML_groups` pe hartă

### Rezultate

- Chenarul rezultatelor indică metoda, numărul de grupuri și câte puncte cad în fiecare (de exemplu «Grupul A (n=42)» / *Group A (n=42)*)
- Graficul arată punctele în planul primelor două componente principale (PC1, PC2) ale variabilelor, colorate pe grupuri
- Se creează un strat de puncte temporar, `ML_groups` (K-Means, DBSCAN) sau `ML_anomalies` (Isolation Forest), cu o legendă pe categorii: gri pentru punctele izolate, roșu și mai mare pentru anomalii; cu panoul în italiană numele sunt `Gruppi_ML` și `Anomalie_ML`

| Câmp | Conținut |
|------|----------|
| `cluster_id` | Numărul grupului (-1 = izolate la DBSCAN; 1 = anomalie și 0 = normal la Isolation Forest) |
| `cluster_name` | Nume lizibil, de exemplu «Group A (n=42)», «Isolated / noise (n=5)», «Anomaly (n=12)» |
| `cluster_size` | Numărul de puncte din grup |
| `method` | Metoda folosită |
| `x_coord`, `y_coord` | Coordonatele punctului |

### Clasificarea supervizată

Sub metodă, panoul amintește că clasificarea supervizată (Random Forest cu un câmp de etichete) se găsește în **Processing → GeoArchaeo**. Acel algoritm aparține pluginului GeoArchaeo independent: în PyArchInit furnizorul Processing al GeoArchaeo nu este înregistrat, așa că Random Forest nu este disponibil. Pentru a-l folosi este nevoie de pluginul GeoArchaeo separat.

---

## Fila Eșantionare

Fila **Eșantionare** (*Sampling*, «5. Noi puncte de eșantionare» / *5. New sampling locations*) sugerează unde să se eșantioneze sau să se sape în viitor pornind de la punctele existente și creează un strat cu punctele propuse.

### Criterii de eșantionare

| Criteriu (intrare din listă) | Cum alege punctele | Când se folosește |
|------------------------------|--------------------|-------------------|
| **«Acoperire (maximin)»** (*Coverage (maximin)*) | Fiecare punct nou este cât mai departe de toate celelalte | Umplerea golurilor în mod uniform |
| **«Reducerea incertitudinii (varianța kriging)»** (*Uncertainty reduction (kriging variance)*) | Fiecare punct nou merge acolo unde varianța kriging este maximă | Reducerea erorii kriging acolo unde este cea mai mare |
| **«Grilă stratificată»** (*Stratified grid*) | O poziție pe celulă a unei grile regulate, cu o ușoară perturbare aleatoare | Acoperirea regulată a unei zone definite |
| **«Adaptiv (zone mai puțin dense)»** (*Adaptive (sparser areas)*) | Extragere aleatoare cu probabilitate mai mare acolo unde sunt puține puncte | Favorizarea zonelor mai puțin eșantionate, păstrând o componentă aleatoare |

Criteriul «Reducerea incertitudinii» folosește variograma calculată dacă se referă la același strat și același câmp și dacă în fila Kriging este bifată «Folosește variograma calculată»; altfel folosește un model generic bazat pe distanța tipică dintre puncte.

### Proiectarea eșantionării

1. Verificați **«Puncte existente:»** (*Existing points:*): este stratul ales sus în grupul «Date de intrare» (pentru eșantionare câmpul numeric nu este necesar)
2. Opțional: alegeți la **«Zona de studiu (poligon, opțional):»** (*Study area (polygon, optional):*) un strat de poligoane; toate poligoanele sale sunt unite și reproiectate în SRC-ul punctelor, chiar dacă stratul este în alt SRC
3. Setați **«Puncte noi de propus:»** (*New points to propose:*) (de la 1 la 500, implicit 10)
4. Alegeți **«Criteriu:»** (*Criterion:*): sub listă apare descrierea lui
5. Faceți clic pe **«Calculează puncte noi»** (*Calculate new points*)

Fără zonă de studiu, punctele sunt căutate în dreptunghiul care cuprinde punctele existente, lărgit cu 20 % pe fiecare latură.

<!-- IMAGE: Puncte noi de esantionare propuse -->
> **Fig. 9**: Noile puncte de eșantionare (stele galbene) propuse în interiorul zonei de studiu

### Rezultatele eșantionării

- Chenarul rezultatelor indică câte puncte au fost propuse și cu ce criteriu; dedesubt, tabelul «Coordonatele punctelor propuse:» (*Coordinates of the proposed points:*) listează numărul, X și Y
- Se creează stratul de puncte temporar `New_sampling_points` (`Nuovi_punti_campionamento` cu panoul în italiană), cu simbol de stea galbenă și câmpurile `point_id`, `x_coord`, `y_coord` și `type` (valoarea `suggested`)

---

## Fila Raport

Fila **Raport** (*Report*, «6. Raport» / *6. Report*) reunește într-un singur document analizele efectuate în sesiune: statistici, grafice interactive, parametri și validare.

### Conținutul raportului

În grupul **«Secțiuni de inclus»** (*Sections to include*), fiecare secțiune este marcată «disponibil» (*available*) sau «încă necalculat» (*not yet calculated*); secțiunile necalculate nu pot fi alese.

| Secțiune | Conținut |
|----------|----------|
| **Statistici descriptive** (*Descriptive statistics*) | Strat și câmp, tabelul statisticilor cu interpretarea în cuvinte, histogramă |
| **Variogramă** (*Variogram*) | Model, nugget, sill, range, RMSE, distanța maximă, interpretare, grafic |
| **Kriging și validare încrucișată** (*Kriging and cross-validation*) | Metodă, dimensiunea celulei, dimensiunile grilei, metricile validării încrucișate, grafic |
| **Recunoașterea tiparelor** (*Pattern recognition*) | Straturi analizate, grupuri cu numărul lor de puncte, grafic |
| **Noi puncte de eșantionare** (*New sampling locations*) | Criteriu, strat, tabelul coordonatelor |

Fiecare secțiune conține **ultima** analiză de tipul său efectuată în sesiune.

### Generarea raportului

1. Efectuați analizele dorite în celelalte file
2. Deschideți fila **Raport** și lăsați bifate secțiunile de inclus (sunt bifate implicit)
3. Faceți clic pe **«Salvează raportul HTML»** (*Save HTML report*) sau pe **«Salvează raportul PDF»** (*Save PDF report*) și alegeți numele fișierului

La salvare, panoul afișează și o previzualizare a raportului fără grafice; nota «Previzualizare: graficele interactive sunt incluse în fișierul HTML salvat.» (*Preview: the interactive charts are included in the saved HTML file.*) amintește unde se găsesc.

<!-- IMAGE: Raport HTML GeoArchaeo deschis in browser -->
> **Fig. 10**: Un raport HTML GeoArchaeo cu grafice interactive, deschis în browser

### Export

| Format | Conținut | Note |
|--------|----------|------|
| **HTML** (`geoarchaeo_report.html`) | Text, tabele și **grafice interactive** | Fișierul este autonom (biblioteca de grafice este inclusă, funcționează și fără conexiune) și se deschide imediat în browser |
| **PDF** (`geoarchaeo_report.pdf`) | Text și tabele, **fără grafice** | Dacă PDF-ul nu poate fi creat, salvați raportul HTML și tipăriți-l în PDF din browser |

Dacă nu s-a efectuat nicio analiză apare «Nicio analiză disponibilă: rulați mai întâi cel puțin o analiză.» (*No analysis available: run at least one analysis first.*); dacă nu este bifată nicio secțiune, «Selectați cel puțin o secțiune» (*Select at least one section*).

---

## Fluxul de lucru operațional

Un exemplu complet cu datele de exemplu incluse în modul (panou în engleză).

### Pasul 1: Pregătirea datelor

1. Deschideți GeoArchaeo din bara de instrumente PyArchInit
2. Faceți clic pe **«Încarcă date de exemplu»** (*Load example data*) și confirmați cu **OK** (se încarcă fișierele GeoPackage și GeoJSON)
3. În grupul «Date de intrare», alegeți stratul `villa_ceramica` și câmpul `ceramic_count`
4. Verificați rezumatul: 500 de puncte valide din 500, SRC EPSG:32633

### Pasul 2: Explorarea datelor

1. Fila **Date** → **«Calculează statisticile»** (*Calculate statistics*)
2. Citiți asimetria și valorile aberante; la o asimetrie puternică la dreapta, luați în calcul o transformare logaritmică

### Pasul 3: Analiza variogramei

1. Fila **Variogramă** → **«Auto»** pentru distanța maximă, modelul **«Sferic (recomandat)»** (*Spherical (recommended)*) → **«Calculează variograma»** (*Calculate variogram*)
2. Repetați cu **«Exponențial»** (*Exponential*) și comparați RMSE-ul ajustării
3. Opțional: recalculați cu **«Verifică anizotropia (variograme direcționale)»**
4. Recalculați la final modelul ales și notați nugget, sill și range

### Pasul 4: Interpolarea

1. Fila **Kriging**: verificați linia «Variogramă disponibilă … ✓» (*Variogram available … ✓*)
2. Păstrați dimensiunea propusă a celulei sau setați 1 (metru)
3. **«Rulează kriging»** (*Run kriging*)
4. Examinați rasterele `Kriging_ceramic_count` și `Kriging_ceramic_count_uncertainty` și valorile R² și MSDR

### Pasul 5: Tipare și eșantionare (opționale)

1. Fila **Tipare (ML)**: lăsați selectat în listă doar `necropoli`, metoda DBSCAN → **«Pornește recunoașterea tiparelor»** (*Run pattern recognition*); stratul `ML_groups` arată grupurile de morminte și punctele izolate
2. Sus, alegeți stratul `ricognizione_survey` (câmpul `densita_mq`); fila **Eșantionare**: zona de studiu `area_studio`, 10 puncte, criteriul «Acoperire (maximin)» (*Coverage (maximin)*) → **«Calculează puncte noi»** (*Calculate new points*)

### Pasul 6: Raport

1. Fila **Raport**: lăsați bifate secțiunile disponibile
2. **«Salvează raportul HTML»** (*Save HTML report*): raportul se deschide în browser cu graficele interactive
3. Exportați rasterele și straturile temporare pe care vreți să le păstrați

---

## Depanare

### Probleme frecvente

| Problemă | Cauză | Soluție |
|----------|-------|---------|
| «Niciun strat de puncte în proiect…» (*No point layer in the project: load one or use the example data.*) | Proiectul nu are straturi de puncte | Adăugați un strat de puncte sau folosiți **«Încarcă date de exemplu»** |
| «Stratul nu are câmpuri numerice…» (*The layer has no numeric fields…*) | Câmpul de analizat este de tip text | Convertiți-l în număr cu calculatorul de câmpuri |
| «Sunt necesare cel puțin 5 puncte cu valoare validă…» (*At least 5 points with a valid value are required (found …)*) | Prea multe valori NULL sau nenumerice | Verificați tabelul de atribute sau alegeți alt câmp |
| Avertismentul «SRC geografic (grade)» (*geographic CRS (degrees)*) | Stratul nu este într-un SRC proiectat | Reproiectați stratul, de exemplu în UTM, și repetați analiza |
| Eroarea «No point pairs within the maximum distance…» | Distanța maximă a variogramei este prea mică | Măriți **«Distanța maximă:»** sau folosiți **«Auto»** |
| «Perechi insuficiente pentru variogramele direcționale.» (*Not enough pairs for directional variograms.*) | Prea puține perechi pe direcție | Măriți distanța maximă sau renunțați la verificarea anizotropiei |
| Kriging lent, cerere de confirmare sau «Memorie insuficientă: măriți dimensiunea celulei.» (*Out of memory: increase the cell size.*) | Grilă cu prea multe celule | Măriți **«Dimensiunea celulei:»** |
| R² scăzut la validarea încrucișată | Corelație spațială slabă sau prea mult zgomot | Considerați harta doar orientativă și consultați rasterul de incertitudine |
| DBSCAN pune aproape toate punctele în «Izolate / zgomot» (*Isolated / noise*) | Densitate uniformă sau prea multe variabile | Încercați K-Means sau reduceți câmpurile numerice |
| «Machine Learning features not available. Please install scikit-learn.» | Lipsește scikit-learn | Instalați scikit-learn în mediul Python al QGIS |
| «Plotly visualization not available. Please install plotly.» | Lipsește Plotly | Instalați plotly în mediul Python al QGIS |
| Grafic doar ca imagine statică | QtWebEngine nu este disponibil | Folosiți **«Deschide graficul interactiv în browser»** (*Open interactive chart in browser*) |
| «Nu se poate crea PDF-ul…» (*Cannot create the PDF…*) | Eroare la tipărirea PDF-ului | Salvați raportul HTML și tipăriți-l din browser |
| Panou invizibil | Panou închis | Redeschideți-l din bara de instrumente sau din meniul pyArchInit: rezultatele sesiunii sunt încă acolo |

### Erori frecvente

- **«O analiză este deja în curs…»** (*An analysis is already running: wait for it to finish or cancel it.*): așteptați terminarea calculului sau apăsați «Anulează»
- **«Analiză anulată»** (*Analysis cancelled*): analiza a fost întreruptă cu «Anulează» și nu a produs rezultate
- **«Selectați cel puțin un strat»** (*Select at least one layer*, fila Tipare): selectați cel puțin un strat din listă
- **«Selectați stratul punctelor existente (sus)»** (*Select the existing points layer (above)*, fila Eșantionare): alegeți stratul în grupul «Date de intrare»
- **«Selectați un strat de puncte și un câmp numeric (în partea de sus a panoului)»** (*Select a point layer and a numeric field (at the top of the panel)*): completați alegerea în grupul «Date de intrare»

### Performanță

- Analizele rulează într-un **fir de execuție în fundal**: QGIS rămâne utilizabil, iar calculul poate fi anulat
- Variograma folosește cel mult 3000 de puncte (subeșantion aleator), validarea încrucișată cel mult 200
- Kriging-ul folosește cele mai apropiate 20 de puncte pentru fiecare celulă: timpul depinde mai ales de numărul de celule
- Grila este limitată la 500 × 500 de celule; peste 40.000 de celule panoul cere confirmare
- La seturi de date mari (de exemplu cele 4800 de puncte din `geofisica_survey`), măriți dimensiunea celulei

---

## Note tehnice

### Versiune și origine

- Modulul `modules/geoarchaeo/` este aliniat la **GeoArchaeo 1.3.1**, pluginul independent al lui Enzo Cocca (github.com/enzococca/GeoArchaeo)
- În PyArchInit este integrat doar panoul: furnizorul Processing al GeoArchaeo (co-kriging, kriging spațio-temporal, kriging pe blocuri, analiză compozițională, Random Forest) **nu** este înregistrat
- Modulul este compatibil cu QGIS 3 (Qt5) și QGIS 4 (Qt6)

### Dependențe

| Bibliotecă | Utilizare |
|------------|-----------|
| **NumPy** | Calcule numerice |
| **SciPy** | Ajustarea modelelor de variogramă, căutarea vecinilor (KD-tree), statistici |
| **scikit-learn** | K-Means, DBSCAN, Isolation Forest, componente principale (necesară pentru fila Tipare) |
| **Plotly** | Grafice interactive în panou și în raportul HTML |
| **Matplotlib** | Previzualizări statice ale graficelor când lipsește QtWebEngine |
| **QtWebEngine** (opțional) | Grafice interactive direct în panou |
| **threadpoolctl** (opțional) | Limitează firele de calcul în timpul analizelor din fundal |
| **GDAL** | Scrierea rasterelor GeoTIFF (inclus în QGIS) |

### Sisteme de referință

- Distanțele (distanța maximă, range, dimensiunea celulei) sunt exprimate în **unitățile SRC-ului stratului de puncte**
- Folosiți un **SRC proiectat** în metri: cu un SRC geografic rezumatul avertizează, iar variograma și kriging-ul cer confirmare
- Rasterele kriging și straturile create folosesc SRC-ul stratului de puncte (în fila Tipare, pe cel al primului strat selectat)
- Zona de studiu este reproiectată automat în SRC-ul punctelor

### Straturi și fișiere generate

| Produs | Tip | Locație |
|--------|-----|---------|
| `Kriging_<câmp>`, `Kriging_<câmp>_uncertainty` | Raster GeoTIFF (compresie LZW) | Dosarul temporar al sistemului |
| `ML_groups` / `ML_anomalies` | Strat de puncte temporar (în memorie) | Doar în proiectul deschis |
| `New_sampling_points` | Strat de puncte temporar (în memorie) | Doar în proiectul deschis |
| Raport | HTML sau PDF | Calea aleasă la salvare |

Rasterele și straturile temporare trebuie exportate (meniul contextual al stratului → **Export**) pentru a nu fi pierdute la închiderea proiectului. Numele straturilor urmează limba panoului din momentul calculului.

### Setări

- Limba panoului este salvată în setările QGIS (cheia `GeoArchaeo/language`)
- Rezultatele rămân în memorie cât timp QGIS este deschis: închiderea panoului nu le șterge

---

> **Notă**: GeoArchaeo este în dezvoltare continuă. Pentru a raporta erori sau a sugera îmbunătățiri, folosiți sistemul de urmărire a problemelor (issues) al proiectului PyArchInit pe GitHub.
