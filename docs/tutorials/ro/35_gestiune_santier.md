# PyArchInit - Gestiune Santier

## Cuprins
1. [Introducere](#introducere)
2. [Accesarea modulului](#accesarea-modulului)
3. [Panou Santier (Dashboard)](#panou-santier-dashboard)
4. [Fisa Personal](#fisa-personal)
5. [Fisa Prezente](#fisa-prezente)
6. [Fisa Echipamente](#fisa-echipamente)
7. [Fisa Buget](#fisa-buget)
8. [Computo Metric](#computo-metric)
9. [Flux de lucru recomandat](#flux-de-lucru-recomandat)
10. [Depanare](#depanare)
11. [Intrebari frecvente](#intrebari-frecvente)

---

## Introducere

Modulul **Gestiune Santier** ofera un set complet de instrumente pentru administrarea operationala a unui santier arheologic. In loc sa gestionati doar datele stratigrafice, acest modul va permite sa monitorizati personalul, prezentele, echipamentele si bugetul direct din QGIS.

Modulul este compus din **cinci formulare** interconectate:

| Formular | Functie |
|----------|---------|
| **Panou Santier** | Dashboard central cu sumar buget, personal, echipamente si computo metric |
| **Personal** | Gestionarea datelor angajatilor si colaboratorilor |
| **Prezente** | Inregistrarea zilnica a prezentelor, orelor si costurilor |
| **Echipamente** | Inventarul echipamentelor si programul de mentenanta |
| **Buget** | Planificarea si monitorizarea cheltuielilor pe categorii |

Toate datele sunt stocate in baza de date PyArchInit (PostgreSQL sau SQLite) si sunt filtrate automat in functie de santierul selectat.

<!-- VIDEO: Introducere in modulul Gestiune Santier -->
> **Tutorial Video**: [Inserati link video pentru introducerea in Gestiune Santier]

---

## Accesarea modulului

Modulul Gestiune Santier dispune de o **bara de instrumente dedicata** in QGIS, cu 5 pictograme:

<!-- IMAGINE: Bara de instrumente Gestiune Santier cu cele 5 pictograme -->
> **Fig. 1**: Bara de instrumente "Gestiune Santier" cu cele cinci pictograme

| # | Pictograma | Formular | Descriere |
|---|------------|----------|-----------|
| 1 | Dashboard | **Panou Santier** | Dashboard central cu sumare si computo metric |
| 2 | Personal | **Personal** | Fisa pentru gestionarea personalului |
| 3 | Prezente | **Prezente** | Fisa pentru inregistrarea prezentelor |
| 4 | Echipamente | **Echipamente** | Fisa pentru inventarul echipamentelor |
| 5 | Buget | **Buget** | Fisa pentru gestionarea bugetului |

Formularele sunt accesibile si din meniul **PyArchInit** --> **Archaeological GIS Tools**.

<!-- IMAGINE: Accesul din meniul PyArchInit -->
> **Fig. 2**: Accesarea formularelor Gestiune Santier din meniul principal

---

## Panou Santier (Dashboard)

Panoul Santier este **formularul central** al modulului. Ofera o vizualizare sintetica a tuturor datelor operationale pentru santierul si anul selectate.

<!-- IMAGINE: Dashboard complet cu toate sectiunile adnotate -->
> **Fig. 3**: Panoul Santier (Dashboard) cu zonele functionale numerotate

### Selectorul Santier/An

In partea superioara a panoului se gasesc doua liste derulante:

| Camp | Descriere |
|------|-----------|
| **Santier** | Selecteaza santierul curent (populat din `site_table`) |
| **An** | Selecteaza anul de referinta (ultimii 10 ani) |

Modificarea oricarei selectii **actualizeaza automat** toate sumarele din panou. Butonul **Actualizeaza** permite reincarcarea manuala a datelor.

<!-- IMAGINE: Selectorul santier/an din partea superioara -->
> **Fig. 4**: Selectorul de santier si an cu butonul Actualizeaza

### Sumar Buget

Sectiunea de sumar buget prezinta o comparatie intre cheltuielile planificate si cele efective:

| Element | Descriere |
|---------|-----------|
| **Buget planificat** | Suma totala a importurilor prevazute pentru anul selectat |
| **Buget cheltuit** | Suma totala a importurilor efective |
| **Bara de progres** | Procentul bugetului consumat (0-100%) |
| **Grafic circular** | Distributia cheltuielilor pe categorii |

Bara de progres se coloreaza in mod diferit in functie de procentul utilizat:
- **Verde**: sub 70%
- **Galben**: intre 70-90%
- **Rosu**: peste 90%

<!-- IMAGINE: Sectiunea sumar buget cu bara de progres si grafic circular -->
> **Fig. 5**: Sumarul bugetului cu bara de progres si graficul circular pe categorii

### Sumar Personal

Sectiunea de sumar personal afiseaza situatia prezentelor pentru **ziua curenta** si totaluri lunare:

| Indicator | Descriere |
|-----------|-----------|
| **Prezenti** | Numarul de persoane cu tip zi "lucratoare" astazi |
| **Concediu** | Numarul de persoane in concediu astazi |
| **Medical** | Numarul de persoane in concediu medical astazi |
| **Ore luna** | Totalul orelor (ordinare + suplimentare) pentru luna curenta |
| **Cost luna** | Costul total al zilelor lucrate in luna curenta |

<!-- IMAGINE: Sectiunea sumar personal cu indicatorii zilnici si lunari -->
> **Fig. 6**: Sumarul personalului cu indicatorii de prezenta si totalurile lunare

### Sumar Echipamente

Sectiunea de sumar echipamente ofera o privire de ansamblu asupra inventarului:

| Indicator | Descriere |
|-----------|-----------|
| **Total** | Numarul total de echipamente inregistrate pentru santier |
| **In uz** | Echipamente cu starea `in_uso` |
| **Mentenanta** | Echipamente cu starea `manutenzione` |
| **Alerte intarziere** | Echipamente cu data urmatoarei mentenante depasita |

Alertele de intarziere sunt afisate cu **text rosu** si includ numarul de echipamente cu mentenanta intarziata.

<!-- IMAGINE: Sectiunea sumar echipamente cu alerta de mentenanta -->
> **Fig. 7**: Sumarul echipamentelor cu alerta de mentenanta intarziata (text rosu)

---

## Fisa Personal

Fisa Personal este un formular CRUD standard pentru gestionarea datelor angajatilor si colaboratorilor santierului.

<!-- IMAGINE: Fisa Personal completa -->
> **Fig. 8**: Fisa Personal cu toate campurile vizibile

### Campuri disponibile

| Camp | Tip | Descriere |
|------|-----|-----------|
| **Santier** | Text | Santierul de referinta |
| **Nume** | Text | Numele de familie |
| **Prenume** | Text | Prenumele |
| **Calificare** | Text | Calificarea profesionala |
| **Rol** | Text | Rolul pe santier (director, arheolog, muncitor etc.) |
| **Cod fiscal** | Text | Codul fiscal |
| **Email** | Text | Adresa de email |
| **Telefon** | Text | Numarul de telefon |
| **Data nasterii** | Data | Data de nastere |
| **Adresa** | Text | Adresa de domiciliu |
| **Tip contract** | Text | Tipul contractului |
| **Data inceput contract** | Data | Data angajarii / inceputului contractului |
| **Data sfarsit contract** | Data | Data expirarii contractului |
| **Tarif orar** | Numeric | Costul pe ora |
| **Tarif zilnic** | Numeric | Costul pe zi |
| **IBAN** | Text | Coordonate bancare |
| **Activ** | Boolean | Daca persoana este activa pe santier |
| **Note** | Text | Observatii suplimentare |

### Bara de instrumente DBMS

Fisa Personal dispune de bara DBMS standard PyArchInit:

| Buton | Functie |
|-------|---------|
| **Inregistrare noua** | Pregateste formularul pentru o noua persoana |
| **Salvare** | Salveaza inregistrarea curenta |
| **Stergere** | Sterge inregistrarea curenta (cu confirmare) |
| **Cautare noua** | Activeaza modul de cautare |
| **Cauta** | Executa cautarea |
| **Vizualizare toate** | Afiseaza toate inregistrarile |
| **Navigare** | Prima / Anterioara / Urmatoare / Ultima inregistrare |
| **Sortare** | Ordoneaza inregistrarile dupa un camp selectat |

<!-- IMAGINE: Bara DBMS din fisa Personal -->
> **Fig. 9**: Bara de instrumente DBMS din fisa Personal

---

## Fisa Prezente

Fisa Prezente permite inregistrarea zilnica a activitatii fiecarei persoane.

<!-- IMAGINE: Fisa Prezente completa -->
> **Fig. 10**: Fisa Prezente cu toate campurile

### Campuri disponibile

| Camp | Tip | Descriere |
|------|-----|-----------|
| **Santier** | Text | Santierul de referinta |
| **ID Personal** | Numeric | Identificatorul persoanei (din fisa Personal) |
| **Data** | Data | Data prezentei |
| **Ora intrare** | Ora | Ora de inceput a programului |
| **Ora iesire** | Ora | Ora de sfarsit a programului |
| **Ore ordinare** | Numeric | Numarul de ore de lucru ordinare |
| **Ore suplimentare** | Numeric | Numarul de ore suplimentare |
| **Tip zi** | Lista | Tipul zilei: `lucratoare`, `concediu`, `medical`, `permis` |
| **Tur** | Text | Turul de lucru |
| **Zona de lucru** | Text | Zona / sectorul de lucru pe santier |
| **Cost zi** | Numeric | Costul total al zilei (calculat automat sau manual) |
| **Note** | Text | Observatii suplimentare |

### Flux tipic de utilizare

1. Deschideti fisa Prezente
2. Faceti clic pe **Inregistrare noua**
3. Selectati santierul si introduceti ID-ul personalului
4. Introduceti data, orele de intrare/iesire si tipul zilei
5. Completati orele ordinare/suplimentare si costul zilei
6. Faceti clic pe **Salvare**

<!-- IMAGINE: Exemplu de completare a fisei Prezente -->
> **Fig. 11**: Exemplu de inregistrare a unei zile lucratoare cu 8 ore ordinare

---

## Fisa Echipamente

Fisa Echipamente gestioneaza inventarul echipamentelor si programul de mentenanta.

<!-- IMAGINE: Fisa Echipamente completa -->
> **Fig. 12**: Fisa Echipamente cu toate campurile

### Campuri disponibile

| Camp | Tip | Descriere |
|------|-----|-----------|
| **Santier** | Text | Santierul de referinta |
| **Cod inventar** | Text | Codul unic de inventar |
| **Nume** | Text | Denumirea echipamentului |
| **Categorie** | Text | Tipul/categoria (topografie, sapatura, fotografie etc.) |
| **Marca** | Text | Marca producatorului |
| **Model** | Text | Modelul echipamentului |
| **Numar de serie** | Text | Numarul de serie |
| **Proprietate** | Text | Proprietar (santier / inchiriat / imprumut) |
| **Data achizitie** | Data | Data cumpararii/inchirierii |
| **Cost achizitie** | Numeric | Costul de achizitie |
| **Cost inchiriere/zi** | Numeric | Costul zilnic de inchiriere (daca este cazul) |
| **Stare** | Lista | Starea curenta: `in_uso`, `manutenzione`, `fuori_uso` |
| **Asignat la** | Text | Persoana responsabila |
| **Ultima mentenanta** | Data | Data ultimei mentenante |
| **Urmatoarea mentenanta** | Data | Data programata pentru urmatoarea mentenanta |
| **Note** | Text | Observatii suplimentare |

### Alerte de mentenanta

Cand data campului **Urmatoarea mentenanta** este depasita si starea echipamentului nu este `fuori_uso`, sistemul genereaza o alerta vizibila in Panoul Santier. Este recomandat sa verificati periodic dashboard-ul pentru a identifica echipamentele care necesita mentenanta.

<!-- IMAGINE: Detaliu al alertei de mentenanta in fisa Echipamente -->
> **Fig. 13**: Echipament cu mentenanta intarziata (evidentiata in panou)

---

## Fisa Buget

Fisa Buget permite planificarea si monitorizarea cheltuielilor pe categorii.

<!-- IMAGINE: Fisa Buget completa -->
> **Fig. 14**: Fisa Buget cu toate campurile

### Campuri disponibile

| Camp | Tip | Descriere |
|------|-----|-----------|
| **Santier** | Text | Santierul de referinta |
| **An** | Numeric | Anul bugetar |
| **Categorie** | Text | Categoria cheltuielii (personal, echipamente, logistica etc.) |
| **Descriere** | Text | Descrierea articolului de cheltuiala |
| **Suma planificata** | Numeric | Importul prevazut (bugetat) |
| **Suma efectiva** | Numeric | Importul real cheltuit |
| **Data inregistrarii** | Data | Data cand inregistrarea a fost creata |
| **Data cheltuielii** | Data | Data efectuarii cheltuielii |
| **Furnizor** | Text | Numele furnizorului |
| **Numar factura** | Text | Numarul facturii |
| **Note** | Text | Observatii suplimentare |

### Categorii tipice de buget

| Categorie | Descriere |
|-----------|-----------|
| Personal | Salarii, indemnizatii, contributii |
| Echipamente | Achizitie si inchiriere echipamente |
| Logistica | Transport, cazare, masa |
| Materiale | Consumabile, materiale de laborator |
| Consultanta | Servicii externe, analize de specialitate |
| Diverse | Alte cheltuieli neincadrate |

<!-- IMAGINE: Exemplu de grafic circular al distributiei bugetului pe categorii -->
> **Fig. 15**: Graficul circular din Panoul Santier arata distributia bugetului pe categorii

---

## Computo Metric

Sectiunea **Computo Metric** din Panoul Santier ofera instrumente de calcul al volumelor excavate pe baza straturilor DEM (Model Digital de Elevatie) incarcate in proiectul QGIS.

<!-- IMAGINE: Sectiunea Computo Metric din dashboard -->
> **Fig. 16**: Sectiunea Computo Metric cu selectoarele DEM si tabelul istoric

### Metode de calcul

Sunt disponibile doua metode de calcul:

#### 1. Diferenta DEM

Calculeaza volumul excavat ca diferenta intre doua straturi DEM (pre-sapatura si post-sapatura):

| Camp | Descriere |
|------|-----------|
| **DEM Pre** | Stratul raster DEM inainte de sapatura |
| **DEM Post** | Stratul raster DEM dupa sapatura |

Volumul este calculat pixel cu pixel ca diferenta de altitudine inmultita cu aria fiecarui pixel.

#### 2. DEM + Poligon

Calculeaza volumul intr-o zona delimitata de un poligon vectorial:

| Camp | Descriere |
|------|-----------|
| **DEM** | Stratul raster DEM |
| **Strat poligon** | Stratul vectorial cu poligonul de delimitare |

### Procedura de calcul

1. Selectati metoda de calcul (Diferenta DEM sau DEM + Poligon)
2. Selectati straturile DEM din listele derulante (se populeaza automat din proiectul QGIS)
3. Faceti clic pe **Calculeaza**
4. Rezultatele sunt afisate in aria si volumul calculate
5. Faceti clic pe **Salveaza Computo** pentru a inregistra rezultatul in baza de date

### Istoric Computo

Tabelul din partea inferioara a sectiunii afiseaza toate calculele anterioare:

| Coloana | Descriere |
|---------|-----------|
| **Data calcul** | Data si ora efectuarii calculului |
| **Tip calcul** | Metoda utilizata (diferenta DEM / DEM + poligon) |
| **Arie (mp)** | Aria calculata in metri patrati |
| **Volum (mc)** | Volumul calculat in metri cubi |
| **Note** | Observatii suplimentare |

<!-- IMAGINE: Tabelul istoric computo cu mai multe inregistrari -->
> **Fig. 17**: Istoricul calculelor de computo metric cu mai multe inregistrari

---

## Flux de lucru recomandat

### Configurarea initiala a santierului

1. **Creati santierul** in Fisa Santier (Tutorial 02) daca nu exista deja
2. **Adaugati personalul**: Deschideti fisa Personal si creati o inregistrare pentru fiecare membru al echipei
3. **Inregistrati echipamentele**: Deschideti fisa Echipamente si adaugati toate instrumentele si dispozitivele
4. **Planificati bugetul**: Deschideti fisa Buget si introduceti sumele planificate pe categorii

### Operatiuni zilnice

1. **Inregistrati prezentele** la inceputul si sfarsitul fiecarei zile de lucru
2. **Verificati Panoul Santier** pentru a monitoriza situatia generala
3. **Actualizati starea echipamentelor** cand se modifica (mentenanta, scos din uz etc.)
4. **Inregistrati cheltuielile** in fisa Buget pe masura ce apar

### Monitorizare periodica

1. Verificati **bara de progres a bugetului** in Panoul Santier
2. Verificati **alertele de mentenanta** pentru echipamente
3. Rulati calculul **Computo Metric** pentru a monitoriza volumele excavate
4. Exportati rapoarte de situatie din Panoul Santier

<!-- IMAGINE: Schema fluxului de lucru recomandat -->
> **Fig. 18**: Schema fluxului de lucru recomandat pentru utilizarea modulului Gestiune Santier

---

## Depanare

### Panoul Santier nu afiseaza date

- Verificati ca ati selectat un santier valid din lista derulanta
- Verificati conexiunea la baza de date
- Faceti clic pe butonul **Actualizeaza** pentru a forta reincarcarea datelor
- Asigurati-va ca exista inregistrari in tabelele de buget, prezente si echipamente pentru santierul selectat

### Fisa Personal / Prezente / Echipamente / Buget nu se deschide

- Verificati ca bara de instrumente "Gestiune Santier" este vizibila (Vizualizare --> Bare de instrumente)
- Verificati conexiunea la baza de date din configurarea PyArchInit
- Reporniti QGIS si reincarcati plugin-ul

### Calculul Computo Metric esueaza

- Asigurati-va ca straturile DEM sunt incarcate in proiectul QGIS curent
- Verificati ca straturile DEM au aceeasi proiectie si rezolutie
- Pentru metoda DEM + Poligon, asigurati-va ca stratul poligon este valid si contine cel putin un poligon

### Graficul circular nu se afiseaza

- Verificati ca exista inregistrari buget cu categorii diferite
- Verificati ca valorile numerice sunt corecte (numere pozitive)

### Alertele de mentenanta nu apar

- Verificati ca datele de mentenanta sunt completate corect in fisa Echipamente
- Asigurati-va ca formatul datei este corect (YYYY-MM-DD)

---

## Intrebari frecvente

### Pot utiliza modulul Gestiune Santier fara conexiune la internet?

**Da.** Modulul functioneaza complet offline, folosind baza de date locala SQLite sau PostgreSQL. Nu este necesara conexiune la internet pentru nicio functionalitate.

### Cum se leaga prezentele de fisa Personal?

Fiecare inregistrare de prezenta contine un camp **ID Personal** care face referinta la inregistrarea corespunzatoare din fisa Personal. Panoul Santier foloseste aceasta legatura pentru a calcula totalurile lunare.

### Pot gestiona mai multe santiere simultan?

Da, dar Panoul Santier afiseaza datele pentru **un singur santier la un moment dat**. Puteti comuta intre santiere folosind selectorul din partea superioara a panoului. Fiecare formular CRUD (Personal, Prezente, Echipamente, Buget) filtreaza automat datele in functie de santierul configurat in PyArchInit.

### Cum functioneaza calculul volumului din Computo Metric?

Calculul **Diferenta DEM** scade valorile de altitudine ale DEM-ului post-sapatura din DEM-ul pre-sapatura, pixel cu pixel. Suma diferentelor inmultita cu aria fiecarui pixel da volumul total in metri cubi. Metoda **DEM + Poligon** limiteaza acest calcul la zona acoperita de poligonul selectat.

### Datele sunt compatibile atat cu PostgreSQL cat si cu SQLite?

**Da.** Toate cele cinci formulare functioneaza cu ambele sisteme de baze de date suportate de PyArchInit. Datele sunt stocate in tabelele `personale_table`, `presenze_table`, `attrezzature_table`, `budget_table` si `computo_metrico`.

### Pot exporta datele bugetului sau prezentelor?

In prezent, datele pot fi vizualizate si gestionate din formularele CRUD. Exportul in format CSV sau PDF este planificat pentru versiunile viitoare. Puteti utiliza instrumentele de export standard ale bazei de date (pgAdmin pentru PostgreSQL, DB Browser for SQLite) pentru a exporta datele.

---

## Note Tehnice

| Element | Detalii |
|---------|---------|
| **Tabele baza de date** | `personale_table`, `presenze_table`, `attrezzature_table`, `budget_table`, `computo_metrico` |
| **Controlere** | `tabs/Cantiere.py`, `tabs/Personale.py`, `tabs/Presenze.py`, `tabs/Attrezzature.py`, `tabs/Budget.py` |
| **Fisiere UI** | `gui/ui/Cantiere.ui`, `gui/ui/Personale.ui`, `gui/ui/Presenze.ui`, `gui/ui/Attrezzature.ui`, `gui/ui/Budget.ui` |
| **Mapper** | `PERSONALE`, `PRESENZE`, `ATTREZZATURE`, `BUDGET`, `COMPUTO_METRICO` |
| **Bara de instrumente** | "pyArchInit - Gestione Cantiere" (objectName: `pyArchInitCantiere`) |

---

*Documentatie PyArchInit - Gestiune Santier*
*Versiune: 5.0.x*
*Ultima actualizare: februarie 2026*
