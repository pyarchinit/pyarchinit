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
1. Creeaza mediul virtual in `~/pyarchinit/bin/pottery_venv/`
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
- `gui/ui/Pottery_tools.ui` - Macheta UI

### Foldere
- `~/pyarchinit/bin/pottery_venv/` - Mediu virtual
- `~/pyarchinit/models/` - Modele AI

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

*Ultima actualizare: ianuarie 2026*
