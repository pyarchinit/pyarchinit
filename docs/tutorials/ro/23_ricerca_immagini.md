# Tutorial 23: Cautarea imaginilor

## Introducere

Functia **Cautare imagini** va permite sa cautati rapid imagini in baza de date PyArchInit filtrand dupa sit, tip de entitate si alte criterii. Este un instrument complementar Managerului Media pentru cautarea globala.

## Acces

### Din meniu
**PyArchInit** > **Cautare imagini**

## Interfata

### Panoul de cautare

```
+--------------------------------------------------+
|           Cautare imagini                         |
+--------------------------------------------------+
| Filtre:                                           |
|   Sit: [ComboBox]                                |
|   Tip entitate: [-- Toate -- | US | Ceramica | ...]|
|   [ ] Doar imagini neetichetate                  |
+--------------------------------------------------+
| [Cautare]  [Golire]                              |
+--------------------------------------------------+
| Rezultate:                                        |
|  +------+  +------+  +------+                    |
|  | img  |  | img  |  | img  |                    |
|  | info |  | info |  | info |                    |
|  +------+  +------+  +------+                    |
+--------------------------------------------------+
| [Deschide imaginea] [Export] [Salt la inregistrare]|
+--------------------------------------------------+
```

### Filtre disponibile

| Filtru | Descriere |
|--------|-----------|
| Sit | Selectati un sit specific sau toate |
| Tip entitate | US, Ceramica, Materiale, Mormant, Structura, UT |
| Doar neetichetate | Afisare doar imagini fara legaturi |

### Tipuri de entitati

| Tip | Descriere |
|-----|-----------|
| -- Toate -- | Toate entitatile |
| US | Unitati Stratigrafice |
| Ceramica | Ceramica |
| Materiale | Descoperiri/Inventar |
| Mormant | Inhumari |
| Structura | Structuri |
| UT | Unitati Topografice |

## Functionalitati

### Cautare de baza

1. Selectati filtrele dorite
2. Faceti clic pe **"Cautare"**
3. Vizualizati rezultatele in grila

### Actiuni pe rezultate

| Buton | Functie |
|-------|---------|
| Deschide imaginea | Vizualizare imagine la dimensiune originala |
| Export | Exportul imaginii selectate |
| Salt la inregistrare | Deschidere formular entitate legata |
| Deschide Manager Media | Deschidere Manager Media cu imaginea selectata |

### Meniu contextual (clic dreapta)

- **Deschide imaginea**
- **Exporta imaginea...**
- **Salt la inregistrare**

### Cautarea imaginilor neetichetate

Caseta de bifare **"Doar imagini neetichetate"**:
- Gaseste imaginile din baza de date fara legaturi
- Utila pentru curatare si organizare
- Permite identificarea imaginilor de catalogat

## Flux de lucru tipic

### 1. Gasirea imaginilor unui sit

```
1. Selectati situl din ComboBox
2. Lasati "-- Toate --" pentru tipul entitatii
3. Faceti clic pe Cautare
4. Navigati prin rezultate
```

### 2. Gasirea imaginilor unei US specifice

```
1. Selectati situl
2. Selectati "US" ca tip de entitate
3. Faceti clic pe Cautare
4. Dublu clic pentru deschiderea imaginii
```

### 3. Identificarea imaginilor necatalogate

```
1. Selectati situl (sau toate)
2. Activati "Doar imagini neetichetate"
3. Faceti clic pe Cautare
4. Pentru fiecare rezultat:
   - Deschideti imaginea
   - Identificati continutul
   - Legati prin Manager Media
```

## Export

### Export imagine individuala

1. Selectati imaginea in rezultate
2. Faceti clic pe **"Export"** sau meniu contextual
3. Selectati destinatia
4. Salvati

### Export multiplu

Pentru exportul mai multor imagini, utilizati functia dedicata **Export imagini** (Tutorial 24).

## Bune practici

### 1. Cautare eficienta

- Utilizati filtre specifice pentru rezultate tintite
- Incepeti cu filtre largi, apoi restrangeti
- Utilizati periodic cautarea imaginilor neetichetate

### 2. Organizare

- Catalogati regulat imaginile neetichetate
- Verificati legaturile dupa import
- Mentineti o denumire consistenta

## Depanare

### Fara rezultate

**Cauze**:
- Filtre prea restrictive
- Nu exista imagini pentru criteriile alese

**Solutii**:
- Largiti filtrele
- Verificati ca datele exista

### Imaginea nu poate fi vizualizata

**Cauze**:
- Fisier negasit
- Format nesuportat

**Solutii**:
- Verificati calea fisierului
- Verificati formatul imaginii

## Referinte

### Fisiere sursa
- `tabs/Image_search.py` - Interfata de cautare
- `gui/ui/pyarchinit_image_search_dialog.ui` - Macheta UI

### Baza de date
- `media_table` - Date media
- `media_to_entity_table` - Legaturi

---

## Tutorial video

### Cautarea imaginilor
`[Placeholder: video_ricerca_immagini.mp4]`

**Continut**:
- Utilizarea filtrelor
- Cautare avansata
- Exportul rezultatelor

**Durata estimata**: 8-10 minute

---

*Ultima actualizare: ianuarie 2026*
