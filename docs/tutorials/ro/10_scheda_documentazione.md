# Tutorial 10: Fișa Documentație

## Introducere

**Fișa Documentație** este modulul PyArchInit pentru gestionarea documentației grafice de săpătură: planuri, secțiuni, elevații, relevee și orice altă producție grafică realizată în cursul activităților arheologice.

### Tipuri de Documentație

- **Planuri**: planuri de strat, planuri de fază, planuri generale
- **Secțiuni**: secțiuni stratigrafice
- **Elevații**: elevații de ziduri, fronturi de săpătură
- **Relevee**: relevee topografice, fotogrammetrice
- **Ortofotografii**: rezultate drone/fotogrammetrie
- **Desene de artefacte**: ceramică, metale, etc.

---

## Accesarea Fișei

### Din Meniu
1. Meniul **PyArchInit** din bara de meniu QGIS
2. Selectați **Fișa Documentație**

### Din Bara de Instrumente
1. Localizați bara de instrumente PyArchInit
2. Faceți clic pe pictograma **Documentație**

---

## Prezentare Generală a Interfeței

### Zone Principale

| # | Zonă | Descriere |
|---|------|-----------|
| 1 | Bara DBMS | Navigare, căutare, salvare |
| 2 | Info BD | Starea înregistrării, sortare, contor |
| 3 | Câmpuri de Identificare | Sit, Nume, Dată |
| 4 | Câmpuri Tipologice | Tip, Sursă, Scară |
| 5 | Câmpuri Descriptive | Desenator, Note |

---

## Bara DBMS

### Butoane Standard

| Funcție | Descriere |
|---------|-----------|
| Prima/Anterioară/Următoare/Ultima înreg. | Navigare între înregistrări |
| Înregistrare nouă | Creează o înregistrare nouă |
| Salvare | Salvează modificările |
| Ștergere | Șterge înregistrarea |
| Căutare nouă / Caută | Funcții de căutare |
| Ordonează după | Sortează rezultatele |
| Vizualizare toate | Vizualizează toate înregistrările |

---

## Câmpuri ale Fișei

### Sit

**Câmp**: `comboBox_sito_doc`
**Baza de date**: `sito`

Situl arheologic de referință.

### Numele Documentului

**Câmp**: `lineEdit_nome_doc`
**Baza de date**: `nome_doc`

Numele de identificare al documentului.

**Convenții de denumire:**
- `P` = Plan (ex.: P001)
- `S` = Secțiune (ex.: S001)
- `E` = Elevație (ex.: E001)
- `R` = Releveu (ex.: R001)

### Data

**Câmp**: `dateEdit_data`
**Baza de date**: `data`

Data de execuție a desenului/releveului.

### Tipul Documentației

**Câmp**: `comboBox_tipo_doc`
**Baza de date**: `tipo_documentazione`

Tipul documentului.

**Valori tipice:**
| Tip | Descriere |
|-----|-----------|
| Plan de strat | US individual |
| Plan de fază | US contemporane multiple |
| Plan general | Vedere de ansamblu |
| Secțiune stratigrafică | Profil vertical |
| Elevație | Zidărie în elevație |
| Releveu topografic | Planimetrie generală |
| Ortofotografie | Din fotogrammetrie |
| Desen de artefact | Ceramică, metal, etc. |

### Sursa

**Câmp**: `comboBox_sorgente`
**Baza de date**: `sorgente`

Sursa/metoda de producție.

**Valori:**
- Releveu direct
- Fotogrammetrie
- Scanner laser
- GPS/Stație totală
- Digitizare CAD
- Ortofotografie cu dronă

### Scara

**Câmp**: `comboBox_scala`
**Baza de date**: `scala`

Scara de reprezentare.

**Scări frecvente:**
| Scară | Utilizare tipică |
|-------|------------------|
| 1:1 | Desene de artefacte |
| 1:5 | Detalii |
| 1:10 | Secțiuni, detalii |
| 1:20 | Planuri de strat |
| 1:50 | Planuri generale |
| 1:100 | Planimetrii |
| 1:200+ | Hărți topografice |

### Desenator

**Câmp**: `comboBox_disegnatore`
**Baza de date**: `disegnatore`

Autorul desenului/releveului.

### Note

**Câmp**: `textEdit_note`
**Baza de date**: `note`

Note suplimentare despre document.

---

## Flux de Lucru Operațional

### Înregistrarea unei Documentații Noi

1. **Deschideți fișa**
   - Din meniu sau bara de instrumente

2. **Înregistrare nouă**
   - Faceți clic pe „Înregistrare Nouă"

3. **Date de identificare**
   ```
   Sit: Vila Romană din Settefinestre
   Nume: P025
   Data: 15/06/2024
   ```

4. **Clasificare**
   ```
   Tip: Plan de strat
   Sursa: Releveu direct
   Scara: 1:20
   ```

5. **Autor și note**
   ```
   Desenator: M. Rossi
   Note: Plan US 150. Evidențiază
   limitele suprafeței de podea.
   ```

6. **Salvare**
   - Faceți clic pe „Salvare"

### Căutarea Documentației

1. Faceți clic pe „Căutare Nouă"
2. Completați criteriile:
   - Sit
   - Tip documentație
   - Scară
   - Desenator
3. Faceți clic pe „Caută"
4. Navigați prin rezultate

---

## Export PDF

Fișa suportă exportul PDF pentru:
- Lista documentației
- Fișe detaliate

---

## Bune Practici

### Denumire

- Folosiți coduri consistente pe tot proiectul
- Numerotare progresivă pe tip
- Documentați convențiile adoptate

### Organizare

- Legați întotdeauna de situl de referință
- Indicați scara reală
- Înregistrați data și autorul

### Arhivare

- Legați fișierele digitale prin gestionarea media
- Mențineți copii de siguranță
- Folosiți formate standard (PDF, TIFF)

---

## Depanare

### Problemă: Tipul de documentație nu este disponibil

**Cauză**: Tezaurul nu este configurat.

**Soluție**:
1. Deschideți Fișa Tezaur
2. Adăugați tipurile lipsă pentru `documentazione_table`

### Problemă: Fișierul nu este afișat

**Cauză**: Cale incorectă sau fișier lipsă.

**Soluție**:
1. Verificați că fișierul există
2. Verificați calea în configurarea media

---

## Referințe

### Baza de Date

- **Tabel**: `documentazione_table`
- **Clasă mapper**: `DOCUMENTAZIONE`
- **ID**: `id_documentazione`

### Fișiere Sursă

- **UI**: `gui/ui/Documentazione.ui`
- **Controller**: `tabs/Documentazione.py`
- **Export PDF**: `modules/utility/pyarchinit_exp_Documentazionesheet_pdf.py`

---

## Tutorial Video

### Gestionarea Documentației Grafice
**Durată**: 6-8 minute
- Înregistrarea unei documentații noi
- Clasificare și metadate
- Căutare și consultare

[Substituent video: video_documentazione.mp4]

---

*Ultima actualizare: ianuarie 2026*
*PyArchInit - Sistem de Gestionare a Datelor Arheologice*
