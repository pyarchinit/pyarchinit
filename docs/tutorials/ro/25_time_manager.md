# Tutorial 25: Manager Temporal (Controller temporal GIS)

## Introducere

**Managerul Temporal** (Controller temporal GIS) este un instrument avansat pentru vizualizarea secventei stratigrafice in timp. Permite "navigarea" prin nivelurile stratigrafice utilizand un control temporal, afisand progresiv US de la cele mai recente la cele mai vechi.

### Functionalitati principale

- Vizualizare progresiva a nivelurilor stratigrafice
- Control prin disc/cursor
- Mod cumulativ sau nivel individual
- Generare automata de imagini/video
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
|         Nivel: [SpinBox: 1-N]                   |
+--------------------------------------------------+
| [x] Mod cumulativ (afiseaza <= nivel)            |
+--------------------------------------------------+
| [ ] Afisare Matrix    [Stop] [Generare video]    |
+--------------------------------------------------+
| [Previzualizare Matrix/Imagine]                  |
+--------------------------------------------------+
```

### Controale

| Control | Functie |
|---------|---------|
| Caseta strat | Selectare straturi de controlat |
| Disc | Navigare intre niveluri (rotire) |
| SpinBox | Introducere directa a nivelului |
| Mod cumulativ | Afisare toate nivelurile pana la cel selectat |
| Afisare Matrix | Afisare Harris Matrix sincronizata |

## Campul order_layer

### Ce este order_layer?

Campul `order_layer` defineste ordinea de afisare stratigrafice:
- **1** = Nivelul cel mai recent (suprafata)
- **N** = Nivelul cel mai vechi (adancime)

### Completarea order_layer

In formularul US, campul **"Index stratigrafic"**:
1. Atribuiti valori crescatoare de la suprafata
2. US contemporane pot avea aceeasi valoare
3. Urmati secventa Matricei

### Exemplu

| US | order_layer | Descriere |
|----|-------------|-----------|
| US001 | 1 | Humus de suprafata |
| US002 | 2 | Strat arat |
| US003 | 3 | Prabusire |
| US004 | 4 | Podea de utilizare |
| US005 | 5 | Fundatie |

## Moduri de vizualizare

### Modul nivel individual

Caseta de bifare **NEACTIVATA**:
- Afiseaza DOAR US de la nivelul selectat
- Util pentru izolarea straturilor individuale
- Vizualizare "sectiune"

### Modul cumulativ

Caseta de bifare **ACTIVATA**:
- Afiseaza toate US pana la nivelul selectat
- Simuleaza excavarea progresiva
- Vizualizare mai realista

## Integrarea cu Matrix

### Vizualizare sincronizata

Cu caseta de bifare **"Afisare Matrix"** activata:
- Harris Matrix apare in panou
- Se actualizeaza sincronizat cu nivelul
- Evidentiaza US nivelului curent

### Generare imagini

Managerul Temporal poate genera:
- Captura de ecran pentru fiecare nivel
- Secventa de imagini
- Video time-lapse

## Generare video/imagini

### Proces

1. Selectati straturile de inclus
2. Configurati intervalul de niveluri (min-max)
3. Faceti clic pe **"Generare video"**
4. Asteptati procesarea
5. Iesire in folderul desemnat

### Iesire

- Imagini PNG pentru fiecare nivel
- Optional: video MP4 compilat

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
1. Activati "Afisare Matrix"
2. Generati capturi de ecran semnificative
3. Optional: generati video
```

## Sabloane de macheta

### Incarcarea sabloanelor

Managerul Temporal suporta sabloane QGIS pentru:
- Machete de tiparire personalizate
- Antete si legende
- Formate standard

### Sabloane disponibile

In folderul `resources/templates/`:
- Sablon de baza
- Sablon cu Matrix
- Sablon pentru video

## Bune practici

### 1. order_layer

- Completati INAINTE de a utiliza Managerul Temporal
- Utilizati valori consecutive
- US contemporane = aceeasi valoare

### 2. Vizualizare

- Incepeti de la nivelul 1 (suprafata)
- Procedati in ordine crescatoare
- Utilizati modul cumulativ pentru prezentari

### 3. Documentatie

- Capturati capturi de ecran la niveluri semnificative
- Documentati tranzitiile de faze
- Generati video pentru rapoarte

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
- Generarea video
- Integrarea cu Matrix

**Durata estimata**: 15-18 minute

---

*Ultima actualizare: ianuarie 2026*

---

## Animatie interactiva

Explorati animatia interactiva pentru a afla mai multe despre acest subiect.

[Deschideti animatia interactiva](../../animations/pyarchinit_timemanager_animation.html)
