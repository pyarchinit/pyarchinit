# PyArchInit - Fisa Santier

## Cuprins
1. [Introducere](#introducere)
2. [Accesarea Fisei](#accesarea-fisei)
3. [Interfata Utilizator](#interfata-utilizator)
4. [Date Descriptive ale Santierului](#date-descriptive-ale-santierului)
5. [Bara de Instrumente DBMS](#bara-de-instrumente-dbms)
6. [Functionalitati GIS](#functionalitati-gis)
7. [Generare Fise US](#generare-fise-us)
8. [MoveCost - Analiza Traseelor](#movecost---analiza-traseelor)
9. [Export Rapoarte](#export-rapoarte)
10. [Flux de Lucru Operational](#flux-de-lucru-operational)

---

## Introducere

**Fisa Santier** este punctul de plecare pentru documentarea unei sapaturi arheologice in PyArchInit. Fiecare proiect arheologic incepe cu crearea unui santier, care serveste drept container principal pentru toate celelalte informatii (Unitati Stratigrafice, Structuri, Descoperiri etc.).

Un **santier arheologic** in PyArchInit reprezinta o zona geografica definita in care au loc activitati de cercetare arheologica. Poate fi o sapatura, o zona de prospectare, un monument etc.

<!-- VIDEO: Introducere in Fisa Santier -->
> **Tutorial Video**: [Inserati link video pentru introducerea in fisa santier]

---

## Accesarea Fisei

Pentru a accesa Fisa Santier:

1. Meniu **PyArchInit** → **Gestionare inregistrari arheologice** → **Santier**
2. Sau din bara de instrumente PyArchInit, faceti clic pe pictograma **Santier**

<!-- IMAGINE: Captură de ecran pentru accesul la fisa santier din meniu -->
![Acces Fisa Santier](images/02_scheda_sito/01_menu_scheda_sito.png)
*Figura 1: Accesarea Fisei Santier din meniul PyArchInit*

<!-- IMAGINE: Captură de ecran a barei de instrumente cu pictograma santier -->
![Bara Santier](images/02_scheda_sito/02_toolbar_sito.png)
*Figura 2: Pictograma Fisei Santier in bara de instrumente*

---

## Interfata Utilizator

Fisa Santier este impartita in mai multe zone functionale:

<!-- IMAGINE: Captură de ecran a fisei complete cu zone numerotate -->
![Interfata Fisei Santier](images/02_scheda_sito/03_interfaccia_completa.png)
*Figura 3: Interfata completa a Fisei Santier*

### Zone Principale

| # | Zona | Descriere |
|---|------|-----------|
| 1 | **Bara de Instrumente DBMS** | Bara pentru navigare si gestionarea inregistrarilor |
| 2 | **Date Descriptive** | Campuri pentru introducerea informatiilor despre santier |
| 3 | **Generator US** | Instrument pentru crearea in lot a fiselor US |
| 4 | **Vizualizator GIS** | Controale pentru afisarea cartografica |
| 5 | **MoveCost** | Instrumente avansate de analiza spatiala |
| 6 | **Ajutor** | Documentatie si tutoriale video |

---

## Date Descriptive ale Santierului

### Fila Date Descriptive

<!-- IMAGINE: Captură de ecran a filei date descriptive -->
![Fila Date Descriptive](images/02_scheda_sito/04_tab_dati_descrittivi.png)
*Figura 4: Fila Date Descriptive*

#### Campuri Obligatorii

| Camp | Descriere | Note |
|------|-----------|------|
| **Santier** | Numele de identificare al santierului | Camp obligatoriu, trebuie sa fie unic |

#### Campuri Geografice

| Camp | Descriere | Exemplu |
|------|-----------|---------|
| **Tara** | Tara in care se afla santierul | Italia |
| **Regiune** | Regiunea administrativa | Lazio |
| **Provincie** | Provincia | Roma |
| **Municipiu** | Municipiul | Roma |

<!-- IMAGINE: Captură de ecran cu campurile geografice completate -->
![Campuri Geografice](images/02_scheda_sito/05_campi_geografici.png)
*Figura 5: Exemplu de completare a campurilor geografice*

#### Campuri Descriptive

| Camp | Descriere |
|------|-----------|
| **Nume** | Numele extins/descriptiv al santierului |
| **Definitie** | Tipul santierului (din tezaur) |
| **Descriere** | Camp text liber pentru descriere detaliata |
| **Dosar** | Calea catre dosarul local al proiectului |

<!-- IMAGINE: Captură de ecran a campului descriere -->
![Campul Descriere](images/02_scheda_sito/06_campo_descrizione.png)
*Figura 6: Campul de descriere text*

### Definitia Santierului (Tezaur)

Campul **Definitie** foloseste un vocabular controlat (tezaur). Optiunile disponibile includ:

| Definitie | Descriere |
|-----------|-----------|
| Zona de sapatura | Zona supusa investigatiei stratigrafice |
| Zona de prospectare | Zona de recunoastere de suprafata |
| Sit arheologic | Locatie cu dovezi arheologice |
| Monument | Structura monumentala individuala |
| Necropola | Zona funerara |
| Asezare | Zona rezidentiala |
| Sanctuar | Zona sacra/de cult |
| ... | Alte definitii din tezaur |

<!-- IMAGINE: Captură de ecran cu dropdown-ul definitiei santierului -->
![Definitia Santierului](images/02_scheda_sito/07_definizione_sito.png)
*Figura 7: Selectarea definitiei santierului din tezaur*

### Dosarul Proiectului

Campul **Dosar** va permite sa asociati un director local cu santierul pentru organizarea fisierelor proiectului.

<!-- IMAGINE: Captură de ecran a selectiei dosarului -->
![Selectia Dosarului](images/02_scheda_sito/08_selezione_cartella.png)
*Figura 8: Selectia dosarului proiectului*

| Buton | Functie |
|-------|---------|
| **...** | Navigati pentru a selecta dosarul |
| **Deschide** | Deschide dosarul in managerul de fisiere |

---

## Bara de Instrumente DBMS

Bara de instrumente DBMS ofera toate controalele pentru gestionarea inregistrarilor.

<!-- IMAGINE: Captură de ecran a barei DBMS -->
![Bara DBMS](images/02_scheda_sito/09_toolbar_dbms.png)
*Figura 9: Bara de Instrumente DBMS*

### Indicatori de Stare

| Indicator | Descriere |
|-----------|-----------|
| **Info BD** | Afiseaza tipul bazei de date conectate (SQLite/PostgreSQL) |
| **Stare** | Starea curenta: `Utilizare` (navigare), `Cautare` (cautare), `Inregistrare Noua` |
| **Sortare** | Indica daca inregistrarile sunt sortate |
| **inregistrarea nr.** | Numarul inregistrarii curente |
| **total inregistrari** | Totalul inregistrarilor |

<!-- IMAGINE: Captură de ecran a indicatorilor de stare -->
![Indicatori de Stare](images/02_scheda_sito/10_indicatori_stato.png)
*Figura 10: Indicatori de stare*

### Navigare Inregistrari

| Buton | Pictograma | Functie | Scurtatura |
|-------|------------|---------|------------|
| **Prima inreg.** | |< | Mergi la prima inregistrare | - |
| **Inreg. anterioara** | < | Mergi la inregistrarea anterioara | - |
| **Inreg. urmatoare** | > | Mergi la inregistrarea urmatoare | - |
| **Ultima inreg.** | >| | Mergi la ultima inregistrare | - |

<!-- IMAGINE: Captură de ecran a butoanelor de navigare -->
![Navigare](images/02_scheda_sito/11_navigazione_record.png)
*Figura 11: Butoane de navigare*

### Gestionare Inregistrari

| Buton | Functie | Descriere |
|-------|---------|-----------|
| **Inregistrare noua** | Creare noua | Pregateste formularul pentru introducerea unui santier nou |
| **Salvare** | Salvare | Salveaza modificarile sau inregistrarea noua |
| **Stergere inregistrare** | Stergere | Sterge inregistrarea curenta (cu confirmare) |
| **Vizualizare toate inregistrarile** | Vizualizare toate | Afiseaza toate inregistrarile din baza de date |

<!-- IMAGINE: Captură de ecran a butoanelor de gestionare -->
![Gestionare Inregistrari](images/02_scheda_sito/12_gestione_record.png)
*Figura 12: Butoane de gestionare a inregistrarilor*

### Cautare si Sortare

| Buton | Functie | Descriere |
|-------|---------|-----------|
| **cautare noua** | Cautare noua | Porneste modul de cautare |
| **cauta !!!** | Executa cautare | Executa cautarea cu criteriile introduse |
| **Ordoneaza dupa** | Sortare | Deschide panoul de sortare |

<!-- IMAGINE: Captură de ecran a cautarii -->
![Cautare](images/02_scheda_sito/13_ricerca.png)
*Figura 13: Functii de cautare*

#### Cum se Efectueaza o Cautare

1. Faceti clic pe **cautare noua** - starea se schimba in "Cautare"
2. Completati campurile cu criteriile de cautare
3. Faceti clic pe **cauta !!!** pentru executare
4. Rezultatele sunt afisate si puteti naviga prin ele

<!-- IMAGINE: Captură de ecran cu exemplu de cautare -->
![Exemplu de Cautare](images/02_scheda_sito/14_esempio_ricerca.png)
*Figura 14: Exemplu de cautare dupa regiune*

<!-- VIDEO: Cum se efectueaza cautari -->
> **Tutorial Video**: [Inserati link video pentru cautare]

#### Panoul de Sortare

Faceti clic pe **Ordoneaza dupa** pentru a deschide panoul de sortare a inregistrarilor:

<!-- IMAGINE: Captură de ecran a panoului de sortare -->
![Panou de Sortare](images/02_scheda_sito/15_pannello_ordinamento.png)
*Figura 15: Panoul de sortare*

| Optiune | Descriere |
|---------|-----------|
| **Camp** | Selectati campul pentru sortare |
| **Crescator** | Ordine A-Z, 0-9 |
| **Descrescator** | Ordine Z-A, 9-0 |

---

## Functionalitati GIS

Fisa Santier ofera diverse functionalitati de integrare GIS.

<!-- IMAGINE: Captură de ecran a sectiunii GIS -->
![Sectiune GIS](images/02_scheda_sito/16_sezione_gis.png)
*Figura 16: Sectiunea de functionalitati GIS*

### Incarcarea Straturilor

| Buton | Functie |
|-------|---------|
| **Vizualizator GIS** | Incarca toate straturile pentru introducerea geometriilor |
| **Incarca stratul santierului** (pictograma glob) | Incarca doar straturile santierului curent |
| **Incarca toate santierele** (pictograma globuri multiple) | Incarca straturile pentru toate santierele |

<!-- IMAGINE: Captură de ecran a butoanelor GIS -->
![Butoane GIS](images/02_scheda_sito/17_bottoni_gis.png)
*Figura 17: Butoane de incarcare straturi GIS*

### Geocodificare - Cautare Adrese

Functia de geocodificare va permite sa localizati o adresa pe harta.

<!-- IMAGINE: Captură de ecran a geocodificarii -->
![Geocodificare](images/02_scheda_sito/18_geocoding.png)
*Figura 18: Campul de cautare adrese*

1. Introduceti adresa in campul de text
2. Faceti clic pe **Zoom pe**
3. Harta se centreaza pe locatia gasita

| Camp | Descriere |
|------|-----------|
| **Adresa** | Introduceti strada, orasul, tara |
| **Zoom pe** | Centreaza harta pe adresa |

### Modul GIS Activ

Comutatorul **Activare incarcare cautare** activeaza/dezactiveaza afisarea automata a rezultatelor cautarii pe harta.

<!-- IMAGINE: Captură de ecran a comutatorului GIS -->
![Comutator GIS](images/02_scheda_sito/19_toggle_gis.png)
*Figura 19: Comutatorul modului GIS*

- **Activ**: Cautarile sunt afisate automat pe harta
- **Inactiv**: Cautarile nu modifica afisarea hartii

### WMS Restrictii Arheologice

Butonul WMS incarca stratul de restrictii arheologice de la Ministerul Culturii italian.

<!-- IMAGINE: Captură de ecran a restrictiilor WMS -->
![Restrictii WMS](images/02_scheda_sito/20_wms_vincoli.png)
*Figura 20: Stratul WMS de restrictii arheologice*

### Harti de Baza

Butonul Harti de Baza permite incarcarea hartilor de baza (Google Maps, OpenStreetMap etc.).

<!-- IMAGINE: Captură de ecran a hartilor de baza -->
![Harti de Baza](images/02_scheda_sito/21_base_maps.png)
*Figura 21: Selectia hartilor de baza*

---

## Generare Fise US

Aceasta functionalitate permite crearea automata a unui numar arbitrar de fise US pentru santierul curent.

<!-- IMAGINE: Captură de ecran a generatorului US -->
![Generator US](images/02_scheda_sito/22_generatore_us.png)
*Figura 22: Sectiunea de generare fise US*

### Parametri

| Camp | Descriere | Exemplu |
|------|-----------|---------|
| **Numarul Zonei** | Numarul zonei de sapatura | 1 |
| **Numarul initial al fisei US** | Numarul US initial | 1 |
| **Numarul de fise de creat** | Cate US sa genereze | 100 |
| **Tip** | US sau USM | US |

### Procedura

1. Asigurati-va ca sunteti pe santierul corect
2. Introduceti numarul zonei
3. Introduceti numarul US de start
4. Introduceti cate fise sa creeze
5. Selectati tipul (US sau USM)
6. Faceti clic pe **Genereaza US**

<!-- IMAGINE: Captură de ecran cu exemplu de generare -->
![Exemplu de Generare](images/02_scheda_sito/23_esempio_generazione.png)
*Figura 23: Exemplu de generare a 50 US incepand de la US 101*

<!-- VIDEO: Cum se genereaza fise US in lot -->
> **Tutorial Video**: [Inserati link video pentru generare US]

---

## MoveCost - Analiza Traseelor

Sectiunea **MovecostToPyarchinit** integreaza functii R pentru analiza traseelor de cost minim.

<!-- IMAGINE: Captură de ecran a sectiunii MoveCost -->
![MoveCost](images/02_scheda_sito/24_movecost_sezione.png)
*Figura 24: Sectiunea MoveCost*

### Cerinte Preliminare

- **R** instalat pe sistem
- Pachetul R **movecost** instalat
- Plugin-ul **Processing R Provider** activ in QGIS

### Functii Disponibile

| Functie | Descriere |
|---------|-----------|
| **movecost** | Calculeaza costul de deplasare si traseele de cost minim de la un punct de origine |
| **movecost by polygon** | La fel ca mai sus, folosind un poligon pentru descarcarea DTM |
| **movebound** | Calculeaza limitele de cost de deplasare in jurul punctelor |
| **movebound by polygon** | La fel ca mai sus, folosind un poligon |
| **movcorr** | Calculeaza coridoarele de cost minim intre puncte |
| **movecorr by polygon** | La fel ca mai sus, folosind un poligon |
| **movalloc** | Alocarea teritoriului pe baza costurilor |
| **movealloc by polygon** | La fel ca mai sus, folosind un poligon |

<!-- IMAGINE: Captură de ecran cu exemplu movecost -->
![Exemplu MoveCost](images/02_scheda_sito/25_esempio_movecost.png)
*Figura 25: Exemplu de rezultat al analizei MoveCost*

### Adaugare Scripturi

Butonul **Adaugare scripturi** instaleaza automat scripturile R necesare in profilul QGIS.

<!-- VIDEO: Analiza MoveCost -->
> **Tutorial Video**: [Inserati link video MoveCost]

---

## Export Rapoarte

### Export Raport de Sapatura

Butonul **Export** genereaza un PDF cu raportul de sapatura pentru santierul curent.

<!-- IMAGINE: Captură de ecran a exportului -->
![Export](images/02_scheda_sito/26_esportazione.png)
*Figura 26: Butonul de export raport*

**Nota**: Aceasta functionalitate este in versiune de dezvoltare si poate contine erori.

Raportul include:
- Date de identificare a santierului
- Lista US
- Secventa stratigrafica
- Harris Matrix (daca este disponibila)

<!-- IMAGINE: Captură de ecran cu exemplu PDF -->
![Exemplu PDF](images/02_scheda_sito/27_esempio_pdf.png)
*Figura 27: Exemplu de raport PDF generat*

---

## Flux de Lucru Operational

### Crearea unui Santier Nou

<!-- VIDEO: Flux de lucru pentru crearea unui santier nou -->
> **Tutorial Video**: [Inserati link video pentru flux de lucru santier nou]

#### Pasul 1: Deschideti Fisa Santier
<!-- IMAGINE: Pasul 1 -->
![Flux Pasul 1](images/02_scheda_sito/28_workflow_step1.png)
*Figura 28: Pasul 1 - Deschiderea formularului*

#### Pasul 2: Faceti clic pe "Inregistrare noua"
Starea se schimba in "Inregistrare Noua" si campurile sunt golite.

<!-- IMAGINE: Pasul 2 -->
![Flux Pasul 2](images/02_scheda_sito/29_workflow_step2.png)
*Figura 29: Pasul 2 - Inregistrare noua*

#### Pasul 3: Completati Datele Obligatorii
Introduceti cel putin numele santierului (camp obligatoriu).

<!-- IMAGINE: Pasul 3 -->
![Flux Pasul 3](images/02_scheda_sito/30_workflow_step3.png)
*Figura 30: Pasul 3 - Introducerea datelor*

#### Pasul 4: Completati Datele Geografice
Introduceti tara, regiunea, provincia, municipiul.

<!-- IMAGINE: Pasul 4 -->
![Flux Pasul 4](images/02_scheda_sito/31_workflow_step4.png)
*Figura 31: Pasul 4 - Date geografice*

#### Pasul 5: Selectati Definitia
Alegeti tipul santierului din tezaur.

<!-- IMAGINE: Pasul 5 -->
![Flux Pasul 5](images/02_scheda_sito/32_workflow_step5.png)
*Figura 32: Pasul 5 - Definitia santierului*

#### Pasul 6: Adaugati Descrierea
Completati campul de descriere cu informatii detaliate.

<!-- IMAGINE: Pasul 6 -->
![Flux Pasul 6](images/02_scheda_sito/33_workflow_step6.png)
*Figura 33: Pasul 6 - Descriere*

#### Pasul 7: Salvati
Faceti clic pe **Salvare** pentru a salva noul santier.

<!-- IMAGINE: Pasul 7 -->
![Flux Pasul 7](images/02_scheda_sito/34_workflow_step7.png)
*Figura 34: Pasul 7 - Salvare*

#### Pasul 8: Verificati
Santierul a fost creat, starea revine la "Utilizare".

<!-- IMAGINE: Pasul 8 -->
![Flux Pasul 8](images/02_scheda_sito/35_workflow_step8.png)
*Figura 35: Pasul 8 - Verificarea crearii*

### Modificarea unui Santier Existent

1. Navigati la santierul de modificat
2. Modificati campurile dorite
3. Faceti clic pe **Salvare**
4. Confirmati salvarea modificarilor

### Stergerea unui Santier

**Atentie**: Stergerea unui santier NU sterge automat US-urile, structurile si descoperirile asociate.

1. Navigati la santierul de sters
2. Faceti clic pe **Stergere inregistrare**
3. Confirmati stergerea

<!-- IMAGINE: Captură de ecran a dialogului de confirmare stergere -->
![Confirmare Stergere](images/02_scheda_sito/36_conferma_eliminazione.png)
*Figura 36: Dialogul de confirmare a stergerii*

---

## Fila Ajutor

Fila Ajutor ofera acces rapid la documentatie.

<!-- IMAGINE: Captură de ecran a filei ajutor -->
![Fila Ajutor](images/02_scheda_sito/37_tab_help.png)
*Figura 37: Fila Ajutor*

| Resursa | Link |
|---------|------|
| Tutorial Video | YouTube |
| Documentatie | pyarchinit.github.io |
| Comunitate | Facebook UnaQuantum |

---

## Gestionarea Concurentei (PostgreSQL)

Cand se utilizeaza PostgreSQL intr-un mediu multi-utilizator, sistemul gestioneaza automat conflictele de modificare:

- **Indicator de blocare**: Arata daca inregistrarea este editata de un alt utilizator
- **Control versiune**: Detecteaza modificarile concurente
- **Rezolvarea conflictelor**: Permite alegerea versiunii de pastrat

<!-- IMAGINE: Captură de ecran a indicatorului de concurenta -->
![Concurenta](images/02_scheda_sito/38_concorrenza.png)
*Figura 38: Indicatorul de inregistrare blocata*

---

## Depanare

### Santierul nu este salvat
- Verificati ca campul "Santier" este completat
- Verificati ca numele nu exista deja in baza de date

### Straturile GIS nu se incarca
- Verificati conexiunea la baza de date
- Verificati ca exista geometrii asociate santierului

### Eroare de geocodificare
- Verificati conexiunea la internet
- Verificati ca adresa este scrisa corect

### MoveCost nu functioneaza
- Verificati ca R este instalat
- Verificati ca plugin-ul Processing R Provider este activ
- Instalati pachetul movecost in R

---

## Note Tehnice

- **Tabelul bazei de date**: `site_table`
- **Campurile bazei de date**: sito, nazione, regione, comune, descrizione, provincia, definizione_sito, sito_path
- **Straturi GIS asociate**: PYSITO_POLYGON, PYSITO_POINT
- **Tezaur**: tipologia_sigla = '1.1'

---

*Documentatie PyArchInit - Fisa Santier*
*Versiune: 4.9.x*
*Ultima actualizare: Ianuarie 2026*
