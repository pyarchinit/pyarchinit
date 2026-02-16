# PyArchInit - Fisa US/USM (Unitate Stratigrafica)

## Cuprins
1. [Introducere](#introducere)
2. [Concepte Fundamentale](#concepte-fundamentale)
3. [Accesarea Fisei](#accesarea-fisei)
4. [Interfata Generala](#interfata-generala)
5. [Campuri de Identificare](#campuri-de-identificare)
6. [Fila Localizare](#fila-localizare)
7. [Fila Date Descriptive](#fila-date-descriptive)
8. [Fila Periodizare](#fila-periodizare)
9. [Fila Relatii Stratigrafice](#fila-relatii-stratigrafice)
10. [Fila Date Fizice](#fila-date-fizice)
11. [Fila Date de Catalogare](#fila-date-de-catalogare)
12. [Fila Masuratori US](#fila-masuratori-us)
13. [Fila Documentatie](#fila-documentatie)
14. [Fila Tehnica Constructiva USM](#fila-tehnica-constructiva-usm)
15. [Fila Lianti USM](#fila-lianti-usm)
16. [Fila Media](#fila-media)
17. [Fila Ajutor - Instrumente](#fila-ajutor---instrumente)
18. [Harris Matrix](#harris-matrix)
19. [Functionalitati GIS](#functionalitati-gis)
20. [Exporturi](#exporturi)
21. [Flux de Lucru Operational](#flux-de-lucru-operational)
22. [Depanare](#depanare)

---

## Introducere

**Fisa US/USM** (Unitate Stratigrafica / Unitate Stratigrafica Murala) este inima documentatiei arheologice in PyArchInit. Reprezinta instrumentul principal pentru inregistrarea tuturor informatiilor legate de unitatile stratigrafice identificate in timpul sapaturii.

Aceasta fisa implementeaza principiile **metodei stratigrafice** dezvoltate de Edward C. Harris, permitand documentarea:
- Caracteristicilor fizice ale fiecarui strat
- Relatiilor stratigrafice intre unitati
- Cronologiei relative si absolute
- Documentatiei grafice si fotografice asociate

<!-- VIDEO: Introducere in Fisa US -->
> **Tutorial Video**: [Inserati link video pentru introducerea in fisa US]

---

## Concepte Fundamentale

### Ce este o Unitate Stratigrafica (US)

O **Unitate Stratigrafica** este cea mai mica unitate de sapatura care poate fi identificata si distinsa de celelalte. Poate fi:
- **Strat**: depozit de pamant cu caracteristici omogene
- **Interfata**: suprafata de contact intre straturi (de ex., taietura unei gropi)
- **Element structural**: parte a unei constructii

### Tipuri de Unitati

| Tip | Cod | Descriere |
|-----|-----|-----------|
| US | Unitate Stratigrafica | Strat generic |
| USZ | Unitate Stratigrafica de Zidarie | Element de constructie de zidarie |
| USVA | Unita Stratigrafica Verticale A | Alzato verticale tipo A |
| USVB | Unita Stratigrafica Verticale B | Alzato verticale tipo B |
| USVC | Unita Stratigrafica Verticale C | Alzato verticale tipo C |
| USD | Unita Stratigrafica di Demolizione | Strato di crollo/demolizione |
| CON | Conci | Blocchi architettonici |
| VSF | Virtual Stratigraphic Feature | Elemento virtuale |
| SF | Stratigraphic Feature | Feature stratigrafica |
| SUS | Sub-Unita Stratigrafica | Suddivisione di US |
| DOC | Documentazione | Elemento documentario |

### Relatii Stratigrafice

Relatiile stratigrafice definesc relatiile temporale intre US-uri:

| Relatie | Inversa | Semnificatie |
|---------|---------|--------------|
| **Acopera** | Acoperit de | US-ul se suprapune fizic |
| **Taie** | Taiat de | US-ul intrerupe/traverseaza |
| **Umple** | Umplut de | US-ul umple o cavitate |
| **Se sprijina pe** | Este sprijinit de | Relatie de sprijin |

<!-- IMAGINE: Diagrama relatiilor stratigrafice -->
![Relatii Stratigrafice](images/03_scheda_us/01_schema_rapporti.png)
*Figura 1: Diagrama relatiilor stratigrafice*

---

## Accesarea Fisei

Pentru a accesa Fisa US:

1. Meniu **PyArchInit** → **Gestionare inregistrari arheologice** → **US/USM**
2. Sau din bara de instrumente PyArchInit, faceti clic pe pictograma **US/USM**

<!-- IMAGINE: Captură de ecran a meniului de acces -->
![Acces Fisa US](images/03_scheda_us/02_menu_scheda_us.png)
*Figura 2: Accesarea Fisei US din meniu*

<!-- IMAGINE: Captură de ecran a barei de instrumente -->
![Bara US](images/03_scheda_us/03_toolbar_us.png)
*Figura 3: Pictograma Fisei US in bara de instrumente*

---

## Interfata Generala

Fisa US este organizata in mai multe zone functionale:

<!-- IMAGINE: Captură de ecran a interfetei complete cu zone numerotate -->
![Interfata US](images/03_scheda_us/04_interfaccia_completa.png)
*Figura 4: Interfata completa a Fisei US*

### Zone Principale

| # | Zona | Descriere |
|---|------|-----------|
| 1 | **Campuri de Identificare** | Santier, Zona, US, Tip, Definitii |
| 2 | **Bara de Instrumente DBMS** | Navigare, salvare, cautare |
| 3 | **File de Date** | File tematice pentru date |
| 4 | **Bara de Instrumente GIS** | Instrumente de afisare pe harta |
| 5 | **Fila Instrumente** | Instrumente avansate si Matrix |

### Bara de Instrumente DBMS

Bara de instrumente DBMS este identica cu cea a Fisei Santier cu cateva functionalitati suplimentare:

<!-- IMAGINE: Captură de ecran a barei DBMS US -->
![Bara DBMS](images/03_scheda_us/05_toolbar_dbms.png)
*Figura 5: Bara de Instrumente DBMS a Fisei US*

| Buton | Functie | Descriere |
|-------|---------|-----------|
| **Inregistrare noua** | Nou | Creeaza o fisa US noua |
| **Salvare** | Salvare | Salveaza modificarile |
| **Stergere** | Stergere | Sterge fisa curenta |
| **Vizualizare toate** | Vizualizare toate | Afiseaza toate inregistrarile |
| **Prima/Anterioara/Urmatoarea/Ultima** | Navigare | Navigare intre inregistrari |
| **cautare noua** | Cautare | Porneste modul de cautare |
| **cauta !!!** | Executare | Executa cautarea |
| **Ordoneaza dupa** | Sortare | Sorteaza inregistrarile |
| **Raport** | Tiparire | Genereaza raport PDF |
| **Lista US/Foto** | Lista | Genereaza liste |

---

## Campuri de Identificare

Campurile de identificare sunt intotdeauna vizibile in partea superioara a fisei.

<!-- IMAGINE: Captură de ecran a campurilor de identificare -->
![Campuri de Identificare](images/03_scheda_us/06_campi_identificativi.png)
*Figura 6: Campuri de identificare*

### Campuri Obligatorii

| Camp | Descriere | Format |
|------|-----------|--------|
| **Santier** | Numele santierului arheologic | Text (din combobox) |
| **Zona** | Numarul zonei de sapatura | Intreg (1-20) |
| **US/USM** | Numarul unitatii stratigrafice | Intreg |
| **Tip unitate** | Tipul unitatii (US, USM etc.) | Selectie |

### Campuri Descriptive

| Camp | Descriere |
|------|-----------|
| **Definitie stratigrafica** | Clasificarea stratigrafica (din tezaur) |
| **Definitie interpretativa** | Interpretarea functionala (din tezaur) |

### Definitii Stratigrafice (Exemple)

| Definitie | Descriere |
|-----------|-----------|
| Strat | Depozit generic |
| Umplutura | Material de umplere |
| Taietura | Interfata negativa |
| Suprafata de circulatie | Suprafata de mers |
| Prabusire | Material de prabusire |
| Pamant batut | Pardoseala din pamant batut |

### Definitii Interpretative (Exemple)

| Definitie | Descriere |
|-----------|-----------|
| Activitate de constructie | Faza de constructie |
| Abandonare | Faza de abandonare |
| Pardoseala | Suprafata de podea |
| Zid | Structura de zid |
| Groapa | Sapatura intentionata |
| Nivelare | Strat de pregatire |

---

## Fila Localizare

Contine date de pozitionare in cadrul sapaturii.

<!-- IMAGINE: Captură de ecran a filei localizare -->
![Fila Localizare](images/03_scheda_us/07_tab_localizzazione.png)
*Figura 7: Fila Localizare*

### Campuri de Localizare

| Camp | Descriere | Note |
|------|-----------|------|
| **Sector** | Sectorul de sapatura | Litere A-H sau numere 1-20 |
| **Careu/Zid** | Referinta spatiala | Pentru sapaturi cu grila |
| **Incapere** | Numarul incaperii | Pentru cladiri/structuri |
| **Sondaj** | Numarul sondajului | Pentru sondaje de testare |

### Numere de Catalog

| Camp | Descriere |
|------|-----------|
| **Nr. Cat. General** | Numarul de catalog general |
| **Nr. Cat. Intern** | Numarul de catalog intern |
| **Nr. Cat. International** | Codul international |

---

## Fila Date Descriptive

Contine descrierea textuala a unitatii stratigrafice.

<!-- IMAGINE: Captură de ecran a filei date descriptive -->
![Fila Date Descriptive](images/03_scheda_us/08_tab_dati_descrittivi.png)
*Figura 8: Fila Date Descriptive*

### Campuri Descriptive

| Camp | Descriere | Sugestii |
|------|-----------|----------|
| **Descriere** | Descrierea fizica a US-ului | Culoare, consistenta, compozitie, limite |
| **Interpretare** | Interpretarea functionala | Functie, formare, semnificatie |
| **Elemente de datare** | Materiale pentru datare | Ceramica, monede, obiecte de datare |
| **Observatii** | Note suplimentare | Dubii, ipoteze, comparatii |

### Cum se Descrie o US

**Descriere fizica:**
```
Strat de sol argilos, culoare maro inchis (10YR 3/3),
consistenta compacta, cu incluziuni de fragmente de caramida (2-5 cm),
pietre calcaroase (1-3 cm) si carbune. Limite clare deasupra,
difuze dedesubt. Grosime variabila 15-25 cm.
```

**Interpretare:**
```
Strat de abandonare format in urma incetarii
activitatilor din incapere. Prezenta materialului de constructie
fragmentat sugereaza prabusirea partiala a structurilor.
```

---

## Fila Periodizare

Gestioneaza cronologia unitatii stratigrafice.

<!-- IMAGINE: Captură de ecran a filei periodizare -->
![Fila Periodizare](images/03_scheda_us/09_tab_periodizzazione.png)
*Figura 9: Fila Periodizare*

### Periodizare Relativa

| Camp | Descriere |
|------|-----------|
| **Perioada Initiala** | Perioada de formare |
| **Faza Initiala** | Faza de formare |
| **Perioada Finala** | Perioada de acoperire |
| **Faza Finala** | Faza de acoperire |

**Nota**: Perioadele si fazele trebuie mai intai create in **Fisa de Periodizare**.

### Cronologie Absoluta

| Camp | Descriere |
|------|-----------|
| **Datare** | Data absoluta sau interval |
| **An** | Anul sapaturii |

### Alte Campuri

| Camp | Descriere | Valori |
|------|-----------|--------|
| **Activitate** | Tipul activitatii | Text liber |
| **Structura** | Codul structurii asociate | Din Fisa Structura |
| **Sapata** | Starea sapaturii | Da / Nu |
| **Metoda de sapatura** | Modul de sapatura | Mecanica / Stratigrafica |

### Campul Structura - Legatura cu Fisa Structura

Campul **Structura** va permite sa asociati una sau mai multe structuri cu unitatea stratigrafica curenta. Este un camp cu selectie multipla (casete de bifare).

#### Cum functioneaza sincronizarea

1. **Mai intai** creati structurile in **Fisa Structura**
2. In Fisa Structura completati: **Santier** (acelasi cu US), **Cod** (de ex., "MUR"), **Numar** (de ex., 1)
3. In Fisa US, campul Structura va afisa structurile disponibile in format `COD-NUMAR`

#### Selectarea structurilor

1. Faceti clic pe campul **Structura** pentru a deschide meniul derulant
2. Bifati casutele structurilor de asociat
3. Puteti selecta **mai multe structuri** simultan
4. Salvati inregistrarea

#### Eliminarea unei singure structuri

1. Faceti clic pe campul **Structura** pentru a deschide meniul derulant
2. **Debifati** casuta structurii de eliminat
3. Salvati inregistrarea

#### Eliminarea tuturor structurilor (Golire camp)

1. **Clic dreapta** pe campul Structura
2. Selectati "**Golire camp Structura**" din meniul contextual
3. Salvati inregistrarea pentru a confirma modificarea

> **Nota**: Functia "Golire camp" elimina TOATE structurile asociate. Pentru a elimina doar una, folositi casutele de bifare.

---

## Fila Relatii Stratigrafice

**Aceasta este cea mai importanta fila din fisa US.** Defineste relatiile stratigrafice cu alte unitati.

<!-- IMAGINE: Captură de ecran a filei relatii stratigrafice -->
![Fila Relatii](images/03_scheda_us/10_tab_rapporti.png)
*Figura 10: Fila Relatii Stratigrafice*

<!-- VIDEO: Cum se introduc relatiile stratigrafice -->
> **Tutorial Video**: [Inserati link video pentru relatii stratigrafice]

### Structura Tabelului de Relatii

| Coloana | Descriere |
|---------|-----------|
| **Santier** | Santierul US-ului asociat |
| **Zona** | Zona US-ului asociat |
| **US** | Numarul US-ului asociat |
| **Tip relatie** | Tipul relatiei |

### Tipuri de Relatii Disponibile

| Italiana | Engleza | Germana |
|----------|---------|---------|
| Copre | Covers | Liegt uber |
| Coperto da | Covered by | Liegt unter |
| Taglia | Cuts | Schneidet |
| Tagliato da | Cut by | Geschnitten von |
| Riempie | Fills | Verfullt |
| Riempito da | Filled by | Verfullt von |
| Si appoggia a | Abuts | Stutzt sich auf |
| Gli si appoggia | Supports | Wird gestutzt von |
| Uguale a (=) | Same as | Gleich |
| Anteriore (>>) | Earlier | Fruher |
| Posteriore (<<) | Later | Spater |

### Introducerea Relatiilor

1. Faceti clic pe **+** pentru a adauga un rand
2. Introduceti Santier, Zona, US al US-ului asociat
3. Selectati tipul relatiei
4. Salvati

<!-- IMAGINE: Captură de ecran a introducerii relatiei -->
![Introducere Relatie](images/03_scheda_us/11_inserimento_rapporto.png)
*Figura 11: Introducerea unei relatii stratigrafice*

### Butoane Relatii

| Buton | Functie |
|-------|---------|
| **+** | Adauga rand |
| **-** | Elimina rand |
| **Inserare sau actualizare relatie inversa** | Creeaza automat relatia inversa |
| **Mergi la US** | Navigheaza la US-ul selectat |
| **Afiseaza matrix** | Afiseaza Harris Matrix |
| **Repara** | Repara erorile de relatie |

### Relatii Inverse Automate

Cand introduceti o relatie, puteti crea automat inversa:

| Daca introduceti | Se va crea |
|------------------|------------|
| US 1 **acopera** US 2 | US 2 **acoperit de** US 1 |
| US 1 **taie** US 2 | US 2 **taiat de** US 1 |
| US 1 **umple** US 2 | US 2 **umplut de** US 1 |

### Verificare Relatii

Butonul **Verificare relatii** verifica consistenta relatiilor:
- Detecteaza relatiile lipsa
- Gaseste inconsistentele
- Semnaleaza erorile logice

<!-- IMAGINE: Captură de ecran a verificarii relatiilor -->
![Verificare Relatii](images/03_scheda_us/12_controllo_rapporti.png)
*Figura 12: Rezultatul verificarii relatiilor*

---

## Fila Relatii Extended Matrix

Fila dedicata gestionarii avansate a relatiilor pentru Extended Matrix.

<!-- IMAGINE: Captură de ecran a filei EM -->
![Fila EM](images/03_scheda_us/13_tab_em.png)
*Figura 13: Fila Relatii Extended Matrix*

Aceasta fila permite adaugarea de informatii suplimentare pentru fiecare relatie:
- Tipul unitatii
- Definitia interpretativa
- Periodizarea

---

## Fila Date Fizice

Descrie caracteristicile fizice ale unitatii stratigrafice.

<!-- IMAGINE: Captură de ecran a filei date fizice -->
![Fila Date Fizice](images/03_scheda_us/14_tab_dati_fisici.png)
*Figura 14: Fila Date Fizice*

### Caracteristici Generale

| Camp | Valori |
|------|--------|
| **Culoare** | Maro, Galben, Gri, Negru etc. |
| **Consistenta** | Argiloasa, Compacta, Friabila, Nisipoasa |
| **Formare** | Artificiala, Naturala |
| **Pozitie** | - |
| **Mod de formare** | Aport, Scadere, Acumulare, Alunecare |
| **Criterii de distinctie** | Text liber |

### Tabele de Componente

| Tabel | Continut |
|-------|----------|
| **Comp. organice** | Oase, lemn, carbune, seminte etc. |
| **Comp. anorganice** | Pietre, caramizi, ceramica etc. |
| **Incluziuni artificiale** | Materiale antropice incluse |

Pentru fiecare tabel:
- **+** Adauga rand
- **-** Elimina rand

### Prelevare

| Camp | Valori |
|------|--------|
| **Flotatie** | Da / Nu |
| **Cernere** | Da / Nu |
| **Fiabilitate** | Slaba, Buna, Satisfacatoare, Excelenta |
| **Stare de conservare** | Insuficienta, Slaba, Buna, Satisfacatoare, Excelenta |

---

## Fila Date de Catalogare

Informatii despre compilarea fisei.

<!-- IMAGINE: Captură de ecran a filei date catalogare -->
![Fila Date Catalogare](images/03_scheda_us/15_tab_schedatura.png)
*Figura 15: Fila Date de Catalogare*

### Entitate si Responsabili

| Camp | Descriere |
|------|-----------|
| **Entitatea Responsabila** | Entitatea care gestioneaza sapatura |
| **Superintendenta** | SABAP competenta |
| **Directorul Stiintific** | Directorul sapaturii |
| **Responsabil Compilare** | Cine a compilat fisa de teren |
| **Responsabil Prelucrare** | Cine a prelucrat datele |

### Referinte

| Camp | Descriere |
|------|-----------|
| **Ref. TM** | Referinta fisa TM (Tabel Materiale) |
| **Ref. RA** | Referinta fisa RA (Descoperiri Arheologice) |
| **Ref. Ceramica** | Referinta fisa ceramica |

### Date

| Camp | Format |
|------|--------|
| **Data cercetarii** | ZZ/LL/AAAA |
| **Data catalogarii** | ZZ/LL/AAAA |
| **Data prelucrarii** | ZZ/LL/AAAA |

---

## Fila Masuratori US

Contine toate masuratorile unitatii stratigrafice.

<!-- IMAGINE: Captură de ecran a filei masuratori -->
![Fila Masuratori](images/03_scheda_us/16_tab_misure.png)
*Figura 16: Fila Masuratori US*

### Cote

| Camp | Descriere | Unitate |
|------|-----------|---------|
| **Cota absoluta** | Cota fata de nivelul marii | metri |
| **Cota relativa** | Cota relativa la punctul de referinta | metri |
| **Cota absoluta maxima** | Cota absoluta maxima | metri |
| **Cota relativa maxima** | Cota relativa maxima | metri |
| **Cota absoluta minima** | Cota absoluta minima | metri |
| **Cota relativa minima** | Cota relativa minima | metri |

### Dimensiuni

| Camp | Descriere | Unitate |
|------|-----------|---------|
| **Lungime maxima** | Lungimea maxima | metri |
| **Latime medie** | Latimea medie | metri |
| **Inaltime maxima** | Inaltimea maxima | metri |
| **Inaltime minima** | Inaltimea minima | metri |
| **Grosime** | Grosimea stratului | metri |
| **Adancime maxima** | Adancimea maxima | metri |
| **Adancime minima** | Adancimea minima | metri |

---

## Fila Documentatie

Gestioneaza referintele la documentatia grafica si fotografica.

<!-- IMAGINE: Captură de ecran a filei documentatie -->
![Fila Documentatie](images/03_scheda_us/17_tab_documentazione.png)
*Figura 17: Fila Documentatie*

### Tabelul Documentatiei

| Coloana | Descriere |
|---------|-----------|
| **Tip documentatie** | Foto, Plan, Sectiune, Elevatie etc. |
| **Referinte** | Numarul/codul documentului |

### Tipuri de Documentatie

| Tip | Descriere |
|-----|-----------|
| Foto | Documentatie fotografica |
| Plan | Plan de sapatura |
| Sectiune | Sectiune stratigrafica |
| Elevatie | Elevatie de zid |
| Releveu | Releveu grafic |
| 3D | Model tridimensional |

### Butoane

| Buton | Functie |
|-------|---------|
| **inserare rand** | Adauga referinta |
| **eliminare rand** | Elimina referinta |
| **Actualizare doc** | Actualizeaza din tabelul de documentatie |
| **Vizualizare documentatie** | Afiseaza documentele asociate |

---

## Fila Tehnica Constructiva USM

Fila specifica pentru Unitatile Stratigrafice Murale (USM).

<!-- IMAGINE: Captură de ecran a filei tehnica constructiva -->
![Fila Tehnica Constructiva](images/03_scheda_us/18_tab_tecnica_usm.png)
*Figura 18: Fila Tehnica Constructiva USM*

### Date Specifice USM

| Camp | Descriere |
|------|-----------|
| **Lungime USM** | Lungimea zidului (metri) |
| **Inaltime USM** | Inaltimea zidului (metri) |
| **Suprafata analizata** | Procentul analizat |
| **Sectiunea zidului** | Tipul sectiunii |
| **Modul** | Modulul constructiv |
| **Tipologie lucrare** | Tipul de zidarie |
| **Orientare** | Orientarea structurii |
| **Refolosire** | Da / Nu |

### Materiale si Tehnici

| Sectiune | Campuri |
|----------|--------|
| **Caramizi** | Materiale, Prelucrare, Consistenta, Forma, Culoare, Amestec, Asezare |
| **Elemente de piatra** | Materiale, Prelucrare, Consistenta, Forma, Culoare, Taiere, Asezare |

### Esantioane

| Camp | Descriere |
|------|-----------|
| **Esantioane de mortar** | Referinte esantioane mortar |
| **Esantioane de caramida** | Referinte esantioane caramida |
| **Esantioane de piatra** | Referinte esantioane piatra |

---

## Fila Lianti USM

Descrie caracteristicile liantilor (mortarelor) in structurile de zidarie.

<!-- IMAGINE: Captură de ecran a filei lianti -->
![Fila Lianti](images/03_scheda_us/19_tab_leganti.png)
*Figura 19: Fila Lianti USM*

### Caracteristici Liant

| Camp | Descriere |
|------|-----------|
| **Tip liant** | Mortar, Noroi, Absent etc. |
| **Consistenta** | Tenace, Friabila etc. |
| **Culoare** | Culoarea liantului |
| **Finisaj** | Tipul de finisaj |
| **Grosime liant** | Grosimea in cm |

### Compozitie

| Sectiune | Descriere |
|----------|-----------|
| **Agregate** | Componente grosiere |
| **Inerti** | Componente fine |
| **Incluziuni** | Materiale incluse |

---

## Fila Media

Afiseaza imaginile asociate unitatii stratigrafice.

<!-- IMAGINE: Captură de ecran a filei media -->
![Fila Media](images/03_scheda_us/20_tab_media.png)
*Figura 20: Fila Media*

### Lista US

Tabelul afiseaza toate US-urile cu imagini asociate:
- Mergi la fisa
- Casuta de bifare pentru selectie multipla
- Previzualizare miniatura

### Butoane

| Buton | Functie |
|-------|---------|
| **Cautare imagini** | Cauta imaginile asociate |
| **Salvare** | Salveaza asocierile |
| **Revenire** | Anuleaza modificarile |

---

## Fila Ajutor - Instrumente

Contine instrumente avansate pentru verificare si export.

<!-- IMAGINE: Captură de ecran a filei instrumente -->
![Fila Instrumente](images/03_scheda_us/21_tab_toolbox.png)
*Figura 21: Fila Instrumente*

### Sisteme de Verificare

| Instrument | Descriere |
|------------|-----------|
| **Verificare relatii stratigrafice** | Verifica consistenta relatiilor |
| **Verifica, porneste!!!!** | Executa verificarea |

### Export Matrix

| Buton | Rezultat |
|-------|----------|
| **Export Matrix** | Fisier DOT pentru Graphviz |
| **Export Graphml** | Fisier GraphML pentru yEd |
| **Export catre Extended Matrix** | Format S3DGraphy |
| **Matrix interactiva** | Vizualizare interactiva |

### Instrumente Suplimentare

| Instrument | Descriere |
|------------|-----------|
| **Ordine stratigrafica** | Calculeaza secventa stratigrafica |
| **Creare Cod Perioada** | Genereaza coduri de perioada |
| **csv2us** | Importa US din CSV |
| **Graphml2csv** | Exporta GraphML in CSV |

---

## Ordonare Stratigrafica (Nivelul Stratului)

Sistemul de **Ordonare Stratigrafica** calculeaza automat secventa US-urilor pe baza relatiilor stratigrafice introduse. Este un calcul automat care atribuie o valoare numerica progresiva fiecarui US in functie de pozitia sa in secventa stratigrafica.

### Cum functioneaza

Sistemul analizeaza relatiile stratigrafice (acopera/acoperit de, taie/taiat de etc.) si construieste un graf orientat. Apoi calculeaza ordinea topologica, atribuind:
- **Nivelul 0**: US-urile cele mai vechi (la baza stratigrafiei)
- **Nivelul 1, 2, 3...**: US-uri progresiv mai recente
- **Nivelul N**: US-urile cele mai recente (in varful stratigrafiei)

### Cerinte pentru ordonare

1. **Relatii complete**: Toate US-urile trebuie sa aiba relatii stratigrafice introduse
2. **Fara paradoxuri**: Nu trebuie sa existe cicluri in relatii (de ex., US1 acopera US2 si US2 acopera US1)
3. **Relatii inverse**: Toate relatiile trebuie sa aiba inversa lor

### Cum se executa ordonarea

1. Efectuati o **cautare** dupa Santier si Zona (sistemul functioneaza pe un singur santier/zona)
2. Mergeti la **Fila Ajutor** → **Instrumente**
3. Faceti clic pe **Ordine stratigrafica**
4. Confirmati operatiunea
5. Asteptati finalizarea

### Formatul ordonarii

Ordonarea este **intotdeauna numeric secventiala**:
```
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13...
```

**Reguli:**
- Numerele sunt **intotdeauna consecutive** (niciodata 1, 2, 5, 8 - intotdeauna 1, 2, 3, 4)
- Fara goluri in secventa
- US-urile la acelasi nivel stratigrafic au acelasi numar
- Ordinea poate fi **inversata** (casuta de bifare "Ordine: Antic → Recent"):
  - **Activ**: 0 = cel mai vechi, N = cel mai recent
  - **Inactiv**: 0 = cel mai recent, N = cel mai vechi

### Campul Nivel Strat

Rezultatul este salvat in campul **Nivel Strat** (lineEditOrderLayer) al fiecarui US. Acest camp:
- Este **calculat automat** de sistem
- Poate fi **modificat manual** daca este necesar
- Este folosit pentru sortarea US-urilor in vizualizare

### Erori frecvente

| Eroare | Cauza | Solutie |
|--------|-------|---------|
| "Paradox stratigrafic" | Ciclu in relatii | Verificati si corectati relatiile |
| "US-uri lipsa" | US-urile referite nu exista | Creati US-urile lipsa |
| "Relatie lipsa" | Relatie fara tip sau numar | Completati relatiile |

### Vizualizare

Odata calculata ordinea, puteti:
- **Sorta** inregistrarile dupa Nivel Strat
- **Filtra** dupa niveluri specifice
- **Exporta** Matrix cu niveluri

---

### Functii GIS

| Buton | Functie |
|-------|---------|
| **Deseneaza US** | Incarca stratul pentru desenare |
| **Previzualizare plan US** | Previzualizare pe harta |
| **Deschide fisele US** | Deschide fisele selectate |
| **Pan** | Instrument de panoramare |
| **Afiseaza imagini** | Afiseaza fotografiile |

### Exporturi Planse

| Buton | Rezultat |
|-------|----------|
| **Export planse** | Planse de sapatura |
| **simbologie** | Gestionare simbologie |
| **Deschide dosar** | Deschide dosarul de output |

---

## Harris Matrix

Harris Matrix este o reprezentare grafica a relatiilor stratigrafice.

<!-- IMAGINE: Captură de ecran a Harris Matrix -->
![Harris Matrix](images/03_scheda_us/22_matrix_harris.png)
*Figura 22: Exemplu de Harris Matrix*

<!-- VIDEO: Generare Harris Matrix -->
> **Tutorial Video**: [Inserati link video Harris Matrix]

### Generare Matrix

1. Selectati santierul si zona
2. Verificati ca relatiile sunt corecte
3. Mergeti la **Fila Ajutor** → **Instrumente**
4. Faceti clic pe **Export Matrix**

### Formate de Export

| Format | Software | Utilizare |
|--------|----------|-----------|
| DOT | Graphviz | Vizualizare de baza |
| GraphML | yEd, Gephi | Editare avansata |
| Extended Matrix | S3DGraphy | Vizualizare 3D |
| CSV | Excel | Analiza datelor |

### Extended Matrix

Extended Matrix adauga informatii suplimentare:
- Periodizare
- Definitii interpretative
- Date cronologice
- Compatibilitate CIDOC-CRM

<!-- IMAGINE: Captură de ecran a Extended Matrix -->
![Extended Matrix](images/03_scheda_us/23_extended_matrix.png)
*Figura 23: Dialogul Extended Matrix*

### Matrix Interactiva

Vizualizare interactiva a Matrix-ului:
- Zoom si panoramare
- Selectare noduri
- Navigare la fise

---

## Functionalitati GIS

Fisa US este strans integrata cu QGIS.

<!-- IMAGINE: Captură de ecran a integrarii GIS -->
![Integrare GIS](images/03_scheda_us/24_gis_integration.png)
*Figura 24: Integrare GIS*

### Bara de Instrumente GIS

| Buton | Functie | Scurtatura |
|-------|---------|------------|
| **Vizualizator GIS** | Incarca straturile US | Ctrl+G |
| **Previzualizare plan US** | Previzualizare geometrie | Ctrl+G |
| **Deseneaza US** | Activeaza desenarea | - |

### Straturi GIS Asociate

| Strat | Geometrie | Descriere |
|-------|-----------|-----------|
| PYUS | Poligon | Unitati stratigrafice |
| PYUSM | Poligon | Unitati murale |
| PYQUOTE | Punct | Cote |
| PYQUOTEUSM | Punct | Cote USM |
| PYUS_NEGATIVE | Poligon | US negative |

### Vizualizarea Rezultatelor Cautarii

Cand modul GIS este activ:
- Cautarile sunt afisate pe harta
- Rezultatele sunt evidentiate
- Puteti naviga intre rezultate

---

## Exporturi

### Fise US PDF

1. Faceti clic pe **Raport** in bara de instrumente
2. Alegeti formatul (PDF, Word)
3. Selectati fisele de exportat

<!-- IMAGINE: Captură de ecran a exportului PDF -->
![Export PDF](images/03_scheda_us/25_esportazione_pdf.png)
*Figura 25: Optiuni de export PDF*

### Liste

| Tip | Continut |
|-----|----------|
| **Lista US** | Lista tuturor US-urilor |
| **Lista Foto cu Miniatura** | Lista cu previzualizari |
| **Lista Foto fara Miniatura** | Lista simpla |
| **Fise US** | Fise complete |

### Conversie Word

Butonul **Convertire in Word** permite:
1. Selectarea unui PDF
2. Conversia in format DOCX
3. Editarea in Word

---

## Flux de Lucru Operational

### Crearea unei US Noi

<!-- VIDEO: Flux de lucru creare US -->
> **Tutorial Video**: [Inserati link video pentru creare US]

#### Pasul 1: Deschideti Fisa
<!-- IMAGINE: Pasul 1 -->
![Pasul 1](images/03_scheda_us/26_workflow_step1.png)

#### Pasul 2: Faceti clic pe Inregistrare Noua
<!-- IMAGINE: Pasul 2 -->
![Pasul 2](images/03_scheda_us/27_workflow_step2.png)

#### Pasul 3: Introduceti Identificarea
- Selectati Santierul
- Introduceti Zona
- Introduceti numarul US
- Selectati Tipul

<!-- IMAGINE: Pasul 3 -->
![Pasul 3](images/03_scheda_us/28_workflow_step3.png)

#### Pasul 4: Definitii
- Selectati definitia stratigrafica
- Selectati definitia interpretativa

<!-- IMAGINE: Pasul 4 -->
![Pasul 4](images/03_scheda_us/29_workflow_step4.png)

#### Pasul 5: Descriere
- Completati descrierea fizica
- Completati interpretarea

<!-- IMAGINE: Pasul 5 -->
![Pasul 5](images/03_scheda_us/30_workflow_step5.png)

#### Pasul 6: Relatii Stratigrafice
- Introduceti relatiile cu alte US-uri
- Creati relatiile inverse

<!-- IMAGINE: Pasul 6 -->
![Pasul 6](images/03_scheda_us/31_workflow_step6.png)

#### Pasul 7: Date Fizice si Masuratori
- Completati caracteristicile fizice
- Introduceti masuratorile

<!-- IMAGINE: Pasul 7 -->
![Pasul 7](images/03_scheda_us/32_workflow_step7.png)

#### Pasul 8: Salvare
- Faceti clic pe Salvare
- Verificati salvarea

<!-- IMAGINE: Pasul 8 -->
![Pasul 8](images/03_scheda_us/33_workflow_step8.png)

### Generarea Harris Matrix

1. Verificati ca toate relatiile sunt introduse
2. Executati verificarea relatiilor
3. Corectati eventualele erori
4. Exportati Matrix-ul

### Asocierea Documentatiei

1. Mai intai creati fisele in tabelul de Documentatie
2. In fisa US, fila Documentatie
3. Adaugati referintele
4. Verificati cu "Vizualizare documentatie"

---

## Depanare

### Eroare de salvare
- Verificati ca Santier, Zona si US sunt completate
- Verificati ca combinatia este unica

### Relatii inconsistente
- Folositi verificarea relatiilor
- Verificati relatiile inverse
- Reparati cu butonul Repara

### Matrix-ul nu se genereaza
- Verificati ca Graphviz este instalat
- Verificati calea in configurare
- Verificati ca exista relatii

### Straturile GIS nu se incarca
- Verificati conexiunea la baza de date
- Verificati ca exista geometrii
- Verificati sistemul de referinta a coordonatelor

### Imaginile nu se afiseaza
- Verificati caile miniaturilor
- Verificati asocierile media
- Verificati permisiunile dosarului

---

## Note Tehnice

### Baza de Date

- **Tabel principal**: `us_table`
- **Campuri principale**: peste 80 de campuri
- **Cheie primara**: `id_us`
- **Cheie compusa**: santier + zona + us

### Tezaur

Campurile cu tezaur (definitii) folosesc tabelul `pyarchinit_thesaurus_sigle`:
- tipologia_sigla = '1.1' pentru definitia stratigrafica
- tipologia_sigla = '1.2' pentru definitia interpretativa

### Straturi GIS

| Strat | Tabel | Tip |
|-------|-------|-----|
| PYUS | pyarchinit_us_view | Poligon |
| PYUSM | pyarchinit_usm_view | Poligon |
| PYQUOTE | pyarchinit_quote_view | Punct |

---

*Documentatie PyArchInit - Fisa US/USM*
*Versiune: 4.9.x*
*Ultima actualizare: Ianuarie 2026*
