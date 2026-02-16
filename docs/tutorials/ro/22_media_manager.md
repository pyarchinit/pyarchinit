# Tutorial 22: Manager Media

## Introducere

**Managerul Media** este instrumentul central al PyArchInit pentru gestionarea imaginilor si continutului multimedia asociat cu inregistrarile arheologice. Permite legarea fotografiilor, desenelor, videoclipurilor si a altor fisiere media de US, descoperiri, morminte, structuri si alte entitati.

### Functionalitati principale

- Gestionarea centralizata a tuturor fisierelor media
- Legarea la entitati arheologice (US, Descoperiri, Ceramica, Morminte, Structuri, UT)
- Vizualizare miniaturi si imagini la dimensiune completa
- Etichetare si categorizare
- Cautare avansata
- Integrare GPT pentru analiza imaginilor

## Acces

### Din meniu
**PyArchInit** > **Manager Media**

### Din bara de instrumente
Pictograma **Manager Media** in bara de instrumente PyArchInit

## Interfata

### Panoul principal

```
+----------------------------------------------------------+
|                    Manager Media                          |
+----------------------------------------------------------+
| Sit: [ComboBox]  Arie: [ComboBox]  US: [ComboBox]        |
+----------------------------------------------------------+
| [Grila miniaturi imagini]                                 |
|  +------+  +------+  +------+  +------+                  |
|  | img1 |  | img2 |  | img3 |  | img4 |                  |
|  +------+  +------+  +------+  +------+                  |
|  +------+  +------+  +------+  +------+                  |
|  | img5 |  | img6 |  | img7 |  | img8 |                  |
|  +------+  +------+  +------+  +------+                  |
+----------------------------------------------------------+
| Etichete: [Lista etichetelor asociate]                    |
+----------------------------------------------------------+
| [Navigare] << < Inregistrarea X din Y > >>                |
+----------------------------------------------------------+
```

### Filtre de cautare

| Camp | Descriere |
|------|-----------|
| Sit | Filtrare dupa situl arheologic |
| Arie | Filtrare dupa aria de excavare |
| US | Filtrare dupa Unitate Stratigrafice |
| Cod structura | Filtrare dupa codul structurii |
| Nr. structura | Filtrare dupa numarul structurii |

### Controale miniaturi

| Control | Functie |
|---------|---------|
| Cursor dimensiune | Ajustarea dimensiunii miniaturilor |
| Dublu clic | Deschidere imagine la dimensiune originala |
| Selectie multipla | Ctrl+clic pentru selectarea mai multor imagini |

## Gestionarea fisierelor media

### Adaugarea imaginilor noi

1. Deschideti Managerul Media
2. Selectati situl de destinatie
3. Faceti clic pe **"Inregistrare noua"** sau utilizati meniul contextual
4. Selectati imaginile de adaugat
5. Completati metadatele

### Legarea fisierelor media la entitati

1. Selectati imaginea in grila
2. In panoul Etichete, selectati:
   - **Tipul entitatii**: US, Descoperire, Ceramica, Mormant, Structura, UT
   - **Identificator**: Numarul/codul entitatii
3. Faceti clic pe **"Leaga"**

### Tipuri de entitati suportate

| Tip | Tabel BD | Descriere |
|-----|----------|-----------|
| US | us_table | Unitati Stratigrafice |
| DESCOPERIRE | inventario_materiali_table | Descoperiri/Materiale |
| CERAMICA | pottery_table | Ceramica |
| MORMANT | tomba_table | Inhumari |
| STRUCTURA | struttura_table | Structuri |
| UT | ut_table | Unitati Topografice |

### Vizualizarea imaginii originale

- **Dublu clic** pe miniatura
- Deschide vizualizatorul cu:
  - Zoom (rotita mouse-ului)
  - Deplasare (tragere)
  - Rotire
  - Masurare

## Functionalitati avansate

### Cautare avansata

Managerul Media suporta cautarea dupa:
- Numele fisierului
- Data intrarii
- Entitatea legata
- Etichete/categorii

### Integrare GPT

Butonul **"GPT Sketch"** pentru:
- Analiza automata a imaginii
- Generarea descrierilor
- Sugestii de clasificare

### Incarcare la distanta

Suport pentru imagini pe servere la distanta:
- URL-uri directe
- Servere FTP
- Stocare cloud

## Baza de date

### Tabele implicate

| Tabel | Descriere |
|-------|-----------|
| `media_table` | Metadate media |
| `media_thumb_table` | Miniaturi |
| `media_to_entity_table` | Legaturi cu entitatile |

### Clase mapper

- `MEDIA` - Entitatea media principala
- `MEDIA_THUMB` - Miniaturi
- `MEDIATOENTITY` - Relatia media-entitate

## Bune practici

### 1. Organizarea fisierelor

- Utilizati nume de fisiere descriptive
- Organizati dupa sit/arie/an
- Pastrati copii de siguranta ale originalelor

### 2. Metadate

- Completati intotdeauna situl si aria
- Adaugati descrieri semnificative
- Utilizati etichete consistente

### 3. Calitatea imaginii

- Rezolutie minima recomandata: 1920x1080
- Format: JPG pentru fotografii, PNG pentru desene
- Compresie moderata

### 4. Legaturi

- Legati fiecare imagine de entitatile relevante
- Verificati legaturile dupa importul in lot
- Utilizati cautarea pentru imaginile nelegate

## Depanare

### Miniaturile nu sunt afisate

**Cauze**:
- Cale imagine gresita
- Fisier lipsa
- Probleme de permisiuni

**Solutii**:
- Verificati calea in baza de date
- Verificati existenta fisierului
- Verificati permisiunile folderului

### Imaginea nu poate fi legata

**Cauze**:
- Entitatea nu exista
- Tip de entitate gresit

**Solutii**:
- Verificati ca inregistrarea exista
- Verificati tipul de entitate selectat

## Referinte

### Fisiere sursa
- `tabs/Image_viewer.py` - Interfata principala
- `modules/utility/pyarchinit_media_utility.py` - Utilitare media

### Baza de date
- `media_table` - Date media
- `media_to_entity_table` - Legaturi

---

## Tutorial video

### Manager Media complet
`[Placeholder: video_media_manager.mp4]`

**Continut**:
- Adaugarea imaginilor
- Legarea la entitati
- Cautare si filtre
- Functionalitati avansate

**Durata estimata**: 15-18 minute

---

*Ultima actualizare: ianuarie 2026*

---

## Animatie interactiva

Explorati animatia interactiva pentru a afla mai multe despre acest subiect.

[Deschideti animatia interactiva](../../animations/pyarchinit_media_manager_animation.html)
