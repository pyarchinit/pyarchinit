# Tutorial 11: Matricea Harris

## Introducere

**Matricea Harris** (sau diagrama stratigrafică) este un instrument fundamental în arheologie pentru reprezentarea grafică a relațiilor stratigrafice dintre diferitele Unități Stratigrafice (US). PyArchInit generează automat Matricea Harris din relațiile stratigrafice introduse în fișele US.

### Ce este Matricea Harris?

Matricea Harris este o diagramă care reprezintă:
- **Secvența temporală** a US-urilor (de la cel mai recent în vârf la cel mai vechi în bază)
- **Relațiile fizice** dintre US-uri (acoperă/acoperit de, taie/tăiat de, se leagă de)
- **Periodizarea** săpăturii (grupare pe perioade și faze)

### Tipuri de Relații Reprezentate

| Relație | Semnificație | Reprezentare |
|---------|-------------|--------------|
| Acoperă/Acoperit de | Suprapunere fizică | Linie continuă descendentă |
| Taie/Tăiat de | Acțiune negativă (interfață) | Linie punctată |
| Se leagă de/Echivalent cu | Contemporaneitate | Linie bidirecțională orizontală |
| Umple/Umplut de | Umplerea unei tăieturi | Linie continuă |
| Se sprijină pe/Susține | Suport structural | Linie continuă |

## Accesarea Funcției

### Din Meniul Principal
1. **PyArchInit** în bara de meniu
2. Selectați **Matricea Harris**

### Din Fișa US
1. Deschideți Fișa US
2. Tab-ul **Hartă**
3. Butonul **„Export Matrice"** sau **„Vizualizare Matrice"**

### Prerequisite
- Bază de date conectată corect
- US-uri cu relații stratigrafice completate
- Periodizare definită (opțional dar recomandat)
- Graphviz instalat pe sistem

## Configurarea Matricei

### Fereastra de Configurare (Setting_Matrix)

Înaintea generării, apare o fereastră de configurare:

#### Tab-ul General

| Câmp | Descriere | Valoare Recomandată |
|------|-----------|---------------------|
| DPI | Rezoluția imaginii | 150-300 |
| Afișare Perioade | Grupare US pe perioadă/fază | Da |
| Afișare Legendă | Include legendă în diagramă | Da |

#### Tab-ul Noduri „Ante/Post" (Relații Normale)

| Parametru | Descriere | Opțiuni |
|-----------|-----------|---------|
| Formă nod | Formă geometrică | box, ellipse, diamond |
| Culoare umplere | Culoare internă | white, lightblue, etc. |
| Stil | Aspect margine | solid, dashed |
| Lățime linie | Grosime margine | 0.5 - 2.0 |
| Tip săgeată | Cap de săgeată | normal, diamond, none |
| Dimensiune săgeată | Dimensiune cap | 0.5 - 1.5 |

#### Tab-ul Noduri „Negative" (Tăieturi)

| Parametru | Descriere | Opțiuni |
|-----------|-----------|---------|
| Formă nod | Formă geometrică | box, ellipse, diamond |
| Culoare umplere | Culoare distinctivă | gray, lightcoral |
| Stil linie | Aspect conexiune | dashed |

#### Tab-ul Noduri „Contemporane"

| Parametru | Descriere | Opțiuni |
|-----------|-----------|---------|
| Formă nod | Formă geometrică | box, ellipse |
| Culoare umplere | Culoare distinctivă | lightyellow, white |
| Stil linie | Aspect conexiune | solid |
| Săgeată | Tip conexiune | none (bidirecțional) |

## Tipuri de Export

### 1. Export Matrice Standard

Generează matricea de bază cu:
- Toate relațiile stratigrafice
- Grupare pe perioade/faze
- Aspect vertical (TB - De sus în jos)

**Rezultat**: `pyarchinit_Matrix_folder/Harris_matrix.jpg`

### 2. Export Matrice Extinsă (2ED)

Versiune extinsă cu:
- Informații suplimentare pe noduri (US + definiție + datare)
- Conexiuni speciale (>, >>)
- Export format GraphML

**Rezultat**: `pyarchinit_Matrix_folder/Harris_matrix2ED.jpg`

### 3. Vizualizare Matrice (Vizualizare Rapidă)

Pentru vizualizare rapidă fără opțiuni de configurare:
- Folosește setări implicite
- Generare mai rapidă
- Ideal pentru verificări rapide

## Procesul de Generare

### Pasul 1: Colectarea Datelor

Sistemul colectează automat:
```
Pentru fiecare US din situl/zona selectată:
  - Număr US
  - Tip unitate (US/USM)
  - Relații stratigrafice
  - Perioadă și fază inițială
  - Definiție interpretativă
```

### Pasul 2: Construcția Grafului

Crearea relațiilor:
```
Secvență (Ante/Post):
  US1 -> US2 (US1 acoperă US2)

Negativă (Tăieturi):
  US3 -> US4 (US3 taie US4)

Contemporană:
  US5 <-> US6 (US5 se leagă de US6)
```

### Pasul 3: Gruparea pe Perioade

Grupare ierarhică:
```
Sit
  └── Zonă
      └── Perioadă 1 : Fază 1 : „Epoca Romană"
          ├── US101
          ├── US102
          └── US103
      └── Perioadă 1 : Fază 2 : „Antichitatea Târzie"
          ├── US201
          └── US202
```

### Pasul 4: Reducerea Tranzitivă (tred)

Comanda Graphviz `tred` elimină relațiile redundante:
- Dacă US1 -> US2 și US2 -> US3, elimină US1 -> US3
- Simplifică diagrama
- Păstrează doar relațiile directe

### Pasul 5: Redare Finală

Generarea imaginii în multiple formate:
- DOT (sursă Graphviz)
- JPG (imagine comprimată)
- PNG (imagine fără pierderi)

## Interpretarea Matricei

### Citire Verticală

```
     [US cel mai recent]
           ↓
        US 001
           ↓
        US 002
           ↓
        US 003
           ↓
     [US cel mai vechi]
```

### Citirea Clusterelor

Casetele colorate reprezintă perioade/faze:
- **Albastru deschis**: Cluster perioadă
- **Galben**: Cluster fază
- **Gri**: Fundalul sitului

### Tipuri de Conexiuni

```
─────────→  Linie continuă = Acoperă/Umple/Se sprijină pe
- - - - →  Linie punctată = Taie
←────────→  Bidirecțional = Contemporan/Echivalent cu
```

### Culorile Nodurilor

| Culoare | Semnificație Tipică |
|---------|---------------------|
| Alb | US depozit normal |
| Gri | US negativă (tăietură) |
| Galben | US contemporană |
| Albastru | US cu relații speciale |

## Depanare

### Eroare: „Buclă Detectată"

**Cauză**: Există cicluri în relații (A acoperă B, B acoperă A)

**Soluție**:
1. Deschideți Fișa US
2. Verificați relațiile US-urilor indicate
3. Corectați relațiile circulare
4. Regenerați matricea

### Eroare: „Comanda tred nu a fost găsită"

**Cauză**: Graphviz nu este instalat

**Soluție**:
- **Windows**: Instalați Graphviz de la graphviz.org
- **macOS**: `brew install graphviz`
- **Linux**: `sudo apt install graphviz`

### Matricea Nu Este Generată

**Cauze posibile**:
1. Nu sunt introduse relații stratigrafice
2. US fără perioadă/fază atribuită
3. Probleme de permisiuni în folderul de ieșire

**Verificare**:
1. Verificați că US-urile au relații
2. Verificați periodizarea
3. Verificați permisiunile pe `pyarchinit_Matrix_folder`

### Matricea Prea Mare

**Problemă**: Imagine ilizibilă cu multe US-uri

**Soluții**:
1. Reduceți DPI (100-150)
2. Filtrați pe o zonă specifică
3. Folosiți Vizualizare Matrice pentru zone individuale
4. Exportați în format vectorial (DOT) și deschideți cu yEd

## Fișierele Generate și Ieșiri

### Folderul de Ieșire

```
~/pyarchinit/pyarchinit_Matrix_folder/
├── Harris_matrix.dot           # Sursă Graphviz
├── Harris_matrix_tred.dot      # După reducerea tranzitivă
├── Harris_matrix_tred.dot.jpg  # Imagine JPG finală
├── Harris_matrix_tred.dot.png  # Imagine PNG finală
├── Harris_matrix2ED.dot        # Versiune extinsă
├── Harris_matrix2ED_graphml.dot # Pentru export GraphML
└── matrix_error.txt            # Jurnal erori
```

### Utilizarea Fișierelor

| Fișier | Utilizare |
|--------|-----------|
| *.jpg/*.png | Inserare în rapoarte |
| *.dot | Editare cu editor Graphviz |
| _graphml.dot | Import în yEd pentru editare avansată |

## Bune Practici

### 1. Înainte de Generare

- Verificați completitudinea relațiilor stratigrafice
- Verificați absența ciclurilor
- Atribuiți perioadă/fază tuturor US-urilor
- Completați definiția interpretativă

### 2. În Timpul Compilării US

- Introduceți relații bidirecționale corecte
- Folosiți terminologie consistentă
- Verificați zona corectă în relații

### 3. Optimizarea Ieșirii

- Pentru tipărire: DPI 300
- Pentru ecran: DPI 150
- Pentru săpături complexe: împărțiți pe zone

### 4. Controlul Calității

- Comparați matricea cu documentația de săpătură
- Verificați secvențele logice
- Verificați grupările pe perioade

## Integrare cu Alte Instrumente

### Export pentru yEd

Fișierul `_graphml.dot` poate fi deschis în yEd pentru:
- Editarea manuală a aspectului
- Adăugarea de adnotări
- Exportul în diferite formate

### Export pentru s3egraph

PyArchInit suportă exportul pentru sistemul s3egraph:
- Format compatibil
- Menține relațiile stratigrafice
- Suport pentru vizualizare 3D

## Referințe

### Fișiere Sursă
- `tabs/Interactive_matrix.py` - Interfață interactivă
- `modules/utility/pyarchinit_matrix_exp.py` - Clasele HarrisMatrix și ViewHarrisMatrix

### Baza de Date
- `us_table` - Date și relații US
- `periodizzazione_table` - Perioade și faze

### Dependențe
- Graphviz (dot, tred)
- Biblioteca Python graphviz

---

## Tutorial Video

### Matricea Harris - Generare Completă
`[Substituent: video_matrix_harris.mp4]`

**Conținut**:
- Configurarea setărilor
- Generarea matricei
- Interpretarea rezultatelor
- Rezolvarea problemelor frecvente

**Durată estimată**: 15-20 minute

---

*Ultima actualizare: ianuarie 2026*

---

## Animație Interactivă

Explorați animația interactivă pentru a afla mai multe despre acest subiect.

[Deschideți Animația Interactivă](../../animations/harris_matrix_animation.html)
