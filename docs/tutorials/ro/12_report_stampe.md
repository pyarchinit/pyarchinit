# Tutorial 12: Rapoarte și Tipăriri PDF

## Introducere

PyArchInit oferă un sistem complet de generare a **rapoartelor PDF** pentru toate fișele arheologice. Această funcție permite exportul documentației în format tipăribil, conform standardelor ministeriale și gata pentru arhivare.

### Tipuri de Rapoarte Disponibile

| Tip | Descriere | Fișa Sursă |
|-----|-----------|------------|
| Fișe US | Rapoarte complete US/USM | Fișa US |
| Index US | Lista sintetică a US-urilor | Fișa US |
| Fișe Periodizare | Rapoarte perioadă/fază | Fișa Periodizare |
| Fișe Structură | Rapoarte structuri | Fișa Structură |
| Fișe Artefacte | Rapoarte inventar materiale | Fișa Inventar |
| Fișe Morminte | Rapoarte funerare | Fișa Mormânt |
| Fișe Probe | Rapoarte probe | Fișa Probe |
| Fișe Individ | Rapoarte antropologice | Fișa Individ |

## Accesarea Funcției

### Din Meniul Principal
1. **PyArchInit** în bara de meniu
2. Selectați **Export PDF**

### Din Bara de Instrumente
Faceți clic pe pictograma **PDF** din bara de instrumente PyArchInit

## Interfața de Export

### Prezentarea Ferestrei

Fereastra de export PDF prezintă:

```
+------------------------------------------+
|        PyArchInit - Export PDF            |
+------------------------------------------+
| Sit: [ComboBox selectare sit]     [v]   |
+------------------------------------------+
| Fișe de exportat:                        |
| [x] Fișe US                             |
| [x] Fișe Periodizare                    |
| [x] Fișe Structură                      |
| [x] Fișe Artefacte                      |
| [x] Fișe Morminte                       |
| [x] Fișe Probe                          |
| [x] Fișe Individ                        |
+------------------------------------------+
| [Deschide Folder]  [Export PDF]  [Anulare]|
+------------------------------------------+
```

### Selectarea Sitului

| Câmp | Descriere |
|------|-----------|
| ComboBox Sit | Lista tuturor siturilor din baza de date |

**Notă**: Exportul se face per sit individual. Pentru a exporta mai multe situri, repetați operația.

### Casetele de Selectare

Fiecare casetă activează exportul unui tip specific:

| Casetă | Generează |
|--------|-----------|
| Fișe US | Fișe complete + Index US |
| Fișe Periodizare | Fișe perioade + Index |
| Fișe Structură | Fișe structuri + Index |
| Fișe Artefacte | Fișe materiale + Index |
| Fișe Morminte | Fișe funerare + Index |
| Fișe Probe | Fișe probe + Index |
| Fișe Individ | Fișe antropologice + Index |

## Procesul de Export

### Pasul 1: Selectarea Datelor

```python
# Sistemul execută pentru fiecare tip selectat:
1. Interogare bază de date pentru situl selectat
2. Sortarea datelor (după număr, zonă, etc.)
3. Pregătirea listei pentru generare
```

### Pasul 2: Generarea PDF

Pentru fiecare tip de fișă:
1. **Fișă individuală**: PDF detaliat pentru fiecare înregistrare
2. **Index**: PDF rezumativ cu toate înregistrările

### Pasul 3: Salvarea

Ieșire în folderul:
```
~/pyarchinit/pyarchinit_PDF_folder/
```

## Conținutul Rapoartelor

### Fișa US

Informații incluse:
- **Date de identificare**: Sit, Zonă, Număr US, Tip unitate
- **Definiții**: Stratigrafică, Interpretativă
- **Descriere**: Text descriptiv complet
- **Interpretare**: Analiză interpretativă
- **Periodizare**: Perioadă/Fază Inițială/Finală
- **Caracteristici fizice**: Culoare, consistență, formare
- **Măsurători**: Cote min/max, dimensiuni
- **Relații**: Lista relațiilor stratigrafice
- **Documentație**: Referințe grafice și fotografice
- **Date USM**: (dacă este cazul) Tehnică de construcție, materiale

### Index US

Tabel rezumativ cu coloane:
| Sit | Zonă | US | Def. Stratigrafică | Def. Interpretativă | Perioadă |

### Fișa Periodizare

- Sit
- Număr perioadă
- Număr fază
- Cronologie inițială/finală
- Datare extinsă
- Descrierea perioadei

### Fișa Structură

- Date de identificare (Sit, Cod, Număr)
- Categorie, Tip, Definiție
- Descriere și Interpretare
- Periodizare
- Materiale folosite
- Elemente structurale
- Relații structuri
- Măsurători și cote

### Fișa Artefacte

- Sit, Număr inventar
- Tip artefact, Definiție
- Descriere
- Proveniență (Zonă, US)
- Stare de conservare
- Datare
- Elemente și măsurători
- Bibliografie

### Fișa Mormânt

- Date de identificare
- Rit (înhumare/incinerare)
- Tip de înmormântare și depunere
- Descriere și interpretare
- Inventar funerar (prezență, tip, descriere)
- Periodizare
- Cote ale structurii și individului
- US asociate

### Fișa Probe

- Sit, Număr probă
- Tip probă
- Descriere
- Proveniență (Zonă, US)
- Locul de conservare
- Număr cutie

### Fișa Individ

- Date de identificare
- Sex, Vârstă (min/max), Clase de vârstă
- Poziția scheletului
- Orientare (ax, azimut)
- Stare de conservare
- Observații

## Limbi Suportate

Sistemul generează rapoarte în funcție de limba sistemului:

| Limbă | Cod | Șablon |
|-------|-----|--------|
| Italiană | IT | `build_*_sheets()` |
| Germană | DE | `build_*_sheets_de()` |
| Engleză | EN | `build_*_sheets_en()` |

Limba este detectată automat din setările QGIS.

## Folderul de Ieșire

### Cale Standard
```
~/pyarchinit/pyarchinit_PDF_folder/
```

### Structura Fișierelor Generate

```
pyarchinit_PDF_folder/
├── US_[sit]_forms.pdf           # Fișe US complete
├── US_[sit]_index.pdf           # Index US
├── Periodization_[sit].pdf      # Fișe periodizare
├── Structure_[sit]_forms.pdf    # Fișe structuri
├── Structure_[sit]_index.pdf    # Index structuri
├── Finds_[sit]_forms.pdf        # Fișe artefacte
├── Finds_[sit]_index.pdf        # Index artefacte
├── Grave_[sit]_forms.pdf        # Fișe morminte
├── Sample_[sit]_forms.pdf       # Fișe probe
├── Individual_[sit]_forms.pdf   # Fișe individ
└── ...
```

### Deschidere Folder

Butonul **„Deschide Folder"** deschide direct directorul de ieșire în managerul de fișiere al sistemului.

## Personalizarea Rapoartelor

### Șabloane PDF

Șabloanele sunt definite în module:
- `modules/utility/pyarchinit_exp_USsheet_pdf.py`
- `modules/utility/pyarchinit_exp_Findssheet_pdf.py`
- `modules/utility/pyarchinit_exp_Periodizzazionesheet_pdf.py`
- `modules/utility/pyarchinit_exp_Individui_pdf.py`
- `modules/utility/pyarchinit_exp_Strutturasheet_pdf.py`
- `modules/utility/pyarchinit_exp_Tombasheet_pdf.py`
- `modules/utility/pyarchinit_exp_Campsheet_pdf.py`

### Biblioteca Utilizată

PDF-urile sunt generate cu **ReportLab**, care permite:
- Aspecte personalizabile
- Inserarea de imagini
- Tabele formatate
- Anteturi/subsoluri

### Fonturi Necesare

Sistemul folosește fonturi specifice:
- **Cambria** (font principal)
- Instalare automată la prima pornire a pluginului

## Flux de Lucru Recomandat

### 1. Pregătirea Datelor

```
1. Completați toate fișele sitului
2. Verificați completitudinea datelor
3. Verificați periodizarea
4. Verificați relațiile stratigrafice
```

### 2. Export

```
1. Deschideți Export PDF
2. Selectați situl
3. Selectați tipurile de fișe
4. Faceți clic pe „Export PDF"
5. Așteptați finalizarea
```

### 3. Verificare

```
1. Deschideți folderul de ieșire
2. Verificați PDF-urile generate
3. Verificați formatarea
4. Tipăriți sau arhivați
```

## Depanare

### Eroare: „Nu există fișe de tipărit"

**Cauză**: Nu s-au găsit înregistrări pentru tipul selectat

**Soluție**:
- Verificați că există date pentru situl selectat
- Verificați baza de date

### PDF-uri Goale sau Incomplete

**Cauze posibile**:
1. Câmpuri obligatorii necompletate
2. Probleme de codificare a caracterelor
3. Fonturi lipsă

**Soluții**:
- Completați câmpurile obligatorii
- Verificați instalarea fontului Cambria

### Eroare de Font

**Cauză**: Fontul Cambria nu este instalat

**Soluție**:
- Pluginul încearcă instalarea automată
- Dacă apar probleme, instalați manual

### Export Lent

**Cauză**: Multe înregistrări de exportat

**Soluție**:
- Exportați pe tip separat
- Așteptați finalizarea

## Bune Practici

### 1. Organizare

- Exportați regulat în timpul săpăturii
- Creați copii de siguranță ale PDF-urilor generate
- Organizați pe campanie/an

### 2. Completitudinea Datelor

- Completați toate câmpurile înainte de export
- Verificați cotele din măsurătorile GIS
- Verificați relațiile stratigrafice

### 3. Arhivare

- Salvați PDF-urile pe suport sigur
- Includeți în documentația finală
- Atașați la raportul de săpătură

### 4. Tipărire

- Folosiți hârtie fără acid pentru arhivare
- Tipăriți în format A4
- Legați pe campanie

## Integrare cu Alte Funcții

### Cote din GIS

Sistemul recuperează automat:
- Cotele minime și maxime din geometrii
- Referințe la planurile GIS

### Documentație Fotografică

Rapoartele pot include referințe la:
- Fotografii asociate
- Desene și relevee

### Periodizare

Rapoartele US includ automat:
- Datarea extinsă din perioadă/fază atribuită
- Referințe cronologice

## Referințe

### Fișiere Sursă
- `tabs/Pdf_export.py` - Interfața de export
- `modules/utility/pyarchinit_exp_*_pdf.py` - Generatoare PDF

### Dependențe
- ReportLab (generare PDF)
- Fontul Cambria

---

## Tutorial Video

### Export PDF Complet
`[Substituent: video_export_pdf.mp4]`

**Conținut**:
- Selectarea sitului și fișelor
- Procesul de export
- Verificarea ieșirii
- Organizarea arhivei

**Durată estimată**: 10-12 minute

---

*Ultima actualizare: ianuarie 2026*
