# Tutorial 25: Manager Temporal (Controller temporal GIS)

## Introducere

**Managerul Temporal** (Controller temporal GIS) este un instrument avansat pentru vizualizarea secventei stratigrafice in timp. Permite "navigarea" prin nivelurile stratigrafice utilizand un control temporal, afisand progresiv US de la cele mai vechi la cele mai recente (formarea sitului).

### Functionalitati principale

- Vizualizare progresiva a nivelurilor stratigrafice
- Control prin disc/cursor
- Mod cumulativ sau nivel individual
- Tiparirea automata a planselor atlasului, una pe nivel
- Integrare cu Harris Matrix

## Acces

### Din meniu
**PyArchInit** > **Manager Temporal**

### Cerinte prealabile

- Strat cu campul `order_layer` (index stratigrafic)
- US cu order_layer completat
- Straturi incarcate in QGIS

## Interfata

### Panoul principal

```
+--------------------------------------------------+
|         Gestionare Temporala GIS                  |
+--------------------------------------------------+
| Straturi disponibile:                             |
| [ ] pyunitastratigrafiche                        |
| [ ] pyunitastratigrafiche_usm                    |
| [ ] alt_strat                                    |
+--------------------------------------------------+
|              [Disc circular]                     |
|                   /  \                           |
|                  /    \                          |
|                 /______\                         |
|                                                  |
|         Nivel: [SpinBox: 0-N]                   |
+--------------------------------------------------+
| [ ] Mod cumulativ (afiseaza <= nivel)            |
+--------------------------------------------------+
| [ ] Vizualizare matrice                          |
| [Plăci din perioada imprimării atlasului]        |
| [Opriți procesul de imprimare]                   |
+--------------------------------------------------+
| [Previzualizare Matrix/Imagine]                  |
+--------------------------------------------------+
```

### Controale

| Control | Functie |
|---------|---------|
| File (sus) | **Sistem cronologic relativ** (lista straturilor, discul și nivelul) și **Sistem cronologic absolut** (căutare după ani, vezi «Cronologie absolută») |
| Caseta strat | Selectare straturi de controlat |
| Disc | Navigare intre niveluri (rotire) |
| SpinBox | Introducere directa a nivelului |
| Mod cumulativ | Afisare toate nivelurile pana la cel selectat |
| Vizualizare matrice | Afisare Harris Matrix sincronizata |

## Campul order_layer

### Ce este order_layer?

Campul `order_layer` defineste ordinea de afisare stratigrafice:
- **0** = Nivelul cel mai vechi (adancime)
- **N** = Nivelul cel mai recent (suprafata)

Aceasta este conventia butonului **Ordinea stratigrafica** cu caseta "Ordine: Antic → Recent" activata (setarea implicita, vezi Tutorialul 03): daca ordonarea a fost calculata invers, Managerul Temporal si harta afiseaza secventa rasturnata.

### Completarea order_layer

In formularul US, fila **Ajutor** > **Instrumente**, butonul **Ordinea stratigrafica** calculeaza `order_layer` din relatiile stratigrafice (vezi Tutorialul 03); valoarea US curente apare in campul de sub buton. Reguli:
1. 0 pentru US cele mai vechi, valori crescatoare spre cele mai recente (la suprafata)
2. US contemporane pot avea aceeasi valoare
3. Urmati secventa Matricei

### Exemplu

| US | order_layer | Descriere |
|----|-------------|-----------|
| US001 | 4 | Humus de suprafata |
| US002 | 3 | Strat arat |
| US003 | 2 | Prabusire |
| US004 | 1 | Podea de utilizare |
| US005 | 0 | Fundatie |

Incepand cu 5.13.19-alpha, straturile US si USM pe care pyArchInit le incarca pe harta (vezi Tutorialul 14, *Alegerea Stilului*) sunt desenate in aceeasi ordine folosita de Manager Temporal: dupa cronologia perioadei, apoi dupa `order_layer` (0 = cea mai veche), astfel incat unitatile cele mai recente sunt deasupra.

## Moduri de vizualizare

### Modul nivel individual

Caseta de bifare **NEACTIVATA**:
- Afiseaza DOAR US de la nivelul selectat
- Util pentru izolarea straturilor individuale
- Vizualizare "sectiune"

### Modul cumulativ

Caseta de bifare **ACTIVATA**:
- Afiseaza toate US de la nivelul 0 (cel mai vechi) pana la cel selectat
- Arata formarea sitului, de la US cele mai vechi la cele mai recente
- Vizualizare mai realista

### Cronologie absolută

A doua filă a ferestrei, **Sistem cronologic absolut**, lucrează cu ani în loc de nivelurile `order_layer`: se alege un interval de timp și se încarcă pe hartă unitățile stratigrafice (US) din perioadele care se suprapun cu acel interval. Cere ca Periodizarea să fie completată (vezi Tutorialul 04), cu **Cronologie inițială** și **Cronologie finală** pentru fiecare perioadă și fază: o perioadă fără ani nu este găsită.

**Controale.**

- **Cronologia inițială** și **Cronologia finală**: două casete numerice, care se citesc «Afișează intervalul de timp dintre an: … iar anul …». Anii pot fi între `-4.000.000` și `2100`: valorile negative sunt î.Hr. (268 î.Hr. = `-268`), cele pozitive d.Hr., fără semn (1400 d.Hr. = `1400`). Anul cel mai vechi se pune în Cronologia inițială.
- Butonul **Vedere**: pornește căutarea.

**Ce face butonul Vedere.**

1. Caută în Periodizare (a tuturor siturilor din baza de date) perioadele și fazele a căror datare **se suprapune** cu intervalul, adică cele care nu se termină înainte de anul inițial și nu încep după anul final. Dacă nu găsește niciuna, avertizează «There are no Periods in this time interval» (mesajul apare în engleză) și se oprește.
2. Preia unitățile stratigrafice (US) a căror perioadă inițială și fază inițială corespund cu cele găsite. Dacă nu există niciuna, avertizează «There are no geometries to display» (tot în engleză).
3. Încarcă pe hartă straturile acestor US, cu același mecanism de încărcare ca formularul US (vezi Tutorialul 03).
4. Actualizează previzualizarea matricei, dacă **Vizualizare matrice** este activată: previzualizarea urmează straturile bifate și nivelul filei relative, nu intervalul de ani.

**Diferența față de fila relativă.** Discul și modul cumulativ **filtrează** straturile deja încărcate; **Vedere**, în schimb, **adaugă** în proiect un grup nou de straturi la fiecare clic (cele de dinainte rămân în proiect). Ca în formularul US, cu o bază de date PostgreSQL mecanismul de încărcare filtrează după sit și nu după fiecare US în parte: straturile arată tot situl.

## Integrarea cu Matrix

### Vizualizare sincronizata

Cu caseta de bifare **"Vizualizare matrice"** activata:
- Harris Matrix apare in panou
- Se actualizeaza sincronizat cu nivelul
- Evidentiaza US nivelului curent

### Generare imagini

Managerul Temporal poate genera:
- O plansa pentru fiecare nivel, alcatuita cu sablonul de macheta ales (imagine JPG)
- Matricea Harris a acelui nivel in interiorul plansei, daca **Vizualizare matrice** este activata

## Tiparirea planselor

### Proces

1. Selectati straturile de inclus
2. Activati **Vizualizare matrice** daca matricea trebuie sa apara pe planse (altfel imaginea matricei din sablon este ascunsa)
3. Faceti clic pe **Plăci din perioada imprimării atlasului**
4. In fereastra care se deschide, alegeti sablonul de macheta (vezi nota «Ce sablon sa alegi» de la final) si confirmati
5. Alegeti folderul in care se salveaza plansele
6. Raspundeti la intrebarea daca se deschide Layout Designer pentru a retusa sablonul inainte de a incepe
7. Asteptati: o bara de progres arata plansa in lucru si, la sfarsit, un mesaj spune unde au fost salvate
8. Pentru a opri generarea, faceti clic pe **Opriți procesul de imprimare**: plansele deja scrise raman in folder

### Iesire

- Un `Tavola_N.jpg` pentru fiecare nivel (N este valoarea `order_layer`), in folderul ales: harta la acel nivel, in modul activ (cumulativ sau nivel individual)
- Titlul «Tavola N» si imaginea matricei apar daca sablonul le prevede (matricea doar cu **Vizualizare matrice** activata)
- Nivelurile in care nicio US nu are datarea completata sunt omise: acele numere lipsesc din secventa de fisiere
- Cu un sablon cu doua pagini fiecare nivel produce doua imagini, a doua fiind `Tavola_N_2.jpg` (vezi nota «A face apt orice sablon» de la final)

**Etichetele plansei.** În timp ce generează plansele atlasului, Time Manager pune pe straturile alese etichetele plansei — numărul unității într-un cerc pe US, cota pe puncte — și le scoate la sfârșitul generării, repunându-le pe cele care erau înainte. Începând cu 5.13.110-alpha le scoate în orice caz, chiar dacă o planșă eșuează: înainte, în acest caz, rămâneau pe straturile proiectului și ajungeau în fișierul proiectului când acesta era salvat.

## Flux de lucru tipic

### 1. Pregatire

```
1. Deschideti proiectul QGIS cu straturi US
2. Verificati ca order_layer este completat
3. Deschideti Managerul Temporal
```

### 2. Selectarea straturilor

```
1. Selectati straturile de controlat
2. De obicei: pyunitastratigrafiche si/sau _usm
```

### 3. Navigare

```
1. Utilizati discul sau spinbox-ul
2. Observati schimbarea vizualizarii
3. Activati/dezactivati modul cumulativ
```

### 4. Documentatie

```
1. Activati "Vizualizare matrice"
2. Tipariti plansele cu "Plăci din perioada imprimării atlasului"
3. Verificati fisierele Tavola_N.jpg din folderul ales
```

## Sabloane de macheta

### Incarcarea sabloanelor

Managerul Temporal suporta sabloane QGIS pentru:
- Machete de tiparire personalizate
- Antete si legende
- Formate standard

### Sabloane disponibile

Fereastra de alegere listeaza fisierele `.qpt` gasite in folderul plugin-ului, in `resources/dbfiles/` si in `~/pyarchinit_5/bin/profile/template/`:
- `layout_TimeManager`: sablonul Time Manager, cu titlul «Tavola N» si imaginea matricei
- sabloanele de tiparire din profilul pyArchInit (de exemplu cele «Modello adArte…»)
- orice alt `.qpt`, ales cu butonul **Sfoglia...** (Rasfoire)

## Bune practici

### 1. order_layer

- Completati INAINTE de a utiliza Managerul Temporal
- Utilizati valori consecutive
- US contemporane = aceeasi valoare

### 2. Vizualizare

- Incepeti de la nivelul 0 (cel mai vechi)
- Procedati in ordine crescatoare
- Utilizati modul cumulativ pentru prezentari

### 3. Documentatie

- Capturati capturi de ecran la niveluri semnificative
- Documentati tranzitiile de faze
- Tipariti plansele pentru rapoarte (una pe nivel)

## Depanare

### Straturile nu sunt vizibile in lista

**Cauza**: Strat fara campul order_layer

**Solutie**:
- Adaugati campul order_layer la strat
- Populati cu valori corespunzatoare

### Nicio schimbare vizuala

**Cauze**:
- order_layer necompletat
- Filtru neaplicat

**Solutii**:
- Verificati valorile order_layer in US
- Verificati ca stratul este selectat

### Discul nu raspunde

**Cauza**: Niciun strat selectat

**Solutie**: Selectati cel putin un strat din lista

## Referinte

### Fisiere sursa
- `tabs/Gis_Time_controller.py` - Interfata principala
- `gui/ui/Gis_Time_controller.ui` - Macheta UI

### Camp baza de date
- `us_table.order_layer` - Index stratigrafic

---

## Tutorial video

### Manager Temporal
`[Placeholder: video_time_manager.mp4]`

**Continut**:
- Configurarea order_layer
- Navigarea temporala
- Tipărirea planșelor
- Integrarea cu Matrix

**Durata estimata**: 15-18 minute

---

*Ultima actualizare: ianuarie 2026*

---

## Animatie interactiva

Explorati animatia interactiva pentru a afla mai multe despre acest subiect.

[Deschideti animatia interactiva](../../animations/pyarchinit_timemanager_animation.html)

---

## Matricea, de la 5.13.44

Matricea din Time Manager nu mai trece prin Graphviz. O deseneaza acelasi motor de compozitie ca panoul **Vezi matricea**, in QGIS si fara subprocese.

- **Este imediata.** Pe situl de exemplu (51 US, 81 relatii) desenul costa cateva milisecunde in loc de circa trei zecimi de secunda, iar procesele `dot` si `tred` care uneori ramaneau blocate au disparut. Perioadele sitului se citesc **o singura data**.
- **In atlas matricea este vectoriala.** Imaginea din plansa este un SVG de cateva zeci de KB in loc de un JPEG de megabytes.
- **Este aceeasi matrice** ca in panoul Extended Matrix: aceleasi benzi de perioada, aceeasi simbologie, aceeasi reducere a redundantelor. Sagetile care **urca** benzile — unde stratigrafia contrazice cronologia — sunt desenate cu **rosu**.
- Matricea contine in continuare doar US vizibile la pozitia curenta a cadranului.

- US care **nu sunt vizibile** la pozitia curenta dar pe care o relatie le citeaza intra totusi in desen, **estompate**: fara ele secventa ar parea rupta.

> **Ce sablon sa alegi.** In selector fiecare sablon este marcat: **✓** are titlul si imaginea matricei, **•** doar harta, **✗** nu are harta. Inainte, alegerea unuia fara acele elemente facea generatorul sa se intoarca fara un cuvant.

> **A face apt orice sablon.** `scripts/prepare_atlas_templates.py`, rulat cu Python-ul din QGIS, scrie langa fiecare sablon o copie cu sufixul « + Time Manager» care poarta titlul si imaginea matricei pe o **pagina noua**. Originalele nu se ating.
