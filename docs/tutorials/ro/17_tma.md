# Tutorial 17: TMA - Tabelul Materialelor Arheologice

## Introducere

**Formularul TMA** (Tabelul Materialelor Arheologice) este modulul avansat PyArchInit pentru gestionarea materialelor din excavare conform standardelor ministeriale italiene. Permite catalogarea detaliata conform reglementarilor ICCD (Institutul Central pentru Catalogare si Documentare).

### Functionalitati principale

- Catalogare conform ICCD
- Gestionarea materialelor pe cutii/containere
- Campuri cronologice detaliate
- Tabel de materiale asociate
- Gestionare media integrata
- Export de etichete si formulare PDF

---

## Accesarea formularului

### Prin meniu
1. Meniul **PyArchInit** din bara de meniu QGIS
2. Selectati **Formular TMA**

### Prin bara de instrumente
1. Localizati bara de instrumente PyArchInit
2. Faceti clic pe pictograma **TMA**

---

## Prezentarea interfetei

Formularul prezinta o interfata complexa cu multe campuri.

### Zone principale

| # | Zona | Descriere |
|---|------|-----------|
| 1 | Bara de instrumente DBMS | Navigare, cautare, salvare |
| 2 | Campuri de identificare | Sit, Arie, US, Cutie |
| 3 | Campuri de localizare | Locatie, Camera, Sondaj |
| 4 | Campuri cronologice | Perioada, Fractiune, Cronologii |
| 5 | Tabel materiale | Detalii materiale asociate |
| 6 | Fila Media | Imagini si documente |

---

## Campuri de identificare

### Sit

**Camp**: `comboBox_sito`
**Baza de date**: `sito`

Situl arheologic (SCAN - Denumirea Excavarii ICCD).

### Arie

**Camp**: `comboBox_area`
**Baza de date**: `area`

Aria de excavare.

### US (DSCU)

**Camp**: `comboBox_us`
**Baza de date**: `dscu`

Unitatea Stratigrafice Sursa (DSCU = Descrierea Unitatii de Excavare).

### Sector

**Camp**: `comboBox_settore`
**Baza de date**: `settore`

Sectorul de excavare.

### Inventar

**Camp**: `lineEdit_inventario`
**Baza de date**: `inventario`

Numarul de inventar.

### Cutie

**Camp**: `lineEdit_cassetta`
**Baza de date**: `cassetta`

Numarul cutiei/containerului.

---

## Campuri de localizare ICCD

### LDCT - Tipul locatiei

**Camp**: `comboBox_ldct`
**Baza de date**: `ldct`

Tipul locatiei de depozitare.

**Valori ICCD:**
- muzeu
- superintendenta
- depozit
- laborator
- altele

### LDCN - Numele locatiei

**Camp**: `lineEdit_ldcn`
**Baza de date**: `ldcn`

Numele specific al locatiei de depozitare.

### Locatia anterioara

**Camp**: `lineEdit_vecchia_coll`
**Baza de date**: `vecchia_collocazione`

Locatia anterioara daca este cazul.

### SCAN - Numele excavarii

**Camp**: `lineEdit_scan`
**Baza de date**: `scan`

Numele oficial al excavarii/cercetarii.

### Sondaj

**Camp**: `comboBox_saggio`
**Baza de date**: `saggio`

Sondajul de referinta.

### Camera/Locus

**Camp**: `lineEdit_vano`
**Baza de date**: `vano_locus`

Camera sau locusul de origine.

---

## Campuri cronologice

### DTZG - Perioada cronologica

**Camp**: `comboBox_dtzg`
**Baza de date**: `dtzg`

Perioada cronologica generala.

**Exemple ICCD:**
- Epoca Bronzului
- Epoca Fierului
- Epoca Romana
- Epoca Medievala

### DTZS - Fractiunea cronologica

**Camp**: `comboBox_dtzs`
**Baza de date**: `dtzs`

Subdiviziunea perioadei.

**Exemple:**
- timpurie
- mijlocie
- tarzie
- finala

### Cronologii

**Camp**: `tableWidget_cronologie`
**Baza de date**: `cronologie`

Tabel pentru cronologii multiple sau detaliate.

---

## Campuri de achizitie

### AINT - Tipul achizitiei

**Camp**: `comboBox_aint`
**Baza de date**: `aint`

Metoda de achizitie a materialelor.

**Valori ICCD:**
- excavare
- prospectiune
- achizitie
- donatie
- confiscare

### AIND - Data achizitiei

**Camp**: `dateEdit_aind`
**Baza de date**: `aind`

Data achizitiei.

### RCGD - Data prospectiunii

**Camp**: `dateEdit_rcgd`
**Baza de date**: `rcgd`

Data prospectiunii (daca este cazul).

### RCGZ - Detalii prospectiune

**Camp**: `textEdit_rcgz`
**Baza de date**: `rcgz`

Note privind prospectiunea.

---

## Campuri materiale

### OGTM - Material

**Camp**: `comboBox_ogtm`
**Baza de date**: `ogtm`

Materialul principal (Tipul Materialului Obiectului).

**Valori ICCD:**
- ceramica
- sticla
- metal
- os
- piatra
- caramida/tigla

### Nr. de descoperiri

**Camp**: `spinBox_n_reperti`
**Baza de date**: `n_reperti`

Numarul total de descoperiri.

### Greutate

**Camp**: `doubleSpinBox_peso`
**Baza de date**: `peso`

Greutatea totala in grame.

### DESO - Descrierea obiectului

**Camp**: `textEdit_deso`
**Baza de date**: `deso`

Descrierea succinta a obiectelor.

---

## Tabelul detaliat al materialelor

**Widget**: `tableWidget_materiali`
**Tabel asociat**: `tma_materiali`

Permite inregistrarea materialelor individuale continute in cutie.

### Coloane

| Camp ICCD | Descriere |
|-----------|-----------|
| MADI | Inventar material |
| MACC | Categorie |
| MACL | Clasa |
| MACP | Specificatie tipologica |
| MACD | Definitie |
| Cronologie | Datare specifica |
| MACQ | Cantitate |

### Gestionarea randurilor

| Buton | Functie |
|-------|---------|
| + | Adaugare material |
| - | Eliminare material |

---

## Campuri de documentatie

### FTAP - Tipul fotografiei

**Camp**: `comboBox_ftap`
**Baza de date**: `ftap`

Tipul documentatiei fotografice.

### FTAN - Codul fotografiei

**Camp**: `lineEdit_ftan`
**Baza de date**: `ftan`

Codul de identificare al fotografiei.

### DRAT - Tipul desenului

**Camp**: `comboBox_drat`
**Baza de date**: `drat`

Tipul documentatiei grafice.

### DRAN - Codul desenului

**Camp**: `lineEdit_dran`
**Baza de date**: `dran`

Codul de identificare al desenului.

### DRAA - Autorul desenului

**Camp**: `lineEdit_draa`
**Baza de date**: `draa`

Autorul desenului.

---

## Fila Media

Gestionarea imaginilor asociate cutiei/TMA.

### Functionalitati

- Vizualizare miniaturi
- Drag & drop pentru adaugarea imaginilor
- Dublu clic pentru vizualizare
- Legatura cu baza de date media

---

## Fila vizualizare tabelara

Vizualizare tabelara a tuturor inregistrarilor TMA pentru consultare rapida.

### Functionalitati

- Vizualizare grila
- Sortare pe coloane
- Filtre rapide
- Selectie multipla

---

## Export si tiparire

### Export PDF

| Optiune | Descriere |
|---------|-----------|
| Formular TMA | Formularul complet |
| Etichete | Etichete pentru cutii |

### Etichete pentru cutii

Generare automata de etichete pentru:
- Identificarea cutiei
- Continut succint
- Date de provenienta
- Cod de bare (optional)

---

## Flux de lucru operational

### Inregistrarea unui TMA nou

1. **Deschideti formularul**
   - Prin meniu sau bara de instrumente

2. **Inregistrare noua**
   - Faceti clic pe "Inregistrare noua"

3. **Date de identificare**
   ```
   Sit: Vila Romana
   Arie: 1000
   US: 150
   Cutie: C-001
   ```

4. **Locatie**
   ```
   LDCT: depozit
   LDCN: Depozitul Superintendentei Roma
   SCAN: Excavarile Vilei Romane 2024
   ```

5. **Cronologie**
   ```
   DTZG: Epoca Romana
   DTZS: Imperial
   ```

6. **Materiale** (tabel)
   ```
   | Inv | Cat | Clasa | Def | Cant |
   |-----|-----|-------|-----|------|
   | 001 | ceramica | comuna | borcan | 5 |
   | 002 | ceramica | sigillata | farfurie | 3 |
   | 003 | sticla | - | unguentarium | 1 |
   ```

7. **Salvare**
   - Faceti clic pe "Salvare"

---

## Bune practici

### Standarde ICCD

- Utilizati vocabularele controlate ICCD
- Urmati abrevierile oficiale
- Mentineti consistenta terminologica

### Organizarea cutiilor

- Numerotare progresiva unica
- Un TMA per cutie fizica
- Separati pe US cand este posibil

### Documentatie

- Legati intotdeauna fotografiile si desenele
- Utilizati coduri unice pentru media
- Inregistrati autorul si data

---

## Depanare

### Problema: Vocabularele ICCD nu sunt disponibile

**Cauza**: Tezaurul nu este configurat.

**Solutie**:
1. Importati vocabularele standard ICCD
2. Verificati configuratia tezaurului

### Problema: Materialele nu sunt salvate

**Cauza**: Tabelul de materiale nu este sincronizat.

**Solutie**:
1. Verificati ca toate campurile obligatorii sunt completate
2. Salvati formularul principal inainte de a adauga materiale

---

## Referinte

### Baza de date

- **Tabel principal**: `tma_materiali_archeologici`
- **Tabel detaliu**: `tma_materiali`
- **Clasa mapper**: `TMA`, `TMA_MATERIALI`
- **ID**: `id`

### Fisiere sursa

- **UI**: `gui/ui/Tma.ui`
- **Controller**: `tabs/Tma.py`
- **Export PDF**: `modules/utility/pyarchinit_exp_Tmasheet_pdf.py`
- **Etichete**: `modules/utility/pyarchinit_tma_label_pdf.py`

---

## Tutorial video

### Catalogarea TMA
**Durata**: 15-18 minute
- Standarde ICCD
- Completare integrala
- Gestionarea materialelor

[Video placeholder: video_tma_catalogazione.mp4]

### Generarea etichetelor
**Durata**: 5-6 minute
- Configurarea etichetelor
- Tiparire in lot
- Personalizare

[Video placeholder: video_tma_etichette.mp4]

---

*Ultima actualizare: ianuarie 2026*
*PyArchInit - Sistem de gestionare a datelor arheologice*
