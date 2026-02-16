# Tutorial 13: Gestionarea Tezaurului

## Introducere

**Tezaurul** din PyArchInit este sistemul centralizat pentru gestionarea vocabularelor controlate. Permite definirea și menținerea listelor de valori utilizate în toate formularele pluginului, asigurând consistența terminologică și facilitând căutarea.

### Funcții Principale

- Gestionarea vocabularelor pentru fiecare formular
- Suport multilingv
- Coduri și descrieri extinse
- Integrare GPT pentru sugestii
- Import/export fișiere CSV

---

## Accesarea Tezaurului

### Din Meniu
1. Meniul **PyArchInit** din bara de meniu QGIS
2. Selectați **Tezaur** (sau **Fișa Tezaur**)

### Din Bara de Instrumente
1. Localizați bara de instrumente PyArchInit
2. Faceți clic pe pictograma **Tezaur** (carte/dicționar)

---

## Prezentare Generală a Interfeței

### Zone Principale

| # | Zonă | Descriere |
|---|------|-----------|
| 1 | Bara DBMS | Navigare, căutare, salvare |
| 2 | Selectare Tabel | Alegerea formularului de configurat |
| 3 | Câmpuri Cod | Cod, extensie, tip |
| 4 | Descriere | Descrierea detaliată a termenului |
| 5 | Limbă | Selectarea limbii |
| 6 | Instrumente | Import CSV, sugestii GPT |

---

## Câmpurile Tezaurului

### Numele Tabelului

**Câmp**: `comboBox_nome_tabella`
**Baza de date**: `nome_tabella`

Selectați formularul pentru care doriți să definiți valori.

**Tabele disponibile:**
| Tabel | Descriere |
|-------|-----------|
| `us_table` | Fișa US/USM |
| `site_table` | Fișa Sit |
| `periodizzazione_table` | Periodizare |
| `inventario_materiali_table` | Inventar Materiale |
| `pottery_table` | Fișa Ceramică |
| `campioni_table` | Fișa Probe |
| `documentazione_table` | Documentație |
| `tomba_table` | Fișa Mormânt |
| `individui_table` | Fișa Individ |
| `fauna_table` | Arheozoologie |
| `ut_table` | Fișa UT |

### Cod

**Câmp**: `comboBox_sigla`
**Baza de date**: `sigla`

Codul scurt/abrevierea termenului.

**Exemple:**
- `ZD` pentru Zid
- `US` pentru Unitate Stratigrafică
- `CR` pentru Ceramică

### Cod Extins

**Câmp**: `comboBox_sigla_estesa`
**Baza de date**: `sigla_estesa`

Forma completă a termenului.

**Exemple:**
- `Zid perimetral`
- `Unitate Stratigrafică`
- `Ceramică comună`

### Descriere

**Câmp**: `textEdit_descrizione_sigla`
**Baza de date**: `descrizione`

Descrierea detaliată a termenului, definiție, note de utilizare.

### Tipul Codului

**Câmp**: `comboBox_tipologia_sigla`
**Baza de date**: `tipologia_sigla`

Cod numeric care identifică câmpul de destinație.

**Structura codului:**
```
X.Y unde:
X = numărul tabelului
Y = numărul câmpului
```

**Exemple pentru us_table:**
| Cod | Câmp |
|-----|------|
| 1.1 | Definiția stratigrafică |
| 1.2 | Modul de formare |
| 1.3 | Tipul US |

### Limba

**Câmp**: `comboBox_lingua`
**Baza de date**: `lingua`

Limba termenului.

**Limbi suportate:**
- IT (Italiană)
- EN_US (Engleză)
- DE (Germană)
- FR (Franceză)
- ES (Spaniolă)
- AR (Arabă)
- CA (Catalană)

---

## Câmpuri de Ierarhie

### ID Părinte

**Câmp**: `comboBox_id_parent`
**Baza de date**: `id_parent`

ID-ul termenului părinte (pentru structuri ierarhice).

### Cod Părinte

**Câmp**: `comboBox_parent_sigla`
**Baza de date**: `parent_sigla`

Codul termenului părinte.

### Nivel Ierarhie

**Câmp**: `spinBox_hierarchy`
**Baza de date**: `hierarchy_level`

Nivelul în ierarhie (0=rădăcină, 1=primul nivel, etc.).

---

## Funcții Speciale

### Sugestii GPT

Butonul „Sugestii" folosește OpenAI GPT pentru:
- Generarea automată de descrieri
- Furnizarea de link-uri Wikipedia de referință
- Sugerarea de definiții în context arheologic

**Utilizare:**
1. Selectați sau introduceți un termen în „Cod extins"
2. Faceți clic pe „Sugestii"
3. Selectați modelul GPT
4. Așteptați generarea
5. Revizuiți și salvați

**Notă:** Necesită o cheie API OpenAI configurată.

### Import CSV

Pentru baze de date SQLite, vocabularele pot fi importate din fișiere CSV.

**Formatul CSV necesar:**
```csv
nome_tabella,sigla,sigla_estesa,descrizione,tipologia_sigla,lingua
us_table,ZD,Zid,Structură de zid,1.3,EN_US
us_table,PD,Podea,Suprafață de călcat,1.3,EN_US
```

**Procedură:**
1. Faceți clic pe „Import CSV"
2. Selectați fișierul
3. Confirmați importul
4. Verificați datele importate

---

## Flux de Lucru Operațional

### Adăugarea unui Termen Nou

1. **Deschideți Tezaurul**
   - Din meniu sau bara de instrumente

2. **Înregistrare nouă**
   - Faceți clic pe „Înregistrare Nouă"

3. **Selectarea tabelului**
   ```
   Numele tabelului: us_table
   ```

4. **Definirea termenului**
   ```
   Cod: FT
   Cod extins: Fântână
   Tipul codului: 1.3
   Limba: EN_US
   ```

5. **Descriere**
   ```
   Structură excavată în sol pentru
   alimentarea cu apă. De formă generală
   circulară cu căptușeală de piatră sau cărămidă.
   ```

6. **Salvare**
   - Faceți clic pe „Salvare"

### Căutarea Termenilor

1. Faceți clic pe „Căutare Nouă"
2. Completați criteriile:
   - Numele tabelului
   - Cod sau cod extins
   - Limba
3. Faceți clic pe „Caută"
4. Navigați prin rezultate

### Modificarea unui Termen Existent

1. Căutați termenul de modificat
2. Modificați câmpurile necesare
3. Faceți clic pe „Salvare"

---

## Organizarea Tipurilor de Cod

### Structură Recomandată

Pentru fiecare tabel, organizați codurile sistematic:

**us_table (1.x):**
| Cod | Câmp |
|-----|------|
| 1.1 | Definiția stratigrafică |
| 1.2 | Modul de formare |
| 1.3 | Tipul US |
| 1.4 | Consistența |
| 1.5 | Culoarea |

**inventario_materiali_table (2.x):**
| Cod | Câmp |
|-----|------|
| 2.1 | Tipul artefactului |
| 2.2 | Clasa materialului |
| 2.3 | Definiția |
| 2.4 | Starea de conservare |

**pottery_table (3.x):**
| Cod | Câmp |
|-----|------|
| 3.1 | Forma |
| 3.2 | Clasa ceramică |
| 3.3 | Pasta |
| 3.4 | Tratament de suprafață |

---

## Bune Practici

### Consistență Terminologică

- Folosiți întotdeauna aceiași termeni pentru aceleași concepte
- Evitați sinonimele nedocumentate
- Documentați convențiile adoptate

### Multilingv

- Creați termeni în toate limbile necesare
- Mențineți corespondențele între limbi
- Folosiți traduceri oficiale când sunt disponibile

### Ierarhie

- Folosiți structura ierarhică pentru termeni înrudiți
- Definiți clar nivelurile
- Documentați relațiile

### Întreținere

- Revizuiți periodic vocabularele
- Eliminați termenii obsoleți
- Actualizați descrierile

---

## Depanare

### Problemă: Termenul nu este vizibil în ComboBox-uri

**Cauză:** Cod de tip incorect sau limbă nepotrivită.

**Soluție:**
1. Verificați codul tipologia_sigla
2. Verificați limba setată
3. Verificați că înregistrarea este salvată

### Problemă: Importul CSV a eșuat

**Cauză:** Format incorect al fișierului.

**Soluție:**
1. Verificați structura CSV
2. Verificați delimitatorii (virgulă)
3. Verificați codificarea (UTF-8)

### Problemă: Sugestiile GPT nu funcționează

**Cauză:** Cheie API lipsă sau invalidă.

**Soluție:**
1. Verificați configurarea cheii API
2. Verificați conexiunea la internet
3. Verificați creditul OpenAI

---

## Referințe

### Baza de Date

- **Tabel**: `pyarchinit_thesaurus_sigle`
- **Clasă mapper**: `PYARCHINIT_THESAURUS_SIGLE`
- **ID**: `id_thesaurus_sigle`

### Fișiere Sursă

- **UI**: `gui/ui/Thesaurus.ui`
- **Controller**: `tabs/Thesaurus.py`

---

## Tutorial Video

### Gestionarea Vocabularelor
**Durată**: 10-12 minute
- Structura tezaurului
- Adăugarea termenilor
- Organizarea codurilor

[Substituent video: video_thesaurus_gestione.mp4]

### Multilingv și Import
**Durată**: 8-10 minute
- Configurarea limbilor
- Import CSV
- Sugestii GPT

[Substituent video: video_thesaurus_avanzato.mp4]

---

*Ultima actualizare: ianuarie 2026*
*PyArchInit - Sistem de Gestionare a Datelor Arheologice*

---

## Animație Interactivă

Explorați animația interactivă pentru a afla mai multe despre acest subiect.

[Deschideți Animația Interactivă](../../animations/pyarchinit_thesaurus_animation.html)
