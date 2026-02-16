# Tutorial 07: Fisa Individ

## Introducere

**Fisa Individ** este modulul PyArchInit dedicat documentatiei antropologice a ramasitelor umane descoperite in timpul sapaturii. Aceasta fisa inregistreaza informatii despre sex, varsta, pozitia corpului si starea de conservare a scheletului.

### Concepte de Baza

**Individ in PyArchInit:**
- Un individ este un ansamblu de ramasite osoase atribuibile unei singure persoane
- Este legat de Fisa Mormant (contextul funerar)
- Este legat de Fisa Structura (structura fizica)
- Poate fi legat de Arheozoologie pentru analize specifice

**Date Antropologice:**
- Estimarea sexului biologic
- Estimarea varstei la deces
- Pozitia si orientarea corpului
- Starea de conservare si gradul de completitudine

---

## Accesarea Fisei

### Din Meniu
1. Meniu **PyArchInit** din bara de meniu QGIS
2. Selectati **Fisa Individ**

![Acces din meniu](images/07_scheda_individui/02_menu_accesso.png)

### Din Bara de Instrumente
1. Localizati bara de instrumente PyArchInit
2. Faceti clic pe pictograma **Individ** (figura umana)

![Acces din bara](images/07_scheda_individui/03_toolbar_accesso.png)

---

## Vedere Generala a Interfetei

Fisa prezinta o structura organizata in sectiuni functionale:

![Interfata completa](images/07_scheda_individui/04_interfaccia_completa.png)

### Zone Principale

| # | Zona | Descriere |
|---|------|-----------|
| 1 | Bara DBMS | Navigare, cautare, salvare |
| 2 | Info BD | Starea inregistrarii, sortare, contor |
| 3 | Campuri de Identificare | Santier, Zona, US, Nr. Individ |
| 4 | Legatura Structura | Cod si numar structura |
| 5 | Zona de File | File tematice pentru date specifice |

---

## Bara de Instrumente DBMS

Bara principala ofera instrumente pentru gestionarea inregistrarilor.

![Bara DBMS](images/07_scheda_individui/05_toolbar_dbms.png)

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
| ![Nou](../../resources/icons/newrec.png) | Inregistrare noua | Creeaza o inregistrare noua de individ |
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
| ![PDF](../../resources/icons/pdf-icon.png) | Export PDF | Exporta in PDF |
| ![Director](../../resources/icons/directoryExp.png) | Deschide director | Deschide dosarul de export |

---

## Campuri de Identificare

Campurile de identificare definesc in mod unic individul in baza de date.

![Campuri de identificare](images/07_scheda_individui/06_campi_identificativi.png)

### Santier

**Camp**: `comboBox_sito`
**Baza de date**: `sito`

Selectati santierul arheologic de apartenenta.

### Zona

**Camp**: `comboBox_area`
**Baza de date**: `area`

Zona de sapatura din cadrul santierului. Valorile sunt populate din tezaur.

### US

**Camp**: `comboBox_us`
**Baza de date**: `us`

Unitatea Stratigrafica de referinta.

### Numarul Individului

**Camp**: `lineEdit_individuo`
**Baza de date**: `nr_individuo`

Numarul progresiv al individului. Urmatorul numar disponibil este propus automat.

**Note:**
- Combinatia Santier + Zona + US + Nr. Individ trebuie sa fie unica
- Numarul este atribuit automat la creare

### Legatura cu Structura

| Camp | Baza de date | Descriere |
|------|--------------|-----------|
| Cod structura | `sigla_struttura` | Codul structurii (de ex., TM) |
| Nr. structura | `nr_struttura` | Numarul structurii |

Aceste campuri leaga individul de structura funerara.

---

## Date de Catalogare

![Date de catalogare](images/07_scheda_individui/07_dati_schedatura.png)

### Data Catalogarii

**Camp**: `dateEdit_schedatura`
**Baza de date**: `data_schedatura`

Data compilarii fisei.

### Catalogator

**Camp**: `comboBox_schedatore`
**Baza de date**: `schedatore`

Numele operatorului care compileaza fisa.

---

## Fila Date Descriptive

Prima fila contine datele antropologice fundamentale.

![Fila Date Descriptive](images/07_scheda_individui/08_tab_descrittivi.png)

### Estimarea Sexului

**Camp**: `comboBox_sesso`
**Baza de date**: `sesso`

Estimarea sexului biologic pe baza caracterelor morfologice.

**Valori:**
| Valoare | Descriere |
|---------|-----------|
| Masculin | Caractere masculine clare |
| Feminin | Caractere feminine clare |
| Probabil masculin | Caractere predominant masculine |
| Probabil feminin | Caractere predominant feminine |
| Nedeterminat | Nu se poate determina |

**Criterii de determinare:**
- Morfologia bazinului
- Morfologia craniului
- Robustetea generala a scheletului
- Dimensiunile osoase

### Estimarea Varstei la Deces

| Camp | Baza de date | Descriere |
|------|--------------|-----------|
| Varsta minima | `eta_min` | Limita inferioara a estimarii |
| Varsta maxima | `eta_max` | Limita superioara a estimarii |

**Metode de estimare:**
- Simfiza pubiana
- Suprafata auriculara
- Suturi craniene
- Dezvoltare dentara (pentru subadulti)
- Epifize osoase (pentru subadulti)

### Clase de Varsta

**Camp**: `comboBox_classi_eta`
**Baza de date**: `classi_eta`

Clasificarea pe grupe de varsta.

**Valori tipice:**
| Clasa | Varsta aproximativa |
|-------|---------------------|
| Infans I | 0-6 ani |
| Infans II | 7-12 ani |
| Juvenis | 13-20 ani |
| Adultus | 21-40 ani |
| Maturus | 41-60 ani |
| Senilis | >60 ani |

### Observatii

**Camp**: `textEdit_osservazioni`
**Baza de date**: `osservazioni`

Camp text pentru note antropologice specifice.

**Continut recomandat:**
- Patologii observate
- Traumatisme
- Markeri ocupationali
- Anomalii scheletice
- Note privind determinarea sexului si varstei

---

## Fila Orientare si Pozitie

Aceasta fila documenteaza pozitia si orientarea corpului.

![Fila Orientare](images/07_scheda_individui/09_tab_orientamento.png)

### Stare de Conservare

| Camp | Baza de date | Valori |
|------|--------------|--------|
| Complet | `completo_si_no` | Da / Nu |
| Deranjat | `disturbato_si_no` | Da / Nu |
| In conexiune | `in_connessione_si_no` | Da / Nu |

**Definitii:**
- **Complet**: toate districtele anatomice sunt reprezentate
- **Deranjat**: dovezi de perturbare post-depositionala
- **In conexiune**: articulatiile sunt pastrate

### Lungimea Scheletului

**Camp**: `lineEdit_lunghezza`
**Baza de date**: `lunghezza_scheletro`

Lungimea scheletului masurata in situ (in cm sau m).

### Pozitia Scheletului

**Camp**: `comboBox_posizione_scheletro`
**Baza de date**: `posizione_scheletro`

Pozitia generala a corpului.

**Valori:**
- Supina (pe spate)
- Prona (cu fata in jos)
- Lateral drept
- Lateral stang
- Chircit
- Neregulata

### Pozitia Craniului

**Camp**: `comboBox_posizione_cranio`
**Baza de date**: `posizione_cranio`

Orientarea capului.

**Valori:**
- Cu fata la dreapta
- Cu fata la stanga
- Cu fata in sus
- Cu fata in jos
- Nedeterminabila

### Pozitia Membrelor Superioare

**Camp**: `comboBox_arti_superiori`
**Baza de date**: `posizione_arti_superiori`

Pozitia bratelor.

**Valori:**
- Intinse de-a lungul corpului
- Pe bazin
- Pe piept
- Incrucisate pe piept
- Mixta
- Nedeterminabila

### Pozitia Membrelor Inferioare

**Camp**: `comboBox_arti_inferiori`
**Baza de date**: `posizione_arti_inferiori`

Pozitia picioarelor.

**Valori:**
- Intinse
- Indoite
- Incrucisate
- Desfacute
- Nedeterminabila

### Orientarea Axei

**Camp**: `comboBox_orientamento_asse`
**Baza de date**: `orientamento_asse`

Orientarea axei longitudinale a corpului.

**Valori:**
- N-S (capul la Nord)
- S-N (capul la Sud)
- E-V (capul la Est)
- V-E (capul la Vest)
- NE-SV, NV-SE etc.

### Orientare Azimut

**Camp**: `lineEdit_azimut`
**Baza de date**: `orientamento_azimut`

Valoarea numerica a azimutului in grade (0-360).

---

## Fila Ramasite Osteologice

Aceasta fila este dedicata documentarii districtelor anatomice.

![Fila Ramasite Osteologice](images/07_scheda_individui/10_tab_osteologici.png)

### Documentarea Districtelor

Permite inregistrarea:
- Prezenta/absenta elementelor osoase individuale
- Starea de conservare pe district
- Lateralitatea (dreapta/stanga) pentru elementele perechi

**Districte principale:**
| District | Elemente |
|----------|----------|
| Craniu | Calvaria, mandibula, dinti |
| Coloana vertebrala | Vertebre cervicale, toracice, lombare, sacrum |
| Torace | Coaste, stern |
| Membre superioare | Clavicule, scapule, humeri, radius, ulna, maini |
| Bazin | Coxale |
| Membre inferioare | Femure, tibie, peronee, picioare |

---

## Fila Alte Caracteristici

Aceasta fila contine informatii suplimentare.

![Fila Alte Caracteristici](images/07_scheda_individui/11_tab_altre.png)

### Continut

- Caracteristici metrice specifice
- Indici antropometrici
- Patologii detaliate
- Relatii cu alti indivizi

---

## Export si Tiparire

### Export PDF

Butonul PDF deschide un panou cu optiuni:

| Optiune | Descriere |
|---------|-----------|
| Lista Indivizilor | Lista sintetica |
| Fise Individ | Fise complete detaliate |
| Tiparire | Genereaza PDF |

### Continutul Fisei PDF

Fisa PDF include:
- Date de identificare
- Date antropologice (sex, varsta)
- Pozitie si orientare
- Stare de conservare
- Observatii

---

## Flux de Lucru Operational

### Crearea unui Individ Nou

1. **Deschideti fisa**
   - Din meniu sau bara de instrumente

2. **Inregistrare noua**
   - Faceti clic pe "Inregistrare Noua"
   - Numarul individului este propus automat

3. **Date de identificare**
   ```
   Santier: Necropola Isola Sacra
   Zona: 1
   US: 150
   Nr. Individ: 1
   Cod structura: TM
   Nr. structura: 45
   ```

4. **Date de catalogare**
   ```
   Data: 15/03/2024
   Catalogator: M. Rossi
   ```

5. **Date antropologice** (Fila 1)
   ```
   Sex: Masculin
   Varsta min.: 35
   Varsta max.: 45
   Clasa de varsta: Adultus

   Observatii: Statura estimata 170 cm.
   Artroza lombara. Carii multiple.
   ```

6. **Orientare si Pozitie** (Fila 2)
   ```
   Complet: Da
   Deranjat: Nu
   In conexiune: Da
   Lungime: 165 cm
   Pozitie: Supina
   Craniu: Cu fata la dreapta
   Membre superioare: Intinse de-a lungul corpului
   Membre inferioare: Intinse
   Orientare: E-V
   Azimut: 90
   ```

7. **Ramasite osteologice** (Fila 3)
   - Documentati districtele prezente

8. **Salvare**
   - Faceti clic pe "Salvare"

### Cautarea Indivizilor

1. Faceti clic pe "Cautare Noua"
2. Completati criteriile:
   - Santier
   - Sex
   - Clasa de varsta
   - Pozitie
3. Faceti clic pe "Cautare"
4. Navigati prin rezultate

---

## Relatii cu Alte Fise

| Fisa | Relatie |
|------|---------|
| **Fisa Santier** | Santierul contine indivizi |
| **Fisa Structura** | Structura contine individul |
| **Fisa Mormant** | Mormantul documenteaza contextul |
| **Arheozoologie** | Pentru analize osteologice specifice |

### Flux de Lucru Recomandat

1. Creati **Fisa Structura** pentru mormant
2. Creati **Fisa Mormant**
3. Creati **Fisa Individ** pentru fiecare schelet
4. Legati individul de mormant si structura

---

## Bune Practici

### Determinarea Sexului

- Folositi indicatori morfologici multipli
- Indicati nivelul de fiabilitate
- Specificati criteriile utilizate in observatii

### Estimarea Varstei

- Furnizati intotdeauna un interval (min-max)
- Indicati metodele utilizate
- Pentru subadulti, specificati dezvoltarea dentara si epifizara

### Pozitie si Orientare

- Documentati cu fotografii inainte de ridicare
- Folositi referinte cardinale
- Masurati azimutul cu busola

### Conservare

- Distingetei pierderile tafonomice de inlaturarile antice
- Documentati perturbatiile post-depositionare
- Inregistrati conditiile de recuperare

---

## Depanare

### Problema: Numar de individ duplicat

**Cauza**: Exista deja un individ cu acelasi numar.

**Solutie**:
1. Verificati numerotarea existenta
2. Folositi numarul propus automat
3. Verificati zona si US-ul

### Problema: Structura nu este gasita

**Cauza**: Structura nu exista sau are un cod diferit.

**Solutie**:
1. Verificati ca Fisa Structura exista
2. Verificati codul si numarul
3. Creati structura mai intai daca este necesar

### Problema: Clasele de varsta nu sunt disponibile

**Cauza**: Tezaurul nu este configurat.

**Solutie**:
1. Verificati configurarea tezaurului
2. Verificati setarea limbii
3. Contactati administratorul

---

## Referinte

### Baza de Date

- **Tabel**: `individui_table`
- **Clasa mapper**: `SCHEDAIND`
- **ID**: `id_scheda_ind`

### Fisiere Sursa

- **UI**: `gui/ui/Schedaind.ui`
- **Controller**: `tabs/Schedaind.py`
- **Export PDF**: `modules/utility/pyarchinit_exp_Individui_pdf.py`

---

## Tutorial Video

### Prezentare Generala Fisa Individ
**Durata**: 5-6 minute
- Prezentarea interfetei
- Campuri principale
- Navigarea intre file

[Substituent video: video_panoramica_individui.mp4]

### Documentatie Antropologica Completa
**Durata**: 12-15 minute
- Crearea unei inregistrari noi
- Determinarea sexului si varstei
- Documentarea pozitiei
- Inregistrarea ramasitelor osteologice

[Substituent video: video_schedatura_individui.mp4]

### Legatura Mormant-Individ
**Durata**: 5-6 minute
- Relatiile intre fise
- Flux de lucru corect
- Bune practici

[Substituent video: video_collegamento_tomba_individuo.mp4]

---

*Ultima actualizare: Ianuarie 2026*
*PyArchInit - Sistem de Gestionare a Datelor Arheologice*
