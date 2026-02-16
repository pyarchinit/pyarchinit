# Tutorial 04: Fisa de Periodizare

## Cuprins
1. [Introducere](#introducere)
2. [Accesarea Fisei](#accesarea-fisei)
3. [Interfata Utilizator](#interfata-utilizator)
4. [Concepte Fundamentale](#concepte-fundamentale)
5. [Campurile Fisei](#campurile-fisei)
6. [Bara de Instrumente DBMS](#bara-de-instrumente-dbms)
7. [Functionalitati GIS](#functionalitati-gis)
8. [Export PDF](#export-pdf)
9. [Integrare AI](#integrare-ai)
10. [Flux de Lucru Operational](#flux-de-lucru-operational)
11. [Bune Practici](#bune-practici)
12. [Depanare](#depanare)

---

## Introducere

**Fisa de Periodizare** este un instrument fundamental pentru gestionarea fazelor cronologice ale unei sapaturi arheologice. Va permite sa definiti perioadele si fazele care caracterizeaza secventa stratigrafica a santierului, asociind fiecarei perechi perioada/faza o datare cronologica si o descriere.

### Scopul Fisei

- Definirea secventei cronologice a sapaturii
- Asocierea perioadelor si fazelor cu unitatile stratigrafice
- Gestionarea cronologiei absolute (ani) si relative (perioade istorice)
- Afisarea US-urilor pe perioada/faza pe harta GIS
- Generarea rapoartelor PDF ale periodizarii

### Relatia cu Alte Fise

Fisa de Periodizare este strans legata de:
- **Fisa US/USM**: Fiecare US este atribuit unei perioade si faze
- **Fisa Santier**: Perioadele sunt specifice fiecarui santier
- **Harris Matrix**: Perioadele coloreaza Matrix-ul pe faze cronologice

![Vedere Generala Fisa Periodizare](images/04_scheda_periodizzazione/01_panoramica.png)
*Figura 1: Vedere generala a Fisei de Periodizare*

---

## Accesarea Fisei

### Din Meniu

1. Deschideti QGIS cu plugin-ul PyArchInit activ
2. Meniu **PyArchInit** → **Gestionare inregistrari arheologice** → **Sapatura - Calcul pierdere de folosinta** → **Perioada si Faza**

![Meniu Periodizare](images/04_scheda_periodizzazione/02_menu_accesso.png)
*Figura 2: Accesarea fisei din meniu*

### Din Bara de Instrumente

1. Localizati bara de instrumente PyArchInit
2. Faceti clic pe pictograma **Periodizare** (pictograma santier cu ceas)

![Bara Periodizare](images/04_scheda_periodizzazione/03_toolbar_accesso.png)
*Figura 3: Pictograma in bara de instrumente*

---

## Interfata Utilizator

Interfata Fisei de Periodizare este organizata intr-un mod simplu si liniar:

![Interfata Completa](images/04_scheda_periodizzazione/04_interfaccia_completa.png)
*Figura 4: Structura completa a interfetei*

### Zone Principale

| Zona | Descriere |
|------|-----------|
| **1. Bara de Instrumente DBMS** | Bara pentru navigare si gestionarea inregistrarilor |
| **2. Indicatori de Stare** | Info BD, Stare, Sortare |
| **3. Date de Identificare** | Santier, Perioada, Faza, Cod perioada |
| **4. Date Descriptive** | Descrierea textuala a perioadei |
| **5. Cronologie** | Anul initial si final |
| **6. Datare Extinsa** | Selectie din vocabularul de epoci istorice |

---

## Concepte Fundamentale

### Perioada si Faza

Sistemul de periodizare din PyArchInit se bazeaza pe o structura ierarhica pe doua niveluri:

#### Perioada
**Perioada** reprezinta o macro-faza cronologica a sapaturii. Este identificata printr-un numar intreg (1, 2, 3, ...) si reprezinta subdiviziunile majore ale secventei stratigrafice.

Exemple de perioade:
- Perioada 1: Epoca contemporana
- Perioada 2: Epoca medievala
- Perioada 3: Epoca romana imperiala
- Perioada 4: Epoca romana republicana

#### Faza
**Faza** reprezinta o subdiviziune interna a perioadei. Este de asemenea identificata printr-un numar intreg si permite detalierea ulterioara a secventei.

Exemple de faze in Perioada 3 (Epoca romana imperiala):
- Faza 1: Secolele III-IV d.Hr.
- Faza 2: Secolul II d.Hr.
- Faza 3: Secolul I d.Hr.

### Codul Perioadei

**Codul Perioadei** este un identificator numeric unic care leaga perechea perioada/faza de US-uri. Cand atribuiti o perioada/faza unui US in Fisa US, acest cod este utilizat.

> **Important**: Codul perioadei trebuie sa fie unic pentru fiecare combinatie santier/perioada/faza.

### Schema Conceptuala

```
Santier
└── Perioada 1 (Epoca contemporana)
│   ├── Faza 1 → Cod 101
│   └── Faza 2 → Cod 102
├── Perioada 2 (Epoca medievala)
│   ├── Faza 1 → Cod 201
│   ├── Faza 2 → Cod 202
│   └── Faza 3 → Cod 203
└── Perioada 3 (Epoca romana)
    ├── Faza 1 → Cod 301
    └── Faza 2 → Cod 302
```

---

## Campurile Fisei

### Campuri de Identificare

#### Santier
- **Tip**: ComboBox (doar citire in modul navigare)
- **Obligatoriu**: Da
- **Descriere**: Selectati santierul arheologic caruia ii apartine periodizarea
- **Note**: Daca un santier implicit este setat in configurare, acest camp va fi precompletat si needitabil

![Campul Santier](images/04_scheda_periodizzazione/05_campo_sito.png)
*Figura 5: Campul de selectie santier*

#### Perioada
- **Tip**: ComboBox editabil
- **Obligatoriu**: Da
- **Valori**: Numere intregi de la 1 la 15 (predefinite) sau valori personalizate
- **Descriere**: Numarul cronologic al perioadei
- **Note**: Numerele mai mici indica perioade mai recente, numerele mai mari indica perioade mai vechi

#### Faza
- **Tip**: ComboBox editabil
- **Obligatoriu**: Da
- **Valori**: Numere intregi de la 1 la 15 (predefinite) sau valori personalizate
- **Descriere**: Numarul fazei in cadrul perioadei

![Campuri Perioada si Faza](images/04_scheda_periodizzazione/06_campi_periodo_fase.png)
*Figura 6: Campurile Perioada si Faza*

#### Codul Perioadei
- **Tip**: LineEdit (text)
- **Obligatoriu**: Nu (dar foarte recomandat)
- **Descriere**: Cod numeric unic pentru identificarea perechii perioada/faza
- **Sugestie**: Folositi o conventie de tip `[perioada][faza]` (de ex., 101, 102, 201, 301)

![Campul Cod Perioada](images/04_scheda_periodizzazione/07_codice_periodo.png)
*Figura 7: Campul Cod Perioada*

### Campuri Descriptive

#### Descriere
- **Tip**: TextEdit (mai multe linii)
- **Obligatoriu**: Nu
- **Descriere**: Descrierea textuala a perioadei/fazei
- **Continut sugerat**:
  - Caracteristici generale ale perioadei
  - Evenimente istorice legate
  - Tipuri de structuri/materiale asteptate
  - Referinte bibliografice

![Campul Descriere](images/04_scheda_periodizzazione/08_campo_descrizione.png)
*Figura 8: Campul de descriere*

### Campuri Cronologice

#### Cronologie Initiala
- **Tip**: LineEdit (numeric)
- **Obligatoriu**: Nu
- **Format**: An numeric
- **Note**:
  - Valori pozitive = d.Hr.
  - Valori negative = i.Hr.
  - Exemplu: `-100` pentru 100 i.Hr., `200` pentru 200 d.Hr.

#### Cronologie Finala
- **Tip**: LineEdit (numeric)
- **Obligatoriu**: Nu
- **Format**: An numeric (aceleasi conventii ca la Cronologia Initiala)

![Campuri Cronologie](images/04_scheda_periodizzazione/09_campi_cronologia.png)
*Figura 9: Campurile Cronologie Initiala si Finala*

#### Datare Extinsa (Epoci Istorice)
- **Tip**: ComboBox editabil cu vocabular preincarcat
- **Obligatoriu**: Nu
- **Descriere**: Selectie dintr-un vocabular de epoci istorice predefinite
- **Functie automata**: La selectarea unei epoci, campurile Cronologie Initiala si Finala se completeaza automat

![Datare Extinsa](images/04_scheda_periodizzazione/10_datazione_estesa.png)
*Figura 10: ComboBox Datare Extinsa cu epoci preincarcate*

### Vocabularul Epocilor Istorice

Vocabularul include o gama larga de perioade istorice:

| Categorie | Exemple |
|-----------|---------|
| **Epoca Contemporana** | Secolul XXI, Secolul XX |
| **Epoca Moderna** | Secolele XIX-XVI |
| **Epoca Medievala** | Secolele XV-VIII |
| **Epoca Antica** | Secolele VII-I |
| **Imperiul Roman** | Perioade specifice (Iulio-Claudiana, Flaviana etc.) |
| **Imperiul Bizantin** | Perioade specifice |
| **Preistorie** | Paleolitic, Mezolitic, Neolitic, Epoca Bronzului, Epoca Fierului |

---

## Bara de Instrumente DBMS

Bara de instrumente DBMS permite gestionarea completa a inregistrarilor:

![Bara DBMS](images/04_scheda_periodizzazione/11_toolbar_dbms.png)
*Figura 11: Bara de instrumente DBMS completa*

### Butoane de Navigare

| Pictograma | Nume | Functie | Scurtatura |
|------------|------|---------|------------|
| ![Prima](images/icons/first.png) | Prima | Mergi la prima inregistrare | - |
| ![Anterioara](images/icons/prev.png) | Anterioara | Mergi la inregistrarea anterioara | - |
| ![Urmatoarea](images/icons/next.png) | Urmatoarea | Mergi la inregistrarea urmatoare | - |
| ![Ultima](images/icons/last.png) | Ultima | Mergi la ultima inregistrare | - |

### Butoane de Gestionare Inregistrari

| Pictograma | Nume | Functie |
|------------|------|---------|
| ![Nou](images/icons/new.png) | Inregistrare noua | Creeaza o inregistrare noua |
| ![Salvare](images/icons/save.png) | Salvare | Salveaza modificarile |
| ![Stergere](images/icons/delete.png) | Stergere | Sterge inregistrarea curenta |
| ![Vizualizare Toate](images/icons/view_all.png) | Vizualizare toate | Vizualizeaza toate inregistrarile |

### Butoane de Cautare

| Pictograma | Nume | Functie |
|------------|------|---------|
| ![Cautare Noua](images/icons/new_search.png) | Cautare noua | Activeaza modul de cautare |
| ![Cautare](images/icons/search.png) | Cauta!!! | Executa cautarea |
| ![Sortare](images/icons/sort.png) | Ordoneaza dupa | Sorteaza inregistrarile |

### Indicatori de Stare

![Indicatori de Stare](images/04_scheda_periodizzazione/12_indicatori_stato.png)
*Figura 12: Indicatori de stare*

| Indicator | Descriere |
|-----------|-----------|
| **Stare** | Modul curent: "Utilizare" (navigare), "Cautare" (cautare), "Inregistrare Noua" |
| **Sortare** | "Nesortat" sau "Sortat" |
| **inregistrarea nr.** | Numarul inregistrarii curente |
| **total inregistrari** | Numarul total de inregistrari |

---

## Functionalitati GIS

Fisa de Periodizare ofera functionalitati puternice de vizualizare GIS pentru a vizualiza US-urile asociate fiecarei perioade/faze.

### Butoane GIS

![Butoane GIS](images/04_scheda_periodizzazione/13_pulsanti_gis.png)
*Figura 13: Butoane pentru vizualizare GIS*

#### Vizualizare Perioada Unica (Pictograma GIS)
- **Functie**: Incarca toate US-urile asociate perioadei/fazei curente pe harta QGIS
- **Cerinta**: Campul Cod Perioada trebuie completat
- **Straturi incarcate**: US si USM filtrate dupa codul perioadei

#### Vizualizare Toate Perioadele - US (Pictograma Straturi Multiple)
- **Functie**: Incarca toate perioadele ca straturi separate pe harta (doar US)
- **Rezultat**: Un strat pentru fiecare combinatie perioada/faza

#### Vizualizare Toate Perioadele - USM (Pictograma GIS3)
- **Functie**: Incarca toate perioadele ca straturi separate pe harta (doar USM)
- **Rezultat**: Un strat pentru fiecare combinatie perioada/faza pentru unitatile murale

### Vizualizare pe Harta

![Harta cu Perioade](images/04_scheda_periodizzazione/14_mappa_periodi.png)
*Figura 14: US-uri afisate pe perioada pe harta QGIS*

La incarcarea straturilor pe perioade:
- Fiecare perioada/faza are o culoare distinctiva
- US-urile sunt filtrate pe baza codului de perioada atribuit
- Straturile individuale pot fi activate/dezactivate

---

## Export PDF

Fisa ofera doua moduri de export PDF:

### Export Fisa Individuala

![Buton PDF Fisa](images/04_scheda_periodizzazione/15_pulsante_pdf_scheda.png)
*Figura 15: Butonul de export PDF fisa*

- **Pictograma**: PDF
- **Functie**: Genereaza un PDF cu datele perioadei/fazei curente
- **Continut**:
  - Informatii de identificare (Santier, Perioada, Faza)
  - Cronologie (initiala, finala, datare extinsa)
  - Descriere completa

### Export Lista Periodizare

![Buton PDF Lista](images/04_scheda_periodizzazione/16_pulsante_pdf_lista.png)
*Figura 16: Butonul de export PDF lista*

- **Pictograma**: Fisa
- **Functie**: Genereaza un PDF cu lista tuturor perioadelor/fazelor santierului
- **Continut**: Tabel sumar cu toate perioadele

### Exemplu PDF Generat

![Exemplu PDF](images/04_scheda_periodizzazione/17_esempio_pdf.png)
*Figura 17: Exemplu de PDF generat*

---

## Integrare AI

Fisa de Periodizare include integrare GPT pentru obtinerea sugestiilor automate de descrieri ale perioadelor istorice.

### Butonul Sugestii

![Buton Sugestii](images/04_scheda_periodizzazione/18_pulsante_suggerimenti.png)
*Figura 18: Butonul Sugestii AI*

### Cum Functioneaza

1. Selectati o epoca istorica din campul **Datare Extinsa**
2. Faceti clic pe butonul **Sugestii**
3. Selectati modelul GPT de utilizat (gpt-4o sau gpt-4)
4. Sistemul genereaza automat:
   - O descriere a perioadei istorice
   - 3 linkuri relevante Wikipedia
5. Textul generat poate fi inserat in campul Descriere

### Configurare Cheie API

Pentru a utiliza aceasta functionalitate:
1. Obtineti o Cheie API de la OpenAI
2. La prima utilizare, sistemul solicita cheia
3. Cheia este salvata in `PYARCHINIT_HOME/bin/gpt_api_key.txt`

> **Nota**: Aceasta functionalitate necesita conexiune la internet si un cont OpenAI cu credite disponibile.

---

## Flux de Lucru Operational

### Crearea unei Periodizari Noi

#### Pasul 1: Accesati Fisa
1. Deschideti Fisa de Periodizare din meniu sau bara de instrumente
2. Verificati conexiunea la baza de date (indicator de stare)

![Flux Pasul 1](images/04_scheda_periodizzazione/19_workflow_step1.png)
*Figura 19: Deschiderea fisei*

#### Pasul 2: Inregistrare Noua
1. Faceti clic pe butonul **Inregistrare noua**
2. Starea se schimba in "Inregistrare Noua"
3. Campurile devin editabile

![Flux Pasul 2](images/04_scheda_periodizzazione/20_workflow_step2.png)
*Figura 20: Clic pe Inregistrare noua*

#### Pasul 3: Selectia Santierului
1. Daca nu este presetat, selectati **Santierul** din meniul derulant
2. Santierul trebuie sa existe deja in Fisa Santier

![Flux Pasul 3](images/04_scheda_periodizzazione/21_workflow_step3.png)
*Figura 21: Selectia santierului*

#### Pasul 4: Definirea Perioadei si Fazei
1. Selectati sau introduceti numarul **Perioadei**
2. Selectati sau introduceti numarul **Fazei**
3. Introduceti **Codul Perioadei** unic

![Flux Pasul 4](images/04_scheda_periodizzazione/22_workflow_step4.png)
*Figura 22: Definirea perioadei si fazei*

#### Pasul 5: Cronologie
1. Selectati **Datarea Extinsa** din vocabularul de epoci
2. Campurile Cronologie Initiala si Finala se completeaza automat
3. Sau introduceti anii manual

![Flux Pasul 5](images/04_scheda_periodizzazione/23_workflow_step5.png)
*Figura 23: Setarea cronologiei*

#### Pasul 6: Descriere
1. Completati campul **Descriere** cu informatii despre perioada
2. Optional: folositi butonul **Sugestii** pentru a obtine text generat de AI

![Flux Pasul 6](images/04_scheda_periodizzazione/24_workflow_step6.png)
*Figura 24: Completarea descrierii*

#### Pasul 7: Salvare
1. Faceti clic pe butonul **Salvare**
2. Inregistrarea este salvata in baza de date
3. Starea revine la "Utilizare"

![Flux Pasul 7](images/04_scheda_periodizzazione/25_workflow_step7.png)
*Figura 25: Salvare*

### Schema de Periodizare Recomandata

Pentru o sapatura tipica, se recomanda crearea periodizarii dupa aceasta schema:

| Perioada | Faza | Cod | Descriere |
|----------|------|-----|-----------|
| 1 | 1 | 101 | Epoca contemporana - Aratura |
| 1 | 2 | 102 | Epoca contemporana - Abandonare |
| 2 | 1 | 201 | Epoca medievala - Faza tarzie |
| 2 | 2 | 202 | Epoca medievala - Faza centrala |
| 2 | 3 | 203 | Epoca medievala - Faza initiala |
| 3 | 1 | 301 | Epoca romana - Faza imperiala |
| 3 | 2 | 302 | Epoca romana - Faza republicana |
| 4 | 1 | 401 | Epoca pre-romana |

---

## Bune Practici

### Conventii de Numerotare

1. **Perioade**: Numerotati de la cea mai recenta (1) la cea mai veche
2. **Faze**: Numerotati de la cea mai recenta (1) la cea mai veche in cadrul perioadei
3. **Coduri**: Folositi formula `[perioada * 100 + faza]` pentru coduri unice

### Descrieri Eficiente

O buna descriere a perioadei ar trebui sa includa:
- Cadrul cronologic
- Caracteristicile principale ale perioadei
- Tipurile de structuri/materiale asteptate
- Comparatii cu situri contemporane
- Referinte bibliografice

### Gestionarea Cronologiei

- Folositi intotdeauna ani numerici pentru cronologii
- Pentru date i.Hr., folositi numere negative
- Verificati consistenta: cronologia finala trebuie sa fie >= initiala (in valoare absoluta pentru i.Hr.)

### Legatura cu US-urile

Dupa crearea periodizarii:
1. Deschideti Fisa US
2. In fila **Periodizare**, atribuiti Perioada Initiala/Finala si Faza Initiala/Finala
3. Sistemul va asocia automat US-ul cu periodizarea

---

## Depanare

### Probleme Frecvente

#### "Codul perioadei nu a fost adaugat"
- **Cauza**: Campul Cod Perioada este gol
- **Solutie**: Completati campul Cod Perioada inainte de a utiliza functiile GIS

#### Cronologia nu se completeaza automat
- **Cauza**: Epoca selectata nu are date asociate
- **Solutie**: Verificati ca epoca este prezenta in fisierul CSV de epoci istorice

#### Eroare de salvare: inregistrare duplicata
- **Cauza**: Exista deja o inregistrare cu aceeasi combinatie Santier/Perioada/Faza
- **Solutie**: Verificati valorile si folositi o combinatie unica

#### US-urile nu apar in vizualizarea GIS
- **Cauza**: US-urile nu au codul perioadei atribuit
- **Solutie**:
  1. Verificati in Fisa US ca campurile Perioada/Faza sunt completate
  2. Verificati ca Codul Perioadei corespunde

#### Sugestiile AI nu functioneaza
- **Cauza**: Cheie API lipsa sau invalida
- **Solutie**:
  1. Verificati conexiunea la internet
  2. Verificati validitatea cheii API
  3. Reinstalati bibliotecile: `pip install --upgrade openai pydantic`

---

## Tutorial Video

### Video 1: Prezentare Generala a Fisei de Periodizare
*Durata: 3-4 minute*

[Substituent tutorial video]

**Continut:**
- Deschiderea fisei
- Descrierea interfetei
- Navigarea intre inregistrari

### Video 2: Creare Periodizare Completa
*Durata: 5-6 minute*

[Substituent tutorial video]

**Continut:**
- Crearea unei periodizari noi
- Completarea tuturor campurilor
- Utilizarea vocabularului de epoci
- Salvare

### Video 3: Vizualizare GIS pe Perioade
*Durata: 3-4 minute*

[Substituent tutorial video]

**Continut:**
- Utilizarea butoanelor GIS
- Vizualizarea US-urilor pe perioade
- Gestionarea straturilor incarcate

---

## Rezumat Campuri

| Camp | Tip | Obligatoriu | Baza de Date |
|------|-----|-------------|--------------|
| Santier | ComboBox | Da | sito |
| Perioada | ComboBox | Da | periodo |
| Faza | ComboBox | Da | fase |
| Cod Perioada | LineEdit | Nu | cont_per |
| Descriere | TextEdit | Nu | descrizione |
| Cronologie Initiala | LineEdit | Nu | cron_iniziale |
| Cronologie Finala | LineEdit | Nu | cron_finale |
| Datare Extinsa | ComboBox | Nu | datazione_estesa |

---

*Ultima actualizare: Ianuarie 2026*
*PyArchInit - Sketches of Sketches*
