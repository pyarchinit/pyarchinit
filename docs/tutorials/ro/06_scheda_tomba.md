# Tutorial 06: Fisa Mormant

## Introducere

**Fisa Mormant** este modulul PyArchInit dedicat documentarii inmormantarilor arheologice. Acest instrument va permite sa inregistrati toate aspectele unui mormant: de la structura funerara la rit, de la inventarul funerar la indivizii inmormantati.

### Concepte de Baza

**Mormant in PyArchInit:**
- Un mormant este o structura funerara care contine unul sau mai multi indivizi
- Este legat de Fisa Structura (structura fizica a inmormantarii)
- Este legat de Fisa Individ (pentru datele antropologice)
- Documenteaza ritul, inventarul funerar si caracteristicile depunerii

**Relatii:**
```
Mormant → Structura (containerul fizic)
        → Individ(i) (ramacitele umane)
        → Inventar funerar (obiecte insotitoare)
        → Inventar Materiale (descoperiri asociate)
```

---

## Accesarea Fisei

### Din Meniu
1. Meniu **PyArchInit** din bara de meniu QGIS
2. Selectati **Fisa Mormant**

![Acces din meniu](images/06_scheda_tomba/02_menu_accesso.png)

### Din Bara de Instrumente
1. Localizati bara de instrumente PyArchInit
2. Faceti clic pe pictograma **Mormant** (simbol funerar)

![Acces din bara](images/06_scheda_tomba/03_toolbar_accesso.png)

---

## Vedere Generala a Interfetei

Fisa prezinta o structura organizata in sectiuni functionale:

![Interfata completa](images/06_scheda_tomba/04_interfaccia_completa.png)

### Zone Principale

| # | Zona | Descriere |
|---|------|-----------|
| 1 | Bara DBMS | Navigare, cautare, salvare |
| 2 | Info BD | Starea inregistrarii, sortare, contor |
| 3 | Campuri de Identificare | Santier, Zona, Nr. Fisa, Structura |
| 4 | Campuri Individ | Legatura cu individul |
| 5 | Zona de File | File tematice pentru date specifice |

---

## Bara de Instrumente DBMS

Bara principala ofera instrumente pentru gestionarea inregistrarilor.

![Bara DBMS](images/06_scheda_tomba/05_toolbar_dbms.png)

### Butoane de Navigare

| Pictograma | Functie | Descriere |
|------------|---------|-----------|
| ![Prima](../../resources/icons/5_leftArrows.png) | Prima inreg. | Mergi la prima inregistrare |
| ![Anterioara](../../resources/icons/4_leftArrow.png) | Inreg. anterioara | Mergi la inregistrarea anterioara |
| ![Urmatoarea](../../resources/icons/6_rightArrow.png) | Inreg. urmatoare | Mergi la inregistrarea urmatoare |
| ![Ultima](../../resources/icons/7_rightArrows.png) | Ultima inreg. | Mergi la ultima inregistrare |

### Butoane CRUD

| Pictograma | Functie | Descriere |
|------------|---------|-----------|
| ![Nou](../../resources/icons/newrec.png) | Inregistrare noua | Creeaza o inregistrare noua de mormant |
| ![Salvare](../../resources/icons/b_save.png) | Salvare | Salveaza modificarile |
| ![Stergere](../../resources/icons/delete.png) | Stergere | Sterge inregistrarea curenta |

### Butoane de Cautare

| Pictograma | Functie | Descriere |
|------------|---------|-----------|
| ![Cautare Noua](../../resources/icons/new_search.png) | Cautare noua | Porneste cautare noua |
| ![Cautare](../../resources/icons/search.png) | Cauta!!! | Executa cautarea |
| ![Sortare](../../resources/icons/sort.png) | Ordoneaza dupa | Sorteaza rezultatele |
| ![Vizualizare Toate](../../resources/icons/view_all.png) | Vizualizare toate | Vizualizeaza toate inregistrarile |

### Butoane Speciale

| Pictograma | Functie | Descriere |
|------------|---------|-----------|
| ![GIS](../../resources/icons/GIS.png) | GIS | Incarca mormantul pe harta |
| ![PDF](../../resources/icons/pdf-icon.png) | Export PDF | Exporta in PDF |
| ![Director](../../resources/icons/directoryExp.png) | Deschide director | Deschide dosarul de export |

---

## Campuri de Identificare

Campurile de identificare definesc in mod unic mormantul in baza de date.

![Campuri de identificare](images/06_scheda_tomba/06_campi_identificativi.png)

### Santier

**Camp**: `comboBox_sito`
**Baza de date**: `sito`

Selectati santierul arheologic de apartenenta.

### Zona

**Camp**: `comboBox_area`
**Baza de date**: `area`

Zona de sapatura din cadrul santierului.

### Numarul Fisei

**Camp**: `lineEdit_nr_scheda`
**Baza de date**: `nr_scheda_taf`

Numarul progresiv al fisei mormantului. Urmatorul numar disponibil este propus automat.

### Codul si Numarul Structurii

| Camp | Baza de date | Descriere |
|------|--------------|-----------|
| Cod structura | `sigla_struttura` | Codul structurii (de ex., TM, TB) |
| Nr. structura | `nr_struttura` | Numarul structurii |

Aceste campuri leaga mormantul de Fisa Structura corespunzatoare.

### Numarul Individului

**Camp**: `comboBox_nr_individuo`
**Baza de date**: `nr_individuo`

Numarul individului inmormantat. Leaga mormantul de Fisa Individ.

**Note:**
- Un mormant poate contine mai multi indivizi (inmormantare multipla)
- Meniul afiseaza indivizii disponibili pentru structura selectata

---

## Fila Date Descriptive

Prima fila contine campuri fundamentale pentru descrierea inmormantarii.

![Fila Date Descriptive](images/06_scheda_tomba/07_tab_descrittivi.png)

### Rit

**Camp**: `comboBox_rito`
**Baza de date**: `rito`

Tipul ritualului funerar practicat.

**Valori tipice:**
| Rit | Descriere |
|-----|-----------|
| Inhumare | Depunerea corpului intreg |
| Incinerare | Arderea ramasitelor |
| Incinerare primara | Incinerare pe loc |
| Incinerare secundara | Incinerare in alta parte si depunere |
| Mixt | Combinatie de rituri |
| Nedeterminat | Nu se poate determina |

### Tipul de Inmormantare

**Camp**: `comboBox_tipo_sepoltura`
**Baza de date**: `tipo_sepoltura`

Clasificarea tipologica a inmormantarii.

**Exemple:**
- Mormant simplu in groapa
- Mormant in cista
- Mormant cu camera
- Mormant alla cappuccina
- Mormant enchytrismos
- Sarcofag
- Osuar

### Tipul de Depunere

**Camp**: `comboBox_tipo_deposizione`
**Baza de date**: `tipo_deposizione`

Metoda de depunere a corpului.

**Valori:**
- Primara (depunere directa)
- Secundara (reducere/deplasare)
- Multipla simultana
- Multipla succesiva

### Stare de Conservare

**Camp**: `comboBox_stato_conservazione`
**Baza de date**: `stato_di_conservazione`

Evaluarea starii de conservare.

**Scala:**
- Excelenta
- Buna
- Satisfacatoare
- Slaba
- Foarte slaba

### Descriere

**Camp**: `textEdit_descrizione`
**Baza de date**: `descrizione_taf`

Descriere detaliata a mormantului.

**Continut recomandat:**
- Forma si dimensiunile gropii
- Orientare
- Adancime
- Caracteristicile umpluturii
- Conditia la momentul sapaturii

### Interpretare

**Camp**: `textEdit_interpretazione`
**Baza de date**: `interpretazione_taf`

Interpretarea istorico-arheologica a inmormantarii.

---

## Caracteristicile Mormantului

### Semnale Funerare

**Camp**: `comboBox_segnacoli`
**Baza de date**: `segnacoli`

Prezenta si tipul semnalelor funerare.

**Valori:**
- Absent
- Stela
- Cipus
- Tumul
- Incinta
- Altele

### Canal de Libatie

**Camp**: `comboBox_canale_libatorio`
**Baza de date**: `canale_libatorio_si_no`

Prezenta canalului pentru libatii rituale.

**Valori:** Da / Nu

### Acoperire

**Camp**: `comboBox_copertura_tipo`
**Baza de date**: `copertura_tipo`

Tipul de acoperire a mormantului.

**Exemple:**
- Tigle
- Lespezi de piatra
- Scanduri de lemn
- Pamant
- Absenta

### Container pentru Ramasite

**Camp**: `comboBox_tipo_contenitore`
**Baza de date**: `tipo_contenitore_resti`

Tipul containerului pentru ramasite.

**Exemple:**
- Groapa in pamant
- Cutie de lemn
- Cutie de piatra
- Amfora
- Urna
- Sarcofag

### Obiecte Exterioare

**Camp**: `comboBox_oggetti_esterno`
**Baza de date**: `oggetti_rinvenuti_esterno`

Obiecte gasite in afara mormantului dar asociate cu acesta.

---

## Fila Inventar Funerar

Aceasta fila gestioneaza documentarea inventarului funerar.

![Fila Inventar Funerar](images/06_scheda_tomba/08_tab_corredo.png)

### Prezenta Inventarului Funerar

**Camp**: `comboBox_corredo_presenza`
**Baza de date**: `corredo_presenza`

Indica daca mormantul contine inventar funerar.

**Valori:**
- Da
- Nu
- Probabil
- Inlaturat

### Tipul Inventarului Funerar

**Camp**: `comboBox_corredo_tipo`
**Baza de date**: `corredo_tipo`

Clasificarea generala a inventarului funerar.

**Categorii:**
- Personal (bijuterii, fibule)
- Ritual (vase, lampi)
- Simbolic (monede, amulete)
- Instrumental (unelte)
- Mixt

### Descrierea Inventarului Funerar

**Camp**: `textEdit_corredo_descrizione`
**Baza de date**: `corredo_descrizione`

Descrierea detaliata a obiectelor din inventarul funerar.

### Tabelul Inventarului Funerar

**Widget**: `tableWidget_corredo_tipo`

Tabel pentru inregistrarea elementelor individuale ale inventarului funerar.

**Coloane:**
| Coloana | Descriere |
|---------|-----------|
| ID Descoperire | Numarul de inventar al descoperirii |
| ID Indiv. | Individul asociat |
| Material | Tipul materialului |
| Pozitia in mormant | Unde a fost localizat in mormant |
| Pozitia fata de corp | Pozitia relativa la corp |

**Note:**
- Elementele sunt legate de Fisa Inventar Materiale
- Tabelul este populat automat cu descoperirile din structura

---

## Fila Alte Caracteristici

Aceasta fila contine informatii suplimentare despre inmormantare.

![Fila Alte Caracteristici](images/06_scheda_tomba/09_tab_altre.png)

### Periodizare

| Camp | Baza de date | Descriere |
|------|--------------|-----------|
| Perioada initiala | `periodo_iniziale` | Perioada de inceput a utilizarii |
| Faza initiala | `fase_iniziale` | Faza in cadrul perioadei |
| Perioada finala | `periodo_finale` | Perioada de sfarsit a utilizarii |
| Faza finala | `fase_finale` | Faza in cadrul perioadei |
| Datare extinsa | `datazione_estesa` | Datare literala |

Valorile sunt populate pe baza Fisei de Periodizare pentru santier.

---

## Fila Instrumente

Fila Instrumente contine functionalitati suplimentare.

![Fila Instrumente](images/06_scheda_tomba/10_tab_tools.png)

### Gestionare Media

Va permite sa:
- Vizualizati imaginile asociate
- Adaugati fotografii noi prin tragere si plasare
- Cautati medii in baza de date

### Export

Optiuni de export:
- Lista Mormintelor (lista sintetica)
- Fise Mormant (fise complete)
- Conversie PDF in Word

---

## Integrare GIS

### Vizualizare pe Harta

| Buton | Functie |
|-------|---------|
| Comutator GIS | Activare/dezactivare incarcare automata |
| Incarca in GIS | Incarca mormantul pe harta |

### Straturi GIS

Fisa foloseste straturi specifice pentru morminte:
- **pyarchinit_tomba**: geometria mormantului
- Legatura cu straturile de structura si US

---

## Export si Tiparire

### Export PDF

Butonul PDF deschide un panou cu optiuni:

| Optiune | Descriere |
|---------|-----------|
| Lista Mormintelor | Lista sintetica a mormintelor |
| Fise Mormant | Fise complete detaliate |
| Tiparire | Genereaza PDF |

### Continutul Fisei PDF

Fisa PDF include:
- Date de identificare
- Rit si tip de inmormantare
- Descriere si interpretare
- Date inventar funerar
- Periodizare
- Imagini asociate

---

## Flux de Lucru Operational

### Crearea unui Mormant Nou

1. **Deschideti fisa**
   - Din meniu sau bara de instrumente

2. **Inregistrare noua**
   - Faceti clic pe "Inregistrare Noua"
   - Numarul fisei este propus automat

3. **Date de identificare**
   ```
   Santier: Necropola Isola Sacra
   Zona: 1
   Nr. Fisa: 45
   Cod structura: TM
   Nr. structura: 45
   ```

4. **Legatura cu individul**
   ```
   Nr. Individ: 1
   ```

5. **Date descriptive** (Fila 1)
   ```
   Rit: Inhumare
   Tip inmormantare: Mormant simplu in groapa
   Tip depunere: Primara
   Stare conservare: Buna

   Descriere: Groapa dreptunghiulara cu
   colturi rotunjite, orientata E-V...

   Semnale: Cipus
   Acoperire: Tigle alla cappuccina
   ```

6. **Inventar funerar** (Fila 2)
   ```
   Prezenta: Da
   Tip: Personal
   Descriere: Fibula de bronz langa
   umarul drept, moneda langa gura...
   ```

7. **Periodizare**
   ```
   Perioada initiala: II - Faza A
   Perioada finala: II - Faza A
   Datare: Secolul al II-lea d.Hr.
   ```

8. **Salvare**
   - Faceti clic pe "Salvare"

### Cautarea Mormintelor

1. Faceti clic pe "Cautare Noua"
2. Completati criteriile:
   - Santier
   - Rit
   - Tip inmormantare
   - Perioada
3. Faceti clic pe "Cautare"
4. Navigati prin rezultate

---

## Relatii cu Alte Fise

| Fisa | Relatie |
|------|---------|
| **Fisa Santier** | Santierul contine morminte |
| **Fisa Structura** | Structura fizica a mormantului |
| **Fisa Individ** | Ramasitele umane din mormant |
| **Fisa Inventar Materiale** | Descoperirile din inventarul funerar |
| **Fisa de Periodizare** | Cronologia |

### Flux de Lucru Recomandat

1. Creati **Fisa Santier** (daca nu exista)
2. Creati **Fisa Structura** pentru mormant
3. Creati **Fisa Mormant** legand-o de structura
4. Creati **Fisa Individ** pentru fiecare individ
5. Inregistrati inventarul funerar in **Fisa Inventar Materiale**

---

## Bune Practici

### Denumire

- Folositi coduri consistente (TM, TB, SEP)
- Numerotare progresiva in cadrul santierului
- Documentati conventiile adoptate

### Descriere

- Descrieti sistematic forma, dimensiunile, orientarea
- Documentati conditia la momentul sapaturii
- Separati observatiile obiective de interpretari

### Inventar Funerar

- Inregistrati pozitia exacta a fiecarui obiect
- Legati fiecare element de Inventarul Materiale
- Documentati asocierile semnificative

### Periodizare

- Bazati datarea pe elemente de diagnostic
- Indicati nivelul de fiabilitate
- Comparati cu inmormantari similare

---

## Depanare

### Problema: Individul nu este disponibil in meniu

**Cauza**: Individul nu a fost inca creat sau nu este asociat cu structura.

**Solutie**:
1. Verificati ca Fisa Individ exista
2. Verificati ca individul este asociat cu aceeasi structura

### Problema: Inventarul funerar nu se afiseaza in tabel

**Cauza**: Descoperirile nu sunt legate de structura.

**Solutie**:
1. Deschideti Fisa Inventar Materiale
2. Verificati ca descoperirile au structura corecta
3. Reimprospatati Fisa Mormant

### Problema: Mormantul nu este vizibil pe harta

**Cauza**: Geometria nu este asociata.

**Solutie**:
1. Verificati ca stratul mormantului exista
2. Verificati ca structura are geometrie
3. Verificati sistemul de referinta a coordonatelor

---

## Referinte

### Baza de Date

- **Tabel**: `tomba_table`
- **Clasa mapper**: `TOMBA`
- **ID**: `id_tomba`

### Fisiere Sursa

- **UI**: `gui/ui/Tomba.ui`
- **Controller**: `tabs/Tomba.py`
- **Export PDF**: `modules/utility/pyarchinit_exp_Tombasheet_pdf.py`

---

## Tutorial Video

### Prezentare Generala Fisa Mormant
**Durata**: 5-6 minute
- Prezentarea interfetei
- Campuri principale
- Navigarea intre file

[Substituent video: video_panoramica_tomba.mp4]

### Documentarea Completa a Mormantului
**Durata**: 10-12 minute
- Crearea unei inregistrari noi
- Completarea tuturor campurilor
- Legarea individului si inventarului funerar

[Substituent video: video_schedatura_tomba.mp4]

### Gestionarea Inventarului Funerar
**Durata**: 6-8 minute
- Inregistrarea elementelor inventarului funerar
- Legatura cu Inventarul Materiale
- Documentarea pozitiei

[Substituent video: video_corredo_tomba.mp4]

---

*Ultima actualizare: Ianuarie 2026*
*PyArchInit - Sistem de Gestionare a Datelor Arheologice*
