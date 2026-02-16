# Tutorial 15: Fișa de Arheozoologie (Faună)

## Introducere

**Fișa de Arheozoologie/Faună** (FIȘA FAUNĂ - FF) este modulul PyArchInit dedicat analizei și documentării resturilor faunistice. Permite înregistrarea datelor arheozoologice detaliate pentru studiul economiilor de subzistență antice.

### Concepte de Bază

**Arheozoologia:**
- Studiul resturilor animale din contexte arheologice
- Analiza relațiilor om-animal în trecut
- Reconstituirea dietelor, creșterii animalelor, vânătorii

**Date înregistrate:**
- Identificare taxonomică (specie)
- Părți scheletice prezente
- NMI (Numărul Minim de Indivizi)
- Stare de conservare
- Urme tafonomice
- Urme de tăiere/tranșare

---

## Accesarea Fișei

### Din Meniu
1. Meniul **PyArchInit** din bara de meniu QGIS
2. Selectați **Fișa Faună** (sau **Fișa Faună**)

### Din Bara de Instrumente
1. Localizați bara de instrumente PyArchInit
2. Faceți clic pe pictograma **Faună** (os stilizat)

---

## Prezentare Generală a Interfeței

Fișa este organizată în tab-uri tematice:

### Tab-uri Principale

| # | Tab | Conținut |
|---|-----|---------|
| 1 | Date de Identificare | Sit, Zonă, US, Context |
| 2 | Date Arheozoologice | Specie, NMI, Părți scheletice |
| 3 | Date Tafonomice | Conservare, Fragmentare, Urme |
| 4 | Date Contextuale | Context depozițional, Asocieri |
| 5 | Statistici | Diagrame și cuantificări |

---

## Bara de Instrumente

Bara de instrumente oferă funcții standard:

| Pictogramă | Funcție |
|------------|---------|
| Prima/Anterioară/Următoare/Ultima | Navigare înregistrări |
| Nou | Înregistrare nouă |
| Salvare | Salvare |
| Ștergere | Ștergere |
| Căutare | Căutare |
| Vizualizare Toate | Vizualizare toate |
| PDF | Export PDF |

---

## Tab-ul Date de Identificare

### Selectare US

**Câmp**: `comboBox_us_select`

Selectează US-ul sursă. Afișează US-urile disponibile în format „Sit - Zonă - US".

### Sit

**Câmp**: `comboBox_sito`
**Baza de date**: `sito`

Situl arheologic.

### Zonă

**Câmp**: `comboBox_area`
**Baza de date**: `area`

Zona de săpătură.

### Sondaj

**Câmp**: `comboBox_saggio`
**Baza de date**: `saggio`

Sondajul sursă.

### US

**Câmp**: `comboBox_us`
**Baza de date**: `us`

Unitatea Stratigrafică.

### Datarea US

**Câmp**: `lineEdit_datazione`
**Baza de date**: `datazione_us`

Cadrul cronologic al US-ului.

### Responsabil

**Câmp**: `comboBox_responsabile`
**Baza de date**: `responsabile_scheda`

Autorul fișei.

### Data Completării

**Câmp**: `dateEdit_data`
**Baza de date**: `data_compilazione`

Data completării fișei.

---

## Tab-ul Date Arheozoologice

### Context

**Câmp**: `comboBox_contesto`
**Baza de date**: `contesto`

Tipul contextului depozițional.

**Valori:**
- Așezare
- Groapă de deșeuri
- Umplutură
- Suprafață de locuire
- Înmormântare
- Ritual

### Specie

**Câmp**: `comboBox_specie`
**Baza de date**: `specie`

Identificare taxonomică.

**Specii arheozoologice frecvente:**
| Specie | Nume științific |
|--------|----------------|
| Bovine | Bos taurus |
| Oaie | Ovis aries |
| Capră | Capra hircus |
| Porc | Sus domesticus |
| Cal | Equus caballus |
| Cerb | Cervus elaphus |
| Mistreț | Sus scrofa |
| Iepure | Lepus europaeus |
| Câine | Canis familiaris |
| Pisică | Felis catus |
| Găină | Gallus gallus |

### Numărul Minim de Indivizi (NMI)

**Câmp**: `spinBox_nmi`
**Baza de date**: `numero_minimo_individui`

Estimarea numărului minim de indivizi reprezentați.

### Părți Scheletice

**Câmp**: `tableWidget_parti`
**Baza de date**: `parti_scheletriche`

Tabel pentru înregistrarea părților anatomice prezente.

**Coloane:**
| Coloană | Descriere |
|---------|-----------|
| Element | Os/parte anatomică |
| Lateralitate | Drept/Stâng/Axial |
| Cantitate | Număr de fragmente |
| NMI | Contribuție la NMI |

### Măsurători Osoase

**Câmp**: `tableWidget_misure`
**Baza de date**: `misure_ossa`

Măsurători osteometrice standard.

---

## Tab-ul Date Tafonomice

### Stare de Fragmentare

**Câmp**: `comboBox_frammentazione`
**Baza de date**: `stato_frammentazione`

Gradul de fragmentare al resturilor.

**Valori:**
- Complet
- Ușor fragmentat
- Fragmentat
- Puternic fragmentat

### Stare de Conservare

**Câmp**: `comboBox_conservazione`
**Baza de date**: `stato_conservazione`

Condiții generale de conservare.

**Valori:**
- Excelentă
- Bună
- Acceptabilă
- Proastă
- Foarte proastă

### Urme de Combustie

**Câmp**: `comboBox_combustione`
**Baza de date**: `tracce_combustione`

Prezența urmelor de foc.

**Valori:**
- Absent
- Înnegrire
- Carbonizare
- Calcinare

### Semne Tafonomice

**Câmp**: `comboBox_segni_tafo`
**Baza de date**: `segni_tafonomici_evidenti`

Urme de alterare post-depozițională.

**Tipuri:**
- Degradare atmosferică
- Urme de rădăcini
- Rozături
- Călcare

### Alterări Morfologice

**Câmp**: `textEdit_alterazioni`
**Baza de date**: `alterazioni_morfologiche`

Descrierea detaliată a alterărilor observate.

---

## Tab-ul Date Contextuale

### Metodologia de Recuperare

**Câmp**: `comboBox_metodologia`
**Baza de date**: `metodologia_recupero`

Metoda de colectare a resturilor.

**Valori:**
- Colectare manuală
- Cernere uscată
- Flotare
- Cernere umedă

### Resturi în Conexiune Anatomică

**Câmp**: `checkBox_connessione`
**Baza de date**: `resti_connessione_anatomica`

Prezența părților conectate.

### Clase de Artefacte Asociate

**Câmp**: `textEdit_associazioni`
**Baza de date**: `classi_reperti_associazione`

Alte materiale asociate cu resturile faunistice.

### Observații

**Câmp**: `textEdit_osservazioni`
**Baza de date**: `osservazioni`

Note generale.

### Interpretare

**Câmp**: `textEdit_interpretazione`
**Baza de date**: `interpretazione`

Interpretarea contextului faunistic.

---

## Tab-ul Statistici

Oferă instrumente pentru:
- Diagrame de distribuție pe specii
- Calculul NMI total
- Comparații între US-uri/faze
- Export date statistice

---

## Flux de Lucru Operațional

### Înregistrarea Resturilor Faunistice

1. **Deschideți fișa**
   - Din meniu sau bara de instrumente

2. **Înregistrare nouă**
   - Faceți clic pe „Înregistrare Nouă"

3. **Date de identificare**
   ```
   Sit: Vila Romană
   Zonă: 1000
   US: 150
   Responsabil: G. Verdi
   Data: 20/07/2024
   ```

4. **Date arheozoologice** (Tab 2)
   ```
   Context: Groapă de deșeuri
   Specie: Bos taurus
   NMI: 3

   Părți scheletice:
   - Humerus / Drept / 2 / 1
   - Tibie / Stâng / 3 / 2
   - Metapodial / - / 5 / 1
   ```

5. **Date tafonomice** (Tab 3)
   ```
   Fragmentare: Fragmentat
   Conservare: Bună
   Combustie: Absent
   Semne tafonomice: Urme de rădăcini
   ```

6. **Interpretare**
   ```
   Groapă de deșeuri alimentare.
   Prezența urmelor de tranșare
   pe unele oase lungi.
   ```

7. **Salvare**
   - Faceți clic pe „Salvare"

---

## Bune Practici

### Identificare

- Folosiți colecții de referință
- Indicați nivelul de certitudine al identificării
- Înregistrați și resturile neidentificabile

### NMI

- Calculați pentru fiecare specie separat
- Luați în considerare lateralitatea și vârsta artefactelor
- Documentați metoda de calcul

### Tafonomie

- Observați sistematic fiecare specimen
- Documentați urmele înainte de spălare
- Fotografiați cazurile semnificative

### Context

- Legați întotdeauna de US sursă
- Înregistrați metoda de recuperare
- Notați asocierile semnificative

---

## Export PDF

Fișa permite generarea:
- Fișe individuale detaliate
- Liste pe US sau fază
- Rapoarte statistice

---

## Depanare

### Problemă: Specia nu este disponibilă

**Cauză**: Lista de specii incompletă.

**Soluție**:
1. Verificați tezaurul de faună
2. Adăugați speciile lipsă
3. Contactați administratorul

### Problemă: NMI nu este calculat

**Cauză**: Părțile scheletice nu sunt înregistrate.

**Soluție**:
1. Completați tabelul de părți scheletice
2. Indicați lateralitatea și cantitatea
3. Sistemul va calcula automat

---

## Referințe

### Baza de Date

- **Tabel**: `fauna_table`
- **Clasă mapper**: `FAUNA`
- **ID**: `id_fauna`

### Fișiere Sursă

- **Controller**: `tabs/Fauna.py`
- **Export PDF**: `modules/utility/pyarchinit_exp_Faunasheet_pdf.py`

---

## Tutorial Video

### Înregistrare Arheozoologică
**Durată**: 12-15 minute
- Identificare taxonomică
- Înregistrarea părților scheletice
- Analiză tafonomică

[Substituent video: video_archeozoologia.mp4]

### Statistici Faunistice
**Durată**: 8-10 minute
- Calculul NMI
- Diagrame de distribuție
- Export date

[Substituent video: video_fauna_statistiche.mp4]

---

*Ultima actualizare: ianuarie 2026*
*PyArchInit - Sistem de Gestionare a Datelor Arheologice*
