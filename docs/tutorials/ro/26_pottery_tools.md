# Tutorial 26: Instrumente ceramica

## Introducere

**Instrumente ceramica** este un modul avansat pentru procesarea imaginilor de ceramica. Ofera instrumente pentru extragerea imaginilor din PDF-uri, generarea machetelor de planse, procesarea desenelor cu AI (PotteryInk) si alte functionalitati specializate pentru documentarea ceramicii.

### Functionalitati principale

- Extragerea imaginilor din PDF-uri
- Generarea machetelor de planse ceramice
- Procesarea imaginilor cu AI
- Conversia formatelor de desen
- Integrare cu formularul Ceramica

## Acces

### Din meniu
**PyArchInit** > **Instrumente ceramica**

## Interfata

### Panoul principal

```
+--------------------------------------------------+
|              Instrumente ceramica                  |
+--------------------------------------------------+
| [Fila: Extractie PDF]                            |
| [Fila: Generator macheta]                        |
| [Fila: Procesare imagini]                        |
| [Fila: PotteryInk AI]                            |
+--------------------------------------------------+
| [Bara de progres]                                |
| [Mesaje jurnal]                                  |
+--------------------------------------------------+
```

## Fila Extractie PDF

### Functie

Extrage automat imagini din documente PDF care contin planse ceramice.

### Utilizare

1. Selectati fisierul PDF sursa
2. Specificati folderul de destinatie
3. Faceti clic pe **"Extrage"**
4. Imaginile sunt salvate ca fisiere separate

### Optiuni

| Optiune | Descriere |
|---------|-----------|
| DPI | Rezolutia extractiei (150-600) |
| Format | PNG, JPG, TIFF |
| Pagini | Toate sau interval specific |

## Fila Generator macheta

### Functie

Genereaza automat planse ceramice cu macheta standardizata.

### Tipuri de macheta

| Macheta | Descriere |
|---------|-----------|
| Grila | Imagini in grila regulata |
| Secventa | Imagini in secventa numerotata |
| Comparatie | Macheta pentru comparatie |
| Catalog | Format catalog cu legende |

### Utilizare

1. Selectati imaginile de inclus
2. Alegeti tipul de macheta
3. Configurati parametrii (dimensiuni, margini)
4. Generati plansa

### Parametrii machetei

| Parametru | Descriere |
|-----------|-----------|
| Dimensiune pagina | A4, A3, Personalizat |
| Orientare | Portret, Peisaj |
| Margini | Spatiere la margini |
| Spatiere | Distanta intre imagini |
| Legende | Text sub imagini |

## Fila Procesare imagini

### Functie

Procesare in lot a imaginilor de ceramica.

### Operatiuni disponibile

| Operatiune | Descriere |
|------------|-----------|
| Redimensionare | Scalare imagini |
| Decupare | Decupare automata/manuala |
| Rotire | Rotire in grade |
| Convertire | Schimbare format |
| Optimizare | Compresie de calitate |

### Procesare in lot

1. Selectati folderul sursa
2. Alegeti operatiunile de aplicat
3. Specificati destinatia
4. Executati procesarea

## Fila PotteryInk AI

### Functie

Utilizeaza inteligenta artificiala pentru:
- Conversia foto in desen tehnic
- Recunoasterea formei ceramice
- Sugestii de clasificare
- Masurare automata

### Cerinte

- Mediu virtual Python configurat
- Modele AI descarcate (YOLO, etc.)
- GPU recomandat (dar nu obligatoriu)

### Modele AI

**Modele de tușare (PotteryInk).** În fila **🏺 PotteryInk**, grupul **Enhancement Settings**, lista **Model:** afișează modelele PyPotteryInk 2.1.2; butonul **Download** de alături descarcă modelul selectat de pe Hugging Face (`lrncrd/PyPotteryInk`) în dosarul `~/pyarchinit_5/bin/models/` (dacă fișierul există deja, întreabă dacă trebuie descărcat din nou). Fiecare model are aproximativ 38 MB.

| Model (intrare din listă) | Fișier | Utilizare |
|---------------------------|--------|-----------|
| 10k Model (General) | `model_10k.pkl` | Model general pentru desene de ceramică |
| 6h-MCG Model (Bronze Age) | `6h-MCG.pkl` | Desene din epoca bronzului |
| 6h-MC Model (Protohistoric) | `6h-MC.pkl` | Desene protoistorice și istorice |
| 4h-PAINT Model (Historic/Painted) | `4h-PAINT.pkl` | Ceramică istorică și pictată |
| 5h-PAPERGRID Model (Paper grid tables) | `5h_PAPERGRID.pkl` | Desene pe hârtie milimetrică (planșe cu caroiaj); nu suportă umbrele |

**Detectorul de desene (YOLO).** Modelul `BasicModelv8_v01.pt` al PyPotteryLens, care găsește desenele în paginile extrase din PDF-uri (opțiunea **Auto-detect pottery (ML)** și fila **2. Apply Model**), se instalează cu butonul **Download YOLO Model** din fila **PDF Extraction**: dacă găsește o copie locală a PyPotteryLens, o copiază; altfel îl descarcă de pe Hugging Face (`lrncrd/PyPotteryLens`, aproximativ 144 MB) și, dacă descărcarea eșuează, de pe fork-ul GitHub, ca rezervă. Fișierul este salvat în `~/pyarchinit_5/bin/`; o descărcare eșuată nu lasă fișiere incomplete.

### Utilizare

1. Incarcati imaginea ceramica
2. Selectati tipul de procesare
3. Asteptati procesarea AI
4. Verificati si salvati rezultatul

### Tipuri de procesare AI

| Tip | Descriere |
|-----|-----------|
| Conversie tus | Converteste fotografia in desen tehnic |
| Detectie forma | Recunoaste forma vasului |
| Extractie profil | Extrage profilul ceramicii |
| Analiza decoratie | Analizeaza decoratiunile |

## Mediul virtual

### Configurare automata

La prima lansare, Instrumente ceramica:
1. Creeaza mediul virtual in `~/pyarchinit_5/bin/pottery_venv/`
2. Instaleaza dependentele necesare
3. Descarca modelele AI (daca este necesar)

### Dependente

- PyTorch
- Ultralytics (YOLO)
- OpenCV
- Pillow

### Verificarea instalarii

Jurnalul afiseaza starea:
```
Mediu virtual creat
Dependente instalate
Modele descarcate
Instrumente ceramica initializate cu succes!
```

## Integrarea cu baza de date

### Legarea la formularul Ceramica

Imaginile procesate pot fi:
- Legate automat la inregistrarile de ceramica
- Salvate cu metadate corespunzatoare
- Organizate dupa sit/inventar

## Bune practici

### 1. Calitatea imaginilor de intrare

- Rezolutie minima: 300 DPI
- Iluminare uniforma
- Fundal neutru (alb/gri)
- Scala metrica vizibila

### 2. Procesare AI

- Verificati intotdeauna rezultatele AI
- Corectati manual daca este necesar
- Salvati originalele si fisierele procesate

### 3. Organizarea iesirii

- Utilizati denumire consistenta
- Organizati dupa sit/campanie
- Mentineti trasabilitatea

## Depanare

### Mediul virtual nu este creat

**Cauze**:
- Python nu este gasit
- Permisiuni insuficiente

**Solutii**:
- Verificati instalarea Python
- Verificati permisiunile folderului

### Procesare AI lenta

**Cauze**:
- GPU indisponibil
- Imagini prea mari

**Solutii**:
- Reduceti dimensiunea imaginilor
- Utilizati CPU (mai lent dar functioneaza)

### Extractia PDF a esuat

**Cauze**:
- PDF protejat
- Format nesuportat

**Solutii**:
- Verificati protectia PDF-ului
- Incercati cu alt software PDF

## Referinte

### Fisiere sursa
- `tabs/Pottery_tools.py` - Interfata principala
- `modules/utility/pottery_utilities.py` - Utilitare de procesare
- `modules/utility/pottery_models.py` - Registrul modelelor (PotteryInk și detectorul YOLO)
- `gui/ui/Pottery_tools.ui` - Macheta UI

### Foldere
- `~/pyarchinit_5/bin/pottery_venv/` - Mediu virtual
- `~/pyarchinit_5/bin/models/` - Modele PotteryInk (`.pkl`)
- `~/pyarchinit_5/bin/BasicModelv8_v01.pt` - Detectorul YOLO

---

## Tutorial video

### Instrumente ceramica complet
`[Placeholder: video_pottery_tools.mp4]`

**Continut**:
- Extractie PDF
- Generare machete
- Procesare AI
- Integrare cu baza de date

**Durata estimata**: 20-25 minute

---

*Ultima actualizare: octombrie 2026*
