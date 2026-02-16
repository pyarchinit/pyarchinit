# Tutorial 09: Fișa Probe

## Introducere

**Fișa Probe** este modulul PyArchInit dedicat gestionării probelor arheologice. Permite înregistrarea și urmărirea tuturor tipurilor de probe prelevate în timpul săpăturilor: pământ, cărbune, semințe, oase, mortare, metale și alte materiale destinate analizelor de specialitate.

### Tipuri de Probe

Probele arheologice includ:
- **Sedimente**: pentru analize sedimentologice, granulometrice
- **Cărbune**: pentru datare radiocarbon (C14)
- **Semințe/Polen**: pentru analize arheobotanice
- **Oase**: pentru analize arheozoologice, izotopice, ADN
- **Mortare/Tencuieli**: pentru analize arheometrice
- **Metale/Zgură**: pentru analize metalurgice
- **Ceramică**: pentru analize de pastă și proveniență

---

## Accesarea Fișei

### Din Meniu
1. Meniul **PyArchInit** din bara de meniu QGIS
2. Selectați **Fișa Probe**

### Din Bara de Instrumente
1. Localizați bara de instrumente PyArchInit
2. Faceți clic pe pictograma **Probe**

---

## Prezentare Generală a Interfeței

Fișa prezintă un aspect simplificat pentru gestionarea rapidă a probelor.

### Zone Principale

| # | Zonă | Descriere |
|---|------|-----------|
| 1 | Bara DBMS | Navigare, căutare, salvare |
| 2 | Info BD | Starea înregistrării, sortare, contor |
| 3 | Câmpuri de Identificare | Sit, Nr. Probă, Tip |
| 4 | Câmpuri Descriptive | Descriere, note |
| 5 | Câmpuri Depozitare | Cutie, Locație |

---

## Bara DBMS

### Butoane de Navigare

| Pictogramă | Funcție | Descriere |
|------------|---------|-----------|
| Prima înreg. | Mergi la prima înregistrare |
| Înreg. anterioară | Mergi la înregistrarea anterioară |
| Înreg. următoare | Mergi la înregistrarea următoare |
| Ultima înreg. | Mergi la ultima înregistrare |

### Butoane CRUD

| Pictogramă | Funcție | Descriere |
|------------|---------|-----------|
| Înregistrare nouă | Creează o nouă înregistrare de probă |
| Salvare | Salvează modificările |
| Ștergere | Șterge înregistrarea curentă |

### Butoane de Căutare

| Pictogramă | Funcție | Descriere |
|------------|---------|-----------|
| Căutare nouă | Începe o căutare nouă |
| Caută!!! | Execută căutarea |
| Ordonează după | Sortează rezultatele |
| Vizualizare toate | Vizualizează toate înregistrările |

---

## Câmpuri ale Fișei

### Sit

**Câmp**: `comboBox_sito`
**Baza de date**: `sito`

Selectați situl arheologic de apartenență.

### Număr Probă

**Câmp**: `lineEdit_nr_campione`
**Baza de date**: `nr_campione`

Număr progresiv de identificare a probei.

### Tip Probă

**Câmp**: `comboBox_tipo_campione`
**Baza de date**: `tipo_campione`

Clasificarea tipologică a probei. Valorile provin din tezaur.

**Tipuri frecvente:**
| Tip | Descriere |
|-----|-----------|
| Sediment | Probă de sol |
| Cărbune | Pentru datare C14 |
| Semințe | Resturi carpologice |
| Oase | Resturi faunistice |
| Mortar | Lianți de construcție |
| Ceramică | Pentru analiza pastei |
| Metal | Pentru analiză metalurgică |
| Polen | Pentru analiză palinologică |

### Descriere

**Câmp**: `textEdit_descrizione`
**Baza de date**: `descrizione`

Descrierea detaliată a probei.

**Conținut recomandat:**
- Caracteristicile fizice ale probei
- Cantitatea prelevată
- Metoda de colectare
- Motivul prelevării
- Analizele planificate

### Zonă

**Câmp**: `comboBox_area`
**Baza de date**: `area`

Zona de săpătură sursă.

### US

**Câmp**: `comboBox_us`
**Baza de date**: `us`

Unitatea Stratigrafică sursă.

### Număr Inventar Material

**Câmp**: `lineEdit_nr_inv_mat`
**Baza de date**: `numero_inventario_materiale`

Dacă proba este legată de un artefact inventariat, indicați numărul de inventar.

### Număr Cutie

**Câmp**: `lineEdit_nr_cassa`
**Baza de date**: `nr_cassa`

Cutia sau containerul de depozitare.

### Locul de Conservare

**Câmp**: `comboBox_luogo_conservazione`
**Baza de date**: `luogo_conservazione`

Unde este depozitată proba.

**Exemple:**
- Laboratorul de săpături
- Depozitul muzeului
- Laboratorul de analize extern
- Universitatea

---

## Flux de Lucru Operațional

### Crearea unei Probe Noi

1. **Deschideți fișa**
   - Din meniu sau bara de instrumente

2. **Înregistrare nouă**
   - Faceți clic pe „Înregistrare Nouă"

3. **Date de identificare**
   ```
   Sit: Vila Romană din Settefinestre
   Nr. Probă: C-2024-001
   Tip probă: Cărbune
   ```

4. **Proveniență**
   ```
   Zonă: 1000
   US: 150
   ```

5. **Descriere**
   ```
   Probă de cărbune prelevată din
   suprafața arsă a US 150.
   Cantitate: aprox. 50 gr.
   Colectată pentru datare C14.
   ```

6. **Depozitare**
   ```
   Nr. Cutie: Samp-1
   Locație: Laboratorul de săpături
   ```

7. **Salvare**
   - Faceți clic pe „Salvare"

### Căutarea Probelor

1. Faceți clic pe „Căutare Nouă"
2. Completați criteriile:
   - Sit
   - Tip probă
   - US
3. Faceți clic pe „Caută"
4. Navigați prin rezultate

---

## Export PDF

Fișa suportă exportul PDF pentru:
- Lista probelor
- Fișe individuale detaliate

---

## Bune Practici

### Denumire

- Folosiți coduri unice și semnificative
- Format recomandat: `SIT-AN-PROGRESIV`
- Exemplu: `VRS-2024-C001`

### Colectare

- Documentați întotdeauna coordonatele colectării
- Fotografiați punctul de colectare
- Notați adâncimea și contextul

### Depozitare

- Folosiți containere adecvate tipului
- Etichetați clar fiecare probă
- Mențineți condiții adecvate

### Documentare

- Legați întotdeauna de US sursă
- Indicați analizele planificate
- Înregistrați expedierile către laboratoare externe

---

## Depanare

### Problemă: Tipul de probă nu este disponibil

**Cauză**: Tezaurul nu este configurat.

**Soluție**:
1. Deschideți Fișa Tezaur
2. Adăugați tipul lipsă pentru `campioni_table`
3. Salvați și redeschideți Fișa Probe

### Problemă: US nu este afișată

**Cauză**: US nu este înregistrată pentru situl selectat.

**Soluție**:
1. Verificați că US există în Fișa US
2. Verificați că aparține aceluiași sit

---

## Referințe

### Baza de Date

- **Tabel**: `campioni_table`
- **Clasă mapper**: `CAMPIONI`
- **ID**: `id_campione`

### Fișiere Sursă

- **UI**: `gui/ui/Campioni.ui`
- **Controller**: `tabs/Campioni.py`
- **Export PDF**: `modules/utility/pyarchinit_exp_Campsheet_pdf.py`

---

## Tutorial Video

### Gestionarea Probelor
**Durată**: 5-6 minute
- Crearea unei probe noi
- Completarea câmpurilor
- Căutare și export

[Substituent video: video_campioni.mp4]

---

*Ultima actualizare: ianuarie 2026*
*PyArchInit - Sistem de Gestionare a Datelor Arheologice*
