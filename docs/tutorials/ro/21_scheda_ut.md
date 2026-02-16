# Tutorial 21: Formularul UT - Unitati Topografice

## Introducere

**Formularul UT** (Unitati Topografice) este modulul PyArchInit dedicat documentarii prospectiunilor arheologice de suprafata. Permite inregistrarea datelor legate de concentratiile de materiale, anomaliile de teren si siturile identificate in timpul prospectiunilor de teren.

### Concepte de baza

**Unitate Topografica (UT):**
- Zona delimitata cu caracteristici arheologice omogene
- Identificata in timpul prospectiunii de suprafata
- Definita prin concentratia de materiale sau anomalii vizibile

**Prospectiune:**
- Prospectare sistematica a teritoriului
- Colectarea datelor privind prezenta umana antica
- Documentare fara excavare

---

## Accesarea formularului

### Prin meniu
1. Meniul **PyArchInit** din bara de meniu QGIS
2. Selectati **Formular UT**

### Prin bara de instrumente
1. Localizati bara de instrumente PyArchInit
2. Faceti clic pe pictograma **UT**

---

## Prezentarea interfetei

Formularul este organizat in mai multe file pentru a documenta toate aspectele prospectiunii.

### File principale

| # | Fila | Descriere |
|---|------|-----------|
| 1 | Identificare | Proiect, Nr. UT, Localizare |
| 2 | Descriere | Definitie, descriere, interpretare |
| 3 | Date UT | Conditii, metodologie, date |
| 4 | Analiza | Potential si risc arheologic |

### Bara de instrumente principala

| Buton | Functie |
|-------|---------|
| Prima | Salt la prima inregistrare |
| Ant. | Inregistrarea anterioara |
| Urm. | Inregistrarea urmatoare |
| Ultima | Salt la ultima inregistrare |
| Cautare | Cautare avansata |
| Salvare | Salvare inregistrare |
| Stergere | Stergere inregistrare |
| PDF | Export fisa PDF |
| **Lista PDF** | Export lista UT in PDF |
| **Export GNA** | Export in format GNA |
| Afisare strat | Afisare strat pe harta |

---

## Campuri de identificare

### Proiect

**Camp**: `comboBox_progetto`
**Baza de date**: `progetto`

Numele proiectului de prospectiune.

### Numarul UT

**Camp**: `comboBox_nr_ut`
**Baza de date**: `nr_ut`

Numarul progresiv al Unitatii Topografice.

### Litera UT

**Camp**: `lineEdit_ut_letterale`
**Baza de date**: `ut_letterale`

Sufix alfabetic optional (de ex., UT 15a, 15b).

---

## Campuri de localizare

### Date administrative

| Camp | Baza de date | Descriere |
|------|--------------|-----------|
| Tara | `nazione` | Tara |
| Regiune | `regione` | Regiune administrativa |
| Provincie | `provincia` | Provincie |
| Municipiu | `comune` | Municipiu |
| Fractiune | `frazione` | Fractiune/localitate |
| Localitate | `localita` | Toponim local |
| Adresa | `indirizzo` | Strada/drum |
| Nr. | `nr_civico` | Numarul strazii |

### Date cartografice

| Camp | Baza de date | Descriere |
|------|--------------|-----------|
| Harta IGM | `carta_topo_igm` | Foaia IGM |
| Harta CTR | `carta_ctr` | Element CTR |
| Foaie cadastrala | `foglio_catastale` | Referinta cadastru |

### Coordonate

| Camp | Baza de date | Descriere |
|------|--------------|-----------|
| Coord. geografice | `coord_geografiche` | Lat/Long (format: lat, lon) |
| Coord. plane | `coord_piane` | UTM/proiectie locala (format: x, y) |
| Altitudine | `quota` | Elevatia deasupra nivelului marii |
| Precizia coord. | `coordinate_precision` | Precizia GPS in metri |

**IMPORTANT**: Coordonatele sunt utilizate pentru generarea hartilor de densitate. Cel putin unul dintre campurile `coord_geografiche` sau `coord_piane` trebuie completat pentru fiecare UT.

---

## Campuri descriptive

### Definitia UT

**Camp**: `comboBox_def_ut`
**Baza de date**: `def_ut`
**Tezaur**: Cod 12.7

Clasificarea tipologica a UT. Valorile sunt incarcate din tezaur si traduse automat in limba curenta.

**Valori standard:**
| Cod | Engleza | Italiana |
|-----|---------|---------|
| scatter | Material scatter | Area di dispersione materiali |
| site | Archaeological site | Sito archeologico |
| anomaly | Terrain anomaly | Anomalia del terreno |
| structure | Outcropping structure | Struttura affiorante |
| concentration | Finds concentration | Concentrazione reperti |
| traces | Anthropic traces | Tracce antropiche |
| findspot | Sporadic find | Rinvenimento sporadico |
| negative | Negative result | Esito negativo |

### Descrierea UT

**Camp**: `textEdit_descrizione`
**Baza de date**: `descrizione_ut`

Descrierea detaliata a Unitatii Topografice.

**Continut:**
- Extensia si forma ariei
- Densitatea materialelor
- Caracteristicile terenului
- Vizibilitatea si conditiile

### Interpretarea UT

**Camp**: `textEdit_interpretazione`
**Baza de date**: `interpretazione_ut`

Interpretare functionala/istorica.

---

## Campuri de prospectiune cu tezaur

Urmatoarele campuri utilizeaza sistemul de tezaur pentru a asigura o terminologie standardizata tradusa in 7 limbi (IT, EN, DE, ES, FR, AR, CA).

### Tipul prospectiunii (12.1)

**Camp**: `comboBox_survey_type`
**Baza de date**: `survey_type`

| Cod | Engleza | Descriere |
|-----|---------|-----------|
| intensive | Intensive survey | Prospectiune sistematica intensiva |
| extensive | Extensive survey | Prospectiune prin esantionare |
| targeted | Targeted survey | Investigare a zonelor specifice |
| random | Random sampling | Metodologie aleatorie |

### Acoperirea vegetatiei (12.2)

**Camp**: `comboBox_vegetation_coverage`
**Baza de date**: `vegetation_coverage`

| Cod | Engleza | Descriere |
|-----|---------|-----------|
| none | Absent | Sol gol |
| sparse | Sparse | Acoperire < 25% |
| moderate | Moderate | Acoperire 25-50% |
| dense | Dense | Acoperire 50-75% |
| very_dense | Very dense | Acoperire > 75% |

### Metoda GPS (12.3)

**Camp**: `comboBox_gps_method`
**Baza de date**: `gps_method`

| Cod | Engleza | Descriere |
|-----|---------|-----------|
| handheld | Handheld GPS | Dispozitiv GPS portabil |
| dgps | Differential GPS | DGPS cu statie de baza |
| rtk | RTK GPS | Cinematica in timp real |
| total_station | Total station | Ridicare cu statie totala |

### Starea suprafetei (12.4)

**Camp**: `comboBox_surface_condition`
**Baza de date**: `surface_condition`

| Cod | Engleza | Descriere |
|-----|---------|-----------|
| ploughed | Ploughed | Camp arat recent |
| stubble | Stubble | Prezenta miriste |
| pasture | Pasture | Teren de pasune/faneata |
| woodland | Woodland | Zona impadurita |
| urban | Urban | Zona urbana/construita |

### Accesibilitate (12.5)

**Camp**: `comboBox_accessibility`
**Baza de date**: `accessibility`

| Cod | Engleza | Descriere |
|-----|---------|-----------|
| easy | Easy access | Fara restrictii |
| moderate_access | Moderate access | Unele dificultati |
| difficult | Difficult access | Probleme semnificative |
| restricted | Restricted access | Doar cu autorizatie |

### Conditii meteorologice (12.6)

**Camp**: `comboBox_weather_conditions`
**Baza de date**: `weather_conditions`

| Cod | Engleza | Descriere |
|-----|---------|-----------|
| sunny | Sunny | Vreme senina |
| cloudy | Cloudy | Conditii noroase |
| rainy | Rainy | Ploaie in timpul prospectiunii |
| windy | Windy | Vant puternic |

---

## Date de mediu

### Procentaj vizibilitate

**Camp**: `spinBox_visibility_percent`
**Baza de date**: `visibility_percent`

Procentajul vizibilitatii solului (0-100%). Valoare numerica importanta pentru calculul potentialului arheologic.

### Panta terenului

**Camp**: `lineEdit_andamento_terreno_pendenza`
**Baza de date**: `andamento_terreno_pendenza`

Morfologia si panta terenului.

### Utilizarea terenului

**Camp**: `lineEdit_utilizzo_suolo_vegetazione`
**Baza de date**: `utilizzo_suolo_vegetazione`

Utilizarea terenului la momentul prospectiunii.

---

## Date materiale

### Dimensiunile UT

**Camp**: `lineEdit_dimensioni_ut`
**Baza de date**: `dimensioni_ut`

Extensia in metri patrati.

### Descoperiri per mp

**Camp**: `lineEdit_rep_per_mq`
**Baza de date**: `rep_per_mq`

Densitatea materialelor per metru patrat. Valoare critica pentru calculul potentialului.

### Descoperiri databile

**Camp**: `lineEdit_rep_datanti`
**Baza de date**: `rep_datanti`

Descrierea materialelor diagnostice.

---

## Cronologie

### Perioada I

| Camp | Baza de date |
|------|--------------|
| Perioada I | `periodo_I` |
| Datare I | `datazione_I` |
| Interpretare I | `interpretazione_I` |

### Perioada II

| Camp | Baza de date |
|------|--------------|
| Perioada II | `periodo_II` |
| Datare II | `datazione_II` |
| Interpretare II | `interpretazione_II` |

---

## Fila Analiza - Potential si risc arheologic

Fila **Analiza** ofera instrumente avansate pentru calculul automat al potentialului si riscului arheologic.

### Potentialul arheologic

Sistemul calculeaza un scor de la 0 la 100 bazat pe factori ponderati:

| Factor | Pondere | Descriere | Cum se calculeaza |
|--------|---------|-----------|-------------------|
| Definitia UT | 30% | Tipul de evidenta arheologica | "site" = 100, "structure" = 90, "concentration" = 80, "scatter" = 60, etc. |
| Perioada istorica | 25% | Cronologia materialelor | Perioadele mai vechi au pondere mai mare (Preistoric = 90, Roman = 85, Medieval = 70, etc.) |
| Densitatea descoperirilor | 20% | Materiale per mp | >10/mp = 100, 5-10 = 80, 2-5 = 60, <2 = 40 |
| Starea suprafetei | 15% | Vizibilitate si accesibilitate | "ploughed" = 90, "stubble" = 70, "pasture" = 50, "woodland" = 30 |
| Documentatie | 10% | Calitatea documentatiei | Prezenta foto = +20, bibliografie = +30, investigatii = +50 |

**Clasificarea scorului:**

| Scor | Nivel | Culoare | Semnificatie |
|------|-------|---------|--------------|
| 80-100 | Ridicat | Verde | Probabilitate ridicata de depozite semnificative |
| 60-79 | Mediu-Ridicat | Galben-Verde | Probabilitate buna, verificare recomandata |
| 40-59 | Mediu | Portocaliu | Probabilitate moderata |
| 20-39 | Scazut | Rosu | Probabilitate scazuta |
| 0-19 | Nu poate fi evaluat | Gri | Date insuficiente |

### Riscul arheologic

Evalueaza riscul de impact/pierdere a patrimoniului:

| Factor | Pondere | Descriere | Cum se calculeaza |
|--------|---------|-----------|-------------------|
| Accesibilitate | 25% | Usurinta accesului in zona | "easy" = 80, "moderate" = 50, "difficult" = 30, "restricted" = 10 |
| Utilizarea terenului | 25% | Activitati agricole/constructii | "urban" = 90, "ploughed" = 70, "pasture" = 40, "woodland" = 20 |
| Constrangeri existente | 20% | Protectii legale | Fara constrangeri = 80, protectie peisagistica = 40, protectie arheologica = 10 |
| Investigatii anterioare | 15% | Starea cunoasterii | Fara investigatii = 60, prospectiune = 40, excavare = 20 |
| Potential | 15% | Invers proportional cu potentialul | Potential ridicat = risc ridicat de pierdere |

**Clasificarea riscului:**

| Scor | Nivel | Culoare | Actiune recomandata |
|------|-------|---------|---------------------|
| 75-100 | Ridicat | Rosu | Interventie urgenta, masuri de protectie imediata |
| 50-74 | Mediu | Portocaliu | Monitorizare activa, evaluare protectie |
| 25-49 | Scazut | Galben | Monitorizare periodica |
| 0-24 | Niciun risc | Verde | Nu este necesara interventie imediata |

### Campuri de baza de date pentru analiza

| Camp | Baza de date | Descriere |
|------|--------------|-----------|
| Scor potential | `potential_score` | Valoare calculata 0-100 |
| Scor risc | `risk_score` | Valoare calculata 0-100 |
| Factori potential | `potential_factors` | JSON cu detalii factori |
| Factori risc | `risk_factors` | JSON cu detalii factori |
| Data analizei | `analysis_date` | Marca temporala a calculului |
| Metoda analizei | `analysis_method` | Algoritmul utilizat |

---

## Straturi de geometrie UT

PyArchInit gestioneaza trei tipuri de geometrii pentru Unitatile Topografice:

### Tabele de geometrie

| Strat | Tabel | Tip geometrie | Utilizare |
|-------|-------|---------------|-----------|
| Puncte UT | `pyarchinit_ut_point` | Punct | Localizare punctuala |
| Linii UT | `pyarchinit_ut_line` | Linie | Urme, trasee |
| Poligoane UT | `pyarchinit_ut_polygon` | Poligon | Arii de dispersie |

### Crearea straturilor UT

1. **Prin Navigatorul QGIS:**
   - Deschideti baza de date in Navigator
   - Localizati tabelul `pyarchinit_ut_point/line/polygon`
   - Trageti pe harta

2. **Prin meniul PyArchInit:**
   - Meniu **PyArchInit** > **Instrumente GIS** > **Incarca straturi UT**
   - Selectati tipul de geometrie

### Conexiunea UT-Geometrie

Fiecare inregistrare de geometrie este legata de formularul UT prin:

| Camp | Descriere |
|------|-----------|
| `progetto` | Numele proiectului (trebuie sa corespunda) |
| `nr_ut` | Numarul UT (trebuie sa corespunda) |

### Fluxul de creare a geometriei

1. **Activati editarea** pe stratul UT dorit
2. **Desenati** geometria pe harta
3. **Completati** atributele `progetto` si `nr_ut`
4. **Salvati** stratul
5. **Verificati** conexiunea din formularul UT

---

## Generarea hartii de densitate

Modulul de generare a hartii de densitate permite vizualizarea distributiei spatiale a potentialului si riscului arheologic.

### Cerinte minime

- **Cel putin 2 UT** cu coordonate valide (`coord_geografiche` SAU `coord_piane`)
- **Scoruri calculate** pentru potential si/sau risc
- **CRS definit** in proiectul QGIS

### Metode de interpolare

| Metoda | Descriere | Cand se utilizeaza |
|--------|-----------|---------------------|
| **KDE** (Densitate kernel) | Estimare densitate kernel gaussian | Distributie continua, multe puncte |
| **IDW** (Distanta inversa) | Ponderare cu distanta inversa | Date rare, valori punctuale importante |
| **Grila** | Interpolare pe grila regulata | Analiza sistematica |

### Parametrii hartii de densitate

| Parametru | Valoare implicita | Descriere |
|-----------|-------------------|-----------|
| Dimensiune celula | 50 m | Rezolutia grilei |
| Latime de banda (KDE) | Auto | Raza de influenta |
| Putere (IDW) | 2 | Exponentul ponderarii |

### Procedura de generare

1. **Din formularul UT:**
   - Mergeti la fila **Analiza**
   - Verificati ca scorurile sunt calculate
   - Faceti clic pe **Generare harta de densitate**

2. **Selectati parametrii:**
   - Tip: Potential sau Risc
   - Metoda: KDE, IDW sau Grila
   - Dimensiune celula: de obicei 25-100 m

3. **Iesire:**
   - Strat raster adaugat in QGIS
   - Salvat in `pyarchinit_Raster_folder`
   - Simbologie aplicata automat

### Harta de densitate cu masca poligon (GNA)

Pentru a genera harti de densitate **in interiorul unei arii de proiect** (de ex., perimetrul de studiu):

1. **Pregatiti poligonul** pentru aria proiectului
2. **Utilizati Export GNA** (vezi sectiunea urmatoare)
3. Sistemul **aplica automat masca** pe harta de densitate conform poligonului

---

## Export GNA - Geoportalul National pentru Arheologie

### Ce este GNA?

**Geoportalul National pentru Arheologie** (GNA) este sistemul informatic al Ministerului Culturii din Italia pentru gestionarea datelor arheologice teritoriale. PyArchInit suporta exportul in formatul standard GNA GeoPackage.

### Structura GNA GeoPackage

| Strat | Tip | Descriere |
|-------|-----|-----------|
| **MOPR** | Poligon | Aria/perimetrul proiectului |
| **MOSI** | Punct/Poligon | Situri arheologice (UT) |
| **VRP** | MultiPoligon | Harta potentialului arheologic |
| **VRD** | MultiPoligon | Harta riscului arheologic |

### Maparea campurilor UT la MOSI GNA

| Camp GNA | Camp UT PyArchInit | Note |
|----------|---------------------|------|
| ID | `{progetto}_{nr_ut}` | Identificator compus |
| AMA | `def_ut` | Vocabular controlat GNA |
| OGD | `interpretazione_ut` | Definitia obiectului |
| OGT | `geometria` | Tipul geometriei |
| DES | `descrizione_ut` | Descriere (max 10000 caractere) |
| OGM | `metodo_rilievo_e_ricognizione` | Metoda de identificare |
| DTSI | `periodo_I` -> data | Data de inceput (negativa pentru i.Hr.) |
| DTSF | `periodo_II` -> data | Data de sfarsit |
| PRVN | `nazione` | Tara |
| PVCR | `regione` | Regiune |
| PVCP | `provincia` | Provincie |
| PVCC | `comune` | Municipiu |
| LCDQ | `quota` | Elevatia |

### Clasificare VRP (Potential)

| Interval | Cod GNA | Eticheta | Culoare |
|----------|---------|----------|---------|
| 0-20 | NV | Nu poate fi evaluat | Gri |
| 20-40 | NU | Niciun potential | Verde |
| 40-60 | BA | Scazut | Galben |
| 60-80 | ME | Mediu | Portocaliu |
| 80-100 | AL | Ridicat | Rosu |

### Clasificare VRD (Risc)

| Interval | Cod GNA | Eticheta | Culoare |
|----------|---------|----------|---------|
| 0-25 | NU | Niciun risc | Verde |
| 25-50 | BA | Scazut | Galben |
| 50-75 | ME | Mediu | Portocaliu |
| 75-100 | AL | Ridicat | Rosu |

### Procedura de export GNA

1. **Pregatirea datelor:**
   - Verificati ca toate UT au coordonate
   - Calculati scorurile de potential/risc
   - Pregatiti poligonul ariei proiectului (MOPR)

2. **Initiati exportul:**
   - Din formularul UT, faceti clic pe **Export GNA**
   - Sau meniu **PyArchInit** > **GNA** > **Export**

3. **Configurare:**
   ```
   Proiect: [selectati proiectul]
   Aria proiectului: [selectati stratul poligon MOPR]
   Iesire: [calea fisierului .gpkg]

   [x] Export MOSI (situri)
   [x] Generare VRP (potential)
   [x] Generare VRD (risc)

   Metoda harta de densitate: KDE
   Dimensiune celula: 50 m
   ```

4. **Executie:**
   - Faceti clic pe **Export**
   - Asteptati generarea (poate dura cateva minute)
   - GeoPackage este salvat la calea specificata

5. **Verificati iesirea:**
   - Deschideti GeoPackage in QGIS
   - Verificati straturile MOPR, MOSI, VRP, VRD
   - Verificati ca geometriile VRP/VRD sunt decupate la MOPR

### Validare GNA

Pentru a valida iesirea conform specificatiilor GNA:

1. Incarcati GeoPackage in **sablonul oficial GNA**
2. Verificati ca straturile sunt recunoscute
3. Verificati vocabularele controlate
4. Verificati relatiile geometrice (MOSI in interiorul MOPR)

---

## Export PDF

### Fisa UT individuala

Exporta fisa UT completa in format PDF profesional.

**Continut:**
- Antet cu proiect si numarul UT
- Sectiunea de identificare
- Sectiunea de localizare
- Sectiunea de teren
- Sectiunea de date de prospectiune
- Sectiunea de cronologie
- Sectiunea de analiza (potential/risc cu bare colorate)
- Sectiunea de documentatie

**Procedura:**
1. Selectati inregistrarea UT
2. Faceti clic pe butonul **PDF** din bara de instrumente
3. PDF-ul este salvat in `pyarchinit_PDF_folder`

### Lista UT (Lista PDF)

Exporta o lista tabelara a tuturor UT in format peisaj.

**Coloane:**
- UT, Proiect, Definitie, Interpretare
- Municipiu, Coordonate, Perioada I, Perioada II
- Descoperiri/mp, Vizibilitate, Potential, Risc

**Procedura:**
1. Incarcati UT de exportat (cautare sau vizualizare totala)
2. Faceti clic pe butonul **Lista PDF** din bara de instrumente
3. PDF-ul este salvat ca `UT_List.pdf`

### Raport de analiza UT

Genereaza un raport detaliat de analiza potential/risc.

**Continut:**
1. Date de identificare UT
2. Sectiunea de potential arheologic
   - Scor cu indicator grafic
   - Text narativ descriptiv
   - Tabel de factori cu contributii
3. Sectiunea de risc arheologic
   - Scor cu indicator grafic
   - Text narativ cu recomandari
   - Tabel de factori cu contributii
4. Sectiunea de metodologie

---

## Flux de lucru operational complet

### Faza 1: Configurarea proiectului

1. **Creati un proiect nou** in PyArchInit sau utilizati unul existent
2. **Definiti aria de studiu** (poligon MOPR)
3. **Configurati CRS** al proiectului QGIS

### Faza 2: Inregistrarea UT pe teren

1. **Deschideti formularul UT**
2. **Inregistrare noua** (faceti clic pe "Inregistrare noua")
3. **Completati datele de identificare:**
   ```
   Proiect: Prospectiunea Vaii Tibrului 2024
   Nr. UT: 25
   ```

4. **Completati localizarea:**
   ```
   Regiune: Lazio
   Provincie: Roma
   Municipiu: Fiano Romano
   Localitate: Colle Alto
   Coord. geografice: 42.1234, 12.5678
   Altitudine: 125 m
   Precizie GPS: 3 m
   ```

5. **Completati descrierea** (utilizand tezaurul):
   ```
   Definitie: Concentratie de descoperiri
   Descriere: Zona eliptica de aprox. 50x30 m
   cu concentratie de fragmente ceramice
   si tigla pe versantul sudic...
   ```

6. **Completati datele de prospectiune** (utilizand tezaurul):
   ```
   Tipul prospectiunii: Prospectiune intensiva
   Acoperire vegetatie: Rara
   Metoda GPS: GPS diferential
   Starea suprafetei: Arat
   Accesibilitate: Acces usor
   Conditii meteorologice: Senin
   Vizibilitate: 80%
   Data: 15/04/2024
   Responsabil: Echipa A
   ```

7. **Completati materialele si cronologia:**
   ```
   Dimensiuni: 1500 mp
   Descoperiri/mp: 5-8
   Descoperiri databile: Ceramica comuna,
   sigillata italiana, tigla

   Perioada I: Roman
   Datare I: sec. I-II d.Hr.
   Interpretare I: Vila rurala
   ```

8. **Salvare** (faceti clic pe "Salvare")

### Faza 3: Crearea geometriei

1. **Incarcati stratul** `pyarchinit_ut_polygon`
2. **Activati editarea**
3. **Desenati** perimetrul UT pe harta
4. **Completati atributele**: progetto, nr_ut
5. **Salvati** stratul

### Faza 4: Analiza

1. **Deschideti fila Analiza** in formularul UT
2. **Verificati** scorurile calculate automat
3. **Generati harta de densitate** daca este necesar
4. **Exportati raportul PDF** al analizei

### Faza 5: Export GNA (daca este necesar)

1. **Verificati completitudinea datelor** pentru toate UT
2. **Pregatiti poligonul MOPR** al ariei proiectului
3. **Executati Export GNA**
4. **Validati iesirea** conform specificatiilor GNA

---

## Sfaturi si trucuri

### Optimizarea fluxului de lucru

1. **Pre-populati tezaurele** inainte de a incepe prospectiunile
2. **Utilizati sabloane de proiect** cu date comune presetate
3. **Sincronizati coordonatele** din GPS in campul `coord_geografiche`
4. **Salvati frecvent** in timpul introducerii datelor

### Imbunatatirea calitatii datelor

1. **Completati TOATE campurile relevante** pentru fiecare UT
2. **Utilizati intotdeauna tezaurele** in loc de text liber
3. **Verificati coordonatele** pe harta inainte de salvare
4. **Documentati fotografic** fiecare UT

### Optimizarea hartii de densitate

1. **Dimensiune celula adecvata**: utilizati 25-50m pentru arii mici, 100-200m pentru arii extinse
2. **Metoda KDE** pentru distributii continue si omogene
3. **Metoda IDW** cand valorile punctuale sunt critice
4. **Verificati intotdeauna** ca coordonatele sunt corecte inainte de generare

### Export GNA eficient

1. **Pregatiti poligonul MOPR** in avans ca strat separat
2. **Verificati ca toate UT** au coordonate valide
3. **Calculati scorurile** inainte de export
4. **Utilizati nume descriptive** pentru fisierele GeoPackage

### Gestionare multi-utilizator

1. **Definiti conventii de denumire comune** pentru numerotarea UT
2. **Utilizati baza de date PostgreSQL** pentru acces concurent
3. **Sincronizati periodic** datele
4. **Documentati modificarile** in campurile de note

---

## Depanare

### Problema: Casete combo tezaur goale

**Simptome:** Listele derulante pentru survey_type, vegetatie, etc. sunt goale.

**Cauze:**
- Intrarile tezaurului nu sunt prezente in baza de date
- Cod de limba gresit
- Tabelul tezaurului nu este actualizat

**Solutii:**
1. Meniu **PyArchInit** > **Baza de date** > **Actualizare baza de date**
2. Verificati tabelul `pyarchinit_thesaurus_sigle` pentru intrarile `ut_table`
3. Verificati setarile de limba
4. Daca este necesar, reimportati tezaurele din sablon

### Problema: Coordonate invalide

**Simptome:** Eroare la salvare sau coordonate afisate in pozitie gresita.

**Cauze:**
- Format gresit (virgula vs punct zecimal)
- Sistem de coordonate nepotrivit
- Ordine lat/lon inversata

**Solutii:**
1. Format corect pentru `coord_geografiche`: `42.1234, 12.5678` (lat, lon)
2. Format corect pentru `coord_piane`: `1234567.89, 4567890.12` (x, y)
3. Utilizati intotdeauna punctul ca separator zecimal
4. Verificati CRS-ul proiectului QGIS

### Problema: UT nu este vizibila pe harta

**Simptome:** Dupa salvare, UT nu apare pe harta.

**Cauze:**
- Geometria nu este creata in strat
- Atributele `progetto`/`nr_ut` nu corespund
- Stratul nu este incarcat sau este ascuns
- CRS diferit intre strat si proiect

**Solutii:**
1. Verificati ca stratul `pyarchinit_ut_point/polygon` exista
2. Verificati ca atributele sunt completate corect
3. Activati vizibilitatea stratului in panoul Straturi
4. Utilizati "Zoom la strat" pentru a verifica extinderea

### Problema: Harta de densitate nu este generata

**Simptome:** Eroare "Sunt necesare cel putin 2 puncte cu coordonate valide".

**Cauze:**
- Mai putin de 2 UT cu coordonate
- Coordonate in format gresit
- Campuri de coordonate goale

**Solutii:**
1. Verificati ca cel putin 2 UT au `coord_geografiche` SAU `coord_piane` completate
2. Verificati formatul coordonatelor (punct zecimal, ordine corecta)
3. Recalculati scorurile inainte de generarea hartii de densitate
4. Verificati ca campurile nu contin caractere speciale

### Problema: Scorul de potential/risc nu este calculat

**Simptome:** Campurile potential_score si risk_score sunt goale sau zero.

**Cauze:**
- Campuri obligatorii necompletate
- Valori din tezaur nerecunoscute
- Eroare de calcul

**Solutii:**
1. Completati cel putin: `def_ut`, `periodo_I`, `visibility_percent`
2. Utilizati valori din tezaur (nu text liber)
3. Salvati inregistrarea si redeschideti
4. Verificati jurnalele QGIS pentru erori

### Problema: Exportul GNA a esuat

**Simptome:** GeoPackage nu este creat sau este incomplet.

**Cauze:**
- Modulul GNA nu este disponibil
- Date UT incomplete
- Poligon MOPR invalid
- Permisiuni de scriere insuficiente

**Solutii:**
1. Verificati ca modulul `modules/gna` este instalat
2. Verificati ca toate UT au coordonate valide
3. Verificati ca poligonul MOPR este valid (fara autointersectii)
4. Verificati permisiunile pe folderul de iesire
5. Verificati spatiul pe disc suficient

### Problema: Export PDF cu campuri lipsa

**Simptome:** PDF-ul generat nu afiseaza unele campuri sau afiseaza valori gresite.

**Cauze:**
- Campurile bazei de date nu sunt actualizate
- Versiune schema baza de date invechita
- Datele nu sunt salvate inainte de export

**Solutii:**
1. Salvati inregistrarea inainte de export
2. Actualizati baza de date daca este necesar
3. Verificati ca campurile noi (v4.9.67+) exista in tabel

### Problema: Eroare Qt6/QGIS 4.x

**Simptome:** Pluginul nu se incarca pe QGIS 4.x cu eroare `AllDockWidgetFeatures`.

**Cauze:**
- Incompatibilitate Qt5/Qt6
- Fisier UI neactualizat

**Solutii:**
1. Actualizati PyArchInit la ultima versiune
2. Fisierul `UT_ui.ui` trebuie sa utilizeze indicatoare explicite in loc de `AllDockWidgetFeatures`

---

## Referinte

### Baza de date

- **Tabel**: `ut_table`
- **Clasa mapper**: `UT`
- **ID**: `id_ut`

### Tabele de geometrie

- **Puncte**: `pyarchinit_ut_point`
- **Linii**: `pyarchinit_ut_line`
- **Poligoane**: `pyarchinit_ut_polygon`

### Fisiere sursa

| Fisier | Descriere |
|--------|-----------|
| `gui/ui/UT_ui.ui` | Interfata utilizator Qt |
| `tabs/UT.py` | Controller principal |
| `modules/utility/pyarchinit_exp_UTsheet_pdf.py` | Export fisa PDF |
| `modules/utility/pyarchinit_exp_UT_analysis_pdf.py` | Export analiza PDF |
| `modules/analysis/ut_potential.py` | Calculul potentialului |
| `modules/analysis/ut_risk.py` | Calculul riscului |
| `modules/analysis/ut_heatmap_generator.py` | Generarea hartii de densitate |
| `modules/gna/gna_exporter.py` | Export GNA |
| `modules/gna/gna_vocabulary_mapper.py` | Maparea vocabularului GNA |

### Coduri tezaur UT

| Cod | Camp | Descriere |
|-----|------|-----------|
| 12.1 | survey_type | Tipul prospectiunii |
| 12.2 | vegetation_coverage | Acoperirea vegetatiei |
| 12.3 | gps_method | Metoda GPS |
| 12.4 | surface_condition | Starea suprafetei |
| 12.5 | accessibility | Accesibilitate |
| 12.6 | weather_conditions | Conditii meteorologice |
| 12.7 | def_ut | Definitia UT |

---

## Tutoriale video

### Documentarea prospectiunii
**Durata**: 15-18 minute
- Inregistrarea UT
- Date de prospectiune cu tezaur
- Geolocalizare

### Analiza potential si risc
**Durata**: 10-12 minute
- Calculul automat al scorurilor
- Interpretarea rezultatelor
- Generarea hartii de densitate

### Export GNA
**Durata**: 12-15 minute
- Pregatirea datelor
- Configurarea exportului
- Validarea iesirii

### Export raport PDF
**Durata**: 8-10 minute
- Fisa UT standard
- Lista UT
- Raport de analiza cu harti

---

*Ultima actualizare: ianuarie 2026*
*PyArchInit v4.9.68 - Sistem de gestionare a datelor arheologice*
