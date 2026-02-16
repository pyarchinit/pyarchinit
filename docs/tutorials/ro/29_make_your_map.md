# Tutorial 29: Creeaza-ti harta

## Introducere

**Creeaza-ti harta** este functia PyArchInit pentru generarea hartilor profesionale si a machetelor de tiparire direct din vizualizarea curenta QGIS. Utilizeaza sabloane predefinite de macheta pentru a crea iesiri cartografice standardizate.

### Functionalitati

- Generare rapida de harti din vizualizarea curenta
- Sabloane predefinite pentru diverse formate
- Personalizarea antetului si legendei
- Export in PDF, PNG, SVG

## Acces

### Din bara de instrumente
Pictograma **"Make your Map"** (imprimanta) in bara de instrumente PyArchInit

### Din meniu
**PyArchInit** > **Make your Map**

## Utilizare de baza

### Generare rapida

1. Configurati vizualizarea dorita a hartii in QGIS
2. Setati zoom-ul si extensia corecte
3. Faceti clic pe **"Make your Map"**
4. Selectati sablonul dorit
5. Introduceti titlul si informatiile
6. Generati harta

## Sabloane disponibile

### Formate standard

| Sablon | Format | Orientare | Utilizare |
|--------|--------|-----------|-----------|
| A4 Portret | A4 | Portret | Documentatie standard |
| A4 Peisaj | A4 | Peisaj | Vederi extinse |
| A3 Portret | A3 | Portret | Planse detaliate |
| A3 Peisaj | A3 | Peisaj | Planimetrii |

### Elementele sablonului

Fiecare sablon include:
- **Zona hartii** - Vizualizarea principala
- **Antet** - Titlu si informatii proiect
- **Scara** - Bara de scara grafica
- **Nord** - Sageata nordului
- **Legenda** - Simboluri straturi
- **Cartusu** - Informatii tehnice

## Personalizare

### Informatii editabile

| Camp | Descriere |
|------|-----------|
| Titlu | Numele hartii |
| Subtitlu | Descriere suplimentara |
| Sit | Numele sitului arheologic |
| Arie | Numarul ariei |
| Data | Data crearii |
| Autor | Numele autorului |
| Scara | Scara de reprezentare |

### Stilul hartii

Inainte de generare:
1. Configurati stilurile straturilor in QGIS
2. Activati/dezactivati straturile dorite
3. Setati etichetele
4. Verificati legenda

## Export

### Formate disponibile

| Format | Utilizare | Calitate |
|--------|-----------|----------|
| PDF | Tiparire, arhivare | Vectorial |
| PNG | Web, prezentari | Raster |
| SVG | Editare, publicare | Vectorial |
| JPG | Web, previzualizare | Raster comprimat |

### Rezolutie

| DPI | Utilizare |
|-----|-----------|
| 96 | Ecran/previzualizare |
| 150 | Publicare web |
| 300 | Tiparire standard |
| 600 | Tiparire de inalta calitate |

## Integrarea cu Managerul Temporal

### Generarea secventelor

In combinatie cu Managerul Temporal:
1. Configurati Managerul Temporal
2. Pentru fiecare nivel stratigrafic:
   - Setati nivelul
   - Generati harta
   - Salvati cu nume progresiv

### Iesire animatie

Serii de harti pentru:
- Prezentari
- Video time-lapse
- Documentatie progresiva

## Flux de lucru tipic

### 1. Pregatire

```
1. Incarcati straturile necesare
2. Configurati stiluri corespunzatoare
3. Setati sistemul de referinta al coordonatelor
4. Definiti extensia hartii
```

### 2. Configurarea vizualizarii

```
1. Faceti zoom la zona de interes
2. Activati/dezactivati straturile
3. Verificati etichetele
4. Verificati legenda
```

### 3. Generare

```
1. Faceti clic pe Make your Map
2. Selectati sablonul
3. Completati informatiile
4. Alegeti formatul de export
5. Salvati
```

## Bune practici

### 1. Inainte de generare

- Verificati completitudinea datelor
- Verificati stilurile straturilor
- Setati scara corespunzatoare

### 2. Sabloane

- Utilizati sabloane consistente in proiect
- Personalizati antetele pentru institutie
- Mentineti standardele cartografice

### 3. Iesire

- Salvati in rezolutie inalta pentru tiparire
- Mentineti o copie PDF pentru arhiva
- Utilizati denumire descriptiva

## Personalizarea sabloanelor

### Modificarea sabloanelor

Sabloanele QGIS pot fi modificate:
1. Deschideti Managerul de machete in QGIS
2. Modificati sablonul existent
3. Salvati ca sablon nou
4. Disponibil in Make your Map

### Crearea sabloanelor

1. Creati o macheta noua in QGIS
2. Adaugati elementele necesare
3. Configurati variabilele pentru campuri dinamice
4. Salvati in folderul de sabloane

## Depanare

### Harta goala

**Cauze**:
- Niciun strat activ
- Extensie gresita

**Solutii**:
- Activati straturile vizibile
- Faceti zoom la zona cu date

### Legenda incompleta

**Cauza**: Straturile nu sunt configurate corect

**Solutie**: Verificati proprietatile straturilor in QGIS

### Exportul a esuat

**Cauze**:
- Calea nu permite scriere
- Format nesuportat

**Solutii**:
- Verificati permisiunile folderului
- Alegeti un format diferit

## Referinte

### Fisiere sursa
- `pyarchinitPlugin.py` - Functia runPrint
- Sabloane in folderul `resources/templates/`

### QGIS
- Manager de machete
- Compozitor de tiparire

---

## Tutorial video

### Creeaza-ti harta
`[Placeholder: video_make_map.mp4]`

**Continut**:
- Pregatirea vizualizarii
- Utilizarea sabloanelor
- Personalizare
- Formate de export

**Durata estimata**: 10-12 minute

---

*Ultima actualizare: ianuarie 2026*

---

## Animatie interactiva

Explorati animatia interactiva pentru a afla mai multe despre acest subiect.

[Deschideti animatia interactiva](../../animations/pyarchinit_create_map_animation.html)
