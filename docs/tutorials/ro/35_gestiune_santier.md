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
9. [Vizualizare 2D si 3D a Computo Metric](#vizualizare-2d-si-3d-a-computo-metric)
10. [Export PDF si CSV al Panoului](#export-pdf-si-csv-al-panoului)
11. [Flux de lucru recomandat](#flux-de-lucru-recomandat)
12. [Depanare](#depanare)
13. [Intrebari frecvente](#intrebari-frecvente)

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

### Noul aspect cu file al Panoului Santier

Incepand cu versiunea curenta, fereastra **Panou Santier** a fost reorganizata in **trei file** pentru a face loc noului panou **Analiza Costurilor** fara a incarca vizual interfata. Randul de antet cu **Santier**, **An** si butonul **Actualizeaza** ramane vizibil deasupra filelor, astfel incat santierul sau anul pot fi schimbate in orice moment: toate filele se actualizeaza automat.

| Fila | Continut |
|------|----------|
| **Sumar** | Vederea afisata la deschiderea panoului. Sus, pe toata latimea, **Sumarul Bugetului** (bara de progres si grafic de tip placinta); sub acesta, alaturat, sumarele **Personal** si **Echipamente** |
| **Computo Metric** | Grupeaza intregul flux de calcul DEM: combo-urile **DEM Pre**, **DEM Post** si **Poligon**, butoanele radio **Diferenta DEM** / **DEM pe Poligon**, butonul **Calculeaza**, etichetele de **arie** si **volum**, noul grup **Analiza Costurilor** (EUR/m3, m3/zi -> cost total, zile estimate, cost zilnic), butonul **Salveaza Inregistrare**, butoanele **Afisare 2D** / **Afisare 3D** / **Export 2DM + 3D** si **tabelul de istoric** in partea de jos |
| **Export** | Butoanele de **export PDF** si **CSV** insotite de o scurta descriere |

<!-- IMAGINE: Noul aspect cu file al Panoului Santier (Sumar / Computo Metric / Export) -->
> **Fig. 7a**: Noul aspect cu file al Panoului Santier cu antetul Santier / An / Actualizeaza mereu vizibil

**Fix**: DEM-urile nu mai dispar la apasarea butonului **Calculeaza** (regresie din 5.0.13-alpha in care reimprospatarea automata a combo-urilor resetata selectia curenta).

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

Incepand cu versiunea 5.1, langa butonul **Calculeaza** sunt disponibile si butoanele **Afiseaza 2D**, **Afiseaza 3D** si **Creeaza plasa 3D**, pentru a vizualiza rezultatul calculului direct pe harta si intr-o vedere tridimensionala interactiva. Vezi sectiunea [Vizualizare 2D si 3D a Computo Metric](#vizualizare-2d-si-3d-a-computo-metric).

---

## Vizualizare 2D si 3D a Computo Metric

Incepand cu versiunea 5.1, dupa apasarea butonului **Calculeaza** din panoul Computo Metric, Panoul Santier nu se mai limiteaza la afisarea valorilor numerice (aria si volum): creeaza automat un set de straturi cartografice si pune la dispozitie o vedere 3D interactiva.

### Ce se intampla la apasarea butonului "Calculeaza"

La finalizarea unui calcul de diferenta DEM, Panoul Santier executa automat urmatorii pasi:

1. **Salvare permanenta a rasterului diferenta**: rasterul rezultat (DEM post - DEM pre) este salvat ca GeoTIFF permanent in `<PYARCHINIT_HOME>/site_dashboard/<numele santierului>/`. Astfel, rasterul nu mai este pierdut la inchiderea QGIS si poate fi reutilizat oricand.
2. **Adaugare la proiectul QGIS**: rasterul este adaugat in panoul Straturi intr-un grup dedicat numit **"Site Dashboard - Computi"**, pentru a pastra toate calculele organizate.
3. **Stil automat**: rasterul primeste o **rampa de culori divergenta**:
   - **Rosu** pentru zonele de sapatura (valori negative, pamant excavat)
   - **Albastru** pentru zonele de umplutura (valori pozitive, pamant adaugat)
   - **Transparent / neutru** pentru celulele cu variatie neglijabila (|diff| <= 1 cm)
4. **Poligonizarea zonei de interventie**: celulele raster cu |diff| > 1 cm sunt convertite intr-un strat vectorial de poligoane, adaugat tot in grupul "Site Dashboard - Computi" cu un stil evidentiat, pentru a arata dintr-o privire extinderea totala a interventiei.
5. **Zoom automat**: harta principala QGIS este centrata automat pe extinderea calculului.

### Cerinte

Pentru a folosi noile vizualizari 2D / 3D este necesar:

- Sa aveti **doua straturi raster DEM** incarcate in proiectul QGIS (de obicei un DEM **pre** si un DEM **post** sapatura)
- Sa le selectati corect in listele derulante **DEM Pre** si **DEM Post** din panoul Computo Metric
- Sistemul de referinta (CRS) al celor doua rastere sa fie coerent

### Butoane noi

Langa butonul **Calculeaza** sunt acum disponibile trei butoane noi:

| Buton | Descriere |
|-------|-----------|
| **Afiseaza 2D** | Recentreaza harta QGIS pe extinderea ultimului calcul. Util pentru a reveni rapid la Computo Metric activ dupa ce ati lucrat in alte zone. |
| **Afiseaza 3D** | Deschide un dialog 3D interactiv care foloseste DEM **pre** ca suprafata de teren, cu rasterul diferenta suprapus. Include: un control pentru **exagerarea verticala**, casete de bifare pentru activarea / dezactivarea straturilor individuale si un buton **Reseteaza vederea**. |
| **Creeaza plasa 3D** | Construieste plase TIN din DEM pre si post (prin algoritmii QGIS Processing). Plasele pot fi afisate in vizualizatorul 3D pentru a compara vizual cele doua suprafete si volumul dintre ele. |

<!-- IMAGINE: Noile butoane Afiseaza 2D, Afiseaza 3D si Creeaza plasa 3D langa butonul Calculeaza -->
> **Fig. 18**: Noile butoane **Afiseaza 2D**, **Afiseaza 3D** si **Creeaza plasa 3D** langa butonul **Calculeaza**

<!-- IMAGINE: Dialog 3D interactiv cu DEM pre ca teren si rasterul diferenta suprapus -->
> **Fig. 19**: Dialogul 3D interactiv al Computo Metric cu exagerare verticala si control al straturilor

### Flux de lucru tipic

1. Incarcati in proiectul QGIS cele doua rastere DEM (pre si post)
2. Deschideti **Panoul Santier**
3. In sectiunea **Computo Metric** selectati cele doua DEM-uri in **DEM Pre** si **DEM Post**
4. Apasati **Calculeaza**: rasterul diferenta si poligonul de interventie sunt create automat, iar harta este centrata pe extindere
5. Cititi valorile numerice (aria, volum, sapatura, umplutura) direct in panou
6. Apasati **Afiseaza 3D** pentru a deschide vederea tridimensionala
7. (Optional) Apasati **Creeaza plasa 3D** pentru a genera si afisa plasele TIN ale celor doua DEM-uri
8. Apasati **Salveaza Computo** pentru a arhiva rezultatul in istoric

### Organizare pe disc

Toate rasterele si straturile generate de Computo Metric sunt salvate in:

```
<PYARCHINIT_HOME>/site_dashboard/<numele santierului>/
```

unde `<PYARCHINIT_HOME>` este folderul de lucru configurat in setarile PyArchInit, iar `<numele santierului>` este santierul curent selectat in panou. Astfel se pastreaza un istoric fizic al tuturor calculelor si straturile pot fi reutilizate si in alte proiecte QGIS.

### Actualizare: "Afiseaza 2D" -- Dialog analitic de sectiune

Incepand cu urmatoarea versiune, butonul **Afiseaza 2D** din panoul Computo Metric nu se mai limiteaza la recentrarea hartii pe ultimul calcul: deschide un **dialog analitic bazat pe matplotlib** care prezinta rezultatele sapaturii ca o sectiune arheologica clasica.

Dialogul este disponibil **numai atunci cand calculul a fost efectuat in modul "Diferenta DEM"** (cu DEM pre si DEM post). Daca ati folosit modul **DEM + Poligon**, butonul se comporta ca inainte si doar face zoom pe harta QGIS la extinderea calculului.

Cand este disponibil, dialogul contine urmatoarele panouri:

| Panou | Descriere |
|-------|-----------|
| **Harta termica a diferentei DEM** | Harta termica 2D a rasterului sapatura/umplutura cu o rampa de culori divergenta (rosu pentru sapatura, albastru pentru umplutura) |
| **Histograma** | Distributia adancimilor de **sapatura** si a inaltimilor de **umplutura**, pentru a obtine imediat un rezumat statistic al volumului deplasat |
| **Sectiune longitudinala (E-V)** | Sectiunea arheologica clasica: **DEM pre** este desenat in **albastru**, **DEM post** in **rosu**, iar volumul excavat este **umplut** intre cele doua linii |
| **Sectiune transversala (N-S)** | Aceeasi logica ca si sectiunea E-V, dar pe directia Nord-Sud |
| **Spinbox rand / coloana** | Permit deplasarea interactiva a pozitiei celor doua sectiuni pe raster, pentru a explora intreaga sapatura |
| **Butonul "Salveaza PNG"** | Exporta intreaga figura (harta termica, histograma si ambele sectiuni) ca imagine PNG, gata de inclus in raportul de sapatura |

<!-- IMAGINE: Dialog analitic Afiseaza 2D cu harta termica, histograma si sectiuni E-V / N-S -->
> **Fig. 20**: Noul dialog analitic **Afiseaza 2D** cu harta termica a diferentei DEM, histograma sapatura / umplutura si ambele sectiuni longitudinala si transversala (DEM pre in albastru, DEM post in rosu, volumul excavat umplut intre cele doua linii)

### Actualizare: "Afiseaza 3D" -- Rezerva matplotlib

Butonul **Afiseaza 3D** gestioneaza acum automat doua scenarii in functie de versiunea de QGIS instalata:

1. **QGIS cu modulul 3D nativ (Qt3D disponibil)**: ca si inainte, se deschide dialogul `Qgs3DMapCanvas` incorporat, cu teren construit din DEM pre, exagerare verticala si control al straturilor.
2. **QGIS fara modulul 3D (eroare "QGIS 3D module not available")**: Panoul Santier trece automat la un **vizualizator 3D bazat pe matplotlib**. Deoarece matplotlib face parte din dependentele instalate deja de plugin, acest vizualizator **functioneaza intotdeauna**, chiar si pe build-uri QGIS minimale, compilate fara suport 3D.

Vizualizatorul de rezerva ofera:

| Control | Descriere |
|---------|-----------|
| **Mod de afisare** | Trei moduri selectabile: **Pre + Post** (ambele suprafete suprapuse), **Doar diferenta** (numai suprafata de sapatura/umplutura), **Doar Pre** (DEM pre ca suprafata de referinta) |
| **Exagerare verticala** | Un cursor pentru a accentua diferenta de cota dintre cele doua suprafete -- util cand sapatura este putin adanca |
| **Rotatie interactiva** | Tragand cu mouse-ul, scena 3D poate fi rotita in timp real pentru a explora sapatura din orice unghi |

<!-- IMAGINE: Vizualizator 3D matplotlib de rezerva in modul Pre + Post -->
> **Fig. 21**: Vizualizatorul 3D matplotlib de rezerva, folosit atunci cand modulul Qt3D nativ al QGIS nu este disponibil: arata suprafetele pre si post cu exagerare verticala reglabila

### Actualizare: "Creeaza plasa 3D" -- Stil automat de teren

Butonul **Creeaza plasa 3D** aplica acum automat o **rampa de culori de tip teren** grupului de seturi de date de elevatie al plasei (**Bed Elevation**). Anterior, plasa arata ca o suprafata plata, dificil de citit; acum devine imediat o harta expresiva a cotelor:

- **Verde** pentru cotele cele mai joase
- **Portocaliu** pentru cotele intermediare
- **Maro** pentru cotele cele mai inalte

Astfel, plasa este imediat vizibila si semnificativa in harta QGIS, chiar inainte de a deschide vederea 3D. Dupa ce ati construit-o, este suficient sa apasati **Afiseaza 3D** pentru a o vedea redata ca suprafata tridimensionala, fie prin modulul 3D nativ al QGIS, fie prin vizualizatorul matplotlib de rezerva descris mai sus.

<!-- IMAGINE: Plasa 3D cu noua rampa verde / portocaliu / maro de tip teren -->
> **Fig. 22**: Plasa 3D cu noua rampa de culori de tip teren aplicata automat pe setul de date de elevatie

### Actualizare: poligon ca masca de decupare

Daca in panoul Computo Metric, pe langa cele doua DEM-uri, selectati si un strat vectorial in combobox-ul **Strat Poligon** mentinand activa modalitatea **Diferenta DEM**, poligonul este folosit acum ca **masca de decupare**: ambele DEM-uri sunt decupate pe poligon inainte de calculul diferentei, astfel incat sectiunea analitica 2D, rezerva 3D matplotlib si plasa TIN lucreaza exclusiv pe zona de interventie. Fluxul tipic este: desenati un poligon in jurul sapaturii, selectati DEM-urile pre si post, alegeti poligonul in combobox-ul **Strat Poligon** si apasati **Calculeaza**. Cele doua rastere decupate sunt adaugate automat in grupul **"Cruscotto Cantiere - Computi"** din arborele de straturi, gata de reutilizare.

### Actualizare: "Creeaza plasa 3D" -- fara blocari

Versiunile anterioare puteau provoca blocari ale QGIS pe unele build-uri din cauza unui segfault C++ in interiorul algoritmilor de Processing folositi pentru construirea plasei. Generarea a fost rescrisa in **Python pur**: Panoul citeste DEM-ul cu GDAL si scrie direct un fisier 2DM cu o **plasa de patrulatere pe grila regulata**, fara a depinde de algoritmii nativi. Rezultatul este sigur pe orice versiune de QGIS. Plasele cu mai mult de aproximativ **15 000 de celule** sunt reesantionate automat pentru a mentine construirea rapida si fisierul usor, iar celulele cu valoare nodata sunt omise: atunci cand este activa o masca poligonala, plasa urmeaza deci exact forma zonei de interventie decupate. In rarul caz in care generarea esueaza din alte motive (disc plin, permisiuni), dialogul sugereaza acum sa deschideti direct **Afiseaza 3D**, care foloseste vizualizatorul matplotlib de rezerva si nu are nevoie de niciun strat plasa.

### Actualizare: auto-reincarcarea combourilor la click pe "Calculeaza"

Panoul Computo Metric **actualizeaza acum automat listele de DEM si de poligon de fiecare data cand se face click pe "Calculeaza"**: nu mai este necesar sa inchideti si sa redeschideti Panoul Santier dupa incarcarea unui nou raster sau dupa desenarea unui nou poligon in proiect. Este suficient sa adaugati stratul in QGIS, sa reveniti in panou si sa apasati **Calculeaza** -- combourile **DEM Pre**, **DEM Post** si **Strat Poligon** sunt repopulate instantaneu cu starea curenta a proiectului. Diagnosticul eventual al decuparii (succes, SRC incompatibil, intersectie vida) este afisat in **bara de mesaje a QGIS**, astfel incat sa fie mereu clar ce straturi au fost folosite efectiv in calcul.

### Actualizare: buton redenumit "Exporta 2DM + 3D"

Butonul numit anterior **Creeaza plasa 3D** a fost redenumit in **Exporta 2DM + 3D** pentru a reflecta noul sau comportament: **nu mai** incarca plasa ca strat in proiectul QGIS (API-ul nativ de mesh poate provoca blocari pe unele build-uri de QGIS) si, in schimb, efectueaza doua actiuni sigure si complementare. Scrie fisierele **2DM** pe disc pornind de la DEM-urile pre si post (utile pentru import in software extern de post-procesare) si deschide direct **vizualizarea 3D matplotlib** pe DEM-urile decupate, astfel incat rezultatul poate fi evaluat vizual imediat. In acest fel, riscul de blocare este eliminat complet, pentru ca API-ul de mesh al QGIS nu mai este apelat niciodata.

### Actualizare: decuparea poligonului cu diagnostica vizibila

Atunci cand selectati un strat in combobox-ul **Strat Poligon** impreuna cu cele doua DEM-uri, decuparea rasterelor pe poligon este acum **inregistrata in bara de mesaje a QGIS**: in caz de succes este afisata lista fisierelor decupate scrise pe disc, iar in caz de esec este indicat motivul concret (de exemplu poligon intr-un SRC diferit de cel al DEM-urilor, nicio intersectie geometrica intre poligon si raster, fisier sursa lipsa sau necitibil). Astfel este imediat clar de ce o decupare nu a fost aplicata si ce trebuie corectat (reproiectarea poligonului, mutarea lui peste zona DEM-urilor, verificarea caii fisierului), fara a fi nevoie sa deschideti log-uri sau consola Python.

### Actualizare: decuparea poligonului si in modul "DEM pe Poligon"

Decuparea poligonului functioneaza acum si atunci cand este selectat butonul radio **DEM pe Poligon** (modul zonal-stats cu un singur DEM): rasterul este decupat la extinderea poligonului **inainte** de a fi transmis vizualizatoarelor **Arata 2D**, **Arata 3D** si **Exporta 2DM + 3D**, astfel incat sectiunea si vederea 3D afiseaza doar zona de interventie in loc de intregul DEM, asa cum se intampla inainte. Mesajul de diagnostica al decuparii apare in **bara de mesaje a QGIS** exact ca in modul Diferenta DEM. In acest scenariu cu un singur DEM, vizualizatorul **Arata 2D** se adapteaza automat: heat-map-ul afiseaza cotele cu o rampa de culori **terrain**, histograma reprezinta distributia cotelor cu linia mediei, iar cele doua sectiuni longitudinala/transversala traseaza o singura linie de cota (fara umplere intre pre si post, pentru ca DEM-ul post nu exista).

### Actualizare: Analiza Costurilor la Computo Metric

In panoul Computo Metric al Panoului Santier a fost adaugat un nou bloc **Analiza Costurilor** cu doi parametri de intrare: **Cost unitar** (in euro/mc) si **Productivitate** (in mc/zi). La fiecare apasare a butonului **Calculeaza**, panoul actualizeaza automat trei valori derivate vizibile dintr-o privire: **Cost total** (volum x cost unitar), **Zile estimate** (volum / productivitate) si **Cost zilnic** (cost unitar x productivitate). Ambele intrari sunt salvate automat **pe santier** in setarile QGIS (chei `pyArchInit/site_dashboard/costs/<santier>/...`), astfel incat este suficient sa le introduceti o singura data pentru fiecare santier: la schimbarea santierului valorile salvate sunt reincarcate automat, iar cele trei totaluri sunt recalculate in timp real la fiecare nou calcul.

### Actualizare: decupare pre/post aliniata

Calculul diferentei DEM necesita ca cele doua DEM-uri (pre si post) sa fie perfect aliniate pe aceeasi grila de pixeli. In versiunile anterioare, atunci cand se folosea un poligon de decupare, cele doua DEM-uri decupate puteau ajunge pe grile usor diferite, iar calculul `pre - post` rezulta eronat sau gol. Acum ambele decupari folosesc **rezolutia nativa a DEM-ului pre** ca referinta (aceleasi `xRes` / `yRes` si aceeasi aliniere a grilei), astfel incat cele doua rastere decupate sunt intotdeauna aliniate la nivel de pixel, iar diferenta produce un rezultat valid. Chiar si transeele minime din care au fost scoase doar "10 galeti de pamant" (aproximativ 1 mc) sunt acum capturate corect de calculul cantitatilor.

### Actualizare: noul combo "Ziduri / Structuri"

In panoul Computo Metric a fost adaugat un al doilea combo **Ziduri / Structuri** care permite selectarea unui strat de poligoane reprezentand ziduri, structuri in elevatie, piloni sau alte parti construite care **nu trebuie luate in calcul** in cubajul de sapatura. Cand se apasa **Calculeaza**, poligoanele zidurilor sunt rasterizate ca NODATA pe rasterul de diferenta decupat, iar celulele lor sunt excluse din totalul de volum; mesajul de diagnostica apare in bara de mesaje a QGIS (de exemplu `walls masked: muri_trincea_42`). Flux de lucru arheologic tipic: incarca DEM pre + DEM post + poligonul zonei de sapatura + poligonul zidurilor descoperite, selecteaza-le pe ambele in cele doua combo-uri si apasa **Calculeaza** -- volumul sapat exclude automat volumul structurilor.

---

## Export PDF si CSV al Panoului

Panoul Santier permite exportul unui rezumat complet al datelor de gestiune in doua formate: **PDF** (document paginat, ideal pentru predare catre beneficiar sau pentru arhivare) si **CSV** (ideal pentru analize ulterioare in Excel sau alte foi de calcul).

### Export PDF

Butonul **Exporta PDF** genereaza un raport complet al santierului. Incepand cu versiunea 5.1, PDF-ul include:

- **Pagina de coperta reinnoita** cu numele santierului, anul de referinta si data generarii
- **Rezumat buget** cu tabele detaliate pe categorii si totaluri (planificat vs efectiv)
- **Rezumat personal** cu statistici de prezenta, ore lucrate si costuri
- **Rezumat echipamente** cu starea inventarului si mentenanțe scadente
- **Sectiune noua "Computo Metric"** care include:
  - Un tabel detaliat cu toate calculele salvate
  - **Totaluri**: aria totala (mp) si volumul total (mc)
  - **Statistici**: volumul de sapatura, volumul de umplutura, aria afectata
- **Sectiune noua "Analiza Costurilor"** (plasata intre **Computo Metric** si **Statistici**) cu o parameter card a valorilor configurate (cost unitar in euro/mc si productivitate in mc/zi), un tabel detaliat pe fiecare inregistrare (data, tip, volum, cost, zile estimate, cost zilnic) si un rand de **totaluri** la baza tabelului; blocul **Statistici** a fost extins cu **cost total** si **zile totale** de santier
- **Suport complet pentru caractere speciale**: randarea PDF a fost corectata pentru toate limbile suportate, inclusiv literele cu diacritice din romana (**a**, **a**, **i**, **s**, **t**), caracterele **grecesti**, **arabe**, **portugheze** si **catalane**.

### Export CSV

Butonul **Exporta CSV** genereaza un fisier CSV compatibil cu principalele aplicatii de calcul tabelar. Incepand cu versiunea 5.1:

- **Codificare UTF-8 cu BOM**: garanteaza ca Excel (in special versiunea europeana) deschide corect fisierul fara sa corupa literele cu diacritice si caracterele speciale
- **Separator `;`** (punct si virgula): compatibil cu localizarea europeana a Excel-ului
- **Sectiune COMPUTO METRICO**: include toate datele de computo metric, cu tipul, aria, volumul si notele fiecarui calcul
- **Sectiune noua `=== ANALIZA COSTURILOR ===`**: incepe cu cei doi parametri (cost unitar in euro/mc si productivitate in mc/zi) si este urmata de tabelul detaliat pe fiecare inregistrare (data, tip, volum, cost, zile estimate, cost zilnic), gata pentru a fi filtrat sau agregat in Excel
- **Bloc SUMMARY final extins**: un rezumat agregat cu totaluri si statistici, util pentru analize rapide fara a fi nevoie de formule; acum include si **Cost total** si **Zile totale** calculate pornind de la noua Analiza Costurilor

<!-- IMAGINE: PDF exportat cu noua sectiune Computo Metric -->
> **Fig. 20**: Exemplu de PDF exportat cu noua sectiune **Computo Metric** (tabel, totaluri si statistici)

<!-- IMAGINE: CSV exportat deschis in Excel cu sectiunea COMPUTO METRICO si blocul SUMMARY -->
> **Fig. 21**: Exemplu de CSV exportat deschis in Excel cu sectiunea **COMPUTO METRICO** si blocul **SUMMARY** final

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
