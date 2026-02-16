# Tutorial 08: Fisa Inventar Materiale

## Cuprins
1. [Introducere](#introducere)
2. [Accesarea Fisei](#accesarea-fisei)
3. [Interfata Utilizator](#interfata-utilizator)
4. [Campuri Principale](#campuri-principale)
5. [Filele Fisei](#filele-fisei)
6. [Bara de Instrumente DBMS](#bara-de-instrumente-dbms)
7. [Gestionare Media](#gestionare-media)
8. [Functionalitati GIS](#functionalitati-gis)
9. [Cuantificari si Statistici](#cuantificari-si-statistici)
10. [Export si Rapoarte](#export-si-rapoarte)
11. [Integrare AI](#integrare-ai)
12. [Flux de Lucru Operational](#flux-de-lucru-operational)
13. [Bune Practici](#bune-practici)
14. [Depanare](#depanare)

---

## Introducere

**Fisa Inventar Materiale** este instrumentul principal pentru gestionarea descoperirilor arheologice in PyArchInit. Va permite sa catalogati, descrieti si cuantificati toate materialele descoperite in timpul sapaturii, de la ceramica la metale, de la sticla la oase de animale.

### Scopul Fisei

- Inventarierea tuturor descoperirilor recuperate
- Asocierea descoperirilor cu US-urile de provenienta
- Gestionarea clasificarii tipologice
- Documentarea caracteristicilor fizice si tehnologice
- Calcularea cuantificarilor (vase minime, EVE, greutate)
- Asocierea fotografiilor si desenelor cu descoperirile
- Generarea rapoartelor si statisticilor

### Tipuri de Materiale Gestionabile

Fisa suporta diverse tipuri de materiale:
- **Ceramica**: Olarie, teracote, materiale de constructie
- **Metale**: Bronz, fier, plumb, aur, argint
- **Sticla**: Recipiente, sticla de fereastra
- **Os/Fildes**: Obiecte din material animal dur
- **Piatra**: Unelte litice, sculpturi
- **Monede**: Numismatica
- **Organice**: Lemn, textile, piele

---

## Accesarea Fisei

### Din Meniu

1. Deschideti QGIS cu plugin-ul PyArchInit activ
2. Meniu **PyArchInit** → **Gestionare inregistrari arheologice** → **Artefact** → **Fisa artefact**

### Din Bara de Instrumente

1. Localizati bara de instrumente PyArchInit
2. Faceti clic pe pictograma **Descoperiri** (pictograma amfora/vas)

### Scurtatura de Tastatura

- **Ctrl+G**: Activare/dezactivare vizualizarea GIS a descoperirii curente

---

## Interfata Utilizator

Interfata este organizata in trei zone principale:

### Zone Principale

| Zona | Descriere |
|------|-----------|
| **1. Antet** | Bara DBMS, indicatori de stare, butoane GIS si export |
| **2. Campuri de Identificare** | Santier, Zona, US, Numar inventar, RA, Tip descoperire |
| **3. Campuri Descriptive** | Clasa, Definitie, Stare conservare, Datare |
| **4. File de Detaliu** | 6 file pentru date specifice |

### File Disponibile

| Fila | Continut |
|------|----------|
| **Descriere** | Text descriptiv, vizualizator media, datare |
| **Diapozitive** | Gestionare diapozitive si negative |
| **Date Cantitative** | Elemente descoperire, forme, masuratori ceramice |
| **Tehnologii** | Tehnici de productie si decorative |
| **Ref. Bibliografice** | Referinte bibliografice |
| **Cuantificari** | Grafice si statistici |

---

## Campuri Principale

### Campuri de Identificare

#### Santier
- **Tip**: ComboBox (doar citire dupa salvare)
- **Obligatoriu**: Da
- **Descriere**: Santierul arheologic de origine

#### Numar Inventar
- **Tip**: LineEdit numeric
- **Obligatoriu**: Da
- **Descriere**: Numarul unic progresiv al descoperirii in cadrul santierului
- **Constrangere**: Unic pe santier

#### Zona
- **Tip**: ComboBox editabil
- **Obligatoriu**: Nu
- **Descriere**: Zona de sapatura de provenienta

#### US (Unitate Stratigrafica)
- **Tip**: LineEdit
- **Obligatoriu**: Nu (dar foarte recomandat)
- **Descriere**: Numarul US-ului de provenienta
- **Legatura**: Conecteaza descoperirea de fisa US corespunzatoare

#### Structura
- **Tip**: ComboBox editabil
- **Obligatoriu**: Nu
- **Descriere**: Structura de apartenenta (daca este cazul)

#### RA (Descoperire Arheologica)
- **Tip**: LineEdit numeric
- **Obligatoriu**: Nu
- **Descriere**: Numar alternativ al descoperirii

### Campuri de Clasificare

#### Tip Descoperire
- **Tip**: ComboBox editabil
- **Obligatoriu**: Da
- **Valori tipice**: Ceramica, Metal, Sticla, Os, Piatra, Moneda etc.

#### Clasa Material (Criteriu de Catalogare)
- **Tip**: ComboBox editabil
- **Obligatoriu**: Nu
- **Exemple pentru ceramica**:
  - Ceramica comuna
  - Sigillata italica
  - Sigillata africana
  - Ceramica cu firnis negru
  - Ceramica cu perete subtire
  - Amfore
  - Lampi

#### Definitie
- **Tip**: ComboBox editabil
- **Obligatoriu**: Nu
- **Exemple**: Farfurie, Ceasa, Oala, Ulcior, Capac etc.

### Campuri de Stare si Conservare

#### Spalat
- **Tip**: ComboBox
- **Valori**: Da, Nu

#### Catalogat
- **Tip**: ComboBox
- **Valori**: Da, Nu

#### Diagnostic
- **Tip**: ComboBox
- **Valori**: Da, Nu

#### Stare de Conservare
- **Tip**: ComboBox editabil
- **Valori tipice**: Complet, Fragmentar, Lacunar, Restaurat

---

## Filele Fisei

### Fila 1: Descriere

Fila principala contine descrierea textuala si gestionarea media.

#### Campul Descriere
- **Tip**: TextEdit pe mai multe linii
- **Continut sugerat**:
  - Forma generala
  - Parti pastrate
  - Caracteristici tehnice
  - Decoratiuni
  - Comparatii tipologice

#### Datarea Descoperirii
- **Tip**: ComboBox editabil
- **Format**: Text (de ex., "Sec. I i.Hr.", "Sec. II-III d.Hr.")

#### Vizualizator Media
Zona pentru vizualizarea imaginilor asociate descoperirii:
- **Vizualizare toate imaginile**: Incarca toate fotografiile asociate
- **Cautare imagini**: Cauta imagini
- **Eliminare eticheta**: Elimina asocierea imagine-descoperire
- **SketchGPT**: Genereaza descriere AI din imagine

### Fila 2: Diapozitive

Gestionarea documentatiei fotografice traditionale.

#### Tabelul Diapozitive
| Coloana | Descriere |
|---------|-----------|
| Cod | Cod de identificare diapozitiv |
| Nr. | Numar progresiv |

#### Tabelul Negative
| Coloana | Descriere |
|---------|-----------|
| Cod | Cod rola negativ |
| Nr. | Numarul cadrului |

### Fila 3: Date Cantitative

Fila fundamentala pentru analiza cantitativa, in special pentru ceramica.

#### Tabelul Elementelor Descoperirii
Inregistreaza elementele individuale care compun descoperirea:

| Coloana | Descriere | Exemplu |
|---------|-----------|---------|
| Element gasit | Partea anatomica a vasului | Buza, Perete, Baza, Toarta |
| Tip cantitate | Starea fragmentului | Fragment, Complet |
| Cantitate | Numarul de piese | 5 |

#### Campuri de Cuantificare Ceramica

| Camp | Descriere |
|------|-----------|
| **Vase minime** | Numarul Minim de Indivizi (NMI) |
| **Vase maxime** | Numarul Maxim de Indivizi |
| **Total fragmente** | Calculat automat din tabelul de elemente |
| **Greutate** | Greutatea in grame |
| **Diametru buza** | Diametrul buzei in cm |
| **EVE buza** | Echivalent Vas Estimat (procentul de buza pastrat) |

### Fila 4: Tehnologii

Inregistrarea tehnicilor de productie si decorative.

#### Tabelul Tehnologiilor

| Coloana | Descriere | Exemplu |
|---------|-----------|---------|
| Tip tehnologie | Categorie tehnica | Productie, Decorare |
| Pozitie | Unde se gaseste | Interior, Exterior, Corp |
| Cantitate | Daca este cazul | - |
| Unitate | Daca este cazul | - |

#### Campuri Specifice Ceramicii

| Camp | Descriere |
|------|-----------|
| **Corp ceramic** | Tipul pastei (Fina, Semi-fina, Grosiera) |
| **Acoperire** | Tipul acoperirii (Angoba, Engoba, Glazura) |

### Fila 5: Referinte Bibliografice

Gestionarea bibliografiei comparative.

#### Tabelul Referintelor

| Coloana | Descriere |
|---------|-----------|
| Autor | Numele autorului(lor) |
| An | Anul publicarii |
| Titlu | Titlul prescurtat |
| Pagina | Referinta paginii |
| Figura | Referinta figura/plansa |

### Fila 6: Cuantificari

Fila pentru generarea graficelor si statisticilor.

#### Tipuri de Cuantificari Disponibile

| Tip | Descriere |
|-----|-----------|
| **Vase minime** | Grafic NMI |
| **Vase maxime** | Grafic numar maxim |
| **Total fragmente** | Grafic numarare fragmente |
| **Greutate** | Grafic greutate |
| **EVE buza** | Grafic EVE |

#### Parametri de Grupare

Graficele pot fi grupate dupa:
- Tip descoperire
- Clasa material
- Definitie
- Corp ceramic
- Acoperire
- Tip
- Datare
- RA
- An

---

## Bara de Instrumente DBMS

### Butoane Standard

| Pictograma | Functie | Descriere |
|------------|---------|-----------|
| Test conexiune | Test conexiune | Verifica conexiunea la baza de date |
| Prima/Anterioara/Urmatoarea/Ultima | Navigare | Navigare intre inregistrari |
| Inregistrare noua | Nou | Creeaza descoperire noua |
| Salvare | Salvare | Salveaza modificarile |
| Stergere | Stergere | Sterge descoperirea curenta |
| Vizualizare toate | Toate | Vizualizeaza toate inregistrarile |
| Cautare noua | Cautare | Activeaza modul de cautare |
| Cauta!!! | Executare | Executa cautarea |
| Ordoneaza dupa | Sortare | Sorteaza inregistrarile |

### Butoane Specifice

| Pictograma | Functie | Descriere |
|------------|---------|-----------|
| GIS | Vizualizare GIS | Afiseaza descoperirea pe harta |
| PDF | Export PDF | Genereaza fisa PDF |
| Fisa | Export lista | Genereaza lista PDF |
| Excel | Export Excel | Exporta in format Excel/CSV |
| A5 | Export A5 | Genereaza eticheta format A5 |
| Cuant. | Cuantificari | Deschide panoul de cuantificari |

---

## Gestionare Media

### Asociere Imagini

#### Tragere si Plasare
Puteti trage imaginile direct in lista pentru a le asocia cu descoperirea.

#### Butoane Media

| Buton | Functie |
|-------|---------|
| **Toate imaginile** | Incarca toate imaginile asociate |
| **Cautare imagini** | Deschide cautarea de imagini |
| **Eliminare eticheta** | Elimina asocierea curenta |

### Vizualizator Imagini

Dublu clic pe o imagine din lista deschide vizualizatorul complet cu:
- Zoom
- Panoramare
- Rotire
- Informatii EXIF

---

## Functionalitati GIS

### Vizualizare pe Harta

#### Buton GIS (Comutator)
- **Activ**: Descoperirea este evidentiata pe harta QGIS
- **Inactiv**: Fara vizualizare
- **Scurtatura**: Ctrl+G

#### Cerinte
- Descoperirea trebuie sa aiba US-ul de provenienta specificat
- US-ul trebuie sa aiba geometrie in stratul GIS

---

## Cuantificari si Statistici

### Accesarea Cuantificarilor

1. Faceti clic pe butonul **Cuant.** din bara de instrumente
2. Selectati tipul de cuantificare
3. Selectati parametrii de grupare
4. Faceti clic pe OK

### Tipuri de Grafice

#### Grafic cu Bare
Afiseaza distributia pe categoria selectata.

### Export Cuantificari

Datele de cuantificare sunt exportate automat in:
- Fisier CSV in `pyarchinit_Quantificazioni_folder`
- Grafic afisat pe ecran

---

## Export si Rapoarte

### Export PDF Fisa Individuala

Genereaza o fisa PDF completa a descoperirii curente cu:
- Toate datele de identificare
- Descriere
- Date cantitative
- Referinte bibliografice
- Imagini asociate (daca sunt disponibile)

### Export PDF Lista

Genereaza o lista PDF a tuturor descoperirilor afisate (rezultatul cautarii curente):
- Tabel sumar
- Date esentiale pentru fiecare descoperire

### Export A5 (Etichete)

Genereaza etichete in format A5 pentru:
- Identificarea cutiilor
- Etichetarea descoperirilor
- Fise mobile

### Export Excel/CSV

Exporta datele in format tabelar pentru:
- Prelucrare statistica externa
- Import in alte programe
- Arhivare

---

## Integrare AI

### SketchGPT

Functionalitate AI pentru generarea automata a descrierilor descoperirilor din imagini.

#### Utilizare

1. Asociati o imagine descoperirii
2. Faceti clic pe butonul **SketchGPT**
3. Selectati imaginea de analizat
4. Selectati modelul GPT (gpt-4-vision, gpt-4o)
5. Sistemul genereaza descrierea arheologica

#### Rezultat

Descrierea generata include:
- Identificarea tipului de descoperire
- Descrierea caracteristicilor vizibile
- Posibile comparatii tipologice
- Sugestii de datare

> **Nota**: Necesita Cheie API OpenAI configurata.

---

## Flux de Lucru Operational

### Crearea unei Descoperiri Noi

#### Pasul 1: Deschideti Fisa
1. Deschideti Fisa Inventar Materiale
2. Verificati conexiunea la baza de date

#### Pasul 2: Inregistrare Noua
1. Faceti clic pe **Inregistrare noua**
2. Starea se schimba in "Inregistrare Noua"

#### Pasul 3: Date de Identificare
1. Verificati/selectati **Santierul**
2. Introduceti **Numarul de inventar** (progresiv)
3. Introduceti **Zona** si **US-ul** de provenienta

#### Pasul 4: Clasificare
1. Selectati **Tipul descoperirii**
2. Selectati **Clasa de material**
3. Selectati/introduceti **Definitia**

#### Pasul 5: Descriere
1. Completati campul **Descriere** in fila Descriere
2. Selectati **Datarea**
3. Asociati eventualele imagini

#### Pasul 6: Date Cantitative (daca ceramica)
1. Deschideti fila **Date Cantitative**
2. Introduceti elementele in tabel
3. Completati vasele minime/maxime
4. Introduceti greutatea si masuratorile

#### Pasul 7: Depozitare
1. Introduceti **Nr. cutie**
2. Selectati **Locul de depozitare**
3. Indicati **Starea de conservare**

#### Pasul 8: Salvare
1. Faceti clic pe **Salvare**
2. Verificati mesajul de confirmare
3. Inregistrarea este acum salvata in baza de date

### Cautarea Descoperirilor

#### Cautare Simpla
1. Faceti clic pe **Cautare noua**
2. Completati campurile de cautare dorite
3. Faceti clic pe **Cauta!!!**

#### Cautare dupa US
1. Activati cautarea
2. Introduceti doar numarul US in campul US
3. Executati cautarea

---

## Bune Practici

### Numerotare Inventar

- Folositi numerotare progresiva fara goluri
- Un numar = o descoperire (sau grup omogen)
- Documentati criteriile de inventariere

### Clasificare

- Folositi vocabulare controlate pentru clase
- Mentineti consistenta in definitiile tipurilor
- Actualizati tezaurul cand este necesar

### Cuantificare Ceramica

Pentru cuantificare corecta:
1. **Vase minime (NMI)**: Numarati doar elementele de diagnostic (buze, baze distinctive)
2. **EVE**: Masurati procentul de circumferinta pastrat
3. **Greutate**: Cantariti toate fragmentele din grup

### Documentatie Fotografica

- Fotografiati toate descoperirile de diagnostic
- Folositi scara metrica in fotografii
- Asociati fotografiile prin managerul media

### Legatura cu US

- Verificati intotdeauna ca US-ul exista inainte de asociere
- Pentru descoperiri de curatare/suprafata, folositi US-ul corespunzator
- Documentati descoperirile din afara contextului

---

## Depanare

### Probleme Frecvente

#### Numar de inventar duplicat
- **Eroare**: "Exista deja o inregistrare cu acest numar de inventar"
- **Cauza**: Numarul deja folosit pentru santier
- **Solutie**: Verificati urmatorul numar disponibil cu "Vizualizare toate"

#### Imaginile nu se afiseaza
- **Cauza**: Cale imagine incorecta
- **Solutie**:
  1. Verificati configurarea caii in Setari
  2. Verificati ca imaginile sunt in dosarul corect
  3. Reasociati imaginile

#### Cuantificari goale
- **Cauza**: Campurile cantitative necompletate
- **Solutie**: Completati vasele minime/maxime sau totalul fragmentelor

#### GIS nu functioneaza
- **Cauza**: US-ul nu are geometrie sau stratul nu este incarcat
- **Solutie**:
  1. Verificati ca stratul US este incarcat in QGIS
  2. Verificati ca US-ul are geometrie asociata

---

## Tutorial Video

### Video 1: Prezentare Generala Fisa Inventar
*Durata: 5-6 minute*

**Continut:**
- Interfata generala
- Navigarea intre file
- Functionalitati principale

### Video 2: Documentare Completa Ceramica
*Durata: 8-10 minute*

**Continut:**
- Completarea tuturor campurilor
- Cuantificare ceramica
- Elemente descoperire
- Tehnologii

### Video 3: Media si Gestionare Fotografii
*Durata: 4-5 minute*

**Continut:**
- Asociere imagini
- Vizualizator
- SketchGPT

### Video 4: Export si Cuantificari
*Durata: 5-6 minute*

**Continut:**
- Export PDF
- Export Excel
- Grafice de cuantificare

---

*Ultima actualizare: Ianuarie 2026*
*PyArchInit - Gestionare Date Arheologice*
