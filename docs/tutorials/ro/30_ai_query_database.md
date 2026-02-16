# Tutorial 30: Interogare AI a bazei de date (Text2SQL)

## Introducere

**Interogare AI a bazei de date** este o functionalitate avansata PyArchInit care permite interogarea bazei de date arheologice utilizand **limbaj natural**. Sistemul converteste automat intrebarile in interogari SQL folosind inteligenta artificiala.

### Cum functioneaza

1. Utilizatorul scrie o intrebare in engleza/italiana
2. AI analizeaza cererea
3. Genereaza interogarea SQL corespunzatoare
4. Executa interogarea pe baza de date
5. Returneaza rezultatele

### Exemple de intrebari

- *"Gaseste toate descoperirile ceramice de la situl Vila Romana"*
- *"Arata US din epoca romana in aria 1000"*
- *"Cati indivizi au fost gasiti in morminte?"*
- *"Listeaza structurile cu datare medievala"*

## Acces

### Din formularul US/Descoperiri
Fila dedicata **"Interogare AI"** sau **"Text2SQL"**

### Din meniu
**PyArchInit** > **Interogare AI baza de date**

## Interfata

### Panoul de interogare

```
+--------------------------------------------------+
|         Generare SQL cu AI                        |
+--------------------------------------------------+
| Modul de generare:                                |
|   (o) OpenAI GPT-4 (API deja configurat)         |
|   ( ) Ollama (model local)                       |
|   ( ) API gratuit (daca este disponibil)         |
+--------------------------------------------------+
| Model Ollama: [llama3.2 v] [Verifica Ollama]     |
+--------------------------------------------------+
| Intrare:                                          |
|   Tip baza de date: [sqlite | postgresql]        |
|                                                  |
|   Descrieti interogarea:                         |
|   +--------------------------------------------+ |
|   | Gaseste toate descoperirile ceramice de la  | |
|   | situl Vila Romana cu datare intre sec. I-II | |
|   +--------------------------------------------+ |
+--------------------------------------------------+
| [Genereaza SQL]  [Golire]                        |
+--------------------------------------------------+
| Interogare SQL generata:                          |
|   +--------------------------------------------+ |
|   | SELECT * FROM inventario_materiali_table   | |
|   | WHERE sito = 'Vila Romana'                 | |
|   | AND tipo_reperto LIKE '%ceramic%'          | |
|   +--------------------------------------------+ |
| [Explica interogarea] [Copiaza] [Utilizeaza]     |
+--------------------------------------------------+
| Explicatie:                                       |
|   Interogarea selecteaza toate campurile din...  |
+--------------------------------------------------+
```

## Moduri de generare

### 1. OpenAI GPT-4

- **Cerinte**: Cheie API OpenAI configurata
- **Calitate**: Excelenta
- **Cost**: Plata la utilizare (API)
- **Viteza**: Rapida

### 2. Ollama (Local)

- **Cerinte**: Ollama instalat si pornit
- **Calitate**: Buna-Excelenta (depinde de model)
- **Cost**: Gratuit
- **Viteza**: Depinde de hardware

### 3. API gratuit

- **Cerinte**: Conexiune la internet
- **Calitate**: Variabila
- **Cost**: Gratuit
- **Limitari**: Limitare posibila a ratei

## Configurare

### OpenAI

1. Obtineti cheia API de pe [OpenAI](https://platform.openai.com/)
2. Configurati in **PyArchInit** > **Configurare** > **Chei API**
3. Selectati "OpenAI GPT-4" ca mod

### Ollama

1. Instalati Ollama de pe [ollama.ai](https://ollama.ai/)
2. Porniti Ollama: `ollama serve`
3. Descarcati modelul: `ollama pull llama3.2`
4. Selectati "Ollama" si verificati conexiunea

### Modele Ollama recomandate

| Model | Dimensiune | Calitate SQL |
|-------|-----------|--------------|
| llama3.2 | 2GB | Buna |
| mistral | 4GB | Excelenta |
| codellama | 7GB | Excelenta pentru SQL |
| qwen2.5-coder | 4GB | Excelenta pentru cod |

## Utilizare

### 1. Scrieti intrebarea

In caseta de intrare, descrieti ce doriti sa cautati:
- Utilizati limbaj natural
- Fiti specific cand este posibil
- Mentionati tabelele/campurile daca le cunoasteti

### 2. Generati SQL

1. Faceti clic pe **"Genereaza SQL"**
2. Asteptati procesarea
3. Vizualizati interogarea generata

### 3. Verificati interogarea

- Cititi interogarea SQL generata
- Faceti clic pe **"Explica interogarea"** pentru a intelege
- Verificati corectitudinea logica

### 4. Executati interogarea

- **"Copiaza interogarea"**: Copiaza in clipboard
- **"Utilizeaza interogarea"**: Executa direct in sistem

## Schema bazei de date

### Tabele principale

Sistemul cunoaste schema PyArchInit:

| Tabel | Descriere |
|-------|-----------|
| site_table | Situri arheologice |
| us_table | Unitati Stratigrafice |
| inventario_materiali_table | Descoperiri |
| pottery_table | Ceramica |
| tomba_table | Morminte |
| individui_table | Indivizi |
| struttura_table | Structuri |
| periodizzazione_table | Periodizare |
| campioni_table | Esantioane |
| documentazione_table | Documentatie |

### Campuri comune

AI cunoaste campurile principale:
- `sito` - Numele sitului
- `area` - Numarul ariei
- `us` - Numarul US
- `periodo_iniziale` / `fase_iniziale`
- `datazione_estesa`
- `descrizione` / `interpretazione`

## Exemple de interogari

### Cautarea descoperirilor

**Intrebare**: *"Gaseste toate descoperirile de bronz de la situl Roma Antica"*

```sql
SELECT * FROM inventario_materiali_table
WHERE sito = 'Roma Antica'
AND (tipo_reperto LIKE '%bronz%' OR definizione LIKE '%bronz%')
```

### Numararea US

**Intrebare**: *"Cate US exista pe perioada la situl Villa Adriana?"*

```sql
SELECT periodo_iniziale, COUNT(*) as num_us
FROM us_table
WHERE sito = 'Villa Adriana'
GROUP BY periodo_iniziale
```

### Cautare spatiala

**Intrebare**: *"Arata US din aria 1000 cu cote sub 10 metri"*

```sql
SELECT * FROM us_table
WHERE area = '1000'
AND quota_min_usm < 10
```

## Bune practici

### 1. Intrebari eficiente

- Fiti specific: nume de situri, numere, date
- Indicati ce doriti: lista, numaratoare, detalii
- Mentionati filtrele dorite

### 2. Verificarea rezultatelor

- Verificati intotdeauna interogarea generata
- Utilizati "Explica interogarea" daca nu este clara
- Testati pe un subset inainte de interogari complexe

### 3. Iteratie

- Daca rezultatul este incorect, reformulati intrebarea
- Adaugati detalii daca interogarea este prea larga
- Simplificati daca interogarea este prea complexa

## Depanare

### Interogarea nu este generata

**Cauze**:
- API neconfigurata
- Conexiune lipsa
- Intrebare neinteleasa

**Solutii**:
- Verificati configuratia API
- Verificati conexiunea
- Reformulati intrebarea

### Rezultate gresite

**Cauze**:
- Intrebare ambigua
- Camp/tabel inexistent

**Solutii**:
- Fiti mai specific
- Verificati numele tabelelor/campurilor

### Ollama nu raspunde

**Cauze**:
- Ollama nu este pornit
- Modelul nu este descarcat

**Solutii**:
- Porniti `ollama serve`
- Descarcati modelul necesar

## Referinte

### Fisiere sursa
- `modules/utility/textTosql.py` - Clasa MakeSQL
- `modules/utility/database_schema.py` - Schema bazei de date

### API-uri externe
- [OpenAI API](https://platform.openai.com/)
- [Ollama](https://ollama.ai/)

---

## Tutorial video

### Interogare AI a bazei de date
`[Placeholder: video_ai_query.mp4]`

**Continut**:
- Configurarea API
- Scrierea intrebarilor eficiente
- Interpretarea rezultatelor
- Bune practici

**Durata estimata**: 15-18 minute

---

*Ultima actualizare: ianuarie 2026*
