# Tutorial 16: Fișa Ceramică (Ceramică Specializată)

## Cuprins
1. [Introducere](#introducere)
2. [Accesarea Fișei](#accesarea-fișei)
3. [Interfața Utilizatorului](#interfața-utilizatorului)
4. [Câmpuri Principale](#câmpuri-principale)
5. [Tab-urile Fișei](#tab-urile-fișei)
6. [Instrumente Ceramică](#instrumente-ceramică)
7. [Căutare Vizuală de Similitudine](#căutare-vizuală-de-similitudine)
8. [Cuantificări](#cuantificări)
9. [Gestionarea Media](#gestionarea-media)
10. [Export și Rapoarte](#export-și-rapoarte)
11. [Flux de Lucru Operațional](#flux-de-lucru-operațional)
12. [Bune Practici](#bune-practici)
13. [Depanare](#depanare)

---

## Introducere

**Fișa Ceramică** este un instrument specializat pentru catalogarea detaliată a ceramicii arheologice. Spre deosebire de formularul Inventar Materiale (mai generalist), această fișă este concepută specific pentru analiza ceramică aprofundată, cu câmpuri dedicate pentru pastă, clasă ceramică, decoruri și măsurători specifice vaselor.

### Diferențe față de Fișa Inventar Materiale

| Aspect | Inventar Materiale | Ceramică |
|--------|---------------------|---------|
| **Scop** | Toate tipurile de artefacte | Doar ceramică |
| **Detaliu** | General | Specializat |
| **Câmpuri pastă** | Corp ceramic (generic) | Pastă detaliată |
| **Decoruri** | Câmp unic | Interior/Exterior separat |
| **Măsurători** | Generice | Specifice vaselor |
| **Instrumente AI** | SketchGPT | PotteryInk, YOLO, Căutare Similitudine |

### Funcții Avansate

Fișa Ceramică include funcții AI de ultimă generație:
- **PotteryInk**: Generarea automată a desenelor arheologice din fotografii
- **Detecție YOLO**: Recunoașterea automată a formelor ceramice
- **Căutare Vizuală de Similitudine**: Căutarea ceramicii similare prin embedding-uri vizuale
- **Generator Layout**: Generarea automată a planșelor ceramice

---

## Accesarea Fișei

### Din Meniu

1. Deschideți QGIS cu pluginul PyArchInit activ
2. Meniu **PyArchInit** → **Gestionare înregistrări arheologice** → **Artefact** → **Ceramică**

### Din Bara de Instrumente

1. Localizați bara de instrumente PyArchInit
2. Faceți clic pe pictograma **Ceramică** (pictogramă vas/amforă)

---

## Interfața Utilizatorului

Interfața este organizată eficient pentru catalogarea ceramicii:

### Zone Principale

| Zonă | Descriere |
|------|-----------|
| **1. Antet** | Bara DBMS, indicatori de stare, filtre |
| **2. Identificare** | Sit, Zonă, US, Număr ID, Cutie, Pungă |
| **3. Clasificare** | Formă, Clasă, Pastă, Material |
| **4. Tab-uri Detalii** | Descriere, Date Tehnice, Suplimente |
| **5. Panou Media** | Vizualizator imagini, previzualizare |

### Tab-uri Disponibile

| Tab | Conținut |
|-----|---------|
| **Date descriptive** | Descriere, decoruri, note |
| **Date Tehnice** | Măsurători, tratament suprafață, Munsell |
| **Suplimente** | Bibliografie, Statistici |

---

## Câmpuri Principale

### Câmpuri de Identificare

#### Număr ID
- **Tip**: Integer
- **Obligatoriu**: Da
- **Descriere**: Numărul unic de identificare al fragmentului ceramic
- **Constrângere**: Unic pe sit

#### Sit
- **Tip**: ComboBox
- **Obligatoriu**: Da
- **Descriere**: Situl arheologic de origine

#### Zonă
- **Tip**: ComboBox editabil
- **Descriere**: Zona de săpătură

#### US (Unitate Stratigrafică)
- **Tip**: Integer
- **Descriere**: Numărul US de descoperire

#### Sector
- **Tip**: Text
- **Descriere**: Sectorul specific de descoperire

### Câmpuri de Depozitare

#### Cutie
- **Tip**: Integer
- **Descriere**: Numărul cutiei de depozitare

#### Pungă
- **Tip**: Integer
- **Descriere**: Numărul pungii

#### An
- **Tip**: Integer
- **Descriere**: Anul descoperirii/catalogării

### Câmpuri de Clasificare Ceramică

#### Formă
- **Tip**: ComboBox editabil
- **Recomandat**: Da
- **Valori tipice**: Bol, Borcan, Cană, Farfurie, Ceașcă, Amforă, Capac, etc.
- **Descriere**: Forma generală a vasului

#### Formă Specifică
- **Tip**: ComboBox editabil
- **Descriere**: Tipologie specifică (ex.: Hayes 50, Dressel 1)

#### Formă Detaliată
- **Tip**: Text
- **Descriere**: Variantă morfologică detaliată

#### Clasă Ceramică
- **Tip**: ComboBox editabil
- **Descriere**: Clasa ceramică
- **Exemple**:
  - Sigilată africană
  - Sigilată italică
  - Ceramică cu pereți subțiri
  - Ceramică comună
  - Amforă
  - Ceramică de bucătărie

#### Material
- **Tip**: ComboBox editabil
- **Descriere**: Materialul de bază
- **Valori**: Ceramică, Teracotă, Porțelan, etc.

#### Pastă
- **Tip**: ComboBox editabil
- **Descriere**: Tipul pastei ceramice
- **Caracteristici de considerat**:
  - Culoarea pastei
  - Granulometria incluziunilor
  - Duritatea
  - Porozitatea

### Câmpuri de Conservare

#### Procent
- **Tip**: ComboBox editabil
- **Descriere**: Procentul păstrat din vas
- **Valori tipice**: <10%, 10-25%, 25-50%, 50-75%, >75%, Complet

#### CANT (Cantitate)
- **Tip**: Integer
- **Descriere**: Număr de fragmente

### Câmpuri de Documentare

#### Foto
- **Tip**: Text
- **Descriere**: Referință fotografică

#### Desen
- **Tip**: Text
- **Descriere**: Referință desen

---

## Tab-urile Fișei

### Tab 1: Date Descriptive

Tab-ul principal pentru descrierea fragmentului.

#### Decoruri

| Câmp | Descriere |
|------|-----------|
| **Decor Exterior** | Tipul decorului exterior |
| **Decor Interior** | Tipul decorului interior |
| **Descriere Decor Exterior** | Descrierea detaliată a decorului exterior |
| **Descriere Decor Interior** | Descrierea detaliată a decorului interior |
| **Tip Decor** | Tipologia decorativă (Pictat, Incizat, Aplicat, etc.) |
| **Motiv Decor** | Motivul decorativ (Geometric, Vegetal, Figurativ) |
| **Poziție Decor** | Poziția decorului (Buză, Corp, Bază, Toartă) |

#### Realizat la Roată
- **Tip**: ComboBox
- **Valori**: Da, Nu, Necunoscut
- **Descriere**: Indică dacă vasul a fost realizat la roată

#### Note
- **Tip**: TextEdit multilinie
- **Descriere**: Note și observații suplimentare

#### Vizualizator Media
Zonă pentru vizualizarea imaginilor asociate:
- Glisare și plasare pentru asocierea imaginilor
- Dublu clic pentru deschiderea vizualizatorului complet
- Butoane pentru gestionarea etichetelor

### Tab 2: Date Tehnice

Date tehnice și măsurători.

#### Culoarea Munsell
- **Tip**: ComboBox editabil
- **Descriere**: Codul culorii Munsell al pastei
- **Format**: ex.: „10YR 7/4", „5YR 6/6"
- **Notă**: Consultați Munsell Soil Color Chart

#### Tratament Suprafață
- **Tip**: ComboBox editabil
- **Descriere**: Tratamentul suprafeței
- **Valori tipice**:
  - Slip
  - Brunisare
  - Glazurare
  - Pictare
  - Simplu

#### Măsurători (în cm)

| Câmp | Descriere |
|------|-----------|
| **Diametru Max** | Diametrul maxim al vasului |
| **Diametru Buză** | Diametrul buzei |
| **Diametru Bază** | Diametrul bazei |
| **Înălțime Totală** | Înălțime totală (dacă reconstituibilă) |
| **Înălțime Păstrată** | Înălțimea păstrată |

#### Datare
- **Tip**: ComboBox editabil
- **Descriere**: Cadrul cronologic
- **Format**: Text (ex.: „sec. I-II d.Hr.")

### Tab 3: Suplimente

Tab cu sub-secțiuni pentru date suplimentare.

#### Sub-Tab: Bibliografie
Gestionarea referințelor bibliografice pentru comparații tipologice.

| Coloană | Descriere |
|---------|-----------|
| Autor | Autori |
| An | Anul publicării |
| Titlu | Titlu abreviat |
| Pagină | Referință pagină |
| Figură | Figură/Planșă |

#### Sub-Tab: Statistici
Acces la funcții de cuantificare și diagrame statistice.

---

## Instrumente Ceramică

Fișa Ceramică include un set puternic de instrumente AI pentru procesarea imaginilor ceramice.

### Accesarea Instrumentelor Ceramică

1. Meniu **PyArchInit** → **Gestionare înregistrări arheologice** → **Artefact** → **Instrumente Ceramică**

Sau din butonul dedicat din Fișa Ceramică.

### PotteryInk - Generare Desene

Transformă automat fotografiile ceramice în desene arheologice stilizate.

#### Utilizare

1. Selectați o imagine ceramică
2. Faceți clic pe „Generare Desen"
3. Sistemul procesează imaginea cu AI
4. Desenul este generat în stil arheologic

#### Cerințe
- Mediu virtual dedicat (creat automat)
- Modele AI pre-antrenate
- GPU recomandat pentru performanță optimă

### Detecție YOLO Ceramică

Recunoașterea automată a formelor ceramice în imagini.

#### Funcții

- Identifică automat forma vasului
- Sugerează clasificarea
- Detectează părți anatomice (buză, perete, bază, toartă)

### Generator Layout

Generează automat planșe ceramice pentru publicare.

#### Rezultat

- Planșe în format arheologic standard
- Scară metrică automată
- Layout optimizat
- Export în PDF sau imagine

### Extractor PDF

Extrage imagini ceramice din publicații PDF pentru comparații.

---

## Căutare Vizuală de Similitudine

Funcție avansată pentru găsirea ceramicii vizual similare în baza de date.

### Cum Funcționează

Sistemul folosește **embedding-uri vizuale** generate de modele de deep learning pentru a reprezenta fiecare imagine ceramică ca un vector numeric. Căutarea găsește ceramica cu vectorii cei mai similari.

### Utilizare

1. Selectați o imagine de referință
2. Faceți clic pe „Găsește Similar"
3. Sistemul caută în baza de date
4. Ceramica cea mai similară este afișată ordonată după similitudine

### Modele Disponibile

- **ResNet50**: Echilibru bun viteză/precizie
- **EfficientNet**: Performanță optimă
- **CLIP**: Căutare multimodală (text + imagine)

### Actualizarea Embedding-urilor

Embedding-urile sunt generate automat la adăugarea de imagini noi. Este posibilă forțarea actualizării din meniul Instrumente Ceramică.

---

## Cuantificări

### Acces

1. Faceți clic pe butonul **Quant** din bara de instrumente
2. Selectați parametrul de cuantificare
3. Vizualizați diagrama

### Parametri Disponibili

| Parametru | Descriere |
|-----------|-----------|
| **Pastă** | Distribuție pe tip de pastă |
| **US** | Distribuție pe unitate stratigrafică |
| **Zonă** | Distribuție pe zonă de săpătură |
| **Material** | Distribuție pe material |
| **Procent** | Distribuție pe procent păstrat |
| **Formă** | Distribuție pe formă |
| **Formă specifică** | Distribuție pe formă specifică |
| **Clasă ceramică** | Distribuție pe clasă ceramică |
| **Culoare Munsell** | Distribuție pe culoare |
| **Tratament suprafață** | Distribuție pe tratament suprafață |
| **Decor exterior** | Distribuție pe decor exterior |
| **Decor interior** | Distribuție pe decor interior |
| **Realizat la roată** | Distribuție roată da/nu |

### Export Cuantificări

Datele sunt exportate în:
- Fișier CSV în `pyarchinit_Quantificazioni_folder`
- Diagramă afișată pe ecran

---

## Gestionarea Media

### Asocierea Imaginilor

#### Metode

1. **Glisare și Plasare**: Glisați imaginile în listă
2. **Butonul Toate Imaginile**: Încărcați toate imaginile asociate
3. **Căutare Imagini**: Căutați imagini specifice

### Player Video

Pentru ceramica cu documentație video, este disponibil un player integrat.

### Integrare Cloudinary

Suport pentru imagini la distanță pe Cloudinary:
- Încărcare automată miniaturi
- Cache local pentru performanță
- Sincronizare cloud

---

## Export și Rapoarte

### Export Fișă PDF

Generează o fișă PDF completă cu:
- Date de identificare
- Clasificare
- Măsurători
- Imagini asociate
- Note

### Export Listă

Generează lista PDF a tuturor înregistrărilor afișate.

### Export Date

Buton pentru export în format tabelar (CSV/Excel).

---

## Flux de Lucru Operațional

### Înregistrarea unui Fragment Ceramic Nou

#### Pasul 1: Deschidere și Înregistrare Nouă
1. Deschideți Fișa Ceramică
2. Faceți clic pe **Înregistrare nouă**

#### Pasul 2: Date de Identificare
1. Verificați/selectați **Sit**
2. Introduceți **Număr ID** (progresiv)
3. Introduceți **Zonă**, **US**, **Sector**
4. Introduceți **Cutie** și **Pungă**

#### Pasul 3: Clasificare
1. Selectați **Formă** (Bol, Borcan, etc.)
2. Selectați **Clasă ceramică** (clasa ceramică)
3. Selectați **Pastă** (tipul pastei)
4. Indicați **Material** și **Procent**

#### Pasul 4: Date Tehnice
1. Deschideți tab-ul **Date Tehnice**
2. Introduceți **culoarea Munsell**
3. Selectați **Tratament suprafață**
4. Introduceți **măsurătorile** (diametre, înălțimi)
5. Indicați **Realizat la roată**

#### Pasul 5: Decoruri (dacă sunt prezente)
1. Reveniți la tab-ul **Date descriptive**
2. Selectați tipul **Decor Exterior/Interior**
3. Completați descrierile detaliate
4. Indicați **Tip decor**, **motiv**, **poziție**

#### Pasul 6: Documentare
1. Asociați fotografii (glisare și plasare)
2. Introduceți referința **Foto** și **Desen**
3. Completați **Note** cu observații

#### Pasul 7: Datare și Comparații
1. Introduceți **Datarea**
2. Deschideți tab-ul **Suplimente** → **Bibliografie**
3. Adăugați referințe bibliografice

#### Pasul 8: Salvare
1. Faceți clic pe **Salvare**
2. Verificați confirmarea

---

## Bune Practici

### Clasificare Consistentă

- Folosiți vocabulare standardizate pentru Formă, Clasă, Pastă
- Mențineți consistența în nomenclatură
- Actualizați tezaurul când este necesar

### Documentare Fotografică

- Fotografiați fiecare fragment cu scară
- Includeți vedere interioară și exterioară
- Documentați detaliile decorative

### Măsurători

- Folosiți șublerul pentru măsurători precise
- Indicați întotdeauna unitatea de măsură (cm)
- Pentru fragmente, măsurați doar părțile păstrate

### Culoarea Munsell

- Folosiți întotdeauna Munsell Soil Color Chart
- Măsurați pe fractură proaspătă
- Indicați condițiile de iluminare

### Utilizarea Instrumentelor AI

- Verificați întotdeauna rezultatele automate
- PotteryInk funcționează mai bine cu fotografii de bună calitate
- Căutarea de similitudine este utilă pentru comparații, nu înlocuiește analiza

---

## Depanare

### Probleme Frecvente

#### Număr ID Duplicat
- **Eroare**: „Există deja o înregistrare cu acest ID"
- **Soluție**: Verificați următorul număr disponibil

#### Instrumentele Ceramică nu pornesc
- **Cauză**: Mediul virtual nu este configurat
- **Soluție**:
  1. Verificați conexiunea la internet
  2. Așteptați configurarea automată
  3. Verificați jurnalul în `pyarchinit/bin/pottery_venv`

#### PotteryInk lent
- **Cauză**: Procesare pe CPU în loc de GPU
- **Soluție**:
  1. Instalați driverele CUDA (NVIDIA)
  2. Verificați că PyTorch folosește GPU

#### Căutare Similitudine Goală
- **Cauză**: Embedding-urile nu sunt generate
- **Soluție**:
  1. Deschideți Instrumente Ceramică
  2. Faceți clic pe „Actualizare Embedding-uri"
  3. Așteptați finalizarea

#### Imaginile nu se încarcă
- **Cauză**: Cale incorectă sau Cloudinary nu este configurat
- **Soluție**:
  1. Verificați configurarea căii în Setări
  2. Pentru Cloudinary: verificați credențialele

---

## Tutorial Video

### Video 1: Prezentarea Fișei Ceramică
*Durată: 5-6 minute*

[Substituent video]

### Video 2: Înregistrare Completă Ceramică
*Durată: 8-10 minute*

[Substituent video]

### Video 3: Instrumente Ceramică și AI
*Durată: 10-12 minute*

[Substituent video]

### Video 4: Căutare Similitudine
*Durată: 5-6 minute*

[Substituent video]

---

## Rezumat Câmpuri Bază de Date

| Câmp | Tip | Baza de date | Obligatoriu |
|------|-----|--------------|-------------|
| Număr ID | Integer | id_number | Da |
| Sit | Text | sito | Da |
| Zonă | Text | area | Nu |
| US | Integer | us | Nu |
| Cutie | Integer | box | Nu |
| Pungă | Integer | bag | Nu |
| Sector | Text | sector | Nu |
| Foto | Text | photo | Nu |
| Desen | Text | drawing | Nu |
| An | Integer | anno | Nu |
| Pastă | Text | fabric | Nu |
| Procent | Text | percent | Nu |
| Material | Text | material | Nu |
| Formă | Text | form | Nu |
| Formă Specifică | Text | specific_form | Nu |
| Formă Detaliată | Text | specific_shape | Nu |
| Clasă Ceramică | Text | ware | Nu |
| Culoare Munsell | Text | munsell | Nu |
| Tratament Suprafață | Text | surf_trat | Nu |
| Decor Exterior | Text | exdeco | Nu |
| Decor Interior | Text | intdeco | Nu |
| Realizat la Roată | Text | wheel_made | Nu |
| Descriere Decor Ext. | Text | descrip_ex_deco | Nu |
| Descriere Decor Int. | Text | descrip_in_deco | Nu |
| Note | Text | note | Nu |
| Diametru Max | Numeric | diametro_max | Nu |
| CANT | Integer | qty | Nu |
| Diametru Buză | Numeric | diametro_rim | Nu |
| Diametru Bază | Numeric | diametro_bottom | Nu |
| Înălțime Totală | Numeric | diametro_height | Nu |
| Înălțime Păstrată | Numeric | diametro_preserved | Nu |
| Tip Decor | Text | decoration_type | Nu |
| Motiv Decor | Text | decoration_motif | Nu |
| Poziție Decor | Text | decoration_position | Nu |
| Datare | Text | datazione | Nu |

---

*Ultima actualizare: ianuarie 2026*
*PyArchInit - Analiză Ceramică Arheologică*

---

## Animație Interactivă

Explorați animația interactivă pentru a afla mai multe despre acest subiect.

[Deschideți Animația Interactivă](../../animations/pyarchinit_pottery_tools_animation.html)
